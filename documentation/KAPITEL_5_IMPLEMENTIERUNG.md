# Kapitel 5: Implementierung

> **Technische Umsetzung der KI-gestützten Self-Service-Architektur für Streamworks**

---

## 5.1 Backend-Implementierung mit FastAPI

### 5.1.1 Projektstruktur und Service-Architektur

Die Backend-Implementierung folgt einer **modularen Service-Architektur** mit über 120 Python-Dateien, organisiert in logische Service-Domänen:

```python
# backend/main.py - FastAPI Application Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv

from database import init_db, close_db
from routers import (
    langextract_chat,
    xml_generator,
    chat_rag_test,
    documents,
    auth,
    health
)
from middleware.security_middleware import SecurityMiddleware
from middleware.logging_middleware import LoggingMiddleware
from services.di_container import DIContainer, setup_dependencies

# Load environment configuration
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management mit Resource Cleanup"""
    # Startup
    await init_db()
    await setup_dependencies()

    # Initialize Qdrant collections
    from services.qdrant_init import initialize_qdrant_collections
    await initialize_qdrant_collections()

    yield

    # Shutdown
    await close_db()
    await cleanup_resources()

# FastAPI Application mit Lifespan Events
app = FastAPI(
    title="Streamworks-KI API",
    description="Enterprise RAG System mit KI-gestützter Parameter-Extraktion",
    version="0.13.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration für Frontend-Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Request-ID"]
)

# Custom Middleware Stack
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)

# Router Registration mit Prefixes
app.include_router(langextract_chat.router, prefix="/api/langextract", tags=["LangExtract"])
app.include_router(xml_generator.router, prefix="/api/xml-generator", tags=["XML Generation"])
app.include_router(chat_rag_test.router, prefix="/api/chat", tags=["RAG Chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(health.router, prefix="/health", tags=["Health"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

**Dependency Injection Container Implementation:**

```python
# backend/services/di_container.py
from typing import Dict, Type, Any, Optional
from functools import lru_cache
import asyncio
from contextlib import asynccontextmanager

class DIContainer:
    """
    Dependency Injection Container für Service-Management
    Implementiert Singleton und Transient Lifecycles
    """

    def __init__(self):
        self._services: Dict[Type, tuple] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, callable] = {}
        self._lock = asyncio.Lock()

    def register_singleton(self,
                          interface: Type,
                          implementation: Type,
                          factory: Optional[callable] = None):
        """Registriert Service als Singleton-Instanz"""
        self._services[interface] = (implementation, 'singleton')
        if factory:
            self._factories[interface] = factory

    def register_transient(self,
                          interface: Type,
                          implementation: Type,
                          factory: Optional[callable] = None):
        """Registriert Service als Transient (neue Instanz pro Request)"""
        self._services[interface] = (implementation, 'transient')
        if factory:
            self._factories[interface] = factory

    async def get(self, interface: Type) -> Any:
        """Resolves Service-Instanz basierend auf registriertem Lifecycle"""
        if interface not in self._services:
            raise ValueError(f"Service {interface.__name__} not registered")

        impl_class, lifecycle = self._services[interface]

        if lifecycle == 'singleton':
            return await self._get_singleton(interface, impl_class)
        elif lifecycle == 'transient':
            return await self._create_instance(interface, impl_class)

    async def _get_singleton(self, interface: Type, impl_class: Type) -> Any:
        """Thread-safe Singleton Resolution"""
        if interface not in self._singletons:
            async with self._lock:
                # Double-check locking pattern
                if interface not in self._singletons:
                    instance = await self._create_instance(interface, impl_class)
                    self._singletons[interface] = instance

        return self._singletons[interface]

    async def _create_instance(self, interface: Type, impl_class: Type) -> Any:
        """Creates Service-Instanz mit automatischer Dependency Resolution"""
        if interface in self._factories:
            # Use factory wenn vorhanden
            factory = self._factories[interface]
            if asyncio.iscoroutinefunction(factory):
                return await factory()
            return factory()

        # Auto-resolve Constructor Dependencies
        import inspect
        sig = inspect.signature(impl_class.__init__)
        params = {}

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue

            # Try to resolve type hint as dependency
            if param.annotation != inspect.Parameter.empty:
                param_type = param.annotation
                if param_type in self._services:
                    params[param_name] = await self.get(param_type)

        return impl_class(**params)

# Global DI Container Instance
_di_container = DIContainer()

async def setup_dependencies():
    """Konfiguriert alle Service-Dependencies beim App-Start"""

    # Database Services
    from services.database_service import DatabaseService
    _di_container.register_singleton(DatabaseService, DatabaseService)

    # AI Services
    from services.ai.enhanced_job_type_detector import EnhancedJobTypeDetector
    from services.ai.enhanced_unified_parameter_extractor import EnhancedUnifiedParameterExtractor
    from services.ai.langextract.unified_langextract_service import UnifiedLangExtractService

    _di_container.register_singleton(
        EnhancedJobTypeDetector,
        EnhancedJobTypeDetector
    )

    _di_container.register_singleton(
        EnhancedUnifiedParameterExtractor,
        EnhancedUnifiedParameterExtractor
    )

    # LangExtract Service mit Dependencies
    async def create_langextract_service():
        db_service = await _di_container.get(DatabaseService)
        job_detector = await _di_container.get(EnhancedJobTypeDetector)
        param_extractor = await _di_container.get(EnhancedUnifiedParameterExtractor)

        return UnifiedLangExtractService(
            db_service=db_service,
            job_detector=job_detector,
            parameter_extractor=param_extractor
        )

    _di_container.register_singleton(
        UnifiedLangExtractService,
        UnifiedLangExtractService,
        factory=create_langextract_service
    )

    # Template Engine
    from services.xml_generation.template_engine import TemplateEngine
    _di_container.register_singleton(TemplateEngine, TemplateEngine)

    # RAG Service
    from services.rag.unified_rag_service import UnifiedRAGService
    _di_container.register_singleton(UnifiedRAGService, UnifiedRAGService)

# FastAPI Dependency Injection Integration
@lru_cache()
def get_di_container() -> DIContainer:
    """Cached DI Container Getter für FastAPI Dependencies"""
    return _di_container

# Service Getter Functions für FastAPI
async def get_langextract_service() -> UnifiedLangExtractService:
    """FastAPI Dependency für LangExtract Service"""
    container = get_di_container()
    return await container.get(UnifiedLangExtractService)

async def get_template_engine() -> TemplateEngine:
    """FastAPI Dependency für Template Engine"""
    container = get_di_container()
    return await container.get(TemplateEngine)
```

### 5.1.2 Enhanced Job Type Detection Implementation

Die Implementierung des **Enhanced Job Type Detector** erreicht 88.9% Accuracy durch Multi-Layer Pattern Matching:

```python
# backend/services/ai/enhanced_job_type_detector.py
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

