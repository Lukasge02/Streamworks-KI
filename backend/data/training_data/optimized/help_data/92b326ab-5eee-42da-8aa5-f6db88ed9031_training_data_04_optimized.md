# Training Data 04

**Automatisch generiert aus**: 92b326ab-5eee-42da-8aa5-f6db88ed9031_training_data_04.txt  
**Konvertiert am**: 04.07.2025 15:17  
**Typ**: StreamWorks-Dokumentation

---

```
StreamWorks **XML** (XML-Konfiguration)-Konfiguration
```

```
XML-STRUKTUR:
StreamWorks verwendet XML-basierte Konfigurationsdateien für die Definition von Jobs und Streams. Die XML-Struktur folgt einem vordefinierten Schema.
```


## GRUNDLEGENDE STRUKTUR

```
<?xml version="1.0" encoding="UTF-8"?>
<**stream** (Stream-Verarbeitung) xmlns="http://streamworks.com/schema/v1">
```

  <metadata>
    <name>JobName</name>
    <description>Beschreibung</description>
    <version>1.0</version>
  </metadata>
  <**schedule** (Zeitplanung)>
    <**cron** (Cron-Ausdruck)>0 2 * * *</cron>
    <timezone>Europe/Berlin</timezone>
  </schedule>
```
  <jobs>
```

    <**job** (Verarbeitungsauftrag) id="1">
      <name>ProcessingJob</name>
      <type>**batch** (Batch-Verarbeitung)</type>
      <parameters>
        <parameter name="input" type="path">/data/input</parameter>
        <parameter name="output" type="path">/data/output</parameter>
      </parameters>
    </job>
  </jobs>
</stream>


## WICHTIGE ELEMENTE



### METADATA

- name: Eindeutiger Name des Streams
- description: Beschreibung des Zwecks
- version: Versionsnummer
- owner: Verantwortlicher Benutzer
- tags: Kategorisierung


### ⏰ SCHEDULE

- cron: Cron-Ausdruck für Zeitplanung
- timezone: Zeitzone für Ausführung
- enabled: Aktiv/Inaktiv Status


### JOBS

- id: Eindeutige Job-ID
- name: Anzeigename
- type: Job-Typ (batch, streaming, etc.)
- parameters: Job-spezifische Parameter
- dependencies: Abhängigkeiten zu anderen Jobs


### PARAMETER-TYPEN

- string: Textparameter
- integer: Ganzzahl
- boolean: Wahr/Falsch
- path: Dateipfad
- date: Datum
- array: Liste von Werten


### ⚙️ BEISPIEL-KONFIGURATIONEN



## 📥 DATENIMPORT

```
<job id="**import** (Datenimport)" type="batch">
```

  <name>**CSV** (CSV-Datenverarbeitung)-Import</name>
  <parameters>
    <parameter name="source" type="path">/data/csv/*.csv</parameter>
    <parameter name="delimiter" type="string">,</parameter>
    <parameter name="header" type="boolean">true</parameter>
    <parameter name="target_table" type="string">imported_data</parameter>
  </parameters>
</job>


## 📤 DATENEXPORT

```
<job id="**export** (Datenexport)" type="batch">
```

  <name>Report-Export</name>
  <parameters>
```
    <parameter name="query" type="string">SELECT * FROM reports</parameter>
```

    <parameter name="format" type="string">xlsx</parameter>
    <parameter name="output" type="path">/data/reports/</parameter>
  </parameters>
</job>


## VALIDIERUNG

```
StreamWorks validiert alle XML-Konfigurationen gegen das Schema. Fehler werden beim Import gemeldet.
```


## BEST PRACTICES

- Verwenden Sie aussagekräftige Namen
- Dokumentieren Sie komplexe Konfigurationen
```
- Versionieren Sie Ihre XML-Dateien
```

- Testen Sie Konfigurationen in der Entwicklungsumgebung
- Verwenden Sie Kommentare für Erklärungen


## ❌ COMMON ERRORS

- Fehlende Namespace-Deklaration
- Ungültige Cron-Ausdrücke
- Falsche Parameter-Typen
```
- Nicht geschlossene XML-Tags
```

---

## 📊 Dokumenten-Metadaten

### 🏷️ Schlüsselwörter
batch, cron, csv, data, error, export, import, job, jobs, process, schedule, schema, script, stream, streamworks, struktur, version, xml

### 🎯 Themen
Batch-Verarbeitung, Zeitplanung, Konfiguration, Troubleshooting, Datenverarbeitung, PowerShell, FAQ

### 📈 Komplexität
Mittel (Fortgeschritten)

### 🌐 Sprache
Deutsch

### 🔍 Suchbegriffe
batch, batch verarbeitung, batch-verarbeitung, cron, cron-ausdruck, csv, csv-datenverarbeitung, data, datenexport, datenimport, datenstream, datenverarbeitung, error, export, faq

### 📏 Statistiken
- **Wortanzahl**: 239 Wörter
- **Zeilen**: 96 Zeilen
- **Geschätzte Lesezeit**: 1 Minuten

---

*Dieses Dokument wurde automatisch für StreamWorks-KI optimiert - 04.07.2025 15:17*
