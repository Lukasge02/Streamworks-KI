"""
Unified RAG Service
Professional conversational AI service integrating LlamaIndex with enhanced capabilities
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from uuid import UUID

from . import RAGMode, RAGResponse, DocumentSource
from ..qdrant_rag_service import get_rag_service
from .context_manager import get_context_manager
from .query_processor import get_query_processor
from .adaptive_retrieval import get_adaptive_retriever
from ..performance_monitor import performance_monitor, PerformanceTracker
from ..ai_response_cache import get_cached_ai_response, cache_ai_response
from ..advanced_cache_system import get_advanced_cache
from ..document.crud_operations import DocumentCrudOperations
from ..rag_metrics_service import get_rag_metrics_service

logger = logging.getLogger(__name__)

class UnifiedRAGService:
    """
    Unified RAG Service providing professional conversational AI capabilities

    Features:
    - Multiple RAG modes (Fast, Accurate, Comprehensive)
    - Intelligent context management
    - Advanced source filtering and ranking
    - Response quality optimization
    - Fallback mechanisms
    """

    def __init__(self):
        self._initialized = False
        self._llamaindex_service = None
        self._context_manager = None
        # Phase 2 components
        self._query_processor = None
        self._adaptive_retriever = None
        self._query_cache = {}
        self._advanced_cache = None  # Advanced multi-level cache
        self._performance_metrics = {
            "total_queries": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0,
            "phase2_queries": 0  # Track Phase 2 enhanced queries
        }

    async def initialize(self) -> bool:
        """Initialize the unified RAG service"""
        if self._initialized:
            return True

        try:
            logger.info("🚀 Initializing Unified RAG Service with Phase 2 enhancements...")

            # Initialize LlamaIndex RAG service
            self._llamaindex_service = await get_rag_service()
            await self._llamaindex_service.initialize()
            logger.info("✅ LlamaIndex service initialized")

            # Initialize Context Manager
            self._context_manager = await get_context_manager()
            logger.info("✅ Context Manager initialized")

            # Initialize Advanced Cache System
            self._advanced_cache = await get_advanced_cache()
            logger.info("✅ Advanced Multi-Level Cache System initialized")

            # Initialize Phase 2 components
            try:
                # Query Processor (Phase 2)
                self._query_processor = await get_query_processor(
                    llm_service=self._llamaindex_service.llm,
                    embed_model=self._llamaindex_service.embed_model
                )
                await self._query_processor.initialize()
                logger.info("✅ Phase 2 Query Processor initialized")

                # Adaptive Retriever (Phase 2)
                self._adaptive_retriever = await get_adaptive_retriever(
                    qdrant_service=self._llamaindex_service.qdrant_service,
                    embed_model=self._llamaindex_service.embed_model
                )
                await self._adaptive_retriever.initialize()
                logger.info("✅ Phase 2 Adaptive Retriever initialized")

            except Exception as phase2_error:
                logger.warning(f"⚠️ Phase 2 components failed to initialize: {str(phase2_error)}")
                logger.warning("🔄 Falling back to Phase 1 (basic RAG) functionality")
                # Continue without Phase 2 components
                self._query_processor = None
                self._adaptive_retriever = None

            logger.info("✅ Unified RAG Service initialized successfully")
            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Unified RAG Service: {str(e)}")
            return False

    async def query(
        self,
        query: str,
        mode: RAGMode = RAGMode.ACCURATE,
        filters: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[List[Dict[str, Any]]] = None,
        max_sources: int = 5,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> RAGResponse:
        """
        Process a query using the unified RAG system - PERFORMANCE OPTIMIZED

        Args:
            query: User query
            mode: RAG processing mode
            filters: Document filters (doc_type, date_range, etc.)
            conversation_context: Previous conversation for context awareness
            max_sources: Maximum number of source documents to return

        Returns:
            RAGResponse with answer and metadata
        """
        async with PerformanceTracker("unified_rag", "query_processing", {"mode": mode.value, "query_length": len(query)}) as tracker:
            start_time = time.time()

            if not await self.initialize():
                raise Exception("Failed to initialize RAG service")

            # Advanced multi-level cache lookup
            cache_key = f"{query}_{mode.value}_{str(filters)}_{str(conversation_context)}"

            # Generate query embedding for semantic cache
            query_embedding = None
            if self._llamaindex_service and self._llamaindex_service.embed_model:
                try:
                    query_embedding = self._llamaindex_service.embed_model.get_text_embedding(query)
                except Exception as e:
                    logger.warning(f"Failed to generate query embedding for cache: {str(e)}")

            # Try advanced cache first
            cached_response = None
            if self._advanced_cache:
                cached_response = await self._advanced_cache.get(
                    key=cache_key,
                    semantic_vector=query_embedding,
                    use_semantic=True
                )

            # Fallback to simple cache
            if not cached_response:
                cached_response = get_cached_ai_response(cache_key, method="rag_unified")

            if cached_response:
                logger.info(f"🎯 Cache HIT for RAG query: {query[:50]}...")
                await performance_monitor.record_metric(
                    component="cache",
                    operation="rag_query_hit",
                    duration_ms=1,
                    cache_hit=True
                )
                self._performance_metrics["cache_hits"] += 1
                return cached_response

            try:
                logger.info(f"🔍 Processing query in {mode.value} mode: {query[:100]}...")

                # Check if Phase 2 components are available
                use_phase2 = (self._query_processor is not None and
                             self._adaptive_retriever is not None)

                if use_phase2:
                    logger.info("🚀 Using Phase 2 enhanced RAG pipeline")
                    self._performance_metrics["phase2_queries"] += 1

                    # Phase 2: Advanced Query Processing
                    from . import QueryContext
                    query_context = QueryContext(
                        original_query=query,
                        conversation_context=conversation_context or [],
                        session_id=session_id,
                        user_id=user_id,
                        filters=filters,
                        mode=mode
                    )

                    enhanced_query, sub_queries, query_metadata = await self._query_processor.process_query(
                        query_context=query_context,
                        mode=mode
                    )
                    logger.info(f"📝 Phase 2 query enhancement: {len(sub_queries)} sub-queries generated")

                    # Phase 2: Adaptive Retrieval
                    processed_sources = await self._adaptive_retriever.retrieve(
                        query=query,
                        enhanced_query=enhanced_query,
                        sub_queries=sub_queries,
                        mode=mode,
                        filters=filters
                    )
                    logger.info(f"🔍 Phase 2 adaptive retrieval: {len(processed_sources)} sources")

                    # Generate answer from retrieved sources
                    if processed_sources:
                        context_texts = [source.content for source in processed_sources]
                        context_str = "\n\n".join(context_texts[:8])  # Limit context

                        from llama_index.core.prompts import PromptTemplate
                        qa_template = PromptTemplate(
                            """Basierend auf dem folgenden Kontext, beantworte die Frage:

