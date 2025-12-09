"""
Chat Service - Kernlogik für Parameterextraktion und Konversation
"""
from typing import Dict, Any, List, Optional
from services.ai.parameter_extractor import ParameterExtractor
from services.ai.schemas import StreamworksParams


class ChatService:
    """Service for handling chat logic and parameter extraction"""
    
    def __init__(self):
        self._extractor: Optional[ParameterExtractor] = None
    
    @property
    def extractor(self) -> ParameterExtractor:
        """Lazy loading of extractor"""
        if self._extractor is None:
            self._extractor = ParameterExtractor()
        return self._extractor
    
    def process_message(
        self,
        message: str,
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a user message and extract parameters
        
        Returns dict with:
        - extraction: StreamworksParams
        - params: merged parameters
        - job_type: detected job type
        - completion: completion percentage
        - response: AI response text
        """
        # Add user message to history
        session["messages"].append({"role": "user", "content": message})
        
        # Extract parameters
        extraction = self.extractor.extract(
            message=message,
            conversation_history=session["messages"][-6:],
            existing_params=session["params"]
        )
        
        # Merge with existing params
        merged_params = self.extractor.merge_params(
            session["params"],
            extraction
        )
        
        # Calculate completion
        completion = self._calculate_completion(
            extraction.job_type,
            merged_params,
            extraction.missing_required
        )
        
        # Generate response
        if extraction.missing_required:
            response = extraction.follow_up_question or self._generate_response(
                extraction,
                merged_params
            )
        else:
            response = "✅ Alle Parameter wurden erfasst! Sie können jetzt die XML generieren."
        
        # Add AI response to history
        session["messages"].append({"role": "assistant", "content": response})
        
        return {
            "extraction": extraction,
            "params": merged_params,
            "job_type": extraction.job_type,
            "completion": completion,
            "response": response,
            "confidence": extraction.confidence
        }
    
    def _calculate_completion(
        self, 
        job_type: str, 
        params: Dict, 
        missing: List[str]
    ) -> float:
        """Calculate completion percentage based on job type requirements"""
        required_fields = {
            "FILE_TRANSFER": ["stream_name", "source_agent", "target_agent", "source_file_pattern"],
            "STANDARD": ["stream_name", "agent_detail", "main_script"],
            "SAP": ["stream_name", "sap_report"]
        }
        
        required = required_fields.get(job_type, ["stream_name"])
        
        if not required:
            return 100.0
        
        completed = sum(1 for field in required if params.get(field))
        return (completed / len(required)) * 100
    
    def _generate_response(
        self,
        extraction: StreamworksParams,
        params: Dict
    ) -> str:
        """Generate a helpful response based on extraction results"""
        job_names = {
            "FILE_TRANSFER": "Dateitransfer",
            "STANDARD": "Standard-Job",
            "SAP": "SAP-Job"
        }
        
        job_name = job_names.get(extraction.job_type, "Job")
        response_parts = [f"Ich habe einen **{job_name}** erkannt."]
        
        # Show what was extracted
        extracted = []
        if params.get("stream_name"):
            extracted.append(f"Stream: {params['stream_name']}")
        if params.get("source_agent"):
            extracted.append(f"Quelle: {params['source_agent']}")
        if params.get("target_agent"):
            extracted.append(f"Ziel: {params['target_agent']}")
        if params.get("agent_detail"):
            extracted.append(f"Agent: {params['agent_detail']}")
        if params.get("schedule"):
            extracted.append(f"Zeitplan: {params['schedule']}")
        
        if extracted:
            response_parts.append("\n\n**Erkannt:**\n• " + "\n• ".join(extracted))
        
        # Add follow-up question
        if extraction.follow_up_question:
            response_parts.append(f"\n\n{extraction.follow_up_question}")
        
        return "".join(response_parts)


# Global service instance
chat_service = ChatService()
