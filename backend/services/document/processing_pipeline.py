"""
Document Processing Pipeline
Modern document processing with LlamaIndex RAG pipeline
"""

import logging
from pathlib import Path
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Document, DocumentStatus
from .llamaindex_processing_pipeline import LlamaIndexProcessingPipeline

logger = logging.getLogger(__name__)


class DocumentProcessingPipeline:
    """
    Modern document processing with LlamaIndex RAG pipeline
    """

    def __init__(self):
        # New LlamaIndex pipeline
        self._llamaindex_pipeline = None

    async def _get_llamaindex_pipeline(self):
        """Get LlamaIndex processing pipeline"""
        if self._llamaindex_pipeline is None:
            self._llamaindex_pipeline = LlamaIndexProcessingPipeline()
        return self._llamaindex_pipeline

    async def process_document_with_llamaindex(
        self,
        db: AsyncSession,
        document: Document,
        file_path: Path,
        job_id: Optional[str] = None
    ) -> None:
        """
        Process document with LlamaIndex RAG pipeline

        Args:
            db: Database session
            document: Document record
            file_path: Path to the uploaded file
            job_id: Optional job ID for progress tracking
        """
        try:
            # Validate inputs
            if not file_path or not file_path.exists():
                raise ValueError(f"File not found: {file_path}")

            if not document:
                raise ValueError("Document record is required")

            # Log processing start
            logger.info(f"🚀 Starting document processing: {document.filename} (ID: {document.id})")

            # Delegate to LlamaIndex pipeline
            pipeline = await self._get_llamaindex_pipeline()
            await pipeline.process_document_with_llamaindex(db, document, file_path, job_id)

            logger.info(f"✅ Document processing completed successfully: {document.filename}")

        except Exception as e:
            # Enhanced error handling
            error_message = f"Document processing failed: {str(e)}"
            logger.error(f"❌ {error_message} (Document: {document.filename if document else 'Unknown'})")

            # Update document status to error if possible
            if document:
                try:
                    document.status = DocumentStatus.ERROR.value
                    document.error_message = error_message
                    document.processing_metadata = document.processing_metadata or {}
                    document.processing_metadata.update({
                        "processing_failed_at": datetime.utcnow().isoformat(),
                        "error": error_message,
                        "processing_engine": "llamaindex_rag"
                    })
                    await db.commit()
                    logger.info(f"📝 Document status updated to ERROR in database")
                except Exception as db_error:
                    logger.error(f"❌ Failed to update document status: {str(db_error)}")

            # Re-raise the original exception
            raise

    # Legacy method name for backward compatibility
    async def process_document_with_docling(
        self,
        db: AsyncSession,
        document: Document,
        file_path: Path,
        job_id: Optional[str] = None
    ) -> None:
        """Legacy method name - redirects to LlamaIndex processing"""
        await self.process_document_with_llamaindex(db, document, file_path, job_id)

    async def reprocess_document(
        self,
        db: AsyncSession,
        document: Document,
        file_path: Path
    ) -> None:
        """
        Reprocess document with LlamaIndex

        Args:
            db: Database session
            document: Document record
            file_path: Path to the file
        """
        try:
            # Validate inputs
            if not file_path or not file_path.exists():
                raise ValueError(f"File not found: {file_path}")

            if not document:
                raise ValueError("Document record is required")

            logger.info(f"🔄 Starting document reprocessing: {document.filename} (ID: {document.id})")

            # Delegate to LlamaIndex pipeline
            pipeline = await self._get_llamaindex_pipeline()
            await pipeline.reprocess_document(db, document, file_path)

            logger.info(f"✅ Document reprocessing completed successfully: {document.filename}")

        except Exception as e:
            # Enhanced error handling
            error_message = f"Document reprocessing failed: {str(e)}"
            logger.error(f"❌ {error_message} (Document: {document.filename if document else 'Unknown'})")

            # Update document status to error if possible
            if document:
                try:
                    document.status = DocumentStatus.ERROR.value
                    document.error_message = error_message
                    document.processing_metadata = document.processing_metadata or {}
                    document.processing_metadata.update({
                        "reprocessing_failed_at": datetime.utcnow().isoformat(),
                        "error": error_message,
                        "processing_engine": "llamaindex_rag"
                    })
                    await db.commit()
                    logger.info(f"📝 Document status updated to ERROR after reprocessing failure")
                except Exception as db_error:
                    logger.error(f"❌ Failed to update document status after reprocessing failure: {str(db_error)}")

            # Re-raise the original exception
            raise