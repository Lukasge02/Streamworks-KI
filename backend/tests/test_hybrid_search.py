"""Tests for hybrid search components."""

from services.hybrid_search import HybridSearcher


class TestTokenize:
    def test_basic_tokenization(self):
        s = HybridSearcher()
        tokens = s._tokenize("Hello World! This is a test.")
        assert tokens == ["hello", "world", "this", "is", "a", "test"]

    def test_german_text(self):
        s = HybridSearcher()
        tokens = s._tokenize("Dateitransfer taeglich ausfuehren")
        assert "dateitransfer" in tokens
        assert "taeglich" in tokens

    def test_empty_string(self):
        s = HybridSearcher()
        assert s._tokenize("") == []


class TestReciprocalRankFusion:
    def test_single_list(self):
        results = [
            [
                {"text": "first", "score": 0.9},
                {"text": "second", "score": 0.7},
            ]
        ]
        fused = HybridSearcher._reciprocal_rank_fusion(results, k=60)
        assert len(fused) == 2
        # First should have higher score
        assert fused[0]["score"] > fused[1]["score"]

    def test_two_lists_with_overlap(self):
        list1 = [
            {"text": "doc_a content", "score": 0.9, "document_name": "a"},
            {"text": "doc_b content", "score": 0.8, "document_name": "b"},
        ]
        list2 = [
            {"text": "doc_b content", "score": 0.95, "document_name": "b"},
            {"text": "doc_c content", "score": 0.7, "document_name": "c"},
        ]
        fused = HybridSearcher._reciprocal_rank_fusion([list1, list2], k=60)
        # doc_b appears in both lists so should have highest fused score
        assert fused[0]["text"] == "doc_b content"
        assert fused[0]["source"] == "hybrid"

    def test_deduplication(self):
        list1 = [{"text": "same doc", "score": 0.9}]
        list2 = [{"text": "same doc", "score": 0.8}]
        fused = HybridSearcher._reciprocal_rank_fusion([list1, list2], k=60)
        assert len(fused) == 1

    def test_empty_lists(self):
        fused = HybridSearcher._reciprocal_rank_fusion([[], []], k=60)
        assert fused == []
