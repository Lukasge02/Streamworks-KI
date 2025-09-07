"""
Embedding Service für Streamworks RAG MVP
Erstellt OpenAI Embeddings für document chunks
"""

import asyncio
import logging
from typing import List, Dict, Any, Union, Optional
import numpy as np
import openai
from openai import AsyncOpenAI
import tiktoken
import torch

from config import settings
from .docling_ingest import DocumentChunk

logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, falling back to OpenAI only")

class LocalGammaEmbedder:
    """Local Gamma embedding model handler"""
    
    def __init__(self, model_name: str = None, device: str = "auto"):
        # Use configured model if not provided
        if model_name is None:
            from config import settings
            model_name = getattr(settings, 'GAMMA_MODEL_NAME', "google/embeddinggemma-300m")
        
        self.model_name = model_name
        self.model = None
        self.device = device
        self._initialized = False
        self._initialization_error = None
        
    def _initialize(self):
        """Lazy initialization of local embedding model"""
        if self._initialized:
            return True
            
        if self._initialization_error:
            raise self._initialization_error
            
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")
            
        try:
            # Auto-detect device if needed
            if self.device == "auto":
                if torch.backends.mps.is_available():
                    self.device = "mps"
                elif torch.cuda.is_available():
                    self.device = "cuda" 
                else:
                    self.device = "cpu"
            
            logger.info(f"Initializing local embedding model {self.model_name} on {self.device}")
            
            # Load the model with trust_remote_code for custom models
            self.model = SentenceTransformer(self.model_name, device=self.device, trust_remote_code=True)
            self.model.eval()  # Set to evaluation mode
            
            # Get model dimensions
            self.dimensions = self.model.get_sentence_embedding_dimension()
            
            self._initialized = True
            logger.info(f"✅ Local embedding model loaded: {self.model_name} ({self.dimensions}D) on {self.device}")
            return True
            
        except Exception as e:
            self._initialization_error = e
            logger.error(f"Failed to initialize local embedding model: {str(e)}")
            raise e
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Create embeddings for texts using local model
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not self._initialize():
            raise RuntimeError("Local embedding model not initialized")
        
        try:
            # Process in batches to manage memory
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Generate embeddings - use appropriate method for EmbeddingGemma
                with torch.no_grad():
                    # Check if this is EmbeddingGemma model
                    if "embeddinggemma" in self.model_name.lower():
                        # EmbeddingGemma uses encode_document for document embeddings
                        embeddings = self.model.encode_document(
                            batch,
                            convert_to_tensor=False,
                            show_progress_bar=False
                        )
                    else:
                        # Standard sentence-transformers models
                        embeddings = self.model.encode(
                            batch,
                            convert_to_tensor=False,
                            show_progress_bar=False,
                            normalize_embeddings=True  # Normalize for better similarity
                        )
                
                # Convert to list of lists
                if isinstance(embeddings, np.ndarray):
                    embeddings = embeddings.tolist()
                elif hasattr(embeddings, 'cpu'):
                    embeddings = embeddings.cpu().numpy().tolist()
                
                all_embeddings.extend(embeddings)
                
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Local embedding generation failed: {str(e)}")
            raise Exception(f"Local embedding error: {str(e)}")
    
    def embed_query(self, query: str) -> List[float]:
        """
        Create embedding for a search query using local model
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding vector
        """
        if not self._initialize():
            raise RuntimeError("Local embedding model not initialized")
        
        try:
            with torch.no_grad():
                # Check if this is EmbeddingGemma model
                if "embeddinggemma" in self.model_name.lower():
                    # EmbeddingGemma uses encode_query for query embeddings
                    embedding = self.model.encode_query(
                        query,
                        convert_to_tensor=False
                    )
                else:
                    # Standard sentence-transformers models
                    embedding = self.model.encode(
                        [query],
                        convert_to_tensor=False,
                        show_progress_bar=False,
                        normalize_embeddings=True
                    )[0]
                
                # Convert to list
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                elif hasattr(embedding, 'cpu'):
                    embedding = embedding.cpu().numpy().tolist()
                    
                return embedding
                
        except Exception as e:
            logger.error(f"Local query embedding generation failed: {str(e)}")
            raise Exception(f"Local query embedding error: {str(e)}")


