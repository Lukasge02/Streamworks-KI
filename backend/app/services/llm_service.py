"""
LLM Service für DirectChat mit Ollama 7B Modellen
Verwendet Ollama für bessere Performance und größere Modelle
"""
import logging
import asyncio
from typing import Optional
import ollama
import re
from app.core.config import settings

logger = logging.getLogger(__name__)

# StreamWorks-spezifische System Prompts für CodeLlama
STREAMWORKS_SYSTEM_PROMPT = """
Du bist SKI (StreamWorks-KI), ein hochspezialisierter Experte für StreamWorks-Automatisierung bei Arvato Systems.

SPRACHE: Antworte ausschließlich auf DEUTSCH!

EXPERTISE:
- XML-Stream-Erstellung und -Konfiguration
- Batch-Job-Automatisierung und PowerShell-Integration
- CSV-Datenverarbeitung und Workload-Management
- StreamWorks-Architektur und Best Practices

ANTWORT-FORMAT:
- Verwende Markdown-Formatierung
- Strukturiere mit ##, ### für Überschriften
- Code-Beispiele in ```xml, ```powershell, ```batch Blöcken
- Deutsche Kommentare in Code-Beispielen
- Emojis für visuelle Struktur: 📋, 🔧, ✅, 🚀
- Zitiere Quellen: [Quelle: filename]

ANTWORT-STIL:
- Präzise und technisch korrekt
- Verständlich für Fachleute
- Konkrete Beispiele und Code-Snippets
- Proaktive Lösungsvorschläge
"""

