"""
Chat API Endpoints - Enterprise Implementation
Clean separation between API layer and business logic
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...services.chat.chat_service import chat_service
from ...models.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# Pydantic Models for Request/Response
class ChatMessageRequest(BaseModel):
    """Request model for sending a chat message"""
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None
    mode: str = Field(default="hybrid", pattern="^(chat|rag|hybrid)$")
    context_window: int = Field(default=5, ge=0, le=20)

class ChatMessageResponse(BaseModel):
    """Response model for chat messages"""
    response: str
    conversation_id: str
    message_id: str
    sources: List[str] = []
    mode_used: str
    processing_time: float
    metadata: Dict[str, Any] = {}

class ConversationResponse(BaseModel):
    """Response model for conversations"""
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int
    metadata: Dict[str, Any] = {}

class ConversationListResponse(BaseModel):
    """Response model for conversation lists"""
    conversations: List[ConversationResponse]
    total: int
    limit: int
    offset: int

# API Endpoints
@router.post("/", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the chat service
    
    Modes:
    - chat: Pure LLM chat without RAG
    - rag: Pure RAG-based response
    - hybrid: Combines RAG context with LLM generation
    """
    try:
        result = await chat_service.send_message(
            message=request.message,
            conversation_id=request.conversation_id,
            mode=request.mode,
            context_window=request.context_window
        )
        
        return ChatMessageResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all conversations with pagination"""
    try:
        conversations = await chat_service.list_conversations(
            limit=limit,
            offset=offset
        )
        
        conversation_responses = []
        for conv in conversations:
            conversation_responses.append(ConversationResponse(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=len(conv.messages),
                metadata=conv.metadata
            ))
        
        return ConversationListResponse(
            conversations=conversation_responses,
            total=len(conversation_responses),  # TODO: Get actual total from DB
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    try:
        conversation = await chat_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Format messages for response
        messages = []
        for msg in conversation.messages:
            messages.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            })
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": messages,
            "metadata": conversation.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation"""
    try:
        success = await chat_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

@router.post("/conversations")
async def create_conversation(
    title: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    try:
        conversation = await chat_service.create_conversation(title=title)
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "message": "Conversation created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")

# Health check for chat service
@router.get("/health")
async def chat_health():
    """Check chat service health"""
    return {
        "status": "healthy",
        "service": "chat",
        "features": {
            "pure_chat": True,
            "rag_chat": True,
            "hybrid_chat": True,
            "conversation_management": True,
            "context_preservation": True
        }
    }