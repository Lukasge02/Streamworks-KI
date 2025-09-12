"""
Query Enhancement Service - Phase 2 RAG Improvement
Smart query preprocessing using spaCy, NLTK, and proven NLP libraries
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import time

# NLP Libraries
import spacy
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from textblob import TextBlob
from unidecode import unidecode

# Local imports
from config import settings
from .adaptive_retrieval import QueryType, QueryAnalyzer, QueryContext

logger = logging.getLogger(__name__)

class QueryLanguage(str, Enum):
    """Detected query language"""
    GERMAN = "de"
    ENGLISH = "en"
    MIXED = "mixed"
    UNKNOWN = "unknown"

@dataclass
class EnhancedQuery:
    """Enhanced query with all preprocessing applied"""
    original: str
    preprocessed: str
    normalized: str
    language: QueryLanguage
    query_type: QueryType
    expanded_terms: List[str]
    synonyms: Dict[str, List[str]]
    alternative_forms: List[str]
    confidence: float

class QueryEnhancer:
    """
    Production-grade query enhancement using proven NLP libraries
    Optimized for German/English mixed RAG systems with local embeddings
    """
    
    def __init__(self):
        self.nlp_de = None
        self.nlp_en = None
        self.german_stopwords = set()
        self.english_stopwords = set()
        self.query_analyzer = QueryAnalyzer()
        self._initialized = False
        
        # German-specific patterns
        self.german_patterns = {
            'umlauts': {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'},
            'articles': {'der', 'die', 'das', 'dem', 'den', 'des'},
            'common_words': {'und', 'oder', 'aber', 'auch', 'noch', 'nur'},
            'question_words': {'was', 'wie', 'wo', 'wann', 'warum', 'wer'}
        }
        
        # Domain-specific term mappings
        self.domain_terms = {
            'document': ['dokument', 'datei', 'file', 'paper', 'text', 'content'],
            'process': ['prozess', 'workflow', 'ablauf', 'verfahren', 'methode'],
            'system': ['system', 'anlage', 'infrastructure', 'plattform'],
            'data': ['daten', 'information', 'informationen', 'content'],
            'analysis': ['analyse', 'auswertung', 'untersuchung', 'bewertung']
        }
    
    async def initialize(self) -> None:
        """Initialize spaCy models and NLTK resources"""
        if self._initialized:
            return
        
        logger.info("🚀 Initializing Query Enhancer with NLP libraries...")
        
        try:
            # Load spaCy models
            logger.info("Loading spaCy German model...")
            self.nlp_de = spacy.load("de_core_news_sm")
            
            logger.info("Loading spaCy English model...")
            try:
                self.nlp_en = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("English spaCy model not found, downloading...")
                spacy.cli.download("en_core_web_sm")
                self.nlp_en = spacy.load("en_core_web_sm")
            
            # Load stopwords
            self.german_stopwords = set(stopwords.words('german'))
            self.english_stopwords = set(stopwords.words('english'))
            
            # Add custom German stopwords
            self.german_stopwords.update(self.german_patterns['articles'])
            self.german_stopwords.update(self.german_patterns['common_words'])
            
            logger.info("✅ Query Enhancer initialized successfully")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Query Enhancer: {e}")
            raise
    
    async def enhance_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> EnhancedQuery:
        """
        Main entry point for query enhancement
        
        Args:
            query: Original user query
            context: Optional context information
            
        Returns:
            EnhancedQuery with all enhancements applied
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        logger.debug(f"🔍 Enhancing query: '{query}'")
        
        # Step 1: Basic preprocessing
        preprocessed = await self._preprocess_query(query)
        
        # Step 2: Language detection
        language = self._detect_language(preprocessed)
        
        # Step 3: Advanced preprocessing based on language
        normalized = await self._normalize_query(preprocessed, language)
        
        # Step 4: Query type analysis
        query_context = self.query_analyzer.analyze_query(normalized)
        
        # Step 5: Synonym expansion
        expanded_terms, synonyms = await self._expand_with_synonyms(normalized, language)
        
        # Step 6: Generate alternative forms
        alternatives = await self._generate_alternatives(normalized, language, query_context.query_type)
        
        # Step 7: Calculate confidence
        confidence = self._calculate_confidence(query, preprocessed, expanded_terms)
        
        processing_time = time.time() - start_time
        logger.debug(f"✅ Query enhanced in {processing_time:.3f}s - confidence: {confidence:.2f}")
        
        return EnhancedQuery(
            original=query,
            preprocessed=preprocessed,
            normalized=normalized,
            language=language,
            query_type=query_context.query_type,
            expanded_terms=expanded_terms,
            synonyms=synonyms,
            alternative_forms=alternatives,
            confidence=confidence
        )
    
    async def _preprocess_query(self, query: str) -> str:
        """Basic query preprocessing"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', query.strip())
        
        # Normalize quotes and punctuation
        cleaned = re.sub(r'[„""]', '"', cleaned)
        cleaned = re.sub(r'[''´`]', "'", cleaned)
        
        # Handle common contractions
        contractions = {
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "n't": " not", "'re": " are", "'ve": " have", "'ll": " will"
        }
        
        for contraction, expansion in contractions.items():
            cleaned = re.sub(rf'\b\w+{re.escape(contraction)}\b', 
                           lambda m: m.group(0).replace(contraction, expansion), 
                           cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _detect_language(self, query: str) -> QueryLanguage:
        """Detect query language using TextBlob and patterns"""
        # Check for German-specific patterns
        german_indicators = 0
        english_indicators = 0
        
        # German patterns
        if re.search(r'\b(was|wie|wo|warum|wer)\b', query.lower()):
            german_indicators += 2
        if re.search(r'\b(der|die|das|dem|den|des)\b', query.lower()):
            german_indicators += 2
        if re.search(r'[äöüß]', query.lower()):
            german_indicators += 3
        if re.search(r'\b(und|oder|auch)\b', query.lower()):
            german_indicators += 1
        
        # English patterns  
        if re.search(r'\b(what|how|where|why|who)\b', query.lower()):
            english_indicators += 2
        if re.search(r'\b(the|and|or|of|in|to)\b', query.lower()):
            english_indicators += 1
        
        # Use TextBlob as fallback
        try:
            blob = TextBlob(query)
            detected_lang = blob.detect_language()
            if detected_lang == 'de':
                german_indicators += 1
            elif detected_lang == 'en':
                english_indicators += 1
        except:
            pass  # TextBlob detection can fail
        
        # Decision logic
        if german_indicators > english_indicators + 1:
            return QueryLanguage.GERMAN
        elif english_indicators > german_indicators + 1:
            return QueryLanguage.ENGLISH
        elif german_indicators > 0 and english_indicators > 0:
            return QueryLanguage.MIXED
        else:
            return QueryLanguage.UNKNOWN
    
    async def _normalize_query(self, query: str, language: QueryLanguage) -> str:
        """Advanced normalization using spaCy"""
        # Unicode normalization (umlauts)
        normalized = query
        
        if language in [QueryLanguage.GERMAN, QueryLanguage.MIXED]:
            # Apply German-specific normalization
            for umlaut, replacement in self.german_patterns['umlauts'].items():
                normalized = normalized.replace(umlaut, replacement)
                normalized = normalized.replace(umlaut.upper(), replacement.upper())
        
        # spaCy processing
        if language == QueryLanguage.GERMAN:
            doc = self.nlp_de(normalized)
        elif language == QueryLanguage.ENGLISH:
            doc = self.nlp_en(normalized)
        else:
            # Default to German for mixed/unknown
            doc = self.nlp_de(normalized)
        
        # Extract meaningful tokens
        meaningful_tokens = []
        for token in doc:
            # Skip stop words, punctuation, and spaces
            if (token.is_stop or token.is_punct or token.is_space or 
                len(token.text.strip()) < 2):
                continue
            
            # Use lemma for better normalization, but keep original if lemma is generic
            lemma = token.lemma_.lower()
            original = token.text.lower()
            
            # Prefer original for proper nouns and specific terms
            if token.pos_ in ['PROPN', 'NOUN'] and len(original) > 3:
                meaningful_tokens.append(original)
            elif lemma not in ['-PRON-', 'be', 'have', 'do'] and len(lemma) > 2:
                meaningful_tokens.append(lemma)
            elif len(original) > 2:
                meaningful_tokens.append(original)
        
        # Reconstruct query maintaining some structure
        if meaningful_tokens:
            return ' '.join(meaningful_tokens)
        else:
            # Fallback to simple normalization
            return ' '.join(query.lower().split())
    
    async def _expand_with_synonyms(self, query: str, language: QueryLanguage) -> Tuple[List[str], Dict[str, List[str]]]:
        """Expand query terms with synonyms using WordNet and domain terms"""
        expanded_terms = []
        synonyms_dict = {}
        
        # Get query terms
        terms = query.lower().split()
        
        for term in terms:
            term_synonyms = set([term])  # Include original
            
            # Domain-specific expansion
            for domain_key, domain_synonyms in self.domain_terms.items():
                if term in domain_synonyms or any(term in s for s in domain_synonyms):
                    term_synonyms.update(domain_synonyms)
            
            # WordNet synonyms (English)
            if language in [QueryLanguage.ENGLISH, QueryLanguage.MIXED]:
                try:
                    synsets = wordnet.synsets(term, lang='eng')
                    for synset in synsets[:2]:  # Limit to top 2 synsets
                        for lemma in synset.lemmas():
                            synonym = lemma.name().replace('_', ' ').lower()
                            if len(synonym) > 2 and synonym != term:
                                term_synonyms.add(synonym)
                except:
                    pass
            
            # German WordNet (if available)
            if language in [QueryLanguage.GERMAN, QueryLanguage.MIXED]:
                try:
                    # Try German wordnet
                    synsets = wordnet.synsets(term, lang='deu')
                    for synset in synsets[:2]:
                        for lemma in synset.lemmas('deu'):
                            synonym = lemma.name().replace('_', ' ').lower()
                            if len(synonym) > 2 and synonym != term:
                                term_synonyms.add(synonym)
                except:
                    pass
            
            # Store results
            term_synonyms_list = list(term_synonyms)[:5]  # Limit to 5 synonyms per term
            if len(term_synonyms_list) > 1:
                synonyms_dict[term] = term_synonyms_list
            expanded_terms.extend(term_synonyms_list)
        
        # Remove duplicates while preserving order
        expanded_terms = list(dict.fromkeys(expanded_terms))
        
        logger.debug(f"🔄 Expanded '{query}' to {len(expanded_terms)} terms")
        return expanded_terms, synonyms_dict
    
    async def _generate_alternatives(self, query: str, language: QueryLanguage, query_type: QueryType) -> List[str]:
        """Generate alternative query formulations"""
        alternatives = []
        
        # Type-specific reformulations
        if query_type == QueryType.WHAT_IS:
            alternatives.extend([
                f"definition {query.replace('was ist', '').replace('what is', '').strip()}",
                f"explain {query.replace('was ist', '').replace('what is', '').strip()}",
                f"meaning {query.replace('was ist', '').replace('what is', '').strip()}"
            ])
        
        elif query_type == QueryType.HOW_DOES:
            alternatives.extend([
                f"process {query.replace('wie funktioniert', '').replace('how does', '').strip()}",
                f"workflow {query.replace('wie funktioniert', '').replace('how does', '').strip()}",
                f"procedure {query.replace('wie funktioniert', '').replace('how does', '').strip()}"
            ])
        
        elif query_type == QueryType.PROCEDURE:
            alternatives.extend([
                f"steps {query}",
                f"tutorial {query}",
                f"guide {query}"
            ])
        
        # Language-specific alternatives
        if language == QueryLanguage.GERMAN:
            alternatives.append(self._translate_to_english(query))
        elif language == QueryLanguage.ENGLISH:
            alternatives.append(self._translate_to_german(query))
        
        # Clean and filter alternatives
        clean_alternatives = []
        for alt in alternatives:
            alt = alt.strip()
            if alt and alt != query and len(alt) > 3:
                clean_alternatives.append(alt)
        
        return clean_alternatives[:3]  # Limit to 3 alternatives
    
    def _translate_to_english(self, german_query: str) -> str:
        """Simple German to English translation for common terms"""
        translations = {
            'dokument': 'document', 'prozess': 'process', 'system': 'system',
            'daten': 'data', 'information': 'information', 'analyse': 'analysis',
            'was ist': 'what is', 'wie funktioniert': 'how does', 'wo ist': 'where is'
        }
        
        translated = german_query.lower()
        for german, english in translations.items():
            translated = translated.replace(german, english)
        
        return translated
    
    def _translate_to_german(self, english_query: str) -> str:
        """Simple English to German translation for common terms"""
        translations = {
            'document': 'dokument', 'process': 'prozess', 'system': 'system',
            'data': 'daten', 'information': 'information', 'analysis': 'analyse',
            'what is': 'was ist', 'how does': 'wie funktioniert', 'where is': 'wo ist'
        }
        
        translated = english_query.lower()
        for english, german in translations.items():
            translated = translated.replace(english, german)
        
        return translated
    
    def _calculate_confidence(self, original: str, preprocessed: str, expanded_terms: List[str]) -> float:
        """Calculate enhancement confidence score"""
        confidence = 0.5  # Base confidence
        
        # Length and complexity indicators
        if len(original.split()) >= 3:
            confidence += 0.1
        
        # Preprocessing success
        if len(preprocessed) > len(original) * 0.5:
            confidence += 0.1
        
        # Expansion success
        expansion_ratio = len(expanded_terms) / max(len(original.split()), 1)
        if expansion_ratio >= 2:
            confidence += 0.2
        elif expansion_ratio >= 1.5:
            confidence += 0.1
        
        # Language detection confidence
        if re.search(r'[äöüß]', original) or re.search(r'\b(der|die|das)\b', original.lower()):
            confidence += 0.1  # Clear German indicators
        
        return min(confidence, 1.0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get enhancement statistics"""
        return {
            "initialized": self._initialized,
            "supported_languages": ["German", "English", "Mixed"],
            "domain_terms": len(self.domain_terms),
            "german_stopwords": len(self.german_stopwords),
            "english_stopwords": len(self.english_stopwords)
        }