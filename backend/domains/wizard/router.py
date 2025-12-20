"""
Wizard Router for Streamworks Stream Creation
Step-by-step guided wizard with AI-assisted parameter extraction
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid

from services.xml_generator import XMLGenerator
from services.ai.parameter_extractor import ParameterExtractor
from services.xml_parser import XMLParser
from services.stream_command_service import stream_command_service
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

    DESCRIBE = "describe"  # NEW: Document upload or text description for AI analysis
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


class StreamCommandRequest(BaseModel):
    """Request for natural language stream commands"""

    command: str
    session_id: Optional[str] = None  # Optional context for param updates


class StreamCommandResponse(BaseModel):
    """Response from stream command execution"""

    success: bool
    session_id: Optional[str] = None
    action: str = ""
    changes: Optional[Dict[str, Any]] = None
    original_name: Optional[str] = None
    redirect_url: Optional[str] = None
    message: str = ""
    suggestions: Optional[List[str]] = None


@router.post("/sessions/command", response_model=StreamCommandResponse)
async def execute_stream_command(request: StreamCommandRequest):
    """
    Execute a natural language command for stream editing.

    Examples:
    - "Benenne test123 in teststream456 um"
    - "Öffne Stream xyz"
    - "Setze Agent auf UC4_UNIX_01" (requires session_id)
    - "Dupliziere Stream abc"
    """
    # Parse the command
    parsed = stream_command_service.parse_command(request.command)

    # Execute the command
    result = stream_command_service.execute_command(parsed, request.session_id)

    return StreamCommandResponse(
        success=result.success,
        session_id=result.session_id,
        action=result.action,
        changes=result.changes,
        original_name=result.original_name,
        redirect_url=result.redirect_url,
        message=result.message,
        suggestions=result.suggestions,
    )


@router.get("/sessions/search")
async def search_sessions(query: str, limit: int = 10):
    """
    Fuzzy search for streams by name.

    Returns matching sessions sorted by relevance score.
    """
    matches = stream_command_service.find_stream_by_name(query, threshold=0.3)

    # Limit results and clean up internal fields
    results = []
    for match in matches[:limit]:
        result = {k: v for k, v in match.items() if not k.startswith("_")}
        results.append(result)

    return results


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
        "current_step": WizardStep.DESCRIBE,
        "completed_steps": [],
        "params": {},
        "ai_suggestions": {},
        "detected_job_type": None,
        "status": "draft",
    }

    db.save_session(session_id, initial_data)

    return WizardSessionResponse(
        session_id=session_id,
        current_step=WizardStep.DESCRIBE,
        completed_steps=[],
        params={},
        ai_suggestions={},
        detected_job_type=None,
        completion_percent=0.0,
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
        completion_percent=completion,
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
        completion_percent=completion,
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


@router.post(
    "/sessions/{session_id}/analyze", response_model=AnalyzeDescriptionResponse
)
async def analyze_description(session_id: str, req: AnalyzeDescriptionRequest):
    """Analyze description with AI to extract parameters and suggest job type"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        extractor = get_extractor()

        # Extract parameters from description
        result = extractor.extract(
            message=req.description, conversation_history=[], existing_params={}
        )

        # Extract suggested params
        suggested_params = {}
        result_dict = (
            result.model_dump() if hasattr(result, "model_dump") else result.dict()
        )

        for key, value in result_dict.items():
            if value is not None and key not in [
                "job_type",
                "confidence",
                "missing_required",
                "follow_up_question",
            ]:
                suggested_params[key] = value

        # Store suggestions in session
        session["ai_suggestions"] = suggested_params
        session["detected_job_type"] = result.job_type
        
        # Also save extracted params directly to params for form pre-filling
        if "params" not in session:
            session["params"] = {}
        for key, value in suggested_params.items():
            # Only set if not already explicitly set by user
            if key not in session["params"] or not session["params"][key]:
                session["params"][key] = value
        
        # Save the original AI input separately (not as stream_documentation!)
        session["params"]["ai_input_text"] = req.description

        db.save_session(session_id, session)

        # Generate explanation
        job_names = {
            "FILE_TRANSFER": "Dateitransfer",
            "STANDARD": "Standard-Job (Script-Ausführung)",
            "SAP": "SAP-Job",
        }

        explanation = f"Basierend auf Ihrer Beschreibung erkenne ich einen **{job_names.get(result.job_type, result.job_type)}**."

        if suggested_params:
            param_list = ", ".join(
                [f"{k}: {v}" for k, v in list(suggested_params.items())[:3]]
            )
            explanation += f" Erkannte Parameter: {param_list}"

        return AnalyzeDescriptionResponse(
            detected_job_type=result.job_type,
            suggested_params=suggested_params,
            confidence=result.confidence,
            explanation=explanation,
        )

    except Exception as e:
        return AnalyzeDescriptionResponse(
            detected_job_type=None,
            suggested_params={},
            confidence=0.0,
            explanation=f"Analyse konnte nicht durchgeführt werden: {str(e)}",
        )


