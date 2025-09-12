# 🚀 Setup Guide

> **Schritt-für-Schritt Installation und Konfiguration von Streamworks-KI**  
> Von der lokalen Entwicklung bis zur Produktion - inkl. XML Wizard Setup

---

## 🎯 **Überblick**

Dieser Guide führt Sie durch die vollständige Einrichtung des Streamworks-KI RAG Systems:

- **⚡ Schnellstart** - Lokales System in 5 Minuten
- **🔧 Detaillierte Konfiguration** - Erweiterte Setup-Optionen inkl. XML Wizard
- **🤖 Ollama Integration** - Lokale LLM-Modelle für XML-Generierung
- **🐳 Docker Deployment** - Containerisierte Bereitstellung
- **🏭 Produktion Setup** - Enterprise-grade Konfiguration
- **🛠️ Troubleshooting** - Häufige Probleme und Lösungen

---

## 📋 **Systemanforderungen**

### **Minimum Requirements**
- **CPU**: 2 Cores (4+ empfohlen für AI/ML Operations)
- **RAM**: 4GB (8GB+ empfohlen für große Dokumente)
- **Storage**: 2GB verfügbarer Speicherplatz
- **Python**: 3.11+ 
- **Node.js**: 18.0+
- **Ollama**: Für lokale XML-Generierung (optional)

### **Empfohlen für Production**
- **CPU**: 8+ Cores
- **RAM**: 16GB+ 
- **Storage**: SSD mit 50GB+
- **GPU**: NVIDIA GPU für lokale AI Models (optional)
- **Ollama**: Mit Llama2/CodeLlama Modellen für XML-Generierung

---

## ⚡ **Schnellstart (5 Minuten)**

### **1. Repository klonen**
```bash
git clone <repository-url>
cd Streamworks-KI
```

### **2. Backend Setup**
```bash
cd backend

# Virtual Environment erstellen (empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder: venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Backend starten
python main.py
```

### **3. Frontend Setup** 
```bash
# Neues Terminal öffnen
cd frontend

# Node Dependencies installieren
npm install

# Development Server starten
npm run dev
```

### **4. System testen**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **XML Wizard**: http://localhost:3000/xml

✅ **Das System ist einsatzbereit!** Laden Sie ein Dokument hoch, stellen Sie Fragen, oder erstellen Sie XML-Dokumente.

---

## 🔧 **Detaillierte Konfiguration**

### **Environment Variablen**

#### **Backend (.env)**
```bash
# Database Configuration (Optional - verwendet lokale SQLite wenn nicht gesetzt)
SUPABASE_DB_URL=postgresql://user:password@host:port/database

# AI/ML Configuration
OPENAI_API_KEY=your_openai_api_key  # Für OpenAI Models
COHERE_API_KEY=your_cohere_api_key  # Für Cohere Reranker

# Storage Configuration  
STORAGE_PATH=./storage/documents  # Lokaler Dokumentenspeicher
CHROMA_PERSIST_DIR=./storage/chroma  # ChromaDB Speicher

# Performance Settings
MAX_UPLOAD_SIZE=104857600  # 100MB in bytes
CHUNK_SIZE=1000  # Text chunking size
CHUNK_OVERLAP=200  # Chunk overlap for context

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./logs/streamworks.log

# Security (für Production)
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

#### **Frontend (.env.local)**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_LOCAL_AI=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_MAX_FILE_SIZE=104857600

# UI Configuration
NEXT_PUBLIC_APP_NAME=Streamworks-KI
NEXT_PUBLIC_THEME=system  # light, dark, system
```

### **Database Setup**

#### **Option 1: Lokale SQLite (Standard)**
Keine weitere Konfiguration erforderlich. Das System erstellt automatisch eine lokale SQLite-Datei.

#### **Option 2: PostgreSQL/Supabase**
```bash
# 1. Supabase Projekt erstellen oder lokale PostgreSQL installieren
# 2. Database URL in .env setzen:
SUPABASE_DB_URL=postgresql://user:pass@host:port/dbname

# 3. Tabellen erstellen (automatisch beim ersten Start)
python main.py
```

#### **Option 3: Docker PostgreSQL**
```bash
# PostgreSQL Container starten
docker run --name streamworks-db \
  -e POSTGRES_DB=streamworks \
  -e POSTGRES_USER=streamworks \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Database URL setzen
SUPABASE_DB_URL=postgresql://streamworks:password@localhost:5432/streamworks
```

### **Erweiterte Backend-Konfiguration**

