from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    model_name: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat mit LLM - einfach und funktional"""
    try:
        print(f"📨 Chat Request: {request.message}")
        
        response = llm_service.generate_response(request.message)
        
        print(f"✅ Chat Response: {response}")
        
        return ChatResponse(
            response=response,
            model_name=llm_service.model_name
        )
    except Exception as e:
        logger.error(f"❌ Chat Error: {str(e)}")
        print(f"❌ Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat Error: {str(e)}")

@router.get("/health")
async def chat_health():
    """Health Check für Chat"""
    return {
        "status": "ok",
        "model_loaded": llm_service.is_initialized,
        "model_name": llm_service.model_name,
        "device": llm_service.device
    }

@router.post("/test")
async def test_simple():
    """Test ohne LLM"""
    return {
        "response": "Test erfolgreich! Backend läuft.",
        "model_name": "test"
    }