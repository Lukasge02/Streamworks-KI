# 🤖 Claude Code - StreamWorks-KI Project Basics

## 📋 **ESSENTIAL PROJECT CONTEXT**

### **👤 Student & Project Info**
- **Name**: Ravel-Lukas Geck
- **Hochschule**: Fachhochschule der Wirtschaft (FHDW), Paderborn
- **Betreuer**: Prof. Dr. Christian Ewering
- **Unternehmen**: Arvato Systems / Bertelsmann
- **Zeitrahmen**: 3. Quartal 2025 (12 Wochen)
- **Ziel**: Bachelorarbeit Note 1 (90+/100 Punkte)

### **🎯 Project Mission**
**"StreamWorks-KI: Intelligente Workload-Automatisierung durch Self-Service und KI"**

- **Intelligente Q&A**: Beantwortet StreamWorks-Fragen via RAG
- **Multi-Source Knowledge**: StreamWorks Hilfe + JIRA + DDDS
- **User Groups**: Developer, Admin, Business, Support, Architect
- **API Integration**: Automatische StreamWorks API-Calls
- **XML Generator**: Template-basierte Stream-Erstellung

---

## 🏗️ **CURRENT ARCHITECTURE (v2.0)**

### **Tech Stack**
```
Frontend: React + TypeScript + Tailwind CSS + Zustand
Backend:  Python + FastAPI + ChromaDB + Langchain
AI:       Mistral 7B (Ollama) + Sentence Transformers
Database: SQLite + SQLAlchemy (async) → PostgreSQL (production)
Vector:   ChromaDB (persistent)
Testing:  pytest + React Testing Library + Playwright
```

### **Core Services**
```python
# Backend Structure
app/
├── api/           # FastAPI endpoints
├── services/      # Business logic
│   ├── rag_service.py        # RAG with ChromaDB + Langchain
│   ├── mistral_service.py    # LLM integration
│   ├── user_group_service.py # NEW: Multi-user chains
│   ├── xml_generator.py      # Template-based XML
│   └── training_service.py   # Document management
├── models/        # Pydantic + SQLAlchemy models
└── core/          # Configuration + utilities
```

### **Database Schema**
```sql
-- Core Tables
training_files (id, filename, file_path, source_type, category, is_indexed)
conversations (id, user_id, session_id, messages, created_at)
document_metadata (id, source_type, source_path, title, category, tags)
user_profiles (id, user_role, preferences, created_at)
```

---

## 🎯 **CURRENT DEVELOPMENT PHASE**

### **Status: Phase 3 - Advanced Features**
- ✅ **Phase 1**: Foundation (Backend + Frontend komplett)
- ✅ **Phase 2**: RAG Service + Mistral Integration komplett
- 🎯 **Phase 3**: Multi-Source + User Groups (IN PROGRESS)
- 📅 **Phase 4**: Evaluation + Production Ready

### **This Week's Priority**
1. **UserGroupService**: Langchain Chains für verschiedene User Roles
2. **Multi-Source**: StreamWorks + JIRA + DDDS mit source_type
3. **Citations**: Quellenangaben in Antworten
4. **Frontend**: User Role Selection + Citation Display

### **Architecture Score: 90+/100** (Production Ready)

---

## 🔧 **DEVELOPMENT STANDARDS**

### **Code Quality Rules**
```python
# Python Standards
- Type hints ALWAYS: def search(query: str) -> Dict[str, Any]
- Docstrings ALWAYS: """Search documents with RAG"""
- Async/await for I/O: async def search_documents()
- Error handling: try/except with logging
- Pydantic models for data validation
```

### **Testing Standards**
```python
# Testing Requirements
- Unit tests: 80%+ coverage
- Integration tests: All API endpoints
- Pytest fixtures for dependencies
- Mock external services (Ollama, ChromaDB)
- AAA pattern: Arrange, Act, Assert
```

### **File Organization**
```bash
# Always update these files:
claude_context.md          # Auto-update with changes
daily_progress.md          # Log daily progress
GOALS.md                   # Track objectives
TESTING_STRATEGY.md        # Testing approach
```

---

## 🤖 **CLAUDE CODE INSTRUCTIONS**

### **🎯 Primary Directives**
1. **ALWAYS** maintain context with project basics
2. **ALWAYS** update `claude_context.md` with changes
3. **ALWAYS** follow coding standards above
4. **ALWAYS** generate tests for new code
5. **ALWAYS** use existing services as base patterns

### **📊 Development Workflow**
```python
# For every new feature:
1. Analyze existing code structure
2. Design following current patterns
3. Implement with proper error handling
4. Generate comprehensive tests
5. Update documentation
6. Log changes in claude_context.md
```

### **🔄 Change Management**
```python
# Every code change must include:
- Type hints and docstrings
- Error handling
- Unit tests (80%+ coverage)
- Integration with existing services
- Update to relevant documentation
```

---

