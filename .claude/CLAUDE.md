# Streamworks-KI: Claude Code Projektanweisungen

> **Spezialisierte Claude-Anweisungen für das Streamworks-KI RAG System v0.13**
> Enterprise RAG System mit Advanced AI Parameter Extraction & Template-basierter XML-Generierung

---

## 📋 **Projekt-Übersicht v0.13**

**Streamworks-KI** ist ein hochmodernes RAG-System für Enterprise-Umgebungen mit:
- **Backend**: FastAPI mit 120+ Python-Dateien in modularer Service-Architektur
- **Frontend**: Next.js 15 mit 600+ TypeScript-Dateien
- **Core Features**:
  - LangExtract Parameter Extraction System (88.9% Accuracy)
  - Template-basierte XML-Generierung mit Jinja2
  - Knowledge Graph & Temporal Memory System
  - JWT Authentication & Role Management
  - RAG-basierte Fragebeantwortung

---

## 🏗️ **Enhanced Backend-Architektur (v0.13)**

### AI-Services (Neu: Enhanced Parameter Extraction)
```
backend/services/ai/
├── langextract/                   # → LangExtract System (Hauptfeature)
│   ├── unified_langextract_service.py      # Haupt-LangExtract Service
│   ├── session_persistence_service.py      # Session Management
│   ├── mcp_session_persistence_service.py  # MCP Persistence
│   └── sqlalchemy_session_persistence_service.py
├── enhanced_job_type_detector.py           # 88.9% Accuracy Job Detection
├── enhanced_unified_parameter_extractor.py # Enhanced Parameter Extraction
├── enterprise_parameter_engine.py          # Enterprise Parameter Logic
├── parameter_extraction_ai.py              # Parameter AI Core
├── parameter_state_manager.py              # State Management
└── intelligent_dialog_manager.py           # Dialog Management
```

### XML-Generation Services (Template-basiert)
```
backend/services/xml_generation/
├── template_engine.py            # Jinja2 Template Engine
└── parameter_mapper.py           # Intelligente Parameter-Mappings
```

### Knowledge Graph Services (Neu)
```
backend/services/knowledge_graph/
├── unified_knowledge_service.py    # Haupt-Knowledge Service
├── context_memory_system.py        # Kontext-Memory
├── entity_extraction_pipeline.py   # Entity Extraction
├── temporal_graph_service.py       # Zeitbasierte Graphen
└── monitoring_service.py           # Graph Monitoring
```

### Chat XML Services (Spezialisiert)
```
backend/services/chat_xml/
├── chat_session_service.py       # XML Chat Sessions
├── dialog_manager.py             # Dialog Management
├── parameter_extractor.py        # Parameter Extraction
└── xml_chat_validator.py         # XML Validation
```

### Authentication Services (Enterprise-Ready)
```
backend/services/auth/
├── auth_service.py               # Authentication Logic
├── jwt_service.py                # JWT Token Management
└── permission_service.py         # Role-based Permissions
```

### API Router (Enhanced Endpoints)
```
backend/routers/
├── langextract_chat.py           # LangExtract Chat API
├── chat_xml_unified.py           # Unified XML Chat
├── xml_generator.py              # Template XML Generation
├── enhanced_chat_xml.py          # Enhanced Chat XML
├── auth.py                       # Authentication Endpoints
├── chat_rag_test.py              # RAG Chat Testing
└── documents/                    # Document Management
    ├── crud.py                   # CRUD Operations
    ├── analytics.py              # Document Analytics
    ├── bulk_operations.py        # Bulk Operations
    └── chunks.py                 # Document Chunking
```

---

## 🎯 **Frontend-Architektur v0.13**

### LangExtract Interface (Hauptfeature)
```
frontend/src/components/langextract-chat/
├── LangExtractInterface.tsx       # Haupt-LangExtract UI
├── components/
│   ├── LangExtractSessionSidebar.tsx    # Session Management
│   ├── ParameterOverview.tsx            # Parameter Display
│   ├── SmartSuggestions.tsx             # AI Suggestions
│   └── XMLGenerationPanel.tsx           # XML Generation UI
└── hooks/
    └── useLangExtractChat.ts             # LangExtract Hooks
```

### Enhanced Chat Components
```
frontend/src/components/chat/
├── ModernChatInterface.tsx        # Modern Chat UI
├── CompactChatInterface.tsx       # Compact Chat Widget
├── FloatingChatWidget.tsx         # Floating Chat
├── EnterpriseResponseFormatter.tsx # Enterprise Formatting
├── EnterpriseInputArea.tsx        # Enhanced Input
├── ChatProvider.tsx               # Chat Context Provider
└── RAGMetrics.tsx                 # RAG Performance Metrics
```

