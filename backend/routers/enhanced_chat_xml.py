"""
Enhanced Chat XML Router mit LangExtract Source Grounding
Revolutionärer Chat-zu-XML Service mit Source-Grounded Parameter Extraction
"""

import logging
import os
from typing import List, Optional, Dict, Any, Tuple
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from pydantic import BaseModel, Field

# LangExtract Integration
from models.source_grounded_models import (
    SourceGroundedParameter,
    SourceGroundedExtractionResult,
    JobTypeDetection,
    LangExtractConfig,
    ParameterCorrectionRequest,
    ParameterCorrectionResult
)

from services.ai.langextract_parameter_service import get_langextract_parameter_service

# Existing services for compatibility
from services.chat_xml.chat_session_service import get_chat_session_service
from services.ai.intelligent_dialog_manager import get_intelligent_dialog_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/enhanced-chat-xml", tags=["Enhanced Chat XML with Source Grounding"])

# ================================
# ENHANCED PYDANTIC MODELS
# ================================

class SourceGroundingInfo(BaseModel):
    """Source Grounding Information für Frontend"""
    parameter_name: str
    source_text: str
    character_offsets: Tuple[int, int]
    confidence: float
    highlight_color: str = "blue"

class EnhancedChatSessionRequest(BaseModel):
    """Enhanced Chat Session mit LangExtract Support"""
    user_id: Optional[str] = None
    job_type: Optional[str] = None  # Kann vorgegeben werden
    initial_message: Optional[str] = None
    enable_source_grounding: bool = True
    language: str = "de"

