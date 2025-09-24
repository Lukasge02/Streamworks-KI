# RAG Support System - Kontextuelle Wissensbasis

> **🧠 Knowledge-First:** Retrieval-Augmented Generation System mit Qdrant Vector Database für kontextuelle StreamWorks-Unterstützung

## **System-Philosophie**

Das RAG Support System ergänzt die LangExtract-Parameter-Extraktion um eine **intelligente Wissensbasis**, die Benutzern kontextuelle Hilfe und Expertise zur Verfügung stellt. Anstatt sich ausschließlich auf LLM-Parameterwissen zu verlassen, kombiniert das System externes, kuriertes Wissen mit generativen Fähigkeiten.

### **Design-Prinzipien**
- **External Knowledge First:** Verlässliches, kuriertes Wissen vor LLM-Halluzinationen
- **Source Grounding:** Jede Antwort mit verifizierbaren Dokumentenreferenzen
- **Hybrid Search:** Kombiniert semantische und lexikalische Suche
- **Real-time Indexing:** Dynamische Wissensbasis mit Live-Updates
- **Multi-Language Support:** Deutsche und englische Dokumentation

---

## **Architektur-Design**

### **RAG Pipeline Architecture**

```
Document Ingestion Pipeline
    ├── Layout-Aware Processing (Docling)
    ├── Semantic Chunking (Boundary Detection)
    ├── Embedding Generation (Gamma/OpenAI)
    └── Vector Storage (Qdrant)

Query Processing Pipeline
    ├── Query Understanding (Intent Classification)
    ├── Hybrid Retrieval (Vector + Lexical)
    ├── Context Consolidation (Relevant Chunks)
    ├── Response Generation (LLM + Sources)
    └── Source Citation (Document References)
```

### **Knowledge Base Structure**

```
Streamworks Knowledge Base
├── streamworks_documents/        # Haupt-Dokumente Collection
│   ├── User Manuals             # Benutzerhandbücher
│   ├── Technical Specifications # Technische Spezifikationen
│   ├── API Documentation        # API-Dokumentation
│   ├── Best Practices           # Best Practice Guides
│   └── Troubleshooting Guides   # Problemlösungsanleitungen
└── streamworks_hybrid/           # Hybrid Search Collection
    ├── FAQ Database             # Häufige Fragen
    ├── Code Examples            # Code-Beispiele
    └── Configuration Templates  # Konfigurationsvorlagen
```

---

## **Technische Implementierung**

### **1. Unified RAG Service**

**Core Orchestrator:**

```python
class UnifiedRAGService:
    """
    🧠 Unified RAG Service für kontextuelle StreamWorks-Unterstützung

    Kombiniert Vector Search, Hybrid Retrieval und Response Generation
    """

    def __init__(self,
                 vector_service: QdrantVectorService,
                 embedding_service: EmbeddingService,
                 llm_service: LLMService,
                 document_processor: DocumentProcessor):
        self.vector_service = vector_service
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.document_processor = document_processor

        # RAG Configuration
        self.retrieval_config = {
            'top_k': 5,                    # Top K ähnliche Dokumente
            'score_threshold': 0.7,        # Minimum Similarity Score
            'max_context_length': 4000,    # Maximum Context Tokens
            'hybrid_weight': 0.7           # Gewichtung Vector vs Lexical Search
        }

    async def query(self, question: str,
                   context: Optional[Dict] = None) -> RAGResponse:
        """
        🎯 Main RAG Query Processing

        1. Query Understanding & Intent Classification
        2. Hybrid Retrieval (Vector + Lexical)
        3. Context Consolidation & Ranking
        4. LLM Response Generation mit Source Grounding
        """

        # 1. Query Processing
        processed_query = await self._preprocess_query(question, context)

        # 2. Hybrid Retrieval
        retrieval_results = await self._hybrid_retrieval(processed_query)

        if not retrieval_results:
            return RAGResponse(
                answer="Entschuldigung, ich konnte keine relevanten Informationen finden.",
                sources=[],
                confidence=0.0,
                retrieval_method="no_results"
            )

        # 3. Context Consolidation
        consolidated_context = await self._consolidate_context(retrieval_results)

        # 4. Response Generation
        response = await self._generate_response(
            question=processed_query.original_question,
            context=consolidated_context,
            sources=retrieval_results
        )

        # 5. Post-processing & Source Attribution
        return await self._finalize_response(response, retrieval_results)
```

