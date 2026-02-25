"""Tests for the reranker service."""

import json
from unittest.mock import patch, MagicMock

from services.reranker import rerank


class TestReranker:
    def test_empty_results(self):
        assert rerank("query", [], top_k=5) == []

    def test_fewer_than_top_k_no_api_call(self):
        results = [
            {"text": "doc1", "score": 0.9},
            {"text": "doc2", "score": 0.7},
        ]
        reranked = rerank("query", results, top_k=5)
        assert len(reranked) == 2
        # Should have rerank_score set from original score
        assert all("rerank_score" in r for r in reranked)

    def test_mocked_openai_reranking(self):
        results = [
            {"text": f"Document {i} text content", "score": 0.5}
            for i in range(10)
        ]

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps([
            {"id": 3, "score": 0.95},
            {"id": 7, "score": 0.90},
            {"id": 0, "score": 0.85},
            {"id": 1, "score": 0.80},
            {"id": 5, "score": 0.75},
        ])

        with patch("services.reranker.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client

            reranked = rerank("test query", results, top_k=3)

        assert len(reranked) == 3
        assert reranked[0]["rerank_score"] == 0.95
        assert reranked[0]["text"] == "Document 3 text content"

    def test_api_error_fallback(self):
        results = [
            {"text": f"Doc {i}", "score": 0.5 + i * 0.05}
            for i in range(10)
        ]

        with patch("services.reranker.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            MockOpenAI.return_value = mock_client

            reranked = rerank("test query", results, top_k=3)

        # Should fall back to original order, limited to top_k
        assert len(reranked) == 3
        assert all("rerank_score" in r for r in reranked)
