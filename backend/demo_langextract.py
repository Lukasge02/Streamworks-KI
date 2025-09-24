#!/usr/bin/env python3
"""
LangExtract Integration Demo
Live demonstration der Source-Grounded Parameter Extraction
"""

import json
import sys
import os
import time
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def display_demo_header():
    """Display demo header"""
    print("=" * 80)
    print("🚀 LANGEXTRACT INTEGRATION DEMO")
    print("=" * 80)
    print("✨ Source-Grounded Parameter Extraction für Streamworks-KI")
    print("🎯 Revolutionäre Genauigkeit durch Text-zu-Parameter Mapping")
    print("=" * 80)
    print()

def simulate_extraction(user_input: str, job_type: str) -> Dict[str, Any]:
    """Simulate LangExtract parameter extraction"""

    # Demo extraction results based on job type
    if job_type == "FILE_TRANSFER":
        return {
            "detected_job_type": "FILE_TRANSFER",
            "job_type_confidence": 0.95,
            "stream_parameters": [
                {
                    "name": "source_system",
                    "value": "PROD-DB01",
                    "confidence": 0.92,
                    "source_text": "PROD-DB01",
                    "character_offsets": [25, 34],
                    "extraction_method": "direct_mention",
                    "context": "from server PROD-DB01 to"
                },
                {
                    "name": "target_system",
                    "value": "STAGING-ENV",
                    "confidence": 0.89,
                    "source_text": "STAGING-ENV",
                    "character_offsets": [38, 49],
                    "extraction_method": "direct_mention",
                    "context": "to STAGING-ENV using"
                },
                {
                    "name": "protocol",
                    "value": "SFTP",
                    "confidence": 0.97,
                    "source_text": "SFTP",
                    "character_offsets": [56, 60],
                    "extraction_method": "direct_mention",
                    "context": "using SFTP protocol"
                }
            ],
            "job_parameters": [
                {
                    "name": "file_pattern",
                    "value": "*.csv",
                    "confidence": 0.88,
                    "source_text": "*.csv",
                    "character_offsets": [70, 75],
                    "extraction_method": "pattern_recognition",
                    "context": "files matching *.csv pattern"
                }
            ],
            "source_grounding_data": {
                "highlighted_ranges": [
                    [25, 34, "source_system"],
                    [38, 49, "target_system"],
                    [56, 60, "protocol"],
                    [70, 75, "file_pattern"]
                ],
                "full_text": user_input,
                "extraction_quality": "excellent",
                "overall_confidence": 0.915
            },
            "completion_percentage": 85.0,
            "missing_parameters": ["backup_location"],
            "suggested_questions": [
                "Wo sollen die Backup-Dateien gespeichert werden?",
                "Soll eine Komprimierung verwendet werden?"
            ]
        }

    elif job_type == "SAP":
        return {
            "detected_job_type": "SAP",
            "job_type_confidence": 0.93,
            "stream_parameters": [
                {
                    "name": "sap_system",
                    "value": "ERP-PROD",
                    "confidence": 0.96,
                    "source_text": "ERP-PROD",
                    "character_offsets": [20, 28],
                    "extraction_method": "sap_system_recognition",
                    "context": "from SAP system ERP-PROD"
                },
                {
                    "name": "table_name",
                    "value": "MARA",
                    "confidence": 0.94,
                    "source_text": "MARA",
                    "character_offsets": [35, 39],
                    "extraction_method": "sap_table_recognition",
                    "context": "table MARA for material"
                }
            ],
            "job_parameters": [
                {
                    "name": "extraction_mode",
                    "value": "incremental",
                    "confidence": 0.82,
                    "source_text": "delta",
                    "character_offsets": [55, 60],
                    "extraction_method": "synonym_mapping",
                    "context": "using delta extraction"
                }
            ],
            "source_grounding_data": {
                "highlighted_ranges": [
                    [20, 28, "sap_system"],
                    [35, 39, "table_name"],
                    [55, 60, "extraction_mode"]
                ],
                "full_text": user_input,
                "extraction_quality": "excellent",
                "overall_confidence": 0.906
            },
            "completion_percentage": 70.0,
            "missing_parameters": ["field_selection", "where_clause"]
        }

    else:  # STANDARD
        return {
            "detected_job_type": "STANDARD",
            "job_type_confidence": 0.87,
            "stream_parameters": [
                {
                    "name": "job_name",
                    "value": "DataSync_Daily",
                    "confidence": 0.91,
                    "source_text": "DataSync_Daily",
                    "character_offsets": [15, 29],
                    "extraction_method": "job_name_pattern",
                    "context": "batch job DataSync_Daily"
                }
            ],
            "job_parameters": [
                {
                    "name": "schedule",
                    "value": "daily",
                    "confidence": 0.85,
                    "source_text": "täglich",
                    "character_offsets": [40, 47],
                    "extraction_method": "schedule_mapping",
                    "context": "läuft täglich um"
                }
            ],
            "source_grounding_data": {
                "highlighted_ranges": [
                    [15, 29, "job_name"],
                    [40, 47, "schedule"]
                ],
                "full_text": user_input,
                "extraction_quality": "good",
                "overall_confidence": 0.88
            },
            "completion_percentage": 60.0,
            "missing_parameters": ["execution_time", "dependencies"]
        }

