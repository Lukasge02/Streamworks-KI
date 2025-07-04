# StreamWorks-KI - Technische Dokumentation v2.0

## 🎯 Projekt-Übersicht

**StreamWorks-KI** ist eine intelligente Web-Anwendung zur Automatisierung von StreamWorks Workloads durch KI-gestützte Q&A und XML-Stream-Generierung. Das System kombiniert moderne Retrieval-Augmented Generation (RAG) mit LoRA Fine-Tuning für spezialisierte XML-Erstellung.

### Kernfunktionen
- **RAG-basierte Q&A**: Intelligente Antworten basierend auf StreamWorks-Dokumentation
- **XML Stream Generator**: LoRA-tuned XML-Generierung für StreamWorks
- **Training Data Management**: File Upload und Kategorisierung
- **Mistral 7B Integration**: Optimiert für deutsche Antworten
- **Full-Stack Web-Interface**: React + FastAPI

## 🏗️ System-Architektur

### High-Level Architektur
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   KI Services   │
│   React + TS    │◄──►│   FastAPI       │◄──►│   RAG + LoRA    │
│   Port 3001     │    │   Port 8000     │    │   Mistral 7B    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Components │    │   REST APIs     │    │   Vector DB     │
│   • Chat        │    │   • /chat/      │    │   ChromaDB      │
│   • Generator   │    │   • /xml/       │    │   Embeddings    │
│   • Training    │    │   • /training/  │    │   Documents     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Datenfluss
```
User Input → Frontend → API Gateway → Service Router → AI Processing → Response
    │                                        │              │
    │                                        ▼              ▼
    │                                   Vector Search   LLM Generation
    │                                   (ChromaDB)     (Mistral 7B)
    │                                        │              │
    │                                        ▼              ▼
    └────────────────────────────────── Structured Response ──┘
```

## 🔧 Backend-Architektur (Python/FastAPI)

### Service-Layer Architektur
```python
app/
├── api/v1/                 # REST API Endpoints
│   ├── chat.py            # RAG-basierte Q&A
│   ├── xml_generation.py  # LoRA XML Generator  
│   ├── xml_validation.py  # XSD Validation
│   └── training.py        # File Management
├── services/              # Core Business Logic
│   ├── rag_service.py     # ChromaDB + LangChain
│   ├── xml_generator.py   # LoRA Fine-Tuning
│   ├── mistral_rag_service.py  # Mistral Integration
│   └── training_service.py     # Data Processing
├── core/                  # Configuration & Utils
│   ├── config.py         # Settings Management
│   └── logging.py        # Structured Logging
├── models/               # Database & Schemas
│   ├── database.py       # SQLAlchemy Models
│   └── schemas.py        # Pydantic Schemas
└── middleware/           # Cross-cutting Concerns
    ├── monitoring.py     # Performance Metrics
    └── mistral_monitoring.py  # LLM Metrics
```

### Kern-Services im Detail

#### 1. RAGService (`rag_service.py`)
```python
class RAGService:
    """RAG-basierte Q&A mit ChromaDB + LangChain"""
    
    # Komponenten:
    embeddings: HuggingFaceEmbeddings  # sentence-transformers/all-MiniLM-L6-v2
    vector_store: Chroma               # Persistente Vector Database
    text_splitter: RecursiveCharacterTextSplitter
    
    # Methoden:
    async def search_documents()       # Vector Similarity Search
    async def generate_answer()        # RAG Pipeline
    async def add_documents()          # Document Indexing
```

#### 2. XMLGeneratorService (`xml_generator.py`)
```python
class XMLGeneratorService:
    """LoRA-tuned XML Generation"""
    
    # Komponenten:
    base_model: AutoModelForCausalLM   # DialoGPT-small
    tokenizer: AutoTokenizer
    lora_model: PeftModel              # LoRA Adapter
    
    # Modi:
    mock_mode: bool = True             # Development Mock
    fine_tuned_mode: bool = False      # Production LoRA
```

#### 3. MistralRAGService (`mistral_rag_service.py`)
```python
class MistralRAGService:
    """Mistral 7B + RAG Integration"""
    
    # Features:
    - Deutsche Optimierung
    - Context-aware Responses  
    - StreamWorks-spezifische Prompts
    - Performance Monitoring
```

### API-Endpoints

#### Chat-APIs (RAG Q&A)
```bash
POST /api/v1/chat/          # Haupt-Chat Interface
POST /api/v1/chat/dual-mode # Intelligente Mode-Erkennung
POST /api/v1/chat/upload-docs # Document Upload für Vector DB
GET  /api/v1/chat/search    # Direct Vector Search
```

#### XML-Generation APIs
```bash
POST /api/v1/xml/generate   # XML Stream Generation
GET  /api/v1/xml/health     # Service Status
GET  /api/v1/xml/templates  # Available Templates
```

#### Training & Management APIs
```bash
POST /api/v1/training/upload     # File Upload
GET  /api/v1/training/files      # List Files
DELETE /api/v1/training/files/{id} # Delete File
GET  /api/v1/training/status     # Training Status
```

