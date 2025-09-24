# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Streamworks-KI** is an enterprise RAG (Retrieval-Augmented Generation) system with advanced AI-powered parameter extraction:
- **Backend**: FastAPI with modular service architecture (120+ Python files)
- **Frontend**: Next.js 15 with TypeScript (600+ files)
- **Core Features**: Document processing, RAG-based Q&A, LangExtract parameter extraction, template-based XML generation

## Development Commands

### Backend
```bash
cd backend
python main.py                    # Start server (http://localhost:8000)
pip install -r requirements.txt   # Install dependencies
pytest                           # Run tests (if available)
```

### Frontend
```bash
cd frontend
npm run dev                      # Start dev server (http://localhost:3000)
npm run dev:clean               # Start with cache clear (fixes common issues)
npm run build                   # Production build
npm run type-check              # TypeScript validation
npm run lint                    # ESLint validation
```

### Common Issues
- **Frontend "Internal Server Error"**: Run `npm run dev:clean` to clear Next.js cache
- **Port conflicts**: Use `PORT=3001 npm run dev` or kill existing processes

## Architecture Overview

### Backend Structure
```
backend/
├── main.py                     # FastAPI app entry point
├── config.py                   # Pydantic settings from .env
├── database.py                 # SQLAlchemy async setup
├── services/                   # Modular service layer (40+ services)
│   ├── ai/                     # AI model services
│   │   ├── langextract/        # LangExtract parameter extraction
│   │   │   ├── unified_langextract_service.py
│   │   │   ├── session_persistence_service.py
│   │   │   └── mcp_session_persistence_service.py
│   │   ├── enhanced_job_type_detector.py      # 88.9% accuracy job detection
│   │   ├── enhanced_unified_parameter_extractor.py
│   │   ├── enterprise_parameter_engine.py
│   │   └── parameter_extraction_ai.py
│   ├── knowledge_graph/        # Knowledge graph & memory
│   │   ├── unified_knowledge_service.py
│   │   ├── context_memory_system.py
│   │   ├── entity_extraction_pipeline.py
│   │   └── temporal_graph_service.py
│   ├── xml_generation/         # Template-based XML generation
│   │   ├── template_engine.py
│   │   └── parameter_mapper.py
│   ├── chat_xml/              # XML chat session management
│   │   ├── chat_session_service.py
│   │   ├── dialog_manager.py
│   │   └── parameter_extractor.py
│   ├── auth/                  # Authentication services
│   │   ├── auth_service.py
│   │   ├── jwt_service.py
│   │   └── permission_service.py
│   ├── qdrant_rag_service.py  # Vector search
│   ├── chat_service_sqlalchemy.py # Chat management
│   └── di_container.py        # Dependency injection
└── routers/                   # API endpoints
    ├── langextract_chat.py    # LangExtract chat API
    ├── chat_xml_unified.py    # Unified XML chat
    ├── xml_generator.py       # Template-based XML generation
    ├── chat_rag_test.py       # RAG chat API
    ├── documents/             # Document management
    ├── auth.py               # Authentication endpoints
    └── health.py             # Health checks
```

### Frontend Structure
```
frontend/src/
├── app/                       # Next.js App Router
│   ├── langextract/           # LangExtract interface (/langextract)
│   ├── xml/                   # XML wizard pages (/xml)
│   ├── chat/                  # Chat interface (/chat)
│   ├── auth/                  # Authentication pages
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/             # System dashboard
│   └── documents/             # Document management
├── components/                # React components
│   ├── langextract-chat/      # LangExtract UI components
│   │   ├── LangExtractInterface.tsx
│   │   ├── components/
│   │   │   ├── LangExtractSessionSidebar.tsx
│   │   │   ├── ParameterOverview.tsx
│   │   │   └── SmartSuggestions.tsx
│   │   └── hooks/
│   │       └── useLangExtractChat.ts
│   ├── chat/                  # Chat interface components
│   │   ├── ModernChatInterface.tsx
│   │   ├── CompactChatInterface.tsx
│   │   ├── FloatingChatWidget.tsx
│   │   ├── EnterpriseResponseFormatter.tsx
│   │   └── EnterpriseInputArea.tsx
│   ├── xml-streams/           # XML generation components
│   ├── auth/                  # Authentication components
│   ├── dashboard/             # Dashboard components
│   ├── layout/               # Layout components
│   │   └── AppLayout.tsx
│   └── ui/                   # Reusable UI components
└── services/                 # API client
    └── api.service.ts        # Backend communication
```

## Key Features & Systems

### 1. LangExtract Parameter Extraction System
Advanced AI-powered parameter extraction with 88.9% accuracy:

