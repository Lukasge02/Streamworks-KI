# StreamWorks-KI Project Context

## Project Overview
StreamWorks-KI ist ein RAG (Retrieval-Augmented Generation) System für eine Bachelorarbeit, das deutsche Fragen zu StreamWorks-Software beantwortet.

## Core Architecture

### Backend (`/backend`)
- **FastAPI** Application mit nur 2 aktiven Endpoints:
  - `/api/v1/qa/ask` - Perfect Q&A System
  - `/api/v1/training/upload` - Document Upload
- **Production RAG Service** - E5 Multilingual Embeddings + Mistral 7B
- **ChromaDB** Vector Database für Dokumenten-Embeddings
- **SQLite** für Metadaten und Training Files

### Frontend (`/frontend`)
- **React + TypeScript** Single Page Application
- **Vite** Build System
- **TailwindCSS** für Styling
- **Zustand** für State Management

### Key Services (Only Used)
- `production_rag_service.py` - Main RAG Pipeline
- `training_service.py` - Document Processing
- `multi_format_processor.py` - PDF/DOCX/TXT Processing
- `perfect_qa_service.py` - Q&A Interface

## Data Flow
1. User uploads documents via `/training/upload`
2. Documents processed → embeddings → ChromaDB
3. User asks question via `/qa/ask`  
4. System retrieves relevant chunks + generates answer with Mistral

## Current Status
- **Clean Codebase**: Removed all unused services, APIs, and files
- **Production Ready**: E5 embeddings + optimized Mistral prompts
- **German Optimized**: Perfect German responses for StreamWorks domain
- **Code Review Ready**: Clean, focused architecture

## Important Notes
- Only 2 API endpoints are actively used
- All other services have been cleaned up
- ChromaDB contains pre-loaded StreamWorks training data
- System designed for M4 MacBook Air (MPS optimized)