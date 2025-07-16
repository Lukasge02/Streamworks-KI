# StreamWorks-KI Backend

## 🚀 Enterprise-Grade RAG + LLM System

StreamWorks-KI ist ein produktionsreifes AI-System, das Retrieval-Augmented Generation (RAG) mit Mistral 7B LLM für intelligente Q&A-Funktionalität kombiniert.

### ✨ Features

- **🤖 Mistral 7B Integration**: Optimiert für deutsche Sprache
- **🔍 Advanced RAG**: Semantische Suche mit Embedding-basierter Retrieval
- **📄 Intelligente Dokumentenverarbeitung**: Multi-Format-Support (PDF, DOCX, MD, TXT)
- **🔒 Enterprise Security**: Multi-Layer Security mit Input Validation
- **📊 Production Monitoring**: Umfassendes Monitoring mit Performance-Metriken
- **⚡ High Performance**: <3s Response Time, optimierte Async-Verarbeitung
- **🧪 Comprehensive Testing**: Unit/Integration/Performance Tests
- **🚀 CI/CD Ready**: Automatisierte Deployments mit GitHub Actions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Web UI    │ │  Mobile App │ │  API Client │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Nginx     │ │Rate Limiting│ │   SSL/TLS   │          │
│  │Load Balancer│ │ & Security  │ │   Security  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  FastAPI    │ │  Middleware │ │ Input Valid │          │
│  │   Router    │ │  Monitoring │ │  Sanitizer  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ RAG Service │ │ Mistral LLM │ │   Document  │          │
│  │   + ChromaDB│ │   Service   │ │  Processing │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   SQLite    │ │   ChromaDB  │ │   File      │          │
│  │  Database   │ │ Vector Store│ │   Storage   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Core Services

### 1. **Q&A Service** (`/api/v1/qa/`)
- **Endpoint**: `POST /api/v1/qa/ask`
- **Functionality**: Intelligente Frage-Antwort basierend auf RAG
- **Service**: `production_rag_service.py`

### 2. **Document Management** (`/api/v1/files/`)
- **Endpoints**: 
  - `POST /api/v1/files/upload` - Document upload
  - `GET /api/v1/files/` - List files
  - `DELETE /api/v1/files/{id}` - Delete file
- **Service**: `enterprise_file_manager.py`

### 3. **Training Data** (`/api/v1/training/`)
- **Endpoint**: `POST /api/v1/training/upload`
- **Functionality**: Legacy document upload
- **Service**: `training_service.py`

### 4. **Chunks Analysis** (`/api/v1/chunks/`)
- **Endpoints**: 
  - `GET /api/v1/chunks/analysis` - Chunk statistics
  - `GET /api/v1/chunks/files` - File analysis
- **Service**: `chunks_analysis.py`

### 5. **Categories** (`/api/v1/categories/`)
- **Endpoints**: 
  - `GET /api/v1/categories/` - List categories
  - `POST /api/v1/categories/` - Create category
- **Service**: `categories.py`

---

## 🛠️ Technical Stack

### Core Technologies
- **Python 3.9+** - Runtime environment
- **FastAPI** - Modern web framework
- **Mistral 7B** - Large Language Model (via Ollama)
- **ChromaDB** - Vector database for embeddings
- **SQLite** - Primary database
- **Sentence Transformers** - Embedding generation (`intfloat/multilingual-e5-large`)

### Dependencies
- **LangChain** - RAG pipeline orchestration
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM
- **Asyncio** - Asynchronous processing
- **Uvicorn** - ASGI server

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Mistral model
ollama pull mistral:7b
```

### Installation
```bash
# Clone repository
git clone <repository-url>
cd streamworks-ki/backend

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.models.database import init_db; import asyncio; asyncio.run(init_db())"

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables
```bash
# Create .env file
MISTRAL_MODEL="mistral:7b"
EMBEDDING_MODEL="intfloat/multilingual-e5-large"
VECTOR_DB_PATH="./data/vector_db"
DATABASE_URL="sqlite:///./streamworks_ki.db"
```

---

## 📊 Performance

### Response Times
- **Q&A Query**: < 3s (with RAG retrieval)
- **Document Upload**: < 1s (async indexing)
- **File Management**: < 500ms
- **Health Check**: < 100ms

### Throughput
- **Concurrent Users**: 100+
- **Documents**: 10,000+ files
- **Vector Embeddings**: 1M+ chunks
- **Memory Usage**: < 4GB

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Coverage report
pytest --cov=app --cov-report=html
```

---

## 🔒 Security

### Input Validation
- **Request sanitization** via Pydantic models
- **File type validation** for document uploads
- **Content filtering** to prevent injection attacks

### Data Protection
- **Secure file storage** with access controls
- **Database encryption** for sensitive data
- **API rate limiting** to prevent abuse

---

## 📈 Monitoring

### Health Checks
- `GET /health` - System health status
- `GET /api/v1/status` - Detailed system status
- `GET /api/v1/metrics` - Performance metrics

### Logging
- **Structured logging** with contextual information
- **Error tracking** with stack traces
- **Performance monitoring** with timing data

---

## 🔧 Development

### Code Structure
```
app/
├── api/v1/          # API endpoints
├── core/            # Core configuration
├── models/          # Database models
├── services/        # Business logic
├── middleware/      # Request processing
└── utils/           # Utility functions
```

### Key Services
- `production_rag_service.py` - Main RAG implementation
- `mistral_llm_service.py` - LLM service
- `enterprise_file_manager.py` - File management
- `document_indexer.py` - Background indexing
- `multi_format_processor.py` - Document processing

---

## 🚀 Deployment

### Docker
```bash
# Build image
docker build -t streamworks-ki-backend .

# Run container
docker run -p 8000:8000 streamworks-ki-backend
```

### Production
```bash
# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📞 Support

For technical support and documentation, please refer to:
- **API Documentation**: Available at `/docs` when server is running
- **Technical Issues**: Create GitHub issue
- **Production Support**: Contact development team

---

## 🔄 Updates

### Version 2.1.0 (Current)
- Enterprise code cleanup and optimization
- Improved RAG service performance
- Enhanced document processing pipeline
- Professional codebase structure

### Roadmap
- PostgreSQL migration for production
- Enhanced security features
- Advanced monitoring dashboard
- API versioning improvements