"""
Dependency Injection Container for StreamWorks Backend
Provides centralized service management and proper dependency injection
"""

import logging
from typing import Dict, Any, Type, TypeVar, Generic, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceLifecycle(ABC):
    """Base class for services with lifecycle management"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass


class ServiceConfig:
    """Configuration for service registration"""
    
    def __init__(self, 
                 service_class: Type,
                 singleton: bool = True,
                 factory: Optional[Callable] = None,
                 dependencies: Optional[list] = None):
        self.service_class = service_class
        self.singleton = singleton
        self.factory = factory
        self.dependencies = dependencies or []


class DIContainer:
    """Dependency Injection Container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._configs: Dict[str, ServiceConfig] = {}
        self._initialized = False
        
    def register(self, 
                 name: str, 
                 service_class: Type,
                 singleton: bool = True,
                 factory: Optional[Callable] = None,
                 dependencies: Optional[list] = None):
        """Register a service with the container"""
        self._configs[name] = ServiceConfig(
            service_class=service_class,
            singleton=singleton,
            factory=factory,
            dependencies=dependencies
        )
        logger.info(f"Registered service: {name}")
    
    async def get(self, name: str) -> Any:
        """Get a service instance"""
        config = self._configs.get(name)
        if not config:
            raise ValueError(f"Service {name} not registered")
        
        if config.singleton and name in self._services:
            return self._services[name]
        
        # Create instance
        if config.factory:
            # If factory is a coroutine function, await it
            if asyncio.iscoroutinefunction(config.factory):
                # Resolve dependencies for factory
                deps = {}
                for dep_name in config.dependencies:
                    deps[dep_name] = await self.get(dep_name)
                instance = await config.factory(**deps)
            else:
                # Resolve dependencies for factory
                deps = {}
                for dep_name in config.dependencies:
                    deps[dep_name] = await self.get(dep_name)
                instance = config.factory(**deps)
        else:
            # Resolve dependencies
            deps = {}
            for dep_name in config.dependencies:
                deps[dep_name] = await self.get(dep_name)
            
            instance = config.service_class(**deps)
        
        # Initialize if it's a lifecycle service
        if isinstance(instance, ServiceLifecycle):
            await instance.initialize()
        
        if config.singleton:
            self._services[name] = instance
        
        return instance
    
    async def _initialize_all(self):
        """Initialize all registered services"""
        logger.info("Initializing dependency injection container")
        
        # Initialize in dependency order
        initialized = set()
        
        for name in list(self._configs.keys()):
            if name not in initialized:
                await self._initialize_service(name, initialized)
        
        self._initialized = True
        logger.info("DI container initialized successfully")
    
    async def _initialize_service(self, name: str, initialized: set):
        """Initialize a service and its dependencies"""
        if name in initialized:
            return
        
        config = self._configs[name]
        
        # Initialize dependencies first
        for dep_name in config.dependencies:
            await self._initialize_service(dep_name, initialized)
        
        # Create and initialize the service
        instance = await self.get(name)
        initialized.add(name)
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for all services"""
        results = {}
        
        for name, instance in self._services.items():
            try:
                if isinstance(instance, ServiceLifecycle):
                    results[name] = await instance.health_check()
                else:
                    results[name] = {"status": "healthy"}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
        
        return results
    
    async def cleanup(self):
        """Cleanup all services"""
        logger.info("Cleaning up DI container")
        
        for name, instance in self._services.items():
            try:
                if isinstance(instance, ServiceLifecycle):
                    await instance.cleanup()
            except Exception as e:
                logger.error(f"Failed to cleanup service {name}: {e}")
        
        self._services.clear()
        self._initialized = False


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get the global DI container"""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


async def initialize_container():
    """Initialize the global container (Qdrant + LlamaIndex) with service pre-warming"""
    logger.info("🚀 Starting DI container initialization...")
    container = get_container()

    # Import available services (Qdrant + LlamaIndex architecture)
    logger.info("📦 Importing service modules...")
    try:
        from .ollama_service import OllamaService
        logger.info("✅ Successfully imported OllamaService")
    except ImportError as e:
        logger.error(f"❌ Failed to import OllamaService: {e}")
        raise

    try:
        from .qdrant_rag_service import get_rag_service
        logger.info("✅ Successfully imported get_rag_service")
    except ImportError as e:
        logger.error(f"❌ Failed to import get_rag_service: {e}")
        raise

    try:
        from .qdrant_vectorstore import get_qdrant_service
        logger.info("✅ Successfully imported get_qdrant_service")
    except ImportError as e:
        logger.error(f"❌ Failed to import get_qdrant_service: {e}")
        raise

    # Core infrastructure services that remain
    logger.info("🔧 Registering core services...")
    container.register(
        name="ollama_service",
        service_class=OllamaService,
        singleton=True
    )
    logger.info("✅ Registered ollama_service")

    # Qdrant Vector Store Service
    container.register(
        name="qdrant_service",
        service_class=None,
        factory=get_qdrant_service,
        singleton=True
    )
    logger.info("✅ Registered qdrant_service")

    # Qdrant RAG Service (main pipeline)
    container.register(
        name="rag_service",
        service_class=None,
        factory=get_rag_service,
        singleton=True
    )
    logger.info("✅ Registered rag_service")

    # Legacy services (keep for backward compatibility during transition)
    try:
        from .upload_job_manager_refactored import create_upload_job_manager
        container.register(
            name="upload_job_manager",
            service_class=None,
            factory=create_upload_job_manager,
            singleton=True
        )
        logger.info("✅ Registered upload_job_manager")
    except ImportError:
        logger.warning("⚠️ Upload job manager not available")

    # Initialize all services
    logger.info("🔄 Initializing all registered services...")
    try:
        await container._initialize_all()
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}", exc_info=True)
        raise

    # PRE-WARMING: Initialize critical services to reduce first query latency
    logger.info("🔥 Pre-warming critical services for improved performance...")
    try:
        # Pre-warm Qdrant vector store
        qdrant_service = await container.get("qdrant_service")
        await qdrant_service.initialize()
        logger.info("✅ Qdrant service pre-warmed successfully")

        # Pre-warm RAG service
        rag_service = await container.get("rag_service")
        await rag_service.initialize()
        logger.info("✅ RAG service pre-warmed successfully")

        # Pre-warm Unified RAG service (if available)
        try:
            from .rag.unified_rag_service import get_unified_rag_service
            unified_rag = await get_unified_rag_service()
            await unified_rag.initialize()
            logger.info("✅ Unified RAG service pre-warmed successfully")
        except Exception as e:
            logger.warning(f"⚠️ Unified RAG service pre-warming failed: {str(e)}")

        logger.info("🚀 Service pre-warming completed - first queries will be faster!")

    except Exception as e:
        logger.warning(f"⚠️ Service pre-warming partially failed: {str(e)} - Services will initialize on first use")


async def get_service(name: str) -> Any:
    """Get a service from the global container"""
    return await get_container().get(name)


async def cleanup_container():
    """Cleanup the global container"""
    global _container
    if _container:
        await _container.cleanup()
        _container = None