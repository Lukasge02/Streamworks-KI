# StreamWorks-KI Setup Guide v3.0

## 🎯 Schnellstart

Diese Anleitung führt Sie durch die komplette Installation und Einrichtung von StreamWorks-KI - vom ersten Download bis zur vollständig funktionsfähigen Anwendung.

### ⚡ Express-Setup (für Entwickler)

```bash
# 1. Repository klonen
git clone https://github.com/Lukasge02/Streamworks-KI.git
cd Streamworks-KI

# 2. Ollama & Mistral installieren
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral:7b-instruct

# 3. Backend Setup
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# 4. Frontend Setup (neues Terminal)
cd frontend
npm install
npm run dev

# 5. Browser öffnen: http://localhost:3000
```

---

## 📋 System-Anforderungen

### Minimale Anforderungen
- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **RAM**: 8GB (12GB+ empfohlen für Mistral 7B)
- **Speicher**: 15GB freier Speicherplatz
- **CPU**: 4+ Cores (Intel/AMD x64, Apple M1/M2)
- **Internet**: Für initiale Model-Downloads

### Empfohlene Anforderungen
- **RAM**: 16GB+
- **Speicher**: 25GB+ (für mehrere Models)
- **GPU**: NVIDIA GPU mit CUDA (optional, für bessere Performance)
- **SSD**: Für bessere Model-Loading Performance

---

## 🛠️ Software-Voraussetzungen

### 1. Python 3.9+
```bash
# Überprüfen
python3 --version

# Installation (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip

# Installation (macOS mit Homebrew)
brew install python@3.9

# Installation (Windows)
# Download von https://python.org/downloads/
```

### 2. Node.js 18+
```bash
# Überprüfen
node --version
npm --version

# Installation (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Installation (macOS mit Homebrew)
brew install node@18

# Installation (Windows)
# Download von https://nodejs.org/
```

### 3. Git
```bash
# Überprüfen
git --version

# Installation (Ubuntu/Debian)
sudo apt install git

# Installation (macOS)
# Bereits vorinstalliert oder über Xcode Command Line Tools
xcode-select --install

# Installation (Windows)
# Download von https://git-scm.com/
```

---

## 🧠 Ollama & Mistral 7B Installation

### Ollama Installation

**Linux/macOS:**
```bash
# Automatische Installation
curl -fsSL https://ollama.ai/install.sh | sh

# Ollama als Service starten
ollama serve
```

**Windows:**
```bash
# Download von https://ollama.ai/download/windows
# Installer ausführen und den Anweisungen folgen
```

### Mistral 7B Model Download

```bash
# Model herunterladen (ca. 4.1GB)
ollama pull mistral:7b-instruct

# Installation verifizieren
ollama list

# Test-Chat (optional)
ollama run mistral:7b-instruct
```

**Erwartete Ausgabe:**
```
NAME                    ID              SIZE    MODIFIED
mistral:7b-instruct     f974a74358d6    4.1GB   2 hours ago
```

### Ollama Konfiguration

**Speicher-Optimierung (.ollama/config.json):**
```json
{
  "num_ctx": 2048,
  "num_predict": 512,
  "temperature": 0.7,
  "top_p": 0.9
}
```

---

## 📂 Projekt Setup

### 1. Repository klonen

```bash
# HTTPS
git clone https://github.com/Lukasge02/Streamworks-KI.git

# SSH (empfohlen für Entwickler)
git clone git@github.com:Lukasge02/Streamworks-KI.git

cd Streamworks-KI
```

### 2. Projekt-Struktur verstehen

```
StreamWorks-KI/
├── backend/                # FastAPI Backend
├── frontend/               # React Frontend  
├── Training Data/          # Beispiel-Trainingsdaten
├── CLAUDE.md              # AI Assistant Kontext
├── TECHNICAL_DOCUMENTATION.md
├── API_DOCUMENTATION.md
└── SETUP_GUIDE.md         # Diese Datei
```

---

## 🔧 Backend Installation & Konfiguration

### 1. Python Virtual Environment

```bash
cd backend

# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren (Linux/macOS)
source venv/bin/activate

# Aktivieren (Windows)
venv\Scripts\activate

# Überprüfen
which python
which pip
```

### 2. Dependencies installieren

```bash
# Requirements installieren
pip install -r requirements.txt

# Überprüfung der wichtigsten Pakages
python -c "import fastapi, langchain, chromadb, sentence_transformers; print('✅ All packages installed')"
```

### 3. Umgebungsvariablen (Optional)