**Backend Services:**
- `services/ai/langextract/unified_langextract_service.py` - Main LangExtract service
- `services/ai/enhanced_job_type_detector.py` - Job type detection (88.9% accuracy)
- `services/ai/enhanced_unified_parameter_extractor.py` - Parameter extraction

**Job Types Supported:**
- **STANDARD** - General automation with script execution
- **FILE_TRANSFER** - File transfer between agents/servers
- **SAP** - SAP system integration

**API Endpoints:**
- `POST /api/langextract/sessions` - Create new session
- `POST /api/langextract/sessions/{session_id}/messages` - Process message
- `GET /api/langextract/sessions/{session_id}` - Get session state

### 2. Template-Based XML Generation
Production-ready XML generation with Jinja2 templates:

**⚠️ IMPORTANT: Stream Prefix Configuration**
- **Current Prefix**: `zsw_` (changed from `STREAM_`)
- **Configuration Guide**: See `documentation/XML_STREAM_CONFIGURATION.md`
- **Critical Files for Prefix Changes:**
  - `services/xml_generation/parameter_mapper.py:261` - Main prefix logic
  - `services/xml_generation/template_engine.py:89` - Auto-generation
  - `services/ai/langextract/unified_langextract_service.py:1284` - Fallback names

**Backend Services:**
- `services/xml_generation/template_engine.py` - Template rendering engine
- `services/xml_generation/parameter_mapper.py` - Parameter mapping logic
- `backend/templates/xml_templates/` - XML template library

**Features:**
- 3 job-specific templates (STANDARD, FILE_TRANSFER, SAP)
- Intelligent parameter mapping with fuzzy matching
- Auto-generation of missing parameters
- Smart defaults based on job type

**API Endpoints:**
- `POST /api/xml-generator/template/generate` - Generate XML from session
- `POST /api/xml-generator/template/preview` - Preview parameter mapping
- `GET /api/xml-generator/template/info` - Template metadata

### 3. Knowledge Graph & Memory System
Advanced context management with temporal memory:

**Backend Services:**
- `services/knowledge_graph/unified_knowledge_service.py`
- `services/knowledge_graph/context_memory_system.py`
- `services/knowledge_graph/entity_extraction_pipeline.py`
- `services/knowledge_graph/temporal_graph_service.py`

### 4. Authentication System
JWT-based authentication with role management:

**Backend Services:**
- `services/auth/auth_service.py` - Authentication logic
- `services/auth/jwt_service.py` - JWT token management
- `services/auth/permission_service.py` - Role-based permissions

**Frontend Pages:**
- `/auth/login` - Login interface
- `/auth/register` - Registration interface

## Key Patterns

### Backend Service Pattern
```python
# Services use dependency injection and async patterns
class LangExtractService:
    def __init__(self, db_service, parameter_extractor, job_detector):
        self.db = db_service
        self.parameter_extractor = parameter_extractor
        self.job_detector = job_detector

    async def process_message(self, session_id: str, message: str) -> ProcessedResponse:
        # Always use async/await for I/O operations
        session = await self.db.get_session(session_id)
        job_type = await self.job_detector.detect_job_type(message)
        parameters = await self.parameter_extractor.extract(message, job_type)
        return ProcessedResponse(job_type=job_type, parameters=parameters)
```

### Frontend API Pattern
```typescript
// Use React Query for server state
const { data: session, isLoading } = useQuery({
  queryKey: ['langextract-session', sessionId],
  queryFn: () => fetchLangExtractSession(sessionId)
})

// Use Zustand for client state
const useLangExtractStore = create<LangExtractStore>((set) => ({
  currentSession: null,
  setCurrentSession: (session) => set({ currentSession: session })
}))
```

### Database Pattern
```python
# Always use async SQLAlchemy patterns
async def get_chat_sessions(db: AsyncSession, user_id: str):
    query = select(ChatSession).filter(ChatSession.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()
```

## Important File Locations

### Backend Key Files
- `backend/main.py` - FastAPI application entry point
- `backend/config.py` - Configuration with Pydantic Settings
- `backend/database.py` - SQLAlchemy database setup
- `backend/services/di_container.py` - Dependency injection container
- `backend/services/ai/langextract/unified_langextract_service.py` - Main LangExtract service
- `backend/services/xml_generation/template_engine.py` - XML template engine
- `backend/routers/langextract_chat.py` - LangExtract API endpoints

### Frontend Key Files
- `frontend/src/app/layout.tsx` - Root layout component
- `frontend/src/services/api.service.ts` - API client service
- `frontend/src/components/langextract-chat/LangExtractInterface.tsx` - Main LangExtract UI
- `frontend/src/components/chat/ModernChatInterface.tsx` - Modern chat component
- `frontend/src/components/layout/AppLayout.tsx` - Application layout

