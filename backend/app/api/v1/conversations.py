"""
Conversation Memory API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ConversationSummaryResponse(BaseModel):
    session_id: str
    message_count: int
    duration_minutes: int
    created_at: str
    last_activity: str
    main_topics: List[str]
    first_question: str
    last_question: str

class ConversationContextResponse(BaseModel):
    session_id: str
    context: str
    context_length: int
    message_count: int

class ConversationCleanupResponse(BaseModel):
    cleaned_sessions: int
    remaining_sessions: int

class AllConversationsResponse(BaseModel):
    conversations: List[ConversationSummaryResponse]
    total_count: int

@router.get("/")
async def get_all_conversations(limit: int = 50) -> AllConversationsResponse:
    """Get list of all conversation sessions (Admin)"""
    
    try:
        from app.services.conversation_memory import conversation_memory
        
        sessions = conversation_memory.get_all_sessions(limit=limit)
        
        conversation_summaries = [
            ConversationSummaryResponse(**session) for session in sessions
        ]
        
        return AllConversationsResponse(
            conversations=conversation_summaries,
            total_count=len(conversation_summaries)
        )
        
    except Exception as e:
        logger.error(f"❌ Get all conversations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/summary")
async def get_conversation_summary(session_id: str) -> ConversationSummaryResponse:
    """Get summary of specific conversation session"""
    
    try:
        from app.services.conversation_memory import conversation_memory
        
        summary = conversation_memory.get_session_summary(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationSummaryResponse(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get conversation summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/context")
async def get_conversation_context(session_id: str) -> ConversationContextResponse:
    """Get conversation context for session"""
    
    try:
        from app.services.conversation_memory import conversation_memory
        
        context = conversation_memory.get_context(session_id)
        
        # Count messages by checking for session
        try:
            summary = conversation_memory.get_session_summary(session_id)
            message_count = summary.get("message_count", 0) if summary else 0
        except:
            message_count = 0
        
        return ConversationContextResponse(
            session_id=session_id,
            context=context,
            context_length=len(context),
            message_count=message_count
        )
        
    except Exception as e:
        logger.error(f"❌ Get conversation context failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
async def delete_conversation(session_id: str):
    """Delete specific conversation session"""
    
    try:
        from app.services.conversation_memory import conversation_memory
        import os
        from pathlib import Path
        
        # Check if session exists
        summary = conversation_memory.get_session_summary(session_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete session file
        session_file = Path(conversation_memory.storage_path) / f"session_{session_id}.json"
        if session_file.exists():
            session_file.unlink()
        
        # Remove from cache
        if session_id in conversation_memory.sessions:
            del conversation_memory.sessions[session_id]
        
        logger.info(f"🗑️ Conversation deleted: {session_id}")
        
        return {
            "success": True,
            "message": f"Conversation {session_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete conversation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_conversations() -> ConversationCleanupResponse:
    """Clean up old/inactive conversations"""
    
    try:
        from app.services.conversation_memory import conversation_memory
        
        # Get count before cleanup
        sessions_before = conversation_memory.get_all_sessions(limit=1000)
        
        # Perform cleanup
        deleted_count = conversation_memory.cleanup_old_sessions()
        
        # Get count after cleanup
        sessions_after = conversation_memory.get_all_sessions(limit=1000)
        
        return ConversationCleanupResponse(
            cleaned_sessions=deleted_count,
            remaining_sessions=len(sessions_after)
        )
        
    except Exception as e:
        logger.error(f"❌ Conversation cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_conversation_stats():
    """Get conversation statistics"""
    
    try:
        from app.services.conversation_memory import conversation_memory
        from datetime import timedelta
        import os
        
        # Get all sessions
        all_sessions = conversation_memory.get_all_sessions(limit=1000)
        
        # Calculate statistics
        total_sessions = len(all_sessions)
        total_messages = sum(session.get("message_count", 0) for session in all_sessions)
        
        # Active sessions (last 24 hours)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        active_sessions = [
            session for session in all_sessions
            if datetime.fromisoformat(session.get("last_activity", "1970-01-01")) > cutoff_time
        ]
        
        # Storage usage
        storage_size = 0
        storage_path = conversation_memory.storage_path
        if storage_path.exists():
            for file in storage_path.glob("session_*.json"):
                storage_size += file.stat().st_size
        
        return {
            "total_sessions": total_sessions,
            "active_sessions_24h": len(active_sessions),
            "total_messages": total_messages,
            "average_messages_per_session": total_messages / total_sessions if total_sessions > 0 else 0,
            "storage_size_bytes": storage_size,
            "storage_size_mb": round(storage_size / 1024 / 1024, 2),
            "storage_path": str(storage_path),
            "session_timeout_hours": conversation_memory.session_timeout_hours,
            "max_messages_per_session": conversation_memory.max_messages_per_session,
            "context_window_size": conversation_memory.context_window_size
        }
        
    except Exception as e:
        logger.error(f"❌ Get conversation stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def conversation_health_check():
    """Health check for conversation memory service"""
    
    try:
        from app.services.conversation_memory import conversation_memory
        import uuid
        
        # Test basic functionality
        test_session_id = f"test_{uuid.uuid4().hex[:8]}"
        
        # Test add message
        success = conversation_memory.add_message(
            session_id=test_session_id,
            question="Test question",
            answer="Test answer"
        )
        
        # Test get context
        context = conversation_memory.get_context(test_session_id)
        
        # Test get summary
        summary = conversation_memory.get_session_summary(test_session_id)
        
        # Cleanup test session
        test_file = conversation_memory.storage_path / f"session_{test_session_id}.json"
        if test_file.exists():
            test_file.unlink()
        
        return {
            "status": "healthy",
            "service": "conversation_memory",
            "storage_path": str(conversation_memory.storage_path),
            "features": {
                "add_message": success,
                "get_context": len(context) > 0,
                "get_summary": bool(summary),
                "persistent_storage": True,
                "session_cleanup": True
            },
            "configuration": {
                "max_messages_per_session": conversation_memory.max_messages_per_session,
                "session_timeout_hours": conversation_memory.session_timeout_hours,
                "context_window_size": conversation_memory.context_window_size
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Conversation health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "conversation_memory",
            "error": str(e)
        }