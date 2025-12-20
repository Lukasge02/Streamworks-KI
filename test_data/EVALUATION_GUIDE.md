# Test Generation Evaluation Guide

## Übersicht

Dieses Dokument beschreibt, wie Sie die Test-Generierung evaluieren können, um sicherzustellen, dass alle Requirements aus dem DDD als Testfälle generiert wurden.

## Test-DDD

Ein umfassendes Test-DDD wurde erstellt unter:
- `test_data/test_ddd_comprehensive.md`

**Enthält:**
- 5 Use Cases (UC-001 bis UC-005)
- 8 Business Rules (BR-001 bis BR-008)
- 11 Error Codes (E-0001 bis E-0011)

## Evaluations-Schritte

### 1. Projekt erstellen

1. Öffnen Sie die Testing-Seite: `http://localhost:3000/testing`
2. Klicken Sie auf "Neues Projekt"
3. Geben Sie einen Namen ein, z.B. "User Management Test"

### 2. DDD hochladen

1. Öffnen Sie das erstellte Projekt
2. Laden Sie das Test-DDD hoch:
   - Klicken Sie auf "+ Hochladen" im DDD-Bereich
   - Wählen Sie `test_data/test_ddd_comprehensive.md`
   - Warten Sie bis die Verarbeitung abgeschlossen ist

### 3. Testplan generieren

1. Klicken Sie auf "Testplan generieren"
2. Warten Sie bis die Generierung abgeschlossen ist (kann 1-2 Minuten dauern)
3. Der Testplan wird automatisch angezeigt

### 4. Evaluation durchführen

#### Option A: Automatische Evaluation (Empfohlen)

1. Exportieren Sie den Testplan als JSON:
   - Öffnen Sie die Browser-Entwicklertools (F12)
   - Gehen Sie zur Network-Tab
   - Laden Sie den Testplan neu
   - Finden Sie die Request zu `/api/testing/projects/{id}/plans`
   - Kopieren Sie die Response (JSON)
   - Speichern Sie sie als `test_plan.json`

2. Führen Sie das Evaluations-Script aus:
```bash
cd backend
python scripts/evaluate_test_generation.py test_plan.json ../test_data/test_ddd_comprehensive.md
```

#### Option B: Manuelle Evaluation

1. Prüfen Sie im Frontend:
   - Coverage-Dashboard zeigt alle Use Cases, Business Rules und Error Codes
   - Coverage Gaps sind leer (oder erklären warum etwas fehlt)

2. Prüfen Sie die Testfälle:
   - Jeder Use Case sollte mindestens 1 Happy-Path-Test haben
   - Jeder Use Case sollte mindestens 1 Error-Handling-Test haben
   - Jede Business Rule sollte mindestens 1 Validation-Test haben
   - Jeder Error Code sollte genau 1 Negative-Test haben

## Erwartete Ergebnisse

### Mindestanzahl Testfälle

Basierend auf dem Multi-Pass-Generierungsalgorithmus:

- **Use Cases (5)**: 5 × 2 = 10 Tests (je 1 Happy Path + 1 Error)
- **Business Rules (8)**: 8 × 1 = 8 Tests (je 1 Validation)
- **Error Codes (11)**: 11 × 1 = 11 Tests (je 1 Negative)

**Gesamt: Mindestens 29 Testfälle**

### Coverage-Ziele

- **Use Cases**: 100% (alle UC-001 bis UC-005)
- **Business Rules**: 100% (alle BR-001 bis BR-008)
- **Error Codes**: 100% (alle E-0001 bis E-0011)

## Häufige Probleme

### Problem: Nicht alle Testfälle generiert

**Lösung:**
1. Prüfen Sie die DDD-Struktur - sind alle UC/BR/E-Codes korrekt formatiert?
2. Prüfen Sie die Logs im Backend für Fehler
3. Versuchen Sie die Generierung erneut

### Problem: Coverage Gaps angezeigt

**Lösung:**
1. Prüfen Sie die Coverage Gaps im Dashboard
2. Fügen Sie manuell fehlende Testfälle hinzu
3. Oder passen Sie das DDD an, um die fehlenden Requirements klarer zu beschreiben

### Problem: Zu viele Testfälle

**Lösung:**
- Das ist normal! Der Algorithmus kann zusätzliche Edge-Case-Tests generieren
- Prüfen Sie ob alle erwarteten Requirements abgedeckt sind

## Verbesserungen

Falls die Evaluation zeigt, dass Requirements fehlen:

1. **Backend-Logs prüfen**: Schauen Sie in die Logs während der Generierung
2. **Prompt anpassen**: Die Prompts in `domains/testing/service.py` können angepasst werden
3. **DDD-Struktur verbessern**: Klarere Formatierung hilft der AI

## Nächste Schritte

Nach erfolgreicher Evaluation:

1. ✅ Alle Requirements abgedeckt → System funktioniert korrekt
2. ⚠️ Einige Requirements fehlen → Anpassungen vornehmen
3. 📊 Coverage-Report exportieren für Dokumentation
