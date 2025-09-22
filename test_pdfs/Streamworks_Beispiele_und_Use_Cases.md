# Streamworks Beispiele und Use Cases

## Übersicht

Diese Sammlung zeigt praktische Beispiele für verschiedene Stream-Typen im Streamworks-KI System mit konkreten Konfigurationen und Anwendungsfällen.

---

## SAP Stream Beispiele

### Beispiel 1: Täglicher SAP Fabrikkalender Export

**Use Case**: Automatischer Export des SAP Fabrikkalenders für die Produktionsplanung

**Stream-Konfiguration**:
```json
{
  "stream_name": "PROD_Daily_Calendar_Export",
  "agent_detail": "gtlnmiwvm1636",
  "short_description": "Täglicher Export des SAP Fabrikkalenders",
  "calendar_id": "ProductionCalendar",
  "sap_system": "PRD",
  "sap_mandant": "100",
  "sap_transaction": "EXE_CAL_EXPORT",
  "sap_job_type": "EXPORT",
  "calendar_export": true,
  "jexa_parameters": {
    "user": "EXPORT_USER",
    "variant": "DAILY_EXPORT",
    "output_file": "fabrikkalender_{date}.xml",
    "output_dir": "C:\\SAP\\Export\\Calendar"
  }
}
```

**Generiertes XML-Fragment**:
```xml
<StreamName>PROD_Daily_Calendar_Export</StreamName>
<ShortDescription>SAP Job: PRD - EXE_CAL_EXPORT</ShortDescription>
<JobSapProperty>
  <SapSystem>PRD</SapSystem>
  <SapClient>100</SapClient>
  <SapTransaction>EXE_CAL_EXPORT</SapTransaction>
  <SapOutputPath>/sap/export/calendar/</SapOutputPath>
</JobSapProperty>
```

**Einsatzszenario**:
- Läuft täglich um 6:00 Uhr
- Exportiert Kalenderdaten für die nächsten 30 Tage
- Benachrichtigung bei Fehlern an Produktionsplanung

---

### Beispiel 2: SAP Report mit Parametern

**Use Case**: Wöchentlicher Umsatzbericht mit dynamischen Parametern

**Stream-Konfiguration**:
```json
{
  "stream_name": "ZSW_Weekly_Sales_Report",
  "agent_detail": "gtasswvv15778",
  "short_description": "Wöchentlicher SAP Umsatzbericht",
  "calendar_id": "UATDefaultCalendar",
  "sap_system": "QAS",
  "sap_mandant": "300",
  "sap_transaction": "ZSW_SALES_REPORT",
  "sap_job_type": "REPORT",
  "jexa_parameters": {
    "user": "REPORT_USER",
    "variant": "WEEKLY_SALES",
    "output_file": "sales_report_{week}_{year}.pdf",
    "output_dir": "\\\\fileserver\\reports\\sales"
  },
  "sap_parameters": {
    "P_WERKS": "1000",
    "P_BUKRS": "1000",
    "P_GJAHR": "2024",
    "P_MONAT": "01-12"
  }
}
```

**SAP-spezifische Parameter**:
- **P_WERKS**: Werk (1000 = Hauptwerk)
- **P_BUKRS**: Buchungskreis
- **P_GJAHR**: Geschäftsjahr
- **P_MONAT**: Monatsbereich

---

### Beispiel 3: SAP Batch Job mit Monitoring

**Use Case**: Nächtliche Datensynchronisation mit Fehlerbehandlung

**Stream-Konfiguration**:
```json
{
  "stream_name": "SYNC_Nightly_Data_Transfer",
  "agent_detail": "prodagent001",
  "short_description": "Nächtliche Datensynchronisation zwischen SAP-Systemen",
  "calendar_id": "ProductionCalendar",
  "max_stream_runs": 1,
  "sap_system": "PRD",
  "sap_mandant": "100",
  "sap_transaction": "ZSW_DATA_SYNC",
  "sap_job_type": "BATCH",
  "sap_wait_time": 120,
  "sap_retry_count": 5,
  "scheduling_required": true
}
```

