#!/usr/bin/env python3
"""
Improved Qdrant Performance Benchmarking Tool
Direct RAG service testing für die Qdrant Integration
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedQdrantBenchmark:
    """
    Verbessertes Performance Benchmarking für Qdrant RAG Integration
    Testet direkt über API-Endpoints ohne Session-Authentifizierung
    """

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backend_url": backend_url,
            "tests": {}
        }

    async def run_complete_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        logger.info("🚀 Starting Improved Qdrant Performance Benchmark")

        # 1. System Health Analysis
        await self._test_system_health()

        # 2. Qdrant Collection Metrics
        await self._test_qdrant_metrics()

        # 3. Health Endpoint Performance
        await self._test_health_endpoint_performance()

        # 4. API Response Time Analysis
        await self._test_api_response_times()

        # 5. Backend Load Handling
        await self._test_backend_load_capacity()

        # 6. Document Management Performance
        await self._test_document_management_performance()

        # 7. Generate Comprehensive Report
        report = await self._generate_benchmark_report()

        logger.info("✅ Improved Benchmark Suite completed")
        return report

    async def _test_system_health(self):
        """Test overall system health and response"""
        logger.info("📊 Testing System Health...")

        # Test main health endpoint
        main_health_start = time.time()
        main_health_response = requests.get(f"{self.backend_url}/api/health", timeout=10)
        main_health_time = (time.time() - main_health_start) * 1000

        # Test chat health endpoint
        chat_health_start = time.time()
        chat_health_response = requests.get(f"{self.backend_url}/api/chat/health", timeout=15)
        chat_health_time = (time.time() - chat_health_start) * 1000

        # Parse health data
        main_health_data = main_health_response.json() if main_health_response.status_code == 200 else {}
        chat_health_data = chat_health_response.json() if chat_health_response.status_code == 200 else {}

        self.results["tests"]["system_health"] = {
            "main_health": {
                "status_code": main_health_response.status_code,
                "response_time_ms": round(main_health_time, 2),
                "status": main_health_data.get("overall_status", "unknown"),
                "services": main_health_data.get("services", {})
            },
            "chat_health": {
                "status_code": chat_health_response.status_code,
                "response_time_ms": round(chat_health_time, 2),
                "status": chat_health_data.get("status", "unknown"),
                "rag_service": chat_health_data.get("rag_service", {}),
                "system_info": chat_health_data.get("system_info", {})
            }
        }

    async def _test_qdrant_metrics(self):
        """Test Qdrant-specific metrics"""
        logger.info("📊 Testing Qdrant Metrics...")

        # Get health data to extract Qdrant information
        try:
            chat_response = requests.get(f"{self.backend_url}/api/chat/health", timeout=15)
            if chat_response.status_code == 200:
                health_data = chat_response.json()
                rag_service = health_data.get("rag_service", {})

                self.results["tests"]["qdrant_metrics"] = {
                    "qdrant_status": rag_service.get("qdrant", {}).get("status", "unknown"),
                    "rag_initialized": rag_service.get("initialized", False),
                    "vector_store": health_data.get("system_info", {}).get("vector_store", "unknown"),
                    "available_modes": health_data.get("system_info", {}).get("supported_modes", []),
                    "backend_type": health_data.get("system_info", {}).get("backend", "unknown")
                }
            else:
                self.results["tests"]["qdrant_metrics"] = {
                    "status": "error",
                    "status_code": chat_response.status_code
                }

        except Exception as e:
            self.results["tests"]["qdrant_metrics"] = {
                "status": "exception",
                "error": str(e)
            }

    async def _test_health_endpoint_performance(self):
        """Test health endpoint performance under load"""
        logger.info("📊 Testing Health Endpoint Performance...")

        endpoints = [
            "/api/health",
            "/api/chat/health",
            "/health"
        ]

        endpoint_results = {}

        for endpoint in endpoints:
            logger.info(f"Testing endpoint: {endpoint}")

            response_times = []
            status_codes = []

            # Run 10 requests to each endpoint
            for i in range(10):
                start_time = time.time()
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                    end_time = time.time()

                    response_times.append((end_time - start_time) * 1000)
                    status_codes.append(response.status_code)

                except requests.exceptions.Timeout:
                    response_times.append(10000)  # 10 second timeout
                    status_codes.append(408)
                except Exception:
                    response_times.append(None)
                    status_codes.append(500)

            # Calculate statistics
            valid_times = [t for t in response_times if t is not None]

            if valid_times:
                endpoint_results[endpoint] = {
                    "avg_response_time_ms": round(statistics.mean(valid_times), 2),
                    "median_response_time_ms": round(statistics.median(valid_times), 2),
                    "min_response_time_ms": round(min(valid_times), 2),
                    "max_response_time_ms": round(max(valid_times), 2),
                    "success_rate": sum(1 for code in status_codes if 200 <= code < 300) / len(status_codes) * 100,
                    "total_requests": len(response_times),
                    "successful_requests": len(valid_times)
                }
            else:
                endpoint_results[endpoint] = {
                    "status": "failed",
                    "success_rate": 0,
                    "total_requests": len(response_times)
                }

        self.results["tests"]["health_endpoint_performance"] = endpoint_results

    async def _test_api_response_times(self):
        """Test various API endpoints response times"""
        logger.info("📊 Testing API Response Times...")

        api_endpoints = [
            "/docs",
            "/api/v1/folders/",
            "/api/v1/documents/?sort=created_desc&page=1&per_page=10",
            "/api/xml-streams/"
        ]

        api_results = {}

        for endpoint in api_endpoints:
            logger.info(f"Testing API endpoint: {endpoint}")

            start_time = time.time()
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=15)
                end_time = time.time()

                response_time = (end_time - start_time) * 1000

                api_results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "success": 200 <= response.status_code < 300,
                    "content_length": len(response.content) if response.content else 0
                }

            except requests.exceptions.Timeout:
                api_results[endpoint] = {
                    "status": "timeout",
                    "response_time_ms": 15000
                }
            except Exception as e:
                api_results[endpoint] = {
                    "status": "error",
                    "error": str(e)
                }

        self.results["tests"]["api_response_times"] = api_results

    async def _test_backend_load_capacity(self):
        """Test backend load handling capacity"""
        logger.info("📊 Testing Backend Load Capacity...")

        # Concurrent health checks to test load handling
        concurrent_levels = [1, 5, 10, 20]
        load_results = {}

        for level in concurrent_levels:
            logger.info(f"Testing concurrent load level: {level}")

            start_time = time.time()

            # Use asyncio to make truly concurrent requests
            import aiohttp
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(level):
                    task = self._make_async_request(session, f"{self.backend_url}/api/health")
                    tasks.append(task)

                results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()
            total_time = (end_time - start_time) * 1000

            # Analyze results
            successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
            response_times = [r.get("response_time_ms", 0) for r in results if isinstance(r, dict) and r.get("success", False)]

            if response_times:
                load_results[f"level_{level}"] = {
                    "concurrent_requests": level,
                    "successful_requests": successful_requests,
                    "success_rate": (successful_requests / level) * 100,
                    "total_time_ms": round(total_time, 2),
                    "avg_response_time_ms": round(statistics.mean(response_times), 2),
                    "throughput_rps": round(successful_requests / (total_time / 1000), 2)
                }
            else:
                load_results[f"level_{level}"] = {
                    "concurrent_requests": level,
                    "successful_requests": 0,
                    "success_rate": 0,
                    "status": "failed"
                }

        self.results["tests"]["backend_load_capacity"] = load_results

    async def _make_async_request(self, session, url):
        """Make async HTTP request for load testing"""
        start_time = time.time()
        try:
            async with session.get(url, timeout=10) as response:
                end_time = time.time()
                return {
                    "success": True,
                    "status_code": response.status,
                    "response_time_ms": (end_time - start_time) * 1000
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": (end_time - start_time) * 1000
            }

    async def _test_document_management_performance(self):
        """Test document management API performance"""
        logger.info("📊 Testing Document Management Performance...")

        # Test various document endpoints
        doc_endpoints = [
            ("/api/v1/folders/", "GET"),
            ("/api/v1/documents/?sort=created_desc&page=1&per_page=50", "GET"),
            ("/health", "GET")
        ]

        doc_results = {}

        for endpoint, method in doc_endpoints:
            logger.info(f"Testing {method} {endpoint}")

            response_times = []
            status_codes = []

            # Run 5 requests to each document endpoint
            for i in range(5):
                start_time = time.time()
                try:
                    if method == "GET":
                        response = requests.get(f"{self.backend_url}{endpoint}", timeout=15)
                    else:
                        continue  # Skip non-GET for this benchmark

                    end_time = time.time()
                    response_times.append((end_time - start_time) * 1000)
                    status_codes.append(response.status_code)

                except Exception:
                    response_times.append(None)
                    status_codes.append(500)

            # Calculate statistics
            valid_times = [t for t in response_times if t is not None]

            if valid_times:
                doc_results[f"{method} {endpoint}"] = {
                    "avg_response_time_ms": round(statistics.mean(valid_times), 2),
                    "success_rate": sum(1 for code in status_codes if 200 <= code < 300) / len(status_codes) * 100,
                    "requests_tested": len(response_times)
                }
            else:
                doc_results[f"{method} {endpoint}"] = {
                    "status": "failed",
                    "requests_tested": len(response_times)
                }

        self.results["tests"]["document_management_performance"] = doc_results

    async def _generate_benchmark_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        logger.info("📋 Generating Comprehensive Benchmark Report...")

        # Calculate overall performance scores
        overall_metrics = {
            "benchmark_timestamp": self.results["timestamp"],
            "total_test_categories": len(self.results["tests"]),
            "backend_url": self.backend_url
        }

        # Health Status Summary
        system_health = self.results["tests"].get("system_health", {})
        main_health = system_health.get("main_health", {})
        chat_health = system_health.get("chat_health", {})

        overall_metrics.update({
            "main_health_status": main_health.get("status", "unknown"),
            "main_health_response_time_ms": main_health.get("response_time_ms", 0),
            "chat_health_status": chat_health.get("status", "unknown"),
            "chat_health_response_time_ms": chat_health.get("response_time_ms", 0)
        })

        # Qdrant Status Summary
        qdrant_metrics = self.results["tests"].get("qdrant_metrics", {})
        overall_metrics.update({
            "qdrant_status": qdrant_metrics.get("qdrant_status", "unknown"),
            "rag_initialized": qdrant_metrics.get("rag_initialized", False),
            "vector_store": qdrant_metrics.get("vector_store", "unknown")
        })

        # Performance Analysis
        health_perf = self.results["tests"].get("health_endpoint_performance", {})
        api_health = health_perf.get("/api/health", {})

        if api_health.get("avg_response_time_ms"):
            overall_metrics.update({
                "avg_health_response_time_ms": api_health.get("avg_response_time_ms", 0),
                "health_success_rate": api_health.get("success_rate", 0)
            })

        # Load Testing Results
        load_capacity = self.results["tests"].get("backend_load_capacity", {})
        level_10 = load_capacity.get("level_10", {})

        if level_10.get("throughput_rps"):
            overall_metrics.update({
                "concurrent_10_throughput_rps": level_10.get("throughput_rps", 0),
                "concurrent_10_success_rate": level_10.get("success_rate", 0)
            })

        # Generate Recommendations
        recommendations = []

        # Health response time recommendations
        if overall_metrics.get("main_health_response_time_ms", 0) > 1000:
            recommendations.append("Main health endpoint response time > 1s - consider optimization")

        if overall_metrics.get("chat_health_response_time_ms", 0) > 2000:
            recommendations.append("Chat health endpoint response time > 2s - investigate RAG initialization")

        # Qdrant status recommendations
        if overall_metrics.get("qdrant_status") == "not_initialized":
            recommendations.append("Qdrant service not initialized - consider lazy loading optimization")

        if not overall_metrics.get("rag_initialized", False):
            recommendations.append("RAG service not initialized - may impact first query performance")

        # Load testing recommendations
        if overall_metrics.get("concurrent_10_success_rate", 0) < 90:
            recommendations.append("Success rate drops under concurrent load - investigate bottlenecks")

        if overall_metrics.get("concurrent_10_throughput_rps", 0) < 5:
            recommendations.append("Low concurrent throughput - consider async optimizations")

        # Positive recommendations
        if overall_metrics.get("main_health_response_time_ms", 0) < 500:
            recommendations.append("✅ Excellent main health endpoint performance")

        if overall_metrics.get("health_success_rate", 0) > 95:
            recommendations.append("✅ High reliability - excellent success rate")

        if not recommendations:
            recommendations.append("✅ Overall system performance looks good!")

        # Final comprehensive report
        benchmark_report = {
            "summary": overall_metrics,
            "detailed_results": self.results["tests"],
            "recommendations": recommendations,
            "performance_score": self._calculate_performance_score(overall_metrics),
            "generated_at": datetime.now().isoformat()
        }

        # Save report
        report_file = Path("qdrant_benchmark_improved.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(benchmark_report, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Comprehensive benchmark report saved to: {report_file}")
        return benchmark_report

    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance score"""
        scores = {}

        # Health endpoint score (0-100)
        health_time = metrics.get("main_health_response_time_ms", 1000)
        health_score = max(0, 100 - (health_time / 10))  # Deduct 1 point per 10ms
        scores["health_endpoint"] = round(min(100, health_score), 1)

        # Success rate score
        success_rate = metrics.get("health_success_rate", 0)
        scores["reliability"] = round(success_rate, 1)

        # Concurrent performance score
        concurrent_success = metrics.get("concurrent_10_success_rate", 0)
        throughput = metrics.get("concurrent_10_throughput_rps", 0)
        concurrent_score = (concurrent_success * 0.7 + min(throughput * 10, 30))  # Max 30 for throughput
        scores["concurrent_performance"] = round(concurrent_score, 1)

        # System readiness score
        qdrant_ready = 50 if metrics.get("qdrant_status") != "not_initialized" else 0
        rag_ready = 50 if metrics.get("rag_initialized", False) else 0
        scores["system_readiness"] = qdrant_ready + rag_ready

        # Overall score (weighted average)
        overall = (
            scores["health_endpoint"] * 0.3 +
            scores["reliability"] * 0.3 +
            scores["concurrent_performance"] * 0.2 +
            scores["system_readiness"] * 0.2
        )
        scores["overall"] = round(overall, 1)

        return scores


