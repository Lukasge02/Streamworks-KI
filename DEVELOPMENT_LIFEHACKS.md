# 🚀 StreamWorks-KI Development Life Hacks

*Alle Tricks und Shortcuts für super-effizientes Entwickeln*

---

## ⚡ **Schnellstart Commands**

### **Backend starten (1 Sekunde)**
```bash
cd backend && make dev
```

### **Tests ausführen (super schnell)**
```bash
make test-fast    # Nur wichtige Tests
make test        # Alle Tests mit Coverage
```

### **Code formatieren + linting**
```bash
make quick       # Format + Lint + Fast Tests
make full-check  # Kompletter Check
```

---

## 🔧 **VS Code Power Features**

### **Keyboard Shortcuts**

- **F5**: Debug FastAPI Server starten
- **Ctrl+Shift+P** → "Python: Run Tests": Test Explorer öffnen
- **Cmd+Shift+P** → "Tasks: Run Task": Alle Make-Commands
- **Cmd+K, Cmd+S**: Alle Keyboard Shortcuts anzeigen

### **Debug Configurations**
- **🚀 Debug FastAPI Server**: Mit Breakpoints debuggen
- **🧪 Debug Tests**: Einzelne Tests debuggen
- **🏃 Run Test Suite**: Komplette Test Suite ausführen
- **🔍 Debug RAG Service**: RAG Service isoliert testen

### **Automatische Features**
- **Auto-Format**: Beim Speichern (Black + isort)
- **Auto-Import**: Imports automatisch organisieren
- **Type Hints**: Mypy integration
- **GitLens**: Git-History inline sehen

---

## 📋 **Makefile Commands (Backend)**

### **🧪 Testing**
```bash
make test              # Alle Tests + Coverage
make test-fast         # Nur schnelle Tests
make test-unit         # Unit Tests
make test-integration  # Integration Tests
make test-performance  # Performance Tests
make test-coverage     # Detaillierte Coverage
```

### **🔍 Code Quality**
```bash
make lint         # Linting (flake8)
make format       # Code formatieren (black + isort)
make type-check   # Type checking (mypy)
make security     # Security scan (bandit)
make quality      # Alle Quality Checks
```

### **🚀 Development**
```bash
make dev          # Development Server
make dev-bg       # Server im Hintergrund
make stop         # Server stoppen
make health       # API Health Check
make metrics      # Performance Metrics
```

### **🏗️ Build & Deploy**
```bash
make build        # Production Build
make docker       # Docker Image
make docker-run   # Docker Container
make clean        # Temp Files löschen
make reset        # Kompletter Reset
```

---

## 🔍 **Testing Life Hacks**

### **Einzelne Tests ausführen**
```bash
# Spezifische Test-Datei
pytest tests/unit/test_rag_service.py -v

# Spezifische Test-Funktion
pytest tests/unit/test_rag_service.py::test_search_documents -v

# Tests mit Keyword
pytest -k "error_handler" -v

# Tests mit Marker
pytest -m "unit" -v
```

### **Test-Driven Development**
```bash
# Test schreiben → Red
pytest tests/unit/test_new_feature.py -v

# Code implementieren → Green
pytest tests/unit/test_new_feature.py -v

# Refactoring → Blue
pytest tests/ -v
```

### **Coverage Hacks**
```bash
# HTML Coverage Report
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Missing Lines anzeigen
pytest --cov=app --cov-report=term-missing
```

---

## 🏥 **Debugging Life Hacks**

### **FastAPI Debugging**
```bash
# Server mit Debug-Modus
uvicorn app.main:app --reload --log-level debug

# Health Check
curl http://localhost:8000/health | jq .

# API Documentation
open http://localhost:8000/docs
```

### **RAG Service Debugging**
```bash
# Debug Script ausführen
python debug_rag.py

# ChromaDB Collection checken
python -c "from app.services.rag_service import RAGService; rag = RAGService(); print(rag.collection.count())"
```

### **Database Debugging**
```bash
# SQLite Database öffnen
sqlite3 streamworks_ki.db
.tables
.schema training_files
```

---

## 📊 **Performance Monitoring**

### **Response Headers checken**
```bash
curl -I http://localhost:8000/api/v1/chat/

# Zeigt Performance Headers:
X-Response-Time: 0.123s
X-Endpoint-Count: 42
X-System-CPU: 15.2%
X-System-Memory: 68.5%
```

### **Performance Profiling**
```bash
# Server profilen
make profile

# Memory Usage tracken
python -m memory_profiler app/main.py
```

---

## 🎯 **Git Life Hacks**

### **Pre-commit Hooks**
```bash
# Installieren
pre-commit install

# Manuell ausführen
pre-commit run --all-files

# Commit mit Auto-Checks
git commit -m "feat: new feature"  # Hooks laufen automatisch
```

### **Git-Flow für Features**
```bash
# Feature Branch
git checkout -b feature/new-feature

# Development Cycle
make quick           # Fast checks
git add .
git commit -m "feat: implement new feature"

# Before Push
make push-check      # Full quality check
git push origin feature/new-feature
```

---

