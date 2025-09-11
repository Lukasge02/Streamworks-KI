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
            
            # Process document with Docling
            try:
                await self.processor.process_document_with_docling(
                    db, document, file_path, job_id
                )
            except Exception as processing_error:
                logger.warning(f"Document processing failed for {file.filename}: {str(processing_error)}")
                # Document is still saved, just without processing
            
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
        """Delete document and its file"""
        try:
            # Get document info
            document = await self.crud.get_document_by_id(db, document_id)
            if not document:
                return False
            
            # Delete from database
            success = await self.crud.delete_document(db, document_id)
            
            if success:
                # Delete file from storage
                self.storage.delete_file(document.filename)
                logger.info(f"Deleted document and file: {document_id}")
            
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
        """Delete multiple documents"""
        # Get all documents first to track files for deletion
        documents_to_delete = []
        for doc_id in document_ids:
            doc = await self.crud.get_document_by_id(db, doc_id)
            if doc:
                documents_to_delete.append(doc)
        
        # Delete from database
        result = await self.crud.bulk_delete_documents(db, document_ids)
        
        # Delete files for successfully deleted documents
        for doc in documents_to_delete:
            if str(doc.id) in result.deleted:
                try:
                    self.storage.delete_file(doc.filename)
                except Exception as e:
                    logger.warning(f"Failed to delete file for document {doc.id}: {str(e)}")
        
        return result

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