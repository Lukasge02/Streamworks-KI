"""
RAG query orchestration service.

Coordinates hybrid search, cross-encoder reranking, context assembly,
and LLM generation to answer user questions with cited sources.
"""

import json
import logging
from openai import OpenAI
from config import get_settings
from services.hybrid_search import HybridSearcher
from services import reranker as reranker_service

logger = logging.getLogger(__name__)

# Module-level singleton for the hybrid searcher
_hybrid_searcher: HybridSearcher | None = None

SYSTEM_PROMPT = """\
Du bist ein hilfreicher Streamworks-Experte und Assistent fuer ein Enterprise-Automatisierungssystem.

Deine Aufgabe:
- Beantworte Fragen praezise und ausfuehrlich basierend auf dem bereitgestellten Kontext.
- Zitiere deine Quellen mit Referenzen wie [1], [2] usw., die den Kontext-Abschnitten entsprechen.
- Wenn der Kontext nicht ausreicht, um die Frage zu beantworten, sage das ehrlich.
- Erfinde keine Informationen, die nicht im Kontext enthalten sind.
- Antworte in der gleichen Sprache, in der die Frage gestellt wurde.
- Strukturiere deine Antwort klar und uebersichtlich.

Kontext:
{context}

Quellen:
{sources}
"""


def _get_hybrid_searcher() -> HybridSearcher:
    """Return the module-level HybridSearcher singleton."""
    global _hybrid_searcher
    if _hybrid_searcher is None:
        _hybrid_searcher = HybridSearcher()
    return _hybrid_searcher


def mark_index_dirty() -> None:
    """
    Signal that the BM25 index should be rebuilt on the next query.

    Call this after documents are added or removed.
    """
    searcher = _get_hybrid_searcher()
    searcher.mark_dirty()


def _build_context_and_sources(
    results: list[dict],
) -> tuple[str, str, list[dict]]:
    """
    Build the context string and source references from reranked results.

    Args:
        results: Reranked result dicts.

    Returns:
        A tuple of (context_str, sources_str, source_list).
    """
    context_parts: list[str] = []
    sources_parts: list[str] = []
    source_list: list[dict] = []

    for idx, result in enumerate(results, start=1):
        text = result.get("text", "")
        doc_name = result.get("document_name", "Unbekannt")
        page = result.get("page")

        context_parts.append(f"[{idx}] {text}")

        page_info = f", Seite {page}" if page else ""
        sources_parts.append(f"[{idx}] {doc_name}{page_info}")
        source_list.append({
            "index": idx,
            "document_name": doc_name,
            "page": page,
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "score": result.get("rerank_score", result.get("score", 0.0)),
        })

    return "\n\n".join(context_parts), "\n".join(sources_parts), source_list


def _estimate_confidence(results: list[dict]) -> float:
    """
    Estimate answer confidence based on retrieval and reranking scores.

    Returns a value between 0.0 and 1.0.
    """
    if not results:
        return 0.0

    top_score = results[0].get("rerank_score", results[0].get("score", 0.0))

    # Average of top 3 rerank scores (if available)
    top_scores = [
        r.get("rerank_score", r.get("score", 0.0)) for r in results[:3]
    ]
    avg_score = sum(top_scores) / len(top_scores)

    # Weighted combination: 60% top score, 40% average
    confidence = 0.6 * float(top_score) + 0.4 * float(avg_score)
    return round(min(max(confidence, 0.0), 1.0), 3)


def _build_messages(
    question: str,
    context_str: str,
    sources_str: str,
    chat_history: list[dict] | None = None,
) -> list[dict]:
    """
    Assemble the message list for the OpenAI chat completion call.

    Args:
        question: The user question.
        context_str: Formatted context from retrieval.
        sources_str: Formatted source references.
        chat_history: Optional prior conversation turns.

    Returns:
        A list of message dicts for the OpenAI API.
    """
    system_message = SYSTEM_PROMPT.format(
        context=context_str,
        sources=sources_str,
    )

    messages = [{"role": "system", "content": system_message}]

    if chat_history:
        for turn in chat_history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": question})
    return messages