**Besonderheiten**:
- Maximale Laufzeit: 1 parallele Ausführung
- Erweiterte Wartezeit: 120 Sekunden
- 5 Wiederholungsversuche bei Fehlern
- Produktionskalender für Scheduling

---

## File Transfer Stream Beispiele

### Beispiel 4: Automatischer Datei-Backup

**Use Case**: Tägliche Sicherung von Produktionsdateien

**Stream-Konfiguration**:
```json
{
  "stream_name": "BACKUP_Production_Files",
  "agent_detail": "gtlnmiwvm1636",
  "short_description": "Tägliche Sicherung der Produktionsdateien",
  "calendar_id": "UATDefaultCalendar",
  "source_agent": "prodserver01",
  "target_agent": "backupserver",
  "source_path": "C:\\Production\\Data",
  "target_path": "D:\\Backup\\Production",
  "transfer_method": "COPY",
  "file_pattern": "*.{xml,csv,txt}",
  "delete_source": false,
  "archive_mode": true,
  "platform": "Windows"
}
```

**Transfer-Details**:
- **Quelle**: Produktionsserver
- **Ziel**: Backup-Server
- **Dateitypen**: XML, CSV, TXT
- **Archivierung**: Aktiviert für Langzeitspeicherung

---

### Beispiel 5: SFTP Upload zu externem Partner

**Use Case**: Sicherer Datentransfer zu Geschäftspartner

**Stream-Konfiguration**:
```json
{
  "stream_name": "PARTNER_Secure_Upload",
  "agent_detail": "dmz-agent",
  "short_description": "Sicherer Upload zu Geschäftspartner",
  "calendar_id": "BusinessCalendar",
  "source_agent": "internalserver",
  "target_agent": "partner-sftp.example.com",
  "source_path": "/opt/export/partner",
  "target_path": "/incoming/data",
  "transfer_method": "SFTP",
  "file_pattern": "*_EXPORT_*.xml",
  "delete_source": true,
  "archive_mode": false,
  "platform": "Linux"
}
```

**Sicherheitsaspekte**:
- SFTP für verschlüsselte Übertragung
- DMZ-Agent für Netzwerksicherheit
- Quelldateien werden nach Transfer gelöscht
- Spezifisches Datei-Pattern für Partner

---

### Beispiel 6: Multi-Platform Sync

**Use Case**: Synchronisation zwischen Windows und Linux Systemen

**Stream-Konfiguration**:
```json
{
  "stream_name": "SYNC_Cross_Platform",
  "agent_detail": "syncagent01",
  "short_description": "Plattformübergreifende Dateisynchronisation",
  "calendar_id": "UATDefaultCalendar",
  "source_agent": "winserver2019",
  "target_agent": "linuxserver",
  "source_path": "C:\\Shared\\Data",
  "target_path": "/mnt/shared/data",
  "transfer_method": "RSYNC",
  "file_pattern": "*",
  "delete_source": false,
  "archive_mode": true,
  "platform": "Linux"
}
```

**Plattform-Details**:
- **Windows → Linux** Transfer
- RSYNC für efiziente Synchronisation
- Alle Dateien werden übertragen
- Archivierung auf Linux-Seite

---

## Standard Stream Beispiele

### Beispiel 7: Python Datenverarbeitung

**Use Case**: Automatisierte Datenanalyse mit Python

**Stream-Konfiguration**:
```json
{
  "stream_name": "ANALYTICS_Daily_Processing",
  "agent_detail": "analyticsagent",
  "short_description": "Tägliche Datenanalyse und Reportgenerierung",
  "calendar_id": "AnalyticsCalendar",
  "main_script": "python data_processor.py --mode daily --output reports/",
  "job_type": "Linux",
  "working_directory": "/opt/analytics",
  "parameters": "--verbose --email-report admin@company.com",
  "environment_variables": {
    "PYTHONPATH": "/opt/analytics/lib",
    "DATA_SOURCE": "postgresql://localhost/analytics",
    "LOG_LEVEL": "INFO"
  },
  "timeout": 120
}
```

