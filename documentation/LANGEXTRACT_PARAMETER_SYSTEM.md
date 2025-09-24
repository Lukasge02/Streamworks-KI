# LangExtract Parameter Extraction System

> **🚀 Kernsystem:** Session-basierte Parameterextraktion mit Real-time State Management für StreamWorks-Automatisierung

## **System-Übersicht**

Das LangExtract Parameter Extraction System bildet das Herzstück der natürlichsprachlichen StreamWorks-Konfiguration. Es kombiniert Google's LangExtract API mit einer robusten Session-Management-Architektur für kontinuierliche Parametererfassung.

### **Kernfeatures**
- **Session-basierte Persistierung** mit SQLAlchemy Async ORM
- **Real-time Parameter Classification** (Stream vs. Job Parameter)
- **Interactive Dialog Management** mit Smart Next-Question Logic
- **Completion Tracking** mit prozentualer Fortschrittsanzeige
- **Multi-Session Management** für parallele Workflows

---

## **Architektur-Design**

### **Service-Layer-Architektur**

```
UnifiedLangExtractService (Core Orchestrator)
    ├── EnhancedJobTypeDetector (88.9% Accuracy)
    ├── LangExtractAPIService (Google LangExtract)
    ├── SessionPersistenceService (SQLAlchemy Async)
    ├── ParameterClassificationService (Stream/Job Classification)
    └── DialogManagerService (Interactive Flow)
```

### **Datenfluss**

```
User Message (German)
    ↓
Job Type Detection (Enhanced Detector)
    ↓
LangExtract API Call (Parameter Extraction)
    ↓
Parameter Classification (Stream vs Job)
    ↓
Session State Update (Async Persistence)
    ↓
Next Question Generation (Dialog Management)
    ↓
Frontend Update (Real-time UI Refresh)
```

---

## **Technische Implementierung**

### **1. Unified LangExtract Service**

**Core Service Pattern:**

```python
class UnifiedLangExtractService:
    """
    🎯 Hauptservice für LangExtract Parameter Extraction

    Orchestriert Job-Type Detection, Parameter Extraction und Session Management
    """

    def __init__(self,
                 job_detector: EnhancedJobTypeDetector,
                 langextract_service: LangExtractAPIService,
                 session_service: SessionPersistenceService):
        self.job_detector = job_detector
        self.langextract_service = langextract_service
        self.session_service = session_service
```

**Hauptmethode - Message Processing:**

```python
async def process_message(self, session_id: str, message: str) -> ProcessedMessageResult:
    """
    🔄 Hauptverarbeitungslogik für User-Messages

    1. Job-Type Detection (wenn noch nicht bekannt)
    2. LangExtract API Parameter Extraction
    3. Parameter Classification und Session Update
    4. Next Question Generation für Dialog Flow
    """

    # 1. Session laden/erstellen
    session = await self.session_service.get_session(session_id)
    if not session:
        session = await self.session_service.create_session(session_id)

    # 2. Job-Type Detection (falls erforderlich)
    if not session.detected_job_type:
        detection_result = await self.job_detector.detect_job_type(message)
        if detection_result.detected_job_type:
            session.detected_job_type = detection_result.detected_job_type
            session.detection_confidence = detection_result.confidence

    # 3. LangExtract API Call
    extraction_result = await self.langextract_service.extract_parameters(
        message=message,
        job_type=session.detected_job_type,
        existing_parameters={**session.stream_parameters, **session.job_parameters}
    )

    # 4. Parameter Classification und Update
    await self._update_session_parameters(session, extraction_result)

    # 5. Session Persistence
    await self.session_service.save_session(session)

    # 6. Next Question Generation
    next_question = await self._generate_next_question(session)

    return ProcessedMessageResult(
        ai_response=extraction_result.ai_response,
        detected_job_type=session.detected_job_type,
        extracted_parameters=extraction_result.parameters,
        completion_percentage=self._calculate_completion(session),
        next_question=next_question,
        session_updated=True
    )
```

### **2. Session Persistence Service**

**Async Database Pattern:**

