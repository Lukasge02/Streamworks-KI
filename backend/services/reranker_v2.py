"""
Advanced Modular Reranker Service für Streamworks RAG
Implementiert BGE-v2-m3 Cross-Encoder mit modularem Provider-System
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

# Import enhanced hybrid reranker
try:
    from .enhanced_hybrid_reranker import EnhancedHybridReranker
    ENHANCED_HYBRID_AVAILABLE = True
    logger.info("✅ Enhanced Hybrid Reranker available")
except ImportError as e:
    ENHANCED_HYBRID_AVAILABLE = False
    logger.warning(f"Enhanced Hybrid Reranker not available: {e}")


class RerankerProvider(str, Enum):
    """Available reranker providers"""
    BGE = "bge"
    LOCAL = "local"
    COHERE = "cohere"
    JINA = "jina"
    HYBRID = "hybrid"
    NONE = "none"


@dataclass
class RerankResult:
    """Result from reranking operation"""
    chunks: List[Dict[str, Any]]
    scores: List[float]
    provider_used: str
    processing_time: float
    metadata: Dict[str, Any] = None


class BaseReranker(ABC):
    """Abstract base class for all reranker implementations"""
    
    def __init__(self, name: str):
        self.name = name
        self.initialized = False
        self._performance_stats = {
            "total_queries": 0,
            "total_chunks": 0,
            "avg_processing_time": 0.0,
            "errors": 0
        }
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the reranker (lazy loading)"""
        pass
    
    @abstractmethod
    async def score(self, query: str, chunks: List[Dict[str, Any]]) -> List[float]:
        """
        Score chunks based on relevance to query
        
        Args:
            query: Search query
            chunks: List of chunks with 'content' field
            
        Returns:
            List of relevance scores (0-1)
        """
        pass
    
    async def rerank(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]], 
        top_k: Optional[int] = None
    ) -> RerankResult:
        """
        Rerank chunks and return top results
        
        Args:
            query: Search query
            chunks: List of chunks to rerank
            top_k: Number of top results to return
            
        Returns:
            RerankResult with reranked chunks
        """
        start_time = time.time()
        
        try:
            # Initialize if needed
            if not self.initialized:
                await self.initialize()
            
            # Score all chunks
            scores = await self.score(query, chunks)
            
            # Sort by scores
            indexed_scores = list(enumerate(scores))
            indexed_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select top_k if specified
            if top_k:
                indexed_scores = indexed_scores[:top_k]
            
            # Build result
            reranked_chunks = []
            final_scores = []
            
            for idx, score in indexed_scores:
                chunk = chunks[idx].copy()
                chunk['rerank_score'] = score
                chunk['original_rank'] = idx
                reranked_chunks.append(chunk)
                final_scores.append(score)
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(len(chunks), processing_time)
            
            return RerankResult(
                chunks=reranked_chunks,
                scores=final_scores,
                provider_used=self.name,
                processing_time=processing_time,
                metadata={"stats": self._performance_stats.copy()}
            )
            
        except Exception as e:
            logger.error(f"Reranking failed in {self.name}: {str(e)}")
            self._performance_stats["errors"] += 1
            raise
    
    def _update_stats(self, chunk_count: int, processing_time: float):
        """Update performance statistics"""
        stats = self._performance_stats
        stats["total_queries"] += 1
        stats["total_chunks"] += chunk_count
        
        # Update rolling average
        n = stats["total_queries"]
        stats["avg_processing_time"] = (
            (stats["avg_processing_time"] * (n - 1) + processing_time) / n
        )


