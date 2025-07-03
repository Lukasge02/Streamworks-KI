from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import uuid
import logging

from app.models.schemas import ChatRequest, ChatResponse, ChatMessage
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send message to AI and get response"""
    try:
        logger.info(f"📨 Received chat message: {request.message[:50]}...")
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Generate AI response
        ai_response = await llm_service.generate_response(
            message=request.message,
            conversation_id=conversation_id
        )
        
        logger.info(f"✅ Generated AI response: {ai_response[:50]}...")
        
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@router.get("/health")
async def chat_health():
    """Chat service health check"""
    return {
        "status": "healthy",
        "service": "chat",
        "llm_initialized": llm_service.is_initialized
    }