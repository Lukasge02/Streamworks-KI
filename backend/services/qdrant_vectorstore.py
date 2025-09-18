"""
Qdrant Vector Store Service
Modern Qdrant integration with LlamaIndex for superior RAG performance
Replaces ChromaDB with enterprise-grade vector database
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    CollectionStatus,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    SparseVectorParams,
    SparseVector
)
from qdrant_client.http.exceptions import ResponseHandlingException

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.vector_stores.types import VectorStoreQuery

logger = logging.getLogger(__name__)


class QdrantVectorStoreService:
    """
    Enterprise-grade Qdrant Vector Store Service
    Provides high-performance vector operations for RAG pipeline
    """

    def __init__(self):
        self._initialized = False
        self._initialization_error = None

        # Core components
        self.client: Optional[QdrantClient] = None
        self.vector_store: Optional[QdrantVectorStore] = None
        self.collection_name = None

        # Hybrid search components
        self.hybrid_collection_name = None
        self.hybrid_vector_store: Optional[QdrantVectorStore] = None

        # Configuration from settings
        from config import settings
        self.settings = settings

    async def initialize(self) -> bool:
        """Initialize Qdrant vector store with connection validation"""
        if self._initialized:
            return True

        if self._initialization_error:
            raise self._initialization_error

        try:
            logger.info("🚀 Initializing Qdrant Vector Store Service...")

            # 1. Initialize Qdrant Client
            # Handle both local (no API key) and cloud (with API key) configurations
            client_config = {
                "url": self.settings.QDRANT_URL,
                "timeout": 30.0
            }

            # Only add API key if it's provided (for cloud setup)
            if self.settings.QDRANT_API_KEY and self.settings.QDRANT_API_KEY.strip():
                client_config["api_key"] = self.settings.QDRANT_API_KEY

            # Only add gRPC port for cloud setups
            if self.settings.QDRANT_USE_GRPC:
                client_config["grpc_port"] = 443

            self.client = QdrantClient(**client_config)

            # 2. Test connection
            try:
                collections = await asyncio.to_thread(self.client.get_collections)
                logger.info(f"✅ Qdrant connection established - Found {len(collections.collections)} collections")
            except Exception as conn_error:
                raise Exception(f"Failed to connect to Qdrant: {str(conn_error)}")

            # 3. Setup collection
            self.collection_name = self.settings.QDRANT_COLLECTION_NAME
            await self._ensure_collection_exists()

            # 4. Initialize LlamaIndex vector store wrapper
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                enable_hybrid=False,  # Use dense vectors only for BGE embeddings
                batch_size=100
            )

            logger.info(f"✅ Qdrant vector store initialized with collection: {self.collection_name}")

            # 5. Initialize Hybrid Search if enabled
            if self.settings.ENABLE_HYBRID_SEARCH:
                await self._setup_hybrid_collection()

            self._initialized = True
            logger.info("🎯 Qdrant Vector Store Service fully initialized!")
            return True

        except Exception as e:
            self._initialization_error = e
            logger.error(f"❌ Failed to initialize Qdrant Vector Store: {str(e)}")
            raise e

    async def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration"""
        try:
            # Check if collection exists
            collections = await asyncio.to_thread(self.client.get_collections)
            collection_exists = any(
                col.name == self.collection_name
                for col in collections.collections
            )

            if not collection_exists:
                logger.info(f"📝 Creating new Qdrant collection: {self.collection_name}")

                # Create collection with optimized settings for BGE embeddings
                await asyncio.to_thread(
                    self.client.create_collection,
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.settings.QDRANT_VECTOR_SIZE,  # BGE embeddings size (768)
                        distance=Distance.COSINE,  # Best for semantic similarity
                        hnsw_config={
                            "m": 16,  # Number of bi-directional links
                            "ef_construct": 200,  # Higher for better quality
                        }
                    ),
                    optimizers_config={
                        "deleted_threshold": 0.2,
                        "vacuum_min_vector_number": 1000,
                        "default_segment_number": 0,
                        "max_segment_size": 20000,
                        "memmap_threshold": 50000,
                        "indexing_threshold": 10000,
                        "flush_interval_sec": 5,
                        "max_optimization_threads": 1
                    },
                    # Enable payload indexing for fast filtering
                    payload_indexing_config={
                        "doc_id": {"type": "keyword"},
                        "doctype": {"type": "keyword"},
                        "chunk_type": {"type": "keyword"},
                        "file_name": {"type": "text"},
                        "processing_engine": {"type": "keyword"}
                    }
                )
                logger.info(f"✅ Collection '{self.collection_name}' created successfully")
            else:
                logger.info(f"✅ Collection '{self.collection_name}' already exists")

        except Exception as e:
            logger.error(f"❌ Failed to ensure collection exists: {str(e)}")
            raise

    async def _setup_hybrid_collection(self):
        """Setup hybrid collection with sparse + dense vector support"""
        try:
            logger.info("🚀 Setting up Hybrid Search collection...")

            self.hybrid_collection_name = self.settings.HYBRID_COLLECTION_NAME
            await self._ensure_hybrid_collection_exists()

            # Initialize hybrid vector store - use raw client instead of LlamaIndex wrapper to avoid FastEmbed dependency
            # We'll use the raw Qdrant client for hybrid operations since we're implementing our own hybrid logic
            self.hybrid_vector_store = True  # Flag to indicate hybrid collection is available

            logger.info(f"✅ Hybrid search collection initialized: {self.hybrid_collection_name}")

        except Exception as e:
            logger.error(f"❌ Failed to setup hybrid collection: {str(e)}")
            # Don't raise - fall back to regular collection
            logger.warning("⚠️ Hybrid search disabled - falling back to dense vector search only")

    async def _ensure_hybrid_collection_exists(self):
        """Ensure the hybrid collection exists with sparse + dense vector configuration"""
        try:
            # Check if hybrid collection exists
            collections = await asyncio.to_thread(self.client.get_collections)
            collection_exists = any(
                col.name == self.hybrid_collection_name
                for col in collections.collections
            )

            if not collection_exists:
                logger.info(f"📝 Creating new Qdrant hybrid collection: {self.hybrid_collection_name}")

                # Create hybrid collection with both dense and sparse vectors
                # Use the correct API: separate vectors_config and sparse_vectors_config
                await asyncio.to_thread(
                    self.client.create_collection,
                    collection_name=self.hybrid_collection_name,
                    vectors_config={
                        # Dense vectors for semantic similarity (BGE embeddings)
                        "dense": VectorParams(
                            size=self.settings.QDRANT_VECTOR_SIZE,  # BGE embeddings size (768)
                            distance=Distance.COSINE,  # Best for semantic similarity
                            hnsw_config={
                                "m": 16,  # Number of bi-directional links
                                "ef_construct": 200,  # Higher for better quality
                            }
                        )
                    },
                    sparse_vectors_config={
                        # Sparse vectors for keyword matching (BM25-style)
                        "sparse": SparseVectorParams()  # Use default sparse vector configuration
                    },
                    optimizers_config={
                        "deleted_threshold": 0.2,
                        "vacuum_min_vector_number": 1000,
                        "default_segment_number": 0,
                        "max_segment_size": 20000,
                        "memmap_threshold": 50000,
                        "indexing_threshold": 10000,
                        "flush_interval_sec": 5,
                        "max_optimization_threads": 1
                    }
                )
                logger.info(f"✅ Hybrid collection '{self.hybrid_collection_name}' created successfully")
            else:
                logger.info(f"✅ Hybrid collection '{self.hybrid_collection_name}' already exists")

        except Exception as e:
            logger.error(f"❌ Failed to ensure hybrid collection exists: {str(e)}")
            raise

    async def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add documents to Qdrant with batch processing

        Args:
            texts: List of text content
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries

        Returns:
            List of point IDs
        """
        if not await self.initialize():
            raise Exception("Failed to initialize Qdrant vector store")

        try:
            logger.info(f"📝 Adding {len(texts)} documents to Qdrant")

            points = []
            point_ids = []

            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
                # Generate unique point ID
                point_id = str(uuid.uuid4())
                point_ids.append(point_id)

                # Prepare payload with enhanced metadata
                payload = {
                    "text": text,
                    "doc_id": metadata.get("doc_id", "unknown"),
                    "chunk_id": metadata.get("chunk_id", f"chunk_{i}"),
                    "doctype": metadata.get("doctype", "general"),
                    "chunk_type": metadata.get("chunk_type", "text"),
                    "file_name": metadata.get("file_name", ""),
                    "processing_engine": metadata.get("processing_engine", "qdrant"),
                    "created_at": datetime.now().isoformat(),
                    "chunk_index": metadata.get("chunk_index", i),
                    "word_count": metadata.get("word_count", len(text.split())),
                    "char_count": metadata.get("char_count", len(text)),
                    **metadata  # Include all original metadata
                }

                points.append(PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                ))

            # Batch upsert to Qdrant
            await asyncio.to_thread(
                self.client.upsert,
                collection_name=self.collection_name,
                points=points
            )

            logger.info(f"✅ Successfully added {len(points)} documents to Qdrant")
            return point_ids

        except Exception as e:
            logger.error(f"❌ Failed to add documents to Qdrant: {str(e)}")
            raise

    async def add_hybrid_documents(
        self,
        texts: List[str],
        dense_embeddings: List[List[float]],
        sparse_vectors: List[Dict[int, float]],
        metadatas: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add documents to hybrid collection with both dense and sparse vectors

        Args:
            texts: List of text content
            dense_embeddings: List of dense embedding vectors (BGE)
            sparse_vectors: List of sparse vectors (BM25-style)
            metadatas: List of metadata dictionaries

        Returns:
            List of point IDs
        """
        if not self.hybrid_vector_store:
            raise Exception("Hybrid search not initialized - check configuration")

        try:
            logger.info(f"📝 Adding {len(texts)} documents to hybrid collection")

            from qdrant_client.models import SparseVector
            points = []
            point_ids = []

            for i, (text, dense_emb, sparse_vec, metadata) in enumerate(zip(texts, dense_embeddings, sparse_vectors, metadatas)):
                # Generate unique point ID
                point_id = str(uuid.uuid4())
                point_ids.append(point_id)

                # Prepare payload with enhanced metadata
                payload = {
                    "text": text,
                    "doc_id": metadata.get("doc_id", "unknown"),
                    "chunk_id": metadata.get("chunk_id", f"chunk_{i}"),
                    "doctype": metadata.get("doctype", "general"),
                    "chunk_type": metadata.get("chunk_type", "text"),
                    "file_name": metadata.get("file_name", ""),
                    "processing_engine": metadata.get("processing_engine", "hybrid_qdrant"),
                    "created_at": datetime.now().isoformat(),
                    "chunk_index": metadata.get("chunk_index", i),
                    "word_count": metadata.get("word_count", len(text.split())),
                    "char_count": metadata.get("char_count", len(text)),
                    "hybrid_enabled": True,  # Mark as hybrid document
                    **metadata  # Include all original metadata
                }

                # Convert sparse vector format for Qdrant
                # Create sparse vector in the correct format
                sparse_indices = list(sparse_vec.keys())
                sparse_values = list(sparse_vec.values())

                points.append(PointStruct(
                    id=point_id,
                    vector={
                        "dense": dense_emb,
                        "sparse": SparseVector(
                            indices=sparse_indices,
                            values=sparse_values
                        )
                    },
                    payload=payload
                ))

            # Batch upsert to Qdrant
            await asyncio.to_thread(
                self.client.upsert,
                collection_name=self.hybrid_collection_name,
                points=points
            )

            logger.info(f"✅ Successfully added {len(points)} hybrid documents to Qdrant")
            return point_ids

        except Exception as e:
            logger.error(f"❌ Failed to add hybrid documents to Qdrant: {str(e)}")
            raise

    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
        doc_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search in Qdrant

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            doc_filters: Optional metadata filters

        Returns:
            List of search results with content and metadata
        """
        if not await self.initialize():
            raise Exception("Failed to initialize Qdrant vector store")

        try:
            logger.info(f"🔍 Performing similarity search (top_k={top_k})")

            # Build filter if provided
            filter_conditions = None
            if doc_filters:
                conditions = []
                for key, value in doc_filters.items():
                    if value is None:
                        continue

                    try:
                        # Support common filter formats: scalar equality, lists, and {'$in': [...]} style
                        if isinstance(value, dict):
                            if "$in" in value and isinstance(value["$in"], (list, tuple, set)):
                                match_values = [item for item in value["$in"] if item is not None]
                                if match_values:
                                    conditions.append(
                                        FieldCondition(
                                            key=key,
                                            match=MatchAny(any=match_values)
                                        )
                                    )
                                continue

                            if "$eq" in value:
                                value = value["$eq"]
                            else:
                                # Unsupported complex operator – skip rather than failing the query
                                continue

                        if isinstance(value, (list, tuple, set)):
                            match_values = [item for item in value if item is not None]
                            if not match_values:
                                continue
                            conditions.append(
                                FieldCondition(
                                    key=key,
                                    match=MatchAny(any=match_values)
                                )
                            )
                        else:
                            conditions.append(
                                FieldCondition(
                                    key=key,
                                    match=MatchValue(value=value)
                                )
                            )
                    except Exception as filter_error:
                        logger.warning(
                            f"Skipping unsupported filter for key '{key}': {filter_error}"
                        )
                        continue

                if conditions:
                    filter_conditions = Filter(must=conditions)

            # Perform search
            search_results = await asyncio.to_thread(
                self.client.search,
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=filter_conditions,
                with_payload=True,
                with_vectors=False  # Don't return vectors to save bandwidth
            )

            # Format results
            results = []
            for result in search_results:
                results.append({
                    "content": result.payload.get("text", ""),
                    "metadata": {
                        k: v for k, v in result.payload.items()
                        if k != "text"
                    },
                    "score": float(result.score),
                    "point_id": str(result.id)
                })

            logger.info(f"✅ Found {len(results)} similar documents")
            return results

        except Exception as e:
            logger.error(f"❌ Similarity search failed: {str(e)}")
            raise

    async def delete_documents(self, doc_id: str) -> bool:
        """
        Delete all chunks for a document

        Args:
            doc_id: Document ID to delete

        Returns:
            Success status
        """
        if not await self.initialize():
            raise Exception("Failed to initialize Qdrant vector store")

        try:
            logger.info(f"🗑️ Deleting document {doc_id} from Qdrant")

            # Delete points with matching doc_id
            await asyncio.to_thread(
                self.client.delete,
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id)
                        )
                    ]
                )
            )

            logger.info(f"✅ Successfully deleted document {doc_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete document {doc_id}: {str(e)}")
            return False

    async def get_document_chunks(
        self,
        doc_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document from Qdrant

        Args:
            doc_id: Document ID
            limit: Maximum number of chunks to return
            offset: Number of chunks to skip

        Returns:
            List of chunks with content and metadata
        """
        if not await self.initialize():
            raise Exception("Failed to initialize Qdrant vector store")

        try:
            logger.info(f"🔍 Retrieving chunks for document {doc_id}")

            # Query all chunks for this document
            search_results = await asyncio.to_thread(
                self.client.scroll,
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id)
                        )
                    ]
                ),
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            # Format results
            chunks = []
            for point in search_results[0]:  # scroll returns (points, next_page_offset)
                chunk_metadata = {k: v for k, v in point.payload.items() if k != "text"}

                # Extract chunk index from metadata or chunk_id
                chunk_index = chunk_metadata.get("chunk_index", 0)
                if "chunk_id" in chunk_metadata and "_chunk_" in chunk_metadata["chunk_id"]:
                    try:
                        chunk_index = int(chunk_metadata["chunk_id"].split("_chunk_")[-1])
                    except (ValueError, IndexError):
                        pass

                chunks.append({
                    "id": str(point.id),
                    "document_id": doc_id,
                    "chunk_index": chunk_index,
                    "content": point.payload.get("text", ""),
                    "content_preview": point.payload.get("text", "")[:200] + "..." if len(point.payload.get("text", "")) > 200 else point.payload.get("text", ""),
                    "chunk_type": chunk_metadata.get("chunk_type", "text"),
                    "heading": chunk_metadata.get("heading"),
                    "section_name": chunk_metadata.get("section_name"),
                    "page_number": chunk_metadata.get("page_number"),
                    "metadata": {
                        **chunk_metadata,
                        "source": "qdrant"
                    },
                    "word_count": chunk_metadata.get("word_count", len(point.payload.get("text", "").split())),
                    "char_count": chunk_metadata.get("char_count", len(point.payload.get("text", ""))),
                    "created_at": chunk_metadata.get("created_at"),
                    "updated_at": chunk_metadata.get("updated_at")
                })

            # Sort by chunk_index for consistent ordering
            chunks.sort(key=lambda x: x["chunk_index"])

            logger.info(f"✅ Retrieved {len(chunks)} chunks for document {doc_id}")
            return chunks

        except Exception as e:
            logger.error(f"❌ Failed to retrieve chunks for document {doc_id}: {str(e)}")
            raise

    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        if not await self.initialize():
            raise Exception("Failed to initialize Qdrant vector store")

        try:
            collection_info = await asyncio.to_thread(
                self.client.get_collection,
                collection_name=self.collection_name
            )

            return {
                "collection_name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "points_count": collection_info.points_count,
                "segments_count": collection_info.segments_count,
                "status": collection_info.status.value,
                "optimizer_status": collection_info.optimizer_status,
                "config": {
                    "vector_size": collection_info.config.params.vectors.size,
                    "distance": collection_info.config.params.vectors.distance.value
                }
            }

        except Exception as e:
            logger.error(f"❌ Failed to get collection info: {str(e)}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check Qdrant service health"""
        try:
            health = {
                "service": "QdrantVectorStoreService",
                "status": "healthy",
                "initialized": self._initialized,
                "connection": {
                    "url": self.settings.QDRANT_URL,
                    "connected": False
                },
                "collection": {
                    "name": self.collection_name,
                    "exists": False,
                    "vectors_count": 0
                }
            }

            if self.client:
                try:
                    # Test connection
                    collections = await asyncio.to_thread(self.client.get_collections)
                    health["connection"]["connected"] = True

                    # Check collection
                    collection_exists = any(
                        col.name == self.collection_name
                        for col in collections.collections
                    )
                    health["collection"]["exists"] = collection_exists

                    if collection_exists:
                        info = await self.get_collection_info()
                        health["collection"]["vectors_count"] = info["vectors_count"]

                except Exception as e:
                    health["status"] = "unhealthy"
                    health["error"] = str(e)

            return health

        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "service": "QdrantVectorStoreService",
                "status": "unhealthy",
                "error": str(e)
            }

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.client:
                # Qdrant client doesn't need explicit cleanup
                self.client = None
            self.vector_store = None
            self._initialized = False
            logger.info("✅ Qdrant vector store cleaned up")
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {str(e)}")

    def get_vector_store(self) -> QdrantVectorStore:
        """Get the LlamaIndex vector store wrapper"""
        if not self._initialized or not self.vector_store:
            raise Exception("Qdrant vector store not initialized")
        return self.vector_store


# Global service instance
_qdrant_service = None

async def get_qdrant_service() -> QdrantVectorStoreService:
    """Get global Qdrant service instance"""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantVectorStoreService()
    return _qdrant_service
