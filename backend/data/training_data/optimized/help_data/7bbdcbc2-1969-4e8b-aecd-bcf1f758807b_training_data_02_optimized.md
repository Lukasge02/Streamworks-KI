# Training Data 02

**Automatisch generiert aus**: 7bbdcbc2-1969-4e8b-aecd-bcf1f758807b_training_data_02.txt  
**Konvertiert am**: 04.07.2025 15:17  
**Typ**: StreamWorks-Dokumentation

---

**Cron** (Cron-Ausdruck)-Ausdrücke für StreamWorks Scheduling


### CRON-SYNTAX


### 🌊 Cron-Ausdrücke in StreamWorks folgen dem Standard-Format

- * * * * * (Minute Stunde Tag Monat Wochentag)


### FELDER ERKLÄRUNG

- Minute: 0-59
- Stunde: 0-23
- Tag: 1-31
- Monat: 1-12
- Wochentag: 0-6 (0 = Sonntag)


### HÄUFIGE BEISPIELE

0 2 * * * - Täglich um 2:00 Uhr
0 0 * * 0 - Jeden Sonntag um Mitternacht
0 */6 * * * - Alle 6 Stunden
0 9 1 * * - Jeden ersten Tag des Monats um 9:00 Uhr
0 8 * * 1-5 - Montag bis Freitag um 8:00 Uhr


## SPEZIELLE ZEICHEN

- * - Jeder Wert
, - Werteliste (1,3,5)
- - Bereich (1-5)
/ - Schritte (*/2 = alle 2)
? - Beliebig (nur bei Tag oder Wochentag)


## PRAKTISCHE BEISPIELE

**Backup** (Datensicherung)-**Job** (Verarbeitungsauftrag): 0 3 * * 0 (Sonntags um 3 Uhr)
Berichterstellung: 0 7 1 * * (Monatlich am 1. um 7 Uhr)
Überwachung: */15 * * * * (Alle 15 Minuten)
Datenimport: 0 1 * * 1-5 (Werktags um 1 Uhr)


### ZEITZONE

StreamWorks verwendet standardmäßig die Zeitzone Europe/Berlin. Berücksichtigen Sie Sommer-/Winterzeit bei der Planung.


## VALIDIERUNG

Testen Sie Cron-Ausdrücke vor der Produktionsnutzung. Falsche Ausdrücke können zu unerwarteten Ausführungszeiten führen.


## BEST PRACTICES

- Verwenden Sie aussagekräftige Namen für Ihre Jobs
- Vermeiden Sie Überlappungen bei ressourcenintensiven Jobs
- Planen Sie Wartungszeiten ein
- Dokumentieren Sie komplexe Zeitpläne


## TROUBLESHOOTING


### Wenn ein Job nicht zur erwarteten Zeit startet, überprüfen Sie

- Cron-Syntax auf Korrektheit
- Zeitzone-Einstellungen
- System-Uhrzeit
- Job-Status im Dashboard

---

## 📊 Dokumenten-Metadaten

### 🏷️ Schlüsselwörter
alle, backup, cron, import, job, stream, streamworks, system, wochentag, zeitzone

### 🎯 Themen
Batch-Verarbeitung, Zeitplanung, Monitoring, Konfiguration, Datenverarbeitung, Systemadministration

### 📈 Komplexität
Mittel (Fortgeschritten)

### 🌐 Sprache
Deutsch

### 🔍 Suchbegriffe
alle, backup, batch verarbeitung, cron, cron-ausdruck, datenimport, datensicherung, datenstream, datenverarbeitung, import, job, konfiguration, monitoring, stream, stream-verarbeitung

### 📏 Statistiken
- **Wortanzahl**: 247 Wörter
- **Zeilen**: 51 Zeilen
- **Geschätzte Lesezeit**: 1 Minuten

---

*Dieses Dokument wurde automatisch für StreamWorks-KI optimiert - 04.07.2025 15:17*
