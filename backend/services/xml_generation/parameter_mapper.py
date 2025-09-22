"""
Parameter Mapping System
Maps LangExtract JSON parameters to XML template parameters
"""

import logging
import re
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from pydantic import BaseModel

from .template_engine import JobType

logger = logging.getLogger(__name__)


class ParameterMapping(BaseModel):
    """Parameter mapping configuration"""

    # Source field in JSON (from LangExtract)
    source_field: str

    # Target field in XML template
    target_field: str

    # Optional transformation function name
    transform: Optional[str] = None

    # Required flag
    required: bool = False

    # Default value if not found
    default: Optional[Any] = None


class XMLParameterMapper:
    """
    🎯 Parameter Mapper for XML Template Engine

    Maps extracted JSON parameters from LangExtract to XML template parameters
    with intelligent field transformation and validation.
    """

    def __init__(self):
        """Initialize Parameter Mapper"""

        # Define mappings for each job type
        self.mapping_configs = {
            JobType.STANDARD: self._get_standard_mappings(),
            JobType.FILE_TRANSFER: self._get_file_transfer_mappings(),
            JobType.SAP: self._get_sap_mappings()
        }

        # Parameter transformations
        self.transformations = {
            'normalize_stream_name': self._normalize_stream_name,
            'normalize_agent_name': self._normalize_agent_name,
            'format_time': self._format_time,
            'extract_script': self._extract_script,
            'extract_file_path': self._extract_file_path,
            'extract_sap_system': self._extract_sap_system,
            'extract_sap_report': self._extract_sap_report,
            'boolean_from_string': self._boolean_from_string,
            'integer_from_string': self._integer_from_string
        }

        logger.info(f"🎯 XMLParameterMapper initialized with {len(self.mapping_configs)} job type mappings")

    def _get_standard_mappings(self) -> List[ParameterMapping]:
        """Standard job parameter mappings"""
        return [
            # Core stream parameters
            ParameterMapping(source_field="StreamName", target_field="stream_name", transform="normalize_stream_name"),
            ParameterMapping(source_field="stream_name", target_field="stream_name", transform="normalize_stream_name"),
            ParameterMapping(source_field="MaxStreamRuns", target_field="max_stream_runs", transform="integer_from_string", default=100),
            ParameterMapping(source_field="max_stream_runs", target_field="max_stream_runs", transform="integer_from_string", default=100),
            ParameterMapping(source_field="SchedulingRequiredFlag", target_field="scheduling_required_flag", transform="boolean_from_string", default=True),
            ParameterMapping(source_field="scheduling_required_flag", target_field="scheduling_required_flag", transform="boolean_from_string", default=True),
            ParameterMapping(source_field="StartTime", target_field="start_time", transform="format_time"),
            ParameterMapping(source_field="start_time", target_field="start_time", transform="format_time"),

            # Job parameters
            ParameterMapping(source_field="JobName", target_field="job_name"),
            ParameterMapping(source_field="job_name", target_field="job_name"),
            ParameterMapping(source_field="MainScript", target_field="main_script", transform="extract_script"),
            ParameterMapping(source_field="main_script", target_field="main_script", transform="extract_script"),
            ParameterMapping(source_field="script", target_field="main_script", transform="extract_script"),
            ParameterMapping(source_field="command", target_field="main_script", transform="extract_script"),

            # Documentation
            ParameterMapping(source_field="ShortDescription", target_field="short_description"),
            ParameterMapping(source_field="short_description", target_field="short_description"),
            ParameterMapping(source_field="StreamDocumentation", target_field="stream_documentation"),
            ParameterMapping(source_field="stream_documentation", target_field="stream_documentation"),
            ParameterMapping(source_field="description", target_field="stream_documentation"),

            # Agent details
            ParameterMapping(source_field="AgentDetail", target_field="agent_detail", transform="normalize_agent_name"),
            ParameterMapping(source_field="agent_detail", target_field="agent_detail", transform="normalize_agent_name"),
            ParameterMapping(source_field="agent", target_field="agent_detail", transform="normalize_agent_name"),
        ]

    def _get_file_transfer_mappings(self) -> List[ParameterMapping]:
        """File transfer job parameter mappings"""
        return [
            # Include standard mappings
            *self._get_standard_mappings(),

            # File transfer specific
            ParameterMapping(source_field="source_agent", target_field="source_agent", transform="normalize_agent_name"),
            ParameterMapping(source_field="SourceAgent", target_field="source_agent", transform="normalize_agent_name"),
            ParameterMapping(source_field="quell_agent", target_field="source_agent", transform="normalize_agent_name"),
            ParameterMapping(source_field="von_agent", target_field="source_agent", transform="normalize_agent_name"),

            ParameterMapping(source_field="target_agent", target_field="target_agent", transform="normalize_agent_name"),
            ParameterMapping(source_field="TargetAgent", target_field="target_agent", transform="normalize_agent_name"),
            ParameterMapping(source_field="ziel_agent", target_field="target_agent", transform="normalize_agent_name"),
            ParameterMapping(source_field="nach_agent", target_field="target_agent", transform="normalize_agent_name"),

            ParameterMapping(source_field="source_path", target_field="source_path", transform="extract_file_path"),
            ParameterMapping(source_field="SourcePath", target_field="source_path", transform="extract_file_path"),
            ParameterMapping(source_field="quell_pfad", target_field="source_path", transform="extract_file_path"),
            ParameterMapping(source_field="von_pfad", target_field="source_path", transform="extract_file_path"),

            ParameterMapping(source_field="target_path", target_field="target_path", transform="extract_file_path"),
            ParameterMapping(source_field="TargetPath", target_field="target_path", transform="extract_file_path"),
            ParameterMapping(source_field="ziel_pfad", target_field="target_path", transform="extract_file_path"),
            ParameterMapping(source_field="nach_pfad", target_field="target_path", transform="extract_file_path"),

            ParameterMapping(source_field="file_extension", target_field="file_extension", default="*"),
            ParameterMapping(source_field="FileExtension", target_field="file_extension", default="*"),
            ParameterMapping(source_field="datei_typ", target_field="file_extension", default="*"),

            # Transfer options
            ParameterMapping(source_field="transfer_mode", target_field="transfer_mode", default="Copy"),
            ParameterMapping(source_field="delete_source_files", target_field="delete_source_files", transform="boolean_from_string", default=False),
            ParameterMapping(source_field="overwrite_existing_files", target_field="overwrite_existing_files", transform="boolean_from_string", default=True),
        ]

    def _get_sap_mappings(self) -> List[ParameterMapping]:
        """SAP job parameter mappings"""
        return [
            # Include standard mappings
            *self._get_standard_mappings(),

            # SAP specific
            ParameterMapping(source_field="sap_system", target_field="sap_system", transform="extract_sap_system"),
            ParameterMapping(source_field="SapSystem", target_field="sap_system", transform="extract_sap_system"),
            ParameterMapping(source_field="system", target_field="sap_system", transform="extract_sap_system"),

            ParameterMapping(source_field="sap_client", target_field="sap_client", default="100"),
            ParameterMapping(source_field="SapClient", target_field="sap_client", default="100"),
            ParameterMapping(source_field="client", target_field="sap_client", default="100"),
            ParameterMapping(source_field="mandant", target_field="sap_client", default="100"),

            ParameterMapping(source_field="sap_report", target_field="sap_report", transform="extract_sap_report"),
            ParameterMapping(source_field="SapReport", target_field="sap_report", transform="extract_sap_report"),
            ParameterMapping(source_field="report", target_field="sap_report", transform="extract_sap_report"),

            ParameterMapping(source_field="sap_transaction", target_field="sap_transaction"),
            ParameterMapping(source_field="SapTransaction", target_field="sap_transaction"),
            ParameterMapping(source_field="transaction", target_field="sap_transaction"),
            ParameterMapping(source_field="transaktion", target_field="sap_transaction"),

            ParameterMapping(source_field="sap_variant", target_field="sap_variant"),
            ParameterMapping(source_field="SapVariant", target_field="sap_variant"),
            ParameterMapping(source_field="variant", target_field="sap_variant"),
            ParameterMapping(source_field="variante", target_field="sap_variant"),

            ParameterMapping(source_field="sap_user", target_field="sap_user"),
            ParameterMapping(source_field="SapUser", target_field="sap_user"),
            ParameterMapping(source_field="user", target_field="sap_user"),
            ParameterMapping(source_field="benutzer", target_field="sap_user"),

            ParameterMapping(source_field="sap_language", target_field="sap_language", default="DE"),
            ParameterMapping(source_field="SapLanguage", target_field="sap_language", default="DE"),
            ParameterMapping(source_field="language", target_field="sap_language", default="DE"),
            ParameterMapping(source_field="sprache", target_field="sap_language", default="DE"),
        ]

    def map_parameters(
        self,
        job_type: Union[str, JobType],
        extracted_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🎯 Map extracted JSON parameters to XML template parameters

        Args:
            job_type: Target job type
            extracted_parameters: Parameters from LangExtract

        Returns:
            Mapped parameters for XML template
        """

        if isinstance(job_type, str):
            job_type = JobType(job_type.upper())

        mappings = self.mapping_configs.get(job_type)
        if not mappings:
            raise ValueError(f"No mappings defined for job type: {job_type}")

        mapped_params = {}
        missing_required = []

        logger.info(f"🎯 Mapping parameters for job type: {job_type.value}")
        logger.debug(f"Input parameters: {list(extracted_parameters.keys())}")

        for mapping in mappings:
            source_value = extracted_parameters.get(mapping.source_field)

            if source_value is not None:
                # Apply transformation if specified
                if mapping.transform and mapping.transform in self.transformations:
                    try:
                        transformed_value = self.transformations[mapping.transform](source_value)
                        mapped_params[mapping.target_field] = transformed_value
                        logger.debug(f"Mapped {mapping.source_field} -> {mapping.target_field} (transformed)")
                    except Exception as e:
                        logger.warning(f"Transformation {mapping.transform} failed for {mapping.source_field}: {e}")
                        mapped_params[mapping.target_field] = source_value
                else:
                    mapped_params[mapping.target_field] = source_value
                    logger.debug(f"Mapped {mapping.source_field} -> {mapping.target_field}")

            elif mapping.default is not None:
                mapped_params[mapping.target_field] = mapping.default
                logger.debug(f"Used default for {mapping.target_field}: {mapping.default}")

            elif mapping.required:
                missing_required.append(mapping.source_field)

        if missing_required:
            logger.error(f"Missing required parameters: {missing_required}")
            raise ValueError(f"Missing required parameters for {job_type.value}: {missing_required}")

        # Add any unmapped parameters that might be directly usable
        for key, value in extracted_parameters.items():
            if key not in [m.source_field for m in mappings] and key not in mapped_params:
                mapped_params[key] = value
                logger.debug(f"Pass-through parameter: {key}")

        logger.info(f"✅ Parameter mapping completed: {len(mapped_params)} parameters mapped")
        return mapped_params

    # Transformation functions
    def _normalize_stream_name(self, value: str) -> str:
        """Normalize stream name to valid format"""
        if not value:
            return value

        # Remove special characters, replace spaces/dashes with underscores
        normalized = re.sub(r'[^\w\-]', '_', str(value))
        normalized = re.sub(r'[-\s]+', '_', normalized)
        normalized = re.sub(r'_+', '_', normalized)  # Remove duplicate underscores
        normalized = normalized.strip('_')  # Remove leading/trailing underscores

        # Ensure it starts with letter
        if normalized and not normalized[0].isalpha():
            normalized = f"STREAM_{normalized}"

        return normalized.upper()

    def _normalize_agent_name(self, value: str) -> str:
        """Normalize agent name"""
        if not value:
            return value

        # Basic cleanup
        normalized = str(value).strip()

        # Remove common prefixes/suffixes
        normalized = re.sub(r'^(agent_?|server_?)', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'(_?agent|_?server)$', '', normalized, flags=re.IGNORECASE)

        return normalized

    def _format_time(self, value: Union[str, int]) -> Optional[str]:
        """Format time to HH:MM format"""
        if not value:
            return None

        try:
            # Handle various time formats
            if isinstance(value, int):
                # Assume it's hours, convert to HH:00
                return f"{value:02d}:00"

            value_str = str(value).strip()

            # Already in HH:MM format
            if re.match(r'^\d{1,2}:\d{2}$', value_str):
                return value_str

            # Handle formats like "8:00", "08:00", "8", "08"
            if ':' in value_str:
                parts = value_str.split(':')
                hours = int(parts[0])
                minutes = int(parts[1]) if len(parts) > 1 else 0
            else:
                hours = int(value_str)
                minutes = 0

            return f"{hours:02d}:{minutes:02d}"

        except (ValueError, AttributeError):
            logger.warning(f"Could not format time: {value}")
            return None

    def _extract_script(self, value: str) -> str:
        """Extract and clean script content"""
        if not value:
            return "echo 'Default script'"

        script = str(value).strip()

        # Handle common German commands
        script_translations = {
            'ausführen': 'echo "Ausführen"',
            'starten': 'echo "Starten"',
            'verarbeiten': 'echo "Verarbeiten"'
        }

        for german, english in script_translations.items():
            if german.lower() in script.lower():
                return english

        return script

    def _extract_file_path(self, value: str) -> str:
        """Extract and normalize file path"""
        if not value:
            return ""

        path = str(value).strip()

        # Handle German path descriptions
        if any(word in path.lower() for word in ['alle', 'dateien', 'ordner', 'verzeichnis']):
            if 'csv' in path.lower():
                return "*.csv"
            elif any(ext in path.lower() for ext in ['txt', 'xml', 'json']):
                for ext in ['txt', 'xml', 'json']:
                    if ext in path.lower():
                        return f"*.{ext}"
            return "*.*"

        return path

    def _extract_sap_system(self, value: str) -> str:
        """Extract SAP system name"""
        if not value:
            return "PA1_100"

        system = str(value).strip().upper()

        # Extract system ID from common formats
        if '_' in system:
            system = system.split('_')[0]

        return system

    def _extract_sap_report(self, value: str) -> str:
        """Extract SAP report name"""
        if not value:
            return ""

        report = str(value).strip().upper()

        # Ensure it starts with common SAP prefixes
        if not any(report.startswith(prefix) for prefix in ['Z', 'Y', 'R', 'S']):
            report = f"Z{report}"

        return report

    def _boolean_from_string(self, value: Union[str, bool, int]) -> bool:
        """Convert various formats to boolean"""
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            return value != 0

        if isinstance(value, str):
            value_lower = value.strip().lower()
            return value_lower in ['true', 'yes', 'ja', '1', 'on', 'enabled']

        return bool(value)

    def _integer_from_string(self, value: Union[str, int]) -> int:
        """Convert string to integer with fallback"""
        if isinstance(value, int):
            return value

        try:
            return int(str(value).strip())
        except (ValueError, AttributeError):
            logger.warning(f"Could not convert to integer: {value}")
            return 0


# Singleton instance
parameter_mapper = None

def get_parameter_mapper() -> XMLParameterMapper:
    """Get singleton XMLParameterMapper instance"""
    global parameter_mapper

    if parameter_mapper is None:
        parameter_mapper = XMLParameterMapper()

    return parameter_mapper