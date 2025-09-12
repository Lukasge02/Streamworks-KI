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
        # Use absolute path from project root
        base_dir = Path(__file__).parent.parent
        self.templates_dir = base_dir / "templates" if not Path(templates_dir).is_absolute() else Path(templates_dir)
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
        """Load template file content with inline fallback"""
        try:
            template_path = self.templates_dir / template_name
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {str(e)}")
            # Return inline fallback template
            return self._get_fallback_template(template_name)
    
    def _get_fallback_template(self, template_name: str) -> str:
        """Get inline fallback template when file loading fails"""
        if template_name == "streamworks_template.xml":
            return '''<?xml version="1.0" encoding="utf-8"?>
<ExportableStream>
  <Stream>
    <StreamName>{{STREAM_NAME}}</StreamName>
    <StreamDocumentation><![CDATA[{{STREAM_DOCUMENTATION}}]]></StreamDocumentation>
    <AgentDetail>gtasswvk05445</AgentDetail>
    <AccountNoId />
    <CalendarId />
    <StreamType>Normal</StreamType>
    <MaxStreamRuns>5</MaxStreamRuns>
    <ShortDescription><![CDATA[{{SHORT_DESCRIPTION}}]]></ShortDescription>
    <SchedulingRequiredFlag>False</SchedulingRequiredFlag>
    <ScheduleRuleObject />
    
    <Jobs>
      <Job>
        <JobName>{{MAIN_JOB_NAME}}</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[{{JOB_DESCRIPTION}}]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Job</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>{{JOB_TYPE}}</JobType>
        <MainScript><![CDATA[{{MAIN_SCRIPT}}]]></MainScript>
        <DisplayOrder>1</DisplayOrder>
        <TemplateType>Normal</TemplateType>
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>145</CoordinateX>
        <CoordinateY>192</CoordinateY>
      </Job>
    </Jobs>
    
    <StreamContactPersons>
      <StreamContactPerson>
        <FirstName>{{CONTACT_FIRST_NAME}}</FirstName>
        <LastName>{{CONTACT_LAST_NAME}}</LastName>
        <MiddleName />
        <CompanyName>{{CONTACT_COMPANY}}</CompanyName>
        <Department>{{CONTACT_DEPARTMENT}}</Department>
        <ContactType>None</ContactType>
        <HierarchyLevelCd>1</HierarchyLevelCd>
      </StreamContactPerson>
    </StreamContactPersons>
    
    <ScheduleRule>
      <ScheduleRuleXml><![CDATA[&lt;SchedulingRules ShiftRule=&quot;3&quot; ScheduleRuleDialogNotYetVisited=&quot;1&quot; /&gt;]]></ScheduleRuleXml>
    </ScheduleRule>
    
    <StreamPath><![CDATA[]]></StreamPath>
    <StatusFlag>True</StatusFlag>
  </Stream>
</ExportableStream>'''
        
        elif template_name == "job_properties_template.xml":
            return '''<Job>
    <Name>{{JOB_NAME}}</Name>
    <Type>{{JOB_TYPE}}</Type>
    <Agent>{{AGENT}}</Agent>
    <Script>{{SCRIPT}}</Script>
    <Parameters>{{PARAMETERS}}</Parameters>
</Job>'''
        
        else:
            logger.warning(f"No fallback template available for {template_name}")
            return ""
    
    def _get_preview_template(self) -> str:
        """Get simplified preview template based on geck003 structure"""
        return '''<?xml version="1.0" encoding="utf-8"?>
<ExportableStream>
  <Stream>
    <StreamName>{{STREAM_NAME}}</StreamName>
    <StreamDocumentation><![CDATA[{{STREAM_DOCUMENTATION}}]]></StreamDocumentation>
    <AgentDetail>gtasswvk05445</AgentDetail>
    <AccountNoId />
    <CalendarId />
    <StreamType>Normal</StreamType>
    <MaxStreamRuns>5</MaxStreamRuns>
    <ShortDescription><![CDATA[{{SHORT_DESCRIPTION}}]]></ShortDescription>
    <SchedulingRequiredFlag>False</SchedulingRequiredFlag>
    <ScheduleRuleObject />
    
    <Jobs>
      <Job>
        <JobName>{{MAIN_JOB_NAME}}</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[{{JOB_DESCRIPTION}}]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Job</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>{{JOB_TYPE}}</JobType>
        <MainScript><![CDATA[{{MAIN_SCRIPT}}]]></MainScript>
        <DisplayOrder>1</DisplayOrder>
        <TemplateType>Normal</TemplateType>
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>145</CoordinateX>
        <CoordinateY>192</CoordinateY>
      </Job>
    </Jobs>
    
    <StreamContactPersons>
      <StreamContactPerson>
        <FirstName>{{CONTACT_FIRST_NAME}}</FirstName>
        <LastName>{{CONTACT_LAST_NAME}}</LastName>
        <MiddleName />
        <CompanyName>{{CONTACT_COMPANY}}</CompanyName>
        <Department>{{CONTACT_DEPARTMENT}}</Department>
        <ContactType>None</ContactType>
        <HierarchyLevelCd>1</HierarchyLevelCd>
      </StreamContactPerson>
    </StreamContactPersons>
    
    <ScheduleRule>
      <ScheduleRuleXml><![CDATA[&lt;SchedulingRules ShiftRule="3" ScheduleRuleDialogNotYetVisited="1" /&gt;]]></ScheduleRuleXml>
    </ScheduleRule>
    
    <StreamPath><![CDATA[]]></StreamPath>
    <StatusFlag>True</StatusFlag>
  </Stream>
</ExportableStream>'''
    
    def generate_xml(self, wizard_data: WizardFormData, preview_mode: bool = False) -> XMLGenerationResult:
        """
        Generate StreamWorks XML from wizard form data using templates
        
        Args:
            wizard_data: Form data from wizard (can be incomplete)
            preview_mode: If True, generates preview with smart defaults and placeholders
            
        Returns:
            XMLGenerationResult with generated XML content
        """
        try:
            logger.info(f"Generating XML for job type: {wizard_data.job_type}")
            
            # Create replacement dictionary with preview mode
            replacements = self._build_replacements(wizard_data, preview_mode)
            
            # Use different template for preview vs production
            if preview_mode:
                template = self._get_preview_template()
            else:
                template = self.main_template
            
            # Generate XML from template
            xml_content = self._apply_replacements(template, replacements)
            
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
    
    def _build_replacements(self, wizard_data: WizardFormData, preview_mode: bool = False) -> Dict[str, str]:
        """Build dictionary of template placeholders and their replacements"""
        replacements = self.config.get("defaults", {}).copy()
        
        # Stream properties with smart defaults
        stream_props = getattr(wizard_data, 'stream_properties', None)
        
        if preview_mode:
            # Smart defaults for preview mode
            replacements.update({
                "STREAM_NAME": self._get_smart_value(stream_props, 'stream_name', "{{Neuer_Stream}}"),
                "STREAM_DOCUMENTATION": self._get_smart_documentation(stream_props, wizard_data),
                "SHORT_DESCRIPTION": self._get_smart_value(stream_props, 'description', "{{Stream_Beschreibung}}"),
                "CONTACT_FIRST_NAME": self._get_smart_contact_value(stream_props, 'first_name', "{{Vorname}}"),
                "CONTACT_LAST_NAME": self._get_smart_contact_value(stream_props, 'last_name', "{{Nachname}}"),
                "CONTACT_COMPANY": self._get_smart_contact_value(stream_props, 'company', "Arvato Systems"),
                "CONTACT_DEPARTMENT": self._get_smart_contact_value(stream_props, 'department', "{{Abteilung}}"),
                "DEPLOYMENT_DATETIME": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "MAIN_JOB_NAME": self._get_smart_job_name(wizard_data, stream_props),
                "JOB_DESCRIPTION": self._get_smart_job_name(wizard_data, stream_props),
                "JOB_TYPE": "Windows"
            })
        else:
            # Production mode - strict requirements
            if not stream_props:
                raise ValueError("Stream properties are required for production mode")
            
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
        
        # Job-specific replacements with smart defaults
        job_form = getattr(wizard_data, 'job_form', None)
        job_type = getattr(wizard_data, 'job_type', None)
        job_type_config = {}
        
        if job_type:
            job_type_config = self.config.get("job_types", {}).get(job_type.value, {})
        
        # Main job name with smart generation
        replacements["MAIN_JOB_NAME"] = self._get_smart_job_name(wizard_data, stream_props)
        
        # Job description
        if preview_mode:
            replacements["JOB_DESCRIPTION"] = replacements["MAIN_JOB_NAME"]
        else:
            replacements["JOB_DESCRIPTION"] = getattr(job_form, 'job_name', replacements["MAIN_JOB_NAME"]) if job_form else replacements["MAIN_JOB_NAME"]
        
        # Apply job type specific configurations
        replacements.update(job_type_config)
        
        # Job-specific script and extensions
        self._apply_job_specific_replacements(wizard_data, replacements, preview_mode)
        
        # Scheduling
        self._apply_scheduling_replacements(wizard_data, replacements, preview_mode)
        
        # StreamRunJobProperties
        job_properties = self._apply_replacements(self.job_properties_template, replacements)
        replacements["STREAM_RUN_JOB_PROPERTIES"] = job_properties
        
        return replacements
    
    def _apply_job_specific_replacements(self, wizard_data: WizardFormData, replacements: Dict[str, str], preview_mode: bool = False):
        """Apply job type specific replacements"""
        job_form = getattr(wizard_data, 'job_form', None)
        job_type = getattr(wizard_data, 'job_type', None)
        
        if not job_type:
            # No job type selected yet
            if preview_mode:
                replacements["MAIN_SCRIPT"] = "{{Job_Script_hier_einfuegen}}"
            return
        
        if job_type == JobType.STANDARD:
            if job_form and hasattr(job_form, 'script') and job_form.script:
                replacements["MAIN_SCRIPT"] = job_form.script
            elif job_form and isinstance(job_form, dict) and job_form.get('script'):
                replacements["MAIN_SCRIPT"] = job_form['script']
            elif preview_mode:
                replacements["MAIN_SCRIPT"] = "{{Windows_Script_oder_Befehl}}"
            else:
                replacements["MAIN_SCRIPT"] = "echo 'Standard job script'"
                
        elif job_type == JobType.SAP:
            # SAP-specific placeholders
            if job_form and hasattr(job_form, 'system'):
                replacements["SAP_SYSTEM"] = job_form.system
                replacements["SAP_REPORT"] = job_form.report
                replacements["SAP_VARIANT"] = job_form.variant or ""
                replacements["BATCH_USER"] = job_form.batch_user
            elif job_form and isinstance(job_form, dict):
                replacements["SAP_SYSTEM"] = job_form.get('system', 'PA1_100')
                replacements["SAP_REPORT"] = job_form.get('report', 'RBDAGAIN')
                replacements["SAP_VARIANT"] = job_form.get('variant', '')
                replacements["BATCH_USER"] = job_form.get('batchUser', 'Batch_PUR')
            elif preview_mode:
                replacements["SAP_SYSTEM"] = "{{SAP_System}}"
                replacements["SAP_REPORT"] = "{{SAP_Report}}"
                replacements["SAP_VARIANT"] = "{{Variante}}"
                replacements["BATCH_USER"] = "{{Batch_User}}"
            else:
                replacements["SAP_SYSTEM"] = "PA1_100"
                replacements["SAP_REPORT"] = "RBDAGAIN"
                replacements["SAP_VARIANT"] = ""
                replacements["BATCH_USER"] = "Batch_PUR"
            
            replacements["MAIN_SCRIPT"] = ""
            
        elif job_type == JobType.FILE_TRANSFER:
            # File Transfer specific placeholders
            if job_form and hasattr(job_form, 'source_agent'):
                replacements["SOURCE_AGENT"] = job_form.source_agent
                replacements["SOURCE_PATH"] = job_form.source_path
                replacements["TARGET_AGENT"] = job_form.target_agent
                replacements["TARGET_PATH"] = job_form.target_path
            elif job_form and isinstance(job_form, dict):
                replacements["SOURCE_AGENT"] = job_form.get('sourceAgent', '')
                replacements["SOURCE_PATH"] = job_form.get('sourcePath', '')
                replacements["TARGET_AGENT"] = job_form.get('targetAgent', '')
                replacements["TARGET_PATH"] = job_form.get('targetPath', '')
            elif preview_mode:
                replacements["SOURCE_AGENT"] = "{{Quelle_Agent}}"
                replacements["SOURCE_PATH"] = "{{Quelle_Pfad}}"
                replacements["TARGET_AGENT"] = "{{Ziel_Agent}}"
                replacements["TARGET_PATH"] = "{{Ziel_Pfad}}"
            else:
                replacements["SOURCE_AGENT"] = ""
                replacements["SOURCE_PATH"] = ""
                replacements["TARGET_AGENT"] = ""
                replacements["TARGET_PATH"] = ""
            
            replacements["MAIN_SCRIPT"] = ""
        
        # Default empty values for unused placeholders
        placeholders = ["MAIN_SCRIPT", "JOB_NOTIFICATION_RULES", "LOGIN_OBJECT", 
                       "JOB_EXTENSIONS", "PREPARATION_SCRIPT"]
        for placeholder in placeholders:
            if placeholder not in replacements:
                replacements[placeholder] = ""
    
    def _apply_scheduling_replacements(self, wizard_data: WizardFormData, replacements: Dict[str, str], preview_mode: bool = False):
        """Apply scheduling-specific replacements"""
        scheduling = getattr(wizard_data, 'scheduling', None)
        schedule_templates = self.config.get("schedule_templates", {})
        
        if not scheduling:
            if preview_mode:
                replacements["SCHEDULE_RULE_XML"] = "{{Scheduling_noch_konfigurieren}}"
            else:
                replacements["SCHEDULE_RULE_XML"] = schedule_templates.get("manual", "")
            return
        
        if hasattr(scheduling, 'mode') and scheduling.mode.value == "simple" and scheduling.simple:
            preset = scheduling.simple.preset
            if preset in schedule_templates:
                replacements["SCHEDULE_RULE_XML"] = schedule_templates[preset]
            else:
                replacements["SCHEDULE_RULE_XML"] = schedule_templates.get("manual", "")
        elif hasattr(scheduling, 'mode') and scheduling.mode.value == "advanced" and scheduling.advanced and scheduling.advanced.schedule_rule_xml:
            replacements["SCHEDULE_RULE_XML"] = scheduling.advanced.schedule_rule_xml
        else:
            if preview_mode:
                replacements["SCHEDULE_RULE_XML"] = "{{Scheduling_noch_konfigurieren}}"
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
    
    def _get_smart_value(self, obj, attr_name: str, default_placeholder: str) -> str:
        """Get value from object with smart fallback"""
        logger.info(f"_get_smart_value: obj={obj}, attr_name={attr_name}, default={default_placeholder}")
        if obj and hasattr(obj, attr_name):
            value = getattr(obj, attr_name, None)
            logger.info(f"_get_smart_value: found value={value}")
            if value and str(value).strip():
                return str(value)
        return default_placeholder
    
    def _get_smart_contact_value(self, stream_props, attr_name: str, default_placeholder: str) -> str:
        """Get contact person value with smart fallback"""
        if stream_props and hasattr(stream_props, 'contact_person'):
            contact = stream_props.contact_person
            if contact and hasattr(contact, attr_name):
                value = getattr(contact, attr_name, None)
                if value and str(value).strip():
                    return str(value)
        return default_placeholder
    
    def _get_smart_documentation(self, stream_props, wizard_data) -> str:
        """Generate smart documentation from available data"""
        if stream_props:
            if hasattr(stream_props, 'documentation') and stream_props.documentation:
                return stream_props.documentation
            elif hasattr(stream_props, 'description') and stream_props.description:
                return stream_props.description
        
        # Generate from job type
        job_type = getattr(wizard_data, 'job_type', None)
        if job_type:
            return f"{{{{Automatisierter {job_type.value.upper()} Stream}}}}"
        
        return "{{Stream_Dokumentation}}"
    
    def _get_smart_job_name(self, wizard_data, stream_props) -> str:
        """Generate smart job name from available data"""
        job_form = getattr(wizard_data, 'job_form', None)
        
        # Try to get from job form
        if job_form:
            if hasattr(job_form, 'job_name') and job_form.job_name:
                return job_form.job_name
            elif isinstance(job_form, dict) and job_form.get('jobName'):
                return job_form['jobName']
        
        # Generate from stream name
        if stream_props and hasattr(stream_props, 'stream_name') and stream_props.stream_name:
            return f"{stream_props.stream_name}_job"
        
        # Generate from job type
        job_type = getattr(wizard_data, 'job_type', None)
        if job_type:
            return f"{{{{{job_type.value.upper()}_JOB}}}}"
        
        return "{{Job_Name}}"


# Singleton instance
_template_engine = None


def get_template_engine() -> XMLTemplateEngine:
    """Get template engine singleton"""
    global _template_engine
    if _template_engine is None:
        _template_engine = XMLTemplateEngine()
    return _template_engine