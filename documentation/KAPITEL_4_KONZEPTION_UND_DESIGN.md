# Kapitel 4: Konzeption und Design

> **Entwicklung einer KI-gestützten Self-Service-Architektur für Streamworks-Automatisierung**

---

## 4.1 Zielarchitektur des Self-Service-Systems

### 4.1.1 Architektonische Prinzipien

Das Streamworks-KI System basiert auf einer **Clean Architecture** mit strikter Trennung zwischen fachlichen Domänen und technischen Implementierungsdetails. Die Architektur folgt folgenden Kernprinzipien:

**Domain-Driven Design (DDD)**
- **Bounded Contexts** für LangExtract, XML-Generierung, RAG-Support und Authentication
- **Ubiquitous Language** mit StreamWorks-spezifischer Terminologie
- **Aggregates** für Session-Management und Parameter-Extraktion

**Mikroservice-orientierte Modularität**
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (Next.js 15)              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │  LangExtract UI │ │   Chat Interface│ │  XML Generator  ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                                 │
                          ┌─────────────┐
                          │   API Gateway │
                          │   (FastAPI)   │
                          └─────────────┘
                                 │
┌─────────────────────────────────────────────────────────────┐
│                  Service Layer (120+ Komponenten)           │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              AI Services Layer                          ││
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ││
│  │  │  LangExtract  │ │ Job Detection │ │ Parameter AI  │ ││
│  │  │   Service     │ │  (88.9% Acc.) │ │   Extractor   │ ││
│  │  └───────────────┘ └───────────────┘ └───────────────┘ ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │           Knowledge & Generation Layer                  ││
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ││
│  │  │ Knowledge     │ │ XML Template  │ │ RAG Support   │ ││
│  │  │ Graph Service │ │   Engine      │ │   System      │ ││
│  │  └───────────────┘ └───────────────┘ └───────────────┘ ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │  PostgreSQL  │ │    Qdrant     │ │    File Storage      │ │
│  │  (Sessions)  │ │   (Vectors)   │ │   (Documents)        │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Dependency Injection Container**
Das System implementiert ein zentrales DI-Container-Pattern für Lose Kopplung und einfache Testbarkeit:

```python
# services/di_container.py
class DIContainer:
    def __init__(self):
        self._services = {}
        self._singletons = {}

    def register_singleton(self, interface: Type, implementation: Type):
        """Registriert Service als Singleton"""
        self._services[interface] = (implementation, 'singleton')

    def register_transient(self, interface: Type, implementation: Type):
        """Registriert Service als Transient"""
        self._services[interface] = (implementation, 'transient')

# Konkrete Service-Registrierung
container = DIContainer()
container.register_singleton(IJobTypeDetector, EnhancedJobTypeDetector)
container.register_singleton(IParameterExtractor, EnhancedUnifiedParameterExtractor)
container.register_transient(ILangExtractService, UnifiedLangExtractService)
```

### 4.1.2 Multi-Tenant Self-Service Architektur

**Session-basierte Isolierung**
Jeder Benutzer arbeitet in isolierten Sessions mit eigenständiger Parameter-Persistierung:

```python
@dataclass
class LangExtractSession:
    """Session-Modell für Self-Service Isolation"""
    session_id: str
    user_id: Optional[str]
    detected_job_type: Optional[str]
    detection_confidence: float
    extracted_parameters: Dict[str, Any]
    completion_percentage: float
    created_at: datetime
    updated_at: datetime

    def is_complete(self) -> bool:
        """Prüft Session-Vollständigkeit für XML-Generierung"""
        return self.completion_percentage >= 0.80
```

**Horizontale Skalierbarkeit**
- **Stateless Services**: Alle Services sind zustandslos und skalierbar
- **Async Database Patterns**: SQLAlchemy 2.0 mit async/await für hohe Concurrency
- **Vector Database Sharding**: Qdrant-Collections für verschiedene Domänen
- **Caching Strategy**: Redis-kompatibles Caching für Wiederholungsanfragen

### 4.1.3 Event-Driven Communication

**Domain Events für Service-Integration**

```python
@dataclass
class JobTypeDetectedEvent:
    """Event bei erfolgreicher Job-Type-Erkennung"""
    session_id: str
    detected_job_type: str
    confidence: float
    detection_method: str
    timestamp: datetime

@dataclass
class ParameterExtractionCompletedEvent:
    """Event bei vollständiger Parameter-Extraktion"""
    session_id: str
    job_type: str
    extracted_parameters: Dict[str, Any]
    completion_percentage: float
    timestamp: datetime

class EventBus:
    """Zentraler Event Bus für Service-Kommunikation"""
    def __init__(self):
        self._handlers: Dict[Type, List[Callable]] = {}

    def subscribe(self, event_type: Type, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: Any):
        """Publiziert Event an alle registrierten Handler"""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                await handler(event)
```

---

## 4.2 User Interface und User Experience (UI/UX)

### 4.2.1 Design System und Komponenten-Architektur

**Atomic Design Methodology**
Das Frontend folgt der Atomic Design-Methodik mit strikter Komponentenhierarchie:

```
Atoms (Grundbausteine)
├── Input Fields (German-optimized)
├── Buttons (Action-oriented)
├── Status Indicators (Confidence Display)
└── Typography (StreamWorks Corporate)

Molecules (Komponentengruppen)
├── Parameter Input Groups
├── Confidence Score Display
├── Job Type Selector
└── Progress Indicators

Organisms (Komplexe UI-Bereiche)
├── LangExtract Chat Interface
├── Parameter Overview Panel
├── XML Generation Workspace
└── RAG Support Sidebar

Templates (Seiten-Layouts)
├── LangExtract Page Template
├── XML Generation Template
├── Chat Interface Template
└── Dashboard Template

Pages (Konkrete Seiten)
├── /langextract (Hauptfeature)
├── /xml (XML-Generierung)
├── /chat (RAG-Support)
└── /dashboard (Admin)
```

**Responsive Design System**
```typescript
// Design Tokens für konsistente UI
const designTokens = {
  colors: {
    primary: {
      50: '#eff6ff',   // Sehr hell (Backgrounds)
      500: '#3b82f6',  // Standard (Buttons)
      700: '#1d4ed8',  // Dunkel (Focus States)
      900: '#1e3a8a'   // Sehr dunkel (Text)
    },
    confidence: {
      high: '#10b981',    // Grün für ≥90% Confidence
      medium: '#f59e0b',  // Orange für 70-89%
      low: '#ef4444'      // Rot für <70%
    }
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '3rem'
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px'
  }
}
```

**Component Design Pattern**
```typescript
// LangExtract Interface - Hauptkomponente
interface LangExtractInterfaceProps {
  sessionId?: string
  onJobTypeDetected?: (jobType: string, confidence: number) => void
  onParametersExtracted?: (parameters: ExtractedParameters) => void
}

export default function LangExtractInterface({
  sessionId,
  onJobTypeDetected,
  onParametersExtracted
}: LangExtractInterfaceProps) {
  const { data: session, isLoading } = useQuery({
    queryKey: ['langextract-session', sessionId],
    queryFn: () => fetchLangExtractSession(sessionId),
    enabled: !!sessionId
  })

  const processMessage = useMutation({
    mutationFn: processLangExtractMessage,
    onSuccess: (data) => {
      if (data.detection_confidence >= 0.90) {
        onJobTypeDetected?.(data.detected_job_type, data.detection_confidence)
      }
      if (data.completion_percentage >= 0.80) {
        onParametersExtracted?.(data.extracted_parameters)
      }
    }
  })

  return (
    <div className="langextract-interface min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <LangExtractChatPanel
              session={session}
              onMessageProcess={processMessage.mutate}
              isProcessing={processMessage.isPending}
            />
          </div>

          {/* Parameter Sidebar */}
          <div className="lg:col-span-1">
            <ParameterOverviewPanel
              parameters={session?.extracted_parameters}
              completion={session?.completion_percentage}
              jobType={session?.detected_job_type}
              confidence={session?.detection_confidence}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
```

### 4.2.2 German-First UX Design

**Sprachlokalisierung für deutsche Benutzer**

