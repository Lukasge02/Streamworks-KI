# StreamWorks-KI - Technische Dokumentation v3.0

## 🎯 Projekt-Übersicht

**StreamWorks-KI** ist eine moderne Full-Stack Web-Anwendung zur intelligenten Automatisierung von StreamWorks Workloads. Das System kombiniert Retrieval-Augmented Generation (RAG), Mistral 7B LLM und erweiterte Features wie intelligente Suche und Conversation Memory für eine optimale Benutzererfahrung.

### 🏆 Kernfunktionen

- **🧠 Intelligente Q&A**: RAG-basierte Antworten mit Mistral 7B und erweiterte Suchfunktionen
- **🔍 Smart Search**: Synonym-basierte Suche mit Kontext-Erweiterung für bessere Ergebnisse
- **💬 Conversation Memory**: Persistente Chat-Sessions mit Konversations-Kontext
- **📤 Batch Upload**: Mehrere Dateien gleichzeitig mit Progress-Tracking verarbeiten
- **🔄 TXT zu MD Konvertierung**: Automatische Optimierung für bessere RAG-Performance
- **🌊 XML Stream Generator**: KI-gestützte StreamWorks XML-Erstellung
- **📊 Advanced Monitoring**: Umfassende Metriken und Performance-Überwachung

## 🏗️ System-Architektur

### High-Level Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                     StreamWorks-KI System                      │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript)                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │   Chat UI   │ │ Training    │ │ Stream      │              │
│  │   + Memory  │ │ Data Mgmt   │ │ Generator   │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│  Backend API (FastAPI)                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Chat API    │ │ Search API  │ │ Training    │              │
│  │ + Conv.     │ │ + Intent    │ │ API         │              │
│  │ Memory      │ │ Analysis    │ │             │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│  AI Services Layer                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ RAG Service │ │ Intelligent │ │ Mistral 7B  │              │
│  │ + ChromaDB  │ │ Search      │ │ LLM Service │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ SQLite DB   │ │ Vector DB   │ │ File        │              │
│  │ (Metadata)  │ │ (ChromaDB)  │ │ Storage     │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 🔧 Tech Stack

**Frontend:**
- **React 18** + **TypeScript** - Moderne UI-Entwicklung
- **Tailwind CSS** - Utility-first CSS Framework
- **Zustand** - Leichtgewichtiges State Management
- **Lucide Icons** - Moderne Icon-Bibliothek
- **React Dropzone** - Drag & Drop File Upload

**Backend:**
- **FastAPI** - High-Performance Python Web Framework
- **SQLAlchemy** (async) - Database ORM mit async Support
- **Pydantic** - Data Validation und Serialization
- **SQLite** - Lightweight Database für Metadaten

**AI/ML Stack:**
- **Mistral 7B-Instruct** - Large Language Model via Ollama
- **ChromaDB** - Vector Database für Embeddings
- **LangChain** - Framework für LLM Applications
- **Sentence-Transformers** - Text Embeddings (`all-MiniLM-L6-v2`)

**Infrastructure:**
- **Docker** (optional) - Containerization
- **Uvicorn** - ASGI Server für FastAPI
- **CORS** - Cross-Origin Resource Sharing

## 📁 Projekt-Struktur

```
StreamWorks-KI/
├── frontend/                    # React Frontend
│   ├── src/
│   │   ├── components/         # React Components
│   │   │   ├── Chat/          # Chat Interface + Memory
│   │   │   ├── TrainingData/  # File Management + Batch Upload
│   │   │   └── StreamGenerator/ # XML Generation
│   │   ├── services/          # API Services
│   │   ├── hooks/             # Custom React Hooks
│   │   └── store/             # Zustand State Management
│   ├── package.json
│   └── vite.config.ts
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # API Endpoints
│   │   │   ├── chat.py        # Chat + Conversation Memory
│   │   │   ├── search.py      # Intelligent Search API
│   │   │   ├── conversations.py # Conversation Management
│   │   │   ├── training.py    # File Upload + Management
│   │   │   └── xml_generation.py # Stream Generation
│   │   ├── services/          # Business Logic
│   │   │   ├── rag_service.py # RAG + Vector Search
│   │   │   ├── intelligent_search.py # Smart Search
│   │   │   ├── conversation_memory.py # Chat Memory
│   │   │   ├── mistral_llm_service.py # Mistral LLM
│   │   │   ├── training_service.py # File Processing
│   │   │   └── txt_to_md_converter.py # Content Optimization
│   │   ├── models/            # Database Models
│   │   └── core/              # Configuration
│   ├── data/                  # Data Storage
│   │   ├── training_data/     # File Storage
│   │   │   ├── originals/     # Original Files
│   │   │   └── optimized/     # Processed MD Files
│   │   ├── vector_db/         # ChromaDB Storage
│   │   └── conversations/     # Chat Session Storage
│   └── requirements.txt
├── Training Data/              # Sample Training Data
│   ├── TXT/                   # StreamWorks Documentation
│   └── XSD/                   # XML Schemas & Templates
├── CLAUDE.md                  # AI Assistant Instructions
├── TECHNICAL_DOCUMENTATION.md # Diese Datei
└── SETUP_GUIDE.md            # Installation & Setup
```