#### **AI Model Configuration**
```python
# backend/config.py Beispiel-Konfiguration

# Embedding Model (lokal oder API)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Lokales Model
# EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI API

# Chat Model Configuration
CHAT_MODEL = "ollama/llama2"  # Lokales Ollama Model
# CHAT_MODEL = "gpt-3.5-turbo"  # OpenAI API

# Reranker Configuration  
RERANKER_TYPE = "local"  # local, cohere
LOCAL_RERANKER_MODEL = "BAAI/bge-reranker-base"
```

#### **Performance Tuning**
```python
# ChromaDB Configuration
CHROMA_CONFIG = {
    "persist_directory": "./storage/chroma",
    "collection_name": "documents",
    "distance_function": "cosine"  # cosine, euclidean, manhattan
}

# Upload Processing
CONCURRENT_UPLOADS = 3  # Parallel document processing
BATCH_SIZE = 50  # Batch size for embeddings
```

---

## 🐳 **Docker Setup**

### **Docker Compose (Empfohlen)**

#### **1. docker-compose.yml erstellen**
```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: streamworks
      POSTGRES_USER: streamworks  
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Backend
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_DB_URL=postgresql://streamworks:password@postgres:5432/streamworks
      - STORAGE_PATH=/app/storage
    volumes:
      - ./storage:/app/storage
    depends_on:
      - postgres

  # Frontend  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

#### **2. Backend Dockerfile**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Storage directory
RUN mkdir -p /app/storage/documents /app/storage/chroma

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **3. Frontend Dockerfile**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Dependencies
COPY package*.json ./
RUN npm ci --only=production

# App code
COPY . .

# Build
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

#### **4. System starten**
```bash
# Alle Services starten
docker-compose up -d

# Logs verfolgen
docker-compose logs -f

# System stoppen
docker-compose down
```

---

## 🏭 **Production Setup**

### **1. Environment Configuration**

#### **Production .env**
```bash
# Database
SUPABASE_DB_URL=postgresql://user:secure_password@prod-db:5432/streamworks

# Security
SECRET_KEY=your-super-secure-secret-key-here
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# AI Services (Production APIs)
OPENAI_API_KEY=sk-your-production-api-key
COHERE_API_KEY=your-cohere-production-key

# Storage (Cloud Storage empfohlen)
STORAGE_TYPE=s3  # local, s3, gcs
AWS_S3_BUCKET=your-document-bucket
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Performance
MAX_CONCURRENT_UPLOADS=10
CACHE_TTL=3600  # 1 hour
RATE_LIMIT=1000  # requests per hour per IP

# Monitoring
LOG_LEVEL=WARNING
ENABLE_METRICS=true
SENTRY_DSN=your-sentry-dsn
```

### **2. Infrastructure Setup**

#### **Nginx Reverse Proxy**
```nginx
# /etc/nginx/sites-available/streamworks
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/certificate.pem;
    ssl_certificate_key /path/to/private-key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # File upload limits
    client_max_body_size 100M;
    client_body_timeout 60s;
}
```

#### **Systemd Services**

**Backend Service:**
```ini
# /etc/systemd/system/streamworks-backend.service
[Unit]
Description=Streamworks Backend
After=network.target

[Service]
Type=simple
User=streamworks
Group=streamworks
WorkingDirectory=/opt/streamworks/backend
Environment=PATH=/opt/streamworks/venv/bin
ExecStart=/opt/streamworks/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

**Frontend Service:**
```ini
# /etc/systemd/system/streamworks-frontend.service
[Unit]
Description=Streamworks Frontend
After=network.target

[Service]
Type=simple
User=streamworks
Group=streamworks
WorkingDirectory=/opt/streamworks/frontend
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

#### **Service Management**
```bash
# Services aktivieren und starten
sudo systemctl enable streamworks-backend streamworks-frontend
sudo systemctl start streamworks-backend streamworks-frontend

# Status prüfen
sudo systemctl status streamworks-backend
sudo systemctl status streamworks-frontend

# Logs anzeigen
sudo journalctl -u streamworks-backend -f
```

### **3. Monitoring & Logging**

#### **Logging Configuration**
```python
# backend/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/streamworks.log', 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
```

#### **Health Monitoring Script**
```bash
#!/bin/bash
# health_check.sh

# Check backend
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $BACKEND_STATUS -ne 200 ]; then
    echo "Backend unhealthy: $BACKEND_STATUS"
    systemctl restart streamworks-backend
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ $FRONTEND_STATUS -ne 200 ]; then
    echo "Frontend unhealthy: $FRONTEND_STATUS"  
    systemctl restart streamworks-frontend
fi
```

---

## 🛠️ **Troubleshooting**

### **Häufige Probleme**

#### **Backend startet nicht**
```bash
# Fehler: Port bereits belegt
netstat -tulpn | grep :8000
kill -9 <PID>

