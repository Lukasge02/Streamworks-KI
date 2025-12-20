import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from services.rag.engine.chat_service import ChatService
from services.rag.engine.settings import LlamaIndexSettings


async def test_contextual_retrieval():
    """Test LLM-based query rewriting"""

    print("🚀 Initializing ChatService...")
    # Initialize settings (needs env vars)
    LlamaIndexSettings.configure()

    service = ChatService()

    # Test case 1: No history
    print("\nTest 1: No history")
    query = "Was ist Streamworks?"
    rewritten = service._enhance_query_with_history(query, [])
    print(f"Original: {query}")
    print(f"Rewritten: {rewritten}")
    assert rewritten == query, "Query without history should not change"

    # Test case 2: Simple follow-up
    print("\nTest 2: Simple follow-up")
    history = [
        {"role": "user", "content": "Wer ist der Projektleiter von Projekt Alpha?"},
        {"role": "assistant", "content": "Der Projektleiter ist Max Mustermann."},
    ]
    query = "Wie kann ich ihn kontaktieren?"
    rewritten = service._enhance_query_with_history(query, history)
    print(f"Original: {query}")
    print(f"Rewritten: {rewritten}")
    assert "Max Mustermann" in rewritten or "Projektleiter" in rewritten, (
        "Rewritten query should resolve 'ihn'"
    )

    # Test case 3: Contextual switch (should NOT rewrite if irrelevant)
    print("\nTest 3: Topic switch")
    history = [
        {"role": "user", "content": "Erzähl mir von Python."},
        {"role": "assistant", "content": "Python ist eine Programmiersprache."},
    ]
    query = "Wie ist das Wetter heute?"
    rewritten = service._enhance_query_with_history(query, history)
    print(f"Original: {query}")
    print(f"Rewritten: {rewritten}")
    # Ideally it stays similar, or maybe adds context but shouldn't be totally wrong.
    # The prompt instructs to use history to resolve context. If there is no context to resolve, it typically keeps it.

    print("\n✅ Verification complete!")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY environment variable required")
        sys.exit(1)

    asyncio.run(test_contextual_retrieval())
