"""
Simple Upload Progress WebSocket Router
Dedicated endpoint for upload progress tracking only
"""

import logging
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.upload_job_manager_refactored import upload_job_manager, UploadJobProgress

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple connection manager for upload progress
class UploadProgressManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[job_id] = websocket
        logger.info(f"Upload progress WebSocket connected for job: {job_id}")

    def disconnect(self, job_id: str):
        if job_id in self.connections:
            del self.connections[job_id]
            logger.info(f"Upload progress WebSocket disconnected for job: {job_id}")

    async def send_progress(self, job_id: str, progress: UploadJobProgress):
        if job_id in self.connections:
            websocket = self.connections[job_id]
            try:
                progress_data = {
                    "job_id": progress.job_id,
                    "progress": progress.progress_percentage,
                    "stage": progress.current_stage,
                    "status": progress.status.value,  # Convert enum to string
                    "error": progress.error_message
                }
                await websocket.send_json(progress_data)
                logger.debug(f"Sent progress update for job {job_id}: {progress.progress_percentage}%")
            except Exception as e:
                logger.error(f"Failed to send progress for job {job_id}: {e}")
                self.disconnect(job_id)

# Global manager instance
upload_progress_manager = UploadProgressManager()

@router.websocket("/upload-progress/{job_id}")
async def upload_progress_websocket(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for tracking upload progress of a specific job
    """
    await upload_progress_manager.connect(job_id, websocket)
    
    try:
        # Send initial progress if job already exists
        current_progress = upload_job_manager.get_job(job_id)
        if current_progress:
            await upload_progress_manager.send_progress(job_id, current_progress)
        
        # Keep connection alive and handle any incoming messages
        while True:
            data = await websocket.receive_text()
            # Currently we don't need to handle incoming messages for upload progress
            # This just keeps the connection alive
            logger.debug(f"Received message from upload progress client {job_id}: {data}")
            
    except WebSocketDisconnect:
        upload_progress_manager.disconnect(job_id)
    except Exception as e:
        logger.error(f"Upload progress WebSocket error for job {job_id}: {e}")
        upload_progress_manager.disconnect(job_id)

# Function to broadcast progress updates from the upload job manager
async def broadcast_upload_progress(job_id: str, progress: UploadJobProgress):
    """
    Called by upload job manager to broadcast progress updates
    """
    await upload_progress_manager.send_progress(job_id, progress)