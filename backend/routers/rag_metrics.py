"""RAG metrics API endpoints."""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query

from models.rag_metrics import (
    ActivityTimelineResponse,
    DocumentNavigationRequest,
    DocumentNavigationResponse,
    LiveMetricsResponse,
    MetricsHealthResponse,
    SourceInsightsResponse,
)
from services.rag_metrics_service import get_rag_metrics_service

router = APIRouter(
    prefix="/rag-metrics",
    tags=["rag-metrics"],
)


@router.get("/live", response_model=LiveMetricsResponse)
async def get_live_rag_metrics(
    window_minutes: int = Query(15, ge=1, le=240, description="Time window for aggregation"),
) -> LiveMetricsResponse:
    service = await get_rag_metrics_service()
    payload = await service.get_live_metrics(window_minutes=window_minutes)
    return LiveMetricsResponse(**payload)


@router.get("/sources", response_model=SourceInsightsResponse)
async def get_source_insights(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of documents to return"),
    window_hours: int = Query(24, ge=1, le=168, description="Time span for aggregation in hours"),
) -> SourceInsightsResponse:
    service = await get_rag_metrics_service()
    payload = await service.get_source_insights(limit=limit, window_hours=window_hours)
    return SourceInsightsResponse(**payload)


@router.get("/activity", response_model=ActivityTimelineResponse)
async def get_activity_timeline(
    window_minutes: int = Query(60, ge=5, le=720, description="Time window for the timeline in minutes"),
    bucket_minutes: int = Query(5, ge=1, le=120, description="Bucket size in minutes"),
) -> ActivityTimelineResponse:
    service = await get_rag_metrics_service()
    payload = await service.get_activity_timeline(
        window_minutes=window_minutes, bucket_minutes=bucket_minutes
    )
    return ActivityTimelineResponse(**payload)


@router.get("/health", response_model=MetricsHealthResponse)
async def get_metrics_health() -> MetricsHealthResponse:
    service = await get_rag_metrics_service()
    payload = await service.get_health()
    return MetricsHealthResponse(**payload)


@router.post("/reset", response_model=Dict[str, Any])
async def reset_metrics() -> Dict[str, Any]:
    service = await get_rag_metrics_service()
    await service.reset()
    return {
        "status": "reset",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/navigate-to-source", response_model=DocumentNavigationResponse)
async def navigate_to_source(
    request: DocumentNavigationRequest,
) -> DocumentNavigationResponse:
    document_url = f"/documents/{request.document_id}"
    params = []
    if request.page_number is not None:
        params.append(f"page={request.page_number}")
    if request.chunk_id:
        params.append(f"chunk={request.chunk_id}")

    if params:
        document_url = f"{document_url}?{'&'.join(params)}"

    return DocumentNavigationResponse(
        url=document_url,
        document_id=request.document_id,
        page_number=request.page_number,
        chunk_id=request.chunk_id,
    )