## 🧠 AI Services im Detail

### RAG Service (`rag_service.py`)

**Kernfunktionalität:**
- Document Loading und Chunking mit LangChain
- Vector Embeddings mit Sentence-Transformers
- ChromaDB Integration für persistente Speicherung
- Intelligente Query-Erweiterung durch Synonym-Service
- Mistral 7B Integration für kontextbewusste Antworten

**Workflow:**
1. **Document Processing**: TXT/MD Dateien werden geladen und in Chunks aufgeteilt
2. **Embedding Generation**: Chunks werden mit `all-MiniLM-L6-v2` vektorisiert
3. **Vector Storage**: Embeddings werden in ChromaDB gespeichert
4. **Query Processing**: Benutzeranfragen werden erweitert und gegen Vector DB gesucht
5. **Answer Generation**: Mistral 7B generiert Antworten basierend auf gefundenen Kontexten

**Code-Beispiel:**
```python
# RAG Query mit intelligenter Suche
async def query(self, question: str) -> dict:
    # 1. Query Expansion durch Intelligent Search
    expanded_query = intelligent_search.expand_query(question)
    
    # 2. Vector Search in ChromaDB
    relevant_docs = await self.search_documents(expanded_query)
    
    # 3. Context Building
    context = self._build_context(relevant_docs)
    
    # 4. Mistral Answer Generation
    answer = await self._generate_mistral_answer(question, context)
    
    return {
        "answer": answer,
        "sources": sources,
        "expanded_query": expanded_query
    }
```

### Intelligent Search Service (`intelligent_search.py`)

**Features:**
- **Bidirektionale Synonyme**: DE/EN Begriffsmapping für StreamWorks
- **Query Expansion**: Automatische Erweiterung um verwandte Begriffe
- **Intent Analysis**: Erkennung der Benutzerabsicht
- **Search Suggestions**: Intelligente Vervollständigung

**Synonym-Beispiele:**
```python
synonyms = {
    "fehler": ["error", "problem", "issue", "bug", "störung"],
    "zeitplan": ["schedule", "cron", "timer", "planung"],
    "batch": ["stapel", "verarbeitung", "bulk", "masse", "job"],
    "stream": ["datenstrom", "streaming", "pipeline", "flow"]
}
```

### Conversation Memory Service (`conversation_memory.py`)

**Persistent Session Management:**
- JSON-basierte Speicherung von Chat-Sessions
- Automatischer Context-Loading für bessere Antworten
- Session-Cleanup mit konfigurierbarem Timeout
- Conversation Analytics und Statistics

**Session-Struktur:**
```python
@dataclass
class ConversationSession:
    session_id: str
    messages: List[ConversationMessage]
    created_at: datetime
    last_activity: datetime
    metadata: Optional[Dict] = None
```

### Mistral LLM Service (`mistral_llm_service.py`)

**Mistral 7B Integration:**
- Ollama-basierte lokale Mistral 7B Ausführung
- Deutsche Optimierung für StreamWorks-Kontext
- Async Processing für bessere Performance
- Health Monitoring und Error Handling

## 📤 Advanced Features

### Batch Upload System

**Frontend Component:** `BatchUploader.tsx`
**Features:**
- Drag & Drop für bis zu 20 Dateien gleichzeitig
- Progress-Tracking pro Datei mit visueller Anzeige
- Pause/Resume/Cancel Funktionalität
- Error Handling und Retry Logic
- Detaillierte Status-Übersicht

**Upload-Workflow:**
1. File Validation (Format, Größe)
2. Sequential Upload mit Progress-Updates
3. Automatic TXT→MD Conversion
4. RAG Indexing der optimierten Dateien
5. Database Metadata Update

### TXT zu MD Konvertierung

