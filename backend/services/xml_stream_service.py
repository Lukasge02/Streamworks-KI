"""
XMLStreamService - Business logic for XML Stream management
Handles CRUD operations, filtering, and stream workflow management
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from models.core import XMLStream, XMLStreamStatus, JobType
from schemas.xml_streams import (
    XMLStreamCreate, XMLStreamUpdate, XMLStreamResponse,
    XMLStreamListResponse, StreamFilters
)

logger = logging.getLogger(__name__)


class XMLStreamService:
    """Service class for XML Stream operations"""

    @staticmethod
    async def create_stream(
        db: AsyncSession,
        stream_data: XMLStreamCreate
    ) -> XMLStream:
        """
        Create a new XML stream
        """
        try:
            # Create new stream instance
            db_stream = XMLStream(
                stream_name=stream_data.stream_name,
                description=stream_data.description,
                job_type=stream_data.job_type or "standard",
                status=stream_data.status or "draft",
                wizard_data=stream_data.wizard_data or {},
                xml_content=stream_data.xml_content,
                created_by=stream_data.created_by or "system",
                tags=stream_data.tags or [],
                is_favorite=stream_data.is_favorite or False,
                template_id=stream_data.template_id
            )

            db.add(db_stream)
            await db.commit()
            await db.refresh(db_stream)

            logger.info(f"✅ Created XML stream: {db_stream.stream_name} (ID: {db_stream.id})")
            return db_stream

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to create XML stream: {str(e)}")
            raise

    @staticmethod
    async def get_stream(db: AsyncSession, stream_id: str) -> Optional[XMLStream]:
        """
        Get a single XML stream by ID
        """
        try:
            query = select(XMLStream).where(XMLStream.id == stream_id)
            result = await db.execute(query)
            stream = result.scalar_one_or_none()

            if stream:
                logger.debug(f"📄 Retrieved stream: {stream.stream_name}")
            else:
                logger.warning(f"⚠️ Stream not found: {stream_id}")

            return stream

        except Exception as e:
            logger.error(f"❌ Failed to get stream {stream_id}: {str(e)}")
            raise

    @staticmethod
    async def list_streams(
        db: AsyncSession,
        filters: StreamFilters,
        sort_by: str = "updated_desc",
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[XMLStream], int]:
        """
        List XML streams with filtering, sorting, and pagination
        Returns (streams, total_count)
        """
        try:
            # Base query
            query = select(XMLStream)
            count_query = select(func.count(XMLStream.id))

            # Apply filters
            filter_conditions = []

            if filters.search:
                search_term = f"%{filters.search}%"
                filter_conditions.append(
                    or_(
                        XMLStream.stream_name.ilike(search_term),
                        XMLStream.description.ilike(search_term)
                    )
                )

            if filters.job_types:
                filter_conditions.append(XMLStream.job_type.in_(filters.job_types))

            if filters.statuses:
                filter_conditions.append(XMLStream.status.in_(filters.statuses))

            if filters.tags:
                # PostgreSQL array overlap operator
                for tag in filters.tags:
                    filter_conditions.append(XMLStream.tags.contains([tag]))

            if filters.is_favorite is not None:
                filter_conditions.append(XMLStream.is_favorite == filters.is_favorite)

            if filters.created_after:
                filter_conditions.append(XMLStream.created_at >= filters.created_after)

            if filters.created_before:
                filter_conditions.append(XMLStream.created_at <= filters.created_before)

            # Apply filters to queries
            if filter_conditions:
                query = query.where(and_(*filter_conditions))
                count_query = count_query.where(and_(*filter_conditions))

            # Apply sorting
            if sort_by == "updated_desc":
                query = query.order_by(desc(XMLStream.updated_at))
            elif sort_by == "updated_asc":
                query = query.order_by(asc(XMLStream.updated_at))
            elif sort_by == "created_desc":
                query = query.order_by(desc(XMLStream.created_at))
            elif sort_by == "created_asc":
                query = query.order_by(asc(XMLStream.created_at))
            elif sort_by == "name_asc":
                query = query.order_by(asc(XMLStream.stream_name))
            elif sort_by == "name_desc":
                query = query.order_by(desc(XMLStream.stream_name))
            elif sort_by == "favorites_first":
                query = query.order_by(desc(XMLStream.is_favorite), desc(XMLStream.updated_at))

            # Get total count
            count_result = await db.execute(count_query)
            total_count = count_result.scalar()

            # Apply pagination
            query = query.offset(offset).limit(limit)

            # Execute query
            result = await db.execute(query)
            streams = result.scalars().all()

            logger.debug(f"📋 Listed {len(streams)} streams (total: {total_count})")
            return list(streams), total_count

        except Exception as e:
            logger.error(f"❌ Failed to list streams: {str(e)}")
            raise

    @staticmethod
    async def update_stream(
        db: AsyncSession,
        stream_id: str,
        stream_data: XMLStreamUpdate
    ) -> Optional[XMLStream]:
        """
        Update an existing XML stream
        """
        try:
            # Get existing stream
            query = select(XMLStream).where(XMLStream.id == stream_id)
            result = await db.execute(query)
            db_stream = result.scalar_one_or_none()

            if not db_stream:
                logger.warning(f"⚠️ Stream not found for update: {stream_id}")
                return None

            # Update fields if provided
            update_data = stream_data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(db_stream, field, value)

            # Update timestamp
            db_stream.updated_at = datetime.utcnow()

            # If XML content was updated, update generation timestamp
            if "xml_content" in update_data and update_data["xml_content"]:
                db_stream.last_generated_at = datetime.utcnow()

            # Version increment logic (if needed)
            if "xml_content" in update_data or "wizard_data" in update_data:
                db_stream.version += 1

            await db.commit()
            await db.refresh(db_stream)

            logger.info(f"✅ Updated XML stream: {db_stream.stream_name} (ID: {stream_id})")
            return db_stream

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to update stream {stream_id}: {str(e)}")
            raise

    @staticmethod
    async def delete_stream(db: AsyncSession, stream_id: str) -> bool:
        """
        Delete an XML stream
        """
        try:
            query = select(XMLStream).where(XMLStream.id == stream_id)
            result = await db.execute(query)
            db_stream = result.scalar_one_or_none()

            if not db_stream:
                logger.warning(f"⚠️ Stream not found for deletion: {stream_id}")
                return False

            stream_name = db_stream.stream_name
            await db.delete(db_stream)
            await db.commit()

            logger.info(f"🗑️ Deleted XML stream: {stream_name} (ID: {stream_id})")
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to delete stream {stream_id}: {str(e)}")
            raise

    @staticmethod
    async def toggle_favorite(db: AsyncSession, stream_id: str) -> Optional[XMLStream]:
        """
        Toggle the favorite status of a stream
        """
        try:
            query = select(XMLStream).where(XMLStream.id == stream_id)
            result = await db.execute(query)
            db_stream = result.scalar_one_or_none()

            if not db_stream:
                logger.warning(f"⚠️ Stream not found for favorite toggle: {stream_id}")
                return None

            # Toggle favorite status
            db_stream.is_favorite = not db_stream.is_favorite
            db_stream.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(db_stream)

            status = "added to" if db_stream.is_favorite else "removed from"
            logger.info(f"⭐ Stream {status} favorites: {db_stream.stream_name}")
            return db_stream

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to toggle favorite for stream {stream_id}: {str(e)}")
            raise

    @staticmethod
    async def duplicate_stream(
        db: AsyncSession,
        stream_id: str,
        new_name: str
    ) -> Optional[XMLStream]:
        """
        Create a duplicate of an existing stream
        """
        try:
            # Get original stream
            query = select(XMLStream).where(XMLStream.id == stream_id)
            result = await db.execute(query)
            original_stream = result.scalar_one_or_none()

            if not original_stream:
                logger.warning(f"⚠️ Stream not found for duplication: {stream_id}")
                return None

            # Create duplicate
            duplicate_stream = XMLStream(
                stream_name=new_name,
                description=original_stream.description,
                xml_content=original_stream.xml_content,
                wizard_data=original_stream.wizard_data,
                job_type=original_stream.job_type,
                status="draft",  # Always start as draft
                created_by=original_stream.created_by,
                tags=original_stream.tags.copy() if original_stream.tags else [],
                is_favorite=False,  # Don't copy favorite status
                template_id=original_stream.template_id,
                version=1  # Reset version
            )

            db.add(duplicate_stream)
            await db.commit()
            await db.refresh(duplicate_stream)

            logger.info(f"📋 Duplicated stream: {original_stream.stream_name} -> {new_name}")
            return duplicate_stream

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to duplicate stream {stream_id}: {str(e)}")
            raise

    @staticmethod
    async def bulk_delete_streams(db: AsyncSession, stream_ids: List[str]) -> int:
        """
        Delete multiple streams in bulk
        Returns the number of deleted streams
        """
        try:
            query = select(XMLStream).where(XMLStream.id.in_(stream_ids))
            result = await db.execute(query)
            streams_to_delete = result.scalars().all()

            deleted_count = 0
            for stream in streams_to_delete:
                await db.delete(stream)
                deleted_count += 1

            await db.commit()

            logger.info(f"🗑️ Bulk deleted {deleted_count} streams")
            return deleted_count

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to bulk delete streams: {str(e)}")
            raise

    @staticmethod
    async def bulk_toggle_favorite(db: AsyncSession, stream_ids: List[str]) -> int:
        """
        Toggle favorite status for multiple streams
        Returns the number of updated streams
        """
        try:
            query = select(XMLStream).where(XMLStream.id.in_(stream_ids))
            result = await db.execute(query)
            streams = result.scalars().all()

            updated_count = 0
            for stream in streams:
                stream.is_favorite = not stream.is_favorite
                stream.updated_at = datetime.utcnow()
                updated_count += 1

            await db.commit()

            logger.info(f"⭐ Bulk toggled favorites for {updated_count} streams")
            return updated_count

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to bulk toggle favorites: {str(e)}")
            raise