import sys
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))
try:
    from services.rag.vector_store import vector_store
    from services.rag.hybrid_search import HybridSearchEngine
except ImportError:
    # Fallback to local import if needed or path adjustment
    pass

import json


def inspect_metadata():
    print("🔍 Inspecting Vector Store Metadata...")

    # List a few docs
    docs = vector_store.list_documents(limit=100)

    versions = {}

    for doc in docs:
        # Fetch full doc to see metadata
        full_doc = vector_store.get_document(doc["doc_id"])
        meta = full_doc.get("metadata", {})
        v = meta.get("version", "none")
        versions[v] = versions.get(v, 0) + 1

        if "Manual" in doc["filename"]:
            print("   >>> FOUND MONSTER MANUAL <<<")
            # print(f"   Content Preview: {full_doc.get('content')[:100]}...")

    print("\n📊 Version Statistics:")
    print(json.dumps(versions, indent=2))

    print("\n🔍 Testing Vector Search with Filter version='2.0' (Threshold 0.0)...")
    results = vector_store.search(
        "Timeout", limit=5, score_threshold=0.0, filters={"version": "2.0"}
    )
    print(f"Found {len(results)} results.")
    for r in results:
        print(
            f" - {r['filename']} (Score: {r['score']:.4f}, Version: {r['metadata'].get('version')})"
        )

    print(
        "\n🔍 Testing Hybrid Search with Filter version='2.0' (Query: 'Welcher Timeout gilt für die IT Software Katalog')..."
    )
    hs = HybridSearchEngine(vector_store)
    # Note: hybrid search initializes BM25 which might take a second
    results = hs.search(
        "Welcher Timeout gilt für die IT Software Katalog",
        limit=5,
        score_threshold=0.0,
        filters={"version": "2.0"},
    )
    print(f"Found {len(results)} results.")
    for r in results:
        print(
            f" - {r.filename} (Score: {r.score:.4f}, Sem: {r.semantic_score:.4f}, Key: {r.keyword_score:.4f})"
        )


if __name__ == "__main__":
    inspect_metadata()
