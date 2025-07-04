"""
XML Template System for StreamWorks-KI
Professional XML generation with validation and templates
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class XMLTemplate:
    """Represents an XML template"""
    
    def __init__(self, name: str, template_content: str, description: str, 
                 category: str = "general", required_fields: List[str] = None):
        self.name = name
        self.template_content = template_content
        self.description = description
        self.category = category
        self.required_fields = required_fields or []
        self.created_at = datetime.now()
    
    def render(self, **kwargs) -> str:
        """Render template with provided variables"""
        template = Template(self.template_content)
        
        # Add default values
        context = {
            'current_timestamp': datetime.now().isoformat(),
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'author': 'StreamWorks-KI',
            'version': '1.0',
            **kwargs
        }
        
        return template.render(**context)
    
    def validate_requirements(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate that all required fields are present"""
        missing_fields = []
        for field in self.required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields

class XMLTemplateLoader:
    """Loads and manages XML templates"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "data" / "xml_templates"
        self.templates: Dict[str, XMLTemplate] = {}
        self._load_builtin_templates()
        self._load_file_templates()
    
    def _load_builtin_templates(self):
        """Load built-in XML templates"""
        
        # Data Processing Stream Template
        data_processing_template = """<?xml version="1.0" encoding="UTF-8"?>
<stream xmlns="http://streamworks.arvato.com/schema/v1">
  <metadata>
    <name>{{ stream_name }}</name>
    <description>{{ description | default('Automated data processing stream') }}</description>
    <version>{{ version }}</version>
    <created>{{ current_timestamp }}</created>
    <author>{{ author }}</author>
    <category>data-processing</category>
  </metadata>
  
  <configuration>
    <schedule>
      <cron>{{ cron_expression | default('0 2 * * *') }}</cron>
      <timezone>{{ timezone | default('Europe/Berlin') }}</timezone>
      <enabled>true</enabled>
    </schedule>
    
    <resources>
      <memory>{{ memory | default('512MB') }}</memory>
      <timeout>{{ timeout | default('3600') }}</timeout>
      <retry_attempts>{{ retry_attempts | default('3') }}</retry_attempts>
    </resources>
    
    <environment>
      <variables>
        <var name="SOURCE_PATH">{{ data_source }}</var>
        <var name="TARGET_PATH">{{ output_path }}</var>
        <var name="LOG_LEVEL">{{ log_level | default('INFO') }}</var>
        {% for key, value in custom_env_vars.items() if custom_env_vars %}
        <var name="{{ key }}">{{ value }}</var>
        {% endfor %}
      </variables>
    </environment>
  </configuration>
  
  <pipeline>
    <tasks>
      <task id="input" type="file_input">
        <name>Dateneingang</name>
        <source>{{ data_source }}</source>
        <pattern>{{ file_pattern | default('*.csv') }}</pattern>
        <encoding>{{ encoding | default('UTF-8') }}</encoding>
        <validation>
          <required>{{ input_required | default('true') }}</required>
          <schema_check>{{ schema_check | default('enabled') }}</schema_check>
        </validation>
      </task>
      
      <task id="validate" type="data_validation" depends_on="input">
        <name>Datenvalidierung</name>
        <rules>
          <check_empty_fields>{{ check_empty | default('true') }}</check_empty_fields>
          <check_data_types>{{ check_types | default('true') }}</check_data_types>
          <check_duplicates>{{ check_duplicates | default('true') }}</check_duplicates>
        </rules>
        <on_error>
          <action>{{ error_action | default('quarantine') }}</action>
          <notify>{{ error_notify | default('true') }}</notify>
        </on_error>
      </task>
      
      <task id="transform" type="data_transform" depends_on="validate">
        <name>Datentransformation</name>
        <transformations>
          <normalize_encoding>{{ normalize_encoding | default('true') }}</normalize_encoding>
          <standardize_format>{{ standardize_format | default('true') }}</standardize_format>
          <add_timestamp>{{ add_timestamp | default('true') }}</add_timestamp>
          {% if custom_transformations %}
          {% for transform in custom_transformations %}
          <{{ transform.type }}>{{ transform.value | default('true') }}</{{ transform.type }}>
          {% endfor %}
          {% endif %}
        </transformations>
      </task>
      
      <task id="output" type="file_output" depends_on="transform">
        <name>Datenausgang</name>
        <target>{{ output_path }}</target>
        <format>{{ output_format | default('csv') }}</format>
        <compression>{{ compression | default('none') }}</compression>
        <backup>
          <enabled>{{ backup_enabled | default('true') }}</enabled>
          <retention_days>{{ retention_days | default('30') }}</retention_days>
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
      <level>{{ log_level | default('INFO') }}</level>
      <output>/logs/streams/{{ stream_name }}.log</output>
      <rotate>{{ log_rotate | default('daily') }}</rotate>
    </logging>
    
    <notifications>
      <email>
        <enabled>{{ email_notifications | default('true') }}</enabled>
        <recipients>{{ email_recipients | default('admin@company.com') }}</recipients>
        <on_success>{{ notify_success | default('false') }}</on_success>
        <on_failure>{{ notify_failure | default('true') }}</on_failure>
      </email>
      
      <metrics>
        <enabled>{{ metrics_enabled | default('true') }}</enabled>
        <export_interval>{{ metrics_interval | default('300') }}</export_interval>
      </metrics>
    </notifications>
  </monitoring>
  
  <error_handling>
    <global_retry>
      <max_attempts>{{ max_retry_attempts | default('3') }}</max_attempts>
      <backoff_strategy>{{ backoff_strategy | default('exponential') }}</backoff_strategy>
    </global_retry>
    
    <fallback>
      <enabled>{{ fallback_enabled | default('true') }}</enabled>
      <action>{{ fallback_action | default('notify_and_stop') }}</action>
    </fallback>
  </error_handling>
