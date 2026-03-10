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
    folder_id: Optional[str] = None
    created_at: Optional[datetime] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


# ── Folder Models ──────────────────────────────────────────────────

class FolderCreate(BaseModel):
    name: str
    color: str = "#0066cc"


class FolderInfo(BaseModel):
    id: str
    name: str
    color: str
    document_count: int = 0
    created_at: Optional[datetime] = None


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class DocumentMove(BaseModel):
    folder_id: Optional[str] = None


class DocumentPreview(BaseModel):
    id: str
    filename: str
    content: str
    mime_type: str
