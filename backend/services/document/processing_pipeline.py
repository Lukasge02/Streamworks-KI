"""
Document Processing Pipeline
Handles document processing with Docling, chunk creation, and embedding generation
"""

import logging
import shutil
from pathlib import Path
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Document, DocumentStatus
from services.docling_ingest import DoclingIngestService
from services.document_chunk_service import DocumentChunkService
from services.embeddings import EmbeddingService
from services.vectorstore import VectorStoreService
from services.upload_job_manager import upload_job_manager, UploadStage

logger = logging.getLogger(__name__)


class DocumentProcessingPipeline:
    """
    Handles document processing with Docling, chunking, and embedding generation
    """
    
    def __init__(self):
        # Lazy-loaded processing services
        self._docling_service = None
        self._chunk_service = None
        self._embedding_service = None
        self._vector_store_service = None
    
    def _get_docling_service(self) -> Optional[DoclingIngestService]:
        """Get DoclingIngestService instance with lazy loading"""
        if self._docling_service is None:
            try:
                self._docling_service = DoclingIngestService()
                logger.info("DoclingIngestService initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DoclingIngestService: {str(e)}")
                logger.info("DocumentService will operate without advanced document processing")
                self._docling_service = None
        return self._docling_service
        
    def _get_chunk_service(self) -> Optional[DocumentChunkService]:
        """Get DocumentChunkService instance with lazy loading"""
        if self._chunk_service is None:
            try:
                self._chunk_service = DocumentChunkService()
                logger.info("DocumentChunkService initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DocumentChunkService: {str(e)}")
                self._chunk_service = None
        return self._chunk_service
    
    async def _get_embedding_service(self) -> Optional[EmbeddingService]:
        """Get EmbeddingService instance with lazy loading"""
        if self._embedding_service is None:
            try:
                self._embedding_service = EmbeddingService()
                logger.info("EmbeddingService initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EmbeddingService: {str(e)}")
                self._embedding_service = None
        return self._embedding_service
    
    async def _get_vector_store_service(self) -> Optional[VectorStoreService]:
        """Get VectorStoreService instance with lazy loading"""
        if self._vector_store_service is None:
            try:
                from services.vectorstore import VectorStoreService
                self._vector_store_service = VectorStoreService()
                await self._vector_store_service.initialize()
                logger.info("VectorStoreService initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize VectorStoreService: {str(e)}")
                self._vector_store_service = None
        return self._vector_store_service

    async def process_document_with_docling(
        self,
        db: AsyncSession,
        document: Document,
        file_path: Path,
        job_id: Optional[str] = None
    ) -> None:
        """
        Process document with Docling and create chunks with progress tracking
        
        Args:
            db: Database session
            document: Document record
            file_path: Path to the uploaded file
            job_id: Optional job ID for progress tracking
        """
        try:
            if job_id:
                job = upload_job_manager.update_job_progress(
                    job_id, 50.0, UploadStage.ANALYZING, "Starte Dokument-Analyse"
                )
                if job:
                    from routers.websockets import send_upload_progress_to_document_sync
                await send_upload_progress_to_document_sync(job_id, job)
            
            # Update status to processing
            document.status = DocumentStatus.PROCESSING.value
            document.processing_metadata = {
                "processing_started_at": datetime.utcnow().isoformat(),
                "docling_version": "2.14.0"
            }
            await db.flush()
            
            logger.info(f"Starting Docling processing for {document.filename}")
            
            # Check if file type is supported by Docling
            supported_extensions = ['.pdf', '.docx', '.pptx', '.html', '.htm', '.txt', '.md', '.csv', '.xlsx', 
                                  '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
            
            if file_path.suffix.lower() not in supported_extensions:
                logger.info(f"File type {file_path.suffix} not supported for processing, marking as skipped")
                document.status = DocumentStatus.SKIPPED.value
                document.processing_metadata.update({
                    "processing_completed_at": datetime.utcnow().isoformat(),
                    "processing_skipped": True,
                    "reason": f"Unsupported file type: {file_path.suffix}",
                    "supported_types": supported_extensions
                })
                await db.flush()
                
                if job_id:
                    upload_job_manager.complete_job(job_id, 0)
                return
            
            # Process all supported files with Docling
            document.status = DocumentStatus.ANALYZING.value
            await db.flush()
            
            if job_id:
                job = upload_job_manager.update_job_progress(
                    job_id, 65.0, UploadStage.ANALYZING, "Analysiere Dokumentinhalt mit Docling"
                )
                if job:
                    from routers.websockets import send_upload_progress_to_document_sync
                await send_upload_progress_to_document_sync(job_id, job)
            
            # Process document with Docling (with defensive file protection)
            docling_chunks = []
            file_backup_path = None
            try:
                docling_service = self._get_docling_service()
                if docling_service:
                    # Create backup before Docling processing to prevent file loss
                    file_backup_path = file_path.with_suffix(f".backup{file_path.suffix}")
                    shutil.copy2(file_path, file_backup_path)
                    logger.info(f"Created defensive backup: {file_backup_path}")
                    
                    # Verify original file exists before processing
                    if not file_path.exists():
                        raise Exception(f"Original file disappeared before processing: {file_path}")
                    
                    original_size = file_path.stat().st_size
                    logger.info(f"Processing {document.filename} ({original_size} bytes) with Docling")
                    
                    docling_chunks = await docling_service.process_document(
                        str(file_path),
                        doctype="general"
                    )
                    
                    # Verify original file still exists after Docling processing
                    if not file_path.exists():
                        logger.error(f"🚨 CRITICAL: Original file disappeared during Docling processing: {file_path}")
                        if file_backup_path and file_backup_path.exists():
                            logger.info(f"🔄 Restoring from backup: {file_backup_path} -> {file_path}")
                            shutil.move(file_backup_path, file_path)
                            file_backup_path = None  # Mark as used
                        else:
                            raise Exception(f"File lost during processing and no backup available: {file_path}")
                    else:
                        # Check if file was corrupted/modified
                        current_size = file_path.stat().st_size
                        if current_size != original_size:
                            logger.warning(f"⚠️  File size changed during processing: {original_size} -> {current_size} bytes")
                    
                    logger.info(f"Docling created {len(docling_chunks)} chunks for {document.filename}")
                else:
                    logger.warning(f"Docling service not available for {document.filename}, document stored without processing")
                
                if job_id:
                    job = upload_job_manager.update_job_progress(
                        job_id, 80.0, UploadStage.PROCESSING, f"{len(docling_chunks)} Text-Chunks erstellt" if docling_chunks else "Dokument gespeichert (ohne Textverarbeitung)"
                    )
                    if job:
                        from routers.websockets import send_upload_progress_to_document_sync
                await send_upload_progress_to_document_sync(job_id, job)
                
            except Exception as docling_error:
                # In case of error, restore from backup if file is missing
                if file_backup_path and file_backup_path.exists():
                    if not file_path.exists():
                        logger.info(f"🔄 Restoring file from backup after error: {file_backup_path} -> {file_path}")
                        try:
                            shutil.move(file_backup_path, file_path)
                            file_backup_path = None
                        except Exception as restore_error:
                            logger.error(f"Failed to restore backup: {str(restore_error)}")
                
                if job_id:
                    upload_job_manager.fail_job(job_id, f"Docling-Analyse fehlgeschlagen: {str(docling_error)}")
                raise Exception(f"Docling processing error: {str(docling_error)}")
            
            finally:
                # Clean up backup file if not used for restoration
                if file_backup_path and file_backup_path.exists():
                    try:
                        file_backup_path.unlink()
                        logger.info(f"Cleaned up backup file: {file_backup_path}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to cleanup backup file: {str(cleanup_error)}")
            
            # Save chunks to database and create embeddings
            await self._save_chunks_and_embeddings(db, document, docling_chunks, job_id)
            
            # Mark as completed
            document.status = DocumentStatus.READY.value
            document.chunk_count = len(docling_chunks)
            document.processed_at = datetime.utcnow()
            document.processing_metadata.update({
                "processing_completed_at": datetime.utcnow().isoformat(),
                "chunk_count": len(docling_chunks),
                "processing_success": True
            })
            
            await db.commit()
            
            if job_id:
                upload_job_manager.complete_job(job_id, len(docling_chunks))
            
            logger.info(f"✅ Document processing completed successfully: {document.filename} ({len(docling_chunks)} chunks)")
            
        except Exception as e:
            # Update document status to failed
            document.status = DocumentStatus.FAILED.value
            document.error_message = str(e)
            document.processing_metadata = document.processing_metadata or {}
            document.processing_metadata.update({
                "processing_failed_at": datetime.utcnow().isoformat(),
                "processing_success": False,
                "error": str(e)
            })
            
            await db.commit()
            
            if job_id:
                upload_job_manager.fail_job(job_id, str(e))
            
            logger.error(f"❌ Document processing failed: {document.filename} - {str(e)}")
            raise

    async def _save_chunks_and_embeddings(
        self,
        db: AsyncSession,
        document: Document,
        docling_chunks: list,
        job_id: Optional[str] = None
    ) -> None:
        """Save chunks to database and generate embeddings"""
        
        chunk_service = self._get_chunk_service()
        if not docling_chunks or not chunk_service:
            return
            
        try:
            if job_id:
                job = upload_job_manager.update_job_progress(
                    job_id, 90.0, UploadStage.PROCESSING, "Speichere Chunks in Datenbank"
                )
                if job:
                    from routers.websockets import send_upload_progress_to_document_sync
                await send_upload_progress_to_document_sync(job_id, job)
            
            db_chunks = await chunk_service.create_chunks_from_docling(
                db, document.id, docling_chunks
            )
            
            # Auto-generate embeddings and store in ChromaDB
            embedding_chunks = 0
            try:
                if job_id:
                    job = upload_job_manager.update_job_progress(
                        job_id, 92.0, UploadStage.PROCESSING, "Erstelle Embeddings"
                    )
                    if job:
                        from routers.websockets import send_upload_progress_to_document_sync
                await send_upload_progress_to_document_sync(job_id, job)
                
                # Convert db chunks to dictionary format for embedding service
                chunks_for_embedding = []
                for db_chunk in db_chunks:
                    chunk_dict = {
                        "id": str(db_chunk.id),
                        "text": db_chunk.content or "",
                        "metadata": {
                            "doc_id": str(document.id),
                            "doctype": db_chunk.chunk_type.value if db_chunk.chunk_type else "general",
                            "page": db_chunk.page_number or 0,
                            "heading": db_chunk.heading or "",
                            "section": db_chunk.section_name or "",
                            "created_at": datetime.utcnow().isoformat(),
                            "source_file": document.filename,
                            "content_type": "text",
                            "word_count": db_chunk.word_count or 0
                        }
                    }
                    chunks_for_embedding.append(chunk_dict)
                
                # Generate embeddings
                embedding_service = await self._get_embedding_service()
                if embedding_service:
                    embedded_chunks = await embedding_service.embed_chunks(chunks_for_embedding)
                    
                    if job_id:
                        job = upload_job_manager.update_job_progress(
                            job_id, 95.0, UploadStage.PROCESSING, "Speichere in Vektor-Datenbank"
                        )
                        if job:
                            from routers.websockets import send_upload_progress_to_document_sync
                            await send_upload_progress_to_document_sync(job_id, job)
                    
                    # Store in ChromaDB
                    vector_store = await self._get_vector_store_service()
                    if vector_store:
                        await vector_store.store_chunks(embedded_chunks, str(document.id))
                        embedding_chunks = len(embedded_chunks)
                        logger.info(f"✅ Created {embedding_chunks} embeddings and stored in ChromaDB for {document.filename}")
                
            except Exception as embedding_error:
                logger.warning(f"⚠️ Failed to create embeddings for {document.filename}: {str(embedding_error)}")
                # Don't fail the entire process if embeddings fail
            
        except Exception as e:
            logger.error(f"Failed to save chunks for {document.filename}: {str(e)}")
            raise

    async def reprocess_document(
        self,
        db: AsyncSession,
        document: Document,
        file_path: Path
    ) -> None:
        """
        Reprocess document (useful for fixing failed processing)
        
        Args:
            db: Database session
            document: Document record
            file_path: Path to the file
        """
        try:
            logger.info(f"Reprocessing document: {document.filename}")
            
            # Clear existing chunks first
            chunk_service = self._get_chunk_service()
            if chunk_service:
                await chunk_service.delete_document_chunks(db, document.id)
            
            # Reset document status
            document.status = DocumentStatus.UPLOADED.value
            document.error_message = None
            document.chunk_count = 0
            document.processed_at = None
            document.processing_metadata = {
                "reprocessing_initiated_at": datetime.utcnow().isoformat()
            }
            
            await db.flush()
            
            # Process again
            await self.process_document_with_docling(db, document, file_path)
            
            logger.info(f"✅ Document reprocessing completed: {document.filename}")
            
        except Exception as e:
            logger.error(f"❌ Document reprocessing failed: {document.filename} - {str(e)}")
            raise