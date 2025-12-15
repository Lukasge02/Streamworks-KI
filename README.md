# Streamworks-KI: Intelligent XML Generator

> **AI-powered assistant for generating Streamworks XML definitions.**
> Modern FastAPI Backend + Next.js Frontend.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.5.2-000000?style=flat&logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://www.python.org/)

---

## 🎯 **What is Streamworks-KI?**

Streamworks-KI is an intelligent tool designed to simplify the creation of Streamworks job streams. It allows users to describe their desired workflow in natural language, and the AI converts it into valid, structured XML parameters.

**Key Features:**
- **💬 AI Chat Interface** - Describe your stream in plain German.
- **⚡ Real-time Parameter Extraction** - AI extracts structural data from conversation.
- **📄 Live XML Preview** - Interactive Monaco Editor to view and edit generated XML.
- **✅ Validation** - Automatic structure and dependency checking.
- **💾 Persistence** - Sessions stored in Supabase (optional).

### 🏛️ **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   Next.js 15    │◄──►│   FastAPI       │◄──►│   Supabase      │
│   TypeScript    │    │   OpenAI /      │    │   (PostgreSQL)  │
│                 │    │   Instructor    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🚀 **Quick Start**

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **OpenAI API Key**

### 1. Setup
```bash
make setup
```
This installs backend dependencies and frontend packages, and copies `.env.example` to `.env`.

### 2. Configuration
Edit `.env` and add your keys:
```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=... (optional)
SUPABASE_KEY=... (optional)
```

### 3. Start Development
```bash
make dev
```
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:3000

### 4. Docker Services (Qdrant + MinIO)
```bash
# Start Qdrant + MinIO (default profile)
docker compose up -d

# Or start everything including backend
docker compose --profile full up -d

# Or only Qdrant (minimal)
docker compose --profile db-only up -d
```

### 5. Health Checks
```bash
curl http://localhost:8000/health           # Quick check
curl http://localhost:8000/health/detailed  # Component status (Qdrant, MinIO, Supabase)
```

### 6. Run Tests
```bash
make test
```

---

## 📁 **Project Structure**

```
Streamworks-KI/
├── 💻 backend/
│   ├── main.py               # Application Entry Point
│   ├── config.py             # Configuration
│   ├── domains/              # Business Logic Domains
│   │   ├── chat/             # Chat & Session Logic
│   │   └── xml/              # XML Generation & Validation
│   ├── services/             # Core Services
│   │   ├── ai/               # AI Parameter Extraction (Instructor)
│   │   └── xml_generator.py  # Jinja2 Template Engine
│   ├── templates/            # HTML Templates (optional)
│   ├── tests/                # Unit Tests
│   └── requirements.txt      # Python Dependencies
│
├── 🎨 frontend/
│   ├── app/                  # Next.js App Router
│   │   ├── components/       # Shared Components (Header, etc.)
│   │   ├── preview/          # XML Preview Page
│   │   └── page.tsx          # Main Chat Interface
│   └── package.json
│
└── 📚 knowledge/
    └── templates/            # XML Jinja2 Templates
```

---

## 📄 **License**

This project is part of a Bachelor Thesis.
