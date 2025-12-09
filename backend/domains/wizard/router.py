"""
Wizard Router for Streamworks Stream Creation
Step-by-step guided wizard with AI-assisted parameter extraction
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid

from services.xml_generator import XMLGenerator, JobType
from services.ai.parameter_extractor import ParameterExtractor
from services.xml_parser import XMLParser
from config import config

router = APIRouter(prefix="/api/wizard", tags=["Wizard"])

from services.db import db

# In-memory session storage removed - using Supabase


# Initialize AI extractor (lazy loading)
_extractor: Optional[ParameterExtractor] = None


def get_extractor() -> ParameterExtractor:
    """Get or create the parameter extractor instance"""
    global _extractor
    if _extractor is None:
        _extractor = ParameterExtractor()
    return _extractor


class WizardStep(str, Enum):
    """Wizard steps in order"""
    BASIC_INFO = "basic_info"
    CONTACT = "contact"
    JOB_TYPE = "job_type"
    JOB_DETAILS = "job_details"
    SCHEDULE = "schedule"
    PREVIEW = "preview"


STEP_ORDER = list(WizardStep)


class WizardSessionResponse(BaseModel):
    session_id: str
    current_step: WizardStep
    completed_steps: List[WizardStep]
    params: Dict[str, Any]
    ai_suggestions: Dict[str, Any]
    detected_job_type: Optional[str] = None
    completion_percent: float = 0.0


class StepData(BaseModel):
    """Generic step data model"""
    data: Dict[str, Any]


class AnalyzeDescriptionRequest(BaseModel):
    description: str


class AnalyzeDescriptionResponse(BaseModel):
    detected_job_type: Optional[str] = None
    suggested_params: Dict[str, Any] = {}
    confidence: float = 0.0
    explanation: str = ""


@router.get("/sessions")
async def list_all_sessions(limit: int = 50):
    """List all sessions for the dashboard"""
    sessions = db.list_sessions(limit=limit)
    return sessions


@router.post("/sessions", response_model=WizardSessionResponse)
async def create_wizard_session():
    """Create a new wizard session"""
    session_id = str(uuid.uuid4())
    
    initial_data = {
        "session_id": session_id,
        "current_step": WizardStep.BASIC_INFO,
        "completed_steps": [],
        "params": {},
        "ai_suggestions": {},
        "detected_job_type": None,
        "status": "draft",
    }
    
    db.save_session(session_id, initial_data)
    
    return WizardSessionResponse(
        session_id=session_id,
        current_step=WizardStep.BASIC_INFO,
        completed_steps=[],
        params={},
        ai_suggestions={},
        detected_job_type=None,
        completion_percent=0.0
    )


@router.get("/sessions/{session_id}", response_model=WizardSessionResponse)
async def get_wizard_session(session_id: str):
    """Get wizard session state"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    completion = calculate_wizard_completion(session)
    
    return WizardSessionResponse(
        session_id=session_id,
        current_step=session["current_step"],
        completed_steps=session["completed_steps"],
        params=session["params"],
        ai_suggestions=session.get("ai_suggestions", {}),
        detected_job_type=session.get("detected_job_type"),
        completion_percent=completion
    )


@router.post("/sessions/{session_id}/step/{step}", response_model=WizardSessionResponse)
async def save_step_data(session_id: str, step: WizardStep, step_data: StepData):
    """Save data for a specific wizard step"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Merge step data into params
    session["params"].update(step_data.data)
    
    # Handle job type selection
    if step == WizardStep.JOB_TYPE and "job_type" in step_data.data:
        session["detected_job_type"] = step_data.data["job_type"]
    
    # Mark step as completed
    if step not in session["completed_steps"]:
        session["completed_steps"].append(step)
    
    # Advance to next step
    current_index = STEP_ORDER.index(step)
    if current_index < len(STEP_ORDER) - 1:
        session["current_step"] = STEP_ORDER[current_index + 1]
    
    completion = calculate_wizard_completion(session)
    
    # Save updated session
    db.save_session(session_id, session)
    
    return WizardSessionResponse(
        session_id=session_id,
        current_step=session["current_step"],
        completed_steps=session["completed_steps"],
        params=session["params"],
        ai_suggestions=session.get("ai_suggestions", {}),
        detected_job_type=session.get("detected_job_type"),
        completion_percent=completion
    )


class AutoSaveRequest(BaseModel):
    """Autosave request - just params update, no step advancement"""
    params: Dict[str, Any]


@router.post("/sessions/{session_id}/autosave")
async def autosave_session(session_id: str, req: AutoSaveRequest):
    """Auto-save session data without advancing step"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Merge params
    session["params"].update(req.params)
    
    db.save_session(session_id, session)
    
    return {"status": "saved", "session_id": session_id}


