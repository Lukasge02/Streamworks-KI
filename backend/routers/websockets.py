"""
WebSocket Router for Real-time Upload Progress
"""

import asyncio
import logging
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from services.websocket_manager import ConnectionManager
from services.upload_job_manager import upload_job_manager

router = APIRouter(prefix="/ws", tags=["websockets"])
logger = logging.getLogger(__name__)

# Global connection manager
connection_manager = ConnectionManager()


@router.websocket("/documents")
async def document_sync_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time document synchronization and upload progress
    
    Handles document updates, real-time sync, and upload progress tracking.
    """
    # Accept the WebSocket connection first
    await websocket.accept()
    
    client_ip = websocket.client.host if websocket.client else "unknown"
    
    try:
        # Connect client to document sync stream
        await connection_manager.connect(
            websocket, 
            "document_sync", 
            {"client_ip": client_ip, "endpoint": "document_sync"}
        )
        
        logger.info(f"Document sync WebSocket client connected from {client_ip}")
        
        # Send initial welcome message
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to document sync stream",
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client messages (keep-alive, commands, etc.)
                data = await websocket.receive_text()
                
                # Handle client commands
                try:
                    import json
                    message = json.loads(data)
                    await handle_document_sync_message(websocket, message)
                except (json.JSONDecodeError, KeyError):
                    # Invalid message format, send error
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message format",
                        "expected_format": {"type": "ping|request_documents", "data": "..."}
                    })
                    
            except WebSocketDisconnect:
                logger.info(f"Document sync WebSocket client disconnected")
                break
            except Exception as e:
                logger.error(f"Error in document sync WebSocket message handling: {str(e)}")
                await websocket.send_json({
                    "type": "error", 
                    "message": f"Message handling error: {str(e)}"
                })
                break
                
    except Exception as e:
        logger.error(f"Document sync WebSocket connection error: {str(e)}")
    finally:
        # Ensure cleanup
        await connection_manager.disconnect(websocket)


@router.websocket("/upload/{job_id}")
async def upload_progress_websocket(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time upload progress tracking
    
    Clients connect with a job_id to receive progress updates for that specific upload.
    """
    # Accept the WebSocket connection first
    await websocket.accept()
    
    client_ip = websocket.client.host if websocket.client else "unknown"
    
    try:
        # Connect client to upload progress stream
        await connection_manager.connect(
            websocket, 
            job_id, 
            {"client_ip": client_ip, "endpoint": "upload_progress"}
        )
        
        logger.info(f"WebSocket client connected for upload job {job_id} from {client_ip}")
        
        # Send current job status if available
        current_job = upload_job_manager.get_job(job_id)
        if current_job:
            await connection_manager.send_progress_update(job_id, current_job)
        else:
            # Send initial "waiting" status
            await websocket.send_json({
                "type": "job_status",
                "job_id": job_id,
                "message": "Waiting for upload to start...",
                "status": "pending"
            })
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client messages (keep-alive, commands, etc.)
                data = await websocket.receive_text()
                
                # Handle client commands
                try:
                    import json
                    message = json.loads(data)
                    await handle_client_message(websocket, job_id, message)
                except (json.JSONDecodeError, KeyError):
                    # Invalid message format, send error
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message format",
                        "expected_format": {"type": "ping|status_request", "data": "..."}
                    })
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket client disconnected from upload job {job_id}")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket message handling: {str(e)}")
                await websocket.send_json({
                    "type": "error", 
                    "message": f"Message handling error: {str(e)}"
                })
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error for job {job_id}: {str(e)}")
    finally:
        # Ensure cleanup
        await connection_manager.disconnect(websocket)


async def handle_document_sync_message(websocket: WebSocket, message: dict):
    """Handle messages from document sync WebSocket clients"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Respond to ping with pong
        await websocket.send_json({
            "type": "pong",
            "timestamp": asyncio.get_event_loop().time()
        })
        
    elif message_type == "request_documents":
        # Client requests document list - would integrate with document service
        await websocket.send_json({
            "type": "documents_list",
            "data": [],  # TODO: Get actual documents from service
            "timestamp": asyncio.get_event_loop().time()
        })
        
    else:
        # Unknown message type
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "supported_types": ["ping", "request_documents"]
        })


async def handle_client_message(websocket: WebSocket, job_id: str, message: dict):
    """Handle messages from WebSocket clients"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Respond to ping with pong
        await websocket.send_json({
            "type": "pong",
            "timestamp": asyncio.get_event_loop().time(),
            "job_id": job_id
        })
        
    elif message_type == "status_request":
        # Send current job status
        current_job = upload_job_manager.get_job(job_id)
        if current_job:
            await connection_manager.send_progress_update(job_id, current_job)
        else:
            await websocket.send_json({
                "type": "job_status",
                "job_id": job_id,
                "message": "Job not found or completed",
                "status": "not_found"
            })
            
    elif message_type == "cancel_upload":
        # Handle upload cancellation (if supported)
        logger.info(f"Upload cancellation requested for job {job_id}")
        await websocket.send_json({
            "type": "cancellation_response",
            "job_id": job_id,
            "message": "Cancellation request received (not yet implemented)",
            "status": "acknowledged"
        })
        
    else:
        # Unknown message type
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "supported_types": ["ping", "status_request", "cancel_upload"]
        })