**Script-Details**:
- Python-basierte Datenverarbeitung
- Maximale Laufzeit: 2 Stunden
- E-Mail-Benachrichtigung nach Abschluss
- Datenbankverbindung über Environment Variable

---

### Beispiel 8: Windows Batch Verarbeitung

**Use Case**: Legacy System Integration mit Batch-Skripten

**Stream-Konfiguration**:
```json
{
  "stream_name": "LEGACY_Batch_Integration",
  "agent_detail": "legacyagent",
  "short_description": "Integration mit Legacy-System über Batch-Verarbeitung",
  "calendar_id": "ProductionCalendar",
  "main_script": "@echo off\\ncd /d C:\\Legacy\\Scripts\\ncall import_data.bat\\nif %ERRORLEVEL% EQU 0 (\\n    echo Success\\n    call notify_success.bat\\n) else (\\n    echo Error: %ERRORLEVEL%\\n    call notify_error.bat\\n)",
  "job_type": "Windows",
  "working_directory": "C:\\Legacy\\Scripts",
  "parameters": "/LOG:C:\\Logs\\legacy_import.log",
  "timeout": 60
}
```

**Batch-Features**:
- Fehlerbehandlung mit ERRORLEVEL
- Logging in separate Datei
- Erfolg/Fehler-Benachrichtigung
- Maximale Laufzeit: 1 Stunde

---

### Beispiel 9: Database Maintenance

**Use Case**: Automatische Datenbankwartung

**Stream-Konfiguration**:
```json
{
  "stream_name": "DB_Weekly_Maintenance",
  "agent_detail": "dbagent",
  "short_description": "Wöchentliche Datenbankwartung und Optimierung",
  "calendar_id": "MaintenanceCalendar",
  "main_script": "#!/bin/bash\\nset -e\\n\\n# Backup erstellen\\npg_dump proddb > /backup/proddb_$(date +%Y%m%d).sql\\n\\n# Index-Rebuild\\npsql proddb -c \"REINDEX DATABASE proddb;\"\\n\\n# Statistiken aktualisieren\\npsql proddb -c \"ANALYZE;\"\\n\\n# Alte Backups löschen (>30 Tage)\\nfind /backup -name \"proddb_*.sql\" -mtime +30 -delete\\n\\necho \"Maintenance completed successfully\"",
  "job_type": "Linux",
  "working_directory": "/opt/maintenance",
  "environment_variables": {
    "PGPASSWORD": "{{DB_PASSWORD}}",
    "PGUSER": "maintenance",
    "PGHOST": "dbserver.local"
  },
  "timeout": 180
}
```

**Wartungsaufgaben**:
- Automatisches Backup
- Index-Rebuild für Performance
- Statistiken-Update
- Cleanup alter Backups
- Maximale Laufzeit: 3 Stunden

---

## Komplexe Use Cases

### Beispiel 10: Multi-Step Workflow

**Use Case**: Mehrstufiger Workflow mit Abhängigkeiten

**Workflow-Beschreibung**:
1. **Step 1**: SAP Datenexport
2. **Step 2**: Dateitransfer zu Verarbeitungsserver
3. **Step 3**: Python-Datenverarbeitung
4. **Step 4**: Ergebnis-Upload zu Reporting-System

**Stream 1 - SAP Export**:
```json
{
  "stream_name": "WORKFLOW_01_SAP_Export",
  "sap_system": "PRD",
  "sap_transaction": "ZSW_EXPORT_ORDERS",
  "jexa_parameters": {
    "output_file": "orders_{date}.xml",
    "output_dir": "C:\\Export\\Orders"
  }
}
```

**Stream 2 - File Transfer**:
```json
{
  "stream_name": "WORKFLOW_02_Transfer",
  "source_path": "C:\\Export\\Orders",
  "target_path": "/opt/processing/input",
  "file_pattern": "orders_*.xml",
  "transfer_method": "SFTP"
}
```

**Stream 3 - Processing**:
```json
{
  "stream_name": "WORKFLOW_03_Processing",
  "main_script": "python process_orders.py --input /opt/processing/input --output /opt/processing/output",
  "job_type": "Linux"
}
```