**`.env` Datei erstellen:**
```bash
cd backend
cat > .env << EOF
# Core Settings
PROJECT_NAME=StreamWorks-KI
ENV=development
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./streamworks_ki.db

# Service Toggles
RAG_ENABLED=true
LLM_ENABLED=true
XML_GENERATION_ENABLED=false

# Mistral Settings
MISTRAL_MODEL=mistral:7b-instruct
MISTRAL_BASE_URL=http://localhost:11434

# RAG Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB_PATH=data/vector_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# File Upload
MAX_FILE_SIZE=52428800
ALLOWED_EXTENSIONS=["txt", "md", "csv", "bat", "ps1", "xml", "xsd"]

# Conversation Memory
SESSION_TIMEOUT_HOURS=24
MAX_MESSAGES_PER_SESSION=50
CONTEXT_WINDOW_SIZE=3
EOF
```

### 4. Datenbank & Verzeichnisse initialisieren

```bash
# Automatische Initialisierung beim ersten Start
# Verzeichnisse werden automatisch erstellt:
# - data/training_data/originals/
# - data/training_data/optimized/
# - data/vector_db/
# - data/conversations/
```

### 5. Backend starten

```bash
# Development Server mit Auto-Reload
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Produktionsserver (ohne Reload)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Erfolgreiche Ausgabe:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
2025-07-04 12:00:00,000 - app.main - INFO - 🚀 Starting StreamWorks-KI Backend
2025-07-04 12:00:00,000 - app.main - INFO - ✅ Database initialized
2025-07-04 12:00:00,000 - app.main - INFO - ✅ RAG Service ready - 0 documents indexed
2025-07-04 12:00:00,000 - app.main - INFO - ✅ Mistral 7B Service ready
```

### 6. Backend Health Check

```bash
# API testen
curl http://localhost:8000/

# Erwartete Antwort
{
  "status": "healthy",
  "version": "3.0.0",
  "services": {
    "rag_service": "healthy",
    "mistral_llm": "healthy"
  }
}
```

---

## 🎨 Frontend Installation & Konfiguration

### 1. Frontend Dependencies

```bash
# Neues Terminal öffnen
cd frontend

# Node Modules installieren
npm install

# Überprüfung der Installation
npm list --depth=0
```

### 2. Frontend starten

```bash
# Development Server mit Hot-Reload
npm run dev

# Erwartete Ausgabe:
# ➜  Local:   http://localhost:3000/
# ➜  Network: use --host to expose
```

### 3. Frontend Health Check

1. Browser öffnen: `http://localhost:3000`
2. StreamWorks-KI Interface sollte laden
3. Chat-Interface sollte sichtbar sein
4. Training Data Tab sollte verfügbar sein

---

## 📊 Erste Schritte & Funktionstest

### 1. Training Data Upload

**Beispieldaten hochladen:**
```bash
# Im Hauptverzeichnis
cd "Training Data/TXT"

# Dateien sind bereits verfügbar:
# - streamworks_faq.txt
# - csv_verarbeitung_tipps.txt
# - powershell_streamworks.txt
# etc.
```

**Via Web-Interface:**
1. Training Data Tab öffnen
2. "Einzeln" oder "Batch" Upload wählen
3. TXT-Dateien aus `Training Data/TXT/` hochladen
4. Automatische TXT→MD Konvertierung beobachten
5. RAG-Indexierung abwarten

### 2. Chat-System testen

**Beispiel-Fragen:**
```
1. "Was ist StreamWorks?"
2. "Wie erstelle ich einen Batch-Job?"
3. "Wie behebe ich Fehler in der CSV-Verarbeitung?"
4. "Zeige mir PowerShell-Beispiele für StreamWorks"
```

**Erwartetes Verhalten:**
- Intelligente, deutsche Antworten
- Quellenangaben aus hochgeladenen Dokumenten
- Conversation Memory zwischen Fragen
- Query Expansion für bessere Suche

### 3. Advanced Features testen

**Intelligent Search:**
```bash
# Query Expansion testen
curl -X POST http://localhost:8000/api/v1/search/expand \
  -H "Content-Type: application/json" \
  -d '{"query": "batch fehler"}'

# Search Suggestions testen
curl -X POST http://localhost:8000/api/v1/search/suggestions \
  -H "Content-Type: application/json" \
  -d '{"partial_query": "ba"}'
```

**Conversation Memory:**
```bash
# Conversations auflisten
curl http://localhost:8000/api/v1/conversations/

# Conversation Stats
curl http://localhost:8000/api/v1/conversations/stats
```

---

## 🔧 Troubleshooting

### Häufige Probleme & Lösungen

#### 1. Ollama/Mistral Probleme

**Problem:** `Mistral Service nicht verfügbar`
```bash
# Ollama Status prüfen
ollama list
ollama ps

# Ollama Service starten
ollama serve

# Mistral Model erneut pullen
ollama pull mistral:7b-instruct

# Test
ollama run mistral:7b-instruct "Hallo, wie geht es dir?"
```

#### 2. Backend Startup Fehler

