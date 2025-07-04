"""
Robust Error Handler for StreamWorks-KI
Provides graceful fallbacks and error recovery
"""
import logging
import traceback
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
from cachetools import TTLCache
from pathlib import Path
import yaml

# Specific exception classes for better error handling
class LLMConnectionError(Exception):
    """Raised when LLM service connection fails"""
    pass

class LLMTimeoutError(Exception):
    """Raised when LLM service times out"""
    pass

class LLMGenerationError(Exception):
    """Raised when LLM generation fails"""
    pass

class RAGSearchError(Exception):
    """Raised when RAG search fails"""
    pass

class RAGEmbeddingError(Exception):
    """Raised when RAG embedding fails"""
    pass

class RAGVectorDBError(Exception):
    """Raised when RAG vector database fails"""
    pass

class XMLGenerationError(Exception):
    """Raised when XML generation fails"""
    pass

class XMLValidationError(Exception):
    """Raised when XML validation fails"""
    pass

class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    pass

class DatabaseQueryError(Exception):
    """Raised when database query fails"""
    pass

class APIValidationError(Exception):
    """Raised when API input validation fails"""
    pass

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """Types of errors that can occur"""
    LLM_CONNECTION = "llm_connection"
    LLM_TIMEOUT = "llm_timeout"
    LLM_GENERATION = "llm_generation"
    RAG_SEARCH = "rag_search"
    RAG_EMBEDDING = "rag_embedding"
    RAG_VECTORDB = "rag_vectordb"
    XML_GENERATION = "xml_generation"
    XML_VALIDATION = "xml_validation"
    DATABASE_CONNECTION = "database_connection"
    DATABASE_QUERY = "database_query"
    API_VALIDATION = "api_validation"
    SERVICE_UNAVAILABLE = "service_unavailable"
    UNKNOWN = "unknown"

class FallbackType(Enum):
    """Types of fallback responses"""
    CACHED = "cached"
    TEMPLATE = "template"
    STATIC = "static"
    DEGRADED = "degraded"
    ERROR = "error"

@dataclass
class FallbackResponse:
    """Represents a fallback response"""
    message: str
    fallback_type: FallbackType
    confidence: float
    error_type: ErrorType
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message": self.message,
            "fallback_type": self.fallback_type.value,
            "confidence": self.confidence,
            "error_type": self.error_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {},
            "is_fallback": True
        }

class StreamWorksErrorHandler:
    """Central error handler for StreamWorks-KI with TTL caching and pattern matching"""
    
    def __init__(self):
        # TTL Cache to prevent memory leaks
        self.error_cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes TTL
        self.error_counts = defaultdict(int)
        
        # Load response templates from external file if available
        self.cached_responses = self._load_response_templates()
        
        # Compile regex patterns for efficient error classification
        self.connection_pattern = re.compile(
            r'connection|connect|unreachable|refused|network', 
            re.IGNORECASE
        )
        self.timeout_pattern = re.compile(
            r'timeout|time|slow|duration', 
            re.IGNORECASE
        )
        self.generation_pattern = re.compile(
            r'generate|generation|model|inference', 
            re.IGNORECASE
        )
        self.vector_db_pattern = re.compile(
            r'chroma|vector|database|db|index', 
            re.IGNORECASE
        )
        self.embedding_pattern = re.compile(
            r'embedding|encode|transform|tokenize', 
            re.IGNORECASE
        )
        self.search_pattern = re.compile(
            r'search|query|retrieve|find', 
            re.IGNORECASE
        )
        self.validation_pattern = re.compile(
            r'validation|valid|schema|format', 
            re.IGNORECASE
        )
        self.xml_generation_pattern = re.compile(
            r'xml|template|stream|configuration', 
            re.IGNORECASE
        )
        self.db_connection_pattern = re.compile(
            r'database|connection|pool|sqlite|sql', 
            re.IGNORECASE
        )
        self.db_query_pattern = re.compile(
            r'query|execute|select|insert|update|delete', 
            re.IGNORECASE
        )
        
        logger.info("🛡️ Error Handler initialized with TTL cache and pattern matching")
    
    def _load_response_templates(self) -> Dict[str, str]:
        """Load response templates from external file or use defaults"""
        template_file = Path("./data/error_templates.yaml")
        
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load error templates: {e}")
        
        # Default templates (much shorter than before)
        return {
            "general_help": "📚 StreamWorks-KI ist temporär eingeschränkt verfügbar. Nutze Q&A System, XML Generator oder Batch Jobs. Versuche spezifische Fragen wie 'XML erstellen' oder 'Batch Job'.",
            "xml_help": "🔧 XML Generator verfügbar. Templates: Data Processing, Batch Jobs, API Integration. Beispiel: 'Erstelle Stream für CSV-Verarbeitung'. Nutze Template-Generator bei Problemen.",
            "technical_help": "⚙️ StreamWorks-KI nutzt RAG System + Mistral 7B. Bei Problemen: Frage neu formulieren, kürzere Anfragen, Template-basierte Generierung. Service wird wiederhergestellt."
        }
        
        # Default XML templates for fallbacks
        self.xml_fallback_templates = {
            "basic": '''<?xml version="1.0" encoding="UTF-8"?>
<stream xmlns="http://streamworks.arvato.com/schema/v1">
  <metadata>
    <name>FallbackStream</name>
    <description>Generated during service interruption</description>
    <version>1.0</version>
    <created>{timestamp}</created>
    <author>StreamWorks-KI-Fallback</author>
  </metadata>
  
  <configuration>
    <schedule>
      <cron>0 2 * * *</cron>
      <timezone>Europe/Berlin</timezone>
      <enabled>true</enabled>
    </schedule>
  </configuration>
  
  <pipeline>
    <tasks>
      <task id="placeholder" type="data_processing">
        <name>Placeholder Task</name>
        <note>Please review and customize this template</note>
      </task>
    </tasks>
  </pipeline>
</stream>'''
        }
        
        logger.info("🛡️ Error Handler initialized with fallback responses")
    
    async def handle_llm_error(self, error: Exception, context: Dict[str, Any] = None) -> FallbackResponse:
        """Handle LLM service errors with specific exception handling"""
        if isinstance(error, (LLMConnectionError, ConnectionError, TimeoutError)):
            error_type = ErrorType.LLM_CONNECTION
        elif isinstance(error, LLMTimeoutError):
            error_type = ErrorType.LLM_TIMEOUT
        elif isinstance(error, LLMGenerationError):
            error_type = ErrorType.LLM_GENERATION
        else:
            error_type = self._classify_llm_error(error)
        
        self._increment_error_count(error_type)
        logger.warning(f"🚨 LLM Error ({error_type.value}): {str(error)}")
        
        # Get context for better fallback
        query = context.get('query', '') if context else ''
        
        if error_type == ErrorType.LLM_CONNECTION:
            return FallbackResponse(
                message=self._get_cached_response(query, "connection_error"),
                fallback_type=FallbackType.CACHED,
                confidence=0.6,
                error_type=error_type,
                timestamp=datetime.now(),
                metadata={
                    "original_error": str(error),
                    "suggestion": "LLM Service wird wiederhergestellt. Versuche es in wenigen Minuten erneut."
                }
            )
        
        elif error_type == ErrorType.LLM_TIMEOUT:
            return FallbackResponse(
                message="⏱️ Die Anfrage dauert länger als erwartet. Bitte formuliere eine kürzere Frage oder versuche es erneut.",
                fallback_type=FallbackType.STATIC,
                confidence=0.3,
                error_type=error_type,
                timestamp=datetime.now(),
                metadata={
                    "timeout_duration": context.get('timeout', 'unknown') if context else 'unknown',
                    "suggestion": "Verwende kürzere, spezifischere Fragen für bessere Performance."
                }
            )
        
        elif error_type == ErrorType.LLM_GENERATION:
            return FallbackResponse(
                message=self._get_cached_response(query, "generation_error"),
                fallback_type=FallbackType.TEMPLATE,
                confidence=0.5,
                error_type=error_type,
                timestamp=datetime.now(),
                metadata={
                    "fallback_reason": "LLM generation failed",
                    "suggestion": "Verwende Template-basierte Antworten."
                }
            )
        
        else:
            return FallbackResponse(
                message=self.cached_responses["general_help"],
                fallback_type=FallbackType.STATIC,
                confidence=0.4,
                error_type=error_type,
                timestamp=datetime.now(),
                metadata={"error": str(error)}
            )
    
    async def handle_rag_error(self, error: Exception, context: Dict[str, Any] = None) -> FallbackResponse:
        """Handle RAG service errors with specific exception handling"""
        if isinstance(error, RAGVectorDBError):
            error_type = ErrorType.RAG_VECTORDB
        elif isinstance(error, RAGEmbeddingError):
            error_type = ErrorType.RAG_EMBEDDING
        elif isinstance(error, RAGSearchError):
            error_type = ErrorType.RAG_SEARCH
        else:
            error_type = self._classify_rag_error(error)
        
        self._increment_error_count(error_type)
        logger.warning(f"🔍 RAG Error ({error_type.value}): {str(error)}")
        
        query = context.get('query', '') if context else ''
        
        if error_type == ErrorType.RAG_VECTORDB:
            return FallbackResponse(
                message="""
🔍 **Suchfunktion temporär eingeschränkt**

Die Dokumentensuche ist momentan nicht verfügbar. Hier sind einige häufige Themen:

## StreamWorks Grundlagen:
- StreamWorks ist eine Plattform für Workflow-Automatisierung
- Unterstützt Batch-Jobs, Datenverarbeitung und API-Integration
- Konfiguration erfolgt über XML-Streams

## Hilfe bei XML-Generierung:
- Nutze den **Stream Generator** Tab
- Wähle Template basierend auf deinem Use Case
- Passe die Parameter entsprechend an

*Die Suchfunktion wird automatisch wiederhergestellt.*
                """,
                fallback_type=FallbackType.STATIC,
                confidence=0.6,
                error_type=error_type,
                timestamp=datetime.now(),
                metadata={"suggestion": "Nutze den Stream Generator für XML-Erstellung"}
            )
        
        elif error_type == ErrorType.RAG_EMBEDDING:
            return FallbackResponse(
                message=f"""
🤖 **Verarbeitungsproblem erkannt**

Deine Anfrage: "{query[:100]}..." konnte nicht vollständig verarbeitet werden.

**Lösungsvorschläge:**
1. **Vereinfache die Frage**: Verwende konkretere Begriffe
2. **Teile komplexe Fragen auf**: Stelle mehrere kleinere Fragen
3. **Nutze Keywords**: z.B. "XML erstellen", "Batch Job", "API Integration"

**Alternative:** Verwende den Stream Generator im entsprechenden Tab.
                """,
                fallback_type=FallbackType.TEMPLATE,
                confidence=0.5,
                error_type=error_type,
                timestamp=datetime.now(),
                metadata={
                    "query_length": len(query),
                    "suggestion": "Reformuliere die Frage mit spezifischen Keywords"
                }
            )
        
        else:
            return FallbackResponse(
                message=self.cached_responses["technical_help"],
                fallback_type=FallbackType.CACHED,
                confidence=0.4,
                error_type=error_type,
                timestamp=datetime.now()
            )
    
    async def handle_xml_error(self, error: Exception, context: Dict[str, Any] = None) -> FallbackResponse:
        """Handle XML generation errors with specific exception handling"""
        if isinstance(error, XMLValidationError):
            error_type = ErrorType.XML_VALIDATION
        elif isinstance(error, XMLGenerationError):
            error_type = ErrorType.XML_GENERATION
        else:
            error_type = self._classify_xml_error(error)
        
        self._increment_error_count(error_type)
        logger.warning(f"🔧 XML Error ({error_type.value}): {str(error)}")
        
        # Generate fallback XML
        requirements = context.get('requirements', {}) if context else {}
        fallback_xml = self._generate_fallback_xml(requirements)
        
        if error_type == ErrorType.XML_GENERATION:
            message = f"""
# 🔧 XML Stream (Fallback-Modus)

**Hinweis**: Die KI-basierte XML-Generierung ist temporär nicht verfügbar. 
Hier ist ein Basis-Template basierend auf deinen Angaben:

```xml
{fallback_xml}
```

**⚠️ Wichtig**: Bitte überprüfe und passe die Konfiguration an deine spezifischen Anforderungen an.

**Empfehlung**: Verwende den Stream Generator Tab für eine interaktive Konfiguration.
            """
        
        elif error_type == ErrorType.XML_VALIDATION:
            message = f"""
# ⚠️ XML Validierungsfehler

Bei der Validierung ist ein Problem aufgetreten: {str(error)}

**Fallback-Template**:
```xml
{fallback_xml}
```

**Lösungsschritte**:
1. Überprüfe die XML-Syntax
2. Stelle sicher, dass alle Tags geschlossen sind
3. Validiere gegen StreamWorks Schema

**Alternative**: Nutze den Template-basierten Generator.
            """
        
        else:
            message = f"""
# 🔧 XML Generator Fehler

Ein technisches Problem ist aufgetreten. Hier ist ein Standard-Template:

```xml
{fallback_xml}
```

**Bitte manuell anpassen für deine Anforderungen.**
            """
        
        return FallbackResponse(
            message=message,
            fallback_type=FallbackType.TEMPLATE,
            confidence=0.7,  # Template is reliable
            error_type=error_type,
            timestamp=datetime.now(),
            metadata={
                "fallback_xml_provided": True,
                "template_type": "basic",
                "requirements": requirements
            }
        )
    
    async def handle_database_error(self, error: Exception, context: Dict[str, Any] = None) -> FallbackResponse:
        """Handle database errors with specific exception handling"""
        if isinstance(error, DatabaseConnectionError):
            error_type = ErrorType.DATABASE_CONNECTION
        elif isinstance(error, DatabaseQueryError):
            error_type = ErrorType.DATABASE_QUERY
        else:
            error_type = self._classify_database_error(error)
        
        self._increment_error_count(error_type)
        logger.error(f"🗄️ Database Error ({error_type.value}): {str(error)}")
        
        return FallbackResponse(
            message="""
🗄️ **Datenbank temporär nicht verfügbar**

Die Datenpersistierung ist momentan eingeschränkt. Deine Anfrage wurde verarbeitet, aber:

- **Verlauf wird nicht gespeichert**
- **Metriken sind eingeschränkt**
- **Evaluierungsdaten gehen verloren**

**Das System funktioniert weiterhin für:**
- Q&A Anfragen (ohne Verlauf)
- XML Generierung (Template-basiert)
- Dokumentensuche (Speicher-basiert)

*Die Datenbank wird automatisch wiederhergestellt.*
            """,
            fallback_type=FallbackType.DEGRADED,
            confidence=0.8,  # Core functionality still works
            error_type=error_type,
            timestamp=datetime.now(),
            metadata={
                "core_functions_available": True,
                "data_persistence": False
            }
        )
    
    async def handle_api_validation_error(self, error: Exception, context: Dict[str, Any] = None) -> FallbackResponse:
        """Handle API validation errors with specific exception handling"""
        if isinstance(error, APIValidationError):
            error_type = ErrorType.API_VALIDATION
        elif isinstance(error, ValueError):
            error_type = ErrorType.API_VALIDATION
        else:
            error_type = ErrorType.API_VALIDATION
        
        self._increment_error_count(error_type)
        logger.warning(f"📝 API Validation Error: {str(error)}")
        
        # Extract validation details if available
        error_details = str(error)
        field_error = None
        
        if "message" in error_details.lower():
            field_error = "Nachricht zu kurz oder leer"
        elif "length" in error_details.lower():
            field_error = "Eingabe zu lang (Max: 4000 Zeichen)"
        elif "format" in error_details.lower():
            field_error = "Ungültiges Format"
        
        message = f"""
📝 **Eingabe-Validierungsfehler**

{field_error or error_details}

**Lösungsvorschläge:**
1. **Nachrichtenlänge**: 1-4000 Zeichen
2. **Keine leeren Nachrichten**: Stelle eine konkrete Frage
3. **Spezielle Zeichen**: Vermeide problematische Symbole
4. **Format**: Verwende Klartext ohne komplexe Formatierung

**Beispiel-Anfragen:**
- "Was ist StreamWorks?"
- "Erstelle einen XML-Stream für CSV-Verarbeitung"
- "Wie automatisiere ich Batch-Jobs?"

*Bitte versuche es mit einer angepassten Eingabe erneut.*
        """
        
        return FallbackResponse(
            message=message,
            fallback_type=FallbackType.STATIC,
            confidence=0.9,  # Validation errors are clear
            error_type=error_type,
            timestamp=datetime.now(),
            metadata={
                "validation_error": error_details,
                "field_error": field_error,
                "user_action_required": True
            }
        )
    
    def _classify_llm_error(self, error: Exception) -> ErrorType:
        """Classify LLM-related errors using compiled regex patterns"""
        error_str = str(error)
        
        if self.connection_pattern.search(error_str):
            return ErrorType.LLM_CONNECTION
        elif self.timeout_pattern.search(error_str):
            return ErrorType.LLM_TIMEOUT
        elif self.generation_pattern.search(error_str):
            return ErrorType.LLM_GENERATION
        else:
            return ErrorType.UNKNOWN
    
    def _classify_rag_error(self, error: Exception) -> ErrorType:
        """Classify RAG-related errors using compiled regex patterns"""
        error_str = str(error)
        
        if self.vector_db_pattern.search(error_str):
            return ErrorType.RAG_VECTORDB
        elif self.embedding_pattern.search(error_str):
            return ErrorType.RAG_EMBEDDING
        elif self.search_pattern.search(error_str):
            return ErrorType.RAG_SEARCH
        else:
            return ErrorType.UNKNOWN
    
    def _classify_xml_error(self, error: Exception) -> ErrorType:
        """Classify XML-related errors using compiled regex patterns"""
        error_str = str(error)
        
        if self.validation_pattern.search(error_str):
            return ErrorType.XML_VALIDATION
        elif self.xml_generation_pattern.search(error_str):
            return ErrorType.XML_GENERATION
        else:
            return ErrorType.UNKNOWN
    
    def _classify_database_error(self, error: Exception) -> ErrorType:
        """Classify database-related errors using compiled regex patterns"""
        error_str = str(error)
        
        if self.db_connection_pattern.search(error_str):
            return ErrorType.DATABASE_CONNECTION
        elif self.db_query_pattern.search(error_str):
            return ErrorType.DATABASE_QUERY
        else:
            return ErrorType.UNKNOWN
    
    def _get_cached_response(self, query: str, error_context: str = "general") -> str:
        """Get appropriate cached response based on query using pattern matching"""
        # Use compiled patterns for efficient matching
        xml_pattern = re.compile(r'xml|stream|erstell|generier|template', re.IGNORECASE)
        help_pattern = re.compile(r'was ist|hilfe|help|erkläre|info', re.IGNORECASE)
        
        if xml_pattern.search(query):
            return self.cached_responses["xml_help"]
        elif help_pattern.search(query):
            return self.cached_responses["general_help"]
        else:
            return self.cached_responses["technical_help"]
    
    def _generate_fallback_xml(self, requirements: Dict[str, Any]) -> str:
        """Generate basic fallback XML"""
        timestamp = datetime.now().isoformat()
        name = requirements.get('name', 'FallbackStream')
        
        return self.xml_fallback_templates["basic"].format(
            timestamp=timestamp,
            name=name
        )
    
    def _increment_error_count(self, error_type: ErrorType):
        """Track error counts for monitoring"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    async def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        total_errors = sum(self.error_counts.values())
        
        return {
            "total_errors": total_errors,
            "error_counts": {et.value: count for et, count in self.error_counts.items()},
            "most_common_error": max(self.error_counts.items(), key=lambda x: x[1])[0].value if self.error_counts else "none",
            "cache_size": len(self.error_cache),
            "cached_responses": len(self.cached_responses),
            "timestamp": datetime.now().isoformat()
        }
    
    async def reset_error_counts(self):
        """Reset error counts (for testing/monitoring)"""
        self.error_counts.clear()
        logger.info("🧹 Error counts reset")

# Global instance
error_handler = StreamWorksErrorHandler()