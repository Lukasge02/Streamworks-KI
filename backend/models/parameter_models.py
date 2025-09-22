"""
Parameter Models - Pydantic Models für alle Job-Types
Auto-generiert aus job_type_schemas.json
"""

from typing import Optional, List, Union, Any, Dict
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator
from langchain_core.pydantic_v1 import BaseModel as LangChainBaseModel

# ================================
# ENUMS FÜR PARAMETER VALUES
# ================================

class StreamRunDeletionType(str, Enum):
    """Stream Run Deletion Type Options"""
    NONE = "None"
    IMMEDIATE = "Immediate"
    SCHEDULED = "Scheduled"

class SAPSystem(str, Enum):
    """SAP System Options"""
    PA1_100 = "PA1_100"
    PA1_200 = "PA1_200"
    PT1_100 = "PT1_100"
    PD1_100 = "PD1_100"

class ResourceStatus(str, Enum):
    """Resource Status Options"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"

# ================================
# JOB-TYPE PARAMETER MODELS
# ================================

class StandardJobParametersModel(BaseModel):
    """
    STANDARD Job Type - Parameter Model
    Ein einfacher Job-Typ für die Ausführung von Streams
    """

    StreamName: Optional[str] = Field(
        None,
        title="Stream Name",
        description="Der Name des Streams",
        example="geck003_ft"
    )

    StreamDocumentation: Optional[str] = Field(
        "Keine Dokumentation vorhanden.",
        title="Stream Dokumentation",
        description="Dokumentation für den Stream",
        example="Meine Dokumentation"
    )

    MaxStreamRuns: Optional[int] = Field(
        5,
        title="Maximale Stream-Ausführungen",
        description="Maximale Anzahl der Ausführungen des Streams",
        ge=1,
        example=5
    )

    ShortDescription: Optional[str] = Field(
        None,
        title="Kurze Beschreibung",
        description="Kurze Beschreibung des Streams",
        example="Erster Stream"
    )

    SchedulingRequiredFlag: Optional[bool] = Field(
        False,
        title="Planung erforderlich",
        description="Gibt an, ob eine Planung erforderlich ist"
    )

    StreamRunDeletionType: Optional[StreamRunDeletionType] = StreamRunDeletionType.NONE

    JobName: Optional[str] = Field(
        None,
        title="Job Name",
        description="Der Name des Jobs",
        example="StartPoint"
    )

    JobCategory: Optional[str] = Field(
        None,
        title="Job Kategorie",
        description="Kategorie des Jobs",
        example="StartPoint"
    )

    IsNotificationRequired: Optional[bool] = Field(
        False,
        title="Benachrichtigung erforderlich",
        description="Gibt an, ob eine Benachrichtigung erforderlich ist"
    )

    @validator('MaxStreamRuns')
    def validate_max_stream_runs(cls, v):
        if v is not None and v <= 0:
            raise ValueError('MaxStreamRuns muss größer als 0 sein')
        return v

    class Config:
        schema_extra = {
            "example": {
                "StreamName": "geck003_ft",
                "StreamDocumentation": "Export und Import des Streams",
                "MaxStreamRuns": 5,
                "ShortDescription": "Beispiel Export-Import Utility",
                "SchedulingRequiredFlag": False,
                "StreamRunDeletionType": "None",
                "JobName": "StartPoint",
                "JobCategory": "StartPoint",
                "IsNotificationRequired": False
            }
        }

class SAPJobParametersModel(BaseModel):
    """
    SAP Job Type - Parameter Model
    SAP Report oder Programm mit Parametern
    """

    system: Optional[SAPSystem] = Field(
        None,
        title="SAP System",
        description="SAP System für die Ausführung"
    )

    report: Optional[str] = Field(
        None,
        title="SAP Report",
        description="SAP Report Name",
        example="RBDAGAIN"
    )

    variant: Optional[str] = Field(
        None,
        title="Report Variante",
        description="Report-Variante (optional)",
        example="VAR01"
    )

    batch_user: Optional[str] = Field(
        "Batch_PUR",
        title="Batch User",
        description="Batch-Benutzer für die Ausführung",
        example="Batch_PUR"
    )

    @validator('report')
    def validate_report(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Report Name darf nicht leer sein')
        return v

    class Config:
        schema_extra = {
            "example": {
                "system": "PA1_100",
                "report": "RBDAGAIN",
                "variant": "VAR01",
                "batch_user": "Batch_PUR"
            }
        }

class FileTransferParametersModel(BaseModel):
    """
    FILE_TRANSFER Job Type - Parameter Model
    Dateiübertragung zwischen Systemen
    """

    source_agent: Optional[str] = Field(
        None,
        title="Quell-Agent",
        description="Quell-Agent für Dateiübertragung",
        example="gtasswvv15778"
    )

    target_agent: Optional[str] = Field(
        None,
        title="Ziel-Agent",
        description="Ziel-Agent für Dateiübertragung",
        example="gtasswvw15779"
    )

    source_path: Optional[str] = Field(
        None,
        title="Quell-Pfad",
        description="Quell-Dateipfad",
        example="E:\\data\\export.txt"
    )

    target_path: Optional[str] = Field(
        None,
        title="Ziel-Pfad",
        description="Ziel-Dateipfad",
        example="E:\\backup\\"
    )

    @validator('source_path', 'target_path')
    def validate_paths(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Pfad darf nicht leer sein')
        return v

    class Config:
        schema_extra = {
            "example": {
                "source_agent": "gtasswvv15778",
                "target_agent": "gtasswvw15779",
                "source_path": "E:\\data\\export.txt",
                "target_path": "E:\\backup\\"
            }
        }

class CustomJobParametersModel(BaseModel):
    """
    CUSTOM Job Type - Parameter Model
    Ein Job, der benutzerdefinierte Parameter verwendet
    """

    ResourceName: Optional[str] = Field(
        None,
        title="Resource Name",
        description="Der Name der Ressource",
        example="DEMOST01"
    )

    ShortDescription: Optional[str] = Field(
        None,
        title="Kurze Beschreibung",
        description="Eine kurze Beschreibung der Ressource",
        example="RESOURCE FUER STREAM DEMOST01"
    )

    Status: Optional[ResourceStatus] = Field(
        ResourceStatus.ACTIVE,
        title="Status",
        description="Der Status der Ressource"
    )

    MaxParallelAllocations: Optional[int] = Field(
        1,
        title="Max. parallele Zuweisungen",
        description="Die maximale Anzahl paralleler Zuweisungen",
        ge=1,
        example=1
    )

    AutoReleaseFlag: Optional[bool] = Field(
        True,
        title="Automatische Freigabe",
        description="Ob die Ressource automatisch freigegeben werden soll"
    )

    LogicalResourceType: Optional[str] = Field(
        "Normal",
        title="Logischer Resource Type",
        description="Der Typ der logischen Ressource",
        example="Normal"
    )

    MasterLogicalResourceId: Optional[str] = Field(
        None,
        title="Master Logical Resource ID",
        description="Die ID der Master-logischen Ressource",
        example="12345678"
    )

    DefaultMaxParallelAllocations: Optional[int] = Field(
        1,
        title="Standard Max. parallele Zuweisungen",
        description="Der Standardwert für maximale parallele Zuweisungen",
        ge=1,
        example=1
    )

    @validator('MaxParallelAllocations', 'DefaultMaxParallelAllocations')
    def validate_allocation_numbers(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Anzahl Zuweisungen muss größer als 0 sein')
        return v

    class Config:
        schema_extra = {
            "example": {
                "ResourceName": "DEMOST01",
                "ShortDescription": "RESOURCE FUER STREAM DEMOST01",
                "Status": "Active",
                "MaxParallelAllocations": 1,
                "AutoReleaseFlag": True,
                "LogicalResourceType": "Normal",
                "MasterLogicalResourceId": "12345678",
                "DefaultMaxParallelAllocations": 1
            }
        }

# ================================
# PARAMETER STATE MANAGEMENT MODELS
# ================================

class ParameterValidationResult(BaseModel):
    """Ergebnis der Parameter-Validierung"""
    is_valid: bool = Field(description="Ob alle Parameter valide sind")
    errors: List[str] = Field(default_factory=list, description="Liste der Validierungsfehler")
    warnings: List[str] = Field(default_factory=list, description="Liste der Warnungen")
    completion_percentage: float = Field(description="Vervollständigungs-Prozentsatz (0.0-1.0)")
    missing_required_parameters: List[str] = Field(default_factory=list, description="Fehlende erforderliche Parameter")

class JobParameterCollection(BaseModel):
    """Sammlung aller Parameter für einen Job"""
    job_type: str = Field(description="Job-Type (STANDARD, SAP, FILE_TRANSFER, CUSTOM)")
    parameters: Union[
        StandardJobParametersModel,
        SAPJobParametersModel,
        FileTransferParametersModel,
        CustomJobParametersModel
    ] = Field(description="Parameter-Objekt basierend auf Job-Type")
    created_at: datetime = Field(default_factory=datetime.now, description="Erstellungszeitpunkt")
    updated_at: datetime = Field(default_factory=datetime.now, description="Letzte Aktualisierung")
    completion_status: str = Field(default="incomplete", description="Status: incomplete, complete, validated")

class ParameterExtractionHistory(BaseModel):
    """Historie der Parameter-Extraktionen"""
    session_id: str = Field(description="Session ID")
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    user_message: str = Field(description="Original User-Nachricht")
    extracted_parameters: List[str] = Field(description="Liste der extrahierten Parameter-Namen")
    confidence_score: float = Field(description="Konfidenz-Score der Extraktion")
    success: bool = Field(description="Ob die Extraktion erfolgreich war")

# ================================
# LANGCHAIN-COMPATIBLE MODELS
# ================================

class StandardJobParametersLangChain(LangChainBaseModel):
    """LangChain-kompatible Version für STANDARD Job Parameters"""
    StreamName: Optional[str] = Field(None, description="Der Name des Streams")
    StreamDocumentation: Optional[str] = Field(None, description="Dokumentation für den Stream")
    MaxStreamRuns: Optional[int] = Field(None, description="Maximale Anzahl der Ausführungen")
    ShortDescription: Optional[str] = Field(None, description="Kurze Beschreibung des Streams")
    SchedulingRequiredFlag: Optional[bool] = Field(None, description="Ob eine Planung erforderlich ist")
    StreamRunDeletionType: Optional[str] = Field(None, description="Typ der Löschung für Stream-Ausführungen")
    JobName: Optional[str] = Field(None, description="Der Name des Jobs")
    JobCategory: Optional[str] = Field(None, description="Kategorie des Jobs")
    IsNotificationRequired: Optional[bool] = Field(None, description="Ob eine Benachrichtigung erforderlich ist")

class SAPJobParametersLangChain(LangChainBaseModel):
    """LangChain-kompatible Version für SAP Job Parameters"""
    system: Optional[str] = Field(None, description="SAP System")
    report: Optional[str] = Field(None, description="SAP Report Name")
    variant: Optional[str] = Field(None, description="Report-Variante")
    batch_user: Optional[str] = Field(None, description="Batch-Benutzer")

class FileTransferParametersLangChain(LangChainBaseModel):
    """LangChain-kompatible Version für FILE_TRANSFER Job Parameters"""
    source_agent: Optional[str] = Field(None, description="Quell-Agent")
    target_agent: Optional[str] = Field(None, description="Ziel-Agent")
    source_path: Optional[str] = Field(None, description="Quell-Dateipfad")
    target_path: Optional[str] = Field(None, description="Ziel-Dateipfad")

class CustomJobParametersLangChain(LangChainBaseModel):
    """LangChain-kompatible Version für CUSTOM Job Parameters"""
    ResourceName: Optional[str] = Field(None, description="Der Name der Ressource")
    ShortDescription: Optional[str] = Field(None, description="Eine kurze Beschreibung der Ressource")
    Status: Optional[str] = Field(None, description="Der Status der Ressource")
    MaxParallelAllocations: Optional[int] = Field(None, description="Die maximale Anzahl paralleler Zuweisungen")
    AutoReleaseFlag: Optional[bool] = Field(None, description="Ob die Ressource automatisch freigegeben werden soll")
    LogicalResourceType: Optional[str] = Field(None, description="Der Typ der logischen Ressource")
    MasterLogicalResourceId: Optional[str] = Field(None, description="Die ID der Master-logischen Ressource")
    DefaultMaxParallelAllocations: Optional[int] = Field(None, description="Der Standardwert für maximale parallele Zuweisungen")

# ================================
# MODEL MAPPING UTILITIES
# ================================

JOB_TYPE_MODEL_MAPPING = {
    "STANDARD": StandardJobParametersModel,
    "SAP": SAPJobParametersModel,
    "FILE_TRANSFER": FileTransferParametersModel,
    "CUSTOM": CustomJobParametersModel
}

LANGCHAIN_MODEL_MAPPING = {
    "STANDARD": StandardJobParametersLangChain,
    "SAP": SAPJobParametersLangChain,
    "FILE_TRANSFER": FileTransferParametersLangChain,
    "CUSTOM": CustomJobParametersLangChain
}

def get_parameter_model(job_type: str) -> BaseModel:
    """Gibt das Pydantic Model für einen Job-Type zurück"""
    return JOB_TYPE_MODEL_MAPPING.get(job_type.upper())

def get_langchain_model(job_type: str) -> LangChainBaseModel:
    """Gibt das LangChain-kompatible Model für einen Job-Type zurück"""
    return LANGCHAIN_MODEL_MAPPING.get(job_type.upper())

def create_parameter_instance(job_type: str, **kwargs) -> Union[
    StandardJobParametersModel,
    SAPJobParametersModel,
    FileTransferParametersModel,
    CustomJobParametersModel
]:
    """Erstellt eine Parameter-Instanz für einen Job-Type"""
    model_class = get_parameter_model(job_type)
    if model_class:
        return model_class(**kwargs)
    else:
        raise ValueError(f"Unbekannter Job-Type: {job_type}")

# ================================
# HIERARCHICAL STREAM MODELS
# ================================

class ParameterScope(str, Enum):
    """Parameter-Scope für hierarchische Stream-Konfiguration"""
    STREAM = "stream"
    JOB = "job"
    UNKNOWN = "unknown"

class JobConfiguration(BaseModel):
    """Konfiguration für einen einzelnen Job innerhalb eines Streams"""
    job_id: str = Field(description="Eindeutige Job-ID")
    job_type: str = Field(description="Job-Type (STANDARD, SAP, FILE_TRANSFER, CUSTOM)")
    job_name: Optional[str] = Field(None, description="Benutzerfreundlicher Job-Name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Job-spezifische Parameter")
    completion_percentage: float = Field(default=0.0, description="Vervollständigung des Jobs (0.0-1.0)")
    validation_errors: List[str] = Field(default_factory=list, description="Validierungsfehler für diesen Job")
    created_at: datetime = Field(default_factory=datetime.now, description="Erstellungszeitpunkt")
    updated_at: datetime = Field(default_factory=datetime.now, description="Letzte Aktualisierung")

    class Config:
        schema_extra = {
            "example": {
                "job_id": "job_001",
                "job_type": "FILE_TRANSFER",
                "job_name": "MainTransfer",
                "parameters": {
                    "source_agent": "gt123",
                    "target_agent": "basf",
                    "source_path": "E://test",
                    "target_path": "C://test"
                },
                "completion_percentage": 1.0,
                "validation_errors": []
            }
        }

class CompletionStatus(BaseModel):
    """Vervollständigungsstatus für hierarchische Stream-Konfiguration"""
    stream_complete: bool = Field(default=False, description="Stream-Level Parameter vollständig")
    jobs_complete: bool = Field(default=False, description="Alle Jobs vollständig konfiguriert")
    overall_percentage: float = Field(default=0.0, description="Gesamt-Vervollständigung (0.0-1.0)")
    missing_stream_parameters: List[str] = Field(default_factory=list, description="Fehlende Stream-Parameter")
    incomplete_jobs: List[str] = Field(default_factory=list, description="Unvollständige Job-IDs")
    validation_passed: bool = Field(default=False, description="Gesamte Validierung bestanden")

class HierarchicalStreamSession(BaseModel):
    """
    Hierarchische Stream-Session für Parameter-Akkumulation
    Unterstützt sowohl Stream-Level als auch Job-Level Parameter
    """
    session_id: str = Field(description="Eindeutige Session-ID")
    session_type: str = Field(default="STREAM_CONFIGURATION", description="Session-Typ")
    user_id: Optional[str] = Field(None, description="Benutzer-ID")

    # Stream-Level Parameter (aus STANDARD Job-Type)
    stream_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Stream-Level Parameter (Name, Dokumentation, etc.)"
    )

    # Job-Level Konfigurationen
    jobs: List[JobConfiguration] = Field(
        default_factory=list,
        description="Liste der Jobs in diesem Stream"
    )

    # Status und Metadaten
    completion_status: CompletionStatus = Field(
        default_factory=CompletionStatus,
        description="Vervollständigungsstatus"
    )
    dialog_state: str = Field(default="initial", description="Aktueller Dialog-Status")
    last_message: Optional[str] = Field(None, description="Letzte Benutzer-Nachricht")
    suggested_questions: List[str] = Field(default_factory=list, description="Vorgeschlagene Fragen")

    # Zeitstempel
    created_at: datetime = Field(default_factory=datetime.now, description="Erstellungszeitpunkt")
    updated_at: datetime = Field(default_factory=datetime.now, description="Letzte Aktualisierung")
    expires_at: datetime = Field(description="Ablaufzeitpunkt")

    # Metadaten
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Zusätzliche Metadaten")

    def add_or_update_job(self, job_type: str, parameters: Dict[str, Any], job_name: Optional[str] = None) -> str:
        """Fügt einen Job hinzu oder aktualisiert bestehenden Job"""
        import uuid

        # Suche nach bestehendem Job desselben Typs
        existing_job = next((job for job in self.jobs if job.job_type == job_type), None)

        if existing_job:
            # Aktualisiere bestehenden Job
            existing_job.parameters.update(parameters)
            existing_job.updated_at = datetime.now()
            if job_name:
                existing_job.job_name = job_name
            return existing_job.job_id
        else:
            # Erstelle neuen Job
            job_id = str(uuid.uuid4())
            new_job = JobConfiguration(
                job_id=job_id,
                job_type=job_type,
                job_name=job_name or f"{job_type}_Job",
                parameters=parameters,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.jobs.append(new_job)
            return job_id

    def update_stream_parameters(self, parameters: Dict[str, Any]) -> None:
        """Aktualisiert Stream-Level Parameter"""
        self.stream_parameters.update(parameters)
        self.updated_at = datetime.now()

    def get_job_by_type(self, job_type: str) -> Optional[JobConfiguration]:
        """Holt Job-Konfiguration nach Typ"""
        return next((job for job in self.jobs if job.job_type == job_type), None)

    def get_all_parameters(self) -> Dict[str, Any]:
        """Gibt alle Parameter (Stream + Jobs) als flache Struktur zurück"""
        all_params = self.stream_parameters.copy()

        for job in self.jobs:
            # Prefix Job-Parameter mit Job-Type um Konflikte zu vermeiden
            for param_name, param_value in job.parameters.items():
                all_params[f"{job.job_type.lower()}_{param_name}"] = param_value

        return all_params

    def calculate_completion(self) -> CompletionStatus:
        """Berechnet Vervollständigungsstatus"""
        from services.ai.smart_parameter_extractor import get_smart_parameter_extractor

        try:
            extractor = get_smart_parameter_extractor()

            # Stream-Parameter prüfen (STANDARD Schema)
            standard_schema = extractor.get_job_type_info("STANDARD")
            if standard_schema:
                required_stream_params = [p["name"] for p in standard_schema["parameters"] if p["required"]]
                missing_stream = [name for name in required_stream_params
                                if self.stream_parameters.get(name) is None]
                stream_complete = len(missing_stream) == 0
            else:
                missing_stream = []
                stream_complete = True

            # Jobs prüfen
            incomplete_jobs = []
            total_job_completion = 0.0

            for job in self.jobs:
                job_schema = extractor.get_job_type_info(job.job_type)
                if job_schema:
                    required_params = [p["name"] for p in job_schema["parameters"] if p["required"]]
                    missing_params = [name for name in required_params
                                    if job.parameters.get(name) is None]

                    if missing_params:
                        incomplete_jobs.append(job.job_id)
                        job.completion_percentage = max(0.0, 1.0 - len(missing_params) / len(required_params))
                    else:
                        job.completion_percentage = 1.0

                    total_job_completion += job.completion_percentage

            jobs_complete = len(incomplete_jobs) == 0 and len(self.jobs) > 0

            # Gesamt-Completion
            if len(self.jobs) > 0:
                avg_job_completion = total_job_completion / len(self.jobs)
                overall_percentage = (0.3 * (1.0 if stream_complete else 0.5)) + (0.7 * avg_job_completion)
            else:
                overall_percentage = 1.0 if stream_complete else 0.5

            # Update Completion Status
            self.completion_status = CompletionStatus(
                stream_complete=stream_complete,
                jobs_complete=jobs_complete,
                overall_percentage=overall_percentage,
                missing_stream_parameters=missing_stream,
                incomplete_jobs=incomplete_jobs,
                validation_passed=stream_complete and jobs_complete
            )

            return self.completion_status

        except Exception as e:
            # Fallback bei Fehlern
            self.completion_status = CompletionStatus(
                overall_percentage=0.5 if self.stream_parameters or self.jobs else 0.0
            )
            return self.completion_status

    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123",
                "session_type": "STREAM_CONFIGURATION",
                "stream_parameters": {
                    "StreamName": "datentransfer_test",
                    "StreamDocumentation": "Transfer zwischen GT123 und BASF",
                    "ShortDescription": "Datentransfer Test"
                },
                "jobs": [
                    {
                        "job_id": "job_001",
                        "job_type": "FILE_TRANSFER",
                        "job_name": "MainTransfer",
                        "parameters": {
                            "source_agent": "gt123",
                            "target_agent": "basf"
                        }
                    }
                ],
                "completion_status": {
                    "stream_complete": True,
                    "jobs_complete": False,
                    "overall_percentage": 0.65
                }
            }
        }

# ================================
# PARAMETER SCOPE UTILITIES
# ================================

# Stream-Level Parameter (aus STANDARD Job-Type)
STREAM_LEVEL_PARAMETERS = {
    "StreamName", "StreamDocumentation", "MaxStreamRuns", "ShortDescription",
    "SchedulingRequiredFlag", "StreamRunDeletionType", "JobName", "JobCategory",
    "IsNotificationRequired"
}

# Job-Level Parameter nach Job-Type
JOB_LEVEL_PARAMETERS = {
    "SAP": {"system", "report", "variant", "batch_user"},
    "FILE_TRANSFER": {"source_agent", "target_agent", "source_path", "target_path"},
    "CUSTOM": {"ResourceName", "ShortDescription", "Status", "MaxParallelAllocations",
               "AutoReleaseFlag", "LogicalResourceType", "MasterLogicalResourceId",
               "DefaultMaxParallelAllocations"}
}

def classify_parameter_scope(parameter_name: str, context_job_type: Optional[str] = None) -> ParameterScope:
    """Klassifiziert Parameter-Scope basierend auf Name und Kontext"""

    # Stream-Level Parameter prüfen
    if parameter_name in STREAM_LEVEL_PARAMETERS:
        return ParameterScope.STREAM

    # Job-Level Parameter prüfen
    if context_job_type and context_job_type in JOB_LEVEL_PARAMETERS:
        if parameter_name in JOB_LEVEL_PARAMETERS[context_job_type]:
            return ParameterScope.JOB

    # Alle Job-Types durchsuchen
    for job_type, params in JOB_LEVEL_PARAMETERS.items():
        if parameter_name in params:
            return ParameterScope.JOB

    return ParameterScope.UNKNOWN

def split_parameters_by_scope(parameters: Dict[str, Any], context_job_type: Optional[str] = None) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Teilt Parameter nach Scope auf: (stream_params, job_params)"""
    stream_params = {}
    job_params = {}

    for param_name, param_value in parameters.items():
        scope = classify_parameter_scope(param_name, context_job_type)

        if scope == ParameterScope.STREAM:
            stream_params[param_name] = param_value
        elif scope == ParameterScope.JOB:
            job_params[param_name] = param_value
        # UNKNOWN Parameter werden zu Job-Parameter (safer default)
        else:
            job_params[param_name] = param_value

    return stream_params, job_params