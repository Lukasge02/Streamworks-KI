"""
RAG Service for StreamWorks-KI Q&A System
Uses ChromaDB + LangChain + Sentence Transformers with Robust Error Handling
"""
import os
import logging
import time
from typing import List, Optional, Dict, Any
from pathlib import Path
from cachetools import TTLCache

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.core.config import settings
from app.services.error_handler import error_handler, ErrorType
from app.services.citation_service import citation_service
from app.models.schemas import Citation, CitationSummary

logger = logging.getLogger(__name__)

class RAGService:
    """RAG Service for document-based Q&A with Performance Optimization and Error Handling"""
    
    def __init__(self, mistral_service=None):
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = None
        self.is_initialized = False
        self.mistral_service = mistral_service  # Dependency injection
        
        # Performance optimization with caching
        self.query_cache = TTLCache(maxsize=1000, ttl=300)  # 5min cache
        self.embedding_cache = TTLCache(maxsize=5000, ttl=3600)  # 1h cache
        self.document_cache = TTLCache(maxsize=500, ttl=1800)  # 30min cache
        
        # Performance stats
        self.performance_stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_response_time": 0.0,
            "errors_handled": 0,
            "last_query_time": None
        }
        
        logger.info("🔍 RAG Service initialisiert mit Performance-Optimierung")
    
    async def initialize(self):
        """Initialize RAG components"""
        try:
            logger.info("🚀 RAG Service wird initialisiert...")
            
            # Initialize embeddings
            logger.info(f"📊 Lade Embedding Model: {settings.EMBEDDING_MODEL}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'},  # Embeddings auf CPU
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.RAG_CHUNK_SIZE,
                chunk_overlap=settings.RAG_CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Initialize/load vector store
            persist_directory = Path(settings.VECTOR_DB_PATH)
            persist_directory.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"📚 Initialisiere Vector Database: {persist_directory}")
            
            # Disable ChromaDB telemetry
            import os
            os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"
            
            # Check if vector store already exists
            if self._vector_store_exists(persist_directory):
                logger.info("📖 Lade bestehende Vector Database")
                self.vector_store = Chroma(
                    persist_directory=str(persist_directory),
                    embedding_function=self.embeddings
                )
            else:
                logger.info("🆕 Erstelle neue Vector Database")
                self.vector_store = Chroma(
                    persist_directory=str(persist_directory),
                    embedding_function=self.embeddings
                )
                
                # Auto-load training data if available
                await self._auto_load_training_data()
            
            self.is_initialized = True
            logger.info("✅ RAG Service erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ RAG Service Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
            raise
    
    def _vector_store_exists(self, persist_directory: Path) -> bool:
        """Check if vector store already exists"""
        chroma_db_path = persist_directory / "chroma.sqlite3"
        return chroma_db_path.exists()
    
    async def _auto_load_training_data(self):
        """Automatically load training data on first startup"""
        try:
            help_data_path = Path(settings.HELP_DATA_PATH)
            
            if help_data_path.exists():
                logger.info("📁 Auto-loading Training Data...")
                
                documents = []
                for file_path in help_data_path.glob("*.md"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Create document with metadata
                        doc = Document(
                            page_content=content,
                            metadata={
                                "source": str(file_path),
                                "filename": file_path.name,
                                "type": "help_data"
                            }
                        )
                        documents.append(doc)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Fehler beim Laden von {file_path}: {e}")
                
                if documents:
                    await self.add_documents(documents)
                    logger.info(f"✅ {len(documents)} Dokumente automatisch geladen")
                else:
                    logger.info("📭 Keine Training Dokumente gefunden")
            else:
                logger.info("📂 Training Data Ordner nicht gefunden")
                
        except Exception as e:
            logger.warning(f"⚠️ Auto-loading Training Data fehlgeschlagen: {e}")
    
    async def add_documents(self, documents: List[Document]) -> int:
        """Add documents to vector store"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Split documents into chunks
            chunks = []
            for doc in documents:
                doc_chunks = self.text_splitter.split_documents([doc])
                chunks.extend(doc_chunks)
            
            logger.info(f"📄 Verarbeite {len(chunks)} Text-Chunks...")
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            
            # Persist changes
            self.vector_store.persist()
            
            logger.info(f"✅ {len(chunks)} Chunks zur Vector Database hinzugefügt")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Hinzufügen von Dokumenten: {e}")
            raise
    
    async def search_documents(self, query: str, top_k: int = None) -> List[Document]:
        """Optimized document search with caching and error handling"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            top_k = top_k or settings.RAG_TOP_K
            
            # Check cache first
            cache_key = f"search:{self._normalize_query(query)}:{top_k}"
            if cache_key in self.document_cache:
                self.performance_stats["cache_hits"] += 1
                logger.info(f"🚀 Cache hit for query: '{query[:50]}'")
                return self.document_cache[cache_key]
            
            # Cache miss - perform search
            self.performance_stats["cache_misses"] += 1
            
            # Similarity search with error handling
            docs = self.vector_store.similarity_search(
                query=query,
                k=top_k
            )
            
            # Cache results
            self.document_cache[cache_key] = docs
            
            logger.info(f"🔍 Gefunden: {len(docs)} relevante Dokumente für Query: '{query[:50]}'")
            return docs
            
        except Exception as e:
            logger.error(f"❌ Fehler bei der Dokumentensuche: {e}")
            
            # Use error handler for graceful fallback
            try:
                fallback_response = await error_handler.handle_rag_error(e, {"query": query})
                self.performance_stats["errors_handled"] += 1
                logger.info("🔧 Using error handler fallback for document search")
                return []  # Return empty list but don't crash
            except Exception as fallback_error:
                logger.error(f"❌ Error handler also failed: {fallback_error}")
                return []
    
    async def search_documents_with_citations(
        self, 
        query: str, 
        top_k: int = None,
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """Enhanced document search with citation support"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Get documents using existing search
            documents = await self.search_documents(query, top_k)
            
            if not include_citations:
                return {
                    "documents": documents,
                    "citations": [],
                    "citation_summary": None
                }
            
            # Create citations from documents
            citations = await citation_service.create_citations_from_documents(
                documents, query
            )
            
            # Create citation summary
            citation_summary = citation_service.create_citation_summary(citations)
            
            logger.info(f"🔗 Generated {len(citations)} citations with {citation_summary.coverage_score:.1%} coverage")
            
            return {
                "documents": documents,
                "citations": citations,
                "citation_summary": citation_summary
            }
            
        except Exception as e:
            logger.error(f"❌ Error in citation search: {e}")
            # Fallback to basic search
            documents = await self.search_documents(query, top_k)
            return {
                "documents": documents,
                "citations": [],
                "citation_summary": None
            }
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for cache key generation"""
        return query.lower().strip()[:100]  # Limit length for cache efficiency
    
    async def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding or compute new one"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            # This would require access to embedding model directly
            # For now, return None to use standard vector search
            return None
        except Exception as e:
            logger.warning(f"⚠️ Embedding generation failed: {e}")
            return None
    
    async def query(self, question: str) -> dict:
        """Optimized Q&A with robust error handling, caching, and performance tracking"""
        if not self.is_initialized:
            await self.initialize()
        
        # Performance tracking
        query_start_time = time.time()
        self.performance_stats["total_queries"] += 1
        
        try:
            logger.info(f"🔍 RAG Query: {question}")
            
            # Check query cache first
            cache_key = f"query:{self._normalize_query(question)}"
            if cache_key in self.query_cache:
                self.performance_stats["cache_hits"] += 1
                cached_result = self.query_cache[cache_key]
                cached_result["from_cache"] = True
                cached_result["response_time"] = time.time() - query_start_time
                logger.info(f"🚀 Cache hit for query: '{question[:50]}'")
                return cached_result
            
            # Cache miss - process query
            self.performance_stats["cache_misses"] += 1
            
            # Erweitere Query mit intelligenter Suche
            try:
                from app.services.intelligent_search import intelligent_search
                expanded_query = intelligent_search.expand_query(question)
                logger.info(f"🎯 Erweiterte Query: {expanded_query}")
                search_query = expanded_query
            except Exception as e:
                logger.warning(f"⚠️ Intelligent Search nicht verfügbar: {e}")
                search_query = question
            
            # Search relevant documents with expanded query
            relevant_docs = await self.search_documents(search_query)
            
            # Fallback: Versuche mit Original-Query wenn erweiterte Suche keine Ergebnisse bringt
            if not relevant_docs and search_query != question:
                logger.info("🔄 Fallback auf Original-Query")
                relevant_docs = await self.search_documents(question)
            
            if not relevant_docs:
                return {
                    "answer": self._generate_fallback_answer(question),
                    "sources": [],
                    "confidence": 0.0,
                    "expanded_query": search_query if search_query != question else None,
                    "search_results": 0
                }
            
            # Combine context from relevant documents
            context = self._build_context(relevant_docs)
            
            # Try to use Mistral for intelligent answer generation
            answer = await self._generate_mistral_answer(question, context)
            if not answer:
                # Fallback to template-based answer
                answer = self._generate_contextual_answer_enhanced(question, context)
            
            # Extract sources with better formatting
            sources = []
            for doc in relevant_docs:
                filename = doc.metadata.get("filename", "Unbekannt")
                # Remove UUID and optimize filename for display
                if "_optimized.md" in filename:
                    display_name = filename.replace("_optimized.md", "").split("_")[-1]
                    sources.append(f"Training Data {display_name}")
                else:
                    sources.append(filename)
            # Remove duplicates while preserving order
            sources = list(dict.fromkeys(sources))
            
            # Response-Time berechnen
            response_time = time.time() - query_start_time
            
            # Confidence Score berechnen
            confidence = self._calculate_confidence(relevant_docs, answer)
            
            # Response-Objekt vorbereiten
            response_obj = {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "expanded_query": search_query if search_query != question else None,
                "search_results": len(relevant_docs),
                "response_time": response_time,
                "from_cache": False
            }
            
            # Cache successful result
            self.query_cache[cache_key] = response_obj.copy()
            
            # Update performance stats
            self._update_performance_stats(response_time)
            
            # 🔬 EVALUATION: Automatische wissenschaftliche Evaluierung
            try:
                from app.services.evaluation_service import evaluation_service
                
                # Evaluiere die Antwort
                evaluation_metric = await evaluation_service.evaluate_response_quality(
                    query=question,
                    response=answer,
                    sources=sources,
                    confidence=confidence,
                    response_time=response_time,
                    context=context
                )
                
                # Füge Evaluation-Daten zur Response hinzu (für Debugging/Monitoring)
                response_obj["evaluation"] = {
                    "overall_score": evaluation_metric.overall_score,
                    "relevance_score": evaluation_metric.relevance_score,
                    "completeness_score": evaluation_metric.completeness_score,
                    "hallucination_score": evaluation_metric.hallucination_score
                }
                
                logger.info(f"✅ RAG Query beantwortet und evaluiert: '{question[:50]}' (Score: {evaluation_metric.overall_score:.2f})")
                
            except Exception as e:
                logger.warning(f"⚠️ Evaluation konnte nicht durchgeführt werden: {e}")
                # Evaluation-Fehler sollten die normale Antwort nicht blockieren
                logger.info(f"✅ RAG Query beantwortet für: '{question[:50]}' ({len(relevant_docs)} Dokumente)")
            
            return response_obj
            
        except Exception as e:
            logger.error(f"❌ Fehler bei RAG Query: {e}")
            response_time = time.time() - query_start_time
            self.performance_stats["errors_handled"] += 1
            
            # Use error handler for graceful fallback
            try:
                fallback_response = await error_handler.handle_rag_error(e, {"query": question})
                
                # Create fallback response object
                fallback_obj = {
                    "answer": fallback_response.message,
                    "sources": [],
                    "confidence": fallback_response.confidence,
                    "expanded_query": None,
                    "search_results": 0,
                    "response_time": response_time,
                    "is_fallback": True,
                    "fallback_type": fallback_response.fallback_type.value,
                    "error_type": fallback_response.error_type.value
                }
                
                # Cache fallback with shorter TTL
                cache_key_fallback = f"fallback:{self._normalize_query(question)}"
                self.query_cache[cache_key_fallback] = fallback_obj
                
                logger.info(f"🔧 RAG Query fallback provided for: '{question[:50]}'")
                return fallback_obj
                
            except Exception as fallback_error:
                logger.error(f"❌ Error handler also failed: {fallback_error}")
                
                # Ultimate fallback
                return {
                    "answer": self._generate_fallback_answer(question),
                    "sources": [],
                    "confidence": 0.0,
                    "expanded_query": None,
                    "search_results": 0,
                    "response_time": response_time,
                    "is_fallback": True,
                    "error": "Complete system failure"
                }

    async def answer_question(self, question: str) -> str:
        """Answer question using RAG (legacy method)"""
        result = await self.query(question)
        return result["answer"]
    
    def _build_context(self, documents: List[Document]) -> str:
        """Build context from relevant documents"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('filename', 'Unbekannt')
            content = doc.page_content.strip()
            
            context_parts.append(f"[Quelle {i}: {source}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    async def _generate_mistral_answer(self, question: str, context: str) -> str:
        """Generate intelligent answer using Mistral 7B via dependency injection"""
        try:
            # Use dependency injection instead of direct import
            if hasattr(self, 'mistral_service') and self.mistral_service:
                if not self.mistral_service.is_initialized:
                    logger.warning("⚠️ Mistral Service nicht verfügbar, nutze Fallback")
                    return None
                
                # Use Mistral for intelligent answer generation
                answer = await self.mistral_service.generate_german_response(question, context)
                
                if answer and len(answer.strip()) > 10:  # Valid answer check
                    logger.info("✅ Mistral-generierte Antwort verwendet")
                    return answer
                else:
                    logger.warning("⚠️ Mistral-Antwort unzureichend, nutze Fallback")
                    return None
            else:
                logger.debug("Mistral service not injected, using fallback")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Mistral-Generierung fehlgeschlagen: {e}")
            return None
    
    def _generate_contextual_answer_enhanced(self, question: str, context: str) -> str:
        """Enhanced contextual answer generation for dual-mode chat"""
        question_lower = question.lower()
        
        # Build structured response based on question type
        if any(keyword in question_lower for keyword in ["hallo", "hi", "hey", "guten tag"]):
            return """👋 **Hallo! Ich bin SKI, deine StreamWorks-KI-Expertin.**

Ich kann dir helfen bei:
• **StreamWorks Dokumentation** und Fragen
• **API-Verwendung** und Endpoints  
• **XML-Stream Konfiguration**
• **Scheduling** und Zeitpläne

Was möchtest du wissen?"""

        elif any(keyword in question_lower for keyword in ["xml", "stream", "erstell", "generier"]):
            xml_info = self._extract_xml_info(context)
            return f"""🔧 **XML-Stream Erstellung:**

{xml_info}

💡 **Tipp:** Wechsle zum **XML Generator Modus** für interaktive Stream-Erstellung!"""
            
        elif any(keyword in question_lower for keyword in ["api", "schnittstelle", "endpoint"]):
            api_info = self._extract_api_info(context)
            return f"""🔗 **StreamWorks API:**

{api_info}

📚 Weitere Details findest du in der API-Dokumentation."""
            
        elif any(keyword in question_lower for keyword in ["schedule", "zeitplan", "cron", "zeit"]):
            schedule_info = self._extract_schedule_info(context)
            return f"""⏰ **StreamWorks Scheduling:**

{schedule_info}

🕐 **Beispiele:**
- Täglich um 2 Uhr: `0 2 * * *`
- Stündlich: `0 * * * *`
- Wöchentlich: `0 2 * * 0`"""
            
        elif any(keyword in question_lower for keyword in ["config", "konfiguration", "einstellung"]):
            config_info = self._extract_config_info(context)
            return f"""⚙️ **StreamWorks Konfiguration:**

{config_info}"""
        
        # Default structured response
        context_summary = self._summarize_context(context)
        return f"""📚 **StreamWorks Dokumentation:**

{context_summary}

❓ **Spezifischere Frage?** Verwende Begriffe wie "XML", "API", "Schedule" oder "Config" für detailliertere Antworten."""

    def _generate_contextual_answer(self, question: str, context: str) -> str:
        """Generate answer based on context with improved logic"""
        question_lower = question.lower()
        context_lower = context.lower()
        
        # Extract key information from context
        context_summary = self._summarize_context(context)
        
        # Keywords mapping with better responses
        if any(keyword in question_lower for keyword in ["xml", "stream", "erstell", "generier"]):
            xml_info = self._extract_xml_info(context)
            return f"📋 **StreamWorks XML-Stream Erstellung:**\n\n{xml_info}\n\n**Tipp:** Nutze den Stream Generator Tab für eine geführte Erstellung!"
            
        elif any(keyword in question_lower for keyword in ["api", "schnittstelle", "endpoint"]):
            api_info = self._extract_api_info(context)
            return f"🔗 **StreamWorks API Informationen:**\n\n{api_info}"
            
        elif any(keyword in question_lower for keyword in ["schedule", "zeitplan", "cron", "zeit"]):
            schedule_info = self._extract_schedule_info(context)
            return f"⏰ **StreamWorks Scheduling:**\n\n{schedule_info}"
            
        elif any(keyword in question_lower for keyword in ["config", "konfiguration", "einstellung"]):
            config_info = self._extract_config_info(context)
            return f"⚙️ **StreamWorks Konfiguration:**\n\n{config_info}"
            
        elif any(keyword in question_lower for keyword in ["hilfe", "help", "was", "wie", "hallo"]):
            return f"👋 **Hallo! Ich bin SKI, deine StreamWorks-KI.**\n\nBasierend auf der Dokumentation kann ich dir helfen bei:\n\n{context_summary}\n\n**Was möchtest du genauer wissen?**"
        
        # Default: Return formatted context
        return f"📚 **Aus der StreamWorks Dokumentation:**\n\n{context_summary}"
    
    def _extract_xml_info(self, context: str) -> str:
        """Extract XML-related information"""
        lines = context.split('\n')
        xml_lines = [line for line in lines if any(keyword in line.lower() for keyword in ['xml', 'stream', '<', '>'])]
        return '\n'.join(xml_lines[:3]) if xml_lines else "XML-Informationen verfügbar."
    
    def _extract_api_info(self, context: str) -> str:
        """Extract API-related information"""
        lines = context.split('\n')
        api_lines = [line for line in lines if any(keyword in line.lower() for keyword in ['api', 'endpoint', 'http', 'post', 'get'])]
        return '\n'.join(api_lines[:3]) if api_lines else "API-Informationen verfügbar."
    
    def _extract_general_info(self, context: str) -> str:
        """Extract general helpful information"""
        sentences = context.split('.')
        return '. '.join(sentences[:2]) + '.' if sentences else "Informationen verfügbar."
    
    def _summarize_context(self, context: str) -> str:
        """Create a summary of the context"""
        sentences = context.split('.')
        key_sentences = []
        
        for sentence in sentences[:5]:  # First 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20:  # Meaningful sentences
                key_sentences.append(sentence)
        
        return '. '.join(key_sentences)[:300] + '...' if key_sentences else context[:300] + '...'
    
    def _extract_schedule_info(self, context: str) -> str:
        """Extract scheduling-related information"""
        lines = context.split('\n')
        schedule_lines = [line for line in lines if any(keyword in line.lower() for keyword in ['schedule', 'cron', 'zeit', 'daily', 'weekly'])]
        return '\n'.join(schedule_lines[:3]) if schedule_lines else "Scheduling-Informationen in der Dokumentation verfügbar."
    
    def _extract_config_info(self, context: str) -> str:
        """Extract configuration-related information"""
        lines = context.split('\n')
        config_lines = [line for line in lines if any(keyword in line.lower() for keyword in ['config', 'parameter', 'einstellung', 'option'])]
        return '\n'.join(config_lines[:3]) if config_lines else "Konfigurations-Informationen in der Dokumentation verfügbar."
    
    def _calculate_confidence(self, documents: List[Document], answer: str) -> float:
        """Berechne Confidence Score basierend auf Dokumenten und Antwort"""
        if not documents:
            return 0.0
        
        confidence_factors = []
        
        # Faktor 1: Anzahl relevanter Dokumente
        doc_count_score = min(len(documents) / 3, 1.0)  # Optimal bei 3+ Docs
        confidence_factors.append(doc_count_score)
        
        # Faktor 2: Antwortlänge und Struktur
        answer_quality_score = 0.0
        if len(answer) > 200:
            answer_quality_score += 0.3
        if '##' in answer or '###' in answer:
            answer_quality_score += 0.2
        if any(emoji in answer for emoji in ['🔧', '📋', '🚀', '✅', '💡']):
            answer_quality_score += 0.2
        if '```' in answer:
            answer_quality_score += 0.3
        answer_quality_score = min(answer_quality_score, 1.0)
        confidence_factors.append(answer_quality_score)
        
        # Faktor 3: Quellenqualität
        if any('Training Data' in str(doc.metadata.get('filename', '')) for doc in documents):
            confidence_factors.append(0.9)  # Training Data ist hochwertig
        else:
            confidence_factors.append(0.5)  # Andere Quellen
        
        # Berechne durchschnittlichen Confidence Score
        import statistics
        confidence = statistics.mean(confidence_factors)
        
        # Normalisiere auf typischen Range (0.7-0.95)
        confidence = 0.7 + (confidence * 0.25)
        
        return min(confidence, 0.95)
    
    def _generate_fallback_answer(self, question: str) -> str:
        """Generate fallback answer when no relevant docs found"""
        return f"❓ Entschuldigung, ich konnte keine relevanten Informationen zu '{question}' in der StreamWorks Dokumentation finden.\n\n**Tipps:**\n- Versuche eine spezifischere Frage\n- Nutze Begriffe wie 'XML', 'Stream', 'API', 'Schedule'\n- Schaue in den anderen Tabs nach weiteren Features"
    
    async def get_all_documents(self) -> List[dict]:
        """Get all indexed documents with metadata"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Get direct access to ChromaDB collection
            collection = self.vector_store._collection
            
            # Get all documents
            all_data = collection.get()
            
            # Group by source file
            docs_by_source = {}
            
            for i, doc_content in enumerate(all_data['documents']):
                metadata = all_data['metadatas'][i]
                source = metadata.get('source', 'unknown')
                
                if source not in docs_by_source:
                    docs_by_source[source] = {
                        'id': source,
                        'filename': os.path.basename(source),
                        'source_path': source,
                        'chunks': 0,
                        'total_size': 0,
                        'upload_date': metadata.get('upload_date', 'unknown'),
                        'status': 'indexed'
                    }
                
                docs_by_source[source]['chunks'] += 1
                docs_by_source[source]['total_size'] += len(doc_content)
            
            return list(docs_by_source.values())
            
        except Exception as e:
            logger.error(f"❌ Error getting all documents: {e}")
            return []
    
    async def get_document_details(self, doc_id: str) -> dict:
        """Get detailed information about a specific document"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Get direct access to ChromaDB collection
            collection = self.vector_store._collection
            
            # Get all chunks for this document
            results = collection.get(
                where={"source": doc_id}
            )
            
            if not results['documents']:
                raise ValueError(f"Document {doc_id} not found")
            
            # Get first chunk for preview
            preview_content = results['documents'][0][:200] + "..." if len(results['documents'][0]) > 200 else results['documents'][0]
            
            return {
                "id": doc_id,
                "filename": os.path.basename(doc_id),
                "chunks": len(results['documents']),
                "preview": preview_content,
                "metadata": results['metadatas'][0] if results['metadatas'] else {}
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting document details: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document and all its chunks from the vector store"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Get direct access to ChromaDB collection
            collection = self.vector_store._collection
            
            # Find all chunks for this document
            results = collection.get(
                where={"source": doc_id}
            )
            
            if results['ids']:
                # Delete all chunks
                collection.delete(ids=results['ids'])
                
                # Persist changes
                self.vector_store.persist()
                
                logger.info(f"🗑️ Deleted {len(results['ids'])} chunks for document {doc_id}")
                return True
            else:
                logger.warning(f"⚠️ Document {doc_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting document: {e}")
            return False

    async def get_document_count(self) -> int:
        """Get total number of documents in the vector store"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            collection = self.vector_store._collection
            return collection.count()
        except Exception as e:
            logger.error(f"❌ Error getting document count: {e}")
            return 0
    
    async def get_all_chunks(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """Get all chunks from the vector store with pagination"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            collection = self.vector_store._collection
            
            # Get chunks with pagination
            results = collection.get(
                limit=limit,
                offset=offset,
                include=['documents', 'metadatas', 'ids']
            )
            
            documents = []
            if results['documents']:
                for i, doc_content in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    doc_id = results['ids'][i] if results['ids'] else f"chunk_{i}"
                    
                    # Create Document object
                    doc = Document(
                        page_content=doc_content,
                        metadata=metadata
                    )
                    # Add ID as an attribute for compatibility
                    doc.id = doc_id
                    documents.append(doc)
            
            logger.debug(f"📋 Retrieved {len(documents)} chunks (offset: {offset}, limit: {limit})")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error getting all chunks: {e}")
            return []
    
    def _update_performance_stats(self, response_time: float):
        """Update performance statistics"""
        # Update average response time
        total_queries = self.performance_stats["total_queries"]
        current_avg = self.performance_stats["avg_response_time"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_queries - 1)) + response_time) / total_queries
        self.performance_stats["avg_response_time"] = new_avg
        self.performance_stats["last_query_time"] = time.time()
    
    async def get_stats(self) -> dict:
        """Get comprehensive RAG service statistics"""
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        try:
            # Get collection info
            collection = self.vector_store._collection
            doc_count = collection.count()
            
            # Calculate cache efficiency
            total_requests = self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]
            cache_hit_rate = (self.performance_stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "status": "healthy",
                "documents_count": doc_count,
                "embedding_model": settings.EMBEDDING_MODEL,
                "vector_db_path": settings.VECTOR_DB_PATH,
                "chunk_size": settings.RAG_CHUNK_SIZE,
                "top_k": settings.RAG_TOP_K,
                "performance": {
                    **self.performance_stats,
                    "cache_hit_rate_percent": round(cache_hit_rate, 2),
                    "query_cache_size": len(self.query_cache),
                    "document_cache_size": len(self.document_cache),
                    "embedding_cache_size": len(self.embedding_cache)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen der RAG Stats: {e}")
            return {"status": "error", "error": str(e)}

# Global instance
rag_service = RAGService()