"""
Reranker Factory
Creates reranker instances based on configuration with fallback mechanisms
"""

import asyncio
from typing import Dict, Any, Optional, List
import logging
from enum import Enum

from .base_reranker import BaseReranker
from .local_reranker import LocalReranker
from .cohere_reranker import CohereReranker

logger = logging.getLogger(__name__)


class RerankerProvider(Enum):
    """Supported reranker providers"""
    LOCAL = "local"
    COHERE = "cohere"
    NONE = "none"


class RerankerFactory:
    """
    Factory for creating and managing reranker instances
    
    Supports multiple providers with fallback mechanisms and health monitoring.
    Designed to be configuration-driven and easily extensible.
    """
    
    # Registry of available reranker classes
    _PROVIDER_REGISTRY = {
        RerankerProvider.LOCAL: LocalReranker,
        RerankerProvider.COHERE: CohereReranker,
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize RerankerFactory
        
        Args:
            config: Factory configuration including provider settings
        """
        self.config = config or {}
        self._instances: Dict[str, BaseReranker] = {}
        self._initialization_lock = asyncio.Lock()
        
        # Factory configuration
        self.primary_provider = self._parse_provider(
            self.config.get('primary_provider', 'local')
        )
        self.fallback_providers = self._parse_providers(
            self.config.get('fallback_providers', ['cohere'])
        )
        self.auto_fallback = self.config.get('auto_fallback', True)
        self.health_check_enabled = self.config.get('health_check_enabled', True)
        
        logger.info(
            f"RerankerFactory initialized - Primary: {self.primary_provider.value}, "
            f"Fallbacks: {[p.value for p in self.fallback_providers]}"
        )
    
    def _parse_provider(self, provider_str: str) -> RerankerProvider:
        """Parse provider string to enum"""
        try:
            return RerankerProvider(provider_str.lower())
        except ValueError:
            logger.warning(f"Unknown provider '{provider_str}', defaulting to LOCAL")
            return RerankerProvider.LOCAL
    
    def _parse_providers(self, providers_list: List[str]) -> List[RerankerProvider]:
        """Parse list of provider strings to enums"""
        providers = []
        for provider_str in providers_list:
            try:
                provider = RerankerProvider(provider_str.lower())
                providers.append(provider)
            except ValueError:
                logger.warning(f"Unknown fallback provider '{provider_str}', skipping")
        return providers
    
    async def create_reranker(
        self, 
        provider: Optional[RerankerProvider] = None,
        config_override: Optional[Dict[str, Any]] = None
    ) -> BaseReranker:
        """
        Create a reranker instance for the specified provider
        
        Args:
            provider: Specific provider to create (None for primary)
            config_override: Override configuration for this instance
            
        Returns:
            Initialized BaseReranker instance
        """
        if provider is None:
            provider = self.primary_provider
        
        if provider == RerankerProvider.NONE:
            raise ValueError("Cannot create reranker for NONE provider")
        
        # Check if we have a cached instance
        instance_key = f"{provider.value}_{hash(str(config_override))}"
        
        async with self._initialization_lock:
            if instance_key in self._instances:
                return self._instances[instance_key]
            
            # Get provider configuration
            provider_config = self._get_provider_config(provider, config_override)
            
            # Create instance
            if provider not in self._PROVIDER_REGISTRY:
                raise ValueError(f"Unsupported reranker provider: {provider}")
            
            reranker_class = self._PROVIDER_REGISTRY[provider]
            reranker = reranker_class(provider_config)
            
            # Initialize the reranker
            try:
                await reranker.initialize()
                logger.info(f"Successfully created {provider.value} reranker")
                
                # Cache successful instance
                self._instances[instance_key] = reranker
                return reranker
                
            except Exception as e:
                logger.error(f"Failed to initialize {provider.value} reranker: {str(e)}")
                raise
    
    def _get_provider_config(
        self, 
        provider: RerankerProvider,
        config_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get configuration for specific provider"""
        # Start with factory config
        base_config = self.config.copy()
        
        # Add provider-specific config
        provider_configs = self.config.get('providers', {})
        if provider.value in provider_configs:
            provider_config = provider_configs[provider.value].copy()
            base_config.update(provider_config)
        
        # Apply overrides
        if config_override:
            base_config.update(config_override)
        
        return base_config
    
    async def get_best_reranker(
        self, 
        config_override: Optional[Dict[str, Any]] = None
    ) -> BaseReranker:
        """
        Get the best available reranker with automatic fallback
        
        Args:
            config_override: Override configuration
            
        Returns:
            Best available BaseReranker instance
        """
        providers_to_try = [self.primary_provider] + self.fallback_providers
        
        for provider in providers_to_try:
            if provider == RerankerProvider.NONE:
                continue
                
            try:
                reranker = await self.create_reranker(provider, config_override)
                
                # Health check if enabled
                if self.health_check_enabled:
                    health = await reranker.health_check()
                    if health.get("status") == "healthy":
                        logger.debug(f"Using {provider.value} reranker (healthy)")
                        return reranker
                    else:
                        logger.warning(f"{provider.value} reranker unhealthy: {health}")
                        continue
                else:
                    # Skip health check, assume it's good if it initialized
                    logger.debug(f"Using {provider.value} reranker (no health check)")
                    return reranker
                    
            except Exception as e:
                logger.warning(f"Failed to get {provider.value} reranker: {str(e)}")
                continue
        
        # No providers available
        raise RuntimeError(
            "No reranker providers are available. "
            f"Tried: {[p.value for p in providers_to_try]}"
        )
    
    async def get_all_available_rerankers(self) -> Dict[str, BaseReranker]:
        """
        Get all available reranker instances
        
        Returns:
            Dict mapping provider names to reranker instances
        """
        available = {}
        
        for provider in RerankerProvider:
            if provider == RerankerProvider.NONE:
                continue
                
            try:
                reranker = await self.create_reranker(provider)
                if self.health_check_enabled:
                    health = await reranker.health_check()
                    if health.get("status") == "healthy":
                        available[provider.value] = reranker
                else:
                    available[provider.value] = reranker
                    
            except Exception as e:
                logger.debug(f"Provider {provider.value} not available: {str(e)}")
        
        return available
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health check on all configured providers
        
        Returns:
            Dict mapping provider names to health check results
        """
        health_results = {}
        
        for provider in RerankerProvider:
            if provider == RerankerProvider.NONE:
                continue
                
            try:
                reranker = await self.create_reranker(provider)
                health = await reranker.health_check()
                health_results[provider.value] = health
                
            except Exception as e:
                health_results[provider.value] = {
                    "status": "error",
                    "error": str(e),
                    "provider": provider.value
                }
        
        return health_results
    
    def get_factory_info(self) -> Dict[str, Any]:
        """Get information about the factory configuration"""
        return {
            "primary_provider": self.primary_provider.value,
            "fallback_providers": [p.value for p in self.fallback_providers],
            "auto_fallback": self.auto_fallback,
            "health_check_enabled": self.health_check_enabled,
            "supported_providers": [p.value for p in RerankerProvider if p != RerankerProvider.NONE],
            "cached_instances": list(self._instances.keys()),
            "config": {
                k: "***" if "key" in k.lower() or "token" in k.lower() else v
                for k, v in self.config.items()
            }
        }
    
    async def cleanup_all(self) -> None:
        """Clean up all cached reranker instances"""
        cleanup_tasks = []
        
        for instance_key, reranker in self._instances.items():
            cleanup_tasks.append(self._cleanup_instance(instance_key, reranker))
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self._instances.clear()
        logger.info("All reranker instances cleaned up")
    
    async def _cleanup_instance(self, instance_key: str, reranker: BaseReranker) -> None:
        """Clean up a single reranker instance"""
        try:
            await reranker.cleanup()
            logger.debug(f"Cleaned up reranker instance: {instance_key}")
        except Exception as e:
            logger.warning(f"Error cleaning up {instance_key}: {str(e)}")
    
    @classmethod
    def from_config_dict(cls, config: Dict[str, Any]) -> 'RerankerFactory':
        """
        Create RerankerFactory from configuration dictionary
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured RerankerFactory instance
        """
        return cls(config)
    
    @classmethod
    def create_default(cls) -> 'RerankerFactory':
        """
        Create RerankerFactory with sensible defaults
        
        Returns:
            RerankerFactory with default configuration
        """
        default_config = {
            "primary_provider": "local",
            "fallback_providers": ["cohere"],
            "auto_fallback": True,
            "health_check_enabled": True,
            "providers": {
                "local": {
                    "model": "cross-encoder/ms-marco-MiniLM-L-12-v2",
                    "device": "auto",
                    "top_k": 5
                },
                "cohere": {
                    "model": "rerank-english-v2.0",
                    "top_k": 5
                }
            }
        }
        
        return cls(default_config)