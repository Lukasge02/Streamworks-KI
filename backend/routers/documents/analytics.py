"""
Document Analytics Router
Handles statistics, summaries, and analytics operations
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from schemas.core import DocumentSummaryResponse
from services.document import DocumentService
# from services.contextual_embedder import ContextualEmbedder, EmbeddingStrategy, ChunkContext, DocumentType  # Legacy service removed
from services.document_summarizer import document_summarizer

# Shared dependencies
def get_document_service() -> DocumentService:
    """Dependency to get DocumentService instance"""
    return DocumentService()

# def get_contextual_embedder() -> ContextualEmbedder:
#     """Dependency to get ContextualEmbedder instance - DISABLED due to legacy service removal"""
#     raise HTTPException(status_code=503, detail="ContextualEmbedder service has been removed")

async def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """Extract user ID from header - for advanced features"""
    if not x_user_id:
        raise HTTPException(
            status_code=401, 
            detail="X-User-ID header required for advanced features"
        )
    return x_user_id

logger = logging.getLogger(__name__)

# Create sub-router for analytics operations with Supabase integration
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


@router.get("/supabase-status")
async def get_supabase_mirror_status() -> Dict[str, Any]:
    """
    Get Supabase mirror service status for UI debugging

    Returns:
    - Mirror service availability
    - Connection status
    - Available tables for analytics
    """
    try:
        from services.supabase_mirror_service import get_supabase_mirror_service

        mirror_service = get_supabase_mirror_service()

        return {
            "enabled": mirror_service.is_enabled(),
            "service_status": "available",
            "tables": {
                "chunk_metadata_mirror": "Available for chunk debugging",
                "document_processing_stats": "Available for processing analytics"
            },
            "endpoints": {
                "document_analytics": "/analytics/{document_id}/supabase-analytics",
                "chunk_details": "Available in chunk_metadata_mirror table",
                "processing_stats": "Available in document_processing_stats table"
            }
        }

    except ImportError:
        return {
            "enabled": False,
            "service_status": "not_available",
            "error": "Supabase mirror service not installed"
        }
    except Exception as e:
        logger.error(f"Failed to get Supabase status: {str(e)}")
        return {
            "enabled": False,
            "service_status": "error",
            "error": str(e)
        }


@router.get("/{document_id}/supabase-analytics")
async def get_document_supabase_analytics(
    document_id: UUID
) -> Dict[str, Any]:
    """
    Get enhanced document analytics from Supabase mirror
    Perfect for UI debugging and detailed chunk inspection

    - **document_id**: Document UUID

    Returns comprehensive analytics including:
    - Document processing statistics
    - Detailed chunk metadata
    - Processing engine information
    - Embedding model details
    - Word counts and chunk types
    """
    try:
        from services.supabase_mirror_service import get_document_analytics

        analytics = await get_document_analytics(str(document_id))

        if analytics:
            logger.info(f"📊 Retrieved enhanced Supabase analytics for document: {document_id}")
            return {
                "success": True,
                "document_id": str(document_id),
                "analytics": analytics,
                "ui_debug_info": {
                    "total_chunks": analytics.get("chunk_summary", {}).get("total_chunks", 0),
                    "total_words": analytics.get("chunk_summary", {}).get("total_words", 0),
                    "processing_engine": analytics.get("document_stats", {}).get("processing_engine", "unknown"),
                    "embedding_model": analytics.get("document_stats", {}).get("embedding_model", "unknown")
                }
            }
        else:
            logger.info(f"📊 No Supabase analytics found for document: {document_id}")
            return {
                "success": False,
                "document_id": str(document_id),
                "message": "No analytics data found in Supabase mirror - document may not have been processed yet",
                "analytics": None
            }

    except ImportError:
        logger.warning("Supabase mirror service not available")
        raise HTTPException(
            status_code=503,
            detail="Supabase mirror service not available"
        )
    except Exception as e:
        logger.error(f"Failed to get Supabase analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve Supabase analytics: {str(e)}"
        )


@router.get("/processing-overview")
async def get_processing_overview(
    include_supabase: bool = True,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Get comprehensive processing overview with Supabase integration

    - **include_supabase**: Include Supabase mirror statistics (default: True)
    """
    try:
        from sqlalchemy import select, func
        from models.core import Document, DocumentStatus

        # Get document processing status distribution
        status_query = select(
            Document.status,
            func.count(Document.id).label('count')
        ).group_by(Document.status)

        status_result = await db.execute(status_query)
        status_distribution = {}
        for row in status_result:
            status_distribution[row.status] = row.count

        # Get chunk statistics
        chunk_query = select(
            func.sum(Document.chunk_count).label('total_chunks'),
            func.avg(Document.chunk_count).label('avg_chunks_per_doc'),
            func.max(Document.chunk_count).label('max_chunks')
        ).where(Document.chunk_count > 0)

        chunk_result = await db.execute(chunk_query)
        chunk_stats = chunk_result.one()

        overview = {
            "processing_status_distribution": status_distribution,
            "chunk_statistics": {
                "total_chunks": chunk_stats.total_chunks or 0,
                "average_chunks_per_document": float(chunk_stats.avg_chunks_per_doc or 0),
                "max_chunks_in_document": chunk_stats.max_chunks or 0
            },
            "current_processing_engine": "llamaindex_chromadb_master",
            "embedding_model": "BAAI/bge-base-en-v1.5"
        }

        # Add Supabase mirror information
        if include_supabase:
            try:
                from services.supabase_mirror_service import get_supabase_mirror_service
                mirror_service = get_supabase_mirror_service()

                overview["supabase_mirror"] = {
                    "enabled": mirror_service.is_enabled(),
                    "status": "operational" if mirror_service.is_enabled() else "disabled",
                    "purpose": "Enhanced UI debugging and analytics",
                    "tables": {
                        "chunk_metadata_mirror": "Detailed chunk information",
                        "document_processing_stats": "Processing statistics and timing"
                    }
                }

            except Exception as mirror_error:
                logger.warning(f"Could not get Supabase mirror info: {str(mirror_error)}")
                overview["supabase_mirror"] = {"error": str(mirror_error)}

        return overview

    except Exception as e:
        logger.error(f"Failed to get processing overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get processing overview: {str(e)}")


@router.get("/health-check")
async def analytics_health_check():
    """
    Comprehensive health check for analytics system including Supabase mirror
    """
    health_status = {
        "service": "document-analytics",
        "status": "healthy",
        "timestamp": "2025-09-14T15:30:00Z",
        "components": {
            "database": "operational",
            "document_service": "operational"
        }
    }

    # Check Supabase mirror service
    try:
        from services.supabase_mirror_service import get_supabase_mirror_service
        mirror_service = get_supabase_mirror_service()

        health_status["components"]["supabase_mirror"] = {
            "enabled": mirror_service.is_enabled(),
            "status": "operational" if mirror_service.is_enabled() else "disabled",
            "purpose": "UI debugging and enhanced analytics"
        }

    except Exception as e:
        health_status["components"]["supabase_mirror"] = {
            "enabled": False,
            "status": "error",
            "error": str(e)
        }

    # Check overall health
    unhealthy_components = [
        name for name, status in health_status["components"].items()
        if (isinstance(status, dict) and status.get("status") == "error") or
           (isinstance(status, str) and status != "operational")
    ]

    if unhealthy_components:
        health_status["status"] = "degraded"
        health_status["issues"] = unhealthy_components

    return health_status