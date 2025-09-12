"""
Main embedding service orchestrator with hybrid support
"""
import logging
import asyncio
import time
from typing import List, Optional, Dict, Any, Union
import numpy as np

from .base import EmbeddingProvider, EmbeddingConfig, EmbeddingException
from .local_embedder import LocalGammaEmbedder
from .openai_embedder import OpenAIEmbedder
from .cache_manager import EmbeddingCacheManager
from config import settings

# Import DocumentChunk for compatibility
from ..docling_ingest import DocumentChunk

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Hybrid embedding service with local Gamma and OpenAI support with performance caching"""
    
    def __init__(self):
        # Configuration
        self.provider = EmbeddingProvider(getattr(settings, 'EMBEDDING_PROVIDER', 'gamma'))
        self.enable_fallback = getattr(settings, 'ENABLE_EMBEDDING_FALLBACK', True)
        
        # Initialize embedders
        self.local_embedder = None
        self.openai_embedder = None
        
        # Setup OpenAI embedder
        self.openai_embedder = OpenAIEmbedder(
            api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL
        )
        
        # Setup local embedder if available
        try:
            self.local_embedder = LocalGammaEmbedder()
        except Exception as e:
            logger.warning(f"Local embedder not available: {e}")
            if self.provider == EmbeddingProvider.GAMMA:
                logger.warning("Falling back to OpenAI provider")
                self.provider = EmbeddingProvider.OPENAI
        
        # Cache manager
        self.cache_manager = EmbeddingCacheManager(
            max_cache_size=10000,
            cache_ttl=3600,
            semantic_cache_size=1000
        )
        
        # Statistics
        self.stats = {
            "total_embeddings": 0,
            "cache_hits": 0,
            "local_embeddings": 0,
            "openai_embeddings": 0,
            "fallback_count": 0
        }
        
        logger.info(f"EmbeddingService initialized with provider: {self.provider.value}")
    
    async def initialize(self) -> None:
        """Initialize embedding service"""
        if self.openai_embedder:
            await self.openai_embedder.initialize()
        
        if self.local_embedder:
            try:
                await self.local_embedder.initialize()
            except Exception as e:
                logger.warning(f"Local embedder initialization failed: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.openai_embedder:
            await self.openai_embedder.cleanup()
        
        if self.local_embedder:
            await self.local_embedder.cleanup()
        
        self.cache_manager.clear_cache()
    
    def _enhance_text_for_embedding(self, chunk: Union[DocumentChunk, Dict[str, Any]]) -> str:
        """
        Enhance text with metadata for better embedding quality
        
        Args:
            chunk: Document chunk or dictionary with text and metadata
            
        Returns:
            Enhanced text string
        """
        if isinstance(chunk, DocumentChunk):
            text = chunk.text
            metadata = chunk.metadata or {}
        elif isinstance(chunk, dict):
            text = chunk.get('text', '')
            metadata = chunk.get('metadata', {})
        else:
            return str(chunk)
        
        # Build enhanced text with relevant metadata
        enhanced_parts = []
        
        # Add document type if available
        doc_type = metadata.get('doc_type', '')
        if doc_type:
            enhanced_parts.append(f"[{doc_type.upper()}]")
        
        # Add title if available
        title = metadata.get('title', '')
        if title:
            enhanced_parts.append(f"Title: {title}")
        
        # Add section header if available
        section = metadata.get('section', '')
        if section:
            enhanced_parts.append(f"Section: {section}")
        
        # Add the main text
        enhanced_parts.append(text)
        
        # Add keywords if available
        keywords = metadata.get('keywords', [])
        if keywords:
            enhanced_parts.append(f"Keywords: {', '.join(keywords)}")
        
        return "\n".join(enhanced_parts)
    
    async def embed_chunks(self, chunks: List[Union[DocumentChunk, Dict[str, Any]]]) -> List[Union[DocumentChunk, Dict[str, Any]]]:
        """
        Create embeddings for document chunks with caching and enhancement
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Chunks with embeddings added
        """
        if not chunks:
            return chunks
        
        logger.info(f"Embedding {len(chunks)} chunks using {self.provider.value} provider")
        start_time = time.time()
        
        # Prepare texts and check cache
        texts_to_embed = []
        cached_embeddings = {}
        chunk_indices = []
        
        for i, chunk in enumerate(chunks):
            # Enhance text for better embeddings
            enhanced_text = self._enhance_text_for_embedding(chunk)
            
            # Check cache
            cached = self.cache_manager.get_cached_embedding(enhanced_text)
            if cached:
                cached_embeddings[i] = cached
                self.stats["cache_hits"] += 1
            else:
                texts_to_embed.append(enhanced_text)
                chunk_indices.append(i)
        
        # Generate new embeddings if needed
        new_embeddings = []
        if texts_to_embed:
            try:
                if self.provider == EmbeddingProvider.GAMMA:
                    new_embeddings = await self._embed_with_local(texts_to_embed)
                elif self.provider == EmbeddingProvider.OPENAI:
                    new_embeddings = await self._embed_with_openai(texts_to_embed)
                else:  # HYBRID
                    # Try local first, fallback to OpenAI
                    try:
                        new_embeddings = await self._embed_with_local(texts_to_embed)
                    except Exception as e:
                        logger.warning(f"Local embedding failed, using OpenAI: {e}")
                        new_embeddings = await self._embed_with_openai(texts_to_embed)
                        self.stats["fallback_count"] += 1
                
                # Cache new embeddings
                for text, embedding in zip(texts_to_embed, new_embeddings):
                    self.cache_manager.cache_embedding(text, embedding)
                    
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                # Generate temporary embeddings as fallback
                new_embeddings = [await self._generate_temp_embedding(text) for text in texts_to_embed]
        
        # Assign embeddings to chunks
        embedding_idx = 0
        for i, chunk in enumerate(chunks):
            if i in cached_embeddings:
                embedding = cached_embeddings[i]
            else:
                embedding = new_embeddings[embedding_idx]
                embedding_idx += 1
            
            # Add embedding to chunk
            if isinstance(chunk, DocumentChunk):
                chunk.embedding = embedding
            elif isinstance(chunk, dict):
                chunk['embedding'] = embedding
            
            self.stats["total_embeddings"] += 1
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Embedded {len(chunks)} chunks in {elapsed:.2f}s (cache hits: {len(cached_embeddings)})")
        
        return chunks
    
    async def _embed_with_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model"""
        if not self.local_embedder:
            raise EmbeddingException("Local embedder not available")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def run_local_embedding():
            return self.local_embedder.embed_texts_sync(texts)
        
        embeddings = await loop.run_in_executor(None, run_local_embedding)
        self.stats["local_embeddings"] += len(embeddings)
        return embeddings
    
    async def _embed_with_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        if not self.openai_embedder:
            raise EmbeddingException("OpenAI embedder not configured")
        
        # Use retry logic for rate limiting
        embeddings = await self.openai_embedder.embed_texts_with_retry(texts)
        self.stats["openai_embeddings"] += len(embeddings)
        return embeddings
    
    async def _generate_temp_embedding(self, text: str) -> List[float]:
        """
        Generate temporary embedding as fallback
        Uses simple hashing for consistent results
        """
        import hashlib
        
        # Create deterministic embedding from text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Generate 1536-dimensional embedding (OpenAI dimension)
        embedding = []
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i:i+2]
            value = int(hex_pair, 16) / 255.0 - 0.5  # Normalize to [-0.5, 0.5]
            embedding.append(value)
        
        # Pad or truncate to correct dimension
        target_dim = 1536
        if len(embedding) < target_dim:
            # Repeat pattern to fill
            while len(embedding) < target_dim:
                embedding.extend(embedding[:min(len(embedding), target_dim - len(embedding))])
        else:
            embedding = embedding[:target_dim]
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = (np.array(embedding) / norm).tolist()
        
        logger.warning("Generated temporary embedding as fallback")
        return embedding
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Create embedding for a search query with caching
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
        """
        # Check cache first
        cached = self.cache_manager.get_cached_embedding(query)
        if cached:
            self.stats["cache_hits"] += 1
            return cached
        
        try:
            embedding = None
            
            if self.provider == EmbeddingProvider.GAMMA:
                if self.local_embedder:
                    loop = asyncio.get_event_loop()
                    embedding = await loop.run_in_executor(
                        None, 
                        self.local_embedder.embed_query_sync, 
                        query
                    )
                    self.stats["local_embeddings"] += 1
                elif self.enable_fallback and self.openai_embedder:
                    embedding = await self.openai_embedder.embed_query(query)
                    self.stats["openai_embeddings"] += 1
                    self.stats["fallback_count"] += 1
                    
            elif self.provider == EmbeddingProvider.OPENAI:
                if self.openai_embedder:
                    embedding = await self.openai_embedder.embed_query(query)
                    self.stats["openai_embeddings"] += 1
                    
            else:  # HYBRID
                # Try local first
                if self.local_embedder:
                    try:
                        loop = asyncio.get_event_loop()
                        embedding = await loop.run_in_executor(
                            None,
                            self.local_embedder.embed_query_sync,
                            query
                        )
                        self.stats["local_embeddings"] += 1
                    except Exception as e:
                        logger.warning(f"Local query embedding failed: {e}")
                        if self.openai_embedder:
                            embedding = await self.openai_embedder.embed_query(query)
                            self.stats["openai_embeddings"] += 1
                            self.stats["fallback_count"] += 1
                elif self.openai_embedder:
                    embedding = await self.openai_embedder.embed_query(query)
                    self.stats["openai_embeddings"] += 1
            
            if embedding:
                # Cache the embedding
                self.cache_manager.cache_embedding(query, embedding)
                self.stats["total_embeddings"] += 1
                return embedding
            else:
                # Fallback to temporary embedding
                embedding = await self._generate_temp_embedding(query)
                self.stats["total_embeddings"] += 1
                return embedding
                
        except Exception as e:
            logger.error(f"Query embedding failed: {e}")
            # Generate temporary embedding as last resort
            embedding = await self._generate_temp_embedding(query)
            self.stats["total_embeddings"] += 1
            return embedding
    
    def get_embedding(self, query: str) -> List[float]:
        """
        Synchronous wrapper for embed_query (for backward compatibility)
        
        Args:
            query: Query text
            
        Returns:
            Query embedding vector
        """
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.embed_query(query))
        finally:
            loop.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        cache_stats = self.cache_manager.get_statistics()
        
        return {
            "service": {
                "provider": self.provider.value,
                "fallback_enabled": self.enable_fallback,
                "total_embeddings": self.stats["total_embeddings"],
                "local_embeddings": self.stats["local_embeddings"],
                "openai_embeddings": self.stats["openai_embeddings"],
                "fallback_count": self.stats["fallback_count"]
            },
            "cache": cache_stats
        }