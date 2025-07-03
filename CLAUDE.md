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

## 🚀 **Aktueller Status (03.07.2025)**

### ✅ **Vollständig implementiert:**
1. **Full-Stack Web-Anwendung**
   - React Frontend mit 4 Tabs (Chat, Generator, Training Data, Docs)
   - FastAPI Backend mit async/await
   - Code-Llama-7B-Instruct LLM Integration
   - Production-ready Architektur

2. **Training Data Management System**
   - File Upload mit Drag & Drop
   - Kategorisierung: StreamWorks Hilfe / Stream Templates
   - File Manager mit Status Tracking
   - Progress Dashboard
   - SQLAlchemy Database Models
   - File Storage in `data/training_data/`

3. **API Endpoints**
   - `/api/v1/chat/` - Chat mit Code-Llama
   - `/api/v1/streams/` - XML Stream Generation
   - `/api/v1/training/` - Training Data Management (5 Endpoints)

### 🎯 **Nächste Schritte:**
1. Training Data Preprocessing Pipeline
2. LoRA Fine-Tuning Implementation
3. Model Evaluation & Integration

### 📁 **Repository:**
- GitHub: https://github.com/Lukasge02/Streamworks-KI
- Vollständig dokumentiert in `PROJECT_STATUS.md` und `NEXT_STEPS.md`

---
**CONTEXT FÜR NEUE CHATS**: Projekt ist in Phase 3 - LoRA Fine-Tuning Implementation. Training Data System ist vollständig implementiert und funktional.

## 💻 **Git Commit Konfiguration**
- **WICHTIG**: Keine "Co-Authored-By: Claude" Zeilen in Commit Messages
- **Format**: Nur Titel, Beschreibung und Claude Code Link