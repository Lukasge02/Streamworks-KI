"""
Simple Q&A API Endpoint
Focused on answering StreamWorks documentation questions
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
import time
from typing import Optional

from app.services.simple_qa_service import simple_qa_service
from app.services.fast_qa_service import fast_qa_service
from app.services.intelligent_qa_service import intelligent_qa_service

logger = logging.getLogger(__name__)
router = APIRouter()


class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None


class QAResponse(BaseModel):
    answer: str
    documents_used: int = 0
    processing_time: float = 0.0
    session_id: Optional[str] = None


@router.post("/ask", response_model=QAResponse)
async def ask_question(request: QARequest):
    """
    Simple Q&A endpoint for StreamWorks documentation
    
    - No fallbacks
    - Clear error messages
    - Fast response times
    """
    start_time = time.time()
    
    try:
        # Log request
        logger.info(f"📝 Q&A: {request.question[:50]}...")
        
        # Get answer
        result = await simple_qa_service.answer_question(
            question=request.question,
            max_timeout=10.0  # 10 second maximum
        )
        
        # Calculate total time
        total_time = time.time() - start_time
        logger.info(f"✅ Q&A answered in {total_time:.2f}s")
        
        return QAResponse(
            answer=result["response"],
            documents_used=result["documents_used"],
            processing_time=total_time,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"❌ Q&A failed: {e}")
        
        # Clear error messages
        if "Keine relevanten Dokumente" in str(e):
            raise HTTPException(
                status_code=404,
                detail="Keine relevanten Dokumente gefunden. Bitte stellen Sie eine spezifischere Frage zu StreamWorks."
            )
        elif "Zeitüberschreitung" in str(e):
            raise HTTPException(
                status_code=504,
                detail="Die Antwortgenerierung hat zu lange gedauert. Bitte versuchen Sie es mit einer kürzeren Frage."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Fehler bei der Antwortgenerierung: {str(e)}"
            )


@router.post("/smart", response_model=QAResponse)
async def smart_ask_question(request: QARequest):
    """
    Intelligent Q&A endpoint with content analysis and smart ranking
    
    - Analyzes query intent
    - Intelligent document ranking
    - Content-aware response formatting
    - Response time: 1-3 seconds
    """
    start_time = time.time()
    
    try:
        # Log request
        logger.info(f"🧠 Smart Q&A: {request.question[:50]}...")
        
        # Get intelligent answer
        result = await intelligent_qa_service.answer_question(request.question)
        
        # Calculate total time
        total_time = time.time() - start_time
        logger.info(f"✅ Smart Q&A answered in {total_time:.2f}s (intent: {result.get('intent', 'unknown')})")
        
        return QAResponse(
            answer=result["response"],
            documents_used=result["documents_used"],
            processing_time=total_time,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"❌ Smart Q&A failed: {e}")
        
        # Clear error messages
        if "Keine relevanten Dokumente" in str(e):
            raise HTTPException(
                status_code=404,
                detail="Keine relevanten Dokumente zu Ihrer Frage gefunden. Bitte stellen Sie eine spezifischere Frage zu StreamWorks."
            )
        elif "zu langsam" in str(e):
            raise HTTPException(
                status_code=504,
                detail="Die Dokumentensuche hat zu lange gedauert."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Fehler bei der intelligenten Antwortgenerierung: {str(e)}"
            )


@router.post("/fast", response_model=QAResponse)
async def fast_ask_question(request: QARequest):
    """
    Ultra-fast Q&A endpoint using only document search (no LLM)
    
    - Much faster than full LLM processing
    - Returns structured document excerpts
    - No AI-generated content, just document search
    """
    start_time = time.time()
    
    try:
        # Log request
        logger.info(f"⚡ Fast Q&A: {request.question[:50]}...")
        
        # Get answer using document search only
        result = await fast_qa_service.answer_question(request.question)
        
        # Calculate total time
        total_time = time.time() - start_time
        logger.info(f"✅ Fast Q&A answered in {total_time:.2f}s")
        
        return QAResponse(
            answer=result["response"],
            documents_used=result["documents_used"],
            processing_time=total_time,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"❌ Fast Q&A failed: {e}")
        
        # Clear error messages
        if "Keine relevanten Dokumente" in str(e):
            raise HTTPException(
                status_code=404,
                detail="Keine relevanten Dokumente zu Ihrer Frage gefunden. Bitte stellen Sie eine spezifischere Frage zu StreamWorks."
            )
        elif "zu langsam" in str(e):
            raise HTTPException(
                status_code=504,
                detail="Die Dokumentensuche hat zu lange gedauert."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Fehler bei der Dokumentensuche: {str(e)}"
            )


@router.get("/health")
async def health_check():
    """Check if Q&A services are healthy"""
    try:
        simple_initialized = simple_qa_service.is_initialized
        fast_initialized = fast_qa_service.is_initialized
        
        return {
            "status": "healthy" if (simple_initialized or fast_initialized) else "not_ready",
            "services": {
                "simple_qa": simple_initialized,
                "fast_qa": fast_initialized
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }