"""
Dependency Injection Container for StreamWorks-KI
Manages service lifecycle and dependencies
"""
from typing import Dict, Type, TypeVar, Optional, Any, Callable
import asyncio
import logging
from contextlib import asynccontextmanager

from app.core.base_service import BaseService, ServiceStatus, ServiceInitializationError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseService)


class ServiceContainer:
    """
    Dependency injection container for managing service lifecycle
    
    Features:
    - Singleton service management
    - Automatic dependency resolution
    - Graceful shutdown handling
    - Health monitoring
    """
    
    def __init__(self):
        self._services: Dict[Type[BaseService], BaseService] = {}
        self._factories: Dict[Type[BaseService], Callable[[], BaseService]] = {}
        self._dependencies: Dict[Type[BaseService], list] = {}
        self._initialization_order: list = []
        self._is_shutting_down = False
        
    def register_service(
        self, 
        service_type: Type[T], 
        factory: Callable[[], T],
        dependencies: Optional[list] = None
    ) -> None:
        """Register a service factory with its dependencies"""
        self._factories[service_type] = factory
        self._dependencies[service_type] = dependencies or []
        logger.info(f"📋 Registered service: {service_type.__name__}")
        
    async def get_service(self, service_type: Type[T]) -> T:
        """Get or create a service instance"""
        if self._is_shutting_down:
            raise ServiceInitializationError("Container is shutting down")
            
        if service_type in self._services:
            service = self._services[service_type]
            if service.is_ready:
                return service
            elif service.status == ServiceStatus.ERROR:
                raise ServiceInitializationError(
                    f"Service {service_type.__name__} is in error state: {service.error_message}"
                )
        
        return await self._create_service(service_type)
    
    async def _create_service(self, service_type: Type[T]) -> T:
        """Create and initialize a service with its dependencies"""
        if service_type not in self._factories:
            raise ServiceInitializationError(f"Service {service_type.__name__} not registered")
        
        # Initialize dependencies first
        for dep_type in self._dependencies[service_type]:
            await self.get_service(dep_type)
        
        # Create service instance
        factory = self._factories[service_type]
        service = factory()
        
        if not isinstance(service, BaseService):
            raise ServiceInitializationError(
                f"Service {service_type.__name__} must inherit from BaseService"
            )
        
        # Store and initialize
        self._services[service_type] = service
        self._initialization_order.append(service_type)
        
        try:
            await service.initialize()
            logger.info(f"✅ Service initialized: {service_type.__name__}")
            return service
            
        except Exception as e:
            # Remove failed service
            self._services.pop(service_type, None)
            if service_type in self._initialization_order:
                self._initialization_order.remove(service_type)
            raise ServiceInitializationError(f"Failed to initialize {service_type.__name__}: {e}") from e
    
    async def shutdown_all(self) -> None:
        """Shutdown all services in reverse initialization order"""
        if self._is_shutting_down:
            return
            
        self._is_shutting_down = True
        logger.info("🛑 Starting service container shutdown")
        
        # Shutdown in reverse order
        for service_type in reversed(self._initialization_order):
            if service_type in self._services:
                service = self._services[service_type]
                try:
                    await service.cleanup()
                    logger.info(f"✅ Service shutdown: {service_type.__name__}")
                except Exception as e:
                    logger.error(f"❌ Failed to shutdown {service_type.__name__}: {e}")
        
        self._services.clear()
        self._initialization_order.clear()
        logger.info("🏁 Service container shutdown complete")
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        health_results = {
            "container_status": "healthy" if not self._is_shutting_down else "shutting_down",
            "total_services": len(self._services),
            "services": {}
        }
        
        for service_type, service in self._services.items():
            try:
                service_health = await service.health_check()
                health_results["services"][service_type.__name__] = service_health
            except Exception as e:
                health_results["services"][service_type.__name__] = {
                    "service": service_type.__name__,
                    "status": "error",
                    "error": str(e)
                }
        
        # Calculate overall health
        healthy_services = sum(
            1 for health in health_results["services"].values() 
            if health.get("is_ready", False)
        )
        
        health_results["healthy_services"] = healthy_services
        health_results["overall_health"] = (
            "healthy" if healthy_services == len(self._services) else "degraded"
        )
        
        return health_results
    
    @asynccontextmanager
    async def lifespan(self):
        """Context manager for service container lifecycle"""
        try:
            logger.info("🚀 Starting service container")
            yield self
        finally:
            await self.shutdown_all()
    
    def list_services(self) -> Dict[str, Any]:
        """List all registered and active services"""
        return {
            "registered_services": [t.__name__ for t in self._factories.keys()],
            "active_services": [t.__name__ for t in self._services.keys()],
            "initialization_order": [t.__name__ for t in self._initialization_order],
            "dependencies": {
                t.__name__: [d.__name__ for d in deps] 
                for t, deps in self._dependencies.items()
            }
        }


# Global service container instance
service_container = ServiceContainer()