**Service:** `txt_to_md_converter.py`
**Optimierungen:**
- Intelligente Strukturerkennung (Überschriften, Listen, Code)
- StreamWorks-Begriff-Highlighting
- Metadaten-Extraktion für bessere Suchbarkeit
- Q&A Pattern Recognition
- Automatic Keyword Generation

**Konvertierungs-Pipeline:**
```
TXT Input → Content Analysis → Structure Detection → 
Markdown Formatting → Metadata Generation → Optimized MD Output
```

### File Organization System

**Neue Struktur:**
```
data/training_data/
├── originals/          # Ursprüngliche Dateien
│   ├── help_data/      # TXT, CSV, BAT, PS1
│   └── stream_templates/ # XML, XSD
└── optimized/          # Verarbeitete Dateien
    ├── help_data/      # Optimierte MD Dateien
    └── stream_templates/ # Processed Templates
```

**Features:**
- Clean Display Names (ohne UUID-Präfix)
- Cascade Delete (MD wird gelöscht wenn TXT entfernt wird)
- Automatic Category Detection
- File Status Tracking

## 🔌 API Endpoints

### Chat API (`/api/v1/chat/`)

```python
POST /api/v1/chat/
# Chat mit Conversation Memory
{
    "message": "Wie erstelle ich einen Batch-Job?",
    "conversation_id": "optional-session-id"
}

Response:
{
    "response": "Für einen Batch-Job in StreamWorks...",
    "conversation_id": "uuid-session-id",
    "mode": "mistral_rag",
    "processing_time": 2.34
}
```

### Intelligent Search API (`/api/v1/search/`)

```python
POST /api/v1/search/expand
# Query Expansion
{
    "query": "batch fehler"
}

Response:
{
    "original_query": "batch fehler",
    "expanded_query": "batch fehler stapel verarbeitung error problem issue",
    "added_terms": ["stapel", "verarbeitung", "error", "problem", "issue"]
}

POST /api/v1/search/suggestions
# Search Suggestions
{
    "partial_query": "ba"
}

Response:
{
    "suggestions": ["batch", "backup", "background"],
    "count": 3
}
```

### Conversation Memory API (`/api/v1/conversations/`)

```python
GET /api/v1/conversations/
# List all conversations (Admin)

GET /api/v1/conversations/{session_id}/summary
# Get conversation summary

GET /api/v1/conversations/{session_id}/context
# Get conversation context

DELETE /api/v1/conversations/{session_id}
# Delete conversation

POST /api/v1/conversations/cleanup
# Cleanup old conversations
```

### Training Data API (`/api/v1/training/`)

```python
POST /api/v1/training/upload
# File Upload (Single/Batch)

GET /api/v1/training/files
# List training files

GET /api/v1/training/files/{file_id}/conversion-status
# TXT→MD Conversion Status

GET /api/v1/training/conversion-stats
# Conversion Statistics
```

## 🚀 Performance & Monitoring

### Middleware Stack

**Performance Monitoring:**
```python
# Request Timing & Metrics
PerformanceMonitoringMiddleware
RequestLoggingMiddleware  
StreamWorksMetricsMiddleware
MistralPerformanceMiddleware
```

**Metriken:**
- Request/Response Times
- Mistral LLM Performance
- RAG Query Performance
- File Upload Progress
- Conversation Activity

### Health Checks

**Service Health Endpoints:**
- `/api/v1/training/health` - Training Service Status
- `/api/v1/search/health` - Intelligent Search Status
- `/api/v1/conversations/health` - Conversation Memory Status
- `/` - Overall System Health

## 🗄️ Datenmodelle

### Database Schema

**TrainingFile Model:**
```python
class TrainingFile(Base):
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)      # UUID_filename.txt
    display_name = Column(String, nullable=False)  # Clean filename
    category = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer, nullable=False)
    status = Column(String, default="processing")
    
    # ChromaDB Integration
    is_indexed = Column(Boolean, default=False)
    indexed_at = Column(DateTime, nullable=True)
    chunk_count = Column(Integer, default=0)
    chromadb_ids = Column(JSON, nullable=True)
    
    # TXT→MD Conversion
    processed_file_path = Column(String, nullable=True)
    original_format = Column(String, nullable=True)
    optimized_format = Column(String, nullable=True)
    conversion_status = Column(String, nullable=True)
    conversion_metadata = Column(Text, nullable=True)
```

### Conversation Data Model

**Session Storage (JSON):**
```json
{
  "session_id": "uuid",
  "messages": [
    {
      "question": "Benutzer-Frage",
      "answer": "KI-Antwort",
      "timestamp": "2025-07-04T12:00:00Z",
      "metadata": {
        "model_used": "mistral:7b-instruct",
        "context_used": true,
        "processing_time": 2.1
      }
    }
  ],
  "created_at": "2025-07-04T10:00:00Z",
  "last_activity": "2025-07-04T12:00:00Z"
}
```

