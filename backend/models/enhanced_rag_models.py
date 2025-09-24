"""
Enhanced RAG Models with Source Transparency
Updated models for RAG responses with complete source tracking and navigation
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class RAGMode(Enum):
    """RAG operation modes"""
    FAST = "fast"
    ACCURATE = "accurate"
    COMPREHENSIVE = "comprehensive"

class SourceReference(BaseModel):
    """Enhanced source reference with navigation data"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    page_number: Optional[int] = Field(None, description="Page number in document")
    section: Optional[str] = Field(None, description="Document section or heading")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    snippet: str = Field(..., description="Relevant text snippet")
    chunk_index: int = Field(..., description="Chunk index in document")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in source")
    doc_type: Optional[str] = Field(None, description="Document type (pdf, docx, etc.)")
    chunk_id: Optional[str] = Field(None, description="Unique chunk identifier")

    # Navigation metadata
    file_size: Optional[int] = Field(None, description="File size in bytes")
    upload_date: Optional[str] = Field(None, description="Document upload date")
    last_modified: Optional[str] = Field(None, description="Last modification date")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123456",
                "filename": "ProjectPlan_2024.pdf",
                "page_number": 5,
                "section": "Implementation Timeline",
                "relevance_score": 0.89,
                "snippet": "Das Projekt wird in drei Phasen unterteilt...",
                "chunk_index": 12,
                "confidence": 0.92,
                "doc_type": "pdf",
                "chunk_id": "chunk_doc123_12"
            }
        }

class RAGMetrics(BaseModel):
    """Real-time metrics for RAG response"""
    response_time_ms: float = Field(..., description="Total response time in milliseconds")
    source_retrieval_time_ms: float = Field(..., description="Time to retrieve sources")
    llm_generation_time_ms: float = Field(..., description="LLM generation time")
    cache_hit: bool = Field(..., description="Whether response was cached")
    total_chunks_searched: int = Field(..., description="Total chunks searched")
    relevant_chunks_found: int = Field(..., description="Relevant chunks found")
    query_complexity: str = Field(..., description="Query complexity (simple/medium/complex)")
    retrieval_method: str = Field(..., description="Retrieval method used")

    class Config:
        json_schema_extra = {
            "example": {
                "response_time_ms": 1250.5,
                "source_retrieval_time_ms": 200.3,
                "llm_generation_time_ms": 850.2,
                "cache_hit": False,
                "total_chunks_searched": 150,
                "relevant_chunks_found": 5,
                "query_complexity": "medium",
                "retrieval_method": "hybrid_search"
            }
        }

class EnhancedRAGResponse(BaseModel):
    """Enhanced RAG response with complete source transparency"""
    answer: str = Field(..., description="Generated answer")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in answer")
    sources: List[SourceReference] = Field(..., description="Source documents used")
    metrics: RAGMetrics = Field(..., description="Performance metrics")
    mode_used: RAGMode = Field(..., description="RAG mode used for processing")
    query_id: str = Field(..., description="Unique query identifier")
    timestamp: str = Field(..., description="Response timestamp")

    # Enhanced metadata
    context_used: bool = Field(..., description="Whether conversation context was used")
    source_diversity: float = Field(..., ge=0.0, le=1.0, description="Diversity of sources (0-1)")
    answer_completeness: float = Field(..., ge=0.0, le=1.0, description="Answer completeness score")

    # Navigation hints
    primary_source_id: Optional[str] = Field(None, description="Primary source document ID")
    related_queries: List[str] = Field(default_factory=list, description="Related query suggestions")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Das Streamworks-Projekt befindet sich in der Implementierungsphase...",
                "confidence_score": 0.91,
                "sources": [],  # Would contain SourceReference examples
                "metrics": {},  # Would contain RAGMetrics example
                "mode_used": "accurate",
                "query_id": "query_789123",
                "timestamp": "2024-01-15T10:30:45Z",
                "context_used": True,
                "source_diversity": 0.75,
                "answer_completeness": 0.88,
                "primary_source_id": "doc_123456",
                "related_queries": [
                    "Welche Risiken gibt es beim Projekt?",
                    "Wie ist der aktuelle Projektfortschritt?"
                ]
            }
        }

