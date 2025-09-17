"""
Document Chunk Management Router - Qdrant Integration
Handles chunk-related operations using Qdrant as the single source of truth
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from services.document import DocumentService
from services.qdrant_vectorstore import get_qdrant_service

# Shared dependencies
def get_document_service() -> DocumentService:
    """Dependency to get DocumentService instance"""
    return DocumentService()

async def get_qdrant_service_instance():
    """Dependency to get Qdrant service instance"""
    return await get_qdrant_service()

logger = logging.getLogger(__name__)

# Create sub-router for chunk operations
router = APIRouter()


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service),
    qdrant_service = Depends(get_qdrant_service_instance)
):
    """
    Get chunks for a specific document from Qdrant vector store

    - **document_id**: Document UUID
    - **page**: Page number (1-based)
    - **per_page**: Items per page (1-200)
    """
    try:
        # Validate document exists in PostgreSQL
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_id_str = str(document_id)

        # Get chunks directly from Qdrant vector store
        try:
            chunks = await qdrant_service.get_document_chunks(
                doc_id=doc_id_str,
                limit=1000,  # Get all chunks first, then paginate
                offset=0
            )

            if chunks:
                logger.info(f"✅ Retrieved {len(chunks)} chunks from Qdrant for document {doc_id_str}")
            else:
                # No chunks found in Qdrant
                return {
                    "chunks": [],
                    "total_chunks": 0,
                    "page": page,
                    "per_page": per_page,
                    "error": "No chunks found - document may still be processing",
                    "document_status": document.status if document else "unknown"
                }

            # Apply pagination to Qdrant results
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_chunks = chunks[start_idx:end_idx]

            return {
                "chunks": paginated_chunks,
                "total_chunks": len(chunks),
                "page": page,
                "per_page": per_page,
                "document_id": doc_id_str,
                "source": "qdrant"
            }

        except Exception as qdrant_error:
            logger.error(f"Failed to retrieve chunks from Qdrant for document {doc_id_str}: {str(qdrant_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve chunks from vector store: {str(qdrant_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chunks: {str(e)}")


@router.get("/{document_id}/processing-status")
async def get_document_processing_status(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Get document processing status and metadata

    - **document_id**: Document UUID
    """
    try:
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return {
            "document_id": str(document.id),
            "filename": document.filename,
            "status": document.status.value if hasattr(document.status, 'value') else document.status,
            "chunk_count": document.chunk_count,
            "processing_metadata": document.processing_metadata,
            "processed_at": document.processed_at,
            "error_message": document.error_message,
            "created_at": document.created_at,
            "updated_at": document.updated_at
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get processing status: {str(e)}")