## 🔧 Konfiguration

### Environment Variables

```bash
# Core Settings
PROJECT_NAME="StreamWorks-KI"
ENV="development"
LOG_LEVEL="INFO"
DATABASE_URL="sqlite:///./streamworks_ki.db"

# Service Toggles
RAG_ENABLED=true
LLM_ENABLED=true
XML_GENERATION_ENABLED=false

# Mistral Settings
MISTRAL_MODEL="mistral:7b-instruct"
MISTRAL_BASE_URL="http://localhost:11434"

# RAG Configuration
EMBEDDING_MODEL="all-MiniLM-L6-v2"
VECTOR_DB_PATH="data/vector_db"
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# File Upload
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=["txt", "md", "csv", "bat", "ps1", "xml", "xsd"]

# Conversation Memory
SESSION_TIMEOUT_HOURS=24
MAX_MESSAGES_PER_SESSION=50
CONTEXT_WINDOW_SIZE=3
```

### Service Configuration

**RAG Service Config:**
```python
rag_config = {
    "embedding_model": "all-MiniLM-L6-v2",
    "vector_db_path": "data/vector_db",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "similarity_threshold": 0.7
}
```

**Intelligent Search Config:**
```python
search_config = {
    "max_suggestions": 10,
    "min_query_length": 2,
    "context_window": 5,
    "synonym_expansion": True
}
```

## 🎯 Deployment & Production

### Requirements

**System Requirements:**
- Python 3.9+
- Node.js 18+
- Ollama mit Mistral 7B Model
- 8GB+ RAM (für Mistral 7B)
- 10GB+ Disk Space

**Installation:**
```bash
# Backend Setup
cd backend
pip install -r requirements.txt

# Frontend Setup  
cd frontend
npm install

# Ollama Setup
ollama pull mistral:7b-instruct
```

### Production Checklist

- [ ] Environment Variables konfiguriert
- [ ] Ollama Service läuft
- [ ] Database Migration durchgeführt
- [ ] CORS Settings für Production
- [ ] File Upload Limits gesetzt
- [ ] Backup Strategy für Conversations
- [ ] Monitoring & Logging aktiviert
- [ ] Health Checks implementiert

## 🔍 Debugging & Troubleshooting

### Common Issues

**1. Mistral Service nicht verfügbar:**
```bash
# Check Ollama Status
ollama list
ollama serve

# Test Mistral Model
curl -X POST http://localhost:11434/api/generate \
  -d '{"model": "mistral:7b-instruct", "prompt": "Test"}'
```

**2. ChromaDB Probleme:**
```python
# Reset Vector Database
rm -rf backend/data/vector_db/
# Restart backend - auto-recreates DB
```

**3. File Upload Errors:**
```python
# Check file permissions
ls -la backend/data/training_data/
# Check disk space
df -h
```

### Logging

**Log Levels:**
- `DEBUG`: Detaillierte Service-Informationen
- `INFO`: Allgemeine Aktivitäten
- `WARNING`: Potentielle Probleme
- `ERROR`: Service-Fehler

**Log Locations:**
- Backend: Console Output
- Frontend: Browser Console
- Service Logs: Individual service loggers

## 📈 Roadmap & Future Features

### Geplante Erweiterungen

**Phase 1 (Aktuell):**
- ✅ RAG + Mistral Integration
- ✅ Intelligent Search
- ✅ Conversation Memory
- ✅ Batch Upload System

**Phase 2 (Nächste Schritte):**
- [ ] LoRA Fine-Tuning für XML Generation
- [ ] Advanced Analytics Dashboard
- [ ] Multi-User Support
- [ ] API Rate Limiting
- [ ] Advanced File Processing (PDF, DOCX)

**Phase 3 (Zukunft):**
- [ ] Multi-Model Support (GPT, Claude)
- [ ] Real-time Collaboration
- [ ] Advanced Security Features
- [ ] Mobile App
- [ ] Enterprise Features

### Performance Optimierungen

**Geplant:**
- Vector Database Clustering
- Caching Layer für häufige Queries
- Background Job Processing
- Model Quantization für bessere Performance
- CDN Integration für Frontend Assets

---

**Version:** 3.0  
**Letztes Update:** Juli 2025  
**Autor:** Ravel-Lukas Geck  
**Projekt:** StreamWorks-KI Bachelorarbeit