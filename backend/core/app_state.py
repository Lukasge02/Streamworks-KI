"""
Shared Application State
Provides centralized access to application-wide state and services
"""

import threading
from typing import Dict, Any, Optional
from datetime import datetime

class AppState:
    """Centralized application state management"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.performance_middleware = None
        self.startup_time = datetime.utcnow()
        self._initialized = True
    
    def set_performance_middleware(self, middleware):
        """Set the performance middleware instance"""
        self.performance_middleware = middleware
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics from middleware"""
        if self.performance_middleware:
            return self.performance_middleware.get_performance_stats()
        return {
            "status": "middleware_not_available",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_slow_endpoints(self, threshold: float = 1.0) -> Dict[str, Any]:
        """Get slow endpoints from middleware"""
        if self.performance_middleware:
            return self.performance_middleware.get_slow_endpoints(threshold)
        return {
            "status": "middleware_not_available",
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return (datetime.utcnow() - self.startup_time).total_seconds()

# Global instance
app_state = AppState()