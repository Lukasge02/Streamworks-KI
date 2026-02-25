"""
Qdrant vector store with OpenAI embeddings.

Handles embedding generation, chunk upsert, similarity search,
and collection lifecycle management.
"""

import logging
import uuid
from functools import lru_cache
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchAny,
)
from config import get_settings

logger = logging.getLogger(__name__)

VECTOR_DIM = 3072  # text-embedding-3-large dimensionality


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Return a cached Qdrant client singleton."""
    settings = get_settings()
    return QdrantClient(url=settings.qdrant_url)


def _get_openai_client() -> OpenAI:
    """Return an OpenAI client (not cached -- lightweight object)."""
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key)


def ensure_collection() -> None:
    """
    Create the Qdrant collection if it does not already exist.

    Uses cosine distance and 3072-dimensional vectors to match
    the text-embedding-3-large model output.
    """
    settings = get_settings()
    client = get_qdrant_client()
    collection_name = settings.qdrant_collection

    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_DIM,
                distance=Distance.COSINE,
            ),
        )
        logger.info(
            "Created Qdrant collection '%s' (dim=%d, cosine)",
            collection_name,
            VECTOR_DIM,
        )
    else:
        logger.debug("Qdrant collection '%s' already exists", collection_name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts using OpenAI.

    Args:
        texts: The texts to embed.

    Returns:
        A list of embedding vectors (each 3072-dimensional).
    """
    if not texts:
        return []

    settings = get_settings()
    client = _get_openai_client()

    response = client.embeddings.create(
        model=settings.openai_embed_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


def upsert_chunks(document_id: str, chunks: list[dict]) -> None:
    """
    Upsert pre-embedded chunks into Qdrant.

    Each chunk dict must contain:
        - text (str): The chunk text content.
        - embedding (list[float]): The precomputed embedding vector.
        - metadata (dict, optional): Additional metadata (page, etc.).

    A ``document_id`` payload field is added to every point so that
    chunks can be filtered or deleted by document later.

    Args:
        document_id: Unique identifier for the source document.
        chunks: List of chunk dicts with text, embedding, and optional metadata.
    """
    settings = get_settings()
    client = get_qdrant_client()

    points = []
    for chunk in chunks:
        payload = {
            "document_id": document_id,
            "text": chunk["text"],
        }
        if "metadata" in chunk and chunk["metadata"]:
            payload.update(chunk["metadata"])

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=chunk["embedding"],
                payload=payload,
            )
        )

    if points:
        client.upsert(
            collection_name=settings.qdrant_collection,
            points=points,
        )
        logger.info(
            "Upserted %d chunks for document %s", len(points), document_id
        )


def search(
    query_embedding: list[float],
    limit: int = 10,
    filter_doc_ids: list[str] | None = None,
) -> list[dict]:
    """
    Search Qdrant for the nearest chunks to the given embedding.

    Args:
        query_embedding: The query vector (3072-dim).
        limit: Maximum number of results.
        filter_doc_ids: If provided, restrict search to these document IDs.

    Returns:
        A list of dicts, each with keys: id, text, score, document_id,
        plus any additional metadata fields stored in the payload.
    """
    settings = get_settings()
    client = get_qdrant_client()

    query_filter = None
    if filter_doc_ids:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchAny(any=filter_doc_ids),
                )
            ]
        )

    hits = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_embedding,
        limit=limit,
        query_filter=query_filter,
    )

    results = []
    for hit in hits:
        result = {
            "id": str(hit.id),
            "score": hit.score,
        }
        if hit.payload:
            result.update(hit.payload)
        results.append(result)

    return results


def delete_document(document_id: str) -> None:
    """
    Delete all chunks belonging to a given document.

    Args:
        document_id: The document whose chunks should be removed.
    """
    settings = get_settings()
    client = get_qdrant_client()

    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchAny(any=[document_id]),
                )
            ]
        ),
    )
    logger.info("Deleted all chunks for document %s", document_id)


def scroll_all(limit: int = 1000) -> list[dict]:
    """
    Scroll through all points in the collection.

    Useful for building external indexes (e.g. BM25).

    Args:
        limit: Batch size per scroll request.

    Returns:
        A flat list of payload dicts from every point.
    """
    settings = get_settings()
    client = get_qdrant_client()

    all_payloads: list[dict] = []
    offset = None

    while True:
        results, next_offset = client.scroll(
            collection_name=settings.qdrant_collection,
            limit=limit,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in results:
            if point.payload:
                entry = {"id": str(point.id)}
                entry.update(point.payload)
                all_payloads.append(entry)

        if next_offset is None:
            break
        offset = next_offset

    return all_payloads
