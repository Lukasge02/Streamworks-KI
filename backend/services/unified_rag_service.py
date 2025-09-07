"""
Unified RAG Service - Consolidated RAG Pipeline
Combines the best features from all RAG implementations into a single, optimized service
"""

import asyncio
import time
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple, Literal
from openai import AsyncOpenAI
from datetime import datetime
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass

from config import settings
from .vectorstore import VectorStoreService
from .embeddings import EmbeddingService
from .ollama_service import OllamaLLMAdapter, create_ollama_service

logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    """Unified configuration for RAG operations"""
    # Performance settings
    confidence_threshold: float = 0.7
    top_k: int = 6
    max_sources: int = 6
    min_chunk_relevance: float = 0.5
    
    # LLM settings
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 2000
    
    # Cache settings
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Processing mode
    processing_mode: Literal["fast", "accurate", "comprehensive"] = "accurate"


class UnifiedRAGService:
    """
    Unified RAG Service that consolidates:
    - RAG Pipeline (basic functionality)
    - Optimized RAG Pipeline (performance optimizations)
    - QA Pipeline (structured responses with confidence)
    - XML RAG Service (specialized for XML/StreamWorks)
    """
    
    def __init__(self, 
                 vectorstore: VectorStoreService, 
                 embeddings: EmbeddingService,
                 config: Optional[RAGConfig] = None):
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.config = config or RAGConfig()
        
        # Initialize LLM clients based on provider setting
        self.llm_provider = settings.LOCAL_LLM_PROVIDER
        self.fallback_enabled = settings.LLM_FALLBACK_ENABLED
        
        logger.info(f"🤖 LLM Provider: {self.llm_provider}, Fallback: {self.fallback_enabled}")
        
        # Ollama client (PRIMARY for local LLM)
        if self.llm_provider == "ollama":
            try:
                ollama_service = create_ollama_service(settings.OLLAMA_BASE_URL)
                self.ollama_client = OllamaLLMAdapter(ollama_service, settings.OLLAMA_MODEL)
                logger.info(f"✅ Ollama client initialized with model: {settings.OLLAMA_MODEL}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Ollama: {str(e)}")
                self.ollama_client = None
        else:
            self.ollama_client = None
        
        # OpenAI client (for fallback or when explicitly requested)
        if settings.OPENAI_API_KEY and (self.llm_provider == "openai" or (self.fallback_enabled and self.ollama_client is None)):
            try:
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized as fallback")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI: {str(e)}")
                self.openai_client = None
        else:
            self.openai_client = None
        
        # Cache for performance optimization
        self._query_cache = {}
        self._embedding_cache = {}
        
        logger.info(f"Initialized UnifiedRAGService with LLM provider: {self.llm_provider}, fallback: {self.fallback_enabled}")
    
    async def query(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        mode: Optional[Literal["fast", "accurate", "comprehensive"]] = None,
        include_sources: bool = True,
        enable_rerank: bool = False
    ) -> Dict[str, Any]:
        """
        Unified RAG query method that adapts based on processing mode
        
        Args:
            query: User question
            filters: Optional metadata filters
            mode: Processing mode override
            include_sources: Whether to include source citations
            enable_rerank: Enable reranking for better results
            
        Returns:
            Dict with answer, confidence, sources, and metadata
        """
        start_time = time.time()
        processing_mode = mode or self.config.processing_mode
        
        try:
            # Step 1: Check cache if enabled
            if self.config.enable_caching:
                cached_result = await self._check_cache(query, filters)
                if cached_result:
                    cached_result["response_time"] = time.time() - start_time
                    cached_result["from_cache"] = True
                    return cached_result
            
            # Step 2: Retrieve relevant documents
            retrieval_results = await self._retrieve_documents(
                query, filters, processing_mode
            )
            
            # Step 3: Generate response based on mode
            if processing_mode == "fast":
                response = await self._fast_generate(query, retrieval_results)
            elif processing_mode == "comprehensive":
                response = await self._comprehensive_generate(query, retrieval_results, enable_rerank)
            else:  # accurate (default)
                response = await self._accurate_generate(query, retrieval_results)
            
            # Step 4: Add metadata and sources
            result = {
                "answer": response["answer"],
                "confidence": response.get("confidence", 0.8),
                "sources": retrieval_results["sources"] if include_sources else [],
                "processing_mode": processing_mode,
                "response_time": time.time() - start_time,
                "from_cache": False,
                "metadata": {
                    "retrieved_chunks": len(retrieval_results["chunks"]),
                    "total_tokens": response.get("total_tokens", 0),
                    "model_used": self.config.model_name
                }
            }
            
            # Cache result if enabled
            if self.config.enable_caching:
                await self._cache_result(query, filters, result)
            
            return result
            
        except Exception as e:
            logger.error(f"RAG query failed: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error processing your question.",
                "confidence": 0.0,
                "sources": [],
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    async def _retrieve_documents(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]], 
        mode: str
    ) -> Dict[str, Any]:
        """Retrieve relevant documents based on processing mode"""
        
        # Adjust top_k based on mode
        if mode == "fast":
            top_k = max(3, self.config.top_k // 2)
        elif mode == "comprehensive":
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
        
        # Extract chunks and sources
        chunks = []
        sources = set()
        
        for result in search_results:
            chunks.append({
                "content": result.get("content", ""),
                "score": result.get("similarity_score", 0.0),
                "metadata": result.get("metadata", {})
            })
            
            # Extract source information
            metadata = result.get("metadata", {})
            if metadata.get("source_file"):
                sources.add(metadata["source_file"])
        
        return {
            "chunks": chunks,
            "sources": list(sources)[:self.config.max_sources]
        }
    
    async def _fast_generate(self, query: str, retrieval_results: Dict[str, Any]) -> Dict[str, Any]:
        """Fast generation mode - optimized for speed"""
        
        context = "\n".join([
            chunk["content"] for chunk in retrieval_results["chunks"][:3]
        ])
        
        # German prompt for better local model performance
        prompt = f"""Basierend auf dem folgenden Kontext, beantworte die Frage präzise und auf Deutsch:

Kontext:
{context}

Frage: {query}

Antwort:"""
        
        try:
            # FORCE Ollama first when provider is set to ollama
            if self.llm_provider == "ollama" and self.ollama_client:
                logger.info("🚀 Using Ollama for fast generation")
                messages = [{"role": "user", "content": prompt}]
                response = await self.ollama_client.create_chat_completion(
                    messages=messages,
                    temperature=0.1,
                    max_tokens=500
                )
                
                logger.info(f"✅ Ollama fast response: {response.usage.total_tokens} tokens")
                
                return {
                    "answer": response.choices[0].message.content,
                    "confidence": 0.7,
                    "total_tokens": response.usage.total_tokens,
                    "model_used": f"{settings.OLLAMA_MODEL} (local-fast)"
                }
            
            # Fallback to OpenAI if available
            elif self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=500
                )
                
                return {
                    "answer": response.choices[0].message.content,
                    "confidence": 0.7,
                    "total_tokens": response.usage.total_tokens,
                    "model_used": "gpt-3.5-turbo"
                }
            else:
                return {
                    "answer": "Entschuldigung, kein LLM-Service verfügbar.",
                    "confidence": 0.0,
                    "total_tokens": 0,
                    "model_used": "none"
                }
                
        except Exception as e:
            logger.error(f"Fast generation failed: {str(e)}")
            # Try fallback if enabled
            if self.fallback_enabled and self.openai_client and self.ollama_client:
                try:
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                        max_tokens=500
                    )
                    
                    return {
                        "answer": response.choices[0].message.content,
                        "confidence": 0.6,  # Lower confidence for fallback
                        "total_tokens": response.usage.total_tokens,
                        "model_used": "gpt-3.5-turbo (fallback)"
                    }
                except Exception as fallback_error:
                    logger.error(f"Fallback generation also failed: {str(fallback_error)}")
            
            return {
                "answer": f"Entschuldigung, es gab einen Fehler bei der Antwortgenerierung: {str(e)}",
                "confidence": 0.0,
                "total_tokens": 0,
                "model_used": "error"
            }
    
    async def _accurate_generate(self, query: str, retrieval_results: Dict[str, Any]) -> Dict[str, Any]:
        """Accurate generation mode - balanced speed and quality"""
        
        context = "\n\n".join([
            f"Quelle {i+1}: {chunk['content']}"
            for i, chunk in enumerate(retrieval_results["chunks"])
        ])
        
        # German system prompt for better local model performance
        system_prompt = "Du bist ein hilfsreicher Assistent, der Fragen basierend auf bereitgestelltem Kontext beantwortet. Antworte immer auf Deutsch und nutze die Informationen aus dem Kontext."
        
        user_prompt = f"""Kontext:
{context}

Frage: {query}

Bitte gib eine umfassende Antwort basierend auf dem Kontext. Falls der Kontext nicht genügend Informationen enthält, sage das klar.

Antwort:"""
        
        try:
            # FORCE Ollama first when provider is set to ollama
            if self.llm_provider == "ollama" and self.ollama_client:
                logger.info("🤖 Using Ollama for RAG generation")
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                
                response = await self.ollama_client.create_chat_completion(
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                # Simple confidence estimation based on context relevance
                if retrieval_results["chunks"]:
                    avg_score = sum(chunk["score"] for chunk in retrieval_results["chunks"]) / len(retrieval_results["chunks"])
                    confidence = min(0.95, max(0.3, avg_score))
                else:
                    confidence = 0.1  # Low confidence when no context found
                
                logger.info(f"✅ Ollama response generated successfully with {response.usage.total_tokens} tokens")
                
                return {
                    "answer": response.choices[0].message.content,
                    "confidence": confidence,
                    "total_tokens": response.usage.total_tokens,
                    "model_used": f"{settings.OLLAMA_MODEL} (local)"
                }
            
            # Fallback to OpenAI if Ollama fails or provider is openai
            elif self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                if retrieval_results["chunks"]:
                    avg_score = sum(chunk["score"] for chunk in retrieval_results["chunks"]) / len(retrieval_results["chunks"])
                    confidence = min(0.95, max(0.3, avg_score))
                else:
                    confidence = 0.1  # Low confidence when no context found
                
                return {
                    "answer": response.choices[0].message.content,
                    "confidence": confidence,
                    "total_tokens": response.usage.total_tokens,
                    "model_used": self.config.model_name
                }
            else:
                return {
                    "answer": "Entschuldigung, kein LLM-Service verfügbar.",
                    "confidence": 0.0,
                    "total_tokens": 0,
                    "model_used": "none"
                }
                
        except Exception as e:
            logger.error(f"❌ Ollama generation failed: {str(e)}")
            # Try fallback ONLY if explicitly enabled and Ollama was the primary choice
            if self.fallback_enabled and self.openai_client and self.llm_provider == "ollama":
                try:
                    logger.warning("🔄 Falling back to OpenAI due to Ollama error")
                    response = await self.openai_client.chat.completions.create(
                        model=self.config.model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens
                    )
                    
                    avg_score = sum(chunk["score"] for chunk in retrieval_results["chunks"]) / len(retrieval_results["chunks"])
                    confidence = min(0.90, max(0.2, avg_score))  # Slightly lower for fallback
                    
                    return {
                        "answer": response.choices[0].message.content,
                        "confidence": confidence,
                        "total_tokens": response.usage.total_tokens,
                        "model_used": f"{self.config.model_name} (openai-fallback)"
                    }
                except Exception as fallback_error:
                    logger.error(f"❌ OpenAI fallback also failed: {str(fallback_error)}")
            
            return {
                "answer": f"Entschuldigung, es gab einen Fehler bei der Antwortgenerierung: {str(e)}",
                "confidence": 0.0,
                "total_tokens": 0,
                "model_used": "error"
            }
    
    async def _comprehensive_generate(
        self, 
        query: str, 
        retrieval_results: Dict[str, Any], 
        enable_rerank: bool
    ) -> Dict[str, Any]:
        """Comprehensive generation mode - highest quality"""
        
        chunks = retrieval_results["chunks"]
        
        # Optional reranking for better results
        if enable_rerank and len(chunks) > 3:
            chunks = await self._rerank_chunks(query, chunks)
        
        context = "\n\n".join([
            f"Source {i+1} (Relevance: {chunk['score']:.2f}): {chunk['content']}"
            for i, chunk in enumerate(chunks)
        ])
        
        prompt = f"""You are an expert assistant that provides detailed, accurate answers based on provided sources.

Context Sources:
{context}

Question: {query}

Please provide a comprehensive answer that:
1. Directly addresses the question
2. Uses information from the most relevant sources
3. Indicates if any information is uncertain or missing
4. Maintains accuracy and clarity

Answer:"""
        
        response = await self.llm_client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": "You are a knowledgeable assistant providing accurate, source-based answers."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        # More sophisticated confidence estimation
        avg_score = sum(chunk["score"] for chunk in chunks) / len(chunks)
        num_high_relevance = sum(1 for chunk in chunks if chunk["score"] > 0.7)
        confidence = min(0.95, max(0.4, avg_score * (1 + num_high_relevance * 0.1)))
        
        return {
            "answer": response.choices[0].message.content,
            "confidence": confidence,
            "total_tokens": response.usage.total_tokens
        }
    
    async def _rerank_chunks(self, query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple reranking based on keyword matching (placeholder for more advanced reranking)"""
        # This is a simplified version - in production, use a proper reranking model
        query_words = set(query.lower().split())
        
        def relevance_score(chunk):
            content_words = set(chunk["content"].lower().split())
            overlap = len(query_words.intersection(content_words))
            return chunk["score"] + (overlap * 0.1)  # Boost score for keyword overlap
        
        return sorted(chunks, key=relevance_score, reverse=True)
    
    async def _check_cache(self, query: str, filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check if query result is cached"""
        cache_key = self._generate_cache_key(query, filters)
        
        if cache_key in self._query_cache:
            cached_item = self._query_cache[cache_key]
            
            # Check if cache is still valid
            if time.time() - cached_item["timestamp"] < self.config.cache_ttl:
                return cached_item["result"]
            else:
                # Remove expired cache entry
                del self._query_cache[cache_key]
        
        return None
    
    async def _cache_result(self, query: str, filters: Optional[Dict[str, Any]], result: Dict[str, Any]):
        """Cache query result"""
        cache_key = self._generate_cache_key(query, filters)
        
        # Don't cache error results
        if "error" not in result:
            self._query_cache[cache_key] = {
                "result": result,
                "timestamp": time.time()
            }
            
            # Simple cache cleanup - remove oldest entries if cache gets too large
            if len(self._query_cache) > 1000:  # Max 1000 cached queries
                oldest_key = min(self._query_cache.keys(), 
                               key=lambda k: self._query_cache[k]["timestamp"])
                del self._query_cache[oldest_key]
    
    def _generate_cache_key(self, query: str, filters: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for query and filters"""
        cache_data = {
            "query": query.lower().strip(),
            "filters": filters or {},
            "config": {
                "top_k": self.config.top_k,
                "model": self.config.model_name,
                "mode": self.config.processing_mode
            }
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        return {
            "cached_queries": len(self._query_cache),
            "cache_memory_mb": sum(
                len(json.dumps(item["result"]).encode()) 
                for item in self._query_cache.values()
            ) / (1024 * 1024),
            "config": {
                "cache_enabled": self.config.enable_caching,
                "cache_ttl": self.config.cache_ttl,
                "processing_mode": self.config.processing_mode
            }
        }
    
    def clear_cache(self):
        """Clear query cache"""
        self._query_cache.clear()
        logger.info("RAG query cache cleared")


# Factory function for easy instantiation
async def create_unified_rag_service(
    vectorstore: VectorStoreService,
    embeddings: EmbeddingService,
    processing_mode: Literal["fast", "accurate", "comprehensive"] = "accurate"
) -> UnifiedRAGService:
    """Create and configure UnifiedRAGService"""
    config = RAGConfig(processing_mode=processing_mode)
    return UnifiedRAGService(vectorstore, embeddings, config)