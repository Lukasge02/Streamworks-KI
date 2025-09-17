"""
Document Service (Orchestrator)
Main service that coordinates all document operations using specialized modules
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime

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
        Upload a document with transactional consistency between DB and Qdrant

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
        document = None
        qdrant_created = False
        file_saved = False
        temp_file_path = None

        try:
            logger.info(f"🚀 Starting transactional document upload: {file.filename}")

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

            # Generate storage path and save file FIRST (reversible)
            storage_path = self.storage.generate_storage_path(file.filename, file_hash)
            file_path = self.storage.save_file(content, storage_path)
            file_saved = True
            temp_file_path = file_path

            # Detect MIME type
            mime_type = self.storage.detect_mime_type(file.filename, content)

            # Step 1: Process document with Qdrant FIRST (fail-fast approach)
            logger.info(f"📝 Step 1: Processing document with Qdrant pipeline...")
            try:
                from services.qdrant_rag_service import get_rag_service
                rag_service = await get_rag_service()

                # Generate a temporary document ID for Qdrant processing
                import uuid
                temp_doc_id = str(uuid.uuid4())

                # Process document and store in Qdrant
                chunks = await rag_service.process_document(
                    file_path=file_path,
                    doc_id=temp_doc_id,
                    doctype="general"
                )

                if not chunks:
                    raise ValueError("Document processing failed - no chunks generated")

                qdrant_created = True
                logger.info(f"✅ Step 1 completed: {len(chunks)} chunks stored in Qdrant with temp ID: {temp_doc_id}")

            except Exception as qdrant_error:
                logger.error(f"❌ Step 1 failed - Qdrant processing error: {str(qdrant_error)}")
                raise ValueError(f"Document processing failed: {str(qdrant_error)}")

            # Step 2: Create database record with REAL document ID
            logger.info(f"📝 Step 2: Creating database record...")
            try:
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

                # Commit database transaction
                await db.commit()
                logger.info(f"✅ Step 2 completed: Database record created with ID: {document.id}")

            except Exception as db_error:
                logger.error(f"❌ Step 2 failed - Database error: {str(db_error)}")
                await db.rollback()
                raise ValueError(f"Database creation failed: {str(db_error)}")

            # Step 3: Update Qdrant chunks with real document ID
            logger.info(f"📝 Step 3: Updating Qdrant chunks with real document ID...")
            try:
                # Delete temp chunks and recreate with real ID
                await rag_service.delete_document(temp_doc_id)

                # Recreate chunks with real document ID
                real_chunks = await rag_service.process_document(
                    file_path=file_path,
                    doc_id=str(document.id),
                    doctype="general"
                )

                if not real_chunks:
                    raise ValueError("Failed to recreate chunks with real document ID")

                # Update document status and chunk count in database
                document.status = "ready"
                document.chunk_count = len(real_chunks)
                document.processed_at = datetime.now()
                await db.commit()

                logger.info(f"✅ Step 3 completed: {len(real_chunks)} chunks updated with real ID: {document.id}")

            except Exception as update_error:
                logger.error(f"❌ Step 3 failed - Chunk update error: {str(update_error)}")
                # This is critical - we have DB record but inconsistent Qdrant state
                # Mark document as ERROR but don't fail the upload
                document.status = "error"
                document.error_message = f"Qdrant sync failed: {str(update_error)}"
                await db.commit()

                logger.warning(f"⚠️ Document {document.id} created but Qdrant sync failed - marked as ERROR")

            logger.info(f"🎯 Transactional upload completed successfully: {file.filename} → {document.id}")
            return document

        except Exception as e:
            logger.error(f"❌ Transactional upload failed for {file.filename}: {str(e)}")

            # Rollback operations in reverse order
            if document and qdrant_created:
                try:
                    # Delete from Qdrant if it was created
                    rag_service = await get_rag_service()
                    await rag_service.delete_document(str(document.id))
                    logger.info(f"🔄 Rollback: Deleted Qdrant chunks for {document.id}")
                except Exception as rollback_error:
                    logger.warning(f"⚠️ Rollback failed - Qdrant cleanup error: {str(rollback_error)}")

            if document:
                try:
                    # Delete from database if it was created
                    await self.crud.delete_document(db, document.id)
                    await db.commit()
                    logger.info(f"🔄 Rollback: Deleted database record for {document.id}")
                except Exception as rollback_error:
                    logger.warning(f"⚠️ Rollback failed - Database cleanup error: {str(rollback_error)}")

            if file_saved and temp_file_path:
                try:
                    # Delete file if it was saved
                    self.storage.delete_file(storage_path)
                    logger.info(f"🔄 Rollback: Deleted file {storage_path}")
                except Exception as rollback_error:
                    logger.warning(f"⚠️ Rollback failed - File cleanup error: {str(rollback_error)}")

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
        document_id: UUID,
        force: bool = False
    ) -> bool:
        """
        Delete document with robust consistency guarantees

        Uses database-first deletion strategy to prevent orphaned Qdrant chunks

        Args:
            db: Database session
            document_id: Document UUID to delete
            force: If True, ignore Qdrant errors and complete deletion

        Returns:
            Success status
        """
        document = None
        db_deleted = False

        try:
            logger.info(f"🗑️ Starting robust document deletion: {document_id} (force={force})")

            # Get document info
            document = await self.crud.get_document_by_id(db, document_id)
            if not document:
                logger.warning(f"⚠️ Document {document_id} not found in database")
                return False

            filename = document.filename
            original_filename = document.original_filename

            # Step 1: Delete from database FIRST (prevents orphaned chunks)
            logger.info(f"📝 Step 1: Deleting database record for {document_id}")
            try:
                db_success = await self.crud.delete_document(db, document_id)
                if not db_success:
                    raise ValueError("Database deletion failed")

                # Commit database transaction immediately
                await db.commit()
                db_deleted = True
                logger.info(f"✅ Step 1 completed: Database record deleted for {document_id}")

            except Exception as db_error:
                logger.error(f"❌ Step 1 failed - Database deletion error: {str(db_error)}")
                await db.rollback()
                if not force:
                    raise ValueError(f"Database deletion failed: {str(db_error)}")

            # Step 2: Delete from Qdrant (can retry if fails)
            logger.info(f"📝 Step 2: Deleting Qdrant chunks for {document_id}")
            vector_deletion_success = False
            try:
                from services.qdrant_rag_service import get_rag_service
                rag_service = await get_rag_service()
                vector_deletion_success = await rag_service.delete_document(str(document_id))

                if vector_deletion_success:
                    logger.info(f"✅ Step 2 completed: Qdrant chunks deleted for {document_id}")
                else:
                    logger.warning(f"⚠️ Step 2 partial: Qdrant deletion returned false for {document_id}")

            except Exception as vector_error:
                logger.error(f"❌ Step 2 failed - Qdrant deletion error: {str(vector_error)}")
                if not force:
                    logger.error(f"❌ Critical inconsistency: Document {document_id} deleted from DB but not from Qdrant")
                    # Log this as a consistency issue for later cleanup
                    await self._log_consistency_issue(document_id, "orphaned_chunks", str(vector_error))

            # Step 3: Delete from Supabase mirror (non-critical)
            try:
                from services.supabase_mirror_service import get_supabase_mirror_service
                mirror_service = get_supabase_mirror_service()

                if mirror_service.is_enabled():
                    mirror_success = await mirror_service.mirror_document_deletion(str(document_id))
                    if mirror_success:
                        logger.info(f"✅ Step 3 completed: Supabase mirror cleanup for {document_id}")
                    else:
                        logger.warning(f"⚠️ Step 3 failed: Supabase mirror cleanup failed for {document_id}")
                else:
                    logger.info(f"📊 Step 3 skipped: Supabase mirror disabled")

            except Exception as mirror_error:
                logger.warning(f"⚠️ Step 3 failed (non-critical): Supabase mirror error: {str(mirror_error)}")

            # Step 4: Delete file from storage (non-critical)
            logger.info(f"📝 Step 4: Deleting file from storage for {document_id}")
            try:
                self.storage.delete_file(filename)
                logger.info(f"✅ Step 4 completed: File deleted from storage: {filename}")
            except Exception as file_error:
                logger.warning(f"⚠️ Step 4 failed (non-critical): File deletion error: {str(file_error)}")

            # Final status
            overall_success = db_deleted and (vector_deletion_success or force)
            consistency_status = "✅ consistent" if vector_deletion_success else "⚠️ potential_orphaned_chunks"

            logger.info(f"🎯 Robust deletion completed for {document_id}: "
                       f"DB={'✅' if db_deleted else '❌'}, "
                       f"Qdrant={'✅' if vector_deletion_success else '❌'}, "
                       f"Status={consistency_status}")

            return overall_success

        except Exception as e:
            logger.error(f"❌ Robust deletion failed for {document_id}: {str(e)}")

            # Rollback strategy: If database was deleted but process failed, log for manual cleanup
            if db_deleted:
                logger.critical(f"🚨 CRITICAL: Document {document_id} was deleted from database but cleanup failed. Manual intervention may be required.")
                await self._log_consistency_issue(document_id, "incomplete_deletion", str(e))

            if not force:
                raise

            return False

    async def _log_consistency_issue(self, document_id: UUID, issue_type: str, details: str):
        """Log consistency issues for later cleanup"""
        try:
            # In a production system, this would write to a dedicated consistency log table
            logger.warning(f"🔍 CONSISTENCY ISSUE LOGGED: {issue_type} for document {document_id}: {details}")

            # For now, we just log it - in production you'd want to store this in a table
            # for automated cleanup jobs to process

        except Exception as log_error:
            logger.error(f"Failed to log consistency issue: {str(log_error)}")

    async def safe_delete_document(
        self,
        db: AsyncSession,
        document_id: UUID
    ) -> bool:
        """
        Safe deletion with automatic consistency checking

        This method performs deletion and then verifies consistency
        """
        try:
            # Perform deletion
            success = await self.delete_document(db, document_id, force=False)

            if success:
                # Verify consistency after deletion
                await self._verify_deletion_consistency(document_id)

            return success

        except Exception as e:
            logger.error(f"Safe deletion failed for {document_id}: {str(e)}")
            raise

    async def _verify_deletion_consistency(self, document_id: UUID):
        """Verify that document was completely deleted from all systems"""
        try:
            from services.qdrant_rag_service import get_rag_service
            rag_service = await get_rag_service()

            # Check if chunks still exist in Qdrant
            chunks = await rag_service.qdrant_service.get_document_chunks(str(document_id), limit=1)

            if chunks and len(chunks) > 0:
                logger.warning(f"⚠️ CONSISTENCY VERIFICATION FAILED: Document {document_id} still has {len(chunks)} chunks in Qdrant after deletion")
                await self._log_consistency_issue(document_id, "deletion_verification_failed", f"{len(chunks)} chunks remain")

                # Try cleanup again
                cleanup_success = await rag_service.delete_document(str(document_id))
                if cleanup_success:
                    logger.info(f"✅ Consistency repair successful: Cleaned up remaining chunks for {document_id}")
                else:
                    logger.error(f"❌ Consistency repair failed: Could not clean up remaining chunks for {document_id}")
            else:
                logger.info(f"✅ Deletion consistency verified: No remaining chunks for {document_id}")

        except Exception as verify_error:
            logger.warning(f"⚠️ Could not verify deletion consistency for {document_id}: {str(verify_error)}")

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
        """Delete multiple documents with optimized Qdrant cleanup"""
        import time
        start_time = time.time()

        logger.info(f"🗑️ Starting optimized bulk deletion for {len(document_ids)} documents")

        # Convert UUIDs to strings for Qdrant operations
        doc_id_strings = [str(doc_id) for doc_id in document_ids]

        # Step 1: Bulk delete from Qdrant vector store first (most efficient)
        vector_deletion_results = {}
        try:
            from services.qdrant_rag_service import get_rag_service
            rag_service = await get_rag_service()

            # Use optimized bulk deletion
            bulk_results = await rag_service.delete_documents_bulk(doc_id_strings)

            # Map results
            for doc_id in bulk_results["success"]:
                vector_deletion_results[doc_id] = True

            for failed_item in bulk_results["failed"]:
                if isinstance(failed_item, dict) and "doc_id" in failed_item:
                    vector_deletion_results[failed_item["doc_id"]] = False

            logger.info(f"✅ Qdrant bulk deletion completed: {bulk_results['total_deleted']}/{bulk_results['total_requested']} deleted")

        except Exception as vector_error:
            logger.error(f"❌ Qdrant bulk deletion failed: {str(vector_error)}")
            # Continue with individual deletion fallback
            for doc_id in doc_id_strings:
                vector_deletion_results[doc_id] = False

        # Step 2: Process database deletions (can't be easily batched due to file cleanup)
        deleted = []
        failed = []

        for doc_id in document_ids:
            doc_id_str = str(doc_id)
            try:
                # Get document info for file cleanup
                document = await self.crud.get_document_by_id(db, doc_id)
                if not document:
                    failed.append({
                        "id": doc_id_str,
                        "error": "Document not found"
                    })
                    continue

                # Delete document from database
                db_success = await self.crud.delete_document(db, doc_id)

                if db_success:
                    # Clean up file from storage
                    try:
                        self.storage.delete_file(document.filename)
                        logger.debug(f"✅ File deleted: {document.filename}")
                    except Exception as file_error:
                        logger.warning(f"⚠️ File deletion failed for {document.filename}: {str(file_error)}")

                    # Clean up Supabase mirror
                    try:
                        from services.supabase_mirror_service import get_supabase_mirror_service
                        mirror_service = get_supabase_mirror_service()
                        if mirror_service.is_enabled():
                            await mirror_service.mirror_document_deletion(doc_id_str)
                    except Exception as mirror_error:
                        logger.warning(f"⚠️ Supabase mirror cleanup failed for {doc_id_str}: {str(mirror_error)}")

                    deleted.append(doc_id_str)
                    vector_success = vector_deletion_results.get(doc_id_str, False)
                    logger.debug(f"✅ Complete deletion for {doc_id_str} (DB: ✅, Qdrant: {'✅' if vector_success else '❌'})")
                else:
                    failed.append({
                        "id": doc_id_str,
                        "error": "Database deletion failed"
                    })

            except Exception as e:
                failed.append({
                    "id": doc_id_str,
                    "error": str(e)
                })
                logger.error(f"❌ Failed to delete document {doc_id}: {str(e)}")

        processing_time = time.time() - start_time
        success_rate = (len(deleted) / len(document_ids)) * 100 if document_ids else 0

        logger.info(f"✅ Bulk deletion completed: {len(deleted)}/{len(document_ids)} deleted ({success_rate:.1f}% success rate) in {processing_time:.2f}s")

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