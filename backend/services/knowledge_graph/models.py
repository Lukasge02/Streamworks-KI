"""
Knowledge Graph Database Models
Enterprise-grade temporal models for knowledge representation
Implements bi-temporal versioning with entity-relation-fact structure
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, String, DateTime, Float, Integer, Text, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

from models.core import Base

class EntityType(Enum):
    """Types of knowledge entities"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    CONCEPT = "concept"
    PRODUCT = "product"
    SERVICE = "service"
    TECHNOLOGY = "technology"
    EVENT = "event"
    DOCUMENT = "document"
    PROCESS = "process"
    SYSTEM = "system"
    DATA = "data"
    UNKNOWN = "unknown"

class RelationType(Enum):
    """Types of relationships between entities"""
    # Hierarchical relationships
    IS_A = "is_a"
    PART_OF = "part_of"
    CONTAINS = "contains"
    BELONGS_TO = "belongs_to"

    # Functional relationships
    USES = "uses"
    PROVIDES = "provides"
    DEPENDS_ON = "depends_on"
    IMPLEMENTS = "implements"

    # Temporal relationships
    BEFORE = "before"
    AFTER = "after"
    DURING = "during"
    CAUSES = "causes"

    # Spatial relationships
    LOCATED_IN = "located_in"
    NEAR = "near"
    CONNECTS_TO = "connects_to"

    # Social relationships
    WORKS_WITH = "works_with"
    REPORTS_TO = "reports_to"
    COLLABORATES_WITH = "collaborates_with"

    # Generic relationships
    RELATED_TO = "related_to"
    MENTIONS = "mentions"
    DISCUSSES = "discusses"
    REFERENCES = "references"

class FactType(Enum):
    """Types of knowledge facts"""
    ATTRIBUTE = "attribute"           # Entity has a property
    STATE = "state"                   # Entity is in a state
    ACTION = "action"                 # Entity performs action
    OBSERVATION = "observation"       # Observed fact
    INFERENCE = "inference"           # Inferred fact
    MEASUREMENT = "measurement"       # Quantitative fact
    RELATIONSHIP = "relationship"     # Fact about relationship
    TEMPORAL = "temporal"            # Time-based fact
    CONDITIONAL = "conditional"       # If-then fact

class KnowledgeEpisode(Base):
    """
    Conversation episodes - temporal containers for knowledge
    Represents a conversation session or context window
    """
    __tablename__ = "knowledge_episodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)

    # Episode metadata
    name = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    context_tags = Column(ARRAY(String), nullable=True)

    # Temporal fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)  # null = currently valid

    # Metrics
    message_count = Column(Integer, default=0)
    entity_count = Column(Integer, default=0)
    relation_count = Column(Integer, default=0)

    # Relationships
    entities = relationship("KnowledgeEntity", back_populates="episode", lazy="dynamic")
    relations = relationship("KnowledgeRelation", back_populates="episode", lazy="dynamic")
    facts = relationship("KnowledgeFact", back_populates="episode", lazy="dynamic")

class KnowledgeEntity(Base):
    """
    Knowledge entities with bi-temporal versioning
    Represents people, places, concepts, systems, etc.
    """
    __tablename__ = "knowledge_entities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("knowledge_episodes.id"), nullable=False, index=True)

    # Entity identification
    name = Column(String(500), nullable=False, index=True)
    normalized_name = Column(String(500), nullable=True, index=True)  # For deduplication
    entity_type = Column(String, nullable=False, index=True)  # EntityType enum
    aliases = Column(ARRAY(String), nullable=True)

    # Entity properties
    description = Column(Text, nullable=True)
    properties = Column(JSON, nullable=True)  # Flexible properties
    embedding = Column(Text, nullable=True)   # Serialized embedding vector

    # Confidence and quality metrics
    confidence = Column(Float, nullable=False, default=0.5)
    quality_score = Column(Float, nullable=True)
    verification_status = Column(String, default="unverified")  # verified, unverified, disputed

    # Temporal fields (bi-temporal)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)  # null = currently valid

    # Usage tracking
    first_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    occurrence_count = Column(Integer, default=1)

    # Relationships
    episode = relationship("KnowledgeEpisode", back_populates="entities")
    outgoing_relations = relationship("KnowledgeRelation", foreign_keys="[KnowledgeRelation.source_entity_id]", back_populates="source_entity", lazy="dynamic")
    incoming_relations = relationship("KnowledgeRelation", foreign_keys="[KnowledgeRelation.target_entity_id]", back_populates="target_entity", lazy="dynamic")
    facts = relationship("KnowledgeFact", back_populates="primary_entity", lazy="dynamic")

class KnowledgeRelation(Base):
    """
    Relationships between entities with confidence scoring
    Supports typed, weighted, and temporal relationships
    """
    __tablename__ = "knowledge_relations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("knowledge_episodes.id"), nullable=False, index=True)

    # Relation endpoints
    source_entity_id = Column(String, ForeignKey("knowledge_entities.id"), nullable=False, index=True)
    target_entity_id = Column(String, ForeignKey("knowledge_entities.id"), nullable=False, index=True)

    # Relation properties
    relation_type = Column(String, nullable=False, index=True)  # RelationType enum
    description = Column(Text, nullable=True)
    properties = Column(JSON, nullable=True)

    # Confidence and weight
    confidence = Column(Float, nullable=False, default=0.5)
    weight = Column(Float, nullable=False, default=1.0)
    strength = Column(Float, nullable=True)  # Relationship strength

    # Direction and symmetry
    is_directed = Column(Boolean, default=True)
    is_symmetric = Column(Boolean, default=False)

    # Temporal fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)

    # Context
    context = Column(Text, nullable=True)  # Textual context where relation was found

    # Relationships
    episode = relationship("KnowledgeEpisode", back_populates="relations")
    source_entity = relationship("KnowledgeEntity", foreign_keys=[source_entity_id], back_populates="outgoing_relations")
    target_entity = relationship("KnowledgeEntity", foreign_keys=[target_entity_id], back_populates="incoming_relations")

class KnowledgeFact(Base):
    """
    Atomic facts about entities and relationships
    Implements fact-based knowledge representation
    """
    __tablename__ = "knowledge_facts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("knowledge_episodes.id"), nullable=False, index=True)
    primary_entity_id = Column(String, ForeignKey("knowledge_entities.id"), nullable=False, index=True)

    # Fact content
    fact_type = Column(String, nullable=False, index=True)  # FactType enum
    subject = Column(String(500), nullable=False)  # What the fact is about
    predicate = Column(String(500), nullable=False)  # The relationship/property
    object = Column(Text, nullable=False)  # The value/target

    # Additional context
    description = Column(Text, nullable=True)
    properties = Column(JSON, nullable=True)
    units = Column(String(50), nullable=True)  # For measurements

    # Confidence and provenance
    confidence = Column(Float, nullable=False, default=0.5)
    source = Column(String(255), nullable=True)  # Where fact came from
    evidence = Column(Text, nullable=True)  # Supporting evidence

    # Temporal validity
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)

    # Fact-specific temporal info
    fact_time = Column(DateTime, nullable=True)  # When the fact occurred
    fact_duration = Column(Integer, nullable=True)  # Duration in seconds

    # Quality metrics
    verification_count = Column(Integer, default=0)
    dispute_count = Column(Integer, default=0)

    # Relationships
    episode = relationship("KnowledgeEpisode", back_populates="facts")
    primary_entity = relationship("KnowledgeEntity", back_populates="facts")

class KnowledgeCommunity(Base):
    """
    Communities of related entities for hierarchical organization
    Enables clustering and community detection
    """
    __tablename__ = "knowledge_communities"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Community properties
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    community_type = Column(String(100), nullable=True)

    # Metrics
    entity_count = Column(Integer, default=0)
    relation_count = Column(Integer, default=0)
    density = Column(Float, nullable=True)  # Graph density
    centrality_score = Column(Float, nullable=True)

    # Temporal fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)

    # Properties
    properties = Column(JSON, nullable=True)
    tags = Column(ARRAY(String), nullable=True)

class EntityCommunityMembership(Base):
    """
    Many-to-many relationship between entities and communities
    """
    __tablename__ = "entity_community_memberships"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String, ForeignKey("knowledge_entities.id"), nullable=False, index=True)
    community_id = Column(String, ForeignKey("knowledge_communities.id"), nullable=False, index=True)

    # Membership properties
    membership_strength = Column(Float, default=1.0)
    role = Column(String(100), nullable=True)  # Role in community

    # Temporal fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)

    # Relationships
    entity = relationship("KnowledgeEntity")
    community = relationship("KnowledgeCommunity")

class KnowledgeGraphMetrics(Base):
    """
    Performance and quality metrics for the knowledge graph
    """
    __tablename__ = "knowledge_graph_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Timestamp
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Graph size metrics
    total_entities = Column(Integer, default=0)
    total_relations = Column(Integer, default=0)
    total_facts = Column(Integer, default=0)
    total_episodes = Column(Integer, default=0)

    # Quality metrics
    avg_entity_confidence = Column(Float, nullable=True)
    avg_relation_confidence = Column(Float, nullable=True)
    avg_fact_confidence = Column(Float, nullable=True)

    # Performance metrics
    extraction_accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)

    # Graph structure metrics
    graph_density = Column(Float, nullable=True)
    avg_clustering_coefficient = Column(Float, nullable=True)
    diameter = Column(Integer, nullable=True)

    # Temporal metrics
    knowledge_growth_rate = Column(Float, nullable=True)
    fact_decay_rate = Column(Float, nullable=True)

    # System metrics
    query_response_time_ms = Column(Float, nullable=True)
    extraction_time_ms = Column(Float, nullable=True)
    memory_usage_mb = Column(Float, nullable=True)

    # Additional properties
    properties = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)