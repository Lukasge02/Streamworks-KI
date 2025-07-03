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
### **Tech-Stack**
- **Backend**: Python + FastAPI + PyTorch
- **Frontend**: React + TypeScript + Tailwind CSS
- **KI**: LoRA Fine-Tuning auf 3B-10B Parameter LLM
- **Datenbank**: SQLite/PostgreSQL
- **Dokumentation**: RAG-Pipeline mit Langchain

### **Entwicklungsphasen**
1. **Phase 1 (Woche 1-3)**: Foundation & Daten-Preprocessing
2. **Phase 2 (Woche 4-6)**: KI-Training mit LoRA/PEFT
3. **Phase 3 (Woche 7-9)**: API + Backend Development
4. **Phase 4 (Woche 10-12)**: Frontend + Integration

## 📊 **Machbarkeits-Status**
- ✅ **Technisch machbar**: Bewährter Tech-Stack
- ✅ **Ressourcen verfügbar**: Hardware über Arvato Systems
- ✅ **Zeitplan realistisch**: 12 Wochen für MVP
- 🟡 **Abhängigkeiten**: StreamWorks API-Zugang, Trainingsdaten-Qualität

## 💡 **Kernfunktionen**
### **Intelligenter Chat-Bot**
```python
# Beispiel-Interaktion:
User: "Erstelle mir einen Stream für tägliche Datenverarbeitung um 2 Uhr"
AI: "Gerne! Welche Datenquelle möchten Sie verwenden? [Optionen anzeigen]"
User: "CSV-Dateien aus /data/input"
AI: "Verstanden. Hier ist Ihr XML-Stream: [XML generieren + validieren]"
```

### **Automatische Stream-Erstellung**
- Self-Service Formulare für Standard-Anforderungen
- LLM generiert XML basierend auf Patterns aus Trainingsdaten
- XSD-Validierung für Korrektheit
- Direkte API-Integration für Deployment

## 🎓 **Bachelorarbeit-Titel**
"Effiziente Workload-Automatisierung durch Self-Service und Künstliche Intelligenz: Möglichkeiten bei Streamworks"

## 🏢 **Geschäftlicher Kontext**
- **Problem**: Manuelle Stream-Erstellung ist zeitaufwändig
- **Lösung**: KI-gestützte Automatisierung mit Self-Service
- **Nutzen**: Effizienzsteigerung, Fehlerreduzierung, Standardisierung

## 🔥 **Projekt-Vision**
Eine vollständig funktionale "StreamWorks-KI" als Proof of Concept, die zeigt, wie moderne KI-Technologien (LLMs, Fine-Tuning) praktisch in Unternehmensumgebungen eingesetzt werden können.

## 📝 **Nächste Schritte**
1. Detaillierte Projektplanung
2. Datensammlung (Batch-Hilfe, XML-Samples)
3. Development Environment Setup
4. Erste LoRA-Experimente

---
ich werde programmieren mit claude code in vsc. bitte erstelle eine datei imemr mit dem projektfortschritt, um den kontext bei neuen chats zu behalten.