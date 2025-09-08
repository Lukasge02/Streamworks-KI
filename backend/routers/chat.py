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
from services.rag_orchestrator import RAGOrchestrator, RAGRequest, RAGMode
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
    enable_rerank: Optional[bool] = True
    rag_mode: Optional[str] = "adaptive"  # speed, balanced, quality, adaptive
    max_results: Optional[int] = 10
    enable_advanced_rag: Optional[bool] = False  # Use new RAGOrchestrator

class AdvancedRAGRequest(BaseModel):
    query: str
    mode: Optional[str] = "adaptive"  # speed, balanced, quality, adaptive  
    max_results: Optional[int] = 10
    min_relevance_score: Optional[float] = 0.3
    document_filters: Optional[Dict[str, Any]] = None
    context_window: Optional[int] = 3
    enable_reranking: Optional[bool] = True
    custom_instructions: Optional[str] = None

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

# Global RAGOrchestrator instance (initialized once)
_rag_orchestrator: Optional[RAGOrchestrator] = None

async def get_rag_orchestrator() -> RAGOrchestrator:
    """Dependency to get RAGOrchestrator instance"""
    global _rag_orchestrator
    if _rag_orchestrator is None:
        _rag_orchestrator = RAGOrchestrator()
    return _rag_orchestrator

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
# ADVANCED RAG ENDPOINTS
# ================================

@router.post("/advanced", response_model=Dict[str, Any])
async def advanced_rag_query(
    request: AdvancedRAGRequest,
    user_id: str = Depends(get_user_id),
    rag_orchestrator: RAGOrchestrator = Depends(get_rag_orchestrator)
):
    """Advanced RAG query using state-of-the-art RAG orchestrator"""
    try:
        # Check if advanced RAG is enabled for this user
        if not feature_flags.is_enabled("advanced_rag_orchestrator", user_id):
            raise HTTPException(
                status_code=403,
                detail="Advanced RAG features are not enabled for your account"
            )
        
        start_time = time.time()
        # Map string mode to RAGMode enum
        mode_mapping = {
            "speed": RAGMode.SPEED,
            "balanced": RAGMode.BALANCED, 
            "quality": RAGMode.QUALITY,
            "adaptive": RAGMode.ADAPTIVE
        }
        
        rag_mode = mode_mapping.get(request.mode, RAGMode.ADAPTIVE)
        
        # Create RAGRequest
        rag_request = RAGRequest(
            query=request.query,
            mode=rag_mode,
            max_results=request.max_results,
            min_relevance_score=request.min_relevance_score,
            document_filters=request.document_filters,
            context_window=request.context_window,
            enable_reranking=request.enable_reranking,
            custom_instructions=request.custom_instructions
        )
        
        # Process with advanced RAG
        result = await rag_orchestrator.process_query(rag_request)
        
        # Track feature usage
        processing_time = time.time() - start_time
        feature_flags.track_usage("advanced_rag_orchestrator", True, processing_time, user_id)
        
        return {
            "query": result.query,
            "results": result.results,
            "total_found": result.total_results_found,
            "processing_time": f"{result.processing_time:.3f}s",
            "strategy_used": result.strategy_used,
            "complexity": result.complexity_detected.value,
            "confidence_score": result.confidence_score,
            "metadata": result.metadata
        }
        
    except HTTPException as e:
        # Track feature usage failure for HTTP exceptions (user errors)
        if e.status_code != 403:  # Don't track permission errors
            processing_time = time.time() - start_time if 'start_time' in locals() else 0.0
            feature_flags.track_usage("advanced_rag_orchestrator", False, processing_time, user_id)
        raise
    except Exception as e:
        # Track feature usage failure for system errors
        processing_time = time.time() - start_time if 'start_time' in locals() else 0.0
        feature_flags.track_usage("advanced_rag_orchestrator", False, processing_time, user_id)
        logger.error(f"Advanced RAG query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Advanced RAG query failed: {str(e)}"
        )