### **2. Hybrid Retrieval System**

**Vector + Lexical Search Combination:**

```python
class HybridRetrievalService:
    """
    🔍 Hybrid Retrieval: Vector Similarity + Lexical Matching

    Kombiniert semantische Suche mit keyword-basierter Suche
    für optimale Recall und Precision
    """

    async def hybrid_search(self, query: ProcessedQuery) -> List[RetrievalResult]:
        """
        Parallel Vector und Lexical Search mit Score Fusion
        """

        # Parallel Searches
        vector_task = asyncio.create_task(
            self._vector_search(query.embedding, query.expanded_terms)
        )
        lexical_task = asyncio.create_task(
            self._lexical_search(query.keywords, query.entities)
        )

        vector_results, lexical_results = await asyncio.gather(
            vector_task, lexical_task
        )

        # Score Fusion (Reciprocal Rank Fusion)
        fused_results = self._fuse_results(vector_results, lexical_results)

        # Re-ranking basierend auf Relevanz
        ranked_results = await self._rerank_results(fused_results, query)

        return ranked_results[:self.retrieval_config['top_k']]

    async def _vector_search(self, query_embedding: List[float],
                           expanded_terms: List[str]) -> List[VectorResult]:
        """Semantic Vector Search mit Query Expansion"""

        # Primary Vector Search
        primary_results = await self.vector_service.search(
            collection_name="streamworks_documents",
            query_vector=query_embedding,
            limit=self.retrieval_config['top_k'] * 2,  # Over-retrieve für Fusion
            score_threshold=self.retrieval_config['score_threshold']
        )

        # Query Expansion Search (für bessere Recall)
        expansion_results = []
        for term in expanded_terms:
            term_embedding = await self.embedding_service.embed_text(term)
            term_results = await self.vector_service.search(
                collection_name="streamworks_documents",
                query_vector=term_embedding,
                limit=3,
                score_threshold=0.8
            )
            expansion_results.extend(term_results)

        # Combine und deduplicate
        all_results = self._deduplicate_results(primary_results + expansion_results)
        return all_results

    async def _lexical_search(self, keywords: List[str],
                            entities: List[str]) -> List[LexicalResult]:
        """Keyword-based Search mit Entity Matching"""

        lexical_results = []

        # Exact Keyword Matching
        for keyword in keywords:
            keyword_results = await self.vector_service.search_by_keyword(
                collection_name="streamworks_hybrid",
                keyword=keyword,
                limit=5
            )
            lexical_results.extend(keyword_results)

        # Entity-based Search (für StreamWorks-spezifische Begriffe)
        for entity in entities:
            entity_results = await self.vector_service.search_by_metadata(
                collection_name="streamworks_documents",
                filter_conditions={"entity": entity},
                limit=3
            )
            lexical_results.extend(entity_results)

        return self._deduplicate_results(lexical_results)

    def _fuse_results(self, vector_results: List[VectorResult],
                     lexical_results: List[LexicalResult]) -> List[FusedResult]:
        """
        Reciprocal Rank Fusion für Score Kombination

        RRF Score = 1/(k + rank_vector) + 1/(k + rank_lexical)
        """

        rrf_constant = 60  # Standard RRF constant
        fused_scores = {}

        # Vector Results
        for rank, result in enumerate(vector_results, 1):
            doc_id = result.id
            vector_score = 1 / (rrf_constant + rank)
            fused_scores[doc_id] = {
                'vector_score': vector_score,
                'lexical_score': 0,
                'document': result.document,
                'metadata': result.metadata
            }

        # Lexical Results
        for rank, result in enumerate(lexical_results, 1):
            doc_id = result.id
            lexical_score = 1 / (rrf_constant + rank)

            if doc_id in fused_scores:
                fused_scores[doc_id]['lexical_score'] = lexical_score
            else:
                fused_scores[doc_id] = {
                    'vector_score': 0,
                    'lexical_score': lexical_score,
                    'document': result.document,
                    'metadata': result.metadata
                }

        # Calculate Final Scores
        hybrid_weight = self.retrieval_config['hybrid_weight']
        final_results = []

        for doc_id, scores in fused_scores.items():
            final_score = (hybrid_weight * scores['vector_score'] +
                          (1 - hybrid_weight) * scores['lexical_score'])

            final_results.append(FusedResult(
                id=doc_id,
                score=final_score,
                document=scores['document'],
                metadata=scores['metadata'],
                retrieval_details={
                    'vector_score': scores['vector_score'],
                    'lexical_score': scores['lexical_score'],
                    'fusion_method': 'RRF'
                }
            ))

        return sorted(final_results, key=lambda x: x.score, reverse=True)
```

