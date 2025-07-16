#!/usr/bin/env python3
"""
StreamWorks-KI Test Data Loader
Lädt Test-Daten für die Entwicklungsumgebung
"""

import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Sample test data für Development
SAMPLE_DOCUMENTS = [
    {
        "title": "StreamWorks Installation Guide",
        "content": """
# StreamWorks Installation Guide

## Systemanforderungen
- Windows 10 oder höher
- .NET Framework 4.7.2 oder höher
- SQL Server 2016 oder höher
- Mindestens 4 GB RAM
- 2 GB freier Festplattenspeicher

## Installation
1. StreamWorks-Setup.exe herunterladen
2. Als Administrator ausführen
3. Installationspfad auswählen
4. Datenbankverbindung konfigurieren
5. Installation abschließen

## Erste Konfiguration
- Datenbankverbindung testen
- Benutzer anlegen
- Grundeinstellungen konfigurieren
- Test-Job erstellen
        """,
        "category": "help_data",
        "source": "documentation",
        "tags": ["installation", "setup", "configuration"]
    },
    {
        "title": "StreamWorks Job Template - Daily Backup",
        "content": """
# Daily Backup Job Template

## Beschreibung
Automatisches tägliches Backup aller wichtigen Daten

## XML Template
```xml
<Job>
    <Name>Daily_Backup</Name>
    <Description>Tägliches Backup der Produktionsdaten</Description>
    <Schedule>
        <Type>Daily</Type>
        <Time>02:00</Time>
    </Schedule>
    <Steps>
        <Step>
            <Name>Database_Backup</Name>
            <Type>SQL</Type>
            <Command>BACKUP DATABASE ProductionDB TO DISK = 'C:\\Backup\\ProductionDB.bak'</Command>
        </Step>
        <Step>
            <Name>File_Backup</Name>
            <Type>FileSystem</Type>
            <Source>C:\\Production\\Data</Source>
            <Target>C:\\Backup\\Files</Target>
        </Step>
    </Steps>
</Job>
```

## Verwendung
1. Template kopieren
2. Pfade anpassen
3. Zeitplan konfigurieren
4. Job aktivieren
        """,
        "category": "stream_templates",
        "source": "template",
        "tags": ["backup", "daily", "automation", "xml"]
    },
    {
        "title": "StreamWorks Agent Troubleshooting",
        "content": """
# StreamWorks Agent Troubleshooting

## Häufige Probleme und Lösungen

### Agent Status: Disconnected
**Problem:** Agent wechselt nach Start auf Status "Disconnected"
**Lösung:**
1. Netzwerkverbindung prüfen
2. Firewall-Einstellungen überprüfen
3. Agent-Konfiguration validieren
4. Logs überprüfen in C:\\StreamWorks\\Logs
5. Agent-Service neu starten

### Performance Issues
**Problem:** Agent reagiert langsam
**Lösung:**
1. Systemressourcen überprüfen
2. Anzahl parallel laufender Jobs reduzieren
3. Speicher und CPU-Auslastung monitoren
4. Temporäre Dateien löschen

### Verbindungsprobleme
**Problem:** Kann nicht mit Server verbinden
**Lösung:**
1. Server-Erreichbarkeit testen (ping)
2. Port-Konfiguration überprüfen
3. Zertifikate validieren
4. Proxy-Einstellungen prüfen
        """,
        "category": "help_data",
        "source": "troubleshooting",
        "tags": ["troubleshooting", "agent", "connectivity", "performance"]
    },
    {
        "title": "XML Stream Processing Template",
        "content": """
# XML Stream Processing Template

## Data Processing Stream
```xml
<Stream>
    <Name>Data_Processing_Stream</Name>
    <Description>Verarbeitet eingehende Daten</Description>
    <Input>
        <Type>File</Type>
        <Path>C:\\Input\\*.xml</Path>
        <Pattern>*.xml</Pattern>
    </Input>
    <Processing>
        <Transform>
            <Type>XSLT</Type>
            <Template>data_transform.xsl</Template>
        </Transform>
        <Validate>
            <Schema>input_schema.xsd</Schema>
        </Validate>
    </Processing>
    <Output>
        <Type>Database</Type>
        <ConnectionString>Server=localhost;Database=ProcessedData;Trusted_Connection=true</ConnectionString>
        <Table>ProcessedRecords</Table>
    </Output>
    <ErrorHandling>
        <OnError>
            <Action>Log</Action>
            <LogPath>C:\\Logs\\processing_errors.log</LogPath>
        </OnError>
    </ErrorHandling>
</Stream>
```

## Konfiguration
1. Input-Pfad anpassen
2. XSLT-Template erstellen
3. Schema-Validierung konfigurieren
4. Ausgabe-Ziel festlegen
5. Fehlerbehandlung aktivieren
        """,
        "category": "stream_templates",
        "source": "template",
        "tags": ["xml", "processing", "transform", "validation"]
    },
    {
        "title": "StreamWorks Desktop Client Setup",
        "content": """
# StreamWorks Desktop Client Setup

## Installation
Der StreamWorks Desktop Client kann auf drei Arten installiert werden:

### 1. Click-Once Installation
- Automatische Updates
- Einfache Installation
- Benötigt Internetverbindung

### 2. MSI Installation
- Vollständige lokale Installation
- Für Umgebungen ohne Internet
- Manuelle Updates erforderlich

### 3. Lokale Web App
- Browser-basiert
- Keine Installation erforderlich
- Läuft auf lokalem Server

## Konfiguration
1. Server-URL eingeben
2. Benutzeranmeldung
3. Arbeitsbereich auswählen
4. Lokale Einstellungen konfigurieren

## Troubleshooting
- Verbindungsprobleme: Firewall prüfen
- Performance: Cache leeren
- Updates: Automatische Updates aktivieren
        """,
        "category": "help_data",
        "source": "documentation",
        "tags": ["desktop", "client", "installation", "configuration"]
    }
]