class EmbeddingService:
    """Hybrid embedding service with local Gamma and OpenAI support"""
    
    def __init__(self):
        # OpenAI setup
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.openai_model = settings.EMBEDDING_MODEL
        self.encoding = tiktoken.encoding_for_model("text-embedding-3-large")
        self.max_tokens = 8191  # OpenAI embedding limit
        
        # Local model setup
        self.local_embedder = None
        self.provider = getattr(settings, 'EMBEDDING_PROVIDER', 'gamma')  # gamma|openai|hybrid
        self.enable_fallback = getattr(settings, 'ENABLE_EMBEDDING_FALLBACK', True)
        
        logger.info(f"EmbeddingService initialized with provider: {self.provider}")
        
    def _get_local_embedder(self) -> Optional[LocalGammaEmbedder]:
        """Get local embedder with lazy loading"""
        if self.local_embedder is None:
            try:
                # Let LocalGammaEmbedder use its configured model from settings
                device = getattr(settings, 'LOCAL_EMBEDDING_DEVICE', 'auto')
                self.local_embedder = LocalGammaEmbedder(device=device)
                logger.info("Local Gamma embedder initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize local embedder: {str(e)}")
                if not self.enable_fallback:
                    raise e
                return None
        return self.local_embedder
        
    async def embed_chunks(self, chunks: List[Union[DocumentChunk, Dict[str, Any]]]) -> List[Union[DocumentChunk, Dict[str, Any]]]:
        """
        Create embeddings for document chunks using selected provider
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            Same chunks with embeddings added to metadata
        """
        try:
            # Prepare texts for embedding
            texts = []
            for chunk in chunks:
                # Combine content with metadata for better embeddings
                enhanced_text = self._enhance_text_for_embedding(chunk)
                texts.append(enhanced_text)
            
            # Choose embedding method based on provider
            if self.provider == "gamma":
                embeddings = await self._embed_with_local(texts)
                model_name = getattr(settings, 'GAMMA_MODEL_NAME', "google/embeddinggemma-300m")
            elif self.provider == "openai":
                embeddings = await self._embed_with_openai(texts)
                model_name = self.openai_model
            else:  # hybrid - try local first, fallback to OpenAI
                try:
                    embeddings = await self._embed_with_local(texts)
                    model_name = getattr(settings, 'GAMMA_MODEL_NAME', "google/embeddinggemma-300m")
                    logger.info("Used local Gamma embeddings")
                except Exception as e:
                    logger.warning(f"Local embedding failed, falling back to OpenAI: {str(e)}")
                    embeddings = await self._embed_with_openai(texts)
                    model_name = self.openai_model
            
            # Add embeddings to chunk metadata
            for i, embedding in enumerate(embeddings):
                if isinstance(chunks[i], dict):
                    # Dictionary format from unified storage
                    chunks[i]['metadata']['embedding'] = embedding
                    chunks[i]['metadata']['embedding_model'] = model_name
                    chunks[i]['metadata']['embedding_provider'] = self.provider
                else:
                    # DocumentChunk object format
                    chunks[i].metadata['embedding'] = embedding
                    chunks[i].metadata['embedding_model'] = model_name
                    chunks[i].metadata['embedding_provider'] = self.provider
            
            logger.info(f"✅ Created {len(embeddings)} embeddings using {model_name}")
            return chunks
            
        except Exception as e:
            logger.error(f"Embedding creation failed: {str(e)}")
            raise Exception(f"Embedding service error: {str(e)}")
    
    async def _embed_with_local(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using local Gamma model"""
        local_embedder = self._get_local_embedder()
        if not local_embedder:
            raise RuntimeError("Local embedder not available")
        
        # Truncate texts for local model (usually more permissive than OpenAI)
        processed_texts = []
        for text in texts:
            # Most local models can handle longer texts, but let's be conservative
            if len(text) > 8000:  # Conservative limit
                text = text[:8000] + "..."
            processed_texts.append(text)
        
        # Run in thread pool to avoid blocking
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        def run_local_embedding():
            batch_size = getattr(settings, 'BATCH_SIZE_LOCAL', 32)
            return local_embedder.embed_texts(processed_texts, batch_size=batch_size)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            embeddings = await loop.run_in_executor(executor, run_local_embedding)
        
        return embeddings
    
    async def _embed_with_openai(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using OpenAI API"""
        # Truncate texts for OpenAI token limits
        processed_texts = []
        for text in texts:
            processed_texts.append(self._truncate_text(text))
        
        embeddings = []
        batch_size = 100  # OpenAI recommendation
        
        for i in range(0, len(processed_texts), batch_size):
            batch_texts = processed_texts[i:i + batch_size]
            
            # Get embeddings from OpenAI
            response = await self.openai_client.embeddings.create(
                model=self.openai_model,
                input=batch_texts,
                encoding_format="float"
            )
            
            # Extract embeddings
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
            
            logger.info(f"✅ Created OpenAI embeddings for batch {i//batch_size + 1}/{(len(processed_texts)-1)//batch_size + 1}")
        
        return embeddings
    
    def _enhance_text_for_embedding(self, chunk: Union[DocumentChunk, Dict[str, Any]]) -> str:
        """
        Enhance text with context for better embeddings
        """
        parts = []
        
        # Handle both DocumentChunk objects and dictionary format
        if isinstance(chunk, dict):
            # Dictionary format from unified storage
            text = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            doctype = metadata.get("doctype")
            heading = metadata.get("heading")
            page_number = metadata.get("page")
        else:
            # DocumentChunk object format
            text = chunk.content
            doctype = chunk.doctype
            heading = chunk.heading
            page_number = chunk.page_number
        
        # Add document type context
        if doctype and doctype != "general":
            parts.append(f"Document type: {doctype}")
        
        # Add section/heading context
        if heading:
            parts.append(f"Section: {heading}")
        
        # Add main content
        parts.append(text)
        
        # Add page context if available
        if page_number:
            parts.append(f"Page: {page_number}")
        
        return " | ".join(parts)
    
    def _truncate_text(self, text: str) -> str:
        """
        Truncate text to fit OpenAI embedding token limits
        """
        tokens = self.encoding.encode(text)
        
        if len(tokens) <= self.max_tokens:
            return text
        
        # Truncate tokens and decode back to text
        truncated_tokens = tokens[:self.max_tokens]
        return self.encoding.decode(truncated_tokens)
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Create embedding for a search query using selected provider
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding vector
        """
        try:
            # Choose embedding method based on provider
            if self.provider == "gamma":
                embeddings = await self._embed_with_local([query])
                return embeddings[0]
            elif self.provider == "openai":
                embeddings = await self._embed_with_openai([query])
                return embeddings[0]
            else:  # hybrid - try local first, fallback to OpenAI
                try:
                    embeddings = await self._embed_with_local([query])
                    return embeddings[0]
                except Exception as e:
                    logger.warning(f"Local query embedding failed, falling back to OpenAI: {str(e)}")
                    embeddings = await self._embed_with_openai([query])
                    return embeddings[0]
            
        except Exception as e:
            logger.error(f"Query embedding failed: {str(e)}")
            raise Exception(f"Query embedding error: {str(e)}")
    
    def get_embedding(self, query: str) -> List[float]:
        """
        Synchronous wrapper for embed_query - for use in LangGraph nodes
        
        Args:
            query: Search query string
            
        Returns:
            Query embedding vector
        """
        import asyncio
        try:
            # Get current event loop or create new one
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to use a different approach
                # This is a workaround for sync calls in async environments
                import concurrent.futures
                import threading
                
                def run_async():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.embed_query(query))
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async)
                    return future.result(timeout=30)  # 30 second timeout
            else:
                # No event loop running, we can run directly
                return loop.run_until_complete(self.embed_query(query))
        except Exception as e:
            print(f"❌ Sync embedding failed: {str(e)}")
            # Fallback: return a zero vector of appropriate size
            return [0.0] * 3072  # text-embedding-3-large dimension
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        try:
            a_array = np.array(a)
            b_array = np.array(b)
            
            dot_product = np.dot(a_array, b_array)
            norm_a = np.linalg.norm(a_array)
            norm_b = np.linalg.norm(b_array)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
            
        except Exception:
            return 0.0
    
    async def batch_similarity(
        self, 
        query_embedding: List[float], 
        chunk_embeddings: List[List[float]]
    ) -> List[float]:
        """
        Calculate similarities between query and multiple chunk embeddings
        """
        similarities = []
        
        for chunk_embedding in chunk_embeddings:
            similarity = self.cosine_similarity(query_embedding, chunk_embedding)
            similarities.append(similarity)
        
        return similarities