**Stream-Abhängigkeiten**:
- Stream 2 startet nur bei erfolgreichem Abschluss von Stream 1
- Stream 3 startet nur bei erfolgreichem Abschluss von Stream 2
- Bei Fehlern: Automatische Benachrichtigung und Workflow-Stop

---

### Beispiel 11: Conditional Execution

**Use Case**: Bedingte Ausführung basierend auf Datenverfügbarkeit

**Stream-Konfiguration**:
```json
{
  "stream_name": "CONDITIONAL_Data_Processing",
  "agent_detail": "smartagent",
  "short_description": "Datenverarbeitung nur bei verfügbaren Dateien",
  "main_script": "#!/bin/bash\\n\\n# Prüfe ob Eingabedateien vorhanden\\nif [ $(find /input -name \"*.csv\" | wc -l) -gt 0 ]; then\\n    echo \"Dateien gefunden, starte Verarbeitung\"\\n    python process_data.py\\n    echo \"Verarbeitung abgeschlossen\"\\nelse\\n    echo \"Keine Dateien gefunden, überspringe Verarbeitung\"\\n    exit 0\\nfi",
  "job_type": "Linux",
  "environment_variables": {
    "INPUT_DIR": "/input",
    "OUTPUT_DIR": "/output",
    "NOTIFY_EMAIL": "ops@company.com"
  }
}
```

**Conditional Logic**:
- Prüfung auf Eingabedateien vor Verarbeitung
- Graceful Exit wenn keine Daten vorhanden
- E-Mail-Benachrichtigung über Status

---

## Performance und Monitoring

### Beispiel 12: High-Performance Bulk Transfer

**Use Case**: Großmengen-Datentransfer mit Optimierung

**Stream-Konfiguration**:
```json
{
  "stream_name": "BULK_High_Performance_Transfer",
  "agent_detail": "bulkagent",
  "short_description": "Optimierter Transfer für große Datenmengen",
  "calendar_id": "NightlyCalendar",
  "max_stream_runs": 3,
  "source_agent": "datawarehouse",
  "target_agent": "analyticscluster",
  "source_path": "/data/warehouse/bulk",
  "target_path": "/mnt/analytics/incoming",
  "transfer_method": "RSYNC",
  "file_pattern": "*.parquet",
  "platform": "Linux",
  "archive_mode": true
}
```

**Performance-Optimierungen**:
- Parallele Übertragung (max 3 Streams)
- RSYNC für effizienten Transfer
- Parquet-Format für komprimierte Daten
- Nächtliche Ausführung für optimale Bandbreite

---

## Testing und Debugging

### Beispiel 13: Test Environment Setup

**Use Case**: Automatisierte Test-Umgebung Einrichtung

**Stream-Konfiguration**:
```json
{
  "stream_name": "TEST_Environment_Setup",
  "agent_detail": "testagent",
  "short_description": "Automatische Einrichtung der Test-Umgebung",
  "calendar_id": "TestCalendar",
  "main_script": "#!/bin/bash\\nset -e\\n\\n# Test-Datenbank zurücksetzen\\ndropdb testdb || true\\ncreatedb testdb\\npsql testdb < /sql/test_schema.sql\\n\\n# Test-Daten laden\\npython load_test_data.py\\n\\n# Services starten\\nsudo systemctl start test-api\\nsudo systemctl start test-worker\\n\\n# Health Check\\ncurl -f http://localhost:8080/health || exit 1\\n\\necho \"Test environment ready\"",
  "job_type": "Linux",
  "working_directory": "/opt/testing",
  "timeout": 30
}
```

**Test-Funktionen**:
- Datenbank-Reset und Schema-Setup
- Test-Daten automatisch laden
- Service-Start und Health-Check
- Schnelle Ausführung (30 Minuten max)

---

Diese Beispiele zeigen die Vielseitigkeit des Streamworks-KI Systems und decken typische Enterprise-Szenarien ab. Jeder Stream kann individuell angepasst und erweitert werden, um spezifische Anforderungen zu erfüllen.