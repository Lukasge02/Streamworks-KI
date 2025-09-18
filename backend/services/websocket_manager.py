"""
WebSocket Manager for Real-time Upload Progress
Enterprise WebSocket management with connection pooling and broadcasting
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
from services.upload_job_manager_refactored import UploadJobProgress

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    WebSocket Connection Manager
    Handles multiple client connections and broadcasting
    """
    
    def __init__(self):
        # Active WebSocket connections by job_id
        self.job_connections: Dict[str, Set[WebSocket]] = {}
        # All active connections for broadcasting
        self.active_connections: Set[WebSocket] = set()
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        logger.info("WebSocket ConnectionManager initialized")
    
    async def connect(self, websocket: WebSocket, job_id: str, client_info: Dict[str, Any] = None):
        """Register an already accepted WebSocket connection for upload tracking"""
        try:
            # WebSocket should already be accepted at this point
            # Add to active connections
            self.active_connections.add(websocket)
            
            # Add to job-specific connections
            if job_id not in self.job_connections:
                self.job_connections[job_id] = set()
            self.job_connections[job_id].add(websocket)
            
            # Store connection metadata
            self.connection_metadata[websocket] = {
                "job_id": job_id,
                "connected_at": datetime.now().isoformat(),
                "client_info": client_info or {}
            }
            
            logger.info(f"WebSocket connected for job {job_id}. Total connections: {len(self.active_connections)}")
            
            # Send welcome message
            await self._send_to_websocket(websocket, {
                "type": "connection_established",
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Connected to upload progress stream"
            })
            
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {str(e)}")
            await self.disconnect(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        try:
            # Remove from active connections
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            # Remove from job-specific connections
            if websocket in self.connection_metadata:
                job_id = self.connection_metadata[websocket].get("job_id")
                if job_id and job_id in self.job_connections:
                    if websocket in self.job_connections[job_id]:
                        self.job_connections[job_id].remove(websocket)
                    
                    # Clean up empty job connections
                    if not self.job_connections[job_id]:
                        del self.job_connections[job_id]
                
                # Clean up metadata
                del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")
            
        except Exception as e:
            logger.error(f"Error during WebSocket disconnection: {str(e)}")
    
    async def send_progress_update(self, job_id: str, progress: UploadJobProgress):
        """Send progress update to all clients tracking a specific job"""
        if job_id not in self.job_connections:
            return
        
        message = {
            "type": "progress_update",
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "status": progress.status,
                "progress_percentage": progress.progress_percentage,
                "current_stage": progress.current_stage,
                "stage_details": progress.stage_details,
                "current_stage_index": progress.current_stage_index,
                "total_stages": progress.total_stages,
                "chunk_count": progress.chunk_count,
                "file_size_bytes": progress.file_size_bytes,
                "processed_bytes": progress.processed_bytes,
                "error_message": progress.error_message,
                "estimated_completion": progress.estimated_completion
            }
        }
        
        # Send to all connections for this job
        disconnected_connections = set()
        for websocket in self.job_connections[job_id].copy():
            try:
                await self._send_to_websocket(websocket, message)
            except Exception as e:
                logger.warning(f"Failed to send progress update to WebSocket: {str(e)}")
                disconnected_connections.add(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected_connections:
            await self.disconnect(websocket)
    
    async def send_job_completion(self, job_id: str, success: bool, document_id: str = None, error: str = None):
        """Send job completion notification"""
        if job_id not in self.job_connections:
            return
        
        message = {
            "type": "job_completion",
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "success": success,
                "document_id": document_id,
                "error_message": error,
                "final_status": "completed" if success else "failed"
            }
        }
        
        # Send to all connections for this job
        for websocket in list(self.job_connections[job_id]):
            try:
                await self._send_to_websocket(websocket, message)
            except Exception as e:
                logger.warning(f"Failed to send completion notification: {str(e)}")
                await self.disconnect(websocket)
    
    async def broadcast_system_message(self, message: Dict[str, Any]):
        """Broadcast a system message to all connected clients"""
        broadcast_message = {
            "type": "system_message",
            "timestamp": datetime.now().isoformat(),
            "data": message
        }
        
        disconnected_connections = set()
        for websocket in self.active_connections.copy():
            try:
                await self._send_to_websocket(websocket, broadcast_message)
            except Exception as e:
                logger.warning(f"Failed to broadcast system message: {str(e)}")
                disconnected_connections.add(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected_connections:
            await self.disconnect(websocket)
    
    async def send_queue_stats(self, stats: Dict[str, Any]):
        """Send queue statistics to all connected clients"""
        message = {
            "type": "queue_stats",
            "timestamp": datetime.now().isoformat(),
            "data": stats
        }
        
        await self.broadcast_system_message(message)
    
    async def _send_to_websocket(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {str(e)}")
            raise
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "job_connections": len(self.job_connections),
            "jobs_being_tracked": list(self.job_connections.keys()),
            "connections_per_job": {
                job_id: len(connections) 
                for job_id, connections in self.job_connections.items()
            }
        }
    
    async def cleanup_job_connections(self, job_id: str):
        """Clean up all connections for a completed job"""
        if job_id in self.job_connections:
            # Send final cleanup message
            cleanup_message = {
                "type": "job_cleanup",
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Job tracking completed. Connection can be closed."
            }
            
            for websocket in list(self.job_connections[job_id]):
                try:
                    await self._send_to_websocket(websocket, cleanup_message)
                except Exception as e:
                    logger.warning(f"Failed to send cleanup message: {str(e)}")
            
            # Remove job connections after a delay to allow message delivery
            await asyncio.sleep(1)
            
            for websocket in list(self.job_connections[job_id]):
                await self.disconnect(websocket)
    
    async def send_upload_progress_to_document_sync(self, job_id: str, progress: UploadJobProgress):
        """Send upload progress to document sync clients"""
        message = {
            "type": "upload_progress",
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "job_id": job_id,
                "filename": progress.filename,
                "file_size_bytes": progress.file_size_bytes,
                "status": progress.status.value,
                "progress_percentage": progress.progress_percentage,
                "current_stage": progress.current_stage,
                "stage_details": progress.stage_details,
                "current_stage_index": progress.current_stage_index,
                "total_stages": progress.total_stages,
                "chunk_count": progress.chunk_count,
                "processed_bytes": progress.processed_bytes,
                "error_message": progress.error_message,
                "estimated_completion": progress.estimated_completion
            }
        }
        
        # Send to all document sync connections
        if "document_sync" in self.job_connections:
            for websocket in list(self.job_connections["document_sync"]):
                try:
                    await self._send_to_websocket(websocket, message)
                except Exception as e:
                    logger.warning(f"Failed to send upload progress to document sync client: {str(e)}")
                    await self.disconnect(websocket)

