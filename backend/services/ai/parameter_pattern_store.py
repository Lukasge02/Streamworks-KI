"""
Parameter Pattern Store for Enterprise AI Parameter Recognition
Recognizes and stores successful parameter extraction patterns
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import spacy
from sentence_transformers import SentenceTransformer

from .chroma_manager import get_chroma_manager

logger = logging.getLogger(__name__)

@dataclass
class ParameterPattern:
    """Represents a learned parameter extraction pattern"""
    pattern_id: str
    parameter_name: str
    parameter_type: str  # 'sap_system', 'report_name', 'file_path', 'time', etc.
    extraction_patterns: List[Dict[str, Any]]  # NLP patterns for extraction
    validation_rules: Dict[str, Any]
    confidence_score: float
    success_rate: float
    usage_count: int
    examples: List[Dict[str, Any]]  # Successful extractions
    created_at: str
    updated_at: str

@dataclass
class ExtractionRule:
    """Rule for extracting a specific parameter"""
    rule_type: str  # 'regex', 'nlp', 'keyword', 'semantic'
    pattern: str
    weight: float
    context_keywords: List[str]
    validation_callback: Optional[str]

@dataclass
class ExtractionResult:
    """Result of parameter extraction"""
    parameter_name: str
    extracted_value: Any
    confidence: float
    extraction_method: str
    context: str

class ParameterPatternStore:
    """
    Stores and manages parameter extraction patterns

    Features:
    - Pattern learning from successful extractions
    - Multi-method parameter extraction (regex, NLP, semantic)
    - Context-aware pattern matching
    - Dynamic pattern improvement
    """

    def __init__(self):
        self.chroma_manager = get_chroma_manager()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Load spaCy model for NLP
        try:
            self.nlp = spacy.load("de_core_news_sm")
        except OSError:
            logger.warning("German spaCy model not found, using English model")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.error("No spaCy model found! Install with: python -m spacy download de_core_news_sm")
                self.nlp = None

        # Get ChromaDB collections
        self.patterns_collection = self.chroma_manager.get_collection(
            "parameter_patterns", "extraction_patterns"
        )
        self.examples_collection = self.chroma_manager.get_collection(
            "parameter_patterns", "successful_extractions"
        )

        # Pattern cache
        self.pattern_cache = {}
        self.extraction_rules_cache = {}

        # Built-in extraction patterns
        self.builtin_patterns = self._initialize_builtin_patterns()

    def _initialize_builtin_patterns(self) -> Dict[str, List[ExtractionRule]]:
        """Initialize built-in extraction patterns"""
        patterns = {
            'sap_system': [
                ExtractionRule('regex', r'\b[A-Z]\d{2}\b', 0.9, ['sap', 'system'], None),
                ExtractionRule('keyword', r'system\s+([A-Z]\d{2})', 0.8, ['system'], None),
                ExtractionRule('nlp', 'SAP System', 0.7, ['sap'], None)
            ],
            'report_name': [
                ExtractionRule('regex', r'\bZ[A-Z0-9_]+\b', 0.9, ['report', 'programm'], None),
                ExtractionRule('keyword', r'report\s+([ZY][A-Z0-9_]+)', 0.8, ['report'], None),
                ExtractionRule('nlp', 'Report Name', 0.7, ['report'], None)
            ],
            'file_path': [
                ExtractionRule('regex', r'[A-Z]:[\\\/][\w\s\\\/\.]+', 0.8, ['pfad', 'datei', 'path'], None),
                ExtractionRule('regex', r'\/[\w\s\/\.]+', 0.7, ['pfad', 'path'], None),
                ExtractionRule('regex', r'\\\\[\w\s\\\.]+', 0.8, ['netzwerk', 'share'], None)
            ],
            'time': [
                ExtractionRule('regex', r'\b([01]?\d|2[0-3]):[0-5]\d\b', 0.9, ['zeit', 'uhr', 'time'], None),
                ExtractionRule('keyword', r'um\s+(\d{1,2}:\d{2})', 0.8, ['um'], None),
                ExtractionRule('nlp', 'Time', 0.7, ['zeit', 'uhr'], None)
            ],
            'frequency': [
                ExtractionRule('keyword', r'(täglich|wöchentlich|monatlich|daily|weekly|monthly)', 0.8, ['frequenz'], None),
                ExtractionRule('nlp', 'Frequency', 0.7, ['häufigkeit', 'frequenz'], None)
            ],
            'agent_name': [
                ExtractionRule('regex', r'\b[A-Z0-9_-]{4,20}\b', 0.6, ['agent', 'server'], None),
                ExtractionRule('keyword', r'agent\s+([A-Z0-9_-]+)', 0.8, ['agent'], None),
                ExtractionRule('nlp', 'Agent Name', 0.7, ['agent'], None)
            ]
        }
        return patterns

    async def store_extraction_pattern(self, pattern: ParameterPattern) -> bool:
        """
        Store a learned extraction pattern

        Args:
            pattern: ParameterPattern to store

        Returns:
            True if successful
        """
        try:
            # Create description for embedding
            pattern_description = self._create_pattern_description(pattern)

            # Generate embedding
            embedding = self.embedding_model.encode(pattern_description).tolist()

            # Prepare metadata
            metadata = {
                "pattern_id": pattern.pattern_id,
                "parameter_name": pattern.parameter_name,
                "parameter_type": pattern.parameter_type,
                "confidence_score": pattern.confidence_score,
                "success_rate": pattern.success_rate,
                "usage_count": pattern.usage_count,
                "created_at": pattern.created_at,
                "updated_at": pattern.updated_at
            }

            # Store in ChromaDB
            self.patterns_collection.add(
                ids=[pattern.pattern_id],
                embeddings=[embedding],
                documents=[pattern_description],
                metadatas=[metadata]
            )

            # Cache the pattern
            self.pattern_cache[pattern.pattern_id] = pattern

            logger.info(f"✅ Stored extraction pattern: {pattern.pattern_id} ({pattern.parameter_name})")
            return True

        except Exception as e:
            logger.error(f"❌ Error storing extraction pattern: {str(e)}")
            return False

    async def extract_parameters(self, text: str, context: Dict[str, Any] = None) -> List[ExtractionResult]:
        """
        Extract parameters from text using learned patterns

        Args:
            text: Input text to extract from
            context: Additional context (job_type, etc.)

        Returns:
            List of extraction results
        """
        try:
            logger.info(f"🔍 Extracting parameters from: {text[:50]}...")

            results = []
            text_lower = text.lower()

            # Apply built-in patterns first
            for param_type, rules in self.builtin_patterns.items():
                extractions = await self._apply_extraction_rules(text, rules, param_type, context)
                results.extend(extractions)

            # Apply learned patterns
            learned_patterns = await self._get_relevant_patterns(text, context)
            for pattern in learned_patterns:
                extractions = await self._apply_learned_pattern(text, pattern, context)
                results.extend(extractions)

            # Deduplicate and rank results
            results = self._deduplicate_results(results)

            logger.info(f"✅ Extracted {len(results)} parameters")
            return results

        except Exception as e:
            logger.error(f"❌ Error extracting parameters: {str(e)}")
            return []

    async def learn_from_successful_extraction(self, text: str, extracted_params: Dict[str, Any], context: Dict[str, Any] = None):
        """
        Learn from a successful parameter extraction

        Args:
            text: Original text
            extracted_params: Successfully extracted parameters
            context: Extraction context
        """
        try:
            logger.info(f"🧠 Learning from successful extraction: {len(extracted_params)} params")

            for param_name, param_value in extracted_params.items():
                if not param_value:
                    continue

                # Store successful extraction example
                example = {
                    "text": text,
                    "parameter_name": param_name,
                    "extracted_value": param_value,
                    "context": context or {},
                    "timestamp": datetime.now().isoformat()
                }

                await self._store_successful_example(example)

                # Analyze and improve patterns for this parameter
                await self._improve_pattern_for_parameter(param_name, text, param_value, context)

        except Exception as e:
            logger.error(f"❌ Error learning from extraction: {str(e)}")

    async def _apply_extraction_rules(self, text: str, rules: List[ExtractionRule], param_type: str, context: Dict[str, Any]) -> List[ExtractionResult]:
        """Apply extraction rules to text"""
        results = []

        for rule in rules:
            try:
                if rule.rule_type == 'regex':
                    matches = re.finditer(rule.pattern, text, re.IGNORECASE)
                    for match in matches:
                        value = match.group(1) if match.groups() else match.group(0)
                        confidence = rule.weight * self._calculate_context_boost(text, rule.context_keywords)

                        results.append(ExtractionResult(
                            parameter_name=param_type,
                            extracted_value=value.strip(),
                            confidence=confidence,
                            extraction_method=f'regex:{rule.pattern}',
                            context=text[max(0, match.start()-20):match.end()+20]
                        ))

                elif rule.rule_type == 'keyword':
                    matches = re.finditer(rule.pattern, text, re.IGNORECASE)
                    for match in matches:
                        value = match.group(1) if match.groups() else match.group(0)
                        confidence = rule.weight * self._calculate_context_boost(text, rule.context_keywords)

                        results.append(ExtractionResult(
                            parameter_name=param_type,
                            extracted_value=value.strip(),
                            confidence=confidence,
                            extraction_method=f'keyword:{rule.pattern}',
                            context=text[max(0, match.start()-20):match.end()+20]
                        ))

                elif rule.rule_type == 'nlp' and self.nlp:
                    nlp_results = await self._apply_nlp_extraction(text, rule, param_type)
                    results.extend(nlp_results)

            except Exception as e:
                logger.warning(f"Error applying rule {rule.pattern}: {str(e)}")
                continue

        return results

    async def _apply_nlp_extraction(self, text: str, rule: ExtractionRule, param_type: str) -> List[ExtractionResult]:
        """Apply NLP-based extraction"""
        results = []

        if not self.nlp:
            return results

        try:
            doc = self.nlp(text)

            # Extract entities
            for ent in doc.ents:
                if param_type == 'sap_system' and ent.label_ in ['ORG', 'PRODUCT']:
                    if re.match(r'^[A-Z]\d{2}$', ent.text):
                        results.append(ExtractionResult(
                            parameter_name=param_type,
                            extracted_value=ent.text,
                            confidence=rule.weight,
                            extraction_method='nlp:entity',
                            context=ent.sent.text
                        ))

                elif param_type == 'time' and ent.label_ == 'TIME':
                    results.append(ExtractionResult(
                        parameter_name=param_type,
                        extracted_value=ent.text,
                        confidence=rule.weight,
                        extraction_method='nlp:entity',
                        context=ent.sent.text
                    ))

            # Extract based on dependency parsing
            for token in doc:
                if param_type == 'report_name' and token.pos_ == 'NOUN':
                    if token.text.startswith('Z') and len(token.text) > 3:
                        results.append(ExtractionResult(
                            parameter_name=param_type,
                            extracted_value=token.text,
                            confidence=rule.weight * 0.8,
                            extraction_method='nlp:pos',
                            context=token.sent.text
                        ))

        except Exception as e:
            logger.warning(f"NLP extraction error: {str(e)}")

        return results

    def _calculate_context_boost(self, text: str, context_keywords: List[str]) -> float:
        """Calculate confidence boost based on context keywords"""
        if not context_keywords:
            return 1.0

        text_lower = text.lower()
        found_keywords = sum(1 for keyword in context_keywords if keyword in text_lower)

        if found_keywords == 0:
            return 0.5  # Reduce confidence if no context keywords found

        return min(1.5, 1.0 + (found_keywords * 0.1))

    def _deduplicate_results(self, results: List[ExtractionResult]) -> List[ExtractionResult]:
        """Remove duplicate extraction results"""
        seen = {}
        deduplicated = []

        for result in results:
            key = f"{result.parameter_name}:{result.extracted_value}"

            if key not in seen or result.confidence > seen[key].confidence:
                seen[key] = result

        return list(seen.values())

    async def _get_relevant_patterns(self, text: str, context: Dict[str, Any]) -> List[ParameterPattern]:
        """Get relevant learned patterns for the text"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(text).tolist()

            # Search for relevant patterns
            results = self.patterns_collection.query(
                query_embeddings=[query_embedding],
                n_results=10
            )

            patterns = []
            if results['ids'] and results['ids'][0]:
                for pattern_id in results['ids'][0]:
                    pattern = await self._get_pattern_by_id(pattern_id)
                    if pattern:
                        patterns.append(pattern)

            return patterns

        except Exception as e:
            logger.error(f"Error getting relevant patterns: {str(e)}")
            return []

    async def _apply_learned_pattern(self, text: str, pattern: ParameterPattern, context: Dict[str, Any]) -> List[ExtractionResult]:
        """Apply a learned pattern to text"""
        results = []

        try:
            for extraction_pattern in pattern.extraction_patterns:
                rule_type = extraction_pattern.get('type', 'regex')
                rule_pattern = extraction_pattern.get('pattern', '')

                if rule_type == 'regex' and rule_pattern:
                    matches = re.finditer(rule_pattern, text, re.IGNORECASE)
                    for match in matches:
                        value = match.group(1) if match.groups() else match.group(0)
                        confidence = pattern.confidence_score * pattern.success_rate

                        results.append(ExtractionResult(
                            parameter_name=pattern.parameter_name,
                            extracted_value=value.strip(),
                            confidence=confidence,
                            extraction_method=f'learned:{pattern.pattern_id}',
                            context=text[max(0, match.start()-20):match.end()+20]
                        ))

        except Exception as e:
            logger.warning(f"Error applying learned pattern {pattern.pattern_id}: {str(e)}")

        return results

    async def _store_successful_example(self, example: Dict[str, Any]):
        """Store a successful extraction example"""
        try:
            example_id = f"{example['parameter_name']}_{hash(example['text'])}"[:32]

            # Create embedding
            text_for_embedding = f"{example['parameter_name']}: {example['text']}"
            embedding = self.embedding_model.encode(text_for_embedding).tolist()

            # Store in ChromaDB
            self.examples_collection.add(
                ids=[example_id],
                embeddings=[embedding],
                documents=[example['text']],
                metadatas={
                    "parameter_name": example['parameter_name'],
                    "extracted_value": str(example['extracted_value']),
                    "timestamp": example['timestamp']
                }
            )

        except Exception as e:
            logger.error(f"Error storing successful example: {str(e)}")

    async def _improve_pattern_for_parameter(self, param_name: str, text: str, value: Any, context: Dict[str, Any]):
        """Improve extraction patterns for a specific parameter"""
        try:
            # Find existing pattern or create new one
            pattern_id = f"{param_name}_learned"
            pattern = await self._get_pattern_by_id(pattern_id)

            if not pattern:
                # Create new pattern
                pattern = ParameterPattern(
                    pattern_id=pattern_id,
                    parameter_name=param_name,
                    parameter_type=param_name,
                    extraction_patterns=[],
                    validation_rules={},
                    confidence_score=0.7,
                    success_rate=1.0,
                    usage_count=1,
                    examples=[],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
            else:
                pattern.usage_count += 1
                pattern.updated_at = datetime.now().isoformat()

            # Add example
            example = {
                "text": text,
                "value": value,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            pattern.examples.append(example)

            # Generate new extraction pattern if enough examples
            if len(pattern.examples) >= 3:
                new_patterns = self._generate_patterns_from_examples(pattern.examples, param_name)
                pattern.extraction_patterns.extend(new_patterns)

            # Update success rate
            pattern.success_rate = min(1.0, pattern.success_rate + 0.05)

            # Store updated pattern
            await self.store_extraction_pattern(pattern)

        except Exception as e:
            logger.error(f"Error improving pattern for {param_name}: {str(e)}")

    def _generate_patterns_from_examples(self, examples: List[Dict[str, Any]], param_name: str) -> List[Dict[str, Any]]:
        """Generate extraction patterns from successful examples"""
        patterns = []

        try:
            # Extract common regex patterns
            values = [str(example['value']) for example in examples]

            # Find common patterns in values
            if param_name == 'sap_system':
                # Check if all values match SAP system pattern
                if all(re.match(r'^[A-Z]\d{2}$', value) for value in values):
                    patterns.append({
                        'type': 'regex',
                        'pattern': r'\b[A-Z]\d{2}\b',
                        'weight': 0.9
                    })

            elif param_name == 'report_name':
                # Check if all values match report pattern
                if all(value.startswith(('Z', 'Y')) for value in values):
                    patterns.append({
                        'type': 'regex',
                        'pattern': r'\b[ZY][A-Z0-9_]+\b',
                        'weight': 0.9
                    })

            elif param_name == 'time':
                # Check if all values match time pattern
                if all(re.match(r'^\d{1,2}:\d{2}$', value) for value in values):
                    patterns.append({
                        'type': 'regex',
                        'pattern': r'\b\d{1,2}:\d{2}\b',
                        'weight': 0.9
                    })

        except Exception as e:
            logger.error(f"Error generating patterns from examples: {str(e)}")

        return patterns

    async def _get_pattern_by_id(self, pattern_id: str) -> Optional[ParameterPattern]:
        """Get pattern by ID from cache or storage"""
        if pattern_id in self.pattern_cache:
            return self.pattern_cache[pattern_id]

        try:
            results = self.patterns_collection.get(
                ids=[pattern_id],
                include=['metadatas', 'documents']
            )

            if results['ids'] and results['metadatas']:
                metadata = results['metadatas'][0]

                # Reconstruct pattern (simplified)
                pattern = ParameterPattern(
                    pattern_id=pattern_id,
                    parameter_name=metadata['parameter_name'],
                    parameter_type=metadata['parameter_type'],
                    extraction_patterns=[],  # Would need separate storage for full reconstruction
                    validation_rules={},
                    confidence_score=metadata['confidence_score'],
                    success_rate=metadata['success_rate'],
                    usage_count=metadata['usage_count'],
                    examples=[],
                    created_at=metadata['created_at'],
                    updated_at=metadata['updated_at']
                )

                self.pattern_cache[pattern_id] = pattern
                return pattern

        except Exception as e:
            logger.error(f"Error getting pattern {pattern_id}: {str(e)}")

        return None

    def _create_pattern_description(self, pattern: ParameterPattern) -> str:
        """Create natural language description of pattern"""
        return f"{pattern.parameter_name} extraction pattern for {pattern.parameter_type} with {len(pattern.extraction_patterns)} rules"

    def get_stats(self) -> Dict[str, Any]:
        """Get pattern store statistics"""
        try:
            patterns_count = self.patterns_collection.count()
            examples_count = self.examples_collection.count()

            return {
                "total_patterns": patterns_count,
                "total_examples": examples_count,
                "cached_patterns": len(self.pattern_cache),
                "builtin_patterns": len(self.builtin_patterns),
                "embedding_model": "all-MiniLM-L6-v2",
                "nlp_model": "de_core_news_sm" if self.nlp else "none"
            }
        except Exception as e:
            logger.error(f"Error getting pattern store stats: {str(e)}")
            return {"error": str(e)}

# Global instance
_parameter_pattern_store = None

def get_parameter_pattern_store() -> ParameterPatternStore:
    """Get global parameter pattern store instance"""
    global _parameter_pattern_store
    if _parameter_pattern_store is None:
        _parameter_pattern_store = ParameterPatternStore()
    return _parameter_pattern_store