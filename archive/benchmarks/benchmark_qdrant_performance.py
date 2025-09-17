#!/usr/bin/env python3
"""
Qdrant Performance Benchmarking Tool
Comprehensive performance analysis für die Qdrant RAG Integration
"""

import asyncio
import time
import json
import logging
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import requests
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantPerformanceBenchmark:
    """
    Performance Benchmarking Suite für Qdrant RAG Integration
    """

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backend_url": backend_url,
            "tests": {}
        }

    async def run_complete_benchmark(self) -> Dict[str, Any]:
        """Run alle Performance-Tests"""
        logger.info("🚀 Starting Qdrant Performance Benchmark Suite")

        # 1. Backend Health Check
        await self._test_backend_health()

        # 2. Qdrant Collection Health
        await self._test_qdrant_collection_health()

        # 3. Single Query Performance
        await self._test_single_query_performance()

        # 4. Batch Query Performance
        await self._test_batch_query_performance()

        # 5. Various Query Types Performance
        await self._test_query_types_performance()

        # 6. Load Testing
        await self._test_concurrent_load()

        # 7. Similarity Threshold Analysis
        await self._test_similarity_thresholds()

        # 8. Generate Report
        report = await self._generate_performance_report()

        logger.info("✅ Benchmark Suite completed")
        return report

    async def _test_backend_health(self):
        """Test Backend Health & Startup Time"""
        logger.info("📊 Testing Backend Health...")

        start_time = time.time()
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            end_time = time.time()

            self.results["tests"]["backend_health"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": round((end_time - start_time) * 1000, 2),
                "status_code": response.status_code,
                "details": response.json() if response.status_code == 200 else None
            }

        except Exception as e:
            self.results["tests"]["backend_health"] = {
                "status": "error",
                "error": str(e),
                "response_time_ms": None
            }

    async def _test_qdrant_collection_health(self):
        """Test Qdrant Collection Status"""
        logger.info("📊 Testing Qdrant Collection Health...")

        start_time = time.time()
        try:
            response = requests.get(f"{self.backend_url}/api/chat/health", timeout=15)
            end_time = time.time()

            if response.status_code == 200:
                health_data = response.json()
                qdrant_info = health_data.get("qdrant_service", {})

                self.results["tests"]["qdrant_collection"] = {
                    "status": "healthy",
                    "response_time_ms": round((end_time - start_time) * 1000, 2),
                    "collection_info": qdrant_info,
                    "documents_count": qdrant_info.get("collection", {}).get("vectors_count", 0)
                }
            else:
                self.results["tests"]["qdrant_collection"] = {
                    "status": "error",
                    "status_code": response.status_code
                }

        except Exception as e:
            self.results["tests"]["qdrant_collection"] = {
                "status": "error",
                "error": str(e)
            }

    async def _test_single_query_performance(self):
        """Test Single Query Performance"""
        logger.info("📊 Testing Single Query Performance...")

        test_queries = [
            "Was ist eine Kündigung?",
            "Wie funktioniert Projektmanagement?",
            "Welche Tabellen gibt es im Verkaufsbericht?",
            "Erkläre mir die wichtigsten Code-Dokumentationsrichtlinien"
        ]

        query_results = []

        for query in test_queries:
            start_time = time.time()
            try:
                # Create session first
                session_response = requests.post(f"{self.backend_url}/api/chat/sessions",
                                               json={"title": f"Benchmark: {query[:30]}"})

                if session_response.status_code == 200:
                    session_id = session_response.json()["session_id"]

                    # Send message
                    chat_response = requests.post(
                        f"{self.backend_url}/api/chat/sessions/{session_id}/messages",
                        json={"query": query},
                        timeout=30
                    )

                    end_time = time.time()
                    response_time = round((end_time - start_time) * 1000, 2)

                    if chat_response.status_code == 200:
                        chat_data = chat_response.json()

                        query_results.append({
                            "query": query,
                            "response_time_ms": response_time,
                            "status": "success",
                            "confidence_score": chat_data.get("confidence_score", 0),
                            "sources_count": len(chat_data.get("sources", [])),
                            "processing_time_ms": chat_data.get("processing_time_ms", 0),
                            "mode_used": chat_data.get("metadata", {}).get("mode_used", "unknown")
                        })
                    else:
                        query_results.append({
                            "query": query,
                            "response_time_ms": response_time,
                            "status": "error",
                            "status_code": chat_response.status_code
                        })
                else:
                    query_results.append({
                        "query": query,
                        "status": "session_error",
                        "status_code": session_response.status_code
                    })

            except Exception as e:
                query_results.append({
                    "query": query,
                    "status": "exception",
                    "error": str(e)
                })

        # Calculate statistics
        successful_queries = [r for r in query_results if r["status"] == "success"]

        if successful_queries:
            response_times = [r["response_time_ms"] for r in successful_queries]
            confidence_scores = [r["confidence_score"] for r in successful_queries]

            self.results["tests"]["single_query_performance"] = {
                "total_queries": len(test_queries),
                "successful_queries": len(successful_queries),
                "success_rate": round(len(successful_queries) / len(test_queries) * 100, 2),
                "avg_response_time_ms": round(statistics.mean(response_times), 2),
                "median_response_time_ms": round(statistics.median(response_times), 2),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "avg_confidence_score": round(statistics.mean(confidence_scores), 3),
                "detailed_results": query_results
            }
        else:
            self.results["tests"]["single_query_performance"] = {
                "status": "failed",
                "total_queries": len(test_queries),
                "successful_queries": 0,
                "detailed_results": query_results
            }

    async def _test_batch_query_performance(self):
        """Test Batch Query Performance"""
        logger.info("📊 Testing Batch Query Performance...")

        batch_queries = [
            "Was steht in den Dokumenten über Kündigungen?",
            "Zeige mir alle Projektinformationen",
            "Welche Verkaufsdaten sind verfügbar?",
            "Gibt es Code-Beispiele in den Dokumenten?",
            "Was sind die wichtigsten Geschäftsprozesse?"
        ]

        # Test sequential processing
        start_time = time.time()
        sequential_results = []

        session_response = requests.post(f"{self.backend_url}/api/chat/sessions",
                                       json={"title": "Batch Performance Test"})

        if session_response.status_code == 200:
            session_id = session_response.json()["session_id"]

            for query in batch_queries:
                query_start = time.time()
                response = requests.post(
                    f"{self.backend_url}/api/chat/sessions/{session_id}/messages",
                    json={"query": query},
                    timeout=30
                )
                query_end = time.time()

                sequential_results.append({
                    "query": query,
                    "response_time_ms": round((query_end - query_start) * 1000, 2),
                    "status": "success" if response.status_code == 200 else "error"
                })

        end_time = time.time()
        total_sequential_time = round((end_time - start_time) * 1000, 2)

        successful_sequential = [r for r in sequential_results if r["status"] == "success"]

        self.results["tests"]["batch_query_performance"] = {
            "batch_size": len(batch_queries),
            "sequential_processing": {
                "total_time_ms": total_sequential_time,
                "successful_queries": len(successful_sequential),
                "avg_time_per_query_ms": round(total_sequential_time / len(batch_queries), 2),
                "detailed_results": sequential_results
            }
        }

    async def _test_query_types_performance(self):
        """Test verschiedene Query-Types"""
        logger.info("📊 Testing Various Query Types Performance...")

        query_types = {
            "factual": [
                "Wie lautet die Adresse im Kündigungsschreiben?",
                "Welche Termine sind im Projektplan aufgeführt?"
            ],
            "conceptual": [
                "Was sind die wichtigsten Prinzipien des Projektmanagements?",
                "Erkläre die Grundlagen der Dokumentenverwaltung"
            ],
            "analytical": [
                "Vergleiche die verschiedenen Verkaufsmetriken",
                "Analysiere die Code-Qualitätskriterien"
            ],
            "aggregative": [
                "Fasse alle Projektinformationen zusammen",
                "Erstelle eine Übersicht aller verfügbaren Daten"
            ]
        }

        type_results = {}

        for query_type, queries in query_types.items():
            type_start = time.time()
            type_query_results = []

            session_response = requests.post(f"{self.backend_url}/api/chat/sessions",
                                           json={"title": f"Query Type Test: {query_type}"})

            if session_response.status_code == 200:
                session_id = session_response.json()["session_id"]

                for query in queries:
                    query_start = time.time()
                    response = requests.post(
                        f"{self.backend_url}/api/chat/sessions/{session_id}/messages",
                        json={"query": query},
                        timeout=30
                    )
                    query_end = time.time()

                    if response.status_code == 200:
                        data = response.json()
                        type_query_results.append({
                            "query": query,
                            "response_time_ms": round((query_end - query_start) * 1000, 2),
                            "confidence_score": data.get("confidence_score", 0),
                            "sources_count": len(data.get("sources", [])),
                            "status": "success"
                        })
                    else:
                        type_query_results.append({
                            "query": query,
                            "status": "error",
                            "status_code": response.status_code
                        })

            type_end = time.time()

            successful_type_queries = [r for r in type_query_results if r["status"] == "success"]

            if successful_type_queries:
                response_times = [r["response_time_ms"] for r in successful_type_queries]
                confidence_scores = [r["confidence_score"] for r in successful_type_queries]

                type_results[query_type] = {
                    "total_queries": len(queries),
                    "successful_queries": len(successful_type_queries),
                    "avg_response_time_ms": round(statistics.mean(response_times), 2),
                    "avg_confidence_score": round(statistics.mean(confidence_scores), 3),
                    "detailed_results": type_query_results
                }
            else:
                type_results[query_type] = {
                    "total_queries": len(queries),
                    "successful_queries": 0,
                    "status": "failed"
                }

        self.results["tests"]["query_types_performance"] = type_results

    async def _test_concurrent_load(self):
        """Test Concurrent Load Performance"""
        logger.info("📊 Testing Concurrent Load Performance...")

        # Concurrent query test (simplified for this demo)
        test_query = "Was steht in den verfügbaren Dokumenten?"
        concurrent_levels = [1, 3, 5]

        load_results = {}

        for level in concurrent_levels:
            logger.info(f"Testing concurrent level: {level}")

            start_time = time.time()

            # Create sessions for concurrent testing
            sessions = []
            for i in range(level):
                session_response = requests.post(f"{self.backend_url}/api/chat/sessions",
                                               json={"title": f"Concurrent Test {i+1}"})
                if session_response.status_code == 200:
                    sessions.append(session_response.json()["session_id"])

            # Sequential execution for simplicity (real concurrent would need async)
            concurrent_results = []
            for session_id in sessions:
                query_start = time.time()
                response = requests.post(
                    f"{self.backend_url}/api/chat/sessions/{session_id}/messages",
                    json={"query": test_query},
                    timeout=30
                )
                query_end = time.time()

                concurrent_results.append({
                    "session_id": session_id,
                    "response_time_ms": round((query_end - query_start) * 1000, 2),
                    "status": "success" if response.status_code == 200 else "error"
                })

            end_time = time.time()
            total_time = round((end_time - start_time) * 1000, 2)

            successful_concurrent = [r for r in concurrent_results if r["status"] == "success"]

            if successful_concurrent:
                response_times = [r["response_time_ms"] for r in successful_concurrent]

                load_results[f"level_{level}"] = {
                    "concurrent_sessions": level,
                    "successful_queries": len(successful_concurrent),
                    "total_time_ms": total_time,
                    "avg_response_time_ms": round(statistics.mean(response_times), 2),
                    "throughput_queries_per_second": round(len(successful_concurrent) / (total_time / 1000), 2)
                }
            else:
                load_results[f"level_{level}"] = {
                    "concurrent_sessions": level,
                    "successful_queries": 0,
                    "status": "failed"
                }

        self.results["tests"]["concurrent_load"] = load_results

    async def _test_similarity_thresholds(self):
        """Test Similarity Threshold Impact"""
        logger.info("📊 Testing Similarity Threshold Impact...")

        # This would test different similarity thresholds if the API supported it
        # For now, we'll analyze the current threshold performance

        test_queries = [
            "Kündigung", # Very specific
            "Projekt Management Grundlagen", # Moderate specificity
            "Allgemeine Geschäftsinformationen" # Very broad
        ]

        threshold_results = {}

        for query in test_queries:
            session_response = requests.post(f"{self.backend_url}/api/chat/sessions",
                                           json={"title": f"Threshold Test: {query}"})

            if session_response.status_code == 200:
                session_id = session_response.json()["session_id"]

                response = requests.post(
                    f"{self.backend_url}/api/chat/sessions/{session_id}/messages",
                    json={"query": query},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    threshold_results[query] = {
                        "confidence_score": data.get("confidence_score", 0),
                        "sources_count": len(data.get("sources", [])),
                        "processing_time_ms": data.get("processing_time_ms", 0),
                        "query_complexity": "high" if len(query.split()) <= 2 else "medium" if len(query.split()) <= 4 else "low"
                    }

        self.results["tests"]["similarity_threshold_analysis"] = threshold_results

    async def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate Comprehensive Performance Report"""
        logger.info("📋 Generating Performance Report...")

        # Calculate overall metrics
        overall_metrics = {
            "benchmark_timestamp": self.results["timestamp"],
            "total_tests_run": len(self.results["tests"]),
            "backend_status": self.results["tests"].get("backend_health", {}).get("status", "unknown"),
            "qdrant_status": self.results["tests"].get("qdrant_collection", {}).get("status", "unknown")
        }

        # Performance summary
        single_query = self.results["tests"].get("single_query_performance", {})
        if single_query.get("successful_queries", 0) > 0:
            overall_metrics.update({
                "avg_query_response_time_ms": single_query.get("avg_response_time_ms", 0),
                "query_success_rate_percent": single_query.get("success_rate", 0),
                "avg_confidence_score": single_query.get("avg_confidence_score", 0)
            })

        # Recommendations
        recommendations = []

        if overall_metrics.get("avg_query_response_time_ms", 0) > 2000:
            recommendations.append("Consider optimizing query processing - average response time > 2s")

        if overall_metrics.get("query_success_rate_percent", 0) < 90:
            recommendations.append("Investigate query failures - success rate < 90%")

        if overall_metrics.get("avg_confidence_score", 0) < 0.7:
            recommendations.append("Review similarity thresholds - low confidence scores")

        if not recommendations:
            recommendations.append("Performance looks excellent! All metrics within optimal ranges.")

        # Final report
        performance_report = {
            "summary": overall_metrics,
            "detailed_results": self.results["tests"],
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }

        # Save report to file
        report_file = Path("qdrant_performance_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(performance_report, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Performance report saved to: {report_file}")

        return performance_report


async def main():
    """Main benchmark execution"""
    benchmark = QdrantPerformanceBenchmark()

    try:
        report = await benchmark.run_complete_benchmark()

        print("\n" + "="*60)
        print("🏆 QDRANT PERFORMANCE BENCHMARK RESULTS")
        print("="*60)

        summary = report["summary"]
        print(f"⏱️  Average Query Response Time: {summary.get('avg_query_response_time_ms', 'N/A')} ms")
        print(f"✅ Query Success Rate: {summary.get('query_success_rate_percent', 'N/A')}%")
        print(f"🎯 Average Confidence Score: {summary.get('avg_confidence_score', 'N/A')}")
        print(f"🏥 Backend Status: {summary.get('backend_status', 'N/A')}")
        print(f"🗄️  Qdrant Status: {summary.get('qdrant_status', 'N/A')}")

        print("\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"{i}. {rec}")

        print(f"\n📄 Detailed report saved to: qdrant_performance_report.json")
        print("="*60)

    except Exception as e:
        logger.error(f"❌ Benchmark failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())