**Problem:** `ChromaDB Fehler`
```bash
# Vector Database zurücksetzen
rm -rf backend/data/vector_db/
# Backend neu starten - erstellt DB automatisch neu
```

**Problem:** `Port bereits in Verwendung`
```bash
# Prozess finden und beenden
lsof -i :8000
kill -9 <PID>

# Alternativen Port verwenden
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

#### 3. Frontend Probleme

**Problem:** `npm install Fehler`
```bash
# Node Modules löschen und neu installieren
rm -rf node_modules package-lock.json
npm install

# Cache leeren
npm cache clean --force
```

**Problem:** `API Connection Fehler`
```bash
# Backend-Verbindung prüfen
curl http://localhost:8000/

# CORS-Probleme in vite.config.ts prüfen
```

#### 4. Performance Probleme

**Mistral zu langsam:**
```bash
# Ollama Konfiguration optimieren
# Weniger Context für bessere Performance
echo '{"num_ctx": 1024}' > ~/.ollama/config.json
```

**Speicher-Probleme:**
```bash
# System-Speicher prüfen
free -h  # Linux
vm_stat # macOS

# Mistral Model quantization (optional)
ollama pull mistral:7b-instruct-q4_0
```

### Debug-Logs aktivieren

**Backend:**
```bash
# Detaillierte Logs
LOG_LEVEL=DEBUG python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
# Browser Console für detaillierte Logs öffnen (F12)
```

---

## 🚀 Production Deployment

### 1. Environment Setup

**Production .env:**
```bash
ENV=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["https://yourdomain.com"]
DATABASE_URL=postgresql://user:pass@localhost/streamworks_ki
```

### 2. Security Konfiguration

```bash
# HTTPS Zertifikate
# Reverse Proxy (nginx/Apache)
# Firewall Konfiguration
# API Rate Limiting aktivieren
```

### 3. Service Management

**Systemd Service (Linux):**
```ini
[Unit]
Description=StreamWorks-KI Backend
After=network.target

[Service]
Type=simple
User=streamworks
WorkingDirectory=/opt/streamworks-ki/backend
ExecStart=/opt/streamworks-ki/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Monitoring Setup

```bash
# Health Check Endpoints nutzen:
# /api/v1/training/health
# /api/v1/search/health
# /api/v1/conversations/health
```

---

## 📚 Nützliche Befehle

### Development

```bash
# Backend Tests (falls implementiert)
cd backend && python -m pytest

# Frontend Build
cd frontend && npm run build

# Code Quality
cd backend && flake8 app/
cd frontend && npm run lint

# Dependency Updates
cd backend && pip list --outdated
cd frontend && npm outdated
```

### Maintenance

```bash
# Database Backup
cp backend/streamworks_ki.db backup/

# Conversation Cleanup
curl -X POST http://localhost:8000/api/v1/conversations/cleanup

# Vector DB Stats
curl http://localhost:8000/api/v1/training/chromadb-stats

# System Health Check
curl http://localhost:8000/
```

### Performance Monitoring

```bash
# Response Times messen
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Test"}'

# Speicher-Verwendung
docker stats streamworks-ki # falls Docker verwendet
ps aux | grep uvicorn
```

---

## 🎓 Nächste Schritte

### Für Entwickler
1. 📖 [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md) lesen
2. 🔌 [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) studieren
3. 🧠 [CLAUDE.md](./CLAUDE.md) für AI-Assistant Kontext

### Für Benutzer
1. 📚 Training Data aus `Training Data/` hochladen
2. 💬 Chat-System mit verschiedenen Fragen testen
3. 📤 Batch Upload für mehrere Dateien ausprobieren
4. 🔍 Intelligent Search Features erkunden

### Erweiterte Features
1. 🎯 Custom Training Data für spezifische Use Cases
2. ⚙️ XML Stream Generator für automatisierte Workflows
3. 📊 Advanced Analytics über Conversation API
4. 🔧 Custom Synonyme für Intelligent Search

---

## 🆘 Support & Hilfe

### Dokumentation
- **Technische Details**: [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md)
- **API Reference**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Projekt Kontext**: [CLAUDE.md](./CLAUDE.md)

### Community & Issues
- **GitHub Repository**: [Lukasge02/Streamworks-KI](https://github.com/Lukasge02/Streamworks-KI)
- **Issues melden**: GitHub Issues verwenden
- **Feature Requests**: GitHub Discussions

### Logs & Debugging
- **Backend Logs**: Console Output von uvicorn
- **Frontend Logs**: Browser Developer Console (F12)
- **Service Health**: Health Check Endpoints nutzen

---

**Version:** 3.0  
**Letztes Update:** Juli 2025  
**Autor:** Ravel-Lukas Geck  
**Projekt:** StreamWorks-KI Bachelorarbeit

**🎉 Viel Erfolg mit StreamWorks-KI!**