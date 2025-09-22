# 📚 StreamWorks LangExtract Parameter-Extraktion Dokumentation

> **Vollständige Anleitung zum StreamWorks LangExtract System**
> Wie Parameter-Extraktion funktioniert und wie neue Parameter hinzugefügt werden

---

## 🏗️ **System-Architektur Übersicht**

Das LangExtract System basiert auf **Google LangExtract** und extrahiert automatisch StreamWorks-Parameter aus deutschen User-Eingaben.

### **Kern-Komponenten**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  LangExtract    │───▶│   Parameter     │
│  "SAP Export"   │    │    Service      │    │   Anzeige UI    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Job-Typ Detect  │    │ Session Storage │    │ Real-time UI    │
│ FILE_TRANSFER   │    │   SQLAlchemy    │    │   Updates       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📂 **Datei-Struktur**

### **Backend-Komponenten**

```
backend/
├── templates/
│   └── langextract_schemas.json          # 🎯 ZENTRALE SCHEMA-DATEI
├── services/ai/langextract/
│   └── unified_langextract_service.py    # Haupt-Service
├── routers/
│   └── langextract_chat.py               # REST API Endpoints
└── models/
    └── langextract_models.py             # Pydantic Models
```

### **Frontend-Komponenten**

```
frontend/src/components/langextract-chat/
├── components/
│   └── ParameterOverview.tsx             # Parameter UI & Definitionen
├── hooks/
│   └── useLangExtractChat.ts             # State Management Hook
└── LangExtractInterface.tsx              # Haupt-Interface
```

---

## 🎯 **Parameter-System**

### **Parameter-Kategorien**

1. **Stream-Parameter** (für alle Job-Typen):
   ```typescript
   {
     StreamName: "Eindeutiger Stream-Name",
     MaxStreamRuns: 5,                    // 1,3,5,10,20
     SchedulingRequiredFlag: true,        // Zeitgesteuert?
     StartTime: "08:00"                   // Format HH:MM
   }
   ```

2. **Job-spezifische Parameter**:

   **FILE_TRANSFER**:
   ```typescript
   {
     source_agent: "GT123_Server",
     target_agent: "BASF_Agent",
     source_path: "*.csv",
     target_path: "/backup/import/"
   }
   ```

   **SAP**:
   ```typescript
   {
     system: "PA1_100",                   // SAP-System mit Mandant
     report: "ZTV_EXPORT_001",            // Report-Name
     variant: "DAILY_EXPORT"              // Report-Variante
   }
   ```

   **STANDARD**:
   ```typescript
   {
     MainScript: "dir C:\\temp && copy *.log"
   }
   ```

---

## 🔄 **Extractions-Workflow**

### **1. User Input Processing**
```
User: "SAP Export aus System PA1_100 mit Report ZTV_CALENDAR"
  │
  ▼ Router: /api/streamworks/sessions/{id}/messages
  │
  ▼ Service: unified_langextract_service.py
```

### **2. Job-Typ Detection**
```python
# Schema-basierte Detection aus langextract_schemas.json
{
  "input": "SAP Export aus System PA1_100...",
  "output": "SAP",
  "confidence": 0.98
}
```

### **3. Parameter Extraction**
```python
# Google LangExtract mit Few-Shot Examples
langextract.extract(
  text=user_message,
  schema=sap_schema,
  examples=few_shot_examples
)
```

### **4. Session Storage**
```python
# SQLAlchemy Session mit Job-Typ
session.job_type = "SAP"
session.stream_parameters = {...}
session.job_parameters = {...}
```

### **5. Frontend Update**
```typescript
// Job-Typ aus Session (nicht Parameter!)
const currentSession = sessions.find(s => s.session_id === currentSessionId)
const currentJobType = currentSession?.job_type || null

// Nur relevante Parameter anzeigen
if (currentJobType === "SAP") {
  showParameters: ["system", "report", "variant"]
}
```

---

## ➕ **Neue Parameter hinzufügen**

### **Schritt 1: Backend Schema erweitern**

**Datei**: `backend/templates/langextract_schemas.json`

```json
{
  "parameter_extraction": {
    "SAP": {
      "extraction_prompt": "Extrahiere SAP Parameter...\n\n5. new_parameter (string, optional) - Beschreibung",

      "few_shot_examples": [
        {
          "input": "Beispiel User-Input",
          "output": {
            "system": "PA1_100",
            "report": "ZTV_EXPORT",
            "new_parameter": "extracted_value"
          }
        }
      ]
    }
  }
}
```