KONTEXT:
{context_str}

FRAGE: {query_str}

ANTWORT:"""
                        )

                        response_prompt = qa_template.format(
                            context_str=context_str,
                            query_str=query
                        )

                        response = await self._llamaindex_service.llm.acomplete(response_prompt)
                        answer = str(response).strip()
                    else:
                        answer = "Entschuldigung, ich konnte keine relevanten Informationen finden."

                else:
                    # Phase 1: Fallback to basic RAG pipeline
                    logger.info("🔄 Using Phase 1 basic RAG pipeline")

                    # 1. Query preprocessing and enhancement
                    enhanced_query = await self._enhance_query(query, conversation_context, mode)

                    # 2. Determine retrieval parameters based on mode
                    retrieval_params = self._get_retrieval_parameters(mode, max_sources)

                    # 3. Execute RAG pipeline
                    answer, sources = await self._llamaindex_service.query_documents(
                        query=enhanced_query,
                        doc_filters=filters,
                        top_k=retrieval_params["top_k"]
                    )

                    # 4. Process and rank sources
                    processed_sources = await self._process_sources(sources, query, max_sources)

                # 5. Enhance response quality
                enhanced_answer = await self._enhance_response(answer, processed_sources, mode)

                # 6. Calculate confidence score
                confidence_score = await self._calculate_confidence(
                    enhanced_answer, processed_sources, query
                )

                processing_time = int((time.time() - start_time) * 1000)

                # 7. Update metrics
                self._update_metrics(processing_time)

                # 8. Context management and follow-up suggestions
                follow_up_suggestions = []
                if session_id and user_id and self._context_manager:
                    # Add user query to context
                    await self._context_manager.add_conversation_turn(
                        session_id=session_id,
                        user_id=user_id,
                        role="user",
                        content=query
                    )

                    # Add assistant response to context
                    await self._context_manager.add_conversation_turn(
                        session_id=session_id,
                        user_id=user_id,
                        role="assistant",
                        content=enhanced_answer,
                        confidence_score=confidence_score,
                        sources_used=[source.document_id for source in processed_sources]
                    )

                    # Generate follow-up suggestions
                    try:
                        follow_up_suggestions = await self._context_manager.suggest_follow_up_questions(
                            session_id=session_id,
                            user_id=user_id,
                            last_response=enhanced_answer
                        )
                    except Exception as e:
                        logger.warning(f"Failed to generate follow-up suggestions: {str(e)}")

                # 9. Create response with enhanced metadata
                metadata = {
                    "mode_used": mode.value,
                    "query_length": len(query),
                    "enhanced_query": enhanced_query if not use_phase2 else enhanced_query,
                    "sources_returned": len(processed_sources),
                    "model_used": "llama-index + ollama",
                    "follow_up_suggestions": follow_up_suggestions,
                    "timestamp": datetime.now().isoformat(),
                    "pipeline": "phase2" if use_phase2 else "phase1"
                }

                if use_phase2:
                    # Add Phase 2 specific metadata
                    metadata.update({
                        "query_processing": query_metadata,
                        "sub_queries_generated": len(sub_queries),
                        "retrieval_strategy": "adaptive_multi_query",
                        "enhancement_features": [
                            "query_expansion",
                            "sub_query_generation",
                            "adaptive_retrieval",
                            "similarity_reranking",
                            "diversity_enhancement"
                        ]
                    })
                else:
                    # Add Phase 1 specific metadata
                    metadata.update({
                        "total_sources_found": len(sources),
                        "retrieval_strategy": "basic_vector_search"
                    })

                rag_response = RAGResponse(
                    answer=enhanced_answer,
                    confidence_score=confidence_score,
                    sources=await self._format_sources_for_frontend(processed_sources),
                    metadata=metadata,
                    processing_time_ms=processing_time,
                    mode_used=mode
                )

                # Cache the response for future queries (performance optimization)
                if confidence_score > 0.7:  # Only cache high-confidence responses
                    # Use advanced cache system
                    if self._advanced_cache and query_embedding:
                        await self._advanced_cache.set(
                            key=cache_key,
                            value=rag_response,
                            ttl=7200,  # 2 hours for high-confidence responses
                            semantic_vector=query_embedding,
                            confidence_score=confidence_score,
                            tags=['rag_response', mode.value, 'high_confidence']
                        )
                        logger.debug(f"💾 Cached RAG response in advanced cache (score: {confidence_score:.2f})")
                    else:
                        # Fallback to simple cache
                        cache_ai_response(cache_key, rag_response, method="rag_unified")
                        logger.debug(f"💾 Cached RAG response in simple cache (score: {confidence_score:.2f})")

                # Record final performance metrics
                await performance_monitor.record_metric(
                    component="unified_rag",
                    operation="query_complete",
                    duration_ms=processing_time,
                    metadata={
                        "confidence_score": confidence_score,
                        "sources_count": len(processed_sources),
                        "pipeline": "phase2" if use_phase2 else "phase1"
                    }
                )

                # Track RAG query metrics for enhanced analytics
                try:
                    rag_metrics_service = await get_rag_metrics_service()

                    # Convert processed sources to SourceReference format
                    from ..rag_metrics_service import SourceReference
                    source_references = []
                    for source in processed_sources:
                        source_ref = SourceReference(
                            document_id=source.document_id,
                            filename=(
                                source.metadata.get("original_filename")
                                or source.metadata.get("file_name")
                                or source.metadata.get("filename")
                                or "Unknown Document"
                            ),
                            page_number=source.page_number,
                            section=source.metadata.get("section"),
                            relevance_score=source.metadata.get("relevance_score", source.score),
                            snippet=(
                                source.content[:200] + "..."
                                if len(source.content) > 200
                                else source.content
                            ),
                            chunk_index=source.metadata.get("chunk_index", 0),
                            confidence=confidence_score,
                            doc_type=(
                                source.metadata.get("mime_type")
                                or source.metadata.get("doctype")
                                or "unknown"
                            ),
                            chunk_id=source.chunk_id
                        )
                        source_references.append(source_ref)

                    # Track the query
                    await rag_metrics_service.track_rag_query(
                        query=query,
                        sources=source_references,
                        response_time_ms=processing_time,
                        cache_hit=cached_response is not None,
                        mode=mode.value,
                        session_id=session_id
                    )
                    logger.debug(f"✅ RAG query metrics tracked successfully")

                except Exception as e:
                    logger.warning(f"⚠️ Failed to track RAG metrics: {str(e)}")
                    # Don't fail the query if metrics tracking fails

                logger.info(f"✅ Query processed successfully in {processing_time}ms (confidence: {confidence_score:.2f})")
                return rag_response

            except Exception as e:
                logger.error(f"❌ Query processing failed: {str(e)}")

                # Fallback response
                processing_time = int((time.time() - start_time) * 1000)
                return RAGResponse(
                    answer="Entschuldigung, ich konnte Ihre Anfrage nicht vollständig verarbeiten. Bitte versuchen Sie es erneut oder formulieren Sie Ihre Frage anders.",
                    confidence_score=0.0,
                    sources=[],
                    metadata={
                        "error": str(e),
                        "mode_used": mode.value,
                        "timestamp": datetime.now().isoformat()
                    },
                    processing_time_ms=processing_time,
                    mode_used=mode
                )

    async def _enhance_query(
        self,
        query: str,
        context: Optional[List[Dict[str, Any]]],
        mode: RAGMode
    ) -> str:
        """Enhance query with conversation context and mode-specific optimizations"""

        enhanced_query = query.strip()

        # Add conversation context for better understanding
        if context and len(context) > 0:
            # Get last few messages for context
            recent_context = context[-3:] if len(context) > 3 else context
            context_text = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in recent_context if msg.get('content')
            ])

            if context_text:
                enhanced_query = f"Vorheriger Kontext:\n{context_text}\n\nAktuelle Frage: {query}"

        # Mode-specific enhancements
        if mode == RAGMode.COMPREHENSIVE:
            enhanced_query += "\n\nBitte geben Sie eine detaillierte und umfassende Antwort mit allen relevanten Informationen."
        elif mode == RAGMode.FAST:
            enhanced_query += "\n\nBitte geben Sie eine kurze und präzise Antwort."

        return enhanced_query

    def _get_retrieval_parameters(self, mode: RAGMode, max_sources: int) -> Dict[str, Any]:
        """Get retrieval parameters based on RAG mode"""

        base_params = {
            RAGMode.FAST: {"top_k": min(3, max_sources)},
            RAGMode.ACCURATE: {"top_k": min(5, max_sources)},
            RAGMode.COMPREHENSIVE: {"top_k": min(8, max_sources)}
        }

        return base_params.get(mode, base_params[RAGMode.ACCURATE])

    async def _process_sources(
        self,
        raw_sources: List[Dict[str, Any]],
        query: str,
        max_sources: int
    ) -> List[DocumentSource]:
        """Process and rank sources for optimal relevance"""

        processed_sources = []

        for source in raw_sources:
            # Create DocumentSource object
            doc_source = DocumentSource(
                content=source.get("content", ""),
                document_id=source.get("metadata", {}).get("doc_id", "unknown"),
                chunk_id=source.get("metadata", {}).get("chunk_id", "unknown"),
                page_number=source.get("metadata", {}).get("page_number"),
                score=source.get("score", 0.0),
                metadata=source.get("metadata", {})
            )

            # Enrich with database metadata for complete document information
            doc_source = await self._enrich_source_metadata(doc_source)

            # Add relevance scoring
            doc_source.metadata["relevance_score"] = await self._calculate_relevance(
                doc_source.content, query
            )

            processed_sources.append(doc_source)

        # Sort by combined score (retrieval score + relevance)
        processed_sources.sort(
            key=lambda x: x.score * 0.7 + x.metadata.get("relevance_score", 0.0) * 0.3,
            reverse=True
        )

        return processed_sources[:max_sources]

    async def _enrich_source_metadata(self, doc_source: DocumentSource) -> DocumentSource:
        """Enrich DocumentSource with metadata from database"""
        try:
            # Get database session
            from database import AsyncSessionLocal

            async with AsyncSessionLocal() as db:
                crud = DocumentCrudOperations()

                document_uuid = self._normalize_document_id(doc_source.document_id)

                if not document_uuid:
                    logger.debug(
                        "Skipping metadata enrichment for document %s: invalid identifier",
                        doc_source.document_id,
                    )
                    return self._apply_source_fallback_metadata(doc_source)

                # Try to get document by ID
                document = await crud.get_document_by_id(db, document_uuid)

                if document:
                    # Add database metadata to source metadata
                    doc_source.document_id = str(document_uuid)
                    doc_source.metadata["doc_id"] = str(document_uuid)
                    doc_source.metadata.update({
                        "original_filename": document.original_filename,
                        "filename": document.filename,
                        "file_size": document.file_size,
                        "mime_type": document.mime_type,
                        "created_at": document.created_at.isoformat() if document.created_at else None,
                        "updated_at": document.updated_at.isoformat() if document.updated_at else None,
                        "status": document.status.value if hasattr(document.status, 'value') else str(document.status)
                    })
                    logger.debug(f"✅ Enriched source metadata for document {doc_source.document_id}")
                else:
                    logger.warning(f"⚠️ Document {doc_source.document_id} not found in database")
                    self._apply_source_fallback_metadata(doc_source)

        except Exception as e:
            logger.error(f"❌ Failed to enrich source metadata for {doc_source.document_id}: {str(e)}")
            self._apply_source_fallback_metadata(doc_source)

        return doc_source

    @staticmethod
    def _apply_source_fallback_metadata(doc_source: DocumentSource) -> DocumentSource:
        """Ensure source carries minimally useful metadata for UI and metrics."""
        fallback_name = (
            doc_source.metadata.get("original_filename")
            or doc_source.metadata.get("file_name")
            or doc_source.metadata.get("filename")
            or "Unknown Document"
        )

        doc_source.metadata.setdefault("original_filename", fallback_name)
        doc_source.metadata.setdefault("filename", fallback_name)
        doc_source.metadata.setdefault("file_size", doc_source.metadata.get("file_size", 0))
        doc_source.metadata.setdefault(
            "mime_type",
            doc_source.metadata.get("mime_type") or doc_source.metadata.get("doctype", "application/octet-stream"),
        )

        return doc_source

    @staticmethod
    def _normalize_document_id(document_id: Any) -> Optional[UUID]:
        """Convert document identifier to UUID if possible."""
        if isinstance(document_id, UUID):
            return document_id

        if isinstance(document_id, str):
            value = document_id.strip()
            if not value or value.lower() == "unknown":
                return None

            try:
                return UUID(value)
            except ValueError:
                return None

        return None

    async def _format_sources_for_frontend(self, sources: List[DocumentSource]) -> List[Dict[str, Any]]:
        """Format sources for frontend consumption with proper structure"""
        formatted_sources = []

        for source in sources:
            # Create frontend-compatible source format
            formatted_source = {
                "id": source.chunk_id,
                "content": source.content,
                "metadata": {
                    "doc_id": source.document_id,
                    "original_filename": source.metadata.get("original_filename", "Unknown Document"),
                    "filename": source.metadata.get("filename", "unknown"),
                    "page_number": source.page_number,
                    "heading": source.metadata.get("heading"),
                    "section": source.metadata.get("section"),
                    "file_size": source.metadata.get("file_size", 0),
                    "mime_type": source.metadata.get("mime_type", "application/octet-stream"),
                    "created_at": source.metadata.get("created_at"),
                    "updated_at": source.metadata.get("updated_at"),
                    "status": source.metadata.get("status"),
                    "chunk_id": source.chunk_id,
                    "chunk_index": source.metadata.get("chunk_index"),
                },
                "relevance_score": source.metadata.get("relevance_score", source.score),
                "score": source.score,
                # Additional fields for enhanced UI
                "distance": 1.0 - source.score if source.score <= 1.0 else 0.0
            }

            formatted_sources.append(formatted_source)

        return formatted_sources

    async def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate content relevance to query using simple metrics"""

        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        # Jaccard similarity
        intersection = len(query_words & content_words)
        union = len(query_words | content_words)

        return intersection / union if union > 0 else 0.0

    async def _enhance_response(
        self,
        answer: str,
        sources: List[DocumentSource],
        mode: RAGMode
    ) -> str:
        """Enhance response based on mode and available sources"""

        if not answer or not answer.strip():
            return "Entschuldigung, ich konnte keine relevanten Informationen in den Dokumenten finden."

        enhanced_answer = answer.strip()

        # Mode-specific enhancements
        if mode == RAGMode.COMPREHENSIVE and sources:
            # Add source information for comprehensive mode
            source_info = f"\n\n**Quellen ({len(sources)} Dokumente):**"
            for i, source in enumerate(sources[:3], 1):
                doc_name = source.metadata.get("file_name", f"Dokument {i}")
                source_info += f"\n- {doc_name}"
                if source.page_number:
                    source_info += f" (Seite {source.page_number})"

            enhanced_answer += source_info

        return enhanced_answer

    async def _calculate_confidence(
        self,
        answer: str,
        sources: List[DocumentSource],
        query: str
    ) -> float:
        """Calculate confidence score for the response"""

        if not answer or not sources:
            return 0.0

        # Base confidence from source scores
        avg_source_score = sum(source.score for source in sources) / len(sources)

        # Response length factor (longer responses tend to be more informative)
        length_factor = min(len(answer) / 500, 1.0)  # Cap at 500 chars

        # Source count factor (more sources = higher confidence)
        source_factor = min(len(sources) / 3, 1.0)  # Cap at 3 sources

        # Combined confidence
        confidence = (avg_source_score * 0.5 + length_factor * 0.3 + source_factor * 0.2)

        return max(0.0, min(1.0, confidence))  # Ensure 0-1 range

    def _update_metrics(self, processing_time: int):
        """Update performance metrics"""
        self._performance_metrics["total_queries"] += 1

        # Update average response time
        current_avg = self._performance_metrics["avg_response_time"]
        total_queries = self._performance_metrics["total_queries"]

        new_avg = ((current_avg * (total_queries - 1)) + processing_time) / total_queries
        self._performance_metrics["avg_response_time"] = new_avg

    async def health_check(self) -> Dict[str, Any]:
        """Check service health and return status"""
        try:
            # Check LlamaIndex service health
            llama_health = await self._llamaindex_service.get_health_status()

            return {
                "service": "UnifiedRAGService",
                "status": "healthy" if llama_health.get("status") == "healthy" else "degraded",
                "initialized": self._initialized,
                "backend_service": llama_health,
                "performance_metrics": self._performance_metrics,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "service": "UnifiedRAGService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        # Get advanced cache statistics
        advanced_cache_stats = {}
        if self._advanced_cache:
            try:
                advanced_cache_stats = self._advanced_cache.get_statistics()
            except Exception as e:
                logger.warning(f"Failed to get advanced cache stats: {str(e)}")

        return {
            **self._performance_metrics,
            "cache_size": len(self._query_cache),
            "advanced_cache": advanced_cache_stats,
            "initialized": self._initialized,
            "timestamp": datetime.now().isoformat()
        }

    async def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance and return results"""
        if not self._advanced_cache:
            return {"error": "Advanced cache not initialized"}

        try:
            optimization_results = await self._advanced_cache.optimize()
            logger.info(f"✅ Cache optimization completed in {optimization_results['optimization_time_ms']:.2f}ms")
            return optimization_results
        except Exception as e:
            logger.error(f"❌ Cache optimization failed: {str(e)}")
            return {"error": str(e)}

    async def clear_cache(self, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Clear cache by tags or completely"""
        try:
            if self._advanced_cache:
                if tags:
                    removed_count = self._advanced_cache.invalidate_by_tags(tags)
                    logger.info(f"🗑️ Cleared {removed_count} cache entries with tags: {tags}")
                    return {"cleared_entries": removed_count, "tags": tags}
                else:
                    self._advanced_cache.clear_all()
                    logger.info("🧹 Cleared entire advanced cache")
                    return {"message": "All cache levels cleared"}
            else:
                return {"error": "Advanced cache not initialized"}
        except Exception as e:
            logger.error(f"❌ Cache clear failed: {str(e)}")
            return {"error": str(e)}


# Global service instance
_unified_rag_service = None

async def get_unified_rag_service() -> UnifiedRAGService:
    """Get global unified RAG service instance"""
    global _unified_rag_service
    if _unified_rag_service is None:
        _unified_rag_service = UnifiedRAGService()
    return _unified_rag_service
