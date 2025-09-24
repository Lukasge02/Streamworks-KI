"""RAG metrics collection and aggregation service."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


@dataclass
class SourceReference:
    """Normalized reference to a RAG source document."""

    document_id: str
    filename: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    relevance_score: float = 0.0
    snippet: str = ""
    chunk_index: int = 0
    confidence: float = 0.0
    doc_type: Optional[str] = None
    chunk_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "page_number": self.page_number,
            "section": self.section,
            "relevance_score": self.relevance_score,
            "snippet": self.snippet,
            "chunk_index": self.chunk_index,
            "confidence": self.confidence,
            "doc_type": self.doc_type,
            "chunk_id": self.chunk_id,
        }


@dataclass
class QueryEvent:
    """Snapshot of a processed RAG query."""

    timestamp: datetime
    response_time_ms: float
    sources: List[SourceReference]
    cache_hit: bool
    mode: str
    session_id: Optional[str]
    error: Optional[str]

    @property
    def successful(self) -> bool:
        return self.error is None

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def average_relevance(self) -> float:
        if not self.sources:
            return 0.0
        return sum(max(src.relevance_score, 0.0) for src in self.sources) / len(self.sources)


class RAGMetricsService:
    """Collects and aggregates real-time RAG telemetry."""

    def __init__(self, max_events: int = 2000, retention_hours: int = 48) -> None:
        self._events: deque[QueryEvent] = deque(maxlen=max_events)
        self._retention = timedelta(hours=retention_hours)
        self._lock = asyncio.Lock()
        self._updated_at: datetime = datetime.utcnow()
        logger.info("RAG metrics service initialised")

    async def track_rag_query(
        self,
        *,
        query: str,
        sources: List[SourceReference],
        response_time_ms: float,
        cache_hit: bool = False,
        mode: str = "accurate",
        session_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Record telemetry for a single query."""
        event = QueryEvent(
            timestamp=datetime.utcnow(),
            response_time_ms=max(response_time_ms, 0.0),
            sources=sources,
            cache_hit=bool(cache_hit),
            mode=mode,
            session_id=session_id,
            error=error,
        )

        async with self._lock:
            self._events.append(event)
            self._updated_at = event.timestamp
            self._prune_expired()

    async def get_live_metrics(self, *, window_minutes: int = 15) -> Dict[str, Any]:
        """Aggregate metrics for the last ``window_minutes`` minutes."""
        events, updated_at = await self._collect_window(window_minutes)

        if not events:
            return self._empty_live_payload(window_minutes, updated_at)

        durations = [event.response_time_ms for event in events]
        successful = [event for event in events if event.successful]
        failures = len(events) - len(successful)
        cache_hits = sum(1 for event in events if event.cache_hit)
        cache_hit_rate = cache_hits / len(events) if events else 0.0

        avg_response = sum(durations) / len(durations)
        p95 = self._percentile(durations, 0.95)
        p99 = self._percentile(durations, 0.99)

        avg_sources = sum(event.source_count for event in events) / len(events)
        avg_relevance = sum(event.average_relevance for event in events) / len(events)
        unique_sources = len(
            {
                source.document_id
                for event in events
                for source in event.sources
                if source.document_id
            }
        )

        status = self._determine_status(
            average_response_ms=avg_response,
            failure_ratio=failures / len(events) if events else 0.0,
            cache_hit_rate=cache_hit_rate,
        )

        return {
            "status": status,
            "window_minutes": window_minutes,
            "updated_at": updated_at.isoformat(),
            "totals": {
                "queries": len(events),
                "successful": len(successful),
                "failed": failures,
                "cache_hit_rate": round(cache_hit_rate, 4),
            },
            "latency": {
                "average_ms": round(avg_response, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
            },
            "quality": {
                "avg_relevance": round(avg_relevance, 4),
                "avg_sources_per_query": round(avg_sources, 2),
                "unique_sources": unique_sources,
            },
        }

    async def get_source_insights(
        self, *, limit: int = 10, window_hours: int = 24
    ) -> Dict[str, Any]:
        """Return aggregated document utilisation insights."""
        events, updated_at = await self._collect_window(window_hours * 60)

        if not events:
            return {
                "status": "initializing",
                "updated_at": updated_at.isoformat(),
                "totals": {"documents": 0, "usages": 0},
                "top_documents": [],
            }

        doc_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "document_id": "",
                "filename": "Unknown document",
                "usage_count": 0,
                "total_relevance": 0.0,
                "total_confidence": 0.0,
                "last_used": None,
            }
        )
        total_usage = 0

        for event in events:
            for source in event.sources:
                doc_id = source.document_id or "unknown"
                stats = doc_stats[doc_id]
                stats["document_id"] = doc_id
                stats["filename"] = source.filename or stats["filename"]
                stats["usage_count"] += 1
                stats["total_relevance"] += max(source.relevance_score, 0.0)
                stats["total_confidence"] += max(source.confidence, 0.0)
                stats["last_used"] = self._max_datetime(stats["last_used"], event.timestamp)
                total_usage += 1

        insights: List[Dict[str, Any]] = []
        for stats in doc_stats.values():
            usage = stats["usage_count"]
            insights.append(
                {
                    "document_id": stats["document_id"],
                    "filename": stats["filename"],
                    "usage_count": usage,
                    "avg_relevance": round(
                        stats["total_relevance"] / usage if usage else 0.0, 4
                    ),
                    "avg_confidence": round(
                        stats["total_confidence"] / usage if usage else 0.0, 4
                    ),
                    "last_used": stats["last_used"].isoformat() if stats["last_used"] else None,
                }
            )

        insights.sort(
            key=lambda item: (item["usage_count"], item["avg_relevance"]), reverse=True
        )

        return {
            "status": "ok",
            "updated_at": updated_at.isoformat(),
            "totals": {"documents": len(insights), "usages": total_usage},
            "top_documents": insights[:limit],
        }

    async def get_activity_timeline(
        self, *, window_minutes: int = 60, bucket_minutes: int = 5
    ) -> Dict[str, Any]:
        """Return bucketed activity metrics for charts."""
        bucket_minutes = max(bucket_minutes, 1)
        events, updated_at = await self._collect_window(window_minutes)

        if not events:
            return {
                "status": "initializing",
                "updated_at": updated_at.isoformat(),
                "window_minutes": window_minutes,
                "bucket_size_minutes": bucket_minutes,
                "buckets": [],
            }

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=window_minutes)
        buckets: List[Dict[str, Any]] = []

        bucket_start = start_time
        while bucket_start < end_time:
            bucket_end = bucket_start + timedelta(minutes=bucket_minutes)
            bucket_events = [
                event for event in events if bucket_start <= event.timestamp < bucket_end
            ]

            if bucket_events:
                durations = [event.response_time_ms for event in bucket_events]
                avg_duration = sum(durations) / len(durations)
                cache_hits = sum(1 for event in bucket_events if event.cache_hit)
                cache_rate = cache_hits / len(bucket_events)
                error_count = sum(1 for event in bucket_events if not event.successful)
            else:
                avg_duration = 0.0
                cache_rate = 0.0
                error_count = 0

            buckets.append(
                {
                    "start": bucket_start.isoformat(),
                    "end": bucket_end.isoformat(),
                    "total_queries": len(bucket_events),
                    "avg_response_time_ms": round(avg_duration, 2),
                    "cache_hit_rate": round(cache_rate, 4),
                    "error_count": error_count,
                }
            )

            bucket_start = bucket_end

        return {
            "status": "ok",
            "updated_at": updated_at.isoformat(),
            "window_minutes": window_minutes,
            "bucket_size_minutes": bucket_minutes,
            "buckets": buckets,
        }

    async def get_health(self) -> Dict[str, Any]:
        """Provide a lightweight health snapshot."""
        live_metrics = await self.get_live_metrics()
        totals = live_metrics["totals"]

        return {
            "status": live_metrics["status"],
            "updated_at": live_metrics["updated_at"],
            "tracked_queries": totals["queries"],
            "cache_hit_rate": totals["cache_hit_rate"],
        }

    async def reset(self) -> None:
        """Clear all recorded events."""
        async with self._lock:
            self._events.clear()
            self._updated_at = datetime.utcnow()

    async def _collect_window(self, window_minutes: int) -> Tuple[List[QueryEvent], datetime]:
        window_start = datetime.utcnow() - timedelta(minutes=window_minutes)

        async with self._lock:
            events = [event for event in self._events if event.timestamp >= window_start]
            updated_at = self._updated_at if self._events else datetime.utcnow()

        return events, updated_at

    def _prune_expired(self) -> None:
        cutoff = datetime.utcnow() - self._retention
        while self._events and self._events[0].timestamp < cutoff:
            self._events.popleft()

    @staticmethod
    def _percentile(values: Sequence[float], percentile: float) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(round((len(sorted_values) - 1) * percentile))
        index = min(max(index, 0), len(sorted_values) - 1)
        return sorted_values[index]

    @staticmethod
    def _determine_status(
        *, average_response_ms: float, failure_ratio: float, cache_hit_rate: float
    ) -> str:
        if failure_ratio >= 0.4:
            return "error"
        if failure_ratio > 0.1 or average_response_ms > 4000 or cache_hit_rate < 0.3:
            return "degraded"
        return "ok"

    @staticmethod
    def _max_datetime(current: Optional[datetime], candidate: datetime) -> datetime:
        if current is None:
            return candidate
        return candidate if candidate > current else current

    def _empty_live_payload(self, window_minutes: int, updated_at: datetime) -> Dict[str, Any]:
        return {
            "status": "initializing",
            "window_minutes": window_minutes,
            "updated_at": updated_at.isoformat(),
            "totals": {
                "queries": 0,
                "successful": 0,
                "failed": 0,
                "cache_hit_rate": 0.0,
            },
            "latency": {
                "average_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
            },
            "quality": {
                "avg_relevance": 0.0,
                "avg_sources_per_query": 0.0,
                "unique_sources": 0,
            },
        }


_rag_metrics_service: Optional[RAGMetricsService] = None


async def get_rag_metrics_service() -> RAGMetricsService:
    global _rag_metrics_service
    if _rag_metrics_service is None:
        _rag_metrics_service = RAGMetricsService()
    return _rag_metrics_service
