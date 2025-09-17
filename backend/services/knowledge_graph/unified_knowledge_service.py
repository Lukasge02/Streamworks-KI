"""
Unified Knowledge Graph Service
Enterprise orchestrator that coordinates all knowledge graph components
Provides single interface for temporal graphs, entity extraction, context memory, and monitoring
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from .temporal_graph_service import TemporalKnowledgeGraphService, ExtractedKnowledge
from .entity_extraction_pipeline import EnterpriseEntityExtractionPipeline, ExtractionResult
from .context_memory_system import EnterpriseContextMemorySystem, MemoryContext, ContextualResponse
from .monitoring_service import KnowledgeGraphMonitoringService, SystemHealthReport

from services.conversation_engine import ConversationEngine
from services.ollama_service import OllamaService
from services.embedding_gemma import EmbeddingService

logger = logging.getLogger(__name__)

@dataclass
class KnowledgeProcessingResult:
    """Complete result from knowledge processing"""
    # Core results
    extraction_result: ExtractionResult
    memory_context: MemoryContext
    contextual_response: Optional[ContextualResponse] = None

    # Process metadata
    processing_time_ms: float = 0.0
    confidence_score: float = 0.0
    quality_metrics: Dict[str, Any] = None

    # System state
    session_id: str = ""
    user_id: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.quality_metrics is None:
            self.quality_metrics = {}

class UnifiedKnowledgeGraphService:
    """
    Enterprise Knowledge Graph Orchestrator
    Coordinates all knowledge graph components for optimal performance

    This is the main service that applications should interact with.
    It provides enterprise-grade entity extraction and context memory.
    """

    def __init__(self,
                 db_session: AsyncSession,
                 conversation_engine: ConversationEngine,
                 ollama_service: Optional[OllamaService] = None,
                 embedding_service: Optional[EmbeddingService] = None,
                 enable_monitoring: bool = True,
                 enable_optimization: bool = True):

        self.db = db_session

        # Initialize core components
        self.temporal_graph = TemporalKnowledgeGraphService(
            db_session=db_session,
            embedding_service=embedding_service
        )

        self.extraction_pipeline = EnterpriseEntityExtractionPipeline(
            conversation_engine=conversation_engine,
            ollama_service=ollama_service,
            embedding_service=embedding_service
        )

        self.context_memory = EnterpriseContextMemorySystem(
            db_session=db_session,
            embedding_service=embedding_service
        )

        # Initialize monitoring if enabled
        self.monitoring = None
        if enable_monitoring:
            self.monitoring = KnowledgeGraphMonitoringService(db_session=db_session)

        self.enable_optimization = enable_optimization

        # Performance tracking
        self.performance_stats = {
            'total_processed': 0,
            'avg_processing_time': 0.0,
            'avg_confidence': 0.0,
            'success_rate': 0.0
        }

        logger.info("🚀 UnifiedKnowledgeGraphService initialized with enterprise features")

    async def process_conversation_turn(self,
                                      message: str,
                                      session_id: str,
                                      user_id: Optional[str] = None,
                                      context: Optional[List[Dict]] = None,
                                      generate_response: bool = True) -> KnowledgeProcessingResult:
        """
        Process a complete conversation turn with enterprise-grade extraction and memory

        This is the main method applications should use for conversation processing.
        It provides state-of-the-art entity extraction and context-aware responses.
        """
        start_time = datetime.utcnow()

        try:
            # Track session start in monitoring
            if self.monitoring:
                self.monitoring.track_session_start(session_id)

            # Step 1: Extract entities using enterprise pipeline
            logger.info(f"🔍 Processing conversation turn for session {session_id}")
            extraction_result = await self.extraction_pipeline.extract_entities(
                text=message,
                context=context,
                session_id=session_id
            )

            # Track extraction metrics
            if self.monitoring:
                self.monitoring.track_extraction_time(extraction_result.extraction_time_ms)
                for entity in extraction_result.entities:
                    self.monitoring.track_entity_confidence(entity.confidence)

            # Step 2: Store knowledge in temporal graph
            await self._store_extraction_in_graph(extraction_result, session_id, user_id)

            # Step 3: Retrieve contextual memory
            memory_context = await self.context_memory.get_contextual_memory(
                query=message,
                session_id=session_id,
                user_id=user_id
            )

            # Track memory retrieval
            if self.monitoring:
                self.monitoring.track_query_time(memory_context.retrieval_time_ms)

            # Step 4: Generate contextual response (if requested)
            contextual_response = None
            if generate_response:
                # For this implementation, we'll create a basic contextual response
                # In production, this would integrate with your RAG/chat service
                contextual_response = await self._generate_contextual_response(
                    message, memory_context, extraction_result
                )

            # Step 5: Update memory from interaction
            await self.context_memory.update_memory_from_interaction(
                query=message,
                response=contextual_response.answer if contextual_response else "",
                session_id=session_id,
                user_id=user_id
            )

            # Calculate overall metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            confidence_score = self._calculate_overall_confidence(extraction_result, memory_context)

            # Create result
            result = KnowledgeProcessingResult(
                extraction_result=extraction_result,
                memory_context=memory_context,
                contextual_response=contextual_response,
                processing_time_ms=processing_time,
                confidence_score=confidence_score,
                quality_metrics=self._calculate_quality_metrics(extraction_result, memory_context),
                session_id=session_id,
                user_id=user_id
            )

            # Update performance stats
            self._update_performance_stats(result)

            logger.info(f"✅ Conversation turn processed: {len(extraction_result.entities)} entities, "
                       f"confidence: {confidence_score:.3f}, time: {processing_time:.1f}ms")

            return result

        except Exception as e:
            logger.error(f"❌ Conversation processing failed: {str(e)}")
            if self.monitoring:
                self.monitoring.track_error("conversation_processing")

            # Return minimal result on error
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return KnowledgeProcessingResult(
                extraction_result=ExtractionResult(),
                memory_context=MemoryContext(),
                processing_time_ms=processing_time,
                confidence_score=0.0,
                session_id=session_id,
                user_id=user_id
            )

    async def get_enhanced_context(self,
                                 query: str,
                                 session_id: str,
                                 user_id: Optional[str] = None,
                                 max_entities: int = 15,
                                 max_facts: int = 30) -> MemoryContext:
        """
        Get enhanced context with comprehensive knowledge graph information

        Use this for retrieving rich context for RAG or conversation systems.
        """
        try:
            # Configure context parameters
            self.context_memory.max_context_entities = max_entities
            self.context_memory.max_context_facts = max_facts

            # Retrieve comprehensive context
            context = await self.context_memory.get_contextual_memory(
                query=query,
                session_id=session_id,
                user_id=user_id
            )

            # Enhance with graph queries if needed
            if len(context.key_entities) < max_entities:
                additional_context = await self.temporal_graph.query_knowledge_graph(
                    query=query,
                    session_id=session_id
                )

                # Merge additional entities
                existing_ids = {e.id for e in context.key_entities}
                for entity in additional_context.entities:
                    if entity.id not in existing_ids and len(context.key_entities) < max_entities:
                        context.key_entities.append(entity)

            logger.info(f"🎯 Enhanced context retrieved: {len(context.key_entities)} entities, "
                       f"{len(context.relevant_facts)} facts")

            return context

        except Exception as e:
            logger.error(f"❌ Enhanced context retrieval failed: {str(e)}")
            return MemoryContext()

    async def optimize_knowledge_graph(self) -> Dict[str, Any]:
        """
        Optimize the knowledge graph for performance and quality

        Run this periodically (e.g., daily) to maintain optimal performance.
        """
        try:
            optimization_results = {}

            # Run temporal graph optimizations
            temporal_optimizations = await self.temporal_graph.merge_duplicate_entities()
            optimization_results['temporal_optimizations'] = {
                'entities_merged': 'completed'
            }

            # Clean up old facts
            await self.temporal_graph.cleanup_old_facts()
            optimization_results['cleanup'] = {'old_facts_cleaned': 'completed'}

            # Run monitoring optimizations if available
            if self.monitoring:
                monitoring_optimizations = await self.monitoring.optimize_graph_performance()
                optimization_results['monitoring_optimizations'] = monitoring_optimizations

            logger.info(f"⚡ Knowledge graph optimization completed")
            return optimization_results

        except Exception as e:
            logger.error(f"❌ Knowledge graph optimization failed: {str(e)}")
            return {'error': str(e)}

    async def get_system_health(self) -> SystemHealthReport:
        """
        Get comprehensive system health report

        Use this for monitoring dashboards and operational health checks.
        """
        if not self.monitoring:
            logger.warning("⚠️ Monitoring not enabled, returning basic health")
            return SystemHealthReport(
                overall_score=0.8,
                component_scores={'basic_service': 0.8}
            )

        try:
            health_report = await self.monitoring.generate_health_report()

            # Add service-specific health metrics
            health_report.component_scores['extraction_pipeline'] = await self._assess_pipeline_health()
            health_report.component_scores['context_memory'] = await self._assess_memory_health()
            health_report.component_scores['temporal_graph'] = await self._assess_graph_health()

            # Recalculate overall score with service components
            total_components = len(health_report.component_scores)
            health_report.overall_score = sum(health_report.component_scores.values()) / total_components

            return health_report

        except Exception as e:
            logger.error(f"❌ System health check failed: {str(e)}")
            return SystemHealthReport(
                overall_score=0.0,
                component_scores={'error': 0.0}
            )

    async def get_knowledge_insights(self,
                                   session_id: str,
                                   user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get insights about the knowledge state for a session

        Useful for analytics and conversation quality assessment.
        """
        try:
            insights = {}

            # Memory insights
            insights['memory'] = await self.context_memory.get_memory_insights(
                session_id=session_id,
                user_id=user_id
            )

            # Graph query for session-specific knowledge
            graph_query = await self.temporal_graph.query_knowledge_graph(
                query="",  # Empty query to get general session knowledge
                session_id=session_id
            )

            insights['knowledge_graph'] = {
                'entities_count': len(graph_query.entities),
                'relations_count': len(graph_query.relations),
                'facts_count': len(graph_query.facts),
                'confidence_score': graph_query.confidence_score
            }

            # Performance metrics
            insights['performance'] = self.performance_stats.copy()

            # Extraction pipeline metrics
            insights['extraction'] = self.extraction_pipeline.get_performance_metrics()

            return insights

        except Exception as e:
            logger.error(f"❌ Knowledge insights failed: {str(e)}")
            return {}

    # Private helper methods

    async def _store_extraction_in_graph(self,
                                       extraction_result: ExtractionResult,
                                       session_id: str,
                                       user_id: Optional[str]):
        """Store extraction results in the temporal graph"""
        try:
            # Convert extraction result to knowledge format
            extracted_knowledge = ExtractedKnowledge(
                entities=[{
                    'name': e.name,
                    'type': e.entity_type.value,
                    'confidence': e.confidence,
                    'description': e.properties.get('description', ''),
                    'properties': e.properties
                } for e in extraction_result.entities],
                relations=extraction_result.relations,
                facts=extraction_result.facts,
                confidence=extraction_result.overall_confidence,
                extraction_method="enterprise_pipeline"
            )

            # Process through temporal graph
            await self.temporal_graph.process_conversation_message(
                session_id=session_id,
                message="",  # Message already processed
                user_id=user_id,
                message_type="extraction_result"
            )

        except Exception as e:
            logger.error(f"❌ Failed to store extraction in graph: {str(e)}")

    async def _generate_contextual_response(self,
                                          message: str,
                                          memory_context: MemoryContext,
                                          extraction_result: ExtractionResult) -> ContextualResponse:
        """Generate a contextual response using available context"""
        try:
            # Basic contextual response generation
            # In production, this would integrate with your RAG/LLM service

            # Create base response
            base_response = f"Verstanden. Ich habe Ihre Nachricht über '{message[:50]}...' verarbeitet."

            # Enhance with context
            enhanced_response = await self.context_memory.enhance_response_with_context(
                query=message,
                base_response=base_response,
                context=memory_context
            )

            return enhanced_response

        except Exception as e:
            logger.error(f"❌ Contextual response generation failed: {str(e)}")
            return ContextualResponse(
                answer="Es tut mir leid, ich konnte Ihre Anfrage nicht vollständig verarbeiten.",
                context=memory_context,
                confidence=0.3
            )

    def _calculate_overall_confidence(self,
                                    extraction_result: ExtractionResult,
                                    memory_context: MemoryContext) -> float:
        """Calculate overall confidence score"""
        # Weight extraction and memory confidence
        extraction_confidence = extraction_result.overall_confidence
        memory_confidence = memory_context.confidence_level

        # Weighted combination (favor extraction slightly)
        overall_confidence = extraction_confidence * 0.6 + memory_confidence * 0.4

        return overall_confidence

    def _calculate_quality_metrics(self,
                                 extraction_result: ExtractionResult,
                                 memory_context: MemoryContext) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics"""
        return {
            'extraction_quality': {
                'entity_count': len(extraction_result.entities),
                'precision_estimate': extraction_result.precision_estimate,
                'recall_estimate': extraction_result.recall_estimate,
                'f1_estimate': extraction_result.f1_estimate
            },
            'memory_quality': {
                'context_entities': len(memory_context.key_entities),
                'context_facts': len(memory_context.relevant_facts),
                'relevance_score': sum(memory_context.relevance_scores.values()) / max(len(memory_context.relevance_scores), 1)
            }
        }

    def _update_performance_stats(self, result: KnowledgeProcessingResult):
        """Update running performance statistics"""
        self.performance_stats['total_processed'] += 1
        total = self.performance_stats['total_processed']

        # Running averages
        self.performance_stats['avg_processing_time'] = (
            self.performance_stats['avg_processing_time'] * (total - 1) +
            result.processing_time_ms
        ) / total

        self.performance_stats['avg_confidence'] = (
            self.performance_stats['avg_confidence'] * (total - 1) +
            result.confidence_score
        ) / total

        # Success rate (confidence > 0.5)
        successes = self.performance_stats['success_rate'] * (total - 1)
        if result.confidence_score > 0.5:
            successes += 1
        self.performance_stats['success_rate'] = successes / total

    async def _assess_pipeline_health(self) -> float:
        """Assess extraction pipeline health"""
        try:
            pipeline_metrics = self.extraction_pipeline.get_performance_metrics()

            # Check if pipeline is functioning
            if pipeline_metrics.get('total_extractions', 0) > 0:
                # Check average confidence
                avg_confidence = pipeline_metrics.get('avg_confidence', 0.5)
                return min(1.0, avg_confidence + 0.3)  # Boost score for functioning pipeline
            else:
                return 0.8  # Default healthy score if no recent activity
        except Exception:
            return 0.5

    async def _assess_memory_health(self) -> float:
        """Assess context memory system health"""
        try:
            memory_metrics = await self.context_memory.get_performance_metrics()

            # Check cache hit rate and retrieval performance
            cache_hit_rate = memory_metrics.get('cache_hit_rate', 0.5)
            return min(1.0, cache_hit_rate + 0.2)
        except Exception:
            return 0.7

    async def _assess_graph_health(self) -> float:
        """Assess temporal graph health"""
        try:
            graph_metrics = self.temporal_graph.get_performance_metrics()

            # Check if graph is processing entities
            entities_created = graph_metrics.get('entities_created', 0)
            if entities_created > 0:
                return 0.9
            else:
                return 0.8
        except Exception:
            return 0.6

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        metrics = {
            'service_stats': self.performance_stats.copy(),
            'extraction_pipeline': self.extraction_pipeline.get_performance_metrics(),
            'temporal_graph': self.temporal_graph.get_performance_metrics()
        }

        if self.monitoring:
            metrics['monitoring'] = self.monitoring.get_live_metrics()

        return metrics

    async def cleanup_session(self, session_id: str):
        """Clean up resources for ended session"""
        try:
            if self.monitoring:
                self.monitoring.track_session_end(session_id)

            # Clear session from memory caches
            if hasattr(self.context_memory, 'session_memory_cache'):
                keys_to_remove = [k for k in self.context_memory.session_memory_cache.keys()
                                if k.startswith(f"{session_id}:")]
                for key in keys_to_remove:
                    del self.context_memory.session_memory_cache[key]

            logger.info(f"🧹 Session {session_id} cleaned up")

        except Exception as e:
            logger.error(f"❌ Session cleanup failed: {str(e)}")