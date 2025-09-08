"""
Chat Router for Streamworks RAG System
Handles chat sessions and RAG-powered conversations with Supabase integration
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
# Note: RAG Orchestrator is disabled for MVP - using simpler OpenAI RAG Service
# from services.rag_orchestrator import RAGOrchestrator, RAGRequest, RAGMode
from services.feature_flags import feature_flags
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

# ================================
# PYDANTIC MODELS
# ================================

class CreateSessionRequest(BaseModel):
    title: Optional[str] = None
    rag_config: Optional[Dict[str, Any]] = None
    context_filters: Optional[Dict[str, Any]] = None

class SendMessageRequest(BaseModel):
    query: str
    processing_mode: Optional[str] = "accurate"  # fast, accurate, comprehensive
    include_sources: Optional[bool] = True

# Advanced RAG models removed for MVP - using simplified OpenAI RAG service

class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None
    rag_config: Optional[Dict[str, Any]] = None
    context_filters: Optional[Dict[str, Any]] = None

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
    return ChatService()

# RAG Service Dependency Injection
async def get_rag_service():
    """Dependency to get Unified RAG Service instance"""
    from services.di_container import get_service
    return await get_service("unified_rag_service")

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
            title=request.title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            rag_config=request.rag_config,
            context_filters=request.context_filters
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
            title=request.title,
            rag_config=request.rag_config,
            context_filters=request.context_filters
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
    """Send a message and get RAG-powered response"""
    start_time = time.time()
    
    try:
        # Process the message with RAG
        response = await chat_service.process_message(
            session_id=session_id,
            user_id=user_id,
            query=request.query,
            processing_mode=request.processing_mode,
            include_sources=request.include_sources
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return SendMessageResponse(
            session_id=session_id,
            message_id=response["message_id"],
            answer=response["answer"],
            confidence_score=response.get("confidence_score"),
            processing_time_ms=processing_time_ms,
            sources=response.get("sources", []),
            model_used=response.get("model_used")
        )
        
    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )

# ================================
# SIMPLIFIED RAG QUERY
# ================================

@router.post("", response_model=Dict[str, Any])
async def direct_rag_query(
    request: SendMessageRequest,
    user_id: str = Depends(get_user_id),
    rag_service = Depends(get_rag_service)
):
    """Direct RAG query using simplified OpenAI RAG service"""
    start_time = time.time()
    
    try:
        # Process query with OpenAI RAG service
        response = await rag_service.query(
            query=request.query,
            mode=request.processing_mode or "accurate",
            include_sources=request.include_sources
        )
        
        # Track successful usage
        processing_time = time.time() - start_time
        feature_flags.track_usage("openai_rag_service", True, processing_time, user_id)
        
        return {
            "answer": response["answer"],
            "confidence_score": response.get("confidence"),
            "processing_time": f"{response.get('response_time', 0):.2f}s",
            "sources": response.get("sources", []),
            "metadata": {
                "service": "openai_rag",
                "processing_mode": request.processing_mode or "accurate",
                **response.get("metadata", {})
            },
            "model_used": response.get("metadata", {}).get("model_used")
        }
        
    except Exception as e:
        # Track failed usage
        processing_time = time.time() - start_time if 'start_time' in locals() else 0.0
        feature_flags.track_usage("openai_rag_service", False, processing_time, user_id)
        
        logger.error(f"Direct RAG query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG query failed: {str(e)}"
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
# DIRECT MESSAGE ENDPOINTS (for Frontend Integration)
# ================================

class DirectMessageRequest(BaseModel):
    role: str
    content: str
    confidence_score: Optional[float] = None
    processing_time: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    model_info: Optional[str] = None

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
# HEALTH & STATUS
# ================================

@router.get("/health")
async def chat_health():
    """Health check for chat system with Unified RAG"""
    try:
        # Test chat service
        chat_service = ChatService()
        chat_health_result = await chat_service.health_check()
        
        # Test unified RAG service
        from services.di_container import get_service
        rag_service = await get_service("unified_rag_service")
        rag_health_result = await rag_service.health_check()
        
        # Combine health results
        overall_status = "healthy" if (
            chat_health_result.get("status") == "healthy" and 
            rag_health_result.get("status") == "healthy"
        ) else "unhealthy"
        
        return {
            "status": overall_status,
            "chat_service": chat_health_result,
            "rag_service": rag_health_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }