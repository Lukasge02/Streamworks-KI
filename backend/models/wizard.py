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
