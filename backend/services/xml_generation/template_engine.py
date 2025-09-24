"""
XML Template Engine
Jinja2-based template rendering for Streamworks XML generation
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path
from enum import Enum

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class JobType(str, Enum):
    """Supported Streamworks job types"""
    STANDARD = "STANDARD"
    FILE_TRANSFER = "FILE_TRANSFER"
    SAP = "SAP"


class TemplateContext(BaseModel):
    """Template rendering context with validation"""

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
    file_extension: str = "*"
    transfer_mode: str = "Copy"
    preserve_timestamp: bool = True
    create_target_directory: bool = True
    overwrite_existing_files: bool = True
    delete_source_files: bool = False
    retry_count: int = 3
    retry_interval: int = 60

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
    sap_properties: bool = False  # Flag to include SAP properties section

    # Advanced configuration
    calendar_id: str = "UATDefaultCalendar"
    stream_type: str = "Normal"
    account_no_id: Optional[str] = None
    schedule_rule_object: Optional[str] = None
    concurrent_plan_dates_enabled: bool = False
    run_number_1_required: bool = False

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization logic

        ⚠️ STREAM PREFIX: Auto-generates stream names with 'zsw_' prefix
        See documentation/XML_STREAM_CONFIGURATION.md for prefix changes
        """
        # Auto-generate names if not provided
        if not self.stream_name:
            self.stream_name = f"zsw_{self.timestamp}"  # ⚠️ STREAM PREFIX: Change 'zsw_' here

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

        if self.job_type == JobType.FILE_TRANSFER:
            if not self.template_type:
                self.template_type = "FileTransfer"


class XMLTemplateEngine:
    """
    🚀 XML Template Engine

    Jinja2-based XML generation for Streamworks templates with:
    - Type-safe parameter validation
    - Smart defaults and auto-generation
    - Template caching for performance
    - Comprehensive error handling
    """

    def __init__(self, template_dir: Optional[str] = None):
        """Initialize XML Template Engine"""

        if template_dir is None:
            # Default to backend/templates/xml_templates
            current_dir = Path(__file__).parent.parent.parent
            template_dir = current_dir / "templates" / "xml_templates"

        self.template_dir = Path(template_dir)

        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self.env.filters['xml_boolean'] = self._xml_boolean_filter

        # Template mapping
        self.template_mapping = {
            JobType.STANDARD: "standard_job_template.xml",
            JobType.FILE_TRANSFER: "file_transfer_template.xml",
            JobType.SAP: "sap_job_template.xml"
        }

        # Validate templates exist
        self._validate_templates()

        logger.info(f"🚀 XMLTemplateEngine initialized with templates from: {self.template_dir}")

    def _xml_boolean_filter(self, value):
        """Jinja2 filter to convert Python boolean to XML boolean"""
        if value is None:
            return "false"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            if value.lower() in ['true', '1', 'yes']:
                return "true"
            elif value.lower() in ['false', '0', 'no']:
                return "false"
            else:
                return "false"
        return "true" if value else "false"

    def _validate_templates(self):
        """Validate all required templates exist"""
        missing_templates = []

        for job_type, template_file in self.template_mapping.items():
            template_path = self.template_dir / template_file
            if not template_path.exists():
                missing_templates.append(f"{job_type.value}: {template_file}")

        if missing_templates:
            raise FileNotFoundError(f"Missing templates: {', '.join(missing_templates)}")

        logger.info(f"✅ All {len(self.template_mapping)} templates validated")

    def generate_xml(
        self,
        job_type: Union[str, JobType],
        parameters: Dict[str, Any]
    ) -> str:
        """
        🎯 Generate XML from template and parameters

        Args:
            job_type: Job type (STANDARD, FILE_TRANSFER, SAP)
            parameters: Template parameters dictionary

        Returns:
            Generated XML string
        """

        # Convert string to enum if needed
        if isinstance(job_type, str):
            try:
                job_type = JobType(job_type.upper())
            except ValueError:
                raise ValueError(f"Unsupported job type: {job_type}. Supported: {list(JobType)}")

        # Create validated context
        context = TemplateContext(job_type=job_type, **parameters)

        # Get template
        template_file = self.template_mapping[job_type]
        template = self.env.get_template(template_file)

        # Generate XML
        try:
            xml_content = template.render(context.model_dump())
            logger.info(f"✅ XML generated successfully for job type: {job_type.value}")
            return xml_content

        except Exception as e:
            logger.error(f"❌ Template rendering failed for {job_type.value}: {str(e)}")
            raise RuntimeError(f"Template rendering failed: {str(e)}")

    def preview_context(
        self,
        job_type: Union[str, JobType],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🔍 Preview template context without rendering

        Useful for debugging and parameter validation
        """

        if isinstance(job_type, str):
            job_type = JobType(job_type.upper())

        context = TemplateContext(job_type=job_type, **parameters)
        return context.model_dump()

    def list_templates(self) -> Dict[str, str]:
        """List available templates"""
        return {jt.value: template for jt, template in self.template_mapping.items()}

    def get_template_parameters(self, job_type: Union[str, JobType]) -> Dict[str, Any]:
        """Get template parameter schema"""

        if isinstance(job_type, str):
            job_type = JobType(job_type.upper())

        # Return TemplateContext schema for the job type
        schema = TemplateContext.model_json_schema()

        # Filter relevant fields for job type
        if job_type == JobType.STANDARD:
            relevant_fields = [
                'stream_name', 'stream_documentation', 'short_description',
                'job_name', 'job_documentation', 'main_script', 'start_time',
                'max_stream_runs', 'scheduling_required_flag'
            ]
        elif job_type == JobType.FILE_TRANSFER:
            relevant_fields = [
                'stream_name', 'stream_documentation', 'short_description',
                'source_agent', 'target_agent', 'source_path', 'target_path',
                'file_extension', 'transfer_mode', 'start_time',
                'max_stream_runs', 'scheduling_required_flag'
            ]
        else:  # SAP
            relevant_fields = [
                'stream_name', 'stream_documentation', 'short_description',
                'sap_system', 'sap_client', 'sap_report', 'sap_transaction',
                'sap_variant', 'sap_parameters', 'start_time',
                'max_stream_runs', 'scheduling_required_flag'
            ]

        return {
            'job_type': job_type.value,
            'required_fields': relevant_fields,
            'schema': schema
        }


# Singleton instance for global access
xml_template_engine = None

def get_xml_template_engine() -> XMLTemplateEngine:
    """Get singleton XMLTemplateEngine instance"""
    global xml_template_engine

    if xml_template_engine is None:
        xml_template_engine = XMLTemplateEngine()

    return xml_template_engine


# Convenience functions
def generate_standard_xml(parameters: Dict[str, Any]) -> str:
    """Generate STANDARD job XML"""
    engine = get_xml_template_engine()
    return engine.generate_xml(JobType.STANDARD, parameters)


def generate_file_transfer_xml(parameters: Dict[str, Any]) -> str:
    """Generate FILE_TRANSFER job XML"""
    engine = get_xml_template_engine()
    return engine.generate_xml(JobType.FILE_TRANSFER, parameters)


def generate_sap_xml(parameters: Dict[str, Any]) -> str:
    """Generate SAP job XML"""
    engine = get_xml_template_engine()
    return engine.generate_xml(JobType.SAP, parameters)