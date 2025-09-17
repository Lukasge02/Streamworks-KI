"""
Hybrid Entity Recognition System
Combines Template-based Recognition with LLM Fallback for Maximum Accuracy
"""
import re
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from services.conversation_engine import ConversationEngine, ExtractedEntity
from services.ollama_service import OllamaService
from services.llm_factory import get_llm_service
from services.ai_response_cache import get_cached_ai_response, cache_ai_response
from schemas.xml_streams import JobType

logger = logging.getLogger(__name__)

@dataclass
class RecognitionResult:
    """Result from hybrid recognition"""
    job_type: Optional[JobType]
    confidence: float
    method: str  # 'template', 'llm', 'hybrid'
    entities: List[ExtractedEntity]
    reasoning: Optional[str] = None
    fallback_used: bool = False

class RecognitionMethod(Enum):
    """Available recognition methods"""
    TEMPLATE_ONLY = "template"
    LLM_FALLBACK = "llm"
    HYBRID_CONSENSUS = "hybrid"

class HybridEntityRecognizer:
    """
    Professional-grade hybrid entity recognition system
    Combines template-based patterns with LLM intelligence
    """

    def __init__(self,
                 conversation_engine: Optional[ConversationEngine] = None,
                 ollama_service: Optional[OllamaService] = None,
                 template_config_path: Optional[str] = None):
        """Initialize with all recognition components"""

        # Initialize conversation engine for template-based recognition
        self.conversation_engine = conversation_engine or ConversationEngine(template_config_path)

        # Initialize Ollama service for LLM fallback (legacy support)
        self.ollama_service = ollama_service

        # Initialize LLM service (OpenAI/Ollama via factory)
        self.llm_service = None  # Will be initialized on first use

        # Configuration
        self.template_config = self.conversation_engine.template_config
        self.confidence_threshold = 0.3
        self.hybrid_threshold = 0.2  # When to use hybrid approach

        # Recognition statistics
        self.stats = {
            'total_requests': 0,
            'template_success': 0,
            'llm_fallback': 0,
            'hybrid_consensus': 0,
            'recognition_failures': 0
        }

        logger.info("🔥 HybridEntityRecognizer initialized successfully with OpenAI integration")

    async def recognize(self,
                       message: str,
                       context: Optional[List[Dict]] = None,
                       method: RecognitionMethod = RecognitionMethod.HYBRID_CONSENSUS) -> RecognitionResult:
        """
        Main recognition method with multiple strategies
        """
        self.stats['total_requests'] += 1

        try:
            if method == RecognitionMethod.TEMPLATE_ONLY:
                return await self._template_recognition(message, context)
            elif method == RecognitionMethod.LLM_FALLBACK:
                return await self._llm_recognition(message, context)
            else:  # HYBRID_CONSENSUS
                return await self._hybrid_recognition(message, context)

        except Exception as e:
            logger.error(f"❌ Recognition failed: {str(e)}")
            self.stats['recognition_failures'] += 1
            return RecognitionResult(
                job_type=None,
                confidence=0.0,
                method="error",
                entities=[],
                reasoning=f"Recognition error: {str(e)}",
                fallback_used=True
            )

    async def _template_recognition(self,
                                  message: str,
                                  context: Optional[List[Dict]] = None) -> RecognitionResult:
        """Template-based recognition using ConversationEngine"""

        # Extract entities using template patterns
        entities = self.conversation_engine.extract_entities_from_message(message)

        # Detect job type using template patterns
        job_type, confidence = self.conversation_engine.detect_job_type(message, context)

        logger.info(f"📝 Template recognition: {job_type} (confidence: {confidence:.2f})")

        if confidence >= self.confidence_threshold:
            self.stats['template_success'] += 1
            return RecognitionResult(
                job_type=job_type,
                confidence=confidence,
                method="template",
                entities=entities,
                reasoning="Template pattern match"
            )
        else:
            return RecognitionResult(
                job_type=job_type,
                confidence=confidence,
                method="template",
                entities=entities,
                reasoning="Template confidence below threshold"
            )

    async def _llm_recognition(self,
                             message: str,
                             context: Optional[List[Dict]] = None) -> RecognitionResult:
        """Enhanced LLM-based recognition using OpenAI via LLM Factory"""

        try:
            # Initialize LLM service on first use
            if not self.llm_service:
                self.llm_service = await get_llm_service()
                logger.info(f"✅ Initialized LLM service for entity recognition")

            # Create enhanced prompt for structured entity extraction
            system_prompt, user_prompt = self._create_enhanced_classification_prompt(message, context)

            # Check cache first for performance
            cache_context = f"context:{len(context) if context else 0}"
            cached_response = get_cached_ai_response(
                prompt=f"{system_prompt}\n{user_prompt}",
                context=cache_context,
                method="openai_entity_recognition"
            )

            if cached_response:
                logger.info("🎯 Using cached OpenAI response for entity recognition")
                json_data = cached_response
            else:
                # Get structured JSON response from LLM with enhanced error handling
                json_data = {}
                max_retries = 2

                for attempt in range(max_retries + 1):
                    try:
                        if hasattr(self.llm_service, 'generate_json'):
                            # Use OpenAI JSON mode for structured output
                            response = await self.llm_service.generate_json(
                                prompt=user_prompt,
                                system_prompt=system_prompt
                            )
                            json_data = response.get('json', {})

                            # Validate JSON structure
                            if _validate_json_structure(json_data):
                                # Cache successful response
                                cache_ai_response(
                                    prompt=f"{system_prompt}\n{user_prompt}",
                                    response=json_data,
                                    context=cache_context,
                                    method="openai_entity_recognition"
                                )
                                break
                            elif attempt < max_retries:
                                logger.warning(f"Invalid JSON structure, retrying ({attempt + 1}/{max_retries})")
                                continue
                        else:
                            # Fallback for other LLM services
                            response_text = await self.llm_service.generate(f"{system_prompt}\n\n{user_prompt}")
                            json_data = _robust_json_extraction(response_text)

                            if _validate_json_structure(json_data):
                                # Cache successful response
                                cache_ai_response(
                                    prompt=f"{system_prompt}\n{user_prompt}",
                                    response=json_data,
                                    context=cache_context,
                                    method="llm_entity_recognition"
                                )
                                break
                            elif attempt < max_retries:
                                logger.warning(f"Invalid JSON extraction, retrying ({attempt + 1}/{max_retries})")
                                continue

                    except Exception as api_error:
                        if attempt < max_retries:
                            logger.warning(f"API error on attempt {attempt + 1}: {str(api_error)}, retrying...")
                            await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                            continue
                        else:
                            logger.error(f"All API attempts failed: {str(api_error)}")
                            raise api_error

            # Parse structured LLM response
            result = self._parse_structured_llm_response(json_data, message)
            result.method = "llm_enhanced"

            logger.info(f"🚀 Enhanced LLM recognition: {result.job_type} (confidence: {result.confidence:.2f}) - {len(result.entities)} entities")

            self.stats['llm_fallback'] += 1
            return result

        except Exception as e:
            logger.error(f"❌ Enhanced LLM recognition failed: {str(e)}")

            # Enhanced fallback chain - try template recognition as fallback
            try:
                fallback_result = await self._template_recognition(message, context)
                if fallback_result and fallback_result.job_type:
                    fallback_result.method = "template_fallback"
                    fallback_result.reasoning = f"LLM failed: {str(e)}, used template fallback"
                    return fallback_result
            except Exception as template_error:
                logger.warning(f"Template fallback also failed: {str(template_error)}")

            # Final fallback
            return RecognitionResult(
                job_type=None,
                confidence=0.0,
                method="llm_failed",
                entities=[],
                reasoning=f"All LLM methods failed: {str(e)}",
                fallback_used=True
            )

    async def _hybrid_recognition(self,
                                message: str,
                                context: Optional[List[Dict]] = None) -> RecognitionResult:
        """Hybrid approach: Template first, LLM fallback if needed"""

        # Try template recognition first
        template_result = await self._template_recognition(message, context)

        # If template confidence is high enough, use it
        if template_result.confidence >= self.confidence_threshold:
            logger.info(f"✅ Template recognition sufficient: {template_result.job_type}")
            return template_result

        # If template confidence is low, try LLM fallback
        logger.info(f"🔄 Template confidence low ({template_result.confidence:.2f}), trying LLM fallback")

        llm_result = await self._llm_recognition(message, context)

        # Combine results using consensus logic
        combined_result = self._combine_results(template_result, llm_result)
        combined_result.method = "hybrid"
        combined_result.fallback_used = True

        self.stats['hybrid_consensus'] += 1

        logger.info(f"🔀 Hybrid result: {combined_result.job_type} (confidence: {combined_result.confidence:.2f})")

        return combined_result

    def _create_enhanced_classification_prompt(self,
                                             message: str,
                                             context: Optional[List[Dict]] = None) -> Tuple[str, str]:
        """Create enhanced prompts for structured LLM entity extraction"""

        # Get available job types from template config
        job_types_info = []
        for job_type, config in self.template_config.get("job_types", {}).items():
            description = config.get("description", "")
            keywords_de = ", ".join(config.get("keywords_de", [])[:5])  # First 5 keywords
            job_types_info.append(f"- {job_type}: {description} (Keywords: {keywords_de})")

        job_types_text = "\n".join(job_types_info)

        context_text = ""
        if context and len(context) > 0:
            recent_context = context[-3:] if len(context) > 3 else context
            context_text = f"\nPrevious conversation context:\n{json.dumps(recent_context, indent=2)}"

        system_prompt = """You are an expert AI assistant specializing in XML stream configuration and job automation. Your task is to analyze user messages and extract structured information for creating XML stream configurations.

You must respond with a valid JSON object containing job type classification and extracted entities. Be precise and confident in your analysis."""

        user_prompt = f"""Analyze this user message and extract all relevant information for XML stream creation.

Available job types:
{job_types_text}

User message: "{message}"{context_text}

Respond with a JSON object containing:
{{
    "job_type": "standard|sap|file_transfer|custom",
    "confidence": 0.95,
    "reasoning": "Brief explanation of your analysis",
    "entities": [
        {{
            "field_name": "sap_system",
            "value": "P01",
            "confidence": 0.9,
            "source_text": "extracted from user message"
        }}
    ],
    "missing_info": ["List of important fields that might be missing"],
    "suggested_questions": ["Contextual follow-up questions to ask the user"]
}}"""

        return system_prompt, user_prompt

    async def _legacy_ollama_recognition(self,
                                       message: str,
                                       context: Optional[List[Dict]] = None) -> RecognitionResult:
        """Legacy Ollama recognition for fallback"""
        if not self.ollama_service:
            return RecognitionResult(
                job_type=None,
                confidence=0.0,
                method="ollama_legacy",
                entities=[],
                reasoning="Ollama service unavailable",
                fallback_used=True
            )

        try:
            # Use old prompt format for Ollama
            prompt = self._create_legacy_classification_prompt(message, context)
            response = await self.ollama_service.generate_response(prompt)
            result = self._parse_llm_response(response, message)
            result.method = "ollama_legacy"
            return result
        except Exception as e:
            logger.error(f"❌ Legacy Ollama recognition failed: {str(e)}")
            return RecognitionResult(
                job_type=None,
                confidence=0.0,
                method="ollama_legacy",
                entities=[],
                reasoning=f"Ollama error: {str(e)}",
                fallback_used=True
            )

    def _create_legacy_classification_prompt(self,
                                           message: str,
                                           context: Optional[List[Dict]] = None) -> str:
        """Create legacy prompt for Ollama fallback"""
        job_types_info = []
        for job_type, config in self.template_config.get("job_types", {}).items():
            description = config.get("description", "")
            keywords_de = ", ".join(config.get("keywords_de", [])[:5])
            job_types_info.append(f"- {job_type}: {description} (Keywords: {keywords_de})")

        job_types_text = "\n".join(job_types_info)
        context_text = ""
        if context:
            context_text = f"\nContext: {json.dumps(context[-3:], indent=2)}"

        return f"""Analyze this message for XML stream creation:

Job types:
{job_types_text}

Message: "{message}"{context_text}

Respond with JSON: {{"job_type": "type", "confidence": 0.8, "reasoning": "why", "extracted_entities": [{{"field": "name", "value": "value", "confidence": 0.9}}]}}"""

    def _parse_structured_llm_response(self, json_data: Dict[str, Any], original_message: str) -> RecognitionResult:
        """Parse structured JSON response from enhanced LLM into RecognitionResult"""
        try:
            # Extract job type
            job_type_str = json_data.get("job_type")
            job_type = None
            if job_type_str:
                try:
                    job_type = JobType(job_type_str)
                except ValueError:
                    logger.warning(f"⚠️ Unknown job type from LLM: {job_type_str}")

            # Extract confidence
            confidence = float(json_data.get("confidence", 0.0))

            # Extract entities from enhanced structure
            entities = []
            for entity_data in json_data.get("entities", []):
                entity = ExtractedEntity(
                    field_name=entity_data.get("field_name", "unknown"),
                    value=entity_data.get("value", ""),
                    confidence=float(entity_data.get("confidence", 0.5)),
                    source_text=entity_data.get("source_text", original_message[:50])
                )
                entities.append(entity)

            return RecognitionResult(
                job_type=job_type,
                confidence=confidence,
                method="llm_enhanced",
                entities=entities,
                reasoning=json_data.get("reasoning", "Enhanced LLM classification")
            )

        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"❌ Failed to parse structured LLM response: {str(e)}")
            logger.debug(f"Raw JSON data: {json_data}")
            return RecognitionResult(
                job_type=None,
                confidence=0.0,
                method="llm_enhanced",
                entities=[],
                reasoning=f"Failed to parse structured LLM response: {str(e)}"
            )

    def _parse_llm_response(self, response: str, original_message: str) -> RecognitionResult:
        """Legacy: Parse LLM text response into RecognitionResult (fallback for Ollama)"""

        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_text = response[json_start:json_end]
            parsed = json.loads(json_text)

            # Extract job type
            job_type_str = parsed.get("job_type")
            job_type = None
            if job_type_str:
                try:
                    job_type = JobType(job_type_str)
                except ValueError:
                    logger.warning(f"⚠️ Unknown job type from LLM: {job_type_str}")

            # Extract confidence
            confidence = float(parsed.get("confidence", 0.0))

            # Extract entities
            entities = []
            for entity_data in parsed.get("extracted_entities", []):
                entity = ExtractedEntity(
                    field_name=entity_data.get("field", "unknown"),
                    value=entity_data.get("value", ""),
                    confidence=float(entity_data.get("confidence", 0.5)),
                    source_text=original_message[:50] + "..." if len(original_message) > 50 else original_message
                )
                entities.append(entity)

            return RecognitionResult(
                job_type=job_type,
                confidence=confidence,
                method="llm",
                entities=entities,
                reasoning=parsed.get("reasoning", "LLM classification")
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"❌ Failed to parse LLM response: {str(e)}")
            logger.debug(f"Raw response: {response}")

            return RecognitionResult(
                job_type=None,
                confidence=0.0,
                method="llm",
                entities=[],
                reasoning=f"Failed to parse LLM response: {str(e)}"
            )

    def _combine_results(self,
                        template_result: RecognitionResult,
                        llm_result: RecognitionResult) -> RecognitionResult:
        """Combine template and LLM results using consensus logic"""

        # If LLM failed, use template result
        if llm_result.job_type is None:
            return template_result

        # If both agree on job type, use higher confidence
        if template_result.job_type == llm_result.job_type:
            if llm_result.confidence > template_result.confidence:
                combined_entities = llm_result.entities + template_result.entities
                return RecognitionResult(
                    job_type=llm_result.job_type,
                    confidence=max(llm_result.confidence, template_result.confidence),
                    method="hybrid",
                    entities=combined_entities,
                    reasoning=f"Template and LLM consensus: {llm_result.job_type}"
                )
            else:
                return template_result

        # If they disagree, use LLM if it has higher confidence
        if llm_result.confidence > template_result.confidence + 0.1:  # LLM needs to be significantly more confident
            return RecognitionResult(
                job_type=llm_result.job_type,
                confidence=llm_result.confidence,
                method="hybrid",
                entities=llm_result.entities + template_result.entities,
                reasoning=f"LLM override: {llm_result.confidence:.2f} vs template: {template_result.confidence:.2f}"
            )
        else:
            return RecognitionResult(
                job_type=template_result.job_type,
                confidence=template_result.confidence,
                method="hybrid",
                entities=template_result.entities + llm_result.entities,
                reasoning=f"Template preferred: {template_result.confidence:.2f} vs LLM: {llm_result.confidence:.2f}"
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get recognition statistics"""
        success_rate = 0
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['total_requests'] - self.stats['recognition_failures']) / self.stats['total_requests']

        return {
            **self.stats,
            'success_rate': success_rate,
            'template_success_rate': self.stats['template_success'] / max(self.stats['total_requests'], 1),
            'llm_fallback_rate': self.stats['llm_fallback'] / max(self.stats['total_requests'], 1)
        }

    def reset_stats(self):
        """Reset recognition statistics"""
        self.stats = {key: 0 for key in self.stats.keys()}
        logger.info("📊 Recognition statistics reset")

# Utility function for easy integration
async def recognize_entities(message: str,
                           context: Optional[List[Dict]] = None,
                           conversation_engine: Optional[ConversationEngine] = None,
                           ollama_service: Optional[OllamaService] = None) -> RecognitionResult:
    """
    Convenient function for hybrid entity recognition
    """
    recognizer = HybridEntityRecognizer(
        conversation_engine=conversation_engine,
        ollama_service=ollama_service
    )

    return await recognizer.recognize(message, context)

# Enhanced validation and error handling methods
def _validate_json_structure(json_data: Dict[str, Any]) -> bool:
    """Validate that JSON response has expected structure"""
    if not isinstance(json_data, dict):
        return False

    # Check required fields
    required_fields = ['job_type', 'confidence']
    for field in required_fields:
        if field not in json_data:
            logger.warning(f"Missing required field in JSON: {field}")
            return False

    # Validate data types
    if not isinstance(json_data.get('confidence'), (int, float)):
        logger.warning("Invalid confidence type in JSON")
        return False

    if json_data.get('confidence', 0) < 0 or json_data.get('confidence', 0) > 1:
        logger.warning("Confidence out of range (0-1) in JSON")
        return False

    return True

def _robust_json_extraction(response_text: str) -> Dict[str, Any]:
    """Robustly extract JSON from LLM response text"""
    try:
        # First, try direct JSON parsing
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        pass

    try:
        # Try to find JSON object in text
        import re
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            return json.loads(json_text)
    except (json.JSONDecodeError, AttributeError):
        pass

    # Final fallback: create minimal structure
    logger.warning("Could not extract valid JSON, using fallback structure")
    return {
        "job_type": None,
        "confidence": 0.0,
        "reasoning": "Failed to parse LLM response",
        "entities": []
    }

# Add the methods as instance methods
HybridEntityRecognizer._validate_json_structure = _validate_json_structure
HybridEntityRecognizer._robust_json_extraction = _robust_json_extraction