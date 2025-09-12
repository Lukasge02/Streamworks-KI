"""
Base classes and interfaces for embedding services
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class EmbeddingProvider(str, Enum):
    """Available embedding providers"""
    GAMMA = "gamma"
    OPENAI = "openai"
    HYBRID = "hybrid"


@dataclass
class EmbeddingConfig:
    """Configuration for embedding services"""
    provider: EmbeddingProvider = EmbeddingProvider.GAMMA
    model_name: Optional[str] = None
    batch_size: int = 32
    max_tokens: int = 8191
    enable_fallback: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds


class EmbeddingException(Exception):
    """Base exception for embedding errors"""
    pass


class EmbeddingInterface(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def embed_texts(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            **kwargs: Additional provider-specific arguments
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    async def embed_query(self, query: str, **kwargs) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Query text to embed
            **kwargs: Additional provider-specific arguments
            
        Returns:
            Query embedding vector
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the embedding provider"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass