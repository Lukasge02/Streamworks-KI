"""
Mistral LLM Client - Enterprise Implementation
Handles all interactions with Mistral model via Ollama
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
import json
from datetime import datetime

from ...core.config import settings

logger = logging.getLogger(__name__)

class MistralClient:
    """
    Enterprise Mistral Client with proper error handling and monitoring
    """
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
        
    async def _ensure_session(self):
        """Ensure aiohttp session is created"""
        if not self._session:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
    
    async def initialize(self):
        """Initialize the client and verify model availability"""
        try:
            await self._ensure_session()
            
            # Check if model is available
            async with self._session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    if self.model not in models:
                        logger.warning(f"Model {self.model} not found. Available: {models}")
                        # Try to pull the model
                        await self._pull_model()
                    else:
                        logger.info(f"✅ Mistral model {self.model} is available")
                        self._initialized = True
                        
        except Exception as e:
            logger.error(f"Failed to initialize Mistral client: {e}")
            raise
    
    async def _pull_model(self):
        """Pull the model if not available"""
        try:
            logger.info(f"Pulling model {self.model}...")
            async with self._session.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model}
            ) as response:
                if response.status == 200:
                    # Stream the response to show progress
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                if "status" in data:
                                    logger.info(f"Pull status: {data['status']}")
                            except json.JSONDecodeError:
                                pass
                    logger.info(f"✅ Model {self.model} pulled successfully")
                    self._initialized = True
                else:
                    logger.error(f"Failed to pull model: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            raise
    
    async def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None,
        top_k: int = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response from Mistral model
        
        Args:
            prompt: User prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            system_prompt: System instruction
            
        Returns:
            Response dictionary with generated text and metadata
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            await self._ensure_session()
            
            # Build the full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Prepare parameters
            params = {
                "model": self.model,
                "prompt": full_prompt,
                "temperature": temperature or settings.MODEL_TEMPERATURE,
                "top_p": top_p or settings.MODEL_TOP_P,
                "top_k": top_k or settings.MODEL_TOP_K,
                "num_predict": max_tokens or settings.MODEL_MAX_TOKENS,
                "repeat_penalty": settings.MODEL_REPEAT_PENALTY,
                "stream": False
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            start_time = datetime.now()
            
            # Make request
            async with self._session.post(
                f"{self.base_url}/api/generate",
                json=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        "response": data.get("response", ""),
                        "model": self.model,
                        "total_duration": data.get("total_duration", 0) / 1e9,  # Convert to seconds
                        "load_duration": data.get("load_duration", 0) / 1e9,
                        "prompt_eval_duration": data.get("prompt_eval_duration", 0) / 1e9,
                        "eval_duration": data.get("eval_duration", 0) / 1e9,
                        "eval_count": data.get("eval_count", 0),
                        "processing_time": processing_time,
                        "context": data.get("context", [])
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Mistral API error: {response.status} - {error_text}")
                    raise Exception(f"Mistral API error: {response.status}")
                    
        except asyncio.TimeoutError:
            logger.error("Mistral request timed out")
            raise Exception("Request timed out - please try again")
        except Exception as e:
            logger.error(f"Mistral generation error: {e}")
            raise
    
    async def generate_embedding(
        self,
        text: str
    ) -> List[float]:
        """
        Generate embedding for text using Mistral
        Note: Mistral 7B doesn't natively support embeddings,
        so this would need a separate embedding model
        """
        # For now, we'll use the embedding model specified in settings
        # This is typically handled by the VectorDB client
        raise NotImplementedError(
            "Embeddings should be generated via the embedding service"
        )
    
    async def close(self):
        """Close the client session"""
        if self._session:
            await self._session.close()
            self._session = None
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._session:
            asyncio.create_task(self.close())