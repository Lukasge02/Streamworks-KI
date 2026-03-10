from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WizardSession(BaseModel):
    id: str
    data: dict = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SaveStepRequest(BaseModel):
    step: int
    data: dict


class AnalyzeRequest(BaseModel):
    description: str


class AnalyzeResponse(BaseModel):
    job_type: str
    confidence: float
    parameters: dict
    suggestions: list[str] = []


class GenerateXmlRequest(BaseModel):
    session_id: str
    stream_name: Optional[str] = None


class GenerateXmlResponse(BaseModel):
    xml: str
    filename: str
    warnings: list[str] = []


# ---------------------------------------------------------------------------
# Quick Edit
# ---------------------------------------------------------------------------


class QuickEditRequest(BaseModel):
    instruction: str
    session_names: dict[str, str]  # session_id -> stream_name


class FieldChange(BaseModel):
    field: str           # Frontend-Feldname (z.B. "stream_name", "email")
    old_value: Optional[str] = None
    new_value: str
    step: int            # Wizard-Step (0-6)
    label: str           # Menschenlesbar fuer UI


class QuickEditPreview(BaseModel):
    session_id: Optional[str] = None
    session_name: Optional[str] = None
    changes: list[FieldChange] = []
    message: str         # AI-Erklaerung
    error: Optional[str] = None


class QuickEditApplyRequest(BaseModel):
    session_id: str
    changes: list[FieldChange]
