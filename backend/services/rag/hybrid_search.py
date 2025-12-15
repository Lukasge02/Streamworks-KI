"""
Hybrid Search Engine
Combines semantic search (Qdrant) with keyword search (BM25) using Reciprocal Rank Fusion
"""

import re
import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from rank_bm25 import BM25Okapi

from config import config
from .cache import rag_cache


@dataclass
class SearchResult:
    """Unified search result from hybrid search"""

    doc_id: str
    content: str
    filename: str
    score: float
    semantic_score: float
    keyword_score: float
    metadata: Dict[str, Any]
    rank_source: str  # "semantic", "keyword", or "both"


class HybridSearchEngine:
    """
    Enterprise Hybrid Search Engine

    Combines:
    1. Semantic Search (OpenAI embeddings → Qdrant vector similarity)
    2. Keyword Search (BM25 algorithm for term frequency matching)
    3. Reciprocal Rank Fusion (RRF) for result merging

    Benefits:
    - Catches exact term matches that semantic search might miss
    - Handles technical terms, acronyms, and specific values
    - Provides more robust results across query types
    """

    # RRF constant (typically 60 as per original paper)
    RRF_K = 60

    def __init__(self, vector_store=None):
        self._vector_store = vector_store
        self._semantic_weight = config.RAG_SEMANTIC_WEIGHT
        self._keyword_weight = config.RAG_KEYWORD_WEIGHT

    @property
    def vector_store(self):
        if self._vector_store is None:
            from .vector_store import vector_store

            self._vector_store = vector_store
        return self._vector_store

    def search(
        self,
        query: str,
        limit: int = 10,
        semantic_limit: int = 20,
        keyword_limit: int = 20,
        score_threshold: float = 0.2,
        filters: Dict[str, Any] = None,
        use_cache: bool = True,
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic and keyword results.

        Args:
            query: Search query string
            limit: Maximum results to return
            semantic_limit: Max results from semantic search
            keyword_limit: Max results from keyword search
            score_threshold: Minimum score for semantic search
            use_cache: Whether to use cached results

        Returns:
            List of SearchResult objects ranked by fused score
        """
        # Check cache first (include filters in cache key if present)
        cache_key_suffix = f"_{json.dumps(filters, sort_keys=True)}" if filters else ""
        if use_cache:
            # We append the filter string to the query for caching purposes
            cached = rag_cache.get_search_results(
                query + cache_key_suffix, limit, "hybrid"
            )
            if cached:
                return [SearchResult(**r) for r in cached]

        # 1. Semantic search via Qdrant (with native filtering)
        semantic_results = self._semantic_search(
            query, semantic_limit, score_threshold, filters
        )

        # 2. Keyword search via BM25 (with post-hoc filtering)
        keyword_results = self._keyword_search(query, keyword_limit, filters)

        # 3. Merge with Reciprocal Rank Fusion
        fused_results = self._reciprocal_rank_fusion(
            semantic_results, keyword_results, limit
        )

        # Cache results
        if use_cache and fused_results:
            rag_cache.set_search_results(
                query + cache_key_suffix,
                limit,
                [self._result_to_dict(r) for r in fused_results],
                "hybrid",
            )

        return fused_results

    def _semantic_search(
        self,
        query: str,
        limit: int,
        score_threshold: float,
        filters: Dict[str, Any] = None,
    ) -> List[Tuple[Dict[str, Any], int]]:
        """Get semantic search results with ranks"""
        results = self.vector_store.search(
            query=query, limit=limit, score_threshold=score_threshold, filters=filters
        )

        # Return results with their rank (1-indexed)
        return [(r, rank + 1) for rank, r in enumerate(results)]

    def _keyword_search(
        self, query: str, limit: int, filters: Dict[str, Any] = None
    ) -> List[Tuple[Dict[str, Any], int]]:
        """Get keyword search results using BM25"""
        # Check if we need to rebuild BM25 index
        bm25_index = rag_cache.get_bm25_index()

        if bm25_index is None:
            bm25_index = self._build_bm25_index()
            if bm25_index is None:
                return []  # No documents to search

        # Tokenize query
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Get BM25 scores
        scores = bm25_index.get_scores(query_tokens)

        # Get document IDs from cache
        doc_ids = rag_cache.get_bm25_doc_ids()
        if not doc_ids:
            return []

        # Pair scores with document IDs and sort
        scored_docs = [
            (doc_id, score) for doc_id, score in zip(doc_ids, scores) if score > 0
        ]
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        # We fetch more than limit to allow for filtering
        scored_docs = scored_docs[: limit * 20] if filters else scored_docs[:limit]

        # Fetch full documents from vector store and apply filters
        results = []
        rank_counter = 1

        for doc_id, bm25_score in scored_docs:
            doc = self.vector_store.get_document(doc_id)
            if not doc:
                continue

            # Apply Metadata Filters
            if filters:
                match = True
                doc_meta = doc.get("metadata", {})
                for key, val in filters.items():
                    # Handle version matching
                    if key == "version" and str(doc_meta.get("version")) != str(val):
                        match = False
                        break
                    # Handle category matching
                    elif key == "category" and doc_meta.get("category") != val:
                        match = False
                        break
                    # Handle year matching
                    elif key == "year" and doc_meta.get("year") != val:
                        match = False
                        break

                if not match:
                    continue

            doc["bm25_score"] = bm25_score
            results.append((doc, rank_counter))
            rank_counter += 1

            if len(results) >= limit:
                break

        return results

    def _build_bm25_index(self):
        """Build BM25 index from all documents in vector store"""
        try:
            # Get all documents
            all_docs = self.vector_store.list_documents(limit=10000)

            if not all_docs:
                return None

            # Build corpus (tokenized documents)
            corpus = []
            doc_ids = []

            for doc in all_docs:
                content = doc.get("content_preview", "").replace("...", "")
                # For BM25, we need the full content - fetch it
                full_doc = self.vector_store.get_document(doc.get("doc_id"))
                if full_doc:
                    content = full_doc.get("content", content)

                tokens = self._tokenize(content)
                if tokens:
                    corpus.append(tokens)
                    doc_ids.append(doc.get("doc_id"))

            if not corpus:
                return None

            # Create BM25 index
            bm25 = BM25Okapi(corpus)

            # Cache the index
            rag_cache.set_bm25_index(bm25, corpus, doc_ids)

            print(f"✅ Built BM25 index with {len(corpus)} documents")
            return bm25

        except Exception as e:
            print(f"❌ Failed to build BM25 index: {e}")
            return None

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25"""
        if not text:
            return []

        # Lowercase and split on non-alphanumeric
        text = text.lower()
        tokens = re.findall(r"\b[a-zäöüß0-9]+\b", text)

        # Remove very short tokens and stopwords
        stopwords = {
            "der",
            "die",
            "das",
            "und",
            "in",
            "zu",
            "den",
            "von",
            "mit",
            "ist",
            "für",
            "auf",
            "im",
            "eine",
            "ein",
            "einer",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
        }

        return [t for t in tokens if len(t) > 1 and t not in stopwords]

    def _reciprocal_rank_fusion(
        self,
        semantic_results: List[Tuple[Dict, int]],
        keyword_results: List[Tuple[Dict, int]],
        limit: int,
    ) -> List[SearchResult]:
        """
        Merge results using Reciprocal Rank Fusion (RRF).

        RRF Score = Σ 1 / (k + rank)

        This method is robust and doesn't require score normalization.
        """
        # Build score map by doc_id
        rrf_scores: Dict[str, Dict] = {}

        # Process semantic results
        for doc, rank in semantic_results:
            doc_id = doc.get("doc_id")
            if not doc_id:
                continue

            rrf_score = self._semantic_weight / (self.RRF_K + rank)

            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {
                    "doc": doc,
                    "rrf_score": 0,
                    "semantic_score": doc.get("score", 0),
                    "semantic_rank": rank,
                    "keyword_score": 0,
                    "keyword_rank": None,
                    "sources": ["semantic"],
                }

            rrf_scores[doc_id]["rrf_score"] += rrf_score

        # Process keyword results
        for doc, rank in keyword_results:
            doc_id = doc.get("doc_id")
            if not doc_id:
                continue

            rrf_score = self._keyword_weight / (self.RRF_K + rank)

            if doc_id in rrf_scores:
                # Document found in both searches
                rrf_scores[doc_id]["rrf_score"] += rrf_score
                rrf_scores[doc_id]["keyword_score"] = doc.get("bm25_score", 0)
                rrf_scores[doc_id]["keyword_rank"] = rank
                rrf_scores[doc_id]["sources"].append("keyword")
            else:
                rrf_scores[doc_id] = {
                    "doc": doc,
                    "rrf_score": rrf_score,
                    "semantic_score": 0,
                    "semantic_rank": None,
                    "keyword_score": doc.get("bm25_score", 0),
                    "keyword_rank": rank,
                    "sources": ["keyword"],
                }

        # Sort by RRF score and create SearchResult objects
        sorted_results = sorted(
            rrf_scores.values(), key=lambda x: x["rrf_score"], reverse=True
        )[:limit]

        return [
            SearchResult(
                doc_id=r["doc"]["doc_id"],
                content=r["doc"].get("content", ""),
                filename=r["doc"].get("filename", "Unknown"),
                score=r["rrf_score"],
                semantic_score=r["semantic_score"],
                keyword_score=r["keyword_score"],
                metadata=r["doc"].get("metadata", {}),
                rank_source="both" if len(r["sources"]) > 1 else r["sources"][0],
            )
            for r in sorted_results
        ]

    def _result_to_dict(self, result: SearchResult) -> Dict[str, Any]:
        """Convert SearchResult to dict for caching"""
        return {
            "doc_id": result.doc_id,
            "content": result.content,
            "filename": result.filename,
            "score": result.score,
            "semantic_score": result.semantic_score,
            "keyword_score": result.keyword_score,
            "metadata": result.metadata,
            "rank_source": result.rank_source,
        }

    def invalidate_index(self) -> None:
        """Invalidate BM25 index (call after document changes)"""
        rag_cache.invalidate_bm25()
        rag_cache.invalidate_search()

    def get_stats(self) -> Dict[str, Any]:
        """Get hybrid search statistics"""
        cache_stats = rag_cache.get_stats()
        return {
            "semantic_weight": self._semantic_weight,
            "keyword_weight": self._keyword_weight,
            "rrf_k": self.RRF_K,
            "cache": cache_stats,
        }


# Singleton instance
hybrid_search = HybridSearchEngine()