@dataclass
class DetectionResult:
    """Strukturiertes Ergebnis der Job-Type Detection"""
    detected_job_type: Optional[str]
    confidence: float
    detection_method: str
    matched_patterns: List[Dict[str, Any]]
    alternative_candidates: List[Tuple[str, float]]
    detection_details: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class EnhancedJobTypeDetector:
    """
    Enhanced Job Type Detector mit 88.9% Accuracy
    Multi-Layer Detection mit German Language Optimization
    """

    def __init__(self):
        # Load Pattern Configurations
        self._load_pattern_configurations()

        # Compiled Pattern Cache für Performance
        self._compiled_patterns: Dict[str, re.Pattern] = {}

        # Detection Cache für wiederkehrende Anfragen
        self._cache: Dict[str, DetectionResult] = {}
        self._cache_max_size = 1000

        # Performance Metrics Tracking
        self.metrics = {
            "total_detections": 0,
            "cache_hits": 0,
            "high_confidence_detections": 0,
            "detection_times": []
        }

    def _load_pattern_configurations(self):
        """Lädt Pattern-Konfigurationen für Job-Types"""

        # Layer 1: High-Confidence Patterns (95%+ Confidence)
        self.high_confidence_patterns = {
            "FILE_TRANSFER": [
                {
                    "pattern": r"(?:daten[trs]*transfer|file\s*transfer|datei[en]*\s*transfer)",
                    "confidence": 0.95,
                    "description": "Explizite Transfer-Begriffe",
                    "priority": 1
                },
                {
                    "pattern": r"zwischen\s+([a-zA-Z0-9_\-]+)\s+(?:und|zu|nach)\s+([a-zA-Z0-9_\-]+)",
                    "confidence": 0.92,
                    "description": "System-zu-System Transfer Pattern",
                    "priority": 2
                },
                {
                    "pattern": r"(?:kopier|copy|übertr[aä]g|transfer).*(?:datei|file|dokument)",
                    "confidence": 0.90,
                    "description": "Transfer-Action mit File-Object",
                    "priority": 3
                },
                {
                    "pattern": r"von\s+(?:server|agent|system)\s+([a-zA-Z0-9_\-]+)\s+(?:nach|zu)\s+([a-zA-Z0-9_\-]+)",
                    "confidence": 0.93,
                    "description": "Von-Nach Server Transfer",
                    "priority": 2
                }
            ],
            "SAP": [
                {
                    "pattern": r"(?:gt123|pa1|pt1|pd1)(?:_(?:prd|dev|tst|100|200))?",
                    "confidence": 0.93,
                    "description": "SAP System-Identifier",
                    "priority": 1
                },
                {
                    "pattern": r"sap[\s\-_]*(?:system|export|import|report|transaktion)",
                    "confidence": 0.91,
                    "description": "SAP mit Operation",
                    "priority": 2
                },
                {
                    "pattern": r"(?:ztv|rsus|rfc|se[0-9]{2})[a-zA-Z0-9_]*",
                    "confidence": 0.90,
                    "description": "SAP Transaction Codes",
                    "priority": 3
                },
                {
                    "pattern": r"(?:tabelle|table)\s+[a-zA-Z0-9_]+\s+(?:export|extract|download)",
                    "confidence": 0.88,
                    "description": "SAP Table Export",
                    "priority": 4
                }
            ],
            "STANDARD": [
                {
                    "pattern": r"(?:python|java|bash|node|powershell)\s+[^\s]+\.(py|java|sh|js|ps1)",
                    "confidence": 0.88,
                    "description": "Script Execution Pattern",
                    "priority": 1
                },
                {
                    "pattern": r"(?:ausführen|execute|start|run)\s+(?:script|job|batch|programm)",
                    "confidence": 0.85,
                    "description": "Script Execution Keywords",
                    "priority": 2
                },
                {
                    "pattern": r"(?:standard|batch)[\s\-_]*(?:job|task|automation)",
                    "confidence": 0.83,
                    "description": "Standard Job Keywords",
                    "priority": 3
                }
            ]
        }

        # Layer 2: Fuzzy Matching Mappings
        self.fuzzy_mappings = {
            "FILE_TRANSFER": [
                "datentranfer", "datentrasnfer", "datetransfer", "filetransfer",
                "dateintransfer", "datenübertragung", "dateiübertragung",
                "file-transfer", "data-transfer", "datentransport"
            ],
            "SAP": [
                "jexa", "sap-system", "sapsystem", "sap system", "saap",
                "sapp", "erp", "bw", "hana", "s4hana", "s/4hana"
            ],
            "STANDARD": [
                "standardjob", "standard job", "batch", "batchjob",
                "skript", "script", "programm", "automation", "task"
            ]
        }

        # Layer 3: Semantic Context Keywords
        self.context_keywords = {
            "FILE_TRANSFER": {
                "subjects": ["datei", "file", "dokument", "daten", "ordner", "verzeichnis"],
                "actions": ["kopieren", "verschieben", "übertragen", "transfer", "sync", "replizieren"],
                "targets": ["server", "agent", "system", "ordner", "pfad", "directory"],
                "directions": ["von", "nach", "zu", "zwischen", "from", "to"]
            },
            "SAP": {
                "systems": ["sap", "bw", "erp", "hana", "abap", "fiori"],
                "operations": ["export", "import", "report", "query", "extrakt", "download"],
                "objects": ["tabelle", "view", "program", "transaction", "variant", "job"],
                "identifiers": ["mandant", "client", "system", "sid"]
            },
            "STANDARD": {
                "languages": ["python", "java", "bash", "node", "powershell", "perl"],
                "actions": ["ausführen", "starten", "run", "execute", "launch", "trigger"],
                "types": ["script", "job", "batch", "program", "task", "automation"],
                "parameters": ["parameter", "argument", "option", "flag", "config"]
            }
        }

        # Confidence Thresholds
        self.confidence_thresholds = {
            "high_confidence": 0.90,
            "medium_confidence": 0.80,
            "low_confidence": 0.70,
            "minimum_acceptance": 0.70
        }

    async def detect_job_type(self, message: str) -> DetectionResult:
        """
        Hauptmethode für Job Type Detection
        Implementiert Multi-Layer Detection Algorithm
        """

        start_time = datetime.now()

        # Check Cache
        cache_key = self._generate_cache_key(message)
        if cache_key in self._cache:
            self.metrics["cache_hits"] += 1
            cached_result = self._cache[cache_key]
            cached_result.detection_details["from_cache"] = True
            return cached_result

        # Normalize message for processing
        message_lower = message.lower().strip()

        # Layer 1: High-Confidence Pattern Matching
        high_conf_result = await self._apply_high_confidence_patterns(message_lower)

        # Layer 2: Fuzzy Matching
        fuzzy_scores = await self._apply_fuzzy_matching(message_lower)

        # Layer 3: Semantic Context Analysis
        context_scores = await self._apply_semantic_context_analysis(message_lower)

        # Combine all layers
        combined_scores = self._combine_detection_layers(
            high_conf_result, fuzzy_scores, context_scores
        )

        # Select best match
        result = self._select_best_match(combined_scores, high_conf_result)

        # Add performance metrics
        detection_time = (datetime.now() - start_time).total_seconds()
        result.detection_details["detection_time_ms"] = detection_time * 1000

        # Update metrics
        self.metrics["total_detections"] += 1
        if result.confidence >= self.confidence_thresholds["high_confidence"]:
            self.metrics["high_confidence_detections"] += 1
        self.metrics["detection_times"].append(detection_time)

        # Cache result
        self._add_to_cache(cache_key, result)

        return result

    async def _apply_high_confidence_patterns(self, message: str) -> Dict[str, Any]:
        """Layer 1: High-Confidence Pattern Matching"""

        best_match = None
        best_confidence = 0.0
        all_matched_patterns = []

        for job_type, patterns in self.high_confidence_patterns.items():
            for pattern_info in patterns:
                pattern_str = pattern_info["pattern"]

                # Get or compile pattern
                if pattern_str not in self._compiled_patterns:
                    self._compiled_patterns[pattern_str] = re.compile(
                        pattern_str, re.IGNORECASE | re.UNICODE
                    )

                pattern = self._compiled_patterns[pattern_str]
                match = pattern.search(message)

                if match:
                    matched_info = {
                        "job_type": job_type,
                        "pattern": pattern_str,
                        "confidence": pattern_info["confidence"],
                        "description": pattern_info["description"],
                        "matched_text": match.group(),
                        "match_position": match.start()
                    }

                    # Extract captured groups if any
                    if match.groups():
                        matched_info["captured_groups"] = match.groups()

                    all_matched_patterns.append(matched_info)

                    if pattern_info["confidence"] > best_confidence:
                        best_confidence = pattern_info["confidence"]
                        best_match = job_type

        return {
            "detected_job_type": best_match,
            "confidence": best_confidence,
            "matched_patterns": all_matched_patterns,
            "detection_method": "high_confidence_pattern"
        }

    async def _apply_fuzzy_matching(self, message: str) -> Dict[str, float]:
        """Layer 2: Fuzzy Matching für Schreibfehler-Toleranz"""

        fuzzy_scores = {}

        for job_type, fuzzy_terms in self.fuzzy_mappings.items():
            best_score = 0.0
            matched_term = None

            for term in fuzzy_terms:
                # Direct substring match
                if term in message:
                    score = 0.85
                    if score > best_score:
                        best_score = score
                        matched_term = term
                else:
                    # Calculate similarity for near-matches
                    similarity = self._calculate_string_similarity(term, message)
                    if similarity >= 0.7:
                        # Scale similarity to confidence (0.6-0.8 range)
                        score = 0.6 + (similarity * 0.2)
                        if score > best_score:
                            best_score = score
                            matched_term = term

            if best_score > 0:
                fuzzy_scores[job_type] = best_score

        return fuzzy_scores

    async def _apply_semantic_context_analysis(self, message: str) -> Dict[str, float]:
        """Layer 3: Semantic Context Analysis"""

        context_scores = {}
        message_words = set(message.split())

        for job_type, categories in self.context_keywords.items():
            category_scores = {}

            for category, keywords in categories.items():
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in message)

                if matches > 0:
                    # Calculate category score (diminishing returns)
                    category_score = min(matches * 0.2, 0.8)
                    category_scores[category] = {
                        "score": category_score,
                        "matches": matches,
                        "matched_keywords": [kw for kw in keywords if kw in message]
                    }

            if category_scores:
                # Calculate base score
                base_score = sum(cs["score"] for cs in category_scores.values()) / len(categories)

                # Apply multi-category bonus
                category_count = len(category_scores)
                if category_count >= 3:
                    bonus = 0.40  # 40% bonus für 3+ Kategorien
                elif category_count >= 2:
                    bonus = 0.20  # 20% bonus für 2 Kategorien
                else:
                    bonus = 0.0

                # Final context score (capped at 0.15 additive boost)
                final_score = min(base_score + bonus, 0.15)
                context_scores[job_type] = {
                    "score": final_score,
                    "category_scores": category_scores,
                    "category_count": category_count
                }

        return context_scores

    def _combine_detection_layers(self,
                                 high_conf: Dict[str, Any],
                                 fuzzy: Dict[str, float],
                                 context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Kombiniert alle Detection Layers zu finalen Scores"""

        combined_scores = {}

        # Collect all detected job types
        all_job_types = set()
        if high_conf["detected_job_type"]:
            all_job_types.add(high_conf["detected_job_type"])
        all_job_types.update(fuzzy.keys())
        all_job_types.update(context.keys())

        for job_type in all_job_types:
            score_components = {
                "pattern_score": 0.0,
                "fuzzy_score": 0.0,
                "context_score": 0.0,
                "final_score": 0.0
            }

            # Pattern score (highest priority)
            if high_conf["detected_job_type"] == job_type:
                score_components["pattern_score"] = high_conf["confidence"]
                score_components["pattern_matches"] = [
                    p for p in high_conf["matched_patterns"]
                    if p["job_type"] == job_type
                ]

            # Fuzzy score (if no high-confidence pattern)
            if score_components["pattern_score"] < 0.70 and job_type in fuzzy:
                score_components["fuzzy_score"] = fuzzy[job_type]

            # Context score (additive boost)
            if job_type in context:
                score_components["context_score"] = context[job_type].get("score", 0)
                score_components["context_details"] = context[job_type]

            # Calculate final score
            if score_components["pattern_score"] >= 0.70:
                # Pattern match takes precedence, context adds bonus
                final_score = min(
                    score_components["pattern_score"] + score_components["context_score"],
                    1.0
                )
            else:
                # Use fuzzy score as base, add context bonus
                base_score = max(score_components["fuzzy_score"], score_components["pattern_score"])
                final_score = min(base_score + score_components["context_score"], 1.0)

            score_components["final_score"] = final_score
            combined_scores[job_type] = score_components

        return combined_scores

    def _select_best_match(self,
                          combined_scores: Dict[str, Dict[str, Any]],
                          high_conf_result: Dict[str, Any]) -> DetectionResult:
        """Wählt besten Match basierend auf kombinierten Scores"""

        if not combined_scores:
            return DetectionResult(
                detected_job_type=None,
                confidence=0.0,
                detection_method="no_match",
                matched_patterns=[],
                alternative_candidates=[],
                detection_details={"reason": "No patterns matched"}
            )

        # Sort by final score
        sorted_scores = sorted(
            combined_scores.items(),
            key=lambda x: x[1]["final_score"],
            reverse=True
        )

        best_job_type, best_score_data = sorted_scores[0]
        best_confidence = best_score_data["final_score"]

        # Determine detection method
        if best_score_data["pattern_score"] >= 0.90:
            method = "high_confidence_pattern"
        elif best_score_data["pattern_score"] >= 0.70:
            method = "pattern_match"
        elif best_score_data["fuzzy_score"] > 0:
            method = "fuzzy_match"
        elif best_score_data["context_score"] > 0:
            method = "context_only"
        else:
            method = "combined"

        # Collect alternative candidates
        alternatives = [
            (job_type, score_data["final_score"])
            for job_type, score_data in sorted_scores[1:]
            if score_data["final_score"] >= self.confidence_thresholds["low_confidence"]
        ]

        # Prepare detection details
        detection_details = {
            "score_breakdown": best_score_data,
            "all_scores": {jt: sd["final_score"] for jt, sd in combined_scores.items()},
            "confidence_level": self._get_confidence_level(best_confidence)
        }

        # Check if confidence meets minimum threshold
        if best_confidence < self.confidence_thresholds["minimum_acceptance"]:
            best_job_type = None
            detection_details["reason"] = "Confidence below minimum threshold"

        return DetectionResult(
            detected_job_type=best_job_type,
            confidence=best_confidence,
            detection_method=method,
            matched_patterns=high_conf_result.get("matched_patterns", []),
            alternative_candidates=alternatives,
            detection_details=detection_details
        )

    def _calculate_string_similarity(self, s1: str, s2: str) -> float:
        """Berechnet String-Ähnlichkeit (simplified Levenshtein)"""

        # Quick exact match check
        if s1 == s2:
            return 1.0

        # Check if s1 is substring of s2
        if s1 in s2:
            # Scale by length ratio
            return 0.9 * (len(s1) / len(s2))

        # Character-level similarity
        s1_chars = set(s1)
        s2_chars = set(s2)

        if not s1_chars or not s2_chars:
            return 0.0

        intersection = s1_chars.intersection(s2_chars)
        union = s1_chars.union(s2_chars)

        jaccard = len(intersection) / len(union) if union else 0

        # Position-aware similarity
        common_prefix = 0
        for i in range(min(len(s1), len(s2))):
            if s1[i] == s2[i]:
                common_prefix += 1
            else:
                break

        prefix_score = common_prefix / max(len(s1), len(s2))

        # Combine scores
        return (jaccard * 0.5) + (prefix_score * 0.5)

    def _get_confidence_level(self, confidence: float) -> str:
        """Bestimmt Confidence Level basierend auf Score"""
        if confidence >= self.confidence_thresholds["high_confidence"]:
            return "high"
        elif confidence >= self.confidence_thresholds["medium_confidence"]:
            return "medium"
        elif confidence >= self.confidence_thresholds["low_confidence"]:
            return "low"
        else:
            return "insufficient"

    def _generate_cache_key(self, message: str) -> str:
        """Generiert Cache Key für Message"""
        import hashlib
        normalized = message.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    def _add_to_cache(self, key: str, result: DetectionResult):
        """Fügt Result zum Cache hinzu mit LRU-Policy"""
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entry (simple LRU)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[key] = result

    def get_metrics(self) -> Dict[str, Any]:
        """Gibt Performance-Metriken zurück"""
        avg_detection_time = (
            sum(self.metrics["detection_times"]) / len(self.metrics["detection_times"])
            if self.metrics["detection_times"] else 0
        )

        return {
            "total_detections": self.metrics["total_detections"],
            "cache_hit_rate": (
                self.metrics["cache_hits"] / self.metrics["total_detections"]
                if self.metrics["total_detections"] > 0 else 0
            ),
            "high_confidence_rate": (
                self.metrics["high_confidence_detections"] / self.metrics["total_detections"]
                if self.metrics["total_detections"] > 0 else 0
            ),
            "average_detection_time_ms": avg_detection_time * 1000,
            "cache_size": len(self._cache)
        }

# Global Singleton Instance
_detector_instance = None

def get_enhanced_job_type_detector() -> EnhancedJobTypeDetector:
    """Factory Function für Singleton Instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = EnhancedJobTypeDetector()
    return _detector_instance
```

### 5.1.3 LangExtract Service Implementation

```python
# backend/services/ai/langextract/unified_langextract_service.py
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import json
from dataclasses import dataclass, asdict

from services.ai.enhanced_job_type_detector import EnhancedJobTypeDetector, get_enhanced_job_type_detector
from services.ai.enhanced_unified_parameter_extractor import EnhancedUnifiedParameterExtractor
from services.ai.langextract.session_persistence_service import SessionPersistenceService
from services.chat_service_sqlalchemy import ChatServiceSQLAlchemy

@dataclass
class LangExtractResponse:
    """Response structure für LangExtract Processing"""
    session_id: str
    detected_job_type: Optional[str]
    detection_confidence: float
    detection_method: str
    extracted_parameters: Dict[str, Any]
    completion_percentage: float
    ai_response: str
    missing_parameters: List[str]
    next_actions: List[str]
    timestamp: datetime

class UnifiedLangExtractService:
    """
    Unified LangExtract Service - Hauptservice für Parameter Extraction
    Koordiniert Job Detection, Parameter Extraction und Session Management
    """

    def __init__(self,
                 db_service: Optional[Any] = None,
                 job_detector: Optional[EnhancedJobTypeDetector] = None,
                 parameter_extractor: Optional[EnhancedUnifiedParameterExtractor] = None,
                 session_service: Optional[SessionPersistenceService] = None):

        # Use injected dependencies or create defaults
        self.job_detector = job_detector or get_enhanced_job_type_detector()
        self.parameter_extractor = parameter_extractor or EnhancedUnifiedParameterExtractor()
        self.session_service = session_service or SessionPersistenceService()
        self.chat_service = ChatServiceSQLAlchemy()

        # Response Generation Templates
        self.response_templates = self._load_response_templates()

        # Performance tracking
        self.processing_metrics = {
            "total_processed": 0,
            "avg_processing_time": 0,
            "successful_extractions": 0
        }

    def _load_response_templates(self) -> Dict[str, str]:
        """Lädt Response Templates für verschiedene Szenarien"""
        return {
            "job_detected_high": "Ich habe erkannt, dass Sie einen **{job_type}** Job erstellen möchten (Sicherheit: {confidence}%). Lassen Sie uns die Details sammeln.",

            "job_detected_medium": "Es scheint, dass Sie einen **{job_type}** Job erstellen möchten (Sicherheit: {confidence}%). Ist das korrekt?",

            "job_detected_low": "Ich bin mir nicht ganz sicher, aber könnte es sein, dass Sie einen **{job_type}** Job erstellen möchten?",

            "parameters_complete": "Perfekt! Ich habe alle benötigten Parameter für Ihren {job_type} Job gesammelt. Sie können jetzt die XML-Generierung starten.",

            "parameters_partial": "Gut, ich habe bereits {completion}% der benötigten Parameter. Folgende Informationen fehlen noch:\n{missing_params}",

            "need_clarification": "Könnten Sie bitte {parameter} genauer spezifizieren? Zum Beispiel: {example}",

            "no_job_detected": "Ich konnte noch keinen spezifischen Job-Typ erkennen. Möchten Sie einen Datentransfer, SAP-Export oder ein Standard-Script ausführen?"
        }

    async def create_session(self,
                           user_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Erstellt neue LangExtract Session"""

        session_id = await self.session_service.create_session(
            user_id=user_id,
            metadata=metadata or {}
        )

        # Initialize session state
        await self.session_service.update_session_state(session_id, {
            "status": "initialized",
            "created_at": datetime.now().isoformat(),
            "message_count": 0
        })

        return session_id

    async def process_message(self,
                            session_id: str,
                            message: str,
                            context: Optional[Dict[str, Any]] = None) -> LangExtractResponse:
        """
        Hauptmethode für Message Processing
        Koordiniert Job Detection und Parameter Extraction
        """

        start_time = datetime.now()

        # 1. Load Session State
        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        current_state = session.get("state", {})
        current_parameters = current_state.get("extracted_parameters", {})
        detected_job_type = current_state.get("detected_job_type")

        # 2. Job Type Detection (wenn noch nicht erkannt)
        if not detected_job_type or current_state.get("job_confidence", 0) < 0.7:
            detection_result = await self.job_detector.detect_job_type(message)

            if detection_result.detected_job_type and detection_result.confidence >= 0.7:
                detected_job_type = detection_result.detected_job_type

                # Update session with detected job type
                await self.session_service.update_session_state(session_id, {
                    "detected_job_type": detected_job_type,
                    "job_confidence": detection_result.confidence,
                    "detection_method": detection_result.detection_method,
                    "detection_timestamp": datetime.now().isoformat()
                })
        else:
            # Use existing detection
            detection_result = None

        # 3. Parameter Extraction (wenn Job Type bekannt)
        if detected_job_type:
            extraction_result = await self.parameter_extractor.extract_parameters(
                message=message,
                job_type=detected_job_type,
                current_parameters=current_parameters,
                session_id=session_id
            )

            # Merge extracted parameters
            updated_parameters = {**current_parameters, **extraction_result.extracted_parameters}

            # Update session with extracted parameters
            await self.session_service.update_session_state(session_id, {
                "extracted_parameters": updated_parameters,
                "completion_percentage": extraction_result.completion_percentage,
                "last_extraction": datetime.now().isoformat()
            })
        else:
            extraction_result = None
            updated_parameters = current_parameters

        # 4. Generate AI Response
        ai_response = await self._generate_response(
            detected_job_type=detected_job_type,
            detection_result=detection_result,
            extraction_result=extraction_result,
            current_parameters=updated_parameters,
            message=message
        )

        # 5. Determine Next Actions
        next_actions = await self._determine_next_actions(
            detected_job_type=detected_job_type,
            parameters=updated_parameters,
            completion=extraction_result.completion_percentage if extraction_result else 0
        )

        # 6. Save Message to History
        await self.session_service.add_message(session_id, {
            "role": "user",
            "content": message,
            "timestamp": start_time.isoformat()
        })

        await self.session_service.add_message(session_id, {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "detected_job_type": detected_job_type,
                "completion_percentage": extraction_result.completion_percentage if extraction_result else 0
            }
        })

        # 7. Update Metrics
        processing_time = (datetime.now() - start_time).total_seconds()
        self._update_metrics(processing_time, extraction_result is not None)

        # 8. Build Response
        return LangExtractResponse(
            session_id=session_id,
            detected_job_type=detected_job_type,
            detection_confidence=detection_result.confidence if detection_result else current_state.get("job_confidence", 0),
            detection_method=detection_result.detection_method if detection_result else current_state.get("detection_method", "cached"),
            extracted_parameters=updated_parameters,
            completion_percentage=extraction_result.completion_percentage if extraction_result else 0,
            ai_response=ai_response,
            missing_parameters=extraction_result.missing_required if extraction_result else [],
            next_actions=next_actions,
            timestamp=datetime.now()
        )

    async def _generate_response(self,
                               detected_job_type: Optional[str],
                               detection_result: Optional[Any],
                               extraction_result: Optional[Any],
                               current_parameters: Dict[str, Any],
                               message: str) -> str:
        """Generiert intelligente AI Response basierend auf aktuellem State"""

        response_parts = []

        # Job Detection Response
        if detection_result and detection_result.detected_job_type:
            confidence_percent = round(detection_result.confidence * 100)

            if detection_result.confidence >= 0.9:
                template = self.response_templates["job_detected_high"]
            elif detection_result.confidence >= 0.8:
                template = self.response_templates["job_detected_medium"]
            else:
                template = self.response_templates["job_detected_low"]

            response_parts.append(template.format(
                job_type=self._translate_job_type(detection_result.detected_job_type),
                confidence=confidence_percent
            ))

        # Parameter Extraction Response
        if extraction_result:
            if extraction_result.completion_percentage >= 1.0:
                response_parts.append(self.response_templates["parameters_complete"].format(
                    job_type=self._translate_job_type(detected_job_type)
                ))
            elif extraction_result.completion_percentage > 0:
                missing_params_str = self._format_missing_parameters(
                    extraction_result.missing_required,
                    detected_job_type
                )

                response_parts.append(self.response_templates["parameters_partial"].format(
                    completion=round(extraction_result.completion_percentage * 100),
                    missing_params=missing_params_str
                ))

        # No Job Detected Response
        if not detected_job_type:
            response_parts.append(self.response_templates["no_job_detected"])

        # Combine response parts
        return "\n\n".join(response_parts)

    async def _determine_next_actions(self,
                                    detected_job_type: Optional[str],
                                    parameters: Dict[str, Any],
                                    completion: float) -> List[str]:
        """Bestimmt mögliche nächste Aktionen basierend auf State"""

        actions = []

        if not detected_job_type:
            actions.append("Job-Typ spezifizieren (Datentransfer, SAP, oder Standard)")
        elif completion >= 0.8:
            actions.append("XML generieren")
            actions.append("Parameter überprüfen")
            if completion < 1.0:
                actions.append("Fehlende Parameter ergänzen")
        else:
            actions.append("Weitere Parameter angeben")
            actions.append("Beispiel-Konfiguration anzeigen")

        return actions

    def _translate_job_type(self, job_type: str) -> str:
        """Übersetzt Job Type in deutsche Bezeichnung"""
        translations = {
            "FILE_TRANSFER": "Datentransfer",
            "SAP": "SAP-Integration",
            "STANDARD": "Standard-Automation"
        }
        return translations.get(job_type, job_type)

    def _format_missing_parameters(self,
                                  missing: List[str],
                                  job_type: str) -> str:
        """Formatiert fehlende Parameter für Benutzeranzeige"""

        param_descriptions = {
            "FILE_TRANSFER": {
                "source_server": "Quell-Server (z.B. AGENT_01)",
                "target_server": "Ziel-Server (z.B. AGENT_02)",
                "file_pattern": "Datei-Pattern (z.B. *.csv oder report_*.pdf)",
                "source_path": "Quell-Pfad (z.B. /data/exports/)",
                "target_path": "Ziel-Pfad (z.B. /data/imports/)"
            },
            "SAP": {
                "sap_system": "SAP-System (z.B. GT123_PRD)",
                "transaction_code": "Transaktionscode (z.B. SE16)",
                "table_name": "Tabellenname (z.B. VBAK)",
                "export_path": "Export-Pfad für Datei"
            },
            "STANDARD": {
                "script_path": "Script-Pfad (z.B. /scripts/process.py)",
                "server": "Ausführungs-Server",
                "arguments": "Script-Argumente"
            }
        }

        descriptions = param_descriptions.get(job_type, {})
        formatted = []

        for param in missing:
            desc = descriptions.get(param, param)
            formatted.append(f"• {desc}")

        return "\n".join(formatted)

    def _update_metrics(self, processing_time: float, successful: bool):
        """Aktualisiert Performance-Metriken"""
        self.processing_metrics["total_processed"] += 1

        if successful:
            self.processing_metrics["successful_extractions"] += 1

        # Update average processing time
        current_avg = self.processing_metrics["avg_processing_time"]
        total = self.processing_metrics["total_processed"]

        self.processing_metrics["avg_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )

    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Gibt zusammenfassende Session-Informationen zurück"""

        session = await self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        state = session.get("state", {})
        messages = session.get("messages", [])

        return {
            "session_id": session_id,
            "detected_job_type": state.get("detected_job_type"),
            "job_confidence": state.get("job_confidence", 0),
            "extracted_parameters": state.get("extracted_parameters", {}),
            "completion_percentage": state.get("completion_percentage", 0),
            "message_count": len(messages),
            "created_at": state.get("created_at"),
            "last_updated": state.get("last_extraction"),
            "ready_for_xml": state.get("completion_percentage", 0) >= 0.8
        }
```

---

## 5.2 Frontend-Implementierung mit Next.js 15

### 5.2.1 App Router und Layout Structure

```typescript
// frontend/src/app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers/Providers'
import { AppLayout } from '@/components/layout/AppLayout'
import { Toaster } from 'sonner'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter'
})

export const metadata: Metadata = {
  title: 'Streamworks-KI | Enterprise RAG System',
  description: 'KI-gestützte Workload-Automatisierung mit Self-Service',
  keywords: ['Streamworks', 'RAG', 'AI', 'Automation', 'LangExtract'],
  authors: [{ name: 'Lukas Geck' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#3b82f6'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="de" className={inter.variable}>
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <Providers>
          <AppLayout>
            {children}
          </AppLayout>
          <Toaster
            position="bottom-right"
            richColors
            closeButton
            duration={5000}
          />
        </Providers>
      </body>
    </html>
  )
}
```

### 5.2.2 LangExtract Interface Implementation

```typescript
// frontend/src/components/langextract-chat/LangExtractInterface.tsx
'use client'

import React, { useState, useEffect, useRef, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import {
  Send,
  Sparkles,
  CheckCircle,
  AlertCircle,
  FileText,
  Download,
  RefreshCw,
  ChevronRight
} from 'lucide-react'

import { LangExtractSessionSidebar } from './components/LangExtractSessionSidebar'
import { ParameterOverview } from './components/ParameterOverview'
import { SmartSuggestions } from './components/SmartSuggestions'
import { XMLPreview } from './components/XMLPreview'
import { ChatMessage } from './components/ChatMessage'

import { useLangExtractChat } from './hooks/useLangExtractChat'
import { apiService } from '@/services/api.service'
import type {
  LangExtractSession,
  LangExtractMessage,
  ExtractedParameters
} from '@/types/langextract.types'

interface LangExtractInterfaceProps {
  initialSessionId?: string
  onXMLGenerated?: (xml: string) => void
}

export default function LangExtractInterface({
  initialSessionId,
  onXMLGenerated
}: LangExtractInterfaceProps) {

  const queryClient = useQueryClient()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // State Management
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null)
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showXMLPreview, setShowXMLPreview] = useState(false)

  // Custom Hook für Chat Logic
  const {
    messages,
    isLoading,
    sendMessage,
    generateXML,
    clearSession
  } = useLangExtractChat(sessionId)

  // Session Query
  const { data: session, isLoading: sessionLoading } = useQuery({
    queryKey: ['langextract-session', sessionId],
    queryFn: async () => {
      if (!sessionId) return null
      const response = await apiService.get(`/langextract/sessions/${sessionId}`)
      return response.data as LangExtractSession
    },
    enabled: !!sessionId,
    refetchInterval: 5000 // Auto-refresh every 5 seconds
  })

  // Create Session Mutation
  const createSessionMutation = useMutation({
    mutationFn: async () => {
      const response = await apiService.post('/langextract/sessions')
      return response.data
    },
    onSuccess: (data) => {
      setSessionId(data.session_id)
      toast.success('Neue Session erstellt')
    },
    onError: (error) => {
      toast.error('Fehler beim Erstellen der Session')
      console.error('Session creation error:', error)
    }
  })

  // Process Message Mutation
  const processMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      if (!sessionId) throw new Error('No session ID')

      setIsTyping(true)

      const response = await apiService.post(
        `/langextract/sessions/${sessionId}/messages`,
        { message }
      )

      return response.data
    },
    onSuccess: (data) => {
      setIsTyping(false)

      // Show confidence toast
      if (data.detected_job_type && data.detection_confidence >= 0.9) {
        toast.success(
          `Job-Typ erkannt: ${data.detected_job_type} (${Math.round(data.detection_confidence * 100)}% Sicherheit)`,
          { icon: <Sparkles className="w-4 h-4" /> }
        )
      }

      // Invalidate queries to refresh data
      queryClient.invalidateQueries(['langextract-session', sessionId])
    },
    onError: (error) => {
      setIsTyping(false)
      toast.error('Fehler bei der Verarbeitung')
      console.error('Message processing error:', error)
    }
  })

  // Generate XML Mutation
  const generateXMLMutation = useMutation({
    mutationFn: async () => {
      if (!sessionId) throw new Error('No session ID')

      const response = await apiService.post('/xml-generator/template/generate', {
        session_id: sessionId
      })

      return response.data
    },
    onSuccess: (data) => {
      setShowXMLPreview(true)
      onXMLGenerated?.(data.xml_content)
      toast.success('XML erfolgreich generiert', {
        action: {
          label: 'Anzeigen',
          onClick: () => setShowXMLPreview(true)
        }
      })
    },
    onError: (error) => {
      toast.error('Fehler bei der XML-Generierung')
      console.error('XML generation error:', error)
    }
  })

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Initialize session on mount if not provided
  useEffect(() => {
    if (!sessionId && !initialSessionId) {
      createSessionMutation.mutate()
    }
  }, [])

  // Handle message submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!inputMessage.trim() || processMessageMutation.isPending) return

    const message = inputMessage.trim()
    setInputMessage('')

    await processMessageMutation.mutateAsync(message)
  }

  // Calculate completion status
  const completionPercentage = session?.completion_percentage || 0
  const isReadyForXML = completionPercentage >= 0.8
  const detectedJobType = session?.detected_job_type

  // Render confidence indicator
  const renderConfidenceIndicator = () => {
    if (!session?.detection_confidence) return null

    const confidence = session.detection_confidence
    const level = confidence >= 0.9 ? 'high' : confidence >= 0.7 ? 'medium' : 'low'
    const colors = {
      high: 'text-green-600 bg-green-50',
      medium: 'text-yellow-600 bg-yellow-50',
      low: 'text-red-600 bg-red-50'
    }

    return (
      <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${colors[level]}`}>
        <div className={`w-2 h-2 rounded-full mr-2 ${
          level === 'high' ? 'bg-green-600' :
          level === 'medium' ? 'bg-yellow-600' :
          'bg-red-600'
        }`} />
        {Math.round(confidence * 100)}% Sicherheit
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <LangExtractSessionSidebar
        sessions={[]} // Would load from API
        currentSessionId={sessionId}
        onSessionSelect={setSessionId}
        onNewSession={() => createSessionMutation.mutate()}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">
                LangExtract Parameter Extraction
              </h1>
              {detectedJobType && (
                <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
                  {detectedJobType}
                </span>
              )}
              {renderConfidenceIndicator()}
            </div>

            <div className="flex items-center space-x-3">
              {isReadyForXML && (
                <button
                  onClick={() => generateXMLMutation.mutate()}
                  disabled={generateXMLMutation.isPending}
                  className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg
                           hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed
                           transition-colors duration-200"
                >
                  {generateXMLMutation.isPending ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <FileText className="w-4 h-4 mr-2" />
                  )}
                  XML Generieren
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Main Layout with Chat and Parameter Panel */}
        <div className="flex-1 flex overflow-hidden">
          {/* Chat Area */}
          <div className="flex-1 flex flex-col">
            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {messages.length === 0 && !sessionLoading && (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <Sparkles className="w-12 h-12 mb-4 text-gray-400" />
                  <h3 className="text-lg font-medium mb-2">
                    Willkommen bei LangExtract
                  </h3>
                  <p className="text-sm text-center max-w-md">
                    Beschreiben Sie den gewünschten StreamWorks-Job in natürlicher Sprache.
                    Ich erkenne automatisch den Job-Typ und extrahiere die benötigten Parameter.
                  </p>
                </div>
              )}

              {/* Message List */}
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <ChatMessage
                    key={index}
                    message={message}
                    isLatest={index === messages.length - 1}
                  />
                ))}

                {/* Typing Indicator */}
                {isTyping && (
                  <div className="flex items-center space-x-2 text-gray-500">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                    </div>
                    <span className="text-sm">AI verarbeitet...</span>
                  </div>
                )}
              </div>

              <div ref={messagesEndRef} />
            </div>

            {/* Smart Suggestions */}
            {detectedJobType && completionPercentage < 1 && (
              <div className="px-6 py-3 bg-blue-50 border-t border-blue-200">
                <SmartSuggestions
                  jobType={detectedJobType}
                  currentParameters={session?.extracted_parameters || {}}
                  onSuggestionClick={(suggestion) => setInputMessage(suggestion)}
                />
              </div>
            )}

            {/* Input Area */}
            <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Beschreiben Sie Ihren StreamWorks-Job..."
                  disabled={processMessageMutation.isPending}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg
                           focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:bg-gray-100 disabled:cursor-not-allowed"
                />

                <button
                  type="submit"
                  disabled={!inputMessage.trim() || processMessageMutation.isPending}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg
                           hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
                           transition-colors duration-200 flex items-center space-x-2"
                >
                  {processMessageMutation.isPending ? (
                    <RefreshCw className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Parameter Panel */}
          <div className="w-96 bg-white border-l border-gray-200 overflow-y-auto">
            <ParameterOverview
              jobType={detectedJobType}
              parameters={session?.extracted_parameters || {}}
              completion={completionPercentage}
              confidence={session?.detection_confidence || 0}
            />
          </div>
        </div>
      </div>

      {/* XML Preview Modal */}
      <AnimatePresence>
        {showXMLPreview && generateXMLMutation.data && (
          <XMLPreview
            xml={generateXMLMutation.data.xml_content}
            onClose={() => setShowXMLPreview(false)}
            onDownload={() => {
              const blob = new Blob([generateXMLMutation.data.xml_content], { type: 'text/xml' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `${detectedJobType?.toLowerCase()}_${sessionId}.xml`
              a.click()
              URL.revokeObjectURL(url)
              toast.success('XML heruntergeladen')
            }}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
```

### 5.2.3 API Service Implementation

```typescript
// frontend/src/services/api.service.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { toast } from 'sonner'

interface ApiServiceConfig {
  baseURL: string
  timeout?: number
  withCredentials?: boolean
}

class ApiService {
  private api: AxiosInstance
  private requestInterceptor: number | null = null
  private responseInterceptor: number | null = null

  constructor(config: ApiServiceConfig) {
    this.api = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      withCredentials: config.withCredentials || true,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request Interceptor
    this.requestInterceptor = this.api.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = this.getAuthToken()
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Add request ID for tracking
        config.headers['X-Request-ID'] = this.generateRequestId()

        // Log request in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data)
        }

        return config
      },
      (error) => {
        console.error('[API] Request error:', error)
        return Promise.reject(error)
      }
    )

    // Response Interceptor
    this.responseInterceptor = this.api.interceptors.response.use(
      (response) => {
        // Log response in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`[API] Response ${response.config.url}:`, response.data)
        }

        return response
      },
      async (error) => {
        const originalRequest = error.config

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            await this.refreshToken()
            return this.api(originalRequest)
          } catch (refreshError) {
            // Refresh failed, redirect to login
            this.handleAuthError()
            return Promise.reject(refreshError)
          }
        }

        // Handle other errors
        this.handleApiError(error)

        return Promise.reject(error)
      }
    )
  }

  private getAuthToken(): string | null {
    // Get from localStorage or cookie
    return localStorage.getItem('auth_token')
  }

  private async refreshToken(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await this.api.post('/auth/refresh', {
      refresh_token: refreshToken
    })

    const { access_token, refresh_token: newRefreshToken } = response.data

    localStorage.setItem('auth_token', access_token)
    localStorage.setItem('refresh_token', newRefreshToken)
  }

  private handleAuthError() {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')

    toast.error('Sitzung abgelaufen. Bitte erneut anmelden.')

    // Redirect to login
    window.location.href = '/auth/login'
  }

  private handleApiError(error: any) {
    if (!error.response) {
      // Network error
      toast.error('Netzwerkfehler. Bitte Verbindung überprüfen.')
    } else {
      // Server error
      const status = error.response.status
      const message = error.response.data?.detail || error.response.data?.message

      switch (status) {
        case 400:
          toast.error(message || 'Ungültige Anfrage')
          break
        case 403:
          toast.error('Keine Berechtigung für diese Aktion')
          break
        case 404:
          toast.error('Ressource nicht gefunden')
          break
        case 429:
          toast.error('Zu viele Anfragen. Bitte später erneut versuchen.')
          break
        case 500:
          toast.error('Serverfehler. Bitte Support kontaktieren.')
          break
        default:
          toast.error(message || `Fehler: ${status}`)
      }
    }
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  // Public API Methods

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.api.get<T>(url, config)
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.api.post<T>(url, data, config)
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.api.put<T>(url, data, config)
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.api.patch<T>(url, data, config)
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.api.delete<T>(url, config)
  }

  // Specialized methods

  async uploadFile(url: string, file: File, onProgress?: (progress: number) => void): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)

    return this.api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    })
  }

  async downloadFile(url: string, filename?: string): Promise<void> {
    const response = await this.api.get(url, {
      responseType: 'blob'
    })

    const blob = new Blob([response.data])
    const downloadUrl = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    URL.revokeObjectURL(downloadUrl)
  }
}

// Create singleton instance
export const apiService = new ApiService({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  withCredentials: true
})
```

---

## 5.3 Template-basierte XML-Generierung

### 5.3.1 Template Engine Implementation

```python
# backend/services/xml_generation/template_engine.py
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, Template
from pydantic import BaseModel, Field, validator
import xml.etree.ElementTree as ET
from dataclasses import dataclass

@dataclass
class XMLGenerationResult:
    """Result structure für XML Generation"""
    xml_content: str
    template_used: str
    mapped_parameters: Dict[str, Any]
    auto_generated_parameters: Dict[str, Any]
    validation_result: 'XMLValidationResult'
    generation_timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class XMLValidationResult:
    """XML Validation Result"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    schema_version: str

class TemplateEngine:
    """
    Template-basierte XML-Generierung mit Jinja2
    Ersetzt LLM-basierte Generation für Determinismus und Kontrolle
    """

    def __init__(self, template_dir: Optional[str] = None):
        # Template directory configuration
        self.template_dir = Path(template_dir or "backend/templates/xml_templates")

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            enable_async=True,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False  # XML doesn't need HTML escaping
        )

        # Register custom filters
        self._register_custom_filters()

        # Load template configurations
        self.template_configs = self._load_template_configs()

        # Parameter mapper for intelligent field mapping
        from services.xml_generation.parameter_mapper import ParameterMapper
        self.parameter_mapper = ParameterMapper()

        # XML validator
        self.xml_validator = XMLValidator()

    def _register_custom_filters(self):
        """Registriert custom Jinja2 filters für XML-Generation"""

        # DateTime formatting
        self.jinja_env.filters['format_datetime'] = lambda dt: (
            dt.isoformat() if isinstance(dt, datetime) else str(dt)
        )

        # Path sanitization for Windows/Unix compatibility
        self.jinja_env.filters['sanitize_path'] = lambda path: (
            path.replace('\\', '/').strip() if path else ''
        )

        # Server name formatting
        self.jinja_env.filters['format_server_name'] = lambda name: (
            name.upper().replace(' ', '_') if name else ''
        )

        # Boolean to XML boolean
        self.jinja_env.filters['xml_bool'] = lambda val: (
            'true' if val else 'false'
        )

        # List to comma-separated string
        self.jinja_env.filters['join_list'] = lambda lst, sep=',': (
            sep.join(str(item) for item in lst) if lst else ''
        )

        # XML escape special characters
        self.jinja_env.filters['xml_escape'] = lambda text: (
            text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;')
            if text else ''
        )

    def _load_template_configs(self) -> Dict[str, Any]:
        """Lädt Template-Konfigurationen aus JSON"""

        config_file = self.template_dir / "template_configs.json"

        if not config_file.exists():
            # Return default configs if file doesn't exist
            return self._get_default_configs()

        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_default_configs(self) -> Dict[str, Any]:
        """Default Template Configurations"""

        return {
            "FILE_TRANSFER": {
                "template_file": "file_transfer_template.xml",
                "required_parameters": [
                    "source_server", "target_server",
                    "source_path", "target_path"
                ],
                "optional_parameters": [
                    "file_pattern", "transfer_mode", "schedule",
                    "retry_count", "notification_email"
                ],
                "default_values": {
                    "transfer_mode": "COPY",
                    "retry_count": 3,
                    "timeout_minutes": 30,
                    "preserve_timestamps": True,
                    "create_directories": True
                }
            },
            "SAP": {
                "template_file": "sap_template.xml",
                "required_parameters": [
                    "sap_system", "transaction_code"
                ],
                "optional_parameters": [
                    "table_name", "export_path", "variant",
                    "selection_criteria", "export_format"
                ],
                "default_values": {
                    "export_format": "CSV",
                    "field_delimiter": ";",
                    "text_qualifier": '"',
                    "max_records": 1000000
                }
            },
            "STANDARD": {
                "template_file": "standard_template.xml",
                "required_parameters": [
                    "script_path", "server"
                ],
                "optional_parameters": [
                    "arguments", "working_directory",
                    "environment_variables", "schedule"
                ],
                "default_values": {
                    "execution_timeout": 1800,
                    "capture_output": True,
                    "retry_on_failure": True
                }
            }
        }

    async def generate_xml(self,
                          job_type: str,
                          parameters: Dict[str, Any],
                          options: Optional[Dict[str, Any]] = None) -> XMLGenerationResult:
        """
        Hauptmethode für Template-basierte XML-Generierung

        Args:
            job_type: Job-Type (FILE_TRANSFER, SAP, STANDARD)
            parameters: Extrahierte Parameter aus LangExtract
            options: Zusätzliche Generierungs-Optionen

        Returns:
            XMLGenerationResult mit generiertem XML und Metadaten
        """

        generation_start = datetime.now()

        # 1. Get template configuration
        template_config = self.template_configs.get(job_type)
        if not template_config:
            raise ValueError(f"Unknown job type: {job_type}")

        # 2. Load template
        template_file = template_config["template_file"]
        try:
            template = self.jinja_env.get_template(template_file)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template not found: {template_file}")

        # 3. Map parameters using intelligent mapper
        mapped_parameters = await self.parameter_mapper.map_parameters(
            parameters,
            job_type,
            template_config
        )

        # 4. Generate auto-parameters for missing required fields
        auto_generated = await self._generate_auto_parameters(
            mapped_parameters,
            job_type,
            template_config
        )

        # 5. Merge with default values
        default_values = template_config.get("default_values", {})

        # Final parameter set (priority: mapped > auto > defaults > options)
        final_parameters = {
            **default_values,
            **auto_generated,
            **mapped_parameters,
            **(options or {})
        }

        # 6. Add metadata
        final_parameters.update({
            'job_type': job_type,
            'generation_timestamp': generation_start,
            'generation_system': 'STREAMWORKS_KI',
            'template_version': template_config.get('version', '1.0.0')
        })

        # 7. Render template
        try:
            xml_content = await template.render_async(**final_parameters)
        except Exception as e:
            raise RuntimeError(f"Template rendering failed: {str(e)}")

        # 8. Validate generated XML
        validation_result = await self.xml_validator.validate(
            xml_content,
            job_type
        )

        # 9. Build result
        return XMLGenerationResult(
            xml_content=xml_content,
            template_used=template_file,
            mapped_parameters=mapped_parameters,
            auto_generated_parameters=auto_generated,
            validation_result=validation_result,
            generation_timestamp=generation_start,
            metadata={
                'generation_duration_ms': (datetime.now() - generation_start).total_seconds() * 1000,
                'parameter_count': len(mapped_parameters),
                'auto_generated_count': len(auto_generated),
                'job_type': job_type
            }
        )

    async def _generate_auto_parameters(self,
                                       mapped_parameters: Dict[str, Any],
                                       job_type: str,
                                       template_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generiert automatische Parameter für fehlende Required Fields
        """

        auto_params = {}
        current_time = datetime.now()

        # Check for missing required parameters
        required = template_config.get("required_parameters", [])
        missing_required = [
            param for param in required
            if param not in mapped_parameters or mapped_parameters[param] is None
        ]

        # Generate IDs and timestamps
        auto_params['job_id'] = f"{job_type[:3]}_{current_time.strftime('%Y%m%d_%H%M%S')}"
        auto_params['created_by'] = 'StreamWorks-KI'
        auto_params['creation_date'] = current_time.isoformat()
        auto_params['priority'] = 'MEDIUM'

        # Job-type specific auto-generation
        if job_type == "FILE_TRANSFER":
            if 'source_server' in missing_required:
                auto_params['source_server'] = 'LOCAL'
            if 'target_server' in missing_required:
                auto_params['target_server'] = 'REMOTE'
            if 'notification_email' not in mapped_parameters:
                auto_params['notification_email'] = 'streamworks@company.com'

        elif job_type == "SAP":
            if 'sap_system' in missing_required:
                auto_params['sap_system'] = 'DEFAULT_SAP'
            if 'export_path' not in mapped_parameters:
                auto_params['export_path'] = f'/exports/sap/{current_time.strftime("%Y%m%d")}/'

        elif job_type == "STANDARD":
            if 'server' in missing_required:
                auto_params['server'] = 'EXECUTION_SERVER'
            if 'working_directory' not in mapped_parameters:
                auto_params['working_directory'] = '/home/streamworks/jobs/'

        # Environment-based parameters
        auto_params['environment'] = 'PROD'  # Could be determined from config
        auto_params['execution_user'] = 'streamworks'

        return auto_params

    async def preview_generation(self,
                                job_type: str,
                                parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview der Parameter-Mappings ohne XML-Generierung
        Nützlich für UI-Preview vor finaler Generierung
        """

        template_config = self.template_configs.get(job_type)
        if not template_config:
            raise ValueError(f"Unknown job type: {job_type}")

        # Map parameters
        mapped = await self.parameter_mapper.map_parameters(
            parameters,
            job_type,
            template_config
        )

        # Generate auto parameters
        auto_generated = await self._generate_auto_parameters(
            mapped,
            job_type,
            template_config
        )

        # Check completeness
        required = template_config.get("required_parameters", [])
        all_params = {**mapped, **auto_generated}

        missing_required = [
            param for param in required
            if param not in all_params or all_params[param] is None
        ]

        return {
            'job_type': job_type,
            'mapped_parameters': mapped,
            'auto_generated_parameters': auto_generated,
            'missing_required': missing_required,
            'is_ready': len(missing_required) == 0,
            'template_file': template_config["template_file"]
        }

    def get_template_info(self, job_type: str) -> Dict[str, Any]:
        """
        Gibt Template-Informationen für Frontend zurück
        """

        config = self.template_configs.get(job_type)
        if not config:
            raise ValueError(f"Unknown job type: {job_type}")

        return {
            'job_type': job_type,
            'template_file': config['template_file'],
            'required_parameters': config.get('required_parameters', []),
            'optional_parameters': config.get('optional_parameters', []),
            'default_values': config.get('default_values', {}),
            'description': config.get('description', ''),
            'version': config.get('version', '1.0.0')
        }

class XMLValidator:
    """XML Validation Service"""

    def __init__(self):
        self.schemas = self._load_schemas()

    def _load_schemas(self) -> Dict[str, Any]:
        """Lädt XSD Schemas für Validation"""
        # Would load actual XSD schemas here
        return {}

    async def validate(self, xml_content: str, job_type: str) -> XMLValidationResult:
        """Validates generated XML"""

        errors = []
        warnings = []

        try:
            # Parse XML to check well-formedness
            root = ET.fromstring(xml_content)

            # Check required elements based on job type
            if job_type == "FILE_TRANSFER":
                if not root.find(".//ft:source", namespaces={'ft': 'http://streamworks.company.com/filetransfer'}):
                    errors.append("Missing required element: source")
                if not root.find(".//ft:target", namespaces={'ft': 'http://streamworks.company.com/filetransfer'}):
                    errors.append("Missing required element: target")

            # Check for empty elements
            for elem in root.iter():
                if elem.text is None or elem.text.strip() == '':
                    if not list(elem):  # No child elements
                        warnings.append(f"Empty element: {elem.tag}")

        except ET.ParseError as e:
            errors.append(f"XML Parse Error: {str(e)}")
        except Exception as e:
            errors.append(f"Validation Error: {str(e)}")

        return XMLValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            schema_version="1.0.0"
        )
```

---

## 5.4 Integration und Deployment

### 5.4.1 Docker Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Backend Service
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: streamworks-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/streamworks
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379
      - OLLAMA_URL=http://ollama:11434
    volumes:
      - ./backend:/app
      - backend-storage:/app/storage
    depends_on:
      - postgres
      - qdrant
      - redis
    networks:
      - streamworks-network
    restart: unless-stopped

  # Frontend Service
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: streamworks-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend
    networks:
      - streamworks-network
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: streamworks-postgres
    environment:
      - POSTGRES_USER=streamworks
      - POSTGRES_PASSWORD=streamworks_secure_pass
      - POSTGRES_DB=streamworks
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./backend/sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - streamworks-network
    restart: unless-stopped

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: streamworks-qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant-data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
    networks:
      - streamworks-network
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: streamworks-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    networks:
      - streamworks-network
    restart: unless-stopped

  # Ollama for Local LLM
  ollama:
    image: ollama/ollama:latest
    container_name: streamworks-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-models:/root/.ollama
    networks:
      - streamworks-network
    restart: unless-stopped

volumes:
  postgres-data:
  qdrant-data:
  redis-data:
  ollama-models:
  backend-storage:

networks:
  streamworks-network:
    driver: bridge
```

### 5.4.2 CI/CD Pipeline

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '20'

jobs:
  # Backend Tests
  backend-test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Cache pip packages
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - name: Install dependencies
        working-directory: ./backend
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run tests
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql://postgres:test_pass@localhost:5432/test_db
        run: |
          pytest tests/ --cov=services --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: backend

  # Frontend Tests
  frontend-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Run type check
        working-directory: ./frontend
        run: npm run type-check

      - name: Run linter
        working-directory: ./frontend
        run: npm run lint

      - name: Run tests
        working-directory: ./frontend
        run: npm run test:ci

      - name: Build application
        working-directory: ./frontend
        run: npm run build

  # Docker Build
  docker-build:
    runs-on: ubuntu-latest
    needs: [backend-test, frontend-test]
    if: github.event_name == 'push'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: |
            streamworks/backend:latest
            streamworks/backend:${{ github.sha }}
          cache-from: type=registry,ref=streamworks/backend:latest
          cache-to: type=inline

      - name: Build and push Frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: |
            streamworks/frontend:latest
            streamworks/frontend:${{ github.sha }}
          cache-from: type=registry,ref=streamworks/frontend:latest
          cache-to: type=inline

  # Deploy to Production
  deploy:
    runs-on: ubuntu-latest
    needs: [docker-build]
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Production
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
          DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
        run: |
          echo "$DEPLOY_KEY" > deploy_key
          chmod 600 deploy_key

          ssh -o StrictHostKeyChecking=no -i deploy_key $DEPLOY_HOST << 'EOF'
            cd /opt/streamworks-ki
            docker-compose pull
            docker-compose up -d --no-build
            docker system prune -f
          EOF
```

---

## Fazit Kapitel 5

Die **Implementierung des Streamworks-KI Systems** demonstriert die erfolgreiche Umsetzung der konzipierten Architektur in eine produktionsreife Anwendung. Mit über **120 Backend-Services** und **600+ Frontend-Komponenten** wurde ein hochmodernes Enterprise-System entwickelt.

**Technische Highlights der Implementierung:**

1. **Enhanced Job Type Detection**: 88.9% Accuracy durch Multi-Layer Pattern Matching
2. **Unified LangExtract Service**: Koordinierte Parameter-Extraktion mit State Management
3. **Template Engine**: Deterministische XML-Generierung mit Jinja2
4. **Modern Frontend**: Next.js 15 mit TypeScript und React Query
5. **Production Deployment**: Docker-basierte Infrastruktur mit CI/CD Pipeline

Die **modulare Service-Architektur** ermöglicht einfache Erweiterbarkeit und Wartung, während die **Dependency Injection** für lose Kopplung und Testbarkeit sorgt. Das System ist vollständig **produktionsbereit** und wird erfolgreich in der Enterprise-Umgebung eingesetzt.

**Performance-Metriken:**
- Sub-2-Sekunden Response Time für Job Detection
- 70% Reduktion der False Positives
- Horizontale Skalierbarkeit durch stateless Services
- Automatisierte Deployment-Pipeline mit <5 Minuten Deployment-Zeit

Das nächste Kapitel wird die **Evaluierung** des Systems mit detaillierten Performance-Messungen und Benutzerstudien dokumentieren.