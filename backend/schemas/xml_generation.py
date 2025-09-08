"""
XML Generation Schemas for StreamWorks XML Generator
"""
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class JobType(str, Enum):
    STANDARD = "standard"
    SAP = "sap"
    FILE_TRANSFER = "fileTransfer"
    CUSTOM = "custom"


class OSType(str, Enum):
    WINDOWS = "Windows"
    UNIX = "Unix"


class ScheduleMode(str, Enum):
    SIMPLE = "simple"
    NATURAL = "natural"
    ADVANCED = "advanced"


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


# Base Forms
class ContactPerson(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    company: str = Field(default="Arvato Systems")
    department: Optional[str] = None


class SAPParameter(BaseModel):
    parameter: str
    value: str
    type: str = Field(default="SIGN")  # SIGN, OPTION, LOW, HIGH


# Job-specific form data
class StandardJobForm(BaseModel):
    job_name: str = Field(..., min_length=1)
    agent: str = Field(default="gtasswvk05445")
    os: OSType
    script: str = Field(..., min_length=1)
    parameters: List[str] = Field(default_factory=list)


class SAPJobForm(BaseModel):
    job_name: str = Field(..., min_length=1)
    system: str = Field(..., min_length=1)  # PA1_100
    report: str = Field(..., min_length=1)  # RBDAGAIN, ZWM_TO_CREATE
    variant: str = Field(default="")  # 0100_NEST_DEL
    batch_user: str = Field(..., min_length=1)  # Batch_PUR
    selection_parameters: List[SAPParameter] = Field(default_factory=list)


class FileTransferForm(BaseModel):
    job_name: str = Field(..., min_length=1)
    source_agent: str = Field(..., min_length=1)
    source_path: str = Field(..., min_length=1)
    target_agent: str = Field(..., min_length=1)
    target_path: str = Field(..., min_length=1)
    file_pattern: Optional[str] = None
    on_exists_behavior: str = Field(default="Overwrite")  # Overwrite, Abort, Append
    delete_after_transfer: bool = Field(default=False)


# Stream properties
class StreamProperties(BaseModel):
    stream_name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    documentation: Optional[str] = None
    contact_person: ContactPerson
    max_runs: int = Field(default=5, ge=1, le=50)
    retention_days: Optional[int] = None
    severity_group: Optional[str] = None
    stream_path: Optional[str] = None


# Scheduling
class SimpleSchedule(BaseModel):
    preset: str  # manual, daily, weekly, monthly
    time: Optional[str] = None  # HH:MM
    weekdays: List[bool] = Field(default_factory=lambda: [True] * 7)


class NaturalSchedule(BaseModel):
    description: str = Field(..., min_length=1)


class AdvancedSchedule(BaseModel):
    cron_expression: Optional[str] = None
    schedule_rule_xml: Optional[str] = None


class SchedulingForm(BaseModel):
    mode: ScheduleMode
    simple: Optional[SimpleSchedule] = None
    natural: Optional[NaturalSchedule] = None
    advanced: Optional[AdvancedSchedule] = None


# Complete wizard data
class WizardFormData(BaseModel):
    job_type: JobType
    job_form: Union[StandardJobForm, SAPJobForm, FileTransferForm, Dict[str, Any]]
    stream_properties: StreamProperties
    scheduling: SchedulingForm
    
    class Config:
        use_enum_values = True


# Template search and matching
class XMLTemplate(BaseModel):
    id: str
    filename: str
    file_path: str
    job_type: JobType
    description: str
    complexity_score: float = Field(ge=0, le=10)
    job_count: int
    patterns: List[str] = Field(default_factory=list)
    xml_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TemplateSearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    job_type: Optional[JobType] = None
    max_results: int = Field(default=5, ge=1, le=20)


class TemplateMatch(BaseModel):
    template: XMLTemplate
    similarity_score: float = Field(ge=0, le=1)
    reasons: List[str] = Field(default_factory=list)


# Validation results
class ValidationError(BaseModel):
    line: Optional[int] = None
    column: Optional[int] = None
    severity: ValidationSeverity
    message: str
    suggestion: Optional[str] = None


class ValidationResult(BaseModel):
    valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationError] = Field(default_factory=list)
    schema_version: Optional[str] = None


# XML Generation Results
class XMLGenerationResult(BaseModel):
    success: bool
    xml_content: Optional[str] = None
    template_used: Optional[TemplateMatch] = None
    validation_results: Optional[ValidationResult] = None
    requires_human_review: bool = Field(default=False)
    review_reasons: List[str] = Field(default_factory=list)
    generation_time_ms: Optional[int] = None
    error_message: Optional[str] = None


# Job type information
class JobTypeInfo(BaseModel):
    type: JobType
    title: str
    description: str
    complexity: str  # simple, medium, complex
    estimated_time: str  # "3-5 minutes"
    icon: str
    examples: List[str] = Field(default_factory=list)
    template_count: int = Field(default=0)


# Schedule parsing
class ScheduleRule(BaseModel):
    schedule_rule_xml: str
    description: str
    next_executions: List[datetime] = Field(default_factory=list)


# Response models
class JobTypesResponse(BaseModel):
    job_types: List[JobTypeInfo]


class TemplateSearchResponse(BaseModel):
    templates: List[TemplateMatch]
    total_found: int
    search_time_ms: int


class ValidationResponse(BaseModel):
    validation_result: ValidationResult
    validation_time_ms: int


class ScheduleParsingResponse(BaseModel):
    schedule_rule: ScheduleRule
    parsing_time_ms: int