@router.get("/advanced/performance", response_model=Dict[str, Any])
async def get_rag_performance(
    user_id: str = Depends(get_user_id),
    rag_orchestrator: RAGOrchestrator = Depends(get_rag_orchestrator)
):
    """Get performance metrics from RAG orchestrator"""
    try:
        performance_report = await rag_orchestrator.get_performance_report()
        return performance_report
        
    except Exception as e:
        logger.error(f"Failed to get RAG performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.post("/advanced/optimize")
async def optimize_rag_system(
    user_id: str = Depends(get_user_id),
    rag_orchestrator: RAGOrchestrator = Depends(get_rag_orchestrator)
):
    """Trigger RAG system optimization"""
    try:
        optimization_results = await rag_orchestrator.optimize_system()
        return {
            "optimization_applied": True,
            "results": optimization_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"RAG optimization failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )

@router.get("/advanced/health")
async def advanced_rag_health(
    user_id: str = Depends(get_user_id),
    rag_orchestrator: RAGOrchestrator = Depends(get_rag_orchestrator)
):
    """Health check for advanced RAG system"""
    try:
        health_status = await rag_orchestrator.health_check()
        return health_status
        
    except Exception as e:
        logger.error(f"Advanced RAG health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# ================================
# DIRECT RAG QUERY (simplified for OpenAI)
# ================================

@router.post("", response_model=Dict[str, Any])  # This handles /api/chat directly
async def direct_rag_query(
    request: SendMessageRequest,
    user_id: str = Depends(get_user_id)
):
    """Direct RAG query with automatic advanced RAG integration based on feature flags"""
    start_time = time.time()
    
    try:
        # Check if advanced RAG is enabled for this user
        use_advanced_rag = (request.enable_advanced_rag and 
                           feature_flags.is_enabled("advanced_rag_orchestrator", user_id))
        
        if use_advanced_rag:
            logger.info(f"Using advanced RAG for user {user_id}")
            
            # Use advanced RAG orchestrator
            rag_orchestrator = await get_rag_orchestrator()
            
            # Map processing_mode to RAGMode
            mode_mapping = {
                "fast": RAGMode.SPEED,
                "accurate": RAGMode.BALANCED,
                "comprehensive": RAGMode.QUALITY
            }
            
            rag_mode = mode_mapping.get(request.processing_mode, RAGMode.ADAPTIVE)
            
            # Create RAGRequest
            rag_request = RAGRequest(
                query=request.query,
                mode=rag_mode,
                max_results=request.max_results or 10,
                enable_reranking=request.enable_rerank
            )
            
            # Process with advanced RAG
            result = await rag_orchestrator.process_query(rag_request)
            
            # Track feature usage
            processing_time = time.time() - start_time
            feature_flags.track_usage("advanced_rag_orchestrator", True, processing_time, user_id)
            
            return {
                "answer": result.results[0]["content"] if result.results else "No results found",
                "confidence_score": result.confidence_score,
                "processing_time": f"{result.processing_time:.2f}s",
                "sources": result.results,
                "metadata": {
                    "strategy_used": result.strategy_used,
                    "complexity": result.complexity_detected.value,
                    "total_found": result.total_results_found,
                    "service": "advanced_rag",
                    **result.metadata
                },
                "model_used": "RAGOrchestrator"
            }
            
        else:
            # Fallback to standard OpenAI RAG service
            logger.info(f"Using standard RAG for user {user_id}")
            
            # Initialize OpenAI RAG service
            from services.vectorstore import VectorStoreService
            from services.embeddings import EmbeddingService
            from services.openai_rag_service import OpenAIRAGService
            
            vectorstore = VectorStoreService()
            await vectorstore.initialize()
            
            embeddings = EmbeddingService()
            await embeddings.initialize()
            
            rag_service = OpenAIRAGService(vectorstore, embeddings)
            
            # Process query
            response = await rag_service.query(
                query=request.query,
                mode=request.processing_mode or "accurate",
                include_sources=True
            )
            
            # Track standard service usage
            processing_time = time.time() - start_time
            feature_flags.track_usage("standard_rag_service", True, processing_time, user_id)
            
            return {
                "answer": response["answer"],
                "confidence_score": response.get("confidence"),
                "processing_time": f"{response.get('response_time', 0):.2f}s",
                "sources": response.get("sources", []),
                "metadata": {
                    "service": "openai_rag",
                    **response.get("metadata", {})
                },
                "model_used": response.get("metadata", {}).get("model_used")
            }
        
    except Exception as e:
        # Track feature usage failure
        processing_time = time.time() - start_time if 'start_time' in locals() else 0.0
        service_name = "advanced_rag_orchestrator" if (hasattr(request, 'enable_advanced_rag') and 
                                                      request.enable_advanced_rag and 
                                                      feature_flags.is_enabled("advanced_rag_orchestrator", user_id)) else "standard_rag_service"
        feature_flags.track_usage(service_name, False, processing_time, user_id)
        
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
    """Health check for chat system with OpenAI RAG"""
    try:
        # Test chat service
        chat_service = ChatService()
        chat_health_result = await chat_service.health_check()
        
        # Test OpenAI RAG service
        from services.vectorstore import VectorStoreService
        from services.embeddings import EmbeddingService
        from services.openai_rag_service import OpenAIRAGService
        
        vectorstore = VectorStoreService()
        await vectorstore.initialize()
        embeddings = EmbeddingService()
        await embeddings.initialize()
        rag_service = OpenAIRAGService(vectorstore, embeddings)
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