</stream>"""
        
        self.templates["data_processing"] = XMLTemplate(
            name="data_processing",
            template_content=data_processing_template,
            description="Standard data processing stream with validation and transformation",
            category="data-processing",
            required_fields=["stream_name", "data_source", "output_path"]
        )
        
        # Batch Job Template
        batch_job_template = """<?xml version="1.0" encoding="UTF-8"?>
<stream xmlns="http://streamworks.arvato.com/schema/v1">
  <metadata>
    <name>{{ stream_name }}</name>
    <description>{{ description | default('Automated batch job execution') }}</description>
    <version>{{ version }}</version>
    <created>{{ current_timestamp }}</created>
    <author>{{ author }}</author>
    <category>batch-job</category>
  </metadata>
  
  <configuration>
    <schedule>
      <cron>{{ cron_expression | default('0 2 * * *') }}</cron>
      <timezone>{{ timezone | default('Europe/Berlin') }}</timezone>
      <enabled>true</enabled>
    </schedule>
    
    <resources>
      <memory>{{ memory | default('1024MB') }}</memory>
      <timeout>{{ timeout | default('7200') }}</timeout>
      <retry_attempts>{{ retry_attempts | default('2') }}</retry_attempts>
    </resources>
  </configuration>
  
  <pipeline>
    <tasks>
      <task id="batch_execution" type="batch_job">
        <name>{{ job_name | default('Batch Job Execution') }}</name>
        <command>{{ batch_command }}</command>
        <working_directory>{{ working_dir | default('/opt/batch') }}</working_directory>
        <environment>
          {% for key, value in env_variables.items() if env_variables %}
          <var name="{{ key }}">{{ value }}</var>
          {% endfor %}
        </environment>
        <parameters>
          {% for param in job_parameters if job_parameters %}
          <param name="{{ param.name }}">{{ param.value }}</param>
          {% endfor %}
        </parameters>
      </task>
    </tasks>
  </pipeline>
  
  <monitoring>
    <logging>
      <level>{{ log_level | default('INFO') }}</level>
      <output>/logs/batch/{{ stream_name }}.log</output>
    </logging>
    
    <notifications>
      <email>
        <enabled>{{ email_notifications | default('true') }}</enabled>
        <recipients>{{ email_recipients | default('admin@company.com') }}</recipients>
        <on_success>{{ notify_success | default('true') }}</on_success>
        <on_failure>{{ notify_failure | default('true') }}</on_failure>
      </email>
    </notifications>
  </monitoring>
</stream>"""
        
        self.templates["batch_job"] = XMLTemplate(
            name="batch_job",
            template_content=batch_job_template,
            description="Batch job execution stream with monitoring",
            category="batch-processing",
            required_fields=["stream_name", "batch_command"]
        )
        
        # API Integration Template
        api_integration_template = """<?xml version="1.0" encoding="UTF-8"?>
