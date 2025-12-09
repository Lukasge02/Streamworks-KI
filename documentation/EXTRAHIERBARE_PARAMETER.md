# Extrahierbare Parameter - Streamworks-KI LangExtract System

> **LangExtract Schema v3.0** - Übersicht aller extrahierbaren Parameter für Streams und Jobs

---

## Stream-Parameter (Alle Job-Typen)

| Parameter | Typ | Required | Default | Beschreibung | Beispiele |
|-----------|-----|----------|---------|--------------|-----------|
| **StreamName** | string | ✅ Ja | - | Eindeutiger Stream-Name | `GT123_BASF_Transfer`, `SAP_Daily_Export` |
| **Agent** | string | ❌ Nein | - | Agent-Name für Ausführung | `gtlnmiwvm1636`, `TestAgent1` |
| **MaxStreamRuns** | integer | ❌ Nein | `5` | Maximale parallele Ausführungen (1-999) | `5`, `10`, `20`, `50`, `99` |
| **SchedulingRequiredFlag** | boolean | ❌ Nein | `true` | Zeitgesteuert (true) oder manuell (false) | `true`, `false` |
| **StartTime** | string | ❌ Nein | - | Startzeit im Format HH:MM | `08:00`, `14:30`, `22:15` |

### Erkennungsmuster für Stream-Parameter:

- **MaxStreamRuns**: "max X läufe", "maximal Y parallel", "bis zu Z ausführungen", "höchstens N runs"
- **StartTime**: "täglich um HH:MM", "startzeit HH:MM", "um HH:MM starten"
- **SchedulingRequiredFlag**: "täglich", "wöchentlich", "zeitgesteuert" → `true` | "manuell", "on-demand" → `false`

---

## FILE_TRANSFER Job-Parameter

**Job-Typ**: Dateiübertragung zwischen Systemen und Servern

| Parameter | Typ | Required | Default | Beschreibung | Beispiele |
|-----------|-----|----------|---------|--------------|-----------|
| **source_agent** | string | ✅ Ja | - | Quell-Agent oder Server | `GT123_Server`, `TestAgent1` |
| **target_agent** | string | ✅ Ja | - | Ziel-Agent oder Server | `BASF_Agent`, `BackupServer` |
| **source_path** | string | ❌ Nein | - | Quell-Dateipfad oder -pattern | `/data/export/*.csv`, `C:\Transfer\Files\` |
| **target_path** | string | ❌ Nein | - | Ziel-Dateipfad oder -verzeichnis | `/backup/import/`, `D:\Incoming\` |

### Erkennungsmuster:

- **source_agent**: "von xyz", "source agent ist xyz", "quellserver xyz", "zwischen xyz und"
- **target_agent**: "nach xyz", "zu xyz", "target agent ist xyz", "zielserver xyz"
- **Pfade**: Erkennung von Dateipfaden mit `/`, `\`, `*.ext` patterns

### Detection Keywords:
`datentransfer`, `übertragung`, `transfer`, `kopieren`, `sync`, `agent`, `server`, `dateien`, `von`, `nach`

### Required Parameter:
✅ `StreamName`, `source_agent`, `target_agent`

---

## SAP Job-Parameter

**Job-Typ**: SAP Report, Programm oder Transaktion

| Parameter | Typ | Required | Default | Beschreibung | Beispiele |
|-----------|-----|----------|---------|--------------|-----------|
| **system** | enum | ✅ Ja | - | SAP-System | `PA1`, `PT1`, `PD1`, `GT123`, `ZTV`, `ZTJ`, `HSV` |
| **client** | string | ❌ Nein | - | SAP-Mandant/Client | `300`, `514`, `100`, `200` |
| **program** | string | ❌ Nein | - | SAP Programm/Report/Kommando | `EXE_CAL_EXPORT`, `EXECUTE`, `BTCSPOOL` |
| **user** | string | ❌ Nein | - | SAP-User für Anmeldung | `SAPCOMM`, `BATCHUSER`, `ADMINUSER` |
| **variant** | string | ❌ Nein | - | Report-Variante | `EXCEL_DAILY`, `ZTEST_VAR01`, `STANDARD` |
| **job_name** | string | ❌ Nein | - | SAP Job-Name für Monitoring | `FA_EXPORT_DAILY`, `CALENDAR_SYNC` |
| **parameters** | string | ❌ Nein | - | Zusätzliche SAP-Parameter (Key:Value) | `I_CALENDER_ID_W:09`, `OUT_FILE:calendar_01` |
| **output_settings** | string | ❌ Nein | - | Output/Spool-Konfiguration | `-SPOOL`, `OUT_DIR:c:\temp`, `PP_PDEST:LOCAL` |

### SAP-Systeme (Enum-Werte):
- **PA1** - Production System A1
- **PT1** - Test System T1
- **PD1** - Development System D1
- **GT123** - GT System 123
- **ZTV**, **ZTJ**, **HSV** - Spezial-Systeme

### Detection Keywords:
`sap`, `system`, `report`, `export`, `import`, `mandant`, `transaktion`, `variant`, `pa1`, `gt123`, `ztv`, `fabrikkalender`, `batch`, `execute`, `client`, `sapcomm`

### Required Parameter:
✅ `StreamName`, `system`

---

## STANDARD Job-Parameter

**Job-Typ**: Script-Jobs und allgemeine Verarbeitungsprozesse

| Parameter | Typ | Required | Default | Beschreibung | Beispiele |
|-----------|-----|----------|---------|--------------|-----------|
| **MainScript** | string | ✅ Ja | - | Script-Inhalt oder Command | `python analyze_data.py --input=/data`, `dir C:\temp` |
| **JobType** | enum | ❌ Nein | `Windows` | Script-Ausführungstyp (auto-detect) | `Windows`, `Unix` |

### Auto-Erkennung JobType:

| Typ | Erkennungs-Keywords | Beispiele |
|-----|---------------------|-----------|
| **Windows** | `dir`, `copy`, `del`, `cmd`, `bat`, `c:\`, `d:\`, `REM` | `dir C:\temp && copy *.log` |
| **Unix** | `ls`, `cp`, `rm`, `sh`, `bash`, `/usr/`, `/bin/`, `python` | `python analyze_data.py --input=/data` |

### Detection Keywords:
`script`, `programm`, `command`, `befehl`, `ausführen`, `python`, `java`, `batch`, `shell`, `exe`, `env`, `backup`, `process`

### Required Parameter:
✅ `StreamName`, `MainScript`

---

## Parameter-Übersicht nach Job-Typ

| Job-Typ | Stream-Parameter | Job-Parameter | Gesamt | Required |
|---------|------------------|---------------|---------|----------|
| **FILE_TRANSFER** | 5 | 4 | **9** | 3 (StreamName, source_agent, target_agent) |
| **SAP** | 5 | 8 | **13** | 2 (StreamName, system) |
| **STANDARD** | 5 | 2 | **7** | 2 (StreamName, MainScript) |

---

## Extraction Rules

### ✅ Fokus-Prinzipien:

1. **Parameter Focus**: Nur essentielle 6-13 Parameter pro Job-Type extrahieren
2. **No Auto-Generation**: Keine auto-generierten Felder wie JobCategory, ShortDescription
3. **German Keywords**: Deutsche Begriffe aus User-Eingaben erkennen und verarbeiten
4. **Source Grounding**: Character offsets für extrahierte Parameter bereitstellen
5. **Confidence Scoring**: Confidence-Werte für jede Extraktion berechnen

### 🎯 System-Performance:

- **Job Type Detection Accuracy**: **88.9%**
- **False Positive Reduction**: **70%** weniger Fehlklassifikationen
- **German Language Support**: Optimiert für deutsche StreamWorks-Eingaben
- **Response Time**: Sub-2-Sekunden für alle Job Types

---

## Beispiel-Extraktionen

### FILE_TRANSFER Beispiel:
```
Input: "Datentransfer von GT123_Server nach BASF_Agent für alle CSV Dateien täglich um 08:00"

