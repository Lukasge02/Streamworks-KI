"""
Adaptive Retrieval System für StreamWorks RAG
Query-spezifische Threshold-Anpassung und Context-Window-Expansion
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Query types für spezifische Behandlung"""
    WHAT_IS = "what_is"          # "Was ist X?"
    HOW_DOES = "how_does"        # "Wie funktioniert X?"  
    WHERE_IS = "where_is"        # "Wo ist X?"
    WHY = "why"                  # "Warum X?"
    WHO_IS = "who_is"           # "Wer ist X?"
    DEFINITION = "definition"    # Definitionen
    COMPARISON = "comparison"    # Vergleiche
    PROCEDURE = "procedure"      # Anleitungen
    FACTUAL = "factual"         # Faktenfragen
    SHORT = "short"             # Kurze Queries (1-2 Wörter)
    COMPLEX = "complex"         # Komplexe Queries (>10 Wörter)
    GENERAL = "general"         # Allgemeine Queries


@dataclass
class QueryContext:
    """Kontext-Information für eine Query"""
    query: str
    query_type: QueryType
    word_count: int
    has_question_words: bool
    complexity_score: float
    semantic_density: float
    language_confidence: float


@dataclass 
class AdaptiveThresholds:
    """Adaptive Threshold-Konfiguration"""
    high_quality: float
    good_quality: float  
    fallback: float
    min_results: int
    max_results: int
    context_expansion_trigger: float


class QueryAnalyzer:
    """Analysiert Queries für adaptive Retrieval-Strategien"""
    
    def __init__(self):
        self.german_patterns = self._setup_german_patterns()
        self.complexity_indicators = self._setup_complexity_indicators()
        
    def _setup_german_patterns(self) -> Dict[str, str]:
        """Setup deutsche Query-Patterns"""
        return {
            QueryType.WHAT_IS: r'\b(?:was ist|what is)\b',
            QueryType.HOW_DOES: r'\b(?:wie (?:funktioniert|arbeitet|läuft|geht)|how does|how to)\b',
            QueryType.WHERE_IS: r'\b(?:wo (?:ist|befindet sich|liegt)|where is)\b',
            QueryType.WHY: r'\b(?:warum|weshalb|wieso|why)\b',
            QueryType.WHO_IS: r'\b(?:wer ist|who is)\b',
            QueryType.DEFINITION: r'\b(?:definition|bedeutung|erklärung|define|explain)\b',
            QueryType.COMPARISON: r'\b(?:unterschied|vergleich|vs|versus|compare|difference)\b',
            QueryType.PROCEDURE: r'\b(?:anleitung|tutorial|schritt|how to|guide|manual)\b'
        }
    
    def _setup_complexity_indicators(self) -> Dict[str, float]:
        """Setup Complexity-Scoring-Indikatoren"""
        return {
            'technical_terms': 0.3,      # Technische Begriffe
            'multiple_concepts': 0.2,    # Mehrere Konzepte
            'conditional_logic': 0.4,    # Bedingte Logik (wenn, dann, etc.)
            'compound_sentences': 0.2,   # Zusammengesetzte Sätze
            'domain_specific': 0.3       # Domain-spezifische Begriffe
        }
    
    def analyze_query(self, query: str) -> QueryContext:
        """
        Comprehensive Query-Analyse für adaptive Retrieval
        
        Args:
            query: User query string
            
        Returns:
            QueryContext mit allen relevanten Metadaten
        """
        query_lower = query.lower().strip()
        word_count = len(query_lower.split())
        
        # Query-Type-Detection
        query_type = self._detect_query_type(query_lower, word_count)
        
        # Question-Word-Detection
        question_words = ['was', 'wie', 'wo', 'warum', 'wer', 'wann', 'welche', 'what', 'how', 'where', 'why', 'who', 'when', 'which']
        has_question_words = any(qw in query_lower for qw in question_words)
        
        # Complexity-Scoring
        complexity_score = self._calculate_complexity(query_lower, word_count)
        
        # Semantic-Density (Information pro Wort)
        semantic_density = self._calculate_semantic_density(query_lower, word_count)
        
        # Language-Confidence (Deutsch vs Englisch)
        language_confidence = self._estimate_language_confidence(query_lower)
        
        return QueryContext(
            query=query,
            query_type=query_type,
            word_count=word_count,
            has_question_words=has_question_words,
            complexity_score=complexity_score,
            semantic_density=semantic_density,
            language_confidence=language_confidence
        )
    
    def _detect_query_type(self, query_lower: str, word_count: int) -> QueryType:
        """Detect query type basierend auf Patterns"""
        
        # Short queries (1-2 words)
        if word_count <= 2:
            return QueryType.SHORT
            
        # Complex queries (>10 words)
        if word_count > 10:
            return QueryType.COMPLEX
        
        # Pattern-based detection
        for query_type, pattern in self.german_patterns.items():
            if re.search(pattern, query_lower, re.IGNORECASE):
                return query_type
        
        # Factual vs general heuristic
        factual_indicators = ['wert', 'anzahl', 'datum', 'zeit', 'preis', 'kosten', 'größe', 'menge']
        if any(indicator in query_lower for indicator in factual_indicators):
            return QueryType.FACTUAL
        
        return QueryType.GENERAL
    
    def _calculate_complexity(self, query_lower: str, word_count: int) -> float:
        """Calculate query complexity score (0-1)"""
        score = 0.0
        
        # Base complexity von Wortanzahl
        word_complexity = min(1.0, word_count / 20)  # Normiert auf 20 Wörter
        score += word_complexity * 0.3
        
        # Technische Begriffe
        technical_terms = ['api', 'interface', 'implementation', 'algorithm', 'architecture', 'service', 'module', 'component', 'streamworks']
        tech_score = sum(1 for term in technical_terms if term in query_lower) / len(technical_terms)
        score += tech_score * self.complexity_indicators['technical_terms']
        
        # Conditional Logic
        conditional_words = ['wenn', 'dann', 'falls', 'sofern', 'except', 'unless', 'provided', 'assuming']
        if any(word in query_lower for word in conditional_words):
            score += self.complexity_indicators['conditional_logic']
        
        # Compound sentences (Kommas, und, oder, etc.)
        compound_indicators = [',', ' und ', ' oder ', ' aber ', ' jedoch ', ' and ', ' or ', ' but ']
        compound_count = sum(1 for indicator in compound_indicators if indicator in query_lower)
        if compound_count > 0:
            score += min(0.2, compound_count * 0.1)
        
        return min(1.0, score)
    
    def _calculate_semantic_density(self, query_lower: str, word_count: int) -> float:
        """Calculate semantic information density"""
        if word_count == 0:
            return 0.0
            
        # Information-bearing words (exclude stop words)
        german_stop_words = {'der', 'die', 'das', 'und', 'oder', 'ist', 'sind', 'ein', 'eine', 'zu', 'von', 'mit', 'auf', 'für', 'in', 'an', 'bei'}
        english_stop_words = {'the', 'and', 'or', 'is', 'are', 'a', 'an', 'to', 'of', 'with', 'on', 'for', 'in', 'at', 'by'}
        all_stop_words = german_stop_words.union(english_stop_words)
        
        words = query_lower.split()
        meaningful_words = [w for w in words if w not in all_stop_words and len(w) > 2]
        
        # Density = meaningful words / total words
        density = len(meaningful_words) / word_count if word_count > 0 else 0
        
        # Bonus for technical/domain terms
        domain_terms = ['streamworks', 'workflow', 'automation', 'process', 'integration', 'module']
        domain_bonus = sum(1 for term in domain_terms if term in query_lower) * 0.1
        
        return min(1.0, density + domain_bonus)
    
    def _estimate_language_confidence(self, query_lower: str) -> float:
        """Estimate language confidence (1.0 = definitely German, 0.0 = definitely English)"""
        
        # German indicators
        german_indicators = ['ä', 'ö', 'ü', 'ß', 'ist', 'sind', 'der', 'die', 'das', 'wie', 'was', 'wo', 'warum']
        german_score = sum(1 for indicator in german_indicators if indicator in query_lower)
        
        # English indicators  
        english_indicators = ['the', 'and', 'what', 'how', 'where', 'why', 'is', 'are', 'this', 'that']
        english_score = sum(1 for indicator in english_indicators if indicator in query_lower)
        
        if german_score + english_score == 0:
            return 0.5  # Neutral
        
        return german_score / (german_score + english_score)


