# 🧪 Parameter-Extractions-Test Analyse

## 📋 Schema-Parameter-Mapping (Phase 1)

### FILE_TRANSFER Job-Type (9 definierte Parameter)

#### Stream Parameters (5):
1. **StreamName** (string, REQUIRED) - Eindeutiger Stream-Name
2. **Agent** (string, optional) - Agent-Name
3. **MaxStreamRuns** (integer, optional, default: 5) - Parallele Ausführungen (1-999)
4. **SchedulingRequiredFlag** (boolean, optional, default: true) - Zeitgesteuert oder manuell
5. **StartTime** (string, optional) - Startzeit HH:MM (Format: ^([01]?[0-9]|2[0-3]):[0-5][0-9]$)

#### Job Parameters (4):
1. **source_agent** (string, REQUIRED) - Quell-Agent oder Server
2. **target_agent** (string, REQUIRED) - Ziel-Agent oder Server
3. **source_path** (string, optional) - Quell-Dateipfad oder -pattern
4. **target_path** (string, optional) - Ziel-Dateipfad oder -verzeichnis

#### Required Parameters: StreamName, source_agent, target_agent

---

### SAP Job-Type (12+ definierte Parameter)

#### Stream Parameters (4):
1. **StreamName** (string, REQUIRED) - Eindeutiger Stream-Name
2. **MaxStreamRuns** (integer, optional, default: 5) - Parallele Ausführungen (1-999)
3. **SchedulingRequiredFlag** (boolean, optional, default: true) - Zeitgesteuert oder manuell
4. **StartTime** (string, optional) - Startzeit HH:MM

#### Job Parameters (8+):
1. **system** (enum, REQUIRED) - SAP System [PA1, PT1, PD1, GT123, ZTV, ZTJ, HSV]
2. **client** (string, optional) - SAP-Mandant/Client [300, 514, 100, 200]
3. **program** (string, optional) - SAP Programm/Report/Kommando
4. **user** (string, optional) - SAP-User für Anmeldung [SAPCOMM, BATCHUSER, ADMINUSER]
5. **variant** (string, optional) - Report-Variante
6. **job_name** (string, optional) - SAP Job-Name für Monitoring
7. **parameters** (string, optional) - Zusätzliche SAP-Parameter (Key:Value Format)
8. **output_settings** (string, optional) - Output/Spool-Konfiguration

#### Required Parameters: StreamName, system

---

### STANDARD Job-Type (6 definierte Parameter)

#### Stream Parameters (5):
1. **StreamName** (string, REQUIRED) - Eindeutiger Stream-Name
2. **Agent** (string, optional) - Agent-Name
3. **MaxStreamRuns** (integer, optional, default: 5) - Parallele Ausführungen (1-999)
4. **SchedulingRequiredFlag** (boolean, optional, default: false) - Zeitgesteuert oder manuell
5. **StartTime** (string, optional) - Startzeit HH:MM

#### Job Parameters (1):
1. **MainScript** (string, REQUIRED) - Script-Inhalt oder Command
2. **JobType** (enum, optional, default: Windows) - Script-Ausführungstyp [Windows, Unix]

#### Required Parameters: StreamName, MainScript

---

## 🎯 Test-Prioritäten

### Kritische Parameter (REQUIRED):
- FILE_TRANSFER: StreamName, source_agent, target_agent (3 Parameter)
- SAP: StreamName, system (2 Parameter)
- STANDARD: StreamName, MainScript (2 Parameter)

### High-Value Optional Parameter:
- MaxStreamRuns (alle Job-Types)
- StartTime (alle Job-Types)
- SchedulingRequiredFlag (alle Job-Types)

### Spezielle Parameter:
- source_path/target_path (FILE_TRANSFER)
- client, program, variant (SAP)
- JobType (STANDARD)

## 📊 Erwartete Test-Matrix

| Job-Type | Total Params | Required | Optional | Stream | Job |
|----------|--------------|----------|----------|--------|-----|
| FILE_TRANSFER | 9 | 3 | 6 | 5 | 4 |
| SAP | 12+ | 2 | 10+ | 4 | 8+ |
| STANDARD | 6 | 2 | 4 | 5 | 1 |

**Gesamt**: 27+ Parameter zu testen