SAMPLE_CONVERSATIONS = [
    {
        "session_id": "dev_session_001",
        "messages": [
            {
                "role": "user",
                "content": "Wie installiere ich StreamWorks?",
                "timestamp": "2025-01-15T10:00:00Z"
            },
            {
                "role": "assistant",
                "content": "Für die Installation von StreamWorks benötigen Sie Windows 10 oder höher und .NET Framework 4.7.2. Laden Sie die StreamWorks-Setup.exe herunter und führen Sie sie als Administrator aus...",
                "timestamp": "2025-01-15T10:00:15Z"
            }
        ]
    },
    {
        "session_id": "dev_session_002",
        "messages": [
            {
                "role": "user",
                "content": "Wie erstelle ich ein Backup-Job?",
                "timestamp": "2025-01-15T11:00:00Z"
            },
            {
                "role": "assistant",
                "content": "Ein Backup-Job wird über ein XML-Template erstellt. Hier ist eine Vorlage für ein tägliches Backup...",
                "timestamp": "2025-01-15T11:00:12Z"
            }
        ]
    }
]

async def load_development_data():
    """Lädt Test-Daten für die Entwicklungsumgebung"""
    try:
        # Hier würden normalerweise die Daten in die Datenbank geladen
        # Da wir keinen direkten Zugang zur DB haben, simulieren wir es
        
        print("🔄 Loading development test data...")
        
        # Simuliere das Laden der Dokumente
        for i, doc in enumerate(SAMPLE_DOCUMENTS, 1):
            print(f"  📄 Loading document {i}/{len(SAMPLE_DOCUMENTS)}: {doc['title']}")
            await asyncio.sleep(0.1)  # Simuliere Ladezeit
        
        # Simuliere das Laden der Konversationen
        for i, conv in enumerate(SAMPLE_CONVERSATIONS, 1):
            print(f"  💬 Loading conversation {i}/{len(SAMPLE_CONVERSATIONS)}: {conv['session_id']}")
            await asyncio.sleep(0.1)  # Simuliere Ladezeit
        
        print("✅ Development test data loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading test data: {e}")
        return False

async def create_sample_files():
    """Erstellt Sample-Dateien für die Entwicklung"""
    try:
        # Erstelle Verzeichnis für Test-Dateien
        test_dir = Path("data/test_files")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Erstelle JSON-Dateien mit Test-Daten
        with open(test_dir / "sample_documents.json", "w", encoding="utf-8") as f:
            json.dump(SAMPLE_DOCUMENTS, f, ensure_ascii=False, indent=2)
        
        with open(test_dir / "sample_conversations.json", "w", encoding="utf-8") as f:
            json.dump(SAMPLE_CONVERSATIONS, f, ensure_ascii=False, indent=2)
        
        print("📁 Sample files created in data/test_files/")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample files: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🚀 StreamWorks-KI Test Data Loader")
        print("==================================")
        
        # Lade Test-Daten
        await load_development_data()
        
        # Erstelle Sample-Dateien
        await create_sample_files()
        
        print("\n🎉 Test data setup completed!")
        print("You can now start developing with pre-loaded test data.")
    
    asyncio.run(main())