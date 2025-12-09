"""
XML Service - Wraps XML Generator with validation
"""
from typing import Dict, Any, Tuple
from services.xml_generator import XMLGenerator
from .validator import xml_validator


class XMLService:
    """Service for XML generation and validation"""
    
    def __init__(self):
        self._generator = XMLGenerator()
    
    def generate(self, job_type: str, params: Dict[str, Any]) -> str:
        """Generate XML from parameters"""
        return self._generator.generate(job_type, params)
    
    def generate_and_validate(
        self, 
        job_type: str, 
        params: Dict[str, Any]
    ) -> Tuple[str, dict]:
        """
        Generate XML and return with validation results
        
        Returns:
            Tuple of (xml_content, validation_summary)
        """
        xml_content = self.generate(job_type, params)
        validation = xml_validator.get_validation_summary(xml_content, job_type)
        return xml_content, validation
    
    def validate(self, xml_content: str, job_type: str = "FILE_TRANSFER") -> dict:
        """Validate existing XML content"""
        return xml_validator.get_validation_summary(xml_content, job_type)


# Global service instance
xml_service = XMLService()
