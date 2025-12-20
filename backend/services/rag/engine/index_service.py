"""
LlamaIndex Index Service

Manages Qdrant VectorStoreIndex for document storage and retrieval.
Uses existing 'streamworks_documents' collection for backward compatibility.
"""

from typing import Optional, List, Dict, Any

from qdrant_client import QdrantClient
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import TextNode
from llama_index.vector_stores.qdrant import QdrantVectorStore

from .settings import LlamaIndexSettings, configure_llamaindex


class IndexService:
    """
    Central Index Management Service

    Connects LlamaIndex to existing Qdrant collection.
    Supports:
    - Document indexing with metadata
    - Vector similarity search
    - Metadata filtering for access control
    """

    def __init__(self):
        # Ensure LlamaIndex is configured
        configure_llamaindex()

        self._client: Optional[QdrantClient] = None
        self._vector_store: Optional[QdrantVectorStore] = None
        self._index: Optional[VectorStoreIndex] = None

    @property
    def client(self) -> QdrantClient:
        """Lazy-loaded Qdrant client"""
        if self._client is None:
            self._client = QdrantClient(
                host=LlamaIndexSettings.QDRANT_HOST,
                port=LlamaIndexSettings.QDRANT_PORT,
            )
        return self._client

    @property
    def vector_store(self) -> QdrantVectorStore:
        """Lazy-loaded Qdrant vector store"""
        if self._vector_store is None:
            # Use 'content' field to match existing documents in Qdrant
            # (old VectorStore stored text as 'content', not 'text')
            self._vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=LlamaIndexSettings.COLLECTION_NAME,
                content_payload_key="content",  # Match existing schema
            )
        return self._vector_store

    @property
    def index(self) -> VectorStoreIndex:
        """Lazy-loaded VectorStoreIndex connected to Qdrant"""
        if self._index is None:
            storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )
            self._index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                storage_context=storage_context,
            )
        return self._index

    def add_nodes(self, nodes: List[TextNode]) -> List[str]:
        """
        Add nodes to the index

        Args:
            nodes: List of TextNode objects with content and metadata

        Returns:
            List of node IDs
        """
        self.index.insert_nodes(nodes)
        return [node.node_id for node in nodes]

    def delete_nodes(self, node_ids: List[str]) -> bool:
        """
        Delete nodes by ID

        Args:
            node_ids: List of node IDs to delete

        Returns:
            True if successful
        """
        try:
            self.index.delete_nodes(node_ids)
            return True
        except Exception as e:
            print(f"❌ Error deleting nodes: {e}")
            return False

    def delete_by_doc_id(self, doc_id: str) -> int:
        """
        Delete all nodes belonging to a document

        Uses parent_doc_id metadata filter.

        Args:
            doc_id: Parent document ID

        Returns:
            Number of nodes deleted
        """
        from qdrant_client.http import models

        try:
            # Find and delete nodes with matching parent_doc_id
            result = self.client.scroll(
                collection_name=LlamaIndexSettings.COLLECTION_NAME,
                limit=1000,
                scroll_filter=models.Filter(
                    should=[
                        models.FieldCondition(
                            key="parent_doc_id",
                            match=models.MatchValue(value=doc_id),
                        ),
                        models.FieldCondition(
                            key="doc_id",
                            match=models.MatchValue(value=doc_id),
                        ),
                    ]
                ),
            )

            points_to_delete = [point.id for point in result[0]]

            if points_to_delete:
                self.client.delete(
                    collection_name=LlamaIndexSettings.COLLECTION_NAME,
                    points_selector=models.PointIdsList(points=points_to_delete),
                )
                print(f"✅ Deleted {len(points_to_delete)} nodes for doc_id: {doc_id}")
                return len(points_to_delete)

            return 0

        except Exception as e:
            print(f"❌ Error deleting by doc_id: {e}")
            return 0

    def get_retriever(
        self,
        top_k: int = None,
        filters: Dict[str, Any] = None,
    ):
        """
        Get a retriever for querying the index

        Args:
            top_k: Number of results to retrieve
            filters: Metadata filters (e.g., category, access control)

        Returns:
            VectorIndexRetriever instance
        """
        from llama_index.core.vector_stores import MetadataFilters, MetadataFilter

        top_k = top_k or LlamaIndexSettings.TOP_K

        # Build metadata filters if provided
        llama_filters = None
        if filters:
            filter_list = []
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, list):
                        # For list values, create OR conditions
                        for v in value:
                            filter_list.append(MetadataFilter(key=key, value=v))
                    else:
                        filter_list.append(MetadataFilter(key=key, value=value))

            if filter_list:
                llama_filters = MetadataFilters(filters=filter_list)

        return self.index.as_retriever(
            similarity_top_k=top_k,
            filters=llama_filters,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            info = self.client.get_collection(LlamaIndexSettings.COLLECTION_NAME)
            return {
                "collection": LlamaIndexSettings.COLLECTION_NAME,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status.value,
                "embedding_dimension": LlamaIndexSettings.EMBEDDING_DIMENSION,
                "llm_model": LlamaIndexSettings.LLM_MODEL,
            }
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
_index_service: Optional[IndexService] = None


def get_index_service() -> IndexService:
    """Get singleton IndexService instance"""
    global _index_service
    if _index_service is None:
        _index_service = IndexService()
    return _index_service