## Technology Stack

### Backend
- **FastAPI 0.116.0** - Async web framework
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **Qdrant** - Vector database for embeddings
- **LlamaIndex 0.11.0** - RAG orchestration
- **Transformers 4.44.0** - Local embedding models
- **Ollama** - Local LLM integration
- **Jinja2** - Template engine for XML generation

### Frontend
- **Next.js 15.6.0** - React framework with App Router
- **TypeScript 5.x** - Type safety
- **TailwindCSS** - Styling
- **React Query 5.87.1** - Server state management
- **Zustand** - Client state management
- **Monaco Editor 4.7.0** - Code editing for XML
- **Framer Motion** - Animations

## Development Guidelines

### Code Conventions
- **Python**: PEP 8, async/await patterns, type hints required
- **TypeScript**: Strict mode enabled, proper typing required
- **Services**: Respect modular structure - don't create monolithic services
- **API**: Use FastAPI dependency injection for all database/service access

### Module Organization
- **LangExtract features**: Use `services/ai/langextract/` module
- **Parameter extraction**: Use `services/ai/enhanced_*` modules
- **XML generation**: Use `services/xml_generation/` module
- **Knowledge graph**: Use `services/knowledge_graph/` module
- **Authentication**: Use `services/auth/` module
- **Chat features**: Use `services/chat_xml/` modules

### Error Handling
```python
# Backend: Use HTTPException with structured details
raise HTTPException(
    status_code=404,
    detail={"error": "Session not found", "session_id": session_id}
)
```

```typescript
// Frontend: Use React Query error handling
const mutation = useMutation({
  mutationFn: processLangExtractMessage,
  onError: (error) => {
    toast.error(`Processing failed: ${error.message}`)
  }
})
```

## Common Tasks

### Adding LangExtract Features
1. Backend: Extend `services/ai/langextract/` modules
2. Router: Add endpoints in `routers/langextract_chat.py`
3. Frontend: Use React Query for API calls
4. UI: Add components to `components/langextract-chat/`

### Adding XML Generation Features
1. Backend: Modify `services/xml_generation/` modules
2. Templates: Update XML templates in `backend/templates/xml_templates/`
3. Frontend: Extend XML-related components

### Adding Authentication Features
1. Backend: Extend `services/auth/` modules
2. Router: Add endpoints in `routers/auth.py`
3. Frontend: Update auth components and pages

### Adding Knowledge Graph Features
1. Backend: Extend `services/knowledge_graph/` modules
2. Test with knowledge graph services
3. Frontend: Update interfaces for enhanced context

## Performance Metrics

### LangExtract System Performance
- **Job Type Detection Accuracy**: 88.9%
- **Parameter Extraction**: Detailed extraction with auto-generation
- **German Language Support**: Optimized patterns for StreamWorks context
- **False Positive Reduction**: 70% improvement over previous system

### Template XML Generation
- **Template Rendering**: Sub-second performance with caching
- **Parameter Mapping**: Intelligent field mapping with fuzzy matching
- **Template Library**: 3 production-ready templates (STANDARD, FILE_TRANSFER, SAP)

## Environment Setup

### Required Environment Variables
Create `.env` file in backend/ with:
```bash
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key

# LLM Provider (openai|ollama)
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key

# Vector Database
VECTOR_DB=qdrant
QDRANT_URL=http://localhost:6333

# Embedding Provider (gamma for local)
EMBEDDING_PROVIDER=gamma

# Authentication
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Local Development Setup
1. **Qdrant**: `docker run -p 6333:6333 qdrant/qdrant`
2. **Backend**: `cd backend && python main.py`
3. **Frontend**: `cd frontend && npm run dev`

## Testing & Quality

### Backend Testing
```bash
cd backend
pytest                          # Run all tests
pytest tests/test_langextract.py # Run LangExtract tests
pytest tests/test_xml_generation.py # Run XML generation tests
```

### Frontend Testing
```bash
cd frontend
npm run type-check              # TypeScript validation
npm run lint                    # ESLint validation
npm run build                   # Production build test
```

## Health Checks

- **API Health**: http://localhost:8000/health
- **Database Health**: http://localhost:8000/health/database
- **Detailed Health**: http://localhost:8000/health/detailed
- **API Docs**: http://localhost:8000/docs
- **LangExtract Health**: http://localhost:8000/api/langextract/health
- **XML Generator Health**: http://localhost:8000/api/xml-generator/template/health