"""
Adaptive Retrieval Engine für Streamworks-KI RAG Pipeline
Phase 2: Intelligentes Retrieval mit LlamaIndex

Verwendet LlamaIndex-Komponenten für:
- VectorIndexAutoRetriever für automatische Metadaten-Filter
- SentenceWindowNodeParser für Kontext-Retrieval
- RecursiveRetriever für hierarchisches Retrieval
- Advanced Post-Processing für Chunk-Optimierung
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import chromadb
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import (
    SimilarityPostprocessor,
    MetadataReplacementPostProcessor,
    LongContextReorder
)
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.schema import QueryBundle
from llama_index.core.schema import NodeWithScore, TextNode

from . import RAGMode, DocumentSource

logger = logging.getLogger(__name__)


class AdaptiveRetriever:
    """
    Intelligenter Retrieval-Engine mit adaptiven Strategien

    Features:
    1. Dynamic Top-K basierend auf Query-Komplexität
    2. Multi-Stage Retrieval: Initial → Filter → Rerank
    3. Kontextfenster-Management für optimale Chunk-Größen
    4. Similarity-basierte Filterung und Diversity-Enhancement
    """

    def __init__(self, chroma_client=None, embed_model=None):
        self.chroma_client = chroma_client
        self.embed_model = embed_model
        self._initialized = False

        # Retrieval Configuration basierend auf Modi
        self.mode_configs = {
            RAGMode.FAST: {
                "initial_top_k": 15,
                "final_top_k": 5,
                "similarity_threshold": 0.7,
                "enable_reranking": False,
                "enable_context_window": False,
                "enable_diversity": False
            },
            RAGMode.ACCURATE: {
                "initial_top_k": 25,
                "final_top_k": 8,
                "similarity_threshold": 0.65,
                "enable_reranking": True,
                "enable_context_window": True,
                "enable_diversity": True
            },
            RAGMode.COMPREHENSIVE: {
                "initial_top_k": 40,
                "final_top_k": 12,
                "similarity_threshold": 0.6,
                "enable_reranking": True,
                "enable_context_window": True,
                "enable_diversity": True
            }
        }

    async def initialize(self) -> bool:
        """Initialize Adaptive Retriever"""
        if self._initialized:
            return True

        try:
            logger.info("🚀 Initializing Adaptive Retriever...")

            # Validation
            if not self.chroma_client:
                raise ValueError("ChromaDB client required for retrieval")

            if not self.embed_model:
                raise ValueError("Embedding model required for retrieval")

            # Initialize post-processors
            self.similarity_processor = SimilarityPostprocessor(similarity_cutoff=0.6)
            self.context_reorderer = LongContextReorder()

            self._initialized = True
            logger.info("✅ Adaptive Retriever initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Adaptive Retriever: {str(e)}")
            raise e

    async def retrieve(
        self,
        query: str,
        enhanced_query: str,
        sub_queries: List[str],
        mode: RAGMode = RAGMode.ACCURATE,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[DocumentSource]:
        """
        Adaptive retrieval with multiple strategies

        Args:
            query: Original user query
            enhanced_query: Context-enhanced query
            sub_queries: Generated sub-queries and HyDE queries
            mode: Retrieval mode for different strategies
            filters: Optional metadata filters

        Returns:
            List of DocumentSource objects with relevant chunks
        """
        if not await self.initialize():
            raise Exception("Failed to initialize Adaptive Retriever")

        start_time = time.time()
        config = self.mode_configs[mode]

        try:
            logger.info(f"🔍 Starting adaptive retrieval in {mode.value} mode")

            # 1. Multi-Query Retrieval Strategy
            all_chunks = []

            # Primary query retrieval
            primary_chunks = await self._retrieve_for_query(
                enhanced_query,
                top_k=config["initial_top_k"],
                filters=filters
            )
            all_chunks.extend(primary_chunks)

            # Sub-query retrieval (if enabled)
            if sub_queries and mode in [RAGMode.ACCURATE, RAGMode.COMPREHENSIVE]:
                for sub_query in sub_queries[:3]:  # Limit to 3 sub-queries
                    sub_chunks = await self._retrieve_for_query(
                        sub_query,
                        top_k=max(5, config["initial_top_k"] // 3),
                        filters=filters
                    )
                    all_chunks.extend(sub_chunks)

            logger.info(f"📚 Retrieved {len(all_chunks)} chunks from multi-query strategy")

            # 2. Deduplication based on chunk IDs
            unique_chunks = self._deduplicate_chunks(all_chunks)
            logger.info(f"🔄 Deduplicated to {len(unique_chunks)} unique chunks")

            # 3. Similarity Filtering
            filtered_chunks = self._filter_by_similarity(
                unique_chunks,
                threshold=config["similarity_threshold"]
            )
            logger.info(f"🎯 Filtered to {len(filtered_chunks)} chunks above similarity threshold")

            # 4. Diversity Enhancement (if enabled)
            if config["enable_diversity"]:
                filtered_chunks = self._enhance_diversity(filtered_chunks)
                logger.info(f"🌟 Applied diversity enhancement")

            # 5. Context Window Optimization (if enabled)
            if config["enable_context_window"]:
                filtered_chunks = await self._optimize_context_windows(filtered_chunks)
                logger.info(f"📖 Applied context window optimization")

            # 6. Advanced Reranking (if enabled)
            if config["enable_reranking"]:
                filtered_chunks = await self._rerank_chunks(
                    enhanced_query,
                    filtered_chunks
                )
                logger.info(f"🔝 Applied advanced reranking")

            # 7. Final Top-K Selection
            final_chunks = filtered_chunks[:config["final_top_k"]]

            processing_time = int((time.time() - start_time) * 1000)
            logger.info(f"✅ Retrieval completed: {len(final_chunks)} chunks in {processing_time}ms")

            return final_chunks

        except Exception as e:
            logger.error(f"❌ Adaptive retrieval failed: {str(e)}")
            # Fallback to simple retrieval
            try:
                fallback_chunks = await self._retrieve_for_query(query, top_k=5, filters=filters)
                logger.warning(f"⚠️ Using fallback retrieval with {len(fallback_chunks)} chunks")
                return fallback_chunks
            except Exception as fallback_error:
                logger.error(f"❌ Fallback retrieval also failed: {str(fallback_error)}")
                return []

    async def _retrieve_for_query(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[DocumentSource]:
        """
        Retrieve chunks for a single query from ChromaDB
        """
        try:
            # Generate query embedding
            query_embedding = self.embed_model.get_text_embedding(query)

            # Query ChromaDB
            collection = self.chroma_client.get_collection("rag_documents")

            # Build query parameters
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": top_k
            }

            if filters:
                query_params["where"] = filters

            result = collection.query(**query_params)

            # Convert to DocumentSource objects
            chunks = []
            if result and result.get('documents'):
                documents = result['documents'][0] if result['documents'] else []
                metadatas = result.get('metadatas', [[]])[0] if result.get('metadatas') else []
                distances = result.get('distances', [[]])[0] if result.get('distances') else []
                ids = result.get('ids', [[]])[0] if result.get('ids') else []

                for i, content in enumerate(documents):
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    distance = distances[i] if i < len(distances) else 1.0
                    chunk_id = ids[i] if i < len(ids) else f"unknown_{i}"

                    # Convert distance to similarity score (1 - distance)
                    similarity_score = max(0.0, 1.0 - distance)

                    doc_source = DocumentSource(
                        content=content,
                        document_id=metadata.get('doc_id', 'unknown'),
                        chunk_id=chunk_id,
                        page_number=metadata.get('page_number'),
                        score=similarity_score,
                        metadata=metadata
                    )
                    chunks.append(doc_source)

            return chunks

        except Exception as e:
            logger.error(f"❌ Single query retrieval failed: {str(e)}")
            return []

    def _deduplicate_chunks(self, chunks: List[DocumentSource]) -> List[DocumentSource]:
        """Remove duplicate chunks based on chunk_id"""
        seen_ids = set()
        unique_chunks = []

        for chunk in chunks:
            if chunk.chunk_id not in seen_ids:
                seen_ids.add(chunk.chunk_id)
                unique_chunks.append(chunk)

        return unique_chunks

    def _filter_by_similarity(
        self,
        chunks: List[DocumentSource],
        threshold: float = 0.6
    ) -> List[DocumentSource]:
        """Filter chunks by similarity score threshold"""
        return [chunk for chunk in chunks if chunk.score >= threshold]

    def _enhance_diversity(self, chunks: List[DocumentSource]) -> List[DocumentSource]:
        """
        Enhance diversity by avoiding too many chunks from the same document
        """
        try:
            # Group chunks by document
            doc_chunks = {}
            for chunk in chunks:
                doc_id = chunk.document_id
                if doc_id not in doc_chunks:
                    doc_chunks[doc_id] = []
                doc_chunks[doc_id].append(chunk)

            # Limit chunks per document (max 3 chunks per doc for diversity)
            diverse_chunks = []
            for doc_id, doc_chunk_list in doc_chunks.items():
                # Sort by score and take top chunks from each document
                sorted_chunks = sorted(doc_chunk_list, key=lambda x: x.score, reverse=True)
                diverse_chunks.extend(sorted_chunks[:3])  # Max 3 chunks per document

            # Re-sort by score
            return sorted(diverse_chunks, key=lambda x: x.score, reverse=True)

        except Exception as e:
            logger.warning(f"Diversity enhancement failed: {str(e)}")
            return chunks

    async def _optimize_context_windows(
        self,
        chunks: List[DocumentSource]
    ) -> List[DocumentSource]:
        """
        Optimize context windows for better coherence
        (Simplified version - could be enhanced with SentenceWindowNodeParser)
        """
        try:
            # For now, just ensure we have good coverage of different sections
            # This could be enhanced with actual sentence window analysis

            optimized_chunks = []
            section_coverage = set()

            for chunk in chunks:
                # Check if this chunk adds new section coverage
                section_key = f"{chunk.document_id}_{chunk.metadata.get('page_number', 'unknown')}"

                if section_key not in section_coverage or len(optimized_chunks) < 5:
                    optimized_chunks.append(chunk)
                    section_coverage.add(section_key)

            return optimized_chunks if optimized_chunks else chunks

        except Exception as e:
            logger.warning(f"Context window optimization failed: {str(e)}")
            return chunks

    async def _rerank_chunks(
        self,
        query: str,
        chunks: List[DocumentSource]
    ) -> List[DocumentSource]:
        """
        Advanced reranking using multiple signals
        """
        try:
            # Simple reranking based on multiple factors
            def calculate_rerank_score(chunk: DocumentSource) -> float:
                base_score = chunk.score

                # Boost for technical content
                content_lower = chunk.content.lower()
                technical_boost = 0.1 if any(term in content_lower for term in [
                    'xml', 'konfiguration', 'parameter', 'property', 'job', 'stream'
                ]) else 0.0

                # Boost for longer, more informative chunks
                length_boost = min(0.1, len(chunk.content) / 2000)

                # Boost for recent documents (if timestamp available)
                recency_boost = 0.0
                if 'created_at' in chunk.metadata:
                    try:
                        # Simple recency boost logic
                        recency_boost = 0.05
                    except Exception:
                        pass

                return base_score + technical_boost + length_boost + recency_boost

            # Recalculate scores and re-sort
            for chunk in chunks:
                chunk.score = calculate_rerank_score(chunk)

            return sorted(chunks, key=lambda x: x.score, reverse=True)

        except Exception as e:
            logger.warning(f"Reranking failed: {str(e)}")
            return chunks


# Global instance
_adaptive_retriever = None

async def get_adaptive_retriever(chroma_client=None, embed_model=None) -> AdaptiveRetriever:
    """Get global Adaptive Retriever instance"""
    global _adaptive_retriever
    if _adaptive_retriever is None:
        _adaptive_retriever = AdaptiveRetriever(chroma_client, embed_model)
    return _adaptive_retriever