<stream xmlns="http://streamworks.arvato.com/schema/v1">
  <metadata>
    <name>{{ stream_name }}</name>
    <description>{{ description | default('API integration and data synchronization') }}</description>
    <version>{{ version }}</version>
    <created>{{ current_timestamp }}</created>
    <author>{{ author }}</author>
    <category>api-integration</category>
  </metadata>
  
  <configuration>
    <schedule>
      <cron>{{ cron_expression | default('0 */6 * * *') }}</cron>
      <timezone>{{ timezone | default('Europe/Berlin') }}</timezone>
      <enabled>true</enabled>
    </schedule>
    
    <resources>
      <memory>{{ memory | default('256MB') }}</memory>
      <timeout>{{ timeout | default('1800') }}</timeout>
      <retry_attempts>{{ retry_attempts | default('3') }}</retry_attempts>
    </resources>
  </configuration>
  
  <pipeline>
    <tasks>
      <task id="api_call" type="http_request">
        <name>API Data Retrieval</name>
        <url>{{ api_url }}</url>
        <method>{{ http_method | default('GET') }}</method>
        <headers>
          {% for header in api_headers if api_headers %}
          <header name="{{ header.name }}">{{ header.value }}</header>
          {% endfor %}
        </headers>
        <authentication>
          <type>{{ auth_type | default('bearer') }}</type>
          <token>{{ api_token | default('${API_TOKEN}') }}</token>
        </authentication>
        <timeout>{{ request_timeout | default('30') }}</timeout>
      </task>
      
      <task id="process_response" type="data_transform" depends_on="api_call">
        <name>Response Processing</name>
        <input_format>{{ input_format | default('json') }}</input_format>
        <output_format>{{ output_format | default('json') }}</output_format>
        <transformations>
          {% for transform in data_transformations if data_transformations %}
          <{{ transform.type }}>{{ transform.config }}</{{ transform.type }}>
          {% endfor %}
        </transformations>
      </task>
      
      <task id="store_data" type="data_output" depends_on="process_response">
        <name>Data Storage</name>
        <target>{{ output_path }}</target>
        <format>{{ storage_format | default('json') }}</format>
      </task>
    </tasks>
  </pipeline>
  
  <monitoring>
    <logging>
      <level>{{ log_level | default('INFO') }}</level>
      <output>/logs/api/{{ stream_name }}.log</output>
    </logging>
    
    <notifications>
      <email>
        <enabled>{{ email_notifications | default('true') }}</enabled>
        <recipients>{{ email_recipients | default('admin@company.com') }}</recipients>
        <on_failure>{{ notify_failure | default('true') }}</on_failure>
      </email>
    </notifications>
  </monitoring>
