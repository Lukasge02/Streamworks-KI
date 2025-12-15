#!/usr/bin/env python3
"""
RAG Quality Test Suite

Comprehensive testing of the RAG system:
1. Accuracy tests (correct answers)
2. Completeness tests (full information)
3. Source attribution tests
4. Performance tests
5. Edge case tests
"""

import requests
import json
import time
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"

# Test cases with expected content
TEST_CASES = [
    # ========== ACCURACY TESTS ==========
    {
        "name": "Stream Definition",
        "query": "Was ist ein Stream in StreamWorks?",
        "expected_keywords": ["zentrale Einheit", "Name", "Jobs", "Schedule", "Tags"],
        "category": "accuracy",
    },
    {
        "name": "Job Types",
        "query": "Welche Job-Typen gibt es in StreamWorks?",
        "expected_keywords": ["Command", "Script", "SQL", "File Transfer"],
        "category": "accuracy",
    },
    {
        "name": "Hardware Requirements",
        "query": "Welche Hardware wird für StreamWorks empfohlen?",
        "expected_keywords": ["CPU", "RAM", "SSD", "GB"],
        "category": "accuracy",
    },
    {
        "name": "API Base URL",
        "query": "Wie lautet die Base URL für die StreamWorks API?",
        "expected_keywords": ["api.streamworks", "/v2", "REST"],
        "category": "accuracy",
    },
    {
        "name": "Error Codes",
        "query": "Welche Fehlercodes gibt es in StreamWorks?",
        "expected_keywords": ["SW-1001", "SW-1002", "Datenbankverbindung", "Authentifizierung"],
        "category": "accuracy",
    },
    
    # ========== COMPLETENESS TESTS ==========
    {
        "name": "Installation Steps",
        "query": "Wie installiere ich StreamWorks Schritt für Schritt?",
        "expected_keywords": ["Repository", "apt install", "Datenbank", "Konfiguration", "systemctl"],
        "category": "completeness",
    },
    {
        "name": "Mandant Explanation",
        "query": "Erkläre das Mandanten-Konzept in StreamWorks",
        "expected_keywords": ["Multi-Tenancy", "isolierte Daten", "Benutzer", "Administratoren"],
        "category": "completeness",
    },
    {
        "name": "Webhook Events",
        "query": "Welche Webhook-Events gibt es und wie sieht der Payload aus?",
        "expected_keywords": ["stream.started", "stream.completed", "stream.failed", "Payload", "JSON"],
        "category": "completeness",
    },
    
    # ========== CONFIGURATION TESTS ==========
    {
        "name": "Environment Variables",
        "query": "Welche Umgebungsvariablen muss ich für StreamWorks setzen?",
        "expected_keywords": ["STREAMWORKS_DB_HOST", "STREAMWORKS_LOG_LEVEL", "MAX_WORKERS"],
        "category": "configuration",
    },
    {
        "name": "Database Config",
        "query": "Wie konfiguriere ich die Datenbank für StreamWorks?",
        "expected_keywords": ["PostgreSQL", "host", "port", "5432", "password"],
        "category": "configuration",
    },
    
    # ========== TROUBLESHOOTING TESTS ==========
    {
        "name": "Connection Error",
        "query": "Was mache ich bei SW-1001 Datenbankverbindung fehlgeschlagen?",
        "expected_keywords": ["DB-Host", "Port", "prüfen"],
        "category": "troubleshooting",
    },
    {
        "name": "Log Location",
        "query": "Wo finde ich die StreamWorks Logs?",
        "expected_keywords": ["/var/log/streamworks", "Windows", "ProgramData", "Logs"],
        "category": "troubleshooting",
    },
    
    # ========== API TESTS ==========
    {
        "name": "Create Stream API",
        "query": "Wie erstelle ich einen neuen Stream per API?",
        "expected_keywords": ["POST", "/streams", "name", "schedule", "201"],
        "category": "api",
    },
    {
        "name": "Rate Limiting",
        "query": "Wie funktioniert Rate Limiting in der StreamWorks API?",
        "expected_keywords": ["100", "Anfragen", "Minute", "X-RateLimit"],
        "category": "api",
    },
    
    # ========== EDGE CASES ==========
    {
        "name": "Non-Existent Topic",
        "query": "Wie integriere ich StreamWorks mit Kubernetes?",
        "expected_keywords": [],  # Should say it doesn't know
        "category": "edge_case",
        "expect_no_context": True,
    },
]


