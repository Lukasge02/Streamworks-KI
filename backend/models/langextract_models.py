"""
LangExtract Models
Moderne, streamlined Models für das neue LangExtract-First System
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class SessionState(str, Enum):
    """StreamWorks Session States"""
    STREAM_CONFIGURATION = "stream_configuration"
    PARAMETER_COLLECTION = "parameter_collection"
    VALIDATION = "validation"
    READY_FOR_XML = "ready_for_xml"
    COMPLETED = "completed"


class ChatMessage(BaseModel):
    """Chat message within a session"""
    type: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class StreamWorksSession(BaseModel):
    """🎯 StreamWorks Session - Clean & Simple"""

    session_id: str
    job_type: Optional[str] = None
    state: SessionState = SessionState.STREAM_CONFIGURATION

    # Parameters
    stream_parameters: Dict[str, Any] = Field(default_factory=dict)
    job_parameters: Dict[str, Any] = Field(default_factory=dict)

    # Missing Parameters
    critical_missing: List[str] = Field(default_factory=list)

    # Progress tracking
    completion_percentage: float = Field(default=0.0, description="Completion percentage (0.0 to 100.0)")

    # Messages
    messages: List[ChatMessage] = Field(default_factory=list)

    # Timestamps
    created_at: datetime
    last_activity: datetime

    # Optional metadata
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StreamParameter(BaseModel):
    """Stream-level parameter (common to all job types)"""

    name: str
    value: Any
    confidence: float = 1.0
    source_text: Optional[str] = None
    character_offsets: Optional[tuple[int, int]] = None
    user_confirmed: bool = False


class JobParameter(BaseModel):
    """Job-specific parameter"""

    name: str
    value: Any
    confidence: float = 1.0
    source_text: Optional[str] = None
    character_offsets: Optional[tuple[int, int]] = None
    job_type: str
    user_confirmed: bool = False


class ExtractionResult(BaseModel):
    """Result of LangExtract parameter extraction"""

    # Extracted Parameters
    stream_parameters: Dict[str, Any] = Field(default_factory=dict)
    job_parameters: Dict[str, Any] = Field(default_factory=dict)

    # Source Grounding
    highlighted_ranges: List[tuple[int, int, str]] = Field(default_factory=list)
    source_mapping: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    # Quality Metrics
    overall_confidence: float = 0.0
    extraction_quality: str = "medium"  # high, medium, low, needs_review

    # Missing Parameters
    missing_critical: List[str] = Field(default_factory=list)
    next_suggested_parameter: Optional[str] = None

    # Error Handling
    extraction_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    # Metadata
    extraction_duration: float = 0.0
    api_calls_made: int = 0


class LangExtractRequest(BaseModel):
    """Request for LangExtract processing"""

    message: str
    session_id: Optional[str] = None
    job_type: Optional[str] = None

    # Optional context
    previous_context: Dict[str, Any] = Field(default_factory=dict)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)


class LangExtractResponse(BaseModel):
    """🚀 Complete LangExtract Response - Clean & Feature-Rich"""

    # Core Response
    session_id: str
    response_message: str

    # Extracted Parameters
    extracted_stream_parameters: Dict[str, Any] = Field(default_factory=dict)
    extracted_job_parameters: Dict[str, Any] = Field(default_factory=dict)

    # Progress & Guidance
    next_parameter: Optional[str] = None
    suggested_questions: List[str] = Field(default_factory=list)

    # Source Grounding (LangExtract Feature)
    source_grounding_data: Optional[Dict[str, Any]] = None
    source_grounded_parameters: List[Dict[str, Any]] = Field(default_factory=list)

    # Quality & Confidence
    extraction_quality: str = "medium"
    needs_review: bool = False
    parameter_confidences: Dict[str, float] = Field(default_factory=dict)

    # Session Info
    job_type: Optional[str] = None
    session_state: str = "stream_configuration"

    # Performance
    processing_time: float = 0.0

    # Error Handling
    error: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)

    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.now)


class ParameterCorrectionRequest(BaseModel):
    """Request to correct an extracted parameter"""

    session_id: str
    parameter_name: str
    old_value: Any
    new_value: Any
    correction_reason: Optional[str] = None


class ParameterCorrectionResponse(BaseModel):
    """Response after parameter correction"""

    session_id: str
    parameter_name: str
    correction_applied: bool
    updated_confidence: float
    impact_on_other_parameters: List[str] = Field(default_factory=list)


class XMLGenerationRequest(BaseModel):
    """Request for XML generation"""

    session_id: str
    force_generation: bool = False  # Generate even if incomplete
    custom_template: Optional[str] = None


class XMLGenerationResponse(BaseModel):
    """Response with generated XML"""

    session_id: str
    xml_content: str
    generation_successful: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    used_parameters: Dict[str, Any] = Field(default_factory=dict)
    missing_parameters: List[str] = Field(default_factory=list)


# Analytics & Monitoring Models

class ExtractionMetrics(BaseModel):
    """Metrics for monitoring extraction performance"""

    session_id: str
    job_type: str

    # Performance
    extraction_duration: float
    api_call_duration: float
    total_api_calls: int

    # Quality
    parameters_extracted: int
    parameters_with_high_confidence: int
    parameters_needing_review: int
    overall_confidence: float

    # User Interaction
    user_corrections: int
    suggested_questions_used: int

    # Outcome
    xml_generated: bool
    session_completed: bool

    timestamp: datetime = Field(default_factory=datetime.now)


class SessionAnalytics(BaseModel):
    """Analytics for a complete session"""

    session_id: str
    job_type: str

    # Timeline
    session_duration: float
    messages_exchanged: int

    # Parameter Extraction
    total_parameters_extracted: int
    parameters_auto_extracted: int
    parameters_manually_corrected: int

    # Quality
    average_confidence: float
    extraction_accuracy: float  # If we have validation data

    # User Experience
    questions_asked_by_system: int
    suggestions_used_by_user: int
    user_satisfaction_score: Optional[float] = None

    # Outcome
    xml_successfully_generated: bool
    completion_rate: float

    created_at: datetime = Field(default_factory=datetime.now)


# Configuration Models

class LangExtractConfig(BaseModel):
    """Configuration for LangExtract Service"""

    # Model Settings
    model_id: str = "gpt-4o"
    api_key: str

    # Extraction Settings
    enable_source_grounding: bool = True
    confidence_threshold: float = 0.6
    max_retries: int = 3

    # Performance
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour

    # Quality
    auto_correction_threshold: float = 0.9
    manual_review_threshold: float = 0.4

    # Features
    enable_smart_suggestions: bool = True
    enable_parameter_validation: bool = True


# Validation Models

class ParameterValidationRule(BaseModel):
    """Rule for validating extracted parameters"""

    parameter_name: str
    job_types: List[str]  # Which job types this applies to
    validation_type: str  # regex, enum, range, custom
    validation_config: Dict[str, Any]
    error_message: str
    severity: str = "error"  # error, warning, info


class ValidationResult(BaseModel):
    """Result of parameter validation"""

    parameter_name: str
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggested_corrections: List[str] = Field(default_factory=list)


# Export Models for API

__all__ = [
    "SessionState",
    "ChatMessage",
    "StreamWorksSession",
    "StreamParameter",
    "JobParameter",
    "ExtractionResult",
    "LangExtractRequest",
    "LangExtractResponse",
    "ParameterCorrectionRequest",
    "ParameterCorrectionResponse",
    "XMLGenerationRequest",
    "XMLGenerationResponse",
    "ExtractionMetrics",
    "SessionAnalytics",
    "LangExtractConfig",
    "ParameterValidationRule",
    "ValidationResult"
]