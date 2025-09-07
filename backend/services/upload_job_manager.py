"""
Upload Job Progress Management
Tracks upload progress stages for real-time WebSocket updates
"""

import time
import asyncio
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum


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
            self.current_stage = self._get_stage_description(stage)
            
            # Update stage index
            stage_mapping = {
                UploadStage.UPLOADING: 0,
                UploadStage.ANALYZING: 1, 
                UploadStage.PROCESSING: 2,
                UploadStage.READY: 3,
                UploadStage.ERROR: -1
            }
            self.current_stage_index = stage_mapping.get(stage, 0)
        
        if stage_details:
            self.stage_details = stage_details
            
        # Calculate estimated completion
        if self.progress_percentage > 0 and self.progress_percentage < 100:
            elapsed = time.time() - self.start_time
            total_estimated = elapsed * (100 / self.progress_percentage)
            remaining = total_estimated - elapsed
            completion_time = datetime.now() + timedelta(seconds=remaining)
            self.estimated_completion = completion_time.isoformat()
    
    def set_error(self, error_message: str):
        """Set error status with message"""
        self.status = UploadStage.ERROR
        self.error_message = error_message
        self.current_stage = "Upload failed"
        self.stage_details = error_message
        self.last_update = time.time()
    
    def set_completed(self, chunk_count: int):
        """Mark upload as completed"""
        self.status = UploadStage.READY
        self.progress_percentage = 100.0
        self.current_stage = "Upload completed"
        self.stage_details = f"Document processed with {chunk_count} chunks"
        self.chunk_count = chunk_count
        self.last_update = time.time()
        self.estimated_completion = None
    
    def _get_stage_description(self, stage: UploadStage) -> str:
        """Get German description for stage"""
        descriptions = {
            UploadStage.UPLOADING: "Datei wird hochgeladen...",
            UploadStage.ANALYZING: "Dokument wird analysiert...",
            UploadStage.PROCESSING: "Inhalte werden verarbeitet...", 
            UploadStage.READY: "Upload abgeschlossen",
            UploadStage.ERROR: "Fehler beim Upload"
        }
        return descriptions.get(stage, "Upload wird verarbeitet...")
    
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


class UploadJobManager:
    """
    Manages active upload jobs and their progress
    """
    
    def __init__(self):
        self.active_jobs: Dict[str, UploadJobProgress] = {}
    
    def create_job(self, job_id: str, filename: str, file_size_bytes: int) -> UploadJobProgress:
        """Create a new upload job"""
        job = UploadJobProgress(
            job_id=job_id,
            filename=filename,
            file_size_bytes=file_size_bytes
        )
        self.active_jobs[job_id] = job
        return job
    
    def get_job(self, job_id: str) -> Optional[UploadJobProgress]:
        """Get upload job by ID"""
        return self.active_jobs.get(job_id)
    
    def update_job_progress(self, 
                           job_id: str, 
                           percentage: float, 
                           stage: UploadStage = None, 
                           stage_details: str = "") -> Optional[UploadJobProgress]:
        """Update job progress"""
        job = self.active_jobs.get(job_id)
        if job:
            job.update_progress(percentage, stage, stage_details)
            # Broadcast to WebSocket clients
            asyncio.create_task(self._broadcast_progress(job_id, job))
        return job
    
    def complete_job(self, job_id: str, chunk_count: int = 0) -> Optional[UploadJobProgress]:
        """Mark job as completed"""
        job = self.active_jobs.get(job_id)
        if job:
            job.set_completed(chunk_count)
            # Broadcast to WebSocket clients
            asyncio.create_task(self._broadcast_progress(job_id, job))
        return job
    
    def fail_job(self, job_id: str, error_message: str) -> Optional[UploadJobProgress]:
        """Mark job as failed"""
        job = self.active_jobs.get(job_id)
        if job:
            job.set_error(error_message)
            # Broadcast to WebSocket clients
            asyncio.create_task(self._broadcast_progress(job_id, job))
        return job
    
    def remove_job(self, job_id: str):
        """Remove completed or failed job"""
        self.active_jobs.pop(job_id, None)
    
    def cleanup_old_jobs(self, max_age_seconds: int = 3600):
        """Remove jobs older than max_age_seconds"""
        current_time = time.time()
        expired_jobs = [
            job_id for job_id, job in self.active_jobs.items()
            if current_time - job.last_update > max_age_seconds
        ]
        
        for job_id in expired_jobs:
            self.remove_job(job_id)
        
        return len(expired_jobs)

    async def _broadcast_progress(self, job_id: str, job: UploadJobProgress):
        """Broadcast progress update to WebSocket clients"""
        try:
            from routers.upload_progress_websocket import broadcast_upload_progress
            await broadcast_upload_progress(job_id, job)
        except Exception as e:
            print(f"Failed to broadcast progress for job {job_id}: {e}")


# Global upload job manager instance
upload_job_manager = UploadJobManager()