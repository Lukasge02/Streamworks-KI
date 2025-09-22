"""
Chat XML Router - Unified Version
Vollständig integrierte Version mit dem neuen vereinheitlichten System
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from services.ai.enhanced_unified_parameter_extractor import EnhancedUnifiedParameterExtractor, get_enhanced_unified_parameter_extractor
from services.ai.unified_dialog_manager import UnifiedDialogManager, create_unified_dialog_manager
from services.ai.parameter_state_manager import HierarchicalParameterStateManager
from config import settings

logger = logging.getLogger(__name__)

# ================================
# API ROUTER
# ================================

router = APIRouter(
    prefix="/api/chat-xml/unified",
    tags=["chat-xml-unified"]
)

# ================================
# REQUEST/RESPONSE MODELS
# ================================

class ChatMessageRequest(BaseModel):
    """Request für Chat-Nachrichten"""
    message: str = Field(..., description="User-Nachricht")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Zusätzliche Metadaten")

class ChatMessageResponse(BaseModel):
    """Response für Chat-Nachrichten"""
    session_id: str = Field(..., description="Session-ID")
    message: str = Field(..., description="System-Antwort")
    state: str = Field(..., description="Dialog-State")
    priority: str = Field(..., description="Priorität")
    detected_job_type: Optional[str] = Field(None, description="Erkannter Job-Type")
    detection_confidence: float = Field(0.0, description="Job-Type Detection Confidence")
    detection_method: str = Field("unknown", description="Verwendete Detection-Methode")
    completion_percentage: float = Field(..., description="Vervollständigung")
    suggested_questions: List[str] = Field(default_factory=list, description="Vorgeschlagene Fragen")
    extracted_parameters: Dict[str, Any] = Field(default_factory=dict, description="Extrahierte Parameter")
    alternative_job_types: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative Job-Type-Kandidaten")
    ready_for_xml: bool = Field(False, description="Bereit für XML-Generierung")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Zusätzliche Metadaten")

class SessionCreateRequest(BaseModel):
    """Request für Session-Erstellung"""
    user_id: Optional[str] = Field(None, description="Optionale User-ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Initiale Metadaten")

class SessionResponse(BaseModel):
    """Response für Session-Informationen"""
    session_id: str = Field(..., description="Session-ID")
    created_at: str = Field(..., description="Erstellungszeitpunkt")
    session_type: str = Field(..., description="Session-Typ")
    detected_job_type: Optional[str] = Field(None, description="Erkannter Job-Type")
    stream_parameters: Dict[str, Any] = Field(default_factory=dict, description="Stream-Parameter")
    job_parameters: Dict[str, Any] = Field(default_factory=dict, description="Job-Parameter")
    completion_percentage: float = Field(..., description="Vervollständigung")
    status: str = Field(..., description="Session-Status")

class ParameterExportResponse(BaseModel):
    """Response für Parameter-Export"""
    session_id: str = Field(..., description="Session-ID")
    job_type: str = Field(..., description="Job-Type")
    stream_parameters: Dict[str, Any] = Field(default_factory=dict, description="Stream-Parameter")
    job_parameters: Dict[str, Any] = Field(default_factory=dict, description="Job-Parameter")
    xml_ready: bool = Field(..., description="XML-Generation bereit")
    missing_required: List[str] = Field(default_factory=list, description="Fehlende erforderliche Parameter")

class JobTypesResponse(BaseModel):
    """Response für verfügbare Job-Types"""
    job_types: List[Dict[str, Any]] = Field(..., description="Liste der Job-Types")

# ================================
# DEPENDENCY INJECTION
# ================================

# Globale Instanzen für Services
_unified_extractor: Optional[EnhancedUnifiedParameterExtractor] = None
_state_manager: Optional[HierarchicalParameterStateManager] = None
_dialog_manager: Optional[UnifiedDialogManager] = None

def get_unified_services():
    """Dependency Injection für vereinheitlichte Services"""
    global _unified_extractor, _state_manager, _dialog_manager

    # Initialisiere Services bei Bedarf
    if _unified_extractor is None:
        _unified_extractor = get_enhanced_unified_parameter_extractor(settings.OPENAI_API_KEY)
        logger.info("EnhancedUnifiedParameterExtractor initialisiert")

    if _state_manager is None:
        _state_manager = HierarchicalParameterStateManager()
        logger.info("HierarchicalParameterStateManager initialisiert")

    if _dialog_manager is None:
        _dialog_manager = create_unified_dialog_manager(
            _unified_extractor,
            _state_manager,
            settings.OPENAI_API_KEY
        )
        logger.info("UnifiedDialogManager initialisiert")

    return _unified_extractor, _state_manager, _dialog_manager

# ================================
# API ENDPOINTS
# ================================

@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: SessionCreateRequest,
    services = Depends(get_unified_services)
) -> SessionResponse:
    """
    Erstellt eine neue Chat-Session mit vereinheitlichtem System
    """
    try:
        extractor, state_manager, dialog_manager = services

        # Generiere Session-ID
        session_id = str(uuid.uuid4())

        # Erstelle hierarchische Session
        session = state_manager.create_hierarchical_session(
            user_id=request.user_id
        )

        # Setze die gewünschte Session-ID
        session.session_id = session_id

        logger.info(f"Unified Session erstellt: {session_id}")

        return SessionResponse(
            session_id=session_id,
            created_at=datetime.now().isoformat(),
            session_type="UNIFIED_STREAM",
            detected_job_type=None,
            stream_parameters={},
            job_parameters={},
            completion_percentage=0.0,
            status="initial"
        )

    except Exception as e:
        logger.error(f"Fehler bei Session-Erstellung: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def process_message(
    session_id: str,
    request: ChatMessageRequest,
    services = Depends(get_unified_services)
) -> ChatMessageResponse:
    """
    Verarbeitet eine Chat-Nachricht mit dem vereinheitlichten System
    """
    try:
        extractor, state_manager, dialog_manager = services

        logger.info(f"Verarbeite Message für Session {session_id}: '{request.message[:100]}...'")

        # Verarbeite Message mit UnifiedDialogManager
        response = await dialog_manager.process_message(
            user_message=request.message,
            session_id=session_id
        )

        # Hole aktuelle Session für Parameter
        session = state_manager.get_hierarchical_session(session_id)

        # Sammle alle Parameter
        all_parameters = {}
        if session:
            all_parameters.update(session.stream_parameters)
            if session.jobs:
                all_parameters.update(session.jobs[0].parameters)

        # Prüfe XML-Bereitschaft
        ready_for_xml = response.state == "confirmation" or response.completion_percentage >= 1.0

        # Enhanced Response Felder
        detection_confidence = getattr(response, 'detection_confidence', 0.0)
        detection_method = getattr(response, 'detection_method', 'unknown')
        alternative_job_types = []

        # Konvertiere alternative_job_types falls vorhanden
        if hasattr(response, 'alternative_job_types') and response.alternative_job_types:
            alternative_job_types = [
                {"job_type": jt, "confidence": conf}
                for jt, conf in response.alternative_job_types
            ]

        return ChatMessageResponse(
            session_id=session_id,
            message=response.message,
            state=response.state,
            priority=response.priority,
            detected_job_type=response.detected_job_type,
            detection_confidence=detection_confidence,
            detection_method=detection_method,
            completion_percentage=response.completion_percentage,
            suggested_questions=response.suggested_questions,
            extracted_parameters=all_parameters,
            alternative_job_types=alternative_job_types,
            ready_for_xml=ready_for_xml,
            metadata=response.metadata
        )

    except Exception as e:
        logger.error(f"Fehler bei Message-Verarbeitung: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/status", response_model=SessionResponse)
async def get_session_status(
    session_id: str,
    services = Depends(get_unified_services)
) -> SessionResponse:
    """
    Gibt den aktuellen Status einer Session zurück
    """
    try:
        extractor, state_manager, dialog_manager = services

        # Hole Session
        session = state_manager.get_hierarchical_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session nicht gefunden")

        # Bestimme Job-Type
        job_type = None
        job_params = {}
        if session.jobs:
            job_type = session.jobs[0].job_type
            job_params = session.jobs[0].parameters

        # Berechne Completion
        total_params = len(session.stream_parameters) + len(job_params)
        required_count = 2  # StreamName + ShortDescription minimum
        completion = min(total_params / max(required_count, 1), 1.0)

        # Bestimme Status
        if completion >= 1.0:
            status = "completed"
        elif job_type:
            status = "collecting_parameters"
        else:
            status = "detecting_job_type"

        return SessionResponse(
            session_id=session_id,
            created_at=session.created_at.isoformat(),
            session_type=session.session_type,
            detected_job_type=job_type,
            stream_parameters=session.stream_parameters,
            job_parameters=job_params,
            completion_percentage=completion,
            status=status
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Session-Status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/parameters", response_model=ParameterExportResponse)
async def export_parameters(
    session_id: str,
    services = Depends(get_unified_services)
) -> ParameterExportResponse:
    """
    Exportiert alle gesammelten Parameter einer Session
    """
    try:
        extractor, state_manager, dialog_manager = services

        # Hole Session
        session = state_manager.get_hierarchical_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session nicht gefunden")

        # Sammle Parameter
        job_type = "STANDARD"  # Default
        job_params = {}

        if session.jobs:
            job_type = session.jobs[0].job_type
            job_params = session.jobs[0].parameters

        # Prüfe fehlende erforderliche Parameter
        missing = []
        if "StreamName" not in session.stream_parameters:
            missing.append("StreamName")
        if "ShortDescription" not in session.stream_parameters:
            missing.append("ShortDescription")

        xml_ready = len(missing) == 0 and job_type is not None

        return ParameterExportResponse(
            session_id=session_id,
            job_type=job_type,
            stream_parameters=session.stream_parameters,
            job_parameters=job_params,
            xml_ready=xml_ready,
            missing_required=missing
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Parameter-Export: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job-types", response_model=JobTypesResponse)
async def get_available_job_types(
    services = Depends(get_unified_services)
) -> JobTypesResponse:
    """
    Gibt alle verfügbaren Job-Types zurück
    """
    try:
        extractor, state_manager, dialog_manager = services

        job_types = dialog_manager.get_available_job_types()

        return JobTypesResponse(job_types=job_types)

    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Job-Types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    services = Depends(get_unified_services)
) -> Dict[str, str]:
    """
    Löscht eine Session
    """
    try:
        extractor, state_manager, dialog_manager = services

        # Hole Session zum Prüfen
        session = state_manager.get_hierarchical_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session nicht gefunden")

        # Lösche Session aus Storage
        state_manager.sessions.pop(session_id, None)

        # Optional: Lösche auch Datei
        session_file = state_manager.storage_path / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()

        logger.info(f"Session gelöscht: {session_id}")

        return {"message": f"Session {session_id} erfolgreich gelöscht"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Löschen der Session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# HEALTH CHECK
# ================================

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health Check für den Unified Chat XML Service"""
    try:
        # Prüfe ob Services initialisiert werden können
        extractor, state_manager, dialog_manager = get_unified_services()

        return {
            "status": "healthy",
            "service": "chat-xml-unified",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "unified_extractor": "ready",
                "state_manager": "ready",
                "dialog_manager": "ready"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "chat-xml-unified",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

logger.info("Chat XML Unified Router initialisiert")