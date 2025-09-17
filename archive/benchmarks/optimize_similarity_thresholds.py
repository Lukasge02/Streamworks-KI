#!/usr/bin/env python3
"""
Similarity Threshold Optimization Tool
Analysiert und optimiert Similarity Thresholds für bessere RAG Retrieval Performance
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Import der lokalen Services
from services.qdrant_rag_service import get_rag_service
from services.qdrant_vectorstore import get_qdrant_service
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimilarityThresholdOptimizer:
    """
    Tool zur Optimierung der Similarity Thresholds für bessere RAG Performance
    """

    def __init__(self):
        self.rag_service = None
        self.qdrant_service = None
        self.test_queries = [
            # Sehr spezifische Queries (sollten hohe Scores haben)
            "Kündigung Mietvertrag",
            "Projektplan Termine",
            "Verkaufsbericht Tabelle",

            # Mittel-spezifische Queries
            "Wie funktioniert Projektmanagement?",
            "Was steht im Kündigungsschreiben?",
            "Welche Verkaufsdaten sind verfügbar?",

            # Breite konzeptuelle Queries (niedrigere Scores erwartet)
            "Allgemeine Geschäftsinformationen",
            "Management Prinzipien",
            "Dokumentenverwaltung Grundlagen",

            # Edge cases
            "xyz123 unbekannt",
            "sehr spezielle technische Details",
            "irrelevante Abfrage"
        ]

        self.threshold_ranges = {
            "current": settings.SIMILARITY_THRESHOLD,  # 0.08
            "high_quality": settings.HIGH_QUALITY_THRESHOLD,  # 0.18
            "fallback": settings.FALLBACK_THRESHOLD,  # 0.02
            "test_values": [0.01, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30]
        }

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "current_settings": {
                "similarity_threshold": settings.SIMILARITY_THRESHOLD,
                "high_quality_threshold": settings.HIGH_QUALITY_THRESHOLD,
                "fallback_threshold": settings.FALLBACK_THRESHOLD
            },
            "analysis": {}
        }

    async def run_optimization(self) -> Dict[str, Any]:
        """Führe vollständige Threshold-Optimierung durch"""
        logger.info("🚀 Starting Similarity Threshold Optimization")

        # 1. Service Initialisierung
        await self._initialize_services()

        # 2. Current Threshold Analysis
        await self._analyze_current_thresholds()

        # 3. Threshold Range Testing
        await self._test_threshold_ranges()

        # 4. Query Type Analysis
        await self._analyze_query_types()

        # 5. Optimal Threshold Recommendation
        recommendations = await self._generate_threshold_recommendations()

        # 6. Generate Report
        report = await self._generate_optimization_report(recommendations)

        logger.info("✅ Similarity Threshold Optimization completed")
        return report

    async def _initialize_services(self):
        """Initialisiere RAG und Qdrant Services"""
        logger.info("🔧 Initializing services...")

        try:
            self.rag_service = await get_rag_service()
            await self.rag_service.initialize()
            logger.info("✅ RAG service initialized")

            self.qdrant_service = await get_qdrant_service()
            await self.qdrant_service.initialize()
            logger.info("✅ Qdrant service initialized")

        except Exception as e:
            logger.error(f"❌ Service initialization failed: {str(e)}")
            raise

    async def _analyze_current_thresholds(self):
        """Analysiere aktuelle Threshold Performance"""
        logger.info("📊 Analyzing current threshold performance...")

        current_results = {}

        for query in self.test_queries[:6]:  # Test mit ersten 6 Queries
            try:
                logger.info(f"Testing query: {query}")

                # Generate embedding for query
                query_embedding = self.rag_service.embed_model.get_text_embedding(query)

                # Search with current threshold
                results = await self.qdrant_service.similarity_search(
                    query_embedding=query_embedding,
                    top_k=10,
                    score_threshold=settings.SIMILARITY_THRESHOLD
                )

                # Analyze results
                scores = [result["score"] for result in results]

                current_results[query] = {
                    "results_count": len(results),
                    "scores": scores,
                    "avg_score": np.mean(scores) if scores else 0,
                    "max_score": max(scores) if scores else 0,
                    "min_score": min(scores) if scores else 0,
                    "threshold_used": settings.SIMILARITY_THRESHOLD
                }

            except Exception as e:
                logger.warning(f"Query failed: {query} - {str(e)}")
                current_results[query] = {
                    "error": str(e),
                    "results_count": 0
                }

        self.results["analysis"]["current_threshold_performance"] = current_results

    async def _test_threshold_ranges(self):
        """Teste verschiedene Threshold-Werte"""
        logger.info("📊 Testing different threshold values...")

        threshold_analysis = {}

        # Test mit einer repräsentativen Query
        test_query = "Was steht im Kündigungsschreiben?"

        try:
            query_embedding = self.rag_service.embed_model.get_text_embedding(test_query)

            for threshold in self.threshold_ranges["test_values"]:
                logger.info(f"Testing threshold: {threshold}")

                results = await self.qdrant_service.similarity_search(
                    query_embedding=query_embedding,
                    top_k=20,  # Mehr Ergebnisse für bessere Analyse
                    score_threshold=threshold
                )

                scores = [result["score"] for result in results]

                threshold_analysis[str(threshold)] = {
                    "results_count": len(results),
                    "scores": scores,
                    "avg_score": np.mean(scores) if scores else 0,
                    "score_range": max(scores) - min(scores) if scores else 0,
                    "quality_distribution": self._classify_score_quality(scores)
                }

        except Exception as e:
            logger.error(f"Threshold range testing failed: {str(e)}")
            threshold_analysis["error"] = str(e)

        self.results["analysis"]["threshold_range_analysis"] = threshold_analysis

    async def _analyze_query_types(self):
        """Analysiere Performance verschiedener Query-Typen"""
        logger.info("📊 Analyzing query type performance...")

        query_categories = {
            "specific": self.test_queries[:3],
            "moderate": self.test_queries[3:6],
            "broad": self.test_queries[6:9],
            "edge_cases": self.test_queries[9:]
        }

        category_analysis = {}

        for category, queries in query_categories.items():
            logger.info(f"Analyzing category: {category}")

            category_results = []

            for query in queries:
                try:
                    query_embedding = self.rag_service.embed_model.get_text_embedding(query)

                    # Test mit aktueller Threshold
                    results = await self.qdrant_service.similarity_search(
                        query_embedding=query_embedding,
                        top_k=5,
                        score_threshold=settings.SIMILARITY_THRESHOLD
                    )

                    scores = [result["score"] for result in results]

                    category_results.append({
                        "query": query,
                        "results_count": len(results),
                        "avg_score": np.mean(scores) if scores else 0,
                        "max_score": max(scores) if scores else 0
                    })

                except Exception as e:
                    category_results.append({
                        "query": query,
                        "error": str(e),
                        "results_count": 0
                    })

            # Category statistics
            valid_results = [r for r in category_results if "error" not in r]

            if valid_results:
                category_analysis[category] = {
                    "queries_tested": len(queries),
                    "successful_queries": len(valid_results),
                    "avg_results_per_query": np.mean([r["results_count"] for r in valid_results]),
                    "avg_score_across_queries": np.mean([r["avg_score"] for r in valid_results if r["avg_score"] > 0]),
                    "detailed_results": category_results
                }
            else:
                category_analysis[category] = {
                    "queries_tested": len(queries),
                    "successful_queries": 0,
                    "status": "failed"
                }

        self.results["analysis"]["query_type_analysis"] = category_analysis

    def _classify_score_quality(self, scores: List[float]) -> Dict[str, int]:
        """Klassifiziere Scores nach Qualität"""
        if not scores:
            return {"high": 0, "medium": 0, "low": 0}

        classification = {"high": 0, "medium": 0, "low": 0}

        for score in scores:
            if score >= 0.15:  # Hohe Qualität
                classification["high"] += 1
            elif score >= 0.05:  # Mittlere Qualität
                classification["medium"] += 1
            else:  # Niedrige Qualität
                classification["low"] += 1

        return classification

    async def _generate_threshold_recommendations(self) -> Dict[str, Any]:
        """Generiere Empfehlungen für optimale Thresholds"""
        logger.info("📋 Generating threshold recommendations...")

        recommendations = {
            "current_assessment": {},
            "optimization_suggestions": {},
            "proposed_thresholds": {}
        }

        # Analyse der aktuellen Performance
        current_perf = self.results["analysis"].get("current_threshold_performance", {})

        if current_perf:
            # Durchschnittliche Ergebnisanzahl
            avg_results = np.mean([r.get("results_count", 0) for r in current_perf.values() if isinstance(r, dict) and "error" not in r])

            # Durchschnittliche Score-Qualität
            all_scores = []
            for result in current_perf.values():
                if isinstance(result, dict) and "scores" in result:
                    all_scores.extend(result["scores"])

            recommendations["current_assessment"] = {
                "avg_results_per_query": round(avg_results, 2),
                "total_score_samples": len(all_scores),
                "avg_similarity_score": round(np.mean(all_scores), 4) if all_scores else 0,
                "score_range": {
                    "min": round(min(all_scores), 4) if all_scores else 0,
                    "max": round(max(all_scores), 4) if all_scores else 0
                }
            }

        # Threshold Range Analysis
        threshold_analysis = self.results["analysis"].get("threshold_range_analysis", {})

        if threshold_analysis:
            # Finde optimale Balance zwischen Precision und Recall
            optimal_threshold = None
            best_balance_score = 0

            for threshold_str, data in threshold_analysis.items():
                if isinstance(data, dict) and "results_count" in data:
                    threshold_val = float(threshold_str)
                    results_count = data["results_count"]
                    avg_score = data.get("avg_score", 0)

                    # Balance Score: Genügend Ergebnisse + hohe Qualität
                    if results_count > 0:
                        # Normalisiere Scores (mehr Ergebnisse ist gut, aber nicht zu viele)
                        results_score = min(results_count / 10, 1.0)  # Optimal bei ~10 Ergebnissen
                        quality_score = min(avg_score / 0.2, 1.0)  # Optimal bei Scores um 0.2

                        balance_score = (results_score * 0.6 + quality_score * 0.4)

                        if balance_score > best_balance_score:
                            best_balance_score = balance_score
                            optimal_threshold = threshold_val

            recommendations["optimization_suggestions"] = {
                "current_threshold": settings.SIMILARITY_THRESHOLD,
                "optimal_threshold": optimal_threshold,
                "balance_score": round(best_balance_score, 3),
                "reasoning": self._generate_threshold_reasoning(optimal_threshold, settings.SIMILARITY_THRESHOLD)
            }

        # Proposed new threshold configuration
        if optimal_threshold:
            recommendations["proposed_thresholds"] = {
                "similarity_threshold": optimal_threshold,
                "high_quality_threshold": min(optimal_threshold * 2.5, 0.25),
                "fallback_threshold": max(optimal_threshold * 0.25, 0.01),
                "confidence_level": "high" if best_balance_score > 0.7 else "medium"
            }

        return recommendations

    def _generate_threshold_reasoning(self, optimal: Optional[float], current: float) -> str:
        """Generiere Begründung für Threshold-Empfehlung"""
        if optimal is None:
            return "Insufficient data for optimization recommendation"

        if abs(optimal - current) < 0.01:
            return "Current threshold is already near optimal"
        elif optimal > current:
            return f"Increase threshold by {optimal - current:.3f} to improve result quality"
        else:
            return f"Decrease threshold by {current - optimal:.3f} to increase result coverage"

    async def _generate_optimization_report(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Generiere umfassenden Optimierungs-Report"""
        logger.info("📄 Generating optimization report...")

        # Summary metrics
        summary = {
            "optimization_timestamp": datetime.now().isoformat(),
            "services_tested": ["qdrant", "rag_service"],
            "queries_analyzed": len(self.test_queries),
            "thresholds_tested": len(self.threshold_ranges["test_values"]),
            "current_performance": recommendations.get("current_assessment", {}),
            "optimization_recommendations": recommendations.get("optimization_suggestions", {}),
            "proposed_configuration": recommendations.get("proposed_thresholds", {})
        }

        # Implementation guidance
        implementation = {
            "config_changes": {},
            "expected_improvements": [],
            "monitoring_suggestions": []
        }

        proposed = recommendations.get("proposed_thresholds", {})
        if proposed:
            implementation["config_changes"] = {
                "SIMILARITY_THRESHOLD": proposed.get("similarity_threshold"),
                "HIGH_QUALITY_THRESHOLD": proposed.get("high_quality_threshold"),
                "FALLBACK_THRESHOLD": proposed.get("fallback_threshold")
            }

            implementation["expected_improvements"] = [
                "Better balance between precision and recall",
                "More relevant search results",
                "Improved user satisfaction with query responses"
            ]

            implementation["monitoring_suggestions"] = [
                "Monitor query response times after threshold changes",
                "Track user satisfaction scores",
                "Measure result relevancy through feedback",
                "Regular re-optimization (monthly)"
            ]

        # Complete report
        optimization_report = {
            "summary": summary,
            "detailed_analysis": self.results["analysis"],
            "recommendations": recommendations,
            "implementation_guide": implementation,
            "generated_at": datetime.now().isoformat()
        }

        # Save report
        report_file = Path("similarity_threshold_optimization.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(optimization_report, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Optimization report saved to: {report_file}")
        return optimization_report