@router.post("/sessions/{session_id}/complete")
async def complete_session(session_id: str):
    """Mark session as complete"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session["status"] = "complete"
    db.save_session(session_id, session)
    
    return {"status": "complete", "session_id": session_id}


@router.post("/sessions/{session_id}/analyze", response_model=AnalyzeDescriptionResponse)
async def analyze_description(session_id: str, req: AnalyzeDescriptionRequest):
    """Analyze description with AI to extract parameters and suggest job type"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        extractor = get_extractor()
        
        # Extract parameters from description
        result = extractor.extract(
            message=req.description,
            conversation_history=[],
            existing_params={}
        )
        
        # Extract suggested params
        suggested_params = {}
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
        
        for key, value in result_dict.items():
            if value is not None and key not in ['job_type', 'confidence', 'missing_required', 'follow_up_question']:
                suggested_params[key] = value
        
        # Store suggestions in session
        session["ai_suggestions"] = suggested_params
        session["detected_job_type"] = result.job_type
        
        db.save_session(session_id, session)
        
        # Generate explanation
        job_names = {
            "FILE_TRANSFER": "Dateitransfer",
            "STANDARD": "Standard-Job (Script-Ausführung)",
            "SAP": "SAP-Job"
        }
        
        explanation = f"Basierend auf Ihrer Beschreibung erkenne ich einen **{job_names.get(result.job_type, result.job_type)}**."
        
        if suggested_params:
            param_list = ", ".join([f"{k}: {v}" for k, v in list(suggested_params.items())[:3]])
            explanation += f" Erkannte Parameter: {param_list}"
        
        return AnalyzeDescriptionResponse(
            detected_job_type=result.job_type,
            suggested_params=suggested_params,
            confidence=result.confidence,
            explanation=explanation
        )
        
    except Exception as e:
        return AnalyzeDescriptionResponse(
            detected_job_type=None,
            suggested_params={},
            confidence=0.0,
            explanation=f"Analyse konnte nicht durchgeführt werden: {str(e)}"
        )


@router.post("/sessions/{session_id}/generate")
async def generate_xml(session_id: str):
    """Generate XML from wizard session data"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get job type (default to STANDARD)
    job_type = session.get("detected_job_type") or "STANDARD"
    
    # Generate XML
    generator = XMLGenerator()
    xml = generator.generate(
        job_type=job_type,
        params=session["params"]
    )
    
    return {
        "xml": xml,
        "job_type": job_type,
        "params": session["params"],
        "session_id": session_id
    }


@router.post("/sessions/{session_id}/go-to-step/{step}")
async def go_to_step(session_id: str, step: WizardStep):
    """Navigate to a specific wizard step"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session["current_step"] = step
    db.save_session(session_id, session)
    
    completion = calculate_wizard_completion(session)
    
    return WizardSessionResponse(
        session_id=session_id,
        current_step=session["current_step"],
        completed_steps=session["completed_steps"],
        params=session["params"],
        ai_suggestions=session.get("ai_suggestions", {}),
        detected_job_type=session.get("detected_job_type"),
        completion_percent=completion
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a wizard session"""
    success = db.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete session")
    return {"status": "deleted"}


@router.post("/sessions/import", response_model=WizardSessionResponse)
async def import_wizard_session(file: UploadFile = File(...)):
    """Import an existing XML file (Best Effort)"""
    try:
        content = await file.read()
        xml_str = content.decode("utf-8")
        
        parser = XMLParser()
        extracted_params = parser.parse(xml_str)
        
        # Create new session
        session_id = str(uuid.uuid4())
        
        initial_data = {
            "session_id": session_id,
            "current_step": WizardStep.BASIC_INFO,
            "completed_steps": [WizardStep.BASIC_INFO],
            "params": extracted_params,
            "ai_suggestions": {}, 
            "detected_job_type": extracted_params.get("job_type", "STANDARD"),
            "status": "draft",
        }
        
        # Pre-fill steps (Heuristic)
        if "agent_detail" in extracted_params or "sap_system" in extracted_params:
             initial_data["completed_steps"].append(WizardStep.JOB_TYPE)
             
        db.save_session(session_id, initial_data)
        
        completion = calculate_wizard_completion(initial_data)
        
        return WizardSessionResponse(
            session_id=session_id,
            current_step=WizardStep.BASIC_INFO,
            completed_steps=initial_data["completed_steps"],
            params=extracted_params,
            ai_suggestions={},
            detected_job_type=initial_data["detected_job_type"],
            completion_percent=completion
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.post("/sessions/{session_id}/duplicate", response_model=WizardSessionResponse)
async def duplicate_session(session_id: str):
    """Duplicate an existing session"""
    source_session = db.get_session(session_id)
    if not source_session:
        raise HTTPException(status_code=404, detail="Source session not found")
    
    new_session_id = str(uuid.uuid4())
    new_data = source_session.copy()
    new_data["session_id"] = new_session_id
    new_data["status"] = "draft"
    
    # Modify name to indicate copy
    if "stream_name" in new_data["params"]:
        new_data["params"]["stream_name"] = f"{new_data['params']['stream_name']}_COPY"
    
    db.save_session(new_session_id, new_data)
    
    completion = calculate_wizard_completion(new_data)
    
    return WizardSessionResponse(
        session_id=new_session_id,
        current_step=new_data.get("current_step", WizardStep.BASIC_INFO),
        completed_steps=new_data.get("completed_steps", []),
        params=new_data.get("params", {}),
        ai_suggestions=new_data.get("ai_suggestions", {}),
        detected_job_type=new_data.get("detected_job_type"),
        completion_percent=completion
    )


def calculate_wizard_completion(session: Dict) -> float:
    """Calculate wizard completion percentage"""
    completed = len(session.get("completed_steps", []))
    total = len(STEP_ORDER)
    return (completed / total) * 100 if total > 0 else 0.0


@router.get("/health")
async def health():
    """Health check for wizard service"""
    return {
        "status": "ok",
        "openai_configured": bool(config.OPENAI_API_KEY),
        "db_connected": db.client is not None
    }
