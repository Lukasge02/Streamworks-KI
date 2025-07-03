import asyncio
from typing import Optional
import logging
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from ..core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """LLM Service für StreamWorks-KI"""
    
    def __init__(self):
        self.model_name = settings.MODEL_NAME
        self.device = self._detect_device()
        self.tokenizer = None
        self.model = None
        self.is_initialized = False
        logger.info(f"🔧 LLMService initialized with model: {self.model_name}")
    
    def _detect_device(self) -> str:
        """Detect optimal device for model"""
        if settings.DEVICE == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return settings.DEVICE
    
    async def initialize(self):
        """Initialize LLM service"""
        logger.info(f"🤖 Initializing LLM Service with {self.model_name}...")
        logger.info(f"📱 Device: {self.device}")
        
        try:
            # Load tokenizer
            logger.info("📝 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Configure quantization for memory efficiency
            if self.device == "cuda":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16
                )
            else:
                quantization_config = None
            
            # Load model
            logger.info("🧠 Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            )
            
            if self.device != "cuda":
                self.model = self.model.to(self.device)
            
            self.is_initialized = True
            logger.info("✅ LLM Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            # Fallback to mock mode
            self.is_initialized = False
            raise
    
    async def generate_response(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Generate AI response using Code-Llama"""
        if not self.is_initialized:
            await self.initialize()
        
        logger.info(f"🔄 Generating response for: {message[:50]}...")
        
        if not self.model or not self.tokenizer:
            logger.warning("⚠️ Model not loaded, using fallback")
            return self._generate_fallback_response(message)
        
        try:
            # Create instruction prompt for Code-Llama
            prompt = self._create_instruction_prompt(message)
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=settings.MAX_TOKEN_LENGTH
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=settings.MAX_NEW_TOKENS,
                    temperature=settings.TEMPERATURE,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            return response if response else self._generate_fallback_response(message)
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return self._generate_fallback_response(message)
    
    def _create_instruction_prompt(self, message: str) -> str:
        """Create instruction prompt for Code-Llama"""
        system_prompt = """You are SKI (StreamWorks-KI), an AI assistant specialized in StreamWorks automation and XML stream generation. You help users create XML streams, batch files, and API integrations for data processing workflows.

Respond in German and be helpful, concise, and technical when needed."""
        
        return f"[INST] {system_prompt}\n\nUser: {message} [/INST]"
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate fallback response when model fails"""
        message_lower = message.lower()
        
        if "xml" in message_lower or "stream" in message_lower:
            return self._generate_xml_response(message)
        elif "help" in message_lower or "hilfe" in message_lower:
            return self._generate_help_response()
        elif "api" in message_lower:
            return self._generate_api_response()
        else:
            return f"Hallo! Ich bin SKI - die StreamWorks-KI. Sie haben geschrieben: '{message}'. Ich kann Ihnen bei der Erstellung von XML-Streams helfen! Was möchten Sie generieren?"
    
    def _generate_xml_response(self, message: str) -> str:
        """Generate XML stream response"""
        return '''Hier ist ein Beispiel XML-Stream für Sie:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<stream>
  <n>DailyDataProcessing</n>
  <schedule>
    <time>02:00</time>
    <frequency>daily</frequency>
  </schedule>
  <job>
    <n>ProcessCSVData</n>
    <source>/data/input/*.csv</source>
    <target>/data/output/processed</target>
    <transformation>
      <filter>active_records</filter>
      <aggregate>sum(amount)</aggregate>
    </transformation>
  </job>
</stream>
```

Möchten Sie den Stream Generator verwenden, um einen angepassten Stream zu erstellen?'''
    
    def _generate_help_response(self) -> str:
        """Generate help response"""
        return '''Gerne helfe ich Ihnen! Als SKI (StreamWorks-KI) kann ich:

• 🔄 XML-Streams generieren
• 📖 Fragen zur StreamWorks-Dokumentation beantworten  
• 🔗 API-Calls automatisch erstellen
• 📁 Batch-Dateien analysieren
• ⚙️ Workload-Automatisierung optimieren

Verwenden Sie den "Stream Generator" Tab für die XML-Erstellung oder fragen Sie mich einfach!'''
    
    def _generate_api_response(self) -> str:
        """Generate API response"""
        return '''Hier ist ein Beispiel für einen StreamWorks API-Call:

```python
import requests

response = requests.post(
    "https://api.streamworks.com/v1/streams",
    json={
        "name": "DailyProcessing", 
        "schedule": "0 2 * * *",
        "config": {
            "source": "/data/input/",
            "target": "/data/output/"
        }
    }
)
```

Benötigen Sie eine spezifische API-Integration?'''

# Global instance with lazy loading
_llm_service = None

def get_llm_service() -> LLMService:
    """Get LLM service instance (lazy loaded)"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

# Backwards compatibility
llm_service = get_llm_service()