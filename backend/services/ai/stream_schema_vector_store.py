"""
Stream Schema Vector Store for Enterprise AI Parameter Recognition
Learns and manages stream schemas using vector embeddings for intelligent pattern matching
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer

from .chroma_manager import get_chroma_manager

logger = logging.getLogger(__name__)

@dataclass
class StreamSchema:
    """Represents a learned stream schema"""
    schema_id: str
    job_type: str
    required_fields: List[str]
    optional_fields: List[str]
    field_patterns: Dict[str, Any]
    validation_rules: Dict[str, Any]
    usage_frequency: float
    confidence_score: float
    source_stream_ids: List[str]
    created_at: str
    updated_at: str

@dataclass
class FieldPattern:
    """Represents a learned field pattern"""
    field_path: str
    data_type: str
    validation_pattern: Optional[str]
    common_values: List[Any]
    value_frequency: Dict[str, int]
    description: str

class StreamSchemaVectorStore:
    """
    Vector store for learning and matching stream schemas

    Features:
    - Schema pattern learning from existing streams
    - Semantic similarity matching for job types
    - Field validation rule inference
    - Dynamic schema evolution
    """

    def __init__(self):
        self.chroma_manager = get_chroma_manager()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Get ChromaDB collections
        self.schema_collection = self.chroma_manager.get_collection(
            "stream_schemas", "learned_schemas"
        )
        self.field_patterns_collection = self.chroma_manager.get_collection(
            "stream_schemas", "field_patterns"
        )

        # Cache for frequently used schemas
        self.schema_cache = {}
        self.pattern_cache = {}

    async def store_stream_schema(self, schema: StreamSchema) -> bool:
        """
        Store a learned stream schema

        Args:
            schema: StreamSchema object to store

        Returns:
            True if successful
        """
        try:
            # Create description for embedding
            schema_description = self._create_schema_description(schema)

            # Generate embedding
            embedding = self.embedding_model.encode(schema_description).tolist()

            # Prepare metadata
            metadata = {
                "schema_id": schema.schema_id,
                "job_type": schema.job_type,
                "required_fields_count": len(schema.required_fields),
                "optional_fields_count": len(schema.optional_fields),
                "usage_frequency": schema.usage_frequency,
                "confidence_score": schema.confidence_score,
                "created_at": schema.created_at,
                "updated_at": schema.updated_at
            }

            # Store in ChromaDB
            self.schema_collection.add(
                ids=[schema.schema_id],
                embeddings=[embedding],
                documents=[schema_description],
                metadatas=[metadata]
            )

            # Store detailed schema data as JSON
            schema_data = {
                "schema": schema.__dict__,
                "description": schema_description
            }

            # Cache the schema
            self.schema_cache[schema.schema_id] = schema

            logger.info(f"✅ Stored stream schema: {schema.schema_id} ({schema.job_type})")
            return True

        except Exception as e:
            logger.error(f"❌ Error storing stream schema {schema.schema_id}: {str(e)}")
            return False

    async def find_similar_schemas(self, query_description: str, job_type: str = None, limit: int = 5) -> List[Tuple[StreamSchema, float]]:
        """
        Find similar schemas based on description

        Args:
            query_description: Natural language description of desired stream
            job_type: Optional job type filter
            limit: Maximum number of results

        Returns:
            List of (schema, similarity_score) tuples
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query_description).tolist()

            # Build where clause for job_type filter
            where_clause = {}
            if job_type:
                where_clause["job_type"] = job_type

            # Search in ChromaDB
            results = self.schema_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None
            )

            similar_schemas = []

            if results['ids'] and results['ids'][0]:
                for i, schema_id in enumerate(results['ids'][0]):
                    similarity_score = 1.0 - results['distances'][0][i]  # Convert distance to similarity

                    # Get schema from cache or reconstruct
                    schema = await self._get_schema_by_id(schema_id)
                    if schema:
                        similar_schemas.append((schema, similarity_score))

            logger.info(f"🔍 Found {len(similar_schemas)} similar schemas for: {query_description[:50]}...")
            return similar_schemas

        except Exception as e:
            logger.error(f"❌ Error finding similar schemas: {str(e)}")
            return []

    async def learn_from_stream_data(self, stream_data: List[Dict[str, Any]]) -> List[StreamSchema]:
        """
        Learn schemas from existing stream data

        Args:
            stream_data: List of stream dictionaries from SupabaseStreamLoader

        Returns:
            List of learned schemas
        """
        logger.info(f"🧠 Learning schemas from {len(stream_data)} streams...")

        learned_schemas = []
        job_type_groups = {}

        # Group streams by job type
        for stream in stream_data:
            job_type = stream.get('job_type', 'unknown')
            if job_type not in job_type_groups:
                job_type_groups[job_type] = []
            job_type_groups[job_type].append(stream)

        # Learn schema for each job type
        for job_type, streams in job_type_groups.items():
            if len(streams) < 1:  # Need at least 1 stream to learn
                continue

            schema = await self._extract_schema_from_streams(job_type, streams)
            if schema:
                learned_schemas.append(schema)
                await self.store_stream_schema(schema)

        logger.info(f"✅ Learned {len(learned_schemas)} schemas")
        return learned_schemas

    async def get_schema_suggestions(self, partial_data: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """
        Get schema suggestions based on partial data and context

        Args:
            partial_data: Partially filled stream data
            context: Additional context from conversation

        Returns:
            Dictionary with suggestions and confidence scores
        """
        try:
            # Analyze partial data to infer job type
            inferred_job_type = self._infer_job_type_from_partial_data(partial_data)

            # Create query description from partial data and context
            query_description = self._create_query_from_partial_data(partial_data, context)

            # Find similar schemas
            similar_schemas = await self.find_similar_schemas(
                query_description, inferred_job_type, limit=3
            )

            if not similar_schemas:
                return {"suggestions": [], "confidence": 0.0}

            # Generate suggestions from best matching schema
            best_schema, best_score = similar_schemas[0]
            suggestions = self._generate_suggestions_from_schema(best_schema, partial_data)

            return {
                "job_type": best_schema.job_type,
                "suggestions": suggestions,
                "confidence": best_score,
                "matching_schemas": len(similar_schemas),
                "schema_id": best_schema.schema_id
            }

        except Exception as e:
            logger.error(f"❌ Error getting schema suggestions: {str(e)}")
            return {"suggestions": [], "confidence": 0.0, "error": str(e)}

    async def update_schema_usage(self, schema_id: str, success: bool = True):
        """Update schema usage statistics"""
        try:
            schema = await self._get_schema_by_id(schema_id)
            if not schema:
                return

            # Update usage frequency and confidence
            if success:
                schema.usage_frequency += 0.1
                schema.confidence_score = min(1.0, schema.confidence_score + 0.05)
            else:
                schema.usage_frequency = max(0.0, schema.usage_frequency - 0.05)
                schema.confidence_score = max(0.0, schema.confidence_score - 0.02)

            schema.updated_at = datetime.now().isoformat()

            # Re-store updated schema
            await self.store_stream_schema(schema)

            logger.info(f"📊 Updated schema usage: {schema_id} (success: {success})")

        except Exception as e:
            logger.error(f"❌ Error updating schema usage: {str(e)}")

    def _create_schema_description(self, schema: StreamSchema) -> str:
        """Create natural language description of schema"""
        parts = [f"{schema.job_type} job"]

        if schema.required_fields:
            required_fields_str = ", ".join(schema.required_fields)
            parts.append(f"requires: {required_fields_str}")

        if schema.optional_fields:
            optional_fields_str = ", ".join(schema.optional_fields[:5])  # Limit for readability
            parts.append(f"optional: {optional_fields_str}")

        return " | ".join(parts)

    async def _extract_schema_from_streams(self, job_type: str, streams: List[Dict[str, Any]]) -> Optional[StreamSchema]:
        """Extract schema from a group of streams of the same job type"""
        try:
            required_fields = set()
            optional_fields = set()
            field_patterns = {}
            validation_rules = {}
            source_stream_ids = []

            for stream in streams:
                source_stream_ids.append(str(stream.get('id', '')))
                wizard_data = stream.get('wizard_data', {})

                if not wizard_data:
                    continue

                # Analyze wizard_data structure
                for section, params in wizard_data.items():
                    if not isinstance(params, dict):
                        continue

                    for param_name, param_value in params.items():
                        param_path = f"{section}.{param_name}"

                        # Track field patterns
                        if param_path not in field_patterns:
                            field_patterns[param_path] = {
                                'values': [],
                                'types': set(),
                                'frequency': 0
                            }

                        field_patterns[param_path]['frequency'] += 1

                        if param_value is not None and str(param_value).strip():
                            required_fields.add(param_path)
                            field_patterns[param_path]['values'].append(param_value)
                            field_patterns[param_path]['types'].add(type(param_value).__name__)
                        else:
                            optional_fields.add(param_path)

            # Determine truly required fields (appear in >70% of streams)
            stream_count = len(streams)
            truly_required = set()
            truly_optional = set()

            for field in required_fields:
                frequency = field_patterns[field]['frequency'] / stream_count
                if frequency >= 0.7:
                    truly_required.add(field)
                else:
                    truly_optional.add(field)

            truly_optional.update(optional_fields)

            # Calculate usage frequency and confidence
            usage_frequency = min(1.0, stream_count / 10.0)  # More streams = higher frequency
            confidence_score = min(1.0, stream_count / 5.0)   # 5+ streams = full confidence

            schema = StreamSchema(
                schema_id=f"{job_type}_{hash(frozenset(truly_required))}"[:16],
                job_type=job_type,
                required_fields=list(truly_required),
                optional_fields=list(truly_optional),
                field_patterns=field_patterns,
                validation_rules=validation_rules,
                usage_frequency=usage_frequency,
                confidence_score=confidence_score,
                source_stream_ids=source_stream_ids,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )

            logger.info(f"📋 Extracted schema for {job_type}: {len(truly_required)} required, {len(truly_optional)} optional fields")
            return schema

        except Exception as e:
            logger.error(f"❌ Error extracting schema for {job_type}: {str(e)}")
            return None

    def _infer_job_type_from_partial_data(self, partial_data: Dict[str, Any]) -> Optional[str]:
        """Infer job type from partial data"""
        # Check for SAP-specific indicators
        job_form = partial_data.get('jobForm', {})

        if job_form.get('sapSystem') or job_form.get('reportName'):
            return 'sap'

        if job_form.get('sourcePath') or job_form.get('targetPath'):
            return 'file_transfer'

        if job_form.get('scriptPath') or job_form.get('agentName'):
            return 'standard'

        return None

    def _create_query_from_partial_data(self, partial_data: Dict[str, Any], context: str) -> str:
        """Create search query from partial data and context"""
        parts = []

        # Add context first
        if context:
            parts.append(context)

        # Add job form details
        job_form = partial_data.get('jobForm', {})
        for key, value in job_form.items():
            if value:
                parts.append(f"{key}: {value}")

        # Add stream properties
        stream_props = partial_data.get('streamProperties', {})
        for key, value in stream_props.items():
            if value:
                parts.append(f"{key}: {value}")

        return " | ".join(parts) if parts else "general stream configuration"

    def _generate_suggestions_from_schema(self, schema: StreamSchema, partial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate field suggestions from schema"""
        suggestions = []

        # Get current fields
        current_fields = set()
        for section, params in partial_data.items():
            if isinstance(params, dict):
                for param in params.keys():
                    current_fields.add(f"{section}.{param}")

        # Suggest missing required fields
        for field in schema.required_fields:
            if field not in current_fields:
                field_pattern = schema.field_patterns.get(field, {})
                common_values = field_pattern.get('values', [])

                suggestion = {
                    'field': field,
                    'type': 'required',
                    'priority': 'high',
                    'description': f"Required field for {schema.job_type} jobs",
                    'examples': common_values[:3] if common_values else []
                }
                suggestions.append(suggestion)

        # Suggest optional fields with high frequency
        for field in schema.optional_fields:
            if field not in current_fields:
                field_pattern = schema.field_patterns.get(field, {})
                frequency = field_pattern.get('frequency', 0)

                if frequency >= 3:  # Suggest if used in 3+ streams
                    suggestion = {
                        'field': field,
                        'type': 'optional',
                        'priority': 'medium',
                        'description': f"Commonly used in {schema.job_type} jobs",
                        'examples': field_pattern.get('values', [])[:3]
                    }
                    suggestions.append(suggestion)

        return suggestions

    async def _get_schema_by_id(self, schema_id: str) -> Optional[StreamSchema]:
        """Get schema by ID from cache or storage"""
        # Check cache first
        if schema_id in self.schema_cache:
            return self.schema_cache[schema_id]

        try:
            # Query ChromaDB
            results = self.schema_collection.get(
                ids=[schema_id],
                include=['metadatas', 'documents']
            )

            if results['ids'] and results['metadatas']:
                metadata = results['metadatas'][0]

                # Reconstruct schema from metadata (simplified version)
                schema = StreamSchema(
                    schema_id=schema_id,
                    job_type=metadata['job_type'],
                    required_fields=[],  # Would need to store separately for full reconstruction
                    optional_fields=[],
                    field_patterns={},
                    validation_rules={},
                    usage_frequency=metadata['usage_frequency'],
                    confidence_score=metadata['confidence_score'],
                    source_stream_ids=[],
                    created_at=metadata['created_at'],
                    updated_at=metadata['updated_at']
                )

                # Cache it
                self.schema_cache[schema_id] = schema
                return schema

        except Exception as e:
            logger.error(f"❌ Error getting schema {schema_id}: {str(e)}")

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            schema_count = self.schema_collection.count()
            field_patterns_count = self.field_patterns_collection.count()

            return {
                "total_schemas": schema_count,
                "total_field_patterns": field_patterns_count,
                "cached_schemas": len(self.schema_cache),
                "cached_patterns": len(self.pattern_cache),
                "embedding_model": "all-MiniLM-L6-v2"
            }
        except Exception as e:
            logger.error(f"❌ Error getting vector store stats: {str(e)}")
            return {"error": str(e)}

# Global instance
_stream_schema_vector_store = None

def get_stream_schema_vector_store() -> StreamSchemaVectorStore:
    """Get global stream schema vector store instance"""
    global _stream_schema_vector_store
    if _stream_schema_vector_store is None:
        _stream_schema_vector_store = StreamSchemaVectorStore()
    return _stream_schema_vector_store