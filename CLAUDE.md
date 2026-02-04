# CLAUDE.md

## Project Overview

**Streamworks-KI v2** -- Kompletter Neuaufbau als schlanker Monolith.
Zwei Features: **Stream Wizard** (7-Step XML-Generator) + **RAG Chat** (Dokument-Q&A mit Hybrid Search).

Vorher: 600+ Dateien, LlamaIndex, torch, DDD, Knowledge Graph, Testing-Module etc.
Jetzt: **~66 Dateien**, nur OpenAI SDK direkt, flache Struktur.

## Tech Stack

| Komponente | Technologie |
|---|---|
| Backend | FastAPI + Python 3.13 |
| Frontend | Next.js 15.5 + TypeScript + TailwindCSS |
| State Management | React Query (server) + Zustand (client) |
| LLM | OpenAI GPT-4o / GPT-4o-mini (direkt, kein LlamaIndex) |
| Datenbank | Supabase (PostgreSQL) -- mit In-Memory Fallback |
| Vector DB | Qdrant |
| File Storage | MinIO |
| XML Templating | Jinja2 |

## Aktueller Status (Stand: 2026-02-04)

### Was funktioniert (Browser-getestet am 2026-02-04)
- Backend startet, Health-Endpoint antwortet
- Wizard Session CRUD (erstellen, lesen, Steps speichern, loeschen)
- **AI-Analyse**: OpenAI GPT-4o extrahiert 10+ Parameter aus Freitext (95% Konfidenz)
- **XML-Generierung**: Vollstaendige StreamWorks-XML mit GECK003_ Prefix, SAP-Properties, Kontakt-Split
- Dropdown-Optionen (Agents, Schedules, SAP-Systeme etc.)
- Frontend baut und alle 4 Seiten laden (/wizard, /chat, /streams, /xml-editor)
- In-Memory Fallback wenn Supabase nicht erreichbar
- **Wizard End-to-End Flow**: Alle 7 Steps im Browser durchgetestet
- Streams-Uebersicht mit Karten-Grid, SAP-Badge, Session-Verwaltung
- **XML-Editor Seite**: Editierbarer Monaco Editor, Download, Kopieren, Neu-Generierung mit Warnung
- **AI-Parameter-Verteilung**: 25+ Parameter auf alle Steps (Kontakt, SAP, Zeitplan etc.)
- **Bidirektionales Field-Mapping**: Frontend-Feldnamen <-> Backend-Template-Variablen
- **Session-Hydration**: Gespeicherte Wizard-Daten werden korrekt nach Reload geladen
- Navigation: Wizard -> Editor, Streams -> Editor, Editor -> Wizard (bidirektional)

### Was noch getestet/behoben werden muss
- RAG Chat -- braucht Qdrant + MinIO (make infra)
- Dokument-Upload und -Verarbeitung
- SSE Streaming Chat

### Behobene Bugs
- **Hydration-Key Mismatch**: Frontend nutzte `step${i}` statt `step_${i}` -- gespeicherte Sessions konnten Daten nicht laden
- **AI-Parameter-Verteilung**: Nur 4 von 25+ Parametern wurden aus AI-Analyse verteilt -- jetzt vollstaendig ueber alle Steps
- **Backend Field-Mappings**: Fehlende Mappings (documentation, agent, priority, schedule_frequency, phone, overwrite) in xml_generator.py ergaenzt

### Bekannte Issues
- Supabase-Projekt (vbtozorzccsbxsypfdbf) ist offline/geloescht -- DNS NXDOMAIN
  -> db.py faellt automatisch auf In-Memory Storage zurueck
  -> Daten gehen bei Backend-Neustart verloren
  -> Fuer Produktion: Neues Supabase-Projekt anlegen + Migrations ausfuehren
- AI-Schedule-Mapping: AI gibt Umlaute zurueck ("taeglich" vs "täglich"), Select-Match schlaegt fehl
  -> Workaround: Frequenz manuell im Dropdown waehlen
  -> Fix: Umlaut-Normalisierung in onApplyParameters einbauen

## Development Commands

```bash
# Infrastructure (Qdrant + MinIO)
make infra

# Backend (eigenes Terminal)
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py                    # http://localhost:8000

# Frontend (eigenes Terminal)
cd frontend
npm install
npm run dev                       # http://localhost:3000

# Schnelltest
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/wizard/sessions
```

