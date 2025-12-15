from typing import List, Optional
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    doc_type: Optional[str] = None
    doc_id: Optional[str] = None


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[dict]] = None
    num_chunks: int = 5


class ChatResponseModel(BaseModel):
    answer: str
    sources: List[dict]
    has_context: bool
    chunks_found: int
    session_id: Optional[str] = None
    # Enhanced RAG fields
    confidence: Optional[float] = None
    confidence_level: Optional[str] = None
    query_type: Optional[str] = None
    warnings: Optional[List[str]] = None
    search_type: Optional[str] = None
    processing_time_ms: Optional[int] = None


class DocumentResponse(BaseModel):
    doc_id: str
    filename: str
    doc_type: str
    chunks: int
    created_at: str
    has_original: bool = True
    metadata: dict


class SearchResult(BaseModel):
    doc_id: str
    content: str
    filename: str
    score: float
    metadata: dict


class CreateCategoryRequest(BaseModel):
    name: str
    parent: Optional[str] = None


class RenameCategoryRequest(BaseModel):
    new_name: str


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None


class MoveToCategoryRequest(BaseModel):
    category: str


class CategoryAccessRequest(BaseModel):
    access_level: str = "internal"
    allowed_roles: Optional[List[str]] = None
    inheritable: bool = True


class DocumentAccessRequest(BaseModel):
    access_level: str = "internal"  # public, internal, restricted, project
    allowed_roles: Optional[List[str]] = None
    allowed_users: Optional[List[str]] = None


class UpdateSessionRequest(BaseModel):
    title: str


class ChatRequestWithSession(BaseModel):
    query: str
    session_id: Optional[str] = None
