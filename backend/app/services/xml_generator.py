"""
Professional XML Generator Service with Template System
Replaces mock implementation with real template-based generation and validation
"""
import os
import logging
from typing import Dict, Optional, Any, List
from pathlib import Path
from datetime import datetime
import re

from app.core.config import settings
from app.services.xml_templates import XMLTemplateLoader, XMLValidator, schedule_to_cron, detect_stream_type
from app.services.error_handler import error_handler, ErrorType

logger = logging.getLogger(__name__)

class XMLGenerationError(Exception):
    """Custom exception for XML generation errors"""
    pass

class XMLValidationError(Exception):
    """Custom exception for XML validation errors"""
    pass

class XMLGeneratorService:
    """Professional XML Generation Service with Template System"""
    
    def __init__(self):
        self.template_loader = None
        self.validator = None
        self.is_initialized = False
        self.generation_stats = {
            "total_generated": 0,
            "successful_validations": 0,
            "template_fallbacks": 0,
            "validation_warnings": 0,
            "last_generation": None
        }
        
        logger.info("🔧 XML Generator Service initialisiert (Template-based)")
    
    def _ensure_directory_structure(self):
        """Ensure required directories exist"""
        try:
            # Use backend directory as root
            backend_dir = Path(__file__).parent.parent.parent
            templates_dir = backend_dir / "data" / "xml_templates"
            templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Create examples if directory is empty
            if not any(templates_dir.glob("*.xml")):
                self._create_example_templates(templates_dir)
                
            return templates_dir
        except Exception as e:
            logger.warning(f"Could not create templates directory: {e}")
            # Return fallback directory
            return Path(__file__).parent.parent / "data" / "xml_templates"
    
    def _create_example_templates(self, templates_dir: Path):
        """Create example template files"""
        try:
            # Simple data processing example
            simple_template = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Example StreamWorks Template - Data Processing -->
<stream xmlns="http://streamworks.arvato.com/schema/v1">
  <metadata>
    <name>{{ stream_name }}</name>
    <description>{{ description | default('Data processing stream') }}</description>
    <version>1.0</version>
    <created>{{ current_timestamp }}</created>
    <author>StreamWorks-KI</author>
  </metadata>
  
  <configuration>
    <schedule>
      <cron>{{ cron_expression | default('0 2 * * *') }}</cron>
      <timezone>Europe/Berlin</timezone>
    </schedule>
  </configuration>
  
  <pipeline>
    <tasks>
      <task id="process" type="data_processing">
        <name>Process Data</name>
        <source>{{ data_source | default('/data/input') }}</source>
        <target>{{ output_path | default('/data/output') }}</target>
      </task>
    </tasks>
  </pipeline>
