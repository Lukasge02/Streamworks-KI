"""
LlamaIndex Query Service

Enhanced RAG retrieval with:
- Vector similarity search via existing VectorStore
- Cross-encoder reranking for improved precision
- LlamaIndex LLM for response synthesis
- Confidence scoring
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from config import config
from .settings import LlamaIndexSettings, configure_llamaindex


@dataclass
class QueryResult:
    """Structured query result"""
    answer: str
    sources: List[Dict[str, Any]]
    has_context: bool
    chunks_found: int
    confidence: float
    confidence_level: str
    query_type: str
    warnings: List[str]
    reranked: bool = False


class QueryService:
    """
    Query Service for RAG Retrieval
    
    Uses the existing VectorStore for retrieval (compatible with current schema)
    and LlamaIndex LLM for response generation.
    
    Features:
    - Vector similarity search
    - Cross-encoder reranking (optional, configurable)
    - Confidence scoring
    - Query classification
    """
    
    # System prompt for RAG
    RAG_SYSTEM_PROMPT = """Du bist ein hilfreicher Assistent für StreamWorks und beantwortest Fragen 
basierend auf den bereitgestellten Dokumenten. Beantworte Fragen präzise und nutze 
die Informationen aus dem Kontext. Wenn du die Antwort nicht im Kontext findest, 
sage es ehrlich.