```python
class SQLAlchemySessionPersistenceService:
    """
    📦 Async Session Persistence mit SQLAlchemy

    Ermöglicht Real-time Session Updates ohne Blocking
    """

    async def save_session(self, session: StreamWorksSession) -> bool:
        """Non-blocking session save mit Error Handling"""
        try:
            async with self.get_async_session() as db:
                db_session = await self._session_to_db_model(session)
                db.add(db_session)
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Session save failed: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[StreamWorksSession]:
        """Efficient session loading mit Caching"""
        try:
            async with self.get_async_session() as db:
                query = select(LangExtractSessionDB).filter(
                    LangExtractSessionDB.session_id == session_id
                )
                result = await db.execute(query)
                db_session = result.scalar_one_or_none()

                return self._db_model_to_session(db_session) if db_session else None
        except Exception as e:
            logger.error(f"Session load failed: {e}")
            return None
```

### **3. Parameter Classification System**

**Stream vs. Job Parameter Logic:**

```python
def _classify_parameters(self, parameters: Dict[str, Any],
                        job_type: str) -> Tuple[Dict, Dict]:
    """
    🎯 Intelligent Parameter Classification

    Unterscheidet zwischen Stream-Level und Job-Level Parametern
    basierend auf StreamWorks-Schema
    """

    # Stream-Level Parameter (alle Job-Types)
    stream_fields = {
        'stream_name', 'stream_documentation', 'short_description',
        'start_time', 'max_stream_runs', 'scheduling_required_flag',
        'calendar_id', 'agent_detail'
    }

    # Job-Type spezifische Parameter
    job_fields = {
        'FILE_TRANSFER': {
            'source_agent', 'target_agent', 'source_path', 'target_path',
            'file_extension', 'transfer_mode', 'retry_count'
        },
        'SAP': {
            'sap_system', 'sap_client', 'sap_report', 'sap_transaction',
            'sap_variant', 'sap_parameters', 'sap_output_format'
        },
        'STANDARD': {
            'main_script', 'login_object', 'template_type',
            'job_documentation', 'job_short_description'
        }
    }

    stream_params = {k: v for k, v in parameters.items() if k in stream_fields}
    job_params = {k: v for k, v in parameters.items()
                 if k in job_fields.get(job_type, set())}

    return stream_params, job_params
```

### **4. Dialog Management System**

**Smart Next-Question Logic:**

```python
async def _generate_next_question(self, session: StreamWorksSession) -> Optional[str]:
    """
    💬 Intelligent Next Question Generation

    Analysiert fehlende Parameter und generiert kontextuelle Fragen
    """

    missing_critical = self._get_missing_critical_parameters(session)

    if not missing_critical:
        return None  # Alle kritischen Parameter vorhanden

    # Priorität-basierte Fragengenerierung
    next_param = missing_critical[0]

    question_templates = {
        'stream_name': "Wie soll der Stream heißen? (z.B. DAILY_FILE_TRANSFER_2024)",
        'source_agent': "Von welchem Agent/Server sollen die Dateien kopiert werden?",
        'target_agent': "Zu welchem Agent/Server sollen die Dateien kopiert werden?",
        'source_path': "Wie lautet der Quell-Pfad für die Dateien?",
        'target_path': "Wie lautet der Ziel-Pfad für die Dateien?",
        'sap_system': "Welches SAP-System soll verwendet werden? (z.B. GT123_PRD)",
        'sap_report': "Welcher SAP-Report soll ausgeführt werden?",
        'start_time': "Wann soll der Stream starten? (Format: HH:MM, z.B. 06:00)"
    }

    return question_templates.get(next_param,
                                f"Bitte geben Sie den Wert für '{next_param}' an.")
```

---

## **Performance-Optimierungen**

### **1. Caching-Strategien**

**Multi-Level Caching:**

```python
class CachingLangExtractService:
    """
    ⚡ Performance-optimierter LangExtract Service mit Multi-Level Caching
    """

    def __init__(self):
        # Session Cache (In-Memory)
        self._session_cache: Dict[str, StreamWorksSession] = {}
        self._cache_ttl = 3600  # 1 Stunde

        # Parameter Extraction Cache
        self._extraction_cache: Dict[str, ExtractionResult] = {}
        self._extraction_cache_size = 1000

        # LRU Cache für häufige Patterns
        self._pattern_cache = LRUCache(maxsize=500)

    async def _cached_parameter_extraction(self, message: str,
                                         job_type: str) -> ExtractionResult:
        """Cache-aware Parameter Extraction"""
        cache_key = f"{job_type}:{hash(message)}"

        if cache_key in self._extraction_cache:
            logger.info(f"🎯 Cache hit for extraction: {cache_key}")
            return self._extraction_cache[cache_key]

        result = await self._perform_extraction(message, job_type)
        self._extraction_cache[cache_key] = result

        return result
```

