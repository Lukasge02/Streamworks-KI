# Streamworks Parameter Dokumentation

## Übersicht

Das Streamworks-KI System verwaltet verschiedene Stream-Typen mit spezifischen Parametern. Diese Dokumentation beschreibt alle verfügbaren Parameter und deren Verwendung.

## Stream-Typen

### 1. Standard Stream (STANDARD)
Allgemeine Job-Ausführung für Skripte und Anwendungen.

### 2. SAP Stream (SAP)
Speziell für SAP-Systeme und jexa4S Integration.

### 3. File Transfer Stream (FILE_TRANSFER)
Für Dateiübertragungen zwischen Agenten.

### 4. Custom Stream (CUSTOM)
Benutzerdefinierte Streams (verwendet Standard-Schema als Fallback).

---

## Basis-Parameter (für alle Stream-Typen)

### Erforderliche Parameter

| Parameter | Typ | Beschreibung | Beispiele |
|-----------|-----|--------------|-----------|
| `stream_name` | String | Eindeutiger Name des Streams | "StrJ_AC_SAP_Export", "ZSW-T-WIN-FILE-TRANSFER" |
| `agent_detail` | String | Agent auf dem der Stream läuft | "gtlnmiwvm1636", "prodagent001" |
| `short_description` | String | Kurzbeschreibung des Stream-Zwecks | "Täglicher SAP-Export", "Datei-Backup" |
| `calendar_id` | String | Kalender für Scheduling | "UATDefaultCalendar", "ProductionCalendar" |

### Optionale Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `max_stream_runs` | Integer | 10 | Maximale parallele Ausführungen (1-1000) |
| `stream_documentation` | String | - | Ausführliche Dokumentation (mehrzeilig) |
| `scheduling_required` | Boolean | True | Ob Scheduling erforderlich ist |

---

## SAP Stream Parameter

### SAP-spezifische erforderliche Parameter

| Parameter | Typ | Beschreibung | Beispiele | Validation |
|-----------|-----|--------------|-----------|------------|
| `sap_system` | String | SAP System ID | "ZTV", "PA1", "PRD" | 3 Zeichen |
| `sap_mandant` | String | SAP Mandant/Client | "100", "300", "500" | 3 Ziffern |
| `sap_transaction` | String | SAP Transaktion oder Report | "EXE_CAL_EXPORT", "SE16", "RSBDCOS0" | - |

### SAP-spezifische optionale Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `jexa_parameters` | Dict | - | jexa4S spezifische Parameter (user, variant, output_file, output_dir) |
| `sap_job_type` | Enum | "EXPORT" | Art des SAP Jobs: EXPORT, IMPORT, REPORT, BATCH |
| `calendar_export` | Boolean | False | Ob Fabrikkalender exportiert wird |

### SAP XML Template Parameter

Zusätzliche Parameter für die XML-Generierung:

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `sap_client` | String | "100" | SAP Client für Verbindung |
| `sap_user` | String | "SAP_USER" | SAP Benutzername |
| `sap_language` | String | "DE" | SAP Sprache |
| `sap_report` | String | - | SAP Report Name |
| `sap_variant` | String | - | Report-Variante |
| `sap_output_format` | String | "SPOOL" | Ausgabeformat |
| `sap_output_path` | String | "/sap/output/" | Ausgabepfad |
| `sap_archive_mode` | Boolean | False | Archivierung aktiviert |
| `sap_wait_time` | Integer | 30 | Wartezeit in Sekunden |
| `sap_retry_count` | Integer | 3 | Anzahl Wiederholungen |

---

## File Transfer Stream Parameter

### Transfer-spezifische erforderliche Parameter

| Parameter | Typ | Beschreibung | Beispiele |
|-----------|-----|--------------|-----------|
| `source_agent` | String | Quell-Agent für Dateiübertragung | "gtlnmiwvm1636", "fileserver001" |
| `target_agent` | String | Ziel-Agent für Dateiübertragung | "gtasswvv15778", "backupserver" |
| `source_path` | String | Quellpfad der Dateien | "C:\\data\\export", "/home/data/" |
| `target_path` | String | Zielpfad der Dateien | "C:\\archive", "/backup/data" |

### Transfer-spezifische optionale Parameter

