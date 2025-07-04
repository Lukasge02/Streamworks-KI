# StreamWorks-KI Bachelorarbeit - Projektkontext

## 👤 **Student & Kontext**
- **Name**: Ravel-Lukas Geck
- **Hochschule**: Fachhochschule der Wirtschaft (FHDW), Paderborn
- **Betreuer**: Prof. Dr. Christian Ewering 
- **Unternehmen**: Arvato Systems / Bertelsmann
- **Zeitrahmen**: 3. Quartal 2025 (12 Wochen)

## 🎯 **Projektziel**
Entwicklung einer "StreamWorks-KI" als Web-Anwendung, die:
- **Intelligente Q&A**: Beantwortet StreamWorks-Fragen basierend auf Dokumentation (Bacthdatei)
- **API-Integration**: Sendet automatisch API-Calls an StreamWorks
- **Stream-Generator**: Erstellt XML-Streams basierend auf Benutzer-Inputs
- **Web-Interface**: Alles in einer benutzerfreundlichen Oberfläche

## 🔧 **Technischer Ansatz**
### **Tech-Stack** (✅ Implementiert)
- **Backend**: Python + FastAPI + PyTorch + Code-Llama-7B-Instruct
- **Frontend**: React + TypeScript + Tailwind CSS + Zustand
- **KI**: Code-Llama-7B mit LoRA Fine-Tuning (PEFT)
- **Datenbank**: SQLite mit SQLAlchemy async
- **Training Data**: File Upload System mit Kategorisierung

### **Entwicklungsphasen** (Aktualisiert)
1. **✅ Phase 1 (Woche 1)**: Foundation - Frontend + Backend KOMPLETT
2. **✅ Phase 2A (Woche 2)**: Code-Llama-7B Integration KOMPLETT
3. **✅ Phase 2B (Woche 2)**: Training Data Management System KOMPLETT
4. **🎯 Phase 3 (Woche 2-3)**: Training Data Preprocessing + LoRA Fine-Tuning
5. **Phase 4 (Woche 4+)**: Advanced Features + Optimization + Evaluation

## 📊 **Implementierungs-Status**
- ✅ **Full-Stack System**: Frontend + Backend vollständig funktional
- ✅ **Code-Llama Integration**: 7B-Instruct Model mit MPS/GPU Support
- ✅ **Training Data System**: Upload, Management, Storage implementiert
- ✅ **Database**: SQLAlchemy Models für File Tracking
- 🎯 **Nächster Schritt**: Training Data Preprocessing Pipeline

## 💡 **Kernfunktionen**
### **Intelligenter Chat-Bot**
```python
# Beispiel-Interaktion:
User: "Erstelle mir einen Stream für tägliche Datenverarbeitung um 2 Uhr"
AI: "Gerne! Welche Datenquelle möchten Sie verwenden? [Optionen anzeigen]"
User: "CSV-Dateien aus /data/input"
AI: "Verstanden. Hier ist Ihr XML-Stream: [XML generieren + validieren]"
```

### **Training Data Management** (✅ Implementiert)
- **Kategorie-basiertes Upload**: help_data (.txt, .csv, .bat, .md, .ps1) / stream_templates (.xml, .xsd)
- **File Validation**: Extension & Size-Checks (max 50MB)
- **Status Tracking**: uploading → processing → ready → error
- **Storage**: Organisiert in `backend/data/training_data/`
- **UI**: Vollständiger Training Data Tab mit Drag & Drop

### **Automatische Stream-Erstellung** (✅ Implementiert)
- Self-Service Stream Generator Formular
- Code-Llama generiert XML basierend auf Inputs
- XSD-Validierung für Korrektheit
- **Zukünftig**: LoRA Fine-Tuning für StreamWorks-spezifische XML Generation

## 🎓 **Bachelorarbeit-Titel**
"Effiziente Workload-Automatisierung durch Self-Service und Künstliche Intelligenz: Möglichkeiten bei Streamworks"