class LLMService:
    """LLM Service für direkte Chat-Antworten mit Ollama - StreamWorks-optimiert"""
    
    def __init__(self):
        self.is_initialized = False
        self.model_name = getattr(settings, 'OLLAMA_MODEL', 'llama2:7b')
        self.client = ollama.Client()
        
        logger.info(f"🤖 Ollama LLM Service initialisiert mit {self.model_name}")
    
    def _check_ollama_running(self) -> bool:
        """Check if Ollama server is running"""
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.warning(f"⚠️ Ollama server nicht erreichbar: {e}")
            return False
    
    async def initialize(self):
        """Initialize Ollama LLM Service"""
        try:
            logger.info(f"🔄 Initialisiere Ollama mit {self.model_name}...")
            
            # Check if Ollama server is running
            if not self._check_ollama_running():
                logger.error("❌ Ollama server ist nicht verfügbar. Bitte starte Ollama.")
                return
            
            # Check if model is available, if not pull it
            available_models = [model['name'] for model in self.client.list()['models']]
            
            if self.model_name not in available_models:
                logger.info(f"📥 Model {self.model_name} nicht gefunden. Lade Model herunter...")
                try:
                    self.client.pull(self.model_name)
                    logger.info(f"✅ Model {self.model_name} erfolgreich heruntergeladen")
                except Exception as e:
                    logger.error(f"❌ Fehler beim Herunterladen des Models: {e}")
                    # Fallback to smaller model
                    self.model_name = "llama2:7b"
                    if self.model_name not in available_models:
                        logger.info(f"📥 Fallback: Lade {self.model_name}...")
                        self.client.pull(self.model_name)
            
            # Test the model with a simple prompt
            test_response = self.client.generate(
                model=self.model_name,
                prompt="Hello",
                options={"num_predict": 5}
            )
            
            if test_response:
                self.is_initialized = True
                logger.info(f"✅ Ollama LLM erfolgreich initialisiert mit {self.model_name}")
            else:
                raise Exception("Model test failed")
            
        except Exception as e:
            logger.error(f"❌ Ollama LLM Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
            raise
    
    async def generate_response(self, message: str, conversation_history: Optional[list] = None, context: Optional[str] = None) -> str:
        """Generate enhanced LLM response using Ollama with StreamWorks expertise"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Build enhanced conversation context with RAG context
            prompt = self._build_enhanced_context(conversation_history, message, context)
            
            logger.info(f"📝 Generiere Ollama Antwort für: '{message[:50]}...'")
            
            # Generate response with Ollama
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 800,  # More tokens for detailed responses
                        "stop": ["\n\n\n", "User:", "Assistant:"],
                        "repeat_penalty": 1.15,  # Reduce repetition
                        "num_ctx": 8192  # Larger context window for CodeLlama
                    }
                )
            )
            
            if response and 'response' in response:
                generated_text = response['response'].strip()
                
                # Post-process response for quality
                processed_response = self._post_process_response(generated_text)
                
                if processed_response:
                    logger.info(f"✅ Ollama Antwort generiert: '{processed_response[:50]}...'")
                    return processed_response
                else:
                    return self._generate_enhanced_fallback(message)
            else:
                return self._generate_enhanced_fallback(message)
                
        except Exception as e:
            logger.error(f"❌ Ollama Generation Error: {e}")
            return self._generate_enhanced_fallback(message)
    
    def _build_enhanced_context(self, history: Optional[list], current_message: str, rag_context: Optional[str] = None) -> str:
        """Build enhanced conversation context with StreamWorks expertise"""
        context_parts = [
            STREAMWORKS_SYSTEM_PROMPT,
            ""
        ]
        
        # Add RAG context if available
        if rag_context:
            context_parts.append("RELEVANTE DOKUMENTATION:")
            context_parts.append(rag_context)
            context_parts.append("")
        
        # Add conversation history if available
        if history:
            for exchange in history[-3:]:  # Last 3 exchanges
                if isinstance(exchange, dict):
                    user_msg = exchange.get("user", "")
                    ai_msg = exchange.get("assistant", "")
                    if user_msg and ai_msg:
                        context_parts.append(f"User: {user_msg}")
                        context_parts.append(f"Assistant: {ai_msg}")
        
        # Add current message
        context_parts.append(f"User: {current_message}")
        context_parts.append("Assistant:")
        
        return "\n".join(context_parts)
    
    def _post_process_response(self, response: str) -> str:
        """Post-process response for quality and formatting"""
        if not response:
            return ""
        
        # Clean up response
        response = response.strip()
        
        # CodeLlama should handle German better, minimal processing
        
        # Ensure proper Markdown formatting
        response = self._ensure_markdown_formatting(response)
        
        # Add source citations if missing
        response = self._add_source_citations(response)
        
        # Remove artifacts but preserve structure
        response = self._remove_artifacts(response)
        
        return response
    
    def _force_german_response(self, text: str) -> str:
        """Force German response if LLM starts mixing languages"""
        # If response starts in German but switches to English, cut it at the English part
        sentences = text.split('.')
        german_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Common English indicators that suggest language switch
            english_indicators = [
                "you can", "you have", "here's", "there,", "click on", 
                "feel free", "if you have", "Once you've", "They can be",
                "This will", "You can choose", "In terms of"
            ]
            
            # If sentence contains typical English phrases, stop here
            if any(indicator in sentence.lower() for indicator in english_indicators):
                break
                
            german_sentences.append(sentence)
        
        # If we have good German content, use it
        if german_sentences and len(german_sentences) >= 2:
            result = '. '.join(german_sentences) + '.'
            
            # Add a German ending if it was cut short
            if len(german_sentences) < len(sentences) / 2:
                result += "\n\n**Weitere Informationen gerne auf Nachfrage!**"
            
            return result
        
        # Otherwise return original
        return text
    
    def _ensure_markdown_formatting(self, text: str) -> str:
        """Ensure proper Markdown formatting"""
        # Fix code blocks
        text = re.sub(r'```([^\n]*)', r'```\1\n', text)
        text = re.sub(r'([^\n])```', r'\1\n```', text)
        
        # Ensure headers have proper spacing
        text = re.sub(r'(#+)([^\s#])', r'\1 \2', text)
        
        return text
    
    def _add_source_citations(self, text: str) -> str:
        """Add source citations if context mentions files"""
        # This will be enhanced when integrated with RAG
        return text
    
    def _remove_artifacts(self, text: str) -> str:
        """Remove common LLM artifacts while preserving structure"""
        # Remove excessive newlines but preserve paragraph structure
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        
        # Remove repetitive sentences
        sentences = text.split('.')
        unique_sentences = []
        for sent in sentences:
            if sent.strip() and sent.strip() not in [s.strip() for s in unique_sentences]:
                unique_sentences.append(sent)
        
        return '.'.join(unique_sentences).strip()
    
    def _generate_enhanced_fallback(self, message: str) -> str:
        """Generate enhanced fallback response with StreamWorks focus"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["xml", "stream", "erstell"]):
            return """## 🔧 XML-Stream-Erstellung

Gerne helfe ich dir bei der XML-Stream-Erstellung! Hier sind deine Optionen:

1. **Stream Generator Tab**: Für interaktive Stream-Konfiguration
2. **Direkter Chat**: Stelle mir spezifische Fragen zu XML-Strukturen
3. **Dokumentation**: Lade StreamWorks-Dokumentation für detaillierte Anleitungen hoch

Was möchtest du genau erstellen?"""
        
        elif any(word in message_lower for word in ["batch", "job", "schedule"]):
            return """## 📅 Batch-Job Scheduling

Für Batch-Job-Konfiguration kann ich dir helfen mit:

- **Zeitplanung**: Daily, Weekly, Monthly Schedules
- **PowerShell Integration**: Script-Ausführung
- **Fehlerbehandlung**: Retry-Mechanismen

Beschreibe deinen Use-Case genauer!"""
        
        elif any(word in message_lower for word in ["hilfe", "help", "was", "wie"]):
            return """## 👋 Willkommen bei SKI - StreamWorks-KI!

Ich bin dein Experte für:

### 📋 Meine Expertise:
- **XML-Streams**: Erstellung und Konfiguration
- **Batch-Jobs**: Automatisierung und Scheduling
- **PowerShell**: Integration und Scripting
- **Best Practices**: StreamWorks-Architektur

### 🚀 Wie kann ich helfen?
Stelle mir eine spezifische Frage oder nutze die anderen Tabs für:
- Stream Generator (XML-Erstellung)
- Training Data (Dokumenten-Upload)

Was interessiert dich?"""
        
        else:
            return f"""## ❓ Präzisiere deine Frage

Ich konnte '{message}' nicht eindeutig zuordnen. Versuche es mit:

- **Konkreten Begriffen**: XML, Stream, Batch, Schedule
- **Beispielen**: "Wie erstelle ich einen täglichen Job?"
- **Kontext**: Welches Problem möchtest du lösen?

Oder nutze die spezialisierten Tabs für direkte Aktionen!"""
    
    async def generate_response_with_context(self, message: str, rag_context: str, conversation_history: Optional[list] = None) -> str:
        """Special method for RAG-enhanced responses"""
        return await self.generate_response(message, conversation_history, rag_context)
    
    async def get_stats(self) -> dict:
        """Get Ollama LLM service statistics"""
        stats = {
            "status": "healthy" if self.is_initialized else "not_initialized",
            "model_name": self.model_name,
            "backend": "ollama",
            "is_initialized": self.is_initialized,
            "server_running": self._check_ollama_running()
        }
        
        # Add available models if server is running
        if stats["server_running"]:
            try:
                models = self.client.list()
                stats["available_models"] = [model['name'] for model in models.get('models', [])]
            except:
                stats["available_models"] = []
        
        return stats

# Global instance
llm_service = LLMService()