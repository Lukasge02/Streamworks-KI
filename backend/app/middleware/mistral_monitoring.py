"""
Mistral Performance Monitoring Middleware
Überwacht CPU, Memory und Response Times für Mistral 7B
"""
import time
import psutil
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class MistralPerformanceMiddleware(BaseHTTPMiddleware):
    """Mistral-spezifisches Performance Monitoring"""
    
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.request_count = 0
        self.total_response_time = 0.0
        self.mistral_requests = 0
        self.mistral_response_time = 0.0
        
        logger.info("📊 Mistral Performance Monitoring aktiviert")
    
    async def dispatch(self, request: Request, call_next):
        # Performance-Metriken vor Request
        start_time = time.time()
        cpu_before = psutil.cpu_percent(interval=None)
        memory_before = psutil.virtual_memory().percent
        
        # Request verarbeiten
        response = await call_next(request)
        
        # Performance-Metriken nach Request
        process_time = time.time() - start_time
        cpu_after = psutil.cpu_percent(interval=None)
        memory_after = psutil.virtual_memory().percent
        
        # Statistiken aktualisieren
        self.request_count += 1
        self.total_response_time += process_time
        
        # Mistral-spezifische Metriken für Chat-Requests
        if "/chat" in str(request.url) or "/api/v1/chat" in str(request.url):
            self.mistral_requests += 1
            self.mistral_response_time += process_time
            
            # Detailliertes Logging für Mistral-Requests
            logger.info(f"""
=== MISTRAL PERFORMANCE ===
🎯 Request: {request.method} {request.url.path}
⏱️  Response Time: {process_time:.2f}s
🖥️  CPU Usage: {cpu_before:.1f}% → {cpu_after:.1f}%
💾 Memory Usage: {memory_before:.1f}% → {memory_after:.1f}%
🤖 Model: mistral:7b-instruct
📊 Total Mistral Requests: {self.mistral_requests}
📈 Avg Mistral Response: {self.mistral_response_time/self.mistral_requests:.2f}s
""")
            
            # Performance-Warnungen
            if process_time > 10.0:
                logger.warning(f"⚠️ Langsame Mistral-Antwort: {process_time:.2f}s")
            
            if cpu_after > 90:
                logger.warning(f"⚠️ Hohe CPU-Auslastung: {cpu_after:.1f}%")
            
            if memory_after > 85:
                logger.warning(f"⚠️ Hohe Memory-Auslastung: {memory_after:.1f}%")
        
        # Performance-Header hinzufügen
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-CPU-Usage"] = f"{cpu_before:.1f}->{cpu_after:.1f}%"
        response.headers["X-Memory-Usage"] = f"{memory_before:.1f}->{memory_after:.1f}%"
        
        return response
    
    def get_metrics(self) -> dict:
        """Aktuelle Performance-Metriken"""
        
        avg_response_time = self.total_response_time / self.request_count if self.request_count > 0 else 0
        avg_mistral_time = self.mistral_response_time / self.mistral_requests if self.mistral_requests > 0 else 0
        
        # Aktuelle System-Metriken
        current_cpu = psutil.cpu_percent(interval=0.1)
        current_memory = psutil.virtual_memory().percent
        
        return {
            "total_requests": self.request_count,
            "mistral_requests": self.mistral_requests,
            "avg_response_time": round(avg_response_time, 2),
            "avg_mistral_response_time": round(avg_mistral_time, 2),
            "current_cpu_percent": round(current_cpu, 1),
            "current_memory_percent": round(current_memory, 1),
            "mistral_performance_rating": self._calculate_performance_rating(avg_mistral_time, current_cpu, current_memory)
        }
    
    def _calculate_performance_rating(self, avg_time: float, cpu: float, memory: float) -> str:
        """Berechne Performance-Rating für Mistral"""
        
        # Performance-Score basierend auf Antwortzeit, CPU und Memory
        time_score = 100 if avg_time <= 3 else max(0, 100 - (avg_time - 3) * 20)
        cpu_score = max(0, 100 - cpu)
        memory_score = max(0, 100 - memory)
        
        total_score = (time_score + cpu_score + memory_score) / 3
        
        if total_score >= 80:
            return "excellent"
        elif total_score >= 60:
            return "good"
        elif total_score >= 40:
            return "fair"
        else:
            return "poor"
    
    def reset_metrics(self):
        """Metriken zurücksetzen"""
        self.request_count = 0
        self.total_response_time = 0.0
        self.mistral_requests = 0
        self.mistral_response_time = 0.0
        logger.info("📊 Mistral Performance Metriken zurückgesetzt")