"""
XSD Validation Service für Streamworks RAG MVP
Validiert XML outputs gegen Streamworks XSD Schema
"""

import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from lxml import etree
import re

from config import settings

class XSDValidatorService:
    """Service für XML validation against XSD schema"""
    
    def __init__(self):
        self.schema = None
        self.schema_path = settings.XSD_SCHEMA_PATH
        self.enabled = settings.ENABLE_XSD_VALIDATION
        
        if self.enabled:
            self._load_schema()
    
    def _load_schema(self):
        """Load XSD schema from file"""
        try:
            if not self.schema_path.exists():
                print(f"⚠️  XSD schema not found at: {self.schema_path}")
                self.enabled = False
                return
            
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_doc = etree.parse(f)
            
            self.schema = etree.XMLSchema(schema_doc)
            print(f"✅ XSD schema loaded from: {self.schema_path}")
            
        except Exception as e:
            print(f"❌ Failed to load XSD schema: {str(e)}")
            self.enabled = False
    
    async def validate_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        Validate XML content against loaded schema
        
        Args:
            xml_content: XML string to validate
            
        Returns:
            Validation result with errors if any
        """
        if not self.enabled or not self.schema:
            return {
                "enabled": False,
                "valid": None,
                "message": "XSD validation disabled or schema not loaded"
            }
        
        try:
            # Extract XML from content (in case it's embedded in text)
            xml_text = self._extract_xml(xml_content)
            
            if not xml_text:
                return {
                    "enabled": True,
                    "valid": True,
                    "message": "No XML content found to validate",
                    "xml_detected": False
                }
            
            # Parse XML
            try:
                xml_doc = etree.fromstring(xml_text.encode('utf-8'))
            except etree.XMLSyntaxError as e:
                return {
                    "enabled": True,
                    "valid": False,
                    "message": f"Invalid XML syntax: {str(e)}",
                    "errors": [str(e)],
                    "xml_detected": True
                }
            
            # Validate against schema
            is_valid = self.schema.validate(xml_doc)
            
            if is_valid:
                return {
                    "enabled": True,
                    "valid": True,
                    "message": "XML is valid according to Streamworks XSD schema",
                    "xml_detected": True
                }
            else:
                # Collect validation errors
                errors = []
                for error in self.schema.error_log:
                    errors.append({
                        "line": error.line,
                        "column": error.column,
                        "message": error.message,
                        "level": error.level_name
                    })
                
                return {
                    "enabled": True,
                    "valid": False,
                    "message": f"XML validation failed with {len(errors)} error(s)",
                    "errors": errors,
                    "xml_detected": True
                }
                
        except Exception as e:
            return {
                "enabled": True,
                "valid": False,
                "message": f"Validation error: {str(e)}",
                "errors": [str(e)],
                "xml_detected": True
            }
    
    def _extract_xml(self, content: str) -> Optional[str]:
        """
        Extract XML content from text that might contain other content
        """
        try:
            # Look for XML blocks in code fences
            xml_pattern = r'```xml\s*(.*?)\s*```'
            match = re.search(xml_pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # Look for XML without code fences
            xml_pattern = r'<\?xml.*?\?>(.*)'
            match = re.search(xml_pattern, content, re.DOTALL)
            if match:
                return match.group(0).strip()
            
            # Look for any XML-like content starting with root element
            xml_pattern = r'<[^>]+>.*</[^>]+>'
            match = re.search(xml_pattern, content, re.DOTALL)
            if match:
                xml_candidate = match.group(0).strip()
                # Simple check if it looks like valid XML structure
                if xml_candidate.count('<') == xml_candidate.count('>'):
                    return xml_candidate
            
            return None
            
        except Exception:
            return None
    
    async def validate_with_suggestions(self, xml_content: str) -> Dict[str, Any]:
        """
        Validate XML and provide improvement suggestions
        """
        result = await self.validate_xml(xml_content)
        
        if result["valid"] == False and "errors" in result:
            suggestions = self._generate_suggestions(result["errors"])
            result["suggestions"] = suggestions
        
        return result
    
    def _generate_suggestions(self, errors: List[Dict[str, Any]]) -> List[str]:
        """
        Generate helpful suggestions based on validation errors
        """
        suggestions = []
        
        for error in errors:
            message = error.get("message", "").lower()
            
            if "element" in message and "not allowed" in message:
                suggestions.append("Check that all XML elements are valid Streamworks elements")
            
            if "attribute" in message:
                suggestions.append("Verify that all attributes match the Streamworks schema requirements")
            
            if "missing" in message:
                suggestions.append("Add any required elements or attributes specified in the schema")
            
            if "invalid" in message and "value" in message:
                suggestions.append("Check that attribute values match the expected format and constraints")
        
        # Remove duplicates
        return list(set(suggestions))
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded schema
        """
        if not self.enabled or not self.schema:
            return {
                "enabled": False,
                "message": "XSD validation disabled or schema not loaded"
            }
        
        return {
            "enabled": True,
            "schema_path": str(self.schema_path),
            "target_namespace": getattr(self.schema, 'target_namespace', None),
            "message": "XSD schema loaded and ready for validation"
        }