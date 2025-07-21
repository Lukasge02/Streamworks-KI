"""
StreamWorks XML Template Management Service
Enterprise-level template loading and management
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

class XMLTemplate:
    """Represents an XML template with metadata"""
    
    def __init__(self, template_id: str, name: str, description: str, category: str, file_path: str, xml_content: str):
        self.id = template_id
        self.name = name
        self.description = description
        self.category = category
        self.file_path = file_path
        self.xml_content = xml_content
        self.parameters = self._extract_parameters()
    
    def _extract_parameters(self) -> List[str]:
        """Extract template parameters like ${VARIABLE_NAME}"""
        import re
        parameters = re.findall(r'\$\{([^}]+)\}', self.xml_content)
        return list(set(parameters))  # Remove duplicates
    
    def render(self, parameters: Dict[str, str]) -> str:
        """Render template with provided parameters"""
        content = self.xml_content
        for param, value in parameters.items():
            content = content.replace(f"${{{param}}}", value)
        return content
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for API response"""
        return {
            "id": self.id,
            "name": self.name, 
            "description": self.description,
            "category": self.category,
            "parameters": self.parameters,
            "file_path": self.file_path
        }

class XMLTemplateService:
    """Service for managing XML templates"""
    
    def __init__(self, templates_directory: str = "app/templates/xml"):
        self.templates_directory = Path(templates_directory)
        self.templates: Dict[str, XMLTemplate] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all XML templates from the templates directory"""
        try:
            if not self.templates_directory.exists():
                logger.warning(f"Templates directory {self.templates_directory} does not exist")
                return
            
            for xml_file in self.templates_directory.glob("*.xml"):
                try:
                    template = self._load_template_from_file(xml_file)
                    self.templates[template.id] = template
                    logger.info(f"Loaded template: {template.id}")
                except Exception as e:
                    logger.error(f"Failed to load template from {xml_file}: {e}")
            
            logger.info(f"Loaded {len(self.templates)} XML templates")
            
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
    
    def _load_template_from_file(self, file_path: Path) -> XMLTemplate:
        """Load a single template from XML file"""
        # Read XML content
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Parse XML to extract metadata
        root = ET.fromstring(xml_content)
        metadata = root.find('.//{http://streamworks.arvato.com/v1}metadata')
        
        if metadata is None:
            # Fallback to extracting from filename
            template_id = file_path.stem
            name = template_id.replace('-', ' ').title()
            description = f"StreamWorks template for {name}"
            category = "General"
        else:
            name_element = metadata.find('.//{http://streamworks.arvato.com/v1}name')
            template_id = name_element.text if name_element is not None else file_path.stem
            name = template_id.replace('-', ' ').title() if template_id else file_path.stem
            desc_element = metadata.find('.//{http://streamworks.arvato.com/v1}description')
            description = desc_element.text if desc_element is not None else f"StreamWorks template for {name}"
            category_element = metadata.find('.//{http://streamworks.arvato.com/v1}category')
            category = category_element.text if category_element is not None else "General"
        
        return XMLTemplate(
            template_id=template_id or file_path.stem,
            name=name or file_path.stem,
            description=description or f"StreamWorks template for {name}",
            category=category or "General",
            file_path=str(file_path),
            xml_content=xml_content
        )
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates as dictionaries"""
        return [template.to_dict() for template in self.templates.values()]
    
    def get_template_by_id(self, template_id: str) -> Optional[XMLTemplate]:
        """Get a specific template by ID"""
        return self.templates.get(template_id)
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get templates filtered by category"""
        return [
            template.to_dict() 
            for template in self.templates.values() 
            if template.category.lower() == category.lower()
        ]
    
    def render_template(self, template_id: str, parameters: Dict[str, str]) -> Optional[str]:
        """Render a template with provided parameters"""
        template = self.get_template_by_id(template_id)
        if not template:
            return None
        
        return template.render(parameters)
    
    def validate_template(self, xml_content: str) -> Dict[str, Any]:
        """Validate XML template content"""
        try:
            # Parse XML
            ET.fromstring(xml_content)
            
            # Check for StreamWorks namespace
            if 'streamworks' not in xml_content:
                return {
                    "valid": True,
                    "warnings": ["Template should use StreamWorks namespace"]
                }
            
            return {"valid": True, "warnings": []}
            
        except ET.ParseError as e:
            return {
                "valid": False,
                "error": f"XML Parse Error: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}"
            }
    
    def create_template_from_xml(self, name: str, category: str, description: str, xml_content: str) -> Optional[XMLTemplate]:
        """Create a new template from XML content"""
        try:
            # Validate XML first
            validation = self.validate_template(xml_content)
            if not validation["valid"]:
                logger.error(f"Invalid XML template: {validation['error']}")
                return None
            
            # Generate template ID from name
            template_id = name.lower().replace(' ', '-').replace('_', '-')
            
            # Save to file
            file_path = self.templates_directory / f"{template_id}.xml"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            # Create template object
            template = XMLTemplate(
                template_id=template_id,
                name=name,
                description=description,
                category=category,
                file_path=str(file_path),
                xml_content=xml_content
            )
            
            # Add to templates cache
            self.templates[template_id] = template
            
            logger.info(f"Created new template: {template_id}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return None
    
    def reload_templates(self) -> int:
        """Reload all templates from disk"""
        self.templates.clear()
        self._load_templates()
        return len(self.templates)

# Global service instance
xml_template_service = XMLTemplateService()