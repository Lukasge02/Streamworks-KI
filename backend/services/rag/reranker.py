"""
Reranker Service
Uses FlashRank (lightweight, highly efficient reranker) to optimize search results.
"""

from typing import List, Dict, Any
from flashrank import Ranker, RerankRequest


class RerankerService:
    """
    Reranks search results to improve RAG accuracy.
    Uses 'ms-marco-TinyBERT-L-2-v2' (default) which is ~4MB and runs on CPU.
    """

    def __init__(self, model_name: str = "ms-marco-TinyBERT-L-2-v2"):
        # Lazy load model only when needed (though FlashRank loads fast)
        self.model_name = model_name
        self._ranker = None

    @property
    def ranker(self) -> Ranker:
        if self._ranker is None:
            self._ranker = Ranker(model_name=self.model_name)
        return self._ranker

    def rerank(
        self, query: str, documents: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank a list of documents based on relevance to the query.

        Args:
            query: The user query
            documents: List of document dicts (must contain 'content' or 'text')
            top_k: Number of results to return after reranking

        Returns:
            List of reranked documents with updated 'score' (0-1 range)
        """
        if not documents:
            return []

        # Debugging
        print(
            f"DEBUG: Reranker received {len(documents)} docs. Type of first: {type(documents[0])}"
        )
        # print(f"DEBUG: First doc content: {documents[0]}")

        # Format for FlashRank
        # Map doc_id to original document to reconstruct later
        doc_map = {}
        passages = []

        for i, doc in enumerate(documents):
            # Handle both dicts and objects (SearchResult)
            if isinstance(doc, dict):
                doc_id = doc.get("doc_id", str(i))
                text = doc.get("content", "") or doc.get("text", "")
            else:
                doc_id = getattr(doc, "doc_id", str(i))
                text = getattr(doc, "content", "")

            # Store in map
            doc_map[doc_id] = doc

            # Pass minimal meta to avoid FlashRank issues
            passages.append({"id": doc_id, "text": text, "meta": {"id": doc_id}})

        # Rerank
        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)

        # Process results
        reranked_docs = []
        for result in results[:top_k]:
            doc_id = result.get("id")  # FlashRank returns id
            if not doc_id and "meta" in result:
                doc_id = result["meta"].get("id")

            original_doc = doc_map.get(doc_id)
            if not original_doc:
                continue

            new_score = result["score"]

            if isinstance(original_doc, dict):
                original_doc["score"] = new_score
                original_doc["rerank_score"] = new_score
                reranked_docs.append(original_doc)
            else:
                # It's an object (SearchResult)
                try:
                    setattr(original_doc, "score", new_score)
                    original_doc.metadata["rerank_score"] = new_score
                except Exception:
                    pass
                reranked_docs.append(original_doc)

        return reranked_docs


# Singleton instance
reranker = RerankerService()