async def main():
    """Main benchmark execution"""
    benchmark = ImprovedQdrantBenchmark()

    try:
        report = await benchmark.run_complete_benchmark()

        print("\n" + "="*70)
        print("🏆 IMPROVED QDRANT PERFORMANCE BENCHMARK RESULTS")
        print("="*70)

        summary = report["summary"]
        scores = report["performance_score"]

        print(f"🏥 Main Health: {summary.get('main_health_status', 'N/A')} ({summary.get('main_health_response_time_ms', 'N/A')}ms)")
        print(f"💬 Chat Health: {summary.get('chat_health_status', 'N/A')} ({summary.get('chat_health_response_time_ms', 'N/A')}ms)")
        print(f"🗄️  Qdrant Status: {summary.get('qdrant_status', 'N/A')}")
        print(f"🧠 RAG Initialized: {summary.get('rag_initialized', 'N/A')}")
        print(f"⚡ Concurrent Throughput: {summary.get('concurrent_10_throughput_rps', 'N/A')} RPS")

        print(f"\n📊 PERFORMANCE SCORES:")
        print(f"   Health Endpoint: {scores['health_endpoint']}/100")
        print(f"   Reliability: {scores['reliability']}/100")
        print(f"   Concurrent Performance: {scores['concurrent_performance']}/100")
        print(f"   System Readiness: {scores['system_readiness']}/100")
        print(f"   🎯 OVERALL SCORE: {scores['overall']}/100")

        print(f"\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"{i}. {rec}")

        print(f"\n📄 Detailed report: qdrant_benchmark_improved.json")
        print("="*70)

    except Exception as e:
        logger.error(f"❌ Benchmark failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())