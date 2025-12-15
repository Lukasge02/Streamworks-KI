"""
Cross-Encoder Reranker
High-precision reranking of search results using GPT-based relevance scoring
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import openai

from config import config


@dataclass
class RankedResult:
    """A search result with reranking score"""

    doc_id: str
    content: str
    filename: str
    original_score: float
    rerank_score: float
    relevance_explanation: str
    metadata: Dict[str, Any]


class CrossEncoderReranker:
    """
    Cross-Encoder Reranker using GPT

    Unlike bi-encoder similarity (used in initial retrieval), cross-encoders
    look at query and document together, providing much more accurate
    relevance judgments.

    This implementation uses GPT for scoring, with options for:
    1. Batch scoring (faster, less accurate)
    2. Individual scoring (slower, more accurate)
    """

    RERANK_PROMPT = """Bewerte die Relevanz des folgenden Dokument-Auszugs für die Benutzeranfrage.

Anfrage: {query}

Dokument ({filename}):
---
{content}
---

Bewerte auf einer Skala von 0-10:
- 0-2: Nicht relevant, andere Thematik
- 3-4: Schwach relevant, erwähnt ähnliche Begriffe
- 5-6: Teilweise relevant, behandelt verwandtes Thema
- 7-8: Relevant, beantwortet Teile der Frage
- 9-10: Hochrelevant, beantwortet die Frage direkt

Antworte im Format:
SCORE: [Zahl]
GRUND: [Kurze Erklärung in einem Satz]"""

    BATCH_RERANK_PROMPT = """Du bewertest Suchergebnisse für die Anfrage: "{query}"

Ordne die folgenden Dokumente nach Relevanz (von am relevantesten zu am wenigsten relevant).

Dokumente:
{documents}

Antworte NUR mit den Nummern in der neuen Reihenfolge, getrennt durch Kommas.
Beispiel: 3, 1, 4, 2, 5"""

    def __init__(self, use_batch_mode: bool = True):
        self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.LLM_MODEL
        self.use_batch_mode = use_batch_mode
        self._enabled = config.RAG_RERANK_ENABLED
        self._top_k = config.RAG_RERANK_TOP_K

    def rerank(
        self, query: str, results: List[Dict[str, Any]], top_k: int = None
    ) -> List[RankedResult]:
        """
        Rerank search results using cross-encoder scoring.

        Args:
            query: Original user query
            results: List of search results to rerank
            top_k: Number of top results to return (default: config value)

        Returns:
            List of RankedResult objects sorted by relevance
        """
        if not self._enabled or not results:
            return self._convert_to_ranked(results, top_k or self._top_k)

        top_k = top_k or self._top_k

        if self.use_batch_mode:
            return self._batch_rerank(query, results, top_k)
        else:
            return self._individual_rerank(query, results, top_k)

    def _batch_rerank(
        self, query: str, results: List[Dict[str, Any]], top_k: int
    ) -> List[RankedResult]:
        """Rerank using batch comparison (faster, 1 API call)"""
        try:
            # Format documents for batch prompt
            doc_strings = []
            for i, r in enumerate(results, 1):
                content = r.get("content", "")[:300]
                filename = r.get("filename", "Unknown")
                doc_strings.append(f"[{i}] {filename}: {content}...")

            documents_text = "\n".join(doc_strings)

            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": self.BATCH_RERANK_PROMPT.format(
                            query=query, documents=documents_text
                        ),
                    }
                ],
                temperature=0,
                max_tokens=50,
            )

            # Parse response to get new order
            order_str = response.choices[0].message.content.strip()

            # Extract numbers from response
            import re

            numbers = re.findall(r"\d+", order_str)
            new_order = [
                int(n) - 1 for n in numbers if n.isdigit()
            ]  # Convert to 0-indexed

            # Reorder results
            reordered = []
            seen = set()

            # First, add results in the new order
            for idx in new_order:
                if 0 <= idx < len(results) and idx not in seen:
                    reordered.append(results[idx])
                    seen.add(idx)

            # Add any missing results at the end
            for idx, r in enumerate(results):
                if idx not in seen:
                    reordered.append(r)

            # Convert to RankedResult with calculated scores
            ranked = []
            for i, r in enumerate(reordered[:top_k]):
                # Score decreases based on position
                rerank_score = 1.0 - (i / len(reordered))

                ranked.append(
                    RankedResult(
                        doc_id=r.get("doc_id", ""),
                        content=r.get("content", ""),
                        filename=r.get("filename", "Unknown"),
                        original_score=r.get("score", 0),
                        rerank_score=rerank_score,
                        relevance_explanation="Batch reranked",
                        metadata=r.get("metadata", {}),
                    )
                )

            return ranked

        except Exception as e:
            print(f"⚠️ Batch reranking failed: {e}")
            return self._convert_to_ranked(results, top_k)

    def _individual_rerank(
        self, query: str, results: List[Dict[str, Any]], top_k: int
    ) -> List[RankedResult]:
        """Rerank by scoring each document individually (more accurate)"""
        scored_results = []

        for r in results:
            try:
                content = r.get("content", "")[:500]  # Limit content length
                filename = r.get("filename", "Unknown")

                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": self.RERANK_PROMPT.format(
                                query=query, filename=filename, content=content
                            ),
                        }
                    ],
                    temperature=0,
                    max_tokens=100,
                )

                result_text = response.choices[0].message.content.strip()

                # Parse score and reason
                score, reason = self._parse_score_response(result_text)

                scored_results.append(
                    RankedResult(
                        doc_id=r.get("doc_id", ""),
                        content=r.get("content", ""),
                        filename=filename,
                        original_score=r.get("score", 0),
                        rerank_score=score / 10.0,  # Normalize to 0-1
                        relevance_explanation=reason,
                        metadata=r.get("metadata", {}),
                    )
                )

            except Exception as e:
                print(f"⚠️ Individual reranking failed for {r.get('filename')}: {e}")
                scored_results.append(
                    RankedResult(
                        doc_id=r.get("doc_id", ""),
                        content=r.get("content", ""),
                        filename=r.get("filename", "Unknown"),
                        original_score=r.get("score", 0),
                        rerank_score=r.get("score", 0),
                        relevance_explanation="Scoring failed",
                        metadata=r.get("metadata", {}),
                    )
                )

        # Sort by rerank score
        scored_results.sort(key=lambda x: x.rerank_score, reverse=True)

        return scored_results[:top_k]

    def _parse_score_response(self, text: str) -> Tuple[float, str]:
        """Parse score and reason from LLM response"""
        import re

        # Try to find SCORE: pattern
        score_match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
        reason_match = re.search(r"GRUND:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)

        score = float(score_match.group(1)) if score_match else 5.0
        reason = reason_match.group(1).strip() if reason_match else "No explanation"

        # Clamp score
        score = max(0, min(10, score))

        return score, reason

    def _convert_to_ranked(
        self, results: List[Dict[str, Any]], top_k: int
    ) -> List[RankedResult]:
        """Convert raw results to RankedResult without reranking"""
        return [
            RankedResult(
                doc_id=r.get("doc_id", ""),
                content=r.get("content", ""),
                filename=r.get("filename", "Unknown"),
                original_score=r.get("score", 0),
                rerank_score=r.get("score", 0),
                relevance_explanation="Not reranked",
                metadata=r.get("metadata", {}),
            )
            for r in results[:top_k]
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get reranker statistics"""
        return {
            "enabled": self._enabled,
            "batch_mode": self.use_batch_mode,
            "top_k": self._top_k,
            "model": self.model,
        }


# Singleton instance
reranker = CrossEncoderReranker()