@router.get("/upload/demo")
async def websocket_demo_page():
    """
    Demo page for testing WebSocket upload progress
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Progress WebSocket Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .connected { background-color: #d4edda; color: #155724; }
            .disconnected { background-color: #f8d7da; color: #721c24; }
            .progress { background-color: #e2e3e5; height: 20px; border-radius: 10px; margin: 10px 0; }
            .progress-bar { background-color: #007bff; height: 100%; border-radius: 10px; transition: width 0.3s; }
            #messages { height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Upload Progress WebSocket Demo</h1>
            
            <div>
                <label>Job ID:</label>
                <input type="text" id="jobId" placeholder="Enter job ID or generate one">
                <button onclick="generateJobId()">Generate ID</button>
            </div>
            
            <div>
                <button onclick="connect()" id="connectBtn">Connect</button>
                <button onclick="disconnect()" id="disconnectBtn" disabled>Disconnect</button>
                <button onclick="requestStatus()">Request Status</button>
                <button onclick="sendPing()">Send Ping</button>
            </div>
            
            <div class="status" id="status">Disconnected</div>
            
            <div class="progress">
                <div class="progress-bar" id="progressBar" style="width: 0%"></div>
            </div>
            <div id="progressText">0% - Ready to connect</div>
            
            <div id="messages"></div>
        </div>

        <script>
            let ws = null;
            let jobId = null;

            function generateJobId() {
                jobId = 'demo_' + Math.random().toString(36).substr(2, 9);
                document.getElementById('jobId').value = jobId;
            }

            function connect() {
                jobId = document.getElementById('jobId').value.trim();
                if (!jobId) {
                    alert('Please enter a job ID');
                    return;
                }

                const wsUrl = `ws://localhost:8000/ws/upload/${jobId}`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    updateStatus('Connected', 'connected');
                    document.getElementById('connectBtn').disabled = true;
                    document.getElementById('disconnectBtn').disabled = false;
                    addMessage('Connected to WebSocket');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addMessage('Received: ' + JSON.stringify(data, null, 2));
                    
                    if (data.type === 'progress_update' && data.data) {
                        updateProgress(data.data.progress_percentage, data.data.current_stage, data.data.stage_details);
                    }
                };
                
                ws.onclose = function(event) {
                    updateStatus('Disconnected', 'disconnected');
                    document.getElementById('connectBtn').disabled = false;
                    document.getElementById('disconnectBtn').disabled = true;
                    addMessage('WebSocket connection closed');
                };
                
                ws.onerror = function(error) {
                    addMessage('WebSocket error: ' + error);
                };
            }

            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }

            function requestStatus() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({type: 'status_request'}));
                }
            }

            function sendPing() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({type: 'ping'}));
                }
            }

            function updateStatus(message, className) {
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = 'status ' + className;
            }

            function updateProgress(percentage, stage, details) {
                const progressBar = document.getElementById('progressBar');
                const progressText = document.getElementById('progressText');
                
                progressBar.style.width = percentage + '%';
                progressText.textContent = `${percentage.toFixed(1)}% - ${stage}${details ? ' (' + details + ')' : ''}`;
            }

            function addMessage(message) {
                const messages = document.getElementById('messages');
                const timestamp = new Date().toLocaleTimeString();
                messages.innerHTML += `<div>[${timestamp}] ${message}</div>`;
                messages.scrollTop = messages.scrollHeight;
            }

            // Generate initial job ID
            generateJobId();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


async def send_upload_progress_to_document_sync(job_id: str, progress):
    """Helper function to send upload progress to document sync clients"""
    await connection_manager.send_upload_progress_to_document_sync(job_id, progress)


# Export the connection manager for use by other services
__all__ = ["router", "connection_manager", "send_upload_progress_to_document_sync"]