</stream>"""
        
        self.templates["api_integration"] = XMLTemplate(
            name="api_integration",
            template_content=api_integration_template,
            description="API integration stream for data synchronization",
            category="api-integration",
            required_fields=["stream_name", "api_url", "output_path"]
        )
        
        logger.info(f"✅ Loaded {len(self.templates)} built-in XML templates")
    
    def _load_file_templates(self):
        """Load templates from files"""
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created templates directory: {self.templates_dir}")
            return
        
        template_files = list(self.templates_dir.glob("*.xml"))
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract metadata from XML comments or filename
                template_name = template_file.stem
                self.templates[template_name] = XMLTemplate(
                    name=template_name,
                    template_content=content,
                    description=f"Custom template: {template_name}",
                    category="custom"
                )
                logger.info(f"📄 Loaded custom template: {template_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load template {template_file}: {e}")
        
        logger.info(f"✅ Loaded {len(template_files)} custom templates from files")
    
    async def get_template(self, template_type: str) -> XMLTemplate:
        """Get template by type"""
        # Map common request types to templates
        type_mapping = {
            "data_processing": "data_processing",
            "batch": "batch_job",
            "batch_job": "batch_job",
            "api": "api_integration",
            "api_integration": "api_integration",
            "default": "data_processing"
        }
        
        template_name = type_mapping.get(template_type.lower(), "data_processing")
        
        if template_name not in self.templates:
            logger.warning(f"⚠️ Template '{template_name}' not found, using default")
            template_name = "data_processing"
        
        return self.templates[template_name]
    
    async def list_templates(self) -> List[XMLTemplate]:
        """List all available templates"""
        return list(self.templates.values())
    
    def get_template_by_category(self, category: str) -> List[XMLTemplate]:
        """Get templates by category"""
        return [t for t in self.templates.values() if t.category == category]

class XMLValidator:
    """Validates generated XML content"""
    
    def __init__(self):
        self.validation_patterns = [
            (r'<\?xml.*?\?>', "XML declaration"),
            (r'<stream.*?>', "Stream opening tag"),
            (r'</stream>', "Stream closing tag"),
            (r'<metadata>.*?</metadata>', "Metadata section"),
            (r'<configuration>.*?</configuration>', "Configuration section"),
            (r'<pipeline>.*?</pipeline>', "Pipeline section")
        ]
    
    async def validate(self, xml_content: str) -> 'XMLValidationResult':
        """Validate XML content"""
        errors = []
        warnings = []
        
        # Basic structure validation
        if not xml_content or len(xml_content.strip()) < 50:
            errors.append("XML content is too short or empty")
            return XMLValidationResult(False, errors, warnings)
        
        # Check for required patterns
        for pattern, description in self.validation_patterns:
            if not re.search(pattern, xml_content, re.DOTALL | re.IGNORECASE):
                if description in ["XML declaration", "Stream opening tag", "Stream closing tag"]:
                    errors.append(f"Missing required {description}")
                else:
                    warnings.append(f"Missing recommended {description}")
        
        # Check for well-formed XML structure
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(xml_content)
        except ET.ParseError as e:
            errors.append(f"XML parsing error: {str(e)}")
        except Exception as e:
            warnings.append(f"XML validation warning: {str(e)}")
        
        # Validate StreamWorks-specific requirements
        if '<name>' not in xml_content:
            errors.append("Stream name is required")
        
        if '<schedule>' not in xml_content:
            warnings.append("Schedule configuration is recommended")
        
        # Check for potential issues
        if xml_content.count('<task') > 10:
            warnings.append("High number of tasks may impact performance")
        
        if 'password' in xml_content.lower() or 'secret' in xml_content.lower():
            warnings.append("Potential sensitive data in XML - use environment variables")
        
        is_valid = len(errors) == 0
        return XMLValidationResult(is_valid, errors, warnings)

class XMLValidationResult:
    """Represents XML validation result"""
    
    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str]):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
        self.validated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "validated_at": self.validated_at.isoformat()
        }

# Utility functions
def schedule_to_cron(schedule_description: str) -> str:
    """Convert human-readable schedule to cron expression"""
    schedule_lower = schedule_description.lower().strip()
    
    cron_mapping = {
        "hourly": "0 * * * *",
        "every hour": "0 * * * *",
        "daily": "0 2 * * *",
        "every day": "0 2 * * *",
        "weekly": "0 2 * * 0",
        "every week": "0 2 * * 0",
        "monthly": "0 2 1 * *",
        "every month": "0 2 1 * *",
        "twice daily": "0 2,14 * * *",
        "every 6 hours": "0 */6 * * *",
        "every 4 hours": "0 */4 * * *",
        "every 2 hours": "0 */2 * * *",
        "every 30 minutes": "*/30 * * * *",
        "every 15 minutes": "*/15 * * * *"
    }
    
    # Check for exact matches first
    if schedule_lower in cron_mapping:
        return cron_mapping[schedule_lower]
    
    # Check for patterns like "at 3pm", "at 14:30"
    time_pattern = re.search(r'at (\d{1,2}):?(\d{0,2})\s*(am|pm)?', schedule_lower)
    if time_pattern:
        hour = int(time_pattern.group(1))
        minute = int(time_pattern.group(2)) if time_pattern.group(2) else 0
        period = time_pattern.group(3)
        
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        
        return f"{minute} {hour} * * *"
    
    # Default fallback
    logger.warning(f"Could not parse schedule '{schedule_description}', using daily at 2 AM")
    return "0 2 * * *"

def detect_stream_type(requirements: Dict[str, Any]) -> str:
    """Detect stream type from requirements"""
    description = str(requirements.get('description', '')).lower()
    name = str(requirements.get('name', '')).lower()
    source = str(requirements.get('data_source', '')).lower()
    
    # Check for API indicators
    if any(term in description + name for term in ['api', 'rest', 'http', 'endpoint', 'service']):
        return "api_integration"
    
    # Check for batch job indicators
    if any(term in description + name for term in ['batch', 'job', 'script', 'command', 'exec']):
        return "batch_job"
    
    # Default to data processing
    return "data_processing"