### **3. Document Processing Pipeline**

**Layout-Aware Document Processing:**

```python
class DocumentProcessor:
    """
    📄 Advanced Document Processing mit Layout-Awareness

    Nutzt Docling für intelligente Dokumentenverarbeitung
    """

    def __init__(self):
        self.docling_processor = DoclingProcessor()
        self.chunk_size = 1000        # Optimal chunk size für RAG
        self.chunk_overlap = 200      # Overlap für Kontext-Preservation
        self.supported_formats = ['.pdf', '.docx', '.md', '.txt', '.html']

    async def process_document(self, file_path: str) -> DocumentProcessingResult:
        """
        📝 Complete Document Processing Pipeline

        1. Format Detection & Layout Analysis
        2. Content Extraction mit Structure Preservation
        3. Semantic Chunking mit Boundary Detection
        4. Metadata Extraction & Enhancement
        """

        # 1. File Format Detection
        file_format = self._detect_format(file_path)
        if file_format not in self.supported_formats:
            raise UnsupportedFormatError(f"Format not supported: {file_format}")

        # 2. Layout-Aware Content Extraction
        extraction_result = await self.docling_processor.extract_content(
            file_path=file_path,
            preserve_layout=True,
            extract_tables=True,
            extract_images=False  # Focus auf Text für RAG
        )

        # 3. Semantic Chunking
        chunks = await self._semantic_chunking(
            content=extraction_result.text,
            structure=extraction_result.structure,
            metadata=extraction_result.metadata
        )

        # 4. Chunk Enhancement
        enhanced_chunks = await self._enhance_chunks(chunks, file_path)

        return DocumentProcessingResult(
            chunks=enhanced_chunks,
            metadata=extraction_result.metadata,
            processing_stats={
                'total_chunks': len(enhanced_chunks),
                'avg_chunk_size': sum(len(c.text) for c in enhanced_chunks) / len(enhanced_chunks),
                'processing_time': time.time() - start_time
            }
        )

    async def _semantic_chunking(self, content: str, structure: DocumentStructure,
                               metadata: Dict) -> List[DocumentChunk]:
        """
        🧩 Intelligent Semantic Chunking

        Berücksichtigt Document Structure für optimale Chunk-Boundaries
        """

        chunks = []

        # Struktur-basierte Chunking (Sections, Paragraphs)
        if structure.sections:
            for section in structure.sections:
                section_chunks = self._chunk_section(section, metadata)
                chunks.extend(section_chunks)
        else:
            # Fallback: Sliding Window Chunking
            sliding_chunks = self._sliding_window_chunking(content)
            chunks.extend(sliding_chunks)

        # Post-processing: Merge zu kleine Chunks
        optimized_chunks = self._optimize_chunk_sizes(chunks)

        return optimized_chunks

    def _chunk_section(self, section: DocumentSection,
                      metadata: Dict) -> List[DocumentChunk]:
        """Chunk eine Document Section mit Context Preservation"""

        section_text = section.text
        section_title = section.title or "Untitled Section"

        # Split section in Paragraphs
        paragraphs = section_text.split('\n\n')
        current_chunk = ""
        chunks = []

        for paragraph in paragraphs:
            # Check ob hinzufügen würde chunk_size überschreiten
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph

            if len(potential_chunk.split()) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                # Finalize current chunk
                if current_chunk:
                    chunks.append(DocumentChunk(
                        text=current_chunk,
                        metadata={
                            **metadata,
                            'section_title': section_title,
                            'chunk_type': 'section_chunk',
                            'word_count': len(current_chunk.split())
                        }
                    ))

                # Start new chunk
                current_chunk = paragraph

        # Add final chunk
        if current_chunk:
            chunks.append(DocumentChunk(
                text=current_chunk,
                metadata={
                    **metadata,
                    'section_title': section_title,
                    'chunk_type': 'section_chunk',
                    'word_count': len(current_chunk.split())
                }
            ))

        return chunks
```

### **4. Response Generation mit Source Grounding**

**LLM Response Generation mit Source Attribution:**

```python
class ResponseGenerator:
    """
    💬 Source-Grounded Response Generation

    Generiert Antworten mit verifizierbaren Quellenreferenzen
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

        # Response Templates für verschiedene Query-Types
        self.response_templates = {
            'how_to': """
                Basierend auf der StreamWorks-Dokumentation, hier ist eine Schritt-für-Schritt-Anleitung:

                {response}

                **Quellen:**
                {sources}
            """,
            'configuration': """
                Für die StreamWorks-Konfiguration gibt es folgende Optionen:

                {response}

                **Referenzen:**
                {sources}
            """,
            'troubleshooting': """
                Zur Lösung dieses Problems in StreamWorks:

                {response}

                **Weitere Informationen:**
                {sources}
            """,
            'default': """
                {response}

                **Quellen:**
                {sources}
            """
        }

    async def generate_response(self, question: str,
                              context: ConsolidatedContext,
                              sources: List[RetrievalResult]) -> RAGResponse:
        """
        🎯 Generate Source-Grounded Response

        Creates LLM response mit explicit source citations
        """

        # 1. Query Type Classification
        query_type = await self._classify_query_type(question)

        # 2. Build Context-Aware Prompt
        system_prompt = self._build_system_prompt(query_type)
        context_prompt = self._build_context_prompt(context, sources)

        prompt = f"""
        {system_prompt}

        **Kontext aus StreamWorks-Dokumentation:**
        {context_prompt}

        **Benutzerfrage:**
        {question}

        **Anweisungen:**
        - Beantworte die Frage basierend auf dem bereitgestellten Kontext
        - Verwende spezifische Informationen aus den Quelldokumenten
        - Stelle sicher, dass die Antwort faktisch korrekt ist
        - Erwähne konkrete StreamWorks-Features und Konfigurationen
        - Falls der Kontext unvollständig ist, sage es ehrlich
        """

        # 3. LLM Response Generation
        llm_response = await self.llm_service.generate_response(
            prompt=prompt,
            max_tokens=800,
            temperature=0.3,  # Niedrige Temperatur für faktische Korrektheit
            stop_sequences=["**Quellen:**", "**Referenzen:**"]
        )

        # 4. Source Attribution
        source_citations = self._generate_source_citations(sources)

        # 5. Apply Response Template
        template = self.response_templates.get(query_type, self.response_templates['default'])
        formatted_response = template.format(
            response=llm_response.text,
            sources=source_citations
        )

        # 6. Quality Assessment
        quality_score = await self._assess_response_quality(
            question, formatted_response, context, sources
        )

        return RAGResponse(
            answer=formatted_response,
            sources=sources,
            confidence=quality_score,
            retrieval_method="hybrid_search",
            query_type=query_type,
            generation_metadata={
                'llm_tokens_used': llm_response.tokens_used,
                'context_length': len(context_prompt),
                'sources_count': len(sources),
                'quality_score': quality_score
            }
        )

    def _build_system_prompt(self, query_type: str) -> str:
        """Build query-type specific system prompt"""

        base_prompt = """
        Du bist ein Experte für StreamWorks Workload-Automatisierung. Du hilfst Benutzern dabei,
        StreamWorks zu verstehen und zu konfigurieren.

        **Deine Expertise umfasst:**
        - StreamWorks Stream-Konfiguration und -Design
        - Job-Orchestrierung und Scheduling
        - Agent-Management und File-Transfer
        - SAP-Integration und Report-Automation
        - Troubleshooting und Best Practices
        """

        query_specific = {
            'how_to': "Fokussiere auf klare, umsetzbare Anleitungen mit konkreten Schritten.",
            'configuration': "Erkläre Konfigurationsoptionen und deren Auswirkungen detailliert.",
            'troubleshooting': "Biete systematische Problemlösungsansätze und Diagnosehilfen.",
            'default': "Beantworte die Frage umfassend und strukturiert."
        }

        return f"{base_prompt}\n\n{query_specific.get(query_type, query_specific['default'])}"

    def _generate_source_citations(self, sources: List[RetrievalResult]) -> str:
        """Generate formatted source citations"""

        citations = []
        for i, source in enumerate(sources, 1):
            metadata = source.metadata
            document_name = metadata.get('document_name', 'Unbekanntes Dokument')
            section = metadata.get('section_title', '')
            page = metadata.get('page_number', '')

            citation_parts = [f"{i}. {document_name}"]
            if section:
                citation_parts.append(f"Section: {section}")
            if page:
                citation_parts.append(f"Seite {page}")

            citations.append(" - ".join(citation_parts))

        return "\n".join(citations)

    async def _assess_response_quality(self, question: str, response: str,
                                     context: ConsolidatedContext,
                                     sources: List[RetrievalResult]) -> float:
        """
        📊 Response Quality Assessment

        Bewertet die Qualität der generierten Antwort
        """

        quality_factors = {
            'context_usage': 0.3,      # Wie gut wurde der Kontext genutzt?
            'source_grounding': 0.3,   # Sind Aussagen in Sources begründet?
            'completeness': 0.2,       # Ist die Antwort vollständig?
            'relevance': 0.2          # Ist die Antwort relevant zur Frage?
        }

        scores = {}

        # Context Usage Score
        context_keywords = set(context.consolidated_text.lower().split())
        response_keywords = set(response.lower().split())
        context_overlap = len(context_keywords & response_keywords) / len(context_keywords)
        scores['context_usage'] = min(context_overlap * 2, 1.0)  # Max 1.0

        # Source Grounding Score (Simple heuristic)
        source_terms = []
        for source in sources:
            source_terms.extend(source.document.text.lower().split())
        source_keywords = set(source_terms)

        grounding_overlap = len(source_keywords & response_keywords) / max(len(response_keywords), 1)
        scores['source_grounding'] = min(grounding_overlap * 3, 1.0)

        # Completeness Score (basierend auf Antwortlänge)
        ideal_length = 200  # Wörter
        response_length = len(response.split())
        completeness = min(response_length / ideal_length, 1.0)
        scores['completeness'] = completeness

        # Relevance Score (Simple keyword matching)
        question_keywords = set(question.lower().split())
        relevance = len(question_keywords & response_keywords) / len(question_keywords)
        scores['relevance'] = relevance

        # Weighted Final Score
        final_score = sum(scores[factor] * weight
                         for factor, weight in quality_factors.items())

        return final_score
```

