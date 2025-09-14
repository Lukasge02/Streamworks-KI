"""
LlamaIndex RAG Service
Modern document processing and RAG pipeline using LlamaIndex ecosystem
Replaces Docling with state-of-the-art RAG architecture
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
    Document as LlamaDocument
)
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
# Query engine will be created using index.as_query_engine()
# from llama_index.core.postprocessor import SimilarityPostprocessor

import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE

logger = logging.getLogger(__name__)


class DocumentChunk:
    """Document chunk representation for compatibility with existing system"""

    def __init__(
        self,
        content: str,
        doc_id: str,
        chunk_id: str,
        page_number: Optional[int] = None,
        heading: Optional[str] = None,
        section: Optional[str] = None,
        doctype: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.doc_id = doc_id
        self.chunk_id = chunk_id
        self.page_number = page_number
        self.heading = heading
        self.section = section
        self.doctype = doctype
        self.metadata = metadata or {}

        # Compute additional metadata
        self.metadata.update({
            "chunk_length": len(content),
            "word_count": len(content.split()),
            "created_at": datetime.now().isoformat(),
            "processing_engine": "llamaindex"
        })


class LlamaIndexRAGService:
    """
    Modern RAG service using LlamaIndex ecosystem
    Provides document loading, chunking, embedding, and querying
    """

    def __init__(self):
        self._initialized = False
        self._initialization_error = None

        # Core components (simplified for ChromaDB-only)
        self.embed_model = None
        self.text_splitter = None
        self.llm = None

        # Configuration from settings
        from config import settings
        self.settings = settings

    async def initialize(self) -> bool:
        """Initialize LlamaIndex RAG service with dependency validation"""
        if self._initialized:
            return True

        if self._initialization_error:
            raise self._initialization_error

        try:
            logger.info("🚀 Initializing LlamaIndex RAG Service...")

            # 0. Optional dependency validation
            try:
                from services.dependency_validator import get_dependency_validator
                validator = get_dependency_validator(self.settings)
                await validator.validate_all_dependencies()
                logger.info("✅ All dependencies validated")
            except ImportError:
                logger.info("⚠️ Dependency validator not available, skipping validation")
            except Exception as e:
                logger.warning(f"⚠️ Dependency validation failed: {str(e)}")

            # 1. Setup BGE Embeddings (Local, State-of-the-Art)
            # Determine best device
            import torch
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

            logger.info(f"Using device: {device}")

            self.embed_model = HuggingFaceEmbedding(
                model_name="BAAI/bge-base-en-v1.5",
                device=device,
                max_length=512,
                normalize=True
            )
            logger.info("✅ BGE Embedding model initialized")

            # 2. Setup Intelligent Text Splitter
            self.text_splitter = SentenceSplitter(
                chunk_size=self.settings.CHUNK_SIZE,
                chunk_overlap=self.settings.CHUNK_OVERLAP,
                paragraph_separator="\n\n"
            )
            logger.info("✅ Intelligent text splitter configured")

            # 3. Setup Local LLM (Ollama) - REQUIRED
            self.llm = Ollama(
                model=self.settings.OLLAMA_MODEL,
                base_url=self.settings.OLLAMA_BASE_URL,
                temperature=self.settings.LLM_TEMPERATURE,
                request_timeout=120.0
            )
            logger.info(f"✅ Ollama LLM configured: {self.settings.OLLAMA_MODEL}")

            # 4. Initialize ChromaDB client
            await self._initialize_chromadb()

            # 6. Setup Global LlamaIndex Settings (for text processing only)
            Settings.embed_model = self.embed_model
            Settings.llm = self.llm
            Settings.text_splitter = self.text_splitter

            logger.info("✅ LlamaIndex settings configured for processing")

            self._initialized = True
            logger.info("🎯 LlamaIndex RAG Service fully initialized!")
            return True

        except Exception as e:
            self._initialization_error = e
            logger.error(f"❌ Failed to initialize LlamaIndex RAG Service: {str(e)}")
            raise e

    async def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection with robust error handling"""
        try:
            import chromadb
            from pathlib import Path

            # Use settings-based path like in the concept
            chroma_path = Path("./storage/chroma")
            chroma_path.mkdir(parents=True, exist_ok=True)

            # Initialize with better error handling
            try:
                self.chroma_client = chromadb.PersistentClient(
                    path=str(chroma_path),
                    settings=chromadb.config.Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                logger.info(f"✅ ChromaDB client initialized at {chroma_path}")
            except Exception as client_error:
                if "database is locked" in str(client_error) or "compaction" in str(client_error):
                    logger.warning(f"🔧 ChromaDB locked/corrupted, attempting cleanup...")
                    # Try to clear and reinitialize
                    import shutil
                    try:
                        shutil.rmtree(chroma_path)
                        chroma_path.mkdir(parents=True, exist_ok=True)
                        self.chroma_client = chromadb.PersistentClient(
                            path=str(chroma_path),
                            settings=chromadb.config.Settings(
                                anonymized_telemetry=False,
                                allow_reset=True
                            )
                        )
                        logger.info(f"🔄 ChromaDB cleaned and reinitialized at {chroma_path}")
                    except Exception as cleanup_error:
                        logger.error(f"❌ ChromaDB cleanup failed: {str(cleanup_error)}")
                        raise
                else:
                    raise client_error

            # Validate ChromaDB connection
            try:
                # Test ChromaDB connection by getting or creating collection
                collection = self.chroma_client.get_or_create_collection("rag_documents")
                logger.info(f"✅ ChromaDB connection healthy, collection 'rag_documents' ready")
            except Exception as validation_error:
                logger.warning(f"⚠️ ChromaDB validation failed, attempting recovery: {str(validation_error)}")
                # Try once more with reset
                try:
                    self.chroma_client.reset()
                    collection = self.chroma_client.get_or_create_collection("rag_documents")
                    logger.info(f"🔄 ChromaDB recovered after reset")
                except Exception as reset_error:
                    logger.error(f"❌ ChromaDB recovery failed: {str(reset_error)}")
                    # Don't raise - allow processing to continue without ChromaDB

        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {str(e)}")
            # Don't raise - allow system to function without ChromaDB
            self.chroma_client = None

    async def process_document(
        self,
        file_path: Path,
        doc_id: str,
        doctype: str = "general"
    ) -> List[DocumentChunk]:
        """
        Process document using simplified ChromaDB-only pipeline

        Args:
            file_path: Path to document file
            doc_id: Document ID for tracking
            doctype: Document type for metadata

        Returns:
            List of DocumentChunk objects
        """
        if not await self.initialize():
            raise Exception("Failed to initialize RAG service")

        try:
            logger.info(f"🚀 Processing document with ChromaDB-only pipeline: {file_path}")

            # 1. Load document using SimpleDirectoryReader
            reader = SimpleDirectoryReader(
                input_files=[str(file_path)],
                filename_as_id=True,
                recursive=False
            )

            documents = reader.load_data()
            if not documents:
                logger.warning(f"No content extracted from: {file_path}")
                return []

            logger.info(f"✅ Loaded {len(documents)} document(s) from {file_path}")

            # 2. Extract text and create nodes
            full_text = ""
            for doc in documents:
                full_text += doc.text + "\n\n"

            if not full_text.strip():
                logger.warning(f"No text content found in: {file_path}")
                return []

            # 3. Create LlamaDocument with metadata
            llama_doc = LlamaDocument(
                text=full_text,
                doc_id=doc_id,
                metadata={
                    "doc_id": doc_id,
                    "source_file": str(file_path),
                    "doctype": doctype,
                    "processed_at": datetime.now().isoformat(),
                    "processing_engine": "llamaindex"
                }
            )

            # 4. Split into nodes/chunks
            nodes = self.text_splitter.get_nodes_from_documents([llama_doc])
            logger.info(f"✅ Created {len(nodes)} chunks from document")

            # 5. Generate embeddings for all chunks
            embeddings = []
            for node in nodes:
                embedding = self.embed_model.get_text_embedding(node.text)
                embeddings.append(embedding)

            logger.info(f"✅ Generated {len(embeddings)} embeddings")

            # 6. Prepare data for ChromaDB master
            chunks = []
            chunk_data_for_chromadb = []
            metadata_for_chromadb = []

            for i, node in enumerate(nodes):
                # Enhanced metadata extraction
                enhanced_metadata = {
                    "chunk_index": i,
                    "total_chunks": len(nodes),
                    "node_id": node.node_id,
                    "source_file": str(file_path),
                    "file_name": file_path.name,
                    "file_extension": file_path.suffix.lower(),
                    "chunking_strategy": "sentence_splitter",
                    "processing_engine": "llamaindex",
                    "processing_timestamp": datetime.now().isoformat(),
                    "word_count": len(node.text.split()),
                    "char_count": len(node.text),
                    "chunk_type": self._classify_chunk_type(node.text),
                    **node.metadata
                }

                # Extract additional metadata from node if available
                if hasattr(node, 'metadata') and node.metadata:
                    # Add page number if available
                    if 'page_label' in node.metadata:
                        enhanced_metadata['page_number'] = node.metadata['page_label']
                    elif 'page' in node.metadata:
                        enhanced_metadata['page_number'] = node.metadata['page']

                    # Add coordinate information if available
                    if 'coordinates' in node.metadata:
                        enhanced_metadata['coordinates'] = node.metadata['coordinates']

                chunk = DocumentChunk(
                    content=node.text,
                    doc_id=doc_id,
                    chunk_id=f"{doc_id}_chunk_{i}",
                    doctype=doctype,
                    metadata=enhanced_metadata
                )
                chunks.append(chunk)

                # Prepare for ChromaDB
                chunk_data_for_chromadb.append({"content": node.text})
                metadata_for_chromadb.append(chunk.metadata)

            # 7. Store in ChromaDB directly with error recovery
            try:
                collection = self.chroma_client.get_or_create_collection("rag_documents")

                # Prepare IDs for chunks
                chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

                # Add to ChromaDB with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        collection.add(
                            ids=chunk_ids,
                            documents=[chunk["content"] for chunk in chunk_data_for_chromadb],
                            embeddings=embeddings,
                            metadatas=metadata_for_chromadb
                        )
                        break  # Success
                    except Exception as add_error:
                        if "already exists" in str(add_error):
                            # Delete existing and retry
                            logger.warning(f"🔄 Chunks already exist, cleaning up for retry (attempt {attempt + 1})")
                            try:
                                collection.delete(ids=chunk_ids)
                            except Exception:
                                pass  # Ignore deletion errors
                        elif attempt == max_retries - 1:
                            raise add_error  # Final attempt failed
                        else:
                            logger.warning(f"⚠️ ChromaDB add attempt {attempt + 1} failed, retrying: {str(add_error)}")
                            await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

            except Exception as chromadb_error:
                if "compaction" in str(chromadb_error).lower():
                    logger.error(f"🛠️ ChromaDB compaction error detected - attempting database reset")
                    try:
                        # Reset ChromaDB connection
                        await self._reset_chromadb_connection()
                        # Retry once with fresh connection
                        collection = self.chroma_client.get_or_create_collection("rag_documents")
                        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
                        collection.add(
                            ids=chunk_ids,
                            documents=[chunk["content"] for chunk in chunk_data_for_chromadb],
                            embeddings=embeddings,
                            metadatas=metadata_for_chromadb
                        )
                        logger.info(f"✅ ChromaDB reset successful, document processed")
                    except Exception as reset_error:
                        logger.error(f"❌ ChromaDB reset failed: {str(reset_error)}")
                        # Continue processing - allow Supabase mirroring to work
                        pass
                else:
                    logger.error(f"❌ ChromaDB error (continuing with processing): {str(chromadb_error)}")
                    # Don't raise - allow processing to continue for Supabase mirroring

            logger.info(f"🎯 Document processing completed: {file_path} → {len(chunks)} chunks processed")
            return chunks

        except Exception as e:
            logger.error(f"❌ Failed to process document {file_path}: {str(e)}")
            # Don't raise - return empty chunks to allow Supabase mirroring of error status
            return []

    async def query_documents(
        self,
        query: str,
        doc_filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Query documents using simplified ChromaDB-only pipeline

        Args:
            query: User query
            doc_filters: Optional metadata filters
            top_k: Number of chunks to retrieve

        Returns:
            Tuple of (response_text, source_documents)
        """
        if not await self.initialize():
            raise Exception("Failed to initialize RAG service")

        logger.info(f"🔍 Processing query with ChromaDB-only: {query}")

        try:
            # 1. Generate query embedding
            query_embedding = self.embed_model.get_text_embedding(query)
            logger.info("✅ Generated query embedding")

            # 2. Query ChromaDB directly for similar chunks
            collection = self.chroma_client.get_collection("rag_documents")

            query_result = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=doc_filters if doc_filters else None
            )

            # Convert to expected format
            similar_chunks = []
            if query_result and query_result['documents']:
                for i, document in enumerate(query_result['documents'][0]):
                    similar_chunks.append({
                        "content": document,
                        "metadata": query_result['metadatas'][0][i] if query_result['metadatas'] else {},
                        "score": 1.0 - query_result['distances'][0][i] if query_result['distances'] else 1.0
                    })

            logger.info(f"✅ Found {len(similar_chunks)} similar chunks from ChromaDB")

            # 3. Generate LLM response using retrieved context
            if similar_chunks:
                context_texts = [chunk["content"] for chunk in similar_chunks]
                context = "\n\n".join(context_texts)

                # Create prompt for LLM
                prompt = f"""Context:
{context}

Question: {query}

Answer based on the context above:"""

                response = await self.llm.acomplete(prompt)
                response_text = str(response).strip()

                # Format source documents
                source_docs = []
                for chunk in similar_chunks:
                    source_docs.append({
                        "content": chunk["content"],
                        "metadata": chunk["metadata"],
                        "score": chunk["score"]
                    })

                logger.info(f"✅ Generated LLM response using ChromaDB context")
                return response_text, source_docs
            else:
                logger.info("ℹ️ No relevant context found - generating general response")
                response = await self.llm.acomplete(f"Question: {query}\n\nAnswer:")
                return str(response).strip(), []

        except Exception as e:
            logger.error(f"❌ Query processing failed: {str(e)}")
            raise

    async def get_health_status(self) -> Dict[str, Any]:
        """Get RAG service health status for monitoring"""
        try:
            health = {
                "service": "LlamaIndexRAGService",
                "status": "healthy",
                "initialized": self._initialized,
                "chromadb": {
                    "connected": False,
                    "collection_exists": False,
                    "document_count": 0
                }
            }

            # Check ChromaDB health
            if hasattr(self, 'chroma_client') and self.chroma_client:
                try:
                    collection = self.chroma_client.get_collection("rag_documents")
                    health["chromadb"]["connected"] = True
                    health["chromadb"]["collection_exists"] = True
                    health["chromadb"]["document_count"] = collection.count()
                except Exception:
                    # Collection doesn't exist or connection failed
                    health["chromadb"]["connected"] = bool(self.chroma_client)

            return health

        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "service": "LlamaIndexRAGService",
                "status": "unhealthy",
                "error": str(e)
            }

    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete document from ChromaDB master with robust error handling

        Args:
            doc_id: Document ID to delete

        Returns:
            Success status
        """
        try:
            logger.info(f"🗑️ Deleting document {doc_id} from ChromaDB")

            # Ensure service is initialized
            if not hasattr(self, 'chroma_client') or self.chroma_client is None:
                logger.warning(f"⚠️ ChromaDB client not initialized, initializing now...")
                try:
                    await self._initialize_chromadb()
                except Exception as init_error:
                    logger.error(f"❌ Failed to initialize ChromaDB for deletion: {str(init_error)}")
                    return False

            # Delete directly from ChromaDB with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    collection = self.chroma_client.get_collection("rag_documents")
                except Exception as collection_error:
                    if "does not exist" in str(collection_error):
                        logger.info(f"📋 Collection doesn't exist yet, nothing to delete for {doc_id}")
                        return True
                    else:
                        logger.warning(f"⚠️ Collection access failed, creating: {str(collection_error)}")
                        collection = self.chroma_client.get_or_create_collection("rag_documents")

                try:
                    # Find all chunks for this document
                    results = collection.get(
                        where={"doc_id": doc_id}
                    )

                    if results and results.get('ids'):
                        # Delete chunks by their IDs
                        collection.delete(ids=results['ids'])
                        logger.info(f"✅ Deleted {len(results['ids'])} chunks for document {doc_id}")
                        return True
                    else:
                        logger.info(f"📭 No chunks found for document {doc_id} (nothing to delete)")
                        return True

                except Exception as delete_error:
                    if "compaction" in str(delete_error).lower() and attempt < max_retries - 1:
                        logger.warning(f"🔄 ChromaDB compaction error during deletion (attempt {attempt + 1}), retrying...")
                        await asyncio.sleep(1 * (attempt + 1))
                        # Try to reset connection
                        try:
                            await self._reset_chromadb_connection()
                        except Exception:
                            pass  # Continue with existing connection
                        continue
                    else:
                        raise delete_error

                break  # Success, exit retry loop

        except Exception as e:
            logger.error(f"❌ Failed to delete document {doc_id}: {str(e)}")
            # Don't raise - deletion failures shouldn't break the rest of the cleanup
            return False

    async def get_document_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get document metadata without full processing

        Args:
            file_path: Path to document

        Returns:
            Document information dictionary
        """
        try:
            # Quick file analysis
            stat = file_path.stat()

            # Try to load and get basic info
            reader = SimpleDirectoryReader(input_files=[str(file_path)])
            documents = reader.load_data()

            text_length = sum(len(doc.text) for doc in documents) if documents else 0

            return {
                "file_size": stat.st_size,
                "has_text": text_length > 0,
                "estimated_chunks": max(1, text_length // self.settings.CHUNK_SIZE),
                "processing_status": "ready",
                "supported": True,
                "text_length": text_length
            }

        except Exception as e:
            logger.warning(f"Failed to analyze document {file_path}: {str(e)}")
            return {
                "file_size": 0,
                "has_text": False,
                "estimated_chunks": 0,
                "processing_status": "error",
                "supported": False,
                "error": str(e)
            }

    async def _reset_chromadb_connection(self):
        """
        Reset ChromaDB connection in case of corruption
        """
        try:
            logger.info(f"🔄 Resetting ChromaDB connection...")
            # Close existing client if possible
            if hasattr(self, 'chroma_client') and self.chroma_client:
                try:
                    # ChromaDB doesn't have explicit close method, just reset reference
                    self.chroma_client = None
                except Exception:
                    pass

            # Reinitialize ChromaDB
            await self._initialize_chromadb()
            logger.info(f"✅ ChromaDB connection reset successful")

        except Exception as e:
            logger.error(f"❌ ChromaDB connection reset failed: {str(e)}")
            raise

    def _classify_chunk_type(self, text: str) -> str:
        """
        Classify the type of content in a chunk based on text analysis

        Returns:
            Content type: 'title', 'section_header', 'table', 'list', 'code', 'text'
        """
        text_lower = text.lower().strip()

        # Empty or very short text
        if len(text.strip()) < 10:
            return 'text'

        # Title detection (short, often capitalized, no periods)
        if (len(text) < 100 and
            text.count('.') == 0 and
            text.count('\n') == 0 and
            (text.isupper() or text.istitle())):
            return 'title'

        # Section header detection (starts with numbers/bullets, short)
        lines = text.strip().split('\n')
        first_line = lines[0].strip()

        if (len(lines) == 1 and len(first_line) < 150 and
            (first_line[0:3].replace('.', '').replace(' ', '').isdigit() or
             first_line.startswith(('##', '#', '•', '-', '*')) or
             first_line.endswith(':'))):
            return 'section_header'

        # Table detection (contains multiple tabs or pipe separators)
        if (text.count('\t') > 5 or
            text.count('|') > 5 or
            ('tabelle' in text_lower or 'table' in text_lower)):
            return 'table'

        # List detection (multiple bullet points or numbered items)
        bullet_count = sum(1 for line in lines if line.strip().startswith(('•', '-', '*', '1.', '2.', '3.')))
        if bullet_count >= 3:
            return 'list'

        # Code detection (contains programming keywords or special formatting)
        code_indicators = ['function', 'class', 'def ', 'import ', 'const ', 'var ', '{', '}', '()', ';']
        if any(indicator in text_lower for indicator in code_indicators):
            code_char_count = sum(1 for char in text if char in '{}();[]')
            if code_char_count > len(text) * 0.05:  # 5% special characters
                return 'code'

        # Default to regular text
        return 'text'


# Global service instance
_rag_service = None

async def get_rag_service() -> LlamaIndexRAGService:
    """Get global RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = LlamaIndexRAGService()
    return _rag_service