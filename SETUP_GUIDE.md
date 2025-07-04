# StreamWorks-KI - Setup Guide für Entwickler

## 🚀 Schnellstart (5 Minuten)

### Voraussetzungen
```bash
# System Requirements
- Python 3.8+ (empfohlen: 3.9+)
- Node.js 18+ mit npm
- Git
- 8GB+ RAM (für Mistral 7B)
- macOS/Linux (Windows via WSL2)

# Optional aber empfohlen
- Ollama für lokale LLM Inference
- Docker für containerisierte Entwicklung
```

### 1. Repository klonen
```bash
git clone https://github.com/Lukasge02/Streamworks-KI.git
cd Streamworks-KI
```

### 2. Backend Setup
```bash
cd backend/

# Python Dependencies installieren
pip install -r requirements.txt

# Datenbank initialisieren (automatisch beim ersten Start)
# Keine manuellen Schritte nötig

# Backend starten
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup (Neues Terminal)
```bash
cd frontend/

# Dependencies installieren
npm install

# Development Server starten
npm run dev
```

### 4. Zugriff
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Dokumentation**: http://localhost:8000/docs
- **Interaktive API**: http://localhost:8000/redoc

## 🔧 Detaillierte Einrichtung

### Backend-Konfiguration

#### Environment Variables (.env)
```bash
# Erstelle .env im backend/ Verzeichnis
cd backend/
cat > .env << EOF
ENV=development
DATABASE_URL=sqlite:///./streamworks_ki.db
RAG_ENABLED=true
LLM_ENABLED=true
XML_GENERATION_ENABLED=false
FORCE_GERMAN_RESPONSES=true
LOG_LEVEL=INFO
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct
EOF
```

#### Ollama Setup (Optional für vollständige LLM-Funktionalität)
```bash
# Ollama installieren (macOS)
curl https://ollama.ai/install.sh | sh

# Mistral 7B Model herunterladen (einmalig)
ollama pull mistral:7b-instruct

# Ollama Service starten
ollama serve  # Läuft auf Port 11434

# Test
curl http://localhost:11434/api/tags
```

#### Datenbank & Vector Store
```bash
# Automatische Initialisierung beim ersten Backend-Start
# Manuelle Initialisierung (falls nötig):

# SQLite Datenbank
python -c "
from app.models.database import init_db
import asyncio
asyncio.run(init_db())
"

# ChromaDB Vector Store (automatisch erstellt)
# Pfad: backend/data/vector_db/
```

### Frontend-Konfiguration

#### Umgebungsspezifische Settings
```typescript
// frontend/src/services/apiService.ts
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Für Production:
// const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000/api/v1';
```

#### Development vs Production Build
```bash
# Development (Hot Reload)
npm run dev

# Production Build
npm run build
npm run preview

# Linting
npm run lint
```

## 📁 Projekt-Struktur Verstehen

### Backend-Architektur
```
backend/
├── app/
│   ├── main.py                 # FastAPI App & Startup
│   ├── api/v1/                # REST API Endpoints
│   │   ├── chat.py            # RAG Q&A Endpoints
│   │   ├── xml_generation.py  # XML Generator API
│   │   └── training.py        # File Upload/Management
│   ├── services/              # Business Logic Layer
│   │   ├── rag_service.py     # ChromaDB + LangChain
│   │   ├── xml_generator.py   # LoRA XML Generation
│   │   └── mistral_rag_service.py  # Mistral Integration
│   ├── core/                  # Configuration
│   │   └── config.py          # Settings Management
│   └── models/                # Database & Schemas
│       ├── database.py        # SQLAlchemy Models
│       └── schemas.py         # Pydantic Schemas
├── data/                      # Data Storage
│   ├── training_data/         # Uploaded Files
│   └── vector_db/            # ChromaDB Storage
└── requirements.txt           # Python Dependencies
```

### Frontend-Architektur
```
frontend/
├── src/
│   ├── App.tsx               # Main App Component
│   ├── components/           # React Components
│   │   ├── Chat/            # Chat Interface
│   │   │   └── DualModeChat.tsx  # Main Chat Component
│   │   ├── TrainingData/    # File Upload UI
│   │   │   └── TrainingDataTabV2Fixed.tsx  # Active Training Tab
│   │   └── StreamGenerator/ # XML Generator UI
│   ├── services/            # API Service Layer
│   │   └── apiService.ts    # Backend Communication
│   ├── store/               # State Management
│   │   └── appStore.ts      # Zustand Store
│   └── types/               # TypeScript Types
│       └── index.ts         # Shared Types
├── package.json             # Dependencies & Scripts
└── vite.config.ts          # Build Configuration
```

## 🧪 Testing & Validierung

### Backend-Tests
```bash
cd backend/

# Health Check
curl http://localhost:8000/health

# API-Funktionen testen
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Was ist StreamWorks?", "session_id": "test"}'

# Training Data Upload testen
curl -X POST http://localhost:8000/api/v1/training/upload \
  -F "file=@test.txt" \
  -F "category=help_data"
```

### Frontend-Tests
```bash
cd frontend/

# Development Server verfügbar?
curl http://localhost:3001

# Build-Test
npm run build

