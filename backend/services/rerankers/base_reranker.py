"""
Abstract Base Reranker Interface
Defines common interface for all reranking implementations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RerankedResult:
    """Represents a reranked search result with score"""
    content: str
    metadata: Dict[str, Any]
    original_score: float
    rerank_score: float
    rank_position: int
    
    @property
    def combined_score(self) -> float:
        """Combined score considering both similarity and rerank scores"""
        # Weighted combination: 70% rerank, 30% original
        return 0.7 * self.rerank_score + 0.3 * self.original_score


@dataclass
class RerankRequest:
    """Request object for reranking operation"""
    query: str
    documents: List[Dict[str, Any]]
    top_k: Optional[int] = None
    metadata_fields: Optional[List[str]] = None


@dataclass
class RerankResponse:
    """Response object from reranking operation"""
    results: List[RerankedResult]
    total_processed: int
    processing_time_ms: float
    provider: str
    model_info: Optional[Dict[str, Any]] = None


class BaseReranker(ABC):
    """
    Abstract base class for all reranker implementations.
    
    This interface ensures consistency across different reranking providers
    (local cross-encoders, Cohere, etc.) while allowing for provider-specific
    optimizations and features.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize reranker with configuration
        
        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config or {}
        self.is_initialized = False
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the reranker (load models, setup connections, etc.)"""
        pass
    
    @abstractmethod
    async def rerank(self, request: RerankRequest) -> RerankResponse:
        """
        Rerank documents based on query relevance
        
        Args:
            request: RerankRequest containing query and documents
            
        Returns:
            RerankResponse with ranked results and metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if reranker is available and functional"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name (e.g., 'local', 'cohere')"""
        pass
    
    @property
    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        """Get information about the underlying model"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check and return status information
        
        Returns:
            Dict containing health status and diagnostic information
        """
        try:
            is_available = self.is_available()
            return {
                "status": "healthy" if is_available else "unhealthy",
                "provider": self.provider_name,
                "initialized": self.is_initialized,
                "available": is_available,
                "model_info": self.model_info,
                "config": {k: "***" if "key" in k.lower() or "token" in k.lower() 
                          else v for k, v in self.config.items()}
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": self.provider_name,
                "error": str(e),
                "initialized": self.is_initialized
            }
    
    def _extract_content(self, document: Dict[str, Any]) -> str:
        """
        Extract text content from document for reranking
        
        Args:
            document: Document dictionary with various possible content fields
            
        Returns:
            Extracted text content
        """
        # Try different common content fields
        content_fields = ['content', 'text', 'document', 'chunk', 'body']
        
        for field in content_fields:
            if field in document and document[field]:
                return str(document[field])
        
        # Fallback: concatenate all string values
        text_parts = []
        for key, value in document.items():
            if isinstance(value, str) and len(value.strip()) > 0:
                text_parts.append(value.strip())
        
        return " ".join(text_parts) if text_parts else ""
    
    def _extract_metadata(
        self, 
        document: Dict[str, Any], 
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract relevant metadata from document
        
        Args:
            document: Source document
            fields: Specific metadata fields to extract (None for all)
            
        Returns:
            Extracted metadata dictionary
        """
        if fields is None:
            # Return all non-content fields
            content_fields = {'content', 'text', 'document', 'chunk', 'body'}
            return {k: v for k, v in document.items() if k not in content_fields}
        else:
            # Return only specified fields
            return {k: document.get(k) for k in fields if k in document}
    
    async def batch_rerank(
        self, 
        requests: List[RerankRequest]
    ) -> List[RerankResponse]:
        """
        Process multiple rerank requests in batch
        
        Args:
            requests: List of RerankRequest objects
            
        Returns:
            List of RerankResponse objects
        """
        responses = []
        for request in requests:
            response = await self.rerank(request)
            responses.append(response)
        return responses
    
    async def cleanup(self) -> None:
        """Clean up resources (optional override for providers that need it)"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider_name})"