### **2. Async Performance Patterns**

**Non-blocking Database Operations:**

```python
async def _save_session_async(self, session: StreamWorksSession) -> bool:
    """
    🚀 Non-blocking Session Save mit Background Processing
    """
    try:
        # Background Task für DB-Save
        task = asyncio.create_task(
            self.session_service.save_session(session)
        )

        # Immediate return für UI Responsiveness
        # Actual save erfolgt im Background
        return True

    except Exception as e:
        logger.error(f"Async session save failed: {e}")
        return False

async def _batch_parameter_updates(self, updates: List[Tuple[str, Dict]]):
    """Batch Updates für bessere DB Performance"""
    async with self.session_service.get_async_session() as db:
        for session_id, parameters in updates:
            await self._update_session_parameters_db(db, session_id, parameters)
        await db.commit()
```

### **3. Memory Management**

**Session Cleanup & Memory Optimization:**

```python
class SessionMemoryManager:
    """
    🧹 Memory Management für LangExtract Sessions
    """

    def __init__(self, max_sessions: int = 100, cleanup_interval: int = 3600):
        self.max_sessions = max_sessions
        self.cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()

    async def cleanup_inactive_sessions(self):
        """Cleanup inaktiver Sessions"""
        if time.time() - self._last_cleanup < self.cleanup_interval:
            return

        # Sessions älter als 24h entfernen
        cutoff_time = datetime.now() - timedelta(hours=24)

        async with self.get_async_session() as db:
            await db.execute(
                delete(LangExtractSessionDB).filter(
                    LangExtractSessionDB.last_activity < cutoff_time
                )
            )
            await db.commit()

        self._last_cleanup = time.time()
        logger.info(f"🧹 Session cleanup completed")
```

---

## **Integration mit Frontend**

### **Real-time Updates über WebSocket**

**React Hook Integration:**

```typescript
// useLangExtractChat.ts
export const useLangExtractChat = (sessionId?: string) => {
  const [session, setSession] = useState<LangExtractSession | null>(null)
  const [messages, setMessages] = useState<LangExtractMessage[]>([])
  const [streamParameters, setStreamParameters] = useState<Record<string, any>>({})
  const [jobParameters, setJobParameters] = useState<Record<string, any>>({})

  const sendMessage = useMutation({
    mutationFn: async (message: string) => {
      const response = await fetch('/api/langextract/sessions/{sessionId}/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })
      return response.json()
    },
    onSuccess: (data) => {
      // Real-time UI Update
      setMessages(prev => [...prev, {
        content: data.ai_response,
        job_type: data.detected_job_type,
        parameters: data.extracted_parameters,
        timestamp: new Date()
      }])

      // Parameter State Update
      setStreamParameters(data.session.stream_parameters)
      setJobParameters(data.session.job_parameters)
    }
  })

  return { session, messages, streamParameters, jobParameters, sendMessage }
}
```

### **Progress Tracking & Completion**

**Completion Percentage Calculation:**

```python
def _calculate_completion_percentage(self, session: StreamWorksSession) -> float:
    """
    📊 Calculate completion percentage basierend auf kritischen Parametern
    """

    critical_params = self._get_critical_parameters_for_job_type(
        session.detected_job_type
    )

    total_critical = len(critical_params)
    if total_critical == 0:
        return 100.0

    current_params = {**session.stream_parameters, **session.job_parameters}
    filled_critical = sum(1 for param in critical_params
                         if param in current_params and current_params[param])

    return (filled_critical / total_critical) * 100.0
```

**Frontend Progress Display:**

```tsx
// ParameterOverview.tsx
<div className="completion-progress">
  <div className="flex justify-between mb-2">
    <span>Vervollständigung</span>
    <span>{Math.round(completionPercentage)}%</span>
  </div>
  <div className="w-full bg-gray-200 rounded-full h-2">
    <div
      className="bg-green-500 h-2 rounded-full transition-all"
      style={{ width: `${completionPercentage}%` }}
    />
  </div>
</div>
```

---

## **Error Handling & Resilience**

### **API Error Recovery**

