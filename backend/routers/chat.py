"""
Chat Router for Streamworks System
Handles basic chat sessions and conversations
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import time
import logging
from pydantic import BaseModel

from services.chat_service_sqlalchemy import ChatServiceSQLAlchemy as ChatService
from services.xml_stream_conversation_service import get_xml_stream_conversation_service, StreamConversationState
from services.feature_flags import feature_flags
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

# ================================
# PYDANTIC MODELS
# ================================

class CreateSessionRequest(BaseModel):
    title: Optional[str] = None

class SendMessageRequest(BaseModel):
    query: str
    mode: Optional[str] = "accurate"  # fast, accurate, comprehensive

class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None

class UpdateTitleRequest(BaseModel):
    title: str

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_at: Optional[datetime] = None
    is_active: bool

class ChatMessageResponse(BaseModel):
    id: str
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    sources: List[Dict[str, Any]] = []
    created_at: datetime
    sequence_number: int

class SendMessageResponse(BaseModel):
    session_id: str
    message_id: str
    answer: str
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    sources: List[Dict[str, Any]] = []
    model_used: Optional[str] = None

# ================================
# DEPENDENCY INJECTION
# ================================

async def get_chat_service() -> ChatService:
    """Dependency to get ChatService instance"""
    from services.chat_service_sqlalchemy import ChatServiceSQLAlchemy as ChatService
    return ChatService()


async def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """Extract user ID from header - for now using header, later from JWT"""
    if not x_user_id:
        raise HTTPException(
            status_code=401, 
            detail="X-User-ID header required"
        )
    return x_user_id

# ================================
# CHAT SESSION ROUTES
# ================================

@router.post("/sessions", response_model=Dict[str, str])
async def create_chat_session(
    request: CreateSessionRequest,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Create a new chat session for the user"""
    try:
        session_id = await chat_service.create_session(
            user_id=user_id,
            title=request.title or "Neue Unterhaltung"  # Will be auto-updated on first message
        )
        
        return {"session_id": session_id}
        
    except Exception as e:
        logger.error(f"Failed to create chat session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_sessions(
    user_id: str = Depends(get_user_id),
    active_only: bool = True,
    limit: int = 50,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all chat sessions for the user"""
    try:
        sessions = await chat_service.get_user_sessions(
            user_id=user_id,
            active_only=active_only,
            limit=limit
        )
        
        return [
            ChatSessionResponse(
                id=session["id"],
                title=session["title"],
                created_at=session["created_at"],
                updated_at=session["updated_at"],
                message_count=session["message_count"],
                last_message_at=session.get("last_message_at"),
                is_active=session["is_active"]
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Failed to get user sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sessions: {str(e)}"
        )

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: str,
    user_id: str = Depends(get_user_id),
    limit: int = 100,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all messages for a specific chat session"""
    try:
        messages = await chat_service.get_session_messages(
            session_id=session_id,
            user_id=user_id,
            limit=limit
        )
        
        return [
            ChatMessageResponse(
                id=message["id"],
                role=message["role"],
                content=message["content"],
                confidence_score=message.get("confidence_score"),
                processing_time_ms=message.get("processing_time_ms"),
                sources=message.get("sources", []),
                created_at=message["created_at"],
                sequence_number=message["sequence_number"]
            )
            for message in messages
        ]
        
    except Exception as e:
        logger.error(f"Failed to get session messages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get messages: {str(e)}"
        )

@router.put("/sessions/{session_id}")
async def update_chat_session(
    session_id: str,
    request: UpdateSessionRequest,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Update chat session metadata"""
    try:
        await chat_service.update_session(
            session_id=session_id,
            user_id=user_id,
            title=request.title
        )
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Failed to update session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Delete a chat session and all its messages"""
    try:
        await chat_service.delete_session(
            session_id=session_id,
            user_id=user_id
        )
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Failed to delete session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )

# ================================
# MESSAGE & RAG ROUTES
# ================================

@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message with full RAG processing"""
    try:
        # Process message through the chat service with RAG
        response_data = await chat_service.process_message(
            session_id=session_id,
            user_id=user_id,
            query=request.query,
            processing_mode=request.mode or "accurate",  # Use mode from request
            include_sources=True
        )

        return SendMessageResponse(
            session_id=session_id,
            message_id=response_data["message_id"],
            answer=response_data["answer"],
            confidence_score=response_data.get("confidence_score"),
            processing_time_ms=response_data.get("processing_time_ms", 0),
            sources=response_data.get("sources", []),
            model_used=response_data.get("model_used", "unified-rag-service")
        )

    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )

# ================================
# SIMPLIFIED RAG QUERY - TEMPORARILY DISABLED
# ================================

@router.post("", response_model=Dict[str, Any])
async def direct_query(
    request: SendMessageRequest,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Direct query endpoint without session - for quick RAG queries"""
    try:
        # Create temporary session for direct query
        temp_session_id = await chat_service.create_session(
            user_id=user_id,
            title="Direct Query"
        )

        # Process the query
        response_data = await chat_service.process_message(
            session_id=temp_session_id,
            user_id=user_id,
            query=request.query,
            processing_mode=request.mode or "accurate",
            include_sources=True
        )

        # Delete temporary session
        try:
            await chat_service.delete_session(temp_session_id, user_id)
        except:
            pass  # Don't fail if cleanup fails

        return {
            "answer": response_data["answer"],
            "confidence_score": response_data.get("confidence_score"),
            "processing_time_ms": response_data.get("processing_time_ms", 0),
            "sources": response_data.get("sources", []),
            "model_used": response_data.get("model_used", "unified-rag-service"),
            "mode": request.mode or "accurate"
        }

    except Exception as e:
        logger.error(f"Direct query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Direct query failed: {str(e)}"
        )


# ================================
# UTILITY ROUTES  
# ================================

@router.get("/stats")
async def get_chat_stats(
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get chat statistics for the user"""
    try:
        stats = await chat_service.get_user_stats(user_id)
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get chat stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )

@router.get("/search")
async def search_messages(
    q: str,
    user_id: str = Depends(get_user_id),
    limit: int = 20,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Search through user's chat messages"""
    try:
        results = await chat_service.search_messages(
            user_id=user_id,
            query=q,
            limit=limit
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search messages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search messages: {str(e)}"
        )

# ================================
# TITLE MANAGEMENT ROUTES
# ================================

@router.post("/sessions/{session_id}/regenerate-title", response_model=Dict[str, str])
async def regenerate_session_title(
    session_id: str,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Regenerate title for a chat session using AI"""
    try:
        new_title = await chat_service.regenerate_session_title(
            session_id=session_id,
            user_id=user_id
        )
        
        return {"title": new_title}
        
    except Exception as e:
        logger.error(f"Failed to regenerate title: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate title: {str(e)}"
        )

@router.put("/sessions/{session_id}/title", response_model=Dict[str, str])
async def update_session_title(
    session_id: str,
    request: UpdateTitleRequest,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Update session title with custom title"""
    try:
        new_title = await chat_service.update_session_title(
            session_id=session_id,
            user_id=user_id,
            title=request.title
        )
        
        return {"title": new_title}
        
    except Exception as e:
        logger.error(f"Failed to update title: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update title: {str(e)}"
        )

# ================================
# DIRECT MESSAGE ENDPOINTS (for Frontend Integration)
# ================================

class DirectMessageRequest(BaseModel):
    role: str
    content: str
    confidence_score: Optional[float] = None
    processing_time: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    model_info: Optional[str] = None

# ================================
# XML STREAM CONVERSATION MODELS
# ================================

class XMLStreamConversationRequest(BaseModel):
    message: str
    session_id: str
    current_state: Optional[Dict[str, Any]] = None

class XMLStreamConversationResponse(BaseModel):
    message: str
    suggestions: List[str]
    state: Dict[str, Any]
    requires_user_input: bool = True
    action_taken: Optional[str] = None
    errors: List[str] = []

@router.post("/sessions/{session_id}/messages/direct", response_model=Dict[str, str])
async def save_message_direct(
    session_id: str,
    request: DirectMessageRequest,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Direct message saving endpoint for frontend integration"""
    try:
        # Convert processing time to milliseconds if it's a string with 's'
        processing_time_ms = None
        if request.processing_time:
            if isinstance(request.processing_time, str) and request.processing_time.endswith('s'):
                try:
                    time_value = float(request.processing_time[:-1])
                    processing_time_ms = int(time_value * 1000)
                except ValueError:
                    pass
            elif isinstance(request.processing_time, str) and request.processing_time.endswith('ms'):
                try:
                    processing_time_ms = int(float(request.processing_time[:-2]))
                except ValueError:
                    pass
        
        message_id = await chat_service.add_message(
            session_id=session_id,
            user_id=user_id,
            role=request.role,
            content=request.content,
            confidence_score=request.confidence_score,
            processing_time_ms=processing_time_ms,
            sources=request.sources or [],
            model_used=request.model_info
        )
        
        return {"message_id": message_id}
        
    except Exception as e:
        logger.error(f"Failed to save message directly: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save message: {str(e)}"
        )

# ================================
# XML STREAM CONVERSATION ENDPOINTS
# ================================

@router.post("/xml-stream-conversation", response_model=XMLStreamConversationResponse)
async def xml_stream_conversation(
    request: XMLStreamConversationRequest,
    user_id: str = Depends(get_user_id)
):
    """Process conversation for XML stream creation with intelligent entity extraction"""
    try:
        # Get XML stream conversation service
        conversation_service = await get_xml_stream_conversation_service()

        # Convert current_state from dict to StreamConversationState if provided
        current_state = None
        if request.current_state:
            # Parse the state - for now just pass it through
            # In a real implementation, you'd properly deserialize it
            current_state = request.current_state

        # Process conversation
        response = await conversation_service.process_conversation(
            message=request.message,
            session_id=request.session_id,
            user_id=user_id,
            current_state=current_state
        )

        return XMLStreamConversationResponse(
            message=response.message,
            suggestions=response.suggestions,
            state=response.state.__dict__,  # Convert state to dict
            requires_user_input=response.requires_user_input,
            action_taken=response.action_taken,
            errors=response.errors or []
        )

    except Exception as e:
        logger.error(f"XML stream conversation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Conversation processing failed: {str(e)}"
        )

@router.get("/xml-stream-conversation/{session_id}/state")
async def get_xml_stream_conversation_state(
    session_id: str,
    user_id: str = Depends(get_user_id)
):
    """Get current XML stream conversation state"""
    try:
        # For now, return a placeholder state
        # In a real implementation, you'd retrieve stored state
        return {
            "session_id": session_id,
            "phase": "initialization",
            "completion_percentage": 0.0,
            "collected_data": {},
            "missing_required_fields": []
        }

    except Exception as e:
        logger.error(f"Failed to get conversation state: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get state: {str(e)}"
        )

# ================================
# HEALTH & STATUS
# ================================

@router.get("/health")
async def chat_health():
    """Health check for chat system"""
    try:
        # Test chat service
        chat_service = ChatService()
        chat_health_result = await chat_service.health_check()
        
        # Check RAG service health
        rag_health_result = {"status": "disabled", "message": "RAG service not available"}
        try:
            if hasattr(chat_service, 'rag_service') and chat_service.rag_service:
                rag_health_result = await chat_service.rag_service.health_check()
        except Exception as e:
            rag_health_result = {"status": "error", "message": str(e)}

        # Overall status based on both services
        chat_healthy = chat_health_result.get("status") == "healthy"
        rag_healthy = rag_health_result.get("status") in ["healthy", "disabled"]  # Disabled is okay
        overall_status = "healthy" if chat_healthy and rag_healthy else "degraded"
        
        return {
            "status": overall_status,
            "chat_service": chat_health_result,
            "rag_service": rag_health_result,
            "note": "Professional RAG service with LlamaIndex integration",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }