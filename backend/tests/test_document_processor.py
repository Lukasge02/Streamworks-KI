"""Tests for document processing pipeline."""

from unittest.mock import patch, MagicMock

from services.document_processor import _parse_file, _chunk_text, process_document


class TestParseFile:
    def test_txt_file(self):
        content = b"Hello world\nThis is a test."
        result = _parse_file("test.txt", content, "text/plain")
        assert "Hello world" in result
        assert "This is a test." in result

    def test_csv_file(self):
        content = b"name,age\nAlice,30\nBob,25"
        result = _parse_file("data.csv", content, "text/csv")
        assert "Alice" in result

    def test_unsupported_type_raises(self):
        import pytest
        with pytest.raises(ValueError, match="Unsupported file type"):
            _parse_file("image.png", b"\x89PNG", "image/png")

    def test_txt_by_extension(self):
        """Even with generic content_type, .txt extension should work."""
        result = _parse_file("notes.txt", b"some notes", "application/octet-stream")
        assert "some notes" in result


class TestChunkText:
    def test_short_text_one_chunk(self):
        text = "This is short."
        chunks = _chunk_text(text, chunk_size=800, overlap=200)
        assert len(chunks) == 1
        assert chunks[0] == "This is short."

    def test_long_text_multiple_chunks(self):
        # Create text with multiple paragraphs
        paragraphs = [f"Paragraph {i}. " * 20 for i in range(10)]
        text = "\n\n".join(paragraphs)
        chunks = _chunk_text(text, chunk_size=200, overlap=50)
        assert len(chunks) > 1

    def test_empty_text_returns_empty(self):
        assert _chunk_text("") == []
        assert _chunk_text("   ") == []

    def test_whitespace_only_returns_empty(self):
        assert _chunk_text("  \n\n  \n  ") == []


class TestProcessDocument:
    def test_process_with_mocked_services(self):
        with patch("services.document_processor.vector_store") as mock_vs, \
             patch("services.document_processor.file_storage") as mock_fs:
            mock_vs.embed_texts.return_value = [[0.1] * 10]
            mock_vs.ensure_collection.return_value = None
            mock_vs.upsert_chunks.return_value = None
            mock_fs.upload_file.return_value = None

            result = process_document("test.txt", b"Hello world content here", "text/plain")

            assert "document_id" in result
            assert result["filename"] == "test.txt"
            assert result["chunks_count"] >= 1
            mock_vs.embed_texts.assert_called_once()
            mock_fs.upload_file.assert_called_once()

    def test_empty_document(self):
        with patch("services.document_processor.vector_store") as mock_vs, \
             patch("services.document_processor.file_storage") as mock_fs:
            result = process_document("empty.txt", b"", "text/plain")
            assert result["chunks_count"] == 0
            mock_vs.embed_texts.assert_not_called()

    def test_process_returns_document_id(self):
        with patch("services.document_processor.vector_store") as mock_vs, \
             patch("services.document_processor.file_storage") as mock_fs:
            mock_vs.embed_texts.return_value = [[0.1] * 10]
            mock_vs.ensure_collection.return_value = None
            mock_vs.upsert_chunks.return_value = None
            mock_fs.upload_file.return_value = None

            result = process_document("doc.txt", b"Some text", "text/plain")
            import uuid
            uuid.UUID(result["document_id"])  # Should not raise