</stream>'''
            
            with open(templates_dir / "simple_processing.xml", 'w', encoding='utf-8') as f:
                f.write(simple_template)
            
            logger.info("📄 Created example template: simple_processing.xml")
            
        except Exception as e:
            logger.warning(f"Could not create example templates: {e}")
    
    async def initialize(self):
        """Initialize XML Generator with Template System"""
        try:
            logger.info("🚀 XML Generator wird initialisiert (Template System)...")
            
            # Ensure directory structure
            templates_dir = self._ensure_directory_structure()
            
            # Initialize template loader
            self.template_loader = XMLTemplateLoader(templates_dir)
            
            # Initialize validator
            self.validator = XMLValidator()
            
            # Test template loading
            templates = await self.template_loader.list_templates()
            logger.info(f"📄 Loaded {len(templates)} XML templates")
            
            # Log available templates
            for template in templates:
                logger.info(f"  - {template.name} ({template.category}): {template.description}")
            
            self.is_initialized = True
            logger.info("✅ XML Generator initialisiert mit Template System")
            
        except Exception as e:
            logger.error(f"❌ XML Generator Initialisierung fehlgeschlagen: {e}")
            self.is_initialized = False
            
            # Graceful fallback - create minimal template loader
            try:
                self.template_loader = XMLTemplateLoader()
                self.validator = XMLValidator()
                self.is_initialized = True
                logger.warning("⚠️ XML Generator mit Basis-Templates initialisiert")
            except Exception as fallback_error:
                logger.error(f"❌ Fallback initialization failed: {fallback_error}")
                raise XMLGenerationError(f"Failed to initialize XML Generator: {fallback_error}")
    
    async def generate_stream(self, requirements: Dict) -> str:
        """Optimierte XML-Generierung für Chat-Mode"""
        return await self.generate_xml_stream(requirements)
    
    async def generate_xml_stream(self, requirements: Dict) -> str:
        """Generate XML stream using template system with validation"""
        try:
            # Ensure initialization
            if not self.is_initialized:
                await self.initialize()
            
            # Validate input requirements
            if not requirements:
                raise XMLGenerationError("No requirements provided for XML generation")
            
            stream_name = requirements.get('name', f"Stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"📝 Generiere XML für: {stream_name}")
            
            # Detect appropriate template type
            template_type = detect_stream_type(requirements)
            logger.info(f"🎯 Detected template type: {template_type}")
            
            # Get template
            template = await self.template_loader.get_template(template_type)
            
            # Validate requirements against template
            is_valid, missing_fields = template.validate_requirements(requirements)
            if not is_valid:
                logger.warning(f"⚠️ Missing required fields: {missing_fields}")
                # Fill in defaults for missing fields
                requirements = self._fill_missing_requirements(requirements, missing_fields, template_type)
            
            # Prepare template variables
            template_vars = self._prepare_template_variables(requirements)
            
            # Generate XML using template
            xml_content = template.render(**template_vars)
            
            # Validate generated XML
            validation_result = await self.validator.validate(xml_content)
            
            if not validation_result.is_valid:
                logger.warning(f"⚠️ XML validation errors: {validation_result.errors}")
                raise XMLValidationError(f"Generated XML is invalid: {validation_result.errors}")
            
            # Log warnings but continue
            if validation_result.warnings:
                self.generation_stats["validation_warnings"] += 1
                for warning in validation_result.warnings:
                    logger.info(f"💡 XML Warning: {warning}")
            
            # Update statistics
            self.generation_stats["total_generated"] += 1
            self.generation_stats["successful_validations"] += 1
            self.generation_stats["last_generation"] = datetime.now().isoformat()
            
            logger.info(f"✅ XML Stream erfolgreich generiert und validiert ({len(xml_content)} chars)")
            return xml_content
            
        except XMLGenerationError:
            raise
        except XMLValidationError:
            raise
        except Exception as e:
            logger.error(f"❌ XML Generation fehlgeschlagen: {e}")
            
            # Use error handler for graceful fallback
            try:
                fallback_response = await error_handler.handle_xml_error(e, {"requirements": requirements})
                
                # Extract XML from fallback response if available
                if "```xml" in fallback_response.message:
                    xml_match = re.search(r'```xml\n(.*?)\n```', fallback_response.message, re.DOTALL)
                    if xml_match:
                        self.generation_stats["template_fallbacks"] += 1
                        logger.info("🔧 Using fallback XML from error handler")
                        return xml_match.group(1)
                
                # Ultimate fallback - use enhanced mock
                self.generation_stats["template_fallbacks"] += 1
                logger.info("🔧 Using enhanced mock XML as final fallback")
                return self._generate_mock_xml_enhanced(requirements)
                
            except Exception as fallback_error:
                logger.error(f"❌ Even fallback failed: {fallback_error}")
                raise XMLGenerationError(f"XML generation completely failed: {e}")
    
    def _fill_missing_requirements(self, requirements: Dict, missing_fields: List[str], template_type: str) -> Dict:
        """Fill in missing required fields with sensible defaults"""
        filled_requirements = requirements.copy()
        
        defaults = {
            "stream_name": f"Stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "data_source": "/data/input",
            "output_path": "/data/output", 
            "description": f"Auto-generated {template_type.replace('_', ' ')} stream",
            "schedule": "daily",
            "cron_expression": "0 2 * * *",
            "batch_command": "echo 'Please configure batch command'",
            "api_url": "https://api.example.com/data"
        }
        
        for field in missing_fields:
            if field in defaults:
                filled_requirements[field] = defaults[field]
                logger.info(f"🔧 Using default for {field}: {defaults[field]}")
            else:
                logger.warning(f"⚠️ No default available for required field: {field}")
        
        return filled_requirements
    
    def _prepare_template_variables(self, requirements: Dict) -> Dict[str, Any]:
        """Prepare variables for template rendering"""
        variables = {}
        
        # Direct mapping
        direct_fields = [
            'stream_name', 'name', 'description', 'data_source', 'output_path',
            'batch_command', 'api_url', 'working_dir', 'memory', 'timeout'
        ]
        
        for field in direct_fields:
            if field in requirements:
                # Map 'name' to 'stream_name' for templates
                target_field = 'stream_name' if field == 'name' else field
                variables[target_field] = requirements[field]
        
        # Handle schedule conversion
        if 'schedule' in requirements:
            schedule = requirements['schedule']
            variables['cron_expression'] = schedule_to_cron(schedule)
            variables['schedule_description'] = schedule
        
        # Handle environment variables
        if 'env_variables' in requirements:
            variables['env_variables'] = requirements['env_variables']
        elif 'environment' in requirements:
            variables['env_variables'] = requirements['environment']
        else:
            variables['env_variables'] = {}
        
        # Handle custom parameters
        if 'parameters' in requirements:
            variables['job_parameters'] = [
                {"name": k, "value": v} for k, v in requirements['parameters'].items()
            ]
        
        # Handle API specific fields
        if 'headers' in requirements:
            variables['api_headers'] = [
                {"name": k, "value": v} for k, v in requirements['headers'].items()
            ]
        
        if 'auth_token' in requirements:
            variables['api_token'] = requirements['auth_token']
        
        # Set defaults for common optional fields
        defaults = {
            'timezone': 'Europe/Berlin',
            'log_level': 'INFO',
            'encoding': 'UTF-8',
            'file_pattern': '*.csv',
            'output_format': 'csv',
            'backup_enabled': 'true',
            'retention_days': '30',
            'email_notifications': 'true',
            'notify_failure': 'true',
            'notify_success': 'false',
            'retry_attempts': '3'
        }
        
        for key, default_value in defaults.items():
            if key not in variables:
                variables[key] = default_value
        
        # Handle custom transformations
        if 'transformations' in requirements:
            transformations = requirements['transformations']
            if isinstance(transformations, list):
                variables['custom_transformations'] = transformations
            else:
                variables['custom_transformations'] = []
        else:
            variables['custom_transformations'] = []
        
        # Handle custom environment variables
        if 'custom_env_vars' not in variables:
            variables['custom_env_vars'] = {}
        
        # Ensure we have required fields
        if 'stream_name' not in variables:
            variables['stream_name'] = f"Stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🔧 Prepared {len(variables)} template variables")
        return variables
    
    def _generate_mock_xml_enhanced(self, requirements: Dict) -> str:
        """Enhanced mock XML generation as final fallback"""
        name = requirements.get("name", requirements.get("stream_name", "FallbackStream"))
        schedule = requirements.get("schedule", "daily")
        source = requirements.get("source", requirements.get("data_source", "/data/input"))
        target = requirements.get("target", requirements.get("output_path", "/data/output"))
        description = requirements.get("description", "Fallback stream generated due to template error")
        
        # Determine cron expression based on schedule
        cron_expressions = {
            "hourly": "0 * * * *",
            "daily": "0 2 * * *",
            "weekly": "0 2 * * 0",
            "monthly": "0 2 1 * *"
        }
        cron = cron_expressions.get(schedule, "0 2 * * *")
        
        timestamp = datetime.now().isoformat()
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<stream xmlns="http://streamworks.arvato.com/schema/v1">
  <metadata>
    <name>{name}</name>
    <description>{description}</description>
    <version>1.0</version>
    <created>{timestamp}</created>
    <author>StreamWorks-KI-Fallback</author>
    <category>fallback</category>
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
  </configuration>
  
  <pipeline>
    <tasks>
      <task id="input" type="file_input">
        <name>Data Input</name>
        <source>{source}</source>
        <pattern>*.csv</pattern>
        <encoding>UTF-8</encoding>
      </task>
      
      <task id="process" type="data_processing" depends_on="input">
        <name>Data Processing</name>
        <note>Please customize processing steps</note>
      </task>
      
      <task id="output" type="file_output" depends_on="process">
        <name>Data Output</name>
        <target>{target}</target>
        <format>csv</format>
      </task>
    </tasks>
    
    <flow>
      <start>input</start>
      <sequence>
        <step>input</step>
        <step>process</step>
        <step>output</step>
      </sequence>
    </flow>
  </pipeline>
  
  <monitoring>
    <logging>
      <level>INFO</level>
      <output>/logs/streams/{name}.log</output>
    </logging>
    
    <notifications>
      <email>
        <enabled>true</enabled>
        <on_failure>true</on_failure>
      </email>
    </notifications>
  </monitoring>
  
  <error_handling>
    <global_retry>
      <max_attempts>3</max_attempts>
      <backoff_strategy>exponential</backoff_strategy>
    </global_retry>
  </error_handling>
</stream>'''
    
    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available templates"""
        if not self.is_initialized:
            await self.initialize()
        
        templates = await self.template_loader.list_templates()
        return [
            {
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "required_fields": template.required_fields,
                "created_at": template.created_at.isoformat()
            }
            for template in templates
        ]
    
    async def validate_xml(self, xml_content: str) -> Dict[str, Any]:
        """Validate XML content and return validation result"""
        if not self.is_initialized:
            await self.initialize()
        
        validation_result = await self.validator.validate(xml_content)
        return validation_result.to_dict()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get XML Generator statistics"""
        return {
            "status": "healthy" if self.is_initialized else "not_initialized",
            "xml_generation_enabled": True,
            "mode": "template_based",
            "generation_method": "professional_templates",
            "statistics": self.generation_stats,
            "templates_loaded": len(self.template_loader.templates) if self.template_loader else 0,
            "last_check": datetime.now().isoformat()
        }
    
    async def reset_stats(self):
        """Reset generation statistics"""
        self.generation_stats = {
            "total_generated": 0,
            "successful_validations": 0,
            "template_fallbacks": 0,
            "validation_warnings": 0,
            "last_generation": None
        }
        logger.info("🧹 XML Generator statistics reset")

# Global instance
xml_generator = XMLGeneratorService()