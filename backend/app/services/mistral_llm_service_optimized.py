"""
Optimized Mistral LLM Service - Performance-First Design
Target: 15s → <3s Response Time durch Connection Pooling + Caching
"""
import logging
import re
import asyncio
import time
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.prompts.manager import prompt_manager
from app.services.ollama_connection_pool import ollama_pool
from app.services.response_cache import response_cache

logger = logging.getLogger(__name__)

class OptimizedMistralLLMService:
    """
    Performance-optimized Mistral 7B Service
    
    Key Optimizations:
    - Connection pooling for Ollama (eliminates connection overhead)
    - Intelligent response caching (cache hits → <1s response)
    - Fast mode for time-critical responses
    - Async-first design throughout
    """
    
    def __init__(self):
        self.model_name = settings.OLLAMA_MODEL
        self.is_initialized = False
        
        # Performance tracking
        self.request_count = 0
        self.cache_hits = 0
        self.total_response_time = 0.0
        
        # German language optimizations
        self.german_replacements = {
            "Stream": "Stream",
            "Batch Job": "Batch-Job", 
            "Configuration": "Konfiguration",
            "Validation": "Validierung",
            "Automation": "Automatisierung",
            "Processing": "Verarbeitung",
            "Workflow": "Arbeitsablauf",
            "Error": "Fehler",
            "File": "Datei",
            "Data": "Daten"
        }
        
        logger.info("🚀 Optimized Mistral LLM Service initialized")
    
    async def initialize(self):
        """Initialize service with connection pool"""
        try:
            logger.info("🔥 Initializing Optimized Mistral Service...")
            
            # Initialize connection pool
            await ollama_pool.initialize()
            
            # Quick health check
            health_check = await ollama_pool.health_check()
            
            if health_check.get("healthy", False):
                self.is_initialized = True
                logger.info("✅ Optimized Mistral Service ready")
            else:
                logger.warning("⚠️ Health check failed, but continuing...")
                self.is_initialized = True
                
        except Exception as e:
            logger.error(f"❌ Optimized Mistral initialization failed: {e}")
            self.is_initialized = True  # Fallback: continue anyway
    
    async def generate_german_response(self, 
                                     user_message: str, 
                                     context: str = "",
                                     fast_mode: bool = True,
                                     use_cache: bool = True) -> str:
        """
        Generate optimized German response
        
        Args:
            user_message: User's question
            context: RAG context
            fast_mode: Use fast generation parameters
            use_cache: Enable response caching
            
        Returns:
            German response text
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Step 1: Check cache first
            if use_cache:
                cached_result = await response_cache.get(user_message, context)
                if cached_result:
                    response, cache_entry = cached_result
                    self.cache_hits += 1
                    
                    cache_time = time.time() - start_time
                    logger.info(f"🎯 Cache HIT: {cache_time:.3f}s (saved ~{cache_entry.response_time:.1f}s)")
                    
                    return response
            
            # Step 2: Generate new response
            logger.debug(f"🔄 Generating new response (fast_mode: {fast_mode})")
            
            # Build optimized prompt
            prompt = prompt_manager.build_prompt(
                template_type="mistral_system_prompt",
                context={
                    "context": context,
                    "user_message": user_message
                }
            )
            
            # Choose generation options based on mode
            if fast_mode:
                options = {
                    "temperature": 0.3,       # Lower temp = faster
                    "top_p": 0.8,            # More focused
                    "top_k": 20,             # Fewer options
                    "repeat_penalty": 1.1,
                    "num_predict": 512,      # Shorter responses
                    "num_ctx": 2048,         # Reduced context
                    "num_thread": settings.MODEL_THREADS
                }
                timeout = 15.0
            else:
                options = {
                    "temperature": settings.MODEL_TEMPERATURE,
                    "top_p": settings.MODEL_TOP_P,
                    "top_k": settings.MODEL_TOP_K,
                    "repeat_penalty": settings.MODEL_REPEAT_PENALTY,
                    "num_predict": settings.MODEL_MAX_TOKENS,
                    "num_thread": settings.MODEL_THREADS
                }
                timeout = 30.0
            
            # Step 3: Generate using connection pool
            raw_response = await ollama_pool.generate(
                prompt=prompt,
                model=self.model_name,
                options=options,
                timeout=timeout
            )
            
            # Step 4: Post-process for German
            if fast_mode:
                final_response = self._quick_german_processing(raw_response)
            else:
                final_response = self.post_process_german(raw_response)
            
            # Step 5: Cache the result
            generation_time = time.time() - start_time
            if use_cache and final_response:
                await response_cache.set(
                    query=user_message,
                    response=final_response,
                    context=context,
                    response_time=generation_time,
                    metadata={
                        "fast_mode": fast_mode,
                        "model": self.model_name,
                        "options": options
                    }
                )
            
            # Update performance stats
            self.total_response_time += generation_time
            
            logger.info(f"🤖 Generated response: {generation_time:.3f}s (fast_mode: {fast_mode})")
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Optimized generation error: {e}")
            return self._get_fallback_response(str(e))
    
    def _quick_german_processing(self, response: str) -> str:
        """Fast German post-processing for performance"""
        if not response:
            return "Entschuldigung, ich konnte keine Antwort generieren."
        
        # Essential German corrections only
        essential_fixes = [
            (" du ", " Sie "),
            (" dich ", " Sie "),
            (" dein ", " Ihr "),
            (" deine ", " Ihre "),
            (" dir ", " Ihnen "),
            ("Stream", "Stream"),  # Keep technical terms
            ("Batch Job", "Batch-Job"),
            ("Config", "Konfiguration")
        ]
        
        for old, new in essential_fixes:
            response = response.replace(old, new)
        
        return response.strip()
    
    def post_process_german(self, response: str) -> str:
        """Comprehensive German processing (for non-fast mode)"""
        if not response:
            return "Entschuldigung, ich konnte keine Antwort generieren."
        
        # Apply German replacements
        for eng, ger in self.german_replacements.items():
            response = response.replace(eng, ger)
        
        # Formal address patterns
        formal_patterns = [
            (r'\b[Dd]u\b', 'Sie'),
            (r'\b[Dd]ich\b', 'Sie'), 
            (r'\b[Dd]ein\b', 'Ihr'),
            (r'\b[Dd]eine\b', 'Ihre'),
            (r'\b[Dd]ir\b', 'Ihnen')
        ]
        
        for pattern, replacement in formal_patterns:
            response = re.sub(pattern, replacement, response)
        
        # Enhance markdown formatting
        response = self._enhance_markdown_formatting(response)
        
        return response.strip()
    
    def _enhance_markdown_formatting(self, text: str) -> str:
        """Enhance markdown formatting for better readability"""
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Convert bold text to proper headers
            if line.startswith('**') and line.endswith('**') and len(line) > 4:
                header_text = line.replace('**', '').strip()
                line = f"### {header_text}"
            
            # Ensure proper header hierarchy
            elif line.startswith('#'):
                if not line.startswith('##'):
                    line = f"## {line.lstrip('#').strip()}"
            
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _get_fallback_response(self, error_msg: str) -> str:
        """Generate fallback response for errors"""
        if "timeout" in error_msg.lower():
            return "Die Anfrage hat zu lange gedauert. Bitte versuchen Sie es mit einer kürzeren Frage erneut."
        elif "connection" in error_msg.lower():
            return "Verbindungsfehler zum KI-System. Bitte prüfen Sie, ob Ollama läuft."
        else:
            return "Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut."
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            # Test connection pool
            pool_health = await ollama_pool.health_check()
            
            # Test cache
            cache_stats = await response_cache.get_stats()
            
            # Quick generation test
            start_time = time.time()
            test_response = await self.generate_german_response(
                user_message="Test",
                context="",
                fast_mode=True,
                use_cache=False
            )
            test_time = time.time() - start_time
            
            return {
                "service": "optimized_mistral",
                "healthy": True,
                "connection_pool": pool_health,
                "cache_stats": cache_stats,
                "test_response_time": test_time,
                "performance": {
                    "total_requests": self.request_count,
                    "cache_hits": self.cache_hits,
                    "cache_hit_rate": (self.cache_hits / self.request_count * 100) if self.request_count > 0 else 0,
                    "avg_response_time": (self.total_response_time / self.request_count) if self.request_count > 0 else 0
                }
            }
            
        except Exception as e:
            return {
                "service": "optimized_mistral",
                "healthy": False,
                "error": str(e)
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get detailed service statistics"""
        pool_stats = await ollama_pool.get_stats()
        cache_stats = await response_cache.get_stats()
        
        return {
            "service": "optimized_mistral",
            "model_name": self.model_name,
            "is_initialized": self.is_initialized,
            "performance": {
                "total_requests": self.request_count,
                "cache_hits": self.cache_hits,
                "cache_hit_rate": (self.cache_hits / self.request_count * 100) if self.request_count > 0 else 0,
                "avg_response_time": (self.total_response_time / self.request_count) if self.request_count > 0 else 0
            },
            "connection_pool": pool_stats,
            "response_cache": cache_stats,
            "optimizations": {
                "connection_pooling": True,
                "response_caching": True,
                "fast_mode_default": True,
                "german_optimization": True
            }
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        await ollama_pool.cleanup()
        await response_cache.clear()
        response_cache.cleanup_task_shutdown()
        logger.info("🧹 Optimized Mistral Service cleanup complete")

# Global optimized service instance
optimized_mistral_service = OptimizedMistralLLMService()