## 🚨 **Error Handling Life Hacks**

### **Schnelle Error-Diagnose**
```bash
# Logs anzeigen
make logs

# Live Error Monitoring
make logs-live

# Error Handler testen
python -c "
from app.services.error_handler import StreamWorksErrorHandler
handler = StreamWorksErrorHandler()
result = handler.handle_error(Exception('Test error'), 'test_context')
print(result)
"
```

### **Fallback Responses**
```python
# In Tests
def test_error_fallback():
    handler = StreamWorksErrorHandler()
    result = handler.handle_error(ConnectionError(), "chat")
    assert result.fallback_response == "Entschuldigung, es gibt momentan ein Problem mit der Verbindung."
```

---

## 📦 **Dependency Management**

### **Requirements Updates**
```bash
# Production Dependencies
pip install -r requirements.txt

# Development Dependencies
pip install -r requirements-dev.txt

# Update alle Dependencies
pip list --outdated
pip install --upgrade package_name
```

### **Virtual Environment**
```bash
# Neues venv erstellen
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Requirements einfrieren
pip freeze > requirements.txt
```

---

## 🎭 **Demo & Presentation**

### **Quick Demo Setup**
```bash
make demo           # Startet Server + Health Check
make demo-stop      # Stoppt Demo
```

### **Bachelor Thesis Demo**
```bash
# Komplette Demo-Umgebung
make dev-bg         # Server im Hintergrund
make health-full    # Full Health Check
make metrics        # Performance Metrics
make test-fast      # Schnelle Tests

# Demo URLs
open http://localhost:8000/docs    # API Documentation
open http://localhost:8000/health  # Health Status
```

---

## 🔧 **Troubleshooting**

### **Häufige Probleme**
```bash
# Port bereits belegt
lsof -ti:8000 | xargs kill -9

# Database locked
rm streamworks_ki.db && make db-init

# Import Errors
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"

# ChromaDB Issues
rm -rf chroma_db/ && restart server
```

### **Environment Issues**
```bash
# Python Version checken
python --version

# Dependencies checken
pip check

# Environment Variables
env | grep -E "(PYTHONPATH|PATH)"
```

---

## 🚀 **Productivity Hacks**

### **Alias für .bashrc/.zshrc**
```bash
# Zu .bashrc/.zshrc hinzufügen
alias sw="cd /path/to/StreamWorks-KI"
alias swb="cd /path/to/StreamWorks-KI/backend"
alias swf="cd /path/to/StreamWorks-KI/frontend"
alias swdev="cd /path/to/StreamWorks-KI/backend && make dev"
alias swtest="cd /path/to/StreamWorks-KI/backend && make test-fast"
alias swcheck="cd /path/to/StreamWorks-KI/backend && make full-check"
```

### **VS Code Snippets**
```json
// In .vscode/python.json
{
  "Test Function": {
    "prefix": "test",
    "body": [
      "def test_${1:function_name}(self):",
      "    \"\"\"Test ${1:function_name}\"\"\"",
      "    # Arrange",
      "    ${2:# Setup}",
      "    ",
      "    # Act",
      "    ${3:# Execute}",
      "    ",
      "    # Assert",
      "    ${4:# Verify}",
      "    assert ${5:condition}"
    ]
  }
}
```

---

## 📈 **Performance Optimization**

### **Caching**
```python
# In Services
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param):
    return result
```

### **Async Optimization**
```python
# Parallel Operations
import asyncio
results = await asyncio.gather(
    operation1(),
    operation2(),
    operation3()
)
```

---

## 🎓 **Bachelor Thesis Hacks**

### **Metrics Collection**
```bash
# Performance Metrics sammeln
python tools/collect_metrics.py

# Test Coverage Report
make test-coverage
open htmlcov/index.html

# Code Quality Metrics
make quality > quality_report.txt
```

### **Documentation Generation**
```bash
# API Documentation
make docs

# Coverage Badge
coverage-badge -o coverage.svg
```

---

## 🔥 **Ultimate Development Workflow**

### **Morgen-Routine**
```bash
cd backend
git pull
make clean
make install-dev
make health
make test-fast
```

### **Feature-Development**
```bash
# 1. Branch erstellen
git checkout -b feature/new-feature

# 2. Tests schreiben
pytest tests/unit/test_new_feature.py -v

# 3. Implementation
make quick  # Format + Lint + Fast Tests

# 4. Integration Test
make test

# 5. Commit
git add . && git commit -m "feat: implement new feature"

# 6. Push Check
make push-check
```

### **Production Ready Check**
```bash
make full-check     # Alle Tests + Quality
make build         # Production Build
make docker        # Docker Image
make demo          # Demo Setup
```

---

**🎯 Pro-Tip**: Alle Commands sind in der `Makefile` dokumentiert. Einfach `make help` für die komplette Liste!

**⚡ Super-Hack**: VS Code Terminal → `Cmd+Shift+P` → "Tasks: Run Task" → Alle Make-Commands mit einem Klick!

---

*Letztes Update: 2025-07-04 - Optimiert für Note 1 (90+/100) Bachelor Thesis* 🎓