"""
Multi-Query Generation Service - Phase 2 RAG Improvement
Generates multiple query variations for better retrieval using Ollama and proven strategies
"""

import logging
import asyncio
import time
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re

# HTTP client for Ollama
import httpx

# Local imports
from config import settings
from .query_enhancer import QueryEnhancer, EnhancedQuery, QueryLanguage

logger = logging.getLogger(__name__)

@dataclass
class MultiQueryResult:
    """Result from multi-query generation"""
    original_query: str
    enhanced_query: EnhancedQuery
    query_variations: List[str]
    embedding_queries: List[str]  # Final queries to embed
    confidence_scores: List[float]
    generation_time: float

class MultiQueryGenerator:
    """
    Generates multiple query variations using Ollama and query enhancement techniques
    Based on Haystack QueryExpander patterns adapted for local LLM
    """
    
    def __init__(self, ollama_url: str = None):
        self.ollama_url = ollama_url or settings.OLLAMA_BASE_URL
        self.model_name = settings.OLLAMA_MODEL
        self.query_enhancer = QueryEnhancer()
        self._initialized = False
        
        # Query generation templates
        self.generation_templates = {
            QueryLanguage.GERMAN: """
Du bist ein Experte für Suchoptimierung. Generiere 3 alternative Formulierungen für diese Suchanfrage, die semantisch ähnlich sind aber unterschiedliche Wörter verwenden.

Original-Suchanfrage: "{query}"

Regeln:
- Verwende Synonyme und verwandte Begriffe
- Behalte die ursprüngliche Bedeutung bei  
- Variiere die Satzstruktur
- Nutze sowohl formale als auch umgangssprachliche Varianten
- Antworte nur mit den 3 Alternativen, eine pro Zeile

Alternative Suchanfragen:
""",
            
            QueryLanguage.ENGLISH: """
You are an expert in search optimization. Generate 3 alternative formulations for this search query that are semantically similar but use different words.

Original query: "{query}"

Rules:
- Use synonyms and related terms
- Maintain the original meaning
- Vary the sentence structure  
- Use both formal and informal variants
- Reply only with the 3 alternatives, one per line

Alternative queries:
""",
            
            QueryLanguage.MIXED: """
You are bilingual search expert. Generate 3 alternative formulations for this query mixing German and English terms where appropriate.

Original query: "{query}"

Rules:
- Use synonyms in both languages
- Maintain semantic meaning
- Mix German/English terms naturally
- Reply only with the 3 alternatives, one per line

Alternative queries:
"""
        }
    
    async def initialize(self) -> None:
        """Initialize the multi-query generator"""
        if self._initialized:
            return
            
        logger.info("🚀 Initializing Multi-Query Generator...")
        
        # Initialize query enhancer
        await self.query_enhancer.initialize()
        
        # Test Ollama connection
        try:
            await self._test_ollama_connection()
            logger.info("✅ Ollama connection verified")
        except Exception as e:
            logger.warning(f"⚠️ Ollama connection failed: {e}")
            logger.info("Multi-query generation will work with limited capabilities")
        
        self._initialized = True
        logger.info("✅ Multi-Query Generator initialized")
    
    async def _test_ollama_connection(self) -> bool:
        """Test if Ollama is available"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.ollama_url}/api/tags", timeout=5.0)
            return response.status_code == 200
    
    async def generate_multiple_queries(
        self, 
        query: str, 
        max_variations: int = 3,
        use_ollama: bool = True
    ) -> MultiQueryResult:
        """
        Generate multiple query variations for enhanced retrieval
        
        Args:
            query: Original user query
            max_variations: Maximum number of variations to generate
            use_ollama: Whether to use Ollama for generation
            
        Returns:
            MultiQueryResult with all variations and metadata
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        logger.debug(f"🔄 Generating {max_variations} variations for: '{query}'")
        
        # Step 1: Enhance the original query
        enhanced = await self.query_enhancer.enhance_query(query)
        
        # Step 2: Generate variations using different strategies
        variations = []
        confidence_scores = []
        
        # Strategy 1: Use enhanced query alternatives
        for alt in enhanced.alternative_forms[:2]:
            variations.append(alt)
            confidence_scores.append(enhanced.confidence * 0.8)
        
        # Strategy 2: Generate synonym-based variations
        synonym_variations = self._generate_synonym_variations(enhanced)
        for var in synonym_variations[:2]:
            variations.append(var)
            confidence_scores.append(enhanced.confidence * 0.7)
        
        # Strategy 3: Use Ollama for LLM-based generation (if available)
        if use_ollama:
            try:
                ollama_variations = await self._generate_with_ollama(enhanced)
                for var in ollama_variations:
                    variations.append(var)
                    confidence_scores.append(enhanced.confidence * 0.9)
            except Exception as e:
                logger.debug(f"Ollama generation failed: {e}")
        
        # Strategy 4: Generate structural variations
        structural_vars = self._generate_structural_variations(enhanced)
        for var in structural_vars[:1]:
            variations.append(var)
            confidence_scores.append(enhanced.confidence * 0.6)
        
        # Clean and deduplicate variations
        clean_variations = self._clean_and_deduplicate(query, variations)
        
        # Limit to max_variations
        final_variations = clean_variations[:max_variations]
        final_confidence = confidence_scores[:len(final_variations)]
        
        # Prepare final embedding queries (original + variations)
        embedding_queries = [enhanced.normalized] + final_variations
        
        generation_time = time.time() - start_time
        logger.debug(f"✅ Generated {len(final_variations)} variations in {generation_time:.3f}s")
        
        return MultiQueryResult(
            original_query=query,
            enhanced_query=enhanced,
            query_variations=final_variations,
            embedding_queries=embedding_queries,
            confidence_scores=final_confidence,
            generation_time=generation_time
        )
    
    def _generate_synonym_variations(self, enhanced: EnhancedQuery) -> List[str]:
        """Generate variations using synonym substitution"""
        variations = []
        
        if not enhanced.synonyms:
            return variations
        
        # Create variations by substituting synonyms
        base_terms = enhanced.normalized.split()
        
        # Strategy: Replace each term with its best synonym
        for original_term, synonyms in enhanced.synonyms.items():
            if len(synonyms) > 1:
                # Use the first alternative synonym (not the original)
                best_synonym = synonyms[1] if len(synonyms) > 1 else synonyms[0]
                
                # Create variation by substituting
                variation_terms = []
                for term in base_terms:
                    if term == original_term:
                        variation_terms.append(best_synonym)
                    else:
                        variation_terms.append(term)
                
                variation = ' '.join(variation_terms)
                if variation != enhanced.normalized:
                    variations.append(variation)
        
        return variations[:2]  # Limit to 2 synonym variations
    
    def _generate_structural_variations(self, enhanced: EnhancedQuery) -> List[str]:
        """Generate variations by changing query structure"""
        variations = []
        query = enhanced.normalized
        
        # Add context markers
        variations.append(f"information about {query}")
        variations.append(f"explain {query}")
        
        # For German queries
        if enhanced.language == QueryLanguage.GERMAN:
            variations.append(f"informationen über {query}")
            variations.append(f"erkläre {query}")
        
        return variations
    
    async def _generate_with_ollama(self, enhanced: EnhancedQuery) -> List[str]:
        """Generate variations using Ollama LLM"""
        template = self.generation_templates.get(
            enhanced.language, 
            self.generation_templates[QueryLanguage.ENGLISH]
        )
        
        prompt = template.format(query=enhanced.original)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "max_tokens": 200,
                            "top_p": 0.9
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "").strip()
                    
                    # Parse the generated variations
                    variations = self._parse_ollama_response(generated_text)
                    logger.debug(f"🤖 Ollama generated {len(variations)} variations")
                    return variations
                else:
                    logger.warning(f"Ollama request failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.debug(f"Ollama generation error: {e}")
            return []
    
    def _parse_ollama_response(self, response_text: str) -> List[str]:
        """Parse variations from Ollama response"""
        variations = []
        
        # Split by lines and clean
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and metadata
            if not line or line.startswith('Alternative') or line.startswith('Query'):
                continue
            
            # Remove numbering and bullet points
            line = re.sub(r'^\d+\.\s*', '', line)
            line = re.sub(r'^[-•*]\s*', '', line)
            
            # Clean quotes
            line = line.strip('"\'')
            
            if len(line) > 3 and line not in variations:
                variations.append(line)
        
        return variations[:3]  # Limit to 3 variations
    
    def _clean_and_deduplicate(self, original: str, variations: List[str]) -> List[str]:
        """Clean and remove duplicate variations"""
        clean_variations = []
        seen = {original.lower()}  # Don't include original
        
        for var in variations:
            var_clean = var.strip().lower()
            
            # Skip if empty, too short, or duplicate
            if not var_clean or len(var_clean) < 3 or var_clean in seen:
                continue
            
            # Skip if too similar to original (simple similarity check)
            if self._calculate_similarity(original.lower(), var_clean) > 0.9:
                continue
            
            seen.add(var_clean)
            clean_variations.append(var.strip())
        
        return clean_variations
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation based on word overlap"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def embed_all_queries(
        self, 
        multi_result: MultiQueryResult, 
        embedding_service
    ) -> List[Tuple[str, List[float]]]:
        """
        Embed all query variations using the embedding service
        
        Args:
            multi_result: Result from generate_multiple_queries
            embedding_service: EmbeddingService instance
            
        Returns:
            List of (query, embedding) tuples
        """
        embedded_queries = []
        
        for query in multi_result.embedding_queries:
            try:
                embedding = await embedding_service.embed_query(query)
                embedded_queries.append((query, embedding))
                logger.debug(f"✅ Embedded query: '{query[:30]}...'")
            except Exception as e:
                logger.error(f"❌ Failed to embed query '{query}': {e}")
                continue
        
        return embedded_queries
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get multi-query generator statistics"""
        return {
            "initialized": self._initialized,
            "ollama_url": self.ollama_url,
            "model_name": self.model_name,
            "supported_languages": ["German", "English", "Mixed"],
            "max_variations": 3,
            "generation_strategies": ["Synonyms", "Structural", "LLM-based", "Enhanced"]
        }