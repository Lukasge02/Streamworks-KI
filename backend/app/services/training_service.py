import os
import uuid
import aiofiles
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.models.database import TrainingFile
from app.models.schemas import TrainingFileResponse, TrainingFileCreate, TrainingStatusResponse, CategoryStats
from app.core.config import settings

logger = logging.getLogger(__name__)

class TrainingService:
    """Service for managing training data files"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_path = "data/training_data"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure training data directories exist"""
        directories = [
            self.base_path,
            os.path.join(self.base_path, "help_data"),
            os.path.join(self.base_path, "stream_templates")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"📁 Ensured directory exists: {directory}")
    
    async def save_training_file(
        self,
        filename: str,
        file_content: bytes,
        category: str
    ) -> TrainingFileResponse:
        """Save training file to filesystem and database"""
        
        # Generate unique file ID and path
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{filename}"
        file_path = os.path.join(self.base_path, category, safe_filename)
        
        try:
            # Save file to filesystem
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"💾 File saved to: {file_path}")
            
            # Create database record
            db_file = TrainingFile(
                id=file_id,
                filename=filename,
                category=category,
                file_path=file_path,
                file_size=len(file_content),
                status="ready"  # Mock: immediately ready
            )
            
            self.db.add(db_file)
            await self.db.commit()
            await self.db.refresh(db_file)
            
            logger.info(f"📝 Database record created: {file_id}")
            
            # Convert to response model
            return TrainingFileResponse(
                id=db_file.id,
                filename=db_file.filename,
                category=db_file.category,
                file_path=db_file.file_path,
                upload_date=db_file.upload_date.isoformat(),
                file_size=db_file.file_size,
                status=db_file.status
            )
            
        except Exception as e:
            # Clean up file if database operation fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
    
    async def get_training_files(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[TrainingFileResponse]:
        """Get list of training files with optional filtering"""
        
        query = select(TrainingFile)
        
        if category:
            query = query.where(TrainingFile.category == category)
        
        if status:
            query = query.where(TrainingFile.status == status)
        
        query = query.order_by(TrainingFile.upload_date.desc())
        
        result = await self.db.execute(query)
        files = result.scalars().all()
        
        return [
            TrainingFileResponse(
                id=file.id,
                filename=file.filename,
                category=file.category,
                file_path=file.file_path,
                upload_date=file.upload_date.isoformat(),
                file_size=file.file_size,
                status=file.status
            )
            for file in files
        ]
    
    async def delete_training_file(self, file_id: str) -> bool:
        """Delete training file from filesystem and database"""
        
        # Get file record
        query = select(TrainingFile).where(TrainingFile.id == file_id)
        result = await self.db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            return False
        
        try:
            # Delete file from filesystem
            if os.path.exists(file_record.file_path):
                os.remove(file_record.file_path)
                logger.info(f"🗑️ File deleted from filesystem: {file_record.file_path}")
            
            # Delete database record
            await self.db.delete(file_record)
            await self.db.commit()
            
            logger.info(f"🗑️ Database record deleted: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete file {file_id}: {e}")
            await self.db.rollback()
            raise e
    
    async def get_training_status(self) -> TrainingStatusResponse:
        """Get training status statistics for both categories"""
        
        # Get all files
        all_files = await self.get_training_files()
        
        # Calculate stats for help_data
        help_files = [f for f in all_files if f.category == "help_data"]
        help_stats = CategoryStats(
            total=len(help_files),
            ready=len([f for f in help_files if f.status == "ready"]),
            processing=len([f for f in help_files if f.status == "processing"]),
            error=len([f for f in help_files if f.status == "error"])
        )
        
        # Calculate stats for stream_templates
        template_files = [f for f in all_files if f.category == "stream_templates"]
        template_stats = CategoryStats(
            total=len(template_files),
            ready=len([f for f in template_files if f.status == "ready"]),
            processing=len([f for f in template_files if f.status == "processing"]),
            error=len([f for f in template_files if f.status == "error"])
        )
        
        return TrainingStatusResponse(
            help_data_stats=help_stats,
            stream_template_stats=template_stats,
            last_updated=datetime.utcnow().isoformat()
        )
    
    async def process_training_file(self, file_id: str) -> bool:
        """Process training file (mock implementation)"""
        
        # Get file record
        query = select(TrainingFile).where(TrainingFile.id == file_id)
        result = await self.db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            return False
        
        try:
            # Mock processing: update status to processing
            file_record.status = "processing"
            await self.db.commit()
            
            logger.info(f"⚙️ File processing started (mock): {file_id}")
            
            # In a real implementation, here you would:
            # 1. For help_data: Parse and convert to Q&A pairs
            # 2. For stream_templates: Prepare for LoRA training
            # 3. Update status to "ready" when complete
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to process file {file_id}: {e}")
            await self.db.rollback()
            raise e