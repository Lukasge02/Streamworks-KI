
import xml.etree.ElementTree as ET
import re
from typing import Dict, Any, Optional

class XMLParser:
    """
    Parses Streamworks XML files to extract parameters for the Wizard.
    """
    
    def parse(self, xml_content: str) -> Dict[str, Any]:
        """
        Parse XML content and return a dictionary of parameters.
        """
        params = {}
        
        try:
            # Remove encoding declaration if present to avoid parsing errors with strings
            xml_content = re.sub(r'<\?xml.*?\?>', '', xml_content)
            
            root = ET.fromstring(xml_content)
            
            # Navigate to Stream node
            # Structure: <ExportableStream><Stream>...
            stream_node = root.find('.//Stream')
            if stream_node is None:
                # Try simple root if it's just <Stream>
                if root.tag == 'Stream':
                    stream_node = root
                else:
                    return params # No valid stream found
            
            # --- Extract Basic Info ---
            params['stream_name'] = self._get_text(stream_node, 'StreamName')
            params['short_description'] = self._get_text(stream_node, 'ShortDescription')
            
            # Clean up description (remove CDATA wrapper if manual parse missed it, though ET handles it)
            if params['short_description']:
                 params['short_description'] = params['short_description'].replace("<![CDATA[", "").replace("]]>", "")
                 
            # StreamDocumentation often in CDATA
            params['stream_documentation'] = self._get_text(stream_node, 'StreamDocumentation')
            
            
            # --- Heuristics for Job Type & Details ---
            
            # 1. FILE_TRANSFER Detection
            # Look for FileTransfer specific tags or meaningful Agent/Path combinations
            # In our generator: standard uses AgentDetail, FT uses SourceAgent/TargetAgent which are actually 
            # RuntimeDataStorageDaysSource IsNull="True" ?? No.
            # Let's look at geck003_ft.xml structure.
            # It puts source/target stuff in... Wait. The Standard XML doesn't have explicit "SourceAgent" tag in the root <Stream> usually.
            # It uses <StreamSteps> or specific child nodes. 
            # BUT, our `master_template.xml` flattened things or used specific custom mapping?
            # Let's check `master_template.xml` to see where we put SourceAgent.
            
            # Checking master_template.xml logic:
            # It maps:
            # <AgentDetail>{{ params.agent_detail }}</AgentDetail> (Standard)
            # For FileTransfers, Streamworks usually uses a specific Job Type or Step. 
            # BUT our `XMLGenerator` implementation might be simplifying things.
            # Let's try to extract what we can find.
            
            params['agent_detail'] = self._get_text(stream_node, 'AgentDetail')
            
            # If we see "SAP" in valid tags or names, hint SAP
            if "SAP" in (params.get('stream_name') or ""):
                params['job_type'] = "SAP"
            elif self._get_text(stream_node, 'JobType') == "FileTransfer": # Hypothetical
                 params['job_type'] = "FILE_TRANSFER"
            else:
                 params['job_type'] = "STANDARD" # Default
                 
            # Note: A real robust parser would need to dive into <Job> or <Step> children 
            # which are complex in Streamworks. 
            # For now, we extract the basics that match our high-level wizard params.
            
            return {k: v for k, v in params.items() if v is not None}
            
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            return {}
        except Exception as e:
            print(f"General Parse Error: {e}")
            return {}

    def _get_text(self, node, tag_name) -> Optional[str]:
        """Helper to get text content safely"""
        found = node.find(tag_name)
        return found.text if found is not None else None
