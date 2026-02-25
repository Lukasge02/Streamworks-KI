from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class Source(BaseModel):
    document_name: str
    chunk_text: str
    score: float
    page: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []
    session_id: str
    confidence: float = 0.0


class ChatSession(BaseModel):
    id: str
    title: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    sources: list[Source] = []
    created_at: Optional[datetime] = None
