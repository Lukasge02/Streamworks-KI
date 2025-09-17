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
import uuid
import asyncio
from pydantic import BaseModel

from services.chat_service_sqlalchemy import ChatServiceSQLAlchemy as ChatService
# from services.xml_stream_conversation_service import get_xml_stream_conversation_service, StreamConversationState
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

# Streaming response models
class StreamChunk(BaseModel):
    type: str  # "content", "done", "error"
    content: Optional[str] = None
    session_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

# ================================
# DEPENDENCY INJECTION
# ================================

async def get_chat_service() -> ChatService:
    """Dependency to get ChatService instance"""
    from services.chat_service_sqlalchemy import ChatServiceSQLAlchemy as ChatService
    return ChatService()


async def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """Extract user ID from header - with fallback for testing/development"""
    if not x_user_id:
        # For development/testing, use a default user ID
        # In production, this should require authentication
        logger.warning("No X-User-ID header provided, using fallback 'test-user' for development")
        return "test-user"
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

async def validate_session_access(
    session_id: str,
    user_id: str,
    chat_service: ChatService
):
    """Validate that session exists and user has access"""
    # First validate UUID format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID format"
        )

    try:
        # Try to get session messages to validate access
        await chat_service.get_session_messages(
            session_id=session_id,
            user_id=user_id,
            limit=1  # Just check if we can access
        )
    except Exception as e:
        if "not found or access denied" in str(e):
            raise HTTPException(
                status_code=404,
                detail="Session not found or access denied"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate session: {str(e)}"
        )

@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message with full RAG processing"""
    try:
        # First validate session access
        await validate_session_access(session_id, user_id, chat_service)

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

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )

# ================================
# STREAMING CHAT ENDPOINT
# ================================

@router.post("/sessions/{session_id}/stream")
async def stream_chat_message(
    session_id: str,
    request: SendMessageRequest,
    user_id: str = Depends(get_user_id),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message with streaming response using Server-Sent Events"""

    async def generate_stream():
        connection_id = f"{user_id}_{session_id}_{int(time.time())}"
        logger.info(f"Starting stream for connection {connection_id}")

        try:
            # Validate session access
            await validate_session_access(session_id, user_id, chat_service)

            # Send initial connection confirmation
            start_chunk = StreamChunk(
                type="start",
                session_id=session_id,
                content="Connection established"
            )
            yield f"data: {start_chunk.model_dump_json()}\n\n"

            # Process streaming response
            async for chunk in chat_service.process_message_stream(
                session_id=session_id,
                user_id=user_id,
                query=request.query,
                processing_mode=request.mode or "accurate"
            ):
                try:
                    chunk_data = StreamChunk(**chunk)
                    yield f"data: {chunk_data.model_dump_json()}\n\n"
                except Exception as chunk_error:
                    logger.warning(f"Failed to serialize chunk: {chunk_error}")
                    continue

        except HTTPException as http_error:
            logger.error(f"HTTP error in stream {connection_id}: {http_error.detail}")
            error_chunk = StreamChunk(
                type="error",
                session_id=session_id,
                error=f"Access denied: {http_error.detail}"
            )
            yield f"data: {error_chunk.model_dump_json()}\n\n"

        except asyncio.CancelledError:
            logger.info(f"Stream {connection_id} cancelled by client")
            cancel_chunk = StreamChunk(
                type="end",
                session_id=session_id,
                content="Connection closed by client"
            )
            yield f"data: {cancel_chunk.model_dump_json()}\n\n"

        except Exception as e:
            logger.error(f"Stream error {connection_id}: {str(e)}", exc_info=True)
            error_chunk = StreamChunk(
                type="error",
                session_id=session_id,
                error=f"Streaming failed: {str(e)}"
            )
            yield f"data: {error_chunk.model_dump_json()}\n\n"

        finally:
            # Send completion signal
            end_chunk = StreamChunk(
                type="end",
                session_id=session_id,
                content="Stream completed"
            )
            yield f"data: {end_chunk.model_dump_json()}\n\n"
            logger.info(f"Stream {connection_id} completed")

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control, Content-Type, Authorization",
            "X-Accel-Buffering": "no"  # Disable proxy buffering for nginx
        }
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
# XML STREAM CONVERSATION UTILITIES
# ================================

