#!/usr/bin/env python3
"""
Test Generation Evaluation Script

Prüft ob alle Use Cases, Business Rules und Error Codes aus einem DDD
als Testfälle generiert wurden.
"""

import json
import sys
import re
from typing import Dict, List, Set
from pathlib import Path

# Erwartete Requirements aus dem Test-DDD
EXPECTED_USE_CASES = {
    "UC-001", "UC-002", "UC-003", "UC-004", "UC-005"
}

EXPECTED_BUSINESS_RULES = {
    "BR-001", "BR-002", "BR-003", "BR-004", "BR-005", "BR-006", "BR-007", "BR-008"
}

EXPECTED_ERROR_CODES = {
    "E-0001", "E-0002", "E-0003", "E-0004", "E-0005", "E-0006",
    "E-0007", "E-0008", "E-0009", "E-0010", "E-0011"
}


def extract_requirements_from_ddd(ddd_content: str) -> Dict[str, Set[str]]:
    """Extrahiert Requirements aus DDD-Text."""
    found = {
        "use_cases": set(),
        "business_rules": set(),
        "error_codes": set(),
    }

    # Use Cases
    uc_pattern = r"UC-\d{3}"
    for match in re.finditer(uc_pattern, ddd_content):
        found["use_cases"].add(match.group())

    # Business Rules
    br_pattern = r"BR-\d{3}"
    for match in re.finditer(br_pattern, ddd_content):
        found["business_rules"].add(match.group())

    # Error Codes
    ec_pattern = r"E-\d{4}"
    for match in re.finditer(ec_pattern, ddd_content):
        found["error_codes"].add(match.group())

    return found


def extract_requirements_from_test_plan(plan_content: str) -> Dict[str, Set[str]]:
    """Extrahiert Requirements aus generiertem Testplan."""
    found = {
        "use_cases": set(),
        "business_rules": set(),
        "error_codes": set(),
    }

    try:
        plan_data = json.loads(plan_content)
        
        # Handle different formats
        if isinstance(plan_data, dict):
            if plan_data.get("status") == "completed" and plan_data.get("data"):
                data = plan_data["data"]
            elif plan_data.get("format") == "structured_v2" and plan_data.get("data"):
                data = plan_data["data"]
            else:
                data = plan_data

            # Extract from coverage analysis
            if "coverage" in data:
                coverage = data["coverage"]
                if "covered_use_cases" in coverage:
                    found["use_cases"] = set(coverage["covered_use_cases"])
                if "covered_business_rules" in coverage:
                    found["business_rules"] = set(coverage["covered_business_rules"])
                if "covered_error_codes" in coverage:
                    found["error_codes"] = set(coverage["covered_error_codes"])

            # Also check test cases for related_requirements
            if "test_cases" in data:
                for tc in data["test_cases"]:
                    if "related_requirements" in tc:
                        for req in tc["related_requirements"]:
                            if req.startswith("UC-"):
                                found["use_cases"].add(req)
                            elif req.startswith("BR-"):
                                found["business_rules"].add(req)
                            elif req.startswith("E-"):
                                found["error_codes"].add(req)

    except json.JSONDecodeError:
        # Try to extract from markdown/text
        uc_pattern = r"UC-\d{3}"
        for match in re.finditer(uc_pattern, plan_content):
            found["use_cases"].add(match.group())

        br_pattern = r"BR-\d{3}"
        for match in re.finditer(br_pattern, plan_content):
            found["business_rules"].add(match.group())

        ec_pattern = r"E-\d{4}"
        for match in re.finditer(ec_pattern, plan_content):
            found["error_codes"].add(match.group())

    return found


def evaluate_coverage(
    expected: Dict[str, Set[str]],
    found: Dict[str, Set[str]]
) -> Dict[str, Dict]:
    """Bewertet die Coverage."""
    results = {}

    for req_type in ["use_cases", "business_rules", "error_codes"]:
        expected_set = expected.get(req_type, set())
        found_set = found.get(req_type, set())

        missing = expected_set - found_set
        extra = found_set - expected_set
        covered = expected_set & found_set

        total = len(expected_set)
        coverage_pct = (len(covered) / total * 100) if total > 0 else 0

        results[req_type] = {
            "expected": total,
            "found": len(found_set),
            "covered": len(covered),
            "missing": list(missing),
            "extra": list(extra),
            "coverage_percentage": round(coverage_pct, 1),
        }

    return results


def print_evaluation_report(results: Dict[str, Dict]):
    """Gibt einen detaillierten Evaluations-Report aus."""
    print("\n" + "=" * 70)
    print("TEST GENERATION EVALUATION REPORT")
    print("=" * 70 + "\n")

    total_expected = 0
    total_covered = 0

    for req_type, data in results.items():
        type_name = req_type.replace("_", " ").title()
        print(f"📊 {type_name}:")
        print(f"   Erwartet:     {data['expected']}")
        print(f"   Gefunden:     {data['found']}")
        print(f"   Abgedeckt:    {data['covered']}")
        print(f"   Coverage:     {data['coverage_percentage']}%")

        if data["missing"]:
            print(f"   ❌ Fehlend:   {', '.join(sorted(data['missing']))}")
        else:
            print(f"   ✅ Vollständig abgedeckt!")

        if data["extra"]:
            print(f"   ℹ️  Zusätzlich: {', '.join(sorted(data['extra']))}")

        print()
        total_expected += data["expected"]
        total_covered += data["covered"]

    overall_coverage = (total_covered / total_expected * 100) if total_expected > 0 else 0
    print("-" * 70)
    print(f"📈 GESAMT-COVERAGE: {round(overall_coverage, 1)}% ({total_covered}/{total_expected})")
    print("=" * 70 + "\n")

    # Status
    all_covered = all(
        len(data["missing"]) == 0 for data in results.values()
    )

    if all_covered:
        print("✅ ERFOLG: Alle Requirements wurden als Testfälle generiert!")
        return 0
    else:
        print("⚠️  WARNUNG: Einige Requirements fehlen in den generierten Testfällen.")
        return 1


def main():
    """Hauptfunktion."""
    if len(sys.argv) < 2:
        print("Usage: python evaluate_test_generation.py <test_plan_json_file> [ddd_file]")
        print("\nBeispiel:")
        print("  python evaluate_test_generation.py test_plan.json test_ddd_comprehensive.md")
        sys.exit(1)

    plan_file = Path(sys.argv[1])
    if not plan_file.exists():
        print(f"❌ Fehler: Datei {plan_file} nicht gefunden!")
        sys.exit(1)

    # Lade Testplan
    with open(plan_file, "r", encoding="utf-8") as f:
        plan_content = f.read()

    # Lade DDD falls angegeben
    expected = {
        "use_cases": EXPECTED_USE_CASES,
        "business_rules": EXPECTED_BUSINESS_RULES,
        "error_codes": EXPECTED_ERROR_CODES,
    }

    if len(sys.argv) >= 3:
        ddd_file = Path(sys.argv[2])
        if ddd_file.exists():
            with open(ddd_file, "r", encoding="utf-8") as f:
                ddd_content = f.read()
            expected = extract_requirements_from_ddd(ddd_content)
            print(f"📄 DDD geladen: {ddd_file}")
        else:
            print(f"⚠️  Warnung: DDD-Datei {ddd_file} nicht gefunden, verwende Standard-Requirements")

    print(f"📋 Testplan geladen: {plan_file}\n")

    # Extrahiere Requirements aus Testplan
    found = extract_requirements_from_test_plan(plan_content)

    # Evaluierung
    results = evaluate_coverage(expected, found)

    # Report
    exit_code = print_evaluation_report(results)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
