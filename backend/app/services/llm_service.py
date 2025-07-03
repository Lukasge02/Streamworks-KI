# backend/app/services/llm_service.py
import torch
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SimpleLLMService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = settings.MODEL_NAME
        self.device = settings.DEVICE
        self.is_initialized = False
        self.executor = ThreadPoolExecutor(max_workers=1)  # Single thread für LLM
        print(f"🤖 SimpleLLMService erstellt mit {self.model_name}")
    
    def _check_memory(self):
        """Memory Check vor Model Loading"""
        if torch.backends.mps.is_available():
            print(f"📊 MPS verfügbar")
        else:
            print(f"⚠️ MPS nicht verfügbar, fallback auf CPU")
            self.device = "cpu"
    
    def initialize(self):
        """Model laden mit verbessertem Error Handling"""
        try:
            self._check_memory()
            print(f"🚀 Lade {self.model_name} auf {self.device}...")
            
            # Tokenizer laden
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                use_fast=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            print("✅ Tokenizer geladen")
            
            # Model laden mit reduzierten Requirements
            model_kwargs = {
                "low_cpu_mem_usage": True,
                "device_map": None,
            }
            
            # Nur FP16 wenn nicht CPU
            if self.device != "cpu":
                model_kwargs["torch_dtype"] = torch.float16
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Model zu Device bewegen
            self.model.to(self.device)
            self.model.eval()  # Inference mode
            
            self.is_initialized = True
            print("✅ Model erfolgreich geladen!")
            
        except Exception as e:
            logger.error(f"❌ Model Loading Error: {e}")
            print(f"❌ Fehler beim Model laden: {e}")
            # Fallback zu Development Mode
            self.is_initialized = False
    
    def _generate_sync(self, message: str) -> str:
        """Synchrone Generation mit Timeout"""
        try:
            # Development Fallback
            if not self.is_initialized:
                responses = [
                    "🤖 Hallo! Ich bin SKI. Wie kann ich dir bei StreamWorks helfen?",
                    "📋 Ich kann dir beim Erstellen von XML-Streams helfen.",
                    "⚡ StreamWorks-Automatisierung ist meine Spezialität!",
                    "🔧 Lass uns zusammen deinen Workflow optimieren."
                ]
                import random
                return random.choice(responses)
            
            # Real LLM Generation
            prompt = f"""<s>[INST] <<SYS>>
Du bist SKI (StreamWorks-KI), ein hilfsreicher Assistent für StreamWorks-Automatisierung.
Antworte kurz und präzise auf Deutsch. Maximal 2 Sätze.
<</SYS>>

{message} [/INST]"""
            
            # Tokenisieren mit Limits
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt",
                max_length=256,  # Reduziert!
                truncation=True,
                padding=True
            ).to(self.device)
            
            # Generation mit strengen Limits
            with torch.no_grad():
                start_time = time.time()
                outputs = self.model.generate(
                    input_ids=inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=50,  # Sehr kurze Antworten!
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True
                )
                generation_time = time.time() - start_time
                print(f"⏱️ Generation Zeit: {generation_time:.2f}s")
            
            # Response extrahieren
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(prompt, "").strip()
            
            if not response:
                return "🤖 Entschuldigung, ich konnte keine passende Antwort generieren."
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Generation Error: {e}")
            return f"❌ Fehler bei der Antwort-Generierung. Entwicklungsmodus aktiv."
    
    async def generate_response(self, message: str) -> str:
        """Async Wrapper mit Timeout"""
        try:
            print(f"📝 Input: {message}")
            
            # Async execution mit Timeout
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    self.executor, 
                    self._generate_sync, 
                    message
                ),
                timeout=30.0  # 30 Sekunden Timeout
            )
            
            print(f"✅ Response: {response}")
            return response
            
        except asyncio.TimeoutError:
            print("⏰ Generation Timeout!")
            return "⏰ Entschuldigung, die Antwort dauerte zu lange. Versuche es nochmal."
        except Exception as e:
            logger.error(f"❌ Async Generation Error: {e}")
            return "❌ Unerwarteter Fehler. Bitte versuche es erneut."

# Globale Instanz
llm_service = SimpleLLMService()