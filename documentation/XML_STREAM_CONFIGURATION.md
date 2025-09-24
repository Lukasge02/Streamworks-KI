# XML Stream Configuration Guide

> **Anleitung für Stream-Prefix und XML-Template Konfigurationen im Streamworks-KI System**

## 🎯 **Übersicht**

Das Streamworks-KI System generiert XML-Streams mit konfigurierbaren Prefixes. Diese Dokumentation erklärt **wo und wie** Stream-Namen Prefixes geändert werden können.

### **Aktuelle Konfiguration:**
- **Default Prefix**: `zsw_` (geändert von `STREAM_`)
- **Beispiel-Output**: `zsw_12345`, `zsw_FILE_TRANSFER_20250923`
- **System**: Template-basierte XML-Generierung mit Jinja2

---

## 🔧 **Die 3 kritischen Stellen für Stream-Prefixes**

### **1. Parameter Mapper (HAUPTVERURSACHER)** ⭐

**📁 Datei**: `backend/services/xml_generation/parameter_mapper.py`
**📍 Zeile**: ~261
**🎯 Funktion**: `_normalize_stream_name()`

```python
def _normalize_stream_name(self, value: str) -> str:
    """Normalize stream name to valid format"""
    if not value:
        return value

    # Remove special characters, replace spaces/dashes with underscores
    normalized = re.sub(r'[^\w\-]', '_', str(value))
    normalized = re.sub(r'[-\s]+', '_', normalized)
    normalized = re.sub(r'_+', '_', normalized)
    normalized = normalized.strip('_')

    # ⭐ HIER: Stream-Prefix definieren
    if normalized and not normalized[0].isalpha():
        normalized = f"zsw_{normalized}"  # ← ÄNDERN FÜR NEUEN PREFIX

    return normalized.upper()
```

**📝 Zweck**: Fügt Prefix hinzu wenn Stream-Name nicht mit Buchstabe beginnt
**🔧 Beispiel**: `"123"` wird zu `"zsw_123"`

---

### **2. Template Engine (Auto-Generation)**

**📁 Datei**: `backend/services/xml_generation/template_engine.py`
**📍 Zeile**: ~89
**🎯 Funktion**: `model_post_init()`

```python
def model_post_init(self, __context: Any) -> None:
    """Post-initialization logic"""
    # Auto-generate names if not provided
    if not self.stream_name:
        # ⭐ HIER: Auto-generierte Stream-Namen
        self.stream_name = f"zsw_{self.timestamp}"  # ← ÄNDERN FÜR NEUEN PREFIX
```

**📝 Zweck**: Auto-generierte Stream-Namen bei leeren Eingaben
**🔧 Beispiel**: Generiert `"zsw_20250923_143015"`

---

### **3. LangExtract Service (Fallback)**

**📁 Datei**: `backend/services/ai/langextract/unified_langextract_service.py`
**📍 Zeile**: ~1284
**🎯 Funktion**: XML Storage Request

```python
# 🗄️ Store XML in dual storage (Supabase + Local)
storage_request = XMLStorageRequest(
    session_id=session_id,
    # ⭐ HIER: Fallback Stream-Namen
    stream_name=mapped_parameters.get("stream_name", f"zsw_{target_job_type}"),  # ← ÄNDERN
    job_type=target_job_type,
    xml_content=xml_content,
    # ...
)
```

**📝 Zweck**: Fallback Stream-Namen für XML-Speicherung
**🔧 Beispiel**: `"zsw_FILE_TRANSFER"`

---

## 🔍 **Stream-Prefix Änderungen: Schritt-für-Schritt**

### **Schritt 1: Aktuellen Prefix finden**
```bash
cd backend
grep -r "zsw_" services/
# oder
grep -r "STREAM_" services/
```

### **Schritt 2: Die 3 Stellen ändern**

1. **Parameter Mapper** (Line ~261):
   ```python
   normalized = f"NEUER_PREFIX_{normalized}"
   ```

2. **Template Engine** (Line ~89):
   ```python
   self.stream_name = f"NEUER_PREFIX_{self.timestamp}"
   ```

3. **LangExtract Service** (Line ~1284):
   ```python
   stream_name=mapped_parameters.get("stream_name", f"NEUER_PREFIX_{target_job_type}"),
   ```

### **Schritt 3: Backend neu starten**
```bash
cd backend
# Bestehende Prozesse stoppen
lsof -ti:8000 | xargs kill

# Backend neu starten
/opt/homebrew/bin/python3.10 main.py
```

