"""Tests for RAG service internal functions."""

from services.rag_service import (
    _build_context_and_sources,
    _estimate_confidence,
    _build_messages,
)


class TestBuildContextAndSources:
    def test_basic(self):
        results = [
            {"text": "First result text", "document_name": "doc1.pdf", "page": 1, "score": 0.9},
            {"text": "Second result text", "document_name": "doc2.pdf", "page": 3, "rerank_score": 0.85},
        ]
        context_str, sources_str, source_list = _build_context_and_sources(results)

        assert "[1] First result text" in context_str
        assert "[2] Second result text" in context_str
        assert "[1] doc1.pdf, Seite 1" in sources_str
        assert len(source_list) == 2
        assert source_list[0]["index"] == 1

    def test_empty_results(self):
        context_str, sources_str, source_list = _build_context_and_sources([])
        assert context_str == ""
        assert sources_str == ""
        assert source_list == []

    def test_text_preview_truncation(self):
        long_text = "x" * 300
        results = [{"text": long_text, "document_name": "doc.pdf", "page": None, "score": 0.5}]
        _, _, source_list = _build_context_and_sources(results)
        assert source_list[0]["text_preview"].endswith("...")
        assert len(source_list[0]["text_preview"]) < 300


class TestEstimateConfidence:
    def test_empty_results(self):
        assert _estimate_confidence([]) == 0.0

    def test_high_scores(self):
        results = [{"rerank_score": 0.95}, {"rerank_score": 0.90}, {"rerank_score": 0.85}]
        conf = _estimate_confidence(results)
        assert conf > 0.8

    def test_low_scores(self):
        results = [{"score": 0.1}, {"score": 0.05}]
        conf = _estimate_confidence(results)
        assert conf < 0.2

    def test_single_result(self):
        results = [{"rerank_score": 0.7}]
        conf = _estimate_confidence(results)
        assert 0.0 <= conf <= 1.0


class TestBuildMessages:
    def test_without_history(self):
        messages = _build_messages("What is X?", "context here", "sources here")
        assert messages[0]["role"] == "system"
        assert "context here" in messages[0]["content"]
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "What is X?"

    def test_with_history(self):
        history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"},
        ]
        messages = _build_messages("Follow up?", "ctx", "src", chat_history=history)
        assert len(messages) == 4  # system + 2 history + user
        assert messages[1]["content"] == "Previous question"
        assert messages[2]["content"] == "Previous answer"
        assert messages[3]["content"] == "Follow up?"

    def test_empty_history_messages_filtered(self):
        history = [
            {"role": "user", "content": ""},
            {"role": "assistant", "content": "Valid"},
        ]
        messages = _build_messages("Question", "ctx", "src", chat_history=history)
        # Empty content message should be filtered
        assert len(messages) == 3  # system + 1 valid history + user
