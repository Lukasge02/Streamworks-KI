"""
Base Service Interface for StreamWorks-KI
Provides consistent service lifecycle and interface patterns
"""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"


class StreamWorksError(Exception):
    """Base exception for StreamWorks-KI"""
    pass


class ServiceInitializationError(StreamWorksError):
    """Service initialization failed"""
    pass


class ServiceConfigurationError(StreamWorksError):
    """Service configuration error"""
    pass


class ServiceOperationError(StreamWorksError):
    """Service operation failed"""
    pass


class BaseService(ABC):
    """
    Abstract base class for all StreamWorks-KI services
    
    Provides:
    - Consistent initialization pattern
    - Standardized health checks
    - Proper cleanup mechanisms
    - Error handling patterns
    - Status tracking
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._status = ServiceStatus.UNINITIALIZED
        self._error_message: Optional[str] = None
        self._logger = logging.getLogger(f"{__name__}.{service_name}")
        
    @property
    def status(self) -> ServiceStatus:
        """Current service status"""
        return self._status
        
    @property 
    def is_ready(self) -> bool:
        """Check if service is ready for operations"""
        return self._status == ServiceStatus.READY
        
    @property
    def error_message(self) -> Optional[str]:
        """Last error message if service is in error state"""
        return self._error_message
    
    async def initialize(self) -> None:
        """Initialize the service"""
        if self._status != ServiceStatus.UNINITIALIZED:
            self._logger.warning(f"Service {self.service_name} already initialized")
            return
            
        self._status = ServiceStatus.INITIALIZING
        self._error_message = None
        
        try:
            self._logger.info(f"🔄 Initializing service: {self.service_name}")
            await self._initialize_impl()
            self._status = ServiceStatus.READY
            self._logger.info(f"✅ Service ready: {self.service_name}")
            
        except Exception as e:
            self._status = ServiceStatus.ERROR
            self._error_message = str(e)
            self._logger.error(f"❌ Service initialization failed: {self.service_name} - {e}")
            raise ServiceInitializationError(f"Failed to initialize {self.service_name}: {e}") from e
    
    async def cleanup(self) -> None:
        """Cleanup service resources"""
        if self._status == ServiceStatus.SHUTDOWN:
            return
            
        self._status = ServiceStatus.SHUTTING_DOWN
        
        try:
            self._logger.info(f"🧹 Cleaning up service: {self.service_name}")
            await self._cleanup_impl()
            self._status = ServiceStatus.SHUTDOWN
            self._logger.info(f"🛑 Service shutdown: {self.service_name}")
            
        except Exception as e:
            self._status = ServiceStatus.ERROR
            self._error_message = str(e)
            self._logger.error(f"❌ Service cleanup failed: {self.service_name} - {e}")
            raise ServiceOperationError(f"Failed to cleanup {self.service_name}: {e}") from e
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        base_health = {
            "service": self.service_name,
            "status": self._status.value,
            "is_ready": self.is_ready,
            "error_message": self._error_message
        }
        
        if self.is_ready:
            try:
                service_health = await self._health_check_impl()
                return {**base_health, **service_health}
            except Exception as e:
                self._logger.error(f"❌ Health check failed: {self.service_name} - {e}")
                return {
                    **base_health,
                    "health_check_error": str(e),
                    "is_healthy": False
                }
        
        return base_health
    
    # Abstract methods that must be implemented by subclasses
    
    @abstractmethod
    async def _initialize_impl(self) -> None:
        """Service-specific initialization logic"""
        pass
    
    @abstractmethod
    async def _cleanup_impl(self) -> None:
        """Service-specific cleanup logic"""
        pass
    
    @abstractmethod
    async def _health_check_impl(self) -> Dict[str, Any]:
        """Service-specific health check logic"""
        pass
    
    # Helper methods for subclasses
    
    def _ensure_ready(self) -> None:
        """Ensure service is ready for operations"""
        if not self.is_ready:
            raise ServiceOperationError(
                f"Service {self.service_name} is not ready. Status: {self._status.value}"
            )
    
    def _log_operation(self, operation: str, details: str = "") -> None:
        """Log service operation"""
        message = f"🔧 {self.service_name}: {operation}"
        if details:
            message += f" - {details}"
        self._logger.info(message)