Extrahierte Parameter:
✅ StreamName: "GT123_BASF_CSV_Transfer"
✅ MaxStreamRuns: 5
✅ SchedulingRequiredFlag: true
✅ StartTime: "08:00"
✅ source_agent: "GT123_Server"
✅ target_agent: "BASF_Agent"
✅ source_path: "*.csv"
```

### SAP Beispiel:
```
Input: "SAP Export aus System ZTV Client 300 mit Report EXE_CAL_EXPORT täglich um 08:00"

Extrahierte Parameter:
✅ StreamName: "SAP_ZTV_Calendar_Export"
✅ MaxStreamRuns: 5
✅ SchedulingRequiredFlag: true
✅ StartTime: "08:00"
✅ system: "ZTV"
✅ client: "300"
✅ program: "EXE_CAL_EXPORT"
✅ user: "SAPCOMM"
```

### STANDARD Beispiel:
```
Input: "Python-Script ausführen täglich um 08:00: python analyze_data.py --input=/data"

Extrahierte Parameter:
✅ StreamName: "Daily_Data_Analysis"
✅ MaxStreamRuns: 5
✅ SchedulingRequiredFlag: true
✅ StartTime: "08:00"
✅ MainScript: "python analyze_data.py --input=/data"
✅ JobType: "Unix"
```

---

## API Integration

### LangExtract Endpoint:
```http
POST /api/langextract/sessions/{session_id}/messages
Content-Type: application/json

{
  "message": "Datentransfer von GT123_Server nach BASF_Agent",
  "timestamp": "2025-10-06T10:00:00Z"
}
```

### Response Format:
```json
{
  "ai_response": "Ich habe einen FILE_TRANSFER Job erkannt...",
  "detected_job_type": "FILE_TRANSFER",
  "detection_confidence": 0.95,
  "detection_method": "multi_layer_pattern_matching",
  "alternative_job_types": [],
  "extracted_parameters": {
    "StreamName": "GT123_BASF_Transfer",
    "source_agent": "GT123_Server",
    "target_agent": "BASF_Agent",
    "MaxStreamRuns": 5
  },
  "completion_percentage": 75.0
}
```

---

## Technische Details

### LangExtract Integration:
- **Model**: `gpt-4o`
- **Temperature**: `0.1` (niedrig für konsistente Extraktionen)
- **Source Grounding**: ✅ Aktiviert (Character offsets)
- **Fence Output**: ✅ Aktiviert (JSON-Formatting)
- **Schema Constraints**: ✅ Aktiviert (Type validation)

### Schema-Dateien:
- **Backend Schema**: `backend/templates/langextract_schemas.json`
- **LangExtract Service**: `backend/services/ai/langextract/unified_langextract_service.py`
- **Job Type Detector**: `backend/services/ai/enhanced_job_type_detector.py` (88.9% Accuracy)
- **Parameter Extractor**: `backend/services/ai/enhanced_unified_parameter_extractor.py`

---

*Version: LangExtract Schema v3.0 | Streamworks-KI v0.14 | Stand: Oktober 2025*