async def _convert_memory_to_conversation_state(
    session_id: str,
    context_turns: list,
    user_id: str
) -> Dict[str, Any]:
    """
    Convert ConversationMemoryStore format to XMLStreamConversationState format

    Args:
        session_id: Session identifier
        context_turns: List of ConversationTurn objects from memory store
        user_id: User identifier

    Returns:
        XMLStreamConversationState compatible dict
    """
    try:
        if not context_turns:
            return None

        # Initialize conversation state with defaults
        conversation_state = {
            "phase": "initialization",
            "job_type": None,
            "collected_data": {},
            "missing_required_fields": [],
            "validation_errors": [],
            "stream_id": None,
            "xml_content": None,
            "completion_percentage": 0.0,
            "last_user_message": None,
            "context_history": []
        }

        # Extract information from conversation turns
        for turn in context_turns:
            # Update last user message
            if hasattr(turn, 'user_message') and turn.user_message:
                conversation_state["last_user_message"] = turn.user_message

            # Add to context history
            conversation_state["context_history"].append({
                "role": "user",
                "content": getattr(turn, 'user_message', ''),
                "timestamp": getattr(turn, 'timestamp', '')
            })
            conversation_state["context_history"].append({
                "role": "assistant",
                "content": getattr(turn, 'ai_response', ''),
                "timestamp": getattr(turn, 'timestamp', '')
            })

            # Extract collected data from parameters
            if hasattr(turn, 'extracted_parameters') and turn.extracted_parameters:
                for param_name, param_value in turn.extracted_parameters.items():
                    # Map parameter names to nested structure
                    if '.' in param_name:
                        # Handle nested parameters like "jobForm.sapSystem"
                        parts = param_name.split('.')
                        current = conversation_state["collected_data"]

                        for part in parts[:-1]:
                            if part not in current:
                                current[part] = {}
                            current = current[part]

                        current[parts[-1]] = param_value
                    else:
                        conversation_state["collected_data"][param_name] = param_value

            # Update conversation phase if available
            if hasattr(turn, 'conversation_phase') and turn.conversation_phase != "unknown":
                conversation_state["phase"] = turn.conversation_phase

        # Calculate completion percentage based on collected data
        if conversation_state["collected_data"]:
            # Simple heuristic: more collected data = higher completion
            data_keys = len(conversation_state["collected_data"])
            conversation_state["completion_percentage"] = min(0.8, data_keys * 0.2)

        logger.info(f"Converted memory to conversation state: {len(context_turns)} turns, phase={conversation_state['phase']}")
        return conversation_state

    except Exception as e:
        logger.error(f"Error converting memory to conversation state: {str(e)}")
        return None