## 🏢 **Geschäftlicher Kontext**
- **Problem**: Manuelle Stream-Erstellung ist zeitaufwändig
- **Lösung**: KI-gestützte Automatisierung mit Self-Service
- **Nutzen**: Effizienzsteigerung, Fehlerreduzierung, Standardisierung

## 🔥 **Projekt-Vision**
Eine vollständig funktionale "StreamWorks-KI" als Proof of Concept, die zeigt, wie moderne KI-Technologien (LLMs, Fine-Tuning) praktisch in Unternehmensumgebungen eingesetzt werden können.

## 🚀 **Aktueller Status (04.07.2025) - NEUE ARCHITEKTUR**

### 🏗️ **BACKEND REBUILD KOMPLETT - V2.0**
**Architektur-Übergang**: Von monolithischem LLM-System zu spezialisierter RAG + LoRA Architektur

### ✅ **Neu implementiert (V2.0):**

1. **RAG-basiertes Q&A System**
   - ChromaDB Vector Database für Dokumenten-Suche
   - LangChain für Document Processing
   - Sentence-Transformers für Embeddings (`all-MiniLM-L6-v2`)
   - Automatisches Laden der Training Data in Vector DB
   - Context-aware Antworten basierend auf Dokumentation

2. **LoRA Fine-Tuning für XML Generation**
   - Separater XML Generator Service
   - PEFT (Parameter Efficient Fine-Tuning) Integration
   - Base Model: `microsoft/DialoGPT-small` (lightweight)
   - LoRA Adapter Support für spezialisierte XML-Generierung
   - Mock Mode für Development (sofortige XML Templates)

3. **Neue Service-Architektur**
   - `RAGService`: Dokumenten-basierte Q&A
   - `XMLGeneratorService`: LoRA-tuned XML Generation
   - Modulare, erweiterbare Struktur
   - Async/Await für bessere Performance

4. **Erweiterte API Endpoints (V2.0)**
   - `/api/v1/chat/` - RAG-basierte Q&A (neu)
   - `/api/v1/chat/upload-docs` - Document Upload für Vector DB
   - `/api/v1/chat/search` - Vector Search (Dev Endpoint)
   - `/api/v1/xml/generate` - LoRA-tuned XML Generation
   - `/api/v1/xml/health` - XML Service Status
   - Detaillierte Health Checks und Status Endpoints

5. **Frontend Integration**
   - Keine Änderungen nötig - APIs kompatibel
   - Chat funktioniert sofort mit RAG System
   - Stream Generator nutzt automatisch XML Service

### 🔧 **Technical Highlights:**
- **Dependencies**: ChromaDB, LangChain, PEFT, Sentence-Transformers
- **Vector Storage**: Persistente ChromaDB in `data/vector_db/`
- **Model Management**: Automatische Model Loading mit Error Handling  
- **Configuration**: Umfangreiche Config für RAG + LoRA Parameter
- **Development Mode**: Services können einzeln aktiviert/deaktiviert werden

### 🎯 **Nächste Schritte (Phase 3):**
1. LoRA Training Pipeline implementieren
2. Training Data Preprocessing für XML Templates
3. Model Evaluation & Performance Tuning
4. Production Deployment Setup

### 📁 **Repository:**
- GitHub: https://github.com/Lukasge02/Streamworks-KI
- **Neue Architektur**: RAG + LoRA spezialisierte Services
- **Version**: 2.0.0 (Backend Rebuild komplett)

---
**CONTEXT FÜR NEUE CHATS**: Projekt ist in Phase 3 - LoRA Training Pipeline. Backend V2.0 mit RAG + LoRA Architektur ist vollständig implementiert und funktional. Chat System nutzt jetzt RAG für intelligente Antworten basierend auf Dokumentation.

## 💻 **Git Commit Konfiguration**
- **WICHTIG**: Keine "Co-Authored-By: Claude" Zeilen in Commit Messages
- **Format**: Nur Titel, Beschreibung und Claude Code Link