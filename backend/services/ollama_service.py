"""
Ollama LLM Service für lokale KI-Integration
Provides local LLM capabilities for RAG without external API dependencies
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for interacting with local Ollama models"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes for larger models
        
    async def health_check(self) -> Dict[str, Any]:
        """Check if Ollama is running and available"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        models = await response.json()
                        return {
                            "status": "healthy",
                            "available_models": [model["name"] for model in models.get("models", [])],
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
        except Exception as e:
            logger.error(f"Ollama health check failed: {str(e)}")
            return {
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available Ollama models"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("models", [])
                    else:
                        logger.error(f"Failed to list models: HTTP {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []
    
    async def generate_completion(
        self,
        prompt: str,
        model: str = "qwen2.5:7b",
        max_tokens: int = 2000,
        temperature: float = 0.1,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate completion using Ollama model"""
        start_time = time.time()
        
        try:
            # Build the prompt with system context
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "stop": ["User:", "System:"]
                }
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        processing_time_ms = int((time.time() - start_time) * 1000)
                        
                        return {
                            "response": result.get("response", "").strip(),
                            "model": model,
                            "processing_time_ms": processing_time_ms,
                            "prompt_tokens": result.get("prompt_eval_count", 0),
                            "completion_tokens": result.get("eval_count", 0),
                            "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0),
                            "done": result.get("done", False)
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama generate failed: HTTP {response.status} - {error_text}")
                        raise Exception(f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"Ollama completion failed: {str(e)}")
            raise Exception(f"Local LLM error: {str(e)}")

    async def generate(
        self,
        prompt: str,
        model: str = "qwen2.5:7b",
        temperature: float = 0.1
    ) -> str:
        """
        Simple generate method that returns only the response text
        Compatible with DocumentSummarizer usage
        """
        try:
            result = await self.generate_completion(
                prompt=prompt,
                model=model,
                temperature=temperature
            )
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama generate failed: {str(e)}")
            return ""

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "qwen2.5:7b",
        max_tokens: int = 2000,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Chat completion compatible with OpenAI format"""
        start_time = time.time()
        
        try:
            # Convert messages to single prompt for Ollama
            prompt_parts = []
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    prompt_parts.append(f"System: {content}")
                elif role == "user":
                    prompt_parts.append(f"User: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")
            
            # Add final Assistant prompt
            prompt_parts.append("Assistant:")
            full_prompt = "\n\n".join(prompt_parts)
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "stop": ["User:", "System:"]
                }
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        processing_time_ms = int((time.time() - start_time) * 1000)
                        response_text = result.get("response", "").strip()
                        
                        # Format in OpenAI-compatible structure
                        return {
                            "choices": [{
                                "message": {
                                    "content": response_text,
                                    "role": "assistant"
                                },
                                "finish_reason": "stop"
                            }],
                            "usage": {
                                "prompt_tokens": result.get("prompt_eval_count", 0),
                                "completion_tokens": result.get("eval_count", 0),
                                "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                            },
                            "model": model,
                            "processing_time_ms": processing_time_ms
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama chat failed: HTTP {response.status} - {error_text}")
                        raise Exception(f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"Ollama chat completion failed: {str(e)}")
            raise Exception(f"Local LLM error: {str(e)}")
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull/download a model if not available locally"""
        try:
            payload = {"name": model_name}
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1800)) as session:  # 30 min for model download
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        logger.info(f"Successfully pulled model: {model_name}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to pull model {model_name}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Model pull failed: {str(e)}")
            return False

# Factory function for easy instantiation
def create_ollama_service(base_url: str = "http://localhost:11434") -> OllamaService:
    """Create and return OllamaService instance"""
    return OllamaService(base_url)

# Default instance
ollama_service = create_ollama_service()


class OllamaLLMAdapter:
    """Adapter to make OllamaService compatible with OpenAI-style interfaces"""
    
    def __init__(self, ollama_service: OllamaService, default_model: str = "qwen2.5:7b"):
        self.ollama = ollama_service
        self.default_model = default_model
    
    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        **kwargs
    ) -> Any:
        """OpenAI-compatible chat completion"""
        
        class MockUsage:
            def __init__(self, usage_data):
                self.prompt_tokens = usage_data.get("prompt_tokens", 0)
                self.completion_tokens = usage_data.get("completion_tokens", 0)
                self.total_tokens = usage_data.get("total_tokens", 0)
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
        
        class MockChoice:
            def __init__(self, message_content):
                self.message = MockMessage(message_content)
        
        class MockResponse:
            def __init__(self, ollama_response):
                self.choices = [MockChoice(ollama_response["choices"][0]["message"]["content"])]
                self.usage = MockUsage(ollama_response["usage"])
        
        # Use Ollama for completion
        response = await self.ollama.chat_completion(
            messages=messages,
            model=model or self.default_model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return MockResponse(response)