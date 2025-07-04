"""
RAG Service for StreamWorks-KI Q&A System
Uses ChromaDB + LangChain + Sentence Transformers
"""
import os
import logging
from typing import List, Optional
from pathlib import Path

import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

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
    
    async def answer_question(self, question: str) -> str:
        """Answer question using RAG"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Search relevant documents
            relevant_docs = await self.search_documents(question)
            
            if not relevant_docs:
                return self._generate_fallback_answer(question)
            
            # Combine context from relevant documents
            context = self._build_context(relevant_docs)
            
            # Generate answer based on context
            answer = self._generate_contextual_answer(question, context)
            
            logger.info(f"✅ RAG Antwort generiert für: '{question[:50]}'")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Fehler bei RAG Q&A: {e}")
            return self._generate_fallback_answer(question)
    
    def _build_context(self, documents: List[Document]) -> str:
        """Build context from relevant documents"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('filename', 'Unbekannt')
            content = doc.page_content.strip()
            
            context_parts.append(f"[Quelle {i}: {source}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _generate_contextual_answer(self, question: str, context: str) -> str:
        """Generate answer based on context (rule-based for now)"""
        # For now, use rule-based approach
        # Later: Can be replaced with LLM-based generation
        
        question_lower = question.lower()
        context_lower = context.lower()
        
        # Keywords mapping
        if any(keyword in question_lower for keyword in ["xml", "stream", "erstell"]):
            if "xml" in context_lower:
                return f"Basierend auf der Dokumentation kann ich dir bei der XML-Stream-Erstellung helfen. {self._extract_xml_info(context)}"
            
        elif any(keyword in question_lower for keyword in ["api", "schnittstelle"]):
            if "api" in context_lower:
                return f"Hier sind die verfügbaren StreamWorks APIs: {self._extract_api_info(context)}"
            
        elif any(keyword in question_lower for keyword in ["hilfe", "help", "was", "wie"]):
            return f"Gerne helfe ich dir! Basierend auf der Dokumentation: {self._extract_general_info(context)}"
        
        # Default: Return relevant context
        return f"Basierend auf der StreamWorks Dokumentation:\n\n{context[:500]}..."
    
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
    
    def _generate_fallback_answer(self, question: str) -> str:
        """Generate fallback answer when no relevant docs found"""
        return f"Entschuldigung, ich konnte keine relevanten Informationen zu '{question}' in der StreamWorks Dokumentation finden. Könntest du die Frage anders formulieren oder spezifischer sein?"
    
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