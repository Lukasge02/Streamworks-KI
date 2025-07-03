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


@router.get("/health")
async def training_health_check():
    """Health check for training API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "training_api",
        "allowed_extensions": ALLOWED_EXTENSIONS,
        "max_file_size_mb": MAX_FILE_SIZE // (1024*1024)
    }