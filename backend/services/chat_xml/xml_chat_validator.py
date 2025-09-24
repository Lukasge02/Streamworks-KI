"""
Enhanced Chat XML Validator - Phase 3.2
Real-Time Parameter Validation Pipeline with OpenAI-powered intelligent suggestions
and proactive error prevention for chat-based XML generation
"""

import logging
import xml.etree.ElementTree as ET
import json
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from lxml import etree
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re

from services.xml_validator import XSDValidator, get_validator
from services.llm_factory import get_llm_service
from schemas.xml_generation import ValidationResult, ValidationError, ValidationSeverity

logger = logging.getLogger(__name__)

class ChatValidationIssueType(Enum):
    """Spezifische Validierungsfehler-Typen für Chat-Interface"""
    MISSING_REQUIRED_ELEMENT = "missing_required_element"
    INVALID_ELEMENT_VALUE = "invalid_element_value"
    MALFORMED_STRUCTURE = "malformed_structure"
    PLACEHOLDER_NOT_REPLACED = "placeholder_not_replaced"
    INVALID_PARAMETER_TYPE = "invalid_parameter_type"
    DEPENDENCY_VIOLATION = "dependency_violation"
    BUSINESS_RULE_VIOLATION = "business_rule_violation"

    # Real-Time Validation Types
    PARAMETER_FORMAT_WARNING = "parameter_format_warning"
    PROACTIVE_DEPENDENCY_WARNING = "proactive_dependency_warning"
    INTELLIGENT_SUGGESTION = "intelligent_suggestion"
    CONTEXT_INCONSISTENCY = "context_inconsistency"

