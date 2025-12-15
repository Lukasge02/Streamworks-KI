import requests

BASE_URL = "http://localhost:8000"


def delete_all():
    print("🧹 Cleaning up old documents...")
    # List all
    res = requests.get(f"{BASE_URL}/api/documents/list?limit=100")
    if res.status_code != 200:
        print("Failed to list docs")
        return

    docs = res.json().get("documents", [])
    print(f"Found {len(docs)} documents to delete.")

    for doc in docs:
        print(f"   Deleting {doc['doc_id']} ({doc['filename']})...")
        requests.delete(f"{BASE_URL}/api/documents/{doc['doc_id']}")

    print("✅ Cleanup complete.")


if __name__ == "__main__":
    delete_all()
