"""
Qdrant RAG Service
Modern document processing and RAG pipeline using Qdrant + LlamaIndex
High-performance replacement for ChromaDB-based pipeline
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime
import time

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
    Document as LlamaDocument
)
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

from .qdrant_vectorstore import get_qdrant_service, QdrantVectorStoreService

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
            "processing_engine": "qdrant_llamaindex"
        })


class QdrantRAGService:
    """
    High-performance RAG service using Qdrant + LlamaIndex
    Enterprise-grade document processing and querying
    """

    def __init__(self):
        self._initialized = False
        self._initialization_error = None

        # Core components
        self.embed_model = None
        self.text_splitter = None
        self.llm = None
        self.qdrant_service: Optional[QdrantVectorStoreService] = None

        # Configuration from settings
        from config import settings
        self.settings = settings

    async def initialize(self) -> bool:
        """Initialize Qdrant RAG service with dependency validation"""
        if self._initialized:
            return True

        if self._initialization_error:
            raise self._initialization_error

        try:
            logger.info("🚀 Initializing Qdrant RAG Service...")

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

            # 3. Setup LLM - LlamaIndex Compatible
            logger.info(f"🔧 Configuring LLM with provider: {self.settings.LLM_PROVIDER}")
            if self.settings.LLM_PROVIDER == "openai":
                from llama_index.llms.openai import OpenAI
                self.llm = OpenAI(
                    model=self.settings.OPENAI_MODEL,
                    temperature=self.settings.OPENAI_TEMPERATURE,
                    api_key=self.settings.OPENAI_API_KEY
                )
                logger.info(f"✅ OpenAI LLM configured: {self.settings.OPENAI_MODEL}")
            else:
                # Ollama for local LLM
                from llama_index.llms.ollama import Ollama
                self.llm = Ollama(
                    model=self.settings.OLLAMA_MODEL,
                    base_url=self.settings.OLLAMA_BASE_URL,
                    temperature=self.settings.OPENAI_TEMPERATURE,
                    request_timeout=30.0
                )
                logger.info(f"✅ Ollama LLM configured: {self.settings.OLLAMA_MODEL}")

            # For chat service, we'll use the factory pattern separately
            self._chat_llm_service = None

            # 4. Initialize Qdrant Vector Store
            self.qdrant_service = await get_qdrant_service()
            await self.qdrant_service.initialize()
            logger.info("✅ Qdrant vector store initialized")

            # 5. Setup Global LlamaIndex Settings
            Settings.embed_model = self.embed_model
            Settings.llm = self.llm
            Settings.text_splitter = self.text_splitter

            logger.info("✅ LlamaIndex settings configured for processing")

            self._initialized = True
            logger.info("🎯 Qdrant RAG Service fully initialized!")
            return True

        except Exception as e:
            self._initialization_error = e
            logger.error(f"❌ Failed to initialize Qdrant RAG Service: {str(e)}")
            raise e

    async def process_document(
        self,
        file_path: Path,
        doc_id: str,
        doctype: str = "general"
    ) -> List[DocumentChunk]:
        """
        Process document using Qdrant pipeline

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
            logger.info(f"🚀 Processing document with Qdrant pipeline: {file_path}")

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
                    "processing_engine": "qdrant_llamaindex"
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

            # 6. Prepare data for Qdrant
            chunks = []
            texts_for_qdrant = []
            metadata_for_qdrant = []

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
                    "processing_engine": "qdrant_llamaindex",
                    "processing_timestamp": datetime.now().isoformat(),
                    "word_count": len(node.text.split()),
                    "char_count": len(node.text),
                    "chunk_type": self._classify_chunk_type(node.text),
                    "doc_id": doc_id,
                    "doctype": doctype,
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

                # Prepare for Qdrant
                texts_for_qdrant.append(node.text)
                metadata_for_qdrant.append(enhanced_metadata)

            # 7. Store in Qdrant
            try:
                point_ids = await self.qdrant_service.add_documents(
                    texts=texts_for_qdrant,
                    embeddings=embeddings,
                    metadatas=metadata_for_qdrant
                )
                logger.info(f"✅ Stored {len(point_ids)} chunks in Qdrant")
            except Exception as qdrant_error:
                logger.error(f"❌ Qdrant storage error: {str(qdrant_error)}")
                # Continue processing - allow Supabase mirroring to work
                logger.warning("⚠️ Continuing without Qdrant storage")

            # 8. Store in Hybrid Collection if enabled
            if self.settings.ENABLE_HYBRID_SEARCH:
                try:
                    await self._process_hybrid_documents(
                        texts_for_qdrant,
                        embeddings,
                        metadata_for_qdrant
                    )
                except Exception as hybrid_error:
                    logger.warning(f"⚠️ Hybrid processing failed: {str(hybrid_error)}")

            logger.info(f"🎯 Document processing completed: {file_path} → {len(chunks)} chunks processed")
            return chunks

        except Exception as e:
            logger.error(f"❌ Failed to process document {file_path}: {str(e)}")
            return []

    async def _process_hybrid_documents(
        self,
        texts: List[str],
        dense_embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Process documents for hybrid search - generate sparse vectors and store in hybrid collection

        Args:
            texts: List of text content
            dense_embeddings: List of dense embedding vectors
            metadatas: List of metadata dictionaries
        """
        try:
            logger.info(f"🔍 Processing {len(texts)} documents for hybrid search...")

            # Import hybrid text processor
            from .hybrid_text_processor import get_hybrid_text_processor
            text_processor = get_hybrid_text_processor()

            # Generate sparse vectors for all texts
            sparse_vectors = []
            for text in texts:
                sparse_vector = text_processor.process_document(text)
                sparse_vectors.append(sparse_vector)

            logger.info(f"✅ Generated {len(sparse_vectors)} sparse vectors")

            # Store in hybrid collection
            if self.qdrant_service.hybrid_vector_store:
                hybrid_point_ids = await self.qdrant_service.add_hybrid_documents(
                    texts=texts,
                    dense_embeddings=dense_embeddings,
                    sparse_vectors=sparse_vectors,
                    metadatas=metadatas
                )
                logger.info(f"✅ Stored {len(hybrid_point_ids)} documents in hybrid collection")

                # Save vocabulary state after processing
                from .hybrid_text_processor import save_hybrid_vocabulary
                save_hybrid_vocabulary()
            else:
                logger.warning("⚠️ Hybrid collection not available - skipping hybrid storage")

        except Exception as e:
            logger.error(f"❌ Hybrid document processing failed: {str(e)}")
            raise

    async def query_documents(
        self,
        query: str,
        doc_filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Query documents using Qdrant pipeline - PERFORMANCE OPTIMIZED

        Args:
            query: User query
            doc_filters: Optional metadata filters
            top_k: Number of chunks to retrieve

        Returns:
            Tuple of (response_text, source_documents)
        """
        if not await self.initialize():
            raise Exception("Failed to initialize RAG service")

        logger.info(f"🔍 Processing query with Qdrant: {query}")

        try:
            # Performance tracking for embedding generation
            embedding_start = time.time()

            # 1. Generate query embedding
            query_embedding = self.embed_model.get_text_embedding(query)
            embedding_time = (time.time() - embedding_start) * 1000

            logger.info(f"✅ Generated query embedding in {embedding_time:.2f}ms")

            # 2. Optimized Qdrant query with better parameters
            search_start = time.time()

            # Use optimized top_k for better quality/performance balance
            optimized_top_k = min(max(top_k, 10), 20)  # Between 10-20 for better coverage

            similar_chunks = await self.qdrant_service.similarity_search(
                query_embedding=query_embedding,
                top_k=optimized_top_k,  # Use optimized top_k
                score_threshold=self.settings.SIMILARITY_THRESHOLD,
                doc_filters=doc_filters
            )

            search_time = (time.time() - search_start) * 1000
            logger.info(f"✅ Found {len(similar_chunks)} similar chunks from Qdrant in {search_time:.2f}ms")

            # 3. Enhanced chunk ranking and filtering for better quality
            if similar_chunks:
                # Filter and rank chunks for better quality
                filtered_chunks = self._filter_and_rank_chunks(similar_chunks, query, top_k)

                if not filtered_chunks:
                    logger.warning("No high-quality chunks found after filtering")
                    return "Entschuldigung, ich konnte keine relevanten Informationen finden.", []

                context_texts = [chunk["content"] for chunk in filtered_chunks]
                context = "\n\n".join(context_texts)

                # 4. Optimized LLM generation with performance tracking
                llm_start = time.time()

                # Create prompt for LLM
                prompt = f"""Context:
{context}

Question: {query}

Answer based on the context above:"""

                response = await self.llm.acomplete(prompt)
                response_text = str(response).strip()

                llm_time = (time.time() - llm_start) * 1000
                logger.info(f"✅ Generated LLM response in {llm_time:.2f}ms")

                # Format source documents with enhanced metadata
                source_docs = []
                for chunk in filtered_chunks:
                    source_docs.append({
                        "content": chunk["content"],
                        "metadata": {
                            **chunk["metadata"],
                            "relevance_score": chunk["score"],
                            "quality_score": self._calculate_chunk_quality(chunk, query)
                        },
                        "score": chunk["score"]
                    })

                logger.info(f"✅ Generated LLM response using {len(filtered_chunks)} high-quality chunks")
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
                "service": "QdrantRAGService",
                "status": "healthy",
                "initialized": self._initialized,
                "qdrant": await self.qdrant_service.health_check() if self.qdrant_service else {"status": "not_initialized"}
            }

            return health

        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "service": "QdrantRAGService",
                "status": "unhealthy",
                "error": str(e)
            }

    async def health_check(self) -> Dict[str, Any]:
        """Alias for get_health_status for compatibility"""
        return await self.get_health_status()

    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete document from Qdrant with verification and retry logic

        Args:
            doc_id: Document ID to delete

        Returns:
            Success status
        """
        try:
            logger.info(f"🗑️ Starting comprehensive deletion for document {doc_id} from Qdrant")

            if not self.qdrant_service:
                await self.initialize()

            # Step 1: Check if chunks exist before deletion
            try:
                existing_chunks = await self.qdrant_service.get_document_chunks(doc_id, limit=1)
                chunk_count = len(existing_chunks) if existing_chunks else 0
                logger.info(f"📊 Found {chunk_count} chunks to delete for document {doc_id}")

                if chunk_count == 0:
                    logger.info(f"✅ No chunks found for document {doc_id} - already clean")
                    return True
            except Exception as count_error:
                logger.warning(f"⚠️ Could not count chunks for {doc_id}: {str(count_error)}")

            # Step 2: Perform deletion with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    success = await self.qdrant_service.delete_documents(doc_id)

                    if success:
                        # Step 3: Verify deletion was successful
                        try:
                            remaining_chunks = await self.qdrant_service.get_document_chunks(doc_id, limit=1)
                            remaining_count = len(remaining_chunks) if remaining_chunks else 0

                            if remaining_count == 0:
                                logger.info(f"✅ Successfully verified deletion of document {doc_id} from Qdrant")
                                return True
                            else:
                                logger.warning(f"⚠️ Deletion incomplete - {remaining_count} chunks still remain for {doc_id}")
                                if attempt < max_retries - 1:
                                    logger.info(f"🔄 Retrying deletion (attempt {attempt + 2}/{max_retries})")
                                    continue
                                else:
                                    return False
                        except Exception as verify_error:
                            logger.warning(f"⚠️ Could not verify deletion for {doc_id}: {str(verify_error)}")
                            return success  # Trust the deletion result if verification fails
                    else:
                        logger.warning(f"⚠️ Document {doc_id} deletion attempt {attempt + 1} failed")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)  # Brief delay before retry
                            continue
                        return False

                except Exception as delete_error:
                    logger.error(f"❌ Deletion attempt {attempt + 1} failed for {doc_id}: {str(delete_error)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)  # Brief delay before retry
                        continue
                    raise delete_error

            return False

        except Exception as e:
            logger.error(f"❌ Complete deletion failure for document {doc_id}: {str(e)}")
            return False

    async def delete_documents_bulk(self, doc_ids: List[str]) -> Dict[str, Any]:
        """
        Efficiently delete multiple documents from Qdrant

        Args:
            doc_ids: List of document IDs to delete

        Returns:
            Dict with deletion results and statistics
        """
        try:
            start_time = time.time()
            logger.info(f"🗑️ Starting bulk deletion for {len(doc_ids)} documents from Qdrant")

            if not self.qdrant_service:
                await self.initialize()

            results = {
                "success": [],
                "failed": [],
                "total_requested": len(doc_ids),
                "total_deleted": 0,
                "total_failed": 0,
                "processing_time_ms": 0
            }

            # Process deletions in parallel batches of 5 for better performance
            batch_size = 5
            batches = [doc_ids[i:i + batch_size] for i in range(0, len(doc_ids), batch_size)]

            for batch_idx, batch in enumerate(batches):
                logger.info(f"🔄 Processing batch {batch_idx + 1}/{len(batches)} ({len(batch)} documents)")

                # Create deletion tasks for this batch
                tasks = [self.delete_document(doc_id) for doc_id in batch]

                # Execute batch in parallel
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process batch results
                for doc_id, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"❌ Batch deletion failed for {doc_id}: {str(result)}")
                        results["failed"].append({
                            "doc_id": doc_id,
                            "error": str(result)
                        })
                    elif result is True:
                        logger.debug(f"✅ Successfully deleted {doc_id}")
                        results["success"].append(doc_id)
                    else:
                        logger.warning(f"⚠️ Deletion returned false for {doc_id}")
                        results["failed"].append({
                            "doc_id": doc_id,
                            "error": "Deletion returned false"
                        })

                # Brief pause between batches to avoid overwhelming Qdrant
                if batch_idx < len(batches) - 1:
                    await asyncio.sleep(0.1)

            # Calculate final statistics
            results["total_deleted"] = len(results["success"])
            results["total_failed"] = len(results["failed"])
            results["processing_time_ms"] = int((time.time() - start_time) * 1000)

            success_rate = (results["total_deleted"] / results["total_requested"]) * 100 if results["total_requested"] > 0 else 0

            logger.info(f"✅ Bulk deletion completed: {results['total_deleted']}/{results['total_requested']} deleted ({success_rate:.1f}% success rate) in {results['processing_time_ms']}ms")

            return results

        except Exception as e:
            logger.error(f"❌ Bulk deletion failed: {str(e)}")
            return {
                "success": [],
                "failed": [{"error": f"Bulk deletion failed: {str(e)}"}],
                "total_requested": len(doc_ids),
                "total_deleted": 0,
                "total_failed": len(doc_ids),
                "processing_time_ms": int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
            }

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

    async def query(
        self,
        query: str,
        mode: str = "fast",
        max_chunks: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[List[Dict]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy compatibility method for old chat service interface
        Maps to query_documents method
        """
        try:
            response_text, source_documents = await self.query_documents(
                query=query,
                doc_filters=filters,
                top_k=max_chunks
            )

            # Format response to match expected interface
            return {
                "answer": response_text,
                "metadata": {
                    "sources": source_documents,
                    "mode": mode,
                    "chunks_used": len(source_documents),
                    "confidence_score": 0.8 if source_documents else 0.0
                }
            }

        except Exception as e:
            logger.error(f"❌ Query compatibility wrapper failed: {str(e)}")
            return {
                "answer": "Entschuldigung, bei der Verarbeitung Ihrer Anfrage ist ein Problem aufgetreten.",
                "metadata": {
                    "sources": [],
                    "mode": mode,
                    "chunks_used": 0,
                    "confidence_score": 0.0,
                    "error": str(e)
                }
            }

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

    async def generate_xml(self, wizard_data) -> Dict[str, Any]:
        """
        Generate StreamWorks XML using LLM with structured JSON output
        Uses OpenAI JSON mode for better structured generation
        """
        try:
            from .llm_factory import get_llm_service
            from schemas.xml_generation import XMLGenerationResult

            logger.info("🔧 Generating XML using LLM with JSON mode")

            # Get LLM service via factory
            llm_service = await get_llm_service()

            # Check if OpenAI service (supports JSON mode)
            if hasattr(llm_service, 'generate_json'):
                return await self._generate_xml_with_json_mode(llm_service, wizard_data)
            else:
                return await self._generate_xml_with_text_mode(llm_service, wizard_data)

        except Exception as e:
            logger.error(f"❌ XML generation failed: {str(e)}")
            return XMLGenerationResult(
                success=False,
                xml_content="",
                error_message=f"XML generation failed: {str(e)}",
                generation_time_ms=0
            )

    async def _generate_xml_with_json_mode(self, llm_service, wizard_data) -> Dict[str, Any]:
        """Generate XML using OpenAI JSON mode for structured output"""
        try:
            import time
            start_time = time.time()

            # Create structured prompt for JSON mode
            system_prompt = """You are an expert in StreamWorks XML generation. Generate a valid StreamWorks XML structure based on the provided wizard data.

Return your response as JSON with this structure:
{
    "xml_content": "complete XML content here",
    "validation_notes": ["array of validation notes"],
    "generation_notes": "any notes about the generation process"
}"""

            user_prompt = f"""Generate a StreamWorks XML based on this wizard data:

Stream Name: {getattr(wizard_data.stream_properties, 'name', 'Unknown Stream')}
Description: {getattr(wizard_data.stream_properties, 'description', 'No description')}
Job Type: {getattr(wizard_data.job_properties, 'job_type', 'STANDARD')}

Requirements:
1. Valid XML syntax
2. Complete StreamWorks structure
3. Proper CDATA sections for scripts and descriptions
4. Default agent: gtasswvk05445
5. Include all required elements for a functional stream

Generate complete, valid StreamWorks XML."""

            # Generate JSON response
            result = await llm_service.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt
            )

            generation_time_ms = int((time.time() - start_time) * 1000)

            if result.get("json") and result["json"].get("xml_content"):
                from schemas.xml_generation import XMLGenerationResult
                return XMLGenerationResult(
                    success=True,
                    xml_content=result["json"]["xml_content"],
                    generation_time_ms=generation_time_ms,
                    validation_notes=result["json"].get("validation_notes", []),
                    generation_source="llm_json",
                    metadata={
                        "provider": "openai",
                        "model": getattr(llm_service, 'model', 'unknown'),
                        "generation_notes": result["json"].get("generation_notes", ""),
                        "usage": result.get("usage", {})
                    }
                )
            else:
                raise Exception("LLM did not return valid JSON with xml_content")

        except Exception as e:
            logger.error(f"JSON mode XML generation failed: {str(e)}")
            raise

    async def _generate_xml_with_text_mode(self, llm_service, wizard_data) -> Dict[str, Any]:
        """Generate XML using text-based LLM (fallback for Ollama)"""
        try:
            import time
            start_time = time.time()

            prompt = f"""Generate a complete StreamWorks XML based on this data:

Stream Name: {getattr(wizard_data.stream_properties, 'name', 'Unknown Stream')}
Description: {getattr(wizard_data.stream_properties, 'description', 'No description')}
Job Type: {getattr(wizard_data.job_properties, 'job_type', 'STANDARD')}

Requirements:
- Start with <?xml version="1.0" encoding="utf-8"?>
- Use ExportableStream as root element
- Include Stream with StreamName, StreamDocumentation, AgentDetail=gtasswvk05445
- Include Jobs with at least one Job element
- Use CDATA for scripts and descriptions
- Return ONLY the XML, no additional text

Generate the complete XML now:"""

            response = await llm_service.generate(prompt)
            generation_time_ms = int((time.time() - start_time) * 1000)

            # Extract XML from response (in case there's extra text)
            xml_content = self._extract_xml_from_response(response)

            from schemas.xml_generation import XMLGenerationResult
            return XMLGenerationResult(
                success=True,
                xml_content=xml_content,
                generation_time_ms=generation_time_ms,
                generation_source="llm_text",
                metadata={
                    "provider": self.settings.LLM_PROVIDER,
                    "raw_response_length": len(response),
                    "extracted_xml_length": len(xml_content)
                }
            )

        except Exception as e:
            logger.error(f"Text mode XML generation failed: {str(e)}")
            raise

    def _extract_xml_from_response(self, response: str) -> str:
        """Extract XML content from LLM response"""
        import re

        # Look for XML content between <?xml and final closing tag
        xml_match = re.search(
            r'(<\?xml.*?</ExportableStream>)',
            response,
            re.DOTALL | re.IGNORECASE
        )

        if xml_match:
            return xml_match.group(1).strip()

        # Fallback: look for any content that starts with <?xml
        lines = response.strip().split('\n')
        xml_lines = []
        in_xml = False

        for line in lines:
            if line.strip().startswith('<?xml'):
                in_xml = True
            if in_xml:
                xml_lines.append(line)
            if in_xml and '</ExportableStream>' in line:
                break

        return '\n'.join(xml_lines) if xml_lines else response.strip()

    def _filter_and_rank_chunks(self, chunks: List[Dict], query: str, top_k: int) -> List[Dict]:
        """
        Filter and rank chunks for better quality and relevance - PERFORMANCE OPTIMIZED

        Args:
            chunks: Raw chunks from Qdrant
            query: Original query
            top_k: Number of top chunks to return

        Returns:
            Filtered and ranked chunks
        """
        if not chunks:
            return []

        # Calculate enhanced scores for each chunk
        enhanced_chunks = []
        query_words = set(query.lower().split())

        for chunk in chunks:
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})

            # Original similarity score
            similarity_score = chunk.get("score", 0.0)

            # Content quality score
            content_quality = self._calculate_content_quality(content)

            # Keyword overlap score
            content_words = set(content.lower().split())
            keyword_overlap = len(query_words & content_words) / max(len(query_words), 1)

            # Document type bonus (prefer certain document types)
            doc_type_bonus = self._get_doc_type_bonus(metadata.get("doctype", ""))

            # Length penalty for very short or very long chunks
            length_penalty = self._calculate_length_penalty(content)

            # Combined score
            enhanced_score = (
                similarity_score * 0.4 +           # Original similarity
                content_quality * 0.25 +           # Content quality
                keyword_overlap * 0.2 +            # Keyword relevance
                doc_type_bonus * 0.1 +             # Document type preference
                length_penalty * 0.05              # Length appropriateness
            )

            enhanced_chunks.append({
                **chunk,
                "enhanced_score": enhanced_score,
                "content_quality": content_quality,
                "keyword_overlap": keyword_overlap
            })

        # Sort by enhanced score
        enhanced_chunks.sort(key=lambda x: x["enhanced_score"], reverse=True)

        # Apply quality filter - only keep chunks above minimum quality threshold
        min_quality_threshold = 0.3
        filtered_chunks = [
            chunk for chunk in enhanced_chunks
            if chunk["enhanced_score"] > min_quality_threshold
        ]

        # Return top chunks, but ensure we have at least some results
        if not filtered_chunks and enhanced_chunks:
            # If no chunks meet the quality threshold, return top 3 anyway
            return enhanced_chunks[:3]

        return filtered_chunks[:top_k]

    def _calculate_content_quality(self, content: str) -> float:
        """Calculate content quality score (0-1)"""
        if not content or len(content.strip()) < 20:
            return 0.0

        quality_score = 0.0

        # Length appropriateness (prefer 100-1000 characters)
        length = len(content)
        if 100 <= length <= 1000:
            quality_score += 0.3
        elif 50 <= length <= 1500:
            quality_score += 0.2
        else:
            quality_score += 0.1

        # Sentence structure
        sentences = content.split('.')
        if 2 <= len(sentences) <= 10:
            quality_score += 0.2

        # Word variety (simple measure)
        words = content.lower().split()
        unique_words = set(words)
        if len(words) > 0:
            variety_ratio = len(unique_words) / len(words)
            quality_score += variety_ratio * 0.3

        # Avoid repetitive content
        if len(set(content.split('\n'))) > 1:
            quality_score += 0.2

        return min(quality_score, 1.0)

    def _get_doc_type_bonus(self, doctype: str) -> float:
        """Get bonus score based on document type"""
        doc_type_scores = {
            "pdf": 0.8,
            "docx": 0.7,
            "txt": 0.6,
            "html": 0.5,
            "xml": 0.4,
            "general": 0.5
        }
        return doc_type_scores.get(doctype.lower(), 0.5)

    def _calculate_length_penalty(self, content: str) -> float:
        """Calculate penalty/bonus based on content length"""
        length = len(content)

        if 200 <= length <= 800:
            return 1.0  # Optimal length
        elif 100 <= length <= 1200:
            return 0.8  # Good length
        elif 50 <= length <= 1500:
            return 0.6  # Acceptable length
        else:
            return 0.3  # Too short or too long

    def _calculate_chunk_quality(self, chunk: Dict, query: str) -> float:
        """Calculate overall chunk quality for metadata"""
        content = chunk.get("content", "")
        similarity_score = chunk.get("score", 0.0)

        # Combine multiple quality factors
        content_quality = self._calculate_content_quality(content)

        # Query relevance
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        relevance = len(query_words & content_words) / max(len(query_words), 1)

        # Combined quality score
        quality_score = (
            similarity_score * 0.4 +
            content_quality * 0.4 +
            relevance * 0.2
        )

        return min(quality_score, 1.0)


# Global service instance
_rag_service = None

async def get_rag_service() -> QdrantRAGService:
    """Get global RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = QdrantRAGService()
    return _rag_service