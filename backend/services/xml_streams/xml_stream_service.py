"""
XML Stream Service - Stream Management for Streamworks
Manages XML stream persistence, versioning, and CRUD operations
"""
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, delete, update, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_async_session
from models.xml_streams import XMLStream, StreamVersion
from schemas.xml_streams import (
    XMLStreamCreate, XMLStreamUpdate, XMLStreamResponse,
    XMLStreamListResponse, StreamFilters, StreamSortBy
)

logger = logging.getLogger(__name__)


class XMLStreamService:
    """Service for managing XML streams in the database"""
    
    def __init__(self, db_session: AsyncSession = None):
        self.db_session = db_session
    
    async def get_session(self) -> AsyncSession:
        """Get database session"""
        if self.db_session:
            return self.db_session
        
        # Create new session if none provided
        async for session in get_async_session():
            return session
    
    async def create_stream(
        self, 
        stream_data: XMLStreamCreate, 
        user_id: str = "anonymous"
    ) -> XMLStreamResponse:
        """Create a new XML stream"""
        try:
            session = await self.get_session()
            
            # Create new stream
            new_stream = XMLStream(
                id=uuid4(),
                stream_name=stream_data.stream_name,
                description=stream_data.description,
                xml_content=stream_data.xml_content,
                wizard_data=stream_data.wizard_data,
                job_type=stream_data.job_type,
                status=stream_data.status or "draft",
                created_by=user_id,
                tags=stream_data.tags or [],
                is_favorite=stream_data.is_favorite or False
            )
            
            session.add(new_stream)
            await session.commit()
            await session.refresh(new_stream)
            
            # Create initial version
            if stream_data.wizard_data or stream_data.xml_content:
                await self._create_version(
                    session, 
                    new_stream.id, 
                    1, 
                    stream_data.wizard_data,
                    stream_data.xml_content,
                    "Initial version"
                )
                await session.commit()
            
            logger.info(f"Created XML stream: {new_stream.stream_name} (ID: {new_stream.id})")
            
            return XMLStreamResponse.from_orm(new_stream)
            
        except Exception as e:
            logger.error(f"Error creating XML stream: {str(e)}")
            raise
    
    async def get_stream_by_id(
        self, 
        stream_id: UUID, 
        user_id: str = "anonymous"
    ) -> Optional[XMLStreamResponse]:
        """Get a stream by ID"""
        try:
            session = await self.get_session()
            
            query = select(XMLStream).where(
                and_(
                    XMLStream.id == stream_id,
                    XMLStream.created_by == user_id
                )
            )
            
            result = await session.execute(query)
            stream = result.scalar_one_or_none()
            
            if stream:
                return XMLStreamResponse.from_orm(stream)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting stream by ID {stream_id}: {str(e)}")
            raise
    
    async def update_stream(
        self, 
        stream_id: UUID, 
        stream_update: XMLStreamUpdate,
        user_id: str = "anonymous",
        create_version: bool = True
    ) -> Optional[XMLStreamResponse]:
        """Update an existing XML stream"""
        try:
            session = await self.get_session()
            
            # Get existing stream
            query = select(XMLStream).where(
                and_(
                    XMLStream.id == stream_id,
                    XMLStream.created_by == user_id
                )
            )
            
            result = await session.execute(query)
            existing_stream = result.scalar_one_or_none()
            
            if not existing_stream:
                return None
            
            # Check if significant changes warrant a new version
            create_new_version = create_version and self._should_create_version(
                existing_stream, stream_update
            )
            
            # Update fields
            update_data = stream_update.dict(exclude_unset=True)
            
            if update_data:
                # Set last_generated_at if XML content changed
                if "xml_content" in update_data and update_data["xml_content"]:
                    update_data["last_generated_at"] = datetime.utcnow()
                
                # Increment version if creating new version
                if create_new_version:
                    update_data["version"] = existing_stream.version + 1
                
                await session.execute(
                    update(XMLStream)
                    .where(XMLStream.id == stream_id)
                    .values(**update_data)
                )
            
            # Create new version if warranted
            if create_new_version:
                await self._create_version(
                    session,
                    stream_id,
                    existing_stream.version + 1,
                    stream_update.wizard_data if hasattr(stream_update, 'wizard_data') else existing_stream.wizard_data,
                    stream_update.xml_content if hasattr(stream_update, 'xml_content') else existing_stream.xml_content,
                    f"Update: {', '.join(update_data.keys())}"
                )
            
            await session.commit()
            
            # Return updated stream
            return await self.get_stream_by_id(stream_id, user_id)
            
        except Exception as e:
            logger.error(f"Error updating stream {stream_id}: {str(e)}")
            raise
    
    async def delete_stream(
        self, 
        stream_id: UUID, 
        user_id: str = "anonymous"
    ) -> bool:
        """Delete a stream and all its versions"""
        try:
            session = await self.get_session()
            
            # Check if stream exists and belongs to user
            query = select(XMLStream).where(
                and_(
                    XMLStream.id == stream_id,
                    XMLStream.created_by == user_id
                )
            )
            
            result = await session.execute(query)
            stream = result.scalar_one_or_none()
            
            if not stream:
                return False
            
            # Delete stream (versions will be cascade deleted)
            await session.execute(
                delete(XMLStream).where(XMLStream.id == stream_id)
            )
            
            await session.commit()
            
            logger.info(f"Deleted XML stream: {stream.stream_name} (ID: {stream_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting stream {stream_id}: {str(e)}")
            raise
    
    async def list_streams(
        self,
        user_id: str = "anonymous",
        filters: Optional[StreamFilters] = None,
        sort_by: StreamSortBy = StreamSortBy.UPDATED_DESC,
        limit: int = 50,
        offset: int = 0
    ) -> XMLStreamListResponse:
        """List streams with filtering and sorting"""
        try:
            session = await self.get_session()
            
            # Base query
            query = select(XMLStream).where(XMLStream.created_by == user_id)
            
            # Apply filters
            if filters:
                if filters.search:
                    search_term = f"%{filters.search}%"
                    query = query.where(
                        or_(
                            XMLStream.stream_name.ilike(search_term),
                            XMLStream.description.ilike(search_term)
                        )
                    )
                
                if filters.job_types:
                    query = query.where(XMLStream.job_type.in_(filters.job_types))
                
                if filters.statuses:
                    query = query.where(XMLStream.status.in_(filters.statuses))
                
                if filters.tags:
                    for tag in filters.tags:
                        query = query.where(XMLStream.tags.any(tag))
                
                if filters.is_favorite is not None:
                    query = query.where(XMLStream.is_favorite == filters.is_favorite)
                
                if filters.created_after:
                    query = query.where(XMLStream.created_at >= filters.created_after)
                
                if filters.created_before:
                    query = query.where(XMLStream.created_at <= filters.created_before)
            
            # Apply sorting
            if sort_by == StreamSortBy.UPDATED_DESC:
                query = query.order_by(desc(XMLStream.updated_at))
            elif sort_by == StreamSortBy.UPDATED_ASC:
                query = query.order_by(asc(XMLStream.updated_at))
            elif sort_by == StreamSortBy.CREATED_DESC:
                query = query.order_by(desc(XMLStream.created_at))
            elif sort_by == StreamSortBy.CREATED_ASC:
                query = query.order_by(asc(XMLStream.created_at))
            elif sort_by == StreamSortBy.NAME_ASC:
                query = query.order_by(asc(XMLStream.stream_name))
            elif sort_by == StreamSortBy.NAME_DESC:
                query = query.order_by(desc(XMLStream.stream_name))
            elif sort_by == StreamSortBy.FAVORITES_FIRST:
                query = query.order_by(desc(XMLStream.is_favorite), desc(XMLStream.updated_at))
            
            # Get total count
            count_query = select(func.count(XMLStream.id)).where(XMLStream.created_by == user_id)
            if filters:
                # Apply same filters to count query
                if filters.search:
                    search_term = f"%{filters.search}%"
                    count_query = count_query.where(
                        or_(
                            XMLStream.stream_name.ilike(search_term),
                            XMLStream.description.ilike(search_term)
                        )
                    )
                # ... apply other filters similarly
            
            total_result = await session.execute(count_query)
            total_count = total_result.scalar()
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            # Execute query
            result = await session.execute(query)
            streams = result.scalars().all()
            
            # Convert to response models
            stream_responses = [XMLStreamResponse.from_orm(stream) for stream in streams]
            
            return XMLStreamListResponse(
                streams=stream_responses,
                total_count=total_count,
                limit=limit,
                offset=offset,
                has_more=offset + limit < total_count
            )
            
        except Exception as e:
            logger.error(f"Error listing streams: {str(e)}")
            raise
    
    async def duplicate_stream(
        self,
        stream_id: UUID,
        user_id: str = "anonymous",
        new_name: Optional[str] = None
    ) -> Optional[XMLStreamResponse]:
        """Duplicate an existing stream"""
        try:
            # Get original stream
            original = await self.get_stream_by_id(stream_id, user_id)
            if not original:
                return None
            
            # Create new stream data
            duplicate_name = new_name or f"{original.stream_name} (Kopie)"
            
            create_data = XMLStreamCreate(
                stream_name=duplicate_name,
                description=f"Kopie von: {original.description}" if original.description else None,
                xml_content=original.xml_content,
                wizard_data=original.wizard_data,
                job_type=original.job_type,
                status="draft",  # Always start as draft
                tags=original.tags,
                is_favorite=False  # Don't inherit favorite status
            )
            
            return await self.create_stream(create_data, user_id)
            
        except Exception as e:
            logger.error(f"Error duplicating stream {stream_id}: {str(e)}")
            raise
    
    async def toggle_favorite(
        self,
        stream_id: UUID,
        user_id: str = "anonymous"
    ) -> Optional[XMLStreamResponse]:
        """Toggle favorite status of a stream"""
        try:
            session = await self.get_session()
            
            # Get current stream
            stream = await self.get_stream_by_id(stream_id, user_id)
            if not stream:
                return None
            
            # Toggle favorite
            new_favorite_status = not stream.is_favorite
            
            await session.execute(
                update(XMLStream)
                .where(XMLStream.id == stream_id)
                .values(is_favorite=new_favorite_status)
            )
            
            await session.commit()
            
            return await self.get_stream_by_id(stream_id, user_id)
            
        except Exception as e:
            logger.error(f"Error toggling favorite for stream {stream_id}: {str(e)}")
            raise
    
    async def create_stream_from_conversation_data(
        self,
        job_type: str,
        collected_data: Dict[str, Any],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Create an XML stream from conversation-collected data

        Args:
            job_type: Job type string (sap, file_transfer, standard)
            collected_data: Data collected through conversation
            user_id: User creating the stream

        Returns:
            Dictionary with stream_id and xml_content
        """
        try:
            logger.info(f"🔄 Creating {job_type} stream from conversation data...")

            # Transform conversation data to wizard format
            wizard_data = await self._transform_conversation_data_to_wizard_format(
                job_type, collected_data
            )

            # Generate XML content
            xml_content = await self._generate_xml_from_wizard_data(wizard_data, job_type)

            # Extract stream name
            stream_name = (
                collected_data.get("streamProperties", {}).get("streamName") or
                collected_data.get("stream_name") or
                f"{job_type}_Stream_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            )

            # Generate description
            description = self._generate_description(job_type, collected_data)

            # Create stream data
            create_data = XMLStreamCreate(
                stream_name=stream_name,
                description=description,
                xml_content=xml_content,
                wizard_data=wizard_data,
                job_type=job_type,
                status="konfiguration",
                tags=collected_data.get("tags", []),
                is_favorite=False
            )

            # Create stream using existing create_stream method
            stream_response = await self.create_stream(create_data, user_id)

            logger.info(f"✅ Stream created successfully: {stream_response.id}")

            return {
                "stream_id": str(stream_response.id),
                "stream_name": stream_response.stream_name,
                "xml_content": stream_response.xml_content,
                "wizard_data": stream_response.wizard_data,
                "status": stream_response.status,
                "created_at": stream_response.created_at.isoformat() if stream_response.created_at else datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Failed to create stream from conversation data: {str(e)}")
            raise Exception(f"Stream creation failed: {str(e)}")

    async def _transform_conversation_data_to_wizard_format(
        self,
        job_type: str,
        collected_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform conversation-collected data to wizard format"""
        logger.info("🔄 Transforming conversation data to wizard format...")

        # Initialize wizard data structure
        wizard_data = {
            "jobType": job_type,
            "streamProperties": {
                "streamName": collected_data.get("streamProperties", {}).get("streamName", ""),
                "description": collected_data.get("description", ""),
                "environment": collected_data.get("environment", "TEST")
            },
            "jobForm": {},
            "scheduling": {
                "enabled": True,
                "startTime": collected_data.get("scheduling", {}).get("startTime", "06:00"),
                "frequency": collected_data.get("scheduling", {}).get("frequency", "daily")
            }
        }

        # Job-type specific transformations
        if job_type == "sap":
            wizard_data["jobForm"] = {
                "sapSystem": collected_data.get("jobForm", {}).get("sapSystem", ""),
                "reportName": collected_data.get("jobForm", {}).get("reportName", ""),
                "variant": collected_data.get("jobForm", {}).get("variant", ""),
                "parameters": collected_data.get("jobForm", {}).get("parameters", {})
            }
        elif job_type == "file_transfer":
            wizard_data["jobForm"] = {
                "sourcePath": collected_data.get("jobForm", {}).get("sourcePath", ""),
                "targetPath": collected_data.get("jobForm", {}).get("targetPath", ""),
                "sourceServer": collected_data.get("jobForm", {}).get("sourceServer", ""),
                "targetServer": collected_data.get("jobForm", {}).get("targetServer", ""),
                "transferType": collected_data.get("jobForm", {}).get("transferType", "COPY")
            }
        elif job_type == "standard":
            wizard_data["jobForm"] = {
                "scriptPath": collected_data.get("jobForm", {}).get("scriptPath", ""),
                "agentName": collected_data.get("jobForm", {}).get("agentName", ""),
                "workingDirectory": collected_data.get("jobForm", {}).get("workingDirectory", ""),
                "arguments": collected_data.get("jobForm", {}).get("arguments", "")
            }

        return wizard_data

    async def _generate_xml_from_wizard_data(
        self,
        wizard_data: Dict[str, Any],
        job_type: str
    ) -> str:
        """Generate XML content from wizard data"""
        logger.info("🔄 Generating XML from wizard data...")

        try:
            # Try to import existing XML generation logic
            from services.xml_template_engine import XMLTemplateEngine

            xml_engine = XMLTemplateEngine()
            xml_result = xml_engine.generate_xml(wizard_data, job_type)

            if xml_result.get("success"):
                return xml_result.get("xml_content", "")
            else:
                raise Exception(f"XML generation failed: {xml_result.get('error', 'Unknown error')}")

        except ImportError:
            # Fallback: Generate basic XML structure
            logger.warning("⚠️ XML Template Engine not available, using fallback XML generation")
            return self._generate_fallback_xml(wizard_data, job_type)
        except Exception as e:
            logger.error(f"❌ XML generation failed: {str(e)}")
            return self._generate_fallback_xml(wizard_data, job_type)

    def _generate_fallback_xml(
        self,
        wizard_data: Dict[str, Any],
        job_type: str
    ) -> str:
        """Generate basic XML structure as fallback"""
        stream_name = wizard_data.get("streamProperties", {}).get("streamName", "ConversationStream")

        if job_type == "sap":
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<stream>
    <name>{stream_name}</name>
    <type>SAP</type>
    <job>
        <sapSystem>{wizard_data.get('jobForm', {}).get('sapSystem', '')}</sapSystem>
        <reportName>{wizard_data.get('jobForm', {}).get('reportName', '')}</reportName>
    </job>
    <schedule>
        <time>{wizard_data.get('scheduling', {}).get('startTime', '06:00')}</time>
        <frequency>{wizard_data.get('scheduling', {}).get('frequency', 'daily')}</frequency>
    </schedule>
</stream>"""
        elif job_type == "file_transfer":
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<stream>
    <name>{stream_name}</name>
    <type>FILE_TRANSFER</type>
    <job>
        <sourcePath>{wizard_data.get('jobForm', {}).get('sourcePath', '')}</sourcePath>
        <targetPath>{wizard_data.get('jobForm', {}).get('targetPath', '')}</targetPath>
    </job>
    <schedule>
        <time>{wizard_data.get('scheduling', {}).get('startTime', '06:00')}</time>
        <frequency>{wizard_data.get('scheduling', {}).get('frequency', 'daily')}</frequency>
    </schedule>
</stream>"""
        else:  # standard
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<stream>
    <name>{stream_name}</name>
    <type>STANDARD</type>
    <job>
        <scriptPath>{wizard_data.get('jobForm', {}).get('scriptPath', '')}</scriptPath>
        <agentName>{wizard_data.get('jobForm', {}).get('agentName', '')}</agentName>
    </job>
    <schedule>
        <time>{wizard_data.get('scheduling', {}).get('startTime', '06:00')}</time>
        <frequency>{wizard_data.get('scheduling', {}).get('frequency', 'daily')}</frequency>
    </schedule>
</stream>"""

    def _generate_description(
        self,
        job_type: str,
        collected_data: Dict[str, Any]
    ) -> str:
        """Generate descriptive text for the stream"""
        if job_type == "sap":
            sap_system = collected_data.get("jobForm", {}).get("sapSystem", "")
            report_name = collected_data.get("jobForm", {}).get("reportName", "")
            return f"SAP Stream für System {sap_system} Report {report_name}"
        elif job_type == "file_transfer":
            source = collected_data.get("jobForm", {}).get("sourcePath", "")
            target = collected_data.get("jobForm", {}).get("targetPath", "")
            return f"File Transfer von {source} nach {target}"
        elif job_type == "standard":
            script = collected_data.get("jobForm", {}).get("scriptPath", "")
            agent = collected_data.get("jobForm", {}).get("agentName", "")
            return f"Standard Job: {script} auf Agent {agent}"
        return f"{job_type} Stream erstellt über Conversational AI"

    async def auto_save_stream(
        self,
        stream_id: UUID,
        wizard_data: Optional[Dict[str, Any]] = None,
        xml_content: Optional[str] = None,
        user_id: str = "anonymous"
    ) -> Optional[XMLStreamResponse]:
        """Auto-save stream data (lightweight updates without versioning)"""
        try:
            update_data = XMLStreamUpdate()

            if wizard_data is not None:
                update_data.wizard_data = wizard_data

            if xml_content is not None:
                update_data.xml_content = xml_content

            # Auto-save without creating versions
            return await self.update_stream(
                stream_id,
                update_data,
                user_id,
                create_version=False
            )

        except Exception as e:
            logger.error(f"Error auto-saving stream {stream_id}: {str(e)}")
            raise
    
    async def _create_version(
        self,
        session: AsyncSession,
        stream_id: UUID,
        version: int,
        wizard_data: Optional[Dict[str, Any]],
        xml_content: Optional[str],
        changes_description: str
    ):
        """Create a new version entry"""
        try:
            new_version = StreamVersion(
                id=uuid4(),
                stream_id=stream_id,
                version=version,
                wizard_data=wizard_data,
                xml_content=xml_content,
                changes_description=changes_description
            )
            
            session.add(new_version)
            
        except Exception as e:
            logger.error(f"Error creating version for stream {stream_id}: {str(e)}")
            raise
    
    def _should_create_version(
        self, 
        existing_stream: XMLStream, 
        update_data: XMLStreamUpdate
    ) -> bool:
        """Determine if changes warrant a new version"""
        # Create version for significant changes
        if hasattr(update_data, 'xml_content') and update_data.xml_content:
            return update_data.xml_content != existing_stream.xml_content
        
        if hasattr(update_data, 'wizard_data') and update_data.wizard_data:
            return update_data.wizard_data != existing_stream.wizard_data
        
        if hasattr(update_data, 'job_type') and update_data.job_type:
            return update_data.job_type != existing_stream.job_type
        
        return False


# Dependency injection
async def get_xml_stream_service() -> XMLStreamService:
    """Get XML Stream Service dependency"""
    return XMLStreamService()