class BGECrossEncoderReranker(BaseReranker):
    """BGE-v2-m3 Cross-Encoder implementation for multilingual reranking"""
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        super().__init__("bge_cross_encoder")
        self.model_name = model_name
        self.model = None
        self.device = None
        
    async def initialize(self) -> None:
        """Lazy load the cross-encoder model"""
        if self.initialized:
            return
            
        try:
            from sentence_transformers import CrossEncoder
            import torch
            
            # Determine device
            if torch.cuda.is_available():
                self.device = 'cuda'
            elif torch.backends.mps.is_available():
                self.device = 'mps'
            else:
                self.device = 'cpu'
            
            logger.info(f"Loading BGE Cross-Encoder model on {self.device}...")
            
            # Load model
            self.model = CrossEncoder(
                self.model_name,
                max_length=512,
                device=self.device
            )
            
            self.initialized = True
            logger.info(f"✅ BGE Cross-Encoder loaded: {self.model_name}")
            
        except ImportError as e:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise e
        except Exception as e:
            logger.error(f"Failed to initialize BGE Cross-Encoder: {str(e)}")
            raise
    
    async def score(self, query: str, chunks: List[Dict[str, Any]]) -> List[float]:
        """Score chunks using cross-encoder"""
        if not chunks:
            return []
        
        # Prepare query-document pairs
        pairs = [(query, chunk.get('content', '')) for chunk in chunks]
        
        # Run cross-encoder prediction
        # Use sync call in async context (model.predict is not async)
        loop = asyncio.get_event_loop()
        scores = await loop.run_in_executor(
            None, 
            self.model.predict,
            pairs
        )
        
        # Normalize scores to 0-1 range if needed
        scores = np.array(scores)
        if scores.min() < 0:
            # Some models output logits, normalize them
            scores = 1 / (1 + np.exp(-scores))  # Sigmoid
        
        return scores.tolist()


class LocalBM25Reranker(BaseReranker):
    """Improved local BM25-based reranking with German support"""
    
    def __init__(self):
        super().__init__("local_bm25")
        self.bm25_model = None
        self.tokenizer = None
        
    async def initialize(self) -> None:
        """Initialize BM25 components"""
        if self.initialized:
            return
        
        try:
            # Import German-aware tokenizer
            import re
            self.tokenizer = lambda text: re.findall(r'\b\w+\b', text.lower())
            self.initialized = True
            logger.info("✅ Local BM25 reranker initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize BM25 reranker: {str(e)}")
            raise
    
    async def score(self, query: str, chunks: List[Dict[str, Any]]) -> List[float]:
        """Score chunks using improved BM25 + heuristics"""
        if not chunks:
            return []
        
        from collections import Counter
        import math
        
        # Tokenize query
        query_tokens = set(self.tokenizer(query))
        
        scores = []
        for chunk in chunks:
            content = chunk.get('content', '')
            content_tokens = self.tokenizer(content)
            content_counter = Counter(content_tokens)
            
            # BM25-inspired scoring
            k1 = 1.2  # BM25 parameter
            b = 0.75  # BM25 parameter
            avgdl = 200  # Average document length estimate
            
            score = 0.0
            doc_len = len(content_tokens)
            
            for term in query_tokens:
                tf = content_counter.get(term, 0)
                if tf > 0:
                    # BM25 formula component
                    idf = math.log(1 + (len(chunks) / (1 + sum(1 for c in chunks if term in c.get('content', '').lower()))))
                    norm_tf = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avgdl))
                    score += idf * norm_tf
            
            # Add bonus for exact phrase match
            if len(query.split()) > 1 and query.lower() in content.lower():
                score *= 1.5
            
            # Add bonus for early position matches
            for term in query_tokens:
                pos = content.lower().find(term)
                if pos >= 0 and pos < 100:  # Bonus for early matches
                    score *= 1.1
            
            # Incorporate original similarity score if available
            if 'similarity_score' in chunk:
                score = score * 0.3 + chunk['similarity_score'] * 0.7
            
            scores.append(min(score, 1.0))  # Cap at 1.0
        
        return scores


