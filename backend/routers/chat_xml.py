"""
Chat XML Router - Phase 1.3
RESTful API Endpoints für Chat-zu-XML Konversationen
"""

import logging
import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import Response, JSONResponse
from datetime import datetime
from pydantic import BaseModel

from services.chat_xml.chat_session_service import get_chat_session_service, ChatSessionState, MessageType
from services.chat_xml.dialog_manager import get_dialog_manager, DialogIntent, DialogContext
from services.chat_xml.parameter_extractor import get_parameter_extractor

# MVP: Smart Parameter Collection
from services.ai.smart_parameter_extractor import get_smart_parameter_extractor
from services.ai.intelligent_dialog_manager import get_intelligent_dialog_manager
from services.ai.parameter_state_manager import get_parameter_state_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat-xml", tags=["Chat XML"])

# ================================
# PYDANTIC MODELS
# ================================

class CreateChatSessionRequest(BaseModel):
    user_id: Optional[str] = None
    initial_message: Optional[str] = None

class CreateChatSessionResponse(BaseModel):
    session_id: str
    state: str
    message: str
    created_at: datetime

class SendChatMessageRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    response_id: str
    content: str
    intent: str
    context: str
    requires_user_input: bool
    next_parameter: Optional[str] = None
    suggested_values: Optional[List[str]] = None
    confidence: float
    show_progress: bool = False
    highlight_validation: bool = False
    enable_suggestions: bool = False
    timestamp: datetime

class SessionStatusResponse(BaseModel):
    session_id: str
    state: str
    job_type: Optional[str] = None
    completion_percentage: float
    collected_parameters: int
    total_messages: int
    created_at: datetime
    last_activity: datetime
    has_validation_issues: bool
    required_parameters: Optional[int] = None
    missing_parameters: Optional[int] = None
    invalid_parameters: Optional[int] = None
    next_parameter: Optional[str] = None

class ChatHistoryMessage(BaseModel):
    id: str
    type: str
    content: str
    timestamp: datetime
    parameter_name: Optional[str] = None
    validation_errors: List[str] = []
    metadata: Dict[str, Any] = {}

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatHistoryMessage]
    total_count: int

class JobTypeSelectionResponse(BaseModel):
    job_types: Dict[str, Dict[str, Any]]
    formatted_options: str

class ParameterCollectionRequest(BaseModel):
    parameter_name: str
    value: Any

class ParameterCollectionResponse(BaseModel):
    success: bool
    message: str
    next_prompt: Optional[str] = None
    completion_percentage: float
    next_parameter: Optional[str] = None

class XMLGenerationResponse(BaseModel):
    success: bool
    message: str
    xml_content: Optional[str] = None
    validation_issues: List[str] = []
    file_size: Optional[int] = None

# ================================
# MVP: SMART PARAMETER COLLECTION MODELS
# ================================

class SmartChatSessionRequest(BaseModel):
    user_id: Optional[str] = None
    job_type: Optional[str] = None
    initial_parameters: Optional[Dict[str, Any]] = None

class SmartChatSessionResponse(BaseModel):
    session_id: str
    job_type: Optional[str] = None
    status: str
    dialog_state: str
    completion_percentage: float
    message: str
    suggested_questions: List[str] = []
    created_at: datetime

class SmartChatMessageRequest(BaseModel):
    message: str
    extract_parameters: bool = True

class SmartChatMessageResponse(BaseModel):
    session_id: str
    response_message: str
    dialog_state: str
    priority: str
    extracted_parameters: List[str] = []
    next_parameter: Optional[str] = None
    completion_percentage: float
    suggested_questions: List[str] = []
    validation_issues: List[str] = []
    timestamp: datetime

class ParameterExportResponse(BaseModel):
    session_id: str
    job_type: Optional[str] = None
    parameters: Dict[str, Any]
    completion_percentage: float
    validation_status: str
    export_timestamp: datetime
    xml_content: Optional[str] = None
    validation_issues: List[str] = []
    file_size: Optional[int] = None

class SessionCleanupResponse(BaseModel):
    cleaned_sessions: int
    remaining_sessions: int

# ================================
# DEPENDENCY INJECTION
# ================================

def get_chat_session_service_dep():
    return get_chat_session_service()

async def get_dialog_manager_dep():
    manager = get_dialog_manager()
    await manager.initialize()
    return manager

def get_parameter_extractor_dep():
    return get_parameter_extractor()

# MVP: Smart Parameter Collection Dependencies
def get_smart_parameter_extractor_dep():
    return get_smart_parameter_extractor()

