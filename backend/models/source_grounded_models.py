"""
Source-Grounded Parameter Models für LangExtract Integration
Erweiterte Parameter-Models mit Source Grounding für maximale Transparenz
"""

from typing import Any, Dict, List, Optional, Tuple, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class SourceGroundedParameter(BaseModel):
    """Enhanced Parameter mit Source Grounding Information"""

    # Basic Parameter Info
    name: str = Field(description="Name des Parameters")
    value: Any = Field(description="Extrahierter Wert")
    confidence: float = Field(description="Extraktions-Konfidenz 0.0-1.0")

    # 🆕 Source Grounding Features
    source_text: str = Field(description="Original-Text aus dem die Info extrahiert wurde")
    character_offsets: Tuple[int, int] = Field(description="[start, end] Positionen im Original-Text")
    extraction_confidence: float = Field(description="LangExtract spezifische Konfidenz")

    # Parameter Classification
    scope: Literal["stream", "job"] = Field(description="Parameter-Bereich: stream oder job", default="stream")
    data_type: str = Field(description="Datentyp (string, integer, boolean, enum)", default="string")

    # UI Enhancement Data
    highlight_color: str = Field(description="CSS Farbe für Highlighting", default="blue")
    tooltip_info: str = Field(description="Zusätzliche Tooltip-Information", default="")

    # Validation Status
    user_confirmed: bool = Field(description="Ob User den Parameter bestätigt hat", default=False)
    validation_errors: List[str] = Field(description="Validierungsfehler", default_factory=list)

    # Metadata
    extraction_method: Literal["langextract", "unified", "hybrid"] = Field(
        description="Extraktions-Methode",
        default="langextract"
    )
    extracted_at: datetime = Field(description="Zeitpunkt der Extraktion", default_factory=datetime.now)


class JobTypeDetection(BaseModel):
    """Job-Type Erkennungs-Ergebnis mit Source Grounding"""

    detected_job_type: str = Field(description="Erkannter Job-Type (FILE_TRANSFER, SAP, STANDARD)")
    confidence: float = Field(description="Erkennungs-Konfidenz 0.0-1.0")

    # Source Grounding für Job-Type
    detection_source_text: str = Field(description="Text der zur Job-Type Erkennung führte")
    detection_offsets: Tuple[int, int] = Field(description="Positionen der Job-Type Indikatoren")

    # Alternative Kandidaten
    alternative_candidates: List[Dict[str, Any]] = Field(
        description="Alternative Job-Types mit Konfidenz",
        default_factory=list
    )

    # Detection Details
    matched_keywords: List[str] = Field(description="Gefundene Keywords", default_factory=list)
    matched_patterns: List[str] = Field(description="Gefundene Patterns", default_factory=list)
    detection_method: Literal["keywords", "patterns", "llm", "hybrid"] = Field(default="hybrid")


class SourceGroundedExtractionResult(BaseModel):
    """Komplettes LangExtract Ergebnis mit allen Features"""

    # Job-Type Information
    job_type_detection: JobTypeDetection

    # Extracted Parameters mit Source Grounding
    stream_parameters: List[SourceGroundedParameter] = Field(default_factory=list)
    job_parameters: List[SourceGroundedParameter] = Field(default_factory=list)

    # Source Mapping für UI
    full_text: str = Field(description="Original User-Nachricht")
    highlighted_ranges: List[Tuple[int, int, str]] = Field(
        description="Alle Highlight-Bereiche [start, end, parameter_name]",
        default_factory=list
    )

    # Dialog Status
    completion_percentage: float = Field(description="Vervollständigung in Prozent", default=0.0)
    missing_stream_parameters: List[str] = Field(default_factory=list)
    missing_job_parameters: List[str] = Field(default_factory=list)
    next_required_parameter: Optional[str] = Field(default=None)

    # Smart Suggestions
    suggested_questions: List[str] = Field(default_factory=list)
    contextual_suggestions: List[str] = Field(default_factory=list)

    # Quality Metrics
    overall_confidence: float = Field(description="Gesamt-Konfidenz der Extraktion", default=0.0)
    extraction_quality: Literal["high", "medium", "low", "needs_review"] = Field(default="medium")

    # Metadata
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

    # Error Handling
    extraction_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ParameterCorrectionRequest(BaseModel):
    """Request für Parameter-Korrekturen durch User"""

    parameter_name: str
    old_value: Any
    new_value: Any
    correction_reason: Optional[str] = None
    user_feedback: Optional[str] = None


