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

from services.chat_service import ChatService
from services.unified_rag_service import UnifiedRAGService, RAGConfig
from services.vectorstore import VectorStoreService
from services.embeddings import EmbeddingService
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
    enable_rerank: Optional[bool] = False

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
            enable_rerank=request.enable_rerank
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
# DIRECT RAG QUERY (for compatibility)
# ================================

@router.post("", response_model=Dict[str, Any])  # This handles /api/chat directly
async def direct_rag_query(
    request: SendMessageRequest,
    user_id: str = Depends(get_user_id)
):
    """Direct RAG query without session management (for legacy compatibility)"""
    try:
        # Initialize RAG service directly - should use Ollama from env settings
        from services.vectorstore import VectorStoreService
        from services.embeddings import EmbeddingService
        from services.unified_rag_service import UnifiedRAGService
        
        vectorstore = VectorStoreService()
        await vectorstore.initialize()
        
        embeddings = EmbeddingService()
        rag_service = UnifiedRAGService(vectorstore, embeddings)
        
        # Process query
        response = await rag_service.query(
            query=request.query,
            mode=request.processing_mode or "accurate",
            include_sources=True,
            enable_rerank=request.enable_rerank or False
        )
        
        return {
            "answer": response["answer"],
            "confidence_score": response.get("confidence"),
            "processing_time": f"{response.get('response_time', 0):.2f}s",
            "sources": response.get("sources", []),
            "metadata": response.get("metadata", {}),
            "model_used": response.get("metadata", {}).get("model_used")
        }
        
    except Exception as e:
        logger.error(f"Direct RAG query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG query failed: {str(e)}"
        )

# ================================
# LOCAL-ONLY RAG ROUTES (100% Lokale KI)
# ================================

@router.post("/local-only", response_model=Dict[str, Any])
async def local_only_rag_query(
    request: SendMessageRequest,
    user_id: str = Depends(get_user_id)
):
    """Pure local RAG query using only Ollama - no OpenAI fallbacks"""
    try:
        # Initialize pure local RAG service
        from services.vectorstore import VectorStoreService
        from services.embeddings import EmbeddingService
        from services.local_rag_service import LocalRAGService
        
        vectorstore = VectorStoreService()
        await vectorstore.initialize()
        
        embeddings = EmbeddingService()
        local_rag = LocalRAGService(vectorstore, embeddings)
        
        # Process query with pure local AI
        response = await local_rag.query(
            query=request.query,
            mode=request.processing_mode or "accurate"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Local-only RAG query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Local RAG failed: {str(e)}"
        )

@router.get("/local-only/health")
async def local_rag_health():
    """Health check for local-only RAG system"""
    try:
        from services.vectorstore import VectorStoreService
        from services.embeddings import EmbeddingService
        from services.local_rag_service import LocalRAGService
        
        vectorstore = VectorStoreService()
        await vectorstore.initialize()
        
        embeddings = EmbeddingService()
        local_rag = LocalRAGService(vectorstore, embeddings)
        
        health = await local_rag.health_check()
        return health
        
    except Exception as e:
        logger.error(f"Local RAG health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

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
# HEALTH & STATUS
# ================================

@router.get("/health")
async def chat_health():
    """Health check for chat system"""
    try:
        chat_service = ChatService()
        health = await chat_service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"Chat health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }