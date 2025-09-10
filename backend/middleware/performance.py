"""
Performance Monitoring Middleware für StreamWorks
Erfasst API-Performance-Metriken und optimiert Response-Times
"""

import time
import uuid
import logging
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import json

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Performance-Monitoring Middleware für API-Endpoints"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_stats = {}
        self.active_requests = {}
        self.global_stats = {
            "total_requests": 0,
            "total_errors": 0,
            "avg_response_time": 0.0,
            "p95_response_time": 0.0
        }
        
        # Register with app state
        try:
            from core.app_state import app_state
            app_state.set_performance_middleware(self)
        except ImportError:
            logger.warning("Could not register with app state - module not available")
    
    async def dispatch(self, request: Request, call_next):
        """Verarbeitet Requests und erfasst Performance-Metriken"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Request-ID für Tracing hinzufügen
        request.state.request_id = request_id
        
        # Request für Tracking registrieren
        self.active_requests[request_id] = {
            "start_time": start_time,
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        try:
            # Request verarbeiten
            response = await call_next(request)
            
            # Processing-Time berechnen
            processing_time = time.time() - start_time
            
            # Performance-Metriken erfassen
            await self._record_performance_metrics(
                request, response, processing_time, request_id
            )
            
            # Performance-Headers hinzufügen
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Error-Handling mit Performance-Tracking
            processing_time = time.time() - start_time
            self.global_stats["total_errors"] += 1
            
            logger.error(f"Request {request_id} failed after {processing_time:.3f}s: {str(e)}")
            
            # Error-Response mit Performance-Info
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "request_id": request_id,
                    "processing_time": f"{processing_time:.3f}s"
                }
            )
        
        finally:
            # Request aus Active-Tracking entfernen
            self.active_requests.pop(request_id, None)
    
    async def _record_performance_metrics(
        self, 
        request: Request, 
        response: Response, 
        processing_time: float,
        request_id: str
    ):
        """Erfasst Performance-Metriken für den Request"""
        
        # Endpoint identifizieren
        endpoint = f"{request.method} {request.url.path}"
        
        # Endpoint-spezifische Statistiken aktualisieren
        if endpoint not in self.request_stats:
            self.request_stats[endpoint] = {
                "count": 0,
                "total_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "errors": 0,
                "response_times": []
            }
        
        stats = self.request_stats[endpoint]
        stats["count"] += 1
        stats["total_time"] += processing_time
        stats["min_time"] = min(stats["min_time"], processing_time)
        stats["max_time"] = max(stats["max_time"], processing_time)
        
        # Response-Times für P95-Berechnung speichern (max 1000 Einträge)
        if len(stats["response_times"]) >= 1000:
            stats["response_times"].pop(0)
        stats["response_times"].append(processing_time)
        
        # Error-Tracking
        if response.status_code >= 400:
            stats["errors"] += 1
        
        # Globale Statistiken aktualisieren
        self.global_stats["total_requests"] += 1
        self.global_stats["avg_response_time"] = (
            self.global_stats["avg_response_time"] * (self.global_stats["total_requests"] - 1) + processing_time
        ) / self.global_stats["total_requests"]
        
        # Logging für langsame Requests
        if processing_time > 2.0:  # > 2 Sekunden
            logger.warning(f"Slow request detected: {endpoint} took {processing_time:.3f}s")
        
        # Logging für sehr schnelle Requests
        elif processing_time < 0.1:  # < 100ms
            logger.debug(f"Fast request: {endpoint} took {processing_time:.3f}s")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Gibt aktuelle Performance-Statistiken zurück"""
        
        # P95 für jeden Endpoint berechnen
        endpoint_stats = {}
        for endpoint, stats in self.request_stats.items():
            if stats["response_times"]:
                sorted_times = sorted(stats["response_times"])
                p95_index = int(len(sorted_times) * 0.95)
                p95_time = sorted_times[min(p95_index, len(sorted_times) - 1)]
            else:
                p95_time = 0.0
            
            endpoint_stats[endpoint] = {
                "count": stats["count"],
                "avg_time": stats["total_time"] / stats["count"] if stats["count"] > 0 else 0.0,
                "min_time": stats["min_time"] if stats["min_time"] != float('inf') else 0.0,
                "max_time": stats["max_time"],
                "p95_time": p95_time,
                "error_rate": (stats["errors"] / stats["count"] * 100) if stats["count"] > 0 else 0.0
            }
        
        # Globale P95 berechnen
        all_response_times = []
        for stats in self.request_stats.values():
            all_response_times.extend(stats["response_times"])
        
        if all_response_times:
            sorted_times = sorted(all_response_times)
            p95_index = int(len(sorted_times) * 0.95)
            global_p95 = sorted_times[min(p95_index, len(sorted_times) - 1)]
        else:
            global_p95 = 0.0
        
        return {
            "global_stats": {
                **self.global_stats,
                "p95_response_time": global_p95,
                "active_requests": len(self.active_requests)
            },
            "endpoint_stats": endpoint_stats,
            "active_requests": list(self.active_requests.values())
        }
    
    def get_slow_endpoints(self, threshold: float = 1.0) -> Dict[str, Any]:
        """Gibt langsame Endpoints zurück (basierend auf avg response time)"""
        
        slow_endpoints = {}
        for endpoint, stats in self.request_stats.items():
            if stats["count"] > 0:
                avg_time = stats["total_time"] / stats["count"]
                if avg_time > threshold:
                    slow_endpoints[endpoint] = {
                        "avg_time": avg_time,
                        "count": stats["count"],
                        "p95_time": sorted(stats["response_times"])[int(len(stats["response_times"]) * 0.95)] if stats["response_times"] else 0.0
                    }
        
        return slow_endpoints
    
    def reset_stats(self):
        """Setzt alle Performance-Statistiken zurück"""
        self.request_stats.clear()
        self.active_requests.clear()
        self.global_stats = {
            "total_requests": 0,
            "total_errors": 0,
            "avg_response_time": 0.0,
            "p95_response_time": 0.0
        }
        logger.info("Performance statistics reset")

class ResponseCompressionMiddleware:
    """Response-Komprimierung für bessere Performance"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Middleware für Response-Komprimierung"""
        
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Prüfen ob Komprimierung unterstützt wird
        accept_encoding = ""
        for header in scope.get("headers", []):
            if header[0].lower() == b"accept-encoding":
                accept_encoding = header[1].decode().lower()
                break
        
        if "gzip" not in accept_encoding:
            await self.app(scope, receive, send)
            return
        
        # Komprimierte Response senden
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append([b"content-encoding", b"gzip"])
                message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_wrapper)