def query_rag(query: str, num_chunks: int = 5) -> Dict[str, Any]:
    """Send query to RAG API"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/documents/chat",
            json={"query": query, "num_chunks": num_chunks},
            timeout=60,
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def check_keywords(answer: str, keywords: List[str]) -> tuple[int, int, List[str]]:
    """Check how many expected keywords are in the answer"""
    found = []
    missing = []
    answer_lower = answer.lower()
    
    for kw in keywords:
        if kw.lower() in answer_lower:
            found.append(kw)
        else:
            missing.append(kw)
    
    return len(found), len(keywords), missing


def run_tests():
    """Run all test cases"""
    print("=" * 70)
    print("🧪 RAG QUALITY TEST SUITE")
    print("=" * 70)
    print()
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "by_category": {},
        "details": [],
    }
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"[{i}/{len(TEST_CASES)}] Testing: {test['name']}")
        print(f"    Query: {test['query'][:60]}...")
        
        start_time = time.time()
        response = query_rag(test["query"])
        duration = time.time() - start_time
        
        results["total"] += 1
        
        # Check for errors
        if "error" in response:
            print(f"    ❌ ERROR: {response['error']}")
            results["failed"] += 1
            continue
        
        answer = response.get("answer", "")
        sources = response.get("sources", [])
        confidence = response.get("confidence", 0)
        has_context = response.get("has_context", False)
        
        # Check edge case (expect no context)
        if test.get("expect_no_context"):
            if not has_context or confidence < 0.3:
                print(f"    ✅ PASS: Correctly indicated no relevant info (confidence: {confidence})")
                results["passed"] += 1
            else:
                print(f"    ❌ FAIL: Should have indicated no context, but confidence={confidence}")
                results["failed"] += 1
            print()
            continue
        
        # Check keywords
        found, total, missing = check_keywords(answer, test["expected_keywords"])
        score = found / total if total > 0 else 0
        
        test_passed = score >= 0.6 and has_context  # 60% keywords found = pass
        
        if test_passed:
            print(f"    ✅ PASS: {found}/{total} keywords ({score:.0%}), {len(sources)} sources, {duration:.1f}s")
            results["passed"] += 1
        else:
            print(f"    ❌ FAIL: {found}/{total} keywords ({score:.0%})")
            if missing:
                print(f"       Missing: {', '.join(missing[:3])}...")
            results["failed"] += 1
        
        # Track by category
        cat = test["category"]
        if cat not in results["by_category"]:
            results["by_category"][cat] = {"passed": 0, "failed": 0}
        if test_passed:
            results["by_category"][cat]["passed"] += 1
        else:
            results["by_category"][cat]["failed"] += 1
        
        results["details"].append({
            "name": test["name"],
            "passed": test_passed,
            "score": score,
            "confidence": confidence,
            "duration": duration,
            "sources_count": len(sources),
        })
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    print(f"Total: {results['passed']}/{results['total']} passed ({results['passed']/results['total']*100:.0f}%)")
    print()
    print("By Category:")
    for cat, stats in results["by_category"].items():
        total = stats["passed"] + stats["failed"]
        print(f"  {cat}: {stats['passed']}/{total}")
    
    print()
    print("Performance:")
    durations = [d["duration"] for d in results["details"]]
    if durations:
        print(f"  Avg response time: {sum(durations)/len(durations):.2f}s")
        print(f"  Max response time: {max(durations):.2f}s")
    
    return results


if __name__ == "__main__":
    results = run_tests()
    
    # Save results
    with open("/tmp/rag_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print()
    print(f"Results saved to: /tmp/rag_test_results.json")
    
    # Exit code based on pass rate
    pass_rate = results["passed"] / results["total"] if results["total"] > 0 else 0
    exit(0 if pass_rate >= 0.7 else 1)
