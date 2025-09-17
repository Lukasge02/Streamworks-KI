# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Streamworks-KI** is an enterprise RAG (Retrieval-Augmented Generation) system with:
- **Backend**: FastAPI with modular service architecture (40+ services)
- **Frontend**: Next.js 15 with TypeScript (600+ files)
- **Core Features**: Document processing, RAG-based Q&A, XML generation

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
├── services/                   # Modular service layer
│   ├── ai/                     # AI model services
│   ├── document/               # Document processing
│   ├── rag/                    # RAG pipeline
│   ├── qdrant_rag_service.py   # Vector search
│   ├── chat_service_sqlalchemy.py # Chat management
│   └── di_container.py         # Dependency injection
└── routers/                    # API endpoints
    ├── chat_rag_test.py        # Chat API
    ├── documents/              # Document management
    ├── xml_generator.py        # XML wizard
    └── health.py               # Health checks
```

### Frontend Structure
```
frontend/src/
├── app/                        # Next.js App Router
│   ├── xml/                    # XML wizard pages
│   ├── chat/                   # Chat interface
│   └── documents/              # Document management
├── components/                 # React components
│   ├── xml-wizard/             # XML generation UI
│   ├── chat/                   # Chat interface
│   ├── documents/              # Document management
│   └── ui/                     # Reusable components
└── services/                   # API client
    └── api.service.ts          # Backend communication
```

## Key Patterns

### Backend Service Pattern
```python
# Services use dependency injection
class DocumentService:
    def __init__(self, db_service, embedding_service, vectorstore_service):
        self.db = db_service
        self.embeddings = embedding_service
        self.vectorstore = vectorstore_service

    async def process_document(self, file_path: str) -> ProcessedDocument:
        # Always use async/await for I/O operations
```

### Frontend API Pattern
```typescript
// Use React Query for server state
const { data: documents, isLoading } = useQuery({
  queryKey: ['documents', folderId],
  queryFn: () => fetchDocuments(folderId)
})

// Use Zustand for client state
const useDocumentStore = create<DocumentStore>((set) => ({
  selectedDocuments: [],
  setSelectedDocuments: (docs) => set({ selectedDocuments: docs })
}))
```

### Database Pattern
```python
# Always use async SQLAlchemy patterns
async def get_documents(db: AsyncSession, folder_id: Optional[int] = None):
    query = select(Document)
    if folder_id:
        query = query.filter(Document.folder_id == folder_id)
    result = await db.execute(query)
    return result.scalars().all()
```

## Important File Locations

### Backend Key Files
- `backend/main.py` - FastAPI application entry point
- `backend/config.py` - Configuration with Pydantic Settings
- `backend/database.py` - SQLAlchemy database setup
- `backend/services/di_container.py` - Dependency injection container
- `backend/services/qdrant_rag_service.py` - Main RAG service
- `backend/services/chat_service_sqlalchemy.py` - Chat management

### Frontend Key Files
- `frontend/src/app/layout.tsx` - Root layout component
- `frontend/src/services/api.service.ts` - API client service
- `frontend/src/components/chat/ModernChatInterface.tsx` - Main chat component
- `frontend/src/components/xml-wizard/` - XML generation components

## Technology Stack

### Backend
- **FastAPI 0.115.4** - Async web framework
- **SQLAlchemy 2.0.25** - Async ORM with PostgreSQL
- **Qdrant** - Vector database for embeddings
- **LlamaIndex 0.11.0** - RAG orchestration
- **Transformers 4.44.0** - Local embedding models
- **Ollama 0.4.4** - Local LLM integration

### Frontend
- **Next.js 15.5.2** - React framework with App Router
- **TypeScript 5.9.2** - Type safety
- **TailwindCSS 3.4.15** - Styling
- **React Query 5.87.1** - Server state management
- **Zustand 5.0.8** - Client state management
- **Monaco Editor 4.7.0** - Code editing for XML

## Development Guidelines

### Code Conventions
- **Python**: PEP 8, async/await patterns, type hints required
- **TypeScript**: Strict mode enabled, proper typing required
- **Services**: Respect modular structure - don't create monolithic services
- **API**: Use FastAPI dependency injection for all database/service access

### Module Organization
- **Document features**: Use `services/document/` module
- **RAG features**: Use `services/rag/` module
- **AI features**: Use `services/ai/` module
- **Chat features**: Use `services/chat_service_sqlalchemy.py`

### Error Handling
```python
# Backend: Use HTTPException with structured details
raise HTTPException(
    status_code=404,
    detail={"error": "Document not found", "document_id": doc_id}
)
```

```typescript
// Frontend: Use React Query error handling
const mutation = useMutation({
  mutationFn: uploadDocument,
  onError: (error) => {
    toast.error(`Upload failed: ${error.message}`)
  }
})
```

## Common Tasks

### Adding Document Features
1. Backend: Extend `services/document/` modules
2. Router: Add endpoints in `routers/documents/`
3. Frontend: Use React Query for API calls
4. UI: Add components to `components/documents/`

### Adding RAG Features
1. Backend: Extend `services/rag/` modules
2. Test with `services/qdrant_rag_service.py`
3. Frontend: Update chat interface in `components/chat/`

### Adding XML Wizard Features
1. Backend: Modify `routers/xml_generator.py`
2. Templates: Update `services/xml_template_engine.py`
3. Frontend: Extend `components/xml-wizard/` modules

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
pytest tests/test_specific.py   # Run specific test file
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