@router.post("/sessions/{session_id}/generate-descriptions")
async def generate_descriptions(session_id: str):
    """Generate short_description and stream_documentation from AI input text"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    ai_input = session.get("params", {}).get("ai_input_text", "")
    if not ai_input:
        return {"short_description": "", "stream_documentation": ""}
    
    # Generate short description (max 200 chars, one line summary)
    short_desc = ai_input
    # Find first sentence or truncate
    if "." in ai_input[:200]:
        short_desc = ai_input[:ai_input.find(".", 0, 200) + 1]
    else:
        short_desc = ai_input[:200] if len(ai_input) > 200 else ai_input
    
    # Remove line breaks for short description
    short_desc = " ".join(short_desc.split())
    
    # Stream documentation is the full, cleaned input
    documentation = ai_input.strip()
    
    # Save to session
    if "params" not in session:
        session["params"] = {}
    session["params"]["short_description"] = short_desc
    session["params"]["stream_documentation"] = documentation
    db.save_session(session_id, session)
    
    return {
        "short_description": short_desc,
        "stream_documentation": documentation
    }

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
    xml = generator.generate(job_type=job_type, params=session["params"])

    return {
        "xml": xml,
        "job_type": job_type,
        "params": session["params"],
        "session_id": session_id,
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
        completion_percent=completion,
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
        parsed = parser.parse(xml_str)

        # Extract the flat params for wizard compatibility
        wizard_params = parsed.get("params", {})
        stream_data = parsed.get("stream", {})

        # Build flat params structure matching what wizard expects
        flat_params = {
            "stream_name": stream_data.get("name") or wizard_params.get("stream_name"),
            "short_description": stream_data.get("short_description")
            or wizard_params.get("short_description"),
            "stream_documentation": stream_data.get("documentation")
            or wizard_params.get("stream_documentation"),
            "agent_detail": stream_data.get("agent_detail")
            or wizard_params.get("agent_detail"),
            "stream_path": stream_data.get("stream_path")
            or wizard_params.get("stream_path"),
            # Job params
            "job_type": parsed.get("detected_job_type")
            or wizard_params.get("job_type", "STANDARD"),
            "main_script": wizard_params.get("main_script"),
            "job_name": wizard_params.get("job_name"),
            "job_description": wizard_params.get("job_description"),
            # File transfer params
            "source_agent": wizard_params.get("source_agent"),
            "target_agent": wizard_params.get("target_agent"),
            "source_path": wizard_params.get("source_path"),
            "target_path": wizard_params.get("target_path"),
            # Contact
            "contact_name": wizard_params.get("contact_name"),
            "contact_company": wizard_params.get("contact_company"),
        }

        # Remove None values
        flat_params = {k: v for k, v in flat_params.items() if v is not None}

        # Create new session
        session_id = str(uuid.uuid4())
        detected_type = parsed.get("detected_job_type") or "STANDARD"

        initial_data = {
            "session_id": session_id,
            "current_step": WizardStep.BASIC_INFO,
            "completed_steps": [WizardStep.BASIC_INFO],
            "params": flat_params,
            "ai_suggestions": {},
            "detected_job_type": detected_type,
            "status": "complete",  # Mark imports as complete
            # Store full parsed data for reference
            "_import_data": {
                "stream": stream_data,
                "jobs": parsed.get("jobs", []),
                "contacts": parsed.get("contacts", []),
            },
            "_raw_xml": xml_str,
        }

        # Mark more steps as complete based on what we have
        if flat_params.get("agent_detail") or flat_params.get("source_agent"):
            initial_data["completed_steps"].append(WizardStep.JOB_TYPE)
            initial_data["completed_steps"].append(WizardStep.JOB_DETAILS)
        if flat_params.get("contact_name"):
            initial_data["completed_steps"].append(WizardStep.CONTACT)
        initial_data["completed_steps"].append(WizardStep.PREVIEW)

        db.save_session(session_id, initial_data)

        completion = calculate_wizard_completion(initial_data)

        return WizardSessionResponse(
            session_id=session_id,
            current_step=WizardStep.PREVIEW,
            completed_steps=initial_data["completed_steps"],
            params=flat_params,
            ai_suggestions={},
            detected_job_type=detected_type,
            completion_percent=completion,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
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
        completion_percent=completion,
    )


def calculate_wizard_completion(session: Dict) -> float:
    """Calculate wizard completion percentage"""
    completed = len(session.get("completed_steps", []))
    total = len(STEP_ORDER)
    return (completed / total) * 100 if total > 0 else 0.0


# ============ FILE-BASED PARAMETER EXTRACTION ============


class FileExtractionResponse(BaseModel):
    """Response from file-based parameter extraction"""
    streams: List[Dict[str, Any]]
    document_summary: str
    extraction_method: str  # "tabular", "nlp", or "hybrid"
    total_streams: int
    successful_extractions: int
    file_type: str
    warnings: List[str] = []


class StreamSelectionRequest(BaseModel):
    """Request to select streams from extraction result"""
    stream_indices: List[int]  # Which streams to create sessions for


@router.post(
    "/sessions/{session_id}/extract-from-file", 
    response_model=FileExtractionResponse
)
async def extract_parameters_from_file(
    session_id: str,
    file: UploadFile = File(...),
):
    """
    Extract stream parameters from uploaded file.
    
    Supports:
    - Excel (.xlsx, .xls): One row = one stream
    - CSV (.csv): Comma/semicolon separated
    - PDF (.pdf): NLP extraction from text
    - DOCX (.docx): NLP extraction from text
    
    Returns extracted streams with per-parameter confidence scores.
    """
    # Verify session exists
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        from services.ai.batch_parameter_extractor import get_batch_extractor
        
        content = await file.read()
        extractor = get_batch_extractor()
        
        result = extractor.extract_from_document(content, file.filename)
        
        # Store extraction result in session for later use
        session["_last_extraction"] = {
            "filename": file.filename,
            "streams_count": result.total_streams,
            "extraction_method": result.extraction_method,
        }
        db.save_session(session_id, session)
        
        return FileExtractionResponse(
            streams=[s.to_dict() for s in result.streams],
            document_summary=result.document_summary,
            extraction_method=result.extraction_method,
            total_streams=result.total_streams,
            successful_extractions=result.successful_extractions,
            file_type=result.file_type,
            warnings=result.warnings,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Extraction failed: {str(e)}"
        )


@router.post("/extract-from-file", response_model=FileExtractionResponse)
async def extract_parameters_from_file_standalone(
    file: UploadFile = File(...),
):
    """
    Extract stream parameters from uploaded file (standalone, no session).
    
    Supports:
    - Excel (.xlsx, .xls): One row = one stream
    - CSV (.csv): Comma/semicolon separated  
    - PDF (.pdf): NLP extraction from text
    - DOCX (.docx): NLP extraction from text
    
    Returns extracted streams with per-parameter confidence scores.
    """
    try:
        from services.ai.batch_parameter_extractor import get_batch_extractor
        
        content = await file.read()
        extractor = get_batch_extractor()
        
        result = extractor.extract_from_document(content, file.filename)
        
        return FileExtractionResponse(
            streams=[s.to_dict() for s in result.streams],
            document_summary=result.document_summary,
            extraction_method=result.extraction_method,
            total_streams=result.total_streams,
            successful_extractions=result.successful_extractions,
            file_type=result.file_type,
            warnings=result.warnings,
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Extraction failed: {str(e)}"
        )


@router.post("/sessions/create-from-extraction")
async def create_sessions_from_extraction(
    streams_data: List[Dict[str, Any]],
):
    """
    Create wizard sessions from extracted stream data.
    
    Takes the output from extract-from-file and creates
    individual wizard sessions for selected streams.
    """
    created_sessions = []
    
    for stream_data in streams_data:
        session_id = str(uuid.uuid4())
        
        # Convert parameter data to flat params
        params = {}
        if "parameters" in stream_data:
            for key, param_data in stream_data["parameters"].items():
                if isinstance(param_data, dict) and "value" in param_data:
                    params[key] = param_data["value"]
                else:
                    params[key] = param_data
        
        # Add stream_name if present
        if stream_data.get("stream_name"):
            params["stream_name"] = stream_data["stream_name"]
        
        # Determine job type
        job_type = stream_data.get("job_type", "STANDARD")
        
        initial_data = {
            "session_id": session_id,
            "current_step": WizardStep.BASIC_INFO,
            "completed_steps": [WizardStep.BASIC_INFO],
            "params": params,
            "ai_suggestions": {},
            "detected_job_type": job_type,
            "status": "draft",
            "_extraction_source": {
                "row_number": stream_data.get("row_number"),
                "confidence": stream_data.get("overall_confidence", 0.8),
            },
        }
        
        db.save_session(session_id, initial_data)
        
        created_sessions.append({
            "session_id": session_id,
            "stream_name": params.get("stream_name", "Unnamed"),
            "job_type": job_type,
        })
    
    return {
        "created": len(created_sessions),
        "sessions": created_sessions,
    }


@router.get("/health")
async def health():
    """Health check for wizard service"""
    return {
        "status": "ok",
        "openai_configured": bool(config.OPENAI_API_KEY),
        "db_connected": db.client is not None,
    }
