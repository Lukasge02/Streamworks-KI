"""
Enhanced Embedding Service with Query Enhancement - Phase 2
Extends the base embedding service with intelligent query preprocessing
"""

import logging
import asyncio
import time
from typing import List, Optional, Dict, Any, Union, Tuple

from .embedding_service import EmbeddingService
from ..query_enhancer import QueryEnhancer, EnhancedQuery
from ..multi_query_generator import MultiQueryGenerator, MultiQueryResult
from config import settings

logger = logging.getLogger(__name__)

class EnhancedEmbeddingService(EmbeddingService):
    """
    Enhanced embedding service with intelligent query preprocessing and multi-query support
    Extends the base EmbeddingService with Phase 2 improvements
    """
    
    def __init__(self):
        # Initialize base embedding service
        super().__init__()
        
        # Enhancement components
        self.query_enhancer = None
        self.multi_query_generator = None
        
        # Enhancement settings
        self.enable_query_enhancement = getattr(settings, 'ENABLE_QUERY_ENHANCEMENT', True)
        self.enable_multi_query = getattr(settings, 'ENABLE_MULTI_QUERY', True)
        self.max_query_variations = getattr(settings, 'MAX_QUERY_VARIATIONS', 3)
        
        # Enhancement statistics
        self.enhancement_stats = {
            "enhanced_queries": 0,
            "multi_queries_generated": 0,
            "avg_enhancement_time": 0.0,
            "similarity_improvements": []
        }
    
    async def initialize(self) -> None:
        """Initialize enhanced embedding service"""
        # Initialize base service
        await super().initialize()
        
        # Initialize enhancement components
        if self.enable_query_enhancement:
            logger.info("🚀 Initializing Query Enhancement...")
            self.query_enhancer = QueryEnhancer()
            await self.query_enhancer.initialize()
        
        if self.enable_multi_query:
            logger.info("🚀 Initializing Multi-Query Generation...")
            self.multi_query_generator = MultiQueryGenerator()
            await self.multi_query_generator.initialize()
        
        logger.info("✅ Enhanced Embedding Service initialized")
    
    async def embed_query_enhanced(
        self, 
        query: str, 
        use_enhancement: bool = True,
        use_multi_query: bool = False
    ) -> Union[List[float], Tuple[List[float], Dict[str, Any]]]:
        """
        Enhanced query embedding with preprocessing and optional multi-query
        
        Args:
            query: Original query text
            use_enhancement: Whether to apply query enhancement
            use_multi_query: Whether to generate multiple query variations
            
        Returns:
            Either just the embedding or (embedding, metadata) tuple
        """
        start_time = time.time()
        
        # Option 1: Use multi-query approach
        if use_multi_query and self.multi_query_generator:
            return await self._embed_with_multi_query(query)
        
        # Option 2: Use single enhanced query
        elif use_enhancement and self.query_enhancer:
            return await self._embed_with_enhancement(query)
        
        # Option 3: Fallback to base embedding
        else:
            return await self.embed_query(query)
    
    async def _embed_with_enhancement(self, query: str) -> Tuple[List[float], Dict[str, Any]]:
        """Embed query with enhancement preprocessing"""
        start_time = time.time()
        
        # Enhance the query
        enhanced = await self.query_enhancer.enhance_query(query)
        
        # Use the normalized query for embedding
        embedding = await self.embed_query(enhanced.normalized)
        
        # Calculate enhancement time
        enhancement_time = time.time() - start_time
        self.enhancement_stats["enhanced_queries"] += 1
        
        # Update average enhancement time
        current_avg = self.enhancement_stats["avg_enhancement_time"]
        total_enhanced = self.enhancement_stats["enhanced_queries"]
        new_avg = (current_avg * (total_enhanced - 1) + enhancement_time) / total_enhanced
        self.enhancement_stats["avg_enhancement_time"] = new_avg
        
        metadata = {
            "enhanced_query": enhanced,
            "enhancement_time": enhancement_time,
            "original_query": query,
            "normalized_query": enhanced.normalized,
            "query_language": enhanced.language.value,
            "query_type": enhanced.query_type.value,
            "confidence": enhanced.confidence,
            "synonyms_found": len(enhanced.synonyms),
            "alternatives_generated": len(enhanced.alternative_forms)
        }
        
        logger.debug(f"✅ Enhanced query embedding: '{query}' → '{enhanced.normalized}' ({enhancement_time:.3f}s)")
        
        return embedding, metadata
    
    async def _embed_with_multi_query(self, query: str) -> Tuple[List[float], Dict[str, Any]]:
        """Embed query using multi-query approach"""
        start_time = time.time()
        
        # Generate multiple query variations
        multi_result = await self.multi_query_generator.generate_multiple_queries(
            query, max_variations=self.max_query_variations
        )
        
        # Embed all query variations
        embedded_queries = []
        embeddings = []
        
        for query_var in multi_result.embedding_queries:
            embedding = await self.embed_query(query_var)
            embedded_queries.append(query_var)
            embeddings.append(embedding)
        
        # For now, return the first (enhanced) embedding as primary
        # In the future, we could implement embedding fusion strategies
        primary_embedding = embeddings[0] if embeddings else await self.embed_query(query)
        
        processing_time = time.time() - start_time
        self.enhancement_stats["multi_queries_generated"] += 1
        
        metadata = {
            "multi_query_result": multi_result,
            "embedded_queries": embedded_queries,
            "all_embeddings": embeddings,  # For advanced fusion strategies
            "processing_time": processing_time,
            "variations_count": len(multi_result.query_variations),
            "primary_query": embedded_queries[0] if embedded_queries else query
        }
        
        logger.debug(f"✅ Multi-query embedding: {len(embeddings)} queries in {processing_time:.3f}s")
        
        return primary_embedding, metadata
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Override base embed_query to optionally use enhancement
        Falls back to base implementation for compatibility
        """
        # If enhancement is disabled, use base implementation
        if not self.enable_query_enhancement:
            return await super().embed_query(query)
        
        # Use enhanced query embedding but return only the embedding for compatibility
        result = await self.embed_query_enhanced(query, use_enhancement=True, use_multi_query=False)
        
        if isinstance(result, tuple):
            return result[0]  # Return just the embedding
        else:
            return result
    
    async def embed_with_fusion(
        self, 
        query: str, 
        fusion_strategy: str = "average"
    ) -> List[float]:
        """
        Embed query using multi-query with embedding fusion
        
        Args:
            query: Original query
            fusion_strategy: How to combine multiple embeddings ("average", "weighted", "max")
            
        Returns:
            Fused embedding vector
        """
        if not self.enable_multi_query or not self.multi_query_generator:
            return await self.embed_query(query)
        
        # Get multi-query result with all embeddings
        primary_embedding, metadata = await self._embed_with_multi_query(query)
        all_embeddings = metadata.get("all_embeddings", [primary_embedding])
        
        if len(all_embeddings) <= 1:
            return primary_embedding
        
        # Apply fusion strategy
        if fusion_strategy == "average":
            return self._average_embeddings(all_embeddings)
        elif fusion_strategy == "weighted":
            confidence_scores = metadata.get("multi_query_result").confidence_scores
            return self._weighted_average_embeddings(all_embeddings, confidence_scores)
        else:  # Default to first embedding
            return primary_embedding
    
    def _average_embeddings(self, embeddings: List[List[float]]) -> List[float]:
        """Average multiple embeddings"""
        if not embeddings:
            return []
        
        # Convert to numpy for easier computation
        import numpy as np
        embedding_array = np.array(embeddings)
        averaged = np.mean(embedding_array, axis=0)
        return averaged.tolist()
    
    def _weighted_average_embeddings(
        self, 
        embeddings: List[List[float]], 
        weights: List[float]
    ) -> List[float]:
        """Weighted average of multiple embeddings"""
        if not embeddings or not weights or len(embeddings) != len(weights):
            return self._average_embeddings(embeddings)
        
        import numpy as np
        embedding_array = np.array(embeddings)
        weight_array = np.array(weights)
        
        # Normalize weights
        weight_array = weight_array / np.sum(weight_array)
        
        # Compute weighted average
        weighted_avg = np.average(embedding_array, axis=0, weights=weight_array)
        return weighted_avg.tolist()
    
    async def search_with_enhanced_queries(
        self,
        query: str,
        vectorstore,
        top_k: int = 10,
        use_multi_query: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search using enhanced queries and potentially multiple query variations
        
        Args:
            query: Original query
            vectorstore: VectorStore instance
            top_k: Number of results to return
            use_multi_query: Whether to use multi-query approach
            
        Returns:
            Enhanced search results
        """
        if use_multi_query and self.multi_query_generator:
            # Generate multiple queries and search with each
            multi_result = await self.multi_query_generator.generate_multiple_queries(query)
            
            all_results = []
            seen_ids = set()
            
            for query_var in multi_result.embedding_queries:
                query_embedding = await self.embed_query(query_var)
                results = await vectorstore.search_similar(
                    query_embedding=query_embedding,
                    top_k=top_k // len(multi_result.embedding_queries) + 2
                )
                
                # Add query source to results and deduplicate
                for result in results:
                    if result.get('id') not in seen_ids:
                        result['source_query'] = query_var
                        result['multi_query_match'] = True
                        all_results.append(result)
                        seen_ids.add(result.get('id'))
            
            # Sort by similarity score and return top_k
            all_results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
            return all_results[:top_k]
        
        else:
            # Single enhanced query
            embedding, metadata = await self._embed_with_enhancement(query)
            results = await vectorstore.search_similar(
                query_embedding=embedding,
                top_k=top_k
            )
            
            # Add enhancement metadata to results
            for result in results:
                result['enhanced_query'] = metadata['normalized_query']
                result['enhancement_confidence'] = metadata['confidence']
            
            return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get enhanced service statistics"""
        base_stats = super().get_statistics()
        
        enhanced_stats = {
            "enhancement": {
                "enabled": self.enable_query_enhancement,
                "multi_query_enabled": self.enable_multi_query,
                **self.enhancement_stats
            }
        }
        
        if self.query_enhancer:
            enhanced_stats["enhancement"]["query_enhancer"] = self.query_enhancer.get_statistics()
        
        if self.multi_query_generator:
            enhanced_stats["enhancement"]["multi_query_generator"] = self.multi_query_generator.get_statistics()
        
        return {**base_stats, **enhanced_stats}