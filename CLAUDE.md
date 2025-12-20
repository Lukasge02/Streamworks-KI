# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Streamworks-KI** is an enterprise RAG (Retrieval-Augmented Generation) system with advanced AI-powered parameter extraction:
- **Backend**: FastAPI with modular service architecture (130+ Python files)
- **Frontend**: Next.js 15 with TypeScript (600+ files)
- **Core Features**: Document processing, **Enhanced RAG v2.0**, LangExtract parameter extraction, template-based XML generation

### Enhanced RAG v2.0 (NEW)
The RAG system has been upgraded to enterprise level with:
- **Hybrid Search**: Semantic (Qdrant) + Keyword (BM25) with Reciprocal Rank Fusion
- **HyDE**: Hypothetical Document Embeddings for better query matching
- **Cross-Encoder Reranking**: GPT-based relevance scoring
- **Context Compression**: LLM-powered irrelevant sentence removal
- **Citation Generation**: Inline `[1]`, `[2]` references
- **Confidence Scoring**: 0-1 score with warnings for low-confidence answers
- **Caching Layer**: LRU/TTL caching for embeddings and search results

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
npm run test                    # Run tests (Jest)
```

### Common Issues
- **Frontend "Internal Server Error"**: Run `npm run dev:clean` to clear Next.js cache
- **Port conflicts**: Use `PORT=3001 npm run dev` or kill existing processes

## Architecture Overview

### Backend Structure (Clean Architecture)
```
backend/
├── main.py                     # FastAPI app entry point
├── config.py                   # Pydantic settings from .env
├── config/
│   └── parameters.yaml         # Central parameter definitions
├── domains/                    # Domain-Driven Design modules
│   ├── auth/                   # Authentication domain
│   │   └── router.py
│   ├── chat/                   # Chat domain
│   │   ├── router.py
│   │   ├── service.py
│   │   └── session.py
│   ├── documents/              # Document management domain
│   │   ├── router.py
│   │   └── models.py
│   ├── options/                # Options/config domain
│   │   └── router.py
│   ├── testing/                # Test generation domain
│   │   ├── router.py
│   │   └── service.py
│   ├── wizard/                 # Stream wizard domain
│   │   └── router.py
│   └── xml/                    # XML generation domain
│       ├── router.py
│       ├── service.py
│       └── validator.py
├── services/                   # Shared services layer
│   ├── ai/                     # AI services
│   │   ├── parameter_extractor.py
│   │   ├── batch_parameter_extractor.py
│   │   ├── parameter_registry.py
│   │   └── schemas.py
│   ├── rag/                    # RAG system (Enhanced v2.0)
│   │   ├── engine/             # Core RAG engine
│   │   │   ├── chat_service.py
│   │   │   ├── query_service.py
│   │   │   ├── index_service.py
│   │   │   └── ingestion_service.py
│   │   ├── parsers/            # Document parsers
│   │   │   ├── pymupdf_parser.py
│   │   │   ├── excel_parser.py
│   │   │   └── text_parser.py
│   │   ├── chunking/           # Enterprise chunking
│   │   ├── storage/            # File storage (MinIO)
│   │   ├── hybrid_search.py    # Semantic + BM25
│   │   ├── reranker.py         # Cross-encoder reranking
│   │   └── vector_store.py     # Qdrant integration
│   ├── auth_service.py         # Authentication
│   ├── db.py                   # Supabase client
│   ├── container.py            # Dependency injection
│   └── xml_generator.py        # XML generation
├── scripts/                    # Utility scripts
│   ├── seed_data.py            # Database seeding
│   ├── verify_db.py            # DB verification
│   └── evaluate_rag.py         # RAG evaluation
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest fixtures
│   ├── mocks/                  # Service mocks
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
└── storage/                    # Local storage
    └── categories.json         # Category definitions
```

### Frontend Structure (Clean Architecture)
```
frontend/
├── app/                        # Next.js App Router
│   ├── page.tsx                # Landing page (/)
│   ├── layout.tsx              # Root layout
│   ├── globals.css             # Global styles
│   ├── login/                  # Login page (/login)
│   ├── chat/                   # RAG Chat interface (/chat)
│   │   ├── page.tsx
│   │   └── components/
│   │       ├── ChatSessionSidebar.tsx
│   │       └── DocumentPreviewModal.tsx
│   ├── editor/                 # Stream Wizard (/editor)
│   │   ├── page.tsx
│   │   └── components/
│   │       ├── WizardStep0.tsx   # File upload
│   │       ├── WizardStep1.tsx   # Basic info
│   │       ├── WizardStep2.tsx   # Parameters
│   │       ├── WizardStep3.tsx   # Schedule
│   │       ├── WizardStep4.tsx   # Error handling
│   │       ├── WizardStep5.tsx   # Review
│   │       └── WizardStep6.tsx   # Export
│   ├── documents/              # Document management (/documents)
│   ├── streams/                # Stream overview (/streams)
│   ├── testing/                # Test generation (/testing)
│   ├── preview/                # XML preview (/preview)
│   ├── components/             # Shared components
│   │   ├── AppLayout.tsx       # Main layout
│   │   ├── Header.tsx          # Navigation header
│   │   ├── Sidebar.tsx         # Side navigation
│   │   ├── DDDChat.tsx         # DDD-based chat
│   │   ├── ui/                 # UI primitives
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   └── magicui/            # Animation components
│   └── hooks/                  # Custom hooks
│       ├── useAutoSave.ts
│       └── useOptions.ts
├── hooks/                      # Root-level hooks
│   └── useAuth.tsx             # Authentication hook
├── __tests__/                  # Test files
│   └── login.test.tsx
└── package.json                # Dependencies
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