# Linting
npm run lint
```

### Integration-Tests
```bash
# Vollständiger Stack-Test:
# 1. Backend läuft auf :8000
# 2. Frontend läuft auf :3001
# 3. Chat-Interface funktional
# 4. File-Upload funktional
# 5. API-Kommunikation korrekt
```

## 🔄 Development Workflow

### Typischer Entwicklungstag
```bash
# 1. Services starten
cd backend/ && python -m uvicorn app.main:app --reload &
cd frontend/ && npm run dev &

# 2. Code ändern (Hot Reload aktiv)
# Backend: Automatisches Reload bei .py Änderungen
# Frontend: Automatisches Reload bei .tsx/.ts Änderungen

# 3. Testing
# API: http://localhost:8000/docs
# UI: http://localhost:3001

# 4. Logs überwachen
tail -f backend/backend.log  # Falls Log-File existiert
# Oder Console-Output beobachten
```

### Code-Änderungen

#### Backend-Änderungen
```python
# Neue API-Endpoints: app/api/v1/
# Business Logic: app/services/
# Configuration: app/core/config.py
# Database: app/models/database.py

# Nach Schema-Änderungen:
cd backend/
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

#### Frontend-Änderungen
```typescript
// Neue Components: src/components/
// API Integration: src/services/apiService.ts
// State Management: src/store/appStore.ts
// Types: src/types/index.ts

// Nach Type-Änderungen:
npm run build  # Type-Check
```

## 🚨 Troubleshooting

### Häufige Probleme & Lösungen

#### Backend startet nicht
```bash
# Problem: ModuleNotFoundError
# Lösung: Dependencies installieren
pip install -r requirements.txt

# Problem: Port 8000 already in use
# Lösung: Port wechseln oder Process killen
lsof -ti:8000 | xargs kill -9
# Oder anderen Port verwenden:
python -m uvicorn app.main:app --reload --port 8001
```

#### Frontend startet nicht
```bash
# Problem: npm install Fehler
# Lösung: Cache löschen
rm -rf node_modules package-lock.json
npm install

# Problem: Port 3000/3001 in use
# Lösung: Vite findet automatisch freien Port
# Oder manuell:
npm run dev -- --port 3002
```

#### RAG-Service Fehler
```bash
# Problem: ChromaDB Initialisierung
# Lösung: Vector DB neu erstellen
rm -rf backend/data/vector_db/
# Backend neu starten (erstellt DB automatisch)

# Problem: Embedding Model Download
# Lösung: Manueller Download
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
"
```

#### Mistral/Ollama Probleme
```bash
# Problem: Ollama nicht erreichbar
# Lösung: Service prüfen
ps aux | grep ollama
ollama serve

# Problem: Model nicht verfügbar
# Lösung: Model herunterladen
ollama list
ollama pull mistral:7b-instruct

# Problem: Connection refused
# Lösung: Host/Port prüfen
curl http://localhost:11434/api/tags
```

### Performance-Probleme

#### Langsame RAG-Antworten
```python
# backend/app/core/config.py
RAG_CHUNK_SIZE = 300        # Reduzieren für Speed
RAG_TOP_K = 3               # Weniger Dokumente
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Schnellster Model
```

#### Speicher-Probleme (Mistral 7B)
```python
# backend/app/core/config.py
MODEL_THREADS = 4           # Weniger Threads
MODEL_BATCH_SIZE = 1        # Einzelne Requests
# Oder LLM deaktivieren:
LLM_ENABLED = false
```

## 🎯 Nächste Schritte

### Nach erfolgreichem Setup
1. **API testen**: Alle Endpoints in http://localhost:8000/docs
2. **Chat ausprobieren**: Q&A mit StreamWorks-Fragen
3. **Training Data**: Eigene Dokumente hochladen
4. **Code verstehen**: TECHNICAL_DOCUMENTATION.md lesen
5. **Entwickeln**: Eigene Features implementieren

### Empfohlene Entwicklungsreihenfolge
1. **Frontend-Features**: UI-Verbesserungen, neue Components
2. **API-Extensions**: Neue Endpoints, erweiterte Funktionen
3. **LoRA-Training**: XML-Generator Fine-Tuning
4. **Performance**: Optimierungen, Caching
5. **Production**: Deployment, Monitoring

## 📚 Zusätzliche Ressourcen

### Dokumentation
- **API-Docs**: http://localhost:8000/docs (automatisch generiert)
- **Technical Docs**: `TECHNICAL_DOCUMENTATION.md`
- **Code-Kommentare**: Inline-Dokumentation in Services

### Useful Commands
```bash
# Backend
pip freeze > requirements.txt    # Dependencies exportieren
alembic history                  # Migration History
python -m pytest               # Tests ausführen (falls vorhanden)

# Frontend  
npm audit                       # Security Audit
npm outdated                    # Veraltete Dependencies
npm run build -- --watch       # Build mit Watch Mode

# System
docker ps                       # Container Status (falls Docker verwendet)
htop                           # System Resources Monitor
```

### Support & Community
- **GitHub**: https://github.com/Lukasge02/Streamworks-KI
- **Issues**: Bei Problemen GitHub Issues erstellen
- **Discussions**: GitHub Discussions für Fragen

---

**🎯 Ziel**: In 5 Minuten voll funktionsfähiges Entwicklungsumgebung**  
**📧 Support**: Bei Problemen GitHub Issues erstellen**  
**🔄 Updates**: Dieses Setup-Guide wird regelmäßig aktualisiert**