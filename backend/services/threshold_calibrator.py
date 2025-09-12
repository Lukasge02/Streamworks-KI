"""
Threshold Calibrator für Gamma Embeddings
Empirical testing framework to find optimal similarity thresholds
"""

import asyncio
import json
import statistics
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

from config import settings
from .embeddings.embedding_service import EmbeddingService
from .vectorstore import VectorStoreService
# from .docling_ingest import DoclingIngestService  # Not needed for calibration

@dataclass
class ThresholdTestResult:
    """Results from a single threshold test"""
    threshold: float
    retrieved_count: int
    avg_similarity: float
    median_similarity: float
    min_similarity: float
    max_similarity: float
    quality_distribution: Dict[str, int]  # high/good/acceptable/poor

@dataclass
class CalibrationResult:
    """Complete calibration results"""
    optimal_high_threshold: float
    optimal_good_threshold: float
    optimal_fallback_threshold: float
    test_results: List[ThresholdTestResult]
    recommendations: Dict[str, Any]

class ThresholdCalibrator:
    """Calibrates similarity thresholds for Gamma embeddings"""
    
    def __init__(self):
        self.embedding_service = None
        self.vectorstore = None
        
    async def initialize(self):
        """Initialize services"""
        self.embedding_service = EmbeddingService()
        await self.embedding_service.initialize()
        
        self.vectorstore = VectorStoreService()
        await self.vectorstore.initialize()
        
        # self.ingestion_service = DoclingIngestService()  # Not needed for calibration
        print("✅ Threshold calibrator initialized")
    
    async def create_test_dataset(self, num_queries: int = 20) -> List[Dict[str, Any]]:
        """
        Create a diverse test dataset from existing documents
        
        Args:
            num_queries: Number of test queries to generate
            
        Returns:
            List of test queries with expected relevance
        """
        print(f"📊 Creating test dataset with {num_queries} queries...")
        
        # Get all documents from vectorstore
        all_docs = await self.vectorstore.get_all_documents()
        if not all_docs:
            raise ValueError("No documents found in vectorstore. Upload some documents first.")
        
        print(f"Found {len(all_docs)} documents in vectorstore")
        
        # Create diverse test queries based on document content
        test_queries = [
            # General queries that should find results
            {"query": "process", "type": "general", "expected_min_results": 1},
            {"query": "system", "type": "general", "expected_min_results": 1},
            {"query": "data", "type": "general", "expected_min_results": 1},
            {"query": "information", "type": "general", "expected_min_results": 1},
            {"query": "document", "type": "general", "expected_min_results": 1},
            
            # More specific queries
            {"query": "implementation details", "type": "specific", "expected_min_results": 0},
            {"query": "configuration settings", "type": "specific", "expected_min_results": 0},
            {"query": "error handling", "type": "specific", "expected_min_results": 0},
            {"query": "performance metrics", "type": "specific", "expected_min_results": 0},
            {"query": "user interface", "type": "specific", "expected_min_results": 0},
            
            # Technical queries
            {"query": "API endpoint", "type": "technical", "expected_min_results": 0},
            {"query": "database connection", "type": "technical", "expected_min_results": 0},
            {"query": "authentication method", "type": "technical", "expected_min_results": 0},
            {"query": "logging mechanism", "type": "technical", "expected_min_results": 0},
            {"query": "security protocol", "type": "technical", "expected_min_results": 0},
            
            # Edge cases
            {"query": "xyz", "type": "nonsense", "expected_min_results": 0},
            {"query": "qwerty", "type": "nonsense", "expected_min_results": 0},
            {"query": "randomtext", "type": "nonsense", "expected_min_results": 0},
            {"query": "notfound", "type": "nonsense", "expected_min_results": 0},
            {"query": "invalidquery", "type": "nonsense", "expected_min_results": 0},
        ]
        
        return test_queries[:num_queries]
    
    async def test_threshold_range(
        self, 
        test_queries: List[Dict[str, Any]], 
        threshold_range: Tuple[float, float, float] = (0.01, 0.8, 0.05)
    ) -> List[ThresholdTestResult]:
        """
        Test a range of threshold values
        
        Args:
            test_queries: List of test queries
            threshold_range: (start, stop, step) for threshold values
            
        Returns:
            List of test results for each threshold
        """
        start, stop, step = threshold_range
        thresholds = []
        current = start
        while current <= stop:
            thresholds.append(round(current, 2))
            current += step
        
        print(f"🔬 Testing {len(thresholds)} threshold values: {thresholds[0]}-{thresholds[-1]}")
        
        results = []
        for threshold in thresholds:
            print(f"Testing threshold: {threshold:.2f}")
            result = await self._test_single_threshold(test_queries, threshold)
            results.append(result)
            
            # Quick progress feedback
            print(f"  → Retrieved: {result.retrieved_count} chunks, "
                  f"Avg similarity: {result.avg_similarity:.3f}")
        
        return results
    
    async def _test_single_threshold(
        self, 
        test_queries: List[Dict[str, Any]], 
        threshold: float
    ) -> ThresholdTestResult:
        """Test a single threshold value"""
        all_similarities = []
        total_retrieved = 0
        quality_counts = {"high": 0, "good": 0, "acceptable": 0, "poor": 0}
        
        for query_data in test_queries:
            query = query_data["query"]
            
            # Get query embedding
            query_embedding = await self.embedding_service.embed_query(query)
            
            # Search with current threshold by temporarily overriding settings
            original_threshold = settings.SIMILARITY_THRESHOLD
            settings.SIMILARITY_THRESHOLD = threshold
            
            try:
                # Get raw results to analyze similarity distribution
                results = await self.vectorstore.search_similar(
                    query_embedding=query_embedding,
                    top_k=50  # Get more results to analyze distribution
                )
                
                # Count results above threshold
                above_threshold = [r for r in results if r['similarity_score'] >= threshold]
                total_retrieved += len(above_threshold)
                
                # Collect similarities for statistics
                similarities = [r['similarity_score'] for r in results if r['similarity_score'] > 0]
                all_similarities.extend(similarities)
                
                # Classify quality
                for result in results:
                    score = result['similarity_score']
                    if score >= 0.7:
                        quality_counts["high"] += 1
                    elif score >= 0.4:
                        quality_counts["good"] += 1
                    elif score >= 0.2:
                        quality_counts["acceptable"] += 1
                    else:
                        quality_counts["poor"] += 1
                        
            finally:
                # Restore original threshold
                settings.SIMILARITY_THRESHOLD = original_threshold
        
        # Calculate statistics
        if all_similarities:
            avg_similarity = statistics.mean(all_similarities)
            median_similarity = statistics.median(all_similarities)
            min_similarity = min(all_similarities)
            max_similarity = max(all_similarities)
        else:
            avg_similarity = median_similarity = min_similarity = max_similarity = 0.0
        
        return ThresholdTestResult(
            threshold=threshold,
            retrieved_count=total_retrieved,
            avg_similarity=avg_similarity,
            median_similarity=median_similarity,
            min_similarity=min_similarity,
            max_similarity=max_similarity,
            quality_distribution=quality_counts
        )
    
    def analyze_results(self, results: List[ThresholdTestResult]) -> CalibrationResult:
        """
        Analyze test results and recommend optimal thresholds
        
        Args:
            results: List of threshold test results
            
        Returns:
            Calibration recommendations
        """
        print("\n📈 Analyzing calibration results...")
        
        # Find optimal thresholds based on different criteria
        
        # 1. Find threshold that gives reasonable number of results (not too few, not too many)
        target_results_per_query = 3  # Reasonable number of relevant chunks per query
        target_total_results = len(results) * 20 * target_results_per_query  # queries * avg_results
        
        best_balance = None
        best_balance_score = float('inf')
        
        for result in results:
            # Score based on how close we are to target + quality
            results_diff = abs(result.retrieved_count - target_total_results)
            quality_bonus = result.quality_distribution.get("high", 0) + result.quality_distribution.get("good", 0)
            score = results_diff - quality_bonus
            
            if score < best_balance_score:
                best_balance_score = score
                best_balance = result
        
        # 2. Find threshold with best average similarity (quality focus)
        best_quality = max(results, key=lambda r: r.avg_similarity)
        
        # 3. Find reasonable fallback (very permissive)
        fallback_candidates = [r for r in results if r.retrieved_count > 0]
        if fallback_candidates:
            best_fallback = min(fallback_candidates, key=lambda r: r.threshold)
        else:
            best_fallback = results[0]  # Most permissive
        
        # Determine final recommendations
        optimal_high = max(0.3, best_quality.threshold)  # High quality threshold
        optimal_good = best_balance.threshold if best_balance else 0.15  # Balanced threshold
        optimal_fallback = min(0.1, best_fallback.threshold)  # Permissive threshold
        
        recommendations = {
            "analysis": {
                "total_tests": len(results),
                "best_balance_threshold": best_balance.threshold if best_balance else 0.15,
                "best_balance_results": best_balance.retrieved_count if best_balance else 0,
                "best_quality_threshold": best_quality.threshold,
                "best_quality_avg_score": best_quality.avg_similarity,
                "overall_similarity_range": f"{min(r.min_similarity for r in results):.3f} - {max(r.max_similarity for r in results):.3f}"
            },
            "current_vs_recommended": {
                "current_high": 0.7,
                "recommended_high": optimal_high,
                "current_good": 0.3,
                "recommended_good": optimal_good,
                "current_fallback": 0.15,
                "recommended_fallback": optimal_fallback
            }
        }
        
        return CalibrationResult(
            optimal_high_threshold=optimal_high,
            optimal_good_threshold=optimal_good,
            optimal_fallback_threshold=optimal_fallback,
            test_results=results,
            recommendations=recommendations
        )
    
    async def run_full_calibration(
        self, 
        save_results: bool = True,
        threshold_range: Tuple[float, float, float] = (0.01, 0.5, 0.02)
    ) -> CalibrationResult:
        """
        Run complete threshold calibration
        
        Args:
            save_results: Whether to save results to file
            threshold_range: Range of thresholds to test
            
        Returns:
            Complete calibration results
        """
        print("🚀 Starting full threshold calibration...")
        
        # Create test dataset
        test_queries = await self.create_test_dataset(20)
        
        # Test threshold range
        test_results = await self.test_threshold_range(test_queries, threshold_range)
        
        # Analyze results
        calibration = self.analyze_results(test_results)
        
        # Print summary
        self._print_calibration_summary(calibration)
        
        # Save results if requested
        if save_results:
            await self._save_calibration_results(calibration)
        
        return calibration
    
    def _print_calibration_summary(self, calibration: CalibrationResult):
        """Print calibration results summary"""
        print("\n" + "="*60)
        print("🎯 THRESHOLD CALIBRATION RESULTS")
        print("="*60)
        
        print(f"\n📊 RECOMMENDED THRESHOLDS:")
        print(f"  High Quality:  {calibration.optimal_high_threshold:.3f} (was 0.700)")
        print(f"  Good Quality:  {calibration.optimal_good_threshold:.3f} (was 0.300)")
        print(f"  Fallback:      {calibration.optimal_fallback_threshold:.3f} (was 0.150)")
        
        analysis = calibration.recommendations["analysis"]
        print(f"\n📈 ANALYSIS SUMMARY:")
        print(f"  Tests run: {analysis['total_tests']}")
        print(f"  Best balance threshold: {analysis['best_balance_threshold']:.3f}")
        print(f"  Best quality threshold: {analysis['best_quality_threshold']:.3f}")
        print(f"  Best quality avg score: {analysis['best_quality_avg_score']:.3f}")
        print(f"  Overall similarity range: {analysis['overall_similarity_range']}")
        
        print(f"\n🔄 IMPROVEMENT POTENTIAL:")
        current_vs_rec = calibration.recommendations["current_vs_recommended"]
        high_improvement = current_vs_rec["current_high"] - current_vs_rec["recommended_high"]
        good_improvement = current_vs_rec["current_good"] - current_vs_rec["recommended_good"]
        
        if high_improvement > 0.1:
            print(f"  📉 High threshold too restrictive by {high_improvement:.3f}")
        if good_improvement > 0.05:
            print(f"  📉 Good threshold too restrictive by {good_improvement:.3f}")
            
        print(f"\n💡 Expected improvement: Better query relevance with more appropriate thresholds")
        print("="*60)
    
    async def _save_calibration_results(self, calibration: CalibrationResult):
        """Save calibration results to file"""
        results_dir = Path("./calibration_results")
        results_dir.mkdir(exist_ok=True)
        
        # Save detailed results
        results_file = results_dir / "threshold_calibration.json"
        
        # Convert to serializable format
        results_data = {
            "optimal_thresholds": {
                "high": calibration.optimal_high_threshold,
                "good": calibration.optimal_good_threshold,
                "fallback": calibration.optimal_fallback_threshold
            },
            "test_results": [
                {
                    "threshold": result.threshold,
                    "retrieved_count": result.retrieved_count,
                    "avg_similarity": result.avg_similarity,
                    "median_similarity": result.median_similarity,
                    "min_similarity": result.min_similarity,
                    "max_similarity": result.max_similarity,
                    "quality_distribution": result.quality_distribution
                }
                for result in calibration.test_results
            ],
            "recommendations": calibration.recommendations
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"💾 Results saved to: {results_file}")

    async def apply_calibrated_thresholds(self, calibration: CalibrationResult):
        """Apply calibrated thresholds to the system"""
        print("\n🔧 Applying calibrated thresholds to system...")
        
        # Update vectorstore thresholds (temporarily for testing)
        original_settings = {
            "SIMILARITY_THRESHOLD": settings.SIMILARITY_THRESHOLD,
            "HIGH_QUALITY_THRESHOLD": getattr(settings, 'HIGH_QUALITY_THRESHOLD', 0.7),
            "FALLBACK_THRESHOLD": getattr(settings, 'FALLBACK_THRESHOLD', 0.15)
        }
        
        # Apply new thresholds
        settings.SIMILARITY_THRESHOLD = calibration.optimal_good_threshold
        if hasattr(settings, 'HIGH_QUALITY_THRESHOLD'):
            settings.HIGH_QUALITY_THRESHOLD = calibration.optimal_high_threshold
        if hasattr(settings, 'FALLBACK_THRESHOLD'):
            settings.FALLBACK_THRESHOLD = calibration.optimal_fallback_threshold
        
        print(f"✅ Thresholds updated:")
        print(f"   SIMILARITY_THRESHOLD: {settings.SIMILARITY_THRESHOLD:.3f}")
        print(f"   HIGH_QUALITY_THRESHOLD: {getattr(settings, 'HIGH_QUALITY_THRESHOLD', 'N/A')}")
        print(f"   FALLBACK_THRESHOLD: {getattr(settings, 'FALLBACK_THRESHOLD', 'N/A')}")
        
        return original_settings