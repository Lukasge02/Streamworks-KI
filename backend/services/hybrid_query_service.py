"""
Hybrid Query Service für Streamworks-KI
Führt BM25 + Vector Hybrid Search mit Qdrant durch
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from qdrant_client.models import SparseVector
from config import settings
from .hybrid_text_processor import get_hybrid_text_processor
from .qdrant_vectorstore import get_qdrant_service

logger = logging.getLogger(__name__)


class HybridQueryService:
    """
    Hybrid Query Service für kombinierte BM25 + Vector Search

    Features:
    - Qdrant native hybrid search (sparse + dense vectors)
    - Configurable score fusion weights
    - Mode-specific optimization
    - Fallback zu pure vector search
    """

    def __init__(self):
        self._initialized = False
        self._qdrant_service = None
        self._text_processor = None
        self._embed_model = None

    async def initialize(self) -> bool:
        """Initialize Hybrid Query Service"""
        if self._initialized:
            return True

        try:
            logger.info("🚀 Initializing Hybrid Query Service...")

            # Check if hybrid search is enabled
            if not settings.ENABLE_HYBRID_SEARCH:
                logger.info("⚠️ Hybrid search disabled in configuration")
                return False

            # Initialize dependencies
            self._qdrant_service = await get_qdrant_service()
            await self._qdrant_service.initialize()

            # Check if hybrid collection is available
            if not self._qdrant_service.hybrid_vector_store:
                logger.warning("⚠️ Hybrid collection not available - check Qdrant configuration")
                return False

            self._text_processor = get_hybrid_text_processor()

            # Get embedding model (from RAG service)
            from .qdrant_rag_service import get_rag_service
            rag_service = await get_rag_service()
            await rag_service.initialize()
            self._embed_model = rag_service.embed_model

            logger.info("✅ Hybrid Query Service initialized successfully")
            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Hybrid Query Service: {str(e)}")
            return False

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
        score_threshold: float = 0.0,
        doc_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining dense and sparse vectors

        Args:
            query: Search query
            top_k: Number of results to return
            dense_weight: Weight for dense vector (semantic) search
            sparse_weight: Weight for sparse vector (keyword) search
            score_threshold: Minimum score threshold
            doc_filters: Optional metadata filters

        Returns:
            List of search results with metadata
        """
        if not await self.initialize():
            logger.warning("⚠️ Hybrid search not available - falling back to dense search")
            return await self._fallback_dense_search(query, top_k, score_threshold, doc_filters)

        try:
            start_time = time.time()
            logger.info(f"🔍 Starting hybrid search: {query[:100]}...")

            # 1. Generate dense embedding
            dense_embedding = await asyncio.to_thread(
                self._embed_model.get_text_embedding,
                query
            )

            # 2. Generate sparse vector
            sparse_vector_dict = self._text_processor.process_query(query)

            if not sparse_vector_dict:
                logger.warning("⚠️ No sparse vector generated - falling back to dense search")
                return await self._fallback_dense_search(query, top_k, score_threshold, doc_filters)

            # Convert sparse vector format for Qdrant query
            sparse_indices = list(sparse_vector_dict.keys())
            sparse_values = list(sparse_vector_dict.values())

            from qdrant_client.models import SparseVector
            sparse_vector = SparseVector(
                indices=sparse_indices,
                values=sparse_values
            )

            # 3. Build filter conditions
            filter_conditions = self._build_filter_conditions(doc_filters)

            # 4. Perform hybrid search using the correct API format
            # Use query_points with prefetch for hybrid search
            from qdrant_client.models import Prefetch, FusionQuery, Fusion

            search_results = await asyncio.to_thread(
                self._qdrant_service.client.query_points,
                collection_name=self._qdrant_service.hybrid_collection_name,
                prefetch=[
                    # Sparse vector search
                    Prefetch(
                        query=sparse_vector,
                        using="sparse",
                        limit=top_k * 2,  # Get more results for fusion
                        filter=filter_conditions
                    ),
                    # Dense vector search
                    Prefetch(
                        query=dense_embedding,
                        using="dense",
                        limit=top_k * 2,  # Get more results for fusion
                        filter=filter_conditions
                    ),
                ],
                query=FusionQuery(fusion=Fusion.RRF),  # Use Reciprocal Rank Fusion
                limit=top_k,
                with_payload=True,
                with_vectors=False  # Don't return vectors to save bandwidth
            )

            # 5. Format results
            if hasattr(search_results, 'points'):
                # QueryResponse with points attribute
                points_list = search_results.points
            elif isinstance(search_results, (list, tuple)):
                # Direct list/tuple of points
                points_list = search_results
            else:
                logger.error(f"❌ Unexpected response format: {type(search_results)}")
                points_list = []

            results = []
            for result in points_list:
                # Handle ScoredPoint format from query_points API
                if hasattr(result, 'payload') and hasattr(result, 'score') and hasattr(result, 'id'):
                    results.append({
                        "content": result.payload.get("text", ""),
                        "metadata": {
                            k: v for k, v in result.payload.items()
                            if k != "text"
                        },
                        "score": float(result.score),
                        "point_id": str(result.id),
                        "search_type": "hybrid"
                    })
                else:
                    logger.warning(f"⚠️ Skipping unknown result format: {type(result)}")

            processing_time = int((time.time() - start_time) * 1000)
            logger.info(f"✅ Hybrid search completed: {len(results)} results in {processing_time}ms")

            return results

        except Exception as e:
            logger.error(f"❌ Hybrid search failed: {str(e)}")
            logger.warning("⚠️ Falling back to dense vector search")
            return await self._fallback_dense_search(query, top_k, score_threshold, doc_filters)

    async def _fallback_dense_search(
        self,
        query: str,
        top_k: int,
        score_threshold: float,
        doc_filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fallback to pure dense vector search when hybrid fails"""
        try:
            # Generate dense embedding
            dense_embedding = await asyncio.to_thread(
                self._embed_model.get_text_embedding,
                query
            )

            # Use regular similarity search
            results = await self._qdrant_service.similarity_search(
                query_embedding=dense_embedding,
                top_k=top_k,
                score_threshold=score_threshold,
                doc_filters=doc_filters
            )

            # Mark as dense search
            for result in results:
                result["search_type"] = "dense_fallback"

            return results

        except Exception as e:
            logger.error(f"❌ Fallback dense search also failed: {str(e)}")
            return []

    def _build_filter_conditions(self, doc_filters: Optional[Dict[str, Any]]):
        """Build Qdrant filter conditions from doc_filters"""
        if not doc_filters:
            return None

        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

            conditions = []
            for key, value in doc_filters.items():
                if value is None:
                    continue

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

            return Filter(must=conditions) if conditions else None

        except Exception as e:
            logger.warning(f"Failed to build filter conditions: {str(e)}")
            return None

    async def search_with_mode_optimization(
        self,
        query: str,
        mode: str = "accurate",
        top_k: int = 10,
        doc_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search with mode-specific weight optimization

        Args:
            query: Search query
            mode: Search mode (fast, accurate, comprehensive)
            top_k: Number of results
            doc_filters: Optional filters

        Returns:
            Search results optimized for the specific mode
        """
        # Get mode-specific weights
        if mode == "fast":
            dense_weight = settings.HYBRID_FAST_DENSE_WEIGHT
            sparse_weight = 1.0 - dense_weight
            adjusted_top_k = min(top_k, 8)  # Fewer results for speed
        elif mode == "comprehensive":
            dense_weight = settings.HYBRID_COMPREHENSIVE_DENSE_WEIGHT
            sparse_weight = 1.0 - dense_weight
            adjusted_top_k = max(top_k, 12)  # More results for comprehensiveness
        else:  # accurate
            dense_weight = settings.HYBRID_ACCURATE_DENSE_WEIGHT
            sparse_weight = 1.0 - dense_weight
            adjusted_top_k = top_k

        # Adjust score threshold based on mode
        if mode == "fast":
            score_threshold = 0.02  # Higher threshold for speed
        elif mode == "comprehensive":
            score_threshold = 0.005  # Lower threshold for more results
        else:  # accurate
            score_threshold = 0.01  # Balanced threshold

        logger.info(f"🎯 Hybrid search in {mode} mode: dense={dense_weight:.2f}, sparse={sparse_weight:.2f}")

        return await self.hybrid_search(
            query=query,
            top_k=adjusted_top_k,
            dense_weight=dense_weight,
            sparse_weight=sparse_weight,
            score_threshold=score_threshold,
            doc_filters=doc_filters
        )

    async def get_service_status(self) -> Dict[str, Any]:
        """Get hybrid query service status"""
        try:
            status = {
                "service": "HybridQueryService",
                "initialized": self._initialized,
                "hybrid_enabled": settings.ENABLE_HYBRID_SEARCH,
                "text_processor": self._text_processor is not None,
                "embed_model": self._embed_model is not None,
                "qdrant_service": self._qdrant_service is not None,
                "timestamp": datetime.now().isoformat()
            }

            if self._text_processor:
                status["vocabulary_info"] = self._text_processor.get_vocabulary_info()

            if self._qdrant_service:
                status["hybrid_collection"] = self._qdrant_service.hybrid_collection_name

            return status

        except Exception as e:
            return {
                "service": "HybridQueryService",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_mode_weights(self, mode: str) -> Tuple[float, float]:
        """Get dense and sparse weights for a given mode"""
        if mode == "fast":
            dense_weight = settings.HYBRID_FAST_DENSE_WEIGHT
        elif mode == "comprehensive":
            dense_weight = settings.HYBRID_COMPREHENSIVE_DENSE_WEIGHT
        else:  # accurate
            dense_weight = settings.HYBRID_ACCURATE_DENSE_WEIGHT

        sparse_weight = 1.0 - dense_weight
        return dense_weight, sparse_weight


# Global service instance
_hybrid_query_service = None

async def get_hybrid_query_service() -> HybridQueryService:
    """Get global HybridQueryService instance"""
    global _hybrid_query_service
    if _hybrid_query_service is None:
        _hybrid_query_service = HybridQueryService()
    return _hybrid_query_service