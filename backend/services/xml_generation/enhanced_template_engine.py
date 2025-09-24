#!/usr/bin/env python3
"""
Enhanced XML Template Engine with XSD Validation
Includes None-value handling and schema validation for 100% compatibility
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from enum import Enum

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pydantic import BaseModel, Field
import xml.etree.ElementTree as ET
from lxml import etree

logger = logging.getLogger(__name__)


class JobType(str, Enum):
    """Supported Streamworks job types"""
    STANDARD = "STANDARD"
    FILE_TRANSFER = "FILE_TRANSFER"
    SAP = "SAP"


class ValidationResult(BaseModel):
    """XSD validation result"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class EnhancedTemplateContext(BaseModel):
    """Enhanced template rendering context with None-handling"""

    # Core parameters
    job_type: JobType
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime('%Y%m%d_%H%M%S'))

    # Stream metadata
    stream_name: Optional[str] = None
    stream_documentation: Optional[str] = None
    short_description: Optional[str] = None
    agent_detail: Optional[str] = None
    max_stream_runs: int = 100
    scheduling_required_flag: bool = True
    start_time: Optional[str] = None

    # Job configuration
    job_name: Optional[str] = None
    job_documentation: Optional[str] = None
    job_short_description: Optional[str] = None
    main_script: Optional[str] = None
    template_type: Optional[str] = None
    login_object: Optional[str] = None

    # FILE_TRANSFER specific
    source_agent: Optional[str] = None
    target_agent: Optional[str] = None
    source_path: Optional[str] = None
    target_path: Optional[str] = None
    source_file_pattern: Optional[str] = None
    target_file_path: Optional[str] = None
    target_file_name: Optional[str] = None
    position_no: int = 1
    source_unfulfilled_handling: str = "Abort"
    target_file_exists_handling: str = "Overwrite"
    delete_trailing_blanks_flag: bool = False
    linebreak_translation_type: str = "None"
    use_source_attributes_flag: bool = False

    # Contact information
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    contact_middle_name: Optional[str] = None
    company_name: Optional[str] = None
    department: Optional[str] = None
    contact_type: str = "None"
    hierarchy_level_cd: int = 1

    # Coordinate and layout
    coordinate_x: int = 145
    coordinate_y: int = 192
    display_order: int = 2
    edge_end_position: int = 2
    edge_start_position: int = 6

    # SAP specific
    sap_system: Optional[str] = None
    sap_client: Optional[str] = None
    sap_user: Optional[str] = None
    sap_language: str = "DE"
    sap_report: Optional[str] = None
    sap_transaction: Optional[str] = None
    sap_variant: Optional[str] = None
    sap_parameters: Optional[Dict[str, str]] = None
    sap_output_format: str = "SPOOL"
    sap_output_path: str = "/sap/output/"
    sap_properties: bool = False

    # Stream properties
    calendar_id: str = "UATDefaultCalendar"
    stream_type: str = "Normal"
    account_no_id: Optional[str] = None
    schedule_rule_object: Optional[str] = None
    concurrent_plan_dates_enabled: bool = False
    run_number_1_required: bool = False

    # Schedule and version
    schedule_rule_xml: Optional[str] = None
    stream_preparation_script: Optional[str] = None
    stream_script_language: str = "Lua"
    stream_path: Optional[str] = None
    status_flag: bool = True
    stream_version_type: str = "Current"
    stream_version: str = "1.0"
    deploy_as_active: bool = True
    auto_deployment_status: str = "Finished"
    schedule_rules_merge_type: str = "FromNew"
    automatic_prepared_runs: int = 0
    business_service_flag: bool = False
    auto_preparation_type: str = "Complete"
    enable_stream_run_cancelation: bool = False

    # Deployment information
    deployment_date_time: Optional[str] = None
    planned_deployment_date_time: Optional[str] = None
    storage_date_time: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization with enhanced defaults"""

        # Auto-generate names if not provided
        if not self.stream_name:
            self.stream_name = f"zsw_{self.timestamp}"

        if not self.job_name:
            if self.job_type == JobType.FILE_TRANSFER:
                self.job_name = "FileTransferJob"
            elif self.job_type == JobType.SAP:
                self.job_name = "010_SAP_Job"
            else:
                self.job_name = "MainJob"

        # Set job type specific defaults
        if self.job_type == JobType.SAP:
            self.stream_type = "Real"
            self.max_stream_runs = 1
            self.sap_properties = True
            if not self.template_type:
                self.template_type = "Normal"
            if not self.stream_path:
                self.stream_path = "/SAP"

        if self.job_type == JobType.FILE_TRANSFER:
            if not self.template_type:
                self.template_type = "FileTransfer"
            if not self.stream_path:
                self.stream_path = "/FT"
            # Set FILE_TRANSFER specific coordinates
            self.coordinate_x = 0
            self.coordinate_y = 208

        # Set deployment timestamp
        if not self.deployment_date_time:
            self.deployment_date_time = f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"

    def to_template_dict(self) -> Dict[str, Any]:
        """Convert to template dictionary with enhanced XML handling"""
        data = self.model_dump()

        # Enhanced cleaning for XML compatibility
        def clean_for_xml(obj):
            if isinstance(obj, dict):
                return {k: clean_for_xml(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_xml(item) for item in obj]
            elif obj is None:
                return ""
            elif isinstance(obj, bool):
                return "true" if obj else "false"
            elif hasattr(obj, 'value'):  # Enum object
                return str(obj.value)
            elif isinstance(obj, str) and '.' in obj and obj.startswith(('JobType.', 'StreamType.', 'TemplateType.')):
                # Handle enum string representations like 'JobType.STANDARD'
                return obj.split('.')[-1]
            else:
                return obj

        return clean_for_xml(data)


class EnhancedXMLTemplateEngine:
    """
    Enhanced XML Template Engine with XSD validation and None-handling

    Features:
    - XSD schema validation
    - None-value handling
    - Template caching
    - Comprehensive error reporting
    """

    def __init__(self, template_dir: Optional[str] = None, xsd_schema_file: Optional[str] = None):
        """Initialize Enhanced XML Template Engine"""

        if template_dir is None:
            current_dir = Path(__file__).parent.parent.parent
            template_dir = current_dir / "templates" / "xml_templates"

        if xsd_schema_file is None:
            current_dir = Path(__file__).parent.parent.parent
            xsd_schema_file = current_dir / "schemas" / "streamworks_export.xsd"

        self.template_dir = Path(template_dir)
        self.xsd_schema_file = Path(xsd_schema_file)

        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")

        # Initialize Jinja2 environment with custom filters
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self.env.filters['none_to_empty'] = self._none_to_empty_filter
        self.env.filters['safe_default'] = self._safe_default_filter
        self.env.filters['xml_boolean'] = self._xml_boolean_filter
        self.env.filters['xml_enum'] = self._xml_enum_filter
        self.env.filters['safe_int'] = self._safe_int_filter

        # Template mapping
        self.template_mapping = {
            JobType.STANDARD: "standard_job_template.xml",
            JobType.FILE_TRANSFER: "file_transfer_template.xml",
            JobType.SAP: "sap_job_template.xml",
        }

        # Load XSD schema if available
        self.xsd_schema = None
        if self.xsd_schema_file.exists():
            try:
                with open(self.xsd_schema_file, 'r', encoding='utf-8') as f:
                    xsd_doc = etree.parse(f)
                    self.xsd_schema = etree.XMLSchema(xsd_doc)
                logger.info(f"✅ XSD schema loaded: {self.xsd_schema_file}")
            except Exception as e:
                logger.warning(f"⚠️ Could not load XSD schema: {e}")

    def _none_to_empty_filter(self, value):
        """Jinja2 filter to convert None to empty string"""
        return "" if value is None else str(value)

    def _safe_default_filter(self, value, default=""):
        """Jinja2 filter for safe default values"""
        return default if value is None or str(value).lower() == 'none' else value

    def _xml_boolean_filter(self, value):
        """Jinja2 filter to convert Python boolean to XML boolean"""
        if value is None:
            return ""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            if value.lower() in ['true', '1', 'yes']:
                return "true"
            elif value.lower() in ['false', '0', 'no']:
                return "false"
            else:
                return value
        return str(value).lower()

    def _xml_enum_filter(self, value):
        """Jinja2 filter to extract enum value for XML"""
        if value is None:
            return ""
        if hasattr(value, 'value'):  # Enum object
            return str(value.value)
        value_str = str(value)
        if '.' in value_str:  # Handle JobType.STANDARD format
            return value_str.split('.')[-1]
        return value_str

    def _safe_int_filter(self, value, default=0):
        """Jinja2 filter for safe integer conversion"""
        if value is None or str(value) == "":
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def generate_xml(
        self,
        job_type: Union[str, JobType],
        parameters: Dict[str, Any],
        validate_schema: bool = True
    ) -> str:
        """
        Generate XML from template with enhanced validation

        Args:
            job_type: Job type (STANDARD, FILE_TRANSFER, SAP)
            parameters: Template parameters dictionary
            validate_schema: Whether to validate against XSD schema

        Returns:
            Generated XML string
        """

        # Convert string to enum if needed
        if isinstance(job_type, str):
            try:
                job_type = JobType(job_type.upper())
            except ValueError:
                raise ValueError(f"Unsupported job type: {job_type}. Supported: {list(JobType)}")

        # Create enhanced context
        context = EnhancedTemplateContext(job_type=job_type, **parameters)
        template_vars = context.to_template_dict()

        # Get template
        template_file = self.template_mapping[job_type]
        template = self.env.get_template(template_file)

        # Generate XML
        try:
            xml_content = template.render(**template_vars)
            logger.info(f"✅ XML generated successfully for job type: {job_type.value}")

            # Validate against XSD schema if requested and available
            if validate_schema and self.xsd_schema:
                validation_result = self.validate_xml(xml_content)
                if not validation_result.is_valid:
                    logger.error(f"❌ XML validation failed: {validation_result.errors}")
                    raise ValueError(f"Generated XML does not conform to schema: {validation_result.errors}")
                else:
                    logger.info("✅ XML validation successful")

            return xml_content

        except Exception as e:
            logger.error(f"❌ Template rendering failed for {job_type.value}: {str(e)}")
            raise RuntimeError(f"Template rendering failed: {str(e)}")

    def validate_xml(self, xml_content: str) -> ValidationResult:
        """
        Validate XML content against XSD schema

        Args:
            xml_content: XML content as string

        Returns:
            ValidationResult with validation status and errors
        """

        if not self.xsd_schema:
            return ValidationResult(
                is_valid=False,
                errors=["XSD schema not available"],
                warnings=["Skipping XSD validation"]
            )

        try:
            # Parse XML
            xml_doc = etree.fromstring(xml_content.encode('utf-8'))

            # Validate against schema
            if self.xsd_schema.validate(xml_doc):
                return ValidationResult(is_valid=True)
            else:
                errors = [str(error) for error in self.xsd_schema.error_log]
                return ValidationResult(
                    is_valid=False,
                    errors=errors
                )

        except etree.XMLSyntaxError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"XML syntax error: {str(e)}"]
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )

    def preview_context(
        self,
        job_type: Union[str, JobType],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Preview template context with enhanced None-handling"""

        if isinstance(job_type, str):
            job_type = JobType(job_type.upper())

        context = EnhancedTemplateContext(job_type=job_type, **parameters)
        return context.to_template_dict()

    def validate_templates(self) -> Dict[str, ValidationResult]:
        """
        Validate all templates with minimal parameters

        Returns:
            Dictionary mapping template names to validation results
        """

        results = {}

        for job_type in JobType:
            try:
                # Generate XML with minimal parameters
                minimal_params = {
                    'stream_name': f'test_{job_type.value.lower()}',
                    'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
                }

                # Add job-specific minimal parameters
                if job_type == JobType.FILE_TRANSFER:
                    minimal_params.update({
                        'source_agent': 'TEST_SOURCE',
                        'target_agent': 'TEST_TARGET',
                        'source_file_pattern': 'C:\\test\\*.txt',
                        'target_file_path': 'D:\\target\\'
                    })
                elif job_type == JobType.SAP:
                    minimal_params.update({
                        'sap_system': 'PA1_100',
                        'sap_report': 'ZTV_TEST'
                    })

                xml_content = self.generate_xml(job_type, minimal_params, validate_schema=True)
                validation_result = self.validate_xml(xml_content)

                results[job_type.value] = validation_result

            except Exception as e:
                results[job_type.value] = ValidationResult(
                    is_valid=False,
                    errors=[f"Template generation failed: {str(e)}"]
                )

        return results


def main():
    """Test the enhanced template engine"""

    try:
        engine = EnhancedXMLTemplateEngine()

        # Test all templates
        results = engine.validate_templates()

        print("="*50)
        print("ENHANCED TEMPLATE ENGINE VALIDATION")
        print("="*50)

        all_valid = True
        for template_name, result in results.items():
            status = "✅ VALID" if result.is_valid else "❌ INVALID"
            print(f"{template_name}: {status}")

            if not result.is_valid:
                all_valid = False
                for error in result.errors:
                    print(f"  Error: {error}")

        if all_valid:
            print("\n🎉 All templates are valid and ready for production!")
        else:
            print("\n⚠️ Some templates need fixes before production use.")

    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")


if __name__ == "__main__":
    main()