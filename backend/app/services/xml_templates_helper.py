"""
XML Templates Helper Functions
Extracted from deleted xml_templates.py to support xml_generator.py
"""
import re
import logging
from typing import Dict, Optional, Any, List
from pathlib import Path
from datetime import datetime

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
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all XML templates from directory"""
        try:
            if not self.templates_dir.exists():
                logger.warning(f"Templates directory does not exist: {self.templates_dir}")
                return
            
            for template_file in self.templates_dir.glob("*.xml"):
                try:
                    template_name = template_file.stem
                    with open(template_file, 'r', encoding='utf-8') as f:
                        self.templates[template_name] = f.read()
                    logger.debug(f"Loaded template: {template_name}")
                except Exception as e:
                    logger.warning(f"Failed to load template {template_file}: {e}")
            
            logger.info(f"Loaded {len(self.templates)} XML templates")
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Get template by name"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """List all available template names"""
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