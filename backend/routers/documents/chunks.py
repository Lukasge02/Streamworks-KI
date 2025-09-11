"""
Document Chunk Management Router
Handles chunk-related operations: viewing, searching, analytics
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from services.document_service import DocumentService
from services.document_chunk_service import DocumentChunkService

# Shared dependencies
def get_document_service() -> DocumentService:
    """Dependency to get DocumentService instance"""
    return DocumentService()

def get_chunk_service() -> DocumentChunkService:
    """Dependency to get DocumentChunkService instance"""
    return DocumentChunkService()

logger = logging.getLogger(__name__)

# Create sub-router for chunk operations
router = APIRouter()


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: UUID,
    chunk_type: Optional[str] = Query(None, description="Filter by chunk type (text, table, image, code)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service),
    chunk_service: DocumentChunkService = Depends(get_chunk_service)
):
    """
    Get chunks for a specific document
    
    - **document_id**: Document UUID
    - **chunk_type**: Filter by chunk type
    - **page**: Page number (1-based)
    - **per_page**: Items per page (1-200)
    """
    try:
        from models.core import ChunkType
        
        # Validate document exists
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Validate chunk_type if provided
        chunk_type_enum = None
        if chunk_type:
            try:
                chunk_type_enum = ChunkType(chunk_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid chunk_type. Must be one of: {[t.value for t in ChunkType]}"
                )
        
        chunks = await chunk_service.get_document_chunks(
            db=db,
            document_id=document_id,
            chunk_type=chunk_type_enum,
            page=page,
            per_page=per_page
        )
        
        # Convert to response format
        chunk_responses = []
        for chunk in chunks:
            chunk_responses.append({
                "id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "content_preview": chunk.content_preview,
                "heading": chunk.heading,
                "section_name": chunk.section_name,
                "page_number": chunk.page_number,
                "chunk_type": chunk.chunk_type.value,
                "metadata": chunk.chunk_metadata,
                "word_count": chunk.word_count,
                "char_count": chunk.char_count,
                "created_at": chunk.created_at,
                "updated_at": chunk.updated_at
            })
        
        return {
            "chunks": chunk_responses,
            "total_chunks": len(chunk_responses),
            "page": page,
            "per_page": per_page,
            "document_id": str(document_id)
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


@router.get("/{document_id}/chunks/{chunk_id}")
async def get_document_chunk(
    document_id: UUID,
    chunk_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service),
    chunk_service: DocumentChunkService = Depends(get_chunk_service)
):
    """
    Get specific chunk by ID
    
    - **document_id**: Document UUID
    - **chunk_id**: Chunk UUID
    """
    try:
        # Validate document exists
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        chunk = await chunk_service.get_chunk_by_id(db, chunk_id, include_document=True)
        if not chunk or chunk.document_id != document_id:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        return {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "heading": chunk.heading,
            "section_name": chunk.section_name,
            "page_number": chunk.page_number,
            "chunk_type": chunk.chunk_type.value,
            "metadata": chunk.chunk_metadata,
            "word_count": chunk.word_count,
            "char_count": chunk.char_count,
            "created_at": chunk.created_at,
            "updated_at": chunk.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chunk: {str(e)}")


@router.get("/{document_id}/chunks/analytics")
async def get_document_chunk_analytics(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service),
    chunk_service: DocumentChunkService = Depends(get_chunk_service)
):
    """
    Get chunk analytics for a document
    
    - **document_id**: Document UUID
    """
    try:
        # Validate document exists
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        analytics = await chunk_service.get_chunk_analytics(db, document_id)
        
        return {
            "document_id": str(document_id),
            "filename": document.filename,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chunk analytics: {str(e)}")


@router.get("/chunks/search")
async def search_chunks(
    query: str = Query(..., description="Search query"),
    document_id: Optional[UUID] = Query(None, description="Filter by document"),
    chunk_type: Optional[str] = Query(None, description="Filter by chunk type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_async_session),
    chunk_service: DocumentChunkService = Depends(get_chunk_service)
):
    """
    Search chunks by content
    
    - **query**: Search query
    - **document_id**: Filter by document (optional)
    - **chunk_type**: Filter by chunk type (optional)
    - **limit**: Maximum results (1-100)
    """
    try:
        from models.core import ChunkType
        
        # Validate chunk_type if provided
        chunk_type_enum = None
        if chunk_type:
            try:
                chunk_type_enum = ChunkType(chunk_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid chunk_type. Must be one of: {[t.value for t in ChunkType]}"
                )
        
        chunks = await chunk_service.search_chunks(
            db=db,
            query=query,
            document_id=document_id,
            chunk_type=chunk_type_enum,
            limit=limit
        )
        
        # Convert to response format
        chunk_responses = []
        for chunk in chunks:
            chunk_responses.append({
                "id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content_preview": chunk.content_preview,
                "heading": chunk.heading,
                "section_name": chunk.section_name,
                "page_number": chunk.page_number,
                "chunk_type": chunk.chunk_type.value,
                "word_count": chunk.word_count,
                "char_count": chunk.char_count,
                "created_at": chunk.created_at
            })
        
        return {
            "query": query,
            "results": chunk_responses,
            "total_results": len(chunk_responses),
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search chunks: {str(e)}")