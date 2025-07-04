"""
XML Templates Helper Functions
Extracted from deleted xml_templates.py to support xml_generator.py
"""
import re
import logging
from typing import Dict, Optional, Any, List, NamedTuple
from pathlib import Path
from datetime import datetime

class TemplateInfo(NamedTuple):
    """Template information structure"""
    name: str
    category: str
    description: str
    path: Optional[str] = None

logger = logging.getLogger(__name__)

def schedule_to_cron(schedule_text: str) -> str:
    """Convert human-readable schedule to cron expression"""
    schedule_lower = schedule_text.lower().strip()
    
    # Pre-defined mappings
    cron_mappings = {
        "täglich": "0 2 * * *",
        "daily": "0 2 * * *",
        "stündlich": "0 * * * *", 
        "hourly": "0 * * * *",
        "wöchentlich": "0 2 * * 0",
        "weekly": "0 2 * * 0",
        "monatlich": "0 2 1 * *",
        "monthly": "0 2 1 * *"
    }
    
    # Check direct mappings
    if schedule_lower in cron_mappings:
        return cron_mappings[schedule_lower]
    
    # Parse time patterns
    time_patterns = [
        (r"um (\d{1,2}):(\d{2})", lambda m: f"{m.group(2)} {m.group(1)} * * *"),
        (r"um (\d{1,2}) uhr", lambda m: f"0 {m.group(1)} * * *"),
        (r"alle (\d+) stunden", lambda m: f"0 */{m.group(1)} * * *"),
        (r"every (\d+) hours", lambda m: f"0 */{m.group(1)} * * *")
    ]
    
    for pattern, formatter in time_patterns:
        match = re.search(pattern, schedule_lower)
        if match:
            return formatter(match)
    
    # Default fallback
    return "0 2 * * *"

def detect_stream_type(description: str, requirements: Dict[str, Any]) -> str:
    """Detect the most appropriate stream type based on description and requirements"""
    description_lower = description.lower()
    
    # Priority order detection
    if any(keyword in description_lower for keyword in ['api', 'rest', 'webservice', 'endpoint']):
        return 'api_integration'
    elif any(keyword in description_lower for keyword in ['batch', 'script', 'command', 'powershell', 'bash']):
        return 'batch_processing'
    elif any(keyword in description_lower for keyword in ['csv', 'excel', 'database', 'sql', 'data']):
        return 'data_processing'
    elif any(keyword in description_lower for keyword in ['file', 'folder', 'directory', 'copy', 'move']):
        return 'file_processing'
    else:
        return 'data_processing'  # Default

class XMLTemplateLoader:
    """Loads and manages XML templates"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir is None:
            # Default fallback directory
            backend_dir = Path(__file__).parent.parent.parent
            templates_dir = backend_dir / "data" / "xml_templates"
            templates_dir.mkdir(parents=True, exist_ok=True)
            
        self.templates_dir = templates_dir
        self.templates = {}
        self.template_info = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all XML templates from directory"""
        try:
            if not self.templates_dir.exists():
                logger.warning(f"Templates directory does not exist: {self.templates_dir}")
                # Create basic template
                self._create_basic_template()
                return
            
            for template_file in self.templates_dir.glob("*.xml"):
                try:
                    template_name = template_file.stem
                    with open(template_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.templates[template_name] = content
                    
                    # Extract template info from content
                    description = self._extract_description(content)
                    category = self._extract_category(template_name, content)
                    
                    self.template_info[template_name] = TemplateInfo(
                        name=template_name,
                        category=category,
                        description=description,
                        path=str(template_file)
                    )
                    
                    logger.debug(f"Loaded template: {template_name}")
                except Exception as e:
                    logger.warning(f"Failed to load template {template_file}: {e}")
            
            # Create basic template if none exist
            if not self.templates:
                self._create_basic_template()
            
            logger.info(f"Loaded {len(self.templates)} XML templates")
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            self._create_basic_template()
    
    def _extract_description(self, content: str) -> str:
        """Extract description from XML comment"""
        import re
        # Look for comment with description
        match = re.search(r'<!--\s*(.+?)\s*-->', content, re.DOTALL)
        if match:
            return match.group(1).strip()[:100]  # Limit length
        return "XML template for StreamWorks"
    
    def _extract_category(self, name: str, content: str) -> str:
        """Extract category from template name and content"""
        name_lower = name.lower()
        content_lower = content.lower()
        
        if 'simple' in name_lower or 'basic' in name_lower:
            return 'basic'
        elif 'batch' in name_lower or 'batch' in content_lower:
            return 'batch'
        elif 'data' in name_lower or 'processing' in content_lower:
            return 'data_processing'
        elif 'api' in content_lower:
            return 'api'
        else:
            return 'general'
    
    def _create_basic_template(self):
        """Create a basic template as fallback"""
        basic_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Basic StreamWorks Template -->
<stream xmlns="http://streamworks.arvato.com/schema/v1">
  <metadata>
    <name>{{ stream_name | default('Default Stream') }}</name>
    <description>{{ description | default('Basic stream configuration') }}</description>
    <version>1.0</version>
    <created>{{ current_timestamp }}</created>
  </metadata>
  
  <configuration>
    <schedule>
      <cron>{{ cron_expression | default('0 2 * * *') }}</cron>
      <timezone>Europe/Berlin</timezone>
    </schedule>
  </configuration>
  
  <pipeline>
    <tasks>
      <task id="process" type="basic">
        <name>Basic Processing</name>
        <source>{{ data_source | default('/data/input') }}</source>
        <target>{{ output_path | default('/data/output') }}</target>
      </task>
    </tasks>
  </pipeline>
</stream>'''
        
        self.templates['basic'] = basic_content
        self.template_info['basic'] = TemplateInfo(
            name='basic',
            category='basic',
            description='Basic StreamWorks template',
            path=None
        )
        logger.info("Created basic fallback template")
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Get template by name"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[TemplateInfo]:
        """List all available templates with info"""
        return list(self.template_info.values())
    
    def get_template_names(self) -> List[str]:
        """Get simple list of template names"""
        return list(self.templates.keys())

class XMLValidator:
    """Validates XML content"""
    
    def validate(self, xml_content: str) -> Dict[str, Any]:
        """Validate XML content"""
        try:
            import xml.etree.ElementTree as ET
            
            # Try to parse XML
            ET.fromstring(xml_content)
            
            return {
                "valid": True,
                "errors": [],
                "warnings": []
            }
        except ET.ParseError as e:
            return {
                "valid": False,
                "errors": [f"XML Parse Error: {e}"],
                "warnings": []
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation Error: {e}"],
                "warnings": []
            }