async def main():
    """Main optimization execution"""
    optimizer = SimilarityThresholdOptimizer()

    try:
        report = await optimizer.run_optimization()

        print("\n" + "="*70)
        print("🎯 SIMILARITY THRESHOLD OPTIMIZATION RESULTS")
        print("="*70)

        summary = report["summary"]
        current_perf = summary.get("current_performance", {})
        recommendations = summary.get("optimization_recommendations", {})
        proposed = summary.get("proposed_configuration", {})

        print(f"📊 Current Performance:")
        print(f"   Average results per query: {current_perf.get('avg_results_per_query', 'N/A')}")
        print(f"   Average similarity score: {current_perf.get('avg_similarity_score', 'N/A')}")
        print(f"   Current threshold: {recommendations.get('current_threshold', 'N/A')}")

        print(f"\n🎯 Recommendations:")
        print(f"   Optimal threshold: {recommendations.get('optimal_threshold', 'N/A')}")
        print(f"   Balance score: {recommendations.get('balance_score', 'N/A')}")
        print(f"   Reasoning: {recommendations.get('reasoning', 'N/A')}")

        if proposed:
            print(f"\n⚙️ Proposed Configuration:")
            print(f"   SIMILARITY_THRESHOLD: {proposed.get('similarity_threshold', 'N/A')}")
            print(f"   HIGH_QUALITY_THRESHOLD: {proposed.get('high_quality_threshold', 'N/A')}")
            print(f"   FALLBACK_THRESHOLD: {proposed.get('fallback_threshold', 'N/A')}")
            print(f"   Confidence level: {proposed.get('confidence_level', 'N/A')}")

        print(f"\n📄 Detailed report: similarity_threshold_optimization.json")
        print("="*70)

    except Exception as e:
        logger.error(f"❌ Optimization failed: {str(e)}")
        print(f"❌ Optimization failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())