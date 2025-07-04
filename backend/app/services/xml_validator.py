"""
StreamWorks XML Validator Service
Validates XML streams against StreamWorks schema and best practices
"""
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationResult:
    """Result of XML validation"""
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None, suggestions: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.suggestions = suggestions or []
    
    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }

class StreamWorksXMLValidator:
    """Validator for StreamWorks XML configurations"""
    
    def __init__(self):
        # Define required elements for a valid StreamWorks stream
        self.required_elements = ["stream", "name", "schedule"]
        self.valid_schedule_types = ["daily", "weekly", "monthly", "once", "continuous"]
        self.valid_task_types = ["batch", "powershell", "python", "copy", "delete"]
        
        logger.info("🔍 StreamWorks XML Validator initialized")
    
    async def validate_stream(self, xml_content: str) -> ValidationResult:
        """
        Validate XML stream against StreamWorks schema and best practices
        
        Args:
            xml_content: XML string to validate
            
        Returns:
            ValidationResult with errors, warnings, and suggestions
        """
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # 1. Structural Validation
            structural_errors = self._validate_structure(root)
            errors.extend(structural_errors)
            
            # 2. Schema Validation
            schema_errors = self._validate_schema(root)
            errors.extend(schema_errors)
            
            # 3. Business Rules Validation
            rule_errors, rule_warnings = self._validate_business_rules(root)
            errors.extend(rule_errors)
            warnings.extend(rule_warnings)
            
            # 4. Best Practices Check
            practice_warnings, practice_suggestions = self._check_best_practices(root)
            warnings.extend(practice_warnings)
            suggestions.extend(practice_suggestions)
            
            # 5. Performance Optimization Suggestions
            perf_suggestions = self._suggest_performance_improvements(root)
            suggestions.extend(perf_suggestions)
            
        except ET.ParseError as e:
            errors.append(f"XML Parse Error: {str(e)}")
        except Exception as e:
            errors.append(f"Validation Error: {str(e)}")
        
        is_valid = len(errors) == 0
        
        logger.info(f"✅ XML Validation complete: {'VALID' if is_valid else 'INVALID'} ({len(errors)} errors, {len(warnings)} warnings)")
        
        return ValidationResult(is_valid, errors, warnings, suggestions)
    
    def _validate_structure(self, root: ET.Element) -> List[str]:
        """Validate basic XML structure"""
        errors = []
        
        # Check root element
        if root.tag != "stream":
            errors.append("Root element must be 'stream'")
        
        # Check required elements
        for element in self.required_elements[1:]:  # Skip 'stream' as it's the root
            if root.find(element) is None:
                errors.append(f"Required element '{element}' is missing")
        
        return errors
    
    def _validate_schema(self, root: ET.Element) -> List[str]:
        """Validate against StreamWorks schema rules"""
        errors = []
        
        # Validate stream name
        name_elem = root.find("name")
        if name_elem is not None and name_elem.text:
            if not re.match(r'^[a-zA-Z0-9_-]+$', name_elem.text):
                errors.append("Stream name must contain only alphanumeric characters, underscores, and hyphens")
            if len(name_elem.text) > 50:
                errors.append("Stream name must not exceed 50 characters")
        
        # Validate schedule
        schedule_elem = root.find("schedule")
        if schedule_elem is not None:
            schedule_type = schedule_elem.find("type")
            if schedule_type is not None and schedule_type.text:
                if schedule_type.text not in self.valid_schedule_types:
                    errors.append(f"Invalid schedule type '{schedule_type.text}'. Must be one of: {', '.join(self.valid_schedule_types)}")
                
                # Validate schedule-specific requirements
                if schedule_type.text == "daily":
                    time_elem = schedule_elem.find("time")
                    if time_elem is None:
                        errors.append("Daily schedule requires 'time' element")
                    elif not self._validate_time_format(time_elem.text):
                        errors.append("Time must be in HH:MM format")
                
                elif schedule_type.text == "weekly":
                    day_elem = schedule_elem.find("day")
                    if day_elem is None:
                        errors.append("Weekly schedule requires 'day' element")
        
        # Validate tasks
        tasks_elem = root.find("tasks")
        if tasks_elem is not None:
            for task in tasks_elem.findall("task"):
                task_type = task.get("type")
                if task_type and task_type not in self.valid_task_types:
                    errors.append(f"Invalid task type '{task_type}'. Must be one of: {', '.join(self.valid_task_types)}")
                
                # Task-specific validation
                if task_type == "batch" or task_type == "powershell":
                    if task.find("command") is None:
                        errors.append(f"{task_type} task requires 'command' element")
        
        return errors
    
    def _validate_business_rules(self, root: ET.Element) -> Tuple[List[str], List[str]]:
        """Validate StreamWorks business rules"""
        errors = []
        warnings = []
        
        # Check for duplicate task names
        tasks_elem = root.find("tasks")
        if tasks_elem is not None:
            task_names = []
            for task in tasks_elem.findall("task"):
                name = task.get("name")
                if name:
                    if name in task_names:
                        errors.append(f"Duplicate task name '{name}'")
                    task_names.append(name)
        
        # Check for conflicting schedules
        schedule_elem = root.find("schedule")
        if schedule_elem is not None:
            schedule_type = schedule_elem.find("type")
            if schedule_type is not None and schedule_type.text == "continuous":
                if tasks_elem and len(tasks_elem.findall("task")) > 5:
                    warnings.append("Continuous schedule with more than 5 tasks may impact performance")
        
        # Check dependencies
        if tasks_elem is not None:
            for task in tasks_elem.findall("task"):
                depends_on = task.find("depends_on")
                if depends_on is not None and depends_on.text:
                    if depends_on.text not in task_names:
                        errors.append(f"Task dependency '{depends_on.text}' not found")
        
        return errors, warnings
    
    def _check_best_practices(self, root: ET.Element) -> Tuple[List[str], List[str]]:
        """Check for StreamWorks best practices"""
        warnings = []
        suggestions = []
        
        # Check for description
        if root.find("description") is None:
            suggestions.append("Consider adding a 'description' element to document the stream's purpose")
        
        # Check for error handling
        tasks_elem = root.find("tasks")
        if tasks_elem is not None:
            has_error_handling = False
            for task in tasks_elem.findall("task"):
                if task.find("on_error") is not None:
                    has_error_handling = True
                    break
            
            if not has_error_handling:
                suggestions.append("Consider adding error handling with 'on_error' elements in tasks")
        
        # Check for logging configuration
        if root.find("logging") is None:
            suggestions.append("Consider adding a 'logging' element to configure stream logging")
        
        # Check for resource limits
        if root.find("resources") is None:
            warnings.append("No resource limits defined. Consider adding 'resources' element for better resource management")
        
        return warnings, suggestions
    
    def _suggest_performance_improvements(self, root: ET.Element) -> List[str]:
        """Suggest performance optimizations"""
        suggestions = []
        
        # Check for parallel execution opportunities
        tasks_elem = root.find("tasks")
        if tasks_elem is not None:
            tasks = tasks_elem.findall("task")
            if len(tasks) > 3:
                has_parallel = any(task.find("parallel") is not None for task in tasks)
                if not has_parallel:
                    suggestions.append("Consider using parallel task execution for better performance with multiple tasks")
        
        # Check for batch size optimization
        for task in root.findall(".//task[@type='batch']"):
            batch_size = task.find("batch_size")
            if batch_size is None:
                suggestions.append("Consider setting 'batch_size' for batch tasks to optimize processing")
        
        # Check for caching opportunities
        schedule_elem = root.find("schedule")
        if schedule_elem is not None:
            schedule_type = schedule_elem.find("type")
            if schedule_type is not None and schedule_type.text in ["daily", "continuous"]:
                if root.find("cache") is None:
                    suggestions.append("Consider enabling caching for frequently running streams")
        
        return suggestions
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format HH:MM"""
        if not time_str:
            return False
        
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except:
            return False
    
    async def suggest_improvements(self, xml_content: str) -> List[str]:
        """
        Analyze XML and suggest improvements
        
        Args:
            xml_content: XML string to analyze
            
        Returns:
            List of improvement suggestions
        """
        validation_result = await self.validate_stream(xml_content)
        
        all_suggestions = []
        
        # Add validation suggestions
        all_suggestions.extend(validation_result.suggestions)
        
        try:
            root = ET.fromstring(xml_content)
            
            # Additional context-aware suggestions
            context_suggestions = self._get_context_suggestions(root)
            all_suggestions.extend(context_suggestions)
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
        
        return all_suggestions
    
    def _get_context_suggestions(self, root: ET.Element) -> List[str]:
        """Get context-specific suggestions"""
        suggestions = []
        
        # Analyze stream purpose and suggest optimizations
        name_elem = root.find("name")
        if name_elem is not None and name_elem.text:
            name_lower = name_elem.text.lower()
            
            if "backup" in name_lower or "archive" in name_lower:
                suggestions.append("For backup streams, consider adding compression and retention policies")
            
            elif "etl" in name_lower or "transform" in name_lower:
                suggestions.append("For ETL streams, consider adding data validation and transformation error handling")
            
            elif "monitor" in name_lower or "check" in name_lower:
                suggestions.append("For monitoring streams, consider adding alerting and notification configurations")
        
        return suggestions
    
    def create_template(self, stream_type: str) -> str:
        """Create a template XML for common stream types"""
        templates = {
            "daily_batch": """<stream>
    <name>daily_batch_processing</name>
    <description>Daily batch processing stream</description>
    <schedule>
        <type>daily</type>
        <time>02:00</time>
    </schedule>
    <tasks>
        <task type="batch" name="process_data">
            <command>process_daily_data.bat</command>
            <workingDirectory>C:\\StreamWorks\\Jobs</workingDirectory>
            <on_error>continue</on_error>
        </task>
    </tasks>
    <logging>
        <level>INFO</level>
        <path>C:\\StreamWorks\\Logs</path>
    </logging>
</stream>""",
            
            "continuous_monitor": """<stream>
    <name>continuous_monitoring</name>
    <description>Continuous system monitoring</description>
    <schedule>
        <type>continuous</type>
        <interval>300</interval> <!-- 5 minutes -->
    </schedule>
    <tasks>
        <task type="powershell" name="check_system">
            <command>Check-SystemHealth.ps1</command>
            <timeout>60</timeout>
        </task>
    </tasks>
    <alerts>
        <email>admin@company.com</email>
    </alerts>
</stream>""",
            
            "weekly_report": """<stream>
    <name>weekly_report_generation</name>
    <description>Weekly report generation and distribution</description>
    <schedule>
        <type>weekly</type>
        <day>Monday</day>
        <time>08:00</time>
    </schedule>
    <tasks>
        <task type="python" name="generate_report">
            <script>generate_weekly_report.py</script>
            <parameters>
                <start_date>-7d</start_date>
                <end_date>today</end_date>
            </parameters>
        </task>
        <task type="batch" name="send_report" depends_on="generate_report">
            <command>send_report.bat</command>
        </task>
    </tasks>
</stream>"""
        }
        
        return templates.get(stream_type, templates["daily_batch"])

# Global instance
xml_validator = StreamWorksXMLValidator()