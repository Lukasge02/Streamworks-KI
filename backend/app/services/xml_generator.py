"""
XML Generator Service with LoRA Fine-Tuning
Specializes in generating StreamWorks XML Streams
"""
import os
import logging
from typing import Dict, Optional
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, LoraConfig, get_peft_model, TaskType

from app.core.config import settings

logger = logging.getLogger(__name__)

class XMLGeneratorService:
    """XML Generation Service with LoRA Fine-Tuning Support"""
    
    def __init__(self):
        self.base_model = None
        self.tokenizer = None
        self.lora_model = None
        self.is_fine_tuned = False
        self.is_initialized = False
        self.device = self._detect_device()
        
        logger.info("🔧 XML Generator Service initialisiert")
    
    def _detect_device(self) -> str:
        """Detect optimal device"""
        if settings.DEVICE == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return settings.DEVICE
    
    async def initialize(self):
        """Initialize XML Generator"""
        if not settings.XML_GENERATION_ENABLED:
            logger.info("🔧 XML Generation ist deaktiviert")
            return
        
        try:
            logger.info("🚀 XML Generator wird initialisiert...")
            
            # Load tokenizer
            logger.info(f"📝 Lade Tokenizer: {settings.BASE_MODEL}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.BASE_MODEL,
                padding_side="left"  # For generation
            )
            
            # Add pad token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load base model
            logger.info(f"🧠 Lade Base Model: {settings.BASE_MODEL}")
            self.base_model = AutoModelForCausalLM.from_pretrained(
                settings.BASE_MODEL,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                low_cpu_mem_usage=True,
                device_map=None
            )
            
            # Move to device
            self.base_model.to(self.device)
            self.base_model.eval()
            
            # Try to load LoRA adapter if available
            await self._load_lora_adapter()
            
            self.is_initialized = True
            logger.info(f"✅ XML Generator initialisiert auf {self.device}")
            
        except Exception as e:
            logger.error(f"❌ XML Generator Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
            raise
    
    async def _load_lora_adapter(self):
        """Load LoRA adapter if available"""
        try:
            adapter_path = Path(settings.LORA_ADAPTER_PATH)
            
            if adapter_path.exists() and (adapter_path / "adapter_config.json").exists():
                logger.info(f"🔗 Lade LoRA Adapter: {adapter_path}")
                
                self.lora_model = PeftModel.from_pretrained(
                    self.base_model,
                    str(adapter_path),
                    device_map=None
                )
                
                self.is_fine_tuned = True
                logger.info("✅ LoRA Adapter erfolgreich geladen")
            else:
                logger.info("📭 Kein LoRA Adapter gefunden - nutze Base Model")
                self.lora_model = self.base_model
                self.is_fine_tuned = False
                
        except Exception as e:
            logger.warning(f"⚠️ LoRA Adapter laden fehlgeschlagen: {e}")
            self.lora_model = self.base_model
            self.is_fine_tuned = False
    
    async def generate_stream(self, requirements: Dict) -> str:
        """Optimierte XML-Generierung für Chat-Mode"""
        return await self.generate_xml_stream(requirements)

    async def generate_xml_stream(self, requirements: Dict) -> str:
        """Generate XML stream based on requirements"""
        if not self.is_initialized:
            if settings.XML_GENERATION_ENABLED:
                await self.initialize()
            else:
                return self._generate_mock_xml_enhanced(requirements)
        
        try:
            # Create prompt for XML generation
            prompt = self._create_xml_prompt(requirements)
            
            logger.info(f"📝 Generiere XML für: {requirements.get('name', 'Unnamed Stream')}")
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self.device)
            
            # Generate
            model = self.lora_model if self.lora_model else self.base_model
            
            with torch.no_grad():
                outputs = model.generate(
                    input_ids=inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=settings.MAX_NEW_TOKENS,
                    temperature=settings.TEMPERATURE,
                    top_p=settings.TOP_P,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode response
            generated_text = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            # Extract XML from generated text
            xml_content = self._extract_xml(generated_text)
            
            if xml_content:
                logger.info("✅ XML Stream erfolgreich generiert")
                return xml_content
            else:
                logger.warning("⚠️ Keine gültige XML generiert - nutze Template")
                return self._generate_mock_xml_enhanced(requirements)
                
        except Exception as e:
            logger.error(f"❌ XML Generation fehlgeschlagen: {e}")
            return self._generate_mock_xml_enhanced(requirements)
    
    def _create_xml_prompt(self, requirements: Dict) -> str:
        """Create prompt for XML generation"""
        name = requirements.get("name", "DataProcessing")
        schedule = requirements.get("schedule", "daily")
        source = requirements.get("source", "/data/input")
        target = requirements.get("target", "/data/output")
        description = requirements.get("description", "Data processing stream")
        
        if self.is_fine_tuned:
            # Use specialized prompt for fine-tuned model
            prompt = f"""Generiere StreamWorks XML Stream-Konfiguration:
Name: {name}
Zeitplan: {schedule}
Quelle: {source}
Ziel: {target}
Beschreibung: {description}

XML:"""
        else:
            # Use general prompt for base model
            prompt = f"""Erstelle XML-Konfiguration für Datenverarbeitung:
- Stream-Name: {name}
- Zeitplan: {schedule}
- Eingabe: {source}
- Ausgabe: {target}

Generiere XML:"""
        
        return prompt
    
    def _extract_xml(self, text: str) -> Optional[str]:
        """Extract XML content from generated text"""
        # Look for XML patterns
        import re
        
        # Find XML content between tags
        xml_patterns = [
            r'<\?xml.*?</.*?>',  # Full XML document
            r'<stream.*?</stream>',  # Stream tag
            r'<.*?>.*</.*?>'  # Any XML-like content
        ]
        
        for pattern in xml_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                xml_content = match.group(0)
                # Basic validation
                if self._is_valid_xml_structure(xml_content):
                    return xml_content
        
        return None
    
    def _is_valid_xml_structure(self, xml: str) -> bool:
        """Basic XML structure validation"""
        # Simple checks
        has_opening_tag = '<' in xml and '>' in xml
        has_closing_tag = '</' in xml
        has_reasonable_length = 50 < len(xml) < 5000
        
        return has_opening_tag and has_closing_tag and has_reasonable_length
    
    def _generate_mock_xml_enhanced(self, requirements: Dict) -> str:
        """Enhanced mock XML generation for chat mode with better templates"""
        name = requirements.get("name", "DataProcessing")
        schedule = requirements.get("schedule", "daily")
        source = requirements.get("source", "/data/input")
        target = requirements.get("target", "/data/output")
        description = requirements.get("description", "Data processing stream")
        
        # Determine cron expression based on schedule
        cron_expressions = {
            "hourly": "0 * * * *",
            "daily": "0 2 * * *",
            "weekly": "0 2 * * 0",
            "monthly": "0 2 1 * *"
        }
        cron = cron_expressions.get(schedule, "0 2 * * *")
        
        # Enhanced template with more realistic StreamWorks structure
        import datetime
        now = datetime.datetime.now().isoformat()
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<stream xmlns="http://streamworks.arvato.com/schema/v1">
  <metadata>
    <name>{name}</name>
    <description>{description}</description>
    <version>1.0</version>
    <created>{now}</created>
    <author>StreamWorks-KI</author>
    <category>data-processing</category>
  </metadata>
  
  <configuration>
    <schedule>
      <cron>{cron}</cron>
      <timezone>Europe/Berlin</timezone>
      <enabled>true</enabled>
    </schedule>
    
    <resources>
      <memory>512MB</memory>
      <timeout>3600</timeout>
      <retry_attempts>3</retry_attempts>
    </resources>
    
    <environment>
      <variables>
        <var name="SOURCE_PATH">{source}</var>
        <var name="TARGET_PATH">{target}</var>
        <var name="LOG_LEVEL">INFO</var>
      </variables>
    </environment>
  </configuration>
  
  <pipeline>
    <tasks>
      <task id="input" type="file_input">
        <name>Dateneingang</name>
        <source>{source}</source>
        <pattern>*.csv</pattern>
        <encoding>UTF-8</encoding>
        <validation>
          <required>true</required>
          <schema_check>enabled</schema_check>
        </validation>
      </task>
      
      <task id="validate" type="data_validation" depends_on="input">
        <name>Datenvalidierung</name>
        <rules>
          <check_empty_fields>true</check_empty_fields>
          <check_data_types>true</check_data_types>
          <check_duplicates>true</check_duplicates>
        </rules>
        <on_error>
          <action>quarantine</action>
          <notify>true</notify>
        </on_error>
      </task>
      
      <task id="transform" type="data_transform" depends_on="validate">
        <name>Datentransformation</name>
        <transformations>
          <normalize_encoding>true</normalize_encoding>
          <standardize_format>true</standardize_format>
          <add_timestamp>true</add_timestamp>
        </transformations>
      </task>
      
      <task id="output" type="file_output" depends_on="transform">
        <name>Datenausgang</name>
        <target>{target}</target>
        <format>csv</format>
        <compression>none</compression>
        <backup>
          <enabled>true</enabled>
          <retention_days>30</retention_days>
        </backup>
      </task>
    </tasks>
    
    <flow>
      <start>input</start>
      <sequence>
        <step>input</step>
        <step>validate</step>
        <step>transform</step>
        <step>output</step>
      </sequence>
    </flow>
  </pipeline>
  
  <monitoring>
    <logging>
      <level>INFO</level>
      <output>/logs/streams/{name}.log</output>
      <rotate>daily</rotate>
    </logging>
    
    <notifications>
      <email>
        <enabled>true</enabled>
        <recipients>admin@company.com</recipients>
        <on_success>false</on_success>
        <on_failure>true</on_failure>
      </email>
      
      <metrics>
        <enabled>true</enabled>
        <export_interval>300</export_interval>
      </metrics>
    </notifications>
  </monitoring>
  
  <error_handling>
    <global_retry>
      <max_attempts>3</max_attempts>
      <backoff_strategy>exponential</backoff_strategy>
    </global_retry>
    
    <fallback>
      <enabled>true</enabled>
      <action>notify_and_stop</action>
    </fallback>
  </error_handling>
</stream>'''

    def _generate_mock_xml(self, requirements: Dict) -> str:
        """Generate mock XML when model is not available"""
        name = requirements.get("name", "DataProcessing")
        schedule = requirements.get("schedule", "daily")
        source = requirements.get("source", "/data/input")
        target = requirements.get("target", "/data/output")
        description = requirements.get("description", "Data processing stream")
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- StreamWorks XML-Stream generiert von SKI -->
<stream>
    <metadata>
        <name>{name}</name>
        <description>{description}</description>
        <version>1.0</version>
        <created>2025-07-04</created>
    </metadata>
    
    <schedule>
        <frequency>{schedule}</frequency>
        <time>02:00</time>
        <timezone>Europe/Berlin</timezone>
    </schedule>
    
    <pipeline>
        <source>
            <type>file</type>
            <path>{source}</path>
            <pattern>*.csv</pattern>
        </source>
        
        <processing>
            <step id="1">
                <name>Datenvalidierung</name>
                <type>validation</type>
                <config>
                    <rules>basic</rules>
                </config>
            </step>
            
            <step id="2">
                <name>DataTransformation</name>
                <type>transform</type>
                <config>
                    <format>standardize</format>
                </config>
            </step>
        </processing>
        
        <target>
            <type>file</type>
            <path>{target}</path>
            <format>processed</format>
        </target>
    </pipeline>
    
    <monitoring>
        <notifications>true</notifications>
        <logging>detailed</logging>
    </monitoring>
</stream>'''
    
    async def train_lora_adapter(self, training_data_path: str) -> bool:
        """Train LoRA adapter (placeholder for now)"""
        logger.info("🔧 LoRA Training wird in zukünftiger Version implementiert")
        return False
    
    async def get_stats(self) -> Dict:
        """Get XML Generator statistics"""
        return {
            "status": "healthy" if self.is_initialized else "disabled",
            "xml_generation_enabled": settings.XML_GENERATION_ENABLED,
            "base_model": settings.BASE_MODEL,
            "is_fine_tuned": self.is_fine_tuned,
            "lora_adapter_path": settings.LORA_ADAPTER_PATH,
            "device": self.device,
            "lora_config": {
                "r": settings.LORA_R,
                "alpha": settings.LORA_ALPHA,
                "dropout": settings.LORA_DROPOUT
            }
        }

# Global instance
xml_generator = XMLGeneratorService()