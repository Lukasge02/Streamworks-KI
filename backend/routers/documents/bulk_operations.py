"""
Document Bulk Operations Router
Handles bulk delete, move, and reprocessing operations
"""

import logging
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from schemas.core import (
    BulkDeleteRequest, BulkDeleteResponse,
    BulkMoveRequest, BulkMoveResponse, BulkReprocessRequest
)
from services.document_service import DocumentService

# Shared dependencies
def get_document_service() -> DocumentService:
    """Dependency to get DocumentService instance"""
    return DocumentService()

logger = logging.getLogger(__name__)

# Create sub-router for bulk operations
router = APIRouter()


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_documents(
    request: BulkDeleteRequest,
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Delete multiple documents in batch
    
    - **document_ids**: List of document UUIDs to delete
    """
    try:
        result = await doc_service.bulk_delete_documents(db, request.document_ids)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk delete failed: {str(e)}")


@router.post("/bulk-move", response_model=BulkMoveResponse)
async def bulk_move_documents(
    request: BulkMoveRequest,
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Move multiple documents to a target folder
    
    - **document_ids**: List of document UUIDs to move
    - **target_folder_id**: Target folder UUID
    """
    try:
        result = await doc_service.bulk_move_documents(
            db, request.document_ids, request.target_folder_id
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk move failed: {str(e)}")


@router.post("/reprocess-empty-chunks")
async def reprocess_documents_with_empty_chunks(
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Automatically reprocess all ready documents that have 0 chunks
    """
    try:
        from sqlalchemy import select
        from models.core import Document
        
        # Find all ready documents with 0 chunks
        query = select(Document).where(
            (Document.status == 'ready') &
            (Document.chunk_count == 0)
        )
        
        result = await db.execute(query)
        documents = result.scalars().all()
        
        reprocessed = []
        failed = []
        
        logger.info(f"Found {len(documents)} documents with 0 chunks to reprocess")
        
        for document in documents:
            try:
                reprocessed_doc = await doc_service.reprocess_document(db, document.id)
                if reprocessed_doc:
                    reprocessed.append({
                        "id": str(document.id),
                        "filename": document.filename,
                        "new_chunk_count": reprocessed_doc.chunk_count
                    })
                    logger.info(f"Reprocessed {document.filename}: {reprocessed_doc.chunk_count} chunks")
            except Exception as e:
                failed.append({
                    "id": str(document.id),
                    "filename": document.filename,
                    "error": str(e)
                })
                logger.error(f"Failed to reprocess {document.filename}: {str(e)}")
        
        return {
            "message": "Bulk reprocessing completed",
            "total_found": len(documents),
            "reprocessed": reprocessed,
            "failed": failed,
            "success_count": len(reprocessed),
            "failure_count": len(failed)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk reprocess failed: {str(e)}")


@router.post("/bulk-reprocess")
async def bulk_reprocess_documents(
    request: BulkReprocessRequest,
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Reprocess multiple documents with Docling/OCR
    
    - **document_ids**: List of document UUIDs to reprocess
    """
    try:
        reprocessed = []
        failed = []
        
        for document_id in request.document_ids:
            try:
                document = await doc_service.reprocess_document(db, document_id)
                if document:
                    reprocessed.append(str(document_id))
                else:
                    failed.append({
                        "id": str(document_id),
                        "error": "Document not found"
                    })
            except Exception as e:
                failed.append({
                    "id": str(document_id),
                    "error": str(e)
                })
        
        return {
            "reprocessed": reprocessed,
            "failed": failed,
            "total_requested": len(request.document_ids),
            "total_reprocessed": len(reprocessed),
            "total_failed": len(failed)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk reprocess failed: {str(e)}")


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Reprocess document with Docling (useful for fixing failed processing)
    
    - **document_id**: Document UUID
    """
    try:
        document = await doc_service.reprocess_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "message": f"Document reprocessing initiated",
            "document_id": str(document.id),
            "filename": document.filename,
            "status": document.status.value if hasattr(document.status, 'value') else document.status,
            "chunk_count": document.chunk_count,
            "processing_metadata": document.processing_metadata
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reprocess document: {str(e)}")