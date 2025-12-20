"""
AI Testing Utilities

Framework for testing AI/LLM-dependent code including:
- Response quality metrics
- Golden test case management
- Regression detection
- LLM-as-judge evaluation patterns

Usage:
    from tests.ai.ai_testing_utils import AITestEvaluator, GoldenTestManager
    
    evaluator = AITestEvaluator()
    score = evaluator.evaluate_response(response, expected_keywords=["login", "user"])
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import re


@dataclass
class EvaluationResult:
    """Result of an AI response evaluation."""
    passed: bool
    score: float  # 0.0 to 1.0
    metrics: Dict[str, float]
    issues: List[str]
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GoldenTestCase:
    """A golden test case for AI response evaluation."""
    id: str
    query: str
    expected_keywords: List[str]
    min_confidence: float = 0.7
    max_response_time: float = 30.0  # seconds
    expected_sources_count: Optional[int] = None
    negative_keywords: List[str] = field(default_factory=list)
    category: str = "general"
    description: str = ""


class AITestEvaluator:
    """
    Evaluator for AI/LLM responses.
    
    Provides multiple evaluation strategies:
    - Keyword-based evaluation
    - Confidence scoring
    - Response time checks
    - Source validation
    """
    
    def __init__(self):
        self.metrics_history: List[Dict] = []
    
    def evaluate_response(
        self,
        response: Dict[str, Any],
        expected_keywords: List[str] = None,
        negative_keywords: List[str] = None,
        min_confidence: float = 0.5,
        min_sources: int = 0,
        max_response_time: float = None,
        actual_response_time: float = None,
    ) -> EvaluationResult:
        """
        Evaluate an AI response against multiple criteria.
        
        Args:
            response: The response dict with 'answer', 'confidence', 'sources'
            expected_keywords: Keywords that should be in the answer
            negative_keywords: Keywords that should NOT be in the answer
            min_confidence: Minimum confidence score
            min_sources: Minimum number of sources
            max_response_time: Maximum allowed response time
            actual_response_time: Actual time taken
        
        Returns:
            EvaluationResult with pass/fail and detailed metrics
        """
        issues = []
        metrics = {}
        
        answer = response.get("answer", "")
        confidence = response.get("confidence", 0)
        sources = response.get("sources", [])
        
        # Keyword evaluation
        if expected_keywords:
            found = sum(1 for kw in expected_keywords if kw.lower() in answer.lower())
            keyword_score = found / len(expected_keywords)
            metrics["keyword_coverage"] = keyword_score
            
            if keyword_score < 0.5:
                missing = [kw for kw in expected_keywords if kw.lower() not in answer.lower()]
                issues.append(f"Missing keywords: {missing}")
        else:
            metrics["keyword_coverage"] = 1.0
        
        # Negative keyword check
        if negative_keywords:
            found_negatives = [kw for kw in negative_keywords if kw.lower() in answer.lower()]
            if found_negatives:
                metrics["negative_keyword_violations"] = len(found_negatives)
                issues.append(f"Found negative keywords: {found_negatives}")
            else:
                metrics["negative_keyword_violations"] = 0
        
        # Confidence check
        metrics["confidence"] = confidence
        if confidence < min_confidence:
            issues.append(f"Confidence too low: {confidence:.2f} < {min_confidence}")
        
        # Source count check
        metrics["source_count"] = len(sources)
        if len(sources) < min_sources:
            issues.append(f"Insufficient sources: {len(sources)} < {min_sources}")
        
        # Response time check
        if max_response_time and actual_response_time:
            metrics["response_time"] = actual_response_time
            if actual_response_time > max_response_time:
                issues.append(f"Response too slow: {actual_response_time:.2f}s > {max_response_time}s")
        
        # Calculate overall score
        scores = [
            metrics.get("keyword_coverage", 1.0),
            min(confidence / min_confidence, 1.0) if min_confidence > 0 else 1.0,
            1.0 if len(sources) >= min_sources else len(sources) / max(min_sources, 1),
        ]
        overall_score = sum(scores) / len(scores)
        
        passed = len(issues) == 0
        
        result = EvaluationResult(
            passed=passed,
            score=overall_score,
            metrics=metrics,
            issues=issues,
            details={"answer_length": len(answer), "source_ids": [s.get("doc_id") for s in sources]}
        )
        
        # Store for history
        self.metrics_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "passed": passed,
            "score": overall_score,
            "metrics": metrics,
        })
        
        return result
    
    def evaluate_batch(
        self,
        responses: List[Dict[str, Any]],
        test_cases: List[GoldenTestCase],
    ) -> Dict[str, Any]:
        """
        Evaluate a batch of responses against golden test cases.
        
        Returns aggregate statistics.
        """
        results = []
        
        for response, test_case in zip(responses, test_cases):
            result = self.evaluate_response(
                response,
                expected_keywords=test_case.expected_keywords,
                negative_keywords=test_case.negative_keywords,
                min_confidence=test_case.min_confidence,
                min_sources=test_case.expected_sources_count or 0,
            )
            results.append({
                "test_id": test_case.id,
                "passed": result.passed,
                "score": result.score,
                "issues": result.issues,
            })
        
        passed_count = sum(1 for r in results if r["passed"])
        
        return {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "pass_rate": passed_count / len(results) if results else 0,
            "avg_score": sum(r["score"] for r in results) / len(results) if results else 0,
            "results": results,
        }


class GoldenTestManager:
    """
    Manages golden test cases for AI regression testing.
    
    Provides:
    - Test case storage and retrieval
    - Result history tracking
    - Regression detection
    """
    
    def __init__(self, storage_path: str = None):
        self.test_cases: Dict[str, GoldenTestCase] = {}
        self.result_history: List[Dict] = []
        self.storage_path = storage_path
    
    def add_test_case(self, test_case: GoldenTestCase):
        """Add or update a golden test case."""
        self.test_cases[test_case.id] = test_case
    
    def add_test_cases(self, test_cases: List[GoldenTestCase]):
        """Add multiple test cases."""
        for tc in test_cases:
            self.add_test_case(tc)
    
    def get_test_case(self, test_id: str) -> Optional[GoldenTestCase]:
        """Get a test case by ID."""
        return self.test_cases.get(test_id)
    
    def get_all_test_cases(self, category: str = None) -> List[GoldenTestCase]:
        """Get all test cases, optionally filtered by category."""
        cases = list(self.test_cases.values())
        if category:
            cases = [tc for tc in cases if tc.category == category]
        return cases
    
    def record_result(
        self,
        test_id: str,
        passed: bool,
        score: float,
        details: Dict[str, Any] = None
    ):
        """Record a test result for history."""
        self.result_history.append({
            "test_id": test_id,
            "timestamp": datetime.utcnow().isoformat(),
            "passed": passed,
            "score": score,
            "details": details or {},
        })
    
    def detect_regression(
        self,
        current_results: Dict[str, float],
        threshold: float = 0.1
    ) -> List[Dict]:
        """
        Detect regressions compared to historical results.
        
        Args:
            current_results: Dict of test_id -> score
            threshold: Score drop threshold for regression
        
        Returns:
            List of detected regressions
        """
        if len(self.result_history) < 2:
            return []
        
        # Get previous scores by test_id
        prev_scores = {}
        for result in self.result_history[-50:]:  # Last 50 results
            test_id = result["test_id"]
            if test_id not in prev_scores:
                prev_scores[test_id] = []
            prev_scores[test_id].append(result["score"])
        
        regressions = []
        for test_id, current_score in current_results.items():
            if test_id in prev_scores and prev_scores[test_id]:
                avg_prev = sum(prev_scores[test_id]) / len(prev_scores[test_id])
                if current_score < avg_prev - threshold:
                    regressions.append({
                        "test_id": test_id,
                        "current_score": current_score,
                        "previous_avg": avg_prev,
                        "drop": avg_prev - current_score,
                    })
        
        return regressions


# Pre-defined golden test cases for RAG
RAG_GOLDEN_TESTS = [
    GoldenTestCase(
        id="rag-factual-001",
        query="Was ist der Default Timeout für HTTP Jobs?",
        expected_keywords=["60", "seconds", "Sekunden"],
        min_confidence=0.8,
        category="factual",
        description="Test factual recall for timeout value",
    ),
    GoldenTestCase(
        id="rag-technical-001",
        query="Welche SAP Library wird benötigt?",
        expected_keywords=["JCo", "v3.1"],
        min_confidence=0.7,
        category="technical",
        description="Test technical term retrieval",
    ),
    GoldenTestCase(
        id="rag-procedural-001",
        query="Wie funktioniert die Retry Logik?",
        expected_keywords=["exponentiell", "backoff"],
        min_confidence=0.7,
        category="procedural",
        description="Test procedural knowledge retrieval",
    ),
    GoldenTestCase(
        id="rag-negative-001",
        query="Wie backe ich einen Kuchen?",
        expected_keywords=["keine relevanten", "nicht gefunden"],
        min_confidence=0.0,  # Should be low
        negative_keywords=["Rezept", "Mehl", "Zucker"],
        category="negative",
        description="Test rejection of irrelevant queries",
    ),
]

# Pre-defined golden test cases for test plan generation
TEST_PLAN_GOLDEN_TESTS = [
    GoldenTestCase(
        id="testplan-structure-001",
        query="Generate test plan for login functionality",
        expected_keywords=["TC-", "happy_path", "error_handling"],
        min_confidence=0.8,
        category="structure",
        description="Test plan structure validation",
    ),
    GoldenTestCase(
        id="testplan-coverage-001",
        query="Generate comprehensive test plan",
        expected_keywords=["critical", "high", "UC-", "BR-"],
        min_confidence=0.8,
        category="coverage",
        description="Test coverage analysis validation",
    ),
]


def assert_response_quality(
    response: Dict[str, Any],
    expected_keywords: List[str] = None,
    min_confidence: float = 0.5,
    error_message: str = None,
):
    """
    Pytest assertion helper for AI response quality.
    
    Raises AssertionError with detailed message if quality checks fail.
    """
    evaluator = AITestEvaluator()
    result = evaluator.evaluate_response(
        response,
        expected_keywords=expected_keywords,
        min_confidence=min_confidence,
    )
    
    if not result.passed:
        msg = error_message or "AI response quality check failed"
        issue_str = "\n".join(f"  - {issue}" for issue in result.issues)
        raise AssertionError(f"{msg}\nScore: {result.score:.2f}\nIssues:\n{issue_str}")
