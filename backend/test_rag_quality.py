import requests
import time
import sys

BASE_URL = "http://localhost:8000"
DOC_PATH = "test_docs/streamworks_guide.md"


def print_result(name, passed, details=""):
    symbol = "✅" if passed else "❌"
    print(f"{symbol} {name}")
    if details:
        print(f"   Details: {details}")


def upload_document():
    print(f"\n📤 Uploading {DOC_PATH}...")
    with open(DOC_PATH, "rb") as f:
        files = {"file": ("streamworks_guide.md", f, "text/markdown")}
        response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)

    if response.status_code != 202:
        print(f"❌ Upload failed: {response.text}")
        sys.exit(1)

    task_id = response.json()["task_id"]
    print(f"   Task ID: {task_id}")

    # Poll status
    for _ in range(10):
        res = requests.get(f"{BASE_URL}/api/documents/{task_id}/status")
        status = res.json()["status"]
        print(f"   Status: {status}")
        if status == "completed":
            print("✅ Upload complete")
            return
        if status == "failed":
            print("❌ Processing failed")
            sys.exit(1)
        time.sleep(1)
    print("⚠️ Timeout waiting for processing")


def test_queries():
    print("\n🔍 Running Test Queries...")

    test_cases = [
        {
            "name": "Factual Question (Exact Answer)",
            "query": "Was ist der Default Timeout für HTTP Jobs?",
            "expected_keywords": ["60", "seconds", "Sekunden"],
            "min_confidence": 0.8,
        },
        {
            "name": "Keyword Search (Technical Terms)",
            "query": "Welche SAP Library wird benötigt?",
            "expected_keywords": ["JCo", "v3.1"],
            "min_confidence": 0.7,
        },
        {
            "name": "Procedural/HyDE (Implicit Info)",
            "query": "Wie funktioniert die Retry Logik?",
            "expected_keywords": ["exponentiell", "backoff", "2s"],
            "min_confidence": 0.7,
        },
        {
            "name": "Negative Test (Missing Info)",
            "query": "Wie backe ich einen Kuchen?",
            "expected_keywords": ["keine relevanten Dokumente", "nichts gefunden"],
            "expected_confidence_max": 0.6,  # Should be low confidence or explicit rejection
        },
        {
            "name": "Specific Detail (Experimental Feature)",
            "query": "Ist Resume Transfer supported?",
            "expected_keywords": ["experimental", "2.4"],
            "min_confidence": 0.8,
        },
    ]

    score = 0
    total = len(test_cases)

    for test in test_cases:
        print(f"\n--- Test: {test['name']} ---")
        print(f"Query: {test['query']}")

        start = time.time()
        res = requests.post(
            f"{BASE_URL}/api/documents/chat",
            json={"query": test["query"], "num_chunks": 3},
        )
        duration = time.time() - start

        if res.status_code != 200:
            print(f"❌ API Error: {res.status_code}")
            continue

        data = res.json()
        answer = data["answer"]
        confidence = data.get("confidence", 0)
        level = data.get("confidence_level", "unknown")
        sources = data.get("sources", [])

        print(f"Response ({duration:.2f}s): {answer[:150]}...")
        print(f"Confidence: {confidence} ({level})")
        print(f"Sources: {len(sources)}")

        # Validation
        passed = True
        fail_reason = ""

        # Check Keywords
        if "expected_keywords" in test:
            found_kws = [
                kw for kw in test["expected_keywords"] if kw.lower() in answer.lower()
            ]
            if (
                not found_kws and test.get("name") != "Negative Test (Missing Info)"
            ):  # Special handling for rejection
                # Check if it's the negative test standard answer
                if "keine relevanten Dokumente" not in answer:
                    passed = False
                    fail_reason = f"Missing keywords: {test['expected_keywords']}"
            elif test.get("name") == "Negative Test (Missing Info)":
                # For negative test, we expect the rejection message OR low confidence
                if "keine relevanten Dokumente" not in answer and confidence > 0.6:
                    passed = False
                    fail_reason = "Should have rejected or low confidence"

        # Check Confidence
        if "min_confidence" in test and confidence < test["min_confidence"]:
            passed = False
            fail_reason += f" Confidence too low (<{test['min_confidence']})"

        if (
            "expected_confidence_max" in test
            and confidence > test["expected_confidence_max"]
        ):
            if (
                "keine relevanten Dokumente" not in answer
            ):  # Allow high confidence rejection
                passed = False
                fail_reason += (
                    f" Confidence too high (>{test['expected_confidence_max']})"
                )

        print_result(test["name"], passed, fail_reason)
        if passed:
            score += 1

    print(f"\n🎯 Total Score: {score}/{total}")


if __name__ == "__main__":
    upload_document()
    # Wait a bit for indexing to settle (Qdrant is fast but safer to wait 1s)
    time.sleep(2)
    test_queries()