#### System APIs
```bash
GET /health                 # Global Health Check
GET /api/v1/status         # Detailed System Status  
GET /api/v1/metrics        # Performance Metrics
GET /api/v1/mistral-metrics # LLM-specific Metrics
```

### Konfiguration (settings)

#### RAG-Parameter
```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DB_PATH = "./data/vector_db"
RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 50
RAG_TOP_K = 5
```

#### Mistral 7B Optimierung
```python
OLLAMA_MODEL = "mistral:7b-instruct"
MODEL_TEMPERATURE = 0.7
MODEL_TOP_P = 0.95
MODEL_TOP_K = 40
MODEL_MAX_TOKENS = 2048
MODEL_CONTEXT_WINDOW = 8192
FORCE_GERMAN_RESPONSES = True
```

#### LoRA Training
```python
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.1
LORA_TARGET_MODULES = ["c_attn", "c_proj"]
```

## 🎨 Frontend-Architektur (React/TypeScript)

### Komponenten-Hierarchie
```
App.tsx
├── Layout/
│   ├── Header.tsx              # Top Navigation
│   └── NavigationTabs.tsx      # Tab Navigation
├── Chat/
│   ├── DualModeChat.tsx        # Main Chat Interface ⭐
│   ├── ChatInterface.tsx       # Chat UI Components
│   ├── ChatInput.tsx          # Message Input
│   ├── MessageList.tsx        # Message History
│   └── MessageItem.tsx        # Individual Messages
├── StreamGenerator/
│   └── StreamGeneratorForm.tsx # XML Generator UI
├── TrainingData/
│   ├── TrainingDataTabV2Fixed.tsx ⭐ # Active Component
│   ├── UploadZone.tsx         # Drag & Drop
│   ├── FileManager.tsx        # File List
│   ├── CategorySelector.tsx   # help_data/stream_templates
│   └── TrainingStatus.tsx     # Upload Progress
└── Documentation/
    └── DocumentationTab.tsx   # Help & Docs
```

### State Management (Zustand)
```typescript
interface AppStore {
  // Navigation
  activeTab: 'chat' | 'generator' | 'training' | 'docs'
  setActiveTab: (tab: string) => void
  
  // Chat State
  messages: Message[]
  isLoading: boolean
  
  // File Upload State  
  uploadingFiles: File[]
  uploadProgress: Record<string, number>
}
```

### Service Layer
```typescript
// API Service (apiService.ts)
class ApiService {
  // Chat APIs
  async sendMessage(message: string, mode?: string)
  async uploadDocument(file: File, category: string)
  
  // XML Generation
  async generateXML(params: StreamParams)
  async validateXML(xmlContent: string)
  
  // Training Data
  async getTrainingFiles()
  async deleteTrainingFile(id: string)
}

// Stream Service (streamService.ts)  
class StreamService {
  async generateStream(config: StreamConfig)
  async validateStream(xml: string)
}
```

### Hooks
```typescript
// useChat.ts - Chat State Management
export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  // ... chat logic
}

// useFileUpload.ts - File Upload Logic
export const useFileUpload = () => {
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})
  // ... upload logic
}

// useStreamGenerator.ts - XML Generation Logic
export const useStreamGenerator = () => {
  // ... stream generation logic
}
```

## 📊 Datenbank & Storage

### SQLite Database (SQLAlchemy)
```python
# Training Files Table
class TrainingFile(Base):
    __tablename__ = "training_files"
    
    id: str = Column(String, primary_key=True)
    filename: str = Column(String, nullable=False)
    category: str = Column(String, nullable=False)  # help_data/stream_templates
    file_path: str = Column(String, nullable=False)
    file_size: int = Column(Integer, nullable=False)
    upload_date: datetime = Column(DateTime, default=datetime.utcnow)
    status: str = Column(String, default="ready")  # ready/processing/error
    processed_chunks: int = Column(Integer, default=0)
```

### Vector Database (ChromaDB)
```python
# Document Storage Structure
{
    "collection_name": "streamworks_docs",
    "documents": [
        {
            "id": "doc_uuid",
            "content": "chunked_text",
            "metadata": {
                "source": "filename.txt",
                "category": "help_data",
                "chunk_index": 0,
                "upload_date": "2025-07-04"
            },
            "embedding": [0.1, 0.2, ...]  # 384-dim vector
        }
    ]
}
```

### File Storage Structure
```
backend/data/
├── training_data/
│   ├── help_data/              # .txt, .csv, .bat, .md, .ps1
│   │   ├── {uuid}_filename.txt
│   │   └── ...
│   └── stream_templates/       # .xml, .xsd
│       ├── template1.xml
│       └── ...
├── vector_db/                  # ChromaDB Persistence
│   ├── chroma.sqlite3
│   └── embeddings/
└── models/                     # LoRA Adapters (Future)
    └── xml_lora/
```

## 🚀 Deployment & Setup

