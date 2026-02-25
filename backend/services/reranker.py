"""
OpenAI-based reranker.

Re-scores retrieval results by asking GPT to rate relevance,
providing better precision than embedding-only similarity.
"""

import json
import logging
from openai import OpenAI
from config import get_settings

logger = logging.getLogger(__name__)


def rerank(query: str, results: list[dict], top_k: int = 5) -> list[dict]:
    """
    Rerank search results using OpenAI.

    Sends the query and candidate passages to GPT-4o-mini for relevance
    scoring, then returns the top_k highest-scoring results.
    """
    if not results:
        return []

    if len(results) <= top_k:
        for r in results:
            r["rerank_score"] = r.get("score", 0.5)
        return results

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    passages = []
    for i, r in enumerate(results):
        text = r.get("text", "")[:500]
        passages.append(f"[{i}] {text}")

    prompt = f"""Bewerte die Relevanz jedes Textabschnitts fuer die Frage.
Antworte als JSON-Array mit Objekten: [{{"id": 0, "score": 0.85}}, ...]
Score von 0.0 (irrelevant) bis 1.0 (perfekt relevant).

Frage: {query}

Abschnitte:
{chr(10).join(passages)}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        # Handle various JSON shapes: array directly, or object with known keys
        if isinstance(parsed, list):
            scores = parsed
        elif isinstance(parsed, dict):
            # Try common key names, fallback to first list value in the dict
            for key in ("scores", "results", "rankings", "items", "data"):
                if key in parsed and isinstance(parsed[key], list):
                    scores = parsed[key]
                    break
            else:
                # Use the first list value found in the dict
                scores = next(
                    (v for v in parsed.values() if isinstance(v, list)),
                    [],
                )
        else:
            scores = []

        score_map = {}
        for item in scores:
            idx = item.get("id", -1)
            score = item.get("score", 0)
            if 0 <= idx < len(results):
                score_map[idx] = float(score)

        reranked = []
        for i, r in enumerate(results):
            copy = r.copy()
            copy["rerank_score"] = score_map.get(i, r.get("score", 0))
            reranked.append(copy)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]

    except Exception as e:
        logger.warning(f"Reranking failed, using original order: {e}")
        for r in results:
            r["rerank_score"] = r.get("score", 0.5)
        return results[:top_k]
