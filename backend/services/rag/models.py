"""
RAG service models, enums, and interfaces
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum


class RAGMode(str, Enum):
    """RAG processing modes"""
    FAST = "fast"
    ACCURATE = "accurate"
    COMPREHENSIVE = "comprehensive"


class RAGType(str, Enum):
    """Types of RAG processing"""
    DOCUMENT = "document"      # Standard document RAG
    XML_TEMPLATE = "xml"       # XML template generation


@dataclass
class RAGConfig:
    """Configuration for RAG operations"""
    # Retrieval settings
    top_k: int = 6
    similarity_threshold: float = 0.1
    max_sources: int = 6
    
    # OpenAI settings
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 2000
    
    # Processing mode
    processing_mode: RAGMode = RAGMode.ACCURATE
    rag_type: RAGType = RAGType.DOCUMENT
    
    # Advanced settings
    use_adaptive_retrieval: bool = True
    reranking_enabled: bool = False
    context_window_size: int = 16000


class RAGServiceInterface(ABC):
    """Abstract base class for RAG services"""
    
    @abstractmethod
    async def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process a RAG query"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass