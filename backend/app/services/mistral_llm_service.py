"""
Mistral 7B LLM Service - Deutsche Optimierung
Spezialisiert für StreamWorks-KI mit professionellen deutschen Antworten
"""
import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Mistral-optimierte deutsche Prompts
MISTRAL_GERMAN_SYSTEM_PROMPT = """[INST] Du bist SKI (StreamWorks-KI), ein hochspezialisierter deutschsprachiger Experte für StreamWorks-Automatisierung bei Arvato Systems.

=== WICHTIGE REGELN ===
- Antworte AUSSCHLIESSLICH auf Deutsch
- Verwende professionelle Höflichkeitsformen (Sie/Ihnen)
- Strukturiere Antworten mit Markdown und Emojis
- Nutze deutsche IT-Fachbegriffe konsequent
- Zitiere Quellen korrekt mit [Quelle: dateiname]

=== ANTWORT-STRUKTUR ===
## 🔧 [Thema]
### 📋 [Hauptantwort]
### 💡 [Zusätzliche Hinweise]
### 🚀 [Verwandte Themen/Nächste Schritte]

=== FACHBEREICHE ===
- XML-Stream-Erstellung und -Konfiguration
- Batch-Job-Automatisierung
- PowerShell-Integration
- CSV-Datenverarbeitung
- Workload-Management

=== KONTEXT ===
{context}

=== BENUTZERANFRAGE ===
{user_message} [/INST]

Antwort auf Deutsch:
"""

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
    
    async def initialize(self):
        """Initialisiere Mistral Service"""
        try:
            logger.info("🔥 Warming up Mistral 7B...")
            
            # Test-Request um Model zu laden
            test_response = await self.generate_german_response(
                user_message="Hallo SKI, bist du bereit?",
                context=""
            )
            
            if test_response and len(test_response) > 10:
                self.is_initialized = True
                logger.info("✅ Mistral 7B erfolgreich initialisiert und warm-up abgeschlossen")
            else:
                logger.warning("⚠️ Mistral warm-up unvollständig")
                
        except Exception as e:
            logger.error(f"❌ Mistral Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
    
    async def ollama_generate(self, prompt: str, model: str = None, options: Dict[str, Any] = None) -> str:
        """Ollama API Call mit Mistral-Optimierung"""
        
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
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload, timeout=120) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        logger.error(f"Ollama API Error: {response.status}")
                        return "Entschuldigung, es gab ein Problem bei der Verarbeitung Ihrer Anfrage."
                        
        except asyncio.TimeoutError:
            logger.error("Ollama Request Timeout")
            return "Die Anfrage hat zu lange gedauert. Bitte versuchen Sie es erneut."
        except Exception as e:
            logger.error(f"Ollama Request Error: {e}")
            return "Es ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut."
    
    async def generate_german_response(self, user_message: str, context: str = "") -> str:
        """Optimierte deutsche Antwort mit Mistral 7B"""
        
        # Mistral-optimierter Prompt
        prompt = MISTRAL_GERMAN_SYSTEM_PROMPT.format(
            context=context,
            user_message=user_message
        )
        
        # Ollama-Request mit Mistral-Parametern
        response = await self.ollama_generate(
            prompt=prompt,
            model=self.model_name,
            options={
                "temperature": settings.MODEL_TEMPERATURE,
                "top_p": settings.MODEL_TOP_P,
                "top_k": settings.MODEL_TOP_K,
                "repeat_penalty": settings.MODEL_REPEAT_PENALTY,
                "num_predict": settings.MODEL_MAX_TOKENS,
                "num_thread": settings.MODEL_THREADS
            }
        )
        
        # Deutsche Nachbearbeitung
        german_response = self.post_process_german(response)
        
        return german_response
    
    def post_process_german(self, response: str) -> str:
        """Nachbearbeitung für perfekte deutsche Antworten"""
        
        if not response:
            return "Entschuldigung, ich konnte keine Antwort generieren."
        
        # Englische Fachbegriffe ersetzen
        for eng, ger in self.german_replacements.items():
            response = response.replace(eng, ger)
        
        # Höflichkeitsformen sicherstellen (nur wenn nötig)
        if " du " in response or " dich " in response:
            response = response.replace(" du ", " Sie ")
            response = response.replace(" dich ", " Sie ")
            response = response.replace(" dein ", " Ihr ")
            response = response.replace(" deine ", " Ihre ")
            response = response.replace(" dir ", " Ihnen ")
        
        # Markdown-Formatierung verbessern
        response = self.enhance_markdown_formatting(response)
        
        return response
    
    def enhance_markdown_formatting(self, text: str) -> str:
        """Verbessere Markdown-Formatierung"""
        
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Fettgedruckten Text zu Überschrift machen
            if line.startswith('**') and line.endswith('**') and len(line) > 4:
                line = f"### {line.replace('**', '')}"
            
            # Sicherstellen dass Überschriften korrekt formatiert sind
            elif line.startswith('#') and not line.startswith('##'):
                if not line.startswith('## '):
                    line = f"## {line.lstrip('#').strip()}"
            
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
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
            test_response = await self.generate_german_response(
                user_message="Test",
                context=""
            )
            return len(test_response) > 0
        except Exception:
            return False

# Global instance
mistral_llm_service = MistralLLMService()