```typescript
// Lokalisierung mit i18n-Patterns
const germanUXTexts = {
  langextract: {
    welcome: "Willkommen bei StreamWorks LangExtract",
    jobTypeDetection: "Job-Typ wird erkannt...",
    highConfidence: "Hohe Sicherheit ({confidence}%)",
    parameterExtraction: "Parameter werden extrahiert",
    completionStatus: "Vollständigkeit: {percentage}%",
    xmlGeneration: "XML-Generierung möglich"
  },
  confidenceLevels: {
    high: "Sehr sicher (≥90%)",
    medium: "Mittel sicher (70-89%)",
    low: "Niedrig sicher (<70%)",
    unknown: "Unbekannt"
  },
  jobTypes: {
    FILE_TRANSFER: "Datentransfer",
    SAP: "SAP-Integration",
    STANDARD: "Standard-Automation"
  }
}

// UX-optimierte Confidence-Anzeige
function ConfidenceIndicator({ confidence, jobType }: {
  confidence: number
  jobType: string
}) {
  const getConfidenceLevel = (conf: number) => {
    if (conf >= 0.90) return 'high'
    if (conf >= 0.70) return 'medium'
    return 'low'
  }

  const level = getConfidenceLevel(confidence)

  return (
    <div className={`confidence-indicator confidence-${level}`}>
      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full bg-confidence-${level}`} />
        <span className="text-sm font-medium">
          {germanUXTexts.jobTypes[jobType]} • {germanUXTexts.confidenceLevels[level]}
        </span>
        <span className="text-xs text-gray-500">
          {Math.round(confidence * 100)}%
        </span>
      </div>
    </div>
  )
}
```

**Intuitive Interaktionspatterns**

```typescript
// Smart Suggestions für bessere UX
function SmartSuggestions({ jobType, currentParameters }: {
  jobType: string | null
  currentParameters: ExtractedParameters
}) {
  const suggestions = useMemo(() => {
    if (!jobType) return []

    switch (jobType) {
      case 'FILE_TRANSFER':
        return [
          "Welche Dateien sollen übertragen werden?",
          "Vom welchem Server zum welchem Server?",
          "Soll die Übertragung regelmäßig stattfinden?"
        ]
      case 'SAP':
        return [
          "Welches SAP-System (GT123_PRD, PA1_DEV)?",
          "Welche Transaktionscodes werden benötigt?",
          "Export oder Import-Operation?"
        ]
      case 'STANDARD':
        return [
          "Welches Skript soll ausgeführt werden?",
          "Auf welchem Server?",
          "Mit welchen Parametern?"
        ]
      default:
        return []
    }
  }, [jobType])

  const missingParameters = suggestions.filter((suggestion, index) => {
    const parameterKeys = Object.keys(currentParameters)
    return parameterKeys.length < index + 1
  })

  if (missingParameters.length === 0) return null

  return (
    <div className="smart-suggestions bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h4 className="text-sm font-medium text-blue-900 mb-2">
        Vorschläge für weitere Parameter:
      </h4>
      <ul className="space-y-1">
        {missingParameters.map((suggestion, index) => (
          <li key={index} className="text-sm text-blue-700">
            • {suggestion}
          </li>
        ))}
      </ul>
    </div>
  )
}
```

### 4.2.3 Accessibility und Usability

**WCAG 2.1 AA Compliance**

```typescript
// Accessibility-First Komponenten
function AccessibleParameterInput({
  label,
  value,
  onChange,
  required = false,
  ariaDescribedBy
}: AccessibleInputProps) {
  const inputId = useId()
  const errorId = useId()

  return (
    <div className="form-group">
      <label
        htmlFor={inputId}
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        {label}
        {required && <span className="text-red-500 ml-1" aria-label="Pflichtfeld">*</span>}
      </label>

      <input
        id={inputId}
        type="text"
        value={value}
        onChange={onChange}
        className="w-full px-3 py-2 border border-gray-300 rounded-md
                   focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                   disabled:bg-gray-50 disabled:cursor-not-allowed"
        aria-describedby={`${ariaDescribedBy} ${errorId}`}
        aria-required={required}
      />

      {/* Screen Reader Support */}
      <div id={errorId} className="sr-only">
        {required && !value ? `${label} ist ein Pflichtfeld` : ''}
      </div>
    </div>
  )
}

