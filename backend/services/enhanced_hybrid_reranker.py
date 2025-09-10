"""
Advanced Hybrid Reranker mit Multi-Strategy Ensemble und Adaptive Fusion
Optimierte Version des Multi-Model-Reranking-Ensemble für Streamworks RAG
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from .reranker_v2 import BaseReranker, RerankResult

logger = logging.getLogger(__name__)


class EnhancedHybridReranker(BaseReranker):
    """
    Advanced Ensemble Reranker with adaptive fusion, quality monitoring,
    and multi-strategy combination for optimal reranking performance
    """
    
    def __init__(self, rerankers: Dict[str, BaseReranker], weights: Dict[str, float] = None):
        super().__init__("enhanced_hybrid_ensemble")
        self.rerankers = rerankers
        self.weights = weights or {name: 1.0 / len(rerankers) for name in rerankers}
        
        # Advanced ensemble features
        self.adaptive_weights = self.weights.copy()
        self.performance_history = {name: [] for name in rerankers}
        self.ensemble_metrics = {
            "consistency_scores": [],
            "ensemble_improvements": [],
            "adaptive_adjustments": 0,
            "fusion_strategy_usage": {},
            "quality_scores": []
        }
        
        # Ensemble configuration
        self.enable_adaptive_weights = True
        self.enable_quality_boost = True
        self.history_size = 10
        self.min_reranker_weight = 0.05
        
        logger.info(f"✅ Enhanced Hybrid Ensemble initialized with {len(rerankers)} rerankers")
        
    async def initialize(self) -> None:
        """Initialize all sub-rerankers with enhanced monitoring"""
        if self.initialized:
            return
        
        logger.info("Initializing Enhanced Hybrid Reranker ensemble...")
        
        # Initialize all rerankers in parallel
        init_results = await asyncio.gather(*[
            reranker.initialize() 
            for reranker in self.rerankers.values()
        ], return_exceptions=True)
        
        # Check initialization success
        successful_inits = 0
        for (name, reranker), result in zip(self.rerankers.items(), init_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to initialize reranker {name}: {result}")
            else:
                successful_inits += 1
                logger.info(f"✅ Reranker {name} initialized successfully")
        
        if successful_inits == 0:
            raise RuntimeError("No rerankers could be initialized")
        
        self.initialized = True
        logger.info(f"✅ Enhanced Hybrid Ensemble ready with {successful_inits}/{len(self.rerankers)} rerankers")
    
    async def score(self, query: str, chunks: List[Dict[str, Any]]) -> List[float]:
        """
        Advanced ensemble scoring with adaptive fusion and quality monitoring
        
        Features:
        - Multi-strategy fusion (weighted, rank-based, quality-based)
        - Adaptive weight adjustment based on performance
        - Quality monitoring and agreement boosting
        - Fallback strategies for robustness
        """
        if not chunks:
            return []
        
        start_time = time.time()
        
        # Get scores from all rerankers in parallel
        logger.debug(f"🔄 Running {len(self.rerankers)} rerankers on {len(chunks)} chunks...")
        
        all_scores = await asyncio.gather(*[
            reranker.score(query, chunks)
            for reranker in self.rerankers.values()
        ], return_exceptions=True)
        
        # Collect successful results with quality metrics
        successful_results = {}
        quality_scores = {}
        
        for (name, reranker), scores in zip(self.rerankers.items(), all_scores):
            if isinstance(scores, Exception):
                logger.warning(f"⚠️ Reranker {name} failed: {scores}")
                continue
            
            successful_results[name] = scores
            
            # Calculate quality score for this reranker's performance
            quality_scores[name] = self._calculate_quality_score(scores, chunks, query)
            
            # Store performance history for adaptive weighting
            self.performance_history[name].append(quality_scores[name])
            if len(self.performance_history[name]) > self.history_size:
                self.performance_history[name].pop(0)
        
        if not successful_results:
            logger.error("❌ All rerankers failed in enhanced hybrid ensemble")
            return [0.0] * len(chunks)
        
        logger.info(f"✅ {len(successful_results)}/{len(self.rerankers)} rerankers succeeded")
        
        # Adaptive weight adjustment based on recent performance
        if self.enable_adaptive_weights and len(successful_results) > 1:
            self.adaptive_weights = self._adjust_adaptive_weights(quality_scores)
        
        # Multi-strategy ensemble fusion
        ensemble_scores = self._multi_strategy_fusion(
            successful_results, chunks, quality_scores, query
        )
        
        # Quality validation and confidence boosting
        if self.enable_quality_boost:
            final_scores = self._apply_ensemble_quality_boost(
                ensemble_scores, successful_results, chunks
            )
        else:
            final_scores = ensemble_scores
        
        # Update ensemble metrics
        self._update_ensemble_metrics(successful_results, final_scores, start_time)
        
        processing_time = time.time() - start_time
        logger.info(f"🎯 Enhanced ensemble scoring completed in {processing_time:.3f}s")
        
        return final_scores
    
    def _calculate_quality_score(self, scores: List[float], chunks: List[Dict[str, Any]], query: str) -> float:
        """Calculate comprehensive quality score for a reranker's performance"""
        if not scores:
            return 0.0
        
        scores_array = np.array(scores)
        
        # Quality indicators:
        # 1. Score distribution (good rerankers have varied, meaningful scores)
        score_variance = np.var(scores_array) if len(scores) > 1 else 0.0
        
        # 2. Top score quality (good rerankers have high confidence in best matches)
        max_score = np.max(scores_array)
        
        # 3. Score separation (good rerankers clearly separate relevant from irrelevant)
        score_range = np.max(scores_array) - np.min(scores_array)
        
        # 4. Score distribution shape (prefer normal-ish distributions)
        if len(scores) > 2:
            # Standard deviation as distribution quality indicator
            distribution_quality = min(1.0, np.std(scores_array) * 2)  # Normalize
        else:
            distribution_quality = 0.5
        
        # 5. Correlation with original similarity scores (sanity check)
        original_scores = [chunk.get('similarity_score', 0.0) for chunk in chunks]
        if len(scores) > 1 and np.std(original_scores) > 0:
            correlation = np.corrcoef(scores_array, original_scores)[0, 1]
            correlation = max(0.0, correlation) if not np.isnan(correlation) else 0.0
        else:
            correlation = 0.5  # Neutral when can't calculate
        
        # 6. Query-specific quality indicators
        query_specificity = self._assess_query_specificity(query)
        specificity_bonus = query_specificity * 0.1  # Bonus for handling specific queries
        
        # Combine quality indicators with balanced weights
        quality = (
            score_variance * 0.2 +       # Reward meaningful variation
            max_score * 0.25 +           # Reward high confidence
            score_range * 0.2 +          # Reward clear separation
            distribution_quality * 0.15 + # Reward good distribution
            correlation * 0.15 +         # Reward reasonable correlation
            specificity_bonus            # Bonus for query specificity handling
        )
        
        return min(1.0, max(0.0, quality))
    
    def _assess_query_specificity(self, query: str) -> float:
        """Assess how specific/complex a query is"""
        query_lower = query.lower()
        
        # Simple heuristics for query complexity
        specificity = 0.0
        
        # Length bonus (longer queries often more specific)
        word_count = len(query.split())
        if word_count > 3:
            specificity += 0.3
        if word_count > 6:
            specificity += 0.3
        
        # Question words indicate specific information needs
        question_words = ['was', 'wie', 'wo', 'wann', 'warum', 'wer', 'welche', 'what', 'how', 'where', 'when', 'why', 'who']
        if any(qw in query_lower for qw in question_words):
            specificity += 0.4
        
        return min(1.0, specificity)
    
    def _adjust_adaptive_weights(self, current_quality: Dict[str, float]) -> Dict[str, float]:
        """Adjust weights based on recent performance history with stability controls"""
        new_weights = {}
        total_performance = 0.0
        
        for name in self.rerankers.keys():
            if name in current_quality:
                # Combine current quality with historical performance
                history = self.performance_history.get(name, [])
                if history:
                    # Use weighted average: recent performance more important
                    historical_avg = sum(history) / len(history)
                    recent_weight = 0.7 if len(history) >= 3 else 0.5
                    performance_score = current_quality[name] * recent_weight + historical_avg * (1 - recent_weight)
                else:
                    performance_score = current_quality[name]
                
                new_weights[name] = performance_score
                total_performance += performance_score
            else:
                # Reranker failed, give minimal weight
                new_weights[name] = 0.01
                total_performance += 0.01
        
        # Normalize weights
        if total_performance > 0:
            new_weights = {name: weight / total_performance for name, weight in new_weights.items()}
            
            # Ensure minimum weight for stability (prevent complete elimination)
            for name in new_weights:
                new_weights[name] = max(new_weights[name], self.min_reranker_weight)
                
            # Re-normalize after minimum weight adjustment
            total = sum(new_weights.values())
            new_weights = {name: weight / total for name, weight in new_weights.items()}
            
            self.ensemble_metrics["adaptive_adjustments"] += 1
            
            # Log significant weight changes
            max_change = max(abs(new_weights[name] - self.adaptive_weights.get(name, 0)) 
                           for name in new_weights)
            if max_change > 0.1:
                logger.info(f"🔧 Significant weight adaptation: {new_weights}")
        else:
            new_weights = self.weights.copy()  # Fallback to original weights
        
        return new_weights
    
    def _multi_strategy_fusion(self, 
                             successful_results: Dict[str, List[float]], 
                             chunks: List[Dict[str, Any]], 
                             quality_scores: Dict[str, float],
                             query: str) -> List[float]:
        """Apply multiple fusion strategies and intelligently select the best"""
        strategies = {}
        
        # Strategy 1: Adaptive Weighted Average (current best practice)
        strategies['adaptive_weighted'] = self._weighted_fusion(
            successful_results, self.adaptive_weights
        )
        
        # Strategy 2: Quality-Weighted Fusion (weight by current performance)
        quality_weights = {name: quality_scores.get(name, 0.0) for name in successful_results.keys()}
        total_quality = sum(quality_weights.values())
        if total_quality > 0:
            quality_weights = {name: w / total_quality for name, w in quality_weights.items()}
            strategies['quality_weighted'] = self._weighted_fusion(
                successful_results, quality_weights
            )
        
        # Strategy 3: Rank-based Fusion (Reciprocal Rank Fusion)
        strategies['rank_fusion'] = self._rank_based_fusion(successful_results)
        
        # Strategy 4: Confidence-based Fusion (emphasize high-confidence results)
        strategies['confidence_fusion'] = self._confidence_based_fusion(successful_results)
        
        # Strategy 5: Hybrid Max-Average Fusion
        strategies['hybrid_max_avg'] = self._hybrid_max_average_fusion(successful_results)
        
        # Select best strategy based on comprehensive evaluation
        best_strategy = self._select_best_fusion_strategy(strategies, chunks, query)
        
        # Track strategy usage
        self.ensemble_metrics["fusion_strategy_usage"][best_strategy] = \
            self.ensemble_metrics["fusion_strategy_usage"].get(best_strategy, 0) + 1
        
        logger.debug(f"🔄 Selected fusion strategy: {best_strategy}")
        return strategies[best_strategy]
    
    def _weighted_fusion(self, results: Dict[str, List[float]], weights: Dict[str, float]) -> List[float]:
        """Standard weighted fusion with normalization"""
        if not results:
            return []
        
        chunk_count = len(next(iter(results.values())))
        combined_scores = [0.0] * chunk_count
        
        for name, scores in results.items():
            weight = weights.get(name, 0.0)
            for i, score in enumerate(scores):
                combined_scores[i] += score * weight
        
        return combined_scores
    
    def _rank_based_fusion(self, results: Dict[str, List[float]]) -> List[float]:
        """Improved Reciprocal Rank Fusion with dynamic k parameter"""
        if not results:
            return []
        
        chunk_count = len(next(iter(results.values())))
        rrf_scores = [0.0] * chunk_count
        
        # Dynamic k based on number of chunks (larger k for more chunks)
        k = min(60, max(30, chunk_count // 2))
        
        for name, scores in results.items():
            # Convert scores to ranks (higher score = better rank)
            indexed_scores = [(i, score) for i, score in enumerate(scores)]
            indexed_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Apply RRF formula with dynamic k
            for rank, (chunk_idx, _) in enumerate(indexed_scores, 1):
                rrf_scores[chunk_idx] += 1.0 / (k + rank)
        
        return rrf_scores
    
    def _confidence_based_fusion(self, results: Dict[str, List[float]]) -> List[float]:
        """Fusion that emphasizes high-confidence predictions"""
        if not results:
            return []
        
        chunk_count = len(next(iter(results.values())))
        confidence_scores = [0.0] * chunk_count
        
        for name, scores in results.items():
            max_score = max(scores) if scores else 0.0
            
            for i, score in enumerate(scores):
                # Boost scores that are close to the maximum (high confidence)
                if max_score > 0:
                    confidence_factor = (score / max_score) ** 2  # Quadratic boost
                    confidence_scores[i] += score * confidence_factor
                else:
                    confidence_scores[i] += score
        
        # Normalize by number of rerankers
        num_rerankers = len(results)
        if num_rerankers > 0:
            confidence_scores = [score / num_rerankers for score in confidence_scores]
        
        return confidence_scores
    
    def _hybrid_max_average_fusion(self, results: Dict[str, List[float]]) -> List[float]:
        """Combines max and average fusion with intelligent weighting"""
        if not results:
            return []
        
        chunk_count = len(next(iter(results.values())))
        
        # Calculate both max and average
        max_scores = [0.0] * chunk_count
        avg_scores = [0.0] * chunk_count
        
        for name, scores in results.items():
            for i, score in enumerate(scores):
                max_scores[i] = max(max_scores[i], score)
                avg_scores[i] += score
        
        # Average scores
        num_rerankers = len(results)
        if num_rerankers > 0:
            avg_scores = [score / num_rerankers for score in avg_scores]
        
        # Hybrid combination: weight by confidence spread
        hybrid_scores = []
        for i in range(chunk_count):
            # If max and average are close, trust the consensus (use average)
            # If they're far apart, there's disagreement (use max for safety)
            if max_scores[i] > 0:
                consensus_factor = avg_scores[i] / max_scores[i]  # How much agreement
                # High consensus -> more weight to average, low consensus -> more weight to max
                hybrid_score = avg_scores[i] * consensus_factor + max_scores[i] * (1 - consensus_factor)
            else:
                hybrid_score = 0.0
            
            hybrid_scores.append(hybrid_score)
        
        return hybrid_scores
    
    def _select_best_fusion_strategy(self, 
                                   strategies: Dict[str, List[float]], 
                                   chunks: List[Dict[str, Any]], 
                                   query: str) -> str:
        """Intelligently select the best fusion strategy based on multiple criteria"""
        if len(strategies) == 1:
            return list(strategies.keys())[0]
        
        strategy_scores = {}
        
        for strategy_name, scores in strategies.items():
            if not scores:
                strategy_scores[strategy_name] = 0.0
                continue
            
            # Criteria for strategy evaluation:
            quality_score = 0.0
            
            # 1. Score distribution quality
            quality_score += self._evaluate_fusion_quality(scores) * 0.3
            
            # 2. Top score confidence
            max_score = max(scores)
            quality_score += max_score * 0.2
            
            # 3. Score separation (ability to distinguish)
            score_range = max(scores) - min(scores)
            quality_score += min(1.0, score_range * 2) * 0.2
            
            # 4. Stability (prefer strategies that don't give extreme results)
            std_dev = np.std(scores)
            stability = max(0.0, 1.0 - std_dev)  # Lower std = more stable
            quality_score += stability * 0.1
            
            # 5. Historical performance bonus
            usage_count = self.ensemble_metrics["fusion_strategy_usage"].get(strategy_name, 0)
            if usage_count > 0:
                # Slight bonus for strategies that have been successful before
                quality_score += min(0.1, usage_count * 0.01)
            
            # 6. Query-specific preferences
            query_bonus = self._get_strategy_query_bonus(strategy_name, query)
            quality_score += query_bonus * 0.1
            
            strategy_scores[strategy_name] = quality_score
        
        # Select the strategy with the highest score
        best_strategy = max(strategy_scores, key=strategy_scores.get)
        
        logger.debug(f"📊 Strategy scores: {strategy_scores}")
        return best_strategy
    
    def _get_strategy_query_bonus(self, strategy_name: str, query: str) -> float:
        """Give bonuses to strategies based on query characteristics"""
        query_lower = query.lower()
        
        # Simple query -> prefer simpler fusion
        if len(query.split()) <= 2:
            if strategy_name == 'adaptive_weighted':
                return 0.5
        
        # Complex query -> prefer rank-based or quality-weighted
        if len(query.split()) > 5:
            if strategy_name in ['rank_fusion', 'quality_weighted']:
                return 0.5
        
        # Question queries -> prefer confidence-based
        question_indicators = ['was', 'wie', 'wo', 'warum', 'what', 'how', 'where', 'why']
        if any(qi in query_lower for qi in question_indicators):
            if strategy_name == 'confidence_fusion':
                return 0.5
        
        return 0.0
    
    def _evaluate_fusion_quality(self, scores: List[float]) -> float:
        """Evaluate the quality of a fusion result"""
        if not scores or len(scores) < 2:
            return 0.0
        
        scores_array = np.array(scores)
        
        # Quality indicators for fusion
        # 1. Score separation (good fusion clearly ranks items)
        score_range = np.max(scores_array) - np.min(scores_array)
        separation_score = min(1.0, score_range * 2)  # Normalize
        
        # 2. Distribution quality (not all scores the same, but not too chaotic)
        variance = np.var(scores_array)
        distribution_score = min(1.0, variance * 3)  # Normalize
        
        # 3. Top score confidence (best items should have high scores)
        top_score = np.max(scores_array)
        confidence_score = top_score
        
        # 4. Reasonable score distribution (prefer scores in reasonable ranges)
        mean_score = np.mean(scores_array)
        reasonableness_score = 1.0 if 0.1 <= mean_score <= 0.9 else 0.5
        
        # Combine quality metrics
        quality = (
            separation_score * 0.3 +
            distribution_score * 0.25 +
            confidence_score * 0.25 +
            reasonableness_score * 0.2
        )
        
        return min(1.0, max(0.0, quality))
    
    def _apply_ensemble_quality_boost(self, 
                                    ensemble_scores: List[float], 
                                    successful_results: Dict[str, List[float]], 
                                    chunks: List[Dict[str, Any]]) -> List[float]:
        """Apply intelligent quality boost based on ensemble agreement and confidence"""
        if len(successful_results) < 2:
            return ensemble_scores
        
        boosted_scores = ensemble_scores.copy()
        
        for i, score in enumerate(ensemble_scores):
            # Calculate agreement metrics for this chunk
            chunk_scores = [results[i] for results in successful_results.values()]
            
            if len(chunk_scores) < 2:
                continue
            
            # Agreement analysis
            score_std = np.std(chunk_scores)
            score_mean = np.mean(chunk_scores)
            score_max = np.max(chunk_scores)
            score_min = np.min(chunk_scores)
            
            # High agreement with high scores gets boost
            if score_std < 0.15 and score_mean > 0.6:
                # Strong consensus on high quality
                agreement_boost = min(0.2, (0.6 - score_mean + 0.15 - score_std) * 0.3)
                boosted_scores[i] = min(1.0, score + agreement_boost)
            
            # Very high agreement on medium scores gets moderate boost
            elif score_std < 0.1 and score_mean > 0.4:
                agreement_boost = min(0.1, (0.1 - score_std) * 0.5)
                boosted_scores[i] = min(1.0, score + agreement_boost)
            
            # High disagreement gets penalty (unless one reranker is very confident)
            elif score_std > 0.4:
                if score_max < 0.7:  # No reranker is very confident
                    disagreement_penalty = min(0.15, score_std * 0.3)
                    boosted_scores[i] = max(0.0, score - disagreement_penalty)
                # If one reranker is very confident, don't penalize (might be finding hidden relevance)
            
            # Bonus for chunks that consistently rank high across rerankers
            if all(s > 0.5 for s in chunk_scores):
                consistency_boost = 0.05
                boosted_scores[i] = min(1.0, boosted_scores[i] + consistency_boost)
        
        return boosted_scores
    
    def _update_ensemble_metrics(self, 
                               successful_results: Dict[str, List[float]], 
                               final_scores: List[float],
                               start_time: float):
        """Update comprehensive ensemble performance metrics"""
        if len(successful_results) < 2:
            return
        
        # Calculate consistency score (how well rerankers agree)
        all_reranker_scores = list(successful_results.values())
        consistency_scores = []
        
        for i in range(len(final_scores)):
            chunk_scores = [scores[i] for scores in all_reranker_scores]
            if len(chunk_scores) > 1:
                # Use coefficient of variation (std/mean) as consistency metric
                mean_score = np.mean(chunk_scores)
                if mean_score > 0:
                    cv = np.std(chunk_scores) / mean_score
                    consistency = max(0.0, 1.0 - cv)  # Lower CV = higher consistency
                    consistency_scores.append(consistency)
        
        if consistency_scores:
            avg_consistency = np.mean(consistency_scores)
            self.ensemble_metrics["consistency_scores"].append(avg_consistency)
            
            # Keep last 20 consistency measurements
            if len(self.ensemble_metrics["consistency_scores"]) > 20:
                self.ensemble_metrics["consistency_scores"].pop(0)
        
        # Calculate overall ensemble quality
        ensemble_quality = self._evaluate_fusion_quality(final_scores)
        self.ensemble_metrics["quality_scores"].append(ensemble_quality)
        
        if len(self.ensemble_metrics["quality_scores"]) > 20:
            self.ensemble_metrics["quality_scores"].pop(0)
        
        # Update processing time stats
        processing_time = time.time() - start_time
        self._update_stats(len(final_scores), processing_time)
    
    def get_ensemble_analytics(self) -> Dict[str, Any]:
        """Get detailed ensemble analytics and performance insights"""
        analytics = {
            "current_adaptive_weights": self.adaptive_weights,
            "original_weights": self.weights,
            "performance_history": self.performance_history,
            "ensemble_metrics": self.ensemble_metrics,
            "reranker_count": len(self.rerankers),
            "active_rerankers": [name for name, reranker in self.rerankers.items() 
                               if reranker.initialized]
        }
        
        # Calculate aggregate statistics
        if self.ensemble_metrics["consistency_scores"]:
            analytics["avg_consistency"] = np.mean(self.ensemble_metrics["consistency_scores"])
            analytics["consistency_trend"] = "improving" if len(self.ensemble_metrics["consistency_scores"]) > 1 and \
                self.ensemble_metrics["consistency_scores"][-1] > self.ensemble_metrics["consistency_scores"][-2] else "stable"
        
        if self.ensemble_metrics["quality_scores"]:
            analytics["avg_quality"] = np.mean(self.ensemble_metrics["quality_scores"])
        
        # Strategy preferences
        if self.ensemble_metrics["fusion_strategy_usage"]:
            most_used_strategy = max(self.ensemble_metrics["fusion_strategy_usage"], 
                                   key=self.ensemble_metrics["fusion_strategy_usage"].get)
            analytics["preferred_fusion_strategy"] = most_used_strategy
        
        return analytics