# Fehler: Dependencies fehlen
pip install -r requirements.txt --force-reinstall

# Fehler: Database Connection
# Prüfen Sie SUPABASE_DB_URL in .env
psql $SUPABASE_DB_URL -c "SELECT 1;"
```

#### **Frontend Build Fehler**
```bash
# Node Modules löschen und neu installieren  
rm -rf node_modules package-lock.json
npm install

# TypeScript Fehler
npm run type-check

# Memory Fehler bei Build
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

#### **Document Upload Fehler**
```bash
# Speicher-Berechtigungen prüfen
mkdir -p storage/documents
chmod 755 storage/documents

# Maximale Upload-Größe prüfen
# Nginx: client_max_body_size
# Backend: MAX_UPLOAD_SIZE in .env

# Disk Space prüfen
df -h
```

#### **AI/ML Model Probleme**
```bash
# Embedding Model Download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# ChromaDB Permissions
chmod -R 755 storage/chroma

# Memory für große Models
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
```

### **Performance Tuning**

#### **Backend Optimization**
```python
# config.py
PERFORMANCE_CONFIG = {
    # Database
    "db_pool_size": 10,
    "db_max_overflow": 20,
    "db_pool_recycle": 1800,
    
    # Processing
    "max_concurrent_uploads": 5,
    "chunk_batch_size": 100,
    "embedding_batch_size": 50,
    
    # Caching
    "enable_response_cache": True,
    "cache_ttl": 3600,
    "max_cache_size": "1GB"
}
```

#### **Frontend Optimization**
```javascript
// next.config.js
module.exports = {
  experimental: {
    optimizeCss: true,
    optimizeImages: true,
  },
  compress: true,
  poweredByHeader: false,
  generateEtags: false
}
```

### **Debug Modi**

#### **Backend Debug**
```bash
# Detaillierte Logs
LOG_LEVEL=DEBUG python main.py

# Profiling
pip install py-spy
py-spy top --pid <backend_pid>
```

#### **Frontend Debug** 
```bash
# Development mit Debug Info
DEBUG=* npm run dev

# Bundle Analysis
npm run build
npm run analyze
```

### **Testing**

#### **Backend Tests**
```bash
# API Tests
pip install pytest httpx
pytest tests/

# Load Testing
pip install locust
locust -f tests/load_test.py --host http://localhost:8000
```

#### **Frontend Tests**
```bash
# Unit Tests
npm run test

# E2E Tests  
npm run test:e2e

# Performance Testing
npm run lighthouse
```

---

## 📊 **Deployment Checklist**

### **Pre-Deployment**
- [ ] Environment Variablen konfiguriert
- [ ] Database Migrationen ausgeführt  
- [ ] SSL Zertifikate installiert
- [ ] Firewall Regeln konfiguriert
- [ ] Backup Strategie implementiert
- [ ] Monitoring Setup aktiviert

### **Security Checklist**
- [ ] Strong passwords/API keys
- [ ] CORS richtig konfiguriert
- [ ] Rate Limiting aktiviert
- [ ] File Upload Validation
- [ ] Security Headers (HTTPS, HSTS, etc.)
- [ ] Regular Security Updates

### **Performance Checklist** 
- [ ] Database Indizes optimiert
- [ ] Caching Layer konfiguriert
- [ ] CDN für statische Assets
- [ ] Gzip Compression aktiviert
- [ ] Image Optimization
- [ ] Bundle Size optimiert

---

## 🚀 **Updates & Maintenance**

### **System Updates**
```bash
# Backend Updates
cd backend
git pull origin main
pip install -r requirements.txt --upgrade
systemctl restart streamworks-backend

# Frontend Updates  
cd frontend
git pull origin main
npm install
npm run build
systemctl restart streamworks-frontend
```

### **Database Maintenance**
```bash
# Backup erstellen
pg_dump $SUPABASE_DB_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Vacuum/Analyze (PostgreSQL)
psql $SUPABASE_DB_URL -c "VACUUM ANALYZE;"

# Storage Cleanup
find storage/documents -type f -mtime +90 -delete  # Dateien > 90 Tage
```

---

## 💬 **Support & Community**

- **📖 Dokumentation**: [docs/](../docs/)
- **🐛 Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **💬 Diskussionen**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **📧 Email**: support@your-domain.com

---

**✅ Setup erfolgreich!** Das Streamworks-KI System ist jetzt einsatzbereit für intelligente Dokumentenverarbeitung.

*Guide Version 2.0.0 - Letzte Aktualisierung: January 2025*