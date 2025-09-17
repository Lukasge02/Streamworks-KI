"""
Central LLM Factory - Single Point of Provider Control
Provides unified access to different LLM providers based on configuration
"""

import logging
from typing import Optional, Union, Any
from abc import ABC, abstractmethod

from config import settings
from .openai_llm_service import OpenAILLMService, OpenAILLMAdapter
from .ollama_service import OllamaService, OllamaLLMAdapter

logger = logging.getLogger(__name__)

class LLMServiceInterface(ABC):
    """Abstract interface for LLM services"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text completion"""
        pass

    @abstractmethod
    async def chat_completion(self, messages: list, **kwargs) -> dict:
        """Generate chat completion"""
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        """Check service health"""
        pass

class LLMFactory:
    """Factory for creating LLM service instances"""

    _instance = None
    _openai_service = None
    _ollama_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def get_llm_service(cls, provider: Optional[str] = None) -> Union[OpenAILLMService, OllamaService]:
        """
        Get LLM service instance based on configuration

        Args:
            provider: Optional provider override ("openai" or "ollama")

        Returns:
            LLM service instance
        """
        # Use provided provider or fall back to config
        active_provider = provider or settings.LLM_PROVIDER

        logger.info(f"🤖 Initializing LLM service with provider: {active_provider}")

        if active_provider == "openai":
            return await cls._get_openai_service()
        elif active_provider == "ollama":
            return await cls._get_ollama_service()
        else:
            logger.warning(f"Unknown LLM provider '{active_provider}', falling back to OpenAI")
            return await cls._get_openai_service()

    @classmethod
    async def _get_openai_service(cls) -> OpenAILLMService:
        """Get or create OpenAI service instance"""
        if cls._openai_service is None:
            try:
                cls._openai_service = OpenAILLMService()

                # Verify service is working
                health = await cls._openai_service.health_check()
                if health.get("status") != "healthy":
                    logger.error(f"OpenAI service unhealthy: {health}")
                    raise Exception(f"OpenAI service failed health check: {health.get('error', 'Unknown error')}")

                logger.info("✅ OpenAI LLM service initialized successfully")

            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI service: {str(e)}")
                raise

        return cls._openai_service

    @classmethod
    async def _get_ollama_service(cls) -> OllamaService:
        """Get or create Ollama service instance"""
        if cls._ollama_service is None:
            try:
                cls._ollama_service = OllamaService()

                # Verify service is working
                health = await cls._ollama_service.health_check()
                if health.get("status") != "healthy":
                    logger.error(f"Ollama service unhealthy: {health}")
                    raise Exception(f"Ollama service failed health check: {health.get('error', 'Unknown error')}")

                logger.info("✅ Ollama LLM service initialized successfully")

            except Exception as e:
                logger.error(f"❌ Failed to initialize Ollama service: {str(e)}")
                raise

        return cls._ollama_service

    @classmethod
    async def get_adapter(cls, provider: Optional[str] = None) -> Union[OpenAILLMAdapter, OllamaLLMAdapter]:
        """
        Get LLM adapter for compatibility with existing interfaces

        Args:
            provider: Optional provider override

        Returns:
            LLM adapter instance
        """
        service = await cls.get_llm_service(provider)

        if isinstance(service, OpenAILLMService):
            return OpenAILLMAdapter(service)
        elif isinstance(service, OllamaService):
            return OllamaLLMAdapter(service)
        else:
            raise ValueError(f"Unknown service type: {type(service)}")

    @classmethod
    async def switch_provider(cls, new_provider: str) -> bool:
        """
        Switch to a different LLM provider

        Args:
            new_provider: New provider ("openai" or "ollama")

        Returns:
            Success status
        """
        logger.info(f"🔄 Switching LLM provider from {settings.LLM_PROVIDER} to {new_provider}")

        try:
            # Test the new provider
            test_service = await cls.get_llm_service(new_provider)
            health = await test_service.health_check()

            if health.get("status") != "healthy":
                logger.error(f"Cannot switch to {new_provider}: {health}")
                return False

            # Update settings (note: this doesn't persist to .env)
            settings.LLM_PROVIDER = new_provider

            logger.info(f"✅ Successfully switched to {new_provider}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to switch to {new_provider}: {str(e)}")
            return False

    @classmethod
    async def get_current_provider_info(cls) -> dict:
        """Get information about the current provider"""
        try:
            service = await cls.get_llm_service()
            health = await service.health_check()

            return {
                "provider": settings.LLM_PROVIDER,
                "health": health,
                "service_type": type(service).__name__
            }
        except Exception as e:
            return {
                "provider": settings.LLM_PROVIDER,
                "error": str(e),
                "health": {"status": "unhealthy"}
            }

# Convenience functions for easy access
async def get_llm_service(provider: Optional[str] = None) -> Union[OpenAILLMService, OllamaService]:
    """
    Get LLM service instance - Main entry point

    Args:
        provider: Optional provider override

    Returns:
        LLM service instance
    """
    return await LLMFactory.get_llm_service(provider)

async def get_llm_adapter(provider: Optional[str] = None) -> Union[OpenAILLMAdapter, OllamaLLMAdapter]:
    """
    Get LLM adapter for compatibility

    Args:
        provider: Optional provider override

    Returns:
        LLM adapter instance
    """
    return await LLMFactory.get_adapter(provider)

# Health check utilities
async def check_all_providers() -> dict:
    """Check health of all available providers"""
    results = {}

    # Check OpenAI
    try:
        openai_service = await LLMFactory._get_openai_service()
        results["openai"] = await openai_service.health_check()
    except Exception as e:
        results["openai"] = {"status": "unhealthy", "error": str(e)}

    # Check Ollama
    try:
        ollama_service = await LLMFactory._get_ollama_service()
        results["ollama"] = await ollama_service.health_check()
    except Exception as e:
        results["ollama"] = {"status": "unhealthy", "error": str(e)}

    return results

async def get_provider_status() -> dict:
    """Get status of current provider and configuration"""
    return {
        "current_provider": settings.LLM_PROVIDER,
        "current_info": await LLMFactory.get_current_provider_info(),
        "all_providers": await check_all_providers()
    }