### App Router Structure (Erweitert)
```
frontend/src/app/
├── langextract/                  # → LangExtract Interface (/langextract)
│   └── page.tsx                 # LangExtract Hauptseite
├── xml/                         # → XML Wizard (/xml)
│   └── page.tsx                 # XML Generation
├── chat/                        # → Chat Interface (/chat)
│   └── page.tsx                 # Chat Hauptseite
├── auth/                        # → Authentication
│   ├── login/page.tsx           # Login Seite
│   └── register/page.tsx        # Registration Seite
├── dashboard/                   # → System Dashboard
│   └── page.tsx                 # Dashboard
└── documents/                   # → Document Management
    └── [id]/page.tsx            # Document Details
```

---

## ⚙️ **Entwicklungsrichtlinien v0.13**

### LangExtract System Patterns (Neu)
```python
# LangExtract Service Pattern
class UnifiedLangExtractService:
    def __init__(self,
                 job_detector: EnhancedJobTypeDetector,
                 parameter_extractor: EnhancedUnifiedParameterExtractor,
                 session_service: SessionPersistenceService):
        self.job_detector = job_detector
        self.parameter_extractor = parameter_extractor
        self.session_service = session_service

    async def process_message(self, session_id: str, message: str):
        # 1. Job Type Detection (88.9% Accuracy)
        job_type = await self.job_detector.detect_job_type(message)

        # 2. Parameter Extraction
        parameters = await self.parameter_extractor.extract_parameters(
            message, job_type
        )

        # 3. Session Persistence
        await self.session_service.update_session(session_id, parameters)

        return {
            "detected_job_type": job_type,
            "detection_confidence": confidence,
            "extracted_parameters": parameters
        }
```

### Enhanced Job Type Detection (88.9% Accuracy)
```python
# Multi-Layer Pattern Matching
class EnhancedJobTypeDetector:
    def __init__(self):
        self.patterns = {
            "FILE_TRANSFER": [
                r"(?:datentransfer|übertragung|transfer).*(?:von|nach)",
                r"(?:dateien|files).*(?:zwischen|between)",
                r"(?:kopieren|copy).*(?:server|agent)"
            ],
            "SAP": [
                r"sap\s+(?:system|export|import|report)",
                r"(?:gt123|pa1|pt1|pd1)(?:_(?:prd|dev|tst))?",
                r"(?:ztv|rsus|rfc)[a-zA-Z0-9_]*"
            ],
            "STANDARD": [
                r"python\s+[^\s]+\.py",
                r"(?:script|ausführen|execute)",
                r"(?:java|node|bash)\s+"
            ]
        }

    async def detect_job_type(self, message: str) -> Dict[str, Any]:
        # Multi-layer detection with confidence scoring
        confidence_scores = await self._calculate_confidence(message)
        return self._select_best_match(confidence_scores)
```

### Template-basierte XML Generation
```python
# XML Template Engine Pattern
class TemplateEngine:
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader('templates/xml_templates/'),
            enable_async=True
        )

    async def generate_xml(self, job_type: str, parameters: Dict) -> str:
        # 1. Load job-specific template
        template = await self.jinja_env.get_template(f"{job_type.lower()}_template.xml")

        # 2. Map parameters with intelligent field mapping
        mapped_params = await self.parameter_mapper.map_parameters(
            parameters, job_type
        )

        # 3. Render XML with auto-generated defaults
        xml_content = await template.render_async(**mapped_params)

        return xml_content
```

