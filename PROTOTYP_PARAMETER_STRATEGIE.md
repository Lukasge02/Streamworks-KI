# StreamWorks Prototyp Parameter-Strategie

**Ziel**: Minimale User-Eingaben, maximale XML-Qualität durch intelligente Auto-Generation

---

## ✅ **EXTRAKTION** (User muss eingeben)

### **📋 Stream-Grundlagen** (3 Parameter)
- `StreamName` - Eindeutiger Stream-Name
- `MaxStreamRuns` - Maximale parallele Ausführungen (1, 3, 5, 10, 20)
- `SchedulingRequiredFlag` - Zeitgesteuert (true) oder manuell (false)
- `StartTime` - Startzeit (z.B. "08:00", "14:30") - NUR wenn SchedulingRequiredFlag=true

### **📊 SAP-Jobs** (3 Parameter)
- `system` - SAP-System (PA1_100, GT123_PRD, PT1_100, etc.)
- `report` - Report/Programm-Name (ZTV_EXPORT_001, RSUSR003, etc.)
- `variant` - Report-Variante (DAILY_EXPORT, MONTHLY_REPORT, etc.) - OPTIONAL

### **📁 File Transfer-Jobs** (4 Parameter)
- `source_agent` - Quell-Agent/Server (GT123_Server, BASF_Agent, etc.)
- `target_agent` - Ziel-Agent/Server (BASF_Server, TargetAgent_002, etc.)
- `source_path` - Quell-Pfad (/data/export/*.csv, C:\Transfer\Files\) - OPTIONAL
- `target_path` - Ziel-Pfad (/backup/import/, D:\Incoming\) - OPTIONAL

### **⚙️ Standard/Script-Jobs** (2 Parameter)
- `MainScript` - Script-Inhalt (ls, python script.py, batch commands)
- `JobType` - Script-Typ (Windows, Unix) - oder AUTO-DETECT aus Script

**TOTAL EXTRAKTION: 6-9 Parameter (je nach Job-Typ)**

---

## 🤖 **AUTO-GENERATION** (Algorithmus erstellt automatisch)

### **🏷️ Namen & Identifikation**
- `JobName` - Auto: "StartPoint", "0010_{StreamName}", "0020_{StreamName}"
- `JobCategory` - Auto: "StartPoint" (Index 0), "Job" (Index 1+), "Endpoint" (letzter bei >2 Jobs)

### **📝 KI-Generierte Beschreibungen**
- `ShortDescription` - KI-generiert aus StreamName + Job-Typ (max. 50 Zeichen)
- `StreamDocumentation` - KI-generiert ausführliche Beschreibung basierend auf Parametern

### **🎨 UI & Layout**
- `CoordinateX` - Auto: 100 (alle Jobs gleiche X-Position)
- `CoordinateY` - Auto: 0, 150, 300, 450... (150px Abstand)
- `DisplayOrder` - Auto: 1, 2, 3, 4... (fortlaufend)

### **🔗 Workflow-Verbindungen**
- `JobInternalSuccessors` - Auto: StartPoint → Job1 → Job2 → ...
- `EdgeEndPosition` - Auto: 2 (Standard-Verbindung)
- `EdgeStartPosition` - Auto: 6 (Standard-Verbindung)

### **📝 Script-Templates** (für SAP)
- `MainScript` - Auto-generiert aus system + report + variant:
  ```
  cd C:\Program Files\Arvato Systems\jexa
  jexa4s {system} {report} EXECUTE JOB:{report} VARIANT:{variant}
  ```

### **📁 File Transfer Commands**
- `MainScript` - Auto-generiert für File Transfer:
  ```
  rem Transfer from {source_agent} to {target_agent}
  copy "{source_path}" "{target_path}"
  ```

**TOTAL AUTO-GENERATION: ~17 Parameter**

---

## ❌ **HARDCODING** (Feste Prototyp-Werte)

### **📋 Stream-Konfiguration**
- `StreamType` = "Normal"
- `StreamRunDeletionType` = "None"
- `AgentDetail` = "PrototypAgent"
- `CalendarId` = "Default Calendar"
- `AccountNoId` = "" (leer)
- `InteractivePslFlag` = false
- `ConcurrentPlanDatesEnabled` = false
- `StreamRunDeletionDays` = null
- `KeepPreparedRuns` = false
- `RuntimeDataStorageDays` = null
- `StreamRunInterval` = null

### **👷 Job-Konfiguration**
- `StatusFlag` = true
- `TemplateType` = "Normal"
- `NormalJobFlag` = true (false nur bei StartPoint)
- `IsNotificationRequired` = false
- `MinJobDuration` = null
- `CentralJobLogStorageDays` = null
- `ReportToIncidentManagementFlag` = false
- `ExternalJobScriptRequired` = false
- `JobShortName` = null
- `ControlFilePath` = null

### **🏢 Enterprise-Features** (Prototyp-Standard)
- `SeverityId` = "Super Low"
- `MaxStreamRunDuration` = null
- `MinStreamRunDuration` = null
- `CentralJobLogAreaFlag` = false
- `AgentJobLogStorageDays` = null
- `MaxJobLogSize` = null
- `ReorgType` = null
- `UncatExclusion` = null

### **📊 SAP-Spezifisch**
- `batch_user` = "BATCH_USER"
- `JobType` = "Windows" (für SAP-Jobs)

### **📁 File Transfer-Spezifisch**
- `JobType` = "FileTransfer"
- `AllocationType` = "Shared"
- `TransferMode` = "Binary"
- `OverwriteFlag` = true

### **⏰ Scheduling & Timing**
- `StartTimeTimeZone` = "(UTC+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna"
- `StartTimeDayType` = "CalendarDay"
- `StartTimeType` = "AbsoluteStartTime" (wenn StartTime extrahiert)
- `RelativeStartTime` = null
- `LatestStartTime` = null
- `LatestStartTimeAction` = null

### **🛠️ Error Handling** (Prototyp ohne)
- `RecoveryRules` = null
- `JobCompletionCodeRules` = null
- `JobNotificationRules` = null
- `JobHoldFlag` = false
- `BypassStatus` = null

### **🔗 Dependencies** (Prototyp ohne)
- `ExternalDependencies` = null
- `FileDependency` = null
- `LogicalResourceDependencies` = null

**TOTAL HARDCODING: ~35 Parameter**

---

## 📊 **Strategie-Übersicht**

| Kategorie | Anzahl | Begründung |
|-----------|--------|------------|
| **✅ EXTRAKTION** | 6-9 | Business-kritische, variable Parameter |
| **🤖 AUTO-GENERATION** | ~17 | Algorithmus-basiert, KI-generiert, intelligent |
| **❌ HARDCODING** | ~35 | Standard-Konfiguration, technische Details |
| **📊 TOTAL** | ~60 | Vollständige StreamWorks XML-Struktur |

## 🎯 **Prototyp-Vorteile**

### **👤 User Experience**
- Nur 6-9 relevante Eingaben statt 60+
- Fokus auf Business-Parameter
- KI-generierte Beschreibungen (kein manueller Text)
- Einfache Zeitangabe statt komplexer Scheduling-Parameter
- Kein technischer XML-Overhead

### **🤖 System Intelligence**
- Smart Defaults für alle Standard-Konfigurationen
- Algorithmus-basierte Layout-Generierung
- Template-System für Job-Type spezifische Scripts
- KI-generierte Beschreibungen basierend auf Stream-Kontext
- Intelligente Startzeit-Konfiguration (Zeitzone, DayType automatisch)

### **🚀 Entwicklung**
- 87% weniger Parameter-Extraktion (6-9 statt 60+)
- Konsistente XML-Qualität
- KI-Integration für bessere User Experience
- Einfache Erweiterbarkeit für Enterprise-Features

---

**Status**: Ready for Implementation
**Next**: User-Review und Anpassungen der Parameter-Listen