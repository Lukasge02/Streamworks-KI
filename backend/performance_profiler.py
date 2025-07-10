#!/usr/bin/env python3
"""
Performance Profiler für Mistral LLM Response Zeit Optimierung
Profiling der gesamten Pipeline: Request → RAG → LLM → Response
"""
import asyncio
import time
import logging
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
from contextlib import asynccontextmanager

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.rag_service import rag_service
from app.services.mistral_llm_service import mistral_llm_service
from app.services.mistral_rag_service import mistral_rag_service
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceProfiler:
    """Detailed Performance Profiler für Response Zeit Analyse"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        
    async def profile_complete_pipeline(self, query: str) -> Dict[str, Any]:
        """Profile die komplette Pipeline und identifiziere Bottlenecks"""
        
        profile_result = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "total_time": 0.0,
            "stages": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        start_time = time.time()
        
        # 1. RAG Search Profiling
        rag_start = time.time()
        try:
            documents = await rag_service.search_documents(query, top_k=5)
            rag_time = time.time() - rag_start
            profile_result["stages"]["rag_search"] = {
                "time": rag_time,
                "documents_found": len(documents),
                "status": "success"
            }
            logger.info(f"🔍 RAG Search: {rag_time:.3f}s ({len(documents)} docs)")
        except Exception as e:
            rag_time = time.time() - rag_start
            profile_result["stages"]["rag_search"] = {
                "time": rag_time,
                "error": str(e),
                "status": "failed"
            }
            logger.error(f"❌ RAG Search failed: {e}")
            documents = []
        
        # 2. Context Building Profiling
        context_start = time.time()
        try:
            context = self._build_context_from_docs(documents)
            context_time = time.time() - context_start
            profile_result["stages"]["context_building"] = {
                "time": context_time,
                "context_length": len(context),
                "status": "success"
            }
            logger.info(f"📝 Context Building: {context_time:.3f}s ({len(context)} chars)")
        except Exception as e:
            context_time = time.time() - context_start
            profile_result["stages"]["context_building"] = {
                "time": context_time,
                "error": str(e),
                "status": "failed"
            }
            context = ""
        
        # 3. LLM Generation Profiling (Hauptbottleneck)
        llm_start = time.time()
        try:
            response = await mistral_llm_service.generate_german_response(
                user_message=query,
                context=context,
                fast_mode=False  # Teste zuerst normal mode
            )
            llm_time = time.time() - llm_start
            profile_result["stages"]["llm_generation"] = {
                "time": llm_time,
                "response_length": len(response),
                "mode": "normal",
                "status": "success"
            }
            logger.info(f"🤖 LLM Generation: {llm_time:.3f}s ({len(response)} chars)")
        except Exception as e:
            llm_time = time.time() - llm_start
            profile_result["stages"]["llm_generation"] = {
                "time": llm_time,
                "error": str(e),
                "status": "failed"
            }
            response = "Error in LLM generation"
        
        # 4. Response Processing Profiling
        processing_start = time.time()
        try:
            # German post-processing
            final_response = mistral_llm_service.post_process_german(response)
            processing_time = time.time() - processing_start
            profile_result["stages"]["response_processing"] = {
                "time": processing_time,
                "final_length": len(final_response),
                "status": "success"
            }
            logger.info(f"🔧 Response Processing: {processing_time:.3f}s")
        except Exception as e:
            processing_time = time.time() - processing_start
            profile_result["stages"]["response_processing"] = {
                "time": processing_time,
                "error": str(e),
                "status": "failed"
            }
        
        total_time = time.time() - start_time
        profile_result["total_time"] = total_time
        
        # Bottleneck Analysis
        self._analyze_bottlenecks(profile_result)
        
        logger.info(f"🎯 Total Pipeline Time: {total_time:.3f}s")
        return profile_result
    
    def _build_context_from_docs(self, documents) -> str:
        """Build context from documents (simplified for profiling)"""
        context_parts = []
        for doc in documents[:3]:  # Limit to 3 docs for performance
            content = doc.page_content[:300]  # Limit content length
            context_parts.append(content)
        return "\n\n".join(context_parts)
    
    def _analyze_bottlenecks(self, profile_result: Dict[str, Any]):
        """Analysiere Bottlenecks und gebe Empfehlungen"""
        stages = profile_result["stages"]
        total_time = profile_result["total_time"]
        
        # Identifiziere das langsamste Stage
        slowest_stage = max(stages.items(), 
                          key=lambda x: x[1].get("time", 0) if x[1].get("status") == "success" else 0)
        
        bottlenecks = []
        recommendations = []
        
        # LLM Generation Analysis (Expected main bottleneck)
        llm_time = stages.get("llm_generation", {}).get("time", 0)
        if llm_time > 10.0:
            bottlenecks.append({
                "stage": "llm_generation",
                "time": llm_time,
                "severity": "critical",
                "description": f"LLM generation takes {llm_time:.1f}s (>10s threshold)"
            })
            recommendations.extend([
                "Implement Ollama connection pooling",
                "Enable fast_mode for LLM generation",
                "Reduce context length and num_predict",
                "Add response caching for common queries"
            ])
        
        # RAG Search Analysis
        rag_time = stages.get("rag_search", {}).get("time", 0)
        if rag_time > 1.0:
            bottlenecks.append({
                "stage": "rag_search",
                "time": rag_time,
                "severity": "medium",
                "description": f"RAG search takes {rag_time:.1f}s (>1s threshold)"
            })
            recommendations.append("Optimize vector search with caching")
        
        # Context Building Analysis
        context_time = stages.get("context_building", {}).get("time", 0)
        if context_time > 0.5:
            bottlenecks.append({
                "stage": "context_building",
                "time": context_time,
                "severity": "low",
                "description": f"Context building takes {context_time:.1f}s (>0.5s threshold)"
            })
            recommendations.append("Optimize context building with pre-processing")
        
        profile_result["bottlenecks"] = bottlenecks
        profile_result["recommendations"] = recommendations
        
        # Log critical findings
        if bottlenecks:
            logger.warning(f"🚨 Found {len(bottlenecks)} performance bottlenecks")
            for bottleneck in bottlenecks:
                logger.warning(f"   {bottleneck['stage']}: {bottleneck['time']:.3f}s ({bottleneck['severity']})")
    
    async def test_fast_mode_comparison(self, query: str) -> Dict[str, Any]:
        """Teste Fast Mode vs Normal Mode für LLM Generation"""
        
        logger.info("🏃‍♂️ Testing Fast Mode vs Normal Mode...")
        
        comparison = {
            "query": query,
            "normal_mode": {},
            "fast_mode": {},
            "improvement": {}
        }
        
        # Test Normal Mode
        start_time = time.time()
        try:
            normal_response = await mistral_llm_service.generate_german_response(
                user_message=query,
                context="Test context",
                fast_mode=False
            )
            normal_time = time.time() - start_time
            comparison["normal_mode"] = {
                "time": normal_time,
                "response_length": len(normal_response),
                "status": "success"
            }
            logger.info(f"📊 Normal Mode: {normal_time:.3f}s")
        except Exception as e:
            normal_time = time.time() - start_time
            comparison["normal_mode"] = {
                "time": normal_time,
                "error": str(e),
                "status": "failed"
            }
        
        # Test Fast Mode
        start_time = time.time()
        try:
            fast_response = await mistral_llm_service.generate_german_response(
                user_message=query,
                context="Test context",
                fast_mode=True
            )
            fast_time = time.time() - start_time
            comparison["fast_mode"] = {
                "time": fast_time,
                "response_length": len(fast_response),
                "status": "success"
            }
            logger.info(f"⚡ Fast Mode: {fast_time:.3f}s")
        except Exception as e:
            fast_time = time.time() - start_time
            comparison["fast_mode"] = {
                "time": fast_time,
                "error": str(e),
                "status": "failed"
            }
        
        # Calculate improvement
        if (comparison["normal_mode"].get("status") == "success" and 
            comparison["fast_mode"].get("status") == "success"):
            
            time_saved = normal_time - fast_time
            percent_improvement = (time_saved / normal_time) * 100
            
            comparison["improvement"] = {
                "time_saved": time_saved,
                "percent_improvement": percent_improvement,
                "recommendation": "Use fast_mode" if time_saved > 2.0 else "Stick with normal_mode"
            }
            
            logger.info(f"💡 Improvement: {time_saved:.3f}s saved ({percent_improvement:.1f}%)")
        
        return comparison
    
    async def test_ollama_connection_performance(self) -> Dict[str, Any]:
        """Teste Ollama Connection Performance"""
        
        logger.info("🔗 Testing Ollama Connection Performance...")
        
        connection_test = {
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
        # Test multiple small requests to identify connection overhead
        for i in range(3):
            start_time = time.time()
            try:
                response = await mistral_llm_service.ollama_generate(
                    prompt="Test",
                    options={
                        "temperature": 0.1,
                        "num_predict": 5,  # Very short response
                        "num_ctx": 256     # Minimal context
                    },
                    timeout=10.0
                )
                request_time = time.time() - start_time
                
                connection_test["tests"].append({
                    "test_number": i + 1,
                    "time": request_time,
                    "response_length": len(response),
                    "status": "success"
                })
                logger.info(f"🔗 Connection Test {i+1}: {request_time:.3f}s")
                
            except Exception as e:
                request_time = time.time() - start_time
                connection_test["tests"].append({
                    "test_number": i + 1,
                    "time": request_time,
                    "error": str(e),
                    "status": "failed"
                })
        
        # Analyze connection overhead
        successful_tests = [t for t in connection_test["tests"] if t["status"] == "success"]
        if successful_tests:
            avg_time = sum(t["time"] for t in successful_tests) / len(successful_tests)
            min_time = min(t["time"] for t in successful_tests)
            max_time = max(t["time"] for t in successful_tests)
            
            connection_test["analysis"] = {
                "average_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "variance": max_time - min_time,
                "connection_overhead_estimate": avg_time - 0.1  # Estimate processing time
            }
            
            logger.info(f"📊 Avg Connection Time: {avg_time:.3f}s (variance: {max_time - min_time:.3f}s)")
        
        return connection_test
    
    async def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Führe umfassende Performance-Analyse durch"""
        
        logger.info("🚀 Starting Comprehensive Performance Analysis...")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "test_queries": [
                "Was ist StreamWorks?",
                "Wie erstelle ich einen Batch Job?",
                "XML Template Beispiel"
            ],
            "results": {}
        }
        
        # Test 1: Pipeline Profiling
        logger.info("📊 Phase 1: Pipeline Profiling")
        pipeline_results = []
        for query in analysis["test_queries"]:
            result = await self.profile_complete_pipeline(query)
            pipeline_results.append(result)
            await asyncio.sleep(1)  # Brief pause between tests
        
        analysis["results"]["pipeline_profiling"] = pipeline_results
        
        # Test 2: Fast Mode Comparison
        logger.info("⚡ Phase 2: Fast Mode Comparison")
        fast_mode_result = await self.test_fast_mode_comparison(analysis["test_queries"][0])
        analysis["results"]["fast_mode_comparison"] = fast_mode_result
        
        # Test 3: Ollama Connection Performance
        logger.info("🔗 Phase 3: Ollama Connection Performance")
        connection_result = await self.test_ollama_connection_performance()
        analysis["results"]["connection_performance"] = connection_result
        
        # Generate Summary
        analysis["summary"] = self._generate_performance_summary(analysis)
        
        return analysis
    
    def _generate_performance_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive performance summary with recommendations"""
        
        pipeline_results = analysis["results"]["pipeline_profiling"]
        
        # Calculate averages
        avg_total_time = sum(r["total_time"] for r in pipeline_results) / len(pipeline_results)
        avg_llm_time = sum(r["stages"].get("llm_generation", {}).get("time", 0) for r in pipeline_results) / len(pipeline_results)
        avg_rag_time = sum(r["stages"].get("rag_search", {}).get("time", 0) for r in pipeline_results) / len(pipeline_results)
        
        summary = {
            "current_performance": {
                "average_total_time": avg_total_time,
                "average_llm_time": avg_llm_time,
                "average_rag_time": avg_rag_time,
                "target_time": 3.0,
                "improvement_needed": avg_total_time - 3.0
            },
            "critical_bottlenecks": [],
            "optimization_priority": [],
            "implementation_roadmap": []
        }
        
        # Identify critical bottlenecks
        if avg_llm_time > 8.0:
            summary["critical_bottlenecks"].append({
                "component": "LLM Generation",
                "current_time": avg_llm_time,
                "impact": "critical",
                "potential_improvement": "5-8s reduction with connection pooling and fast mode"
            })
            summary["optimization_priority"].append("LLM Connection Optimization")
        
        if avg_rag_time > 1.0:
            summary["critical_bottlenecks"].append({
                "component": "RAG Search",
                "current_time": avg_rag_time,
                "impact": "medium",
                "potential_improvement": "0.5-1s reduction with vector caching"
            })
            summary["optimization_priority"].append("RAG Search Caching")
        
        # Implementation roadmap
        summary["implementation_roadmap"] = [
            {
                "phase": 1,
                "title": "Ollama Connection Pooling",
                "description": "Implement persistent connections to eliminate connection overhead",
                "expected_improvement": "3-5s reduction",
                "effort": "medium"
            },
            {
                "phase": 2,
                "title": "LLM Response Caching",
                "description": "Cache responses for common queries",
                "expected_improvement": "90% cache hit rate → sub-second responses",
                "effort": "low"
            },
            {
                "phase": 3,
                "title": "Fast Mode Default",
                "description": "Use optimized LLM parameters for better speed",
                "expected_improvement": "2-3s reduction for non-cached queries",
                "effort": "low"
            },
            {
                "phase": 4,
                "title": "RAG Vector Caching",
                "description": "Cache vector search results",
                "expected_improvement": "0.5-1s reduction",
                "effort": "medium"
            }
        ]
        
        return summary

async def main():
    """Hauptfunktion für Performance Profiling"""
    
    logger.info("🎯 StreamWorks-KI Performance Profiler")
    logger.info("Target: Reduce response time from 15.6s to <3s")
    logger.info("=" * 60)
    
    try:
        # Initialize services
        await rag_service.initialize()
        await mistral_llm_service.initialize()
        
        # Run comprehensive analysis
        profiler = PerformanceProfiler()
        analysis = await profiler.run_comprehensive_analysis()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"performance_analysis_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        
        # Print summary
        summary = analysis["summary"]
        logger.info("=" * 60)
        logger.info("📊 PERFORMANCE ANALYSIS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Current Avg Response Time: {summary['current_performance']['average_total_time']:.2f}s")
        logger.info(f"Target Response Time: {summary['current_performance']['target_time']:.2f}s")
        logger.info(f"Improvement Needed: {summary['current_performance']['improvement_needed']:.2f}s")
        logger.info("")
        
        logger.info("🚨 Critical Bottlenecks:")
        for bottleneck in summary["critical_bottlenecks"]:
            logger.info(f"  - {bottleneck['component']}: {bottleneck['current_time']:.2f}s ({bottleneck['impact']})")
        
        logger.info("")
        logger.info("🎯 Optimization Priority:")
        for i, priority in enumerate(summary["optimization_priority"], 1):
            logger.info(f"  {i}. {priority}")
        
        logger.info("")
        logger.info(f"📄 Detailed analysis saved to: {output_file}")
        logger.info("=" * 60)
        
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Performance profiling failed: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(main())