| Parameter | Typ | Standard | Beschreibung | Werte |
|-----------|-----|----------|--------------|-------|
| `transfer_method` | Enum | "COPY" | Übertragungsmethode | COPY, FTP, SFTP, RSYNC, SCP |
| `file_pattern` | String | "*.*" | Dateifilter/Pattern | "*.xml", "*.csv", "report_*.txt" |
| `delete_source` | Boolean | False | Quelldateien nach Transfer löschen | - |
| `archive_mode` | Boolean | False | Archivierung aktiviert | - |
| `platform` | Enum | "Windows" | Plattform/OS | Windows, Linux, Unix, AIX, SLES12, SLES15 |

---

## Standard Stream Parameter

### Standard-spezifische erforderliche Parameter

| Parameter | Typ | Beschreibung | Beispiele |
|-----------|-----|--------------|-----------|
| `main_script` | String | Hauptskript oder Befehl (mehrzeilig) | "python process.py", "batch_job.bat" |
| `job_type` | Enum | Betriebssystem/Plattform | Windows, Linux, Unix, None |

### Standard-spezifische optionale Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `working_directory` | String | - | Arbeitsverzeichnis | "C:\\scripts", "/opt/batch" |
| `parameters` | String | - | Skript-Parameter | "--input data.csv --output result.txt" |
| `environment_variables` | Dict | - | Umgebungsvariablen (PATH, CONFIG) |
| `timeout` | Integer | 0 | Maximale Laufzeit in Minuten (0 = unbegrenzt) |

---

## Parameter-Validierung

### Namenskonventionen

- **Stream Names**: Alphanumerisch mit Bindestrichen und Unterstrichen
- **SAP System**: Genau 3 Zeichen (A-Z, 0-9)
- **SAP Mandant**: Genau 3 Ziffern

### Beispiel-Prompts

Das System generiert intelligente Prompts für fehlende Parameter:

```
Stream Name: "Wie soll der Stream heißen? (z.B. PROD_Daily_Report oder ZSW-T-SAP-Export)"
SAP System: "Welches SAP-System? (z.B. ZTV, PA1, PRD)"
Agent Detail: "Auf welchem Agent soll der Stream laufen?"
```

### Parameter-Mapping

Die Parameter werden in verschiedenen Bereichen organisiert:

1. **Base Parameters**: Gemeinsam für alle Stream-Typen
2. **Type-specific Required**: Typ-spezifische Pflichtfelder
3. **Type-specific Optional**: Typ-spezifische optionale Felder

---

## XML-Generierung

### Template-System

Streams werden in XML-Templates konvertiert mit:

- **Jinja2-Templating**: `{{ parameter_name | default('default_value') }}`
- **Bedingte Blöcke**: `{% if condition %}...{% endif %}`
- **CDATA-Sections**: Für Skripte und mehrzeilige Inhalte

### Job-Struktur

Jeder Stream enthält standardmäßig drei Jobs:

1. **StartPoint**: Initialisierung
2. **Haupt-Job**: Eigentliche Ausführung (SAP, Transfer, Standard)
3. **EndPoint**: Abschluss

### Stream-Properties

- **RunNumber**: 0 (Standard), optional 1 für erweiterte Konfiguration
- **Scheduling**: Kalender-basierte Ausführung
- **Dependencies**: Job-Abhängigkeiten und Successors
- **Logging**: Central Job Log und Agent Log Konfiguration

---

## Verwendung im System

### API-Endpoints

- `POST /xml-streams/` - Stream erstellen
- `GET /xml-streams/{id}` - Stream abrufen
- `PUT /xml-streams/{id}` - Stream aktualisieren
- `DELETE /xml-streams/{id}` - Stream löschen

### Datenbank-Schema

Streams werden in der `XMLStream` Tabelle gespeichert mit:

- **wizard_data**: JSON mit Eingabeparametern
- **xml_content**: Generiertes XML
- **status**: draft, active, paused, archived
- **tags**: Array für Kategorisierung
- **is_favorite**: Favoriten-Status

### Service-Layer

- `XMLStreamService`: CRUD-Operationen
- `XMLTemplateEngine`: XML-Generierung
- `ParameterExtractor`: Parameter-Validierung