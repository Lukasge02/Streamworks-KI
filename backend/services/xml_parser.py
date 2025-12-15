"""
Enterprise-grade XML Parser for Streamworks Export Files
Extracts comprehensive information from Streamworks XML exports for the Wizard.
"""

import xml.etree.ElementTree as ET
import re
from typing import Dict, Any, Optional, List


class XMLParser:
    """
    Comprehensive parser for Streamworks XML export files.
    Extracts all relevant parameters for stream editing and recreation.
    """

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """
        Parse XML content and return a comprehensive dictionary of parameters.

        Returns:
            Dictionary with stream metadata, jobs, and all relevant parameters
        """
        result = {"stream": {}, "jobs": [], "contacts": [], "raw_xml": xml_content}

        try:
            # Remove encoding declaration to avoid parsing errors with strings
            xml_content = re.sub(r"<\?xml.*?\?>", "", xml_content)

            root = ET.fromstring(xml_content)

            # Navigate to Stream node
            stream_node = root.find(".//Stream")
            if stream_node is None:
                if root.tag == "Stream":
                    stream_node = root
                else:
                    return result

            # Extract stream-level information
            result["stream"] = self._parse_stream(stream_node)

            # Extract jobs
            jobs_node = stream_node.find("Jobs")
            if jobs_node is not None:
                for job in jobs_node.findall("Job"):
                    parsed_job = self._parse_job(job)
                    if parsed_job:
                        result["jobs"].append(parsed_job)

            # Extract contacts
            contacts_node = stream_node.find("StreamContactPersons")
            if contacts_node is not None:
                for contact in contacts_node.findall("StreamContactPerson"):
                    parsed_contact = self._parse_contact(contact)
                    if parsed_contact:
                        result["contacts"].append(parsed_contact)

            # Determine overall job type based on jobs
            result["detected_job_type"] = self._detect_job_type(result["jobs"])

            # Create flat params for backward compatibility with wizard
            result["params"] = self._create_wizard_params(result)

            return result

        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            return result
        except Exception as e:
            print(f"General Parse Error: {e}")
            import traceback

            traceback.print_exc()
            return result

    def _parse_stream(self, stream_node) -> Dict[str, Any]:
        """Extract stream-level metadata"""
        stream = {}

        # Basic info
        stream["name"] = self._get_text(stream_node, "StreamName")
        stream["short_description"] = self._clean_cdata(
            self._get_text(stream_node, "ShortDescription")
        )
        stream["documentation"] = self._clean_cdata(
            self._get_text(stream_node, "StreamDocumentation")
        )
        stream["agent_detail"] = self._get_text(stream_node, "AgentDetail")
        stream["stream_type"] = self._get_text(stream_node, "StreamType")
        stream["stream_path"] = self._clean_cdata(
            self._get_text(stream_node, "StreamPath")
        )

        # Configuration
        stream["max_stream_runs"] = self._get_text(stream_node, "MaxStreamRuns")
        stream["scheduling_required"] = self._get_text(
            stream_node, "SchedulingRequiredFlag"
        )
        stream["status_flag"] = self._get_text(stream_node, "StatusFlag")
        stream["interactive_psl_flag"] = self._get_text(
            stream_node, "InteractivePslFlag"
        )

        # Runtime settings
        stream["runtime_data_storage_days"] = self._get_nullable_text(
            stream_node, "RuntimeDataStorageDays"
        )
        stream["central_job_log_storage_days"] = self._get_nullable_text(
            stream_node, "CentralJobLogStorageDays"
        )
        stream["agent_job_log_storage_days"] = self._get_nullable_text(
            stream_node, "AgentJobLogStorageDays"
        )
        stream["max_job_log_size"] = self._get_nullable_text(
            stream_node, "MaxJobLogSize"
        )

        # Version info
        version_node = stream_node.find("StreamVersionDetail")
        if version_node is not None:
            stream["version"] = self._get_text(version_node, "StreamVersion")
            stream["version_type"] = self._get_text(version_node, "StreamVersionType")
            stream["deployment_datetime"] = self._get_text(
                version_node, "DeploymentDateTime"
            )

        # Preparation script
        prep_script_node = stream_node.find("StreamPreparationScript")
        if prep_script_node is not None:
            stream["preparation_script"] = self._clean_cdata(
                self._get_text(prep_script_node, "Script")
            )
            stream["preparation_script_language"] = self._get_text(
                prep_script_node, "ScriptLanguage"
            )

        # Schedule rule
        schedule_node = stream_node.find("ScheduleRule")
        if schedule_node is not None:
            stream["schedule_rule_xml"] = self._clean_cdata(
                self._get_text(schedule_node, "ScheduleRuleXml")
            )

        return {k: v for k, v in stream.items() if v is not None}

    def _parse_job(self, job_node) -> Dict[str, Any]:
        """Extract job-level information"""
        job = {}

        # Basic info
        job["name"] = self._get_text(job_node, "JobName")
        job["short_description"] = self._clean_cdata(
            self._get_text(job_node, "ShortDescription")
        )
        job["documentation"] = self._clean_cdata(
            self._get_nullable_text(job_node, "JobDocumentation")
        )
        job["category"] = self._get_text(job_node, "JobCategory")
        job["job_type"] = self._get_text(job_node, "JobType")
        job["template_type"] = self._get_text(job_node, "TemplateType")
        job["status_flag"] = self._get_text(job_node, "StatusFlag")
        job["normal_job_flag"] = self._get_text(job_node, "NormalJobFlag")
        job["display_order"] = self._get_text(job_node, "DisplayOrder")

        # Position
        job["coordinate_x"] = self._get_text(job_node, "CoordinateX")
        job["coordinate_y"] = self._get_text(job_node, "CoordinateY")

        # Script
        job["main_script"] = self._clean_cdata(
            self._get_nullable_text(job_node, "MainScript")
        )

        # Successors (job flow)
        successors_node = job_node.find("JobInternalSuccessors")
        if successors_node is not None:
            job["successors"] = []
            for succ in successors_node.findall("JobInternalSuccessor"):
                succ_name = self._get_text(succ, "JobName")
                if succ_name:
                    job["successors"].append(succ_name)

        # File Transfer properties (for FileTransfer jobs)
        ft_node = job_node.find("JobFileTransferProperty")
        if ft_node is not None:
            job["file_transfer"] = self._parse_file_transfer(ft_node)
            job["is_file_transfer"] = True
        else:
            job["is_file_transfer"] = False

        # Run properties (agent details per run, etc.)
        run_props = job_node.find("StreamRunJobProperties")
        if run_props is not None:
            first_run = run_props.find("StreamRunJobProperty")
            if first_run is not None:
                job["agent_detail"] = self._get_text(first_run, "AgentDetail")
                job["account_detail"] = self._get_text(first_run, "AccountDetail")
                job["severity_group"] = self._get_text(first_run, "SeverityGroup")
                job["start_time"] = self._get_nullable_text(first_run, "StartTime")
                job["max_job_duration"] = self._get_nullable_text(
                    first_run, "MaxJobDuration"
                )

        return {k: v for k, v in job.items() if v is not None}

    def _parse_file_transfer(self, ft_node) -> Dict[str, Any]:
        """Extract file transfer properties"""
        ft = {}

        ft["source_agent"] = self._get_text(ft_node, "SourceAgent")
        ft["target_agent"] = self._get_text(ft_node, "TargetAgent")
        ft["source_login"] = self._get_text(ft_node, "SourceLoginObject")
        ft["target_login"] = self._get_text(ft_node, "TargetLoginObject")

        # File definitions
        defs_node = ft_node.find("FileTransferDefinitions")
        if defs_node is not None:
            ft["definitions"] = []
            for defn in defs_node.findall("FileTransferDefinition"):
                file_def = {
                    "position": self._get_text(defn, "PositionNo"),
                    "source_file_pattern": self._clean_cdata(
                        self._get_text(defn, "SourceFilePattern")
                    ),
                    "target_file_path": self._clean_cdata(
                        self._get_text(defn, "TargetFilePath")
                    ),
                    "target_file_name": self._clean_cdata(
                        self._get_text(defn, "TargetFileName")
                    ),
                    "source_unfulfilled_handling": self._get_text(
                        defn, "SourceUnfulfilledHandling"
                    ),
                    "source_file_delete": self._get_text(defn, "SourceFileDeleteFlag"),
                    "target_exists_handling": self._get_text(
                        defn, "TargetFileExistsHandling"
                    ),
                    "source_encoding": self._get_text(defn, "SourceEncodingDetail"),
                    "target_encoding": self._get_text(defn, "TargetEncodingDetail"),
                    "linebreak_translation": self._get_text(
                        defn, "LinebreakTranslationType"
                    ),
                }
                ft["definitions"].append({k: v for k, v in file_def.items() if v})

        return {k: v for k, v in ft.items() if v is not None}

    def _parse_contact(self, contact_node) -> Dict[str, Any]:
        """Extract contact person information"""
        return {
            "first_name": self._get_text(contact_node, "FirstName"),
            "last_name": self._get_text(contact_node, "LastName"),
            "company": self._get_text(contact_node, "CompanyName"),
            "department": self._get_text(contact_node, "Department"),
            "contact_type": self._get_text(contact_node, "ContactType"),
        }

    def _detect_job_type(self, jobs: List[Dict]) -> str:
        """Determine the primary job type from the jobs list"""
        # First pass: check for FileTransfer jobs (highest priority)
        for job in jobs:
            if job.get("category") in [
                "StartPoint",
                "Endpoint",
                "RecoveryJobNetStartPoint",
                "RecoveryJobNetEndPoint",
            ]:
                continue
            if (
                job.get("is_file_transfer")
                or job.get("template_type") == "FileTransfer"
            ):
                return "FILE_TRANSFER"

        # Second pass: check for specific job types
        for job in jobs:
            if job.get("category") in [
                "StartPoint",
                "Endpoint",
                "RecoveryJobNetStartPoint",
                "RecoveryJobNetEndPoint",
            ]:
                continue

            job_type = job.get("job_type", "").upper()
            if job_type == "WINDOWS":
                return "WINDOWS"
            elif job_type == "UNIX":
                return "UNIX"
            elif "SAP" in job_type:
                return "SAP"

        return "STANDARD"

    def _create_wizard_params(self, result: Dict) -> Dict[str, Any]:
        """Create flat parameters dictionary for wizard compatibility"""
        stream = result.get("stream", {})
        jobs = result.get("jobs", [])

        params = {
            "stream_name": stream.get("name"),
            "short_description": stream.get("short_description"),
            "stream_documentation": stream.get("documentation"),
            "agent_detail": stream.get("agent_detail"),
            "stream_path": stream.get("stream_path"),
            "job_type": result.get("detected_job_type", "STANDARD"),
        }

        # Find the main job (not StartPoint/EndPoint)
        main_job = None
        for job in jobs:
            if job.get("category") == "Job" and job.get("normal_job_flag") == "True":
                main_job = job
                break

        if main_job:
            params["main_script"] = main_job.get("main_script")
            params["job_name"] = main_job.get("name")
            params["job_description"] = main_job.get("short_description")

            # FileTransfer specific
            ft = main_job.get("file_transfer")
            if ft:
                params["source_agent"] = ft.get("source_agent")
                params["target_agent"] = ft.get("target_agent")

                defs = ft.get("definitions", [])
                if defs:
                    params["source_path"] = defs[0].get("source_file_pattern")
                    params["target_path"] = defs[0].get("target_file_path")

        # Contact info
        contacts = result.get("contacts", [])
        if contacts:
            params["contact_name"] = (
                f"{contacts[0].get('first_name', '')} {contacts[0].get('last_name', '')}".strip()
            )
            params["contact_company"] = contacts[0].get("company")

        return {k: v for k, v in params.items() if v is not None}

    def _get_text(self, node, tag_name: str) -> Optional[str]:
        """Get text content of a child element"""
        found = node.find(tag_name)
        if found is not None and found.text:
            return found.text.strip()
        return None

    def _get_nullable_text(self, node, tag_name: str) -> Optional[str]:
        """Get text content, returning None if IsNull='True'"""
        found = node.find(tag_name)
        if found is not None:
            if found.get("IsNull") == "True":
                return None
            if found.text:
                return found.text.strip()
        return None

    def _clean_cdata(self, text: Optional[str]) -> Optional[str]:
        """Remove CDATA wrapper if present"""
        if text is None:
            return None
        text = text.replace("<![CDATA[", "").replace("]]>", "")
        return text.strip() if text.strip() else None


# Global parser instance
xml_parser = XMLParser()
