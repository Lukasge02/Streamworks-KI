#!/usr/bin/env python3
"""
Quick Test für Enhanced Job-Type Detection (ohne LLM)
Testet nur die Pattern-basierte Erkennung
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Enhanced Services
from services.ai.enhanced_job_type_detector import get_enhanced_job_type_detector

def print_header():
    """Print test header"""
    print("=" * 80)
    print("🚀 QUICK JOB-TYPE DETECTION TEST")
    print("=" * 80)
    print("🎯 Teste nur die Enhanced Job-Schema-Erkennung (ohne LLM)")
    print("📊 Problem-Beispiele aus Screenshots")
    print("=" * 80)
    print()

def test_job_type_detection():
    """Test Enhanced Job-Type Detection"""
    detector = get_enhanced_job_type_detector()

    # Problem-Beispiele aus Screenshots + Enhanced Tests
    test_cases = [
        {
            "title": "Screenshot Problem 1 - Ing_Job",
            "input": "_ing_Job als Stream-Name",
            "expected": None,  # Sollte NICHT automatisch STANDARD werden
            "comment": "Zu wenig Info für automatische Klassifikation"
        },
        {
            "title": "Screenshot Problem 2 - Agent_Test_Execution",
            "input": "Agent_Test_Execution als Stream-Name",
            "expected": "STANDARD",  # Sollte durch 'Agent' Pattern erkannt werden
            "comment": "Könnte durch Agent-Pattern erkannt werden"
        },
        {
            "title": "Enhanced Test - Explicit File Transfer",
            "input": "Datentransfer von GT123_Server nach BASF_Agent für alle CSV Dateien",
            "expected": "FILE_TRANSFER",
            "comment": "Sollte durch 'Datentransfer' + 'von X nach Y' Pattern erkannt werden"
        },
        {
            "title": "Enhanced Test - SAP Export",
            "input": "SAP Export aus System PA1_100 mit Report ZTV_001",
            "expected": "SAP",
            "comment": "Sollte durch 'SAP' + 'System' + 'Report' erkannt werden"
        },
        {
            "title": "Enhanced Test - Python Script",
            "input": "Python Script ausführen: python analyze_data.py --input=/data",
            "expected": "STANDARD",
            "comment": "Sollte durch 'python' + 'script' + 'ausführen' erkannt werden"
        },
        {
            "title": "Enhanced Test - Transfer zwischen Servern",
            "input": "Transfer zwischen Server001 und Server002 für PDF Dateien",
            "expected": "FILE_TRANSFER",
            "comment": "Sollte durch 'Transfer zwischen X und Y' Pattern erkannt werden"
        },
        {
            "title": "Fuzzy Test - Schreibfehler",
            "input": "datentrasnfer von Agent001 zu Agent002",  # Schreibfehler in 'datentransfer'
            "expected": "FILE_TRANSFER",
            "comment": "Sollte durch Fuzzy-Matching erkannt werden"
        },
        {
            "title": "Context Test - Multiple Keywords",
            "input": "übertragung von dateien zwischen servern mit sync",
            "expected": "FILE_TRANSFER",
            "comment": "Sollte durch Multiple FILE_TRANSFER Keywords erkannt werden"
        },
        {
            "title": "Edge Case - Unclear Input",
            "input": "stream für datenverarbeitung",
            "expected": None,  # Sollte unclear sein
            "comment": "Zu vage für sichere Klassifikation"
        }
    ]

    print("🔍 TESTING ENHANCED JOB-TYPE DETECTION")
    print("=" * 50)

    success_count = 0
    total_count = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 TEST {i}: {test_case['title']}")
        print(f"Input: \"{test_case['input']}\"")
        print(f"Expected: {test_case['expected']}")
        print(f"Comment: {test_case['comment']}")
        print("-" * 50)

        # Teste Job-Type Detection
        result = detector.detect_job_type(test_case["input"])

        print(f"🎯 RESULT:")
        print(f"   Detected: {result.detected_job_type}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Method: {result.detection_method}")

        if result.alternative_candidates:
            alternatives = ", ".join([f"{jt} ({conf:.1%})" for jt, conf in result.alternative_candidates[:3]])
            print(f"   Alternatives: {alternatives}")

        # Bewerte Ergebnis
        expected = test_case["expected"]
        actual = result.detected_job_type

        if expected == actual:
            status = "✅ SUCCESS"
            success_count += 1
        elif expected is None and actual is None:
            status = "✅ SUCCESS (correctly uncertain)"
            success_count += 1
        elif expected is None and result.confidence < 0.65:
            status = "✅ SUCCESS (low confidence as expected)"
            success_count += 1
        else:
            status = "❌ FAILED"

        print(f"📈 EVALUATION: {status}")
        print(f"   Expected: {expected} | Got: {actual}")

        print()
        print("=" * 80)
        print()

    # Final Results
    success_rate = (success_count / total_count) * 100
    print("🎉 FINAL RESULTS:")
    print("=" * 20)
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    print()

    if success_rate >= 80:
        print("🚀 EXCELLENT! Enhanced Detection System is working great!")
    elif success_rate >= 60:
        print("⚠️  GOOD, but needs some improvements")
    else:
        print("❌ NEEDS WORK - Major improvements required")

    print()
    print("🔧 IMPROVEMENTS IMPLEMENTED:")
    print("   • Multi-layer pattern matching")
    print("   • Fuzzy matching for typos")
    print("   • Context-aware keyword analysis")
    print("   • German language optimizations")
    print("   • Confidence-based thresholds")
    print("=" * 80)

if __name__ == "__main__":
    print_header()
    test_job_type_detection()