class HybridReranker(BaseReranker):
    """Combines multiple rerankers with weighted fusion"""
    
    def __init__(self, rerankers: Dict[str, BaseReranker], weights: Dict[str, float] = None):
        super().__init__("hybrid")
        self.rerankers = rerankers
        self.weights = weights or {name: 1.0 / len(rerankers) for name in rerankers}
        
    async def initialize(self) -> None:
        """Initialize all sub-rerankers"""
        if self.initialized:
            return
        
        # Initialize all rerankers in parallel
        await asyncio.gather(*[
            reranker.initialize() 
            for reranker in self.rerankers.values()
        ])
        
        self.initialized = True
        logger.info(f"✅ Hybrid reranker initialized with {len(self.rerankers)} providers")
    
    async def score(self, query: str, chunks: List[Dict[str, Any]]) -> List[float]:
        """Score using weighted combination of rerankers"""
        if not chunks:
            return []
        
        # Get scores from all rerankers in parallel
        all_scores = await asyncio.gather(*[
            reranker.score(query, chunks)
            for reranker in self.rerankers.values()
        ], return_exceptions=True)
        
        # Combine scores with weights
        combined_scores = [0.0] * len(chunks)
        successful_rerankers = 0
        
        for (name, reranker), scores in zip(self.rerankers.items(), all_scores):
            if isinstance(scores, Exception):
                logger.warning(f"Reranker {name} failed: {scores}")
                continue
            
            weight = self.weights.get(name, 0.0)
            for i, score in enumerate(scores):
                combined_scores[i] += score * weight
            successful_rerankers += 1
        
        # Normalize if not all rerankers succeeded
        if successful_rerankers < len(self.rerankers):
            normalization_factor = len(self.rerankers) / successful_rerankers
            combined_scores = [s * normalization_factor for s in combined_scores]
        
        return combined_scores