### **Schritt 2: Frontend UI erweitern**

**Datei**: `frontend/src/components/langextract-chat/components/ParameterOverview.tsx`

```typescript
const JOB_SPECIFIC_PARAMETER_DEFINITIONS = {
  SAP: {
    system: { label: 'SAP System', description: '...', required: true },
    report: { label: 'Report/Programm', description: '...', required: false },
    variant: { label: 'Report-Variante', description: '...', required: false },

    // ✨ Neuer Parameter
    new_parameter: {
      label: 'Neuer Parameter',
      description: 'Beschreibung des neuen Parameters',
      required: false
    }
  }
}
```

### **Schritt 3: Parameter-Filterung erweitern**

```typescript
const parameterPatterns = {
  'SAP': ['system', 'report', 'variant', 'new_parameter'], // Erweitert
  'FILE_TRANSFER': ['source_agent', 'target_agent', 'source_path', 'target_path'],
  'STANDARD': ['MainScript', 'script', 'command']
}
```

---

## 🚨 **Wichtige Regeln**

### **✅ DO's**
- **Schema als Single Source of Truth**: Alle Parameter-Definitionen kommen aus `langextract_schemas.json`
- **Job-Typ aus Session nehmen**: `currentSession?.job_type` statt Parameter-Detection
- **Few-Shot Examples aktualisieren**: Bei neuen Parametern immer Beispiele hinzufügen
- **Frontend-Backend Konsistenz**: Parameter-Namen müssen exakt übereinstimmen

### **❌ DON'Ts**
- **Keine Legacy-Fallbacks**: Nur die beste Lösung, keine `|| fallback` Logic
- **Keine komplizierte Parameter-Detection**: Backend macht Job-Typ Detection
- **Keine doppelten Parameter-Definitionen**: Ein Parameter = ein Ort im Schema
- **Keine UI-Performance Probleme**: Parameter-Filterung optimiert halten

---

## 🔧 **Debugging & Monitoring**

### **Backend Logs**
```python
logger.info(f"✅ Message processed: {len(stream_params) + len(job_params)} parameters")
logger.info(f"🔍 Job-Typ detected: {session.job_type}")
```

### **Frontend Debug**
```typescript
console.log('🔍 LangExtract ParameterOverview Debug:', {
  currentSessionId,
  backendJobType: currentSession?.job_type,
  currentJobType,
  hasJobTypeDetected
})
```

### **Typische Probleme**
1. **Parameter nicht angezeigt**: Schema-Konsistenz prüfen
2. **Job-Typ nicht erkannt**: Few-Shot Examples erweitern
3. **UI Performance**: Parameter-Filterung optimieren
4. **Session nicht gefunden**: Session-Management prüfen

---

## 📊 **Performance Considerations**

### **Schema-Größe**
- **PERFECT v3.0**: Optimiert auf 6-8 Parameter pro Job-Typ
- **Warum weniger besser ist**: Schnellere LangExtract Extraktion
- **Balance**: Vollständigkeit vs. Performance

### **UI-Filterung**
```typescript
// ✅ Effizient: Einmal filtern
const jobTypeSpecificParams = hasJobTypeDetected ?
  getJobTypeSpecificParameters(currentJobType, allParams) : jobParams

// ❌ Ineffizient: Jedes Render filtern
{params.filter(p => isRelevant(p)).map(...)}
```

---

## 🚀 **Best Practices**

### **Schema Design**
1. **Klare Parameter-Namen**: `source_agent` statt `src_agt`
2. **Deutsche Keywords**: `datentransfer`, `übertragung` für bessere Detection
3. **Realistische Examples**: Basierend auf echten Export-Streams
4. **Confidence Scores**: Mindestens 0.9+ für Production

### **Frontend Integration**
1. **Session-basierte Job-Typ Detection**: Einfach und zuverlässig
2. **Parameter-Definitionen centralisiert**: Alle Labels/Descriptions an einem Ort
3. **Real-time Updates**: Immediate UI Updates bei Parameter-Änderungen
4. **Error Handling**: Graceful Fallbacks bei API-Fehlern

### **Testing Strategy**
1. **Schema Validation**: Alle Parameter in Examples testen
2. **UI Consistency**: Parameter-Namen Backend ↔ Frontend
3. **Performance Tests**: Große Parameter-Sets testen
4. **Integration Tests**: End-to-End User-Flows

---

**🎯 Diese Dokumentation stellt sicher, dass neue Parameter erfolgreich integriert werden können, ohne die System-Performance oder -Stabilität zu beeinträchtigen.**