"""
Smart Search Service for StreamWorks-KI RAG System
Implements intelligent query classification and advanced search strategies
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import re

from langchain.schema import Document
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

class SearchStrategy(Enum):
    """Available search strategies"""
    SEMANTIC_ONLY = "semantic_only"
    HYBRID = "hybrid"
    FILTERED = "filtered"
    CONTEXTUAL = "contextual"
    CONCEPT_BASED = "concept_based"

@dataclass
class SearchFilter:
    """Advanced search filters"""
    document_types: Optional[List[str]] = None
    file_formats: Optional[List[str]] = None
    complexity_range: Optional[Tuple[int, int]] = None
    concepts: Optional[List[str]] = None
    chunk_types: Optional[List[str]] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    source_categories: Optional[List[str]] = None
    processing_methods: Optional[List[str]] = None

@dataclass
class SearchResult:
    """Enhanced search result with metadata"""
    content: str
    score: float
    metadata: Dict[str, Any]
    explanation: str
    chunk_type: str
    document_type: str
    file_format: str
    processing_method: str
    relevance_factors: List[str]

class QueryClassifier:
    """Intelligent query classification for optimal search strategy"""
    
    def __init__(self):
        # StreamWorks-specific intent patterns
        self.intent_patterns = {
            'xml_generation': [
                'erstell', 'generier', 'xml', 'stream', 'job', 'konfiguration',
                'create', 'generate', 'build', 'template', 'schedule'
            ],
            'troubleshooting': [
                'fehler', 'error', 'problem', 'funktioniert nicht', 'fix',
                'broken', 'issue', 'debug', 'warum', 'why', 'help'
            ],
            'how_to': [
                'wie', 'how', 'anleitung', 'tutorial', 'beispiel', 'guide',
                'step', 'instruction', 'setup', 'configure'
            ],
            'api_usage': [
                'api', 'endpoint', 'request', 'response', 'integration',
                'call', 'invoke', 'parameter', 'rest', 'http'
            ],
            'configuration': [
                'config', 'einstell', 'parameter', 'setup', 'settings',
                'configure', 'property', 'option', 'value'
            ],
            'general_info': [
                'was ist', 'what is', 'erklär', 'erkläre', 'definition',
                'describe', 'explain', 'overview', 'about'
            ],
            'data_processing': [
                'batch', 'processing', 'data', 'transform', 'convert',
                'import', 'export', 'format', 'parse'
            ],
            'scheduling': [
                'schedule', 'time', 'cron', 'timer', 'daily', 'weekly',
                'zeitplan', 'automatisch', 'trigger'
            ]
        }
        
        # Technical complexity indicators
        self.complexity_indicators = {
            'advanced': [
                'integration', 'architecture', 'performance', 'optimization',
                'security', 'scalability', 'enterprise', 'production'
            ],
            'intermediate': [
                'configuration', 'parameter', 'setup', 'api', 'xml',
                'database', 'connection', 'authentication'
            ],
            'basic': [
                'what', 'how', 'simple', 'basic', 'start', 'begin',
                'example', 'tutorial', 'guide'
            ]
        }
        
        # StreamWorks domain concepts
        self.domain_concepts = {
            'data_processing': ['batch', 'stream', 'pipeline', 'etl', 'transform'],
            'xml_workflow': ['xml', 'xsd', 'schema', 'validation', 'parsing'],
            'scheduling': ['cron', 'schedule', 'timer', 'trigger', 'automation'],
            'api_integration': ['rest', 'api', 'endpoint', 'request', 'response'],
            'configuration': ['config', 'settings', 'parameter', 'property']
        }
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """Comprehensive query classification"""
        query_lower = query.lower()
        
        # 1. Intent Detection
        intent_scores = self._calculate_intent_scores(query_lower)
        primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else 'general_info'
        
        # 2. Complexity Assessment
        complexity = self._assess_complexity(query_lower)
        
        # 3. Domain Concept Detection
        detected_concepts = self._detect_domain_concepts(query_lower)
        
        # 4. Document Type Preferences
        doc_type_preferences = self._get_doc_type_preferences(primary_intent, detected_concepts)
        
        # 5. Search Strategy Selection
        search_strategy = self._determine_search_strategy(primary_intent, complexity, len(query.split()))
        
        # 6. Query Enhancement Suggestions
        enhancement_suggestions = self._generate_enhancement_suggestions(query, primary_intent, detected_concepts)
        
        return {
            'primary_intent': primary_intent,
            'intent_confidence': intent_scores.get(primary_intent, 0),
            'complexity_level': complexity,
            'detected_concepts': detected_concepts,
            'preferred_doc_types': doc_type_preferences,
            'search_strategy': search_strategy,
            'enhancement_suggestions': enhancement_suggestions,
            'suggested_filters': self._create_suggested_filters(primary_intent, complexity, detected_concepts),
            'query_metadata': {
                'word_count': len(query.split()),
                'character_count': len(query),
                'technical_terms': self._count_technical_terms(query_lower),
                'question_type': self._detect_question_type(query)
            }
        }
    
    def _calculate_intent_scores(self, query_lower: str) -> Dict[str, int]:
        """Calculate scores for each intent category"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in query_lower:
                    # Weight longer patterns higher
                    weight = len(pattern.split())
                    score += weight
            
            if score > 0:
                intent_scores[intent] = score
        
        return intent_scores
    
    def _assess_complexity(self, query_lower: str) -> str:
        """Assess query complexity level"""
        scores = {'basic': 0, 'intermediate': 0, 'advanced': 0}
        
        for level, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if indicator in query_lower:
                    scores[level] += 1
        
        # Determine complexity based on highest score
        max_level = max(scores, key=scores.get)
        
        # Additional heuristics
        word_count = len(query_lower.split())
        if word_count > 20:
            return 'advanced'
        elif word_count > 10:
            return 'intermediate' if scores['intermediate'] >= scores['basic'] else 'basic'
        
        return max_level if scores[max_level] > 0 else 'basic'
    
    def _detect_domain_concepts(self, query_lower: str) -> List[str]:
        """Detect StreamWorks domain concepts in query"""
        detected = []
        
        for concept_category, keywords in self.domain_concepts.items():
            if any(keyword in query_lower for keyword in keywords):
                detected.append(concept_category)
        
        return detected
    
    def _get_doc_type_preferences(self, intent: str, concepts: List[str]) -> List[str]:
        """Determine preferred document types based on intent and concepts"""
        base_preferences = {
            'xml_generation': ['xml_config', 'schema_def', 'code_script'],
            'troubleshooting': ['qa_faq', 'help_docs', 'log_file'],
            'how_to': ['help_docs', 'qa_faq', 'api_docs'],
            'api_usage': ['api_docs', 'code_script', 'configuration'],
            'configuration': ['xml_config', 'configuration', 'help_docs'],
            'general_info': ['help_docs', 'qa_faq', 'office_doc'],
            'data_processing': ['code_script', 'structured_data', 'help_docs'],
            'scheduling': ['xml_config', 'code_script', 'help_docs']
        }
        
        preferences = base_preferences.get(intent, ['help_docs'])
        
        # Enhance based on detected concepts
        if 'xml_workflow' in concepts:
            preferences = ['xml_config', 'schema_def'] + preferences
        if 'api_integration' in concepts:
            preferences = ['api_docs', 'code_script'] + preferences
        if 'data_processing' in concepts:
            preferences = ['structured_data', 'code_script'] + preferences
        
        return list(dict.fromkeys(preferences))  # Remove duplicates while preserving order
    
    def _determine_search_strategy(self, intent: str, complexity: str, word_count: int) -> SearchStrategy:
        """Determine optimal search strategy"""
        
        # Strategy mapping based on intent
        if intent in ['xml_generation', 'configuration'] and complexity in ['intermediate', 'advanced']:
            return SearchStrategy.FILTERED
        elif intent == 'troubleshooting':
            return SearchStrategy.CONTEXTUAL
        elif complexity == 'advanced' or word_count > 15:
            return SearchStrategy.HYBRID
        elif intent in ['api_usage', 'data_processing']:
            return SearchStrategy.CONCEPT_BASED
        else:
            return SearchStrategy.SEMANTIC_ONLY
    
    def _generate_enhancement_suggestions(self, query: str, intent: str, concepts: List[str]) -> List[str]:
        """Generate query enhancement suggestions"""
        suggestions = []
        
        # Intent-based suggestions
        if intent == 'xml_generation' and 'xml' not in query.lower():
            suggestions.append("Consider adding 'XML' to your query for more specific results")
        
        if intent == 'troubleshooting' and 'error' not in query.lower():
            suggestions.append("Try including specific error messages or symptoms")
        
        # Concept-based suggestions
        if not concepts:
            suggestions.append("Try adding technical terms like 'StreamWorks', 'API', or 'configuration'")
        
        # Length-based suggestions
        if len(query.split()) < 3:
            suggestions.append("Consider providing more context for better results")
        
        return suggestions
    
    def _create_suggested_filters(self, intent: str, complexity: str, concepts: List[str]) -> SearchFilter:
        """Create suggested search filters"""
        return SearchFilter(
            document_types=self._get_doc_type_preferences(intent, concepts),
            complexity_range=self._get_complexity_range(complexity),
            concepts=concepts if concepts else None,
            file_formats=self._suggest_file_formats(intent, concepts),
            processing_methods=self._suggest_processing_methods(intent)
        )
    
    def _get_complexity_range(self, complexity: str) -> Tuple[int, int]:
        """Map complexity level to numeric range"""
        ranges = {
            'basic': (1, 3),
            'intermediate': (3, 7),
            'advanced': (6, 10)
        }
        return ranges.get(complexity, (1, 10))
    
    def _suggest_file_formats(self, intent: str, concepts: List[str]) -> Optional[List[str]]:
        """Suggest relevant file formats"""
        format_mapping = {
            'xml_generation': ['xml', 'xsd'],
            'api_usage': ['json', 'yaml', 'py'],
            'configuration': ['xml', 'json', 'yaml', 'ini'],
            'data_processing': ['csv', 'json', 'xml']
        }
        
        suggested = format_mapping.get(intent, [])
        
        # Add concept-based formats
        if 'xml_workflow' in concepts:
            suggested.extend(['xml', 'xsd'])
        if 'api_integration' in concepts:
            suggested.extend(['json', 'py'])
        
        return list(set(suggested)) if suggested else None
    
    def _suggest_processing_methods(self, intent: str) -> Optional[List[str]]:
        """Suggest relevant processing methods"""
        method_mapping = {
            'xml_generation': ['element_based', 'structure_based'],
            'api_usage': ['function_based', 'structure_based'],
            'data_processing': ['row_based', 'structure_based']
        }
        return method_mapping.get(intent)
    
    def _count_technical_terms(self, query_lower: str) -> int:
        """Count technical terms in query"""
        technical_terms = [
            'xml', 'api', 'config', 'parameter', 'schedule', 'batch',
            'stream', 'database', 'server', 'endpoint', 'request'
        ]
        return sum(1 for term in technical_terms if term in query_lower)
    
    def _detect_question_type(self, query: str) -> str:
        """Detect the type of question being asked"""
        query_lower = query.lower().strip()
        
        if query_lower.startswith(('what', 'was')):
            return 'definition'
        elif query_lower.startswith(('how', 'wie')):
            return 'procedural'
        elif query_lower.startswith(('why', 'warum')):
            return 'explanatory'
        elif query_lower.startswith(('when', 'wann')):
            return 'temporal'
        elif query_lower.startswith(('where', 'wo')):
            return 'locational'
        elif '?' in query:
            return 'interrogative'
        else:
            return 'statement'

