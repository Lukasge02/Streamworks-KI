"""
XML Generator Service
Generates Streamworks XML using a unified Master Template
"""
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class JobType(str, Enum):
    STANDARD = "STANDARD"
    FILE_TRANSFER = "FILE_TRANSFER"
    SAP = "SAP"


class XMLGenerator:
    """
    Generates Streamworks XML from parameters using the Master Template
    """
    
    def __init__(self):
        # Template directory
        template_dir = Path(__file__).parent.parent.parent / "knowledge" / "templates"
        
        if template_dir.exists():
            self.env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
            # Add custom filter for XML boolean values
            # Streamworks requires 'True' and 'False' (Capitalized)
            self.env.filters['xml_boolean'] = lambda x: 'True' if x else 'False'
        else:
            self.env = None
        
        # All types now use the master template
        self.master_template = "master_template.xml"
    
    def generate(self, job_type: str, params: Dict[str, Any]) -> str:
        """
        Generate XML from job type and parameters
        """
        # Normalize job type
        if isinstance(job_type, str):
            job_type = JobType(job_type.upper())
        
        # Add defaults and prepare params
        params = self._prepare_params(job_type, params)
        
        # Use master template
        if self.env:
            try:
                template = self.env.get_template(self.master_template)
                return template.render(**params)
            except Exception as e:
                print(f"Error rendering template: {e}")
                return self._generate_fallback(job_type, params)
        
        return self._generate_fallback(job_type, params)
    
    def _prepare_params(self, job_type: JobType, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply defaults and derived values"""
        from .schedule_generator import generate_schedule_xml
        
        # Base defaults
        defaults = {
            "stream_name": "NewStream",
            "job_name": f"0100_{params.get('stream_name', 'NewStream')}",
            "job_type": job_type.value,
            "status_flag": True,
            "deploy_as_active": True,
        }
        
        # Generate schedule_rule_xml from natural language if provided
        if params.get("schedule") or params.get("start_time"):
            defaults["schedule_rule_xml"] = generate_schedule_xml(
                schedule=params.get("schedule"),
                start_time=params.get("start_time")
            )
        
        # Ensure GECK003_ prefix (User Rule)
        stream_name = params.get("stream_name", defaults["stream_name"])
        if stream_name and not stream_name.startswith("GECK003_"):
            defaults["stream_name"] = f"GECK003_{stream_name}"
            # Update job name if it was based on stream name
            if "job_name" not in params:
                 defaults["job_name"] = f"0100_{defaults['stream_name']}"
        
        # Merge: defaults < params
        return {**defaults, **params}
    
    def _generate_fallback(self, job_type: JobType, params: Dict[str, Any]) -> str:
        """Minimal fallback if template fails"""
        return f'''<?xml version="1.0" encoding="utf-8"?>
<ExportableStream>
  <Stream>
    <StreamName>{params.get("stream_name", "ErrorStream")}</StreamName>
    <ShortDescription>Error generating full XML</ShortDescription>
    <Jobs>
      <Job><JobType>{job_type.value}</JobType></Job>
    </Jobs>
  </Stream>
</ExportableStream>'''