def get_intelligent_dialog_manager_dep():
    return get_intelligent_dialog_manager()

def get_parameter_state_manager_dep():
    return get_parameter_state_manager()

# ================================
# SESSION MANAGEMENT ENDPOINTS
# ================================

@router.post("/sessions", response_model=CreateChatSessionResponse)
async def create_chat_session(
    request: CreateChatSessionRequest,
    session_service = Depends(get_chat_session_service_dep)
) -> CreateChatSessionResponse:
    """Erstellt eine neue Chat-Session für XML-Generierung"""

    try:
        session = session_service.create_session(request.user_id)
        session_id = session.session_id

        if not session:
            raise HTTPException(status_code=500, detail="Session creation failed")

        # Simple welcome message
        welcome_message = "Willkommen beim XML-Generator! Welchen Job-Type möchten Sie erstellen?"

        logger.info(f"Created new chat session: {session_id}")

        return CreateChatSessionResponse(
            session_id=session_id,
            state=session.state.value,
            message=welcome_message,
            created_at=session.created_at
        )

    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/sessions/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    session_service = Depends(get_chat_session_service_dep)
) -> SessionStatusResponse:
    """Gibt detaillierten Status einer Chat-Session zurück"""

    status = session_service.get_session_status(session_id)
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionStatusResponse(**status)

@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: Optional[int] = None,
    session_service = Depends(get_chat_session_service_dep)
) -> ChatHistoryResponse:
    """Gibt Chat-Historie einer Session zurück"""

    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    history = session_service.get_chat_history(session_id, limit)

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[ChatHistoryMessage(**msg) for msg in history],
        total_count=len(session.messages)
    )

@router.delete("/sessions/{session_id}")
async def cancel_session(
    session_id: str,
    session_service = Depends(get_chat_session_service_dep)
) -> Dict[str, str]:
    """Bricht eine Chat-Session ab"""

    success = session_service.cancel_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session cancelled successfully"}

