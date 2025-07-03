from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SimpleLLMService:
    """Einfacher LLM Service - erstmal nur zum Testen"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = settings.MODEL_NAME
        self.device = settings.DEVICE
        self.is_initialized = False
        print(f"🤖 SimpleLLMService erstellt mit {self.model_name}")
    
    def initialize(self):
        """Model laden - einfach und ohne Schnickschnack"""
        try:
            print(f"🚀 Lade {self.model_name}...")
            
            # Tokenizer laden
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("✅ Tokenizer geladen")
            
            # Model laden - Code-Llama optimiert
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device in ["cuda", "mps"] else torch.float32,
                low_cpu_mem_usage=True,
                device_map=None
            )
            
            self.model.to(self.device)
            self.is_initialized = True
            print("✅ Model geladen!")
            
        except Exception as e:
            logger.error(f"❌ Model laden fehlgeschlagen: {e}")
            print(f"❌ Fehler: {e}")
            self.is_initialized = False
    
    def generate_response(self, message: str) -> str:
        """Antwort generieren - einfach und funktional"""
        if not self.is_initialized:
            print("🔄 Model nicht initialisiert, lade jetzt...")
            self.initialize()
        
        if not self.is_initialized:
            return "❌ LLM nicht verfügbar. Versuche es später nochmal."
        
        try:
            # Code-Llama Instruction Prompt
            prompt = f"""<s>[INST] <<SYS>>
Du bist SKI (StreamWorks-KI), ein hilfsreicher Assistent für StreamWorks-Automatisierung.
Antworte immer höflich und verständlich auf Deutsch.
<</SYS>>

{message} [/INST]"""
            
            print(f"📝 Input: {message}")
            print(f"🎯 Prompt: {prompt}")
            
            # Tokenisieren
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)
            
            # Generieren - Code-Llama optimiert
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=settings.MAX_NEW_TOKENS,
                    temperature=settings.TEMPERATURE,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Antwort extrahieren
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.replace(prompt, "").strip()
            
            print(f"🤖 Raw Response: {response}")
            
            if not response:
                return "🤖 Ich verstehe dich nicht ganz. Kannst du die Frage anders stellen?"
            
            return response
            
        except Exception as e:
            logger.error(f"Generation Error: {e}")
            print(f"❌ Generation Error: {e}")
            return f"❌ Fehler bei der Antwort-Generierung: {str(e)}"

# Globale Instanz
llm_service = SimpleLLMService()