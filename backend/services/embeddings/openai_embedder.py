"""
OpenAI embedding provider implementation
"""
import logging
import asyncio
from typing import List, Optional
import openai
from openai import AsyncOpenAI
import tiktoken

from .base import EmbeddingInterface, EmbeddingException
from config import settings

logger = logging.getLogger(__name__)


class OpenAIEmbedder(EmbeddingInterface):
    """OpenAI embedding provider"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: str = "text-embedding-3-large",
                 max_tokens: int = 8191):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.max_tokens = max_tokens
        self.client = None
        self.encoding = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize the OpenAI client"""
        if self._initialized:
            return
            
        try:
            self.client = AsyncOpenAI(api_key=self.api_key)
            self.encoding = tiktoken.encoding_for_model("text-embedding-3-large")
            self._initialized = True
            logger.info(f"OpenAI embedder initialized with model {self.model}")
        except Exception as e:
            raise EmbeddingException(f"Failed to initialize OpenAI embedder: {str(e)}")
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.client:
            await self.client.close()
            self.client = None
            self._initialized = False
    
    def _truncate_text(self, text: str) -> str:
        """Truncate text to fit within token limits"""
        if not self.encoding:
            # Fallback to character limit if encoding not available
            max_chars = self.max_tokens * 4  # Rough estimate
            if len(text) > max_chars:
                return text[:max_chars]
            return text
        
        tokens = self.encoding.encode(text)
        if len(tokens) > self.max_tokens:
            tokens = tokens[:self.max_tokens]
            return self.encoding.decode(tokens)
        return text
    
    async def embed_texts(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using OpenAI
        
        Args:
            texts: List of texts to embed
            **kwargs: Additional arguments
            
        Returns:
            List of embedding vectors
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Truncate texts to fit token limits
            truncated_texts = [self._truncate_text(text) for text in texts]
            
            # OpenAI batch embedding
            response = await self.client.embeddings.create(
                model=self.model,
                input=truncated_texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            logger.debug(f"Generated {len(embeddings)} OpenAI embeddings")
            return embeddings
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise EmbeddingException(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {str(e)}")
            raise EmbeddingException(f"OpenAI embedding error: {str(e)}")
    
    async def embed_query(self, query: str, **kwargs) -> List[float]:
        """
        Generate embedding for a search query using OpenAI
        
        Args:
            query: Query text to embed
            **kwargs: Additional arguments
            
        Returns:
            Query embedding vector
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Truncate query if needed
            truncated_query = self._truncate_text(query)
            
            # Generate single embedding
            response = await self.client.embeddings.create(
                model=self.model,
                input=truncated_query
            )
            
            embedding = response.data[0].embedding
            
            logger.debug(f"Generated OpenAI query embedding")
            return embedding
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error for query: {str(e)}")
            raise EmbeddingException(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"OpenAI query embedding failed: {str(e)}")
            raise EmbeddingException(f"OpenAI query embedding error: {str(e)}")
    
    async def embed_texts_with_retry(self, 
                                    texts: List[str], 
                                    max_retries: int = 3,
                                    retry_delay: float = 1.0) -> List[List[float]]:
        """
        Generate embeddings with retry logic for rate limiting
        
        Args:
            texts: List of texts to embed
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            List of embedding vectors
        """
        for attempt in range(max_retries):
            try:
                return await self.embed_texts(texts)
            except EmbeddingException as e:
                if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                    logger.warning(f"Rate limit hit, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise
        
        raise EmbeddingException(f"Failed to generate embeddings after {max_retries} attempts")