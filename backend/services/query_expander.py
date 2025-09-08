"""
Query Expander - Multi-Query Generation for Enhanced Retrieval Coverage
Uses LLM to generate semantically diverse alternative queries
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config import settings

logger = logging.getLogger(__name__)

class ExpansionStrategy(Enum):
    """Query expansion strategies"""
    SEMANTIC = "semantic"          # Semantic alternatives
    REFORMULATION = "reformulation"  # Different phrasings
    PERSPECTIVE = "perspective"     # Different viewpoints
    SPECIFICITY = "specificity"     # More/less specific versions
    COMPREHENSIVE = "comprehensive" # All strategies combined
    SIMPLE = "simple"              # Simple fallback expansion

@dataclass
class ExpandedQuery:
    """Represents an expanded query variant"""
    original_query: str
    expanded_query: str
    strategy: str
    confidence: float
    query_type: str
    estimated_relevance: float

class QueryExpander:
    """
    Advanced Multi-Query Expansion System
    
    Features:
    - LLM-powered query generation with multiple strategies (if OpenAI available)
    - Simple rule-based fallback expansion
    - Query quality assessment and filtering
    - German/English bilingual support
    - Performance optimization with caching
    """
    
    def __init__(self, 
                 model_name: str = "gpt-4o-mini",
                 max_expansions: int = 4,
                 min_confidence: float = 0.7):
        """
        Initialize Query Expander
        
        Args:
            model_name: OpenAI model for query generation
            max_expansions: Maximum number of query variants
            min_confidence: Minimum confidence threshold
        """
        self.model_name = model_name
        self.max_expansions = max_expansions
        self.min_confidence = min_confidence
        
        # Initialize OpenAI client if available
        self.openai_client = None
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("🔍 QueryExpander initialized with OpenAI support")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
        else:
            logger.info("🔍 QueryExpander initialized with fallback mode (no OpenAI)")
        
        # Performance tracking
        self.expansion_stats = {
            'total_expansions': 0,
            'successful_expansions': 0,
            'avg_expansion_time': 0.0,
            'cache_hits': 0
        }
        
        # Simple query cache
        self.query_cache: Dict[str, List[ExpandedQuery]] = {}
        self.cache_max_size = 1000
    
    async def expand_query(
        self,
        query: str,
        strategy: ExpansionStrategy = ExpansionStrategy.COMPREHENSIVE,
        context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> List[ExpandedQuery]:
        """
        Generate expanded query variants
        
        Args:
            query: Original user query
            strategy: Expansion strategy to use
            context: Optional context information
            use_cache: Whether to use cached results
            
        Returns:
            List of ExpandedQuery objects
        """
        start_time = time.time()
        self.expansion_stats['total_expansions'] += 1
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(query, strategy)
            if use_cache and cache_key in self.query_cache:
                self.expansion_stats['cache_hits'] += 1
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return self.query_cache[cache_key]
            
            # Analyze query characteristics
            query_analysis = self._analyze_query(query, context)
            
            # Generate expansions based on available capabilities
            if self.openai_client and strategy != ExpansionStrategy.SIMPLE:
                expanded_queries = await self._llm_expansion(query, strategy, query_analysis)
            else:
                # Fallback to simple rule-based expansion
                expanded_queries = self._simple_expansion(query, query_analysis)
            
            # Filter and rank expansions
            filtered_queries = self._filter_and_rank_queries(expanded_queries)
            
            # Cache results
            if use_cache:
                self._cache_results(cache_key, filtered_queries)
            
            # Update performance stats
            expansion_time = time.time() - start_time
            self._update_performance_stats(expansion_time, len(filtered_queries) > 0)
            
            logger.info(f"Query expansion: '{query}' → {len(filtered_queries)} variants in {expansion_time:.3f}s")
            return filtered_queries
            
        except Exception as e:
            logger.error(f"Query expansion failed: {str(e)}")
            return []
    
    def _analyze_query(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze query characteristics for optimal expansion"""
        import re
        
        analysis = {
            'word_count': len(query.split()),
            'char_count': len(query),
            'language': 'de' if any(word in query.lower() for word in ['wie', 'was', 'warum', 'wo', 'wann']) else 'en',
            'is_question': query.strip().endswith('?') or any(q in query.lower() for q in ['wie', 'was', 'how', 'what', 'why']),
            'has_technical_terms': bool(re.search(r'\b(?:API|HTTP|SSL|JSON|XML|SQL)\b', query, re.I)),
            'has_quotes': '"' in query,
            'has_numbers': bool(re.search(r'\d+', query)),
            'complexity': 'simple' if len(query.split()) <= 5 else 'complex',
            'query_type': self._classify_query_type(query),
            'context': context or {}
        }
        
        return analysis
    
    def _classify_query_type(self, query: str) -> str:
        """Classify query type for targeted expansion"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['wie', 'how']):
            return 'how_to'
        elif any(word in query_lower for word in ['was', 'what']):
            return 'definition'
        elif any(word in query_lower for word in ['warum', 'why']):
            return 'explanation'
        elif any(word in query_lower for word in ['unterschied', 'vergleich', 'vs', 'difference', 'compare']):
            return 'comparison'
        elif any(word in query_lower for word in ['problem', 'fehler', 'error', 'bug']):
            return 'troubleshooting'
        else:
            return 'general'
    
    async def _llm_expansion(self, query: str, strategy: ExpansionStrategy, analysis: Dict[str, Any]) -> List[ExpandedQuery]:
        """Generate expansions using LLM (OpenAI)"""
        if not self.openai_client:
            return []
        
        language = analysis['language']
        query_type = analysis['query_type']
        
        # Create expansion prompt
        system_prompt = f"""
Du bist ein Experte für Suchmaschinenoptimierung. Generiere alternative Suchquerys, die semantisch ähnlich sind, aber verschiedene Aspekte und Formulierungen abdecken.

Sprache: {language}
Query-Typ: {query_type}

Generiere 2-3 alternative Queries, die:
1. Verschiedene Synonyme und Formulierungen nutzen
2. Spezifischere oder allgemeinere Begriffe verwenden
3. Verschiedene Perspektiven oder Aspekte beleuchten

Antworte nur mit einem JSON-Array:
{{"queries": [{{"query": "alternative query", "confidence": 0.8}}]}}
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: \"{query}\""}
                ],
                temperature=0.7,
                max_tokens=400,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse response
            expanded_queries = []
            for item in result.get('queries', []):
                if isinstance(item, dict) and 'query' in item:
                    expanded_query = ExpandedQuery(
                        original_query=query,
                        expanded_query=item['query'].strip(),
                        strategy=strategy.value,
                        confidence=float(item.get('confidence', 0.8)),
                        query_type=query_type,
                        estimated_relevance=0.8
                    )
                    expanded_queries.append(expanded_query)
            
            return expanded_queries
            
        except Exception as e:
            logger.error(f"LLM expansion failed: {str(e)}")
            return []
    
    def _simple_expansion(self, query: str, analysis: Dict[str, Any]) -> List[ExpandedQuery]:
        """Simple rule-based query expansion as fallback"""
        expanded_queries = []
        query_type = analysis['query_type']
        
        # Simple synonym replacement patterns
        synonym_patterns = {
            'de': {
                'problem': ['schwierigkeit', 'issue', 'fehler'],
                'lösung': ['antwort', 'hilfe', 'fix'],
                'wie': ['auf welche weise', 'wodurch'],
                'was': ['welche', 'was für'],
                'warum': ['weshalb', 'wieso']
            },
            'en': {
                'problem': ['issue', 'difficulty', 'trouble'],
                'solution': ['answer', 'fix', 'resolution'],
                'how': ['in what way', 'by what means'],
                'what': ['which', 'what kind of'],
                'why': ['for what reason', 'how come']
            }
        }
        
        language = analysis['language']
        patterns = synonym_patterns.get(language, synonym_patterns['en'])
        
        # Generate simple variations
        variations = []
        query_words = query.lower().split()
        
        for word, synonyms in patterns.items():
            if word in query_words:
                for synonym in synonyms[:2]:  # Use first 2 synonyms
                    new_query = query.replace(word, synonym)
                    if new_query != query:
                        variations.append(new_query)
        
        # Add question variations
        if not analysis['is_question'] and analysis['query_type'] in ['definition', 'explanation']:
            if language == 'de':
                variations.append(f"Was ist {query}?")
                variations.append(f"Wie funktioniert {query}?")
            else:
                variations.append(f"What is {query}?")
                variations.append(f"How does {query} work?")
        
        # Convert to ExpandedQuery objects
        for i, variation in enumerate(variations[:3]):  # Limit to 3 variations
            expanded_query = ExpandedQuery(
                original_query=query,
                expanded_query=variation,
                strategy="simple",
                confidence=0.6,  # Lower confidence for rule-based
                query_type=query_type,
                estimated_relevance=0.7
            )
            expanded_queries.append(expanded_query)
        
        return expanded_queries
    
    def _filter_and_rank_queries(self, queries: List[ExpandedQuery]) -> List[ExpandedQuery]:
        """Filter and rank expanded queries by quality"""
        if not queries:
            return []
        
        # Filter by confidence threshold and basic quality checks
        filtered = [
            q for q in queries 
            if q.confidence >= (self.min_confidence - 0.2) and  # More lenient for fallback
               q.expanded_query.strip() and
               q.expanded_query != q.original_query and
               len(q.expanded_query.split()) >= 2
        ]
        
        # Remove duplicates (case-insensitive)
        seen_queries = set()
        deduplicated = []
        
        for query in filtered:
            query_normalized = query.expanded_query.lower().strip()
            if query_normalized not in seen_queries:
                seen_queries.add(query_normalized)
                deduplicated.append(query)
        
        # Sort by confidence * estimated_relevance
        deduplicated.sort(
            key=lambda q: q.confidence * q.estimated_relevance,
            reverse=True
        )
        
        # Return top results
        return deduplicated[:self.max_expansions]
    
    def _get_cache_key(self, query: str, strategy: ExpansionStrategy) -> str:
        """Generate cache key for query + strategy"""
        import hashlib
        content = f"{query.strip().lower()}_{strategy.value}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _cache_results(self, cache_key: str, results: List[ExpandedQuery]):
        """Cache expansion results"""
        if len(self.query_cache) >= self.cache_max_size:
            # Remove oldest entry (simple LRU)
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
        
        self.query_cache[cache_key] = results
    
    def _update_performance_stats(self, expansion_time: float, success: bool):
        """Update performance statistics"""
        if success:
            self.expansion_stats['successful_expansions'] += 1
        
        total_expansions = self.expansion_stats['total_expansions']
        old_avg = self.expansion_stats['avg_expansion_time']
        
        # Update running average
        self.expansion_stats['avg_expansion_time'] = (
            (old_avg * (total_expansions - 1) + expansion_time) / total_expansions
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring"""
        success_rate = (
            self.expansion_stats['successful_expansions'] / 
            max(1, self.expansion_stats['total_expansions'])
        )
        
        return {
            **self.expansion_stats,
            'success_rate': round(success_rate, 3),
            'cache_size': len(self.query_cache),
            'cache_hit_rate': (
                self.expansion_stats['cache_hits'] / 
                max(1, self.expansion_stats['total_expansions'])
            ),
            'openai_available': self.openai_client is not None
        }
    
    def clear_cache(self):
        """Clear query cache"""
        self.query_cache.clear()
        logger.info("Query expansion cache cleared")