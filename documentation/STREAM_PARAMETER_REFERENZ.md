# Stream Parameter Referenz

**Streamworks-KI LangExtract System**
**Version:** 0.14
**Erstellt:** 2025-10-22

Diese Dokumentation enthält alle bekannten Stream-Parameter des Streamworks-KI Systems mit detaillierten Informationen zu Pflichtfeldern, Datentypen, Default-Werten und Verwendung.

---

## 📋 Inhaltsverzeichnis

1. [Kritische Parameter (Required)](#kritische-parameter-required)
2. [Stream Properties](#stream-properties)
3. [Job Properties](#job-properties)
4. [Scheduling & Runtime](#scheduling--runtime)
5. [File Transfer Specific](#file-transfer-specific)
6. [SAP Specific](#sap-specific)
7. [Contact & Version Properties](#contact--version-properties)
8. [Parameter-Prioritäten](#parameter-prioritäten)
9. [Job-Type-Zuordnung](#job-type-zuordnung)

---

## 🎯 Kritische Parameter (Required)

Diese 12 Parameter sind die Kern-Parameter, die tatsächlich extrahiert werden müssen und keine sinnvollen Default-Werte haben.

### Stream Level Critical Parameters (5)

| Parameter | Typ | Pflicht | Priorität | Beschreibung | Beispiele |
|-----------|-----|---------|-----------|--------------|-----------|
| **StreamName** | string | ✅ JA | CRITICAL | Individueller Stream-Name nach Namenskonvention | `StrJ_JobScript_001`, `StrFT_FileTrans_001`, `geck003_Backup_Stream` |
| **ShortDescription** | string | ✅ JA | HIGH | Spezifische Beschreibung des Stream-Zwecks | `Executing external scripts via Job Script`, `Demo File Transfer` |
| **AgentDetail** | string | ✅ JA | CRITICAL | Konkreter Agent-Name für Ausführung | `TestAgent1`, `ServerA`, `ProdAgent_Berlin`, `servera` |
| **StreamDocumentation** | string | ❌ NEIN | MEDIUM | Individuelle Dokumentation und Admin-Hinweise | `DEMO - Ausführen externer Skripte`, `Wichtig: Vor Ausführung Backup prüfen` |
| **MaxStreamRuns** | integer | ❌ NEIN | HIGH | Variable Anzahl maximaler Stream-Läufe (1-999) | `10`, `50`, `99`, `5` |

**Validierung:**
- `StreamName`: Pattern `^[A-Za-z0-9_]+$`
- `MaxStreamRuns`: Pattern `^[1-9]\d{0,2}$` (1-999)

---

### Job Level Critical Parameters (3)

| Parameter | Typ | Pflicht | Priorität | Beschreibung | Beispiele |
|-----------|-----|---------|-----------|--------------|-----------|
| **JobName** | string | ✅ JA | HIGH | Job-Name, meist generiert aus StreamName | `0010_StrJ_JobScript_001`, `0010_StrFT_FileTrans_001` |
| **JobShortDescription** | string | ❌ NEIN | HIGH | Job-spezifische Beschreibung | `Execute Visual Basic .exe`, `Job 0010 File Transfer` |
| **MainScript** | string | ✅ JA* | CRITICAL | Konkretes Skript oder Command (*nur für STANDARD) | `C:\Streamworks\Scripts\VisualBasic\CreateFolder.exe`, `python /opt/scripts/backup.py` |

**Hinweis:** `MainScript` ist nur für **STANDARD** Job-Type erforderlich, nicht für FILE_TRANSFER.

---

### File Transfer Specific Critical Parameters (4)

| Parameter | Typ | Pflicht | Priorität | Beschreibung | Beispiele |
|-----------|-----|---------|-----------|--------------|-----------|
| **SourceAgent** | string | ✅ JA* | CRITICAL | Agent mit der Quelle (*nur für FILE_TRANSFER) | `TestAgent1`, `ServerA`, `servera` |
| **TargetAgent** | string | ✅ JA* | CRITICAL | Agent mit dem Ziel (*nur für FILE_TRANSFER) | `TestAgent2`, `ServerB`, `serverb` |
| **SourceFilePattern** | string | ❌ NEIN | HIGH | Quell-Dateipfad oder Pattern (*nur für FILE_TRANSFER) | `E:\WORK\Streamworks\FT\Source\452_files\1%2.*`, `/source/files/*.txt` |
| **TargetFilePath** | string | ❌ NEIN | HIGH | Ziel-Verzeichnispfad (*nur für FILE_TRANSFER) | `E:\WORK\Streamworks\FT\Target`, `/target/`, `\\server\share\data\` |

---

## 🏗️ Stream Properties

Allgemeine Stream-Eigenschaften, die für alle Job-Types gelten.

### Stream Design Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| StreamType | string | ❌ | `Normal` | Stream-Typ | ALL |
| StatusFlag | boolean | ❌ | `false` | Stream aktiviert/deaktiviert | ALL |
| StreamVersion | string | ❌ | `1.0` | Stream-Versionsnummer | ALL |

### Stream Account Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| AccountNoId | string | ❌ | `111111111` | Account-Nummer für Stream | ALL |
| CalendarId | string | ❌ | `UATDefaultCalendar` | Kalender-ID für Scheduling | ALL |

### Stream Concurrency Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| ConcurrentPlanDatesEnabled | boolean | ❌ | `false` | Parallele Plan-Daten erlaubt | ALL |
| ConcurrentStreamRunsEnabled | boolean | ❌ | `false` | Parallele Stream-Läufe erlaubt | ALL |

### Stream Severity Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| SeverityGroup | string | ❌ | `Low` | Wichtigkeitsstufe: Low, Medium, High | ALL |

---

## 🔧 Job Properties

Job-spezifische Eigenschaften.

### Job Execution Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| JobStatusFlag | boolean | ❌ | `false` | Job aktiviert/deaktiviert | ALL |
| JobType | enum | ❌ | `Windows` | Job-Ausführungstyp: Windows, Unix, None | STANDARD, SAP |
| MaxJobDuration | string | ❌ | - | Maximale Job-Laufzeit | ALL |
| DisplayOrder | integer | ❌ | `2` | Anzeigereihenfolge im UI | ALL |
| TemplateType | string | ❌ | `Normal` | Template-Typ: Normal, FileTransfer | ALL |

### Job Script Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| ExternalJobScriptRequired | boolean | ❌ | `false` | Externes Job-Script erforderlich | ALL |
| LoginObject | string | ❌ | - | Login-Objekt für Job-Ausführung | ALL |

### Job Log Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| CentralJobLogAreaFlag | boolean | ❌ | `true` | Zentrales Job-Log verwenden | ALL |
| AgentJobLogStorageDays | integer | ❌ | `10` | Speichertage für Agent-Logs | ALL |
| MaxJobLogSize | float | ❌ | `5.00` | Maximale Log-Größe in MB | ALL |

---

## ⏰ Scheduling & Runtime

Scheduling und Runtime-Verwaltung.

### Scheduling Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| SchedulingRequiredFlag | boolean | ❌ | `true` | Zeitgesteuert (true) oder manuell (false) | ALL |
| StartTime | string | ❌ | - | Startzeit im Format HH:MM | ALL |
| ScheduleRuleObject | string | ❌ | - | Schedule-Regel-Objekt | ALL |
| ScheduleRuleXml | string | ❌ | `<SchedulingRules...>` | XML-Darstellung der Schedule-Regel | ALL |

**Validierung:**
- `StartTime`: Pattern `^([01]?[0-9]|2[0-3]):[0-5][0-9]$` (HH:MM Format)

### Preparation Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| AutoPreparationType | string | ❌ | `Complete` | Auto-Vorbereitung: Complete, None | ALL |
| AutomaticPreparedRuns | integer | ❌ | `0` | Automatisch vorbereitete Läufe | ALL |

### Runtime Data Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| RuntimeDataStorageDays | integer | ❌ | `50` | Speichertage für Runtime-Daten | ALL |

### Cleanup Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Job-Types |
|-----------|-----|---------|---------|--------------|-----------|
| StreamRunDeletionTime | string | ❌ | `00:15:00` | Löschzeit für Stream-Läufe | ALL |
| StreamRunDeletionDayType | string | ❌ | `Calendar day` | Tag-Typ für Löschung | ALL |
| StreamRunDeletionDays | integer | ❌ | `1` | Anzahl Tage bis zur Löschung | ALL |
| DeletionTimeTimeZoneId | string | ❌ | `UTC+1:00` | Zeitzone für Löschzeit | ALL |
| StreamRunDeletionType | string | ❌ | `Export` | Löschtyp: Export, None | ALL |

---

## 📁 File Transfer Specific

Parameter speziell für FILE_TRANSFER Job-Type.

### File Transfer Agent Properties

| Parameter | Typ | Pflicht | Default | Beschreibung |
|-----------|-----|---------|---------|--------------|
| SourceAgent | string | ✅ JA | - | Quell-Agent/Server |
| TargetAgent | string | ✅ JA | - | Ziel-Agent/Server |
| SourceLoginObject | string | ❌ | - | Login-Objekt für Quelle |
| TargetLoginObject | string | ❌ | - | Login-Objekt für Ziel |

### File Transfer Path Properties

| Parameter | Typ | Pflicht | Default | Beschreibung |
|-----------|-----|---------|---------|--------------|
| SourceFilePattern | string | ❌ | - | Quell-Dateipfad oder Pattern (z.B. `*.csv`) |
| TargetFilePath | string | ❌ | - | Ziel-Verzeichnispfad |
| TargetFileName | string | ❌ | - | Ziel-Dateiname (optional, für Umbenennung) |
| ControlFilePathFlag | boolean | ❌ | `false` | Control-File verwenden |

### File Transfer Behavior Properties

| Parameter | Typ | Pflicht | Default | Beschreibung |
|-----------|-----|---------|---------|--------------|
| SourceUnfulfilledHandling | string | ❌ | `Abort` | Verhalten bei fehlenden Quelldateien: Abort, Continue |
| SourceFileDeleteFlag | boolean | ❌ | `false` | Quelldateien nach Transfer löschen |
| TargetFileExistsHandling | string | ❌ | `Overwrite` | Verhalten bei existierenden Zieldateien: Overwrite, Skip, Rename |
| UseSourceAttributesFlag | boolean | ❌ | `false` | Quell-Attribute (Timestamp etc.) übernehmen |

### File Transfer Encoding Properties

| Parameter | Typ | Pflicht | Default | Beschreibung |
|-----------|-----|---------|---------|--------------|
| SourceEncodingDetail | string | ❌ | - | Encoding der Quelldateien |
| TargetEncodingDetail | string | ❌ | - | Encoding der Zieldateien |
| LinebreakTranslationType | string | ❌ | `None` | Zeilenumbruch-Konvertierung: None, Unix2Windows, Windows2Unix |
| DeleteTrailingBlanksFlag | boolean | ❌ | `false` | Trailing Blanks entfernen |

---

## 🟦 SAP Specific

Parameter speziell für SAP Job-Type.

### SAP Connection Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Beispiele |
|-----------|-----|---------|---------|--------------|-----------|
| system | enum | ✅ JA | - | SAP System-ID | `ZTV`, `ZTJ`, `GT123`, `PA1`, `PT1`, `PD1` |
| client | string | ❌ | `100` | SAP Mandant/Client | `300`, `514`, `100`, `200` |
| user | string | ❌ | - | SAP-User für Anmeldung | `SAPCOMM`, `BATCHUSER` |

### SAP Program Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Beispiele |
|-----------|-----|---------|---------|--------------|-----------|
| program | string | ❌ | - | SAP Programm/Report/Kommando | `EXE_CAL_EXPORT`, `EXECUTE`, `BTCSPOOL` |
| variant | string | ❌ | - | Report-Variante | `EXCEL_DAILY`, `ZTEST_VAR01` |
| job_name | string | ❌ | - | SAP Job-Name für Monitoring | `FA_EXPORT_DAILY`, `CALENDAR_SYNC` |
| parameters | string | ❌ | - | Zusätzliche SAP-Parameter (Key:Value) | `I_CALENDER_ID_W:09`, `OUT_FILE:calendar_01` |

### SAP Output Properties

| Parameter | Typ | Pflicht | Default | Beschreibung | Beispiele |
|-----------|-----|---------|---------|--------------|-----------|
| output_settings | string | ❌ | - | Output/Spool-Konfiguration | `-SPOOL`, `OUT_DIR:c:\temp`, `PP_PDEST:LOCAL` |

---

## 👥 Contact & Version Properties

Kontakt- und Versionsinformationen.

### Contact Properties

| Parameter | Typ | Pflicht | Default | Beschreibung |
|-----------|-----|---------|---------|--------------|
| contact_first_name | string | ❌ | `System` | Vorname des Ansprechpartners |
| contact_last_name | string | ❌ | `Generated` | Nachname des Ansprechpartners |
| contact_middle_name | string | ❌ | - | Zweiter Vorname |
| company_name | string | ❌ | `Streamworks` | Firmenname |
| department | string | ❌ | - | Abteilung |
| contact_type | string | ❌ | `None` | Kontakt-Typ |
| hierarchy_level_cd | integer | ❌ | `1` | Hierarchie-Level |

### Version Properties

| Parameter | Typ | Pflicht | Default | Beschreibung |
|-----------|-----|---------|---------|--------------|
| stream_version_type | string | ❌ | `Current` | Version-Typ: Current, Archived |
| deployment_date_time | string | ❌ | (current timestamp) | Deployment-Zeitpunkt |
| deploy_as_active | boolean | ❌ | `true` | Als aktiv deployen |
| auto_deployment_status | string | ❌ | `Finished` | Auto-Deployment-Status |
| schedule_rules_merge_type | string | ❌ | `FromNew` | Schedule-Merge-Typ |

---

## 🎨 Parameter-Prioritäten

Die Parameter sind in 3 Prioritätsstufen eingeteilt:

### CRITICAL Priority (🔴)
**Muss zuerst extrahiert werden** - ohne diese Parameter kann der Stream nicht funktionieren:
- `StreamName`
- `AgentDetail`
- `MainScript` (nur STANDARD)
- `SourceAgent` (nur FILE_TRANSFER)
- `TargetAgent` (nur FILE_TRANSFER)

### HIGH Priority (🟡)
**Wichtig für Funktionalität** - sollte zeitnah extrahiert werden:
- `ShortDescription`
- `JobName`
- `JobShortDescription`
- `MaxStreamRuns`
- `SourceFilePattern` (FILE_TRANSFER)
- `TargetFilePath` (FILE_TRANSFER)

### MEDIUM Priority (🟢)
**Kann später ergänzt werden** - Nice-to-have oder mit guten Defaults:
- `StreamDocumentation`
- Alle anderen optionalen Parameter

---

## 🏷️ Job-Type-Zuordnung

### STANDARD Job-Type
**Erforderliche Parameter:**
- `StreamName` (CRITICAL)
- `AgentDetail` (CRITICAL)
- `MainScript` (CRITICAL)
- `JobName` (HIGH)
- `ShortDescription` (HIGH)

**Optionale Parameter:**
- Alle Stream Properties
- Alle Job Properties
- Alle Scheduling Properties

### FILE_TRANSFER Job-Type
**Erforderliche Parameter:**
- `StreamName` (CRITICAL)
- `SourceAgent` (CRITICAL)
- `TargetAgent` (CRITICAL)
- `JobName` (HIGH)
- `ShortDescription` (HIGH)

**Optionale Parameter:**
- `SourceFilePattern` (HIGH)
- `TargetFilePath` (HIGH)
- Alle Stream Properties
- Alle File Transfer Specific Properties
- Alle Scheduling Properties

**Hinweis:** Bei FILE_TRANSFER wird `AgentDetail` oft aus `SourceAgent` oder `TargetAgent` abgeleitet.

### SAP Job-Type
**Erforderliche Parameter:**
- `StreamName` (CRITICAL)
- `AgentDetail` (CRITICAL)
- `system` (CRITICAL)
- `JobName` (HIGH)
- `ShortDescription` (HIGH)

**Optionale Parameter:**
- `client` (HIGH)
- `program` (HIGH)
- `user` (MEDIUM)
- `variant` (MEDIUM)
- Alle Stream Properties
- Alle SAP Specific Properties
- Alle Scheduling Properties

---

## 📊 Parameter-Statistik

### Gesamt-Übersicht

| Kategorie | Anzahl Parameter |
|-----------|------------------|
| **Kritische Parameter** | 12 |
| Stream Properties | ~25 |
| Job Properties | ~15 |
| Scheduling & Runtime | ~15 |
| File Transfer Specific | ~15 |
| SAP Specific | ~8 |
| Contact & Version | ~15 |
| **GESAMT** | ~105 Parameter |

### Job-Type Breakdown

| Job-Type | Required Parameters | Optional Parameters |
|----------|---------------------|---------------------|
| STANDARD | 5 | ~60 |
| FILE_TRANSFER | 7 | ~75 |
| SAP | 6 | ~65 |

---

## 🔍 Verwendung in LangExtract

Die LangExtract Parameter-Extraktion fokussiert sich auf die **12 kritischen Parameter**:

```python
# Beispiel: Required Parameters für FILE_TRANSFER
required_params = [
    "StreamName",           # CRITICAL
    "SourceAgent",          # CRITICAL
    "TargetAgent",          # CRITICAL
    "JobName",              # HIGH
    "ShortDescription",     # HIGH
    "SourceFilePattern",    # HIGH
    "TargetFilePath",       # HIGH
    "MaxStreamRuns"         # HIGH
]
```

**Alle anderen Parameter** werden entweder:
- Aus den kritischen Parametern abgeleitet
- Mit intelligenten Default-Werten befüllt
- Durch Template-Engine automatisch generiert

---

## 📝 Hinweise zur Verwendung

### 1. Namenskonventionen
- **StreamName**: Sollte dem Pattern `zsw_*` oder `GECK003_*` folgen
- **JobName**: Wird automatisch im Format `0100_<StreamName>` generiert

### 2. Agent-Namen
- Agent-Namen werden **case-sensitiv** und **vollständig** übernommen
- Beispiel: `servera` (lowercase) vs `ServerA` (CamelCase)

### 3. Dateipfade
- Windows-Pfade: `C:\Pfad\Datei.txt` oder `\\server\share\datei.txt`
- Unix-Pfade: `/pfad/datei.txt`
- Patterns: `*.csv`, `file_*.txt`, `*.{csv,txt}`

### 4. Zeitangaben
- **StartTime**: Format `HH:MM` (z.B. `08:00`, `14:30`)
- **Zeitzonen**: UTC+1:00, UTC, etc.

### 5. Boolean-Werte
- Akzeptiert: `true`, `false`, `yes`, `no`, `ja`, `nein`, `1`, `0`
- In XML als: `<StatusFlag>true</StatusFlag>`

---

## 🔗 Verwandte Dokumentation

- **Parameter Extraction**: `backend/services/ai/enhanced_unified_parameter_extractor.py`
- **Parameter Mapping**: `backend/services/xml_generation/parameter_mapper.py`
- **Required Parameters Schema**: `backend/schemas/required_parameters.py`
- **XML Templates**: `backend/templates/xml_templates/`
- **LangExtract Schemas**: `backend/templates/langextract_schemas.json`

---

**Letzte Aktualisierung:** 2025-10-22
**System Version:** Streamworks-KI v0.14
