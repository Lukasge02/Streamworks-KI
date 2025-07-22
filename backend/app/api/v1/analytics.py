"""
Analytics API Endpoints für Bachelor-Arbeit Dashboard
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import logging

from app.core.database_postgres import get_db
from app.services.analytics_service import analytics_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/performance/summary")
async def get_performance_summary(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get performance summary for dashboard"""
    
    try:
        return await analytics_service.get_performance_summary(days)
    except Exception as e:
        logger.error(f"Failed to get performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/processing")
async def get_document_processing_stats(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get document processing statistics"""
    
    try:
        return await analytics_service.get_document_processing_stats()
    except Exception as e:
        logger.error(f"Failed to get document stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rag/effectiveness")
async def get_rag_effectiveness(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get RAG system effectiveness metrics"""
    
    try:
        return await analytics_service.get_rag_effectiveness_metrics()
    except Exception as e:
        logger.error(f"Failed to get RAG effectiveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/thesis-data")
async def export_thesis_data(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Export all analytics data for Bachelor thesis"""
    
    try:
        output_path = await analytics_service.export_thesis_data()
        return {
            "message": "Thesis data exported successfully",
            "file_path": output_path
        }
    except Exception as e:
        logger.error(f"Failed to export thesis data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def analytics_health() -> Dict[str, str]:
    """Analytics service health check"""
    
    return {
        "service": "analytics",
        "status": "healthy",
        "features": ["performance_tracking", "document_analytics", "rag_metrics"]
    }