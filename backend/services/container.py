"""
Dependency Injection Container
Lightweight DI container for managing service instances.
"""

from typing import Dict, Any, Optional, TypeVar, Type
from functools import lru_cache

T = TypeVar("T")


class Container:
    """
    Simple Dependency Injection Container.

    Manages service instances with lazy initialization and singleton pattern.
    No external dependencies required.

    Usage:
        # Get a service instance
        vector_store = Container.get_vector_store()
        health_service = Container.get_health_service()

        # Override for testing
        Container.override("vector_store", mock_vector_store)
    """

    _instances: Dict[str, Any] = {}
    _overrides: Dict[str, Any] = {}
    _initialized: bool = False

    @classmethod
    def _get_or_create(cls, key: str, factory):
        """Get existing instance or create new one using factory"""
        # Check for test override first
        if key in cls._overrides:
            return cls._overrides[key]

        # Return existing instance if available
        if key in cls._instances:
            return cls._instances[key]

        # Create new instance
        instance = factory()
        cls._instances[key] = instance
        return instance

    @classmethod
    def get_vector_store(cls):
        """Get VectorStore singleton"""

        def factory():
            from services.rag.vector_store import VectorStore

            return VectorStore()

        return cls._get_or_create("vector_store", factory)

    @classmethod
    def get_db_service(cls):
        """Get DatabaseService singleton"""

        def factory():
            from services.db import DatabaseService

            return DatabaseService()

        return cls._get_or_create("db_service", factory)

    @classmethod
    def get_health_service(cls):
        """Get HealthService singleton"""

        def factory():
            from services.health_service import HealthService

            return HealthService()

        return cls._get_or_create("health_service", factory)

    @classmethod
    def get_document_service(cls):
        """Get DocumentService singleton"""

        def factory():
            from services.rag.document_service import DocumentService

            return DocumentService()

        return cls._get_or_create("document_service", factory)

    @classmethod
    def get_chat_session_service(cls):
        """Get ChatSessionService singleton"""

        def factory():
            from services.chat_session_service import ChatSessionService

            return ChatSessionService()

        return cls._get_or_create("chat_session_service", factory)



    @classmethod
    def override(cls, key: str, instance: Any):
        """
        Override a service instance (for testing).

        Args:
            key: Service key (e.g., "vector_store", "db_service")
            instance: Mock or alternative implementation
        """
        cls._overrides[key] = instance

    @classmethod
    def clear_overrides(cls):
        """Clear all test overrides"""
        cls._overrides.clear()

    @classmethod
    def reset(cls):
        """Reset all instances (useful for testing)"""
        cls._instances.clear()
        cls._overrides.clear()
        cls._initialized = False

    @classmethod
    def initialize(cls):
        """
        Initialize the container and wire up dependencies.
        Called once during application startup.
        """
        if cls._initialized:
            return

        # Get health service and configure it with clients
        health_service = cls.get_health_service()

        # Wire up Qdrant client
        try:
            vector_store = cls.get_vector_store()
            if hasattr(vector_store, "client"):
                health_service.set_qdrant_client(vector_store.client)
        except Exception as e:
            print(f"⚠️ Could not wire Qdrant client: {e}")

        # Wire up Supabase client
        try:
            db_service = cls.get_db_service()
            if db_service.client:
                health_service.set_supabase_client(db_service.client)
        except Exception as e:
            print(f"⚠️ Could not wire Supabase client: {e}")

        # Wire up MinIO client (if available)
        try:
            from services.rag.storage.file_storage import file_storage

            if file_storage and hasattr(file_storage, "client"):
                health_service.set_minio_client(file_storage.client)
        except Exception as e:
            print(f"⚠️ Could not wire MinIO client: {e}")

        cls._initialized = True
        print("✅ DI Container initialized")


# FastAPI Dependency functions
def get_vector_store():
    """FastAPI dependency for VectorStore"""
    return Container.get_vector_store()


def get_db_service():
    """FastAPI dependency for DatabaseService"""
    return Container.get_db_service()


def get_health_service():
    """FastAPI dependency for HealthService"""
    return Container.get_health_service()


def get_document_service():
    """FastAPI dependency for DocumentService"""
    return Container.get_document_service()





def get_chat_session_service():
    """FastAPI dependency for ChatSessionService"""
    return Container.get_chat_session_service()