class WebSocketManager:
    """
    WebSocket Manager Integration with Upload Job Manager
    Bridges upload progress with WebSocket broadcasting
    """
    
    def __init__(self, upload_job_manager):
        self.upload_job_manager = upload_job_manager
        self.connection_manager = ConnectionManager()
        
        # Start periodic stats broadcasting
        asyncio.create_task(self._periodic_stats_broadcast())
        
        logger.info("WebSocketManager initialized")
    
    async def handle_websocket_connection(self, websocket: WebSocket, job_id: str):
        """Handle new WebSocket connection for upload tracking"""
        try:
            # Validate job exists
            job = await self.upload_job_manager.get_job_details(job_id)
            if not job:
                await websocket.close(code=4004, reason="Job not found")
                return
            
            # Connect WebSocket
            await self.connection_manager.connect(websocket, job_id, {
                "job_filename": job.filename,
                "job_status": job.status
            })
            
            # Register progress callback for this job
            async def progress_callback(progress: UploadJobProgress):
                await self.connection_manager.send_progress_update(job_id, progress)
            
            self.upload_job_manager.add_progress_callback(job_id, progress_callback)
            
            # Send current job status immediately
            current_progress = await self.upload_job_manager.get_job_status(job_id)
            if current_progress:
                await self.connection_manager.send_progress_update(job_id, current_progress)
            
            try:
                # Keep connection alive
                while True:
                    try:
                        # Wait for client messages (like ping/pong)
                        data = await websocket.receive_text()
                        message = json.loads(data)
                        
                        if message.get("type") == "ping":
                            await websocket.send_text(json.dumps({
                                "type": "pong",
                                "timestamp": datetime.now().isoformat()
                            }))
                        
                    except WebSocketDisconnect:
                        break
                    except json.JSONDecodeError:
                        logger.warning("Invalid JSON received from WebSocket client")
                        continue
            
            finally:
                # Clean up
                self.upload_job_manager.remove_progress_callback(job_id, progress_callback)
                await self.connection_manager.disconnect(websocket)
        
        except Exception as e:
            logger.error(f"Error handling WebSocket connection for job {job_id}: {str(e)}")
            try:
                await websocket.close(code=1011, reason="Internal server error")
            except:
                pass
    
    async def _periodic_stats_broadcast(self):
        """Periodically broadcast queue statistics to all clients"""
        while True:
            try:
                await asyncio.sleep(30)  # Every 30 seconds
                
                # Get queue stats
                stats = await self.upload_job_manager.get_queue_stats()
                if stats:
                    await self.connection_manager.send_queue_stats(stats)
                
            except Exception as e:
                logger.error(f"Error in periodic stats broadcast: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive WebSocket statistics"""
        return {
            "websocket_stats": self.connection_manager.get_connection_stats(),
            "manager_info": {
                "active": True,
                "stats_broadcast_enabled": True
            }
        }