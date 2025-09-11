"""
XML Template Engine for StreamWorks XML Generation
Simple template-based generation using predefined templates with placeholders
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from schemas.xml_generation import WizardFormData, JobType, XMLGenerationResult

logger = logging.getLogger(__name__)


class XMLTemplateEngine:
    """Simple template engine for generating StreamWorks XML from templates"""
    
    def __init__(self, templates_dir: str = "backend/templates"):
        self.templates_dir = Path(templates_dir)
        self.config = self._load_template_config()
        self.main_template = self._load_template("streamworks_template.xml")
        self.job_properties_template = self._load_template("job_properties_template.xml")
        
    def _load_template_config(self) -> Dict[str, Any]:
        """Load template configuration from JSON file"""
        try:
            config_path = self.templates_dir / "template_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load template config: {str(e)}")
            return {"defaults": {}, "job_types": {}, "schedule_templates": {}}
    
    def _load_template(self, template_name: str) -> str:
        """Load template file content"""
        try:
            template_path = self.templates_dir / template_name
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {str(e)}")
            return ""
    
    def generate_xml(self, wizard_data: WizardFormData) -> XMLGenerationResult:
        """
        Generate StreamWorks XML from wizard form data using templates
        
        Args:
            wizard_data: Complete form data from wizard
            
        Returns:
            XMLGenerationResult with generated XML content
        """
        try:
            logger.info(f"Generating XML for job type: {wizard_data.job_type}")
            
            # Create replacement dictionary
            replacements = self._build_replacements(wizard_data)
            
            # Generate XML from template
            xml_content = self._apply_replacements(self.main_template, replacements)
            
            # Basic validation - check if all required placeholders were replaced
            missing_placeholders = self._find_missing_placeholders(xml_content)
            
            result = XMLGenerationResult(
                success=True,
                xml_content=xml_content,
                requires_human_review=len(missing_placeholders) > 0,
                review_reasons=missing_placeholders,
                generation_time_ms=0
            )
            
            if missing_placeholders:
                logger.warning(f"Generated XML has missing placeholders: {missing_placeholders}")
            else:
                logger.info("XML generation completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"XML generation failed: {str(e)}")
            return XMLGenerationResult(
                success=False,
                requires_human_review=True,
                review_reasons=[f"Generation error: {str(e)}"],
                error_message=str(e)
            )
    
    def _build_replacements(self, wizard_data: WizardFormData) -> Dict[str, str]:
        """Build dictionary of template placeholders and their replacements"""
        replacements = self.config.get("defaults", {}).copy()
        
        # Stream properties
        stream_props = wizard_data.stream_properties
        replacements.update({
            "STREAM_NAME": stream_props.stream_name,
            "STREAM_DOCUMENTATION": stream_props.documentation or stream_props.description,
            "SHORT_DESCRIPTION": stream_props.description,
            "CONTACT_FIRST_NAME": stream_props.contact_person.first_name,
            "CONTACT_LAST_NAME": stream_props.contact_person.last_name,
            "CONTACT_COMPANY": stream_props.contact_person.company,
            "CONTACT_DEPARTMENT": stream_props.contact_person.department or "",
            "DEPLOYMENT_DATETIME": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        })
        
        # Job-specific replacements
        job_form = wizard_data.job_form
        job_type_config = self.config.get("job_types", {}).get(wizard_data.job_type.value, {})
        
        # Main job name
        if hasattr(job_form, 'job_name'):
            replacements["MAIN_JOB_NAME"] = job_form.job_name
        elif isinstance(job_form, dict) and 'jobName' in job_form:
            replacements["MAIN_JOB_NAME"] = job_form['jobName']
        else:
            replacements["MAIN_JOB_NAME"] = f"{stream_props.stream_name}_job"
        
        # Job description
        replacements["JOB_DESCRIPTION"] = getattr(job_form, 'job_name', replacements["MAIN_JOB_NAME"])
        
        # Apply job type specific configurations
        replacements.update(job_type_config)
        
        # Job-specific script and extensions
        self._apply_job_specific_replacements(wizard_data, replacements)
        
        # Scheduling
        self._apply_scheduling_replacements(wizard_data, replacements)
        
        # StreamRunJobProperties
        job_properties = self._apply_replacements(self.job_properties_template, replacements)
        replacements["STREAM_RUN_JOB_PROPERTIES"] = job_properties
        
        return replacements
    
    def _apply_job_specific_replacements(self, wizard_data: WizardFormData, replacements: Dict[str, str]):
        """Apply job type specific replacements"""
        job_form = wizard_data.job_form
        job_type = wizard_data.job_type
        
        if job_type == JobType.STANDARD:
            if hasattr(job_form, 'script'):
                replacements["MAIN_SCRIPT"] = job_form.script
            elif isinstance(job_form, dict) and 'script' in job_form:
                replacements["MAIN_SCRIPT"] = job_form['script']
            else:
                replacements["MAIN_SCRIPT"] = "echo 'Standard job script'"
                
        elif job_type == JobType.SAP:
            # SAP-specific placeholders
            if hasattr(job_form, 'system'):
                replacements["SAP_SYSTEM"] = job_form.system
                replacements["SAP_REPORT"] = job_form.report
                replacements["SAP_VARIANT"] = job_form.variant or ""
                replacements["BATCH_USER"] = job_form.batch_user
            elif isinstance(job_form, dict):
                replacements["SAP_SYSTEM"] = job_form.get('system', 'PA1_100')
                replacements["SAP_REPORT"] = job_form.get('report', 'RBDAGAIN')
                replacements["SAP_VARIANT"] = job_form.get('variant', '')
                replacements["BATCH_USER"] = job_form.get('batchUser', 'Batch_PUR')
            
            replacements["MAIN_SCRIPT"] = ""
            
        elif job_type == JobType.FILE_TRANSFER:
            # File Transfer specific placeholders
            if hasattr(job_form, 'source_agent'):
                replacements["SOURCE_AGENT"] = job_form.source_agent
                replacements["SOURCE_PATH"] = job_form.source_path
                replacements["TARGET_AGENT"] = job_form.target_agent
                replacements["TARGET_PATH"] = job_form.target_path
            elif isinstance(job_form, dict):
                replacements["SOURCE_AGENT"] = job_form.get('sourceAgent', '')
                replacements["SOURCE_PATH"] = job_form.get('sourcePath', '')
                replacements["TARGET_AGENT"] = job_form.get('targetAgent', '')
                replacements["TARGET_PATH"] = job_form.get('targetPath', '')
            
            replacements["MAIN_SCRIPT"] = ""
        
        # Default empty values for unused placeholders
        placeholders = ["MAIN_SCRIPT", "JOB_NOTIFICATION_RULES", "LOGIN_OBJECT", 
                       "JOB_EXTENSIONS", "PREPARATION_SCRIPT"]
        for placeholder in placeholders:
            if placeholder not in replacements:
                replacements[placeholder] = ""
    
    def _apply_scheduling_replacements(self, wizard_data: WizardFormData, replacements: Dict[str, str]):
        """Apply scheduling-specific replacements"""
        scheduling = wizard_data.scheduling
        schedule_templates = self.config.get("schedule_templates", {})
        
        if scheduling.mode.value == "simple" and scheduling.simple:
            preset = scheduling.simple.preset
            if preset in schedule_templates:
                replacements["SCHEDULE_RULE_XML"] = schedule_templates[preset]
            else:
                replacements["SCHEDULE_RULE_XML"] = schedule_templates.get("manual", "")
        elif scheduling.mode.value == "advanced" and scheduling.advanced and scheduling.advanced.schedule_rule_xml:
            replacements["SCHEDULE_RULE_XML"] = scheduling.advanced.schedule_rule_xml
        else:
            replacements["SCHEDULE_RULE_XML"] = schedule_templates.get("manual", "")
    
    def _apply_replacements(self, template: str, replacements: Dict[str, str]) -> str:
        """Apply all replacements to template"""
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(f"{{{{{placeholder}}}}}", str(value))
        return result
    
    def _find_missing_placeholders(self, xml_content: str) -> list[str]:
        """Find unreplaced placeholders in generated XML"""
        import re
        placeholders = re.findall(r'\{\{([^}]+)\}\}', xml_content)
        return list(set(placeholders))


# Singleton instance
_template_engine = None


def get_template_engine() -> XMLTemplateEngine:
    """Get template engine singleton"""
    global _template_engine
    if _template_engine is None:
        _template_engine = XMLTemplateEngine()
    return _template_engine