def query(
    question: str,
    chat_history: list[dict] | None = None,
) -> dict:
    """
    Answer a question using the full RAG pipeline.

    Pipeline:
    1. Hybrid search (BM25 + semantic) to find relevant chunks.
    2. Cross-encoder reranking to improve precision.
    3. Context assembly with numbered source references.
    4. OpenAI chat completion with the enriched prompt.
    5. Confidence estimation based on retrieval scores.

    Args:
        question: The user's question.
        chat_history: Optional list of prior conversation turns,
            each a dict with 'role' and 'content'.

    Returns:
        A dict with keys: answer, sources, confidence.
    """
    try:
        settings = get_settings()
        searcher = _get_hybrid_searcher()

        # 1. Hybrid search
        raw_results = searcher.search(query=question, limit=15)

        # 2. Rerank
        reranked = reranker_service.rerank(
            query=question,
            results=raw_results,
            top_k=5,
        )

        # 3. Build context
        context_str, sources_str, source_list = _build_context_and_sources(reranked)

        # 4. LLM generation
        if not reranked:
            return {
                "answer": (
                    "Es konnten keine relevanten Informationen zu Ihrer Frage "
                    "gefunden werden. Bitte formulieren Sie die Frage um oder "
                    "stellen Sie sicher, dass die entsprechenden Dokumente "
                    "hochgeladen wurden."
                ),
                "sources": [],
                "confidence": 0.0,
            }

        messages = _build_messages(question, context_str, sources_str, chat_history)

        client = OpenAI(api_key=settings.openai_api_key)
        completion = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.2,
            max_tokens=2048,
        )
        answer = completion.choices[0].message.content or ""

        # 5. Confidence
        confidence = _estimate_confidence(reranked)

        return {
            "answer": answer,
            "sources": source_list,
            "confidence": confidence,
        }
    except (ConnectionError, OSError) as e:
        logger.warning("RAG query failed (service unavailable): %s", e)
        return {
            "answer": (
                "Die Wissensdatenbank ist derzeit nicht erreichbar. "
                "Bitte stellen Sie sicher, dass Qdrant laeuft "
                "(make infra) und laden Sie Dokumente hoch."
            ),
            "sources": [],
            "confidence": 0.0,
        }
    except Exception as e:
        logger.error("RAG query failed unexpectedly: %s", e)
        return {
            "answer": (
                "Bei der Verarbeitung Ihrer Frage ist ein Fehler aufgetreten. "
                "Bitte versuchen Sie es erneut."
            ),
            "sources": [],
            "confidence": 0.0,
        }


def query_stream(
    question: str,
    chat_history: list[dict] | None = None,
):
    """
    Stream an answer using Server-Sent Events (SSE).

    Yields SSE-formatted strings that can be returned directly from
    a FastAPI StreamingResponse.

    The stream emits three event types:
    - ``chunk``: Incremental answer text tokens.
    - ``sources``: JSON payload with source references (sent once before chunks).
    - ``done``: Final event with confidence score.

    Args:
        question: The user's question.
        chat_history: Optional list of prior conversation turns.

    Yields:
        SSE-formatted strings (``data: ...\\n\\n``).
    """
    try:
        settings = get_settings()
        searcher = _get_hybrid_searcher()

        # 1. Hybrid search
        raw_results = searcher.search(query=question, limit=15)

        # 2. Rerank
        reranked = reranker_service.rerank(
            query=question,
            results=raw_results,
            top_k=5,
        )

        # 3. Build context
        context_str, sources_str, source_list = _build_context_and_sources(reranked)

        if not reranked:
            no_result_msg = (
                "Es konnten keine relevanten Informationen zu Ihrer Frage "
                "gefunden werden."
            )
            yield {"type": "sources", "data": []}
            yield {"type": "chunk", "data": no_result_msg}
            yield {"type": "done", "data": 0.0}
            return

        # Emit sources first so the frontend can render them immediately
        yield {"type": "sources", "data": source_list}

        # 4. Streaming LLM generation
        messages = _build_messages(question, context_str, sources_str, chat_history)

        client = OpenAI(api_key=settings.openai_api_key)
        stream = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.2,
            max_tokens=2048,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield {"type": "chunk", "data": delta.content}

        # 5. Done event with confidence
        confidence = _estimate_confidence(reranked)
        yield {"type": "done", "data": confidence}

    except (ConnectionError, OSError) as e:
        logger.warning("RAG stream failed (service unavailable): %s", e)
        error_msg = (
            "Die Wissensdatenbank ist derzeit nicht erreichbar. "
            "Bitte stellen Sie sicher, dass Qdrant laeuft "
            "(make infra) und laden Sie Dokumente hoch."
        )
        yield {"type": "sources", "data": []}
        yield {"type": "chunk", "data": error_msg}
        yield {"type": "done", "data": 0.0}
    except Exception as e:
        logger.error("RAG stream failed unexpectedly: %s", e)
        yield {"type": "sources", "data": []}
        yield {"type": "chunk", "data": "Bei der Verarbeitung ist ein Fehler aufgetreten."}
        yield {"type": "done", "data": 0.0}