class ParameterCorrectionResult(BaseModel):
    """Ergebnis einer Parameter-Korrektur"""

    parameter_name: str
    updated_value: Any
    confidence_after_correction: float
    needs_revalidation: bool = False

    # Update Source Grounding nach Korrektur
    updated_source_text: Optional[str] = None
    updated_offsets: Optional[Tuple[int, int]] = None

    # Metadata
    corrected_at: datetime = Field(default_factory=datetime.now)
    correction_applied: bool = True


class LangExtractConfig(BaseModel):
    """Konfiguration für LangExtract Service"""

    # Model Configuration
    model_id: str = Field(default="gpt-4o")
    api_key: str
    fence_output: bool = Field(default=True)
    use_schema_constraints: bool = Field(default=False)

    # Source Grounding Settings
    enable_source_grounding: bool = Field(default=True)
    min_confidence_threshold: float = Field(default=0.5)

    # Job-Type Detection
    job_type_detection_enabled: bool = Field(default=True)
    confidence_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "high_confidence": 0.85,
            "medium_confidence": 0.65,
            "low_confidence": 0.45
        }
    )

    # Performance Settings
    max_retries: int = Field(default=3)
    timeout_seconds: int = Field(default=30)

    # Debug Settings
    enable_debug_logging: bool = Field(default=False)
    save_extraction_logs: bool = Field(default=False)


class ExtractionMetrics(BaseModel):
    """Metriken für LangExtract Performance Tracking"""

    # Timing
    extraction_duration: float = Field(description="Dauer der Extraktion in Sekunden")
    api_call_duration: float = Field(description="API Call Dauer")
    post_processing_duration: float = Field(description="Post-Processing Dauer")

    # Quality Metrics
    parameters_extracted: int = Field(description="Anzahl extrahierter Parameter")
    parameters_with_high_confidence: int = Field(description="Parameter mit hoher Konfidenz")
    parameters_needing_review: int = Field(description="Parameter die Review brauchen")

    # Source Grounding Metrics
    total_highlighted_chars: int = Field(description="Anzahl hervorgehobener Zeichen")
    highlight_coverage_percentage: float = Field(description="Abdeckung des Original-Texts")

    # Error Tracking
    extraction_errors: int = Field(default=0)
    api_errors: int = Field(default=0)
    validation_errors: int = Field(default=0)

    # User Interaction
    user_corrections_made: int = Field(default=0)
    user_confirmations: int = Field(default=0)

    # Metadata
    session_id: Optional[str] = None
    job_type: Optional[str] = None
    recorded_at: datetime = Field(default_factory=datetime.now)


class StreamWorksSchema(BaseModel):
    """Schema-Definition für StreamWorks Parameter"""

    # Schema Metadata
    schema_name: str
    schema_version: str
    job_type: str

    # Parameter Definitions
    stream_parameters: List[Dict[str, Any]] = Field(default_factory=list)
    job_parameters: List[Dict[str, Any]] = Field(default_factory=list)

    # LangExtract Integration
    few_shot_examples: List[Dict[str, Any]] = Field(default_factory=list)
    extraction_prompts: Dict[str, str] = Field(default_factory=dict)

    # Validation Rules
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    required_parameters: List[str] = Field(default_factory=list)

    # Detection Configuration
    detection_config: Dict[str, Any] = Field(default_factory=dict)


# Utility Functions für Source Grounding

def calculate_highlight_coverage(
    text: str,
    highlighted_ranges: List[Tuple[int, int, str]]
) -> float:
    """Berechnet die Abdeckung des Texts durch Highlights"""
    if not text or not highlighted_ranges:
        return 0.0

    highlighted_chars = set()
    for start, end, _ in highlighted_ranges:
        highlighted_chars.update(range(start, end))

    return len(highlighted_chars) / len(text)


def merge_overlapping_ranges(
    ranges: List[Tuple[int, int, str]]
) -> List[Tuple[int, int, str]]:
    """Merged überlappende Highlight-Bereiche"""
    if not ranges:
        return []

    # Sort by start position
    sorted_ranges = sorted(ranges, key=lambda x: x[0])
    merged = [sorted_ranges[0]]

    for current in sorted_ranges[1:]:
        last = merged[-1]

        # Check for overlap
        if current[0] <= last[1]:
            # Merge ranges
            new_end = max(last[1], current[1])
            new_name = f"{last[2]}, {current[2]}"
            merged[-1] = (last[0], new_end, new_name)
        else:
            merged.append(current)

    return merged


def validate_character_offsets(
    text: str,
    offsets: Tuple[int, int]
) -> bool:
    """Validiert ob Character-Offsets im Text gültig sind"""
    start, end = offsets
    return (
        0 <= start < len(text) and
        start <= end <= len(text)
    )