class AdaptiveThresholdManager:
    """Manages adaptive thresholds basierend auf Query-Context"""
    
    def __init__(self):
        self.base_thresholds = {
            'high_quality': 0.7,
            'good_quality': 0.3,
            'fallback': 0.15
        }
        
        self.query_type_adjustments = self._setup_query_adjustments()
        
    def _setup_query_adjustments(self) -> Dict[QueryType, Dict[str, float]]:
        """Setup query-type-specific threshold adjustments"""
        return {
            QueryType.SHORT: {
                'high_quality': -0.1,     # Niedrigere Standards für kurze Queries
                'good_quality': -0.05,
                'fallback': -0.02,
                'min_results': 3,
                'context_expansion': 0.4   # Frühere Context-Expansion
            },
            QueryType.COMPLEX: {
                'high_quality': +0.05,    # Höhere Standards für komplexe Queries 
                'good_quality': +0.02,
                'fallback': 0.0,
                'min_results': 5,
                'context_expansion': 0.5
            },
            QueryType.FACTUAL: {
                'high_quality': +0.1,     # Sehr hohe Standards für Fakten
                'good_quality': +0.05,
                'fallback': +0.02,
                'min_results': 2,
                'context_expansion': 0.6
            },
            QueryType.DEFINITION: {
                'high_quality': +0.05,    # Hohe Standards für Definitionen
                'good_quality': +0.02,
                'fallback': 0.0,
                'min_results': 3,
                'context_expansion': 0.45
            },
            QueryType.HOW_DOES: {
                'high_quality': +0.02,    # Leicht erhöhte Standards für Prozesse
                'good_quality': 0.0,
                'fallback': -0.01,
                'min_results': 4,
                'context_expansion': 0.4
            }
        }
    
    def get_adaptive_thresholds(self, query_context: QueryContext) -> AdaptiveThresholds:
        """
        Calculate adaptive thresholds basierend auf Query-Context
        
        Args:
            query_context: Analyzed query context
            
        Returns:
            AdaptiveThresholds mit optimierten Werten
        """
        
        # Start mit base thresholds
        thresholds = self.base_thresholds.copy()
        
        # Query-Type-Adjustments
        if query_context.query_type in self.query_type_adjustments:
            adjustments = self.query_type_adjustments[query_context.query_type]
            
            thresholds['high_quality'] += adjustments.get('high_quality', 0)
            thresholds['good_quality'] += adjustments.get('good_quality', 0)
            thresholds['fallback'] += adjustments.get('fallback', 0)
        
        # Complexity-based adjustments
        complexity_factor = query_context.complexity_score
        if complexity_factor > 0.7:  # High complexity
            thresholds['high_quality'] += 0.03
            thresholds['good_quality'] += 0.02
        elif complexity_factor < 0.3:  # Low complexity
            thresholds['high_quality'] -= 0.02
            thresholds['good_quality'] -= 0.01
        
        # Semantic density adjustments
        density_factor = query_context.semantic_density
        if density_factor > 0.8:  # High density
            thresholds['high_quality'] += 0.02
        elif density_factor < 0.4:  # Low density
            thresholds['good_quality'] -= 0.02
            thresholds['fallback'] -= 0.01
        
        # Ensure thresholds are in valid ranges
        thresholds['high_quality'] = max(0.5, min(0.9, thresholds['high_quality']))
        thresholds['good_quality'] = max(0.2, min(0.6, thresholds['good_quality']))  
        thresholds['fallback'] = max(0.05, min(0.3, thresholds['fallback']))
        
        # Result count settings
        min_results = self.query_type_adjustments.get(query_context.query_type, {}).get('min_results', 3)
        max_results = min(15, min_results * 3)  # Max is 3x min
        
        # Context expansion trigger
        context_trigger = self.query_type_adjustments.get(query_context.query_type, {}).get('context_expansion', 0.5)
        
        return AdaptiveThresholds(
            high_quality=thresholds['high_quality'],
            good_quality=thresholds['good_quality'],
            fallback=thresholds['fallback'],
            min_results=min_results,
            max_results=max_results,
            context_expansion_trigger=context_trigger
        )


class ContextExpansionService:
    """Service für intelligent context window expansion"""
    
    def __init__(self):
        self.expansion_strategies = {
            'neighbor_chunks': self._expand_with_neighbors,
            'document_context': self._expand_with_document_context,
            'semantic_similar': self._expand_with_semantic_similar,
            'progressive': self._expand_progressively
        }
    
    def expand_context(
        self,
        chunks: List[Dict[str, Any]],
        query_context: QueryContext,
        thresholds: AdaptiveThresholds,
        vectorstore_service: Any
    ) -> List[Dict[str, Any]]:
        """
        Expand context wenn similarity scores zu niedrig sind
        
        Args:
            chunks: Original retrieved chunks
            query_context: Query analysis results  
            thresholds: Adaptive thresholds
            vectorstore_service: Access to vectorstore for additional retrieval
            
        Returns:
            Expanded chunk list mit zusätzlichem Kontext
        """
        
        if not chunks:
            return chunks
        
        # Check wenn expansion nötig ist
        avg_score = np.mean([chunk.get('similarity_score', 0) for chunk in chunks])
        
        if avg_score >= thresholds.context_expansion_trigger:
            logger.debug("Context expansion not needed - sufficient similarity scores")
            return chunks
        
        logger.info(f"Triggering context expansion - avg score: {avg_score:.3f}, trigger: {thresholds.context_expansion_trigger}")
        
        # Select expansion strategy basierend auf query type
        if query_context.query_type == QueryType.SHORT:
            expanded = self._expand_progressively(chunks, query_context, vectorstore_service)
        elif query_context.query_type in [QueryType.COMPLEX, QueryType.DEFINITION]:
            expanded = self._expand_with_document_context(chunks, query_context, vectorstore_service)
        else:
            expanded = self._expand_with_neighbors(chunks, query_context, vectorstore_service)
        
        return expanded[:thresholds.max_results]  # Respect max results limit
    
    def _expand_with_neighbors(self, chunks: List[Dict], query_context: QueryContext, vectorstore: Any) -> List[Dict]:
        """Expand with neighboring chunks from same documents"""
        # Implementation would retrieve chunks before/after current chunks
        # For now, return original chunks (placeholder)
        logger.debug("Neighbor expansion strategy applied")
        return chunks
    
    def _expand_with_document_context(self, chunks: List[Dict], query_context: QueryContext, vectorstore: Any) -> List[Dict]:
        """Expand with chunks from same documents"""
        # Implementation would retrieve more chunks from same documents
        logger.debug("Document context expansion strategy applied") 
        return chunks
    
    def _expand_with_semantic_similar(self, chunks: List[Dict], query_context: QueryContext, vectorstore: Any) -> List[Dict]:
        """Expand with semantically similar chunks"""
        # Implementation would find semantically related chunks
        logger.debug("Semantic similarity expansion strategy applied")
        return chunks
    
    def _expand_progressively(self, chunks: List[Dict], query_context: QueryContext, vectorstore: Any) -> List[Dict]:
        """Progressive expansion mit mehreren Strategien"""
        # Implementation would try multiple expansion strategies
        logger.debug("Progressive expansion strategy applied")
        return chunks