class RealTimeValidationLevel(Enum):
    """Real-time validation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUGGESTION = "suggestion"

@dataclass
class ChatValidationIssue:
    """Chat-spezifisches Validierungsproblem mit KI-freundlichen Metadaten"""
    issue_type: ChatValidationIssueType
    element_path: str
    element_name: str
    current_value: Optional[str]
    expected_value: Optional[str]
    line_number: Optional[int]
    column_number: Optional[int]

    # Chat-spezifische Eigenschaften
    human_message: str  # Für Benutzer verständliche Nachricht
    ai_repair_hint: str  # Hinweis für KI-Reparatur
    parameter_name: Optional[str] = None  # Bezug zu Chat-Parameter
    severity: ValidationSeverity = ValidationSeverity.ERROR

    # Kontext für intelligente Reparatur
    related_elements: List[str] = None
    suggested_fix: Optional[str] = None
    fix_confidence: float = 0.0  # 0.0 - 1.0

    def __post_init__(self):
        if self.related_elements is None:
            self.related_elements = []

@dataclass
class ChatValidationResult:
    """Erweiterte Validierungsresultate für Chat-Interface"""
    is_valid: bool
    issues: List[ChatValidationIssue]
    validation_time_ms: float

    # Chat-spezifische Metriken
    total_placeholders: int = 0
    replaced_placeholders: int = 0
    placeholder_completion: float = 0.0

    # KI-Reparatur Metadaten
    auto_repairable: bool = False
    repair_confidence: float = 0.0
    repair_suggestions: List[str] = None

    def __post_init__(self):
        if self.repair_suggestions is None:
            self.repair_suggestions = []

@dataclass
class RealTimeValidationResult:
    """Real-time validation result for individual parameters"""
    parameter_name: str
    parameter_value: Any
    is_valid: bool
    validation_level: RealTimeValidationLevel
    issues: List[ChatValidationIssue] = field(default_factory=list)

    # OpenAI Intelligence Features
    intelligent_suggestions: List[str] = field(default_factory=list)
    format_corrections: List[str] = field(default_factory=list)
    proactive_warnings: List[str] = field(default_factory=list)
    context_recommendations: List[str] = field(default_factory=list)

    # Metadata
    validation_time_ms: float = 0.0
    confidence_score: float = 1.0

@dataclass
class ParameterValidationContext:
    """Context for parameter validation"""
    job_type: str
    existing_parameters: Dict[str, Any] = field(default_factory=dict)
    conversation_keywords: List[str] = field(default_factory=list)
    session_history: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntelligentSuggestion:
    """OpenAI-powered intelligent suggestion"""
    suggestion_type: str  # "correction", "enhancement", "alternative"
    original_value: str
    suggested_value: str
    reasoning: str
    confidence: float
    examples: List[str] = field(default_factory=list)

class ChatXMLValidator:
    """Enhanced Chat XML Validator with Real-Time Intelligence and OpenAI-powered suggestions"""

    def __init__(self):
        """Initialize the enhanced chat XML validator"""
        self.base_validator = get_validator()
        self.streamworks_rules = self._load_streamworks_business_rules()
        self.llm_service = None  # Lazy initialization for OpenAI

        # Real-Time Validation Configuration
        self.enable_real_time_validation = True
        self.enable_intelligent_suggestions = True
        self.enable_proactive_warnings = True

        # Caching for performance
        self.suggestion_cache: Dict[str, IntelligentSuggestion] = {}
        self.validation_patterns: Dict[str, List[str]] = {}

        # Intelligence Metrics
        self.validation_metrics = {
            "total_validations": 0,
            "real_time_validations": 0,
            "intelligent_suggestions_generated": 0,
            "proactive_warnings_issued": 0,
            "average_response_time_ms": 0
        }

        logger.info("Enhanced Chat XML Validator with Real-Time Intelligence initialized")

    def _load_streamworks_business_rules(self) -> Dict[str, Any]:
        """Lädt Streamworks-spezifische Business Rules"""
        return {
            "required_elements": {
                "StreamName": {"max_length": 50, "pattern": r"^[a-zA-Z0-9_]+$"},
                "JobName": {"max_length": 50, "pattern": r"^[a-zA-Z0-9_]+$"},
                "JobType": {"enum": ["Windows", "Unix", "Linux", "SAP", "None"]},
                "TemplateType": {"enum": ["Normal", "FileTransfer"]},
                "AgentDetail": {"pattern": r"^[a-zA-Z0-9]+$"},
                "MaxStreamRuns": {"type": "integer", "min": 1, "max": 100}
            },
            "dependencies": {
                "JobFileTransferProperty": ["SourceAgent", "TargetAgent"],
                "SAPJobProperty": ["SystemId", "ReportName"]
            },
            "placeholder_patterns": [
                r"\{\{[\w_]+\}\}",  # {{parameter_name}}
                r"\{\{[^}]+\}\}",   # {{any content}}
            ]
        }

    def validate_chat_xml(self, xml_content: str, context: Optional[Dict[str, Any]] = None) -> ChatValidationResult:
        """
        Hauptvalidierung für Chat-generierte XMLs

        Args:
            xml_content: XML-Inhalt als String
            context: Zusätzlicher Kontext (Job-Type, gesammelte Parameter, etc.)

        Returns:
            ChatValidationResult mit detaillierten Issues
        """
        import time
        start_time = time.time()

        issues = []

        # 1. Standard XML Schema Validierung
        base_result = self.base_validator.validate_xml_string(xml_content)

        # Konvertiere Standard-Validierungsfehler zu Chat-Issues
        for error in base_result.errors:
            issues.append(self._convert_base_error_to_chat_issue(error))

        # 2. Chat-spezifische Validierungen
        try:
            # Parse XML für weitere Analysen
            root = etree.fromstring(xml_content.encode('utf-8'))

            # Placeholder-Analyse
            placeholder_issues = self._check_placeholders(xml_content, root)
            issues.extend(placeholder_issues)

            # Streamworks Business Rules
            business_rule_issues = self._check_business_rules(root, context)
            issues.extend(business_rule_issues)

            # Parameter-XML Konsistenz (falls Kontext verfügbar)
            if context and context.get('collected_parameters'):
                consistency_issues = self._check_parameter_consistency(root, context['collected_parameters'])
                issues.extend(consistency_issues)

            # Job-Type spezifische Validierung
            if context and context.get('job_type'):
                job_issues = self._check_job_type_requirements(root, context['job_type'])
                issues.extend(job_issues)

        except Exception as e:
            logger.error(f"Error during chat validation: {str(e)}")
            issues.append(ChatValidationIssue(
                issue_type=ChatValidationIssueType.MALFORMED_STRUCTURE,
                element_path="/",
                element_name="root",
                current_value=None,
                expected_value=None,
                line_number=None,
                column_number=None,
                human_message="Das XML ist nicht korrekt strukturiert",
                ai_repair_hint=f"Fix XML structure error: {str(e)}",
                severity=ValidationSeverity.ERROR
            ))

        # 3. Berechne Reparatur-Confidence
        repair_confidence = self._calculate_repair_confidence(issues)
        auto_repairable = repair_confidence > 0.7

        # 4. Generiere Repair-Suggestions
        repair_suggestions = self._generate_repair_suggestions(issues)

        # 5. Placeholder-Statistiken
        total_placeholders, replaced_placeholders = self._count_placeholders(xml_content)
        placeholder_completion = replaced_placeholders / total_placeholders if total_placeholders > 0 else 1.0

        validation_time_ms = (time.time() - start_time) * 1000

        return ChatValidationResult(
            is_valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0,
            issues=issues,
            validation_time_ms=validation_time_ms,
            total_placeholders=total_placeholders,
            replaced_placeholders=replaced_placeholders,
            placeholder_completion=placeholder_completion,
            auto_repairable=auto_repairable,
            repair_confidence=repair_confidence,
            repair_suggestions=repair_suggestions
        )

    def _convert_base_error_to_chat_issue(self, error: ValidationError) -> ChatValidationIssue:
        """Konvertiert Standard-Validierungsfehler zu Chat-Issue"""

        # Analysiere Fehlermeldung für bessere KI-Hints
        ai_hint = error.message
        if "not allowed" in error.message.lower():
            ai_hint = f"Remove or replace invalid element. {error.suggestion or ''}"
        elif "missing" in error.message.lower():
            ai_hint = f"Add missing required element. {error.suggestion or ''}"

        return ChatValidationIssue(
            issue_type=ChatValidationIssueType.MALFORMED_STRUCTURE,
            element_path=f"line {error.line or 'unknown'}",
            element_name="unknown",
            current_value=None,
            expected_value=None,
            line_number=error.line,
            column_number=error.column,
            human_message=f"XML-Struktur Problem: {error.message}",
            ai_repair_hint=ai_hint,
            severity=error.severity
        )

    def _check_placeholders(self, xml_content: str, root: etree.Element) -> List[ChatValidationIssue]:
        """Prüft auf nicht-ersetzte Platzhalter"""
        issues = []

        for pattern in self.streamworks_rules["placeholder_patterns"]:
            matches = re.finditer(pattern, xml_content)
            for match in matches:
                placeholder = match.group(0)

                # Berechne ungefähre Zeilennummer
                line_number = xml_content[:match.start()].count('\n') + 1

                issues.append(ChatValidationIssue(
                    issue_type=ChatValidationIssueType.PLACEHOLDER_NOT_REPLACED,
                    element_path=f"line {line_number}",
                    element_name="placeholder",
                    current_value=placeholder,
                    expected_value="actual value",
                    line_number=line_number,
                    column_number=match.start(),
                    human_message=f"Parameter '{placeholder}' wurde noch nicht gesetzt",
                    ai_repair_hint=f"Replace placeholder {placeholder} with actual value from user input",
                    parameter_name=placeholder.strip('{}'),
                    severity=ValidationSeverity.WARNING,
                    suggested_fix=f"<Replace {placeholder} with user-provided value>",
                    fix_confidence=0.9
                ))

        return issues

    def _check_business_rules(self, root: etree.Element, context: Optional[Dict[str, Any]]) -> List[ChatValidationIssue]:
        """Prüft Streamworks-spezifische Business Rules"""
        issues = []

        # Prüfe required elements
        for element_name, rules in self.streamworks_rules["required_elements"].items():
            elements = root.xpath(f".//{element_name}")

            if not elements:
                issues.append(ChatValidationIssue(
                    issue_type=ChatValidationIssueType.MISSING_REQUIRED_ELEMENT,
                    element_path=f"//{element_name}",
                    element_name=element_name,
                    current_value=None,
                    expected_value="required",
                    line_number=None,
                    column_number=None,
                    human_message=f"Pflichtfeld '{element_name}' fehlt",
                    ai_repair_hint=f"Add required element <{element_name}>value</{element_name}>",
                    parameter_name=element_name,
                    severity=ValidationSeverity.ERROR,
                    suggested_fix=f"<{element_name}>{{value}}</{element_name}>",
                    fix_confidence=0.8
                ))
                continue

            # Validiere Element-Werte
            for element in elements:
                value = element.text or ""
                issues.extend(self._validate_element_value(element_name, value, rules, element))

        return issues

    def _validate_element_value(self, element_name: str, value: str, rules: Dict[str, Any], element: etree.Element) -> List[ChatValidationIssue]:
        """Validiert einen Element-Wert gegen Business Rules"""
        issues = []

        # Pattern-Validierung
        if "pattern" in rules:
            if not re.match(rules["pattern"], value):
                issues.append(ChatValidationIssue(
                    issue_type=ChatValidationIssueType.INVALID_ELEMENT_VALUE,
                    element_path=element.getroottree().getpath(element),
                    element_name=element_name,
                    current_value=value,
                    expected_value=f"matching pattern {rules['pattern']}",
                    line_number=element.sourceline,
                    column_number=None,
                    human_message=f"'{element_name}' hat ungültiges Format: '{value}'",
                    ai_repair_hint=f"Fix {element_name} format to match pattern {rules['pattern']}",
                    parameter_name=element_name,
                    severity=ValidationSeverity.ERROR,
                    fix_confidence=0.7
                ))

        # Enum-Validierung
        if "enum" in rules:
            if value not in rules["enum"]:
                valid_options = ", ".join(rules["enum"])
                issues.append(ChatValidationIssue(
                    issue_type=ChatValidationIssueType.INVALID_ELEMENT_VALUE,
                    element_path=element.getroottree().getpath(element),
                    element_name=element_name,
                    current_value=value,
                    expected_value=f"one of: {valid_options}",
                    line_number=element.sourceline,
                    column_number=None,
                    human_message=f"'{element_name}' muss einer dieser Werte sein: {valid_options}",
                    ai_repair_hint=f"Change {element_name} to one of: {valid_options}",
                    parameter_name=element_name,
                    severity=ValidationSeverity.ERROR,
                    suggested_fix=rules["enum"][0],  # Suggest first valid option
                    fix_confidence=0.9
                ))

        # Typ-Validierung
        if "type" in rules and rules["type"] == "integer":
            try:
                int_value = int(value)

                # Min/Max Validierung
                if "min" in rules and int_value < rules["min"]:
                    issues.append(self._create_range_issue(element_name, value, rules["min"], "minimum", element))
                if "max" in rules and int_value > rules["max"]:
                    issues.append(self._create_range_issue(element_name, value, rules["max"], "maximum", element))

            except ValueError:
                issues.append(ChatValidationIssue(
                    issue_type=ChatValidationIssueType.INVALID_PARAMETER_TYPE,
                    element_path=element.getroottree().getpath(element),
                    element_name=element_name,
                    current_value=value,
                    expected_value="integer",
                    line_number=element.sourceline,
                    column_number=None,
                    human_message=f"'{element_name}' muss eine Zahl sein, nicht '{value}'",
                    ai_repair_hint=f"Convert {element_name} value '{value}' to integer",
                    parameter_name=element_name,
                    severity=ValidationSeverity.ERROR,
                    fix_confidence=0.8
                ))

        return issues

    def _create_range_issue(self, element_name: str, value: str, limit: int, limit_type: str, element: etree.Element) -> ChatValidationIssue:
        """Erstellt Issue für Wertebereich-Verletzungen"""
        return ChatValidationIssue(
            issue_type=ChatValidationIssueType.INVALID_ELEMENT_VALUE,
            element_path=element.getroottree().getpath(element),
            element_name=element_name,
            current_value=value,
            expected_value=f"{limit_type} {limit}",
            line_number=element.sourceline,
            column_number=None,
            human_message=f"'{element_name}' Wert {value} überschreitet {limit_type} {limit}",
            ai_repair_hint=f"Adjust {element_name} to meet {limit_type} requirement of {limit}",
            parameter_name=element_name,
            severity=ValidationSeverity.ERROR,
            suggested_fix=str(limit),
            fix_confidence=0.9
        )

    def _check_parameter_consistency(self, root: etree.Element, collected_parameters: Dict[str, Any]) -> List[ChatValidationIssue]:
        """Prüft Konsistenz zwischen gesammelten Chat-Parametern und generiertem XML"""
        issues = []

        # Mappings von Chat-Parameter zu XML-Elementen
        parameter_mappings = {
            "StreamName": "//StreamName",
            "stream_name": "//StreamName",
            "MaxStreamRuns": "//MaxStreamRuns",
            "max_runs": "//MaxStreamRuns",
            "script": "//MainScript",
            "job_name": "//JobName"
        }

        for param_name, param_value in collected_parameters.items():
            if param_name in parameter_mappings:
                xpath = parameter_mappings[param_name]
                elements = root.xpath(xpath)

                if elements:
                    xml_value = elements[0].text or ""
                    if str(param_value) != xml_value:
                        issues.append(ChatValidationIssue(
                            issue_type=ChatValidationIssueType.DEPENDENCY_VIOLATION,
                            element_path=xpath,
                            element_name=elements[0].tag,
                            current_value=xml_value,
                            expected_value=str(param_value),
                            line_number=elements[0].sourceline,
                            column_number=None,
                            human_message=f"Parameter '{param_name}' stimmt nicht mit XML überein",
                            ai_repair_hint=f"Update XML element {elements[0].tag} to match chat parameter value: {param_value}",
                            parameter_name=param_name,
                            severity=ValidationSeverity.WARNING,
                            suggested_fix=str(param_value),
                            fix_confidence=0.95
                        ))

        return issues

    def _check_job_type_requirements(self, root: etree.Element, job_type: str) -> List[ChatValidationIssue]:
        """Prüft Job-Type spezifische Anforderungen"""
        issues = []

        if job_type == "FILE_TRANSFER":
            # FileTransfer muss JobFileTransferProperty haben
            ft_elements = root.xpath("//JobFileTransferProperty")
            if not ft_elements:
                issues.append(ChatValidationIssue(
                    issue_type=ChatValidationIssueType.MISSING_REQUIRED_ELEMENT,
                    element_path="//Job",
                    element_name="JobFileTransferProperty",
                    current_value=None,
                    expected_value="required for FILE_TRANSFER",
                    line_number=None,
                    column_number=None,
                    human_message="File Transfer Job benötigt JobFileTransferProperty",
                    ai_repair_hint="Add <JobFileTransferProperty> section with SourceAgent, TargetAgent, and FileTransferDefinitions",
                    severity=ValidationSeverity.ERROR,
                    fix_confidence=0.8
                ))

        elif job_type == "SAP":
            # SAP Jobs sollten spezifische Properties haben
            sap_elements = root.xpath("//SAPJobProperty")
            if not sap_elements:
                issues.append(ChatValidationIssue(
                    issue_type=ChatValidationIssueType.MISSING_REQUIRED_ELEMENT,
                    element_path="//Job",
                    element_name="SAPJobProperty",
                    current_value=None,
                    expected_value="required for SAP jobs",
                    line_number=None,
                    column_number=None,
                    human_message="SAP Job benötigt SAPJobProperty",
                    ai_repair_hint="Add <SAPJobProperty> section with SystemId, ReportName, and optional Variant",
                    severity=ValidationSeverity.WARNING,
                    fix_confidence=0.7
                ))

        return issues

    def _calculate_repair_confidence(self, issues: List[ChatValidationIssue]) -> float:
        """Berechnet Confidence für automatische Reparatur"""
        if not issues:
            return 1.0

        total_confidence = 0.0
        error_count = 0

        for issue in issues:
            if issue.severity == ValidationSeverity.ERROR:
                total_confidence += issue.fix_confidence
                error_count += 1

        return total_confidence / error_count if error_count > 0 else 1.0

    def _generate_repair_suggestions(self, issues: List[ChatValidationIssue]) -> List[str]:
        """Generiert konkrete Reparatur-Vorschläge für KI"""
        suggestions = []

        # Gruppiere Issues nach Typ
        by_type = {}
        for issue in issues:
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type].append(issue)

        # Generiere Typ-spezifische Suggestions
        for issue_type, type_issues in by_type.items():
            if issue_type == ChatValidationIssueType.PLACEHOLDER_NOT_REPLACED:
                placeholders = [i.current_value for i in type_issues]
                suggestions.append(f"Replace placeholders: {', '.join(placeholders)} with actual values")

            elif issue_type == ChatValidationIssueType.MISSING_REQUIRED_ELEMENT:
                elements = [i.element_name for i in type_issues]
                suggestions.append(f"Add missing required elements: {', '.join(elements)}")

            elif issue_type == ChatValidationIssueType.INVALID_ELEMENT_VALUE:
                for issue in type_issues:
                    if issue.suggested_fix:
                        suggestions.append(f"Change {issue.element_name} from '{issue.current_value}' to '{issue.suggested_fix}'")

        return suggestions

    def _count_placeholders(self, xml_content: str) -> Tuple[int, int]:
        """Zählt Gesamt- und ersetzte Platzhalter"""
        total = 0
        for pattern in self.streamworks_rules["placeholder_patterns"]:
            total += len(re.findall(pattern, xml_content))

        # Annahme: Alles was nicht {{}} Format hat ist ersetzt
        replaced = len(re.findall(r'[^{][\w\s]+[^}]', xml_content))

        return total, max(0, replaced - total)

    def validate_preview_xml(self, xml_content: str, allow_placeholders: bool = True) -> ChatValidationResult:
        """Spezielle Validierung für Preview-XMLs mit Platzhaltern"""
        result = self.validate_chat_xml(xml_content)

        if allow_placeholders:
            # Filtere Placeholder-Issues für Preview
            result.issues = [i for i in result.issues
                           if i.issue_type != ChatValidationIssueType.PLACEHOLDER_NOT_REPLACED]

            # Neuberechnung der Validität
            error_count = len([i for i in result.issues if i.severity == ValidationSeverity.ERROR])
            result.is_valid = error_count == 0

        return result

    # ===== REAL-TIME VALIDATION PIPELINE =====

    async def _get_llm_service(self):
        """Get LLM service instance (lazy initialization) - Prefer OpenAI"""
        if self.llm_service is None:
            try:
                self.llm_service = await get_llm_service("openai")
                logger.info("OpenAI service initialized for intelligent validation")
            except Exception as e:
                logger.warning(f"OpenAI not available for validation, falling back: {e}")
                self.llm_service = await get_llm_service()
        return self.llm_service

    async def validate_parameter_real_time(
        self,
        parameter_name: str,
        parameter_value: Any,
        context: ParameterValidationContext
    ) -> RealTimeValidationResult:
        """Real-time parameter validation with OpenAI intelligence"""

        import time
        start_time = time.time()

        if not self.enable_real_time_validation:
            return RealTimeValidationResult(
                parameter_name=parameter_name,
                parameter_value=parameter_value,
                is_valid=True,
                validation_level=RealTimeValidationLevel.INFO
            )

        try:
            # Basic validation first
            basic_validation = self._validate_parameter_basic(parameter_name, parameter_value, context)

            # Generate intelligent suggestions if enabled
            intelligent_suggestions = []
            if self.enable_intelligent_suggestions:
                intelligent_suggestions = await self._generate_intelligent_suggestions(
                    parameter_name, parameter_value, context
                )

            # Check for proactive warnings
            proactive_warnings = []
            if self.enable_proactive_warnings:
                proactive_warnings = await self._check_proactive_warnings(
                    parameter_name, parameter_value, context
                )

            # Generate context recommendations
            context_recommendations = await self._generate_context_recommendations(
                parameter_name, parameter_value, context
            )

            # Determine validation level
            validation_level = self._determine_validation_level(
                basic_validation, intelligent_suggestions, proactive_warnings
            )

            validation_time_ms = (time.time() - start_time) * 1000

            result = RealTimeValidationResult(
                parameter_name=parameter_name,
                parameter_value=parameter_value,
                is_valid=basic_validation["is_valid"],
                validation_level=validation_level,
                issues=basic_validation.get("issues", []),
                intelligent_suggestions=intelligent_suggestions,
                proactive_warnings=proactive_warnings,
                context_recommendations=context_recommendations,
                validation_time_ms=validation_time_ms,
                confidence_score=basic_validation.get("confidence", 1.0)
            )

            # Update metrics
            self.validation_metrics["real_time_validations"] += 1
            if intelligent_suggestions:
                self.validation_metrics["intelligent_suggestions_generated"] += 1
            if proactive_warnings:
                self.validation_metrics["proactive_warnings_issued"] += 1

            logger.info(f"Real-time validation for {parameter_name}: {validation_level.value} ({validation_time_ms:.1f}ms)")
            return result

        except Exception as e:
            logger.error(f"Real-time validation failed for {parameter_name}: {e}")
            return RealTimeValidationResult(
                parameter_name=parameter_name,
                parameter_value=parameter_value,
                is_valid=True,  # Fail gracefully
                validation_level=RealTimeValidationLevel.INFO,
                validation_time_ms=(time.time() - start_time) * 1000
            )

    def _validate_parameter_basic(
        self, parameter_name: str, parameter_value: Any, context: ParameterValidationContext
    ) -> Dict[str, Any]:
        """Basic parameter validation without AI"""

        issues = []
        is_valid = True
        confidence = 1.0

        # Check against Streamworks business rules
        if parameter_name in self.streamworks_rules["required_elements"]:
            rules = self.streamworks_rules["required_elements"][parameter_name]

            # Pattern validation
            if "pattern" in rules:
                if not re.match(rules["pattern"], str(parameter_value)):
                    is_valid = False
                    issues.append(ChatValidationIssue(
                        issue_type=ChatValidationIssueType.INVALID_ELEMENT_VALUE,
                        element_path=f"parameter:{parameter_name}",
                        element_name=parameter_name,
                        current_value=str(parameter_value),
                        expected_value=f"Pattern: {rules['pattern']}",
                        line_number=None,
                        column_number=None,
                        human_message=f"Parameter '{parameter_name}' entspricht nicht dem erwarteten Format",
                        ai_repair_hint=f"Fix format of {parameter_name} to match pattern {rules['pattern']}",
                        parameter_name=parameter_name,
                        severity=ValidationSeverity.ERROR
                    ))

            # Enum validation
            if "enum" in rules:
                if str(parameter_value) not in rules["enum"]:
                    is_valid = False
                    valid_options = ", ".join(rules["enum"])
                    issues.append(ChatValidationIssue(
                        issue_type=ChatValidationIssueType.INVALID_ELEMENT_VALUE,
                        element_path=f"parameter:{parameter_name}",
                        element_name=parameter_name,
                        current_value=str(parameter_value),
                        expected_value=f"One of: {valid_options}",
                        line_number=None,
                        column_number=None,
                        human_message=f"Parameter '{parameter_name}' muss einer dieser Werte sein: {valid_options}",
                        ai_repair_hint=f"Change {parameter_name} to one of: {valid_options}",
                        parameter_name=parameter_name,
                        severity=ValidationSeverity.ERROR
                    ))

        return {
            "is_valid": is_valid,
            "confidence": confidence,
            "issues": issues
        }

    async def _generate_intelligent_suggestions(
        self, parameter_name: str, parameter_value: Any, context: ParameterValidationContext
    ) -> List[str]:
        """Generate intelligent suggestions using OpenAI"""

        if not self.enable_intelligent_suggestions:
            return []

        # Check cache first
        cache_key = f"{parameter_name}:{parameter_value}:{context.job_type}"
        if cache_key in self.suggestion_cache:
            cached = self.suggestion_cache[cache_key]
            return [f"{cached.suggested_value} ({cached.reasoning})"]

        try:
            llm_service = await self._get_llm_service()

            suggestion_prompt = f"""Analysiere diesen Streamworks Parameter und gib intelligente Verbesserungsvorschläge:

Parameter: {parameter_name}
Aktueller Wert: {parameter_value}
Job-Type: {context.job_type}
Existierende Parameter: {context.existing_parameters}
Kontext-Keywords: {context.conversation_keywords}

Erstelle 2-3 konkrete Verbesserungsvorschläge für diesen Parameter:
1. Format-Korrekturen (falls nötig)
2. Häufig verwendete Alternativen
3. Best-Practice Empfehlungen

Antworte mit JSON: {{"suggestions": ["vorschlag1", "vorschlag2", "vorschlag3"]}}

Fokussiere auf praktische, umsetzbare Vorschläge für Streamworks XML-Generierung."""

            response = await llm_service.generate(suggestion_prompt)

            try:
                result = json.loads(response)
                suggestions = result.get("suggestions", [])

                # Cache successful suggestions
                if suggestions and len(suggestions) > 0:
                    self.suggestion_cache[cache_key] = IntelligentSuggestion(
                        suggestion_type="enhancement",
                        original_value=str(parameter_value),
                        suggested_value=suggestions[0],
                        reasoning="AI-generated suggestion",
                        confidence=0.8
                    )

                return suggestions[:3]  # Max 3 suggestions

            except json.JSONDecodeError:
                logger.warning("Failed to parse AI suggestion response")
                return []

        except Exception as e:
            logger.warning(f"Intelligent suggestion generation failed: {e}")
            return []

    async def _check_proactive_warnings(
        self, parameter_name: str, parameter_value: Any, context: ParameterValidationContext
    ) -> List[str]:
        """Check for proactive warnings using context and AI"""

        if not self.enable_proactive_warnings:
            return []

        warnings = []

        # Check for potential dependency issues
        if context.job_type == "FILE_TRANSFER":
            if parameter_name in ["source_path", "target_path"]:
                if not any(param in context.existing_parameters for param in ["source_agent", "target_agent"]):
                    warnings.append("⚠️ Für File Transfer werden auch Source-Agent und Target-Agent benötigt")

        elif context.job_type == "SAP":
            if parameter_name == "sap_report":
                if "sap_system" not in context.existing_parameters:
                    warnings.append("⚠️ SAP-System sollte vor dem Report definiert werden")

        # Check for common mistakes using AI
        try:
            llm_service = await self._get_llm_service()

            warning_prompt = f"""Prüfe diesen Streamworks Parameter auf potentielle Probleme:

