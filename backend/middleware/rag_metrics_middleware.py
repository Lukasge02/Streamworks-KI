"""
RAG Metrics Tracking Middleware
Automatic performance tracking for all RAG-related endpoints
"""

import time
import json
import logging
from typing import Dict, Any, Optional, Set, List
from datetime import datetime
from fastapi import Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from services.rag_metrics_service import get_rag_metrics_service, SourceReference

logger = logging.getLogger(__name__)

class RAGMetricsMiddleware:
    """
    Middleware for automatic RAG performance tracking

    Features:
    - Automatic response time measurement
    - Source tracking extraction
    - Cache hit detection
    - Error tracking
    - No performance impact on non-RAG endpoints
    """

    def __init__(self):
        # Define RAG endpoints to track
        self.rag_endpoints: Set[str] = {
            "/api/chat",
            "/api/chat/send",
            "/api/chat/sessions/{session_id}/send",
            "/api/rag/query",
            "/api/langextract/sessions/{session_id}/messages",
            "/api/xml-chat/sessions/{session_id}/send"
        }

        # Cache detection patterns
        self.cache_hit_indicators = [
            "cache_hit",
            "cached_response",
            "from_cache"
        ]

        logger.info("🎯 RAG Metrics Middleware initialized")

    def is_rag_endpoint(self, path: str) -> bool:
        """Check if the endpoint should be tracked"""
        # Exact matches
        if path in self.rag_endpoints:
            return True

        # Pattern matches for dynamic routes
        rag_patterns = [
            "/api/chat/sessions/",
            "/api/rag/",
            "/api/langextract/",
            "/api/xml-chat/"
        ]

        return any(pattern in path for pattern in rag_patterns)

    async def __call__(self, request: Request, call_next) -> Response:
        """Process request and track RAG metrics"""

        # Debug logging
        print(f"🔍 Middleware processing: {request.url.path}")

        # Skip non-RAG endpoints for performance
        if not self.is_rag_endpoint(request.url.path):
            print(f"⏭️ Skipping non-RAG endpoint: {request.url.path}")
            return await call_next(request)

        print(f"📊 Tracking RAG endpoint: {request.url.path}")

        start_time = time.time()
        query_data = await self._extract_query_data(request)

        try:
            # Process request
            response = await call_next(request)

            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000

            # Track metrics only for successful RAG responses
            if response.status_code == 200:
                await self._track_rag_metrics(
                    request=request,
                    response=response,
                    query_data=query_data,
                    response_time_ms=response_time_ms
                )

            return response

        except Exception as e:
            # Track error metrics
            response_time_ms = (time.time() - start_time) * 1000
            await self._track_error_metrics(
                request=request,
                query_data=query_data,
                response_time_ms=response_time_ms,
                error=str(e)
            )
            raise e

    async def _extract_query_data(self, request: Request) -> Dict[str, Any]:
        """Extract query data from request"""
        try:
            # Clone request body for analysis
            body = await request.body()
            if not body:
                return {}

            # Parse JSON body
            try:
                data = json.loads(body.decode())
            except json.JSONDecodeError:
                return {}

            return {
                "query": data.get("query", data.get("message", "")),
                "mode": data.get("mode", "unknown"),
                "session_id": data.get("session_id"),
                "max_sources": data.get("max_sources"),
                "include_context": data.get("include_context", False)
            }

        except Exception as e:
            logger.debug(f"Failed to extract query data: {str(e)}")
            return {}

    async def _track_rag_metrics(
        self,
        request: Request,
        response: Response,
        query_data: Dict[str, Any],
        response_time_ms: float
    ) -> None:
        """Track successful RAG request metrics"""
        try:
            metrics_service = await get_rag_metrics_service()

            # Extract response data
            response_data = await self._extract_response_data(response)

            if not response_data:
                return

            # Extract sources
            sources = self._extract_sources(response_data)

            # Detect cache hit
            cache_hit = self._detect_cache_hit(response_data)

            # Extract session ID from URL or body
            session_id = self._extract_session_id(request, query_data)

            # Track the metrics
            await metrics_service.track_rag_query(
                query=query_data.get("query", ""),
                sources=sources,
                response_time_ms=response_time_ms,
                cache_hit=cache_hit,
                mode=query_data.get("mode", "accurate"),
                session_id=session_id
            )

            logger.debug(f"📊 Tracked RAG metrics: {len(sources)} sources, {response_time_ms:.1f}ms")

        except Exception as e:
            logger.error(f"❌ Failed to track RAG metrics: {str(e)}")

    async def _track_error_metrics(
        self,
        request: Request,
        query_data: Dict[str, Any],
        response_time_ms: float,
        error: str
    ) -> None:
        """Track failed RAG request metrics"""
        try:
            metrics_service = await get_rag_metrics_service()

            session_id = self._extract_session_id(request, query_data)

            await metrics_service.track_rag_query(
                query=query_data.get("query", ""),
                sources=[],  # No sources for failed requests
                response_time_ms=response_time_ms,
                cache_hit=False,
                mode=query_data.get("mode", "accurate"),
                session_id=session_id,
                error=error
            )

            logger.debug(f"📊 Tracked RAG error: {error}, {response_time_ms:.1f}ms")

        except Exception as e:
            logger.error(f"❌ Failed to track RAG error metrics: {str(e)}")

    async def _extract_response_data(self, response: Response) -> Optional[Dict[str, Any]]:
        """Extract data from response body"""
        try:
            # Handle different response types
            if isinstance(response, JSONResponse):
                return response.body
            elif isinstance(response, StreamingResponse):
                # Skip streaming responses for now
                return None
            elif hasattr(response, 'body'):
                try:
                    body_data = json.loads(response.body.decode())
                    return body_data
                except (json.JSONDecodeError, AttributeError):
                    return None

            return None

        except Exception as e:
            logger.debug(f"Failed to extract response data: {str(e)}")
            return None

    def _extract_sources(self, response_data: Dict[str, Any]) -> List[SourceReference]:
        """Extract source references from response data"""
        try:
            sources = []

            # Look for sources in different response structures
            source_data = None

            if "sources" in response_data:
                source_data = response_data["sources"]
            elif "data" in response_data and isinstance(response_data["data"], dict):
                source_data = response_data["data"].get("sources", [])
            elif "answer_data" in response_data:
                source_data = response_data["answer_data"].get("sources", [])

            if not source_data:
                return sources

            # Convert source data to SourceReference objects
            for source in source_data:
                if not isinstance(source, dict):
                    continue

                sources.append(SourceReference(
                    document_id=source.get("document_id", source.get("doc_id", "unknown")),
                    filename=source.get("filename", source.get("original_filename", "Unknown")),
                    page_number=source.get("page_number"),
                    section=source.get("section", source.get("heading")),
                    relevance_score=source.get("relevance_score", source.get("score", 0.0)),
                    snippet=source.get("snippet", source.get("content", ""))[:200],  # Truncate
                    chunk_index=source.get("chunk_index", source.get("index", 0)),
                    confidence=source.get("confidence", source.get("relevance_score", 0.0)),
                    doc_type=source.get("doc_type", source.get("type")),
                    chunk_id=source.get("chunk_id", source.get("id"))
                ))

            return sources

        except Exception as e:
            logger.debug(f"Failed to extract sources: {str(e)}")
            return []

    def _detect_cache_hit(self, response_data: Dict[str, Any]) -> bool:
        """Detect if response was served from cache"""
        try:
            # Convert response to string for pattern matching
            response_str = json.dumps(response_data).lower()

            # Check for cache hit indicators
            return any(indicator in response_str for indicator in self.cache_hit_indicators)

        except Exception:
            return False

    def _extract_session_id(self, request: Request, query_data: Dict[str, Any]) -> Optional[str]:
        """Extract session ID from request"""
        try:
            # From query data
            if query_data.get("session_id"):
                return query_data["session_id"]

            # From URL path
            path_parts = request.url.path.split("/")
            if "sessions" in path_parts:
                session_index = path_parts.index("sessions")
                if session_index + 1 < len(path_parts):
                    return path_parts[session_index + 1]

            # From query parameters
            return request.query_params.get("session_id")

        except Exception:
            return None


# Create middleware instance
rag_metrics_middleware = RAGMetricsMiddleware()

async def rag_metrics_middleware_func(request: Request, call_next):
    """FastAPI middleware function"""
    return await rag_metrics_middleware(request, call_next)