class AdaptiveRetrievalService:
    """Main service für adaptive retrieval mit allen Komponenten"""
    
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.threshold_manager = AdaptiveThresholdManager()
        self.context_expander = ContextExpansionService()
        
        # Performance tracking
        self.metrics = {
            'total_queries': 0,
            'expansions_triggered': 0,
            'avg_improvement': 0.0,
            'query_type_distribution': {}
        }
    
    def retrieve_adaptively(
        self,
        query: str,
        initial_chunks: List[Dict[str, Any]],
        vectorstore_service: Any
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Main adaptive retrieval method
        
        Args:
            query: User query
            initial_chunks: Initially retrieved chunks
            vectorstore_service: Access to vectorstore
            
        Returns:
            Tuple of (improved_chunks, retrieval_metadata)
        """
        
        # Analyze query
        query_context = self.query_analyzer.analyze_query(query)
        
        # Get adaptive thresholds
        thresholds = self.threshold_manager.get_adaptive_thresholds(query_context)
        
        # Apply quality filtering mit adaptive thresholds
        high_quality = [c for c in initial_chunks if c.get('similarity_score', 0) >= thresholds.high_quality]
        good_quality = [c for c in initial_chunks if c.get('similarity_score', 0) >= thresholds.good_quality]
        fallback = [c for c in initial_chunks if c.get('similarity_score', 0) >= thresholds.fallback]
        
        # Select best tier that meets minimum results
        if len(high_quality) >= thresholds.min_results:
            selected_chunks = high_quality[:thresholds.max_results]
            quality_tier = "high"
        elif len(good_quality) >= thresholds.min_results:
            selected_chunks = good_quality[:thresholds.max_results]  
            quality_tier = "good"
        else:
            selected_chunks = fallback[:thresholds.max_results]
            quality_tier = "fallback"
        
        # Apply context expansion wenn nötig
        expanded_chunks = self.context_expander.expand_context(
            selected_chunks, query_context, thresholds, vectorstore_service
        )
        
        # Update metrics
        self._update_metrics(query_context, len(expanded_chunks) > len(selected_chunks))
        
        # Build metadata
        metadata = {
            'query_type': query_context.query_type.value,
            'complexity_score': query_context.complexity_score,
            'semantic_density': query_context.semantic_density,
            'quality_tier_used': quality_tier,
            'thresholds_used': {
                'high': thresholds.high_quality,
                'good': thresholds.good_quality,
                'fallback': thresholds.fallback
            },
            'context_expanded': len(expanded_chunks) > len(selected_chunks),
            'original_count': len(initial_chunks),
            'final_count': len(expanded_chunks)
        }
        
        logger.info(f"Adaptive retrieval: {query_context.query_type.value} query, {quality_tier} tier, {len(expanded_chunks)} final chunks")
        
        return expanded_chunks, metadata
    
    def _update_metrics(self, query_context: QueryContext, was_expanded: bool):
        """Update performance metrics"""
        self.metrics['total_queries'] += 1
        
        if was_expanded:
            self.metrics['expansions_triggered'] += 1
        
        # Track query type distribution
        qt = query_context.query_type.value
        self.metrics['query_type_distribution'][qt] = self.metrics['query_type_distribution'].get(qt, 0) + 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = self.metrics.copy()
        
        if metrics['total_queries'] > 0:
            metrics['expansion_rate'] = metrics['expansions_triggered'] / metrics['total_queries']
        else:
            metrics['expansion_rate'] = 0.0
        
        return metrics