---

## **Performance Optimizations**

### **1. Advanced Caching Strategy**

```python
class MultiLevelRAGCache:
    """
    ⚡ Multi-Level Caching für RAG Performance

    - Embedding Cache: Wiederverwendung von Query Embeddings
    - Semantic Cache: Ähnliche Fragen mit cached Antworten
    - Response Cache: Complete Response Caching mit TTL
    """

    def __init__(self):
        # Embedding Cache (2500 items, 4h TTL)
        self.embedding_cache = TTLCache(maxsize=2500, ttl=14400)

        # Semantic Cache (500 items, 2h TTL)
        self.semantic_cache = TTLCache(maxsize=500, ttl=7200)

        # Response Cache (LRU-based)
        self.response_cache = LRUCache(maxsize=1000)

    async def get_cached_response(self, question: str,
                                context_hash: str) -> Optional[RAGResponse]:
        """Check for cached response mit semantic similarity"""

        # 1. Exact match cache
        exact_key = f"{question}:{context_hash}"
        if exact_key in self.response_cache:
            return self.response_cache[exact_key]

        # 2. Semantic similarity cache
        question_embedding = await self._get_cached_embedding(question)

        for cached_question, cached_response in self.semantic_cache.items():
            similarity = self._calculate_semantic_similarity(
                question_embedding, cached_question['embedding']
            )

            if similarity >= 0.95:  # High similarity threshold
                logger.info(f"🎯 Semantic cache hit: similarity {similarity:.3f}")
                return cached_response

        return None

    async def cache_response(self, question: str, context_hash: str,
                           response: RAGResponse):
        """Cache response mit multiple cache levels"""

        # 1. Exact response cache
        exact_key = f"{question}:{context_hash}"
        self.response_cache[exact_key] = response

        # 2. Semantic cache
        question_embedding = await self._get_cached_embedding(question)
        self.semantic_cache[question] = {
            'embedding': question_embedding,
            'response': response,
            'timestamp': time.time()
        }

    async def _get_cached_embedding(self, text: str) -> List[float]:
        """Get cached embedding oder generate new"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        embedding = await self.embedding_service.embed_text(text)
        self.embedding_cache[text] = embedding
        return embedding
```

