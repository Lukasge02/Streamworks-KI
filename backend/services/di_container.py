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
    """Initialize the global container"""
    container = get_container()
    
    # Register core services
    from .upload_job_manager_refactored import create_upload_job_manager
    from .unified_rag_service import create_unified_rag_service
    from .rag.rag_coordinator import create_openai_rag_service
    from .vectorstore import VectorStoreService
    from .embeddings import EmbeddingService
    
    # Register upload job manager
    container.register(
        name="upload_job_manager",
        service_class=None,  # Using factory
        factory=create_upload_job_manager,
        singleton=True
    )
    
    # Register vector store
    container.register(
        name="vectorstore",
        service_class=VectorStoreService,
        singleton=True
    )
    
    # Register embeddings
    container.register(
        name="embeddings",
        service_class=EmbeddingService,
        singleton=True
    )
    
    # Register OpenAI RAG service
    container.register(
        name="openai_rag_service",
        service_class=None,  # Using factory with dependencies
        factory=lambda vectorstore, embeddings: create_openai_rag_service(
            vectorstore_service=vectorstore,
            embeddings_service=embeddings
        ),
        singleton=True,
        dependencies=["vectorstore", "embeddings"]
    )
    
    # Register unified RAG service
    container.register(
        name="unified_rag_service",
        service_class=None,  # Using factory
        factory=create_unified_rag_service,
        singleton=True
    )
    
    await container._initialize_all()


async def get_service(name: str) -> Any:
    """Get a service from the global container"""
    return await get_container().get(name)


async def cleanup_container():
    """Cleanup the global container"""
    global _container
    if _container:
        await _container.cleanup()
        _container = None