### **Schritt 4: Änderungen testen**
```bash
# Health Check
curl -s http://localhost:8000/api/xml-generator/template/health

# Test XML Generation (optional)
curl -s -X POST "http://localhost:8000/api/xml-generator/template/generate" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "detected_job_type": "FILE_TRANSFER", "extracted_parameters": {"stream_name": "12345"}}'
```

---

## 📋 **Template-System Übersicht**

### **XML Templates Location:**
```
backend/templates/xml_templates/
├── standard_job_template.xml      # Standard Jobs
├── file_transfer_template.xml     # File Transfer Jobs
└── sap_job_template.xml          # SAP Jobs
```

### **Template Variable für Stream-Namen:**
```xml
<StreamName>{{ stream_name | default('FT_STREAM_' + (timestamp | string)) }}</StreamName>
```

**📝 Hinweis**: Templates verwenden die Variable `{{ stream_name }}` - keine direkte Änderung nötig!

---

## 🚨 **Häufige Fallstricken**

### **❌ Was NICHT funktioniert:**
1. **Nur Template ändern**: Templates verwenden Variablen - der Prefix wird in Python generiert
2. **Frontend-Änderungen**: Frontend zeigt nur an was Backend generiert
3. **Nur eine Stelle ändern**: Alle 3 Stellen müssen konsistent sein

### **✅ Wichtige Punkte:**
- **Konsistenz**: Alle 3 Stellen müssen den gleichen Prefix verwenden
- **Backend Neustart**: Notwendig für Änderungen
- **Case Sensitivity**: `_normalize_stream_name()` macht alles UPPERCASE
- **Alphanumerisch**: Prefix sollte mit Buchstabe beginnen

---

## 🔧 **Erweiterte Konfigurationen**

### **Conditional Prefixes (erweitert):**
```python
def _normalize_stream_name(self, value: str, job_type: str = None) -> str:
    # Prefix basierend auf Job-Type
    prefixes = {
        "FILE_TRANSFER": "ft_",
        "SAP": "sap_",
        "STANDARD": "std_"
    }
    prefix = prefixes.get(job_type, "zsw_")

    if normalized and not normalized[0].isalpha():
        normalized = f"{prefix}{normalized}"

    return normalized.upper()
```

### **Environment-basierte Prefixes:**
```python
import os
PREFIX = os.getenv("STREAM_PREFIX", "zsw_")

# Verwendung:
normalized = f"{PREFIX}_{normalized}"
```

---

## 📊 **Test Cases**

### **Input → Output Beispiele:**

| Input | Parameter Mapper | Template Engine | LangExtract | Final Output |
|-------|-----------------|-----------------|-------------|--------------|
| `"12345"` | `zsw_12345` | - | - | `ZSW_12345` |
| `""` (leer) | - | `zsw_20250923_143015` | - | `zsw_20250923_143015` |
| `None` | - | - | `zsw_FILE_TRANSFER` | `zsw_FILE_TRANSFER` |
| `"Test Stream"` | `TEST_STREAM` | - | - | `TEST_STREAM` |

---

## 🔄 **Migration Guide**

### **Von STREAM_ zu anderem Prefix:**

1. **Backup erstellen**:
   ```bash
   git stash push -m "Before prefix change"
   ```

2. **Änderungen durchführen** (siehe Schritt-für-Schritt oben)

3. **Testen**:
   ```bash
   # Backend starten und testen
   /opt/homebrew/bin/python3.10 main.py
   ```

4. **Commit**:
   ```bash
   git add .
   git commit -m "Change stream prefix from STREAM_ to NEW_PREFIX_"
   ```

---

## 📞 **Support & Troubleshooting**

### **Häufige Probleme:**

1. **"Backend startet nicht"**
   - Check: Python 3.10 verwenden
   - Check: `langextract` Dependency installiert

2. **"Prefix erscheint nicht"**
   - Check: Alle 3 Stellen geändert?
   - Check: Backend neu gestartet?

3. **"XML Generation fehlt"**
   - Check: Health Endpoint: `/api/xml-generator/template/health`

### **Debug Commands:**
```bash
# Backend Logs
tail -f backend/logs/streamworks.log

# Health Check
curl http://localhost:8000/health

# XML Generator Status
curl http://localhost:8000/api/xml-generator/template/health
```

---

**📅 Erstellt**: 2025-09-23
**🔄 Letzte Änderung**: Erfolgreiche Umstellung von `STREAM_` auf `zsw_`
**👤 Maintainer**: Streamworks-KI Development Team