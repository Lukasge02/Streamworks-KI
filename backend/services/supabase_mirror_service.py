"""
Supabase Mirror Service
Mirrors document metadata and chunk information to Supabase for analytics and backup
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class SupabaseMirrorService:
    """
    Service for mirroring document metadata and chunks to Supabase
    Provides analytics and backup capabilities for the RAG system
    """

    def __init__(self):
        self.enabled = False
        self.supabase_client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Supabase client if credentials are available"""
        try:
            from supabase import create_client
            import os

            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

            if supabase_url and supabase_key:
                self.supabase_client = create_client(supabase_url, supabase_key)
                self.enabled = True
                logger.info("✅ Supabase mirror service initialized successfully")
            else:
                logger.info("🔒 Supabase credentials not found - mirror service disabled")

        except ImportError:
            logger.info("📦 Supabase client not installed - mirror service disabled")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Supabase client: {str(e)}")

    async def mirror_document_stats(
        self,
        document_id: str,
        chunk_count: int,
        processing_metadata: Dict[str, Any],
        retry_count: int = 3
    ) -> bool:
        """
        Mirror enhanced document statistics to Supabase with retry logic

        Args:
            document_id: Document ID
            chunk_count: Number of chunks created
            processing_metadata: Processing metadata
            retry_count: Number of retry attempts

        Returns:
            Success status
        """
        if not self.enabled:
            logger.debug("Supabase mirror disabled - skipping document stats")
            return False

        for attempt in range(retry_count):
            try:
                # Prepare enhanced document stats data
                stats_data = {
                    "document_id": document_id,
                    "chunk_count": chunk_count,
                    "processing_engine": processing_metadata.get("processing_engine", "llamaindex"),
                    "embedding_model": processing_metadata.get("embedding_model", "BAAI/bge-base-en-v1.5"),
                    "processed_at": datetime.utcnow().isoformat(),
                    "status": "ready"
                }

                # Insert into correct Supabase table
                result = self.supabase_client.table("document_processing_stats").upsert(stats_data).execute()

                if result.data:
                    logger.info(f"📊 Enhanced document stats mirrored to Supabase: {document_id} ({chunk_count} chunks)")
                    return True
                else:
                    logger.warning(f"⚠️ No data returned from Supabase upsert (attempt {attempt + 1}): {document_id}")

            except Exception as e:
                logger.error(f"❌ Failed to mirror document stats to Supabase (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    return False

        return False

    async def mirror_chunk_metadata(
        self,
        chunks_data: List[Dict[str, Any]],
        document_id: str,
        retry_count: int = 3
    ) -> bool:
        """
        Mirror enhanced chunk metadata to Supabase with retry logic

        Args:
            chunks_data: List of chunk data with id, content, metadata
            document_id: Document ID
            retry_count: Number of retry attempts

        Returns:
            Success status
        """
        if not self.enabled:
            logger.debug("Supabase mirror disabled - skipping chunk metadata")
            return False

        for attempt in range(retry_count):
            try:
                # Prepare enhanced chunk metadata for Supabase
                chunk_metadata_list = []

                for i, chunk in enumerate(chunks_data):
                    metadata = chunk.get("metadata", {})
                    content = chunk.get("content", "")

                    # Enhanced metadata extraction
                    chunk_metadata = {
                        "chunk_id": chunk["id"],
                        "document_id": document_id,
                        "content_preview": content[:200] if content else "",
                        "word_count": metadata.get("word_count", len(content.split()) if content else 0),
                        "chunk_index": metadata.get("chunk_index", i),
                        "processing_status": "processed",
                        "sync_status": "synced",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    chunk_metadata_list.append(chunk_metadata)

                # Batch insert chunk metadata using the correct table name
                if chunk_metadata_list:
                    result = self.supabase_client.table("chunk_metadata_mirror").upsert(chunk_metadata_list).execute()

                    if result.data:
                        logger.info(f"📋 {len(chunk_metadata_list)} enhanced chunk metadata entries mirrored to Supabase")
                        return True
                    else:
                        logger.warning(f"⚠️ No data returned from Supabase chunk metadata upsert (attempt {attempt + 1})")
                else:
                    logger.info("📋 No chunk metadata to mirror")
                    return True

            except Exception as e:
                logger.error(f"❌ Failed to mirror chunk metadata to Supabase (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    return False

        return False

    async def mirror_document_deletion(self, document_id: str, retry_count: int = 3) -> bool:
        """
        Mirror document deletion to Supabase (cleanup) with retry logic

        Args:
            document_id: Document ID to delete
            retry_count: Number of retry attempts

        Returns:
            Success status
        """
        if not self.enabled:
            logger.debug("Supabase mirror disabled - skipping deletion cleanup")
            return False

        for attempt in range(retry_count):
            try:
                # Delete document stats from correct table
                stats_result = self.supabase_client.table("document_processing_stats").delete().eq("document_id", document_id).execute()

                # Delete chunk metadata from correct table
                chunks_result = self.supabase_client.table("chunk_metadata_mirror").delete().eq("document_id", document_id).execute()

                logger.info(f"🗑️ Document {document_id} cleanup mirrored to Supabase (attempt {attempt + 1})")
                return True

            except Exception as e:
                logger.error(f"❌ Failed to mirror document deletion to Supabase (attempt {attempt + 1}/{retry_count}): {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    return False

        return False

    async def get_document_analytics(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get enhanced document analytics from Supabase

        Args:
            document_id: Document ID

        Returns:
            Enhanced analytics data or None
        """
        if not self.enabled:
            return None

        try:
            # Get document stats
            stats_result = self.supabase_client.table("document_processing_stats").select("*").eq("document_id", document_id).execute()

            # Get chunk metadata summary
            chunks_result = self.supabase_client.table("chunk_metadata_mirror").select("chunk_id, word_count, chunk_index, processing_status").eq("document_id", document_id).execute()

            analytics = {}

            if stats_result.data:
                analytics["document_stats"] = stats_result.data[0]

            if chunks_result.data:
                analytics["chunk_summary"] = {
                    "total_chunks": len(chunks_result.data),
                    "total_words": sum(chunk.get("word_count", 0) for chunk in chunks_result.data),
                    "processing_status": [chunk.get("processing_status", "unknown") for chunk in chunks_result.data]
                }
                analytics["chunks"] = chunks_result.data

            return analytics if analytics else None

        except Exception as e:
            logger.error(f"❌ Failed to get enhanced document analytics from Supabase: {str(e)}")
            return None

    def is_enabled(self) -> bool:
        """Check if Supabase mirror service is enabled"""
        return self.enabled


# Global service instance
_supabase_mirror_service = None


def get_supabase_mirror_service() -> SupabaseMirrorService:
    """Get or create Supabase mirror service instance"""
    global _supabase_mirror_service

    if _supabase_mirror_service is None:
        _supabase_mirror_service = SupabaseMirrorService()

    return _supabase_mirror_service


# Enhanced convenience functions with reliability improvements
async def mirror_document_stats(document_id: str, chunk_count: int, processing_metadata: Dict[str, Any], retry_count: int = 3) -> bool:
    """Enhanced convenience function to mirror document stats with retry logic"""
    service = get_supabase_mirror_service()
    return await service.mirror_document_stats(document_id, chunk_count, processing_metadata, retry_count)


async def mirror_chunk_metadata(chunks_data: List[Dict[str, Any]], document_id: str, retry_count: int = 3) -> bool:
    """Enhanced convenience function to mirror chunk metadata with retry logic"""
    service = get_supabase_mirror_service()
    return await service.mirror_chunk_metadata(chunks_data, document_id, retry_count)


async def mirror_document_deletion(document_id: str, retry_count: int = 3) -> bool:
    """Enhanced convenience function to mirror document deletion with retry logic"""
    service = get_supabase_mirror_service()
    return await service.mirror_document_deletion(document_id, retry_count)


async def get_document_analytics(document_id: str) -> Optional[Dict[str, Any]]:
    """Enhanced convenience function to get document analytics"""
    service = get_supabase_mirror_service()
    return await service.get_document_analytics(document_id)