### **2. Adaptive Retrieval Configuration**

```python
class AdaptiveRetrievalConfig:
    """
    🎛️ Adaptive Retrieval Configuration

    Passt Retrieval-Parameter basierend auf Query-Typ und Performance an
    """

    def __init__(self):
        self.base_config = {
            'top_k': 5,
            'score_threshold': 0.7,
            'hybrid_weight': 0.7
        }

        # Query-Type spezifische Konfigurationen
        self.query_type_configs = {
            'technical_config': {
                'top_k': 8,              # Mehr Technical Details
                'score_threshold': 0.6,   # Niedrigerer Threshold
                'hybrid_weight': 0.8      # Mehr Vector Search
            },
            'troubleshooting': {
                'top_k': 7,
                'score_threshold': 0.75,
                'hybrid_weight': 0.6      # Mehr Keyword Search
            },
            'how_to': {
                'top_k': 6,
                'score_threshold': 0.7,
                'hybrid_weight': 0.7
            }
        }

        # Performance-basierte Anpassungen
        self.performance_metrics = {
            'avg_response_time': 0.0,
            'cache_hit_rate': 0.0,
            'user_satisfaction': 0.0
        }

    def get_config_for_query(self, query_type: str,
                           current_performance: Dict) -> Dict:
        """
        🎯 Get optimized config für Query-Type und Performance

        Passt Konfiguration basierend auf aktueller Performance an
        """

        # Base configuration
        config = self.query_type_configs.get(query_type, self.base_config).copy()

        # Performance-basierte Anpassungen
        if current_performance.get('avg_response_time', 0) > 3.0:
            # Zu langsam → reduziere top_k
            config['top_k'] = max(config['top_k'] - 2, 3)
            logger.info(f"🐌 Reduced top_k due to slow response time")

        if current_performance.get('cache_hit_rate', 0) < 0.3:
            # Niedrige Cache Hit Rate → erhöhe score_threshold
            config['score_threshold'] = min(config['score_threshold'] + 0.1, 0.9)
            logger.info(f"📈 Increased threshold due to low cache hit rate")

        if current_performance.get('user_satisfaction', 0) < 0.7:
            # Niedrige User Satisfaction → mehr Dokumente abrufen
            config['top_k'] = min(config['top_k'] + 2, 12)
            config['score_threshold'] = max(config['score_threshold'] - 0.05, 0.5)
            logger.info(f"😞 Adjusted config due to low user satisfaction")

        return config
```

---

## **Integration mit LangExtract System**

### **Contextual Help während Parameter Extraction**

