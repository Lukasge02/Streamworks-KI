"""
Enterprise Context-Aware Memory System
Hierarchical memory with Episodes → Facts → Entities → Communities
Real-time context retrieval and relevance scoring
"""
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, deque

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, and_, or_, desc, func
from sqlalchemy.orm import selectinload, joinedload

from .models import (
    KnowledgeEntity, KnowledgeRelation, KnowledgeFact,
    KnowledgeEpisode, EntityType, RelationType, FactType
)
from .temporal_graph_service import GraphQueryResult
from services.embedding_gemma import EmbeddingService

logger = logging.getLogger(__name__)

class MemoryRetrievalMode(Enum):
    """Memory retrieval strategies"""
    RECENT_FIRST = "recent_first"           # Prioritize recent memories
    RELEVANCE_FIRST = "relevance_first"     # Semantic relevance priority
    IMPORTANCE_FIRST = "importance_first"   # High-confidence facts first
    COMPREHENSIVE = "comprehensive"         # Balanced approach
    CONTEXTUAL = "contextual"              # Context-aware retrieval

class ContextScope(Enum):
    """Scope of context retrieval"""
    SESSION_ONLY = "session"               # Current session only
    USER_HISTORY = "user"                  # User's historical context
    GLOBAL_KNOWLEDGE = "global"            # Cross-user knowledge
    COMMUNITY_KNOWLEDGE = "community"      # Community-specific knowledge

@dataclass
class MemoryContext:
    """Rich context container for conversation memory"""
    # Core entities and facts
    key_entities: List[KnowledgeEntity] = field(default_factory=list)
    relevant_facts: List[KnowledgeFact] = field(default_factory=list)
    active_relations: List[KnowledgeRelation] = field(default_factory=list)

    # Episode information
    current_episode: Optional[KnowledgeEpisode] = None
    related_episodes: List[KnowledgeEpisode] = field(default_factory=list)

    # Context metadata
    relevance_scores: Dict[str, float] = field(default_factory=dict)
    context_summary: str = ""
    confidence_level: float = 0.0

    # Temporal information
    time_horizon_hours: int = 24
    last_updated: datetime = field(default_factory=datetime.utcnow)

    # Performance metrics
    retrieval_time_ms: float = 0.0
    total_entities_considered: int = 0
    context_compression_ratio: float = 0.0

@dataclass
class ContextualResponse:
    """Enhanced response with contextual information"""
    answer: str = ""
    context: MemoryContext = field(default_factory=MemoryContext)
    confidence: float = 0.0
    reasoning: str = ""
    sources: List[str] = field(default_factory=list)

