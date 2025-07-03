import xml.etree.ElementTree as ET
from app.models.schemas import StreamConfig
import logging

logger = logging.getLogger(__name__)

def generate_xml_from_config(config: StreamConfig) -> str:
    """Generate XML stream from configuration"""
    try:
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<stream>
  <n>{config.streamName}</n>
  <job>
    <n>{config.jobName}</n>
    <startTime>{config.startTime or "00:00"}</startTime>
    <dataSource>{config.dataSource}</dataSource>
    <outputPath>{config.outputPath}</outputPath>
    <schedule>{config.schedule}</schedule>
  </job>
</stream>'''
        
        return xml_content
        
    except Exception as e:
        logger.error(f"❌ Error generating XML: {str(e)}")
        raise

def validate_xml(xml_content: str) -> bool:
    """Validate XML content"""
    try:
        ET.fromstring(xml_content)
        return True
    except ET.ParseError as e:
        logger.error(f"❌ XML validation error: {str(e)}")
        return False