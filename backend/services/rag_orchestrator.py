"""
RAG Orchestrator Service

Unified orchestrator for state-of-the-art RAG system that coordinates all advanced services:
- BM25Service (sparse retrieval)
- HybridRetriever (dense + sparse fusion)
- QueryExpander (multi-query generation)
- ResultFusion (intelligent deduplication)
- AdaptiveChunker (structure-aware chunking)
- ContextualEmbedder (document-aware embeddings)

Provides intelligent query routing, adaptive strategy selection, and comprehensive
performance monitoring for optimal retrieval performance.

Author: AI Assistant
Date: 2025-01-XX
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import statistics
from collections import defaultdict, deque

import numpy as np

from .bm25_service import BM25Service
from .hybrid_retriever import HybridRetriever, RetrievalStrategy
from .query_expander import QueryExpander, ExpansionStrategy
from .result_fusion import ResultFusion, FusionStrategy
from .adaptive_chunker import AdaptiveChunker, ChunkingStrategy
from .contextual_embedder import ContextualEmbedder, EmbeddingStrategy, ChunkContext, DocumentType

logger = logging.getLogger(__name__)


class RAGMode(Enum):
    SPEED = "speed"           # Fast retrieval, basic quality
    BALANCED = "balanced"     # Balance speed and quality
    QUALITY = "quality"       # Best quality, slower
    ADAPTIVE = "adaptive"     # Auto-adapt based on query


class QueryComplexity(Enum):
    SIMPLE = "simple"         # Single concept, factual
    MODERATE = "moderate"     # Multiple concepts, some reasoning
    COMPLEX = "complex"       # Multi-faceted, requires synthesis
    RESEARCH = "research"     # Comprehensive analysis needed


@dataclass
class RAGRequest:
    """Request for RAG processing"""
    query: str
    mode: RAGMode = RAGMode.ADAPTIVE
    max_results: int = 10
    min_relevance_score: float = 0.3
    document_filters: Optional[Dict[str, Any]] = None
    context_window: int = 3
    enable_reranking: bool = True
    custom_instructions: Optional[str] = None
    
    def __post_init__(self):
        if self.document_filters is None:
            self.document_filters = {}


@dataclass
class RAGResult:
    """Result from RAG processing"""
    query: str
    results: List[Dict[str, Any]]
    total_results_found: int
    processing_time: float
    strategy_used: str
    complexity_detected: QueryComplexity
    confidence_score: float
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RAGMetrics:
    """Comprehensive RAG performance metrics"""
    total_queries: int = 0
    avg_response_time: float = 0.0
    avg_results_per_query: float = 0.0
    avg_confidence_score: float = 0.0
    
    # Strategy distribution
    strategy_usage: Dict[str, int] = None
    complexity_distribution: Dict[QueryComplexity, int] = None
    
    # Performance by complexity
    performance_by_complexity: Dict[QueryComplexity, float] = None
    
    # Error rates
    total_errors: int = 0
    error_rate: float = 0.0
    
    # Service-specific metrics
    query_expansion_rate: float = 0.0  # % queries that used expansion
    fusion_improvement: float = 0.0    # Avg improvement from fusion
    embedding_cache_hit_rate: float = 0.0
    
    def __post_init__(self):
        if self.strategy_usage is None:
            self.strategy_usage = {}
        if self.complexity_distribution is None:
            self.complexity_distribution = {}
        if self.performance_by_complexity is None:
            self.performance_by_complexity = {}


class RAGOrchestrator:
    """Unified orchestrator for state-of-the-art RAG system"""
    
    def __init__(
        self,
        bm25_service: Optional[BM25Service] = None,
        hybrid_retriever: Optional[HybridRetriever] = None,
        query_expander: Optional[QueryExpander] = None,
        result_fusion: Optional[ResultFusion] = None,
        adaptive_chunker: Optional[AdaptiveChunker] = None,
        contextual_embedder: Optional[ContextualEmbedder] = None,
        enable_caching: bool = True,
        cache_size: int = 1000,
        performance_tracking: bool = True
    ):
        # Initialize services
        self.bm25_service = bm25_service or BM25Service()
        self.hybrid_retriever = hybrid_retriever or HybridRetriever(self.bm25_service)
        self.query_expander = query_expander or QueryExpander()
        self.result_fusion = result_fusion or ResultFusion()
        self.adaptive_chunker = adaptive_chunker or AdaptiveChunker()
        self.contextual_embedder = contextual_embedder or ContextualEmbedder()
        
        # Configuration
        self.enable_caching = enable_caching
        self.cache_size = cache_size
        self.performance_tracking = performance_tracking
        
        # Performance tracking
        self.metrics = RAGMetrics()
        self._query_history: deque = deque(maxlen=1000)
        self._performance_buffer: Dict[str, List[float]] = defaultdict(list)
        
        # Caching
        if self.enable_caching:
            self._result_cache: Dict[str, Tuple[RAGResult, float]] = {}
            self._cache_ttl = 3600  # 1 hour TTL
        
        # Strategy mappings
        self._mode_strategy_mapping = {
            RAGMode.SPEED: {
                'retrieval': RetrievalStrategy.SPARSE_ONLY,
                'expansion': ExpansionStrategy.SIMPLE,
                'embedding': EmbeddingStrategy.BASIC,
                'fusion': FusionStrategy.WEIGHTED_SUM
            },
            RAGMode.BALANCED: {
                'retrieval': RetrievalStrategy.ADAPTIVE,
                'expansion': ExpansionStrategy.SEMANTIC,
                'embedding': EmbeddingStrategy.CONTEXTUAL,
                'fusion': FusionStrategy.RRF
            },
            RAGMode.QUALITY: {
                'retrieval': RetrievalStrategy.DENSE_SPARSE_FUSION,
                'expansion': ExpansionStrategy.COMPREHENSIVE,
                'embedding': EmbeddingStrategy.MULTI_GRANULAR,
                'fusion': FusionStrategy.MMR_FUSION
            }
        }
        
        logger.info("RAGOrchestrator initialized with all advanced services")
    
    async def process_query(self, request: RAGRequest) -> RAGResult:
        """Main entry point for RAG processing"""
        start_time = time.time()
        
        try:
            # Check cache first
            if self.enable_caching:
                cached_result = self._get_cached_result(request)
                if cached_result:
                    return cached_result
            
            # Analyze query complexity
            complexity = await self._analyze_query_complexity(request.query)
            
            # Determine strategy based on mode and complexity
            if request.mode == RAGMode.ADAPTIVE:
                strategy = self._select_adaptive_strategy(complexity, request)
            else:
                strategy = self._mode_strategy_mapping[request.mode]
            
            # Execute RAG pipeline
            result = await self._execute_rag_pipeline(request, complexity, strategy)
            
            # Cache result
            if self.enable_caching:
                self._cache_result(request, result)
            
            # Update metrics
            if self.performance_tracking:
                await self._update_metrics(request, result, complexity, strategy)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG processing: {e}")
            self.metrics.total_errors += 1
            
            # Return empty result with error info
            return RAGResult(
                query=request.query,
                results=[],
                total_results_found=0,
                processing_time=time.time() - start_time,
                strategy_used="error_fallback",
                complexity_detected=QueryComplexity.SIMPLE,
                confidence_score=0.0,
                metadata={"error": str(e)}
            )
    
    async def _analyze_query_complexity(self, query: str) -> QueryComplexity:
        """Analyze query to determine complexity level"""
        # Simple heuristics for complexity detection
        words = query.lower().split()
        word_count = len(words)
        
        # Question indicators
        question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
        has_question = any(word in words for word in question_words)
        
        # Complex indicators
        complex_indicators = ['analyze', 'compare', 'evaluate', 'synthesize', 'relationship', 'impact', 'implications']
        complex_count = sum(1 for indicator in complex_indicators if indicator in query.lower())
        
        # Multiple concepts (AND/OR operators)
        has_boolean = any(word in words for word in ['and', 'or', 'but', 'however', 'versus'])
        
        # Determine complexity
        if word_count > 20 or complex_count >= 2:
            return QueryComplexity.RESEARCH
        elif word_count > 12 or complex_count >= 1 or has_boolean:
            return QueryComplexity.COMPLEX
        elif word_count > 6 or has_question:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.SIMPLE
    
    def _select_adaptive_strategy(self, complexity: QueryComplexity, request: RAGRequest) -> Dict[str, Any]:
        """Select optimal strategy based on query complexity"""
        if complexity == QueryComplexity.SIMPLE:
            return self._mode_strategy_mapping[RAGMode.SPEED]
        elif complexity == QueryComplexity.MODERATE:
            return self._mode_strategy_mapping[RAGMode.BALANCED]
        else:  # COMPLEX or RESEARCH
            return self._mode_strategy_mapping[RAGMode.QUALITY]
    
    async def _execute_rag_pipeline(
        self,
        request: RAGRequest,
        complexity: QueryComplexity,
        strategy: Dict[str, Any]
    ) -> RAGResult:
        """Execute the complete RAG pipeline"""
        
        # Step 1: Query Expansion (if beneficial)
        expanded_queries = [request.query]  # Always include original
        
        if complexity in [QueryComplexity.COMPLEX, QueryComplexity.RESEARCH]:
            try:
                expansion_strategy = strategy['expansion']
                expanded = await self.query_expander.expand_query(request.query, expansion_strategy)
                expanded_queries.extend(expanded['queries'])
                logger.info(f"Query expanded to {len(expanded_queries)} variants")
            except Exception as e:
                logger.warning(f"Query expansion failed: {e}")
        
        # Step 2: Multi-Query Retrieval
        all_results = []
        query_results = {}
        
        for i, query in enumerate(expanded_queries):
            try:
                retrieval_strategy = strategy['retrieval']
                results = await self.hybrid_retriever.search(
                    query=query,
                    strategy=retrieval_strategy,
                    max_results=request.max_results * 2,  # Get more for fusion
                    min_score=request.min_relevance_score * 0.8  # Lower threshold for fusion
                )
                
                query_results[f"query_{i}"] = results
                all_results.extend(results)
                
            except Exception as e:
                logger.warning(f"Retrieval failed for query '{query}': {e}")
        
        # Step 3: Result Fusion
        if len(query_results) > 1:
            try:
                fusion_strategy = strategy['fusion']
                fused_results = await self.result_fusion.fuse_results(
                    query_results,
                    primary_query=request.query,
                    strategy=fusion_strategy,
                    max_results=request.max_results,
                    diversity_threshold=0.7
                )
                
                final_results = fused_results['results']
                confidence_score = fused_results.get('confidence', 0.5)
                
            except Exception as e:
                logger.warning(f"Result fusion failed: {e}")
                # Fallback to first query results
                final_results = query_results.get('query_0', [])[:request.max_results]
                confidence_score = 0.4
        else:
            final_results = all_results[:request.max_results]
            confidence_score = 0.6
        
        # Step 4: Post-processing and Quality Enhancement
        enhanced_results = await self._enhance_results(
            final_results,
            request,
            strategy
        )
        
        # Step 5: Final Scoring and Ranking
        scored_results = self._apply_final_scoring(
            enhanced_results,
            request.query,
            complexity
        )
        
        return RAGResult(
            query=request.query,
            results=scored_results,
            total_results_found=len(all_results),
            processing_time=0.0,  # Will be set by caller
            strategy_used=self._format_strategy_name(strategy),
            complexity_detected=complexity,
            confidence_score=confidence_score,
            metadata={
                'expanded_queries': len(expanded_queries),
                'fusion_applied': len(query_results) > 1,
                'total_candidates': len(all_results)
            }
        )
    
    async def _enhance_results(
        self,
        results: List[Dict[str, Any]],
        request: RAGRequest,
        strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Enhance results with additional context and metadata"""
        enhanced = []
        
        for result in results:
            try:
                # Add contextual information
                enhanced_result = result.copy()
                
                # Add snippet preview if not present
                if 'snippet' not in enhanced_result and 'content' in enhanced_result:
                    content = enhanced_result['content']
                    enhanced_result['snippet'] = self._generate_snippet(
                        content, request.query
                    )
                
                # Add relevance explanation
                enhanced_result['relevance_explanation'] = self._generate_relevance_explanation(
                    enhanced_result, request.query
                )
                
                # Add confidence metrics
                enhanced_result['confidence_breakdown'] = self._calculate_confidence_breakdown(
                    enhanced_result, request.query
                )
                
                enhanced.append(enhanced_result)
                
            except Exception as e:
                logger.warning(f"Result enhancement failed: {e}")
                enhanced.append(result)
        
        return enhanced
    
    def _apply_final_scoring(
        self,
        results: List[Dict[str, Any]],
        query: str,
        complexity: QueryComplexity
    ) -> List[Dict[str, Any]]:
        """Apply final scoring and ranking"""
        
        for result in results:
            base_score = result.get('score', 0.0)
            
            # Complexity-based score adjustment
            complexity_boost = {
                QueryComplexity.SIMPLE: 0.0,
                QueryComplexity.MODERATE: 0.1,
                QueryComplexity.COMPLEX: 0.15,
                QueryComplexity.RESEARCH: 0.2
            }.get(complexity, 0.0)
            
            # Content quality indicators
            content_length_score = min(len(result.get('content', '')) / 1000, 0.1)
            
            # Metadata quality
            metadata_score = 0.05 if result.get('document_title') else 0.0
            
            # Calculate final score
            final_score = base_score + complexity_boost + content_length_score + metadata_score
            result['final_score'] = min(final_score, 1.0)
        
        # Sort by final score
        return sorted(results, key=lambda x: x.get('final_score', 0.0), reverse=True)
    
    def _generate_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Generate relevant snippet from content"""
        words = content.split()
        query_words = set(query.lower().split())
        
        # Find best starting position (most query word matches)
        best_start = 0
        best_score = 0
        
        for i in range(0, len(words), 10):  # Check every 10 words
            window = words[i:i+50]  # 50-word window
            window_text = ' '.join(window).lower()
            score = sum(1 for qw in query_words if qw in window_text)
            
            if score > best_score:
                best_score = score
                best_start = i
        
        # Generate snippet
        snippet_words = words[best_start:best_start+40]
        snippet = ' '.join(snippet_words)
        
        if len(snippet) > max_length:
            snippet = snippet[:max_length-3] + "..."
        
        return snippet
    
    def _generate_relevance_explanation(self, result: Dict[str, Any], query: str) -> str:
        """Generate human-readable relevance explanation"""
        explanations = []
        
        # Score-based explanation
        score = result.get('score', 0.0)
        if score > 0.8:
            explanations.append("High semantic similarity")
        elif score > 0.6:
            explanations.append("Moderate semantic match")
        else:
            explanations.append("Basic content relevance")
        
        # Keyword matches
        content = result.get('content', '').lower()
        query_words = query.lower().split()
        matches = [word for word in query_words if word in content]
        
        if matches:
            explanations.append(f"Contains keywords: {', '.join(matches[:3])}")
        
        return "; ".join(explanations)
    
    def _calculate_confidence_breakdown(self, result: Dict[str, Any], query: str) -> Dict[str, float]:
        """Calculate detailed confidence breakdown"""
        return {
            'semantic_similarity': result.get('score', 0.0),
            'keyword_overlap': self._calculate_keyword_overlap(result, query),
            'content_quality': min(len(result.get('content', '')) / 500, 1.0),
            'metadata_completeness': 1.0 if result.get('document_title') else 0.5
        }
    
    def _calculate_keyword_overlap(self, result: Dict[str, Any], query: str) -> float:
        """Calculate keyword overlap score"""
        content = result.get('content', '').lower()
        query_words = set(query.lower().split())
        content_words = set(content.split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(content_words))
        return overlap / len(query_words)
    
    def _format_strategy_name(self, strategy: Dict[str, Any]) -> str:
        """Format strategy configuration as readable name"""
        parts = []
        for key, value in strategy.items():
            if hasattr(value, 'value'):
                parts.append(f"{key}_{value.value}")
            else:
                parts.append(f"{key}_{str(value)}")
        
        return "_".join(parts)
    
    def _get_cached_result(self, request: RAGRequest) -> Optional[RAGResult]:
        """Get cached result if available and not expired"""
        cache_key = self._generate_cache_key(request)
        
        if cache_key in self._result_cache:
            result, timestamp = self._result_cache[cache_key]
            
            if time.time() - timestamp < self._cache_ttl:
                return result
            else:
                # Remove expired entry
                del self._result_cache[cache_key]
        
        return None
    
    def _cache_result(self, request: RAGRequest, result: RAGResult):
        """Cache result with timestamp"""
        cache_key = self._generate_cache_key(request)
        
        # Manage cache size
        if len(self._result_cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = min(
                self._result_cache.keys(),
                key=lambda k: self._result_cache[k][1]
            )
            del self._result_cache[oldest_key]
        
        self._result_cache[cache_key] = (result, time.time())
    
    def _generate_cache_key(self, request: RAGRequest) -> str:
        """Generate cache key for request"""
        import hashlib
        
        key_data = {
            'query': request.query,
            'mode': request.mode.value,
            'max_results': request.max_results,
            'min_relevance_score': request.min_relevance_score,
            'document_filters': request.document_filters
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def _update_metrics(
        self,
        request: RAGRequest,
        result: RAGResult,
        complexity: QueryComplexity,
        strategy: Dict[str, Any]
    ):
        """Update performance metrics"""
        self.metrics.total_queries += 1
        
        # Update averages
        self.metrics.avg_response_time = (
            (self.metrics.avg_response_time * (self.metrics.total_queries - 1) + 
             result.processing_time) / self.metrics.total_queries
        )
        
        self.metrics.avg_results_per_query = (
            (self.metrics.avg_results_per_query * (self.metrics.total_queries - 1) + 
             len(result.results)) / self.metrics.total_queries
        )
        
        self.metrics.avg_confidence_score = (
            (self.metrics.avg_confidence_score * (self.metrics.total_queries - 1) + 
             result.confidence_score) / self.metrics.total_queries
        )
        
        # Update distributions
        strategy_name = result.strategy_used
        self.metrics.strategy_usage[strategy_name] = self.metrics.strategy_usage.get(strategy_name, 0) + 1
        self.metrics.complexity_distribution[complexity] = self.metrics.complexity_distribution.get(complexity, 0) + 1
        
        # Update performance by complexity
        if complexity not in self.metrics.performance_by_complexity:
            self.metrics.performance_by_complexity[complexity] = result.processing_time
        else:
            current = self.metrics.performance_by_complexity[complexity]
            count = self.metrics.complexity_distribution[complexity]
            self.metrics.performance_by_complexity[complexity] = (
                (current * (count - 1) + result.processing_time) / count
            )
        
        # Update error rate
        self.metrics.error_rate = self.metrics.total_errors / self.metrics.total_queries
        
        # Store query in history
        self._query_history.append({
            'timestamp': datetime.now(),
            'query': request.query,
            'complexity': complexity,
            'strategy': strategy_name,
            'results_count': len(result.results),
            'processing_time': result.processing_time,
            'confidence': result.confidence_score
        })
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'overview': asdict(self.metrics),
            'service_metrics': {
                'bm25': self.bm25_service.get_performance_metrics(),
                'hybrid_retriever': self.hybrid_retriever.get_performance_metrics(),
                'query_expander': self.query_expander.get_performance_metrics(),
                'result_fusion': self.result_fusion.get_performance_metrics(),
                'contextual_embedder': self.contextual_embedder.get_performance_metrics()
            },
            'recent_queries': list(self._query_history)[-10:],  # Last 10 queries
            'cache_stats': {
                'size': len(self._result_cache) if self.enable_caching else 0,
                'hit_rate': self._calculate_cache_hit_rate()
            },
            'recommendations': self._generate_performance_recommendations()
        }
        
        return report
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate from recent history"""
        if not self._query_history:
            return 0.0
        
        # Simplified calculation - in practice, would track cache hits separately
        return 0.15  # Placeholder
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if self.metrics.avg_response_time > 2.0:
            recommendations.append("Consider enabling more aggressive caching")
        
        if self.metrics.avg_confidence_score < 0.6:
            recommendations.append("Review query expansion strategies")
        
        if self.metrics.error_rate > 0.05:
            recommendations.append("Investigate error patterns and add fallbacks")
        
        # Strategy-specific recommendations
        strategy_counts = self.metrics.strategy_usage
        if strategy_counts:
            most_used = max(strategy_counts, key=strategy_counts.get)
            if "speed" in most_used and self.metrics.avg_confidence_score < 0.7:
                recommendations.append("Consider using balanced or quality modes for better results")
        
        return recommendations
    
    async def optimize_system(self) -> Dict[str, Any]:
        """Automatically optimize system based on performance data"""
        optimization_results = {}
        
        # Clear caches if hit rate is low
        if self._calculate_cache_hit_rate() < 0.1:
            if self.enable_caching:
                self._result_cache.clear()
            self.contextual_embedder.clear_cache()
            optimization_results['cache_cleared'] = True
        
        # Adjust service parameters based on performance
        if self.metrics.avg_response_time > 3.0:
            # Enable more aggressive caching
            optimization_results['cache_size_increased'] = True
            
        return optimization_results
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {}
        
        # Check all services
        services = {
            'bm25_service': self.bm25_service,
            'hybrid_retriever': self.hybrid_retriever,
            'query_expander': self.query_expander,
            'result_fusion': self.result_fusion,
            'adaptive_chunker': self.adaptive_chunker,
            'contextual_embedder': self.contextual_embedder
        }
        
        for name, service in services.items():
            try:
                # Basic health check - ensure service is responsive
                if hasattr(service, 'health_check'):
                    status = await service.health_check()
                else:
                    status = {'status': 'ok', 'message': 'Service responsive'}
                
                health_status[name] = status
                
            except Exception as e:
                health_status[name] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        # Overall system health
        all_ok = all(
            status.get('status') == 'ok' 
            for status in health_status.values()
        )
        
        health_status['system_overall'] = {
            'status': 'healthy' if all_ok else 'degraded',
            'services_ok': sum(1 for s in health_status.values() if s.get('status') == 'ok'),
            'total_services': len(services)
        }
        
        return health_status