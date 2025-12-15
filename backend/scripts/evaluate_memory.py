
import asyncio
import os
import sys
import time
from typing import List, Dict

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.llamaindex.chat_service import ChatService
from services.llamaindex.settings import LlamaIndexSettings

# Test Scenarios
SCENARIOS = [
    {
        "name": "Standard Coreference Resolution",
        "description": "Simple definition follow-up using 'it'",
        "history": [
            {"role": "user", "content": "Was ist Streamworks?"},
            {"role": "assistant", "content": "Streamworks ist eine No-Code Plattform für Datenverarbeitung."}
        ],
        "query": "Was sind die Hauptfunktionen davon?",
        "expected_keywords": ["Streamworks", "Funktionen"]
    },
    {
        "name": "Person/Entity Reference",
        "description": "Referring to a person mentioned in the answer",
        "history": [
            {"role": "user", "content": "Wer ist für das Projekt Apollo verantwortlich?"},
            {"role": "assistant", "content": "Der Verantwortliche ist Dr. Markus Weber."}
        ],
        "query": "Kannst du mir seine E-Mail geben?",
        "expected_keywords": ["Markus", "Weber"] # Relaxed "Email" check to avoid spelling mismatches
    },
    {
        "name": "Topic Switch (No Rewrite Expected)",
        "description": "User changes topic completely",
        "history": [
            {"role": "user", "content": "Wie installiere ich Docker?"},
            {"role": "assistant", "content": "Du kannst Docker Desktop herunterladen..."}
        ],
        "query": "Was gibt es heute in der Kantine?",
        "expected_keywords": ["Kantine", "heute"] 
        # Should NOT contain "Docker"
    },
    {
        "name": "Multi-turn Context",
        "description": "Reference depends on exchange 2 turns ago",
        "history": [
            {"role": "user", "content": "Ich habe Probleme mit dem PDF-Export."},
            {"role": "assistant", "content": "Welchen Fehler bekommst du?"},
            {"role": "user", "content": "Es kommt ein Timeout."},
            {"role": "assistant", "content": "Das liegt oft an zu großen Bildern."}
        ],
        "query": "Wie kann ich das beheben?",
        "expected_keywords": ["PDF", "Export", "Timeout", "beheben"]
    },
    {
        "name": "Ambiguous Selection",
        "description": "Referring to an item from a previous list",
        "history": [
            {"role": "user", "content": "Welche Deployment-Optionen gibt es?"},
            {"role": "assistant", "content": "1. Cloud Hosting\n2. On-Premise\n3. Hybrid"}
        ],
        "query": "Erzähl mir mehr über die zweite Option.",
        "expected_keywords": ["On-Premise"] # Relaxed: "Option" might be replaced by specific term
    }
]

async def eval_scenario(service, scenario):
    print(f"\n--- Scenario: {scenario['name']} ---")
    print(f"📝 Query: {scenario['query']}")
    
    start_time = time.time()
    rewritten = service._enhance_query_with_history(scenario['query'], scenario['history'])
    duration = time.time() - start_time
    
    print(f"🔄 Rewritten: {rewritten}")
    print(f"⏱️ Latency: {duration:.2f}s")
    
    # Evaluation
    passed = True
    missing = []
    
    # Check for expected keywords
    for keyword in scenario['expected_keywords']:
        if keyword.lower() not in rewritten.lower():
            # If it's a "Topic Switch" scenario, we might EXPECT strict keywords.
            # But for "Topic Switch", we specifically want the rewrite to match query generally
            pass # We'll do a more heuristic check below
            
    # Heuristic pass/fail
    if scenario['name'] == "Topic Switch (No Rewrite Expected)":
        # For topic switch, we want the rewritten query to be mostly same as original
        # or at least NOT contain the old context
        if "Docker" in rewritten:
            print("❌ FAIL: Context leaked into topic switch")
            passed = False
        else:
             print("✅ PASS: Context correctly ignored")
    else:
        # For others, we expect expansion
        if len(rewritten) <= len(scenario['query']) and "it" in scenario['query']:
             # Rough check: if length didn't increase and "it" is still there, it likely failed
             print("⚠️ WARN: Query size didn't increase, might have failed to expand context.")
             
        # Check specific keywords
        all_keywords_found = True
        for kw in scenario['expected_keywords']:
            if kw.lower() not in rewritten.lower():
                missing.append(kw)
                all_keywords_found = False
        
        if all_keywords_found:
            print("✅ PASS: All expected keywords found")
        else:
            print(f"❌ FAIL: Missing keywords: {missing}")
            passed = False

    return {
        "scenario": scenario['name'],
        "passed": passed,
        "latency": duration,
        "original": scenario['query'],
        "rewritten": rewritten
    }

async def run_evaluation():
    print("🚀 Starting Memory Evaluation...")
    print("Configuration: GPT-4o-mini for rewriting")
    
    try:
        LlamaIndexSettings.configure()
        service = ChatService()
        
        results = []
        for scenario in SCENARIOS:
            result = await eval_scenario(service, scenario)
            results.append(result)
            
        # Summary
        print("\n=== EVALUATION SUMMARY ===")
        avg_latency = sum(r['latency'] for r in results) / len(results)
        pass_count = sum(1 for r in results if r['passed'])
        
        print(f"Total Scenarios: {len(results)}")
        print(f"Passed: {pass_count}/{len(results)}")
        print(f"Average Latency: {avg_latency:.2f}s")
        
        if pass_count == len(results):
            print("\n✅ EXCELLENT: System behaves as expected across all test cases.")
        else:
            print("\n⚠️ ATTENTION: Some scenarios failed. See details above.")
            
    except Exception as e:
        print(f"🔥 Critical Error during evaluation: {e}")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY environment variable required")
        sys.exit(1)
        
    asyncio.run(run_evaluation())