// Keyboard Navigation Support
function useKeyboardNavigation() {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl+K: Focus auf Suchfeld
      if (event.ctrlKey && event.key === 'k') {
        event.preventDefault()
        const searchInput = document.querySelector('[data-search-input]') as HTMLElement
        searchInput?.focus()
      }

      // Escape: Schließe Modals
      if (event.key === 'Escape') {
        const modals = document.querySelectorAll('[data-modal-open]')
        modals.forEach(modal => {
          (modal as HTMLElement).click()
        })
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])
}
```

---

## 4.3 Prozess der KI-gestützten XML-Generierung

### 4.3.1 Multi-Layer Job Type Detection

**Algorithmus-Design für 88.9% Accuracy**

Das Enhanced Job Type Detection System implementiert eine mehrstufige Erkennungsstrategie:

```python
class EnhancedJobTypeDetector:
    """
    Multi-Layer Job Type Detection System
    Erreicht 88.9% Accuracy durch kombinierte Erkennungsschichten
    """

    def __init__(self):
        # Layer 1: High-Confidence Pattern Matching (95%+)
        self.high_confidence_patterns = {
            "FILE_TRANSFER": [
                {
                    "pattern": r"(?:daten[trs]*transfer|file\s*transfer|datei[en]*\s*transfer)",
                    "confidence": 0.95,
                    "description": "Explizite Transfer-Begriffe"
                },
                {
                    "pattern": r"zwischen\s+([a-zA-Z0-9_\-]+)\s+(?:und|zu|nach)\s+([a-zA-Z0-9_\-]+)",
                    "confidence": 0.92,
                    "description": "System-zu-System Transfer Pattern"
                }
            ],
            "SAP": [
                {
                    "pattern": r"(?:gt123|pa1|pt1|pd1)(?:_(?:prd|dev|tst|100|200))?",
                    "confidence": 0.93,
                    "description": "SAP System-Identifier"
                },
                {
                    "pattern": r"(?:ztv|rsus|rfc)[a-zA-Z0-9_]*",
                    "confidence": 0.90,
                    "description": "SAP Transaction Codes"
                }
            ],
            "STANDARD": [
                {
                    "pattern": r"python\s+[^\s]+\.py",
                    "confidence": 0.88,
                    "description": "Python Script Execution"
                },
                {
                    "pattern": r"(?:ausführen|execute|start|run)\s+(?:script|job|batch)",
                    "confidence": 0.85,
                    "description": "Script Execution Keywords"
                }
            ]
        }

        # Layer 2: Fuzzy Matching (70-85%)
        self.fuzzy_mappings = {
            "FILE_TRANSFER": ["datentranfer", "datentrasnfer", "datetransfer"],
            "SAP": ["jexa", "sap-system", "sapsystem"],
            "STANDARD": ["standardjob", "standard job", "batch"]
        }

        # Layer 3: Semantic Context Keywords (+15% Boost)
        self.context_keywords = {
            "FILE_TRANSFER": {
                "subjects": ["datei", "file", "dokument", "daten"],
                "actions": ["kopieren", "verschieben", "übertragen"],
                "targets": ["server", "agent", "system", "ordner"],
                "directions": ["von", "nach", "zu", "zwischen"]
            },
            "SAP": {
                "systems": ["sap", "bw", "erp", "hana"],
                "operations": ["export", "import", "report", "query"],
                "objects": ["tabelle", "view", "program", "transaction"]
            },
            "STANDARD": {
                "languages": ["python", "java", "bash", "node"],
                "actions": ["ausführen", "starten", "run", "execute"],
                "types": ["script", "job", "batch", "program"]
            }
        }

    async def detect_job_type(self, message: str) -> Dict[str, Any]:
        """
        Hauptmethode für Multi-Layer Job Type Detection

        Returns:
            {
                "detected_job_type": str,
                "confidence": float,
                "detection_method": str,
                "alternative_candidates": List[Tuple[str, float]]
            }
        """
        message_lower = message.lower().strip()

        # Layer 1: High-Confidence Pattern Matching
        high_conf_result = await self._apply_high_confidence_patterns(message_lower)
        if high_conf_result["confidence"] >= 0.90:
            return high_conf_result

        # Layer 2: Fuzzy Matching für Schreibfehler
        fuzzy_result = await self._apply_fuzzy_matching(message_lower)

        # Layer 3: Semantic Context Analysis
        context_boost = await self._apply_semantic_context_analysis(message_lower)

        # Combined Scoring mit Confidence Thresholds
        final_scores = self._combine_detection_layers(
            high_conf_result, fuzzy_result, context_boost
        )

        return self._select_best_match(final_scores)

    async def _apply_high_confidence_patterns(self, message: str) -> Dict[str, Any]:
        """Layer 1: Direkte Pattern-Matches mit hoher Confidence"""
        best_match = None
        best_confidence = 0.0
        matched_patterns = []

        for job_type, patterns in self.high_confidence_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                confidence = pattern_info["confidence"]

                if re.search(pattern, message, re.IGNORECASE):
                    matched_patterns.append(pattern_info)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = job_type

        return {
            "detected_job_type": best_match,
            "confidence": best_confidence,
            "detection_method": "high_confidence_pattern",
            "matched_patterns": matched_patterns
        }

    async def _apply_fuzzy_matching(self, message: str) -> Dict[str, float]:
        """Layer 2: Fuzzy String-Matching für Schreibfehler"""
        fuzzy_scores = {}

        for job_type, fuzzy_terms in self.fuzzy_mappings.items():
            best_fuzzy_score = 0.0

            for term in fuzzy_terms:
                if term in message:
                    # Direkter Match
                    best_fuzzy_score = max(best_fuzzy_score, 0.85)
                else:
                    # Levenshtein-ähnliche Similarität
                    similarity = self._calculate_similarity(term, message)
                    if similarity >= 0.7:
                        fuzzy_confidence = 0.6 + (similarity * 0.2)  # 0.6-0.8 range
                        best_fuzzy_score = max(best_fuzzy_score, fuzzy_confidence)

            if best_fuzzy_score > 0:
                fuzzy_scores[job_type] = best_fuzzy_score

        return fuzzy_scores

    async def _apply_semantic_context_analysis(self, message: str) -> Dict[str, float]:
        """Layer 3: Semantische Kontext-Analyse mit Bonus-Scoring"""
        context_scores = {}

        for job_type, categories in self.context_keywords.items():
            category_matches = {}

            for category, keywords in categories.items():
                matches = sum(1 for keyword in keywords if keyword in message)
                if matches > 0:
                    # Scoring: min(matches * 0.2, 0.8) pro Kategorie
                    category_score = min(matches * 0.2, 0.8)
                    category_matches[category] = category_score

            if category_matches:
                # Basis-Score: Durchschnitt aller Kategorien
                base_score = sum(category_matches.values()) / len(category_matches)

                # Multi-Category Bonus
                category_count = len(category_matches)
                if category_count >= 3:
                    bonus = 0.4  # 40% Bonus für ≥3 Kategorien
                elif category_count >= 2:
                    bonus = 0.2  # 20% Bonus für ≥2 Kategorien
                else:
                    bonus = 0.0

                # Final Context Score (max 0.15 additiv)
                context_scores[job_type] = min(base_score + bonus, 0.15)

        return context_scores

    def _combine_detection_layers(self,
                                high_conf: Dict[str, Any],
                                fuzzy: Dict[str, float],
                                context: Dict[str, float]) -> Dict[str, float]:
        """Kombiniert alle Detection-Layer zu finalen Confidence-Scores"""
        combined_scores = {}

        # Sammle alle Job-Types aus allen Layern
        all_job_types = set()
        if high_conf["detected_job_type"]:
            all_job_types.add(high_conf["detected_job_type"])
        all_job_types.update(fuzzy.keys())
        all_job_types.update(context.keys())

        for job_type in all_job_types:
            # Base Score aus High-Confidence Layer
            base_score = high_conf["confidence"] if high_conf["detected_job_type"] == job_type else 0.0

            # Fuzzy Layer Addition (wenn kein High-Confidence Match)
            if base_score < 0.70 and job_type in fuzzy:
                base_score = max(base_score, fuzzy[job_type])

            # Context Boost (additiv)
            if job_type in context:
                base_score += context[job_type]

            combined_scores[job_type] = min(base_score, 1.0)  # Cap bei 100%

        return combined_scores

    def _select_best_match(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """Wählt beste Matches basierend auf Confidence-Thresholds"""
        if not scores:
            return {
                "detected_job_type": None,
                "confidence": 0.0,
                "detection_method": "no_match",
                "alternative_candidates": []
            }

        # Sortiere nach Confidence
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_job_type, best_confidence = sorted_scores[0]

        # Alternative Candidates (>= 70% Confidence)
        alternatives = [(job_type, conf) for job_type, conf in sorted_scores[1:] if conf >= 0.70]

        # Detection Method bestimmen
        if best_confidence >= 0.90:
            method = "high_confidence"
        elif best_confidence >= 0.80:
            method = "medium_confidence"
        elif best_confidence >= 0.70:
            method = "low_confidence"
        else:
            method = "insufficient_confidence"

        return {
            "detected_job_type": best_job_type if best_confidence >= 0.70 else None,
            "confidence": best_confidence,
            "detection_method": method,
            "alternative_candidates": alternatives
        }
```

### 4.3.2 Enhanced Parameter Extraction Pipeline

**State-Machine-basierte Parameter-Sammlung**

```python
class EnhancedUnifiedParameterExtractor:
    """
    Enhanced Parameter Extraction mit State-Machine Pattern
    Sammelt Parameter iterativ über mehrere Conversation-Turns
    """

    def __init__(self):
        self.parameter_schemas = self._load_parameter_schemas()
        self.extraction_state_machine = self._init_state_machine()

    async def extract_parameters(self,
                               message: str,
                               job_type: str,
                               session_id: str,
                               current_state: Dict[str, Any]) -> ExtractionResult:
        """
        Hauptmethode für Enhanced Parameter Extraction

        Args:
            message: Benutzer-Nachricht
            job_type: Erkannter Job-Type (FILE_TRANSFER, SAP, STANDARD)
            session_id: Session für State-Persistierung
            current_state: Aktueller Extraction-State

        Returns:
            ExtractionResult mit extrahierten Parametern und Next-Actions
        """

        # 1. Load Job-specific Parameter Schema
        schema = self.parameter_schemas.get(job_type)
        if not schema:
            raise ValueError(f"Unknown job_type: {job_type}")

        # 2. Execute Parameter Extraction State Machine
        extraction_context = ExtractionContext(
            message=message,
            job_type=job_type,
            session_id=session_id,
            current_parameters=current_state.get("parameters", {}),
            required_parameters=schema["required"],
            optional_parameters=schema["optional"],
            current_state=current_state.get("state", "INITIAL")
        )

        # 3. State Machine Execution
        result = await self.extraction_state_machine.execute(extraction_context)

        # 4. Parameter Validation & Enrichment
        validated_result = await self._validate_and_enrich_parameters(result, schema)

        # 5. Generate Next Action Suggestions
        next_actions = await self._generate_next_actions(validated_result, schema)

        return ExtractionResult(
            detected_job_type=job_type,
            extracted_parameters=validated_result.parameters,
            completion_percentage=validated_result.completion_percentage,
            validation_errors=validated_result.validation_errors,
            next_actions=next_actions,
            state=validated_result.state
        )

class ParameterExtractionStateMachine:
    """State Machine für iterative Parameter-Sammlung"""

    def __init__(self):
        self.states = {
            "INITIAL": self._initial_state,
            "COLLECTING_REQUIRED": self._collecting_required_state,
            "COLLECTING_OPTIONAL": self._collecting_optional_state,
            "VALIDATING": self._validating_state,
            "COMPLETED": self._completed_state,
            "ERROR": self._error_state
        }

    async def execute(self, context: ExtractionContext) -> StateResult:
        """Führt State Machine basierend auf aktuellem Zustand aus"""
        current_state = context.current_state
        state_handler = self.states.get(current_state, self._error_state)

        return await state_handler(context)

    async def _initial_state(self, context: ExtractionContext) -> StateResult:
        """Initial State: Beginne Parameter-Extraktion"""

        # Extract parameters from initial message
        extracted = await self._extract_from_message(
            context.message,
            context.required_parameters + context.optional_parameters
        )

        # Merge mit existing parameters
        all_parameters = {**context.current_parameters, **extracted}

        # Check completion status
        required_complete = all(
            param in all_parameters and all_parameters[param] is not None
            for param in context.required_parameters
        )

        if required_complete:
            next_state = "COLLECTING_OPTIONAL"
        else:
            next_state = "COLLECTING_REQUIRED"

        return StateResult(
            parameters=all_parameters,
            state=next_state,
            completion_percentage=self._calculate_completion(
                all_parameters,
                context.required_parameters,
                context.optional_parameters
            )
        )

    async def _collecting_required_state(self, context: ExtractionContext) -> StateResult:
        """Sammelt noch fehlende Required Parameter"""

        # Identifiziere fehlende Required Parameter
        missing_required = [
            param for param in context.required_parameters
            if param not in context.current_parameters or
               context.current_parameters[param] is None
        ]

        if not missing_required:
            # Alle Required Parameter vorhanden
            return StateResult(
                parameters=context.current_parameters,
                state="COLLECTING_OPTIONAL",
                completion_percentage=self._calculate_completion(
                    context.current_parameters,
                    context.required_parameters,
                    context.optional_parameters
                )
            )

        # Extrahiere weitere Parameter aus aktueller Message
        extracted = await self._extract_from_message(context.message, missing_required)
        updated_parameters = {**context.current_parameters, **extracted}

        # Check if still missing required parameters
        still_missing = [
            param for param in context.required_parameters
            if param not in updated_parameters or updated_parameters[param] is None
        ]

        if still_missing:
            next_state = "COLLECTING_REQUIRED"
        else:
            next_state = "COLLECTING_OPTIONAL"

        return StateResult(
            parameters=updated_parameters,
            state=next_state,
            completion_percentage=self._calculate_completion(
                updated_parameters,
                context.required_parameters,
                context.optional_parameters
            ),
            missing_required=still_missing
        )

    async def _collecting_optional_state(self, context: ExtractionContext) -> StateResult:
        """Sammelt Optional Parameter für vollständige Konfiguration"""

        # Extract optional parameters from message
        missing_optional = [
            param for param in context.optional_parameters
            if param not in context.current_parameters
        ]

        if missing_optional:
            extracted = await self._extract_from_message(context.message, missing_optional)
            updated_parameters = {**context.current_parameters, **extracted}
        else:
            updated_parameters = context.current_parameters

        completion = self._calculate_completion(
            updated_parameters,
            context.required_parameters,
            context.optional_parameters
        )

        # Entscheide ob Validation oder mehr Optional Parameters
        if completion >= 0.8:  # 80% Completion Threshold
            next_state = "VALIDATING"
        else:
            next_state = "COLLECTING_OPTIONAL"

        return StateResult(
            parameters=updated_parameters,
            state=next_state,
            completion_percentage=completion
        )

    async def _validating_state(self, context: ExtractionContext) -> StateResult:
        """Validiert alle gesammelten Parameter"""

        validation_errors = []
        validated_parameters = {}

        for param_name, param_value in context.current_parameters.items():
            try:
                # Type validation basierend auf Schema
                validated_value = await self._validate_parameter(
                    param_name, param_value, context
                )
                validated_parameters[param_name] = validated_value
            except ValidationError as e:
                validation_errors.append(f"{param_name}: {str(e)}")

        if validation_errors:
            return StateResult(
                parameters=validated_parameters,
                state="ERROR",
                completion_percentage=0.0,
                validation_errors=validation_errors
            )

        return StateResult(
            parameters=validated_parameters,
            state="COMPLETED",
            completion_percentage=1.0
        )

    async def _completed_state(self, context: ExtractionContext) -> StateResult:
        """Completed State: Parameter-Extraktion abgeschlossen"""
        return StateResult(
            parameters=context.current_parameters,
            state="COMPLETED",
            completion_percentage=1.0
        )

    def _calculate_completion(self,
                            parameters: Dict[str, Any],
                            required: List[str],
                            optional: List[str]) -> float:
        """Berechnet Completion-Percentage basierend auf vorhandenen Parametern"""

        # Required Parameters: 70% des Gesamtgewichts
        required_present = sum(1 for param in required
                             if param in parameters and parameters[param] is not None)
        required_score = (required_present / len(required)) * 0.7 if required else 0.0

        # Optional Parameters: 30% des Gesamtgewichts
        optional_present = sum(1 for param in optional
                             if param in parameters and parameters[param] is not None)
        optional_score = (optional_present / len(optional)) * 0.3 if optional else 0.0

        return required_score + optional_score
```

### 4.3.3 Template-basierte XML-Generierung

**Deterministische XML-Generierung mit Jinja2**

Das System verwendet Template-basierte XML-Generierung anstelle von LLM-basierten Ansätzen für deterministische und validierbare Ergebnisse:

```python
class TemplateEngine:
    """
    Template-basierte XML-Generierung mit Jinja2
    Ersetzt LLM-basierte Generation für Determinismus
    """

    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader('templates/xml_templates/'),
            enable_async=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Custom Jinja2 Filters für StreamWorks
        self.jinja_env.filters['format_datetime'] = self._format_datetime
        self.jinja_env.filters['sanitize_path'] = self._sanitize_path
        self.jinja_env.filters['format_server_name'] = self._format_server_name

        self.parameter_mapper = ParameterMapper()

    async def generate_xml(self,
                          job_type: str,
                          parameters: Dict[str, Any],
                          template_options: Optional[Dict] = None) -> XMLGenerationResult:
        """
        Hauptmethode für Template-basierte XML-Generierung

        Args:
            job_type: Job-Type (FILE_TRANSFER, SAP, STANDARD)
            parameters: Extrahierte Parameter
            template_options: Zusätzliche Template-Optionen

        Returns:
            XMLGenerationResult mit generiertem XML und Metadaten
        """

        # 1. Load job-specific template
        template_name = f"{job_type.lower()}_template.xml"
        try:
            template = await self.jinja_env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateError(f"Template nicht gefunden: {template_name}")

        # 2. Map parameters to template variables
        mapped_parameters = await self.parameter_mapper.map_parameters(
            parameters, job_type
        )

        # 3. Generate auto-parameters for missing fields
        auto_generated = await self._generate_auto_parameters(
            mapped_parameters, job_type
        )

        # 4. Combine all parameters
        template_context = {
            **mapped_parameters,
            **auto_generated,
            **(template_options or {}),
            'generation_timestamp': datetime.now(),
            'job_type': job_type
        }

        # 5. Render XML template
        try:
            xml_content = await template.render_async(**template_context)
        except Exception as e:
            raise TemplateRenderingError(f"Template rendering failed: {str(e)}")

        # 6. Validate generated XML
        validation_result = await self._validate_xml(xml_content, job_type)

        return XMLGenerationResult(
            xml_content=xml_content,
            template_used=template_name,
            mapped_parameters=mapped_parameters,
            auto_generated_parameters=auto_generated,
            validation_result=validation_result,
            generation_timestamp=datetime.now()
        )

class ParameterMapper:
    """Intelligente Parameter-Mappings für Template-Variables"""

    def __init__(self):
        # Field Mappings für verschiedene Job-Types
        self.field_mappings = {
            "FILE_TRANSFER": {
                "source_server": ["von_server", "quell_server", "source", "from_server"],
                "target_server": ["zu_server", "ziel_server", "target", "to_server"],
                "file_pattern": ["dateien", "files", "datei_pattern", "file_list"],
                "transfer_mode": ["modus", "mode", "übertragungsmodus"],
                "schedule": ["zeitplan", "schedule", "cron", "frequency"]
            },
            "SAP": {
                "sap_system": ["system", "sap_system", "mandant", "client"],
                "transaction_code": ["tcode", "transaktion", "transaction"],
                "export_table": ["tabelle", "table", "view"],
                "target_path": ["pfad", "path", "ziel_pfad", "target_dir"],
                "report_name": ["report", "programm", "program_name"]
            },
            "STANDARD": {
                "script_path": ["script", "pfad", "file_path", "executable"],
                "server": ["server", "host", "ziel_server"],
                "arguments": ["parameter", "args", "arguments", "options"],
                "working_directory": ["arbeitsverzeichnis", "workdir", "cwd"],
                "environment": ["umgebung", "env", "environment"]
            }
        }

        # Fuzzy Matching für Field Names
        self.fuzzy_threshold = 0.8

    async def map_parameters(self,
                           parameters: Dict[str, Any],
                           job_type: str) -> Dict[str, Any]:
        """Maps extracted parameters zu Template-Variable-Namen"""

        mappings = self.field_mappings.get(job_type, {})
        mapped = {}

        for template_field, possible_keys in mappings.items():
            # Direct matches first
            for key in possible_keys:
                if key in parameters:
                    mapped[template_field] = parameters[key]
                    break

            # Fuzzy matching if no direct match
            if template_field not in mapped:
                best_match = self._find_fuzzy_match(possible_keys, parameters.keys())
                if best_match:
                    mapped[template_field] = parameters[best_match]

        # Map remaining parameters direkt (falls nicht gemappt)
        for key, value in parameters.items():
            if not any(key in possible_keys for possible_keys in mappings.values()):
                # Direkte Übernahme für unmappable parameters
                mapped[key] = value

        return mapped

    def _find_fuzzy_match(self, target_keys: List[str], available_keys: List[str]) -> Optional[str]:
        """Findet beste fuzzy match zwischen target und available keys"""
        best_match = None
        best_score = 0.0

        for target in target_keys:
            for available in available_keys:
                score = self._calculate_similarity(target.lower(), available.lower())
                if score >= self.fuzzy_threshold and score > best_score:
                    best_score = score
                    best_match = available

        return best_match

    def _calculate_similarity(self, a: str, b: str) -> float:
        """Berechnet String-Similarität (simplified Levenshtein)"""
        if a == b:
            return 1.0

        # Simplified similarity based on common substrings
        common_chars = sum(1 for char in a if char in b)
        max_length = max(len(a), len(b))

        return common_chars / max_length if max_length > 0 else 0.0

    async def _generate_auto_parameters(self,
                                      mapped_parameters: Dict[str, Any],
                                      job_type: str) -> Dict[str, Any]:
        """Generiert automatische Parameter für fehlende Template-Felder"""

        auto_params = {}
        current_time = datetime.now()

        # Job-type-specific auto-generation
        if job_type == "FILE_TRANSFER":
            auto_params.update({
                "job_id": f"FT_{current_time.strftime('%Y%m%d_%H%M%S')}",
                "transfer_mode": "COPY" if "transfer_mode" not in mapped_parameters else mapped_parameters["transfer_mode"],
                "retry_count": 3,
                "timeout_minutes": 30,
                "notification_email": "streamworks@company.com"
            })

        elif job_type == "SAP":
            auto_params.update({
                "job_id": f"SAP_{current_time.strftime('%Y%m%d_%H%M%S')}",
                "export_format": "CSV",
                "field_delimiter": ";",
                "text_qualifier": '"',
                "max_records": 1000000,
                "notification_email": "sap-admin@company.com"
            })

        elif job_type == "STANDARD":
            auto_params.update({
                "job_id": f"STD_{current_time.strftime('%Y%m%d_%H%M%S')}",
                "execution_timeout": 1800,  # 30 minutes
                "retry_on_failure": True,
                "capture_output": True,
                "notification_email": "ops@company.com"
            })

        # Common auto-parameters für alle Job-Types
        auto_params.update({
            "created_by": "StreamWorks-KI",
            "creation_date": current_time.isoformat(),
            "priority": "MEDIUM",
            "environment": "PROD"
        })

        return auto_params
```

**XML Template Beispiele**

```xml
<!-- templates/xml_templates/file_transfer_template.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<streamworks:job xmlns:streamworks="http://streamworks.company.com/schema"
                 xmlns:ft="http://streamworks.company.com/filetransfer">

  <job_metadata>
    <job_id>{{ job_id }}</job_id>
    <job_type>FILE_TRANSFER</job_type>
    <created_by>{{ created_by }}</created_by>
    <creation_date>{{ creation_date }}</creation_date>
    <priority>{{ priority }}</priority>
  </job_metadata>

  <ft:file_transfer>
    <ft:source>
      <ft:server>{{ source_server | format_server_name }}</ft:server>
      <ft:path>{{ source_path | sanitize_path }}</ft:path>
      <ft:file_pattern>{{ file_pattern | default('*.*') }}</ft:file_pattern>
    </ft:source>

    <ft:target>
      <ft:server>{{ target_server | format_server_name }}</ft:server>
      <ft:path>{{ target_path | sanitize_path }}</ft:path>
    </ft:target>

    <ft:options>
      <ft:transfer_mode>{{ transfer_mode | upper }}</ft:transfer_mode>
      <ft:overwrite>{{ overwrite_existing | default(false) | lower }}</ft:overwrite>
      <ft:create_directories>{{ create_target_dirs | default(true) | lower }}</ft:create_directories>
      <ft:preserve_timestamps>{{ preserve_timestamps | default(true) | lower }}</ft:preserve_timestamps>
    </ft:options>

    <ft:retry_policy>
      <ft:retry_count>{{ retry_count }}</ft:retry_count>
      <ft:retry_interval>PT{{ retry_interval_minutes | default(5) }}M</ft:retry_interval>
      <ft:timeout>PT{{ timeout_minutes }}M</ft:timeout>
    </ft:retry_policy>
  </ft:file_transfer>

  {% if schedule %}
  <scheduling>
    <schedule_type>{{ schedule.type | default('CRON') }}</schedule_type>
    <cron_expression>{{ schedule.cron_expression | default('0 0 * * *') }}</cron_expression>
    <timezone>{{ schedule.timezone | default('Europe/Berlin') }}</timezone>
  </scheduling>
  {% endif %}

  <notifications>
    <on_success>
      <email>{{ notification_email }}</email>
      <subject>File Transfer Completed: {{ job_id }}</subject>
    </on_success>
    <on_failure>
      <email>{{ notification_email }}</email>
      <subject>File Transfer Failed: {{ job_id }}</subject>
    </on_failure>
  </notifications>

  <audit>
    <generation_method>STREAMWORKS_KI_TEMPLATE</generation_method>
    <generation_timestamp>{{ generation_timestamp | format_datetime }}</generation_timestamp>
    <parameter_count>{{ mapped_parameters | length }}</parameter_count>
    <auto_generated_count>{{ auto_generated_parameters | length }}</auto_generated_count>
  </audit>
</streamworks:job>
```

---

## 4.4 Konzeption des RAG-basierten Support-Systems

### 4.4.1 Hybrid Retrieval Architektur

**Vector + Lexical Search Kombination**

Das RAG-System implementiert eine **Hybrid Retrieval Strategy**, die dense vector search mit lexical search kombiniert für optimale Relevanz:

```python
class UnifiedRAGService:
    """
    Unified RAG Service mit Hybrid Retrieval
    Kombiniert Vector Search (Qdrant) mit Lexical Search für optimale Ergebnisse
    """

    def __init__(self,
                 qdrant_client: QdrantClient,
                 embedding_service: EmbeddingService,
                 chat_service: ChatService):
        self.qdrant_client = qdrant_client
        self.embedding_service = embedding_service
        self.chat_service = chat_service

        # Hybrid Search Configuration
        self.hybrid_config = HybridSearchConfig(
            vector_weight=0.7,      # 70% Vector Search
            lexical_weight=0.3,     # 30% Lexical Search
            min_score_threshold=0.6,
            max_results=10
        )

        # Collections für verschiedene Domänen
        self.collections = {
            "documents": "streamworks_documents",    # Haupt-Dokumente
            "hybrid": "streamworks_hybrid",         # Hybrid Search Collection
            "knowledge": "streamworks_knowledge"     # Knowledge Base
        }

    async def process_rag_query(self,
                               query: str,
                               context: Optional[RAGContext] = None,
                               search_mode: str = "hybrid") -> RAGResponse:
        """
        Hauptmethode für RAG-basierte Anfrageverarbeitung

        Args:
            query: Benutzer-Anfrage
            context: Optional RAG-Context für kontextuelle Suche
            search_mode: "hybrid", "vector_only", "lexical_only"

        Returns:
            RAGResponse mit Antwort und Source-Grounding
        """

        # 1. Query Understanding & Enhancement
        enhanced_query = await self._enhance_query(query, context)

        # 2. Hybrid Retrieval
        retrieved_docs = await self._hybrid_retrieval(
            enhanced_query, search_mode
        )

        # 3. Re-ranking für Relevanz
        ranked_docs = await self._rerank_documents(
            retrieved_docs, enhanced_query
        )

        # 4. Context Assembly für LLM
        llm_context = await self._assemble_llm_context(
            ranked_docs, enhanced_query, context
        )

        # 5. Response Generation mit Source Grounding
        response = await self._generate_response(
            llm_context, enhanced_query, ranked_docs
        )

        return response

    async def _hybrid_retrieval(self,
                               query: EnhancedQuery,
                               search_mode: str) -> List[RetrievedDocument]:
        """Hybrid Retrieval mit Vector + Lexical Search"""

        if search_mode == "vector_only":
            return await self._vector_search(query)
        elif search_mode == "lexical_only":
            return await self._lexical_search(query)
        else:  # hybrid
            # Parallel Vector + Lexical Search
            vector_results, lexical_results = await asyncio.gather(
                self._vector_search(query),
                self._lexical_search(query)
            )

            # Hybrid Score Fusion
            return await self._fuse_search_results(
                vector_results, lexical_results
            )

    async def _vector_search(self, query: EnhancedQuery) -> List[RetrievedDocument]:
        """Dense Vector Search mit Embedding-Models"""

        # Generate query embedding
        query_vector = await self.embedding_service.embed_query(query.text)

        # Multi-collection search
        search_tasks = []
        for collection_name in self.collections.values():
            search_task = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=self.hybrid_config.max_results,
                score_threshold=self.hybrid_config.min_score_threshold,
                with_payload=True,
                with_vectors=False
            )
            search_tasks.append(search_task)

        # Execute parallel searches
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Aggregate results
        retrieved_docs = []
        for i, results in enumerate(search_results):
            if isinstance(results, Exception):
                logger.warning(f"Vector search failed for collection {i}: {results}")
                continue

            for hit in results:
                doc = RetrievedDocument(
                    id=str(hit.id),
                    content=hit.payload.get("text", ""),
                    metadata=hit.payload,
                    score=hit.score,
                    search_type="vector",
                    collection=list(self.collections.values())[i]
                )
                retrieved_docs.append(doc)

        # Sort by score and deduplicate
        retrieved_docs.sort(key=lambda x: x.score, reverse=True)
        return self._deduplicate_documents(retrieved_docs)

    async def _lexical_search(self, query: EnhancedQuery) -> List[RetrievedDocument]:
        """Lexical Search mit BM25-ähnlichem Scoring"""

        # Query Tokenization
        query_terms = self._tokenize_query(query.text)

        # Build search filters basierend auf Metadaten
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="text",
                    match=MatchText(text=query.text)
                )
            ]
        )

        # Enhanced search mit Payload-Filter
        search_results = []
        for collection_name in self.collections.values():
            try:
                results = await self.qdrant_client.scroll(
                    collection_name=collection_name,
                    scroll_filter=search_filter,
                    limit=self.hybrid_config.max_results,
                    with_payload=True,
                    with_vectors=False
                )

                for hit in results[0]:  # results ist tuple (hits, next_page_offset)
                    # Calculate BM25-style score
                    lexical_score = self._calculate_lexical_score(
                        query_terms, hit.payload.get("text", "")
                    )

                    if lexical_score >= self.hybrid_config.min_score_threshold:
                        doc = RetrievedDocument(
                            id=str(hit.id),
                            content=hit.payload.get("text", ""),
                            metadata=hit.payload,
                            score=lexical_score,
                            search_type="lexical",
                            collection=collection_name
                        )
                        search_results.append(doc)

            except Exception as e:
                logger.warning(f"Lexical search failed for {collection_name}: {e}")

        # Sort by lexical score
        search_results.sort(key=lambda x: x.score, reverse=True)
        return search_results[:self.hybrid_config.max_results]

    async def _fuse_search_results(self,
                                 vector_results: List[RetrievedDocument],
                                 lexical_results: List[RetrievedDocument]) -> List[RetrievedDocument]:
        """Fusioniert Vector und Lexical Search Results mit Gewichtung"""

        # Create unified document map
        doc_map = {}

        # Add vector results mit vector weight
        for doc in vector_results:
            doc_id = doc.id
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
                doc_map[doc_id].hybrid_score = doc.score * self.hybrid_config.vector_weight
                doc_map[doc_id].vector_score = doc.score
                doc_map[doc_id].lexical_score = 0.0

        # Add lexical results mit lexical weight
        for doc in lexical_results:
            doc_id = doc.id
            if doc_id in doc_map:
                # Document found in both searches - boost score
                doc_map[doc_id].hybrid_score += doc.score * self.hybrid_config.lexical_weight
                doc_map[doc_id].lexical_score = doc.score
            else:
                # Document nur in lexical search
                doc_map[doc_id] = doc
                doc_map[doc_id].hybrid_score = doc.score * self.hybrid_config.lexical_weight
                doc_map[doc_id].vector_score = 0.0
                doc_map[doc_id].lexical_score = doc.score

        # Sort by hybrid score
        fused_results = list(doc_map.values())
        fused_results.sort(key=lambda x: x.hybrid_score, reverse=True)

        return fused_results[:self.hybrid_config.max_results]

    async def _rerank_documents(self,
                              documents: List[RetrievedDocument],
                              query: EnhancedQuery) -> List[RankedDocument]:
        """Re-ranking für improved relevance mit Cross-Encoder"""

        ranked_docs = []

        for doc in documents:
            # Calculate relevance score basierend auf verschiedenen Faktoren
            relevance_factors = {
                "semantic_similarity": doc.score,
                "query_term_coverage": self._calculate_query_coverage(query.text, doc.content),
                "document_freshness": self._calculate_freshness_score(doc.metadata),
                "document_authority": self._calculate_authority_score(doc.metadata),
                "content_completeness": self._calculate_completeness_score(doc.content)
            }

            # Weighted relevance score
            relevance_weights = {
                "semantic_similarity": 0.4,
                "query_term_coverage": 0.3,
                "document_freshness": 0.1,
                "document_authority": 0.1,
                "content_completeness": 0.1
            }

            final_relevance = sum(
                relevance_factors[factor] * relevance_weights[factor]
                for factor in relevance_factors
            )

            ranked_doc = RankedDocument(
                **doc.__dict__,
                relevance_score=final_relevance,
                relevance_factors=relevance_factors
            )
            ranked_docs.append(ranked_doc)

        # Sort by final relevance score
        ranked_docs.sort(key=lambda x: x.relevance_score, reverse=True)
        return ranked_docs

    async def _generate_response(self,
                               context: LLMContext,
                               query: EnhancedQuery,
                               source_docs: List[RankedDocument]) -> RAGResponse:
        """Generiert RAG-Response mit Source Grounding"""

        # Build prompt für LLM mit retrieved context
        system_prompt = """Du bist ein hilfreicher Assistent für das StreamWorks-System.
Beantworte Fragen basierend auf den bereitgestellten Dokumenten.

WICHTIG:
- Verwende nur Informationen aus den bereitgestellten Quellen
- Gib immer Quellenreferenzen an
- Bei unvollständigen Informationen, erwähne die Limitierungen
- Antworte auf Deutsch für deutsche Anfragen"""

        user_prompt = f"""
Anfrage: {query.text}

Relevante Dokumenten-Abschnitte:
{self._format_source_documents(source_docs)}

Bitte beantworte die Anfrage basierend auf diesen Informationen."""

        # Generate response via LLM
        try:
            llm_response = await self.chat_service.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1  # Low temperature für konsistente, faktische Antworten
            )

            # Extract source citations
            cited_sources = self._extract_source_citations(
                llm_response, source_docs
            )

            return RAGResponse(
                answer=llm_response,
                sources=cited_sources,
                query=query.text,
                retrieval_method="hybrid",
                confidence_score=self._calculate_response_confidence(
                    source_docs, llm_response
                ),
                processing_time=time.time() - query.start_time,
                metadata={
                    "num_sources_used": len(cited_sources),
                    "avg_source_relevance": np.mean([doc.relevance_score for doc in source_docs]),
                    "search_collections": list(set(doc.collection for doc in source_docs))
                }
            )

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return RAGResponse(
                answer="Es tut mir leid, aber ich konnte keine passende Antwort basierend auf den verfügbaren Dokumenten generieren.",
                sources=[],
                query=query.text,
                retrieval_method="hybrid",
                confidence_score=0.0,
                processing_time=time.time() - query.start_time,
                error=str(e)
            )
