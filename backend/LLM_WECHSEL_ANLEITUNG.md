# LLM Modell Wechsel Anleitung 🤖

## ⚠️ WICHTIG: Priorität der Konfiguration

**Die .env Datei überschreibt IMMER die config.py!**

### Reihenfolge der Konfiguration:
1. `.env` Datei (höchste Priorität)
2. `app/core/config.py` (wird überschrieben)
3. Umgebungsvariablen

## 🔧 Modell wechseln - Schritt für Schritt

### 1. Backend stoppen
```bash
# Im Backend Terminal: CTRL+C
```

### 2. .env Datei bearbeiten
```bash
# Datei: backend/.env
MODEL_NAME=neues/modell-name
MAX_NEW_TOKENS=200  # Je nach Modell anpassen
DEVICE=mps          # mps für Mac, cuda für GPU, cpu für CPU
USE_LORA=False      # Für Tests deaktivieren
```

### 3. Python Cache löschen (optional)
```bash
cd backend
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
```

### 4. Backend neu starten
```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

### 5. Testen
```bash
# Health Check
curl http://localhost:8000/api/v1/chat/health

# Sollte das neue Modell zeigen:
# {"model_name": "neues/modell-name", "llm_initialized": false}
```

## 📋 Unterstützte Modelle

### Schnelle Modelle (für Entwicklung):
- `microsoft/phi-2` (2.7B) - Empfohlen für Tests
- `microsoft/DialoGPT-medium` (355M) - Sehr schnell
- `distilgpt2` (82M) - Ultra schnell

### Code-Modelle (für Produktion):
- `codellama/CodeLlama-7b-Instruct-hf` - Beste Qualität
- `codellama/CodeLlama-13b-Instruct-hf` - Sehr gut, aber langsam
- `WizardLM/WizardCoder-3B-V1.0` - Kompromiss

### Deutsche Modelle:
- `LeoLM/leo-hessianai-7b` - Deutsch optimiert
- `malteos/herberta-base` - Deutsch BERT

## ⚙️ Modell-spezifische Einstellungen

### Phi-2 (microsoft/phi-2):
```env
MODEL_NAME=microsoft/phi-2
MAX_TOKEN_LENGTH=1024
MAX_NEW_TOKENS=200
TEMPERATURE=0.7
USE_LORA=False
```

### Code-Llama 7B:
```env
MODEL_NAME=codellama/CodeLlama-7b-Instruct-hf
MAX_TOKEN_LENGTH=2048
MAX_NEW_TOKENS=512
TEMPERATURE=0.1
USE_LORA=True
LORA_RANK=16
```

### Für schwächere Hardware:
```env
MODEL_NAME=microsoft/phi-2
MAX_TOKEN_LENGTH=512
MAX_NEW_TOKENS=100
DEVICE=cpu
USE_LORA=False
```

## 🔍 Debugging

### Health Check zeigt falsches Modell:
1. `.env` Datei prüfen (überschreibt config.py!)
2. Backend komplett neu starten
3. Cache löschen

### Modell lädt nicht:
1. Internetverbindung prüfen
2. HuggingFace Token setzen (bei privaten Modellen)
3. Speicherplatz prüfen (~5-15GB pro Modell)

### Generierung hängt:
1. `MAX_NEW_TOKENS` reduzieren (50-100)
2. `TEMPERATURE` erhöhen (0.8-1.0)
3. `DEVICE=cpu` testen

### Out of Memory Fehler:
1. Kleineres Modell wählen
2. `MAX_TOKEN_LENGTH` reduzieren
3. Quantisierung aktivieren (nur CUDA)

## 📊 Performance Vergleich (Mac M3)

| Modell | Größe | Ladezeit | Generierung | Qualität |
|--------|-------|----------|-------------|----------|
| phi-2 | 2.7B | ~8s | ~3s | Gut |
| CodeLlama-7B | 7B | ~25s | ~10s | Sehr gut |
| DialoGPT-medium | 355M | ~3s | ~1s | Basic |

## 🎯 Empfehlungen

### Für Entwicklung/Tests:
- **microsoft/phi-2** - Bester Kompromiss

### Für Fine-Tuning:
- **codellama/CodeLlama-7b-Instruct-hf** - Optimal für LoRA

### Für Demo/Präsentation:
- **microsoft/phi-2** - Schnell und zuverlässig

### Für Produktion:
- **codellama/CodeLlama-7b-Instruct-hf** + Fine-Tuning

## 🚨 Häufige Fehler

1. **Config in config.py ändern aber .env vergessen** ❌
2. **Backend nicht neu starten** ❌  
3. **Zu große Token-Limits für kleines Modell** ❌
4. **LoRA mit inkompatiblem Modell** ❌
5. **Falsches Device (cuda auf Mac)** ❌

## ✅ Checkliste für Modell-Wechsel

- [ ] Backend gestoppt (CTRL+C)
- [ ] .env Datei bearbeitet (nicht config.py!)
- [ ] TOKEN_LIMITS angepasst
- [ ] DEVICE korrekt gesetzt
- [ ] Backend neu gestartet
- [ ] Health Check getestet
- [ ] Chat getestet

---

**Erstellt von Claude Code am 03.07.2025**
**Für StreamWorks-KI Bachelorarbeit Projekt**