## 📊 **CURRENT IMPLEMENTATION STATUS**

### **✅ Fully Implemented**
- **RAG Service**: ChromaDB + Langchain + Caching
- **Mistral Service**: 7B model via Ollama
- **Training Service**: File upload + processing
- **Database**: SQLAlchemy async + models
- **API**: FastAPI endpoints with error handling
- **Frontend**: React + TypeScript + Tailwind
- **Health System**: Comprehensive monitoring

### **🚧 In Progress**
- **UserGroupService**: Multi-user Langchain chains
- **Multi-Source**: StreamWorks + JIRA + DDDS integration
- **Citations**: Source attribution in responses
- **Advanced Testing**: Performance + E2E tests

### **📅 Planned**
- **Performance Optimization**: Caching strategies
- **Security**: Authentication + authorization
- **Deployment**: Docker + production config
- **Evaluation**: A/B testing framework

---

## 🎓 **BACHELOR THESIS CONTEXT**

### **Scientific Requirements**
- **Innovation**: Multi-Agent RAG für verschiedene User Groups
- **Evaluation**: Quantitative Metrics für Response Quality
- **Comparison**: Benchmarking gegen existierende Lösungen
- **Documentation**: Wissenschaftliche Methodik + Ergebnisse

### **Technical Excellence Goals**
- **Architecture**: Clean, maintainable, scalable
- **Performance**: < 2s response times
- **Reliability**: 99.5%+ uptime
- **Quality**: 80%+ test coverage

### **Business Value**
- **ROI**: Messbare Zeitersparnis für StreamWorks-Benutzer
- **Usability**: Intuitive Self-Service-Oberfläche
- **Scalability**: Erweiterbar für weitere Datenquellen
- **Integration**: Nahtlose StreamWorks-API-Integration

---

## 💼 **DOMAIN KNOWLEDGE**

### **StreamWorks Context**
- **Was**: Enterprise Data Processing Platform
- **Benutzer**: Entwickler, Administratoren, Business Users
- **Aufgaben**: Batch Jobs, XML Streams, Datenverarbeitung
- **Herausforderung**: Komplexe Konfiguration, manueller Aufwand
- **Lösung**: KI-gestützte Automatisierung + Self-Service

### **Technical Domains**
- **RAG**: Retrieval-Augmented Generation
- **Langchain**: Chain-basierte LLM-Workflows
- **ChromaDB**: Vector Database für Embeddings
- **FastAPI**: Python Web Framework
- **Mistral 7B**: Open-Source LLM

---

## 📁 **REPOSITORY STRUCTURE**

### **Main Directories**
```
StreamWorks-KI/
├── backend/           # Python FastAPI backend
├── frontend/          # React TypeScript frontend
├── Training Data/     # Sample training documents
├── docs/             # Documentation
├── tests/            # Test suites
├── tools/            # Development utilities
└── .claude/          # Claude Code configuration
```

### **Important Files**
```bash
# Core Documentation
README.md                    # Project overview
claude_context.md           # Living context (auto-updated)
GOALS.md                    # Development objectives
TESTING_STRATEGY.md         # Testing approach
TECHNICAL_DOCUMENTATION.md  # Architecture details
API_DOCUMENTATION.md        # API reference

# Development
requirements.txt            # Python dependencies
package.json               # Node.js dependencies
.env                       # Environment variables
docker-compose.yml         # Local development setup
```

---

## 🚀 **QUICK START COMMANDS**

### **Development Environment**
```bash
# Backend (Terminal 1)
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd frontend
npm run dev

# Tests
python -m pytest tests/ --cov=app
npm test
```

### **Common Tasks**
```bash
# Add new feature
python tools/feature_generator.py --name UserGroupService --type service

# Update documentation
python tools/update_claude_context.py

# Check system health
curl http://localhost:8000/api/v1/health

# Run quality checks
python tools/quality_metrics.py
```

---

## 🎯 **SUCCESS METRICS**

### **Technical KPIs**
- **Response Time**: < 2 seconds for RAG queries
- **Test Coverage**: 80%+ for backend, 70%+ for frontend
- **Code Quality**: 90+ maintainability index
- **Performance**: Handle 100+ concurrent users

### **Business KPIs**
- **User Satisfaction**: 4.5/5 rating
- **Time Savings**: 60%+ reduction in manual tasks
- **Accuracy**: 85%+ correct answers
- **Adoption**: 80%+ user activation rate

### **Academic KPIs**
- **Innovation Score**: Novel multi-agent RAG approach
- **Evaluation Rigor**: Statistical significance testing
- **Documentation Quality**: Publication-ready documentation
- **Presentation**: Clear demonstration of business value

---

**🎯 REMEMBER: Focus on Note 1 (90+/100) through technical excellence, scientific rigor, and practical business value.**

*Last Updated: 2025-07-04*  
*Version: 2.0.0*  
*Status: Production Ready for Bachelor Thesis*