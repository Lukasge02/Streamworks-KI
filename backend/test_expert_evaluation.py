#!/usr/bin/env python3
"""
🎯 EXPERT-LEVEL Q&A SYSTEM EVALUATION
Comprehensive testing by KI-Expert for 1.0-Grade performance
"""
import asyncio
import sys
import os
import logging
import time
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.perfect_qa_service import perfect_qa

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result with detailed metrics"""
    question: str
    answer: str
    expected_type: str
    actual_type: str
    confidence: float
    quality_score: float
    processing_time: float
    sources: List[str]
    evaluation_score: float
    feedback: str
    improvement_suggestions: List[str]

class ExpertEvaluator:
    """Expert-level evaluator for Q&A system"""
    
    def __init__(self):
        self.test_cases = [
            # Simple Facts - should be concise and direct
            {
                "question": "Was ist StreamWorks?",
                "expected_type": "simple_fact",
                "expected_length": (50, 150),
                "must_contain": ["StreamWorks", "Plattform", "Datenverarbeitung"],
                "quality_criteria": ["Präzise Definition", "Keine Wiederholungen", "Direkte Antwort"]
            },
            {
                "question": "Wer ist Arne Thiele?",
                "expected_type": "simple_fact",
                "expected_length": (20, 80),
                "must_contain": ["Arne Thiele", "Linux", "Ansprechpartner"],
                "quality_criteria": ["Kurz und präzise", "Klare Rollenbezeichnung"]
            },
            
            # How-To Questions - should be structured
            {
                "question": "Wie erstelle ich einen neuen Job?",
                "expected_type": "howto",
                "expected_length": (200, 600),
                "must_contain": ["POST", "jobs", "JSON"],
                "quality_criteria": ["Strukturierte Schritte", "Code-Beispiele", "Klare Anleitung"]
            },
            {
                "question": "Wie installiere ich StreamWorks?",
                "expected_type": "howto",
                "expected_length": (100, 400),
                "must_contain": ["Installation", "Schritt"],
                "quality_criteria": ["Chronologische Reihenfolge", "Praktische Anweisungen"]
            },
            
            # Complex Concepts - should be detailed
            {
                "question": "Sicherheitskonzept StreamWorks",
                "expected_type": "complex",
                "expected_length": (200, 800),
                "must_contain": ["Sicherheit", "Backup", "Authentifizierung"],
                "quality_criteria": ["Umfassende Erklärung", "Mehrere Aspekte", "Strukturiert"]
            },
            {
                "question": "Passwort-Richtlinien",
                "expected_type": "complex",
                "expected_length": (100, 300),
                "must_contain": ["Passwort", "Zeichen", "Tage"],
                "quality_criteria": ["Vollständige Richtlinien", "Klare Regeln"]
            },
            
            # List Questions - should use bullet points
            {
                "question": "Dashboard-Komponenten",
                "expected_type": "list",
                "expected_length": (200, 600),
                "must_contain": ["•", "Komponenten", "Dashboard"],
                "quality_criteria": ["Bullet Points", "Übersichtlich", "Vollständig"]
            },
            {
                "question": "Welche Funktionen hat StreamWorks?",
                "expected_type": "list",
                "expected_length": (150, 500),
                "must_contain": ["Batch", "Stream", "API"],
                "quality_criteria": ["Strukturierte Liste", "Kernfunktionen", "Verständlich"]
            },
            
            # Edge Cases - should handle gracefully
            {
                "question": "Unbekanntes Thema XYZ",
                "expected_type": "general",
                "expected_length": (30, 200),
                "must_contain": ["StreamWorks", "Dokumentation"],
                "quality_criteria": ["Höfliche Antwort", "Hilfsbereitschaft", "Verweis auf Support"]
            }
        ]
    
    async def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive evaluation with expert analysis"""
        print("🎯 STARTING EXPERT-LEVEL Q&A EVALUATION")
        print("=" * 80)
        
        results = []
        total_score = 0
        
        try:
            # Initialize system
            await perfect_qa.initialize()
            print("✅ System initialized successfully")
            
            # Run all test cases
            for i, test_case in enumerate(self.test_cases, 1):
                print(f"\n📋 Test {i}/{len(self.test_cases)}: {test_case['question']}")
                print("-" * 60)
                
                result = await self._evaluate_single_question(test_case)
                results.append(result)
                total_score += result.evaluation_score
                
                # Print detailed results
                self._print_test_result(result)
                
                # Brief pause between tests
                await asyncio.sleep(0.5)
            
            # Calculate final metrics
            avg_score = total_score / len(results)
            final_report = self._generate_final_report(results, avg_score)
            
            print("\n" + "=" * 80)
            print("🏆 FINAL EVALUATION REPORT")
            print("=" * 80)
            print(final_report)
            
            return {
                "average_score": avg_score,
                "results": results,
                "report": final_report,
                "grade_equivalent": self._calculate_grade(avg_score)
            }
            
        except Exception as e:
            logger.error(f"❌ Evaluation failed: {e}")
            return {"error": str(e)}
    
    async def _evaluate_single_question(self, test_case: Dict[str, Any]) -> TestResult:
        """Evaluate a single question with expert criteria"""
        question = test_case["question"]
        
        try:
            # Get answer from system
            start_time = time.time()
            result = await perfect_qa.ask(question)
            processing_time = time.time() - start_time
            
            # Analyze answer quality
            evaluation_score = self._calculate_evaluation_score(result, test_case)
            feedback = self._generate_feedback(result, test_case)
            improvements = self._suggest_improvements(result, test_case)
            
            return TestResult(
                question=question,
                answer=result.answer,
                expected_type=test_case["expected_type"],
                actual_type=result.question_type,
                confidence=result.confidence,
                quality_score=result.quality_score,
                processing_time=processing_time,
                sources=result.sources,
                evaluation_score=evaluation_score,
                feedback=feedback,
                improvement_suggestions=improvements
            )
            
        except Exception as e:
            logger.error(f"❌ Test failed for '{question}': {e}")
            return TestResult(
                question=question,
                answer="ERROR",
                expected_type=test_case["expected_type"],
                actual_type="error",
                confidence=0.0,
                quality_score=0.0,
                processing_time=0.0,
                sources=[],
                evaluation_score=0.0,
                feedback=f"System error: {e}",
                improvement_suggestions=["Fix system error"]
            )
    
    def _calculate_evaluation_score(self, result, test_case: Dict[str, Any]) -> float:
        """Calculate expert evaluation score (0-10)"""
        score = 0.0
        
        # 1. Type Recognition (2 points)
        if result.question_type == test_case["expected_type"]:
            score += 2.0
        elif result.question_type in ["general", "balanced"] and test_case["expected_type"] != "error":
            score += 1.0
        
        # 2. Answer Length Appropriateness (2 points)
        length = len(result.answer)
        expected_range = test_case["expected_length"]
        if expected_range[0] <= length <= expected_range[1]:
            score += 2.0
        elif expected_range[0] * 0.8 <= length <= expected_range[1] * 1.2:
            score += 1.5
        elif length > 0:
            score += 1.0
        
        # 3. Content Quality (2 points)
        must_contain = test_case["must_contain"]
        contained_count = sum(1 for term in must_contain if term.lower() in result.answer.lower())
        score += (contained_count / len(must_contain)) * 2.0
        
        # 4. Confidence Level (1 point)
        if result.confidence >= 0.8:
            score += 1.0
        elif result.confidence >= 0.6:
            score += 0.7
        elif result.confidence >= 0.4:
            score += 0.5
        
        # 5. Language Quality (1 point)
        answer_lower = result.answer.lower()
        if not any(filler in answer_lower for filler in ['basierend', 'laut', 'gemäß']):
            score += 0.5
        if len(result.answer.split('.')) <= 5:  # Not too verbose
            score += 0.3
        if any(marker in result.answer for marker in ['•', '1.', '2.']):
            score += 0.2
        
        # 6. Processing Speed (1 point)
        if result.processing_time <= 3.0:
            score += 1.0
        elif result.processing_time <= 5.0:
            score += 0.7
        elif result.processing_time <= 10.0:
            score += 0.5
        
        # 7. Source Utilization (1 point)
        if len(result.sources) >= 2:
            score += 1.0
        elif len(result.sources) >= 1:
            score += 0.7
        
        return min(score, 10.0)
    
    def _generate_feedback(self, result, test_case: Dict[str, Any]) -> str:
        """Generate expert feedback"""
        feedback = []
        
        # Type accuracy
        if result.question_type == test_case["expected_type"]:
            feedback.append("✅ Fragetyp korrekt erkannt")
        else:
            feedback.append(f"⚠️ Fragetyp: Erwartet {test_case['expected_type']}, erhalten {result.question_type}")
        
        # Length appropriateness
        length = len(result.answer)
        expected_range = test_case["expected_length"]
        if expected_range[0] <= length <= expected_range[1]:
            feedback.append("✅ Antwortlänge optimal")
        else:
            feedback.append(f"⚠️ Länge: {length} Zeichen (erwartet {expected_range[0]}-{expected_range[1]})")
        
        # Content quality
        must_contain = test_case["must_contain"]
        missing_terms = [term for term in must_contain if term.lower() not in result.answer.lower()]
        if not missing_terms:
            feedback.append("✅ Alle wichtigen Begriffe enthalten")
        else:
            feedback.append(f"⚠️ Fehlende Begriffe: {', '.join(missing_terms)}")
        
        # Confidence
        if result.confidence >= 0.8:
            feedback.append("✅ Hohe Confidence")
        elif result.confidence >= 0.6:
            feedback.append("⚠️ Mittlere Confidence")
        else:
            feedback.append("❌ Niedrige Confidence")
        
        return " | ".join(feedback)
    
    def _suggest_improvements(self, result, test_case: Dict[str, Any]) -> List[str]:
        """Suggest specific improvements"""
        improvements = []
        
        # Type-specific improvements
        if result.question_type != test_case["expected_type"]:
            improvements.append(f"Verbessere Fragetyp-Erkennung für {test_case['expected_type']}")
        
        # Length improvements
        length = len(result.answer)
        expected_range = test_case["expected_length"]
        if length < expected_range[0]:
            improvements.append("Erweitere Antwort mit mehr Details")
        elif length > expected_range[1]:
            improvements.append("Kürze Antwort auf das Wesentliche")
        
        # Content improvements
        must_contain = test_case["must_contain"]
        missing_terms = [term for term in must_contain if term.lower() not in result.answer.lower()]
        if missing_terms:
            improvements.append(f"Ergänze fehlende Begriffe: {', '.join(missing_terms)}")
        
        # Confidence improvements
        if result.confidence < 0.7:
            improvements.append("Verbessere Dokumenten-Matching für höhere Confidence")
        
        return improvements
    
    def _print_test_result(self, result: TestResult):
        """Print detailed test result"""
        print(f"📊 Ergebnis:")
        print(f"   Score: {result.evaluation_score:.1f}/10.0")
        print(f"   Confidence: {result.confidence:.0%}")
        print(f"   Quality: {result.quality_score:.2f}")
        print(f"   Time: {result.processing_time:.2f}s")
        print(f"   Type: {result.actual_type} (erwartet: {result.expected_type})")
        print(f"   Sources: {len(result.sources)}")
        print(f"   Feedback: {result.feedback}")
        if result.improvement_suggestions:
            print(f"   Verbesserungen: {'; '.join(result.improvement_suggestions)}")
        print(f"   Antwort: {result.answer[:200]}...")
    
    def _generate_final_report(self, results: List[TestResult], avg_score: float) -> str:
        """Generate comprehensive final report"""
        report = []
        
        # Overall performance
        report.append(f"📊 GESAMTBEWERTUNG: {avg_score:.1f}/10.0")
        report.append(f"🎯 Note-Äquivalent: {self._calculate_grade(avg_score)}")
        
        # Category analysis
        categories = {}
        for result in results:
            cat = result.expected_type
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result.evaluation_score)
        
        report.append("\n📈 KATEGORIE-ANALYSE:")
        for category, scores in categories.items():
            avg_cat_score = sum(scores) / len(scores)
            report.append(f"   {category}: {avg_cat_score:.1f}/10.0")
        
        # Key metrics
        avg_confidence = sum(r.confidence for r in results) / len(results)
        avg_time = sum(r.processing_time for r in results) / len(results)
        
        report.append(f"\n🔍 PERFORMANCE-METRIKEN:")
        report.append(f"   Durchschnittliche Confidence: {avg_confidence:.0%}")
        report.append(f"   Durchschnittliche Antwortzeit: {avg_time:.2f}s")
        
        # Top issues
        all_improvements = []
        for result in results:
            all_improvements.extend(result.improvement_suggestions)
        
        if all_improvements:
            from collections import Counter
            top_issues = Counter(all_improvements).most_common(3)
            report.append(f"\n🎯 HAUPT-VERBESSERUNGEN:")
            for issue, count in top_issues:
                report.append(f"   • {issue} ({count}x)")
        
        return "\n".join(report)
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate German grade equivalent"""
        if score >= 9.0:
            return "1.0 (Sehr gut)"
        elif score >= 8.0:
            return "1.7 (Gut)"
        elif score >= 7.0:
            return "2.3 (Gut)"
        elif score >= 6.0:
            return "3.0 (Befriedigend)"
        elif score >= 5.0:
            return "3.7 (Ausreichend)"
        else:
            return "4.0+ (Mangelhaft)"

async def main():
    """Run expert evaluation"""
    evaluator = ExpertEvaluator()
    results = await evaluator.run_comprehensive_evaluation()
    
    if "error" in results:
        print(f"❌ Evaluation failed: {results['error']}")
        return 1
    
    final_score = results["average_score"]
    grade = results["grade_equivalent"]
    
    print(f"\n🏆 FINAL RESULT: {final_score:.1f}/10.0 - {grade}")
    
    if final_score >= 8.0:
        print("🎉 EXCELLENT! System ready for 1.0 grade and salary increase!")
        return 0
    else:
        print("⚠️ System needs improvements for top grade")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Evaluation crashed: {e}")
        sys.exit(1)