```

### 4.4.2 Document Processing Pipeline

**Layout-aware Document Chunking**

```python
class DocumentProcessor:
    """
    Layout-aware Document Processing für optimale RAG-Performance
    Berücksichtigt Dokumentstruktur für bessere Chunk-Qualität
    """

    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.min_chunk_size = 100

        # Layout-aware chunking strategies
        self.chunking_strategies = {
            "pdf": self._process_pdf_layout_aware,
            "markdown": self._process_markdown_structured,
            "text": self._process_text_semantic,
            "html": self._process_html_dom_aware
        }

    async def process_document(self,
                             document: UploadedDocument) -> ProcessedDocument:
        """Verarbeitet Dokument mit layout-aware chunking"""

        # 1. Document Type Detection
        doc_type = self._detect_document_type(document)

        # 2. Extract structured content
        structured_content = await self._extract_structured_content(
            document, doc_type
        )

        # 3. Layout-aware chunking
        strategy = self.chunking_strategies.get(doc_type, self._process_text_semantic)
        chunks = await strategy(structured_content)

        # 4. Enhance chunks mit Metadaten
        enhanced_chunks = await self._enhance_chunks_with_metadata(
            chunks, document, structured_content
        )

        # 5. Generate embeddings
        embedded_chunks = await self._generate_embeddings(enhanced_chunks)

        return ProcessedDocument(
            document_id=document.id,
            original_document=document,
            structured_content=structured_content,
            chunks=embedded_chunks,
            processing_metadata=ProcessingMetadata(
                processing_time=time.time(),
                chunk_count=len(embedded_chunks),
                document_type=doc_type,
                layout_structure_detected=True
            )
        )

    async def _process_pdf_layout_aware(self,
                                       structured_content: StructuredContent) -> List[ContentChunk]:
        """PDF-spezifisches Layout-aware Chunking"""

        chunks = []

        for page in structured_content.pages:
            # Respektiere PDF-Layout: Headers, Paragraphs, Tables
            current_chunk = ContentChunk()
            current_size = 0

            for element in page.layout_elements:
                element_text = element.text.strip()
                element_size = len(element_text)

                # Chunk-Grenzen basierend auf Layout-Elementen
                if (current_size + element_size > self.chunk_size and
                    current_chunk.text and
                    element.type in ["paragraph", "heading"]):

                    # Finalize current chunk
                    current_chunk.metadata.update({
                        "page_number": page.page_number,
                        "layout_types": list(set(el.type for el in current_chunk.elements)),
                        "has_tables": any(el.type == "table" for el in current_chunk.elements)
                    })
                    chunks.append(current_chunk)

                    # Start new chunk mit Overlap
                    overlap_text = current_chunk.text[-self.chunk_overlap:] if current_chunk.text else ""
                    current_chunk = ContentChunk(text=overlap_text)
                    current_size = len(overlap_text)

                # Add element to current chunk
                current_chunk.text += f"\n{element_text}"
                current_chunk.elements.append(element)
                current_size += element_size

            # Add final chunk if not empty
            if current_chunk.text.strip():
                current_chunk.metadata.update({
                    "page_number": page.page_number,
                    "layout_types": list(set(el.type for el in current_chunk.elements))
                })
                chunks.append(current_chunk)

        return chunks

    async def _process_markdown_structured(self,
                                         structured_content: StructuredContent) -> List[ContentChunk]:
        """Markdown-Structure-aware Chunking"""

        chunks = []
        markdown_tree = structured_content.markdown_tree

        def process_node(node, parent_context=""):
            """Rekursive Verarbeitung der Markdown-Tree"""

            if node.type == "heading":
                # Heading als neuer Chunk-Kontext
                heading_text = node.text
                full_context = f"{parent_context}\n# {heading_text}" if parent_context else f"# {heading_text}"

                # Process children mit heading context
                for child in node.children:
                    process_node(child, full_context)

            elif node.type in ["paragraph", "list", "code_block"]:
                # Content nodes als Chunks
                chunk_text = f"{parent_context}\n\n{node.text}" if parent_context else node.text

                if len(chunk_text) >= self.min_chunk_size:
                    chunk = ContentChunk(
                        text=chunk_text,
                        metadata={
                            "markdown_type": node.type,
                            "heading_context": parent_context,
                            "level": node.level if hasattr(node, 'level') else 0
                        }
                    )
                    chunks.append(chunk)

        # Process markdown tree
        for root_node in markdown_tree.root_nodes:
            process_node(root_node)

        return chunks

    async def _enhance_chunks_with_metadata(self,
                                          chunks: List[ContentChunk],
                                          document: UploadedDocument,
                                          structured_content: StructuredContent) -> List[EnhancedChunk]:
        """Erweitert Chunks mit reichhaltigen Metadaten für bessere Retrieval"""

        enhanced_chunks = []

        for i, chunk in enumerate(chunks):
            # Extract entities und keywords
            entities = await self._extract_entities(chunk.text)
            keywords = await self._extract_keywords(chunk.text)

            # Calculate content statistics
            stats = ContentStatistics(
                word_count=len(chunk.text.split()),
                sentence_count=chunk.text.count('.') + chunk.text.count('!') + chunk.text.count('?'),
                avg_sentence_length=len(chunk.text.split()) / max(1, chunk.text.count('.')),
                reading_difficulty=self._calculate_reading_difficulty(chunk.text)
            )

            enhanced_metadata = EnhancedMetadata(
                **chunk.metadata,
                document_id=document.id,
                document_title=document.title,
                document_type=document.content_type,
                chunk_index=i,
                chunk_id=f"{document.id}_{i}",
                entities=entities,
                keywords=keywords,
                content_stats=stats,
                created_at=datetime.now(),
                semantic_categories=await self._classify_content_categories(chunk.text)
            )

            enhanced_chunk = EnhancedChunk(
                text=chunk.text,
                metadata=enhanced_metadata,
                elements=chunk.elements
            )
            enhanced_chunks.append(enhanced_chunk)

        return enhanced_chunks
