"""
XML Generation Services Package

Template-based XML generation for Streamworks with:
- Jinja2 template engine for XML rendering
- Parameter mapping system for LangExtract integration
- Support for STANDARD, FILE_TRANSFER, and SAP job types
"""

from .template_engine import (
    XMLTemplateEngine,
    JobType,
    TemplateContext,
    get_xml_template_engine,
    generate_standard_xml,
    generate_file_transfer_xml,
    generate_sap_xml
)

from .parameter_mapper import (
    XMLParameterMapper,
    ParameterMapping,
    get_parameter_mapper
)

__all__ = [
    # Template Engine
    "XMLTemplateEngine",
    "JobType",
    "TemplateContext",
    "get_xml_template_engine",
    "generate_standard_xml",
    "generate_file_transfer_xml",
    "generate_sap_xml",

    # Parameter Mapper
    "XMLParameterMapper",
    "ParameterMapping",
    "get_parameter_mapper"
]