```python
class ContextualRAGHelper:
    """
    🤝 Contextual RAG Integration mit LangExtract System

    Bietet kontextuelle Hilfe während der Parameter-Extraktion
    """

    async def get_contextual_help(self, session: StreamWorksSession,
                                current_parameter: str) -> Optional[RAGResponse]:
        """
        💡 Contextual Help basierend auf aktuellem Parameter

        Bietet automatische Hilfe für schwierige Parameter
        """

        if not current_parameter:
            return None

        # Parameter-spezifische Help Queries
        help_queries = {
            'source_agent': "Wie konfiguriere ich Source Agents in StreamWorks?",
            'target_agent': "Wie definiere ich Target Agents für File Transfer?",
            'sap_system': "Welche SAP System Identifier sind verfügbar?",
            'sap_report': "Wie finde ich den korrekten SAP Report Namen?",
            'start_time': "Welche Zeitformate unterstützt StreamWorks Scheduling?",
            'calendar_id': "Welche Kalender sind in StreamWorks verfügbar?"
        }

        query = help_queries.get(current_parameter)
        if not query:
            return None

        # Contextual Query mit Job-Type Context
        contextual_query = f"{query} (Job-Type: {session.detected_job_type})"

        # RAG Query
        response = await self.rag_service.query(
            question=contextual_query,
            context={'job_type': session.detected_job_type, 'session_id': session.session_id}
        )

        # Add contextual metadata
        response.generation_metadata['context_type'] = 'parameter_help'
        response.generation_metadata['parameter'] = current_parameter
        response.generation_metadata['job_type'] = session.detected_job_type

        return response

    async def get_parameter_suggestions(self, session: StreamWorksSession,
                                      parameter: str) -> List[str]:
        """
        💭 Get parameter value suggestions basierend auf Knowledge Base
        """

        suggestion_queries = {
            'source_agent': "Liste verfügbare StreamWorks Agents",
            'target_agent': "Liste verfügbare StreamWorks Agents",
            'sap_system': "Liste verfügbare SAP Systeme",
            'calendar_id': "Liste verfügbare StreamWorks Kalender"
        }

        query = suggestion_queries.get(parameter)
        if not query:
            return []

        response = await self.rag_service.query(question=query)

        # Extract suggestions from response
        suggestions = self._extract_suggestions(response.answer)
        return suggestions[:5]  # Top 5 suggestions

    def _extract_suggestions(self, response_text: str) -> List[str]:
        """Extract structured suggestions from RAG response"""
        # Simple regex-based extraction
        # In production: Use more sophisticated NLP

        patterns = [
            r'- ([\w_]+)',        # List items
            r'• ([\w_]+)',        # Bullet points
            r'\d+\. ([\w_]+)',    # Numbered lists
            r'"([^"]+)"',         # Quoted strings
            r'`([^`]+)`'          # Code blocks
        ]

        suggestions = []
        for pattern in patterns:
            matches = re.findall(pattern, response_text)
            suggestions.extend(matches)

        # Deduplicate und filter
        unique_suggestions = list(set(suggestions))
        return [s for s in unique_suggestions if len(s) > 2 and len(s) < 50]
```

---

## **Monitoring & Analytics**

### **RAG Performance Metrics**

```python
@dataclass
class LiveRAGMetrics:
    """📊 Real-time RAG Performance Metrics"""

    # Performance Metrics
    response_time_ms: float
    retrieval_count: int
    cache_hit_rate: float
    embedding_generation_time: float
    llm_response_time: float

    # Quality Metrics
    source_quality_score: float      # Qualität der abgerufenen Quellen
    response_relevance_score: float  # Relevanz der generierten Antwort
    user_satisfaction_score: float   # User Feedback Score
    source_citation_accuracy: float  # Genauigkeit der Quellenangaben

    # Usage Metrics
    query_type_distribution: Dict[str, int]
    top_queried_topics: List[str]
    retrieval_method_usage: Dict[str, int]
    knowledge_base_coverage: float

    # Error Metrics
    retrieval_failure_rate: float
    llm_error_rate: float
    context_overflow_rate: float

class RAGMetricsCollector:
    """📈 Comprehensive RAG Metrics Collection"""

    def __init__(self, rag_service: UnifiedRAGService):
        self.rag_service = rag_service
        self.metrics_history = []
        self.collection_interval = 60  # seconds

    async def collect_live_metrics(self) -> LiveRAGMetrics:
        """Collect real-time RAG performance metrics"""

        # Performance Metrics
        response_times = await self._get_recent_response_times()
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        cache_stats = await self._get_cache_statistics()
        retrieval_stats = await self._get_retrieval_statistics()

        # Quality Metrics
        quality_scores = await self._calculate_quality_metrics()
        usage_stats = await self._get_usage_statistics()

        return LiveRAGMetrics(
            response_time_ms=avg_response_time,
            cache_hit_rate=cache_stats['hit_rate'],
            source_quality_score=quality_scores['source_quality'],
            user_satisfaction_score=quality_scores['user_satisfaction'],
            query_type_distribution=usage_stats['query_types'],
            retrieval_failure_rate=retrieval_stats['failure_rate'],
            # ... weitere Metriken
        )

    async def generate_performance_report(self, timeframe: str = '24h') -> PerformanceReport:
        """Generate comprehensive performance report"""

        metrics_data = await self._get_historical_metrics(timeframe)

        report = PerformanceReport(
            timeframe=timeframe,
            total_queries=len(metrics_data),
            avg_response_time=self._calculate_average(metrics_data, 'response_time_ms'),
            cache_efficiency=self._calculate_average(metrics_data, 'cache_hit_rate'),
            quality_trend=self._calculate_trend(metrics_data, 'source_quality_score'),
            top_performance_issues=self._identify_performance_issues(metrics_data),
            recommendations=self._generate_recommendations(metrics_data)
        )

        return report

    def _generate_recommendations(self, metrics_data: List[Dict]) -> List[str]:
        """Generate performance optimization recommendations"""

        recommendations = []

        # Slow response time
        avg_response_time = self._calculate_average(metrics_data, 'response_time_ms')
        if avg_response_time > 2000:
            recommendations.append(
                f"⚡ Response time optimization needed: {avg_response_time:.0f}ms average. "
                "Consider increasing cache size or reducing top_k."
            )

        # Low cache hit rate
        cache_hit_rate = self._calculate_average(metrics_data, 'cache_hit_rate')
        if cache_hit_rate < 0.4:
            recommendations.append(
                f"🎯 Cache optimization needed: {cache_hit_rate:.1%} hit rate. "
                "Consider tuning semantic similarity threshold."
            )

        # Low source quality
        source_quality = self._calculate_average(metrics_data, 'source_quality_score')
        if source_quality < 0.7:
            recommendations.append(
                f"📚 Knowledge base quality improvement needed: {source_quality:.1%}. "
                "Consider updating document chunks or embedding model."
            )

        return recommendations
```

---

## **Fazit**

Das RAG Support System stellt eine **intelligente, externe Wissensbasis** dar, die das LangExtract System um kontextuelle Unterstützung erweitert.

### **Key Innovations:**

**🧠 Hybrid Intelligence:**
- **External Knowledge First** - Verifizierbares Wissen vor LLM-Halluzinationen
- **Source Grounding** - Jede Antwort mit nachvollziehbaren Dokumentenreferenzen
- **Semantic + Lexical Search** - Optimale Balance zwischen Recall und Precision

**⚡ Performance Excellence:**
- **Multi-Level Caching** - Embedding, Semantic und Response Caching
- **Adaptive Configuration** - Performance-basierte Parameter-Optimierung
- **Sub-2-Second Response Times** für die meisten Queries

**🔧 Enterprise Integration:**
- **Contextual Help** - Automatische Unterstützung während Parameter-Extraction
- **Parameter Suggestions** - Intelligente Vorschläge basierend auf Knowledge Base
- **Real-time Monitoring** - Comprehensive Performance und Quality Metrics

### **Production Benefits:**

Das RAG System **reduziert Support-Aufwand** und **erhöht User-Autonomie**:
- **Instant Support** - 24/7 verfügbare Expertise ohne menschliche Intervention
- **Consistent Quality** - Gleichbleibende Antwortqualität basierend auf kurierter Wissensbasis
- **Scalable Knowledge** - Einfache Erweiterung durch neue Dokumente
- **Audit Trail** - Vollständige Nachverfolgbarkeit aller Antworten zu Quellen

Das System bildet den **Support-Layer** der StreamWorks-KI Lösung und ermöglicht Fachanwendern eine **selbstständige, expertensystemgestützte** Nutzung der Workload-Automatisierung.