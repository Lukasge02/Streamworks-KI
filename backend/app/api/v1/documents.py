"""
Document API - PostgreSQL-optimiert
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.services.document_service import document_service
from app.utils.batch_converter import batch_converter
from app.core.database_postgres import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_and_convert(
    file: UploadFile = File(...),
    category: str = "general",
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """Upload and convert document to markdown"""
    
    try:
        # Validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        allowed_extensions = {'.pdf', '.txt', '.md'}
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        if len(file_content) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Convert and save
        result = await document_service.convert_and_save(file.filename, file_content)
        
        if not result.success:
            raise HTTPException(
                status_code=422, 
                detail=f"Conversion failed: {result.error_message}"
            )
        
        return JSONResponse({
            "success": True,
            "message": "Document converted successfully",
            "document_id": result.document_id,
            "original_filename": file.filename,
            "output_path": result.output_path,
            "processing_time": result.processing_time,
            "pages_processed": result.pages_processed,
            "file_size": result.file_size
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch-convert")
async def batch_convert_existing(
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """Batch convert all existing PDF and TXT files"""
    
    try:
        # Start conversion in background
        background_tasks.add_task(
            batch_converter.convert_all_documents, 
            overwrite=overwrite
        )
        
        return JSONResponse({
            "success": True,
            "message": f"Batch conversion started (overwrite={overwrite})",
            "note": "Check logs for progress updates"
        })
        
    except Exception as e:
        logger.error(f"Batch conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversion-stats")
async def get_conversion_stats(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """Get document conversion statistics"""
    
    try:
        stats = document_service.get_stats()
        
        return JSONResponse({
            "service_stats": {
                "total_files": stats.total_files,
                "successful_conversions": stats.successful_conversions,
                "failed_conversions": stats.failed_conversions,
                "success_rate": f"{(stats.successful_conversions/max(stats.total_files,1)*100):.1f}%",
                "total_processing_time": f"{stats.total_processing_time:.2f}s",
                "average_processing_time": f"{stats.average_processing_time:.2f}s",
                "total_size_mb": f"{stats.total_size_mb:.2f} MB"
            }
        })
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def document_service_health() -> JSONResponse:
    """Health check for document service"""
    
    return JSONResponse({
        "service": "document_service",
        "status": "healthy",
        "database": "postgresql",
        "storage": "unified_storage",
        "supported_formats": [".pdf", ".txt", ".md"],
        "features": ["conversion", "batch_processing", "analytics_logging"]
    })