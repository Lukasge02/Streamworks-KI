"""
Simple Stream Service for Streamworks Self-Service Portal
Focuses on practical stream creation with minimal complexity
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import json
from openai import AsyncOpenAI
import os

class SimpleStreamService:
    """Service for creating Streamworks streams from simple forms"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Common values from analyzed XMLs
        self.common_values = {
            "agents": ["TestAgent1", "gtasswvu15777", "gtegklvj14128"],
            "systems": ["PA1_100", "HP1_ERP", "QA1_200"],
            "reports": ["RBDAGAIN", "ZESGHR01", "ZWM_TO_CREATE", "RSNAST00"],
            "variants": ["ZXY-UFA", "0100_NEST_DEL", "STANDARD"],
            "users": ["Batch_PUR", "HPH_BATCH", "ggapcadm", "sapbatch"],
            "calendars": ["Default Calendar", "GER-HET-10", "SAP-FACTORY-DE"],
            "intervals": ["5min", "10min", "15min", "30min", "1h", "daily"],
        }
    
    async def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language request into structured form data
        Example: "Ich brauche RBDAGAIN alle 15 Min von 5:30 bis 23:00"
        """
        
        # Use GPT-3.5 for simple extraction
        prompt = f"""
        Extract stream requirements from this text and return as JSON:
        
        Text: "{text}"
        
        Look for:
        - Reports/Programs (e.g., RBDAGAIN, ZESGHR01)
        - Systems (e.g., PA1_100, HP1)
        - Intervals (e.g., "alle 15 Minuten", "täglich")
        - Time ranges (e.g., "von 5:30 bis 23:00")
        - Users (e.g., Batch_PUR, sapbatch)
        - Variants (e.g., ZXY-UFA)
        - Dependencies (e.g., "nach Job X")
        
        Return JSON with these fields (use null if not found):
        {{
            "report": "REPORT_NAME",
            "system": "SYSTEM_NAME",
            "variant": "VARIANT_NAME",
            "interval": "15min",
            "timeframe_start": "05:30",
            "timeframe_end": "23:00",
            "user": "USER_NAME",
            "predecessor": "JOB_NAME"
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a parser for Streamworks requirements. Extract structured data from German or English text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Add defaults for missing required fields
            if not result.get("stream_name"):
                # Generate name from report/system
                report = result.get("report", "JOB")
                system = result.get("system", "SYS")
                timestamp = datetime.now().strftime("%Y%m%d")
                result["stream_name"] = f"CUST-{system}-{report}-{timestamp}"
            
            return result
            
        except Exception as e:
            print(f"Error parsing natural language: {e}")
            return {}
    
    def suggest_values(self, field: str, context: Dict = None) -> List[str]:
        """
        Suggest common values for form fields based on analysis
        """
        suggestions = {
            "agent": self.common_values["agents"],
            "system": self.common_values["systems"],
            "report": self.common_values["reports"],
            "variant": self.common_values["variants"],
            "user": self.common_values["users"],
            "calendar": self.common_values["calendars"],
            "interval": self.common_values["intervals"],
        }
        
        # Context-aware suggestions
        if context and field == "variant":
            report = context.get("report", "").upper()
            if report == "RBDAGAIN":
                return ["ZXY-UFA", "0100_NEST_DEL", "STANDARD"]
            elif report == "RSNAST00":
                return ["OUTPUT_DAILY", "OUTPUT_IMMEDIATE", "STANDARD"]
        
        if context and field == "user":
            system = context.get("system", "")
            if "PA1" in system:
                return ["Batch_PUR", "sapbatch_pa1"]
            elif "HP1" in system:
                return ["HPH_BATCH", "sapbatch_hp1"]
        
        return suggestions.get(field, [])
    
    def validate_form_data(self, data: Dict) -> tuple[bool, List[str]]:
        """
        Validate form data before XML generation
        Returns (is_valid, error_messages)
        """
        errors = []
        
        # Required fields
        if not data.get("stream_name"):
            errors.append("Stream name is required")
        
        if not data.get("jobs") or len(data["jobs"]) == 0:
            errors.append("At least one job is required")
        
        # Validate job data
        for i, job in enumerate(data.get("jobs", [])):
            if job["type"] == "sap":
                if not job.get("report"):
                    errors.append(f"Job {i+1}: SAP Report is required")
                if not job.get("system"):
                    errors.append(f"Job {i+1}: System is required")
            elif job["type"] in ["unix", "windows", "powershell"]:
                if not job.get("script"):
                    errors.append(f"Job {i+1}: Script is required")
        
        # Validate schedule
        schedule = data.get("schedule", {})
        if schedule.get("interval"):
            # Check interval format
            if not re.match(r"^\d+(min|h|d)$|^daily$|^weekly$", schedule["interval"]):
                errors.append("Invalid interval format (use: 15min, 1h, daily, etc.)")
        
        return len(errors) == 0, errors
    
    def prepare_xml_data(self, form_data: Dict) -> Dict:
        """
        Prepare and enrich form data for XML generation
        """
        # Add defaults
        prepared = {
            "stream_name": form_data.get("stream_name", f"STREAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "description": form_data.get("description", "Streamworks Self-Service Stream"),
            "agent": form_data.get("agent", "TestAgent1"),
            "contact": form_data.get("contact", ""),
            "jobs": [],
            "schedule": form_data.get("schedule", {}),
            "error_action": form_data.get("error_action", "BYPASS"),
            "notify": form_data.get("notify", "")
        }
        
        # Process jobs
        for i, job in enumerate(form_data.get("jobs", [])):
            processed_job = {
                "name": job.get("name") or f"00{i+1}0-{prepared['stream_name']}",
                "type": job["type"],
                "category": "Job",  # StartPoint and EndPoint are added automatically
                **job
            }
            prepared["jobs"].append(processed_job)
        
        # Add schedule defaults
        if prepared["schedule"].get("interval"):
            if not prepared["schedule"].get("startTime"):
                prepared["schedule"]["startTime"] = "06:00"
            if not prepared["schedule"].get("weekends"):
                prepared["schedule"]["weekends"] = True
        
        return prepared