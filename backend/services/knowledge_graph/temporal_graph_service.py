"""
Temporal Knowledge Graph Service
Enterprise-grade knowledge graph implementation inspired by Zep and Graphiti
Handles bi-temporal data models with real-time incremental updates
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, and_, or_
from sqlalchemy.orm import selectinload

from models.core import ConversationSession, ChatMessage
from services.embedding_gemma import EmbeddingService
from .models import (
    KnowledgeEntity, KnowledgeRelation, KnowledgeFact,
    KnowledgeEpisode, EntityType, RelationType, FactType
)

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Confidence levels for knowledge elements"""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95

@dataclass
class ExtractedKnowledge:
    """Container for extracted knowledge from conversation"""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    facts: List[Dict[str, Any]] = field(default_factory=list)
    context_summary: Optional[str] = None
    confidence: float = 0.5
    extraction_method: str = "hybrid"

@dataclass
class GraphQueryResult:
    """Result from knowledge graph queries"""
    entities: List[KnowledgeEntity] = field(default_factory=list)
    relations: List[KnowledgeRelation] = field(default_factory=list)
    facts: List[KnowledgeFact] = field(default_factory=list)
    confidence_score: float = 0.0
    query_time_ms: float = 0.0

class TemporalKnowledgeGraphService:
    """
    Enterprise-grade temporal knowledge graph service
    Implements bi-temporal data models with incremental updates
    """

    def __init__(self,
                 db_session: AsyncSession,
                 embedding_service: EmbeddingService,
                 max_entity_cache_size: int = 1000,
                 fact_retention_days: int = 90):
        self.db = db_session
        self.embedding_service = embedding_service
        self.max_cache_size = max_entity_cache_size
        self.fact_retention_days = fact_retention_days

        # In-memory caches for performance
        self.entity_cache: Dict[str, KnowledgeEntity] = {}
        self.relation_cache: Dict[str, List[KnowledgeRelation]] = defaultdict(list)
        self.session_contexts: Dict[str, Dict] = {}

        # Performance metrics
        self.metrics = {
            'entities_created': 0,
            'relations_created': 0,
            'facts_created': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'extraction_time_ms': 0.0
        }

        logger.info("🧠 TemporalKnowledgeGraphService initialized")

    async def process_conversation_message(self,
                                         session_id: str,
                                         message: str,
                                         user_id: Optional[str] = None,
                                         message_type: str = "user") -> ExtractedKnowledge:
        """
        Process a conversation message and extract knowledge
        Core method for real-time knowledge extraction
        """
        start_time = datetime.utcnow()

        try:
            # Get or create episode for this conversation session
            episode = await self._get_or_create_episode(session_id, user_id)

            # Extract knowledge using multi-stage pipeline
            extracted = await self._extract_knowledge_multi_stage(
                message, session_id, episode.id
            )

            # Store extracted knowledge in graph
            await self._store_extracted_knowledge(extracted, episode.id)

            # Update session context
            self._update_session_context(session_id, extracted)

            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.metrics['extraction_time_ms'] = (
                self.metrics['extraction_time_ms'] * 0.9 + processing_time * 0.1
            )

            logger.info(f"📝 Processed message for session {session_id}: "
                       f"{len(extracted.entities)} entities, "
                       f"{len(extracted.relations)} relations, "
                       f"{len(extracted.facts)} facts")

            return extracted

        except Exception as e:
            logger.error(f"❌ Failed to process conversation message: {str(e)}")
            raise

    async def get_session_context(self,
                                session_id: str,
                                max_facts: int = 20,
                                max_entities: int = 15) -> Dict[str, Any]:
        """
        Get comprehensive context for a conversation session
        Returns relevant entities, facts, and relationships
        """
        try:
            # Check cache first
            if session_id in self.session_contexts:
                self.metrics['cache_hits'] += 1
                cached_context = self.session_contexts[session_id].copy()

                # Refresh if older than 5 minutes
                if (datetime.utcnow() - cached_context.get('updated_at', datetime.min)).total_seconds() > 300:
                    return await self._build_fresh_context(session_id, max_facts, max_entities)

                return cached_context

            self.metrics['cache_misses'] += 1
            return await self._build_fresh_context(session_id, max_facts, max_entities)

        except Exception as e:
            logger.error(f"❌ Failed to get session context: {str(e)}")
            return {}

    async def query_knowledge_graph(self,
                                  query: str,
                                  session_id: Optional[str] = None,
                                  entity_types: Optional[List[EntityType]] = None,
                                  confidence_threshold: float = 0.5) -> GraphQueryResult:
        """
        Query the knowledge graph using semantic search
        Returns relevant entities, relations, and facts
        """
        start_time = datetime.utcnow()

        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.create_embeddings([query])
            if not query_embedding:
                return GraphQueryResult()

            embedding_vector = query_embedding[0]

            # Search for relevant entities using vector similarity
            entities = await self._search_entities_by_embedding(
                embedding_vector, entity_types, confidence_threshold
            )

            # Find relations involving these entities
            relations = await self._get_relations_for_entities(
                [e.id for e in entities], confidence_threshold
            )

            # Get facts related to entities and relations
            facts = await self._get_facts_for_entities_and_relations(
                [e.id for e in entities],
                [r.id for r in relations],
                confidence_threshold
            )

            # Calculate overall confidence score
            avg_confidence = self._calculate_result_confidence(entities, relations, facts)

            query_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return GraphQueryResult(
                entities=entities,
                relations=relations,
                facts=facts,
                confidence_score=avg_confidence,
                query_time_ms=query_time
            )

        except Exception as e:
            logger.error(f"❌ Knowledge graph query failed: {str(e)}")
            return GraphQueryResult()

    async def merge_duplicate_entities(self, similarity_threshold: float = 0.85):
        """
        Merge duplicate entities based on semantic similarity
        Maintains data integrity during merging
        """
        try:
            logger.info("🔄 Starting entity deduplication process...")

            # Get all entities
            result = await self.db.execute(
                select(KnowledgeEntity).where(
                    KnowledgeEntity.valid_to.is_(None)
                )
            )
            entities = result.scalars().all()

            # Group entities by type for efficient comparison
            entities_by_type = defaultdict(list)
            for entity in entities:
                entities_by_type[entity.entity_type].append(entity)

            merged_count = 0

            for entity_type, type_entities in entities_by_type.items():
                if len(type_entities) < 2:
                    continue

                # Compare embeddings for similarity
                for i, entity1 in enumerate(type_entities):
                    for entity2 in type_entities[i+1:]:
                        if entity1.embedding and entity2.embedding:
                            similarity = await self._calculate_embedding_similarity(
                                entity1.embedding, entity2.embedding
                            )

                            if similarity >= similarity_threshold:
                                await self._merge_entities(entity1, entity2)
                                merged_count += 1

            logger.info(f"✅ Merged {merged_count} duplicate entities")

        except Exception as e:
            logger.error(f"❌ Entity deduplication failed: {str(e)}")

    async def cleanup_old_facts(self):
        """
        Clean up old facts based on retention policy
        Maintains temporal integrity
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.fact_retention_days)

            # Soft delete old facts by setting valid_to
            result = await self.db.execute(
                update(KnowledgeFact)
                .where(
                    and_(
                        KnowledgeFact.created_at < cutoff_date,
                        KnowledgeFact.valid_to.is_(None)
                    )
                )
                .values(valid_to=datetime.utcnow())
            )

            cleaned_count = result.rowcount
            await self.db.commit()

            logger.info(f"🧹 Cleaned up {cleaned_count} old facts")

        except Exception as e:
            logger.error(f"❌ Fact cleanup failed: {str(e)}")

    # Private methods for internal operations

    async def _get_or_create_episode(self, session_id: str, user_id: Optional[str]) -> KnowledgeEpisode:
        """Get existing episode or create new one for conversation session"""
        # Try to find existing episode
        result = await self.db.execute(
            select(KnowledgeEpisode).where(
                and_(
                    KnowledgeEpisode.session_id == session_id,
                    KnowledgeEpisode.valid_to.is_(None)
                )
            )
        )
        episode = result.scalar_one_or_none()

        if not episode:
            # Create new episode
            episode = KnowledgeEpisode(
                id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                name=f"Conversation_{session_id[:8]}",
                summary="Active conversation session",
                created_at=datetime.utcnow()
            )
            self.db.add(episode)
            await self.db.commit()
            await self.db.refresh(episode)

        return episode

    async def _extract_knowledge_multi_stage(self,
                                           message: str,
                                           session_id: str,
                                           episode_id: str) -> ExtractedKnowledge:
        """Multi-stage knowledge extraction pipeline"""
        extracted = ExtractedKnowledge()

        # Stage 1: Template-based extraction (fast, high precision)
        template_results = await self._template_based_extraction(message)

        # Stage 2: LLM-based extraction (slower, high recall)
        llm_results = await self._llm_based_extraction(message, session_id)

        # Stage 3: Combine and validate results
        extracted = await self._combine_extraction_results(template_results, llm_results)

        return extracted

    async def _template_based_extraction(self, message: str) -> ExtractedKnowledge:
        """Fast template-based knowledge extraction"""
        # Implementation would use regex patterns and rule-based extraction
        # For now, return empty results - to be implemented
        return ExtractedKnowledge(extraction_method="template")

    async def _llm_based_extraction(self, message: str, session_id: str) -> ExtractedKnowledge:
        """LLM-powered knowledge extraction"""
        # Implementation would use Ollama or other LLM service
        # For now, return empty results - to be implemented
        return ExtractedKnowledge(extraction_method="llm")

    async def _combine_extraction_results(self,
                                        template_results: ExtractedKnowledge,
                                        llm_results: ExtractedKnowledge) -> ExtractedKnowledge:
        """Combine and validate extraction results"""
        # Combine entities, relations, facts with confidence scoring
        combined = ExtractedKnowledge(extraction_method="hybrid")

        # Merge entities with deduplication
        all_entities = template_results.entities + llm_results.entities
        combined.entities = await self._deduplicate_entities(all_entities)

        # Merge relations
        combined.relations = template_results.relations + llm_results.relations

        # Merge facts
        combined.facts = template_results.facts + llm_results.facts

        # Calculate combined confidence
        combined.confidence = (template_results.confidence + llm_results.confidence) / 2

        return combined

    async def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities from extraction results"""
        seen = set()
        deduplicated = []

        for entity in entities:
            key = (entity.get('name', '').lower(), entity.get('type', ''))
            if key not in seen:
                seen.add(key)
                deduplicated.append(entity)

        return deduplicated

    async def _store_extracted_knowledge(self, extracted: ExtractedKnowledge, episode_id: str):
        """Store extracted knowledge in the database"""
        try:
            # Store entities
            for entity_data in extracted.entities:
                await self._create_or_update_entity(entity_data, episode_id)
                self.metrics['entities_created'] += 1

            # Store relations
            for relation_data in extracted.relations:
                await self._create_relation(relation_data, episode_id)
                self.metrics['relations_created'] += 1

            # Store facts
            for fact_data in extracted.facts:
                await self._create_fact(fact_data, episode_id)
                self.metrics['facts_created'] += 1

            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Failed to store extracted knowledge: {str(e)}")
            raise

    async def _create_or_update_entity(self, entity_data: Dict[str, Any], episode_id: str):
        """Create new entity or update existing one"""
        name = entity_data.get('name', '').strip()
        entity_type = entity_data.get('type', 'UNKNOWN')

        if not name:
            return

        # Check if entity already exists
        result = await self.db.execute(
            select(KnowledgeEntity).where(
                and_(
                    KnowledgeEntity.name == name,
                    KnowledgeEntity.entity_type == EntityType(entity_type),
                    KnowledgeEntity.valid_to.is_(None)
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update confidence and last_seen
            existing.confidence = max(existing.confidence, entity_data.get('confidence', 0.5))
            existing.last_seen_at = datetime.utcnow()
            existing.occurrence_count += 1
        else:
            # Create new entity
            embedding = None
            if self.embedding_service:
                embeddings = await self.embedding_service.create_embeddings([name])
                if embeddings:
                    embedding = json.dumps(embeddings[0])

            entity = KnowledgeEntity(
                id=str(uuid.uuid4()),
                name=name,
                entity_type=EntityType(entity_type),
                description=entity_data.get('description', ''),
                confidence=entity_data.get('confidence', 0.5),
                episode_id=episode_id,
                embedding=embedding,
                created_at=datetime.utcnow(),
                last_seen_at=datetime.utcnow(),
                occurrence_count=1
            )
            self.db.add(entity)

    async def _create_relation(self, relation_data: Dict[str, Any], episode_id: str):
        """Create knowledge relation between entities"""
        # Implementation for creating relations
        pass

    async def _create_fact(self, fact_data: Dict[str, Any], episode_id: str):
        """Create knowledge fact"""
        # Implementation for creating facts
        pass

    def _update_session_context(self, session_id: str, extracted: ExtractedKnowledge):
        """Update in-memory session context"""
        self.session_contexts[session_id] = {
            'entities': extracted.entities,
            'relations': extracted.relations,
            'facts': extracted.facts,
            'confidence': extracted.confidence,
            'updated_at': datetime.utcnow()
        }

    async def _build_fresh_context(self, session_id: str, max_facts: int, max_entities: int) -> Dict[str, Any]:
        """Build fresh context from database"""
        # Implementation for building fresh context from DB
        return {}

    async def _search_entities_by_embedding(self,
                                          embedding_vector: List[float],
                                          entity_types: Optional[List[EntityType]],
                                          confidence_threshold: float) -> List[KnowledgeEntity]:
        """Search entities using vector similarity"""
        # Implementation for vector-based entity search
        return []

    async def _get_relations_for_entities(self,
                                        entity_ids: List[str],
                                        confidence_threshold: float) -> List[KnowledgeRelation]:
        """Get relations involving specified entities"""
        # Implementation for relation retrieval
        return []

    async def _get_facts_for_entities_and_relations(self,
                                                  entity_ids: List[str],
                                                  relation_ids: List[str],
                                                  confidence_threshold: float) -> List[KnowledgeFact]:
        """Get facts related to entities and relations"""
        # Implementation for fact retrieval
        return []

    def _calculate_result_confidence(self,
                                   entities: List[KnowledgeEntity],
                                   relations: List[KnowledgeRelation],
                                   facts: List[KnowledgeFact]) -> float:
        """Calculate overall confidence score for query results"""
        if not entities and not relations and not facts:
            return 0.0

        total_confidence = 0.0
        count = 0

        for entity in entities:
            total_confidence += entity.confidence
            count += 1

        for relation in relations:
            total_confidence += relation.confidence
            count += 1

        for fact in facts:
            total_confidence += fact.confidence
            count += 1

        return total_confidence / count if count > 0 else 0.0

    async def _calculate_embedding_similarity(self, emb1: str, emb2: str) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            import numpy as np
            vec1 = np.array(json.loads(emb1))
            vec2 = np.array(json.loads(emb2))

            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0

    async def _merge_entities(self, entity1: KnowledgeEntity, entity2: KnowledgeEntity):
        """Merge two similar entities"""
        # Keep entity with higher confidence, merge properties
        if entity1.confidence >= entity2.confidence:
            primary, secondary = entity1, entity2
        else:
            primary, secondary = entity2, entity1

        # Update primary entity
        primary.occurrence_count += secondary.occurrence_count
        primary.confidence = max(primary.confidence, secondary.confidence)
        primary.last_seen_at = max(primary.last_seen_at or datetime.min,
                                 secondary.last_seen_at or datetime.min)

        # Mark secondary as invalid (soft delete)
        secondary.valid_to = datetime.utcnow()

        # Update relations to point to primary entity
        await self.db.execute(
            update(KnowledgeRelation)
            .where(KnowledgeRelation.source_entity_id == secondary.id)
            .values(source_entity_id=primary.id)
        )

        await self.db.execute(
            update(KnowledgeRelation)
            .where(KnowledgeRelation.target_entity_id == secondary.id)
            .values(target_entity_id=primary.id)
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        return {
            **self.metrics,
            'cache_size': len(self.entity_cache),
            'active_sessions': len(self.session_contexts),
            'cache_hit_rate': self.metrics['cache_hits'] / max(
                self.metrics['cache_hits'] + self.metrics['cache_misses'], 1
            )
        }