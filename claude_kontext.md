# 🤖 Claude Context - StreamWorks-KI Development

## 📋 **Aktueller Projektstatus**
- **Version**: 2.0.0 (Production-Ready)
- **Architektur-Score**: 90+/100
- **Status**: ✅ Vollständig funktional für Bachelorarbeit

### **Letzte Änderungen** (Auto-Update von Claude Code)
```
[2025-07-04 12:00] - Claude Context Setup erstellt
[TIMESTAMP] - [Änderung wird hier automatisch eingefügt]
```

## 🏗️ **Aktuelle Architektur**

### **Backend** (Python + FastAPI)
- **API**: FastAPI mit async/await
- **Database**: SQLAlchemy + SQLite (Production: PostgreSQL)
- **LLM**: Mistral 7B via Ollama
- **RAG**: ChromaDB + Langchain
- **Tests**: Unit Tests für alle Services

### **Frontend** (React + TypeScript)
- **UI**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand (Redux alternative)
- **Testing**: Jest + React Testing Library

### **KI-Pipeline**
- **RAG Service**: Dokumenten-Retrieval + Antwort-Generierung
- **XML Generator**: Template-basierte Stream-Erstellung
- **Evaluation Service**: Automatische Antwort-Qualitätsmessung
- **Training Data**: File Upload + Preprocessing

## 🎯 **Entwicklungskontext für Claude Code**

### **Coding Standards**
- **Python**: PEP 8, Type Hints, Async/Await
- **TypeScript**: Strict Mode, Interface-First Design
- **Testing**: 80%+ Code Coverage angestrebt
- **Documentation**: Docstrings für alle Funktionen

### **Aktuelle Prioritäten**
1. **Unit Tests**: Vollständige Test-Coverage
2. **Performance**: Optimierung der RAG-Pipeline
3. **Security**: Input Validation + API Security
4. **Monitoring**: Health Checks + Metrics

### **Technische Schulden**
- ⚠️ OpenSSL Warning (non-critical)
- ⚠️ Pydantic Warning (non-critical)
- 🔧 PostgreSQL Migration (optional)
- 🔧 Redis Caching (performance)

## 🔧 **Claude Code Workflow**

### **Entwicklungs-Pipeline**
```bash
# 1. Feature entwickeln
# 2. Tests schreiben/updaten
# 3. Code review via Claude
# 4. Integration testen
# 5. Dokumentation updaten
```

### **Auto-Update Regeln**
- **Jeder Commit**: Changelog in diese Datei
- **Neue Features**: Architektur-Diagramm updaten
- **Bug Fixes**: Known Issues aktualisieren
- **Performance**: Metrics dokumentieren

## 📊 **Metrics & KPIs**
- **Response Time**: < 2s für RAG-Anfragen
- **Accuracy**: > 85% für StreamWorks-Fragen
- **Uptime**: > 99.5% für API Services
- **Test Coverage**: > 80% für kritische Komponenten

## 🧪 **Testing Strategy**
- **Unit Tests**: Jeder Service einzeln
- **Integration Tests**: API-Endpoints
- **E2E Tests**: Frontend-Backend-Kombination
- **Performance Tests**: Load Testing für RAG

## 🚀 **Deployment Context**
- **Development**: localhost:8000 (backend), localhost:3000 (frontend)
- **Production**: Docker + nginx + PostgreSQL
- **Monitoring**: Health endpoints + metrics
- **Backup**: Database + Vector Store

## 🎓 **Bachelorarbeit-Fokus**
- **Titel**: "Effiziente Workload-Automatisierung durch Self-Service und KI"
- **Deadline**: Q3 2025 (12 Wochen)
- **Betreuer**: Prof. Dr. Christian Ewering
- **Bewertung**: Note 1 angestrebt (90+/100)

---

## 📝 **Claude Code Instructions**

### **Auto-Update Trigger**
```python
# Füge diese Zeile in jede Datei ein, die Claude Code ändert:
# UPDATE_CLAUDE_CONTEXT: [Beschreibung der Änderung]
```

### **Commit Message Format**
```
feat: neue Funktion für RAG-Optimierung
fix: behebe Memory Leak in Vector Store
test: füge Unit Tests für XML Generator hinzu
docs: aktualisiere API-Dokumentation
```

### **Review-Checkliste**
- [ ] Code funktioniert und ist getestet
- [ ] Dokumentation ist aktuell
- [ ] Performance ist akzeptabel
- [ ] Security-Aspekte berücksichtigt
- [ ] Claude Context ist aktualisiert

---

**🎯 Ziel**: Effizienter Code mit Claude Code, der immer im Kontext der Bachelorarbeit steht und automatisch dokumentiert wird.

*Letzte Aktualisierung: 2025-07-04 12:00*