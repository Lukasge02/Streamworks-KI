"""
Document Chunk Management Router - Supabase PostgreSQL Integration
Handles chunk-related operations using Supabase PostgreSQL as primary source
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from services.document import DocumentService

# Shared dependencies
def get_document_service() -> DocumentService:
    """Dependency to get DocumentService instance"""
    return DocumentService()

logger = logging.getLogger(__name__)

# Create sub-router for chunk operations
router = APIRouter()


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Get chunks for a specific document from Supabase PostgreSQL

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
        chunk_responses = []

        # Try to get chunks from PostgreSQL document_chunks table (primary)
        try:
            from sqlalchemy import select, text
            from models.core import DocumentChunk

            # Query document_chunks table first
            chunks_query = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
            chunks_result = await db.execute(chunks_query)
            chunks = chunks_result.scalars().all()

            if chunks:
                # Use PostgreSQL chunks if available
                for chunk in chunks:
                    chunk_responses.append({
                        "id": str(chunk.id),
                        "document_id": doc_id_str,
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                        "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                        "chunk_type": chunk.chunk_type.value if hasattr(chunk.chunk_type, 'value') else str(chunk.chunk_type),
                        "heading": chunk.heading,
                        "section_name": chunk.section_name,
                        "page_number": chunk.page_number,
                        "metadata": chunk.chunk_metadata if chunk.chunk_metadata else {},
                        "word_count": chunk.word_count,
                        "char_count": chunk.char_count,
                        "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
                        "updated_at": chunk.updated_at.isoformat() if chunk.updated_at else None
                    })

                logger.info(f"✅ Retrieved {len(chunk_responses)} chunks from PostgreSQL document_chunks for document {doc_id_str}")

        except Exception as postgres_error:
            logger.warning(f"PostgreSQL document_chunks failed for document {doc_id_str}: {str(postgres_error)}")

        # Fallback: Use Supabase mirror if no PostgreSQL chunks found
        if not chunk_responses:
            try:
                # Use raw SQL query to get chunk metadata from mirror
                mirror_query = text("""
                    SELECT chunk_id, document_id, content_preview, word_count, chunk_index,
                           processing_status, created_at, updated_at
                    FROM chunk_metadata_mirror
                    WHERE document_id = :doc_id
                    ORDER BY chunk_index
                """)

                # Execute query via SQLAlchemy
                mirror_result = await db.execute(mirror_query, {"doc_id": doc_id_str})
                mirror_rows = mirror_result.fetchall()

                if mirror_rows and len(mirror_rows) > 0:
                    for chunk_data in mirror_rows:
                        content_preview = chunk_data.content_preview or ''
                        chunk_responses.append({
                            "id": chunk_data.chunk_id or f"{doc_id_str}_chunk_{len(chunk_responses)}",
                            "document_id": doc_id_str,
                            "chunk_index": chunk_data.chunk_index or len(chunk_responses),
                            "content": content_preview,  # Use preview as content (full content not available in mirror)
                            "content_preview": content_preview,
                            "chunk_type": "text",
                            "heading": None,
                            "section_name": None,
                            "page_number": None,
                            "metadata": {"source": "supabase_mirror"},
                            "word_count": chunk_data.word_count or 0,
                            "char_count": len(content_preview),
                            "created_at": chunk_data.created_at.isoformat() if chunk_data.created_at else None,
                            "updated_at": chunk_data.updated_at.isoformat() if chunk_data.updated_at else None
                        })

                    logger.info(f"✅ Retrieved {len(chunk_responses)} chunks from Supabase mirror for document {doc_id_str}")

            except Exception as mirror_error:
                logger.error(f"Both PostgreSQL and Supabase Mirror failed for document {doc_id_str}: {str(mirror_error)}")

        # If still no chunks found, return empty with informative message
        if not chunk_responses:
            return {
                "chunks": [],
                "total_chunks": 0,
                "page": page,
                "per_page": per_page,
                "error": "No chunks found - document may still be processing",
                "document_status": document.status if document else "unknown"
            }

        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_chunks = chunk_responses[start_idx:end_idx]

        return {
            "chunks": paginated_chunks,
            "total_chunks": len(chunk_responses),
            "page": page,
            "per_page": per_page,
            "document_id": str(document_id),
            "source": "postgresql" if chunk_responses and chunk_responses[0].get("metadata", {}).get("source") != "supabase_mirror" else "supabase_mirror"
        }

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