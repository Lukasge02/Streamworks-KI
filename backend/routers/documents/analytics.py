"""
Document Analytics Router
Handles statistics, summaries, and analytics operations
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from schemas.core import DocumentSummaryResponse
from services.document_service import DocumentService
from services.contextual_embedder import ContextualEmbedder, EmbeddingStrategy, ChunkContext, DocumentType
from services.document_summarizer import document_summarizer

# Shared dependencies
def get_document_service() -> DocumentService:
    """Dependency to get DocumentService instance"""
    return DocumentService()

def get_contextual_embedder() -> ContextualEmbedder:
    """Dependency to get ContextualEmbedder instance"""
    return ContextualEmbedder()

async def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """Extract user ID from header - for advanced features"""
    if not x_user_id:
        raise HTTPException(
            status_code=401, 
            detail="X-User-ID header required for advanced features"
        )
    return x_user_id

logger = logging.getLogger(__name__)

# Create sub-router for analytics operations
router = APIRouter()


@router.get("/stats/overview")
async def get_document_stats(
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get overall document statistics
    """
    try:
        from sqlalchemy import select, func
        from models.core import Document
        
        # Basic document stats
        stats_query = select(
            func.count(Document.id).label('total_documents'),
            func.sum(Document.file_size).label('total_size_bytes'),
            func.avg(Document.file_size).label('average_size_bytes')
        )
        
        stats_result = await db.execute(stats_query)
        stats = stats_result.one()
        
        return {
            "total_documents": stats.total_documents or 0,
            "total_size_bytes": stats.total_size_bytes or 0,
            "average_size_bytes": float(stats.average_size_bytes or 0),
            "timestamp": "2025-09-05T21:28:00Z"  # Current timestamp would be dynamic
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/{document_id}/summary", response_model=DocumentSummaryResponse)
async def get_document_summary(
    document_id: UUID,
    force_refresh: bool = Query(False, description="Force regeneration of cached summary"),
    db: AsyncSession = Depends(get_async_session),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Get AI-generated summary for a document
    
    - **document_id**: Document UUID
    - **force_refresh**: Force regeneration even if cached summary exists
    """
    try:
        # Validate document exists
        document = await doc_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate or retrieve cached summary
        summary_result = await document_summarizer.generate_summary(
            document_id=str(document_id),
            db=db,
            force_refresh=force_refresh
        )
        
        return DocumentSummaryResponse(
            summary_data=summary_result,
            document_id=document_id,
            cached=summary_result.get("cached", False),
            generated_at=summary_result.get("generated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document summary {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get document summary: {str(e)}")


@router.get("/embedding-strategies")
async def get_embedding_strategies():
    """Get available enhanced embedding strategies and their descriptions"""
    return {
        "strategies": [
            {
                "name": "basic",
                "description": "Standard sentence transformer embeddings",
                "performance": "Fastest",
                "quality": "Basic"
            },
            {
                "name": "contextual",
                "description": "Context-aware embeddings incorporating document metadata",
                "performance": "Fast",
                "quality": "Good"
            },
            {
                "name": "hierarchical",
                "description": "Embeddings with hierarchical position encoding",
                "performance": "Moderate", 
                "quality": "Better"
            },
            {
                "name": "domain_adaptive",
                "description": "Domain-specific embeddings with adaptive weighting",
                "performance": "Slower",
                "quality": "High"
            },
            {
                "name": "multi_granular",
                "description": "Multi-level embeddings (sentence + paragraph level)",
                "performance": "Slowest",
                "quality": "Highest"
            }
        ],
        "document_types": [
            "technical", "academic", "legal", "medical", "financial", "general"
        ]
    }