### Frontend LangExtract Hooks
```typescript
// LangExtract Chat Hook
export const useLangExtractChat = (sessionId: string) => {
  const [messages, setMessages] = useState<LangExtractMessage[]>([])

  const processMessage = useMutation({
    mutationFn: async (message: string) => {
      const response = await api.post(`/api/langextract/sessions/${sessionId}/messages`, {
        message,
        timestamp: new Date().toISOString()
      })
      return response.data
    },
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        content: data.ai_response,
        job_type: data.detected_job_type,
        confidence: data.detection_confidence,
        parameters: data.extracted_parameters
      }])
    }
  })

  const generateXML = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/api/xml-generator/template/generate`, {
        session_id: sessionId
      })
      return response.data
    }
  })

  return { messages, processMessage, generateXML }
}
```

---

## 📁 **Wichtige Dateipfade v0.13**

### Backend Key Files (Aktualisiert)
- `backend/main.py` - FastAPI-Anwendung mit allen Routern
- `backend/services/ai/langextract/unified_langextract_service.py` - **Haupt-LangExtract Service**
- `backend/services/ai/enhanced_job_type_detector.py` - **88.9% Accuracy Job Detection**
- `backend/services/xml_generation/template_engine.py` - **Template-basierte XML-Generierung**
- `backend/routers/langextract_chat.py` - **LangExtract API Endpoints**
- `backend/routers/xml_generator.py` - **XML Generation API**
- `backend/templates/xml_templates/` - **XML Template Library**

### Frontend Key Files (Aktualisiert)
- `frontend/src/components/langextract-chat/LangExtractInterface.tsx` - **Haupt-LangExtract UI**
- `frontend/src/app/langextract/page.tsx` - **LangExtract App Route**
- `frontend/src/components/chat/CompactChatInterface.tsx` - **Neue Compact Chat**
- `frontend/src/components/chat/FloatingChatWidget.tsx` - **Floating Chat Widget**
- `frontend/src/components/layout/AppLayout.tsx` - **App Layout mit Navigation**

---

## 🔧 **Development Commands v0.13**

### Backend Development
```bash
cd backend
python main.py                    # Start server (alle Services aktiv)
pip install -r requirements.txt  # Install dependencies (120+ packages)
pytest tests/test_langextract.py # Test LangExtract System
pytest tests/test_xml_generation.py # Test XML Generation
```

### Frontend Development
```bash
cd frontend
npm run dev                      # Start dev server (http://localhost:3000)
npm run dev:clean               # Start with cache clear (wichtig bei Problemen)
npm run build                   # Production build
npm run type-check              # TypeScript validation
npm run lint                    # ESLint validation
```

---

## 🚨 **Wichtige Coding-Regeln v0.13**

### 1. **Respektiere die Enhanced AI Architecture**
- **LangExtract Features** → verwende `services/ai/langextract/`
- **Parameter Extraction** → verwende `services/ai/enhanced_*`
- **XML Generation** → verwende `services/xml_generation/`
- **Knowledge Graph** → verwende `services/knowledge_graph/`
- **Authentication** → verwende `services/auth/`

### 2. **LangExtract API Patterns**
```python
# Immer Enhanced Detection verwenden
async def process_langextract_message(session_id: str, message: str):
    service = get_unified_langextract_service()

    # Multi-layer job detection
    result = await service.process_message(session_id, message)

    return {
        "detected_job_type": result.job_type,
        "detection_confidence": result.confidence,  # 88.9% accuracy
        "detection_method": result.method,
        "alternative_job_types": result.alternatives,
        "extracted_parameters": result.parameters,
        "completion_percentage": result.completion
    }
```

### 3. **Template-basierte XML Generation**
```python
# Immer Template Engine verwenden (nicht LLM-basiert)
async def generate_xml_from_session(session_id: str):
    # 1. Get session parameters
    session = await session_service.get_session(session_id)

    # 2. Use template engine (nicht LLM!)
    xml_content = await template_engine.generate_xml(
        job_type=session.detected_job_type,
        parameters=session.extracted_parameters
    )

    return {
        "xml_content": xml_content,
        "template_used": f"{session.detected_job_type.lower()}_template.xml",
        "parameter_count": len(session.extracted_parameters)
    }
