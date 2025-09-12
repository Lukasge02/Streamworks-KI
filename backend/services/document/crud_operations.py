"""
Document CRUD Operations
Handles database operations for documents: create, read, update, delete
"""

import logging
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.core import Document, Folder, DocumentStatus
from schemas.core import (
    DocumentUpdate, DocumentWithFolder, DocumentFilter, DocumentSort,
    BulkDeleteResponse, BulkMoveResponse
)
from services.folder_service import FolderService

logger = logging.getLogger(__name__)


class DocumentCrudOperations:
    """
    Handles CRUD operations for documents in the database
    """
    
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

    async def get_document_by_hash(
        self,
        db: AsyncSession,
        file_hash: str
    ) -> Optional[Document]:
        """Get document by file hash to detect duplicates"""
        try:
            result = await db.execute(
                select(Document).where(Document.file_hash == file_hash)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get document by hash {file_hash}: {str(e)}")
            return None

    async def create_document(
        self,
        db: AsyncSession,
        filename: str,
        original_filename: str,
        folder_id: UUID,
        file_hash: str,
        file_size: int,
        mime_type: str,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Document:
        """
        Create new document record in database
        
        Args:
            db: Database session
            filename: Storage filename
            original_filename: Original uploaded filename
            folder_id: Target folder ID
            file_hash: SHA-256 hash of file content
            file_size: File size in bytes
            mime_type: MIME type
            tags: Optional tags list
            description: Optional description
            
        Returns:
            Created document record
        """
        try:
            document = Document(
                filename=filename,
                original_filename=original_filename,
                folder_id=folder_id,
                file_hash=file_hash,
                file_size=file_size,
                mime_type=mime_type,
                storage_path=filename,  # Use same path for both fields
                status=DocumentStatus.UPLOADING.value,
                tags=tags or [],
                description=description,
                chunk_count=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            logger.info(f"Created document: {document.id} - {document.filename}")
            return document
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create document: {str(e)}")
            raise

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
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise e

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
            document_id: Document UUID
            update_data: Update data
            
        Returns:
            Updated document or None if not found
        """
        try:
            # Get existing document
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if not document:
                return None
            
            # Apply updates
            if update_data.filename is not None:
                document.filename = update_data.filename
            if update_data.folder_id is not None:
                # Validate folder exists
                folder_service = FolderService()
                folder = await folder_service.get_folder_by_id(db, update_data.folder_id)
                if not folder:
                    raise ValueError(f"Folder {update_data.folder_id} not found")
                document.folder_id = update_data.folder_id
            if update_data.tags is not None:
                document.tags = update_data.tags
            if update_data.description is not None:
                document.description = update_data.description
            
            document.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(document)
            
            logger.info(f"Updated document: {document.id}")
            return document
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update document {document_id}: {str(e)}")
            raise

    async def delete_document(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> bool:
        """
        Delete document from database
        
        Args:
            db: Database session
            document_id: Document UUID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Get document
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if not document:
                return False
            
            # Delete from database
            await db.delete(document)
            await db.commit()
            
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            raise

    async def bulk_delete_documents(
        self,
        db: AsyncSession,
        document_ids: List[UUID]
    ) -> BulkDeleteResponse:
        """
        Delete multiple documents in batch
        
        Args:
            db: Database session
            document_ids: List of document UUIDs to delete
            
        Returns:
            Bulk delete response with success/failure counts
        """
        deleted = []
        failed = []
        
        for doc_id in document_ids:
            try:
                if await self.delete_document(db, doc_id):
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
        """
        Move multiple documents to a target folder
        
        Args:
            db: Database session
            document_ids: List of document UUIDs to move
            target_folder_id: Target folder UUID
            
        Returns:
            Bulk move response with success/failure counts
        """
        # Validate target folder
        folder_service = FolderService()
        folder = await folder_service.get_folder_by_id(db, target_folder_id)
        if not folder:
            raise ValueError(f"Target folder {target_folder_id} not found")
        
        moved = []
        failed = []
        
        for doc_id in document_ids:
            try:
                update_data = DocumentUpdate(folder_id=target_folder_id)
                document = await self.update_document(db, doc_id, update_data)
                if document:
                    moved.append(str(doc_id))
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
            target_folder_id=target_folder_id,
            total_requested=len(document_ids),
            total_moved=len(moved),
            total_failed=len(failed)
        )