"""
Document Service for File Management
Enterprise-grade document operations with Supabase storage
"""

import os
import hashlib
import logging
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any, BinaryIO
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import UploadFile

from models.core import Document, Folder, DocumentStatus
from schemas.core import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentWithFolder,
    DocumentFilter, DocumentSort, BulkDeleteResponse, BulkMoveResponse
)
from services.folder_service import FolderService
from services.docling_ingest import DoclingIngestService
from services.document_chunk_service import DocumentChunkService
from services.embeddings import EmbeddingService
from services.vectorstore import VectorStoreService
from services.upload_job_manager import upload_job_manager, UploadStage
from routers.websockets import send_upload_progress_to_document_sync

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service for document CRUD operations
    Handles file upload, storage, metadata management
    """
    
    def __init__(self):
        # Create storage directory structure
        self.storage_root = Path("storage/documents")
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        # Lazy-loaded processing services
        self._docling_service = None
        self._chunk_service = None
        self._embedding_service = None
        self._vector_store_service = None
        self._services_initialized = False
        
    def _get_docling_service(self) -> DoclingIngestService:
        """Get DoclingIngestService instance with lazy loading"""
        if self._docling_service is None:
            try:
                self._docling_service = DoclingIngestService()
                logger.info("DoclingIngestService initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DoclingIngestService: {str(e)}")
                logger.info("DocumentService will operate without advanced document processing")
                # Create a minimal stub that won't crash
                self._docling_service = None
        return self._docling_service
        
    def _get_chunk_service(self) -> DocumentChunkService:
        """Get DocumentChunkService instance with lazy loading"""
        if self._chunk_service is None:
            try:
                self._chunk_service = DocumentChunkService()
                logger.info("DocumentChunkService initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DocumentChunkService: {str(e)}")
                # Create a minimal stub
                self._chunk_service = None
        return self._chunk_service
    
    @property
    def docling_service(self) -> Optional[DoclingIngestService]:
        """Property to access DoclingIngestService"""
        return self._get_docling_service()
        
    @property 
    def chunk_service(self) -> Optional[DocumentChunkService]:
        """Property to access DocumentChunkService"""
        return self._get_chunk_service()
    
    async def _get_embedding_service(self):
        """Get EmbeddingService instance with lazy loading"""
        if self._embedding_service is None:
            try:
                self._embedding_service = EmbeddingService()
                logger.info("EmbeddingService initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EmbeddingService: {str(e)}")
                # Continue without embeddings - not critical for basic functionality
                self._embedding_service = None
        return self._embedding_service
    
    async def _get_vector_store_service(self):
        """Get VectorStoreService instance with lazy loading"""
        if self._vector_store_service is None:
            try:
                from .vectorstore import VectorStoreService
                self._vector_store_service = VectorStoreService()
                await self._vector_store_service.initialize()
                logger.info("VectorStoreService initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize VectorStoreService: {str(e)}")
                # Continue without vector storage - not critical for basic functionality
                self._vector_store_service = None
        return self._vector_store_service

    async def upload_document(
        self,
        db: AsyncSession,
        file: UploadFile,
        folder_id: UUID,
        job_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Document:
        """
        Upload and store a document with progress tracking
        
        Args:
            db: Database session
            file: Uploaded file
            folder_id: Target folder ID
            job_id: Optional job ID for progress tracking
            tags: Optional tags
            description: Optional description
            
        Returns:
            Created document record
        """
        try:
            # Create or update progress tracking
            if job_id:
                upload_job_manager.create_job(job_id, file.filename or "unknown", file.size or 0)
                job = upload_job_manager.update_job_progress(
                    job_id, 10.0, UploadStage.UPLOADING, "Validierung und Hash-Berechnung"
                )
                if job:
                    await send_upload_progress_to_document_sync(job_id, job)
            
            # Validate folder exists
            folder = await FolderService.get_folder_by_id(db, folder_id)
            if not folder:
                raise ValueError(f"Folder {folder_id} not found")
            
            # Read file content for hashing
            file_content = await file.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            if job_id:
                job = upload_job_manager.update_job_progress(
                    job_id, 25.0, UploadStage.UPLOADING, "Datei validiert, speichere lokal"
                )
                if job:
                    await send_upload_progress_to_document_sync(job_id, job)
            
            # Check for duplicates
            existing = await self._get_document_by_hash(db, file_hash)
            if existing:
                raise ValueError(f"Document with same content already exists: {existing.filename}")
            
            # Generate storage path
            storage_path = self._generate_storage_path(file.filename, file_hash)
            full_storage_path = self.storage_root / storage_path
            
            # Ensure storage directory exists
            full_storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file to storage
            with open(full_storage_path, 'wb') as f:
                f.write(file_content)
            
            if job_id:
                job = upload_job_manager.update_job_progress(
                    job_id, 40.0, UploadStage.UPLOADING, "Datei gespeichert"
                )
                if job:
                    await send_upload_progress_to_document_sync(job_id, job)
            
            # Detect MIME type
            mime_type = self._detect_mime_type(file.filename, file_content)
            
            # Create document record
            document = Document(
                filename=self._sanitize_filename(file.filename),
                original_filename=file.filename,
                folder_id=folder_id,
                file_hash=file_hash,
                file_size=len(file_content),
                mime_type=mime_type,
                storage_path=str(storage_path),
                status=DocumentStatus.READY.value,
                tags=tags or [],
                description=description
            )
            
            db.add(document)
            await db.flush()
            await db.refresh(document)
            
            logger.info(f"Uploaded document: {document.filename} ({len(file_content)} bytes)")
            
            # Process document with Docling (async)
            try:
                await self._process_document_with_docling(db, document, full_storage_path, job_id)
            except Exception as e:
                logger.error(f"Docling processing failed for {document.filename}: {str(e)}")
                # Update progress tracking with error
                if job_id:
                    upload_job_manager.fail_job(job_id, f"Verarbeitung fehlgeschlagen: {str(e)}")
                # Update document status but don't fail the upload
                document.status = DocumentStatus.ERROR.value
                document.error_message = f"Processing failed: {str(e)}"
                await db.flush()
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to upload document: {str(e)}")
            # Update progress tracking with error
            if job_id:
                upload_job_manager.fail_job(job_id, f"Upload fehlgeschlagen: {str(e)}")
            # Cleanup file if created
            if 'full_storage_path' in locals() and full_storage_path.exists():
                full_storage_path.unlink()
            await db.rollback()
            raise

    async def get_document_by_id(
        self,
        db: AsyncSession,
        document_id: UUID,
        include_folder: bool = False
    ) -> Optional[Document]:
        """
        Get document by ID with optional folder info
        
        Args:
            db: Database session
            document_id: Document UUID
            include_folder: Include folder information
            
        Returns:
            Document or None if not found
        """
        try:
            query = select(Document).where(Document.id == document_id)
            
            if include_folder:
                query = query.options(selectinload(Document.folder))
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {str(e)}")
            return None

    async def get_documents_list(
        self,
        db: AsyncSession,
        folder_id: Optional[UUID] = None,
        filters: Optional[DocumentFilter] = None,
        sort: DocumentSort = DocumentSort.CREATED_DESC,
        page: int = 1,
        per_page: int = 50
    ) -> List[DocumentWithFolder]:
        """
        Get paginated list of documents with filtering and sorting
        
        Args:
            db: Database session
            folder_id: Filter by folder
            filters: Additional filters
            sort: Sort order
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            List of documents with folder info
        """
        try:
            # Build base query
            query = select(Document).options(selectinload(Document.folder))
            
            # Apply folder filter
            if folder_id:
                query = query.where(Document.folder_id == folder_id)
            
            # Apply additional filters
            if filters:
                # Override folder_id if provided in filters (for consistency)
                if filters.folder_id and not folder_id:
                    query = query.where(Document.folder_id == filters.folder_id)
                    
                if filters.status:
                    query = query.where(Document.status == filters.status)
                    
                if filters.mime_types:
                    query = query.where(Document.mime_type.in_(filters.mime_types))
                    
                if filters.tags:
                    # Documents that have any of the specified tags
                    tag_conditions = [Document.tags.contains([tag]) for tag in filters.tags]
                    query = query.where(or_(*tag_conditions))
                    
                if filters.date_from:
                    query = query.where(Document.created_at >= filters.date_from)
                    
                if filters.date_to:
                    query = query.where(Document.created_at <= filters.date_to)
                    
                if filters.search_query:
                    search_pattern = f"%{filters.search_query}%"
                    query = query.where(
                        or_(
                            Document.filename.ilike(search_pattern),
                            Document.original_filename.ilike(search_pattern),
                            Document.description.ilike(search_pattern)
                        )
                    )
            
            # Apply sorting
            sort_column = Document.created_at
            sort_order = desc
            
            if sort == DocumentSort.CREATED_ASC:
                sort_column, sort_order = Document.created_at, asc
            elif sort == DocumentSort.NAME_ASC:
                sort_column, sort_order = Document.filename, asc
            elif sort == DocumentSort.NAME_DESC:
                sort_column, sort_order = Document.filename, desc
            elif sort == DocumentSort.SIZE_ASC:
                sort_column, sort_order = Document.file_size, asc
            elif sort == DocumentSort.SIZE_DESC:
                sort_column, sort_order = Document.file_size, desc
            
            query = query.order_by(sort_order(sort_column))
            
            # Apply pagination
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            result = await db.execute(query)
            documents = result.scalars().all()
            
            # Convert to response format
            responses = []
            for doc in documents:
                folder_response = None
                if doc.folder:
                    folder_response = {
                        "id": doc.folder.id,
                        "name": doc.folder.name,
                        "path": doc.folder.path,
                        "created_at": doc.folder.created_at,
                        "updated_at": doc.folder.updated_at
                    }
                
                doc_response = DocumentWithFolder(
                    id=doc.id,
                    filename=doc.filename,
                    original_filename=doc.original_filename,
                    folder_id=doc.folder_id,
                    file_hash=doc.file_hash,
                    file_size=doc.file_size,
                    mime_type=doc.mime_type,
                    status=doc.status,
                    error_message=doc.error_message,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at,
                    processed_at=doc.processed_at,
                    tags=doc.tags,
                    description=doc.description,
                    folder=folder_response
                )
                responses.append(doc_response)
            
            return responses
            
        except Exception as e:
            logger.error(f"Failed to get documents list: {str(e)}")
            return []

    async def update_document(
        self,
        db: AsyncSession,
        document_id: UUID,
        update_data: DocumentUpdate
    ) -> Optional[Document]:
        """
        Update document metadata
        
        Args:
            db: Database session
            document_id: Document ID
            update_data: Update data
            
        Returns:
            Updated document or None if not found
        """
        try:
            document = await self.get_document_by_id(db, document_id)
            if not document:
                return None
            
            # Update fields
            if update_data.filename is not None:
                document.filename = self._sanitize_filename(update_data.filename)
                
            if update_data.folder_id is not None:
                # Validate new folder exists
                folder = await FolderService.get_folder_by_id(db, update_data.folder_id)
                if not folder:
                    raise ValueError(f"Folder {update_data.folder_id} not found")
                document.folder_id = update_data.folder_id
                
            if update_data.tags is not None:
                document.tags = update_data.tags
                
            if update_data.description is not None:
                document.description = update_data.description
            
            await db.flush()
            await db.refresh(document)
            
            logger.info(f"Updated document: {document.filename}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {str(e)}")
            await db.rollback()
            raise

    async def delete_document(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> bool:
        """
        Delete document and its file
        
        Args:
            db: Database session
            document_id: Document ID
            
        Returns:
            True if deleted successfully
        """
        try:
            document = await self.get_document_by_id(db, document_id)
            if not document:
                return False
            
            # Delete physical file
            storage_path = self.storage_root / document.storage_path
            if storage_path.exists():
                storage_path.unlink()
                logger.info(f"Deleted file: {storage_path}")
            
            # Delete from vector store first
            try:
                vector_store = await self._get_vector_store_service()
                if vector_store:
                    await vector_store.delete_document(str(document_id))
                    logger.info(f"Deleted embeddings from vector store for document {document.filename}")
            except Exception as e:
                logger.warning(f"Failed to delete embeddings for document {document.filename}: {str(e)}")
            
            # Delete chunks from database (should cascade automatically, but explicit is better)
            if self.chunk_service:
                try:
                    chunks_deleted = await self.chunk_service.delete_chunks_by_document(db, document_id)
                    logger.info(f"Deleted {chunks_deleted} chunks for document {document.filename}")
                except Exception as e:
                    logger.warning(f"Failed to delete chunks for document {document.filename}: {str(e)}")
            else:
                logger.info(f"Chunk service not available, skipping chunk deletion for {document.filename}")
            
            # Delete database record
            await db.delete(document)
            await db.flush()
            
            logger.info(f"Deleted document: {document.filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            await db.rollback()
            raise

    async def get_document_file(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> Optional[tuple[Path, str, str]]:
        """
        Get document file path and metadata for download
        
        Args:
            db: Database session
            document_id: Document ID
            
        Returns:
            Tuple of (file_path, filename, mime_type) or None
        """
        try:
            document = await self.get_document_by_id(db, document_id)
            if not document:
                return None
            
            file_path = self.storage_root / document.storage_path
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            return file_path, document.original_filename, document.mime_type
            
        except Exception as e:
            logger.error(f"Failed to get document file {document_id}: {str(e)}")
            return None

    async def bulk_delete_documents(
        self,
        db: AsyncSession,
        document_ids: List[UUID]
    ) -> BulkDeleteResponse:
        """
        Delete multiple documents in batch
        
        Args:
            db: Database session
            document_ids: List of document IDs
            
        Returns:
            Bulk delete response with results
        """
        deleted = []
        failed = []
        
        try:
            for doc_id in document_ids:
                try:
                    success = await self.delete_document(db, doc_id)
                    if success:
                        deleted.append(doc_id)
                    else:
                        failed.append({
                            "id": str(doc_id),
                            "error": "Document not found"
                        })
                except Exception as e:
                    failed.append({
                        "id": str(doc_id),
                        "error": str(e)
                    })
            
            return BulkDeleteResponse(
                deleted=deleted,
                failed=failed,
                total_requested=len(document_ids),
                total_deleted=len(deleted),
                total_failed=len(failed)
            )
            
        except Exception as e:
            logger.error(f"Bulk delete failed: {str(e)}")
            raise

    async def bulk_move_documents(
        self,
        db: AsyncSession,
        document_ids: List[UUID],
        target_folder_id: UUID
    ) -> BulkMoveResponse:
        """
        Move multiple documents to a target folder
        
        Args:
            db: Database session
            document_ids: List of document IDs
            target_folder_id: Target folder ID
            
        Returns:
            Bulk move response with results
        """
        moved = []
        failed = []
        
        try:
            # Validate target folder exists
            target_folder = await FolderService.get_folder_by_id(db, target_folder_id)
            if not target_folder:
                raise ValueError(f"Target folder {target_folder_id} not found")
            
            for doc_id in document_ids:
                try:
                    update_data = DocumentUpdate(folder_id=target_folder_id)
                    result = await self.update_document(db, doc_id, update_data)
                    if result:
                        moved.append(doc_id)
                    else:
                        failed.append({
                            "id": str(doc_id),
                            "error": "Document not found"
                        })
                except Exception as e:
                    failed.append({
                        "id": str(doc_id),
                        "error": str(e)
                    })
            
            return BulkMoveResponse(
                moved=moved,
                failed=failed,
                total_requested=len(document_ids),
                total_moved=len(moved),
                total_failed=len(failed)
            )
            
        except Exception as e:
            logger.error(f"Bulk move failed: {str(e)}")
            raise

    # Private helper methods
    async def _get_document_by_hash(
        self, 
        db: AsyncSession, 
        file_hash: str
    ) -> Optional[Document]:
        """Get document by file hash"""
        query = select(Document).where(Document.file_hash == file_hash)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    def _generate_storage_path(self, filename: str, file_hash: str) -> str:
        """Generate storage path for file"""
        # Use first 2 chars of hash for directory structure
        dir1 = file_hash[:2]
        dir2 = file_hash[2:4]
        
        # Clean filename
        clean_name = self._sanitize_filename(filename)
        
        # Add hash prefix to avoid conflicts
        storage_name = f"{file_hash[:8]}_{clean_name}"
        
        return f"{dir1}/{dir2}/{storage_name}"

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove potentially dangerous characters
        dangerous_chars = '<>:"/\\|?*'
        clean_name = ''.join(c for c in filename if c not in dangerous_chars)
        
        # Limit length
        if len(clean_name) > 200:
            name, ext = os.path.splitext(clean_name)
            clean_name = name[:200-len(ext)] + ext
        
        return clean_name or "unnamed_file"

    def _detect_mime_type(self, filename: str, content: bytes) -> str:
        """Detect MIME type from filename and content"""
        # Simple MIME type detection based on file extension
        ext = Path(filename).suffix.lower()
        
        mime_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        
        return mime_map.get(ext, 'application/octet-stream')

    async def _process_document_with_docling(
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
            # Docling 2.47.1 supports: PDF, DOCX, PPTX, HTML, IMAGE (PNG, JPG, etc.), MD, CSV, XLSX, and more
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
            
            # Process all supported files with Docling (including images with native OCR)
            document.status = DocumentStatus.ANALYZING.value
            await db.flush()
            
            if job_id:
                job = upload_job_manager.update_job_progress(
                    job_id, 65.0, UploadStage.ANALYZING, "Analysiere Dokumentinhalt mit Docling"
                )
                if job:
                    await send_upload_progress_to_document_sync(job_id, job)
            
            # Process document with Docling (with defensive file protection)
            docling_chunks = []
            file_backup_path = None
            try:
                if self.docling_service:
                    # DEFENSIVE STRATEGY: Create backup before Docling processing to prevent file loss
                    import shutil
                    file_backup_path = file_path.with_suffix(f".backup{file_path.suffix}")
                    shutil.copy2(file_path, file_backup_path)
                    logger.info(f"Created defensive backup: {file_backup_path}")
                    
                    # Verify original file exists before processing
                    if not file_path.exists():
                        raise Exception(f"Original file disappeared before processing: {file_path}")
                    
                    original_size = file_path.stat().st_size
                    logger.info(f"Processing {document.filename} ({original_size} bytes) with Docling")
                    
                    docling_chunks = await self.docling_service.process_document(
                        str(file_path),
                        doctype="general"
                    )
                    
                    # DEFENSIVE CHECK: Verify original file still exists after Docling processing
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
                        await send_upload_progress_to_document_sync(job_id, job)
                
            except Exception as docling_error:
                # In case of error, restore from backup if file is missing
                if file_backup_path and file_backup_path.exists():
                    if not file_path.exists():
                        logger.info(f"🔄 Restoring file from backup after error: {file_backup_path} -> {file_path}")
                        try:
                            import shutil
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
            
            # Save chunks to database
            if docling_chunks and self.chunk_service:
                try:
                    if job_id:
                        job = upload_job_manager.update_job_progress(
                            job_id, 90.0, UploadStage.PROCESSING, "Speichere Chunks in Datenbank"
                        )
                        if job:
                            await send_upload_progress_to_document_sync(job_id, job)
                    
                    db_chunks = await self.chunk_service.create_chunks_from_docling(
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
                        embedded_chunks = await embedding_service.embed_chunks(chunks_for_embedding)
                        
                        if job_id:
                            job = upload_job_manager.update_job_progress(
                                job_id, 95.0, UploadStage.PROCESSING, "Speichere in Vektor-Datenbank"
                            )
                            if job:
                                await send_upload_progress_to_document_sync(job_id, job)
                        
                        # Store in ChromaDB
                        vector_store = await self._get_vector_store_service()
                        await vector_store.store_chunks(embedded_chunks, str(document.id))
                        
                        embedding_chunks = len(embedded_chunks)
                        logger.info(f"✅ Created {embedding_chunks} embeddings and stored in ChromaDB for {document.filename}")
                        
                    except Exception as embedding_error:
                        logger.warning(f"Embedding creation failed for {document.filename}: {str(embedding_error)}")
                        # Continue processing - embeddings are optional for basic document storage
                    
                    # Update document metadata
                    document.chunk_count = len(db_chunks)
                    document.processing_metadata.update({
                        "processing_completed_at": datetime.utcnow().isoformat(),
                        "total_chunks": len(db_chunks),
                        "chunk_types": list(set(chunk.chunk_type.value for chunk in db_chunks)),
                        "total_words": sum(chunk.word_count or 0 for chunk in db_chunks),
                        "total_chars": sum(chunk.char_count or 0 for chunk in db_chunks),
                        "embeddings_created": embedding_chunks,
                        "vector_store_enabled": embedding_chunks > 0
                    })
                    
                except Exception as chunk_error:
                    raise Exception(f"Chunk creation error: {str(chunk_error)}")
            else:
                logger.warning(f"No chunks created for {document.filename}")
                document.processing_metadata.update({
                    "processing_completed_at": datetime.utcnow().isoformat(),
                    "total_chunks": 0,
                    "warning": "No extractable content found"
                })
            
            # Update final status
            document.status = DocumentStatus.READY.value
            document.processed_at = datetime.utcnow()
            await db.flush()
            
            # Complete progress tracking
            if job_id:
                completed_job = upload_job_manager.complete_job(job_id, document.chunk_count or 0)
                if completed_job:
                    await send_upload_progress_to_document_sync(job_id, completed_job)
            
            logger.info(f"✅ Completed Docling processing for {document.filename}: {document.chunk_count} chunks")
            
        except Exception as e:
            # Update document with error status
            document.status = DocumentStatus.ERROR.value
            document.error_message = str(e)
            document.processing_metadata.update({
                "processing_failed_at": datetime.utcnow().isoformat(),
                "error": str(e)
            })
            await db.flush()
            
            # Update progress tracking with error
            if job_id:
                failed_job = upload_job_manager.fail_job(job_id, f"Verarbeitung fehlgeschlagen: {str(e)}")
                if failed_job:
                    await send_upload_progress_to_document_sync(job_id, failed_job)
            
            logger.error(f"❌ Docling processing failed for {document.filename}: {str(e)}")
            raise

    async def reprocess_document(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> Optional[Document]:
        """
        Reprocess document with Docling (useful for fixing failed processing)
        
        Args:
            db: Database session
            document_id: Document UUID
            
        Returns:
            Updated document or None if not found
        """
        try:
            document = await self.get_document_by_id(db, document_id)
            if not document:
                return None
            
            # Get file path
            file_path = self.storage_root / document.storage_path
            if not file_path.exists():
                raise ValueError(f"Document file not found: {file_path}")
            
            # Delete existing chunks
            if self.chunk_service:
                try:
                    await self.chunk_service.delete_chunks_by_document(db, document_id)
                    logger.info(f"Deleted existing chunks for document {document_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete chunks for document {document_id}: {str(e)}")
            
            # Reprocess with Docling
            await self._process_document_with_docling(db, document, file_path)
            
            await db.refresh(document)
            logger.info(f"Reprocessed document: {document.filename}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to reprocess document {document_id}: {str(e)}")
            await db.rollback()
            raise