class EnterpriseContextMemorySystem:
    """
    Production-grade context-aware memory system
    Hierarchical memory with intelligent context retrieval
    """

    def __init__(self,
                 db_session: AsyncSession,
                 embedding_service: Optional[EmbeddingService] = None,
                 max_context_entities: int = 20,
                 max_context_facts: int = 50,
                 default_time_horizon_hours: int = 24):

        self.db = db_session
        self.embedding_service = embedding_service
        self.max_context_entities = max_context_entities
        self.max_context_facts = max_context_facts
        self.default_time_horizon = default_time_horizon_hours

        # Memory caches for performance
        self.session_memory_cache: Dict[str, MemoryContext] = {}
        self.entity_embedding_cache: Dict[str, List[float]] = {}
        self.recent_queries_cache = deque(maxlen=100)

        # Context scoring weights
        self.context_weights = {
            'recency': 0.3,
            'relevance': 0.4,
            'importance': 0.2,
            'frequency': 0.1
        }

        # Performance tracking
        self.performance_metrics = {
            'total_retrievals': 0,
            'avg_retrieval_time_ms': 0.0,
            'cache_hit_rate': 0.0,
            'context_relevance_score': 0.0,
            'memory_efficiency': 0.0
        }

        logger.info("🧠 EnterpriseContextMemorySystem initialized")

    async def get_contextual_memory(self,
                                  query: str,
                                  session_id: str,
                                  user_id: Optional[str] = None,
                                  retrieval_mode: MemoryRetrievalMode = MemoryRetrievalMode.COMPREHENSIVE,
                                  scope: ContextScope = ContextScope.SESSION_ONLY,
                                  time_horizon_hours: Optional[int] = None) -> MemoryContext:
        """
        Retrieve rich contextual memory for conversation
        Core method for context-aware responses
        """
        start_time = datetime.utcnow()

        try:
            # Check cache first
            cache_key = f"{session_id}:{hash(query)}"
            if cache_key in self.session_memory_cache:
                cached_context = self.session_memory_cache[cache_key]
                if self._is_context_fresh(cached_context):
                    logger.info("💾 Using cached context")
                    return cached_context

            # Build fresh context
            context = MemoryContext(
                time_horizon_hours=time_horizon_hours or self.default_time_horizon
            )

            # Get current episode
            context.current_episode = await self._get_current_episode(session_id, user_id)

            # Retrieve entities based on query and mode
            context.key_entities = await self._retrieve_relevant_entities(
                query, session_id, retrieval_mode, scope, context.time_horizon_hours
            )

            # Get facts for retrieved entities
            context.relevant_facts = await self._retrieve_relevant_facts(
                context.key_entities, query, retrieval_mode, context.time_horizon_hours
            )

            # Get relations between entities
            context.active_relations = await self._retrieve_active_relations(
                context.key_entities, context.time_horizon_hours
            )

            # Get related episodes for broader context
            if scope != ContextScope.SESSION_ONLY:
                context.related_episodes = await self._get_related_episodes(
                    context.current_episode, user_id, scope
                )

            # Calculate relevance scores
            context.relevance_scores = await self._calculate_relevance_scores(
                context, query
            )

            # Generate context summary
            context.context_summary = await self._generate_context_summary(context)

            # Calculate overall confidence
            context.confidence_level = self._calculate_context_confidence(context)

            # Performance metrics
            retrieval_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            context.retrieval_time_ms = retrieval_time
            context.total_entities_considered = len(context.key_entities)

            # Cache the context
            self.session_memory_cache[cache_key] = context

            # Update performance metrics
            self._update_performance_metrics(context)

            logger.info(f"🎯 Context retrieved: {len(context.key_entities)} entities, "
                       f"{len(context.relevant_facts)} facts, "
                       f"confidence: {context.confidence_level:.3f}, "
                       f"time: {retrieval_time:.1f}ms")

            return context

        except Exception as e:
            logger.error(f"❌ Context memory retrieval failed: {str(e)}")
            return MemoryContext()

    async def enhance_response_with_context(self,
                                          query: str,
                                          base_response: str,
                                          context: MemoryContext) -> ContextualResponse:
        """
        Enhance response with contextual information
        Adds relevant background and improves accuracy
        """
        try:
            # Analyze which context elements are most relevant
            relevant_entities = await self._filter_relevant_entities(
                context.key_entities, query, base_response
            )

            relevant_facts = await self._filter_relevant_facts(
                context.relevant_facts, query, base_response
            )

            # Generate contextual enhancements
            enhancements = await self._generate_contextual_enhancements(
                relevant_entities, relevant_facts, query
            )

            # Combine base response with contextual information
            enhanced_response = await self._combine_response_with_context(
                base_response, enhancements, context
            )

            # Calculate confidence based on context quality
            confidence = self._calculate_response_confidence(
                enhanced_response, context, relevant_entities, relevant_facts
            )

            # Generate reasoning explanation
            reasoning = await self._generate_reasoning_explanation(
                context, relevant_entities, relevant_facts
            )

            # Extract sources
            sources = self._extract_context_sources(relevant_entities, relevant_facts)

            return ContextualResponse(
                answer=enhanced_response,
                context=context,
                confidence=confidence,
                reasoning=reasoning,
                sources=sources
            )

        except Exception as e:
            logger.error(f"❌ Response enhancement failed: {str(e)}")
            return ContextualResponse(
                answer=base_response,
                context=context,
                confidence=0.5
            )

    async def update_memory_from_interaction(self,
                                           query: str,
                                           response: str,
                                           session_id: str,
                                           user_id: Optional[str] = None,
                                           feedback: Optional[Dict[str, Any]] = None):
        """
        Update memory based on user interaction
        Learns from conversation patterns and feedback
        """
        try:
            # Get current episode
            episode = await self._get_current_episode(session_id, user_id)

            # Extract new entities from interaction
            new_entities = await self._extract_interaction_entities(query, response)

            # Store interaction facts
            await self._store_interaction_facts(episode.id, query, response, feedback)

            # Update entity occurrence counts and recency
            await self._update_entity_statistics(new_entities, episode.id)

            # Learn from user feedback if provided
            if feedback:
                await self._process_user_feedback(feedback, episode.id)

            # Update episode metrics
            await self._update_episode_metrics(episode)

            logger.info(f"📝 Memory updated from interaction: {len(new_entities)} new entities")

        except Exception as e:
            logger.error(f"❌ Memory update failed: {str(e)}")

    async def get_memory_insights(self,
                                session_id: str,
                                user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get insights about memory state and patterns
        Useful for conversation analytics
        """
        try:
            insights = {}

            # Episode statistics
            episode = await self._get_current_episode(session_id, user_id)
            insights['current_episode'] = {
                'id': episode.id if episode else None,
                'entity_count': episode.entity_count if episode else 0,
                'message_count': episode.message_count if episode else 0,
                'duration_hours': self._calculate_episode_duration(episode) if episode else 0
            }

            # Entity distribution
            insights['entity_distribution'] = await self._get_entity_type_distribution(session_id)

            # Knowledge density
            insights['knowledge_metrics'] = await self._calculate_knowledge_metrics(session_id)

            # Memory quality scores
            insights['quality_metrics'] = await self._calculate_memory_quality_metrics(session_id)

            # Trends and patterns
            insights['conversation_patterns'] = await self._analyze_conversation_patterns(session_id)

            return insights

        except Exception as e:
            logger.error(f"❌ Memory insights failed: {str(e)}")
            return {}

    # Private methods for internal operations

    async def _get_current_episode(self, session_id: str, user_id: Optional[str]) -> Optional[KnowledgeEpisode]:
        """Get or create current episode for session"""
        result = await self.db.execute(
            select(KnowledgeEpisode).where(
                and_(
                    KnowledgeEpisode.session_id == session_id,
                    KnowledgeEpisode.valid_to.is_(None)
                )
            ).options(
                selectinload(KnowledgeEpisode.entities),
                selectinload(KnowledgeEpisode.facts)
            )
        )
        return result.scalar_one_or_none()

    async def _retrieve_relevant_entities(self,
                                        query: str,
                                        session_id: str,
                                        mode: MemoryRetrievalMode,
                                        scope: ContextScope,
                                        time_horizon_hours: int) -> List[KnowledgeEntity]:
        """Retrieve entities based on query and retrieval mode"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_horizon_hours)

        # Base query for entities
        query_builder = select(KnowledgeEntity).where(
            and_(
                KnowledgeEntity.valid_to.is_(None),
                KnowledgeEntity.last_seen_at >= cutoff_time
            )
        )

        # Apply scope filtering
        if scope == ContextScope.SESSION_ONLY:
            episode = await self._get_current_episode(session_id, None)
            if episode:
                query_builder = query_builder.where(KnowledgeEntity.episode_id == episode.id)

        # Apply retrieval mode ordering
        if mode == MemoryRetrievalMode.RECENT_FIRST:
            query_builder = query_builder.order_by(desc(KnowledgeEntity.last_seen_at))
        elif mode == MemoryRetrievalMode.IMPORTANCE_FIRST:
            query_builder = query_builder.order_by(desc(KnowledgeEntity.confidence))
        elif mode == MemoryRetrievalMode.RELEVANCE_FIRST:
            # For relevance, we need semantic search
            if self.embedding_service:
                return await self._semantic_entity_search(query, query_builder)

        # Limit results
        query_builder = query_builder.limit(self.max_context_entities)

        result = await self.db.execute(query_builder)
        return list(result.scalars().all())

    async def _semantic_entity_search(self,
                                    query: str,
                                    base_query) -> List[KnowledgeEntity]:
        """Search entities using semantic similarity"""
        try:
            # Get query embedding
            query_embeddings = await self.embedding_service.create_embeddings([query])
            if not query_embeddings:
                # Fallback to name-based search
                return await self._text_based_entity_search(query, base_query)

            query_vector = query_embeddings[0]

            # Get all entities from base query
            result = await self.db.execute(base_query)
            all_entities = list(result.scalars().all())

            # Calculate similarities
            entity_similarities = []
            for entity in all_entities:
                if entity.embedding:
                    try:
                        entity_vector = json.loads(entity.embedding)
                        similarity = await self._calculate_vector_similarity(query_vector, entity_vector)
                        entity_similarities.append((entity, similarity))
                    except Exception:
                        entity_similarities.append((entity, 0.0))
                else:
                    # Text fallback similarity
                    text_sim = self._text_similarity(query, entity.name)
                    entity_similarities.append((entity, text_sim))

            # Sort by similarity and return top results
            entity_similarities.sort(key=lambda x: x[1], reverse=True)
            return [entity for entity, _ in entity_similarities[:self.max_context_entities]]

        except Exception as e:
            logger.error(f"❌ Semantic entity search failed: {str(e)}")
            return await self._text_based_entity_search(query, base_query)

    async def _text_based_entity_search(self, query: str, base_query) -> List[KnowledgeEntity]:
        """Fallback text-based entity search"""
        query_words = set(query.lower().split())

        result = await self.db.execute(base_query)
        all_entities = list(result.scalars().all())

        # Score entities by text similarity
        scored_entities = []
        for entity in all_entities:
            score = self._text_similarity(query, entity.name + " " + (entity.description or ""))
            scored_entities.append((entity, score))

        # Sort and return top results
        scored_entities.sort(key=lambda x: x[1], reverse=True)
        return [entity for entity, _ in scored_entities[:self.max_context_entities]]

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity using word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    async def _calculate_vector_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors"""
        try:
            import numpy as np
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            dot_product = np.dot(v1, v2)
            norms = np.linalg.norm(v1) * np.linalg.norm(v2)

            if norms == 0:
                return 0.0

            return float(dot_product / norms)
        except Exception:
            return 0.0

    async def _retrieve_relevant_facts(self,
                                     entities: List[KnowledgeEntity],
                                     query: str,
                                     mode: MemoryRetrievalMode,
                                     time_horizon_hours: int) -> List[KnowledgeFact]:
        """Retrieve facts relevant to entities and query"""
        if not entities:
            return []

        entity_ids = [e.id for e in entities]
        cutoff_time = datetime.utcnow() - timedelta(hours=time_horizon_hours)

        query_builder = select(KnowledgeFact).where(
            and_(
                KnowledgeFact.primary_entity_id.in_(entity_ids),
                KnowledgeFact.valid_to.is_(None),
                KnowledgeFact.created_at >= cutoff_time
            )
        )

        # Apply mode-specific ordering
        if mode == MemoryRetrievalMode.RECENT_FIRST:
            query_builder = query_builder.order_by(desc(KnowledgeFact.created_at))
        elif mode == MemoryRetrievalMode.IMPORTANCE_FIRST:
            query_builder = query_builder.order_by(desc(KnowledgeFact.confidence))

        query_builder = query_builder.limit(self.max_context_facts)

        result = await self.db.execute(query_builder)
        return list(result.scalars().all())

    async def _retrieve_active_relations(self,
                                       entities: List[KnowledgeEntity],
                                       time_horizon_hours: int) -> List[KnowledgeRelation]:
        """Retrieve relations between entities"""
        if not entities:
            return []

        entity_ids = [e.id for e in entities]
        cutoff_time = datetime.utcnow() - timedelta(hours=time_horizon_hours)

        result = await self.db.execute(
            select(KnowledgeRelation).where(
                and_(
                    or_(
                        KnowledgeRelation.source_entity_id.in_(entity_ids),
                        KnowledgeRelation.target_entity_id.in_(entity_ids)
                    ),
                    KnowledgeRelation.valid_to.is_(None),
                    KnowledgeRelation.created_at >= cutoff_time
                )
            ).options(
                joinedload(KnowledgeRelation.source_entity),
                joinedload(KnowledgeRelation.target_entity)
            ).limit(50)
        )

        return list(result.scalars().all())

    async def _get_related_episodes(self,
                                  current_episode: Optional[KnowledgeEpisode],
                                  user_id: Optional[str],
                                  scope: ContextScope) -> List[KnowledgeEpisode]:
        """Get related episodes based on scope"""
        if not current_episode:
            return []

        query_builder = select(KnowledgeEpisode).where(
            and_(
                KnowledgeEpisode.id != current_episode.id,
                KnowledgeEpisode.valid_to.is_(None)
            )
        )

        if scope == ContextScope.USER_HISTORY and user_id:
            query_builder = query_builder.where(KnowledgeEpisode.user_id == user_id)

        # Order by recency and limit
        query_builder = query_builder.order_by(desc(KnowledgeEpisode.created_at)).limit(5)

        result = await self.db.execute(query_builder)
        return list(result.scalars().all())

    async def _calculate_relevance_scores(self,
                                        context: MemoryContext,
                                        query: str) -> Dict[str, float]:
        """Calculate relevance scores for context elements"""
        scores = {}

        # Score entities
        for entity in context.key_entities:
            score = self._calculate_entity_relevance(entity, query)
            scores[f"entity_{entity.id}"] = score

        # Score facts
        for fact in context.relevant_facts:
            score = self._calculate_fact_relevance(fact, query)
            scores[f"fact_{fact.id}"] = score

        return scores

    def _calculate_entity_relevance(self, entity: KnowledgeEntity, query: str) -> float:
        """Calculate relevance score for an entity"""
        # Text similarity
        text_sim = self._text_similarity(query, entity.name + " " + (entity.description or ""))

        # Recency factor
        hours_since_seen = (datetime.utcnow() - (entity.last_seen_at or datetime.utcnow())).total_seconds() / 3600
        recency_factor = max(0.1, 1.0 - (hours_since_seen / 168))  # 7 days decay

        # Confidence factor
        confidence_factor = entity.confidence

        # Occurrence frequency factor
        frequency_factor = min(1.0, entity.occurrence_count / 10.0)

        # Weighted combination
        relevance = (
            text_sim * self.context_weights['relevance'] +
            recency_factor * self.context_weights['recency'] +
            confidence_factor * self.context_weights['importance'] +
            frequency_factor * self.context_weights['frequency']
        )

        return min(1.0, relevance)

    def _calculate_fact_relevance(self, fact: KnowledgeFact, query: str) -> float:
        """Calculate relevance score for a fact"""
        # Text similarity with fact content
        fact_text = f"{fact.subject} {fact.predicate} {fact.object}"
        text_sim = self._text_similarity(query, fact_text)

        # Recency and confidence factors
        hours_since_created = (datetime.utcnow() - fact.created_at).total_seconds() / 3600
        recency_factor = max(0.1, 1.0 - (hours_since_created / 168))
        confidence_factor = fact.confidence

        return (text_sim * 0.5 + recency_factor * 0.3 + confidence_factor * 0.2)

    async def _generate_context_summary(self, context: MemoryContext) -> str:
        """Generate human-readable context summary"""
        if not context.key_entities:
            return "No specific context available."

        # Top entities by relevance
        top_entities = sorted(
            context.key_entities,
            key=lambda e: context.relevance_scores.get(f"entity_{e.id}", 0.0),
            reverse=True
        )[:5]

        entity_names = [e.name for e in top_entities]

        # Recent facts
        recent_facts = sorted(
            context.relevant_facts,
            key=lambda f: f.created_at,
            reverse=True
        )[:3]

        summary_parts = []
        if entity_names:
            summary_parts.append(f"Key entities: {', '.join(entity_names)}")

        if recent_facts:
            fact_summaries = [f"{f.subject} {f.predicate}" for f in recent_facts]
            summary_parts.append(f"Recent facts: {'; '.join(fact_summaries)}")

        if context.current_episode:
            summary_parts.append(f"Episode: {context.current_episode.name}")

        return ". ".join(summary_parts) if summary_parts else "General conversation context."

    def _calculate_context_confidence(self, context: MemoryContext) -> float:
        """Calculate overall confidence in context quality"""
        if not context.key_entities:
            return 0.0

        # Average entity confidence
        entity_confidence = sum(e.confidence for e in context.key_entities) / len(context.key_entities)

        # Average fact confidence
        fact_confidence = 0.5
        if context.relevant_facts:
            fact_confidence = sum(f.confidence for f in context.relevant_facts) / len(context.relevant_facts)

        # Relevance score factor
        avg_relevance = sum(context.relevance_scores.values()) / max(len(context.relevance_scores), 1)

        # Combine factors
        return (entity_confidence * 0.4 + fact_confidence * 0.3 + avg_relevance * 0.3)

    def _is_context_fresh(self, context: MemoryContext) -> bool:
        """Check if cached context is still fresh"""
        age_minutes = (datetime.utcnow() - context.last_updated).total_seconds() / 60
        return age_minutes < 5  # 5-minute cache validity

    async def _filter_relevant_entities(self,
                                      entities: List[KnowledgeEntity],
                                      query: str,
                                      response: str) -> List[KnowledgeEntity]:
        """Filter entities that are relevant to query and response"""
        relevant = []
        combined_text = f"{query} {response}".lower()

        for entity in entities:
            if (entity.name.lower() in combined_text or
                any(alias.lower() in combined_text for alias in entity.aliases or [])):
                relevant.append(entity)

        return relevant

    async def _filter_relevant_facts(self,
                                   facts: List[KnowledgeFact],
                                   query: str,
                                   response: str) -> List[KnowledgeFact]:
        """Filter facts that are relevant to query and response"""
        relevant = []
        combined_text = f"{query} {response}".lower()

        for fact in facts:
            fact_text = f"{fact.subject} {fact.predicate} {fact.object}".lower()
            if any(word in combined_text for word in fact_text.split() if len(word) > 3):
                relevant.append(fact)

        return relevant

    async def _generate_contextual_enhancements(self,
                                              entities: List[KnowledgeEntity],
                                              facts: List[KnowledgeFact],
                                              query: str) -> List[str]:
        """Generate contextual enhancements for response"""
        enhancements = []

        # Add relevant entity information
        for entity in entities[:3]:  # Top 3 entities
            if entity.description:
                enhancements.append(f"Kontext zu {entity.name}: {entity.description}")

        # Add relevant facts
        for fact in facts[:3]:  # Top 3 facts
            enhancement = f"Bekannte Information: {fact.subject} {fact.predicate} {fact.object}"
            enhancements.append(enhancement)

        return enhancements

    async def _combine_response_with_context(self,
                                           base_response: str,
                                           enhancements: List[str],
                                           context: MemoryContext) -> str:
        """Combine base response with contextual enhancements"""
        if not enhancements:
            return base_response

        # Simple approach: append relevant context
        context_section = "\n\nRelevanter Kontext:\n" + "\n".join(f"• {enhancement}" for enhancement in enhancements[:3])

        return base_response + context_section

    def _calculate_response_confidence(self,
                                     response: str,
                                     context: MemoryContext,
                                     entities: List[KnowledgeEntity],
                                     facts: List[KnowledgeFact]) -> float:
        """Calculate confidence in enhanced response"""
        base_confidence = 0.7  # Base confidence for responses

        # Context quality factor
        context_factor = context.confidence_level * 0.3

        # Entity coverage factor
        entity_coverage = len(entities) / max(len(context.key_entities), 1) * 0.2

        # Fact support factor
        fact_support = len(facts) / max(len(context.relevant_facts), 1) * 0.2

        return min(1.0, base_confidence + context_factor + entity_coverage + fact_support)

    async def _generate_reasoning_explanation(self,
                                            context: MemoryContext,
                                            entities: List[KnowledgeEntity],
                                            facts: List[KnowledgeFact]) -> str:
        """Generate explanation of reasoning process"""
        parts = []

        if entities:
            parts.append(f"Basierend auf {len(entities)} relevanten Entitäten")

        if facts:
            parts.append(f"{len(facts)} bekannten Fakten")

        if context.current_episode:
            parts.append(f"Konversationshistorie aus Episode '{context.current_episode.name}'")

        return "Antwort generiert " + " und ".join(parts) if parts else "Standard-Antwort ohne spezifischen Kontext"

    def _extract_context_sources(self,
                                entities: List[KnowledgeEntity],
                                facts: List[KnowledgeFact]) -> List[str]:
        """Extract source information from context"""
        sources = []

        for entity in entities[:3]:
            sources.append(f"Entity: {entity.name} (Confidence: {entity.confidence:.2f})")

        for fact in facts[:3]:
            if fact.source:
                sources.append(f"Fact: {fact.source}")

        return sources

    def _update_performance_metrics(self, context: MemoryContext):
        """Update running performance metrics"""
        self.performance_metrics['total_retrievals'] += 1
        total = self.performance_metrics['total_retrievals']

        # Running averages
        self.performance_metrics['avg_retrieval_time_ms'] = (
            self.performance_metrics['avg_retrieval_time_ms'] * (total - 1) +
            context.retrieval_time_ms
        ) / total

        self.performance_metrics['context_relevance_score'] = (
            self.performance_metrics['context_relevance_score'] * (total - 1) +
            context.confidence_level
        ) / total

    # Additional helper methods would be implemented here for:
    # - _extract_interaction_entities
    # - _store_interaction_facts
    # - _update_entity_statistics
    # - _process_user_feedback
    # - _update_episode_metrics
    # - _get_entity_type_distribution
    # - _calculate_knowledge_metrics
    # - _calculate_memory_quality_metrics
    # - _analyze_conversation_patterns
    # - _calculate_episode_duration

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.performance_metrics.copy()