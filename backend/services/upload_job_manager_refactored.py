"""
Refactored Upload Job Manager with proper dependency injection
"""

import time
import asyncio
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import logging

from .di_container import ServiceLifecycle

logger = logging.getLogger(__name__)


class UploadStage(str, Enum):
    """Upload processing stages"""
    UPLOADING = "uploading"        # File upload to server
    ANALYZING = "analyzing"        # Docling document analysis  
    PROCESSING = "processing"      # Creating chunks and saving to DB
    READY = "ready"               # Upload completed successfully
    ERROR = "error"               # Upload failed


@dataclass
class UploadJobProgress:
    """
    Upload job progress tracking with detailed stage information
    """
    job_id: str
    filename: str
    file_size_bytes: int
    status: UploadStage = UploadStage.UPLOADING
    progress_percentage: float = 0.0
    current_stage: str = "Uploading file..."
    stage_details: str = ""
    current_stage_index: int = 0
    total_stages: int = 4
    chunk_count: int = 0
    processed_bytes: int = 0
    error_message: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    estimated_completion: Optional[str] = None
    
    def update_progress(self, 
                       percentage: float, 
                       stage: UploadStage = None, 
                       stage_details: str = ""):
        """Update progress with stage information"""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        self.last_update = time.time()
        
        if stage:
            self.status = stage
            self.current_stage_index = list(UploadStage).index(stage)
        
        if stage_details:
            self.stage_details = stage_details
        
        # Update current stage description
        stage_descriptions = {
            UploadStage.UPLOADING: "Datei wird hochgeladen...",
            UploadStage.ANALYZING: "Dokument wird analysiert...",
            UploadStage.PROCESSING: "Dokument wird verarbeitet...",
            UploadStage.READY: "Hochladen abgeschlossen",
            UploadStage.ERROR: "Fehler beim Hochladen"
        }
        
        base_description = stage_descriptions.get(self.status, "Verarbeitung...")
        if stage_details:
            self.current_stage = f"{base_description} {stage_details}"
        else:
            self.current_stage = base_description
        
        # Calculate estimated completion
        if self.progress_percentage > 0:
            elapsed = time.time() - self.start_time
            total_estimated = elapsed / (self.progress_percentage / 100)
            remaining = total_estimated - elapsed
            
            if remaining > 0:
                if remaining < 60:
                    self.estimated_completion = f"ca. {int(remaining)}s"
                elif remaining < 3600:
                    self.estimated_completion = f"ca. {int(remaining // 60)}min"
                else:
                    hours = int(remaining // 3600)
                    minutes = int((remaining % 3600) // 60)
                    self.estimated_completion = f"ca. {hours}h {minutes}min"
    
    def set_error(self, error_message: str):
        """Set error state"""
        self.status = UploadStage.ERROR
        self.error_message = error_message
        self.current_stage = f"Fehler: {error_message}"
        self.update_progress(self.progress_percentage)
    
    def complete(self):
        """Mark upload as completed"""
        self.status = UploadStage.READY
        self.progress_percentage = 100.0
        self.current_stage = "Hochladen abgeschlossen"
        self.estimated_completion = "Abgeschlossen"
        self.last_update = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "filename": self.filename,
            "file_size_bytes": self.file_size_bytes,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "current_stage": self.current_stage,
            "stage_details": self.stage_details,
            "current_stage_index": self.current_stage_index,
            "total_stages": self.total_stages,
            "chunk_count": self.chunk_count,
            "processed_bytes": self.processed_bytes,
            "error_message": self.error_message,
            "start_time": self.start_time,
            "last_update": self.last_update,
            "estimated_completion": self.estimated_completion
        }


class UploadJobManager(ServiceLifecycle):
    """
    Manages upload job progress tracking with WebSocket notifications
    Refactored to use proper dependency injection and lifecycle management
    """
    
    def __init__(self):
        self._jobs: Dict[str, UploadJobProgress] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize the upload job manager"""
        if self._initialized:
            return
            
        logger.info("Initializing UploadJobManager")
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_old_jobs())
        
        self._initialized = True
        logger.info("UploadJobManager initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "status": "healthy",
            "active_jobs": len(self._jobs),
            "initialized": self._initialized,
            "cleanup_task_running": self._cleanup_task and not self._cleanup_task.done()
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        logger.info("Cleaning up UploadJobManager")
        
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self._jobs.clear()
        self._initialized = False
        logger.info("UploadJobManager cleaned up")
    
    def create_job(self, job_id: str, filename: str, file_size_bytes: int) -> UploadJobProgress:
        """Create a new upload job"""
        job = UploadJobProgress(
            job_id=job_id,
            filename=filename,
            file_size_bytes=file_size_bytes
        )
        
        self._jobs[job_id] = job
        logger.info(f"Created upload job: {job_id} for {filename}")
        
        # Broadcast initial progress
        asyncio.create_task(self._broadcast_progress(job_id))
        
        return job
    
    def get_job(self, job_id: str) -> Optional[UploadJobProgress]:
        """Get an upload job by ID"""
        return self._jobs.get(job_id)
    
    def update_job(self, job_id: str, **kwargs):
        """Update an upload job"""
        job = self._jobs.get(job_id)
        if not job:
            logger.warning(f"Attempted to update non-existent job: {job_id}")
            return
        
        # Update job based on provided kwargs
        if "progress" in kwargs:
            job.update_progress(
                percentage=kwargs["progress"],
                stage=kwargs.get("stage"),
                stage_details=kwargs.get("stage_details", "")
            )
        
        if "chunk_count" in kwargs:
            job.chunk_count = kwargs["chunk_count"]
        
        if "processed_bytes" in kwargs:
            job.processed_bytes = kwargs["processed_bytes"]
        
        if "error" in kwargs:
            job.set_error(kwargs["error"])
        
        if "complete" in kwargs and kwargs["complete"]:
            job.complete()
        
        # Broadcast progress update
        asyncio.create_task(self._broadcast_progress(job_id))
    
    def complete_job(self, job_id: str):
        """Mark an upload job as completed"""
        job = self._jobs.get(job_id)
        if job:
            job.complete()
            asyncio.create_task(self._broadcast_progress(job_id))
            logger.info(f"Completed upload job: {job_id}")
    
    def fail_job(self, job_id: str, error_message: str):
        """Mark an upload job as failed"""
        job = self._jobs.get(job_id)
        if job:
            job.set_error(error_message)
            asyncio.create_task(self._broadcast_progress(job_id))
            logger.error(f"Failed upload job: {job_id} - {error_message}")
    
    def remove_job(self, job_id: str):
        """Remove an upload job"""
        if job_id in self._jobs:
            del self._jobs[job_id]
            logger.info(f"Removed upload job: {job_id}")
    
    def get_all_jobs(self) -> Dict[str, UploadJobProgress]:
        """Get all active upload jobs"""
        return self._jobs.copy()
    
    async def _broadcast_progress(self, job_id: str):
        """Broadcast progress update via WebSocket"""
        try:
            job = self._jobs.get(job_id)
            if not job:
                return
            
            # Import here to avoid circular dependency
            from routers.upload_progress_websocket import broadcast_upload_progress
            await broadcast_upload_progress(job_id, job)
            
        except Exception as e:
            logger.error(f"Failed to broadcast progress for job {job_id}: {e}")
    
    async def _cleanup_old_jobs(self):
        """Cleanup old completed jobs periodically"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                current_time = time.time()
                jobs_to_remove = []
                
                for job_id, job in self._jobs.items():
                    # Remove jobs older than 1 hour or failed jobs older than 30 minutes
                    age = current_time - job.last_update
                    if (job.status == UploadStage.READY and age > 3600) or \
                       (job.status == UploadStage.ERROR and age > 1800):
                        jobs_to_remove.append(job_id)
                
                for job_id in jobs_to_remove:
                    self.remove_job(job_id)
                    logger.info(f"Cleaned up old job: {job_id}")
                
                if jobs_to_remove:
                    logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error during job cleanup: {e}")


# Factory function for dependency injection
def create_upload_job_manager() -> UploadJobManager:
    """Factory function to create UploadJobManager instance"""
    return UploadJobManager()

# Global instance for backward compatibility
upload_job_manager = UploadJobManager()