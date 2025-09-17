"""
LlamaIndex Document Processing Pipeline
Replaces Docling-based processing with modern LlamaIndex RAG pipeline
"""

import logging
from pathlib import Path
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Document, DocumentStatus
from services.qdrant_rag_service import get_rag_service

logger = logging.getLogger(__name__)


class LlamaIndexProcessingPipeline:
    """
    Modern document processing pipeline using LlamaIndex
    Replaces Docling with state-of-the-art RAG architecture
    """

    def __init__(self):
        self._rag_service = None

    async def _get_rag_service(self):
        """Get RAG service instance"""
        if self._rag_service is None:
            self._rag_service = await get_rag_service()
        return self._rag_service

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
            # Update status to processing
            document.status = DocumentStatus.PROCESSING.value
            document.processing_metadata = {
                "processing_started_at": datetime.utcnow().isoformat(),
                "llamaindex_version": "0.13.0+",
                "processing_engine": "llamaindex_rag"
            }
            await db.flush()

            logger.info(f"Starting LlamaIndex processing for {document.filename}")

            # Progress tracking (if available)
            if job_id:
                try:
                    from services.upload_job_manager import upload_job_manager, UploadStage
                    from routers.websockets import send_upload_progress_to_document_sync

                    job = upload_job_manager.update_job_progress(
                        job_id, 50.0, UploadStage.ANALYZING, "Initialisiere moderne RAG-Pipeline"
                    )
                    if job:
                        await send_upload_progress_to_document_sync(job_id, job)
                except ImportError:
                    logger.info("Upload job manager not available, skipping progress tracking")
                except Exception as progress_error:
                    logger.warning(f"Progress tracking failed: {str(progress_error)}")

            # Check if file type is supported
            supported_extensions = [
                '.pdf', '.docx', '.pptx', '.html', '.htm', '.txt', '.md', '.csv',
                '.xlsx', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.xml'
            ]

            if file_path.suffix.lower() not in supported_extensions:
                logger.info(f"File type {file_path.suffix} not supported, marking as skipped")
                document.status = DocumentStatus.SKIPPED.value
                document.processing_metadata.update({
                    "processing_completed_at": datetime.utcnow().isoformat(),
                    "processing_skipped": True,
                    "reason": f"Unsupported file type: {file_path.suffix}",
                    "supported_types": supported_extensions
                })
                await db.flush()
                return

            # Update status to analyzing
            document.status = DocumentStatus.ANALYZING.value
            await db.flush()

            if job_id:
                try:
                    from services.upload_job_manager import upload_job_manager, UploadStage
                    from routers.websockets import send_upload_progress_to_document_sync

                    job = upload_job_manager.update_job_progress(
                        job_id, 70.0, UploadStage.ANALYZING, "Analysiere Dokumentinhalt mit LlamaIndex"
                    )
                    if job:
                        await send_upload_progress_to_document_sync(job_id, job)
                except ImportError:
                    logger.info("Upload job manager not available for progress update")
                except Exception as e:
                    logger.warning(f"Progress update failed: {str(e)}")

            # Process document with LlamaIndex RAG service
            rag_service = await self._get_rag_service()
            chunks = await rag_service.process_document(
                file_path=file_path,
                doc_id=str(document.id),
                doctype="general"
            )

            logger.info(f"LlamaIndex created {len(chunks)} chunks for {document.filename}")

            if job_id:
                try:
                    from services.upload_job_manager import upload_job_manager, UploadStage
                    from routers.websockets import send_upload_progress_to_document_sync

                    job = upload_job_manager.update_job_progress(
                        job_id, 90.0, UploadStage.PROCESSING, f"{len(chunks)} Chunks erstellt und indiziert"
                    )
                    if job:
                        await send_upload_progress_to_document_sync(job_id, job)
                except ImportError:
                    logger.info("Upload job manager not available for completion update")
                except Exception as e:
                    logger.warning(f"Progress completion update failed: {str(e)}")

            # Update document with chunk count (ChromaDB is already populated)
            await self._update_document_completion(db, document, chunks)

            # Mark as completed with simplified metadata
            document.status = DocumentStatus.READY.value
            document.chunk_count = len(chunks)
            document.processed_at = datetime.utcnow()

            # Simplified processing metadata for ChromaDB-master architecture
            document.processing_metadata.update({
                "processing_completed_at": datetime.utcnow().isoformat(),
                "chunk_count": len(chunks),
                "processing_success": True,
                "processing_engine": "llamaindex_chromadb_master",
                "embedding_model": "BAAI/bge-base-en-v1.5",
                "vector_store": "chromadb_master",
                "architecture": "simplified_single_source"
            })

            await db.commit()
            logger.info(f"📊 Document status updated to READY in database")

            if job_id:
                try:
                    from services.upload_job_manager import upload_job_manager
                    upload_job_manager.complete_job(job_id, len(chunks))
                except ImportError:
                    logger.info("Upload job manager not available for job completion")
                except Exception as e:
                    logger.warning(f"Job completion failed: {str(e)}")

            logger.info(f"✅ LlamaIndex processing completed: {document.filename} ({len(chunks)} chunks)")

        except Exception as e:
            # Update document status to failed
            error_message = f"LlamaIndex processing error: {str(e)}"

            document.status = DocumentStatus.ERROR.value
            document.error_message = error_message
            document.processing_metadata = document.processing_metadata or {}
            document.processing_metadata.update({
                "processing_failed_at": datetime.utcnow().isoformat(),
                "processing_success": False,
                "error": error_message,
                "processing_engine": "llamaindex_rag"
            })

            await db.commit()

            # Mirror error status to Supabase for debugging
            try:
                from services.supabase_mirror_service import get_supabase_mirror_service
                mirror_service = get_supabase_mirror_service()

                if mirror_service.is_enabled():
                    error_metadata = {
                        "processing_engine": "llamaindex_rag",
                        "embedding_model": "BAAI/bge-base-en-v1.5",
                        "chunk_count": 0,
                        "error": error_message,
                        "processing_success": False
                    }
                    await mirror_service.mirror_document_stats(
                        str(document.id), 0, error_metadata
                    )
                    logger.info(f"📤 Error status mirrored to Supabase for debugging: {document.id}")

            except Exception as mirror_error:
                logger.warning(f"⚠️ Failed to mirror error status to Supabase: {str(mirror_error)}")

            if job_id:
                try:
                    from services.upload_job_manager import upload_job_manager
                    upload_job_manager.fail_job(job_id, error_message)
                except ImportError:
                    logger.info("Upload job manager not available for job failure notification")
                except Exception as e:
                    logger.warning(f"Job failure notification failed: {str(e)}")

            logger.error(f"❌ LlamaIndex processing failed: {document.filename} - {error_message}")
            raise

    async def _update_document_completion(
        self,
        db: AsyncSession,
        document: Document,
        chunks: list
    ) -> None:
        """
        Update document completion status (ChromaDB already contains the chunks)

        Args:
            db: Database session
            document: Document record
            chunks: List of processed chunks (for metadata only)
        """
        logger.info(f"✅ Completing document processing for {document.filename}")

        try:
            # Enhanced Supabase mirror with reliable processing (now critical for UI debugging)
            try:
                from services.supabase_mirror_service import get_supabase_mirror_service

                mirror_service = get_supabase_mirror_service()

                if mirror_service.is_enabled():
                    logger.info(f"📤 Starting enhanced Supabase metadata mirroring for {document.id}")

                    # Prepare enhanced chunk data for mirror
                    chunks_data = []
                    for i, chunk in enumerate(chunks):
                        enhanced_metadata = chunk.metadata.copy() if chunk.metadata else {}
                        enhanced_metadata.update({
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "processing_engine": "llamaindex_chromadb_master",
                            "embedding_model": "BAAI/bge-base-en-v1.5",
                            "word_count": len(chunk.content.split()) if chunk.content else 0,
                            "char_count": len(chunk.content) if chunk.content else 0,
                            "chunk_type": getattr(chunk, 'chunk_type', 'text')
                        })

                        chunks_data.append({
                            'id': chunk.chunk_id,
                            'content': chunk.content,
                            'metadata': enhanced_metadata
                        })

                    # Enhanced processing metadata for document stats
                    processing_metadata = {
                        "processing_engine": "llamaindex_chromadb_master",
                        "embedding_model": "BAAI/bge-base-en-v1.5",
                        "chunk_count": len(chunks),
                        "architecture": "simplified_single_source",
                        "vector_store": "chromadb_master"
                    }

                    # Mirror with reliable processing (not background tasks)
                    try:
                        # Mirror chunk metadata with retry logic
                        chunk_success = await mirror_service.mirror_chunk_metadata(
                            chunks_data, str(document.id), retry_count=3
                        )

                        # Mirror document stats with retry logic
                        stats_success = await mirror_service.mirror_document_stats(
                            str(document.id), len(chunks), processing_metadata, retry_count=3
                        )

                        if chunk_success and stats_success:
                            logger.info(f"✅ Enhanced Supabase mirror completed successfully: {len(chunks)} chunks mirrored")
                        else:
                            logger.warning(f"⚠️ Supabase mirror partially failed - chunk_success: {chunk_success}, stats_success: {stats_success}")

                    except Exception as mirror_error:
                        logger.error(f"❌ Enhanced Supabase mirror failed: {str(mirror_error)}")
                        # Continue processing - mirror failure shouldn't block document processing
                else:
                    logger.info(f"📊 Supabase mirror service disabled - skipping metadata mirroring")

            except ImportError as import_error:
                # Mirror service may not be available - this is ok
                logger.info(f"📦 Supabase mirror service not available (skipped): {str(import_error)}")
            except Exception as mirror_error:
                # Mirror failures are logged but don't block processing
                logger.error(f"❌ Supabase mirror service error: {str(mirror_error)}")

            logger.info(f"🎯 Document completion updated: {len(chunks)} chunks processed")

        except Exception as e:
            # This shouldn't fail, but if it does, just log it
            logger.warning(f"⚠️ Document completion update had issues: {str(e)}")
            # Don't raise - the main processing already succeeded

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
            logger.info(f"Reprocessing document with LlamaIndex: {document.filename}")

            # Remove from vector store first
            rag_service = await self._get_rag_service()
            await rag_service.delete_document(str(document.id))

            # Reset document status
            document.status = DocumentStatus.UPLOADED.value
            document.error_message = None
            document.chunk_count = 0
            document.processed_at = None
            document.processing_metadata = {
                "reprocessing_initiated_at": datetime.utcnow().isoformat(),
                "processing_engine": "llamaindex_rag"
            }

            await db.flush()

            # Process again
            await self.process_document_with_llamaindex(db, document, file_path)

            logger.info(f"✅ Document reprocessing completed: {document.filename}")

        except Exception as e:
            logger.error(f"❌ Document reprocessing failed: {document.filename} - {str(e)}")
            raise