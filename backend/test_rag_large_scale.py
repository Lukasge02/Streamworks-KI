import requests
import time
import os
import glob
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8000"
CORPUS_DIR = "test_corpus_large"
MAX_WORKERS = 5  # Parallel uploads


def upload_single_file(filepath):
    filename = os.path.basename(filepath)
    print(f"   Uploading {filename}...")

    with open(filepath, "rb") as f:
        files = {"file": (filename, f, "application/octet-stream")}
        try:
            res = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
            if res.status_code == 202:
                return res.json()["task_id"]
            else:
                print(f"❌ Failed to upload {filename}: {res.text}")
                return None
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
            return None


def wait_for_tasks(task_ids):
    print(f"\n⏳ Waiting for {len(task_ids)} tasks to complete processing...")
    pending = set(task_ids)
    completed = 0
    failed = 0

    start_time = time.time()
    while pending and (time.time() - start_time) < 300:  # 5 min timeout
        for task_id in list(pending):
            try:
                res = requests.get(f"{BASE_URL}/api/documents/{task_id}/status")
                if res.status_code == 200:
                    status = res.json()["status"]
                    if status == "completed":
                        completed += 1
                        pending.remove(task_id)
                        print(
                            f"   ✅ Task {task_id} completed ({completed}/{len(task_ids)})"
                        )
                    elif status == "failed":
                        failed += 1
                        pending.remove(task_id)
                        print(f"   ❌ Task {task_id} failed")
            except:
                pass
        time.sleep(2)

    print(
        f"\n📊 Processing finished: {completed} success, {failed} failed, {len(pending)} timeout"
    )
    return completed


def run_stress_test():
    # 1. Generate Corpus if not exists
    if not os.path.exists(CORPUS_DIR) or not os.listdir(CORPUS_DIR):
        print("Corpus not found. Please run corpus_generator.py first.")
        # But for automation, let's call it via subproocess
        os.system("python3 corpus_generator.py")

    files = glob.glob(f"{CORPUS_DIR}/*")
    print(f"\n🚀 Starting Mass Upload of {len(files)} files...")

    task_ids = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(upload_single_file, files)
        task_ids = [t for t in results if t]

    successful_docs = wait_for_tasks(task_ids)

    # 2. Run Complex Queries
    print("\n🔍 Running Advanced Queries on Large Corpus...")

    queries = [
        # Tests specific "needle in haystack" set in corpus_generator.py
        {
            "q": "Wie viele Urlaubstage haben Mitarbeiter laut HR?",
            "expect_kw": ["25", "Tage"],
            "desc": "Check average value retrieval across multiple similar docs",
        },
        {
            "q": "Was ist das Remote-First Programm?",
            "expect_kw": ["100%", "Homeoffice", "Level 3"],
            "desc": "Find rare fact (only in 1 document)",
        },
        {
            "q": "Was ist die CRITICAL CONFIGURATION im Global Architecture Guide?",
            "expect_kw": ["1337", "connections"],
            "desc": "Needle in Haystack (Monster Manual Page 42)",
        },
        {
            "q": "Ist LegacyAuth noch erlaubt?",
            "expect_kw": ["forbidden", "Patch 4.5.2"],
            "desc": "Needle in Haystack (Monster Manual Page 75)",
        },
        {
            "q": "Welcher Timeout gilt für die IT Software Katalog Version 2.0?",
            "expect_kw": ["120s"],
            "desc": "Version filtering test (Should use metadata filter)",
        },
        {
            "q": "Wie hoch ist das Budget für Streamworks_Migration?",
            "expect_kw": ["50000", "Euro", "EUR"],
            "desc": "JSON retrieval",
        },
        {
            "q": "Gibt es bekannte Memory Leaks?",
            "expect_kw": ["Memory leak", "high load"],
            "desc": "Cross-document search",
        },
    ]

    score = 0
    for query in queries:
        print(f"\n❓ Query: {query['q']}")
        start = time.time()
        res = requests.post(
            f"{BASE_URL}/api/documents/chat",
            json={
                "query": query["q"],
                "num_chunks": 10,
            },  # Request more chunks for large corpus
        )
        duration = time.time() - start

        if res.status_code == 200:
            data = res.json()
            ans = data["answer"]
            conf = data.get("confidence", 0)
            print(f"   Answer: {ans[:200]}...")
            print(f"   Time: {duration:.2f}s | Confidence: {conf}")

            # Simple keyword check
            hit = any(kw.lower() in ans.lower() for kw in query["expect_kw"])
            if hit and conf > 0.6:
                print("   ✅ PASSED")
                score += 1
            else:
                print(f"   ❌ FAILED (Expected {query['expect_kw']})")
        else:
            print("   ❌ API Error")

    print(f"\n🏆 Final Score: {score}/{len(queries)}")


if __name__ == "__main__":
    run_stress_test()
