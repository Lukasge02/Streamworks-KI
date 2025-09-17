"""
Unified RAG Service
Professional conversational AI service integrating LlamaIndex with enhanced capabilities
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from . import RAGMode, RAGResponse, DocumentSource
from ..qdrant_rag_service import get_rag_service
from .context_manager import get_context_manager
from .query_processor import get_query_processor
from .adaptive_retrieval import get_adaptive_retriever

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
        Process a query using the unified RAG system

        Args:
            query: User query
            mode: RAG processing mode
            filters: Document filters (doc_type, date_range, etc.)
            conversation_context: Previous conversation for context awareness
            max_sources: Maximum number of source documents to return

        Returns:
            RAGResponse with answer and metadata
        """
        start_time = time.time()

        if not await self.initialize():
            raise Exception("Failed to initialize RAG service")

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
                sources=[source.__dict__ for source in processed_sources],
                metadata=metadata,
                processing_time_ms=processing_time,
                mode_used=mode
            )

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
        return {
            **self._performance_metrics,
            "cache_size": len(self._query_cache),
            "initialized": self._initialized,
            "timestamp": datetime.now().isoformat()
        }


# Global service instance
_unified_rag_service = None

async def get_unified_rag_service() -> UnifiedRAGService:
    """Get global unified RAG service instance"""
    global _unified_rag_service
    if _unified_rag_service is None:
        _unified_rag_service = UnifiedRAGService()
    return _unified_rag_service