## Projektstruktur

```
streamworks-ki/
├── .env                          # Credentials (nicht in Git)
├── .env.example                  # Template
├── .gitignore
├── CLAUDE.md                     # <-- diese Datei
├── Makefile
├── docker-compose.yml            # Qdrant + MinIO + Backend + Frontend
│
├── backend/
│   ├── main.py                   # FastAPI app + CORS + 5 Router
│   ├── config.py                 # Pydantic Settings (.env, extra=ignore)
│   ├── requirements.txt          # 17 Packages (kein torch/LlamaIndex)
│   ├── Dockerfile
│   │
│   ├── routers/
│   │   ├── health.py             # GET /health
│   │   ├── wizard.py             # Session CRUD + AI Analyze + XML Generate
│   │   ├── rag.py                # Chat + SSE Streaming + Session Management
│   │   ├── documents.py          # Upload, List, Delete
│   │   └── options.py            # Dropdown-Werte
│   │
│   ├── services/
│   │   ├── db.py                 # Supabase Client + In-Memory Fallback
│   │   ├── parameter_extractor.py  # OpenAI Structured Output
│   │   ├── xml_generator.py      # Jinja2 XML Rendering
│   │   ├── vector_store.py       # Qdrant + OpenAI Embeddings
│   │   ├── hybrid_search.py      # BM25 + Semantic + RRF
│   │   ├── reranker.py           # OpenAI-basiertes Reranking
│   │   ├── document_processor.py # Parse + Chunk + Embed Pipeline
│   │   ├── rag_service.py        # Query-Orchestrierung + LLM
│   │   ├── chat_session_service.py # Chat CRUD
│   │   └── file_storage.py       # MinIO Wrapper
│   │
│   ├── models/
│   │   ├── wizard.py             # WizardSession, AnalyzeRequest/Response
│   │   ├── rag.py                # ChatRequest, ChatResponse, Source
│   │   └── documents.py          # UploadResponse, DocumentInfo
│   │
│   ├── config/
│   │   └── parameters.yaml       # 30 Parameter in 7 Gruppen (1:1 aus v1)
│   │
│   ├── templates/
│   │   └── master_template.xml   # Jinja2 XML Template (1:1 aus v1)
│   │
│   └── migrations/
│       ├── 001_sessions.sql
│       ├── 002_streams.sql
│       ├── 003_dropdown_options.sql
│       ├── 004_chat.sql
│       └── 005_seed_data.sql
│
└── frontend/
    ├── package.json              # Next.js 15, React 19, TanStack Query
    ├── tsconfig.json             # Strict, @/* -> app/*, @/lib/* -> lib/*
    ├── tailwind.config.ts        # Arvato Branding (#003366)
    ├── next.config.ts
    ├── Dockerfile
    │
    ├── app/
    │   ├── layout.tsx            # Root + QueryClient Provider
    │   ├── page.tsx              # Redirect -> /wizard
    │   ├── globals.css           # Tailwind + Arvato CSS Variables
    │   │
    │   ├── wizard/
    │   │   ├── page.tsx          # 7-Step Wizard mit Step-Indikator
    │   │   └── components/
    │   │       ├── WizardStep0.tsx  # KI-Beschreibungsanalyse
    │   │       ├── WizardStep1.tsx  # Grundinfos (Name, Beschreibung)
    │   │       ├── WizardStep2.tsx  # Kontaktdaten
    │   │       ├── WizardStep3.tsx  # Job-Typ Auswahl (3 Karten)
    │   │       ├── WizardStep4.tsx  # Job-spezifische Parameter
    │   │       ├── WizardStep5.tsx  # Zeitplan
    │   │       └── WizardStep6.tsx  # Preview + XML Export (Monaco)
    │   │
    │   ├── chat/
    │   │   ├── page.tsx          # RAG Chat mit Streaming
    │   │   └── components/
    │   │       ├── ChatSidebar.tsx  # Sessions + Dokument-Upload
    │   │       └── DocumentPreview.tsx  # Quellen-Modal
    │   │
    │   ├── streams/
    │   │   └── page.tsx          # Session-Dashboard (Karten-Grid)
    │   │
    │   ├── xml-editor/
    │   │   └── page.tsx          # Standalone XML-Editor (Monaco, editierbar)
    │   │
    │   └── components/
    │       ├── AppLayout.tsx     # Header + Sidebar Shell
    │       ├── Header.tsx        # Logo "Streamworks-KI v2.0"
    │       ├── Sidebar.tsx       # Navigation (Wizard, Streams, Chat)
    │       └── ui/               # Button, Card, Dialog, Input, Badge, Toast
    │
    └── lib/
        ├── utils.ts              # cn() Helper
        ├── api/
        │   ├── config.ts         # apiFetch Wrapper
        │   ├── wizard.ts         # React Query Hooks (Wizard)
        │   └── chat.ts           # React Query Hooks (Chat)
        └── hooks/
            └── useStreamingChat.ts  # SSE Streaming Hook

## API Endpoints

### Wizard (/api/wizard)
| Method | Path | Beschreibung |
|--------|------|-------------|
| POST | /sessions | Neue Session erstellen |
| GET | /sessions | Alle Sessions listen |
| GET | /sessions/{id} | Session abrufen |
| PUT | /sessions/{id}/steps | Step-Daten speichern |
| DELETE | /sessions/{id} | Session loeschen |
| POST | /analyze | KI-Beschreibungsanalyse |
| POST | /generate-xml | XML generieren |

### RAG Chat (/api/rag)
| Method | Path | Beschreibung |
|--------|------|-------------|
| POST | /chat | Chat (synchron) |
| POST | /chat/stream | Chat (SSE Streaming) |
| GET | /sessions | Chat-Sessions listen |
| GET | /sessions/{id}/messages | Nachrichten abrufen |
| DELETE | /sessions/{id} | Chat-Session loeschen |

### Documents (/api/documents)
| Method | Path | Beschreibung |
|--------|------|-------------|
| POST | /upload | Dokument hochladen |
| GET | / | Dokumente listen |
| DELETE | /{id} | Dokument loeschen |

### Options (/api/options)
| Method | Path | Beschreibung |
|--------|------|-------------|
| GET | /categories | Kategorien listen |
| GET | /{category} | Optionen einer Kategorie |

## Architektur-Entscheidungen

| Thema | Entscheidung | Grund |
|---|---|---|
| LLM Framework | OpenAI SDK direkt | 50 Zeilen statt LlamaIndex (~200MB) |
| Reranker | OpenAI GPT-4o-mini | FlashRank hatte Dependency-Konflikte |
| Backend-Struktur | routers/ + services/ flach | MVP braucht kein DDD |
| Auth | Keine | Dev-Modus, spaeter ergaenzen |
| DB Fallback | In-Memory wenn Supabase offline | Lokale Entwicklung ohne Cloud-Abhaengigkeit |
| Pydantic Config | extra="ignore" | Frontend-Variablen (NEXT_PUBLIC_*) in .env stoeren nicht |
| Stream Prefix | GECK003_ | Automatisch prepended wenn nicht vorhanden |
| Field-Mapping | Bidirektional in xml_generator.py | Frontend-Feldnamen (z.B. `agent`) werden auf Template-Variablen (z.B. `agent_detail`) gemappt |

## Environment (.env)

```bash
# Pflicht
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co   # oder leer fuer In-Memory
SUPABASE_KEY=eyJ...                     # oder leer fuer In-Memory

# Optional (haben Defaults)
OPENAI_MODEL=gpt-4o
OPENAI_EMBED_MODEL=text-embedding-3-large
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=streamworks
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=streamworks
MINIO_SECRET_KEY=streamworks123
MINIO_BUCKET=documents
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Naechste Schritte

1. **RAG Chat fixen**: Qdrant + MinIO starten (`make infra`), Chat-Endpunkte testen
2. **Dokument-Upload**: Upload-Flow testen und debuggen
3. **SSE Streaming**: Chat-Streaming im Browser verifizieren
4. **Supabase**: Neues Projekt anlegen, Migrations ausfuehren (fuer persistente Daten)
5. **Polish**: UI-Feinschliff, Umlaut-Normalisierung in AI-Parameter-Verteilung
