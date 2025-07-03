# backend/app/api/v1/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_service import llm_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    mode: str  # "mock" oder "llm"
    
    class Config:
        # Fix für Pydantic model_ namespace warning
        protected_namespaces = ()

@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Chat mit SKI - Async mit Mock/LLM Mode"""
    try:
        logger.info(f"📨 Received chat message: {request.message[:50]}...")
        
        # Async LLM call
        response = await llm_service.generate_response(request.message)
        
        mode = "mock" if not settings.ENABLE_LLM else "llm"
        
        logger.info(f"✅ Generated AI response: {response[:50]}...")
        
        return ChatResponse(
            response=response,
            mode=mode
        )
        
    except Exception as e:
        logger.error(f"❌ Chat Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Chat service temporarily unavailable: {str(e)}"
        )

@router.get("/health")
async def chat_health():
    """Health Check für Chat Service"""
    return {
        "status": "healthy",
        "llm_enabled": settings.ENABLE_LLM,
        "llm_initialized": llm_service.is_initialized,
        "model_name": llm_service.model_name if settings.ENABLE_LLM else "mock",
        "device": llm_service.device if settings.ENABLE_LLM else "none",
        "mode": "mock" if not settings.ENABLE_LLM else "llm"
    }

@router.post("/toggle-llm")
async def toggle_llm_mode():
    """Development Helper: Toggle zwischen Mock und LLM Mode"""
    if settings.ENV != "development":
        raise HTTPException(status_code=403, detail="Only available in development")
    
    # Toggle mode
    settings.ENABLE_LLM = not settings.ENABLE_LLM
    llm_service.enable_llm = settings.ENABLE_LLM
    
    if settings.ENABLE_LLM:
        llm_service.initialize()
    
    return {
        "message": f"LLM mode {'enabled' if settings.ENABLE_LLM else 'disabled'}",
        "mode": "llm" if settings.ENABLE_LLM else "mock"
    }