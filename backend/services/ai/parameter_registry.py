"""
ParameterRegistry: Central source of truth for parameter definitions.

Loads parameters.yaml and provides:
- Excel header -> param_key mappings
- AI prompt generation
- Validation rules
- Required field checks
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from pydantic import BaseModel


class ParameterDefinition(BaseModel):
    """Single parameter definition from config"""
    key: str
    label: str
    type: str = "string"
    required: bool = False
    required_for: List[str] = []
    pattern: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None
    max_length: Optional[int] = None
    default: Optional[Any] = None
    options: List[str] = []
    excel_headers: List[str] = []
    ai_keywords: List[str] = []
    example: Optional[str] = None


class ParameterGroup(BaseModel):
    """Group of related parameters"""
    id: str
    label: str
    order: int = 0
    job_types: List[str] = []  # Empty = applies to all
    parameters: List[ParameterDefinition] = []


class JobTypeDefinition(BaseModel):
    """Job type definition"""
    id: str
    label: str
    description: str
    keywords: List[str] = []


class ParameterRegistry:
    """
    Central registry for all parameter definitions.
    Singleton pattern for efficient access.
    """
    _instance = None
    _config: Dict = {}
    _parameters: Dict[str, ParameterDefinition] = {}
    _groups: List[ParameterGroup] = []
    _job_types: Dict[str, JobTypeDefinition] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load parameters.yaml configuration"""
        config_path = Path(__file__).parent.parent.parent / "config" / "parameters.yaml"
        
        if not config_path.exists():
            print(f"⚠️ Config not found: {config_path}")
            return
            
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)
        
        # Parse job types
        for job_id, job_data in self._config.get("job_types", {}).items():
            self._job_types[job_id] = JobTypeDefinition(
                id=job_id,
                label=job_data.get("label", job_id),
                description=job_data.get("description", ""),
                keywords=job_data.get("keywords", [])
            )
        
        # Parse parameter groups
        for group_data in self._config.get("parameter_groups", []):
            params = []
            for param_data in group_data.get("parameters", []):
                param = ParameterDefinition(**param_data)
                params.append(param)
                self._parameters[param.key] = param
            
            self._groups.append(ParameterGroup(
                id=group_data["id"],
                label=group_data.get("label", group_data["id"]),
                order=group_data.get("order", 0),
                job_types=group_data.get("job_types", []),
                parameters=params
            ))
        
        # Sort groups by order
        self._groups.sort(key=lambda g: g.order)
        
        print(f"✅ ParameterRegistry loaded: {len(self._parameters)} parameters in {len(self._groups)} groups")
    
    # ============ EXCEL PARSER SUPPORT ============
    
    def get_excel_mappings(self) -> Dict[str, str]:
        """
        Get all Excel header -> param_key mappings.
        Returns dict like: {"StreamName": "stream_name", "Name": "stream_name", ...}
        """
        mappings = {}
        for param in self._parameters.values():
            for header in param.excel_headers:
                # Lowercase for case-insensitive matching
                mappings[header.lower()] = param.key
        return mappings
    
    def get_header_mapping(self, header: str) -> Optional[str]:
        """Get param_key for a specific header (case-insensitive)"""
        mappings = self.get_excel_mappings()
        return mappings.get(header.lower())
    
    # ============ AI PROMPT SUPPORT ============
    
    def get_ai_extraction_prompt(self) -> str:
        """
        Generate AI extraction prompt section from config.
        Includes all parameters with their keywords and examples.
        """
        lines = ["## PARAMETER EXTRAKTION\n"]
        lines.append("Extrahiere folgende Parameter aus dem Text:\n")
        
        for group in self._groups:
            lines.append(f"\n### {group.label}")
            if group.job_types:
                lines.append(f"(Nur für: {', '.join(group.job_types)})\n")
            
            for param in group.parameters:
                req = " [PFLICHT]" if param.required else ""
                keywords = ", ".join(param.ai_keywords[:5]) if param.ai_keywords else ""
                example = f' (z.B. "{param.example}")' if param.example else ""
                
                lines.append(f"- **{param.key}**: {param.label}{req}")
                if keywords:
                    lines.append(f"  Schlüsselwörter: {keywords}")
                if example:
                    lines.append(f"  {example}")
        
        return "\n".join(lines)
    
    def get_job_type_detection_prompt(self) -> str:
        """Generate job type detection section for AI prompt"""
        lines = ["## JOB-TYP ERKENNUNG\n"]
        
        for job_type in self._job_types.values():
            keywords = ", ".join(job_type.keywords[:8])
            lines.append(f"**{job_type.id}** - {job_type.label}")
            lines.append(f"  {job_type.description}")
            lines.append(f"  Schlüsselwörter: {keywords}\n")
        
        return "\n".join(lines)
    
    # ============ VALIDATION SUPPORT ============
    
    def get_required_fields(self, job_type: str = None) -> List[str]:
        """Get list of required field keys for a job type"""
        required = []
        for param in self._parameters.values():
            if param.required:
                required.append(param.key)
            elif job_type and job_type in param.required_for:
                required.append(param.key)
        return required
    
    def validate_value(self, key: str, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against parameter definition.
        Returns (is_valid, error_message)
        """
        param = self._parameters.get(key)
        if not param:
            return True, None  # Unknown params pass through
        
        if value is None or value == "":
            if param.required:
                return False, f"{param.label} is required"
            return True, None
        
        # Type validation
        if param.type == "integer":
            try:
                val = int(value)
                if param.min is not None and val < param.min:
                    return False, f"{param.label} must be >= {param.min}"
                if param.max is not None and val > param.max:
                    return False, f"{param.label} must be <= {param.max}"
            except (ValueError, TypeError):
                return False, f"{param.label} must be an integer"
        
        if param.type == "email" and value:
            import re
            if not re.match(r"^[\w.-]+@[\w.-]+\.\w+$", str(value)):
                return False, f"{param.label} must be a valid email"
        
        if param.type == "enum" and param.options:
            if str(value).lower() not in [o.lower() for o in param.options]:
                return False, f"{param.label} must be one of: {', '.join(param.options)}"
        
        if param.max_length and len(str(value)) > param.max_length:
            return False, f"{param.label} exceeds max length of {param.max_length}"
        
        return True, None
    
    # ============ ACCESSORS ============
    
    def get_parameter(self, key: str) -> Optional[ParameterDefinition]:
        """Get a single parameter definition"""
        return self._parameters.get(key)
    
    def get_all_parameters(self) -> Dict[str, ParameterDefinition]:
        """Get all parameter definitions"""
        return self._parameters.copy()
    
    def get_groups(self) -> List[ParameterGroup]:
        """Get all parameter groups"""
        return self._groups.copy()
    
    def get_groups_for_job_type(self, job_type: str) -> List[ParameterGroup]:
        """Get groups applicable to a specific job type"""
        return [
            g for g in self._groups 
            if not g.job_types or job_type in g.job_types
        ]
    
    def get_job_types(self) -> Dict[str, JobTypeDefinition]:
        """Get all job type definitions"""
        return self._job_types.copy()
    
    def detect_job_type_from_keywords(self, text: str) -> tuple[str, float]:
        """
        Detect job type from text using keyword matching.
        Returns (job_type, confidence)
        """
        text_lower = text.lower()
        scores = {}
        
        for job_type in self._job_types.values():
            score = sum(1 for kw in job_type.keywords if kw in text_lower)
            if score > 0:
                scores[job_type.id] = score
        
        if not scores:
            return "STANDARD", 0.5
        
        best = max(scores, key=scores.get)
        confidence = min(0.3 + (scores[best] * 0.15), 0.95)
        return best, confidence
    
    def to_frontend_schema(self) -> Dict:
        """
        Export schema for frontend form generation.
        Can be exposed via API endpoint.
        """
        return {
            "version": self._config.get("version", "1.0"),
            "job_types": [
                {"id": jt.id, "label": jt.label, "description": jt.description}
                for jt in self._job_types.values()
            ],
            "groups": [
                {
                    "id": g.id,
                    "label": g.label,
                    "job_types": g.job_types,
                    "parameters": [
                        {
                            "key": p.key,
                            "label": p.label,
                            "type": p.type,
                            "required": p.required,
                            "options": p.options,
                            "default": p.default,
                            "example": p.example,
                        }
                        for p in g.parameters
                    ]
                }
                for g in self._groups
            ]
        }


# Singleton accessor
def get_parameter_registry() -> ParameterRegistry:
    """Get the singleton ParameterRegistry instance"""
    return ParameterRegistry()