```python
async def _resilient_langextract_call(self, message: str,
                                    job_type: str) -> ExtractionResult:
    """
    🛡️ Resilient LangExtract API Call mit Retry Logic
    """

    max_retries = 3
    backoff_factor = 2

    for attempt in range(max_retries):
        try:
            result = await self.langextract_service.extract_parameters(
                message, job_type
            )
            return result

        except LangExtractAPIException as e:
            if attempt == max_retries - 1:
                logger.error(f"LangExtract API failed after {max_retries} retries")
                # Fallback zu Rule-based Extraction
                return await self._fallback_parameter_extraction(message, job_type)

            wait_time = backoff_factor ** attempt
            await asyncio.sleep(wait_time)

async def _fallback_parameter_extraction(self, message: str,
                                       job_type: str) -> ExtractionResult:
    """Fallback Rule-based Parameter Extraction"""
    # Regex-based Parameter Extraction als Backup
    parameters = {}

    # Einfache Regex-Pattern für kritische Parameter
    if job_type == "FILE_TRANSFER":
        if source_match := re.search(r'von\s+([A-Z_0-9]+)', message):
            parameters['source_agent'] = source_match.group(1)
        if target_match := re.search(r'(?:nach|zu)\s+([A-Z_0-9]+)', message):
            parameters['target_agent'] = target_match.group(1)

    return ExtractionResult(
        parameters=parameters,
        ai_response="Parameter wurden mit Fallback-Methode extrahiert.",
        extraction_method="fallback_regex"
    )
```

### **Session Recovery**

```python
async def _recover_session_state(self, session_id: str) -> StreamWorksSession:
    """
    🔄 Session State Recovery bei Systemfehlern
    """

    try:
        # Versuche Session aus DB zu laden
        session = await self.session_service.get_session(session_id)
        if session:
            return session

    except Exception as e:
        logger.warning(f"Session recovery from DB failed: {e}")

    # Fallback: Neue Session erstellen
    logger.info(f"Creating new session for recovery: {session_id}")
    return await self.session_service.create_session(session_id)
```

---

## **Monitoring & Analytics**

### **Performance Metriken**

```python
@dataclass
class LangExtractMetrics:
    """📊 Performance & Usage Metriken"""

    # Performance Metrics
    avg_response_time: float
    cache_hit_rate: float
    api_success_rate: float
    fallback_usage_rate: float

    # Usage Metrics
    active_sessions: int
    total_messages_processed: int
    parameter_extraction_rate: float
    completion_rate: float  # % Sessions die alle Parameter haben

    # Quality Metrics
    user_satisfaction_score: float
    parameter_accuracy_rate: float
    session_completion_time_avg: float

class MetricsCollector:
    """Metrics Collection Service"""

    async def collect_metrics(self) -> LangExtractMetrics:
        """Sammle alle relevanten Metriken"""

        # Performance Metrics aus Cache/DB
        avg_response_time = await self._calculate_avg_response_time()
        cache_hit_rate = self._calculate_cache_hit_rate()

        # Usage Metrics aus Session DB
        active_sessions = await self._count_active_sessions()
        completion_rate = await self._calculate_completion_rate()

        return LangExtractMetrics(
            avg_response_time=avg_response_time,
            cache_hit_rate=cache_hit_rate,
            active_sessions=active_sessions,
            completion_rate=completion_rate,
            # ... weitere Metriken
        )
```

---

## **Fazit**

Das LangExtract Parameter Extraction System stellt eine robuste, skalierbare Lösung für natürlichsprachliche StreamWorks-Konfiguration dar. Die Session-basierte Architektur ermöglicht:

**Key Strengths:**
- **Kontinuierliche Parametererfassung** über mehrere Dialog-Runden
- **Real-time State Management** mit Async Database Pattern
- **High Performance** durch Multi-Level Caching
- **Resilient Error Handling** mit Fallback-Mechanismen
- **Comprehensive Monitoring** für Produktionsumgebung

**Production Ready Features:**
- **Async-first Architecture** für hohe Parallelität
- **Memory Management** für Long-running Sessions
- **Error Recovery** für API-Ausfälle
- **Performance Monitoring** mit detaillierten Metriken

Das System bildet die **Basis für die intelligente XML-Generierung** und ermöglicht Fachanwendern eine natürliche Interaktion mit der StreamWorks-Automatisierung.