```

---

## 4.5 Sicherheits- und Datenschutzaspekte

### 4.5.1 Authentication & Authorization Konzept

**JWT-basierte Authentication mit Role-Based Access Control (RBAC)**

```python
class AuthService:
    """
    Enterprise Authentication Service mit Multi-Factor Authentication
    Implementiert RBAC für granulare Berechtigungskontrolle
    """

    def __init__(self,
                 jwt_service: JWTService,
                 user_repository: UserRepository,
                 permission_service: PermissionService):
        self.jwt_service = jwt_service
        self.user_repository = user_repository
        self.permission_service = permission_service

        # Security Configuration
        self.security_config = SecurityConfig(
            password_min_length=12,
            password_complexity_required=True,
            session_timeout_minutes=30,
            max_login_attempts=5,
            lockout_duration_minutes=30,
            require_2fa_for_admin=True
        )

    async def authenticate_user(self,
                              credentials: UserCredentials) -> AuthResult:
        """Authentifiziert Benutzer mit Multi-Factor Support"""

        # 1. Rate Limiting Check
        await self._check_rate_limits(credentials.username)

        # 2. User Lookup
        user = await self.user_repository.get_by_username(credentials.username)
        if not user or not user.is_active:
            await self._log_security_event("LOGIN_FAILED_USER_NOT_FOUND", credentials.username)
            raise AuthenticationError("Invalid credentials")

        # 3. Password Verification
        if not await self._verify_password(credentials.password, user.password_hash):
            await self._handle_failed_login(user)
            raise AuthenticationError("Invalid credentials")

        # 4. Account Status Checks
        if user.is_locked:
            raise AuthenticationError("Account is locked")

        # 5. Two-Factor Authentication (if required)
        if user.requires_2fa or (user.has_admin_role and self.security_config.require_2fa_for_admin):
            if not credentials.totp_code:
                return AuthResult(
                    status="REQUIRES_2FA",
                    requires_2fa=True,
                    temp_token=await self.jwt_service.generate_temp_token(user.id)
                )

            if not await self._verify_totp(user.totp_secret, credentials.totp_code):
                await self._log_security_event("2FA_FAILED", user.username)
                raise AuthenticationError("Invalid 2FA code")

        # 6. Generate Access & Refresh Tokens
        access_token = await self.jwt_service.generate_access_token(
            user_id=user.id,
            username=user.username,
            roles=user.roles,
            permissions=await self.permission_service.get_user_permissions(user.id)
        )

        refresh_token = await self.jwt_service.generate_refresh_token(user.id)

        # 7. Update Login Statistics
        await self.user_repository.update_last_login(user.id, datetime.now())
        await self._log_security_event("LOGIN_SUCCESS", user.username)

        return AuthResult(
            status="SUCCESS",
            access_token=access_token,
            refresh_token=refresh_token,
            user_profile=UserProfile.from_user(user),
            expires_in=self.jwt_service.access_token_expire_minutes * 60
        )

class PermissionService:
    """Role-Based Access Control (RBAC) Service"""

    def __init__(self):
        # Definierte Rollen mit hierarchischen Berechtigungen
        self.role_hierarchy = {
            "ADMIN": {
                "inherits": ["POWER_USER", "USER"],
                "permissions": [
                    "system.admin",
                    "users.manage",
                    "settings.modify",
                    "security.audit"
                ]
            },
            "POWER_USER": {
                "inherits": ["USER"],
                "permissions": [
                    "langextract.advanced",
                    "xml.template.create",
                    "documents.bulk_operations",
                    "reports.generate"
                ]
            },
            "USER": {
                "permissions": [
                    "langextract.basic",
                    "xml.generate",
                    "documents.read",
                    "documents.upload",
                    "chat.access"
                ]
            },
            "VIEWER": {
                "permissions": [
                    "documents.read",
                    "chat.access.readonly"
                ]
            }
        }

    async def check_permission(self,
                             user_permissions: List[str],
                             required_permission: str) -> bool:
        """Prüft ob Benutzer erforderliche Berechtigung hat"""

        # Direct permission check
        if required_permission in user_permissions:
            return True

        # Wildcard permission check (z.B. "langextract.*" für "langextract.basic")
        for permission in user_permissions:
            if permission.endswith(".*"):
                permission_prefix = permission[:-2]
                if required_permission.startswith(permission_prefix):
                    return True

        return False

    def require_permission(self, permission: str):
        """Decorator für Endpoint-Berechtigungsprüfung"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract user from request context
                request = kwargs.get('request') or (args[0] if args else None)
                if not request:
                    raise HTTPException(status_code=500, detail="Request context missing")

                user_permissions = getattr(request.state, 'user_permissions', [])

                if not await self.check_permission(user_permissions, permission):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Insufficient permissions. Required: {permission}"
                    )

                return await func(*args, **kwargs)
            return wrapper
        return decorator

# Verwendung in API Endpoints
@router.post("/langextract/sessions")
@permission_service.require_permission("langextract.basic")
async def create_langextract_session(
    session_data: CreateSessionRequest,
    request: Request,
    service: UnifiedLangExtractService = Depends(get_langextract_service)
):
    """Erstellt neue LangExtract Session mit Berechtigungsprüfung"""
    pass

@router.post("/xml-generator/template/create")
@permission_service.require_permission("xml.template.create")
async def create_xml_template(
    template_data: CreateTemplateRequest,
    request: Request,
    service: TemplateEngine = Depends(get_template_engine)
):
    """Erstellt neue XML-Template (nur für POWER_USER+)"""
    pass
```

### 4.5.2 Data Privacy & GDPR Compliance

**Privacy-by-Design Implementation**

```python
class DataPrivacyService:
    """
    GDPR-konforme Datenschutz-Implementierung
    Privacy-by-Design für alle Streamworks-KI Daten
    """

    def __init__(self):
        self.privacy_config = PrivacyConfig(
            data_retention_days=365,           # 1 Jahr Aufbewahrung
            anonymization_delay_days=30,      # 30 Tage bis Anonymisierung
            encryption_algorithm="AES-256-GCM",
            key_rotation_days=90,              # Schlüssel-Rotation alle 90 Tage
            audit_log_retention_days=2555     # 7 Jahre Audit-Logs
        )

        self.pii_detector = PIIDetector()
        self.encryption_service = EncryptionService()

    async def process_user_data(self,
                              data: UserData,
                              processing_purpose: ProcessingPurpose) -> ProcessedUserData:
        """Verarbeitet Benutzerdaten GDPR-konform"""

        # 1. Data Minimization - nur notwendige Daten verarbeiten
        minimized_data = await self._apply_data_minimization(data, processing_purpose)

        # 2. PII Detection & Classification
        pii_analysis = await self.pii_detector.analyze(minimized_data)

        # 3. Encryption of sensitive data
        encrypted_data = await self._encrypt_sensitive_data(
            minimized_data, pii_analysis
        )

        # 4. Consent Verification
        consent_valid = await self._verify_consent(
            data.user_id, processing_purpose
        )
        if not consent_valid:
            raise ConsentError(f"No valid consent for purpose: {processing_purpose}")

        # 5. Processing Log für Audit Trail
        await self._log_processing_activity(
            user_id=data.user_id,
            purpose=processing_purpose,
            data_types=pii_analysis.detected_types,
            legal_basis="consent"
        )

        return ProcessedUserData(
            data=encrypted_data,
            pii_analysis=pii_analysis,
            processing_metadata=ProcessingMetadata(
                purpose=processing_purpose,
                processed_at=datetime.now(),
                retention_until=datetime.now() + timedelta(days=self.privacy_config.data_retention_days)
            )
        )

    async def handle_data_subject_request(self,
                                        request: DataSubjectRequest) -> DataSubjectResponse:
        """Behandelt GDPR Data Subject Requests (Art. 15-22)"""

        user_id = request.user_id
        request_type = request.type

        if request_type == "ACCESS":  # Art. 15 - Right of Access
            return await self._handle_access_request(user_id)

        elif request_type == "RECTIFICATION":  # Art. 16 - Right to Rectification
            return await self._handle_rectification_request(user_id, request.rectification_data)

        elif request_type == "ERASURE":  # Art. 17 - Right to Erasure
            return await self._handle_erasure_request(user_id)

        elif request_type == "PORTABILITY":  # Art. 20 - Right to Data Portability
            return await self._handle_portability_request(user_id, request.export_format)

        elif request_type == "OBJECTION":  # Art. 21 - Right to Object
            return await self._handle_objection_request(user_id, request.processing_purposes)

        else:
            raise ValueError(f"Unknown data subject request type: {request_type}")

    async def _handle_erasure_request(self, user_id: str) -> DataSubjectResponse:
        """Behandelt Right to Erasure Request"""

        # 1. Identify all user data across system
        user_data_locations = await self._identify_user_data(user_id)

        erasure_results = []

        for location in user_data_locations:
            try:
                if location.can_be_erased:
                    # Complete erasure
                    await self._erase_data(location)
                    erasure_results.append(
                        ErasureResult(location=location.name, status="ERASED")
                    )
                else:
                    # Anonymization (wenn Erasure nicht möglich wegen rechtlicher Anforderungen)
                    await self._anonymize_data(location)
                    erasure_results.append(
                        ErasureResult(location=location.name, status="ANONYMIZED",
                                    reason="Legal retention requirements")
                    )
            except Exception as e:
                erasure_results.append(
                    ErasureResult(location=location.name, status="ERROR",
                                error=str(e))
                )

        # 2. Log erasure activity
        await self._log_erasure_activity(user_id, erasure_results)

        return DataSubjectResponse(
            request_type="ERASURE",
            status="COMPLETED",
            results=erasure_results,
            processed_at=datetime.now()
        )

    async def _identify_user_data(self, user_id: str) -> List[UserDataLocation]:
        """Identifiziert alle Speicherorte von Benutzerdaten"""

        locations = []

        # 1. Database Tables mit User-Bezug
        db_locations = [
            UserDataLocation(
                name="users",
                type="database_table",
                can_be_erased=True,
                retention_reason=None
            ),
            UserDataLocation(
                name="langextract_sessions",
                type="database_table",
                can_be_erased=True,
                retention_reason=None
            ),
            UserDataLocation(
                name="chat_messages",
                type="database_table",
                can_be_erased=True,
                retention_reason=None
            ),
            UserDataLocation(
                name="audit_logs",
                type="database_table",
                can_be_erased=False,
                retention_reason="Legal compliance - 7 years retention required"
            )
        ]
        locations.extend(db_locations)

        # 2. Vector Database Collections
        vector_locations = [
            UserDataLocation(
                name="user_documents_embeddings",
                type="vector_collection",
                can_be_erased=True,
                retention_reason=None
            )
        ]
        locations.extend(vector_locations)

        # 3. File Storage
        file_locations = await self._find_user_files(user_id)
        locations.extend(file_locations)

        # 4. Cache & Temporary Storage
        cache_locations = await self._find_user_cache_data(user_id)
        locations.extend(cache_locations)

        return locations
```

### 4.5.3 Input Sanitization & Validation

**Multi-Layer Input Protection**

```python
class InputValidationService:
    """
    Multi-Layer Input Validation & Sanitization
    Schutz vor Injection-Attacken und malicious Input
    """

    def __init__(self):
        self.validation_config = ValidationConfig(
            max_input_length=10000,           # 10KB max Input
            max_file_size_mb=50,              # 50MB max File Upload
            allowed_file_types=["pdf", "txt", "docx", "md"],
            blocked_patterns=self._load_blocked_patterns(),
            sql_injection_patterns=self._load_sql_injection_patterns(),
            xss_patterns=self._load_xss_patterns()
        )

    async def validate_langextract_input(self,
                                       user_input: str,
                                       context: ValidationContext) -> ValidatedInput:
        """Validiert LangExtract User Input gegen Injection-Attacken"""

        # 1. Length Validation
        if len(user_input) > self.validation_config.max_input_length:
            raise ValidationError(f"Input too long. Max: {self.validation_config.max_input_length} chars")

        # 2. SQL Injection Detection
        sql_threats = await self._detect_sql_injection(user_input)
        if sql_threats:
            await self._log_security_threat("SQL_INJECTION_ATTEMPT", context.user_id, sql_threats)
            raise SecurityError("Potentially malicious input detected")

        # 3. XSS Detection
        xss_threats = await self._detect_xss_patterns(user_input)
        if xss_threats:
            await self._log_security_threat("XSS_ATTEMPT", context.user_id, xss_threats)
            raise SecurityError("Cross-site scripting attempt detected")

        # 4. Command Injection Detection
        command_threats = await self._detect_command_injection(user_input)
        if command_threats:
            await self._log_security_threat("COMMAND_INJECTION_ATTEMPT", context.user_id, command_threats)
            raise SecurityError("Command injection attempt detected")

        # 5. Content Sanitization (preserve German characters)
        sanitized_input = await self._sanitize_input(user_input, preserve_german=True)

        # 6. Business Logic Validation
        business_validation = await self._validate_business_context(
            sanitized_input, context
        )

        return ValidatedInput(
            original=user_input,
            sanitized=sanitized_input,
            validation_passed=True,
            business_validation=business_validation,
            validated_at=datetime.now()
        )

    async def _detect_sql_injection(self, input_text: str) -> List[ThreatMatch]:
        """Erkennt SQL Injection Patterns"""

        threats = []
        input_lower = input_text.lower()

        for pattern in self.validation_config.sql_injection_patterns:
            matches = re.finditer(pattern["regex"], input_lower, re.IGNORECASE)
            for match in matches:
                threat = ThreatMatch(
                    type="SQL_INJECTION",
                    pattern=pattern["name"],
                    matched_text=match.group(),
                    position=match.start(),
                    severity=pattern["severity"]
                )
                threats.append(threat)

        return threats

    async def _sanitize_input(self,
                            input_text: str,
                            preserve_german: bool = True) -> str:
        """Sanitization mit deutscher Sprachunterstützung"""

        # HTML Entity Decoding
        sanitized = html.unescape(input_text)

        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
        for char in dangerous_chars:
            if char not in sanitized or not self._is_safe_context(sanitized, char):
                sanitized = sanitized.replace(char, '')

        # Preserve German umlauts and special characters
        if preserve_german:
            german_chars = ['ä', 'ö', 'ü', 'ß', 'Ä', 'Ö', 'Ü']
            # German characters are always preserved

        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())

        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in ['\t', '\n'])

        return sanitized.strip()

class SecurityMiddleware:
    """Security Middleware für FastAPI mit Rate Limiting und Monitoring"""

    def __init__(self):
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000
        )

        self.security_monitor = SecurityMonitor()

    async def __call__(self, request: Request, call_next):
        """Security Middleware Execution"""

        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_id = self._extract_user_id(request)

        try:
            # 1. Rate Limiting
            await self.rate_limiter.check_limits(client_ip, user_id)

            # 2. Request Size Validation
            if hasattr(request, 'content_length') and request.content_length:
                if request.content_length > 50 * 1024 * 1024:  # 50MB limit
                    raise HTTPException(413, "Request too large")

            # 3. Security Headers Validation
            await self._validate_security_headers(request)

            # 4. Request Body Inspection (for POST/PUT)
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._inspect_request_body(request)

            # Execute request
            response = await call_next(request)

            # 5. Add Security Response Headers
            response = await self._add_security_headers(response)

            # 6. Log successful request
            processing_time = time.time() - start_time
            await self.security_monitor.log_request(
                client_ip=client_ip,
                user_id=user_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                processing_time=processing_time
            )

            return response

        except HTTPException as e:
            # Security violation detected
            await self.security_monitor.log_security_violation(
                client_ip=client_ip,
                user_id=user_id,
                violation_type=e.detail,
                request_path=request.url.path,
                status_code=e.status_code
            )
            raise

        except Exception as e:
            # Unexpected error
            await self.security_monitor.log_error(
                client_ip=client_ip,
                user_id=user_id,
                error=str(e),
                request_path=request.url.path
            )
            raise HTTPException(500, "Internal server error")

    async def _add_security_headers(self, response: Response) -> Response:
        """Fügt Security Headers zur Response hinzu"""

        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }

        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value

        return response
```

---

## Fazit Kapitel 4

Dieses Kapitel hat die umfassende **Konzeption und das Design** des Streamworks-KI Systems dargestellt. Die entwickelte Architektur kombiniert **moderne Software-Engineering-Prinzipien** mit **spezialisierten KI-Algorithmen** für eine produktionsreife Self-Service-Lösung.

**Kernbeiträge der Konzeption:**

1. **Enhanced Job Type Detection (88.9% Accuracy)**: Multi-Layer Pattern Matching mit deutscher Sprachoptimierung
2. **Template-basierte XML-Generierung**: Deterministische Alternative zu LLM-basierter Generation
3. **Hybrid RAG-System**: Kombination aus Vector Search und Lexical Search für optimale Relevanz
4. **Privacy-by-Design**: GDPR-konforme Implementierung mit umfassenden Datenschutzmaßnahmen
5. **Enterprise Security**: Multi-Layer Security mit RBAC, Input Validation und Monitoring

Die **Clean Architecture** mit **Domain-Driven Design** ermöglicht hohe Wartbarkeit und Erweiterbarkeit, während die **Event-Driven Communication** zwischen Services für lose Kopplung sorgt.

Das System ist darauf ausgelegt, die **Komplexität der StreamWorks-Automatisierung** durch intelligente KI-Unterstützung zu abstrahieren und gleichzeitig **Enterprise-Grade Security** und **Datenschutz** zu gewährleisten.

**Nächste Schritte**: Kapitel 5 wird die **konkrete Implementierung** dieser Konzepte detailliert dokumentieren, einschließlich Code-Beispiele, Performance-Optimierungen und Integration-Patterns.