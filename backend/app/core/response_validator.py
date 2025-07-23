"""
🎯 Enterprise Response Validator
Production-Grade Antwortvalidierung für StreamWorks-KI Enterprise
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class ValidationResult:
    """Single validation result"""
    check_name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    score: float = 0.0
    details: Optional[Dict[str, Any]] = None

@dataclass
class ResponseQualityReport:
    """Comprehensive quality assessment"""
    overall_score: float
    passed_checks: int
    total_checks: int
    critical_issues: List[ValidationResult]
    warnings: List[ValidationResult]
    recommendations: List[str]
    is_production_ready: bool

class EnterpriseResponseValidator:
    """Enterprise-Grade Response Validation Framework"""
    
    def __init__(self):
        self.version = "3.0"
        self.validation_rules = self._initialize_validation_rules()
        logger.info(f"🎯 Enterprise Response Validator v{self.version} initialized")
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize comprehensive validation rules"""
        return {
            # 🛡️ Security validation
            "security": {
                "forbidden_patterns": [
                    r"(?i)forget\s+(previous|all)\s+instructions?",
                    r"(?i)you\s+are\s+now\s+",
                    r"(?i)ignore\s+(your|the)\s+role",
                    r"(?i)confidential|secret|internal",
                    r"(?i)other\s+compan(y|ies)"
                ],
                "required_scope": ["streamworks", "arvato", "batch", "xml", "automation"]
            },
            
            # 🇩🇪 German language compliance
            "language": {
                "forbidden_english": [
                    r"\b(?:the|and|or|of|in|to|for|with|on|at|by|from)\b",
                    r"\b(?:configuration|processing|workflow|management)\b",
                    r"\b(?:error|handling|validation|monitoring)\b"
                ],
                "required_german_terms": [
                    "Konfiguration", "Verarbeitung", "Ablauf", "Verwaltung",
                    "Fehlerbehandlung", "Validierung", "Überwachung"
                ],
                "politeness_patterns": [r"\bSie\b", r"\bIhnen\b", r"\bIhr\b"]
            },
            
            # 📋 Structure compliance
            "structure": {
                "required_sections": [
                    r"##\s*🔧.*?",  # Main title with 🔧
                    r"###\s*📋\s*Überblick",
                    r"###\s*💻\s*Konkrete\s+Umsetzung",
                    r"###\s*💡\s*Wichtige\s+Hinweise",
                    r"###\s*📚\s*Quellen"
                ],
                "emoji_requirements": ["🔧", "📋", "💻", "💡", "📚"]
            },
            
            # 📚 Citation validation
            "citations": {
                "valid_format": r"Quelle:\s+[\w\-_.]+\.(txt|md|yaml|xml|json)$",
                "forbidden_duplicates": True,
                "max_sources": 3,
                "required_citation": True
            },
            
            # 📏 Quality metrics
            "quality": {
                "min_word_count": 150,
                "max_word_count": 2000,
                "min_code_examples": 0,
                "xml_syntax_validation": True
            }
        }
    
    def validate_response(self, response: str, context: Dict[str, Any] = None) -> ResponseQualityReport:
        """Comprehensive response validation"""
        logger.info("🔍 Starting enterprise response validation...")
        
        results = []
        context = context or {}
        
        # Run all validation checks
        results.extend(self._validate_security(response))
        results.extend(self._validate_language_compliance(response))
        results.extend(self._validate_structure(response))
        results.extend(self._validate_citations(response))
        results.extend(self._validate_quality_metrics(response))
        
        # Generate comprehensive report
        return self._generate_quality_report(results)
    
    def _validate_security(self, response: str) -> List[ValidationResult]:
        """Validate security compliance"""
        results = []
        
        # Check for forbidden injection patterns
        for pattern in self.validation_rules["security"]["forbidden_patterns"]:
            if re.search(pattern, response, re.IGNORECASE):
                results.append(ValidationResult(
                    check_name="security_injection_check",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Potential prompt injection detected: {pattern}",
                    score=0.0
                ))
        
        # Verify StreamWorks scope
        scope_keywords = self.validation_rules["security"]["required_scope"]
        scope_found = any(keyword.lower() in response.lower() for keyword in scope_keywords)
        
        if not scope_found:
            results.append(ValidationResult(
                check_name="scope_validation",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="Response appears outside StreamWorks scope",
                score=0.0
            ))
        
        if not results:  # No security issues found
            results.append(ValidationResult(
                check_name="security_validation",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="Security validation passed",
                score=1.0
            ))
        
        return results
    
    def _validate_language_compliance(self, response: str) -> List[ValidationResult]:
        """Validate German language compliance"""
        results = []
        
        # Check for forbidden English terms
        english_violations = []
        for pattern in self.validation_rules["language"]["forbidden_english"]:
            matches = re.findall(pattern, response, re.IGNORECASE)
            english_violations.extend(matches)
        
        if english_violations:
            results.append(ValidationResult(
                check_name="language_purity",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"English terms detected: {english_violations[:5]}",
                score=max(0.0, 1.0 - len(english_violations) * 0.1),
                details={"violations": english_violations}
            ))
        
        # Check for politeness forms
        politeness_score = 0.0
        for pattern in self.validation_rules["language"]["politeness_patterns"]:
            if re.search(pattern, response):
                politeness_score += 0.33
        
        results.append(ValidationResult(
            check_name="politeness_compliance",
            passed=politeness_score >= 0.5,
            severity=ValidationSeverity.MEDIUM,
            message=f"Politeness score: {politeness_score:.2f}",
            score=min(1.0, politeness_score)
        ))
        
        return results
    
    def _validate_structure(self, response: str) -> List[ValidationResult]:
        """Validate response structure compliance"""
        results = []
        
        # Check required sections
        sections_found = 0
        missing_sections = []
        
        for section_pattern in self.validation_rules["structure"]["required_sections"]:
            if re.search(section_pattern, response, re.MULTILINE):
                sections_found += 1
            else:
                missing_sections.append(section_pattern)
        
        total_sections = len(self.validation_rules["structure"]["required_sections"])
        structure_score = sections_found / total_sections
        
        results.append(ValidationResult(
            check_name="structure_compliance",
            passed=structure_score >= 0.8,
            severity=ValidationSeverity.HIGH if structure_score < 0.6 else ValidationSeverity.MEDIUM,
            message=f"Structure compliance: {sections_found}/{total_sections} sections",
            score=structure_score,
            details={"missing_sections": missing_sections}
        ))
        
        # Check emoji usage
        emoji_count = 0
        for emoji in self.validation_rules["structure"]["emoji_requirements"]:
            if emoji in response:
                emoji_count += 1
        
        emoji_score = emoji_count / len(self.validation_rules["structure"]["emoji_requirements"])
        results.append(ValidationResult(
            check_name="emoji_compliance",
            passed=emoji_score >= 0.8,
            severity=ValidationSeverity.LOW,
            message=f"Emoji usage: {emoji_count}/{len(self.validation_rules['structure']['emoji_requirements'])}",
            score=emoji_score
        ))
        
        return results
    
    def _validate_citations(self, response: str) -> List[ValidationResult]:
        """Validate citation quality and format"""
        results = []
        
        # Extract all citations
        citation_pattern = r"Quelle:\s+([\w\-_.]+\.(?:txt|md|yaml|xml|json))"
        citations = re.findall(citation_pattern, response, re.IGNORECASE)
        
        if not citations and self.validation_rules["citations"]["required_citation"]:
            results.append(ValidationResult(
                check_name="citation_required",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message="No valid citations found",
                score=0.0
            ))
        else:
            # Check for duplicates
            unique_citations = list(set(citations))
            has_duplicates = len(citations) != len(unique_citations)
            
            if has_duplicates:
                results.append(ValidationResult(
                    check_name="citation_duplicates",
                    passed=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Duplicate citations found: {len(citations) - len(unique_citations)}",
                    score=0.7
                ))
            
            # Check citation count
            max_sources = self.validation_rules["citations"]["max_sources"]
            if len(unique_citations) > max_sources:
                results.append(ValidationResult(
                    check_name="citation_limit",
                    passed=False,
                    severity=ValidationSeverity.LOW,
                    message=f"Too many sources: {len(unique_citations)}/{max_sources}",
                    score=0.8
                ))
            
            if not has_duplicates and len(unique_citations) <= max_sources:
                results.append(ValidationResult(
                    check_name="citation_quality",
                    passed=True,
                    severity=ValidationSeverity.INFO,
                    message=f"Citation quality excellent: {len(unique_citations)} unique sources",
                    score=1.0
                ))
        
        return results
    
    def _validate_quality_metrics(self, response: str) -> List[ValidationResult]:
        """Validate quality metrics"""
        results = []
        
        # Word count validation
        word_count = len(response.split())
        min_words = self.validation_rules["quality"]["min_word_count"]
        max_words = self.validation_rules["quality"]["max_word_count"]
        
        if word_count < min_words:
            results.append(ValidationResult(
                check_name="word_count_minimum",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Response too short: {word_count}/{min_words} words",
                score=word_count / min_words
            ))
        elif word_count > max_words:
            results.append(ValidationResult(
                check_name="word_count_maximum",
                passed=False,
                severity=ValidationSeverity.LOW,
                message=f"Response too long: {word_count}/{max_words} words",
                score=max_words / word_count
            ))
        else:
            results.append(ValidationResult(
                check_name="word_count_optimal",
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Optimal length: {word_count} words",
                score=1.0
            ))
        
        # XML syntax validation (if XML present)
        xml_blocks = re.findall(r'```xml\s*\n(.*?)\n```', response, re.DOTALL)
        if xml_blocks:
            xml_valid = self._validate_xml_syntax(xml_blocks)
            results.append(ValidationResult(
                check_name="xml_syntax",
                passed=xml_valid,
                severity=ValidationSeverity.HIGH,
                message="XML syntax validation",
                score=1.0 if xml_valid else 0.5
            ))
        
        return results
    
    def _validate_xml_syntax(self, xml_blocks: List[str]) -> bool:
        """Basic XML syntax validation"""
        try:
            import xml.etree.ElementTree as ET
            for xml_content in xml_blocks:
                ET.fromstring(xml_content.strip())
            return True
        except Exception:
            return False
    
    def _generate_quality_report(self, results: List[ValidationResult]) -> ResponseQualityReport:
        """Generate comprehensive quality report"""
        total_checks = len(results)
        passed_checks = sum(1 for r in results if r.passed)
        
        # Calculate weighted score
        total_score = sum(r.score for r in results)
        overall_score = total_score / total_checks if total_checks > 0 else 0.0
        
        # Categorize issues
        critical_issues = [r for r in results if r.severity == ValidationSeverity.CRITICAL and not r.passed]
        warnings = [r for r in results if r.severity in [ValidationSeverity.HIGH, ValidationSeverity.MEDIUM] and not r.passed]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results)
        
        # Determine production readiness
        is_production_ready = (
            len(critical_issues) == 0 and
            overall_score >= 0.85 and
            passed_checks / total_checks >= 0.8
        )
        
        report = ResponseQualityReport(
            overall_score=overall_score,
            passed_checks=passed_checks,
            total_checks=total_checks,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations,
            is_production_ready=is_production_ready
        )
        
        logger.info(f"🎯 Validation complete - Score: {overall_score:.2f}, Production ready: {is_production_ready}")
        return report
    
    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for result in results:
            if not result.passed:
                if result.check_name == "language_purity":
                    recommendations.append("🇩🇪 Ersetzen Sie englische Begriffe durch deutsche Fachterminologie")
                elif result.check_name == "structure_compliance":
                    recommendations.append("📋 Vervollständigen Sie die Antwortstruktur mit allen erforderlichen Sektionen")
                elif result.check_name == "citation_required":
                    recommendations.append("📚 Fügen Sie Quellenangaben im Format 'Quelle: dateiname.ext' hinzu")
                elif result.check_name == "security_injection_check":
                    recommendations.append("🛡️ Entfernen Sie potentielle Sicherheitsverletzungen")
                elif result.check_name == "word_count_minimum":
                    recommendations.append("📏 Erweitern Sie die Antwort für mehr Details")
        
        return recommendations

# Global validator instance
enterprise_validator = EnterpriseResponseValidator()