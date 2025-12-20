"""
Generate RAG Testset
Uses 'ragas' to generate a synthetic testset (Questions, Ground Truths)
from the documents currently in the Vector Store.
"""

import os
import sys
from typing import List
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document as LangChainDocument
from ragas.testset import TestsetGenerator

# from ragas.testset.evolutions import simple, reasoning, multi_context # Deprecated in 0.2
from config import config

# Load env variables
load_dotenv()


def get_documents_from_vector_store() -> List[LangChainDocument]:
    """Fetch documents from our Qdrant vector store and convert to LangChain format"""
    from services.rag.vector_store import vector_store

    print("Fetching documents from Vector Store...")
    # List all documents (limit to 20 for testset generation to save time)
    docs = vector_store.list_documents(limit=20)

    langchain_docs = []
    print(f"Found {len(docs)} candidates. Fetching full content...")

    for doc in docs:
        doc_id = doc.get("doc_id")
        # list_documents only gives preview, we need full content
        full_doc = vector_store.get_document(doc_id)

        if not full_doc:
            continue

        content = full_doc.get("content", "")
        metadata = full_doc.get("metadata", {})

        # Skip empty documents
        if not content or len(content) < 50:
            continue

        lc_doc = LangChainDocument(
            page_content=content,
            metadata={
                "filename": metadata.get("filename", "unknown"),
                "doc_id": doc.get("doc_id"),
                "chunk_index": metadata.get("chunk_index", 0),
            },
        )
        langchain_docs.append(lc_doc)

    print(f"✅ Loaded {len(langchain_docs)} documents for generation.")
    return langchain_docs


def generate_testset(output_file="testset.csv", test_size=10):
    """Generate synthetic testset"""

    # 1. Load Documents
    documents = get_documents_from_vector_store()

    if not documents:
        print("❌ No documents found to generate testset!")
        return

    # 2. Configure Generator
    # Ragas uses LangChain LLMs
    generator_llm = ChatOpenAI(model=config.LLM_MODEL)
    ChatOpenAI(model=config.LLM_MODEL)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    generator = TestsetGenerator.from_langchain(generator_llm, embeddings)

    # 3. Generate
    print(f"🚀 Generating {test_size} synthetic test cases... (This may take a minute)")

    # Use defaults for 0.2 compatibility
    testset = generator.generate_with_langchain_docs(
        documents,
        testset_size=test_size,
        # distributions=distributions, # Use default distribution
        raise_exceptions=False,
    )

    # 4. Save
    df = testset.to_pandas()
    df.to_csv(output_file, index=False)
    print(f"✅ Testset saved to {output_file}")

    return df


if __name__ == "__main__":
    # Allow passing size as argument
    size = 10
    if len(sys.argv) > 1:
        try:
            size = int(sys.argv[1])
        except ValueError:
            pass

    generate_testset(test_size=size)
