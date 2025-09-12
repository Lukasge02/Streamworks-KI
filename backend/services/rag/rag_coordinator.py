"""
RAG coordinator and factory functions
"""
import logging
from typing import Dict, Any, Optional

from .models import RAGServiceInterface, RAGConfig
from .openai_rag import OpenAIRAGService
from ..di_container import get_container

logger = logging.getLogger(__name__)


class UnifiedRAGService:
    """
    Unified RAG service coordinator (deprecated pattern, kept for compatibility)
    Delegates to OpenAI RAG service
    """
    
    def __init__(self):
        self.openai_service = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the unified service"""
        if self._initialized:
            return
        
        try:
            # Get dependencies from container
            container = get_container()
            vectorstore = container.get("vectorstore")
            embeddings = container.get("embeddings")
            
            # Create OpenAI RAG service
            self.openai_service = OpenAIRAGService(
                vectorstore=vectorstore,
                embeddings=embeddings,
                config=RAGConfig()
            )
            
            await self.openai_service.initialize()
            self._initialized = True
            logger.info("Unified RAG Service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Unified RAG Service: {e}")
            raise
    
    async def query(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        mode: str = "accurate",
        include_sources: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process query using OpenAI RAG service
        
        Args:
            query: User question
            filters: Optional metadata filters
            mode: Processing mode ("fast", "accurate", "comprehensive")
            include_sources: Include source citations
            **kwargs: Additional arguments
            
        Returns:
            Dict with answer, confidence, sources, and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        # Convert string mode to enum if needed
        from .models import RAGMode
        if isinstance(mode, str):
            mode_map = {
                "fast": RAGMode.FAST,
                "accurate": RAGMode.ACCURATE,
                "comprehensive": RAGMode.COMPREHENSIVE
            }
            mode = mode_map.get(mode, RAGMode.ACCURATE)
        
        return await self.openai_service.query(
            query=query,
            filters=filters,
            mode=mode,
            include_sources=include_sources,
            **kwargs
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        if not self._initialized:
            return {"status": "unhealthy", "error": "Service not initialized"}
        
        return await self.openai_service.health_check()
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.openai_service:
            await self.openai_service.cleanup()
        self._initialized = False


def create_unified_rag_service() -> UnifiedRAGService:
    """
    Factory function to create unified RAG service
    
    Returns:
        UnifiedRAGService instance
    """
    return UnifiedRAGService()


def create_openai_rag_service(
    vectorstore_service=None,
    embeddings_service=None,
    config: Optional[RAGConfig] = None
) -> OpenAIRAGService:
    """
    Factory function to create OpenAI RAG service
    
    Args:
        vectorstore_service: Optional vectorstore service (will get from container if None)
        embeddings_service: Optional embeddings service (will get from container if None)
        config: Optional RAG configuration
        
    Returns:
        OpenAIRAGService instance
    """
    try:
        # Get dependencies from container if not provided
        if vectorstore_service is None or embeddings_service is None:
            container = get_container()
            vectorstore_service = vectorstore_service or container.get("vectorstore")
            embeddings_service = embeddings_service or container.get("embeddings")
        
        return OpenAIRAGService(
            vectorstore=vectorstore_service,
            embeddings=embeddings_service,
            config=config or RAGConfig()
        )
        
    except Exception as e:
        logger.error(f"Failed to create OpenAI RAG service: {e}")
        raise