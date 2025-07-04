from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import aiofiles
import uuid
from datetime import datetime
import logging

from app.core.config import settings
from app.models.schemas import TrainingFileResponse, TrainingFileCreate, TrainingStatusResponse
from app.services.training_service import TrainingService
from app.models.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed file extensions by category
ALLOWED_EXTENSIONS = {
    "help_data": [".txt", ".csv", ".bat", ".md", ".ps1"],
    "stream_templates": [".xml", ".xsd"]
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.post("/upload", response_model=TrainingFileResponse)
async def upload_training_file(
    file: UploadFile = File(...),
    category: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a training data file"""
    logger.info(f"📤 Uploading file: {file.filename} to category: {category}")
    
    # Validate category
    if category not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Allowed: {list(ALLOWED_EXTENSIONS.keys())}"
        )
    
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS[category]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension for category {category}. Allowed: {ALLOWED_EXTENSIONS[category]}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Create training service
        training_service = TrainingService(db)
        
        # Save file and create database record
        training_file = await training_service.save_training_file(
            filename=file.filename,
            file_content=file_content,
            category=category
        )
        
        logger.info(f"✅ File uploaded successfully: {training_file.id}")
        return training_file
        
    except Exception as e:
        logger.error(f"❌ Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@router.get("/files", response_model=List[TrainingFileResponse])
async def list_training_files(
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get list of all training files"""
    logger.info(f"📋 Listing training files - category: {category}, status: {status}")
    
    try:
        training_service = TrainingService(db)
        files = await training_service.get_training_files(category=category, status=status)
        
        logger.info(f"✅ Retrieved {len(files)} training files")
        return files
        
    except Exception as e:
        logger.error(f"❌ Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve files: {str(e)}")


@router.delete("/files/{file_id}")
async def delete_training_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a training file"""
    logger.info(f"🗑️ Deleting training file: {file_id}")
    
    try:
        training_service = TrainingService(db)
        success = await training_service.delete_training_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"✅ File deleted successfully: {file_id}")
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/status", response_model=TrainingStatusResponse)
async def get_training_status(db: AsyncSession = Depends(get_db)):
    """Get training status for both categories"""
    logger.info("📊 Getting training status")
    
    try:
        training_service = TrainingService(db)
        status = await training_service.get_training_status()
        
        logger.info("✅ Training status retrieved successfully")
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get training status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.post("/process/{file_id}")
async def process_training_file(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Process a training file (mock implementation)"""
    logger.info(f"⚙️ Processing training file: {file_id}")
    
    try:
        training_service = TrainingService(db)
        success = await training_service.process_training_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"✅ File processing started: {file_id}")
        return {"message": "File processing started", "file_id": file_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to process file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.post("/index/{file_id}")
async def index_to_chromadb(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Index a training file to ChromaDB"""
    logger.info(f"🔍 Indexing file to ChromaDB: {file_id}")
    
    try:
        training_service = TrainingService(db)
        result = await training_service.index_file_to_chromadb(file_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"✅ File indexed successfully: {file_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to index file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to index file: {str(e)}")


@router.post("/index/batch")
async def batch_index_to_chromadb(
    file_ids: List[str],
    db: AsyncSession = Depends(get_db)
):
    """Batch index multiple files to ChromaDB"""
    logger.info(f"🔍 Batch indexing {len(file_ids)} files to ChromaDB")
    
    try:
        training_service = TrainingService(db)
        results = await training_service.batch_index_to_chromadb(file_ids)
        
        logger.info(f"✅ Batch indexing completed")
        return results
        
    except Exception as e:
        logger.error(f"❌ Failed to batch index files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to batch index files: {str(e)}")


@router.delete("/index/{file_id}")
async def remove_from_chromadb(
    file_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Remove a file from ChromaDB index"""
    logger.info(f"🗑️ Removing file from ChromaDB: {file_id}")
    
    try:
        training_service = TrainingService(db)
        success = await training_service.remove_from_chromadb(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found or not indexed")
        
        logger.info(f"✅ File removed from index: {file_id}")
        return {"message": "File removed from index successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to remove from index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove from index: {str(e)}")


@router.get("/chromadb/stats")
async def get_chromadb_stats(db: AsyncSession = Depends(get_db)):
    """Get ChromaDB statistics"""
    logger.info("📊 Getting ChromaDB statistics")
    
    try:
        training_service = TrainingService(db)
        stats = await training_service.get_chromadb_stats()
        
        logger.info("✅ ChromaDB stats retrieved successfully")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get ChromaDB stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/files/{file_id}/conversion-status")
async def get_conversion_status(file_id: str, db: AsyncSession = Depends(get_db)):
    """Get TXT to MD conversion status"""
    
    try:
        training_service = TrainingService(db)
        
        # Get file record
        files = await training_service.get_training_files()
        file_record = next((f for f in files if f.id == file_id), None)
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_id": file_id,
            "filename": file_record.filename,
            "original_format": getattr(file_record, 'original_format', None),
            "optimized_format": getattr(file_record, 'optimized_format', None),
            "conversion_status": getattr(file_record, 'conversion_status', None),
            "processed_file_path": getattr(file_record, 'processed_file_path', None),
            "conversion_error": getattr(file_record, 'conversion_error', None),
            "file_status": file_record.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get conversion status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/optimized-content")
async def get_optimized_content(file_id: str, db: AsyncSession = Depends(get_db)):
    """Get optimized markdown content"""
    
    try:
        training_service = TrainingService(db)
        
        # Get file record
        files = await training_service.get_training_files()
        file_record = next((f for f in files if f.id == file_id), None)
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if optimized file exists
        processed_file_path = getattr(file_record, 'processed_file_path', None)
        if not processed_file_path or not os.path.exists(processed_file_path):
            raise HTTPException(status_code=404, detail="Optimized file not found")
        
        # Read optimized content
        async with aiofiles.open(processed_file_path, 'r', encoding='utf-8') as f:
            optimized_content = await f.read()
        
        return {
            "file_id": file_id,
            "original_filename": file_record.filename,
            "optimized_filename": os.path.basename(processed_file_path),
            "optimized_content": optimized_content,
            "conversion_metadata": getattr(file_record, 'conversion_metadata', None),
            "file_size": len(optimized_content),
            "conversion_status": getattr(file_record, 'conversion_status', None)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get optimized content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversion-stats")
async def get_conversion_stats(db: AsyncSession = Depends(get_db)):
    """Get TXT to MD conversion statistics"""
    
    try:
        training_service = TrainingService(db)
        files = await training_service.get_training_files()
        
        # Filter TXT files
        txt_files = [f for f in files if f.filename.lower().endswith('.txt')]
        
        # Count conversion statuses
        conversion_stats = {
            "total_txt_files": len(txt_files),
            "conversions_completed": len([f for f in txt_files if getattr(f, 'conversion_status', None) == 'completed']),
            "conversions_failed": len([f for f in txt_files if getattr(f, 'conversion_status', None) == 'failed']),
            "conversions_pending": len([f for f in txt_files if getattr(f, 'conversion_status', None) is None]),
            "optimized_files_created": len([f for f in txt_files if getattr(f, 'processed_file_path', None) is not None])
        }
        
        # Calculate success rate
        if conversion_stats["total_txt_files"] > 0:
            conversion_stats["success_rate"] = round(
                (conversion_stats["conversions_completed"] / conversion_stats["total_txt_files"]) * 100, 2
            )
        else:
            conversion_stats["success_rate"] = 0.0
        
        return conversion_stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get conversion stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def training_health_check():
    """Health check for training API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "training_api",
        "allowed_extensions": ALLOWED_EXTENSIONS,
        "max_file_size_mb": MAX_FILE_SIZE // (1024*1024),
        "features": {
            "txt_to_md_conversion": True,
            "rag_indexing": True,
            "conversion_tracking": True
        }
    }