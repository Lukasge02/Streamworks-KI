"""
XML Generator Service for StreamWorks-KI
Generates XML stream configurations based on user requirements
"""
import logging
from typing import Dict, Any, Optional
from xml.etree import ElementTree as ET
from xml.dom import minidom

logger = logging.getLogger(__name__)


class XMLGeneratorService:
    """Service for generating XML stream configurations"""
    
    def __init__(self):
        self.logger = logger
        
    def generate_stream_xml(self, requirements: Dict[str, Any]) -> str:
        """Generate XML stream configuration from requirements"""
        try:
            # Create root element
            root = ET.Element("StreamConfiguration")
            
            # Add metadata
            metadata = ET.SubElement(root, "Metadata")
            ET.SubElement(metadata, "Name").text = requirements.get("name", "DefaultStream")
            ET.SubElement(metadata, "Description").text = requirements.get("description", "Auto-generated stream")
            ET.SubElement(metadata, "Version").text = "1.0"
            ET.SubElement(metadata, "CreatedBy").text = "StreamWorks-KI"
            
            # Add schedule configuration
            schedule = ET.SubElement(root, "Schedule")
            ET.SubElement(schedule, "Type").text = requirements.get("schedule", "daily")
            ET.SubElement(schedule, "Time").text = "00:00:00"
            ET.SubElement(schedule, "Enabled").text = "true"
            
            # Add source configuration
            source = ET.SubElement(root, "Source")
            ET.SubElement(source, "Type").text = "File"
            ET.SubElement(source, "Path").text = requirements.get("source", "/data/input")
            ET.SubElement(source, "Pattern").text = "*.xml"
            
            # Add target configuration
            target = ET.SubElement(root, "Target")
            ET.SubElement(target, "Type").text = "File"
            ET.SubElement(target, "Path").text = requirements.get("target", "/data/output")
            ET.SubElement(target, "Format").text = "XML"
            
            # Add processing configuration
            processing = ET.SubElement(root, "Processing")
            ET.SubElement(processing, "Mode").text = "Automatic"
            ET.SubElement(processing, "ErrorHandling").text = "Continue"
            ET.SubElement(processing, "LogLevel").text = "Info"
            
            # Convert to string with pretty formatting
            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            # Remove empty lines
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Error generating XML: {e}")
            return self._generate_fallback_xml(requirements)
    
    def _generate_fallback_xml(self, requirements: Dict[str, Any]) -> str:
        """Generate simple fallback XML if main generation fails"""
        name = requirements.get("name", "DefaultStream")
        schedule = requirements.get("schedule", "daily")
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<StreamConfiguration>
  <Metadata>
    <Name>{name}</Name>
    <Description>Auto-generated stream configuration</Description>
    <Version>1.0</Version>
    <CreatedBy>StreamWorks-KI</CreatedBy>
  </Metadata>
  <Schedule>
    <Type>{schedule}</Type>
    <Time>00:00:00</Time>
    <Enabled>true</Enabled>
  </Schedule>
  <Source>
    <Type>File</Type>
    <Path>/data/input</Path>
    <Pattern>*.xml</Pattern>
  </Source>
  <Target>
    <Type>File</Type>
    <Path>/data/output</Path>
    <Format>XML</Format>
  </Target>
  <Processing>
    <Mode>Automatic</Mode>
    <ErrorHandling>Continue</ErrorHandling>
    <LogLevel>Info</LogLevel>
  </Processing>
</StreamConfiguration>"""
    
    def validate_xml(self, xml_string: str) -> Dict[str, Any]:
        """Validate generated XML"""
        try:
            ET.fromstring(xml_string)
            return {
                "valid": True,
                "message": "XML is valid",
                "size": len(xml_string)
            }
        except ET.ParseError as e:
            return {
                "valid": False,
                "message": f"XML validation error: {e}",
                "size": len(xml_string)
            }
    
    def extract_requirements_from_text(self, text: str) -> Dict[str, Any]:
        """Extract XML requirements from user text"""
        requirements = {
            "name": "DataProcessing",
            "description": text,
            "schedule": "daily",
            "source": "/data/input",
            "target": "/data/output"
        }
        
        text_lower = text.lower()
        
        # Schedule extraction
        if "stündlich" in text_lower or "hourly" in text_lower:
            requirements["schedule"] = "hourly"
        elif "wöchentlich" in text_lower or "weekly" in text_lower:
            requirements["schedule"] = "weekly"
        elif "täglich" in text_lower or "daily" in text_lower:
            requirements["schedule"] = "daily"
        
        # Name extraction
        if "import" in text_lower:
            requirements["name"] = "DataImport"
        elif "export" in text_lower:
            requirements["name"] = "DataExport"
        elif "transformation" in text_lower or "transform" in text_lower:
            requirements["name"] = "DataTransformation"
        elif "backup" in text_lower:
            requirements["name"] = "DataBackup"
        
        return requirements


# Global instance
xml_generator = XMLGeneratorService()