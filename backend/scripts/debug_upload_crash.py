import sys
import os
from pathlib import Path

# Fix path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

# from services.rag.document_service import DocumentService
from datetime import datetime
import re


# Mock classes
class MockParserRegistry:
    def parse(self, content, filename):
        class ParsedDoc:
            doc_type = type("obj", (object,), {"value": "md"})
            metadata = {"source": "test", "page_data": []}
            title = "Test"
            page_count = 1
            word_count = 100
            parsing_method = "test"
            content = "Version: 2.0\nThis is a test content."

        return ParsedDoc()


class MockVectorStore:
    def add_document(self, content, metadata, doc_id):
        print(f"✅ Add Document: {metadata}")

    def add_documents_batch(self, documents):
        print(f"✅ Add Batch: {len(documents)}")


class MockChunker:
    def chunk(self, text, strategy=None, page_info=None):
        class Chunk:
            content = "chunk"

            class Meta:
                chunk_index = 0
                total_chunks = 1
                word_count = 10
                sentence_count = 1
                start_char = 0
                end_char = 10
                page_numbers = []
                section_title = None

            metadata = Meta()

        return [Chunk()]


# Mock Service with overrides
# service = DocumentService()
# service._parser_registry = MockParserRegistry()
# service.vector_store = MockVectorStore()
# service._file_storage = type('obj', (object,), {'save_file': lambda c, f, i: None})
# We need to mock module import for enterprise_chunker inside the method
# This is hard because it's imported INSIDE the method.


def test_extraction():
    print("Testing extraction logic...")
    filename = "IT_Software_Katalog_1.md"
    parsed_doc = MockParserRegistry().parse(None, filename)

    # Replicate the logic I added to document_service.py

    # Extract Version (v1.0, v2025, etc)
    version_match = re.search(
        r"(?:v|version)[_-\s]?(\d+(?:[\.-]\d+)*)", filename, re.IGNORECASE
    )
    version = version_match.group(1) if version_match else "unknown"
    print(f"Filename Version: {version}")

    # Fallback: Look for version in first 500 chars of content
    if version == "unknown" and parsed_doc.content:
        content_v_match = re.search(
            r"Version[:\s]*(\d+(?:\.\d+)+)", parsed_doc.content[:500], re.IGNORECASE
        )
        if content_v_match:
            version = content_v_match.group(1)

    print(f"Final Version: {version}")

    # Check regex
    txt = "Version: 2.0"
    m = re.search(r"Version[:\s]*(\d+(?:\.\d+)+)", txt, re.IGNORECASE)
    print(f"Regex Match: {m.group(1) if m else 'No match'}")


if __name__ == "__main__":
    test_extraction()