```

### 4. **Frontend LangExtract Integration**
```typescript
// LangExtract Interface Pattern
export default function LangExtractInterface() {
  const { data: session } = useQuery({
    queryKey: ['langextract-session', sessionId],
    queryFn: () => fetchLangExtractSession(sessionId)
  })

  const processMessage = useMutation({
    mutationFn: processLangExtractMessage,
    onSuccess: (data) => {
      // Handle enhanced detection response
      if (data.detection_confidence >= 0.90) {
        toast.success(`Job Type detected: ${data.detected_job_type} (${Math.round(data.detection_confidence * 100)}%)`)
      } else {
        toast.warning(`Low confidence: ${data.detected_job_type} (${Math.round(data.detection_confidence * 100)}%)`)
      }
    }
  })

  return (
    <div className="langextract-interface">
      <LangExtractSessionSidebar session={session} />
      <ParameterOverview parameters={session?.extracted_parameters} />
      <SmartSuggestions jobType={session?.detected_job_type} />
    </div>
  )
}
```

---

## 🎯 **Performance Metriken v0.13**

### Enhanced Parameter Extraction System
- **Job Type Detection Accuracy**: **88.9%** (Dramatische Verbesserung von 67%)
- **False Positives Reduction**: **70%** weniger Fehlklassifikationen
- **German Language Support**: **Excellent** - Optimiert für deutsche StreamWorks-Eingaben
- **Response Time**: Sub-2-Sekunden für alle Job Types
- **Confidence Reporting**: Präzise Confidence-Scores für Transparenz

### Template XML Generation System
- **Template Rendering**: Sub-Sekunden Performance mit Caching
- **Parameter Mapping**: Intelligente Feld-Mappings mit Fuzzy-Matching
- **Template Library**: 3 produktionsreife Templates (STANDARD, FILE_TRANSFER, SAP)
- **Auto-Generation**: Automatische Generierung fehlender Parameter

### Knowledge Graph Performance
- **Entity Extraction**: Real-time Entity-Erkennung
- **Temporal Memory**: Kontext-basierte Erinnerung über Sessions hinweg
- **Graph Monitoring**: Performance-Monitoring für Graph-Operationen

---

## 🔄 **LangExtract Spezifika (Hauptfeature)**

### Backend Integration
```python
# Enhanced LangExtract Router
@router.post("/sessions/{session_id}/messages")
async def process_message(
    session_id: str,
    message_request: MessageRequest,
    service: UnifiedLangExtractService = Depends(get_unified_langextract_service)
):
    result = await service.process_message(session_id, message_request.message)

    # Enhanced response mit confidence & alternatives
    return {
        "ai_response": result.ai_response,
        "detected_job_type": result.detected_job_type,
        "detection_confidence": result.detection_confidence,
        "detection_method": result.detection_method,
        "alternative_job_types": result.alternative_job_types,
        "extracted_parameters": result.extracted_parameters,
        "completion_percentage": result.completion_percentage
    }
```

### Frontend Integration
- **Route**: `/langextract` - Haupt-LangExtract Interface
- **Komponenten**: Modular aufgebaute LangExtract UI
- **Hooks**: `useLangExtractChat` für State Management
- **Features**: Real-time Parameter Extraction mit Confidence Display

---

## 💡 **Häufige Aufgaben v0.13**

### Neues LangExtract Feature hinzufügen
1. **Backend**: Erweitere `services/ai/langextract/` Module
2. **Enhanced Detection**: Nutze `enhanced_job_type_detector.py` für Job-Type Detection
3. **Parameter Extraction**: Verwende `enhanced_unified_parameter_extractor.py`
4. **Frontend**: Erweitere `components/langextract-chat/` Komponenten
5. **API**: Neue Endpoints in `routers/langextract_chat.py`

### Template-basierte XML-Generation erweitern
1. **Templates**: Neue XML-Templates in `backend/templates/xml_templates/`
2. **Engine**: Erweitere `services/xml_generation/template_engine.py`
3. **Mapping**: Neue Parameter-Mappings in `parameter_mapper.py`
4. **Testing**: Test Template-Rendering mit realen Parametern

### Knowledge Graph Features hinzufügen
1. **Backend**: Erweitere `services/knowledge_graph/` Module
2. **Entity Extraction**: Nutze `entity_extraction_pipeline.py`
3. **Memory**: Erweitere `context_memory_system.py`
4. **Integration**: Verbinde mit LangExtract System

### Authentication & Authorization erweitern
1. **Backend**: Erweitere `services/auth/` Module
2. **JWT**: Nutze `jwt_service.py` für Token Management
3. **Permissions**: Erweitere `permission_service.py`
4. **Frontend**: Auth-Komponenten in `components/auth/`

---

## 🎉 **System Status: Production Ready v0.13**

### ✅ **Erfolgreich implementiert:**
- **LangExtract Parameter Extraction**: 88.9% Accuracy, Live-Production aktiv
- **Template-basierte XML-Generierung**: Produktionsreife Templates
- **Enhanced Job Type Detection**: Multi-Layer Pattern Matching
- **Knowledge Graph System**: Kontext-Memory & Entity Extraction
- **Authentication System**: JWT-basiert mit Role Management
- **Modern Frontend**: Next.js 15 mit TypeScript & TailwindCSS

### 🚀 **Performance Highlights:**
- **88.9% Job Detection Accuracy** - Weit über dem Ziel von 80%
- **70% Reduction in False Positives** - Dramatische Verbesserung
- **Sub-2-Second Response Times** - Optimierte Performance
- **German Language Optimized** - Speziell für StreamWorks-Kontext
- **Template-First Approach** - Reliable, nicht LLM-abhängig

**🎯 Das Enhanced Streamworks-KI System v0.13 ist vollständig produktionsreif und arbeitet erfolgreich in der Live-Umgebung!**