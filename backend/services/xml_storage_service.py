"""
XML Storage Service
Handles dual storage of generated XMLs: Supabase DB + Local Filesystem
"""

import os
import json
import logging
import aiofiles
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from database import get_supabase_client

logger = logging.getLogger(__name__)


class GeneratedXML(BaseModel):
    """Pydantic model for generated XML record"""

    id: UUID
    session_id: str
    stream_name: str
    job_type: str
    xml_content: str
    parameters_used: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    version: int = 1
    file_path: Optional[str] = None
    file_size: Optional[int] = None


class XMLStorageRequest(BaseModel):
    """Request model for storing XML"""

    session_id: str
    stream_name: str
    job_type: str
    xml_content: str
    parameters_used: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None


class XMLStorageService:
    """
    🗄️ XML Storage Service

    Handles dual storage strategy:
    - Supabase PostgreSQL: Full XML + metadata for persistence
    - Local Filesystem: Quick file access for downloads/exports

    Features:
    - Automatic versioning for multiple generations
    - Cleanup of old local files
    - Deduplication based on parameters
    - Fast retrieval by session or XML ID
    """

    def __init__(self):
        """Initialize XML Storage Service"""

        # Supabase client
        self.supabase = get_supabase_client()

        # Local storage configuration
        self.base_path = Path(__file__).parent.parent / "generated_xmls"
        self.ensure_directories()

        # Storage settings
        self.local_retention_days = 7  # Keep local files for 7 days
        self.max_file_size = 10 * 1024 * 1024  # 10MB max per XML

        logger.info(f"🗄️ XMLStorageService initialized")
        logger.info(f"📁 Local storage: {self.base_path}")

    def ensure_directories(self):
        """Ensure all required directories exist"""

        # Create base directory
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create current month directory
        current_date = datetime.now()
        month_path = self.base_path / f"{current_date.year}-{current_date.month:02d}"
        month_path.mkdir(exist_ok=True)

        # Create daily directory
        day_path = month_path / f"{current_date.day:02d}"
        day_path.mkdir(exist_ok=True)

        logger.debug(f"📁 Ensured directory structure: {day_path}")

    async def store_xml(self, request: XMLStorageRequest) -> GeneratedXML:
        """
        🗄️ Store XML in both Supabase and local filesystem

        Args:
            request: XMLStorageRequest with all required data

        Returns:
            GeneratedXML record with storage information
        """

        try:
            logger.info(f"🗄️ Storing XML for session: {request.session_id}")

            # Check for existing XML with same parameters to avoid duplicates
            existing_xml = await self._check_duplicate(request)
            if existing_xml:
                logger.info(f"♻️ Found existing XML with same parameters: {existing_xml.id}")
                return existing_xml

            # Determine version number
            version = await self._get_next_version(request.session_id)

            # Generate file path
            file_path = self._generate_file_path(request.stream_name, version)

            # Store locally first (faster rollback if needed)
            local_path = await self._store_locally(request.xml_content, file_path)

            # Calculate file size
            file_size = len(request.xml_content.encode('utf-8'))

            # Prepare metadata
            storage_metadata = {
                **request.metadata,
                "storage_timestamp": datetime.now().isoformat(),
                "template_engine": "Jinja2",
                "xml_size": file_size,
                "local_path": str(local_path)
            }

            # Store in Supabase
            xml_record = await self._store_in_supabase(
                request=request,
                version=version,
                file_path=str(local_path),
                file_size=file_size,
                metadata=storage_metadata
            )

            logger.info(f"✅ XML stored successfully: DB={xml_record.id}, File={local_path}")
            return xml_record

        except Exception as e:
            logger.error(f"❌ Failed to store XML: {str(e)}")
            raise RuntimeError(f"XML storage failed: {str(e)}")

    async def get_xml_by_id(self, xml_id: UUID) -> Optional[GeneratedXML]:
        """Get XML by its ID"""

        try:
            response = self.supabase.table("generated_xmls").select("*").eq("id", str(xml_id)).execute()

            if response.data:
                return GeneratedXML(**response.data[0])
            return None

        except Exception as e:
            logger.error(f"❌ Failed to get XML by ID {xml_id}: {str(e)}")
            return None

    async def get_xmls_by_session(self, session_id: str) -> List[GeneratedXML]:
        """Get all XMLs for a session"""

        try:
            response = self.supabase.table("generated_xmls").select("*").eq("session_id", session_id).order("created_at", desc=True).execute()

            return [GeneratedXML(**record) for record in response.data]

        except Exception as e:
            logger.error(f"❌ Failed to get XMLs for session {session_id}: {str(e)}")
            return []

    async def get_recent_xmls(self, limit: int = 20) -> List[GeneratedXML]:
        """Get recently generated XMLs"""

        try:
            response = self.supabase.table("generated_xmls").select("*").order("created_at", desc=True).limit(limit).execute()

            return [GeneratedXML(**record) for record in response.data]

        except Exception as e:
            logger.error(f"❌ Failed to get recent XMLs: {str(e)}")
            return []

    async def get_local_file_content(self, xml_id: UUID) -> Optional[str]:
        """Get XML content from local file"""

        try:
            # Get record to find file path
            xml_record = await self.get_xml_by_id(xml_id)
            if not xml_record or not xml_record.file_path:
                return None

            # Read from local file
            file_path = Path(xml_record.file_path)
            if file_path.exists():
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    return await f.read()
            else:
                # Fallback to database content
                logger.warning(f"⚠️ Local file not found: {file_path}, using DB content")
                return xml_record.xml_content

        except Exception as e:
            logger.error(f"❌ Failed to get local file content: {str(e)}")
            return None

    async def delete_xml(self, xml_id: UUID) -> bool:
        """Delete XML from both storage locations"""

        try:
            # Get record first
            xml_record = await self.get_xml_by_id(xml_id)
            if not xml_record:
                return False

            # Delete local file
            if xml_record.file_path:
                file_path = Path(xml_record.file_path)
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"🗑️ Deleted local file: {file_path}")

            # Delete from database
            response = self.supabase.table("generated_xmls").delete().eq("id", str(xml_id)).execute()

            logger.info(f"✅ Deleted XML: {xml_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete XML {xml_id}: {str(e)}")
            return False

    async def cleanup_old_files(self):
        """Clean up old local files based on retention policy"""

        try:
            cutoff_date = datetime.now() - timedelta(days=self.local_retention_days)
            deleted_count = 0

            for file_path in self.base_path.rglob("*.xml"):
                try:
                    file_stat = file_path.stat()
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)

                    if file_date < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1

                except Exception as e:
                    logger.warning(f"⚠️ Failed to delete old file {file_path}: {e}")

            logger.info(f"🧹 Cleaned up {deleted_count} old XML files")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {str(e)}")
            return 0

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""

        try:
            # Database stats
            db_response = self.supabase.table("generated_xmls").select("id", count="exact").execute()
            total_xmls = db_response.count if hasattr(db_response, 'count') else len(db_response.data)

            # Local storage stats
            local_files = list(self.base_path.rglob("*.xml"))
            total_local_files = len(local_files)
            total_local_size = sum(f.stat().st_size for f in local_files if f.exists())

            return {
                "total_xmls_in_db": total_xmls,
                "total_local_files": total_local_files,
                "total_local_size_bytes": total_local_size,
                "total_local_size_mb": round(total_local_size / (1024 * 1024), 2),
                "base_path": str(self.base_path),
                "retention_days": self.local_retention_days
            }

        except Exception as e:
            logger.error(f"❌ Failed to get storage stats: {str(e)}")
            return {}

    # Private methods

    async def _check_duplicate(self, request: XMLStorageRequest) -> Optional[GeneratedXML]:
        """Check if XML with same parameters already exists"""

        try:
            # Compare based on session_id, job_type, and key parameters
            response = self.supabase.table("generated_xmls").select("*").eq("session_id", request.session_id).eq("job_type", request.job_type).order("created_at", desc=True).limit(5).execute()

            for record in response.data:
                existing_params = record.get("parameters_used", {})

                # Simple comparison of key parameters
                if self._params_similar(existing_params, request.parameters_used):
                    return GeneratedXML(**record)

            return None

        except Exception as e:
            logger.warning(f"⚠️ Duplicate check failed: {e}")
            return None

    def _params_similar(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> bool:
        """Check if two parameter sets are similar enough to be considered duplicates"""

        # Key parameters that must match exactly
        key_params = ['stream_name', 'source_agent', 'target_agent', 'sap_system', 'main_script']

        for param in key_params:
            if param in params1 and param in params2:
                if params1[param] != params2[param]:
                    return False

        return True

    async def _get_next_version(self, session_id: str) -> int:
        """Get next version number for this session"""

        try:
            response = self.supabase.table("generated_xmls").select("version").eq("session_id", session_id).order("version", desc=True).limit(1).execute()

            if response.data:
                return response.data[0]["version"] + 1
            return 1

        except Exception as e:
            logger.warning(f"⚠️ Version check failed: {e}")
            return 1

    def _generate_file_path(self, stream_name: str, version: int) -> str:
        """Generate local file path for XML"""

        # Clean stream name for filesystem
        safe_name = "".join(c for c in stream_name if c.isalnum() or c in ['_', '-', '.']).rstrip()
        if not safe_name:
            safe_name = "stream"

        # Create path with date structure
        now = datetime.now()
        date_path = f"{now.year}-{now.month:02d}/{now.day:02d}"

        # Generate filename with timestamp and version
        timestamp = now.strftime("%H%M%S")
        filename = f"{safe_name}_v{version}_{timestamp}.xml"

        return str(self.base_path / date_path / filename)

    async def _store_locally(self, xml_content: str, file_path: str) -> Path:
        """Store XML content to local filesystem"""

        local_path = Path(file_path)

        # Ensure directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        async with aiofiles.open(local_path, 'w', encoding='utf-8') as f:
            await f.write(xml_content)

        logger.debug(f"📁 Stored locally: {local_path}")
        return local_path

    async def _store_in_supabase(
        self,
        request: XMLStorageRequest,
        version: int,
        file_path: str,
        file_size: int,
        metadata: Dict[str, Any]
    ) -> GeneratedXML:
        """Store XML record in Supabase"""

        record_data = {
            "session_id": request.session_id,
            "stream_name": request.stream_name,
            "job_type": request.job_type,
            "xml_content": request.xml_content,
            "parameters_used": request.parameters_used,
            "metadata": metadata,
            "user_id": request.user_id,
            "version": version,
            "file_path": file_path,
            "file_size": file_size
        }

        response = self.supabase.table("generated_xmls").insert(record_data).execute()

        if not response.data:
            raise RuntimeError("Failed to insert XML record into database")

        return GeneratedXML(**response.data[0])


# Singleton instance
_xml_storage_service: Optional[XMLStorageService] = None

def get_xml_storage_service() -> XMLStorageService:
    """Get singleton XMLStorageService instance"""
    global _xml_storage_service

    if _xml_storage_service is None:
        _xml_storage_service = XMLStorageService()

    return _xml_storage_service