#!/usr/bin/env python3
"""
RAG Mass Benchmark Test

Tests:
1. Throughput (queries per minute)
2. Response consistency
3. Latency distribution  
4. Error rate under load
"""

import requests
import json
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

BASE_URL = "http://localhost:8000"

# Diverse test queries
BATCH_QUERIES = [
    "Was ist ein Stream?",
    "Wie konfiguriere ich die Datenbank?",
    "Welche Fehlercodes gibt es?",
    "Wo sind die Log-Dateien?",
    "Wie erstelle ich einen Job?",
    "Was bedeutet Multi-Tenancy?",
    "Wie funktionieren Webhooks?",
    "Was sind die Systemanforderungen?",
    "Wie installiere ich StreamWorks?",
    "Welche API-Endpunkte gibt es?",
    "Was ist ein Mandant?",
    "Wie starte ich einen Stream per API?",
    "Was ist die maximale Job-Dauer?",
    "Wie konfiguriere ich Authentifizierung?",
    "Was ist BM25 Suche?",  # Not in docs
]


def single_query(query: str, query_id: int) -> Dict:
    """Execute a single query and return timing info"""
    start = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/api/documents/chat",
            json={"query": query, "num_chunks": 3},
            timeout=60,
        )
        duration = time.time() - start
        data = response.json()
        
        return {
            "id": query_id,
            "query": query[:30],
            "success": "answer" in data,
            "duration": duration,
            "confidence": data.get("confidence", 0),
            "sources": len(data.get("sources", [])),
            "has_context": data.get("has_context", False),
        }
    except Exception as e:
        return {
            "id": query_id,
            "query": query[:30],
            "success": False,
            "duration": time.time() - start,
            "error": str(e),
        }


def run_batch_test(num_queries: int = 30, concurrency: int = 3):
    """Run batch test with specified parallelism"""
    print("=" * 70)
    print(f"🚀 RAG MASS BENCHMARK TEST")
    print(f"   Queries: {num_queries}, Concurrency: {concurrency}")
    print("=" * 70)
    print()
    
    # Create query list (cycle through base queries)
    queries = [BATCH_QUERIES[i % len(BATCH_QUERIES)] for i in range(num_queries)]
    
    results = []
    start_time = time.time()
    
    # Run with thread pool
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {
            executor.submit(single_query, q, i): i 
            for i, q in enumerate(queries)
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            status = "✅" if result["success"] else "❌"
            print(f"  [{result['id']+1:2}/{num_queries}] {status} {result['query']:<30} {result['duration']:.1f}s")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    durations = [r["duration"] for r in successful]
    
    print()
    print("=" * 70)
    print("📊 BENCHMARK RESULTS")
    print("=" * 70)
    print()
    
    # Success rate
    success_rate = len(successful) / len(results) * 100
    print(f"Success Rate: {len(successful)}/{len(results)} ({success_rate:.1f}%)")
    
    # Throughput
    qpm = len(results) / (total_time / 60)
    print(f"Throughput: {qpm:.1f} queries/minute")
    print(f"Total Time: {total_time:.1f}s")
    
    # Latency
    if durations:
        print()
        print("Latency Statistics:")
        print(f"  Min:    {min(durations):.2f}s")
        print(f"  Max:    {max(durations):.2f}s")
        print(f"  Avg:    {statistics.mean(durations):.2f}s")
        print(f"  Median: {statistics.median(durations):.2f}s")
        if len(durations) > 1:
            print(f"  StdDev: {statistics.stdev(durations):.2f}s")
        
        # Percentiles
        sorted_durations = sorted(durations)
        p50 = sorted_durations[int(len(sorted_durations) * 0.5)]
        p90 = sorted_durations[int(len(sorted_durations) * 0.9)]
        p95 = sorted_durations[int(len(sorted_durations) * 0.95)] if len(sorted_durations) > 20 else sorted_durations[-1]
        print(f"  P50:    {p50:.2f}s")
        print(f"  P90:    {p90:.2f}s")
        print(f"  P95:    {p95:.2f}s")
    
    # Confidence distribution
    if successful:
        confidences = [r["confidence"] for r in successful]
        high_conf = sum(1 for c in confidences if c >= 0.8)
        med_conf = sum(1 for c in confidences if 0.5 <= c < 0.8)
        low_conf = sum(1 for c in confidences if c < 0.5)
        
        print()
        print("Confidence Distribution:")
        print(f"  High (>=0.8): {high_conf} ({high_conf/len(confidences)*100:.0f}%)")
        print(f"  Medium:       {med_conf} ({med_conf/len(confidences)*100:.0f}%)")
        print(f"  Low (<0.5):   {low_conf} ({low_conf/len(confidences)*100:.0f}%)")
    
    # Source coverage
    if successful:
        sources = [r["sources"] for r in successful]
        print()
        print("Source Coverage:")
        print(f"  Avg sources per query: {statistics.mean(sources):.1f}")
        print(f"  Queries with context:  {sum(1 for r in successful if r['has_context'])}")
    
    # Save results
    with open("/tmp/rag_benchmark_results.json", "w") as f:
        json.dump({
            "total_queries": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "total_time": total_time,
            "throughput_qpm": qpm,
            "latency_avg": statistics.mean(durations) if durations else 0,
            "latency_p90": p90 if durations else 0,
            "results": results,
        }, f, indent=2)
    
    print()
    print(f"Results saved to: /tmp/rag_benchmark_results.json")
    
    return success_rate >= 90


if __name__ == "__main__":
    # Run benchmark
    success = run_batch_test(num_queries=20, concurrency=2)
    exit(0 if success else 1)