class RerankerService:
    """Main service for managing reranking operations"""
    
    def __init__(self, provider: str = None, enable_fallback: bool = True):
        """
        Initialize reranker service
        
        Args:
            provider: Primary reranker provider to use
            enable_fallback: Whether to fallback to other providers on failure
        """
        from config import settings
        
        self.provider = provider or settings.RERANKER_PROVIDER
        self.enable_fallback = enable_fallback
        
        # Initialize reranker registry
        self._rerankers: Dict[str, BaseReranker] = {}
        self._fallback_chain = []
        
        # Setup rerankers based on configuration
        self._setup_rerankers()
        
        # Performance monitoring
        self.metrics = {
            "total_reranks": 0,
            "provider_usage": {},
            "avg_improvement": 0.0
        }
        
        logger.info(f"RerankerService initialized with provider: {self.provider}")
    
    def _setup_rerankers(self):
        """Setup available rerankers based on configuration"""
        from config import settings
        
        # Always add local reranker as fallback
        self._rerankers[RerankerProvider.LOCAL] = LocalBM25Reranker()
        
        # Add BGE if selected or as primary option
        if self.provider in [RerankerProvider.BGE, RerankerProvider.HYBRID]:
            self._rerankers[RerankerProvider.BGE] = BGECrossEncoderReranker()
        
        # Setup advanced hybrid ensemble if requested
        if self.provider == RerankerProvider.HYBRID:
            hybrid_rerankers = {}
            hybrid_weights = {}
            
            # Add available rerankers to hybrid ensemble
            if RerankerProvider.BGE in self._rerankers:
                hybrid_rerankers["bge"] = self._rerankers[RerankerProvider.BGE]
                hybrid_weights["bge"] = 0.7  # BGE gets higher initial weight
            
            if RerankerProvider.LOCAL in self._rerankers:
                hybrid_rerankers["local"] = self._rerankers[RerankerProvider.LOCAL]
                hybrid_weights["local"] = 0.3  # Local gets lower initial weight
            
            # Only create hybrid if we have multiple rerankers
            if len(hybrid_rerankers) > 1:
                # Use enhanced hybrid reranker if available, fallback to basic hybrid
                if ENHANCED_HYBRID_AVAILABLE and getattr(settings, 'USE_ENHANCED_HYBRID', True):
                    self._rerankers[RerankerProvider.HYBRID] = EnhancedHybridReranker(
                        rerankers=hybrid_rerankers,
                        weights=hybrid_weights
                    )
                    logger.info(f"🚀 Enhanced Hybrid Ensemble initialized with {len(hybrid_rerankers)} rerankers")
                else:
                    self._rerankers[RerankerProvider.HYBRID] = HybridReranker(
                        rerankers=hybrid_rerankers,
                        weights=hybrid_weights
                    )
                    logger.info(f"✅ Basic Hybrid Ensemble initialized with {len(hybrid_rerankers)} rerankers")
            else:
                logger.warning("Hybrid reranker requested but only one reranker available, using single reranker")
                # Fallback to available single reranker
                if hybrid_rerankers:
                    self.provider = list(hybrid_rerankers.keys())[0]
                else:
                    self.provider = RerankerProvider.LOCAL
        
        # Setup fallback chain
        if self.enable_fallback:
            if self.provider == RerankerProvider.BGE:
                self._fallback_chain = [RerankerProvider.BGE, RerankerProvider.LOCAL]
            elif self.provider == RerankerProvider.HYBRID:
                self._fallback_chain = [RerankerProvider.HYBRID, RerankerProvider.BGE, RerankerProvider.LOCAL]
            else:
                self._fallback_chain = [RerankerProvider.LOCAL]
        else:
            self._fallback_chain = [self.provider] if self.provider != RerankerProvider.NONE else []
    
    async def rerank(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: Optional[int] = None,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Rerank chunks with fallback support
        
        Args:
            query: Search query
            chunks: Chunks to rerank
            top_k: Number of top results to return
            min_score: Minimum score threshold
            
        Returns:
            Reranked chunks
        """
        if not chunks or self.provider == RerankerProvider.NONE:
            return chunks[:top_k] if top_k else chunks
        
        # Try rerankers in fallback chain
        for provider_name in self._fallback_chain:
            if provider_name not in self._rerankers:
                continue
            
            try:
                reranker = self._rerankers[provider_name]
                result = await reranker.rerank(query, chunks, top_k)
                
                # Filter by minimum score
                filtered_chunks = [
                    chunk for chunk, score in zip(result.chunks, result.scores)
                    if score >= min_score
                ]
                
                # Update metrics
                self.metrics["total_reranks"] += 1
                self.metrics["provider_usage"][provider_name] = \
                    self.metrics["provider_usage"].get(provider_name, 0) + 1
                
                # Calculate improvement (compare top result scores)
                if chunks and filtered_chunks:
                    original_score = chunks[0].get('similarity_score', 0.0)
                    reranked_score = filtered_chunks[0].get('rerank_score', 0.0)
                    improvement = reranked_score - original_score
                    
                    # Update rolling average
                    n = self.metrics["total_reranks"]
                    self.metrics["avg_improvement"] = (
                        (self.metrics["avg_improvement"] * (n - 1) + improvement) / n
                    )
                
                logger.info(
                    f"✅ Reranking successful with {provider_name}: "
                    f"{len(filtered_chunks)}/{len(chunks)} chunks "
                    f"(took {result.processing_time:.3f}s)"
                )
                
                return filtered_chunks
                
            except Exception as e:
                logger.warning(f"Reranker {provider_name} failed: {str(e)}")
                if not self.enable_fallback:
                    raise
                continue
        
        # If all rerankers failed, return original chunks
        logger.warning("All rerankers failed, returning original ranking")
        return chunks[:top_k] if top_k else chunks
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics including enhanced ensemble analytics"""
        metrics = self.metrics.copy()
        
        # Add individual reranker stats
        metrics["reranker_stats"] = {}
        for name, reranker in self._rerankers.items():
            if hasattr(reranker, '_performance_stats'):
                metrics["reranker_stats"][name] = reranker._performance_stats
            
            # Add enhanced ensemble analytics if available
            if hasattr(reranker, 'get_ensemble_analytics'):
                try:
                    ensemble_analytics = reranker.get_ensemble_analytics()
                    metrics["enhanced_ensemble_analytics"] = ensemble_analytics
                    logger.debug("📊 Enhanced ensemble analytics collected")
                except Exception as e:
                    logger.warning(f"Failed to get enhanced ensemble analytics: {e}")
        
        return metrics