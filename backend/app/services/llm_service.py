import asyncio
from typing import Optional
import logging
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel, LoraConfig, get_peft_model
from tqdm import tqdm
import time
from ..core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """LLM Service für StreamWorks-KI"""
    
    def __init__(self):
        # Force reload settings
        from ..core.config import Settings
        fresh_settings = Settings()
        self.model_name = fresh_settings.MODEL_NAME
        self.tokenizer = None
        self.model = None
        self.is_initialized = False
        print(f"🔧 LLMService initialized with model: {self.model_name}")
        logger.info(f"🔧 LLMService initialized with model: {self.model_name}")
        
    @property
    def device(self):
        """Get current device setting"""
        return self._detect_device()
    
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
        """Initialize LLM service with progress bars"""
        print(f"\n🤖 Initializing LLM Service with {self.model_name}...")
        print(f"📱 Device: {self.device}")
        logger.info(f"🤖 Initializing LLM Service with {self.model_name}...")
        logger.info(f"📱 Device: {self.device}")
        
        # Skip heavy model loading if requested
        if settings.SKIP_MODEL_LOADING:
            print("⚡ Skipping model loading - using fallback responses only")
            self.is_initialized = True
            return
        
        try:
            # Load tokenizer with progress
            print("📝 Loading tokenizer...")
            logger.info("📝 Loading tokenizer...")
            
            # Progress bar for tokenizer loading
            with tqdm(total=100, desc="🔤 Tokenizer", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                pbar.update(100)
            print("✅ Tokenizer loaded successfully")
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Configure quantization for memory efficiency 
            # Skip quantization on MPS (Mac) as it's not supported
            if self.device == "cuda":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16
                )
            else:
                quantization_config = None
            
            # Load model with Mac optimizations and progress
            print(f"🧠 Loading {self.model_name} model...")
            logger.info(f"🧠 Loading {self.model_name} model...")
            
            # Progress bar for model loading
            with tqdm(total=100, desc="🧠 Model", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=quantization_config,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float16 if self.device in ["cuda", "mps"] else torch.float32,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True
                )
                pbar.update(100)
            print("✅ Model loaded successfully")
            
            # Setup LoRA for fine-tuning if enabled
            if settings.USE_LORA:
                print("🔧 Setting up LoRA configuration...")
                logger.info("🔧 Setting up LoRA configuration...")
                
                with tqdm(total=100, desc="🔧 LoRA", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
                    lora_config = LoraConfig(
                        r=settings.LORA_RANK,
                        lora_alpha=settings.LORA_ALPHA,
                        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
                        lora_dropout=settings.LORA_DROPOUT,
                        bias="none",
                        task_type="CAUSAL_LM"
                    )
                    self.model = get_peft_model(self.model, lora_config)
                    pbar.update(100)
                print("✅ LoRA configuration applied")
                logger.info("✅ LoRA configuration applied")
            else:
                print("🔧 LoRA disabled - using base model")
                logger.info("🔧 LoRA disabled - using base model")
            
            # Move model to device with progress
            if self.device != "cuda":
                print(f"📱 Moving model to {self.device}...")
                with tqdm(total=100, desc="📱 Device", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
                    self.model = self.model.to(self.device)
                    pbar.update(100)
                print(f"✅ Model moved to {self.device}")
            
            self.is_initialized = True
            print("\n🎉 LLM Service initialized successfully!\n")
            logger.info("✅ LLM Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            # Fallback to mock mode
            self.is_initialized = False
            raise
    
    async def generate_response(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Generate AI response using Code-Llama 7B"""
        if not self.is_initialized:
            await self.initialize()
        
        print(f"🔄 Generating response for: {message[:50]}...")
        logger.info(f"🔄 Generating response for: {message[:50]}...")
        
        if not self.model or not self.tokenizer:
            logger.warning("⚠️ Model not loaded, using fallback")
            return self._generate_fallback_response(message)
        
        try:
            # Create instruction prompt for Code-Llama
            prompt = self._create_instruction_prompt(message)
            print(f"🔍 Prompt: '{prompt}'")
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=settings.MAX_TOKEN_LENGTH
            ).to(self.device)
            
            # Generate response with simplified settings for debugging
            print("🤖 Generating response...")
            print(f"Input shape: {inputs.input_ids.shape}")
            print(f"Input tokens: {inputs.input_ids[0].tolist()}")
            decoded_input = self.tokenizer.decode(inputs.input_ids[0])
            print(f"Decoded input: '{decoded_input}'")
            
            start_time = time.time()
            try:
                with torch.no_grad():
                    # T5 models need different parameters
                    if "t5" in self.model_name.lower():
                        outputs = self.model.generate(
                            input_ids=inputs.input_ids,
                            attention_mask=inputs.attention_mask,
                            max_new_tokens=settings.MAX_NEW_TOKENS,
                            temperature=settings.TEMPERATURE,
                            do_sample=True
                        )
                    else:
                        outputs = self.model.generate(
                            input_ids=inputs.input_ids,
                            attention_mask=inputs.attention_mask,
                            max_new_tokens=settings.MAX_NEW_TOKENS,
                            temperature=settings.TEMPERATURE,
                            do_sample=True,
                            pad_token_id=self.tokenizer.eos_token_id,
                            eos_token_id=self.tokenizer.eos_token_id,
                            repetition_penalty=1.1,  # Weniger aggressive Wiederholungsstrafe
                            top_p=0.85,  # Etwas fokussierter
                            top_k=50,  # Top-K Sampling hinzufügen
                            no_repeat_ngram_size=3,  # Verhindert 3-Wort-Wiederholungen
                            early_stopping=True
                        )
                
                generation_time = time.time() - start_time
                print(f"✅ Generation completed in {generation_time:.2f}s")
                
            except Exception as e:
                print(f"❌ Generation failed: {e}")
                raise
            
            # Decode response correctly
            # Get only the newly generated tokens
            input_length = inputs.input_ids.shape[1]
            generated_tokens = outputs[0][input_length:]
            
            response = self.tokenizer.decode(
                generated_tokens,
                skip_special_tokens=True
            ).strip()
            
            # Clean up response - remove common artifacts
            response = response.replace('\n', ' ').strip()
            
            # If response is empty or too short, use fallback
            if not response or len(response) < 5:
                final_response = self._generate_fallback_response(message)
            else:
                final_response = response
            
            print(f"📤 Response ready: {final_response[:100]}...\n")
            return final_response
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            logger.error(f"❌ Error generating response: {e}")
            return self._generate_fallback_response(message)
    
    def _create_instruction_prompt(self, message: str) -> str:
        """Create instruction prompt for Phi-2"""
        # Phi-2 works best with simple conversation format
        return f"Human: {message}\nAssistant: "
    
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

def reset_llm_service():
    """Reset LLM service to force reload"""
    global _llm_service
    _llm_service = None

# Create fresh instance
llm_service = LLMService()