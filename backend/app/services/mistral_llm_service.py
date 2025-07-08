"""
Mistral 7B LLM Service - Deutsche Optimierung
Spezialisiert für StreamWorks-KI mit professionellen deutschen Antworten
"""
import logging
import re
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.prompts.manager import prompt_manager

logger = logging.getLogger(__name__)

class MistralLLMService:
    """Mistral 7B Service mit deutscher Optimierung"""
    
    def __init__(self):
        self.model_name = settings.OLLAMA_MODEL
        self.ollama_url = f"{settings.OLLAMA_HOST}/api/generate"
        self.is_initialized = False
        
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
        
        logger.info("🤖 Mistral LLM Service initialisiert")
    
    async def initialize(self, skip_warmup: bool = False):
        """Initialisiere Mistral Service mit optimierter Performance"""
        try:
            logger.info("🔥 Initializing Mistral 7B...")
            
            if skip_warmup:
                # Schnelle Initialisierung ohne Warm-up
                logger.info("⚡ Skipping warm-up for faster startup")
                self.is_initialized = True
                return
            
            # Lightweight warm-up statt vollständiger deutscher Antwort
            logger.info("🏃‍♂️ Quick warm-up with minimal request...")
            test_response = await self.ollama_generate(
                prompt="Test",
                options={
                    "temperature": 0.1,
                    "num_predict": 3,  # Minimal response
                    "num_ctx": 256,    # Minimal context
                    "num_thread": settings.MODEL_THREADS
                },
                timeout=15.0  # Shorter timeout for init
            )
            
            if test_response:
                self.is_initialized = True
                logger.info("✅ Mistral 7B initialisiert - Warm-up erfolgreich")
            else:
                # Fallback: Markiere als initialisiert auch ohne Warm-up
                logger.warning("⚠️ Warm-up fehlgeschlagen, aber Service als verfügbar markiert")
                self.is_initialized = True
                
        except Exception as e:
            logger.error(f"❌ Mistral Initialisierung fehlgeschlagen: {e}")
            # Fallback: Service trotzdem als verfügbar markieren
            logger.info("🔄 Fallback: Service wird als verfügbar markiert für spätere Requests")
            self.is_initialized = True
    
    async def ollama_generate(self, prompt: str, model: str = None, options: Dict[str, Any] = None, timeout: float = 30.0) -> str:
        """Ollama API Call mit Mistral-Optimierung und verbessertem Error Handling"""
        
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
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options
        }
        
        try:
            # Connection mit optimierten Timeouts
            connector = aiohttp.TCPConnector(
                limit=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30
            )
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=timeout, connect=5.0)
            ) as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        logger.error(f"Ollama API Error: {response.status} - {await response.text()}")
                        return self._get_fallback_response("API_ERROR")
                        
        except asyncio.TimeoutError:
            logger.error(f"Ollama Request Timeout after {timeout}s")
            return self._get_fallback_response("TIMEOUT")
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Ollama Connection Error: {e}")
            return self._get_fallback_response("CONNECTION_ERROR")
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
    
    async def generate_german_response(self, user_message: str, context: str = "", fast_mode: bool = False) -> str:
        """Optimierte deutsche Antwort mit Mistral 7B und Performance-Modi"""
        
        # Performance-Optimierung: Fast Mode für kritische Antworten
        if fast_mode:
            options = {
                "temperature": 0.3,      # Niedrigere Temp für schnellere Antworten
                "top_p": 0.8,           # Fokussierter
                "top_k": 20,            # Weniger Optionen = schneller
                "repeat_penalty": 1.1,
                "num_predict": 256,     # Kürzere Antworten
                "num_ctx": 1024,        # Weniger Context = schneller
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
        
        try:
            # Nutze Prompt Manager für konsistente Prompts
            prompt = prompt_manager.build_prompt(
                template_type="mistral_system_prompt",
                context={
                    "context": context,
                    "user_message": user_message
                }
            )
            
            # Ollama-Request mit optimierten Parametern
            response = await self.ollama_generate(
                prompt=prompt,
                model=self.model_name,
                options=options,
                timeout=timeout
            )
            
            # Deutsche Nachbearbeitung (schneller im Fast Mode)
            if fast_mode:
                german_response = self._quick_german_processing(response)
            else:
                german_response = self.post_process_german(response)
            
            return german_response
            
        except Exception as e:
            logger.error(f"Error generating German response: {e}")
            return self._get_fallback_response("GENERAL_ERROR")
    
    def _quick_german_processing(self, response: str) -> str:
        """Schnelle deutsche Nachbearbeitung für Fast Mode"""
        if not response:
            return "Entschuldigung, ich konnte keine Antwort generieren."
        
        # Nur essenzielle Korrekturen
        essential_replacements = {
            " du ": " Sie ",
            " dich ": " Sie ",
            " dein ": " Ihr ",
            " deine ": " Ihre ",
            " dir ": " Ihnen "
        }
        
        for eng, ger in essential_replacements.items():
            response = response.replace(eng, ger)
        
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
        """Mistral Service Statistiken"""
        return {
            "service": "mistral_llm",
            "model_name": self.model_name,
            "is_initialized": self.is_initialized,
            "temperature": settings.MODEL_TEMPERATURE,
            "top_p": settings.MODEL_TOP_P,
            "top_k": settings.MODEL_TOP_K,
            "max_tokens": settings.MODEL_MAX_TOKENS,
            "context_window": settings.MODEL_CONTEXT_WINDOW,
            "threads": settings.MODEL_THREADS,
            "german_optimization": settings.FORCE_GERMAN_RESPONSES,
            "status": "ready" if self.is_initialized else "initializing"
        }
    
    async def health_check(self) -> bool:
        """Health Check für Mistral Service"""
        try:
            # Quick health check with timeout
            test_response = await asyncio.wait_for(
                self.ollama_generate(
                    prompt="Reply with 'OK' if working",
                    model=self.model_name,
                    options={
                        "temperature": 0.1,
                        "num_predict": 10,  # Very short response
                        "num_ctx": 512  # Minimal context
                    }
                ),
                timeout=5.0  # 5 second timeout
            )
            return len(test_response) > 0
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

# Global instance
mistral_llm_service = MistralLLMService()