### Development Setup
```bash
# Backend Setup
cd backend/
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend Setup  
cd frontend/
npm install
npm run dev  # Startet auf Port 3001

# Access
Frontend: http://localhost:3001
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

### Environment Variables
```bash
# .env (Backend)
ENV=development
DATABASE_URL=sqlite:///./streamworks_ki.db
RAG_ENABLED=true
LLM_ENABLED=true
XML_GENERATION_ENABLED=false
FORCE_GERMAN_RESPONSES=true
LOG_LEVEL=INFO
```

### Dependencies

#### Backend (Python)
```python
# Core Framework
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0

# AI/ML Stack
transformers==4.36.0
peft==0.6.0
torch==2.1.0
sentence-transformers==2.2.2

# RAG Components
langchain==0.0.350
chromadb==0.4.18

# Database
sqlalchemy==2.0.23
aiosqlite==0.19.0

# Utilities
pandas==2.1.0
aiofiles==23.2.1
requests==2.31.0
```

#### Frontend (TypeScript/React)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.4.1",
    "react-dropzone": "^14.3.8",
    "lucide-react": "^0.263.1",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.0",
    "@vitejs/plugin-react": "^4.2.1"
  }
}
```

## 📈 Status & Roadmap

### ✅ Implementiert (v2.0)
- **Full-Stack Foundation**: React Frontend + FastAPI Backend
- **RAG Q&A System**: ChromaDB + LangChain + Sentence Transformers
- **Mistral 7B Integration**: Ollama + Deutsche Optimierung
- **Training Data Management**: File Upload + Kategorisierung
- **XML Generator Framework**: LoRA-ready Architecture
- **Performance Monitoring**: Request/Response Metrics
- **Development Environment**: Vollständig funktional

### 🎯 In Entwicklung (Phase 3)
- **LoRA Training Pipeline**: Automated Fine-Tuning
- **XML Template Processing**: Training Data → LoRA Dataset
- **Production XML Generation**: Mock → Fine-tuned Models
- **Advanced RAG Features**: Multi-document Reasoning
- **Evaluation Framework**: Model Performance Metrics

### 🚀 Geplant (Phase 4+)
- **Production Deployment**: Docker + CI/CD
- **Advanced UI Features**: Stream Visualization
- **API-Integration**: StreamWorks API Calls
- **User Management**: Authentication & Sessions
- **Monitoring & Alerting**: Production Observability

## 🔧 Troubleshooting & FAQ

### Häufige Probleme

#### Backend startet nicht
```bash
# Check Dependencies
pip list | grep fastapi

# Check Python Version (>=3.8 required)
python --version

# Check Port
lsof -i :8000
```

#### Frontend Build Fehler
```bash
# Clear Cache
rm -rf node_modules package-lock.json
npm install

# TypeScript Errors
npm run build
```

#### RAG Service Fehler
```bash
# Check Vector DB
ls -la backend/data/vector_db/

# Re-initialize ChromaDB
rm -rf backend/data/vector_db/
# Restart backend (auto-creates new DB)
```

#### Mistral/Ollama Connection
```bash
# Check Ollama Service
ollama list
ollama pull mistral:7b-instruct

# Test Connection
curl http://localhost:11434/api/tags
```

### Performance Optimization

#### RAG Performance
- **Chunk Size**: 500 tokens (optimal für Sentence-BERT)
- **Top-K**: 5 documents (balance relevance/speed)
- **Embedding Model**: all-MiniLM-L6-v2 (fast + good quality)

#### Mistral 7B Settings
- **Temperature**: 0.7 (balance creativity/consistency)
- **Context Window**: 8192 tokens
- **Threads**: 8 (optimiert für M4 MacBook)

## 📊 Metriken & Monitoring

### Performance KPIs
```python
{
    "response_times": {
        "rag_search": "< 500ms",
        "llm_generation": "< 2000ms", 
        "total_pipeline": "< 3000ms"
    },
    "accuracy_metrics": {
        "vector_search_relevance": "> 0.8",
        "answer_quality_score": "> 0.7",
        "xml_validation_rate": "> 0.95"
    }
}
```

### System Health Endpoints
```bash
GET /health                    # Global system status
GET /api/v1/status            # Detailed component status
GET /api/v1/metrics           # Performance metrics
GET /api/v1/mistral-metrics   # LLM-specific metrics
```

## 🎓 Entwickler-Notizen

### Code-Qualität
- **Type Safety**: Vollständige TypeScript Coverage
- **Error Handling**: Strukturierte Exception Handling
- **Logging**: Structured Logging mit Loguru
- **Testing**: Unit Tests für Core Services
- **Documentation**: Inline Code Documentation

### Architektur-Prinzipien
- **Separation of Concerns**: Services ↔ API ↔ UI
- **Dependency Injection**: Configurable Service Layer
- **Async/Await**: Non-blocking I/O Operations
- **Error Boundaries**: Graceful Error Recovery
- **Performance First**: Optimized für Development + Production

---

**Version**: 2.0.0  
**Letzte Aktualisierung**: 04.07.2025  
**Architektur**: RAG + LoRA Specialized Services  
**Status**: Phase 3 - LoRA Training Pipeline Implementation  

> 🎯 **Ziel**: Vollständig funktionale StreamWorks-KI als Proof of Concept für moderne KI-Integration in Unternehmensumgebungen.