Parameter: {parameter_name}
Wert: {parameter_value}
Job-Type: {context.job_type}
Bisherige Parameter: {context.existing_parameters}

Identifiziere mögliche Probleme:
1. Fehlende Abhängigkeiten
2. Häufige Fehlerquellen
3. Format-Warnungen
4. Kompatibilitätsprobleme

Antworte nur mit konkreten Warnungen als JSON: {{"warnings": ["warnung1", "warnung2"]}}

Nur relevante Warnungen ausgeben, keine allgemeinen Tipps."""

            response = await llm_service.generate(warning_prompt)

            try:
                result = json.loads(response)
                ai_warnings = result.get("warnings", [])
                warnings.extend(ai_warnings[:2])  # Max 2 AI warnings

            except json.JSONDecodeError:
                pass

        except Exception as e:
            logger.warning(f"Proactive warning generation failed: {e}")

        return warnings

    async def _generate_context_recommendations(
        self, parameter_name: str, parameter_value: Any, context: ParameterValidationContext
    ) -> List[str]:
        """Generate context-aware recommendations"""

        recommendations = []

        # Job-type specific recommendations
        if context.job_type == "STANDARD":
            if parameter_name == "script_path":
                recommendations.append("💡 Verwenden Sie absolute Pfade für bessere Zuverlässigkeit")

        elif context.job_type == "SAP":
            if parameter_name == "sap_system":
                recommendations.append("💡 Format: <SID>_<Client> (z.B. PA1_100)")

        elif context.job_type == "FILE_TRANSFER":
            if parameter_name in ["source_path", "target_path"]:
                recommendations.append("💡 Überprüfen Sie Dateiberechtigungen am Zielsystem")

        # Generate AI-powered recommendations
        try:
            llm_service = await self._get_llm_service()

            recommendation_prompt = f"""Gib kontextbezogene Empfehlungen für diesen Streamworks Parameter:

Parameter: {parameter_name}
Wert: {parameter_value}
Job-Type: {context.job_type}

Erstelle 1-2 hilfreiche Empfehlungen basierend auf Best Practices.
Format: "💡 [Konkrete Empfehlung]"

Antworte mit JSON: {{"recommendations": ["💡 empfehlung1", "💡 empfehlung2"]}}"""

            response = await llm_service.generate(recommendation_prompt)

            try:
                result = json.loads(response)
                ai_recommendations = result.get("recommendations", [])
                recommendations.extend(ai_recommendations[:2])

            except json.JSONDecodeError:
                pass

        except Exception as e:
            logger.warning(f"Context recommendation generation failed: {e}")

        return recommendations

    def _determine_validation_level(
        self, basic_validation: Dict[str, Any], suggestions: List[str], warnings: List[str]
    ) -> RealTimeValidationLevel:
        """Determine overall validation level"""

        if not basic_validation["is_valid"]:
            return RealTimeValidationLevel.ERROR

        if warnings:
            return RealTimeValidationLevel.WARNING

        if suggestions:
            return RealTimeValidationLevel.SUGGESTION

        return RealTimeValidationLevel.INFO

    async def validate_parameters_batch(
        self, parameters: Dict[str, Any], context: ParameterValidationContext
    ) -> Dict[str, RealTimeValidationResult]:
        """Validate multiple parameters in batch with intelligence"""

        results = {}

        # Validate parameters in parallel for better performance
        validation_tasks = []
        for param_name, param_value in parameters.items():
            task = self.validate_parameter_real_time(param_name, param_value, context)
            validation_tasks.append((param_name, task))

        # Execute validations
        for param_name, task in validation_tasks:
            try:
                result = await task
                results[param_name] = result
            except Exception as e:
                logger.error(f"Batch validation failed for {param_name}: {e}")
                results[param_name] = RealTimeValidationResult(
                    parameter_name=param_name,
                    parameter_value=parameters[param_name],
                    is_valid=True,  # Fail gracefully
                    validation_level=RealTimeValidationLevel.INFO
                )

        self.validation_metrics["total_validations"] += len(parameters)
        return results

    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation performance metrics"""
        return {
            **self.validation_metrics,
            "cache_size": len(self.suggestion_cache),
            "enabled_features": {
                "real_time_validation": self.enable_real_time_validation,
                "intelligent_suggestions": self.enable_intelligent_suggestions,
                "proactive_warnings": self.enable_proactive_warnings
            }
        }

# Singleton instance
_chat_validator = None

def get_chat_xml_validator() -> ChatXMLValidator:
    """Get chat XML validator singleton"""
    global _chat_validator
    if _chat_validator is None:
        _chat_validator = ChatXMLValidator()
    return _chat_validator