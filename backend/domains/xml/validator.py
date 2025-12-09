"""
XML Validator - Validates XML against Streamworks XSD Schema
"""
from typing import Tuple, List, Optional, Dict, Any
from pathlib import Path
import re


class XMLValidator:
    """Validates Streamworks XML structure"""
    
    # Required elements for valid Streamworks XML
    REQUIRED_ELEMENTS = {
        "all": ["StreamName", "AgentDetail", "Jobs"],
        "FILE_TRANSFER": ["SourceAgent", "TargetAgent", "FileTransferDefinitions"],
        "STANDARD": ["MainScript"],
        "SAP": ["SAPJobProperty"]
    }
    
    def validate(self, xml_content: str, job_type: str = "FILE_TRANSFER") -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate XML content
        
        Returns:
            Tuple of (is_valid, list of error/warning objects)
        """
        issues = []
        
        # Helper to find line number from index
        def get_line_number(index: int) -> int:
            return xml_content[:index].count('\n') + 1

        # Basic XML structure check
        if not xml_content.strip().startswith("<?xml"):
            issues.append({
                "message": "XML Deklaration fehlt (<?xml ... ?>)",
                "line": 1,
                "severity": "error"
            })
        
        if "<ExportableStream>" not in xml_content:
            issues.append({
                "message": "Root-Element <ExportableStream> fehlt",
                "line": 1,
                "severity": "error"
            })
        
        if "</ExportableStream>" not in xml_content:
            issues.append({
                "message": "Schließendes </ExportableStream> fehlt am Ende",
                "line": get_line_number(len(xml_content)),
                "severity": "error"
            })
        
        # Check required elements for all job types
        for element in self.REQUIRED_ELEMENTS["all"]:
            # Simple check if element exists at all
            if f"<{element}>" not in xml_content and f"<{element} " not in xml_content:
                issues.append({
                    "message": f"Pflicht-Element <{element}> fehlt",
                    "line": 1,
                    "severity": "error"
                })
        
        # Check job-type specific elements
        job_type_upper = job_type.upper()
        if job_type_upper in self.REQUIRED_ELEMENTS:
            for element in self.REQUIRED_ELEMENTS[job_type_upper]:
                if f"<{element}>" not in xml_content and f"<{element} " not in xml_content:
                    issues.append({
                        "message": f"Element <{element}> für Job-Typ '{job_type}' fehlt",
                        "line": 1,
                        "severity": "warning"
                    })
        
        # Check for empty required values using finditer for line numbers
        # Pattern: <Tag>   </Tag>
        empty_pattern = r"<(StreamName|AgentDetail)>\s*</\1>"
        for match in re.finditer(empty_pattern, xml_content):
            tag = match.group(1)
            line = get_line_number(match.start())
            issues.append({
                "message": f"Wert für <{tag}> fehlt",
                "line": line,
                "severity": "error"
            })
        
        # Check CDATA sections
        if "CDATA" in xml_content:
            cdata_pattern = r"<!\[CDATA\[.*?\]\]>"
            if not re.search(cdata_pattern, xml_content, re.DOTALL):
                issues.append({
                    "message": "CDATA-Sektion ist fehlerhaft formatiert",
                    "line": 1,
                    "severity": "warning"
                })
        
        is_valid = not any(i["severity"] == "error" for i in issues)
        return is_valid, issues
    
    def get_validation_summary(self, xml_content: str, job_type: str = "FILE_TRANSFER") -> dict:
        """Get a detailed validation summary"""
        is_valid, issues = self.validate(xml_content, job_type)
        
        # Count elements
        element_count = len(re.findall(r"<[A-Z][a-zA-Z]+[^/]*>", xml_content))
        
        # Get stream name
        stream_name_match = re.search(r"<StreamName>([^<]+)</StreamName>", xml_content)
        stream_name = stream_name_match.group(1) if stream_name_match else "Unknown"
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "error_count": len([i for i in issues if i['severity'] == 'error']),
            "warning_count": len([i for i in issues if i['severity'] == 'warning']),
            "element_count": element_count,
            "stream_name": stream_name,
            "xml_length": len(xml_content)
        }


# Global validator instance
xml_validator = XMLValidator()
