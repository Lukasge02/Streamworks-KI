"""
OpenAI LLM Service for high-quality response generation
Provides OpenAI API integration with streaming support and JSON mode
"""

import asyncio
import json
import time
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
from datetime import datetime

import openai
from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)

class OpenAILLMService:
    """Service for interacting with OpenAI models"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        self.streaming = settings.OPENAI_STREAMING

    async def health_check(self) -> Dict[str, Any]:
        """Check if OpenAI API is accessible"""
        try:
            # Simple test request to verify API key and connectivity
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )

            return {
                "status": "healthy",
                "model": self.model,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI model"""
        start_time = time.time()

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            kwargs = {
                "model": model or self.model,
                "messages": messages,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature if temperature is not None else self.temperature,
                "stream": False
            }

            # Enable JSON mode if requested
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = await self.client.chat.completions.create(**kwargs)

            processing_time_ms = int((time.time() - start_time) * 1000)

            return {
                "response": response.choices[0].message.content,
                "model": response.model,
                "processing_time_ms": processing_time_ms,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason
            }

        except Exception as e:
            logger.error(f"OpenAI completion failed: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Simple generate method that returns only the response text
        Compatible with DocumentSummarizer and other services
        """
        try:
            result = await self.generate_completion(
                prompt=prompt,
                model=model,
                temperature=temperature
            )
            return result.get("response", "")
        except Exception as e:
            logger.error(f"OpenAI generate failed: {str(e)}")
            return ""

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        json_mode: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """Chat completion with optional streaming"""
        start_time = time.time()

        try:
            kwargs = {
                "model": model or self.model,
                "messages": messages,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature if temperature is not None else self.temperature,
                "stream": stream
            }

            # Enable JSON mode if requested
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            if stream:
                # Return async generator for streaming
                return self._stream_chat_completion(**kwargs, start_time=start_time)
            else:
                # Standard non-streaming response
                response = await self.client.chat.completions.create(**kwargs)

                processing_time_ms = int((time.time() - start_time) * 1000)

                # Format in compatible structure
                return {
                    "choices": [{
                        "message": {
                            "content": response.choices[0].message.content,
                            "role": "assistant"
                        },
                        "finish_reason": response.choices[0].finish_reason
                    }],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "model": response.model,
                    "processing_time_ms": processing_time_ms
                }

        except Exception as e:
            logger.error(f"OpenAI chat completion failed: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _stream_chat_completion(self, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle streaming chat completion"""
        start_time = kwargs.pop('start_time')

        try:
            stream = await self.client.chat.completions.create(**kwargs)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield {
                        "choices": [{
                            "delta": {
                                "content": chunk.choices[0].delta.content,
                                "role": "assistant"
                            },
                            "finish_reason": chunk.choices[0].finish_reason
                        }],
                        "model": chunk.model,
                        "object": "chat.completion.chunk"
                    }

                # Send final message with usage info
                if chunk.choices and chunk.choices[0].finish_reason:
                    processing_time_ms = int((time.time() - start_time) * 1000)
                    yield {
                        "choices": [{
                            "delta": {},
                            "finish_reason": chunk.choices[0].finish_reason
                        }],
                        "model": chunk.model,
                        "processing_time_ms": processing_time_ms,
                        "done": True
                    }

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {str(e)}")
            yield {
                "error": f"OpenAI streaming error: {str(e)}",
                "done": True
            }

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON response"""
        try:
            result = await self.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                json_mode=True
            )

            # Parse JSON response
            response_text = result.get("response", "{}")
            try:
                json_data = json.loads(response_text)
                return {
                    "json": json_data,
                    "raw_response": response_text,
                    "processing_time_ms": result.get("processing_time_ms", 0),
                    "usage": {
                        "prompt_tokens": result.get("prompt_tokens", 0),
                        "completion_tokens": result.get("completion_tokens", 0),
                        "total_tokens": result.get("total_tokens", 0)
                    }
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return {
                    "json": {},
                    "raw_response": response_text,
                    "error": f"JSON parse error: {str(e)}"
                }

        except Exception as e:
            logger.error(f"OpenAI JSON generation failed: {str(e)}")
            return {
                "json": {},
                "error": str(e)
            }


class OpenAILLMAdapter:
    """Adapter to make OpenAILLMService compatible with existing interfaces"""

    def __init__(self, openai_service: OpenAILLMService):
        self.openai = openai_service

    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """OpenAI-compatible chat completion interface"""

        if stream:
            # Return async generator for streaming
            return await self.openai.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
        else:
            # Mock response object for compatibility
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
                def __init__(self, openai_response):
                    self.choices = [MockChoice(openai_response["choices"][0]["message"]["content"])]
                    self.usage = MockUsage(openai_response["usage"])

            response = await self.openai.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            return MockResponse(response)


# Factory function for easy instantiation
def create_openai_service() -> OpenAILLMService:
    """Create and return OpenAILLMService instance"""
    return OpenAILLMService()

# Default instance
openai_service = create_openai_service()