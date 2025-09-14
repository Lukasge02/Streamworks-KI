"""
RAG (Retrieval Augmented Generation) Services Module
Professional conversational AI with advanced document understanding
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

class RAGMode(Enum):
    """RAG operation modes for different use cases"""
    FAST = "fast"                    # Quick responses, minimal context
    ACCURATE = "accurate"            # Balanced speed and accuracy
    COMPREHENSIVE = "comprehensive"  # Maximum context, detailed responses

@dataclass
class RAGResponse:
    """Standardized RAG response format"""
    answer: str
    confidence_score: float
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    processing_time_ms: int
    mode_used: RAGMode

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "answer": self.answer,
            "confidence_score": self.confidence_score,
            "sources": self.sources,
            "metadata": self.metadata,
            "processing_time_ms": self.processing_time_ms,
            "mode_used": self.mode_used.value
        }

@dataclass
class DocumentSource:
    """Document source with metadata"""
    content: str
    document_id: str
    chunk_id: str
    page_number: Optional[int] = None
    score: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class QueryContext:
    """Query context for enhanced processing"""
    original_query: str
    conversation_context: List[Dict[str, Any]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    mode: RAGMode = RAGMode.ACCURATE

    def __post_init__(self):
        if self.conversation_context is None:
            self.conversation_context = []