"""
Hybrid search: BM25 keyword search + Qdrant semantic search
with Reciprocal Rank Fusion (RRF).

Combines lexical precision with semantic understanding for
higher-quality retrieval.
"""

import logging
import re
from rank_bm25 import BM25Okapi
from services import vector_store

logger = logging.getLogger(__name__)


class HybridSearcher:
    """
    Performs hybrid retrieval by running BM25 and semantic search
    in parallel, then fusing results via Reciprocal Rank Fusion.
    """

    def __init__(self) -> None:
        self._corpus: list[dict] = []
        self._tokenized_corpus: list[list[str]] = []
        self._bm25: BM25Okapi | None = None
        self._dirty: bool = True

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace + punctuation tokenizer with lowercasing."""
        text = text.lower()
        tokens = re.findall(r"\w+", text)
        return tokens

    def _build_bm25_index(self) -> None:
        """
        Load all chunks from Qdrant via scroll and build the BM25 index.

        Sets the dirty flag to False after a successful rebuild.
        """
        logger.info("Building BM25 index from Qdrant corpus...")
        self._corpus = vector_store.scroll_all()

        if not self._corpus:
            logger.warning("No documents found in Qdrant -- BM25 index is empty")
            self._tokenized_corpus = []
            self._bm25 = None
            self._dirty = False
            return

        self._tokenized_corpus = [
            self._tokenize(doc.get("text", "")) for doc in self._corpus
        ]
        self._bm25 = BM25Okapi(self._tokenized_corpus)
        self._dirty = False
        logger.info("BM25 index built with %d documents", len(self._corpus))

    def mark_dirty(self) -> None:
        """Mark the BM25 index as stale so it is rebuilt on next search."""
        self._dirty = True

    def _ensure_index(self) -> None:
        """Rebuild the BM25 index if it is marked dirty or uninitialized."""
        if self._dirty or self._bm25 is None:
            self._build_bm25_index()

    def _bm25_search(self, query: str, limit: int) -> list[dict]:
        """
        Run BM25 keyword search over the in-memory corpus.

        Returns results sorted by BM25 score (descending).
        """
        self._ensure_index()

        if self._bm25 is None or not self._corpus:
            return []

        tokenized_query = self._tokenize(query)
        scores = self._bm25.get_scores(tokenized_query)

        scored = list(zip(self._corpus, scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for doc, score in scored[:limit]:
            results.append({
                "text": doc.get("text", ""),
                "document_id": doc.get("document_id", ""),
                "document_name": doc.get("document_name", ""),
                "page": doc.get("page"),
                "score": float(score),
                "source": "bm25",
            })
        return results

    def _semantic_search(self, query: str, limit: int) -> list[dict]:
        """
        Run semantic similarity search via Qdrant.

        Embeds the query with OpenAI and retrieves nearest neighbours.
        """
        query_embedding = vector_store.embed_texts([query])[0]
        hits = vector_store.search(query_embedding, limit=limit)

        results = []
        for hit in hits:
            results.append({
                "text": hit.get("text", ""),
                "document_id": hit.get("document_id", ""),
                "document_name": hit.get("document_name", ""),
                "page": hit.get("page"),
                "score": float(hit.get("score", 0.0)),
                "source": "semantic",
            })
        return results

    @staticmethod
    def _reciprocal_rank_fusion(
        result_lists: list[list[dict]],
        k: int = 60,
    ) -> list[dict]:
        """
        Fuse multiple ranked result lists using Reciprocal Rank Fusion.

        RRF score = sum over lists of  1 / (k + rank_i)

        Higher k smooths out rank differences. The standard value is 60.

        Args:
            result_lists: A list of ranked result lists.
            k: The RRF constant.

        Returns:
            A single fused list sorted by descending RRF score.
        """
        fused_scores: dict[str, float] = {}
        doc_map: dict[str, dict] = {}

        for result_list in result_lists:
            for rank, doc in enumerate(result_list):
                # Use text content as dedup key (chunks may not have stable IDs)
                key = doc.get("text", "")[:200]
                rrf_score = 1.0 / (k + rank + 1)
                fused_scores[key] = fused_scores.get(key, 0.0) + rrf_score

                # Keep the richer metadata version
                if key not in doc_map:
                    doc_map[key] = doc

        ranked = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for key, score in ranked:
            doc = doc_map[key].copy()
            doc["score"] = score
            doc["source"] = "hybrid"
            results.append(doc)

        return results

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """
        Execute hybrid search: BM25 + semantic, fused with RRF.

        Args:
            query: The search query string.
            limit: Maximum number of results to return.

        Returns:
            Fused and ranked results. Each dict contains: text,
            document_name, score, page, document_id, source.
        """
        # Fetch more candidates from each source to improve fusion quality
        candidate_limit = limit * 3

        bm25_results = self._bm25_search(query, limit=candidate_limit)
        semantic_results = self._semantic_search(query, limit=candidate_limit)

        fused = self._reciprocal_rank_fusion(
            [bm25_results, semantic_results], k=60
        )

        return fused[:limit]
