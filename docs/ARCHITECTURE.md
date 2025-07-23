# 🏗️ StreamWorks-KI Architecture

## System Overview

StreamWorks-KI follows a modern microservices-inspired architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + TypeScript)            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Q&A Chat   │  │  Document    │  │   Analytics      │  │
│  │  Interface  │  │  Management  │  │   Dashboard      │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────┴────────────────────────────────┐
│                    Backend (FastAPI + Python)                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   RAG       │  │  Document    │  │   Analytics      │  │
│  │  Service    │  │  Service     │  │   Service        │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│         │                 │                    │             │
│  ┌──────┴─────────────────┴────────────────────┴────────┐  │
│  │              Data Access Layer (SQLAlchemy)           │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                        Data Layer                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PostgreSQL  │  │  ChromaDB    │  │   File Storage   │  │
│  │  Database   │  │ Vector Store │  │   (Documents)    │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **React 18**: Modern UI framework with hooks
- **TypeScript 5**: Type-safe development
- **Vite**: Fast build tooling
- **Tailwind CSS**: Utility-first styling with glassmorphism
- **Zustand**: Lightweight state management
- **Lucide React**: Modern icon library

### Backend
- **FastAPI**: High-performance async web framework
- **Python 3.9+**: Modern Python with type hints
- **SQLAlchemy 2.0**: Async ORM with PostgreSQL
- **Pydantic v2**: Data validation
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: E5-multilingual embeddings

### AI/ML Stack
- **Mistral 7B**: Open-source LLM via Ollama
- **RAG Pipeline**: Document retrieval and generation
- **E5-Large**: Multilingual embeddings (1024 dims)
- **Ollama**: Local LLM serving

### Infrastructure
- **PostgreSQL 15**: Primary database
- **Docker**: Containerization
- **Nginx**: Reverse proxy (production)
- **Redis**: Caching (optional)

## Service Architecture

### 1. RAG Service
Handles document retrieval and AI-powered responses:
- Semantic search with ChromaDB
- Context-aware response generation
- German language optimization
- Streaming response support

### 2. Document Service
Manages document lifecycle:
- PDF/TXT to Markdown conversion
- Batch processing with deduplication
- PostgreSQL-based metadata storage
- Unified storage system

### 3. Analytics Service
Provides insights for Bachelor thesis:
- Document processing metrics
- System performance tracking
- CSV export for scientific analysis
- Real-time monitoring

## Data Flow

### Q&A Request Flow
1. User submits question in frontend
2. Request sent to `/api/v1/qa/chat` endpoint
3. RAG service performs semantic search
4. Relevant documents retrieved from ChromaDB
5. Context sent to Mistral 7B for response
6. Streaming response sent back to user

### Document Processing Flow
1. User uploads document via UI
2. File saved to unified storage
3. Background task queued for processing
4. Document converted to Markdown
5. Text chunks created with overlap
6. Embeddings generated and stored
7. Metadata saved to PostgreSQL

## Security Considerations

- CORS configured for localhost only
- Environment-based configuration
- Secure file upload validation
- SQL injection prevention via ORM
- Rate limiting on API endpoints
- Input sanitization throughout

## Performance Optimizations

- Async/await throughout backend
- Connection pooling for PostgreSQL
- Semaphore-limited batch processing
- Efficient vector similarity search
- Response streaming for LLM
- Frontend lazy loading

## Monitoring & Observability

- Request/response middleware logging
- Performance metrics collection
- Health check endpoints
- Error tracking and reporting
- System resource monitoring