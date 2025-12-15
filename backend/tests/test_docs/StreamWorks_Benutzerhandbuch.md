# StreamWorks Benutzerhandbuch

## 1. Einführung

StreamWorks ist eine Enterprise-Plattform für Workflow-Automatisierung und Job-Scheduling. Diese Dokumentation beschreibt die grundlegenden Konzepte und Funktionen des Systems.

## 2. Grundkonzepte

### 2.1 Streams

Ein **Stream** ist die zentrale Einheit in StreamWorks. Ein Stream besteht aus:
- **Name**: Eindeutiger Bezeichner (max. 50 Zeichen)
- **Beschreibung**: Optionale Beschreibung des Zwecks
- **Jobs**: Liste von auszuführenden Jobs
- **Schedule**: Zeitplan für die automatische Ausführung
- **Tags**: Statische Labels zur Klassifikation

### 2.2 Jobs

Ein **Job** ist eine einzelne Aufgabe innerhalb eines Streams:
- **Typ**: Command, Script, SQL, oder File Transfer
- **Parameter**: Konfigurierbare Eingabewerte
- **Dependencies**: Abhängigkeiten zu anderen Jobs
- **Retry-Policy**: Verhalten bei Fehlern (max. 3 Wiederholungen)

### 2.3 Mandanten

StreamWorks unterstützt Multi-Tenancy durch **Mandanten**:
- Jeder Mandant hat isolierte Daten
- Benutzer gehören zu einem oder mehreren Mandanten
- Administratoren können mandantenübergreifend arbeiten

## 3. Benutzeroberfläche

### 3.1 Dashboard

Das Dashboard zeigt:
- Aktive Streams mit Status (Running, Waiting, Error)
- Letzte 10 Ausführungen mit Ergebnissen
- Aktuelle Warnungen und Fehler
- Ressourcenauslastung (CPU, Memory)

### 3.2 Stream-Editor

Im Stream-Editor können Sie:
1. Neue Streams erstellen
2. Jobs hinzufügen und konfigurieren
3. Abhängigkeiten definieren (Drag & Drop)
4. Zeitpläne festlegen (Cron-Syntax oder GUI)
5. Parameter definieren

### 3.3 Ausführungshistorie

Die Historie zeigt alle vergangenen Ausführungen:
- Start- und Endzeit
- Gesamtdauer
- Status jedes Jobs
- Logausgaben (klickbar für Details)

## 4. Konfiguration

### 4.1 Umgebungsvariablen

Wichtige Umgebungsvariablen:
- `STREAMWORKS_DB_HOST`: Datenbankserver (Standard: localhost)
- `STREAMWORKS_DB_PORT`: Datenbankport (Standard: 5432)
- `STREAMWORKS_LOG_LEVEL`: Log-Level (DEBUG, INFO, WARN, ERROR)
- `STREAMWORKS_MAX_WORKERS`: Maximale parallele Jobs (Standard: 10)

### 4.2 Datenbank

StreamWorks verwendet PostgreSQL 14+:
- Mindestens 4 GB RAM für DB-Server
- SSD-Speicher empfohlen
- Automatische Backups konfigurierbar

### 4.3 Authentifizierung

Unterstützte Methoden:
- **LDAP**: Active Directory Integration
- **SAML 2.0**: Single Sign-On
- **Lokale Benutzer**: Für Entwicklung/Test

## 5. Fehlerbehebung

### 5.1 Häufige Fehler

| Fehlercode | Beschreibung | Lösung |
|------------|--------------|--------|
| SW-1001 | Datenbankverbindung fehlgeschlagen | DB-Host und Port prüfen |
| SW-1002 | Authentifizierung fehlgeschlagen | Benutzerdaten prüfen |
| SW-1003 | Job-Timeout | Timeout erhöhen oder Job optimieren |
| SW-1004 | Ressourcenlimit erreicht | Max_Workers erhöhen |

### 5.2 Log-Analyse

Logs befinden sich unter:
- Linux: `/var/log/streamworks/`
- Windows: `C:\ProgramData\StreamWorks\Logs\`

Format: `YYYY-MM-DD HH:MM:SS [LEVEL] [Component] Message`

## 6. Best Practices

1. **Kleine Jobs**: Jobs sollten max. 15 Minuten dauern
2. **Fehlerbehandlung**: Immer Retry-Policy definieren
3. **Logging**: Wichtige Checkpoints loggen
4. **Tags nutzen**: Für bessere Übersicht und Suche
5. **Dokumentation**: Streams und Jobs beschreiben

## 7. Support

- **E-Mail**: support@streamworks.example.com
- **Telefon**: +49 123 456789
- **Online-Portal**: https://support.streamworks.example.com