class EnhancedChatSessionResponse(BaseModel):
    """Enhanced Session Response mit Source Grounding"""
    session_id: str
    job_type: Optional[str] = None
    job_type_confidence: float = 0.0
    status: str
    message: str

    # Source Grounding Data
    source_grounding_enabled: bool = True
    highlighted_ranges: List[Tuple[int, int, str]] = Field(default_factory=list)

    # Dialog State
    completion_percentage: float = 0.0
    suggested_questions: List[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime
    extraction_method: str = "langextract"

class EnhancedChatMessageRequest(BaseModel):
    """Enhanced Message Request"""
    message: str
    session_id: str
    force_job_type: Optional[str] = None  # Override job type detection
    enable_corrections: bool = True

class EnhancedChatMessageResponse(BaseModel):
    """Enhanced Message Response mit Source Grounding"""
    session_id: str
    response_message: str

    # Job Type Detection
    detected_job_type: str
    job_type_confidence: float
    job_type_alternatives: List[Dict[str, Any]] = Field(default_factory=list)

    # Extracted Parameters mit Source Grounding
    stream_parameters: List[SourceGroundedParameter] = Field(default_factory=list)
    job_parameters: List[SourceGroundedParameter] = Field(default_factory=list)

    # Source Grounding für UI
    source_grounding_data: Dict[str, Any] = Field(default_factory=dict)
    highlighted_ranges: List[Tuple[int, int, str]] = Field(default_factory=list)

    # Dialog Status
    completion_percentage: float
    next_required_parameter: Optional[str] = None
    missing_parameters: List[str] = Field(default_factory=list)

    # Smart Suggestions
    suggested_questions: List[str] = Field(default_factory=list)
    contextual_suggestions: List[str] = Field(default_factory=list)

    # Quality Information
    overall_confidence: float
    extraction_quality: str = "medium"
    needs_review: bool = False

    # Metadata
    timestamp: datetime
    extraction_duration: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ParameterHighlightRequest(BaseModel):
    """Request für Parameter Highlighting"""
    session_id: str
    parameter_name: str

class ParameterHighlightResponse(BaseModel):
    """Response mit Highlight Information"""
    parameter_name: str
    source_text: str
    character_offsets: Tuple[int, int]
    confidence: float
    context_preview: str
    alternative_interpretations: List[str] = Field(default_factory=list)

class ParameterCorrectionApiRequest(BaseModel):
    """API Request für Parameter-Korrekturen"""
    session_id: str
    parameter_name: str
    old_value: Any
    new_value: Any
    correction_reason: Optional[str] = None
    user_feedback: Optional[str] = None

class ParameterCorrectionApiResponse(BaseModel):
    """API Response für Parameter-Korrekturen"""
    success: bool
    message: str
    updated_parameter: Optional[SourceGroundedParameter] = None
    needs_revalidation: bool = False

    # Updated Source Grounding
    updated_source_grounding: Optional[Dict[str, Any]] = None

    # Impact on other parameters
    affected_parameters: List[str] = Field(default_factory=list)

    # New completion status
    completion_percentage: float
    suggested_next_questions: List[str] = Field(default_factory=list)

class SessionAnalyticsResponse(BaseModel):
    """Analytics für Session Performance"""
    session_id: str
    total_messages: int
    total_parameters_extracted: int
    average_confidence: float
    extraction_method: str

    # Performance Metrics
    average_extraction_time: float
    total_corrections_made: int
    user_satisfaction_score: Optional[float] = None

    # Source Grounding Metrics
    highlight_coverage_percentage: float
    parameters_with_high_confidence: int
    parameters_needing_review: int

    # Quality Metrics
    extraction_accuracy: float
    user_confirmation_rate: float

    # Timestamps
    session_start: datetime
    session_end: Optional[datetime] = None
    total_duration: Optional[float] = None

class XMLGenerationWithSourceResponse(BaseModel):
    """XML Generation Response mit Source Information"""
    success: bool
    message: str
    xml_content: Optional[str] = None

    # Source Mapping für XML
    xml_source_mapping: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    parameter_to_xml_mapping: Dict[str, str] = Field(default_factory=dict)

    # Quality Information
    generation_confidence: float
    validation_issues: List[str] = Field(default_factory=list)

    # Metadata
    file_size: Optional[int] = None
    generation_duration: float = 0.0
    parameters_used: int = 0

# ================================
# ENHANCED API ENDPOINTS
# ================================

@router.post("/session/create", response_model=EnhancedChatSessionResponse)
async def create_enhanced_chat_session(
    request: EnhancedChatSessionRequest,
    background_tasks: BackgroundTasks
) -> EnhancedChatSessionResponse:
    """
    Erstellt eine neue Enhanced Chat Session mit LangExtract Source Grounding
    """
    try:
        logger.info(f"🚀 Creating enhanced chat session with source grounding enabled: {request.enable_source_grounding}")

        # Initialize LangExtract service
        langextract_service = get_langextract_parameter_service()

        # Create session ID
        session_id = f"enhanced_{int(datetime.now().timestamp() * 1000)}"

        # Initial job type detection if message provided
        job_type = request.job_type
        job_type_confidence = 1.0 if job_type else 0.0
        highlighted_ranges = []

        if request.initial_message and not job_type:
            # Use LangExtract for initial job type detection
            initial_extraction = await langextract_service.extract_parameters_with_grounding(
                user_message=request.initial_message
            )

            job_type = initial_extraction.job_type_detection.detected_job_type
            job_type_confidence = initial_extraction.job_type_detection.confidence
            highlighted_ranges = initial_extraction.highlighted_ranges

        # Generate welcome message
        welcome_message = _generate_welcome_message(job_type, request.initial_message)

        # Store session in background
        background_tasks.add_task(
            _store_enhanced_session,
            session_id,
            request,
            job_type,
            job_type_confidence
        )

        return EnhancedChatSessionResponse(
            session_id=session_id,
            job_type=job_type,
            job_type_confidence=job_type_confidence,
            status="active",
            message=welcome_message,
            source_grounding_enabled=request.enable_source_grounding,
            highlighted_ranges=highlighted_ranges,
            completion_percentage=0.0,
            suggested_questions=_get_initial_suggestions(job_type),
            created_at=datetime.now(),
            extraction_method="langextract"
        )

    except Exception as e:
        logger.error(f"❌ Failed to create enhanced chat session: {e}")
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")

@router.post("/message/send", response_model=EnhancedChatMessageResponse)
async def send_enhanced_chat_message(
    request: EnhancedChatMessageRequest,
    background_tasks: BackgroundTasks
) -> EnhancedChatMessageResponse:
    """
    Verarbeitet Nachricht mit LangExtract Source-Grounded Parameter Extraction
    """
    start_time = datetime.now()

    try:
        logger.info(f"💬 Processing enhanced chat message: '{request.message[:80]}...'")

        # Get LangExtract service
        langextract_service = get_langextract_parameter_service()

        # Load existing session data (simplified for this example)
        session_data = await _load_session_data(request.session_id)

        # Extract parameters with source grounding
        extraction_result = await langextract_service.extract_parameters_with_grounding(
            user_message=request.message,
            job_type=request.force_job_type or session_data.get("job_type"),
            existing_stream_params=session_data.get("stream_parameters", {}),
            existing_job_params=session_data.get("job_parameters", {})
        )

        # Generate response message
        response_message = await _generate_response_message(extraction_result, session_data)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Prepare source grounding data for frontend
        source_grounding_data = {
            "highlighted_ranges": extraction_result.highlighted_ranges,
            "parameter_sources": [
                {
                    "name": param.name,
                    "source_text": param.source_text,
                    "character_offsets": param.character_offsets,
                    "confidence": param.confidence,
                    "highlight_color": param.highlight_color
                }
                for param in extraction_result.stream_parameters + extraction_result.job_parameters
            ],
            "full_text": extraction_result.full_text,
            "extraction_quality": extraction_result.extraction_quality,
            "overall_confidence": extraction_result.overall_confidence
        }

        # Store updated session data in background
        background_tasks.add_task(
            _update_session_data,
            request.session_id,
            extraction_result,
            response_message
        )

        return EnhancedChatMessageResponse(
            session_id=request.session_id,
            response_message=response_message,
            detected_job_type=extraction_result.job_type_detection.detected_job_type,
            job_type_confidence=extraction_result.job_type_detection.confidence,
            job_type_alternatives=extraction_result.job_type_detection.alternative_candidates,
            stream_parameters=extraction_result.stream_parameters,
            job_parameters=extraction_result.job_parameters,
            source_grounding_data=source_grounding_data,
            highlighted_ranges=extraction_result.highlighted_ranges,
            completion_percentage=extraction_result.completion_percentage,
            next_required_parameter=extraction_result.next_required_parameter,
            missing_parameters=extraction_result.missing_stream_parameters + extraction_result.missing_job_parameters,
            suggested_questions=extraction_result.suggested_questions,
            contextual_suggestions=extraction_result.contextual_suggestions,
            overall_confidence=extraction_result.overall_confidence,
            extraction_quality=extraction_result.extraction_quality,
            needs_review=extraction_result.extraction_quality in ["low", "needs_review"],
            timestamp=datetime.now(),
            extraction_duration=processing_time,
            metadata={
                "extraction_method": "langextract",
                "job_type_detected": extraction_result.job_type_detection.detected_job_type,
                "parameters_extracted": len(extraction_result.stream_parameters + extraction_result.job_parameters),
                "processing_time": processing_time
            }
        )

    except Exception as e:
        logger.error(f"❌ Enhanced message processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Message processing failed: {str(e)}")

@router.post("/parameter/highlight", response_model=ParameterHighlightResponse)
async def get_parameter_highlight_info(
    request: ParameterHighlightRequest
) -> ParameterHighlightResponse:
    """
    Liefert detaillierte Highlight-Information für einen Parameter
    """
    try:
        logger.info(f"🔍 Getting highlight info for parameter: {request.parameter_name}")

        # Load session data to get parameter information
        session_data = await _load_session_data(request.session_id)

        # Find parameter in extracted data
        parameter = None
        for param in session_data.get("all_parameters", []):
            if param.get("name") == request.parameter_name:
                parameter = param
                break

        if not parameter:
            raise HTTPException(status_code=404, detail=f"Parameter {request.parameter_name} not found")

        # Generate context preview
        full_text = session_data.get("full_text", "")
        start, end = parameter.get("character_offsets", (0, 0))
        context_start = max(0, start - 20)
        context_end = min(len(full_text), end + 20)
        context_preview = full_text[context_start:context_end]

        return ParameterHighlightResponse(
            parameter_name=request.parameter_name,
            source_text=parameter.get("source_text", ""),
            character_offsets=parameter.get("character_offsets", (0, 0)),
            confidence=parameter.get("confidence", 0.0),
            context_preview=context_preview,
            alternative_interpretations=parameter.get("alternatives", [])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get parameter highlight info: {e}")
        raise HTTPException(status_code=500, detail=f"Highlight info retrieval failed: {str(e)}")

@router.post("/parameter/correct", response_model=ParameterCorrectionApiResponse)
async def correct_parameter(
    request: ParameterCorrectionApiRequest,
    background_tasks: BackgroundTasks
) -> ParameterCorrectionApiResponse:
    """
    Korrigiert einen Parameter und aktualisiert Source Grounding
    """
    try:
        logger.info(f"✏️ Correcting parameter {request.parameter_name}: {request.old_value} → {request.new_value}")

        # Load session data
        session_data = await _load_session_data(request.session_id)

        # Apply correction
        correction_result = await _apply_parameter_correction(
            session_data,
            request.parameter_name,
            request.old_value,
            request.new_value,
            request.correction_reason
        )

        # Update session data in background
        background_tasks.add_task(
            _update_session_after_correction,
            request.session_id,
            correction_result
        )

        return ParameterCorrectionApiResponse(
            success=True,
            message=f"Parameter {request.parameter_name} wurde erfolgreich korrigiert",
            updated_parameter=correction_result.get("updated_parameter"),
            needs_revalidation=correction_result.get("needs_revalidation", False),
            updated_source_grounding=correction_result.get("updated_source_grounding"),
            affected_parameters=correction_result.get("affected_parameters", []),
            completion_percentage=correction_result.get("completion_percentage", 0.0),
            suggested_next_questions=correction_result.get("suggested_questions", [])
        )

    except Exception as e:
        logger.error(f"❌ Parameter correction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Parameter correction failed: {str(e)}")

@router.get("/session/{session_id}/analytics", response_model=SessionAnalyticsResponse)
async def get_session_analytics(session_id: str) -> SessionAnalyticsResponse:
    """
    Liefert detaillierte Analytics für eine Session
    """
    try:
        logger.info(f"📊 Getting analytics for session: {session_id}")

        # Load session data and calculate analytics
        session_data = await _load_session_data(session_id)
        analytics = await _calculate_session_analytics(session_data)

        return SessionAnalyticsResponse(**analytics)

    except Exception as e:
        logger.error(f"❌ Failed to get session analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@router.post("/xml/generate-with-source", response_model=XMLGenerationWithSourceResponse)
async def generate_xml_with_source_mapping(
    session_id: str,
    background_tasks: BackgroundTasks
) -> XMLGenerationWithSourceResponse:
    """
    Generiert XML mit Source Mapping für jeden Parameter
    """
    start_time = datetime.now()

    try:
        logger.info(f"🔧 Generating XML with source mapping for session: {session_id}")

        # Load session data
        session_data = await _load_session_data(session_id)

        # Generate XML with source information
        xml_result = await _generate_xml_with_source_mapping(session_data)

        processing_time = (datetime.now() - start_time).total_seconds()

        # Store generation result in background
        background_tasks.add_task(
            _store_xml_generation_result,
            session_id,
            xml_result
        )

        return XMLGenerationWithSourceResponse(
            success=True,
            message="XML wurde erfolgreich mit Source Mapping generiert",
            xml_content=xml_result.get("xml_content"),
            xml_source_mapping=xml_result.get("source_mapping", {}),
            parameter_to_xml_mapping=xml_result.get("parameter_mapping", {}),
            generation_confidence=xml_result.get("confidence", 0.0),
            validation_issues=xml_result.get("validation_issues", []),
            file_size=len(xml_result.get("xml_content", "").encode('utf-8')),
            generation_duration=processing_time,
            parameters_used=xml_result.get("parameters_used", 0)
        )

    except Exception as e:
        logger.error(f"❌ XML generation with source mapping failed: {e}")
        raise HTTPException(status_code=500, detail=f"XML generation failed: {str(e)}")

# ================================
# HELPER FUNCTIONS
# ================================

def _generate_welcome_message(job_type: Optional[str], initial_message: Optional[str]) -> str:
    """Generiert Willkommensnachricht basierend auf Job-Type"""

    if job_type:
        job_type_messages = {
            "FILE_TRANSFER": "Perfekt! Ich helfe Ihnen bei der Konfiguration eines File Transfer Streams. Lassen Sie uns die Quell- und Ziel-Systeme definieren.",
            "SAP": "Ausgezeichnet! Ich unterstütze Sie bei der SAP-Stream Konfiguration. Welches SAP-System und welche Reports möchten Sie verwenden?",
            "STANDARD": "Gerne helfe ich bei der Standard-Prozess Konfiguration. Beschreiben Sie den gewünschten Workflow.",
            "CUSTOM": "Ich helfe bei der benutzerdefinierten Stream-Konfiguration. Was ist Ihr Ziel?"
        }
        return job_type_messages.get(job_type, "Ich helfe bei der Stream-Konfiguration. Was möchten Sie einrichten?")

    return "Willkommen! Ich unterstütze Sie bei der intelligenten Stream-Konfiguration mit Source-Grounded Parameter-Extraktion. Beschreiben Sie, was Sie einrichten möchten."

def _get_initial_suggestions(job_type: Optional[str]) -> List[str]:
    """Liefert initiale Vorschläge basierend auf Job-Type"""

    if job_type == "FILE_TRANSFER":
        return [
            "Von welchem Server sollen Dateien übertragen werden?",
            "Welche Dateitypen möchten Sie transferieren?",
            "Soll die Übertragung geplant werden?"
        ]
    elif job_type == "SAP":
        return [
            "Welches SAP-System verwenden Sie?",
            "Welche Daten möchten Sie exportieren?",
            "Benötigen Sie eine spezielle Variante?"
        ]
    elif job_type == "STANDARD":
        return [
            "Welche Art von Prozess möchten Sie automatisieren?",
            "Welche Input-Formate verwenden Sie?",
            "Wie oft soll der Prozess laufen?"
        ]

    return [
        "Beschreiben Sie Ihren gewünschten Stream.",
        "Welche Systeme sind beteiligt?",
        "Haben Sie spezielle Anforderungen?"
    ]

async def _load_session_data(session_id: str) -> Dict[str, Any]:
    """Lädt Session-Daten (Stub - würde aus Datenbank geladen)"""
    # TODO: Implement actual session storage/retrieval
    return {
        "session_id": session_id,
        "job_type": "FILE_TRANSFER",
        "stream_parameters": {},
        "job_parameters": {},
        "all_parameters": [],
        "full_text": "",
        "created_at": datetime.now()
    }

async def _store_enhanced_session(
    session_id: str,
    request: EnhancedChatSessionRequest,
    job_type: Optional[str],
    job_type_confidence: float
):
    """Speichert Enhanced Session (Background Task)"""
    # TODO: Implement session storage
    logger.info(f"💾 Storing enhanced session {session_id} with job_type={job_type}")

async def _update_session_data(
    session_id: str,
    extraction_result: SourceGroundedExtractionResult,
    response_message: str
):
    """Aktualisiert Session-Daten (Background Task)"""
    # TODO: Implement session update
    logger.info(f"🔄 Updating session {session_id} with {len(extraction_result.stream_parameters + extraction_result.job_parameters)} parameters")

async def _generate_response_message(
    extraction_result: SourceGroundedExtractionResult,
    session_data: Dict[str, Any]
) -> str:
    """Generiert intelligente Response-Nachricht"""

    total_params = len(extraction_result.stream_parameters + extraction_result.job_parameters)

    if total_params > 0:
        return f"Perfekt! Ich habe {total_params} Parameter aus Ihrer Nachricht extrahiert. {extraction_result.suggested_questions[0] if extraction_result.suggested_questions else 'Möchten Sie weitere Parameter hinzufügen?'}"
    else:
        return "Ich konnte keine spezifischen Parameter erkennen. Können Sie mehr Details zur gewünschten Konfiguration angeben?"

async def _apply_parameter_correction(
    session_data: Dict[str, Any],
    parameter_name: str,
    old_value: Any,
    new_value: Any,
    reason: Optional[str]
) -> Dict[str, Any]:
    """Wendet Parameter-Korrektur an"""
    # TODO: Implement actual parameter correction logic
    return {
        "updated_parameter": None,
        "needs_revalidation": False,
        "updated_source_grounding": {},
        "affected_parameters": [],
        "completion_percentage": 75.0,
        "suggested_questions": ["Sind alle Parameter jetzt korrekt?"]
    }

async def _update_session_after_correction(
    session_id: str,
    correction_result: Dict[str, Any]
):
    """Aktualisiert Session nach Korrektur (Background Task)"""
    logger.info(f"✏️ Applied correction for session {session_id}")

async def _calculate_session_analytics(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Berechnet Session Analytics"""
    # TODO: Implement real analytics calculation
    return {
        "session_id": session_data["session_id"],
        "total_messages": 5,
        "total_parameters_extracted": 8,
        "average_confidence": 0.85,
        "extraction_method": "langextract",
        "average_extraction_time": 1.2,
        "total_corrections_made": 1,
        "highlight_coverage_percentage": 78.5,
        "parameters_with_high_confidence": 6,
        "parameters_needing_review": 2,
        "extraction_accuracy": 0.92,
        "user_confirmation_rate": 0.87,
        "session_start": session_data.get("created_at", datetime.now()),
        "session_end": None,
        "total_duration": None
    }

async def _generate_xml_with_source_mapping(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generiert XML mit Source Mapping"""
    # TODO: Implement actual XML generation with source mapping
    return {
        "xml_content": "<?xml version='1.0'?><stream>...</stream>",
        "source_mapping": {},
        "parameter_mapping": {},
        "confidence": 0.9,
        "validation_issues": [],
        "parameters_used": 8
    }

async def _store_xml_generation_result(
    session_id: str,
    xml_result: Dict[str, Any]
):
    """Speichert XML Generation Result (Background Task)"""
    logger.info(f"💾 Storing XML generation result for session {session_id}")

# Health Check
@router.get("/health")
async def health_check():
    """Health check für Enhanced Chat XML Router"""
    return {
        "status": "healthy",
        "service": "enhanced-chat-xml",
        "features": [
            "source_grounding",
            "langextract_integration",
            "parameter_correction",
            "real_time_highlighting",
            "session_analytics"
        ],
        "timestamp": datetime.now()
    }