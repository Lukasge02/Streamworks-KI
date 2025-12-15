# 🚀 Streamworks KI - System Überblick

## 🎯 Ziel
**Automatisierung** der Streamworks Job-Konfiguration durch **Künstliche Intelligenz**.
Brücke zwischen *natürlicher Sprache* ("Mach Backup") und *technischer Umsetzung* (XML).

## 🏗️ Architektur

```mermaid
graph TD
    User[👤 Benutzer] -- "Natürliche Sprache" --> Frontend[💻 Next.js Frontend]
    Frontend -- REST API --> Backend[⚙️ FastAPI Backend]
    
    subgraph "Backend Core"
        Auth[🔒 Auth System]
        Router[🔀 API Router]
    end
    
    subgraph "AI Engine"
        LLM[🤖 OpenAI GPT-4o]
        Instructor[🔧 Instructor Lib]
        Pydantic[✅ Pydantic Schemas]
    end
    
    subgraph "RAG System"
        Qdrant[📚 Qdrant Vector DB]
        Embedding[🧠 Text Embeddings]
    end
    
    Backend --> AI Engine
    Backend --> RAG System
```

## 🧩 Hauptkomponenten

### 1. 💻 Frontend (Next.js)
*   **Modernes UI**: React, Tailwind, Lucide Icons.
*   **Chat Interface**: Direkte Interaktion mit der KI.
*   **Visual Feedback**: Zeigt sofort, was die KI verstanden hat.

### 2. ⚙️ Backend (Python/FastAPI)
*   **KI Kern**: GPT-4o-mini für "Verstand".
*   **Struktur**: `instructor` zwingt die KI in feste Bahnen (JSON).
*   **Wissen**: RAG-System liefert Firmen-Interna (Servernamen, Prozesse).

---
> [!NOTE]
> Das System "rät" nicht einfach, sondern **extrahiert** präzise Daten und **validiert** sie gegen feste Regeln.
