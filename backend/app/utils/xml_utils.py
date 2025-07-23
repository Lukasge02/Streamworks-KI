"""
XML utility functions for StreamWorks-KI
"""
import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom

from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def generate_xml_from_config(config) -> str:
    """Generate XML from StreamConfig object"""
    try:
        # Create root element
        root = ET.Element("StreamConfiguration")
        
        # Add metadata
        metadata = ET.SubElement(root, "Metadata")
        ET.SubElement(metadata, "Name").text = getattr(config, 'streamName', 'DefaultStream')
        ET.SubElement(metadata, "Description").text = getattr(config, 'description', 'Generated stream configuration')
        ET.SubElement(metadata, "Version").text = "1.0"
        ET.SubElement(metadata, "CreatedBy").text = "StreamWorks-KI"
        
        # Add schedule if available
        if hasattr(config, 'schedule'):
            schedule = ET.SubElement(root, "Schedule")
            ET.SubElement(schedule, "Type").text = getattr(config.schedule, 'type', 'daily')
            ET.SubElement(schedule, "Time").text = getattr(config.schedule, 'time', '00:00:00')
            ET.SubElement(schedule, "Enabled").text = str(getattr(config.schedule, 'enabled', True)).lower()
        
        # Add source configuration if available
        if hasattr(config, 'source'):
            source = ET.SubElement(root, "Source")
            ET.SubElement(source, "Type").text = getattr(config.source, 'type', 'File')
            ET.SubElement(source, "Path").text = getattr(config.source, 'path', '/data/input')
            ET.SubElement(source, "Pattern").text = getattr(config.source, 'pattern', '*.xml')
        
        # Add target configuration if available
        if hasattr(config, 'target'):
            target = ET.SubElement(root, "Target")
            ET.SubElement(target, "Type").text = getattr(config.target, 'type', 'File')
            ET.SubElement(target, "Path").text = getattr(config.target, 'path', '/data/output')
            ET.SubElement(target, "Format").text = getattr(config.target, 'format', 'XML')
        
        # Add processing configuration
        processing = ET.SubElement(root, "Processing")
        ET.SubElement(processing, "Mode").text = "Automatic"
        ET.SubElement(processing, "ErrorHandling").text = "Continue"
        ET.SubElement(processing, "LogLevel").text = "Info"
        
        # Convert to pretty XML string
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Remove empty lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        return '\n'.join(lines)
        
    except Exception as e:
        logger.error(f"Error generating XML from config: {e}")
        return generate_fallback_xml(config)


def generate_fallback_xml(config) -> str:
    """Generate simple fallback XML"""
    stream_name = getattr(config, 'streamName', 'DefaultStream')
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<StreamConfiguration>
  <Metadata>
    <Name>{stream_name}</Name>
    <Description>Auto-generated stream configuration</Description>
    <Version>1.0</Version>
    <CreatedBy>StreamWorks-KI</CreatedBy>
  </Metadata>
  <Schedule>
    <Type>daily</Type>
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


def validate_xml(xml_string: str) -> bool:
    """Validate XML string"""
    try:
        ET.fromstring(xml_string)
        return True
    except ET.ParseError as e:
        logger.error(f"XML validation error: {e}")
        return False


def parse_xml_config(xml_string: str) -> Optional[Dict[str, Any]]:
    """Parse XML configuration into dictionary"""
    try:
        root = ET.fromstring(xml_string)
        config = {}
        
        # Parse metadata
        metadata = root.find('Metadata')
        if metadata is not None:
            config['metadata'] = {
                'name': metadata.find('Name').text if metadata.find('Name') is not None else None,
                'description': metadata.find('Description').text if metadata.find('Description') is not None else None,
                'version': metadata.find('Version').text if metadata.find('Version') is not None else None
            }
        
        # Parse schedule
        schedule = root.find('Schedule')
        if schedule is not None:
            config['schedule'] = {
                'type': schedule.find('Type').text if schedule.find('Type') is not None else None,
                'time': schedule.find('Time').text if schedule.find('Time') is not None else None,
                'enabled': schedule.find('Enabled').text == 'true' if schedule.find('Enabled') is not None else True
            }
        
        # Parse source
        source = root.find('Source')
        if source is not None:
            config['source'] = {
                'type': source.find('Type').text if source.find('Type') is not None else None,
                'path': source.find('Path').text if source.find('Path') is not None else None,
                'pattern': source.find('Pattern').text if source.find('Pattern') is not None else None
            }
        
        # Parse target
        target = root.find('Target')
        if target is not None:
            config['target'] = {
                'type': target.find('Type').text if target.find('Type') is not None else None,
                'path': target.find('Path').text if target.find('Path') is not None else None,
                'format': target.find('Format').text if target.find('Format') is not None else None
            }
        
        return config
        
    except ET.ParseError as e:
        logger.error(f"Error parsing XML config: {e}")
        return None


def xml_to_pretty_string(xml_string: str) -> str:
    """Convert XML string to pretty formatted version"""
    try:
        root = ET.fromstring(xml_string)
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Remove empty lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        return '\n'.join(lines)
        
    except Exception as e:
        logger.error(f"Error formatting XML: {e}")
        return xml_string