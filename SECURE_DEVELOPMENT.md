# 🔒 Sichere Entwicklung im Arbeitsnetzwerk

## Alle Services laufen NUR auf localhost (127.0.0.1)

### ✅ Backend (Port 8000)
```bash
# Option 1: Direkter Start
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Option 2: Via start_backend.sh (bereits angepasst)
cd backend && ./start_backend.sh
```

### ✅ Frontend (Port 3000)
```bash
cd frontend
npm run dev
# Läuft automatisch nur auf localhost:3000
```

### ✅ PostgreSQL (Port 5432)
```bash
# Bereits sicher konfiguriert in docker-compose.simple-db.yml
# Exposed nur auf localhost:5432
./quick-start.sh
```

### ✅ pgAdmin (Port 8080)
```bash
# Bereits sicher auf localhost:8080
# Zugriff: http://localhost:8080
```

## Sicherheits-Checkliste

- ✅ Backend: `--host 127.0.0.1` statt `--host 0.0.0.0`
- ✅ Frontend: Vite läuft standardmäßig nur auf localhost
- ✅ PostgreSQL: Docker-Ports sind auf localhost gebunden
- ✅ pgAdmin: Nur über localhost:8080 erreichbar
- ✅ Ollama: Läuft standardmäßig nur auf localhost:11434

## Keine externen Zugriffe möglich!

Alle Services sind jetzt nur über localhost erreichbar und nicht aus dem Netzwerk zugreifbar. Dies verhindert unerwünschte Zugriffe im Arbeitsnetzwerk.