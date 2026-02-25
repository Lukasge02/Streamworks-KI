from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int
    message: str


class DocumentInfo(BaseModel):
    id: str
    filename: str
    file_size: int
    mime_type: str
    chunks: int = 0
    created_at: Optional[datetime] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 5
