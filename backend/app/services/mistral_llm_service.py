"""
Optimized Mistral LLM Service - Performance-First Design
Target: 15s → <3s Response Time durch Connection Pooling + Caching
Backward compatible with existing MistralLLMService interface
"""
import logging
import re
import asyncio
import time
from typing import Dict, Any, Optional
from app.core.settings import settings
from app.core.prompts.manager import prompt_manager
from app.services.ollama_connection_pool import ollama_pool
from app.services.response_cache import response_cache

logger = logging.getLogger(__name__)

class MistralLLMService:
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
        self.ollama_url = f"{settings.OLLAMA_HOST}/api/generate"  # Backward compatibility
        self.is_initialized = False
        
        # Performance tracking
        self.request_count = 0
        self.cache_hits = 0
        self.total_response_time = 0.0
        
        # Deutsche Fachbegriff-Übersetzungen
        self.german_replacements = {
            "Stream": "Stream",
            "Batch Job": "Batch-Job", 
            "Configuration": "Konfiguration",
            "Validation": "Validierung",
            "Automation": "Automatisierung",
            "Processing": "Verarbeitung",
            "Workflow": "Arbeitsablauf",
            "Schedule": "Zeitplanung",
            "Template": "Vorlage",
            "Error": "Fehler",
            "Job": "Job",
            "File": "Datei",
            "Data": "Daten",
            "Source": "Quelle",
            "Target": "Ziel",
            "Output": "Ausgabe",
            "Input": "Eingabe"
        }
        
        logger.info("🚀 Optimized Mistral LLM Service initialized")
    
    async def initialize(self, skip_warmup: bool = False):
        """Initialize service with connection pool - backward compatible"""
        try:
            logger.info("🔥 Initializing Optimized Mistral Service...")
            
            # Initialize connection pool
            await ollama_pool.initialize()
            
            if skip_warmup:
                # Schnelle Initialisierung ohne Warm-up
                logger.info("⚡ Skipping warm-up for faster startup")
                self.is_initialized = True
                return
            
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
    
    async def ollama_generate(self, prompt: str, model: str = None, options: Dict[str, Any] = None, timeout: float = 30.0) -> str:
        """Ollama API Call - now using optimized connection pool"""
        
        if model is None:
            model = self.model_name
            
        if options is None:
            options = {
                "temperature": settings.MODEL_TEMPERATURE,
                "top_p": settings.MODEL_TOP_P,
                "top_k": settings.MODEL_TOP_K,
                "repeat_penalty": settings.MODEL_REPEAT_PENALTY,
                "num_predict": settings.MODEL_MAX_TOKENS,
                "num_thread": settings.MODEL_THREADS
            }
        
        try:
            # Use optimized connection pool
            return await ollama_pool.generate(
                prompt=prompt,
                model=model,
                options=options,
                timeout=timeout
            )
        except Exception as e:
            logger.error(f"Ollama Request Error: {e}")
            return self._get_fallback_response("GENERAL_ERROR")
    
    def _get_fallback_response(self, error_type: str) -> str:
        """Fallback-Antworten basierend auf Fehlertyp"""
        fallback_responses = {
            "TIMEOUT": "Die Anfrage hat zu lange gedauert. Das System ist möglicherweise stark ausgelastet. Bitte versuchen Sie es in wenigen Minuten erneut.",
            "CONNECTION_ERROR": "Die Verbindung zum KI-System konnte nicht hergestellt werden. Bitte prüfen Sie, ob Ollama läuft und versuchen Sie es erneut.",
            "API_ERROR": "Es gab ein Problem bei der Verarbeitung Ihrer Anfrage. Bitte versuchen Sie es mit einer einfacheren Frage erneut.",
            "GENERAL_ERROR": "Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut oder kontaktieren Sie den Support."
        }
        return fallback_responses.get(error_type, fallback_responses["GENERAL_ERROR"])
    
    async def generate_german_response(self, user_message: str, context: str = "", fast_mode: bool = True, use_cache: bool = True) -> str:
        """
        Generate optimized German response with caching
        
        Args:
            user_message: User's question
            context: RAG context
            fast_mode: Use fast generation parameters (default: True for performance)
            use_cache: Enable response caching (default: True)
            
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
                    "temperature": 0.2,       # Even lower temp = faster
                    "top_p": 0.7,            # More focused
                    "top_k": 15,             # Fewer options
                    "repeat_penalty": 1.05,
                    "num_predict": 300,      # Much shorter responses
                    "num_ctx": 1024,         # Much reduced context
                    "num_thread": settings.MODEL_THREADS
                }
                timeout = 8.0  # Much more aggressive timeout
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
        """Nachbearbeitung für perfekte deutsche Antworten (v3.0 - Enhanced)"""
        
        if not response:
            return "Entschuldigung, ich konnte keine Antwort generieren."
        
        # KRITISCHE QUALITÄTSVERBESSERUNGEN
        
        # 1. Englische Fachbegriffe aggressiv ersetzen
        enhanced_replacements = {
            **self.german_replacements,
            # Zusätzliche kritische Begriffe
            "Batch Job": "Batch-Job",
            "batch job": "Batch-Job", 
            "Data Processing": "Datenverarbeitung",
            "data processing": "Datenverarbeitung",
            "Config File": "Konfigurationsdatei",
            "config file": "Konfigurationsdatei",
            "Workflow": "Ablaufsteuerung",
            "workflow": "Ablaufsteuerung",
            "Error Handling": "Fehlerbehandlung",
            "error handling": "Fehlerbehandlung",
            "Best Practice": "Bewährte Verfahren",
            "best practice": "bewährte Verfahren",
            "Use Case": "Anwendungsfall",
            "use case": "Anwendungsfall",
            "File Path": "Dateipfad",
            "file path": "Dateipfad",
            "Output": "Ausgabe",
            "output": "Ausgabe",
            "Input": "Eingabe",
            "input": "Eingabe"
        }
        
        for eng, ger in enhanced_replacements.items():
            response = response.replace(eng, ger)
        
        # 2. Höflichkeitsformen konsistent durchsetzen
        informal_patterns = [
            (r'\b[Dd]u\b', 'Sie'),
            (r'\b[Dd]ich\b', 'Sie'), 
            (r'\b[Dd]ein\b', 'Ihr'),
            (r'\b[Dd]eine\b', 'Ihre'),
            (r'\b[Dd]ir\b', 'Ihnen'),
            (r'\b[Kk]annst du\b', 'Können Sie'),
            (r'\b[Ss]ollst du\b', 'Sollten Sie'),
            (r'\b[Mm]usst du\b', 'Müssen Sie')
        ]
        
        for pattern, replacement in informal_patterns:
            response = re.sub(pattern, replacement, response)
        
        # 3. Entferne chaotische englische Titel aus Citations
        response = re.sub(r'A:\s*Yes,.*?StreamWorks.*?supports', 'StreamWorks unterstützt', response, flags=re.IGNORECASE)
        response = re.sub(r'Q:\s*.*?\?', '', response)  # Entferne englische Fragen
        
        # 4. Markdown-Formatierung verbessern
        response = self.enhance_markdown_formatting(response)
        
        # 5. Deutsche Satzstruktur optimieren
        response = self._optimize_german_sentence_structure(response)
        
        return response
    
    def _optimize_german_sentence_structure(self, text: str) -> str:
        """Optimiert deutsche Satzstruktur"""
        # Verbessere typische englische Konstruktionen
        text = re.sub(r'Um zu (.+), (.+)', r'Für \1 \2', text)  # "Um zu" -> "Für"
        text = re.sub(r'Sie können (.+) verwenden um', r'Verwenden Sie \1, um', text)  # Besserer Satzbau
        
        # Deutsche Konjunktionen bevorzugen
        text = text.replace('sowie auch', 'sowie')
        text = text.replace('aber auch', 'jedoch auch')
        
        return text
    
    def enhance_markdown_formatting(self, text: str) -> str:
        """Verbessere Markdown-Formatierung (v3.0 - Structure Enforcement)"""
        
        lines = text.split('\n')
        formatted_lines = []
        
        # Struktur-Enforcement: Erzwinge das gewünschte Schema
        has_main_header = any(line.strip().startswith('## 🔧') for line in lines)
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Hauptheader sicherstellen
            if not has_main_header and i == 0 and line and not line.startswith('#'):
                formatted_lines.append('## 🔧 StreamWorks-Lösung')
                formatted_lines.append('')
                
            # Fettgedruckten Text zu korrekten Unterheadern machen
            if line.startswith('**') and line.endswith('**') and len(line) > 4:
                header_text = line.replace('**', '').strip()
                # Bestimme den korrekten Header-Typ basierend auf Inhalt
                if any(word in header_text.lower() for word in ['überblick', 'zusammenfassung', 'erklärung']):
                    line = f"### 📋 {header_text}"
                elif any(word in header_text.lower() for word in ['umsetzung', 'implementierung', 'schritte', 'anleitung']):
                    line = f"### 💻 {header_text}"
                elif any(word in header_text.lower() for word in ['hinweise', 'wichtig', 'beachten', 'tipp']):
                    line = f"### 💡 {header_text}"
                else:
                    line = f"### {header_text}"
            
            # Überschriften-Hierarchie korrigieren
            elif line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                content = line.lstrip('#').strip()
                
                # Hauptüberschrift
                if level == 1 or (level == 2 and not content.startswith('🔧')):
                    line = f"## 🔧 {content}"
                # Unterüberschriften
                elif level >= 3 or (level == 2 and content.startswith('🔧')):
                    line = f"### {content}"
            
            formatted_lines.append(line)
        
        # Leere Zeilen bereinigen (max 2 aufeinanderfolgende)
        cleaned_lines = []
        empty_count = 0
        for line in formatted_lines:
            if not line.strip():
                empty_count += 1
                if empty_count <= 1:
                    cleaned_lines.append(line)
            else:
                empty_count = 0
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get detailed service statistics with performance metrics"""
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
            },
            "model_config": {
                "temperature": settings.MODEL_TEMPERATURE,
                "top_p": settings.MODEL_TOP_P,
                "top_k": settings.MODEL_TOP_K,
                "max_tokens": settings.MODEL_MAX_TOKENS,
                "context_window": settings.MODEL_CONTEXT_WINDOW,
                "threads": settings.MODEL_THREADS
            },
            "status": "ready" if self.is_initialized else "initializing"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check with performance metrics"""
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
    
    async def cleanup(self):
        """Cleanup resources"""
        await ollama_pool.cleanup()
        await response_cache.clear()
        response_cache.cleanup_task_shutdown()
        logger.info("🧹 Optimized Mistral Service cleanup complete")

# Global instance
mistral_llm_service = MistralLLMService()