class SmartSearchService:
    """Advanced search service with intelligent query processing"""
    
    def __init__(self, rag_service_instance=None):
        self.rag_service = rag_service_instance or rag_service
        self.query_classifier = QueryClassifier()
        
        # Search performance metrics
        self.search_stats = {
            'total_searches': 0,
            'strategy_usage': {},
            'average_response_time': 0.0,
            'filter_effectiveness': {}
        }
        
        logger.info("🔍 Smart Search Service initialized")
    
    async def smart_search(self, 
                          query: str, 
                          top_k: int = 5, 
                          custom_filter: Optional[SearchFilter] = None,
                          include_analysis: bool = True) -> Dict[str, Any]:
        """Main smart search interface with comprehensive analysis"""
        
        start_time = datetime.utcnow()
        self.search_stats['total_searches'] += 1
        
        try:
            # 1. Query Analysis & Classification
            query_analysis = self.query_classifier.classify_query(query)
            logger.info(f"🎯 Query classified as: {query_analysis['primary_intent']} "
                       f"(complexity: {query_analysis['complexity_level']})")
            
            # 2. Filter Selection
            search_filter = custom_filter or query_analysis['suggested_filters']
            
            # 3. Strategy Execution
            strategy = query_analysis['search_strategy']
            self.search_stats['strategy_usage'][strategy.value] = \
                self.search_stats['strategy_usage'].get(strategy.value, 0) + 1
            
            logger.info(f"🔍 Executing {strategy.value} search strategy")
            
            # Execute search based on strategy
            raw_results = await self._execute_search_strategy(query, strategy, search_filter, top_k)
            
            # 4. Result Enhancement
            enhanced_results = self._enhance_search_results(raw_results, query_analysis, query)
            
            # 5. Performance Tracking
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_performance_stats(response_time)
            
            # 6. Build Response
            response = {
                'results': enhanced_results,
                'total_results': len(enhanced_results),
                'search_strategy': strategy.value,
                'response_time_ms': round(response_time * 1000, 2)
            }
            
            # Include analysis if requested
            if include_analysis:
                response.update({
                    'query_analysis': query_analysis,
                    'applied_filters': search_filter.__dict__ if search_filter else None,
                    'search_metadata': {
                        'timestamp': start_time.isoformat(),
                        'enhanced_results_count': len(enhanced_results),
                        'raw_results_count': len(raw_results)
                    }
                })
            
            logger.info(f"✅ Smart search completed: {len(enhanced_results)} results in {response_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ Smart search failed: {e}")
            # Fallback to basic search
            try:
                fallback_results = await self.rag_service.search_documents(query, top_k)
                return {
                    'results': [self._convert_to_search_result(doc, query, 'fallback') for doc in fallback_results],
                    'total_results': len(fallback_results),
                    'search_strategy': 'fallback',
                    'error': str(e),
                    'response_time_ms': 0
                }
            except Exception as fallback_error:
                logger.error(f"❌ Fallback search also failed: {fallback_error}")
                return {
                    'results': [],
                    'total_results': 0,
                    'search_strategy': 'failed',
                    'error': str(fallback_error),
                    'response_time_ms': 0
                }
    
    async def _execute_search_strategy(self, 
                                      query: str, 
                                      strategy: SearchStrategy, 
                                      search_filter: SearchFilter, 
                                      top_k: int) -> List[Document]:
        """Execute the selected search strategy"""
        
        if strategy == SearchStrategy.FILTERED:
            return await self._filtered_search(query, search_filter, top_k)
        elif strategy == SearchStrategy.HYBRID:
            return await self._hybrid_search(query, search_filter, top_k)
        elif strategy == SearchStrategy.CONTEXTUAL:
            return await self._contextual_search(query, search_filter, top_k)
        elif strategy == SearchStrategy.CONCEPT_BASED:
            return await self._concept_based_search(query, search_filter, top_k)
        else:  # SEMANTIC_ONLY
            return await self._semantic_search(query, top_k)
    
    async def _filtered_search(self, query: str, filter_obj: SearchFilter, top_k: int) -> List[Document]:
        """Advanced filtered search with metadata constraints"""
        
        try:
            # Build ChromaDB where clause
            where_clause = {}
            
            if filter_obj.document_types:
                where_clause["document_category"] = {"$in": filter_obj.document_types}
            
            if filter_obj.file_formats:
                where_clause["file_format"] = {"$in": filter_obj.file_formats}
            
            if filter_obj.chunk_types:
                where_clause["chunk_type"] = {"$in": filter_obj.chunk_types}
            
            if filter_obj.processing_methods:
                where_clause["processing_method"] = {"$in": filter_obj.processing_methods}
            
            if filter_obj.source_categories:
                where_clause["source_type"] = {"$in": filter_obj.source_categories}
            
            # Execute filtered search
            docs = self.rag_service.vector_store.similarity_search(
                query=query,
                k=min(top_k * 3, 50),  # Get more for better filtering
                filter=where_clause if where_clause else None
            )
            
            # Post-process filtering
            if filter_obj.concepts:
                docs = self._filter_by_concepts(docs, filter_obj.concepts)
            
            return docs[:top_k]
            
        except Exception as e:
            logger.warning(f"⚠️ Filtered search failed: {e}, falling back to semantic search")
            return await self._semantic_search(query, top_k)
    
    async def _hybrid_search(self, query: str, filter_obj: SearchFilter, top_k: int) -> List[Document]:
        """Hybrid search combining multiple strategies"""
        
        # 1. Semantic search (primary)
        semantic_docs = await self._semantic_search(query, top_k)
        
        # 2. Filtered search (secondary)
        if filter_obj:
            filtered_docs = await self._filtered_search(query, filter_obj, top_k)
        else:
            filtered_docs = []
        
        # 3. Keyword-enhanced search
        enhanced_query = self._enhance_query_with_keywords(query)
        if enhanced_query != query:
            keyword_docs = await self._semantic_search(enhanced_query, top_k // 2)
        else:
            keyword_docs = []
        
        # 4. Combine and deduplicate
        combined_docs = self._merge_search_results([semantic_docs, filtered_docs, keyword_docs])
        
        return combined_docs[:top_k]
    
    async def _contextual_search(self, query: str, filter_obj: SearchFilter, top_k: int) -> List[Document]:
        """Contextual search with query expansion"""
        
        # Expand query with domain context
        expanded_query = self._expand_query_with_context(query)
        logger.info(f"🔍 Expanded query: '{query}' → '{expanded_query}'")
        
        # Search with expanded query
        if filter_obj:
            results = await self._filtered_search(expanded_query, filter_obj, top_k)
        else:
            results = await self._semantic_search(expanded_query, top_k)
        
        return results
    
    async def _concept_based_search(self, query: str, filter_obj: SearchFilter, top_k: int) -> List[Document]:
        """Concept-based search focusing on domain-specific terms"""
        
        # Extract key concepts
        concepts = self._extract_key_concepts(query)
        
        # Create concept-enhanced queries
        concept_queries = [query]
        for concept in concepts:
            concept_queries.append(f"{query} {concept}")
        
        # Search with each concept query
        all_results = []
        for cq in concept_queries[:3]:  # Limit to avoid too many queries
            results = await self._semantic_search(cq, top_k // len(concept_queries) + 1)
            all_results.extend(results)
        
        # Merge and deduplicate
        merged_results = self._merge_search_results([all_results])
        
        return merged_results[:top_k]
    
    async def _semantic_search(self, query: str, top_k: int) -> List[Document]:
        """Standard semantic search using RAG service"""
        return await self.rag_service.search_documents(query, top_k)
    
    def _enhance_search_results(self, documents: List[Document], query_analysis: Dict, original_query: str) -> List[SearchResult]:
        """Transform documents into enhanced search results"""
        
        enhanced_results = []
        
        for i, doc in enumerate(documents):
            # Calculate relevance score (simplified)
            relevance_score = self._calculate_relevance_score(doc, query_analysis, original_query)
            
            # Determine relevance factors
            relevance_factors = self._identify_relevance_factors(doc, query_analysis, original_query)
            
            # Generate explanation
            explanation = self._generate_result_explanation(doc, query_analysis, relevance_factors)
            
            # Create enhanced result
            enhanced_result = SearchResult(
                content=doc.page_content,
                score=relevance_score,
                metadata=doc.metadata,
                explanation=explanation,
                chunk_type=doc.metadata.get('chunk_type', 'unknown'),
                document_type=doc.metadata.get('document_category', 'unknown'),
                file_format=doc.metadata.get('file_format', 'unknown'),
                processing_method=doc.metadata.get('processing_method', 'unknown'),
                relevance_factors=relevance_factors
            )
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def _calculate_relevance_score(self, doc: Document, query_analysis: Dict, original_query: str) -> float:
        """Calculate enhanced relevance score"""
        base_score = 0.5  # Start with neutral score
        
        # Intent matching bonus
        intent = query_analysis['primary_intent']
        doc_type = doc.metadata.get('document_category', '')
        
        if intent == 'xml_generation' and 'xml' in doc_type:
            base_score += 0.3
        elif intent == 'api_usage' and 'api' in doc_type:
            base_score += 0.3
        elif intent == 'troubleshooting' and 'qa' in doc_type:
            base_score += 0.2
        
        # Concept matching bonus
        detected_concepts = query_analysis.get('detected_concepts', [])
        content_lower = doc.page_content.lower()
        
        for concept in detected_concepts:
            if concept.replace('_', ' ') in content_lower:
                base_score += 0.1
        
        # Format preference bonus
        preferred_formats = query_analysis.get('suggested_filters', SearchFilter()).file_formats or []
        doc_format = doc.metadata.get('file_format', '')
        
        if doc_format in preferred_formats:
            base_score += 0.1
        
        # Processing method bonus
        preferred_methods = query_analysis.get('suggested_filters', SearchFilter()).processing_methods or []
        doc_method = doc.metadata.get('processing_method', '')
        
        if doc_method in preferred_methods:
            base_score += 0.1
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    def _identify_relevance_factors(self, doc: Document, query_analysis: Dict, original_query: str) -> List[str]:
        """Identify why this result is relevant"""
        factors = []
        
        # Check intent alignment
        intent = query_analysis['primary_intent']
        doc_type = doc.metadata.get('document_category', '')
        
        if intent in ['xml_generation', 'configuration'] and 'xml' in doc_type:
            factors.append("Matches XML/configuration intent")
        
        # Check concept presence
        concepts = query_analysis.get('detected_concepts', [])
        content_lower = doc.page_content.lower()
        
        for concept in concepts:
            if concept.replace('_', ' ') in content_lower:
                factors.append(f"Contains {concept.replace('_', ' ')} content")
        
        # Check format match
        file_format = doc.metadata.get('file_format', '')
        if file_format:
            factors.append(f"Source format: {file_format}")
        
        # Check processing method
        processing_method = doc.metadata.get('processing_method', '')
        if processing_method and processing_method != 'unknown':
            factors.append(f"Processed using {processing_method}")
        
        return factors[:3]  # Limit to top 3 factors
    
    def _generate_result_explanation(self, doc: Document, query_analysis: Dict, relevance_factors: List[str]) -> str:
        """Generate human-readable explanation for result relevance"""
        
        if not relevance_factors:
            return "General content match found"
        
        if len(relevance_factors) == 1:
            return relevance_factors[0]
        elif len(relevance_factors) == 2:
            return f"{relevance_factors[0]} and {relevance_factors[1].lower()}"
        else:
            return f"{relevance_factors[0]}, {relevance_factors[1].lower()}, and {relevance_factors[2].lower()}"
    
    def _filter_by_concepts(self, docs: List[Document], concepts: List[str]) -> List[Document]:
        """Filter documents by concept presence"""
        filtered = []
        
        for doc in docs:
            content_lower = doc.page_content.lower()
            metadata_concepts = doc.metadata.get('concepts', [])
            
            # Check if any concept is present
            concept_found = False
            for concept in concepts:
                concept_normalized = concept.replace('_', ' ')
                if (concept_normalized in content_lower or 
                    concept in metadata_concepts):
                    concept_found = True
                    break
            
            if concept_found:
                filtered.append(doc)
        
        return filtered
    
    def _merge_search_results(self, result_lists: List[List[Document]]) -> List[Document]:
        """Merge multiple result lists with deduplication"""
        seen_content = set()
        merged = []
        
        # Process lists in order of priority
        for result_list in result_lists:
            for doc in result_list:
                # Use first 100 characters as content hash for deduplication
                content_hash = hash(doc.page_content[:100])
                
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    merged.append(doc)
        
        return merged
    
    def _enhance_query_with_keywords(self, query: str) -> str:
        """Enhance query with domain-specific keywords"""
        query_lower = query.lower()
        
        # Add StreamWorks context if not present
        if 'streamworks' not in query_lower and len(query.split()) < 8:
            return f"{query} StreamWorks"
        
        return query
    
    def _expand_query_with_context(self, query: str) -> str:
        """Expand query with contextual information"""
        query_lower = query.lower()
        expansions = []
        
        # Add domain-specific context
        if 'xml' in query_lower and 'streamworks' not in query_lower:
            expansions.append('StreamWorks')
        
        if 'api' in query_lower and 'endpoint' not in query_lower:
            expansions.append('endpoint')
        
        if 'config' in query_lower and 'parameter' not in query_lower:
            expansions.append('configuration')
        
        if expansions:
            return f"{query} {' '.join(expansions)}"
        
        return query
    
    def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key domain concepts from query"""
        query_lower = query.lower()
        concepts = []
        
        # StreamWorks-specific concepts
        concept_keywords = {
            'data processing': ['batch', 'stream', 'data', 'processing'],
            'xml workflow': ['xml', 'schema', 'xsd'],
            'api integration': ['api', 'rest', 'endpoint'],
            'scheduling': ['schedule', 'cron', 'timer'],
            'configuration': ['config', 'settings', 'parameter']
        }
        
        for concept, keywords in concept_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                concepts.append(concept)
        
        return concepts
    
    def _convert_to_search_result(self, doc: Document, query: str, strategy: str) -> SearchResult:
        """Convert a Document to SearchResult (for fallback)"""
        return SearchResult(
            content=doc.page_content,
            score=0.5,  # Default score
            metadata=doc.metadata,
            explanation=f"Found using {strategy} search",
            chunk_type=doc.metadata.get('chunk_type', 'unknown'),
            document_type=doc.metadata.get('document_category', 'unknown'),
            file_format=doc.metadata.get('file_format', 'unknown'),
            processing_method=doc.metadata.get('processing_method', 'unknown'),
            relevance_factors=['Content match']
        )
    
    def _update_performance_stats(self, response_time: float):
        """Update performance statistics"""
        current_avg = self.search_stats['average_response_time']
        total_searches = self.search_stats['total_searches']
        
        # Calculate new average
        new_avg = ((current_avg * (total_searches - 1)) + response_time) / total_searches
        self.search_stats['average_response_time'] = new_avg
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get comprehensive search statistics"""
        return {
            **self.search_stats,
            'strategy_distribution': {
                strategy: count / self.search_stats['total_searches'] * 100
                for strategy, count in self.search_stats['strategy_usage'].items()
            } if self.search_stats['total_searches'] > 0 else {}
        }

# Global instance
smart_search_service = SmartSearchService()