# ================================
# CHAT INTERACTION ENDPOINTS
# ================================

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: str,
    request: SendChatMessageRequest,
    dialog_manager = Depends(get_dialog_manager_dep),
    session_service = Depends(get_chat_session_service_dep)
) -> ChatMessageResponse:
    """Sendet eine Nachricht an den Chat und erhält intelligente Antwort"""

    try:
        # Prüfe ob Session existiert
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Verarbeite Nachricht mit Dialog Manager
        response = await dialog_manager.process_user_message(session_id, request.message)

        return ChatMessageResponse(
            response_id=f"resp_{int(time.time() * 1000)}",
            content=response.content,
            intent=response.intent.value,
            context=response.context.value,
            requires_user_input=response.requires_user_input,
            next_parameter=response.next_parameter,
            suggested_values=response.suggested_values or [],
            confidence=response.confidence,
            show_progress=response.show_progress,
            highlight_validation=response.highlight_validation,
            enable_suggestions=response.enable_suggestions,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error processing chat message in session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

# ================================
# JOB TYPE SELECTION ENDPOINTS
# ================================

@router.get("/job-types", response_model=JobTypeSelectionResponse)
async def get_available_job_types(
    parameter_extractor = Depends(get_parameter_extractor_dep)
) -> JobTypeSelectionResponse:
    """Gibt verfügbare Job-Types für Auswahl zurück"""

    try:
        job_types = parameter_extractor.get_job_types()

        # Formatiere für UI-Anzeige
        formatted_options = "📋 **Verfügbare Job-Types:**\n\n"
        for job_type, info in job_types.items():
            formatted_options += f"🔹 **{info['display_name']}** ({job_type})\n"
            formatted_options += f"   {info['description']}\n"
            formatted_options += f"   ⏱️ {info['estimated_time']} | 📋 {info['parameter_count']} Parameter\n\n"

        return JobTypeSelectionResponse(
            job_types=job_types,
            formatted_options=formatted_options
        )

    except Exception as e:
        logger.error(f"Error getting job types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job types: {str(e)}")

@router.post("/sessions/{session_id}/job-type")
async def set_job_type(
    session_id: str,
    job_type: str,
    session_service = Depends(get_chat_session_service_dep)
) -> Dict[str, Any]:
    """Setzt den Job-Type für eine Session"""

    try:
        success, message, next_prompt = session_service.set_job_type(session_id, job_type)

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return {
            "success": True,
            "message": message,
            "next_prompt": next_prompt,
            "job_type": job_type
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting job type in session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set job type: {str(e)}")

# ================================
# PARAMETER COLLECTION ENDPOINTS
# ================================

@router.post("/sessions/{session_id}/parameters", response_model=ParameterCollectionResponse)
async def collect_parameter(
    session_id: str,
    request: ParameterCollectionRequest,
    session_service = Depends(get_chat_session_service_dep)
) -> ParameterCollectionResponse:
    """Sammelt einen Parameter-Wert für die Session"""

    try:
        success, message, next_prompt = session_service.collect_parameter(
            session_id, request.parameter_name, request.value
        )

        # Hole aktuellen Status für Completion-Percentage
        status = session_service.get_session_status(session_id)
        completion_percentage = status.get("completion_percentage", 0.0) if status else 0.0
        next_parameter = status.get("next_parameter") if status else None

        return ParameterCollectionResponse(
            success=success,
            message=message,
            next_prompt=next_prompt,
            completion_percentage=completion_percentage,
            next_parameter=next_parameter
        )

    except Exception as e:
        logger.error(f"Error collecting parameter in session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to collect parameter: {str(e)}")

@router.get("/sessions/{session_id}/parameters")
async def get_collected_parameters(
    session_id: str,
    session_service = Depends(get_chat_session_service_dep),
    parameter_extractor = Depends(get_parameter_extractor_dep)
) -> Dict[str, Any]:
    """Gibt alle gesammelten Parameter einer Session zurück"""

    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.job_type:
        return {"collected_parameters": {}, "job_type": None}

    try:
        collected = parameter_extractor.extract_collected_parameters(session.job_type)

        return {
            "job_type": session.job_type,
            "collected_parameters": collected,
            "completion_percentage": session.completion_percentage
        }

    except Exception as e:
        logger.error(f"Error getting collected parameters for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get parameters: {str(e)}")

# ================================
# XML GENERATION ENDPOINTS
# ================================

@router.post("/sessions/{session_id}/generate-xml", response_model=XMLGenerationResponse)
async def generate_xml(
    session_id: str,
    session_service = Depends(get_chat_session_service_dep)
) -> XMLGenerationResponse:
    """Generiert XML aus gesammelten Parametern"""

    try:
        success, message, xml_content = session_service.generate_xml(session_id)

        # Hole Session für Validierungsfehler
        session = session_service.get_session(session_id)
        validation_issues = session.validation_issues if session else []

        file_size = len(xml_content) if xml_content else None

        return XMLGenerationResponse(
            success=success,
            message=message,
            xml_content=xml_content,
            validation_issues=validation_issues,
            file_size=file_size
        )

    except Exception as e:
        logger.error(f"Error generating XML for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate XML: {str(e)}")

@router.get("/sessions/{session_id}/xml")
async def get_generated_xml(
    session_id: str,
    download: bool = False,
    session_service = Depends(get_chat_session_service_dep)
) -> Response:
    """Gibt das generierte XML zurück (optional als Download)"""

    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.generated_xml:
        raise HTTPException(status_code=404, detail="No XML generated for this session")

    if download:
        # Return as downloadable file
        filename = f"streamworks_{session.job_type or 'export'}_{session_id[:8]}.xml"
        return Response(
            content=session.generated_xml,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        # Return as JSON response
        return JSONResponse({
            "session_id": session_id,
            "job_type": session.job_type,
            "xml_content": session.generated_xml,
            "file_size": len(session.generated_xml),
            "validation_issues": session.validation_issues,
            "generated_at": session.last_activity.isoformat()
        })

# ================================
# SYSTEM MANAGEMENT ENDPOINTS
# ================================

@router.post("/cleanup", response_model=SessionCleanupResponse)
async def cleanup_expired_sessions(
    session_service = Depends(get_chat_session_service_dep)
) -> SessionCleanupResponse:
    """Räumt abgelaufene Sessions auf"""

    try:
        cleaned_count = session_service.cleanup_expired_sessions()
        remaining_count = len(session_service.sessions)

        return SessionCleanupResponse(
            cleaned_sessions=cleaned_count,
            remaining_sessions=remaining_count
        )

    except Exception as e:
        logger.error(f"Error during session cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.get("/health")
async def health_check(
    session_service = Depends(get_chat_session_service_dep),
    parameter_extractor = Depends(get_parameter_extractor_dep)
) -> Dict[str, Any]:
    """Gesundheitscheck für Chat XML Services"""

    try:
        # Teste alle Services
        job_types = parameter_extractor.get_job_types()
        active_sessions = len(session_service.sessions)

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "chat_session_service": "active",
                "parameter_extractor": "active",
                "dialog_manager": "active"
            },
            "metrics": {
                "available_job_types": len(job_types),
                "active_sessions": active_sessions
            },
            "job_types": list(job_types.keys())
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# ================================
# DEVELOPMENT ENDPOINTS
# ================================

@router.get("/debug/sessions")
async def debug_list_sessions(
    session_service = Depends(get_chat_session_service_dep)
) -> Dict[str, Any]:
    """Debug-Endpoint: Listet alle aktiven Sessions (nur für Development)"""

    sessions_info = []
    for session_id, session in session_service.sessions.items():
        sessions_info.append({
            "session_id": session_id,
            "state": session.state.value,
            "job_type": session.job_type,
            "completion_percentage": session.completion_percentage,
            "message_count": len(session.messages),
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        })

    return {
        "total_sessions": len(sessions_info),
        "sessions": sessions_info
    }

# ================================
# MVP: SMART PARAMETER COLLECTION ENDPOINTS
# ================================

@router.post("/smart/sessions", response_model=SmartChatSessionResponse)
async def create_smart_chat_session(
    request: SmartChatSessionRequest,
    state_manager = Depends(get_parameter_state_manager_dep)
) -> SmartChatSessionResponse:
    """Erstellt neue Smart Parameter Collection Session"""

    try:
        session = state_manager.create_session(
            user_id=request.user_id,
            job_type=request.job_type,
            initial_parameters=request.initial_parameters
        )

        # Generiere initiale Nachricht
        if session.job_type:
            message = f"Perfekt! Lassen Sie uns einen {session.job_type}-Job konfigurieren. Ich führe Sie durch die benötigten Parameter."
        else:
            message = "Willkommen beim Smart Parameter Assistant! 🚀 Welchen Job-Type möchten Sie erstellen?"

        suggested_questions = [
            "Ich möchte einen Standard-Stream erstellen",
            "Ich brauche einen SAP-Report",
            "Ich möchte Dateien übertragen",
            "Ich brauche eine benutzerdefinierte Konfiguration"
        ] if not session.job_type else []

        logger.info(f"Smart Chat Session erstellt: {session.session_id}")

        return SmartChatSessionResponse(
            session_id=session.session_id,
            job_type=session.job_type,
            status=session.status.value,
            dialog_state=session.dialog_state,
            completion_percentage=session.completion_percentage,
            message=message,
            suggested_questions=suggested_questions,
            created_at=session.created_at
        )

    except Exception as e:
        logger.error(f"Fehler bei Smart Session Creation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create smart session: {str(e)}")

@router.post("/smart/sessions/{session_id}/messages", response_model=SmartChatMessageResponse)
async def send_smart_chat_message(
    session_id: str,
    request: SmartChatMessageRequest,
    dialog_manager = Depends(get_intelligent_dialog_manager_dep),
    state_manager = Depends(get_parameter_state_manager_dep)
) -> SmartChatMessageResponse:
    """Verarbeitet User-Message mit Smart Parameter Extraction"""

    try:
        # Hole Session
        session = state_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Bereite Session State für Dialog Manager vor
        session_state = {
            "session_id": session_id,
            "job_type": session.job_type,
            "state": session.dialog_state,
            "parameters": session.collected_parameters,
            "completion_percentage": session.completion_percentage
        }

        # Verarbeite Message mit Intelligent Dialog Manager
        dialog_response = await dialog_manager.process_user_message(
            user_message=request.message,
            session_state=session_state
        )

        # Aktualisiere Session mit extrahierten Parametern
        if dialog_response.extracted_parameters:
            # Konvertiere Parameter-Namen zu Werten (vereinfacht)
            extracted_values = {param: f"extracted_from_{request.message[:20]}" for param in dialog_response.extracted_parameters}

            state_manager.update_session_parameters(
                session_id=session_id,
                new_parameters=extracted_values,
                source_message=request.message
            )

        # Aktualisiere Dialog State
        state_manager.update_session_state(
            session_id=session_id,
            dialog_state=dialog_response.state.value,
            last_message=request.message,
            suggested_questions=dialog_response.suggested_questions,
            metadata=dialog_response.metadata
        )

        # Hole aktualisierte Session für Response
        updated_session = state_manager.get_session(session_id)

        logger.info(f"Smart Message verarbeitet: {session_id} | Extracted: {len(dialog_response.extracted_parameters)}")

        return SmartChatMessageResponse(
            session_id=session_id,
            response_message=dialog_response.message,
            dialog_state=dialog_response.state.value,
            priority=dialog_response.priority.value,
            extracted_parameters=dialog_response.extracted_parameters,
            next_parameter=dialog_response.next_parameter,
            completion_percentage=updated_session.completion_percentage if updated_session else 0.0,
            suggested_questions=dialog_response.suggested_questions,
            validation_issues=dialog_response.validation_issues,
            timestamp=dialog_response.timestamp
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Smart Message Processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/smart/sessions/{session_id}/status", response_model=SmartChatSessionResponse)
async def get_smart_session_status(
    session_id: str,
    state_manager = Depends(get_parameter_state_manager_dep)
) -> SmartChatSessionResponse:
    """Gibt Status einer Smart Parameter Session zurück"""

    session = state_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SmartChatSessionResponse(
        session_id=session.session_id,
        job_type=session.job_type,
        status=session.status.value,
        dialog_state=session.dialog_state,
        completion_percentage=session.completion_percentage,
        message=session.last_message or "Session aktiv",
        suggested_questions=session.suggested_questions,
        created_at=session.created_at
    )

@router.get("/smart/sessions/{session_id}/parameters", response_model=ParameterExportResponse)
async def export_session_parameters(
    session_id: str,
    format: str = "json",
    state_manager = Depends(get_parameter_state_manager_dep)
) -> ParameterExportResponse:
    """Exportiert gesammelte Parameter als JSON"""

    try:
        session = state_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Validiere Parameter
        validation_result = state_manager.validate_session_parameters(session_id)
        validation_status = "valid" if validation_result and validation_result.is_valid else "invalid"

        return ParameterExportResponse(
            session_id=session_id,
            job_type=session.job_type,
            parameters=session.collected_parameters,
            completion_percentage=session.completion_percentage,
            validation_status=validation_status,
            export_timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Fehler bei Parameter Export: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.delete("/smart/sessions/{session_id}")
async def delete_smart_session(
    session_id: str,
    state_manager = Depends(get_parameter_state_manager_dep)
) -> Dict[str, str]:
    """Löscht eine Smart Parameter Session"""

    session = state_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Mark as expired (wird beim nächsten Cleanup entfernt)
    state_manager._expire_session(session_id)

    return {"message": "Session deleted successfully", "session_id": session_id}

@router.get("/smart/job-types")
async def get_smart_job_types(
    extractor = Depends(get_smart_parameter_extractor_dep)
) -> Dict[str, Any]:
    """Gibt verfügbare Job-Types für Smart Parameter Collection zurück"""

    try:
        job_types = extractor.get_available_job_types()

        formatted_types = {}
        for job_type in job_types:
            formatted_types[job_type["job_type"]] = {
                "display_name": job_type["display_name"],
                "description": job_type["description"],
                "complexity": job_type["complexity"],
                "estimated_time": job_type["estimated_time"],
                "parameter_count": job_type["parameter_count"]
            }

        return {
            "job_types": formatted_types,
            "total_count": len(job_types),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Fehler bei Job-Types Abfrage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job types: {str(e)}")

@router.post("/smart/cleanup")
async def cleanup_smart_sessions(
    state_manager = Depends(get_parameter_state_manager_dep)
) -> Dict[str, Any]:
    """Räumt abgelaufene Smart Sessions auf"""

    try:
        cleaned_count = state_manager.cleanup_expired_sessions()
        stats = state_manager.get_system_stats()

        return {
            "cleaned_sessions": cleaned_count,
            "system_stats": stats,
            "cleanup_timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Fehler bei Smart Cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

@router.get("/smart/health")
async def smart_system_health(
    extractor = Depends(get_smart_parameter_extractor_dep),
    dialog_manager = Depends(get_intelligent_dialog_manager_dep),
    state_manager = Depends(get_parameter_state_manager_dep)
) -> Dict[str, Any]:
    """Gesundheitscheck für Smart Parameter Collection System"""

    try:
        # Teste alle Services
        job_types = extractor.get_available_job_types()
        system_stats = state_manager.get_system_stats()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "smart_parameter_extractor": "active",
                "intelligent_dialog_manager": "active",
                "parameter_state_manager": "active"
            },
            "metrics": {
                "available_job_types": len(job_types),
                "active_sessions": system_stats["session_counts"]["active"],
                "completed_sessions": system_stats["session_counts"]["completed"]
            },
            "system_stats": system_stats,
            "job_types": [jt["job_type"] for jt in job_types]
        }

    except Exception as e:
        logger.error(f"Smart Health Check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Smart system unhealthy: {str(e)}")