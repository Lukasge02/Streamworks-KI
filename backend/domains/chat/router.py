"""
Chat Router for Streamworks XML Generation
KI-unterstützte Konversation für Stream-Erstellung mit OpenAI
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import traceback

from services.xml_generator import XMLGenerator, JobType
from services.ai.parameter_extractor import ParameterExtractor
from services.ai.schemas import StreamworksParams
from config import config

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# In-memory session storage
sessions: Dict[str, Dict] = {}

# Initialize AI extractor (lazy loading)
_extractor: Optional[ParameterExtractor] = None


def get_extractor() -> ParameterExtractor:
    """Get or create the parameter extractor instance"""
    global _extractor
    if _extractor is None:
        _extractor = ParameterExtractor()
    return _extractor


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    # Frontend can send current params to ensure backend has latest state
    current_params: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    detected_job_type: Optional[str] = None
    extracted_params: Dict[str, Any] = {}
    completion_percent: float = 0.0
    confidence: float = 1.0
    xml_preview: Optional[str] = None


class GenerateXMLRequest(BaseModel):
    session_id: str


@router.post("/message", response_model=ChatResponse)
async def send_message(msg: ChatMessage):
    """
    Send a message to the chat and get AI response with parameter extraction
    """
    # Create or get session
    session_id = msg.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = {
            "params": {},
            "job_type": None,
            "messages": [],
            "extraction_complete": False
        }
    
    session = sessions[session_id]
    
    # Defensive check: Ensure session structure is valid
    if "messages" not in session or not isinstance(session["messages"], list):
        print(f"Repairing corrupt session state for {session_id}")
        session["messages"] = []
        if "params" not in session: session["params"] = {}
    
    # Update session with current frontend params if provided
    # This prevents the backend from overwriting manual edits with stale state
    if msg.current_params:
        session["params"].update(msg.current_params)
        
    session["messages"].append({"role": "user", "content": msg.message})
    
    try:
        # Use AI extractor
        extractor = get_extractor()
        
        # Extract parameters with conversation context
        extraction_result = extractor.extract(
            message=msg.message,
            conversation_history=session["messages"][-6:],
            existing_params=session["params"]
        )
        
        # Merge with existing params
        session["params"] = extractor.merge_params(
            session["params"], 
            extraction_result
        )
        session["job_type"] = extraction_result.job_type
        
        # Calculate completion percentage
        completion = calculate_completion(
            extraction_result.job_type, 
            session["params"],
            extraction_result.missing_required
        )
        
        # Generate response
        if extraction_result.missing_required:
            response = extraction_result.follow_up_question or generate_response(
                extraction_result, 
                session["params"]
            )
        else:
            session["extraction_complete"] = True
            response = "✅ Alle Parameter wurden erfasst! Sie können jetzt die XML generieren."
        
        # Add AI response to history
        session["messages"].append({"role": "assistant", "content": response})
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            detected_job_type=session["job_type"],
            extracted_params=session["params"],
            completion_percent=completion,
            confidence=extraction_result.confidence
        )
        
    except Exception as e:
        print(f"Error in chat processing: {e}")
        traceback.print_exc()
        
        # Fallback response on error
        error_response = f"⚠️ Fehler bei der Verarbeitung: {str(e)}"
        
        # Check if it's an API key issue
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            error_response = "⚠️ OpenAI API-Key nicht konfiguriert. Bitte .env Datei im backend/ Ordner erstellen."
        
        return ChatResponse(
            response=error_response,
            session_id=session_id,
            detected_job_type=None,
            extracted_params={},
            completion_percent=0,
            confidence=0
        )


def calculate_completion(job_type: str, params: Dict, missing: List[str]) -> float:
    """Calculate completion percentage based on job type requirements"""
    required_fields = {
        "FILE_TRANSFER": ["stream_name", "source_agent", "target_agent", "source_file_pattern"],
        "STANDARD": ["stream_name", "agent_detail", "main_script"],
        "SAP": ["stream_name", "sap_report"]
    }
    
    required = required_fields.get(job_type, ["stream_name"])
    
    if not required:
        return 100.0
    
    completed = sum(1 for field in required if params.get(field))
    return (completed / len(required)) * 100


def generate_response(extraction: StreamworksParams, params: Dict) -> str:
    """Generate a helpful response based on extraction results"""
    job_names = {
        "FILE_TRANSFER": "Dateitransfer",
        "STANDARD": "Standard-Job",
        "SAP": "SAP-Job"
    }
    
    job_name = job_names.get(extraction.job_type, "Job")
    
    response_parts = [f"Ich habe einen **{job_name}** erkannt."]
    
    # Show what was extracted
    extracted = []
    if params.get("stream_name"):
        extracted.append(f"Stream: {params['stream_name']}")
    if params.get("source_agent"):
        extracted.append(f"Quelle: {params['source_agent']}")
    if params.get("target_agent"):
        extracted.append(f"Ziel: {params['target_agent']}")
    if params.get("agent_detail"):
        extracted.append(f"Agent: {params['agent_detail']}")
    if params.get("schedule"):
        extracted.append(f"Zeitplan: {params['schedule']}")
    
    if extracted:
        response_parts.append("\n\n**Erkannt:**\n• " + "\n• ".join(extracted))
    
    # Add follow-up question
    if extraction.follow_up_question:
        response_parts.append(f"\n\n{extraction.follow_up_question}")
    
    return "".join(response_parts)


@router.post("/generate")
async def generate_xml(req: GenerateXMLRequest):
    """
    Generate XML from collected session parameters
    """
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[req.session_id]
    
    generator = XMLGenerator()
    xml = generator.generate(
        job_type=session["job_type"] or "STANDARD",
        params=session["params"]
    )
    
    return {
        "xml": xml,
        "job_type": session["job_type"],
        "params": session["params"]
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get session details
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and start fresh
    """
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "deleted"}


@router.get("/health")
async def health():
    """Health check for chat service"""
    api_configured = bool(config.OPENAI_API_KEY)
    return {
        "status": "ok",
        "openai_configured": api_configured,
        "model": config.LLM_MODEL if api_configured else None
    }