def display_extraction_result(result: Dict[str, Any]):
    """Display extraction result with source grounding visualization"""

    print(f"🎯 ERKANNTER JOB-TYP: {result['detected_job_type']} (Konfidenz: {result['job_type_confidence']:.1%})")
    print()

    # Display source grounding visualization
    print("📍 SOURCE GROUNDING VISUALIZATION:")
    text = result["source_grounding_data"]["full_text"]
    ranges = result["source_grounding_data"]["highlighted_ranges"]

    # Create highlighted text
    highlighted_text = ""
    last_pos = 0

    for start, end, param_name in ranges:
        highlighted_text += text[last_pos:start]
        highlighted_text += f"[{text[start:end]}]"
        last_pos = end
    highlighted_text += text[last_pos:]

    print(f"   {highlighted_text}")
    print()

    # Display extracted parameters
    print("⚙️  STREAM PARAMETER:")
    for param in result["stream_parameters"]:
        confidence_bar = "█" * int(param["confidence"] * 10) + "░" * (10 - int(param["confidence"] * 10))
        print(f"   • {param['name']}: {param['value']} [{confidence_bar}] {param['confidence']:.1%}")
        print(f"     📍 Quelle: \"{param['source_text']}\" (Position {param['character_offsets']})")

    if result.get("job_parameters"):
        print()
        print("🔧 JOB PARAMETER:")
        for param in result["job_parameters"]:
            confidence_bar = "█" * int(param["confidence"] * 10) + "░" * (10 - int(param["confidence"] * 10))
            print(f"   • {param['name']}: {param['value']} [{confidence_bar}] {param['confidence']:.1%}")
            print(f"     📍 Quelle: \"{param['source_text']}\" (Position {param['character_offsets']})")

    # Display quality metrics
    print()
    print("📊 QUALITÄTS-METRIKEN:")
    print(f"   • Vollständigkeit: {result['completion_percentage']:.1f}%")
    print(f"   • Gesamt-Konfidenz: {result['source_grounding_data']['overall_confidence']:.1%}")
    print(f"   • Extraktions-Qualität: {result['source_grounding_data']['extraction_quality']}")

    if result.get("missing_parameters"):
        print()
        print("❌ FEHLENDE PARAMETER:")
        for param in result["missing_parameters"]:
            print(f"   • {param}")

    if result.get("suggested_questions"):
        print()
        print("💡 VORGESCHLAGENE FRAGEN:")
        for question in result["suggested_questions"]:
            print(f"   • {question}")

def run_demo():
    """Run the LangExtract integration demo"""

    display_demo_header()

    # Demo scenarios
    scenarios = [
        {
            "title": "FILE_TRANSFER Scenario",
            "input": "Copy files from server PROD-DB01 to STAGING-ENV using SFTP protocol for *.csv files",
            "job_type": "FILE_TRANSFER"
        },
        {
            "title": "SAP Scenario",
            "input": "Extract data from SAP system ERP-PROD table MARA using delta extraction",
            "job_type": "SAP"
        },
        {
            "title": "STANDARD Scenario",
            "input": "Run batch job DataSync_Daily läuft täglich um 03:00",
            "job_type": "STANDARD"
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"📝 DEMO SCENARIO {i}: {scenario['title']}")
        print(f"User Input: \"{scenario['input']}\"")
        print()

        # Simulate processing
        print("🔄 LangExtract verarbeitet...")
        time.sleep(1)

        # Get extraction result
        result = simulate_extraction(scenario["input"], scenario["job_type"])

        # Display result
        display_extraction_result(result)

        print()
        print("-" * 80)
        print()

        if i < len(scenarios):
            input("⏎ Drücke Enter für nächstes Scenario...")
            print()

    # Final summary
    print("🎉 DEMO ABGESCHLOSSEN!")
    print()
    print("✨ LANGEXTRACT INTEGRATION HIGHLIGHTS:")
    print("   • 🎯 Source-Grounded Parameter Extraction")
    print("   • 📍 Exakte Text-zu-Parameter Zuordnung")
    print("   • 🔍 Automatische Job-Typ Erkennung")
    print("   • 📊 Konfidenz-basierte Qualitätsbewertung")
    print("   • 🎨 Interaktive Frontend-Visualisierung")
    print("   • ⚡ Real-time Parameter Correction")
    print()
    print("🚀 Streamworks-KI ist bereit für die Zukunft der Parameter-Extraktion!")
    print("=" * 80)

if __name__ == "__main__":
    run_demo()