class LiveRAGMetrics(BaseModel):
    """Real-time system-wide RAG metrics"""
    response_time_ms: float = Field(..., description="Average response time")
    source_quality_avg: float = Field(..., ge=0.0, le=1.0, description="Average source quality")
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0, description="Cache hit rate")
    active_sources: int = Field(..., description="Number of active source documents")
    total_queries: int = Field(..., description="Total queries processed")
    avg_sources_per_query: float = Field(..., description="Average sources per query")
    system_status: str = Field(..., description="System health status")
    last_updated: str = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "response_time_ms": 1456.7,
                "source_quality_avg": 0.84,
                "cache_hit_rate": 0.78,
                "active_sources": 145,
                "total_queries": 1256,
                "avg_sources_per_query": 4.2,
                "system_status": "healthy",
                "last_updated": "2024-01-15T10:30:45Z"
            }
        }

class SourceAnalytics(BaseModel):
    """Analytics for document sources"""
    document_id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Document filename")
    usage_count: int = Field(..., description="Number of times used")
    avg_relevance: float = Field(..., ge=0.0, le=1.0, description="Average relevance score")
    last_used: str = Field(..., description="Last usage timestamp")
    recent_queries: List[str] = Field(..., description="Recent queries that used this source")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123456",
                "filename": "ProjectPlan_2024.pdf",
                "usage_count": 45,
                "avg_relevance": 0.87,
                "last_used": "2024-01-15T10:25:30Z",
                "recent_queries": [
                    "Projektplan Status",
                    "Timeline Übersicht",
                    "Implementierung Phase 2"
                ]
            }
        }

# API Request/Response Models
class EnhancedRAGQueryRequest(BaseModel):
    """Enhanced RAG query request"""
    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    mode: RAGMode = Field(default=RAGMode.ACCURATE, description="RAG processing mode")
    max_sources: int = Field(default=5, ge=1, le=20, description="Maximum sources to return")
    include_context: bool = Field(default=True, description="Include conversation context")
    session_id: Optional[str] = Field(None, description="Session identifier")
    filters: Optional[Dict[str, Any]] = Field(None, description="Document filters")

class RAGQueryResponse(BaseModel):
    """RAG query response wrapper"""
    success: bool = Field(..., description="Query success status")
    data: Optional[EnhancedRAGResponse] = Field(None, description="RAG response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    query_id: str = Field(..., description="Query identifier")

# Chat Integration Models
class ChatMessageWithSources(BaseModel):
    """Chat message with enhanced source information"""
    id: str = Field(..., description="Message identifier")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    sources: List[SourceReference] = Field(default_factory=list, description="Source references")
    metrics: Optional[RAGMetrics] = Field(None, description="Performance metrics")
    confidence_score: Optional[float] = Field(None, description="Response confidence")
    timestamp: str = Field(..., description="Message timestamp")

# Source Navigation Models
class DocumentNavigationRequest(BaseModel):
    """Request to navigate to a document source"""
    document_id: str = Field(..., description="Document identifier")
    page_number: Optional[int] = Field(None, description="Target page number")
    chunk_id: Optional[str] = Field(None, description="Target chunk identifier")
    highlight_text: Optional[str] = Field(None, description="Text to highlight")

class DocumentNavigationResponse(BaseModel):
    """Response for document navigation"""
    success: bool = Field(..., description="Navigation success")
    document_url: str = Field(..., description="Document viewer URL")
    document_title: str = Field(..., description="Document title")
    page_count: Optional[int] = Field(None, description="Total pages in document")
    error: Optional[str] = Field(None, description="Error message if failed")