async def _save_conversation_state_to_memory(
    session_id: str,
    user_message: str,
    ai_response: str,
    conversation_state: Dict[str, Any],
    user_id: str = "default"
):
    """
    Save conversation turn to ConversationMemoryStore

    Args:
        session_id: Session identifier
        user_message: User's message
        ai_response: AI's response
        conversation_state: Current conversation state
        user_id: User identifier
    """
    try:
        from services.ai.conversation_memory_store import get_conversation_memory_store

        memory_store = get_conversation_memory_store()

        # Extract parameters from conversation state
        extracted_parameters = {}
        collected_data = conversation_state.get("collected_data", {})

        # Flatten nested parameters
        def flatten_dict(d, parent_key='', sep='.'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        if collected_data:
            extracted_parameters = flatten_dict(collected_data)

        # Determine success score based on phase and completion
        phase = conversation_state.get("phase", "initialization")
        completion = conversation_state.get("completion_percentage", 0.0)
        success_score = min(0.9, 0.3 + completion * 0.6)

        # Add conversation turn to memory
        await memory_store.add_conversation_turn(
            session_id=session_id,
            user_message=user_message,
            ai_response=ai_response,
            extracted_parameters=extracted_parameters,
            conversation_phase=phase,
            success_score=success_score
        )

        logger.info(f"Saved conversation turn to memory: session={session_id}, phase={phase}")

    except Exception as e:
        logger.error(f"Error saving conversation state to memory: {str(e)}")

# ================================
# XML STREAM CONVERSATION MODELS
# ================================

class XMLStreamConversationRequest(BaseModel):
    message: str
    session_id: str
    current_state: Optional[Dict[str, Any]] = None

class ContextualHintResponse(BaseModel):
    id: str
    type: str
    text: str
    example: Optional[str] = None
    icon: str = "💡"
    interactive: bool = False

class XMLStreamConversationResponse(BaseModel):
    message: str
    suggestions: List[str]  # Legacy - for backward compatibility
    hints: Optional[List[ContextualHintResponse]] = None  # New: Contextual hints
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

# @router.post("/xml-stream-conversation", response_model=XMLStreamConversationResponse)
# async def xml_stream_conversation(
#     request: XMLStreamConversationRequest,
#     user_id: str = Depends(get_user_id)
# ):
#     """Process conversation for XML stream creation with intelligent entity extraction"""
#     try:
#         # Get XML stream conversation service
#         conversation_service = await get_xml_stream_conversation_service()

        # Convert current_state from dict to StreamConversationState if provided
        current_state = None
        if request.current_state:
            try:
                # Import the dataclass and enum needed for reconstruction
                from services.xml_stream_conversation_service import StreamConversationState, StreamCreationPhase
                from schemas.xml_streams import JobType

                # Convert dict back to StreamConversationState dataclass
                state_dict = request.current_state

                # Safe enum conversion with fallbacks
                phase = 'initialization'
                if 'phase' in state_dict and state_dict['phase']:
                    try:
                        phase = StreamCreationPhase(state_dict['phase'])
                    except ValueError:
                        phase = StreamCreationPhase('initialization')

                job_type = None
                if 'job_type' in state_dict and state_dict['job_type']:
                    try:
                        job_type = JobType(state_dict['job_type'])
                    except (ValueError, KeyError):
                        job_type = None

                current_state = StreamConversationState(
                    phase=phase,
                    job_type=job_type,
                    collected_data=state_dict.get('collected_data', {}),
                    missing_required_fields=state_dict.get('missing_required_fields', []),
                    validation_errors=state_dict.get('validation_errors', []),
                    stream_id=state_dict.get('stream_id'),
                    xml_content=state_dict.get('xml_content'),
                    completion_percentage=float(state_dict.get('completion_percentage', 0.0)),
                    last_user_message=state_dict.get('last_user_message'),
                    context_history=state_dict.get('context_history', [])
                )
            except Exception as e:
                logger.error(f"Failed to reconstruct state from dict: {e}. Using None.")
                current_state = None

        # Process conversation
        response = await conversation_service.process_conversation(
            message=request.message,
            session_id=request.session_id,
            user_id=user_id,
            current_state=current_state
        )

        # ✅ NEU: Save conversation turn to memory store for persistence
        try:
            await _save_conversation_state_to_memory(
                session_id=request.session_id,
                user_message=request.message,
                ai_response=response.message,
                conversation_state={
                    "phase": response.state.phase.value if hasattr(response.state.phase, 'value') else str(response.state.phase),
                    "collected_data": response.state.collected_data,
                    "completion_percentage": response.state.completion_percentage,
                },
                user_id=user_id
            )
        except Exception as e:
            logger.warning(f"Failed to save conversation to memory store: {str(e)}")

        # Convert StreamConversationState dataclass to dict safely
        try:
            from dataclasses import asdict
            state_dict = asdict(response.state)

            # Ensure enums are serialized as strings
            if 'phase' in state_dict and hasattr(state_dict['phase'], 'value'):
                state_dict['phase'] = state_dict['phase'].value
            if 'job_type' in state_dict and state_dict['job_type'] and hasattr(state_dict['job_type'], 'value'):
                state_dict['job_type'] = state_dict['job_type'].value
        except Exception as e:
            logger.error(f"Failed to convert state to dict: {e}")
            state_dict = {}

        # Convert ContextualHints to response format
        hints_response = None
        if response.hints:
            hints_response = [
                ContextualHintResponse(
                    id=hint.id,
                    type=hint.type,
                    text=hint.text,
                    example=hint.example,
                    icon=hint.icon,
                    interactive=hint.interactive
                )
                for hint in response.hints
            ]

        return XMLStreamConversationResponse(
            message=response.message,
            suggestions=response.suggestions,
            hints=hints_response,
            state=state_dict,
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
    """Get current XML stream conversation state from persistent storage"""
    try:
        # ✅ FIXED: Echte Session State Persistence statt hardcoded null
        from services.ai.conversation_memory_store import get_conversation_memory_store

        memory_store = get_conversation_memory_store()

        # Get conversation context from persistent storage
        context_turns = await memory_store.get_conversation_context(session_id, max_turns=10)

        if not context_turns:
            logger.info(f"No conversation state found for session {session_id}")
            return None

        # Convert memory store format to XMLStreamConversationState format
        conversation_state = await _convert_memory_to_conversation_state(
            session_id, context_turns, user_id
        )

        logger.info(f"Retrieved conversation state for session {session_id}: phase={conversation_state.get('phase', 'unknown')}")
        return conversation_state

    except Exception as e:
        logger.error(f"Failed to get conversation state for session {session_id}: {str(e)}")
        # Return None instead of error to allow fresh start
        return None

# ================================
# HEALTH & STATUS
# ================================

@router.get("/health")
async def chat_health():
    """Enhanced health check for chat system with detailed RAG status"""
    try:
        # Test chat service
        chat_service = ChatService()
        chat_health_result = await chat_service.health_check()

        # Enhanced RAG service health check with detailed information
        rag_health_result = {
            "status": "disabled",
            "message": "RAG service not available",
            "components": {},
            "performance": {},
            "available_modes": []
        }

        try:
            if hasattr(chat_service, 'rag_service') and chat_service.rag_service:
                # Get detailed RAG health
                rag_health = await chat_service.rag_service.health_check()
                rag_health_result.update(rag_health)

                # Add component-specific health information
                if hasattr(chat_service.rag_service, '_initialized'):
                    rag_health_result["components"]["unified_rag"] = {
                        "status": "healthy" if chat_service.rag_service._initialized else "uninitialized",
                        "initialized": chat_service.rag_service._initialized
                    }

                # Add performance metrics if available
                if hasattr(chat_service.rag_service, '_performance_metrics'):
                    rag_health_result["performance"] = chat_service.rag_service._performance_metrics

                # Add available RAG modes
                rag_health_result["available_modes"] = ["fast", "accurate", "comprehensive"]

                # Add phase information
                if hasattr(chat_service.rag_service, '_query_processor') and chat_service.rag_service._query_processor:
                    rag_health_result["components"]["query_processor"] = {"status": "healthy", "phase": "2"}
                else:
                    rag_health_result["components"]["query_processor"] = {"status": "disabled", "phase": "1"}

                if hasattr(chat_service.rag_service, '_adaptive_retriever') and chat_service.rag_service._adaptive_retriever:
                    rag_health_result["components"]["adaptive_retriever"] = {"status": "healthy", "phase": "2"}
                else:
                    rag_health_result["components"]["adaptive_retriever"] = {"status": "disabled", "phase": "1"}

        except Exception as e:
            rag_health_result.update({
                "status": "error",
                "message": str(e),
                "components": {"unified_rag": {"status": "error", "error": str(e)}}
            })

        # Overall status with more granular assessment
        chat_healthy = chat_health_result.get("status") == "healthy"
        rag_status = rag_health_result.get("status", "disabled")

        # Determine overall status
        if chat_healthy and rag_status == "healthy":
            overall_status = "healthy"
        elif chat_healthy and rag_status in ["disabled", "degraded"]:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        return {
            "status": overall_status,
            "chat_service": chat_health_result,
            "rag_service": rag_health_result,
            "system_info": {
                "architecture": "unified_rag_service",
                "supported_modes": ["fast", "accurate", "comprehensive"],
                "backend": "llamaindex_ollama",
                "vector_store": "qdrant/chroma",
                "features": {
                    "query_processing": rag_status == "healthy",
                    "adaptive_retrieval": rag_status == "healthy",
                    "context_management": True,
                    "session_persistence": True
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Chat health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "components": {"chat_service": {"status": "error", "error": str(e)}},
            "timestamp": datetime.utcnow().isoformat()
        }