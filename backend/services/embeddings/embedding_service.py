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
from .cache_manager import EmbeddingCacheManager
from config import settings

# Import DocumentChunk for compatibility
from ..docling_ingest import DocumentChunk

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Local Gamma embedding service with performance caching"""
    
    def __init__(self):
        # Configuration - force to gamma only
        self.provider = EmbeddingProvider.GAMMA
        
        # Initialize local embedder
        self.local_embedder = None
        
        # Setup local embedder
        try:
            self.local_embedder = LocalGammaEmbedder()
        except Exception as e:
            logger.error(f"Local embedder initialization failed: {e}")
            raise EmbeddingException(f"Failed to initialize local embedder: {e}")
        
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
            "local_embeddings": 0
        }
        
        logger.info(f"EmbeddingService initialized with local Gamma provider: {self.provider.value}")
    
    async def initialize(self) -> None:
        """Initialize embedding service"""
        if self.local_embedder:
            await self.local_embedder.initialize()
            logger.info("Local Gamma embedder initialized successfully")
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
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
        
        logger.info(f"Embedding {len(chunks)} chunks using local Gamma provider")
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
                new_embeddings = await self._embed_with_local(texts_to_embed)
                
                # Cache new embeddings
                for text, embedding in zip(texts_to_embed, new_embeddings):
                    self.cache_manager.cache_embedding(text, embedding)
                    
            except Exception as e:
                logger.error(f"Local embedding generation failed: {e}")
                raise EmbeddingException(f"Failed to generate embeddings: {e}")
        
        # Assign embeddings to chunks
        embedding_idx = 0
        for i, chunk in enumerate(chunks):
            if i in cached_embeddings:
                embedding = cached_embeddings[i]
            else:
                embedding = new_embeddings[embedding_idx]
                embedding_idx += 1
            
            # Add embedding to chunk (compatible with VectorStore expectations)
            if isinstance(chunk, DocumentChunk):
                chunk.embedding = embedding
                # Also add to metadata for VectorStore compatibility
                if not hasattr(chunk, 'metadata'):
                    chunk.metadata = {}
                chunk.metadata['embedding'] = embedding
            elif isinstance(chunk, dict):
                # Ensure metadata exists
                if 'metadata' not in chunk:
                    chunk['metadata'] = {}
                # Store embedding in metadata for VectorStore
                chunk['metadata']['embedding'] = embedding
                # Also store directly for backward compatibility
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
            if not self.local_embedder:
                raise EmbeddingException("Local embedder not initialized")
            
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self.local_embedder.embed_query_sync, 
                query
            )
            self.stats["local_embeddings"] += 1
            
            # Cache the embedding
            self.cache_manager.cache_embedding(query, embedding)
            self.stats["total_embeddings"] += 1
            return embedding
                
        except Exception as e:
            logger.error(f"Local query embedding failed: {e}")
            raise EmbeddingException(f"Failed to generate query embedding: {e}")
    
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
                "total_embeddings": self.stats["total_embeddings"],
                "local_embeddings": self.stats["local_embeddings"]
            },
            "cache": cache_stats
        }