"""Pydantic models for the RAG metrics API."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TotalsSummary(BaseModel):
    queries: int = Field(..., ge=0)
    successful: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0)


class LatencySummary(BaseModel):
    average_ms: float = Field(..., ge=0.0)
    p95_ms: float = Field(..., ge=0.0)
    p99_ms: float = Field(..., ge=0.0)


class QualitySummary(BaseModel):
    avg_relevance: float = Field(..., ge=0.0, le=1.0)
    avg_sources_per_query: float = Field(..., ge=0.0)
    unique_sources: int = Field(..., ge=0)


class LiveMetricsResponse(BaseModel):
    status: str = Field(..., description="Aggregated system status")
    window_minutes: int = Field(..., ge=1)
    updated_at: datetime
    totals: TotalsSummary
    latency: LatencySummary
    quality: QualitySummary


class SourceDocumentInsight(BaseModel):
    document_id: str
    filename: str
    usage_count: int = Field(..., ge=0)
    avg_relevance: float = Field(..., ge=0.0, le=1.0)
    avg_confidence: float = Field(..., ge=0.0, le=1.0)
    last_used: Optional[datetime]


class SourceInsightsTotals(BaseModel):
    documents: int = Field(..., ge=0)
    usages: int = Field(..., ge=0)


class SourceInsightsResponse(BaseModel):
    status: str
    updated_at: datetime
    totals: SourceInsightsTotals
    top_documents: List[SourceDocumentInsight]


class ActivityBucket(BaseModel):
    start: datetime
    end: datetime
    total_queries: int = Field(..., ge=0)
    avg_response_time_ms: float = Field(..., ge=0.0)
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0)
    error_count: int = Field(..., ge=0)


class ActivityTimelineResponse(BaseModel):
    status: str
    updated_at: datetime
    window_minutes: int = Field(..., ge=1)
    bucket_size_minutes: int = Field(..., ge=1)
    buckets: List[ActivityBucket]


class MetricsHealthResponse(BaseModel):
    status: str
    updated_at: datetime
    tracked_queries: int = Field(..., ge=0)
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0)


class DocumentNavigationRequest(BaseModel):
    document_id: str
    page_number: Optional[int] = Field(None, ge=1)
    chunk_id: Optional[str] = None


class DocumentNavigationResponse(BaseModel):
    url: str
    document_id: str
    page_number: Optional[int]
    chunk_id: Optional[str]