Formatiere deine Antworten klar und strukturiert. Verwende Aufzählungen wo sinnvoll."""

    def __init__(self, use_reranking: bool = None, use_cache: bool = True):
        configure_llamaindex()
        self._vector_store = None
        self._reranker = None
        self._cache = None
        # Use config if not explicitly set
        self._use_reranking = use_reranking if use_reranking is not None else config.RAG_RERANK_ENABLED
        self._use_cache = use_cache
    
    @property
    def vector_store(self):
        """Use existing VectorStore for retrieval (backward compatible with 'content' field)"""
        if self._vector_store is None:
            from services.rag.vector_store import vector_store
            self._vector_store = vector_store
        return self._vector_store
    
    @property
    def reranker(self):
        """Lazy-loaded reranker"""
        if self._reranker is None and self._use_reranking:
            from services.rag.reranker import CrossEncoderReranker
            self._reranker = CrossEncoderReranker(use_batch_mode=True)
        return self._reranker
    
    @property
    def cache(self):
        """Lazy-loaded RAG cache"""
        if self._cache is None and self._use_cache:
            from services.rag.cache import rag_cache
            self._cache = rag_cache
        return self._cache
    
    @property
    def hybrid_search(self):
        """Lazy-loaded hybrid search engine"""
        if not hasattr(self, '_hybrid_search'):
            self._hybrid_search = None
        if self._hybrid_search is None:
            from services.rag.hybrid_search import hybrid_search
            self._hybrid_search = hybrid_search
        return self._hybrid_search
    
    def query(
        self,
        query_text: str,
        top_k: int = None,
        score_threshold: float = None,
        filters: Dict[str, Any] = None,
        doc_ids: List[str] = None,
        use_reranking: bool = None,
        use_hybrid: bool = None,
    ) -> QueryResult:
        """
        Execute a RAG query
        
        Args:
            query_text: User's question
            top_k: Number of chunks to retrieve
            score_threshold: Minimum similarity score
            filters: Metadata filters (category, access control)
            doc_ids: Specific document IDs to search (for access control)
            use_reranking: Override default reranking setting
            use_hybrid: Use hybrid search (vector + keyword) - default True
            
        Returns:
            QueryResult with answer, sources, and metadata
        """
        top_k = top_k or LlamaIndexSettings.TOP_K
        score_threshold = score_threshold or LlamaIndexSettings.SIMILARITY_THRESHOLD
        should_rerank = use_reranking if use_reranking is not None else self._use_reranking
        should_use_hybrid = use_hybrid if use_hybrid is not None else config.RAG_HYBRID_ENABLED
        
        # Build access filter for doc_ids
        access_filter = None
        if doc_ids:
            access_filter = {"parent_doc_ids": doc_ids}
        
        # Retrieve more candidates if reranking (typical pattern: retrieve 3x, rerank to top_k)
        retrieval_k = top_k * 3 if should_rerank else top_k
        
        # Choose search method: Hybrid (semantic + keyword) or pure semantic
        if should_use_hybrid:
            # Use hybrid search with RRF (Reciprocal Rank Fusion)
            results = self.hybrid_search.search(
                query=query_text,
                limit=retrieval_k,
                score_threshold=score_threshold * 0.7 if should_rerank else score_threshold,
                filters=filters,
            )
            # Convert SearchResult objects to dicts
            retrieved_chunks = [
                {
                    "doc_id": r.doc_id,
                    "content": r.content,
                    "filename": r.filename,
                    "score": r.score,
                    "metadata": r.metadata,
                }
                for r in results
            ]
        else:
            # Use pure semantic search (VectorStore)
            retrieved_chunks = self.vector_store.search(
                query=query_text,
                limit=retrieval_k,
                score_threshold=score_threshold * 0.7 if should_rerank else score_threshold,
                filters=filters,
                access_filter=access_filter,
            )
        
        # Check if we have context
        has_context = len(retrieved_chunks) > 0
        
        if not has_context:
            return QueryResult(
                answer="Ich konnte keine relevanten Informationen in den Dokumenten finden. "
                       "Bitte stelle eine andere Frage oder lade relevante Dokumente hoch.",
                sources=[],
                has_context=False,
                chunks_found=0,
                confidence=0.0,
                confidence_level="no_context",
                query_type="unknown",
                warnings=["Keine relevanten Dokumente gefunden"],
                reranked=False,
            )
        
        # Apply reranking if enabled
        reranked = False
        if should_rerank and self.reranker:
            try:
                ranked_results = self.reranker.rerank(
                    query=query_text,
                    results=retrieved_chunks,
                    top_k=top_k,
                )
                # Convert RankedResult back to dict format
                retrieved_chunks = [
                    {
                        "doc_id": r.doc_id,
                        "content": r.content,
                        "filename": r.filename,
                        "score": r.rerank_score,
                        "original_score": r.original_score,
                        "metadata": r.metadata,
                        "relevance_explanation": r.relevance_explanation,
                    }
                    for r in ranked_results
                ]
                reranked = True
            except Exception as e:
                print(f"⚠️ Reranking failed, using original order: {e}")
        else:
            # Limit to top_k if not reranking
            retrieved_chunks = retrieved_chunks[:top_k]
        
        # === RELEVANCE CHECK ===
        # Check if the results are actually relevant to the query
        # Even if we found documents, they might not answer the question
        is_truly_relevant = self._check_relevance(retrieved_chunks, query_text)
        
        if not is_truly_relevant:
            return QueryResult(
                answer="Zu dieser Frage habe ich leider keine passenden Informationen in den "
                       "verfügbaren Dokumenten gefunden. Die Frage bezieht sich möglicherweise auf "
                       "ein Thema, das nicht in der Dokumentation behandelt wird.",
                sources=[],
                has_context=False,
                chunks_found=0,
                confidence=0.0,
                confidence_level="no_relevant_context",
                query_type=self._classify_query(query_text),
                warnings=["Keine relevanten Informationen für diese spezifische Frage gefunden"],
                reranked=reranked,
            )
        
        # Build context from chunks
        context = self._build_context(retrieved_chunks)
        
        # Generate response using LlamaIndex LLM
        answer = self._generate_response(query_text, context)
        
        # Extract sources
        sources = self._extract_sources(retrieved_chunks)
        
        # Calculate confidence
        confidence, confidence_level = self._calculate_confidence(retrieved_chunks, reranked)
        
        # Classify query type
        query_type = self._classify_query(query_text)
        
        return QueryResult(
            answer=answer,
            sources=sources,
            has_context=has_context,
            chunks_found=len(retrieved_chunks),
            confidence=confidence,
            confidence_level=confidence_level,
            query_type=query_type,
            warnings=[],
            reranked=reranked,
        )
    
    def retrieve_only(
        self,
        query_text: str,
        top_k: int = None,
        filters: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks without generating a response
        
        Useful for inspection or custom processing
        """
        top_k = top_k or LlamaIndexSettings.TOP_K
        
        chunks = self.vector_store.search(
            query=query_text,
            limit=top_k,
            score_threshold=0.0,
            filters=filters,
        )
        
        return [
            {
                "content": chunk.get("content", ""),
                "score": chunk.get("score", 0),
                "metadata": chunk.get("metadata", {}),
            }
            for chunk in chunks
        ]
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            metadata = chunk.get("metadata", {})
            filename = chunk.get("filename") or metadata.get("filename", "Unbekannt")
            chunk_idx = metadata.get("chunk_index", 0)
            content = chunk.get("content", "")
            
            context_parts.append(
                f"[Quelle {i+1}: {filename} (Abschnitt {chunk_idx + 1})]:\n{content}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str) -> str:
        """Generate response using LlamaIndex LLM"""
        from llama_index.core.llms import ChatMessage
        
        llm = LlamaIndexSettings.get_llm()
        
        messages = [
            ChatMessage(role="system", content=self.RAG_SYSTEM_PROMPT),
            ChatMessage(
                role="user",
                content=f"""Basierend auf folgendem Kontext, beantworte die Frage.

KONTEXT:
{context}

FRAGE: {query}

ANTWORT:"""
            ),
        ]
        
        response = llm.chat(messages)
        return response.message.content
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from chunks"""
        sources = []
        
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            content = chunk.get("content", "")
            sources.append({
                "doc_id": meta.get("parent_doc_id") or chunk.get("doc_id") or meta.get("doc_id"),
                "filename": chunk.get("filename") or meta.get("filename", "Unbekannt"),
                "content": content[:500] + "..." if len(content) > 500 else content,
                "score": round(chunk.get("score", 0), 4),
                "chunk_index": meta.get("chunk_index", 0),
                "category": meta.get("category"),
                "relevance_explanation": chunk.get("relevance_explanation"),
            })
        
        return sources
    
    def _check_relevance(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
    ) -> bool:
        """
        Check if retrieved chunks are actually relevant to the query.
        
        The key insight: If the query is about an external technology/tool
        that we don't cover, the results are NOT relevant.
        
        Returns True if results appear relevant, False otherwise.
        """
        if not chunks:
            return False
        
        query_lower = query.lower()
        
        # First: Check if query is about external technologies we don't cover
        external_tech = [
            "kubernetes", "k8s", "docker", "aws", "amazon", "azure", "gcp", "google cloud",
            "terraform", "ansible", "jenkins", "gitlab", "github actions", "jira", "confluence",
            "kafka", "elasticsearch", "mongodb", "mysql", "oracle", "spark", "hadoop",
            "airflow", "mlflow", "grafana", "prometheus", "datadog", "splunk",
            "salesforce", "sap", "servicenow", "tableau", "powerbi", "looker",
            "snowflake", "databricks", "dbt", "fivetran", "airbyte"
        ]
        
        # Check if query contains external tech
        query_has_external_tech = any(tech in query_lower for tech in external_tech)
        
        if query_has_external_tech:
            # Check if this external tech is mentioned in our documents
            content_text = " ".join(c.get("content", "").lower() for c in chunks[:3])
            
            for tech in external_tech:
                if tech in query_lower:
                    # This tech is asked about - is it in our docs?
                    if tech not in content_text:
                        # External tech not covered in our docs
                        return False
        
        # For non-external-tech queries, check keyword overlap
        import re
        # Clean query: remove punctuation and split
        query_clean = re.sub(r'[^\w\s]', '', query_lower)
        query_words = query_clean.split()
        
        # Common stopwords
        stopwords = {
            "was", "wie", "ist", "ein", "eine", "der", "die", "das", "und", "oder", 
            "für", "mit", "in", "zu", "bei", "ich", "du", "wir", "sie", "es", "wird", 
            "werden", "kann", "können", "muss", "müssen", "soll", "hat", "haben", 
            "sind", "sein", "wenn", "dann", "auch", "noch", "schon", "aber", "nur", 
            "nicht", "alle", "diese", "dieser", "dieses", "welche", "welcher", "welches",
            "gibt", "mache", "machen", "tue", "tun", "geht", "gehen", "bitte", "danke",
            "mir", "mich", "dir", "dich", "ihm", "ihr", "uns", "euch", "ihnen",
            "integriere", "integrieren", "verwende", "verwenden", "nutze", "nutzen",
            "erkläre", "erklären", "beschreibe", "beschreiben", "zeige", "zeigen",
            "funktioniert", "funktionieren", "arbeitet", "arbeiten"
        }
        
        # Get non-stopword keywords
        keywords = [w for w in query_words if w not in stopwords and len(w) >= 3]
        
        if not keywords:
            return True  # No clear keywords - assume relevant
        
        # Check how many keywords appear in content
        content_text = " ".join(c.get("content", "").lower() for c in chunks[:5])
        found_count = sum(1 for kw in keywords if kw in content_text)
        
        # Need at least 30% of keywords to be relevant
        return found_count >= max(1, len(keywords) * 0.3)
    
    def _calculate_confidence(
        self,
        chunks: List[Dict[str, Any]],
        reranked: bool = False,
    ) -> tuple[float, str]:
        """Calculate confidence score based on retrieval results"""
        if not chunks:
            return 0.0, "no_context"
        
        # Average score of top results
        scores = [c.get("score", 0) for c in chunks]
        avg_score = sum(scores) / len(scores)
        
        # Boost if multiple high-scoring results
        high_score_count = sum(1 for s in scores if s > 0.7)
        
        # Base confidence from similarity
        confidence = min(avg_score * 1.2, 1.0)
        
        # Boost for multiple supporting sources
        if high_score_count >= 3:
            confidence = min(confidence * 1.1, 1.0)
        
        # Boost if reranked (more trustworthy)
        if reranked:
            confidence = min(confidence * 1.05, 1.0)
        
        # Determine level
        if confidence >= 0.8:
            level = "high"
        elif confidence >= 0.5:
            level = "medium"
        else:
            level = "low"
        
        return round(confidence, 3), level
    
    def _classify_query(self, query: str) -> str:
        """Classify query type"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["wie", "how", "anleitung", "schritt"]):
            return "how_to"
        elif any(word in query_lower for word in ["config", "konfigur", "einstell", "parameter"]):
            return "configuration"
        elif any(word in query_lower for word in ["fehler", "problem", "error", "fix", "lösung"]):
            return "troubleshooting"
        elif any(word in query_lower for word in ["was ist", "what is", "erkläre", "explain"]):
            return "explanation"
        else:
            return "general"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        stats = {
            "reranking_enabled": self._use_reranking,
            "hybrid_search_enabled": config.RAG_HYBRID_ENABLED,
            "caching_enabled": self._use_cache,
        }
        
        if self.reranker:
            stats["reranker"] = self.reranker.get_stats()
        
        if self.cache:
            stats["cache"] = self.cache.get_stats()
        
        if config.RAG_HYBRID_ENABLED:
            try:
                stats["hybrid_search"] = self.hybrid_search.get_stats()
            except Exception:
                pass
        
        return stats


# Singleton instance
_query_service: Optional[QueryService] = None


def get_query_service() -> QueryService:
    """Get singleton QueryService instance"""
    global _query_service
    if _query_service is None:
        _query_service = QueryService()
    return _query_service
