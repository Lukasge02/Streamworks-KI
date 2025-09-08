"""
Unified RAG Service for StreamWorks
Consolidates OpenAI and XML RAG functionality into a single, maintainable service
"""

import time
import json
import logging
from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

from openai import AsyncOpenAI
from datetime import datetime

from .di_container import ServiceLifecycle
from .vectorstore import VectorStoreService
from .embeddings import EmbeddingService
from config import settings

logger = logging.getLogger(__name__)


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
    
    # RAG type
    rag_type: RAGType = RAGType.DOCUMENT


class RAGServiceInterface(ABC):
    """Interface for RAG services"""
    
    @abstractmethod
    async def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Process a RAG query"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        pass


class OpenAIRAGService(RAGServiceInterface, ServiceLifecycle):
    """
    OpenAI-based RAG Service for document queries
    Clean, focused implementation using OpenAI for generation
    """
    
    def __init__(self, 
                 vectorstore: VectorStoreService,
                 embeddings: EmbeddingService,
                 config: Optional[RAGConfig] = None):
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.config = config or RAGConfig()
        self._initialized = False
        
        # Initialize OpenAI client
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY ist erforderlich für OpenAI RAG Service")
        
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def initialize(self) -> None:
        """Initialize the service"""
        if self._initialized:
            return
            
        logger.info("Initializing OpenAI RAG Service")
        
        # Ensure dependencies are initialized
        if hasattr(self.vectorstore, 'initialize') and callable(getattr(self.vectorstore, 'initialize')):
            await self.vectorstore.initialize()
        
        if hasattr(self.embeddings, 'initialize') and callable(getattr(self.embeddings, 'initialize')):
            await self.embeddings.initialize()
        
        self._initialized = True
        logger.info("OpenAI RAG Service initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            # Test OpenAI connection
            openai_healthy = False
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                openai_healthy = True
            except Exception as e:
                logger.error(f"OpenAI health check failed: {str(e)}")
            
            # Test embedding service
            embedding_healthy = False
            try:
                await self.embeddings.embed_query("test")
                embedding_healthy = True
            except Exception as e:
                logger.error(f"Embedding health check failed: {str(e)}")
            
            # Test vectorstore
            vectorstore_healthy = False
            try:
                test_embedding = [0.1] * 1024
                await self.vectorstore.search_similar(
                    query_embedding=test_embedding,
                    top_k=1
                )
                vectorstore_healthy = True
            except Exception as e:
                logger.error(f"Vectorstore health check failed: {str(e)}")
            
            return {
                "status": "healthy" if (openai_healthy and embedding_healthy and vectorstore_healthy) else "unhealthy",
                "openai": "connected" if openai_healthy else "disconnected",
                "embeddings": "ready" if embedding_healthy else "not ready",
                "vectorstore": "ready" if vectorstore_healthy else "not ready",
                "config": {
                    "model": self.config.model_name,
                    "rag_type": self.config.rag_type.value,
                    "top_k": self.config.top_k
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        logger.info("Cleaning up OpenAI RAG Service")
        self._initialized = False
    
    async def query(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        mode: Optional[RAGMode] = None,
        include_sources: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process RAG query with OpenAI generation
        
        Args:
            query: User question
            filters: Optional metadata filters
            mode: Processing mode
            include_sources: Include source citations
            
        Returns:
            Dict with answer, confidence, sources, and metadata
        """
        start_time = time.time()
        processing_mode = mode or self.config.processing_mode
        
        try:
            # Step 1: Retrieve relevant documents
            retrieval_results = await self._retrieve_documents(query, filters, processing_mode)
            
            # Step 2: Generate response with OpenAI
            generation_result = await self._generate_response(query, retrieval_results, processing_mode)
            
            # Step 3: Package result
            result = {
                "answer": generation_result["answer"],
                "confidence": generation_result["confidence"],
                "sources": retrieval_results["sources"] if include_sources else [],
                "processing_mode": processing_mode.value,
                "response_time": time.time() - start_time,
                "metadata": {
                    "retrieved_chunks": len(retrieval_results["chunks"]),
                    "total_tokens": generation_result.get("total_tokens", 0),
                    "model_used": generation_result["model_used"],
                    "embedding_model": "EmbeddingGemma",
                    "rag_type": self.config.rag_type.value
                }
            }
            
            logger.info(f"✅ RAG Query erfolgreich - {result['response_time']:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ RAG Query failed: {str(e)}")
            return {
                "answer": "Entschuldigung, es gab einen Fehler bei der Verarbeitung Ihrer Anfrage.",
                "confidence": 0.0,
                "sources": [],
                "error": str(e),
                "response_time": time.time() - start_time,
                "metadata": {"model_used": "error"}
            }
    
    async def _retrieve_documents(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        mode: RAGMode
    ) -> Dict[str, Any]:
        """Retrieve relevant documents using EmbeddingGemma"""
        
        # Adjust retrieval based on mode
        if mode == RAGMode.FAST:
            top_k = max(3, self.config.top_k // 2)
        elif mode == RAGMode.COMPREHENSIVE:
            top_k = min(15, self.config.top_k * 2)
        else:
            top_k = self.config.top_k
        
        # Get query embedding
        query_embedding = await self.embeddings.embed_query(query)
        
        # Search vector store
        search_results = await self.vectorstore.search_similar(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        # Process results
        chunks = []
        sources = []
        
        for result in search_results:
            # Skip low-relevance chunks
            similarity_score = result.get("similarity_score", 0.0)
            if similarity_score < self.config.similarity_threshold:
                continue
                
            chunks.append({
                "content": result.get("content", ""),
                "score": similarity_score,
                "metadata": result.get("metadata", {})
            })
            
            # Extract source information
            metadata = result.get("metadata", {})
            source_info = {
                "id": result.get("id", ""),
                "source_file": metadata.get("original_filename", metadata.get("source_file", "Unknown")),
                "page_number": metadata.get("page_number"),
                "heading": metadata.get("heading"),
                "similarity_score": similarity_score,
                "content_preview": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", ""),
                "metadata": metadata
            }
            sources.append(source_info)
        
        # Limit sources
        sources = sources[:self.config.max_sources]
        
        logger.info(f"🔍 Retrieval: {len(chunks)} chunks gefunden, {len(sources)} sources")
        
        return {
            "chunks": chunks,
            "sources": sources
        }
    
    async def _generate_response(
        self,
        query: str,
        retrieval_results: Dict[str, Any],
        mode: RAGMode
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        
        chunks = retrieval_results["chunks"]
        
        if not chunks:
            return {
                "answer": "Entschuldigung, ich konnte keine relevanten Informationen in den verfügbaren Dokumenten finden.",
                "confidence": 0.1,
                "total_tokens": 0,
                "model_used": self.config.model_name
            }
        
        # Build context from chunks
        if mode == RAGMode.FAST:
            context = "\\n".join([chunk["content"] for chunk in chunks[:3]])
            max_tokens = min(1000, self.config.max_tokens)
        elif mode == RAGMode.COMPREHENSIVE:
            context = "\\n\\n".join([
                f"Quelle {i+1} (Relevanz: {chunk['score']:.2f}):\\n{chunk['content']}"
                for i, chunk in enumerate(chunks)
            ])
            max_tokens = min(3000, self.config.max_tokens * 1.5)
        else:  # accurate
            context = "\\n\\n".join([
                f"Quelle {i+1}:\\n{chunk['content']}"
                for i, chunk in enumerate(chunks[:6])
            ])
            max_tokens = self.config.max_tokens
        
        # Create messages for OpenAI
        system_prompt = """Du bist ein hilfsreicher Assistent für StreamWorks, der Fragen basierend auf bereitgestelltem Kontext beantwortet.

WICHTIGE REGELN:
1. Antworte immer auf Deutsch
2. Nutze NUR die Informationen aus dem bereitgestellten Kontext
3. Wenn der Kontext nicht ausreicht, sage das klar
4. Gib strukturierte, klare Antworten
5. Verweise auf relevante Quellen wenn möglich
6. Sei präzise und hilfreich"""

        user_prompt = f"""Kontext aus StreamWorks Dokumentation:

{context}

Frage: {query}

Bitte beantworte die Frage basierend auf dem Kontext. Falls nicht genügend Informationen vorhanden sind, sage das ehrlich."""
        
        try:
            # Call OpenAI
            response = await self.openai_client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=max_tokens
            )
            
            # Calculate confidence
            avg_score = sum(chunk["score"] for chunk in chunks) / len(chunks)
            high_relevance_count = sum(1 for chunk in chunks if chunk["score"] > 0.7)
            confidence = min(0.95, max(0.3, avg_score + (high_relevance_count * 0.1)))
            
            logger.info(f"✅ OpenAI Response: {response.usage.total_tokens} tokens, confidence: {confidence:.2f}")
            
            return {
                "answer": response.choices[0].message.content,
                "confidence": confidence,
                "total_tokens": response.usage.total_tokens,
                "model_used": self.config.model_name
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI generation failed: {str(e)}")
            raise Exception(f"OpenAI generation failed: {str(e)}")


class UnifiedRAGService:
    """
    Unified RAG service that provides a single interface for all RAG operations
    Routes queries to appropriate specialized RAG services
    """
    
    def __init__(self):
        self._services: Dict[RAGType, RAGServiceInterface] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all RAG services"""
        if self._initialized:
            return
            
        logger.info("Initializing Unified RAG Service")
        
        # Initialize OpenAI RAG service
        vectorstore = VectorStoreService()
        await vectorstore.initialize()
        
        embeddings = EmbeddingService()
        await embeddings.initialize()
        
        openai_rag = OpenAIRAGService(vectorstore, embeddings)
        await openai_rag.initialize()
        
        self._services[RAGType.DOCUMENT] = openai_rag
        
        # Note: XML RAG service would be initialized here if needed
        # self._services[RAGType.XML_TEMPLATE] = xml_rag_service
        
        self._initialized = True
        logger.info("Unified RAG Service initialized successfully")
    
    async def query(
        self,
        query: str,
        rag_type: RAGType = RAGType.DOCUMENT,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a RAG query using the appropriate service
        
        Args:
            query: The query to process
            rag_type: Type of RAG processing to use
            **kwargs: Additional arguments for the specific RAG service
            
        Returns:
            RAG response with answer, sources, and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        service = self._services.get(rag_type)
        if not service:
            raise ValueError(f"RAG service for type {rag_type} not available")
        
        return await service.query(query, **kwargs)
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for all RAG services"""
        results = {}
        
        for rag_type, service in self._services.items():
            try:
                results[rag_type.value] = await service.health_check()
            except Exception as e:
                results[rag_type.value] = {"status": "unhealthy", "error": str(e)}
        
        overall_status = "healthy" if all(
            result.get("status") == "healthy" 
            for result in results.values()
        ) else "unhealthy"
        
        return {
            "status": overall_status,
            "services": results,
            "available_types": list(self._services.keys())
        }
    
    async def cleanup(self) -> None:
        """Cleanup all services"""
        logger.info("Cleaning up Unified RAG Service")
        
        for service in self._services.values():
            if hasattr(service, 'cleanup'):
                await service.cleanup()
        
        self._services.clear()
        self._initialized = False


# Factory functions for dependency injection
def create_unified_rag_service() -> UnifiedRAGService:
    """Factory function to create UnifiedRAGService instance"""
    return UnifiedRAGService()


def create_openai_rag_service(
    vectorstore: VectorStoreService,
    embeddings: EmbeddingService,
    config: Optional[RAGConfig] = None
) -> OpenAIRAGService:
    """Factory function to create OpenAIRAGService instance"""
    return OpenAIRAGService(vectorstore, embeddings, config)