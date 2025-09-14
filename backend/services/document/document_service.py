"""
Document Service (Orchestrator)
Main service that coordinates all document operations using specialized modules
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Document
from schemas.core import (
    DocumentUpdate, DocumentWithFolder, DocumentFilter, DocumentSort,
    BulkDeleteResponse, BulkMoveResponse
)

from .storage_handler import DocumentStorageHandler
from .crud_operations import DocumentCrudOperations
from .processing_pipeline import DocumentProcessingPipeline
# DocumentChunkService removed - using direct Docling chunking

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Main document service that orchestrates all document operations
    Uses specialized modules for storage, CRUD, and processing
    """
    
    def __init__(self):
        # Initialize specialized modules
        self.storage = DocumentStorageHandler()
        self.crud = DocumentCrudOperations()
        self.processor = DocumentProcessingPipeline()
        # DocumentChunkService removed - chunking handled by Docling in processor
    
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
        Upload a document with full processing pipeline
        
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
            # Read file content
            content = await file.read()
            if not content:
                raise ValueError("Empty file")
            
            # Calculate file hash
            file_hash = self.storage.calculate_file_hash(content)
            
            # Check for duplicates
            existing_doc = await self.crud.get_document_by_hash(db, file_hash)
            if existing_doc:
                logger.info(f"Duplicate file detected: {file.filename} (hash: {file_hash[:8]})")
                return existing_doc
            
            # Generate storage path and save file
            storage_path = self.storage.generate_storage_path(file.filename, file_hash)
            file_path = self.storage.save_file(content, storage_path)
            
            # Detect MIME type
            mime_type = self.storage.detect_mime_type(file.filename, content)
            
            # Create document record
            document = await self.crud.create_document(
                db=db,
                filename=storage_path,
                original_filename=file.filename,
                folder_id=folder_id,
                file_hash=file_hash,
                file_size=len(content),
                mime_type=mime_type,
                tags=tags,
                description=description
            )
            
            # Process document with LlamaIndex RAG pipeline
            try:
                await self.processor.process_document_with_llamaindex(
                    db, document, file_path, job_id
                )
            except Exception as processing_error:
                logger.warning(f"Document processing failed for {file.filename}: {str(processing_error)}")
                # Update document status to ERROR when processing fails
                from models.core import DocumentStatus
                document.status = DocumentStatus.ERROR.value
                document.error_message = str(processing_error)
                await db.commit()
                logger.info(f"Document {document.id} marked as ERROR due to processing failure")
            
            return document
            
        except Exception as e:
            logger.error(f"Upload failed for {file.filename}: {str(e)}")
            raise

    async def get_document_by_id(
        self,
        db: AsyncSession,
        document_id: UUID,
        include_folder: bool = False
    ) -> Optional[Document]:
        """Get document by ID"""
        return await self.crud.get_document_by_id(db, document_id, include_folder)

    async def get_documents_list(
        self,
        db: AsyncSession,
        folder_id: Optional[UUID] = None,
        filters: Optional[DocumentFilter] = None,
        sort: DocumentSort = DocumentSort.CREATED_DESC,
        page: int = 1,
        per_page: int = 50
    ) -> List[DocumentWithFolder]:
        """Get paginated list of documents"""
        return await self.crud.get_documents_list(db, folder_id, filters, sort, page, per_page)

    async def update_document(
        self,
        db: AsyncSession,
        document_id: UUID,
        update_data: DocumentUpdate
    ) -> Optional[Document]:
        """Update document metadata"""
        return await self.crud.update_document(db, document_id, update_data)

    async def delete_document(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> bool:
        """Delete document and its file with complete cleanup"""
        try:
            # Get document info
            document = await self.crud.get_document_by_id(db, document_id)
            if not document:
                return False
            
            logger.info(f"Starting comprehensive deletion for document: {document_id}")
            
            # Step 1: Delete document chunks - handled by vector database cleanup
            # DocumentChunkService removed - chunks are managed by vector database
            chunk_count = 0
            logger.info("Chunk deletion handled by vector database cleanup")
            
            # Step 2: Delete from vector database (LlamaIndex RAG Service)
            try:
                from services.llamaindex_rag_service import get_rag_service
                rag_service = await get_rag_service()
                await rag_service.delete_document(str(document_id))
                logger.info(f"Deleted vectors from ChromaDB for document: {document_id}")
            except Exception as vector_error:
                logger.error(f"Failed to delete from vector store: {str(vector_error)}")
                # Continue with deletion - orphaned vectors can be cleaned up later

            # Step 2.5: Delete from Supabase mirror (for UI debugging)
            try:
                from services.supabase_mirror_service import get_supabase_mirror_service
                mirror_service = get_supabase_mirror_service()

                if mirror_service.is_enabled():
                    mirror_success = await mirror_service.mirror_document_deletion(str(document_id))
                    if mirror_success:
                        logger.info(f"✅ Supabase mirror cleanup completed for document: {document_id}")
                    else:
                        logger.warning(f"⚠️ Supabase mirror cleanup failed for document: {document_id}")
                else:
                    logger.info(f"📊 Supabase mirror disabled - skipping deletion cleanup")

            except Exception as mirror_error:
                logger.warning(f"⚠️ Supabase mirror deletion failed (non-critical): {str(mirror_error)}")
                # Continue - mirror failures shouldn't block document deletion
            
            # Step 3: Delete document from database
            success = await self.crud.delete_document(db, document_id)
            
            if success:
                # Step 4: Delete file from storage
                try:
                    self.storage.delete_file(document.filename)
                    logger.info(f"Deleted file from storage: {document.filename}")
                except Exception as file_error:
                    logger.warning(f"Failed to delete file: {str(file_error)}")
                
                logger.info(f"✅ Complete deletion successful for document: {document_id} (chunks: {chunk_count})")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            raise

    async def get_document_file(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> Optional[Tuple[Path, str, str]]:
        """
        Get file path, filename, and MIME type for document
        
        Returns:
            Tuple of (file_path, original_filename, mime_type) or None
        """
        try:
            document = await self.crud.get_document_by_id(db, document_id)
            if not document:
                return None
            
            file_path = self.storage.get_file_path(document.filename)
            if not self.storage.file_exists(document.filename):
                logger.warning(f"File not found for document {document_id}: {file_path}")
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
        """Delete multiple documents with complete cleanup"""
        logger.info(f"Starting bulk deletion for {len(document_ids)} documents")
        
        # Use individual delete method to ensure proper cleanup
        deleted = []
        failed = []
        
        for doc_id in document_ids:
            try:
                success = await self.delete_document(db, doc_id)
                if success:
                    deleted.append(str(doc_id))
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
                logger.error(f"Failed to delete document {doc_id}: {str(e)}")
        
        logger.info(f"Bulk deletion completed: {len(deleted)} deleted, {len(failed)} failed")
        
        return BulkDeleteResponse(
            deleted=deleted,
            failed=failed,
            total_requested=len(document_ids),
            total_deleted=len(deleted),
            total_failed=len(failed)
        )

    async def bulk_move_documents(
        self,
        db: AsyncSession,
        document_ids: List[UUID],
        target_folder_id: UUID
    ) -> BulkMoveResponse:
        """Move multiple documents to target folder"""
        return await self.crud.bulk_move_documents(db, document_ids, target_folder_id)

    async def reprocess_document(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> Optional[Document]:
        """Reprocess document with Docling"""
        try:
            # Get document
            document = await self.crud.get_document_by_id(db, document_id)
            if not document:
                return None
            
            # Check if file exists
            file_path = self.storage.get_file_path(document.filename)
            if not self.storage.file_exists(document.filename):
                raise ValueError(f"File not found: {document.filename}")
            
            # Reprocess
            await self.processor.reprocess_document(db, document, file_path)
            
            # Return updated document
            return await self.crud.get_document_by_id(db, document_id)
            
        except Exception as e:
            logger.error(f"Failed to reprocess document {document_id}: {str(e)}")
            raise