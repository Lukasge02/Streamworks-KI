"""
Performance benchmark tests for StreamWorks-KI
Measures response times, memory usage, and throughput
"""
import pytest
import time
import asyncio
import psutil
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import json
from datetime import datetime

from app.services.rag_service import RAGService
from app.services.xml_generator import XMLGeneratorService
from app.services.mistral_llm_service import MistralLLMService
from fastapi.testclient import TestClient
from app.main import app


class TestPerformanceBenchmarks:
    """Performance benchmarks for critical system components"""
    
    @pytest.fixture
    def performance_data(self):
        """Storage for performance metrics"""
        return {
            "test_results": [],
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}"
            }
        }
    
    @pytest.fixture
    def client(self):
        """Test client for API performance tests"""
        return TestClient(app)
    
    # RAG Service Performance Tests
    @pytest.mark.performance
    async def test_rag_search_performance(self, performance_data):
        """Test RAG search performance under various loads"""
        rag_service = RAGService()
        
        # Test single query performance
        queries = [
            "Was ist StreamWorks?",
            "Wie erstelle ich einen Batch Job?",
            "XML Stream Konfiguration",
            "Fehlerbehandlung in StreamWorks",
            "Performance Optimierung"
        ]
        
        results = []
        for query in queries:
            start_time = time.time()
            
            try:
                response = await rag_service.search_documents(query, k=5)
                duration = time.time() - start_time
                
                results.append({
                    "query": query,
                    "duration": duration,
                    "results_count": len(response),
                    "status": "success"
                })
                
                # Performance assertion: < 2 seconds
                assert duration < 2.0, f"Query '{query}' took {duration:.2f}s (>2s limit)"
                
            except Exception as e:
                results.append({
                    "query": query,
                    "duration": time.time() - start_time,
                    "error": str(e),
                    "status": "error"
                })
        
        # Calculate averages
        successful_results = [r for r in results if r["status"] == "success"]
        avg_duration = sum(r["duration"] for r in successful_results) / len(successful_results)
        
        performance_data["test_results"].append({
            "test_name": "rag_search_performance",
            "individual_results": results,
            "average_duration": avg_duration,
            "success_rate": len(successful_results) / len(results),
            "requirement": "< 2.0s per query",
            "passed": avg_duration < 2.0
        })
        
        assert avg_duration < 2.0, f"Average RAG search time {avg_duration:.2f}s exceeds 2s limit"
    
    @pytest.mark.performance
    async def test_rag_concurrent_performance(self, performance_data):
        """Test RAG performance under concurrent load"""
        rag_service = RAGService()
        
        async def search_task(query_id: int):
            """Single search task"""
            query = f"Test query {query_id}"
            start_time = time.time()
            
            try:
                await rag_service.search_documents(query, k=3)
                return {
                    "query_id": query_id,
                    "duration": time.time() - start_time,
                    "status": "success"
                }
            except Exception as e:
                return {
                    "query_id": query_id,
                    "duration": time.time() - start_time,
                    "error": str(e),
                    "status": "error"
                }
        
        # Run 10 concurrent searches
        tasks = [search_task(i) for i in range(10)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful_results = [r for r in results if r["status"] == "success"]
        avg_duration = sum(r["duration"] for r in successful_results) / len(successful_results)
        
        performance_data["test_results"].append({
            "test_name": "rag_concurrent_performance",
            "concurrent_queries": 10,
            "total_time": total_time,
            "average_individual_time": avg_duration,
            "success_rate": len(successful_results) / len(results),
            "throughput": len(successful_results) / total_time,
            "requirement": "Handle 10 concurrent queries efficiently",
            "passed": total_time < 10.0 and len(successful_results) >= 8
        })
        
        assert total_time < 10.0, f"Concurrent RAG queries took {total_time:.2f}s (>10s limit)"
        assert len(successful_results) >= 8, f"Only {len(successful_results)}/10 queries succeeded"
    
    # XML Generator Performance Tests
    @pytest.mark.performance
    def test_xml_generation_performance(self, performance_data):
        """Test XML generation performance"""
        xml_generator = XMLGeneratorService()
        
        configs = [
            {"job_name": f"Job{i}", "job_type": "batch", "source_path": f"/data/input{i}"}
            for i in range(20)
        ]
        
        results = []
        for config in configs:
            start_time = time.time()
            
            try:
                xml_content = xml_generator.generate_xml(config)
                duration = time.time() - start_time
                
                results.append({
                    "config": config,
                    "duration": duration,
                    "xml_length": len(xml_content),
                    "status": "success"
                })
                
                # Performance assertion: < 0.5 seconds
                assert duration < 0.5, f"XML generation took {duration:.2f}s (>0.5s limit)"
                
            except Exception as e:
                results.append({
                    "config": config,
                    "duration": time.time() - start_time,
                    "error": str(e),
                    "status": "error"
                })
        
        successful_results = [r for r in results if r["status"] == "success"]
        avg_duration = sum(r["duration"] for r in successful_results) / len(successful_results)
        
        performance_data["test_results"].append({
            "test_name": "xml_generation_performance",
            "total_generations": len(configs),
            "successful_generations": len(successful_results),
            "average_duration": avg_duration,
            "success_rate": len(successful_results) / len(configs),
            "requirement": "< 0.5s per generation",
            "passed": avg_duration < 0.5
        })
        
        assert avg_duration < 0.5, f"Average XML generation time {avg_duration:.2f}s exceeds 0.5s limit"
    
    # API Endpoint Performance Tests
    @pytest.mark.performance
    def test_api_endpoint_performance(self, client, performance_data):
        """Test API endpoint response times"""
        endpoints = [
            ("GET", "/health", None),
            ("GET", "/api/v1/health/", None),
            ("GET", "/api/v1/health/quick", None),
            ("POST", "/api/v1/chat/", {"message": "Was ist StreamWorks?"}),
            ("GET", "/api/v1/metrics", None),
        ]
        
        results = []
        for method, endpoint, data in endpoints:
            start_time = time.time()
            
            try:
                if method == "GET":
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint, json=data)
                
                duration = time.time() - start_time
                
                results.append({
                    "endpoint": f"{method} {endpoint}",
                    "duration": duration,
                    "status_code": response.status_code,
                    "response_size": len(response.content),
                    "status": "success" if 200 <= response.status_code < 300 else "error"
                })
                
                # Performance assertion: < 3 seconds for all endpoints
                assert duration < 3.0, f"{method} {endpoint} took {duration:.2f}s (>3s limit)"
                
            except Exception as e:
                results.append({
                    "endpoint": f"{method} {endpoint}",
                    "duration": time.time() - start_time,
                    "error": str(e),
                    "status": "error"
                })
        
        successful_results = [r for r in results if r["status"] == "success"]
        avg_duration = sum(r["duration"] for r in successful_results) / len(successful_results)
        
        performance_data["test_results"].append({
            "test_name": "api_endpoint_performance",
            "endpoints_tested": len(endpoints),
            "successful_requests": len(successful_results),
            "average_duration": avg_duration,
            "success_rate": len(successful_results) / len(endpoints),
            "requirement": "< 3.0s per endpoint",
            "passed": avg_duration < 3.0
        })
        
        assert avg_duration < 3.0, f"Average API response time {avg_duration:.2f}s exceeds 3s limit"
    
    # Memory Usage Tests
    @pytest.mark.performance
    def test_memory_usage(self, performance_data):
        """Test memory usage during operations"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Simulate memory-intensive operations
        rag_service = RAGService()
        xml_generator = XMLGeneratorService()
        
        # Memory check after initialization
        post_init_memory = process.memory_info().rss
        init_increase = post_init_memory - initial_memory
        
        # Simulate document processing
        large_documents = [f"Large document content {i} " * 1000 for i in range(10)]
        
        # Memory check after document processing
        post_processing_memory = process.memory_info().rss
        processing_increase = post_processing_memory - post_init_memory
        
        performance_data["test_results"].append({
            "test_name": "memory_usage",
            "initial_memory_mb": initial_memory / 1024 / 1024,
            "post_init_memory_mb": post_init_memory / 1024 / 1024,
            "post_processing_memory_mb": post_processing_memory / 1024 / 1024,
            "init_increase_mb": init_increase / 1024 / 1024,
            "processing_increase_mb": processing_increase / 1024 / 1024,
            "total_increase_mb": (post_processing_memory - initial_memory) / 1024 / 1024,
            "requirement": "< 200MB total increase",
            "passed": (post_processing_memory - initial_memory) < 200 * 1024 * 1024
        })
        
        # Memory increase should be reasonable (< 200MB)
        total_increase_mb = (post_processing_memory - initial_memory) / 1024 / 1024
        assert total_increase_mb < 200, f"Memory increased by {total_increase_mb:.1f}MB (>200MB limit)"
    
    # Write performance report
    def test_write_performance_report(self, performance_data):
        """Write performance test results to file"""
        # Calculate overall performance score
        all_tests = performance_data["test_results"]
        passed_tests = [t for t in all_tests if t["passed"]]
        overall_score = len(passed_tests) / len(all_tests) * 100 if all_tests else 0
        
        performance_data["summary"] = {
            "total_tests": len(all_tests),
            "passed_tests": len(passed_tests),
            "failed_tests": len(all_tests) - len(passed_tests),
            "overall_score": overall_score,
            "performance_grade": "EXCELLENT" if overall_score >= 90 else "GOOD" if overall_score >= 80 else "NEEDS_IMPROVEMENT"
        }
        
        # Write report
        report_path = "performance_report.json"
        with open(report_path, "w") as f:
            json.dump(performance_data, f, indent=2)
        
        print(f"\n🚀 Performance Report Generated: {report_path}")
        print(f"📊 Overall Score: {overall_score:.1f}% ({performance_data['summary']['performance_grade']})")
        
        # Performance gate: 80% of tests must pass
        assert overall_score >= 80, f"Performance score {overall_score:.1f}% below 80% threshold"