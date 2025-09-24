"""
XML Validator Service for Streamworks XML Generation
Provides XSD schema validation and error reporting
"""
import logging
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any
from lxml import etree
from pathlib import Path
import time

from schemas.xml_generation import ValidationResult, ValidationError, ValidationSeverity

logger = logging.getLogger(__name__)


class XSDValidator:
    """XSD Schema validator for Streamworks XML files"""
    
    def __init__(self, schema_path: Optional[str] = None):
        self.schema_path = schema_path or self._find_schema_file()
        self.schema = None
        self._load_schema()
    
    def _find_schema_file(self) -> Optional[str]:
        """Try to find Streamworks XSD schema file in common locations"""
        possible_paths = [
            "schemas/streamworks.xsd",
            "../schemas/streamworks.xsd",
            "streamworks.xsd",
            "Export-Streams/streamworks.xsd"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                logger.info(f"Found XSD schema at: {path}")
                return path
        
        logger.warning("No XSD schema file found. Validation will use basic XML parsing only.")
        return None
    
    def _load_schema(self):
        """Load XSD schema for validation"""
        if not self.schema_path:
            return
            
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as schema_file:
                schema_doc = etree.parse(schema_file)
                self.schema = etree.XMLSchema(schema_doc)
                logger.info(f"Loaded XSD schema from {self.schema_path}")
        except Exception as e:
            logger.error(f"Failed to load XSD schema: {str(e)}")
            self.schema = None
    
    def validate_xml_string(self, xml_content: str) -> ValidationResult:
        """
        Validate XML string against Streamworks schema
        
        Args:
            xml_content: XML content as string
            
        Returns:
            ValidationResult with validation status and errors
        """
        start_time = time.time()
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []
        
        # Basic XML parsing validation
        try:
            # Parse with lxml for better error reporting
            parser = etree.XMLParser(recover=False)
            xml_doc = etree.fromstring(xml_content.encode('utf-8'), parser)
            
        except etree.XMLSyntaxError as e:
            errors.append(ValidationError(
                line=e.lineno,
                column=e.offset,
                severity=ValidationSeverity.ERROR,
                message=f"XML Syntax Error: {str(e)}",
                suggestion="Check XML syntax and ensure all tags are properly closed"
            ))
            return ValidationResult(
                valid=False,
                errors=errors,
                warnings=warnings
            )
        except Exception as e:
            errors.append(ValidationError(
                severity=ValidationSeverity.ERROR,
                message=f"XML Parsing Error: {str(e)}",
                suggestion="Ensure valid XML format"
            ))
            return ValidationResult(
                valid=False,
                errors=errors,
                warnings=warnings
            )
        
        # XSD Schema validation if available
        if self.schema:
            try:
                if not self.schema.validate(xml_doc):
                    for error in self.schema.error_log:
                        severity = ValidationSeverity.ERROR if error.level_name == "ERROR" else ValidationSeverity.WARNING
                        errors.append(ValidationError(
                            line=error.line,
                            column=error.column,
                            severity=severity,
                            message=f"Schema Validation: {error.message}",
                            suggestion=self._get_schema_error_suggestion(error.message)
                        ))
            except Exception as e:
                logger.error(f"Schema validation error: {str(e)}")
                warnings.append(ValidationError(
                    severity=ValidationSeverity.WARNING,
                    message=f"Could not validate against schema: {str(e)}",
                    suggestion="Manual review recommended"
                ))
        else:
            warnings.append(ValidationError(
                severity=ValidationSeverity.WARNING,
                message="No XSD schema available - only basic XML validation performed",
                suggestion="Provide Streamworks XSD schema for complete validation"
            ))
        
        # Streamworks-specific validation rules
        streamworks_errors = self._validate_streamworks_structure(xml_doc)
        errors.extend(streamworks_errors)
        
        validation_time = int((time.time() - start_time) * 1000)
        logger.info(f"XML validation completed in {validation_time}ms - Valid: {len(errors) == 0}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            schema_version="1.0" if self.schema else None
        )
    
    def _validate_streamworks_structure(self, xml_doc) -> List[ValidationError]:
        """
        Validate Streamworks-specific structure and requirements
        Based on analysis of existing XML templates
        """
        errors: List[ValidationError] = []
        
        try:
            # Check root element
            if xml_doc.tag != "ExportableStream":
                errors.append(ValidationError(
                    severity=ValidationSeverity.ERROR,
                    message="Root element must be 'ExportableStream'",
                    suggestion="Ensure XML starts with <ExportableStream>"
                ))
                return errors
            
            # Check for required Stream element
            stream_elem = xml_doc.find(".//Stream")
            if stream_elem is None:
                errors.append(ValidationError(
                    severity=ValidationSeverity.ERROR,
                    message="Missing required 'Stream' element",
                    suggestion="Add <Stream> element inside <ExportableStream>"
                ))
                return errors
            
            # Check required Stream fields
            required_stream_fields = [
                "StreamName",
                "AgentDetail", 
                "StreamType",
                "MaxStreamRuns",
                "ShortDescription"
            ]
            
            for field in required_stream_fields:
                if stream_elem.find(field) is None:
                    errors.append(ValidationError(
                        severity=ValidationSeverity.ERROR,
                        message=f"Missing required field: {field}",
                        suggestion=f"Add <{field}> element to Stream"
                    ))
            
            # Check Jobs structure
            jobs_elem = stream_elem.find("Jobs")
            if jobs_elem is not None:
                jobs = jobs_elem.findall("Job")
                if len(jobs) == 0:
                    errors.append(ValidationError(
                        severity=ValidationSeverity.WARNING,
                        message="No jobs defined in stream",
                        suggestion="Add at least one Job element"
                    ))
                
                # Validate each job
                for i, job in enumerate(jobs):
                    job_errors = self._validate_job_structure(job, i)
                    errors.extend(job_errors)
            
            # Check ContactPersons
            contact_persons = stream_elem.find("StreamContactPersons")
            if contact_persons is None or len(contact_persons.findall("StreamContactPerson")) == 0:
                errors.append(ValidationError(
                    severity=ValidationSeverity.WARNING,
                    message="No contact persons defined",
                    suggestion="Add StreamContactPersons with at least one contact"
                ))
        
        except Exception as e:
            logger.error(f"Structure validation error: {str(e)}")
            errors.append(ValidationError(
                severity=ValidationSeverity.ERROR,
                message=f"Structure validation failed: {str(e)}",
                suggestion="Check XML structure manually"
            ))
        
        return errors
    
    def _validate_job_structure(self, job_elem, job_index: int) -> List[ValidationError]:
        """Validate individual job structure"""
        errors: List[ValidationError] = []
        
        # Required job fields
        required_job_fields = [
            "JobName",
            "JobCategory", 
            "StatusFlag",
            "DisplayOrder",
            "TemplateType",
            "CoordinateX",
            "CoordinateY"
        ]
        
        for field in required_job_fields:
            if job_elem.find(field) is None:
                errors.append(ValidationError(
                    severity=ValidationSeverity.ERROR,
                    message=f"Job {job_index + 1}: Missing required field '{field}'",
                    suggestion=f"Add <{field}> to Job element"
                ))
        
        # Check job type specific requirements
        job_type_elem = job_elem.find("JobType")
        template_type_elem = job_elem.find("TemplateType")
        
        if template_type_elem is not None:
            template_type = template_type_elem.text
            
            # FileTransfer jobs need FileTransferProperty
            if template_type == "FileTransfer":
                if job_elem.find("JobFileTransferProperty") is None:
                    errors.append(ValidationError(
                        severity=ValidationSeverity.ERROR,
                        message=f"Job {job_index + 1}: FileTransfer job missing JobFileTransferProperty",
                        suggestion="Add JobFileTransferProperty element for file transfer configuration"
                    ))
            
            # Script-based jobs need MainScript or JobType
            elif template_type == "Normal" and job_type_elem is not None:
                job_type = job_type_elem.text
                main_script = job_elem.find("MainScript")
                
                if job_type in ["Windows", "Unix"] and (main_script is None or not main_script.text):
                    errors.append(ValidationError(
                        severity=ValidationSeverity.WARNING,
                        message=f"Job {job_index + 1}: {job_type} job has no MainScript",
                        suggestion="Add script content to MainScript element"
                    ))
        
        return errors
    
    def _get_schema_error_suggestion(self, error_message: str) -> str:
        """Generate helpful suggestions based on common schema errors"""
        error_msg_lower = error_message.lower()
        
        if "element" in error_msg_lower and "not allowed" in error_msg_lower:
            return "Check element name spelling and XML structure"
        elif "missing" in error_msg_lower:
            return "Add the required element to your XML"
        elif "type" in error_msg_lower and "expected" in error_msg_lower:
            return "Check the data type of the element content"
        elif "attribute" in error_msg_lower:
            return "Check attribute name and value format"
        else:
            return "Review XML structure against Streamworks schema"
    
    def validate_xml_file(self, file_path: str) -> ValidationResult:
        """
        Validate XML file against schema
        
        Args:
            file_path: Path to XML file
            
        Returns:
            ValidationResult
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                xml_content = file.read()
                return self.validate_xml_string(xml_content)
        except FileNotFoundError:
            return ValidationResult(
                valid=False,
                errors=[ValidationError(
                    severity=ValidationSeverity.ERROR,
                    message=f"File not found: {file_path}",
                    suggestion="Check file path and permissions"
                )]
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[ValidationError(
                    severity=ValidationSeverity.ERROR,
                    message=f"Error reading file: {str(e)}",
                    suggestion="Check file format and permissions"
                )]
            )
    
    def is_schema_available(self) -> bool:
        """Check if XSD schema is available for validation"""
        return self.schema is not None


# Global validator instance
validator_instance = None

def get_validator() -> XSDValidator:
    """Get global validator instance (singleton pattern)"""
    global validator_instance
    if validator_instance is None:
        validator_instance = XSDValidator()
    return validator_instance