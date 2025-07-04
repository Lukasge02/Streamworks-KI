"""
RAG Service for StreamWorks-KI Q&A System
Uses ChromaDB + LangChain + Sentence Transformers
"""
import os
import logging
from typing import List, Optional
from pathlib import Path

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.core.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    """RAG Service for document-based Q&A"""
    
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = None
        self.is_initialized = False
        
        logger.info("🔍 RAG Service initialisiert")
    
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
                for file_path in help_data_path.glob("*.txt"):
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
        """Search similar documents"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            top_k = top_k or settings.RAG_TOP_K
            
            # Similarity search
            docs = self.vector_store.similarity_search(
                query=query,
                k=top_k
            )
            
            logger.info(f"🔍 Gefunden: {len(docs)} relevante Dokumente für Query: '{query[:50]}'")
            return docs
            
        except Exception as e:
            logger.error(f"❌ Fehler bei der Dokumentensuche: {e}")
            return []
    
    async def query(self, question: str) -> dict:
        """Optimierte Q&A für Chat-Mode mit Mistral Integration und intelligenter Suche"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            logger.info(f"🔍 RAG Query: {question}")
            
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
            
            # Extract sources
            sources = [doc.metadata.get("filename", "Unbekannt") for doc in relevant_docs]
            
            logger.info(f"✅ RAG Query beantwortet für: '{question[:50]}' ({len(relevant_docs)} Dokumente)")
            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.9 if relevant_docs else 0.0,
                "expanded_query": search_query if search_query != question else None,
                "search_results": len(relevant_docs)
            }
            
        except Exception as e:
            logger.error(f"❌ Fehler bei RAG Query: {e}")
            return {
                "answer": self._generate_fallback_answer(question),
                "sources": [],
                "confidence": 0.0,
                "expanded_query": None,
                "search_results": 0
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
        """Generate intelligent answer using Mistral 7B"""
        try:
            # Import here to avoid circular imports
            from app.services.mistral_llm_service import mistral_llm_service
            
            if not mistral_llm_service.is_initialized:
                logger.warning("⚠️ Mistral Service nicht verfügbar, nutze Fallback")
                return None
            
            # Use Mistral for intelligent answer generation
            answer = await mistral_llm_service.generate_german_response(question, context)
            
            if answer and len(answer.strip()) > 10:  # Valid answer check
                logger.info("✅ Mistral-generierte Antwort verwendet")
                return answer
            else:
                logger.warning("⚠️ Mistral-Antwort unzureichend, nutze Fallback")
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
    
    async def get_stats(self) -> dict:
        """Get RAG service statistics"""
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        try:
            # Get collection info
            collection = self.vector_store._collection
            doc_count = collection.count()
            
            return {
                "status": "healthy",
                "documents_count": doc_count,
                "embedding_model": settings.EMBEDDING_MODEL,
                "vector_db_path": settings.VECTOR_DB_PATH,
                "chunk_size": settings.RAG_CHUNK_SIZE,
                "top_k": settings.RAG_TOP_K
            }
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Abrufen der RAG Stats: {e}")
            return {"status": "error", "error": str(e)}

# Global instance
rag_service = RAGService()