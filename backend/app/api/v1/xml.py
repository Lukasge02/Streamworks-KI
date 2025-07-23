"""
StreamWorks XML Generator API
Enterprise-level XML generation with LLM integration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import re
from datetime import datetime

from app.core.settings import settings
from app.core.database_postgres import get_db
from app.services.mistral_llm_service import mistral_llm_service
from app.services.xml_template_service import xml_template_service

router = APIRouter()

# Pydantic Models
class XMLChatRequest(BaseModel):
    """Chat-based XML generation request"""
    prompt: str = Field(..., min_length=10, max_length=2000)
    context: str = Field(default="streamworks")
    template_id: Optional[str] = None

class XMLFormRequest(BaseModel):
    """Form-based XML generation request"""
    streamName: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    sourceSystem: str = Field(..., min_length=1, max_length=100)
    targetSystem: str = Field(..., min_length=1, max_length=100)
    dataFormat: str = Field(default="JSON", pattern=r"^(JSON|XML|CSV|XLSX)$")
    schedule: str = Field(default="daily", pattern=r"^(realtime|hourly|daily|weekly)$")

class XMLTemplateRequest(BaseModel):
    """Template-based XML generation request"""
    template_id: str = Field(..., min_length=1, max_length=100)
    parameters: Dict[str, str] = Field(default_factory=dict)

class ValidationResult(BaseModel):
    """XML validation result"""
    isValid: bool
    errors: List[str] = []
    warnings: List[str] = []

class XMLGenerationResponse(BaseModel):
    """XML generation response"""
    xml: str
    validation: ValidationResult
    metadata: Dict[str, Any]

class XMLStreamWorksService:
    """StreamWorks-specific XML generation service"""
    
    @staticmethod
    def get_streamworks_system_prompt() -> str:
        """Get StreamWorks-specific system prompt for XML generation"""
        return """Du bist ein StreamWorks XML-Experte. Generiere valides StreamWorks XML basierend auf den Anforderungen.

StreamWorks XML-Struktur:
- <streamworks-config> als Root-Element
- <stream> Elemente für jeden Datenstream
- <source> und <target> für Systeme
- <mapping> für Datenfeld-Zuordnungen  
- <schedule> für Zeitpläne
- <error-handling> für Fehlerbehandlung

Beispiel-Struktur:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<streamworks-config xmlns="http://streamworks.arvato.com/v1">
  <metadata>
    <name>{stream_name}</name>
    <description>{description}</description>
    <version>1.0</version>
    <created>{timestamp}</created>
  </metadata>
  
  <stream id="{stream_id}" type="batch">
    <source system="{source_system}" format="{format}">
      <connection-string>{connection}</connection-string>
      <query>{query}</query>
    </source>
    
    <target system="{target_system}" format="{format}">
      <connection-string>{connection}</connection-string>
      <table>{table}</table>
    </target>
    
    <mapping>
      <field source="id" target="customer_id" type="string" required="true"/>
      <field source="name" target="customer_name" type="string" required="true"/>
    </mapping>
    
    <schedule type="{schedule}">
      <cron>0 2 * * *</cron>
      <timezone>Europe/Berlin</timezone>
    </schedule>
    
    <error-handling>
      <retry-policy max-attempts="3" backoff="exponential"/>
      <dead-letter-queue enabled="true"/>
    </error-handling>
  </stream>
</streamworks-config>
```

Generiere immer valides XML mit korrekter Struktur und passenden StreamWorks-Elementen."""

    @staticmethod
    def generate_form_prompt(form_data: XMLFormRequest) -> str:
        """Generate prompt from form data"""
        return f"""Erstelle eine StreamWorks XML-Konfiguration mit folgenden Parametern:

Stream Name: {form_data.streamName}
Beschreibung: {form_data.description}
Quell-System: {form_data.sourceSystem}  
Ziel-System: {form_data.targetSystem}
Datenformat: {form_data.dataFormat}
Zeitplan: {form_data.schedule}

Generiere eine vollständige StreamWorks XML-Konfiguration mit:
- Metadata-Sektion mit Stream-Informationen
- Source-Konfiguration für {form_data.sourceSystem}
- Target-Konfiguration für {form_data.targetSystem}  
- Beispiel-Datenmapping
- Zeitplan-Konfiguration für {form_data.schedule}
- Fehlerbehandlung und Retry-Policy

Das XML soll production-ready und vollständig konfiguriert sein."""

    @staticmethod
    def validate_xml(xml_string: str) -> ValidationResult:
        """Validate generated XML"""
        errors = []
        warnings = []
        
        try:
            # Parse XML
            root = ET.fromstring(xml_string)
            
            # Check for StreamWorks namespace
            if 'streamworks' not in root.tag:
                warnings.append("XML sollte StreamWorks namespace verwenden")
            
            # Check for required elements
            required_elements = ['metadata', 'stream']
            for element in required_elements:
                if root.find(f".//{element}") is None:
                    errors.append(f"Pflicht-Element '{element}' fehlt")
            
            # Check stream structure
            streams = root.findall('.//stream')
            for i, stream in enumerate(streams):
                if not stream.get('id'):
                    errors.append(f"Stream {i+1} hat keine ID")
                
                if stream.find('.//source') is None:
                    errors.append(f"Stream {i+1} hat keine Source-Konfiguration")
                
                if stream.find('.//target') is None:
                    errors.append(f"Stream {i+1} hat keine Target-Konfiguration")
            
            # Pretty format check
            try:
                formatted = minidom.parseString(xml_string).toprettyxml(indent="  ")
                if len(formatted.split('\n')) < 10:
                    warnings.append("XML könnte besser formatiert sein")
            except:
                warnings.append("XML-Formatierung könnte verbessert werden")
                
        except ET.ParseError as e:
            errors.append(f"XML Parse Error: {str(e)}")
        except Exception as e:
            errors.append(f"Validierung fehlgeschlagen: {str(e)}")
        
        return ValidationResult(
            isValid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod 
    def format_xml(xml_string: str) -> str:
        """Format XML for better readability"""
        try:
            dom = minidom.parseString(xml_string)
            pretty_xml = dom.toprettyxml(indent="  ")
            # Remove extra blank lines
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            return '\n'.join(lines[1:])  # Skip XML declaration duplicate
        except:
            return xml_string

@router.post("/generate-from-chat", response_model=XMLGenerationResponse)
async def generate_xml_from_chat(
    request: XMLChatRequest,
    db: AsyncSession = Depends(get_db)
) -> XMLGenerationResponse:
    """Generate XML from natural language chat input"""
    
    try:
        # Build enhanced prompt
        system_prompt = XMLStreamWorksService.get_streamworks_system_prompt()
        user_prompt = f"""Benutzeranfrage: {request.prompt}

Erstelle eine vollständige StreamWorks XML-Konfiguration basierend auf dieser Anfrage. 
Das XML soll production-ready sein mit allen notwendigen Elementen."""

        # Generate XML using Mistral
        xml_content = await mistral_llm_service.generate_german_response(
            user_message=user_prompt,
            context=system_prompt,
            fast_mode=False,
            use_cache=True
        )
        
        # Extract XML from response (remove markdown code blocks if present)
        xml_content = re.sub(r'```xml\s*', '', xml_content)
        xml_content = re.sub(r'```\s*$', '', xml_content)
        xml_content = xml_content.strip()
        
        # Add XML declaration if missing
        if not xml_content.startswith('<?xml'):
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_content
        
        # Format XML
        formatted_xml = XMLStreamWorksService.format_xml(xml_content)
        
        # Validate XML
        validation = XMLStreamWorksService.validate_xml(formatted_xml)
        
        return XMLGenerationResponse(
            xml=formatted_xml,
            validation=validation,
            metadata={
                "generation_method": "chat",
                "timestamp": datetime.now().isoformat(),
                "prompt_length": len(request.prompt),
                "model": "mistral-7b"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"XML generation failed: {str(e)}"
        )

@router.post("/generate-from-form", response_model=XMLGenerationResponse)
async def generate_xml_from_form(
    request: XMLFormRequest,
    db: AsyncSession = Depends(get_db)
) -> XMLGenerationResponse:
    """Generate XML from structured form input"""
    
    try:
        # Build prompt from form data
        system_prompt = XMLStreamWorksService.get_streamworks_system_prompt()
        user_prompt = XMLStreamWorksService.generate_form_prompt(request)
        
        # Generate XML using Mistral
        xml_content = await mistral_llm_service.generate_german_response(
            user_message=user_prompt,
            context=system_prompt,
            fast_mode=False,
            use_cache=True
        )
        
        # Clean and format XML
        xml_content = re.sub(r'```xml\s*', '', xml_content)
        xml_content = re.sub(r'```\s*$', '', xml_content)
        xml_content = xml_content.strip()
        
        if not xml_content.startswith('<?xml'):
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_content
            
        formatted_xml = XMLStreamWorksService.format_xml(xml_content)
        
        # Validate XML
        validation = XMLStreamWorksService.validate_xml(formatted_xml)
        
        return XMLGenerationResponse(
            xml=formatted_xml,
            validation=validation,
            metadata={
                "generation_method": "form",
                "timestamp": datetime.now().isoformat(),
                "stream_name": request.streamName,
                "source_system": request.sourceSystem,
                "target_system": request.targetSystem,
                "model": "mistral-7b"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"XML generation failed: {str(e)}"
        )

@router.post("/generate-from-template", response_model=XMLGenerationResponse)
async def generate_xml_from_template(
    request: XMLTemplateRequest
) -> XMLGenerationResponse:
    """Generate XML from predefined template"""
    
    try:
        # Get template
        template = xml_template_service.get_template_by_id(request.template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template '{request.template_id}' not found"
            )
        
        # Render template with parameters
        xml_content = template.render(request.parameters)
        
        # Format XML
        formatted_xml = XMLStreamWorksService.format_xml(xml_content)
        
        # Validate XML
        validation = XMLStreamWorksService.validate_xml(formatted_xml)
        
        return XMLGenerationResponse(
            xml=formatted_xml,
            validation=validation,
            metadata={
                "generation_method": "template",
                "timestamp": datetime.now().isoformat(),
                "template_id": request.template_id,
                "template_name": template.name,
                "parameters": request.parameters,
                "model": "template-engine"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Template XML generation failed: {str(e)}"
        )

@router.post("/validate", response_model=ValidationResult)
async def validate_xml(xml_content: str) -> ValidationResult:
    """Validate XML content"""
    return XMLStreamWorksService.validate_xml(xml_content)

@router.get("/templates")
async def get_xml_templates():
    """Get available XML templates"""
    try:
        templates = xml_template_service.get_all_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load templates: {str(e)}"
        )

@router.post("/reload-templates")
async def reload_templates():
    """Reload XML templates from filesystem"""
    try:
        count = xml_template_service.reload_templates()
        return {
            "status": "success",
            "message": f"Reloaded {count} templates",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload templates: {str(e)}"
        )

@router.get("/health")
async def xml_health_check():
    """Health check for XML generation service"""
    try:
        # Test Mistral connection
        test_response = await mistral_llm_service.generate_german_response(
            user_message="Generate a simple XML element",
            context="",
            fast_mode=True,
            use_cache=False
        )
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "mistral_available": bool(test_response),
            "template_count": len(xml_template_service.templates),
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }