# 🧪 RAG-Chunking Evaluierungs-Anleitung

## 📋 Test-PDF Übersicht

Du hast jetzt 6 speziell entwickelte PDF-Dokumente zum manuellen Upload und Testen:

### 1. **01_mini_kuendigung.pdf** (1.9 KB)
- **Szenario**: Sehr kurzes Dokument (wie das ursprüngliche Kuendigung-Mietvertrag.pdf)
- **Erwartetes Verhalten**: 
  - ✅ **Mindestens 1 Chunk** (Single-Chunk Fallback)
  - ✅ **Quality Tier**: `mini_document` oder `small_document_relaxed`
  - ✅ **RAG Enhancement**: Document Type Detection (contract_notice)
- **Test**: Sollte NICHT mehr "0 Chunks" zeigen

### 2. **02_small_bewerbung.pdf** (2.4 KB)  
- **Szenario**: Kleines strukturiertes Dokument
- **Erwartetes Verhalten**:
  - ✅ **1-2 Chunks** à ~500-600 chars (RAG-optimal)
  - ✅ **Keine Über-Fragmentierung** (nicht 6+ kleine Chunks)
  - ✅ **Quality Tier**: `standard`
- **Test**: Optimaler RAG-Chunk-Größenbereich

### 3. **03_medium_projektplan.pdf** (3.7 KB)
- **Szenario**: Mittleres Dokument mit Struktur (Überschriften, Absätze)
- **Erwartetes Verhalten**:
  - ✅ **4-6 Chunks** à ~500-700 chars
  - ✅ **Strukturelle Aufteilung** nach Kapiteln
  - ✅ **Quality Tier**: `standard`
- **Test**: Intelligente Struktur-Erkennung

### 4. **04_table_verkaufsbericht.pdf** (4.1 KB)
- **Szenario**: Dokument mit mehreren Tabellen (wie parkpreiseuebersicht-fra.pdf)
- **Erwartetes Verhalten**:
  - ✅ **3-5 Chunks** (nicht 1 riesiger Chunk)
  - ✅ **Tabellen-Intelligenz**: Tabellen werden erkannt und sinnvoll aufgeteilt
  - ✅ **Quality Tier**: `table_content`
  - ✅ **Kein Single-Chunk Fallback**
- **Test**: Tabellen-spezifische Optimierung

### 5. **05_large_handbuch.pdf** (9.1 KB)
- **Szenario**: Großes mehrseitiges Dokument
- **Erwartetes Verhalten**:
  - ✅ **10-15 Chunks** à ~500-700 chars
  - ✅ **Kapitel-basierte Aufteilung**
  - ✅ **Konsistente Chunk-Größen**
- **Test**: Multi-Page Chunking Performance

### 6. **06_code_documentation.pdf** (3.2 KB)
- **Szenario**: Dokument mit Code-Blöcken
- **Erwartetes Verhalten**:
  - ✅ **Code-spezifische Chunk-Größe** (~450 chars target)
  - ✅ **Code-Block Erhaltung**
  - ✅ **Quality Tier**: `standard`
- **Test**: Content-Type spezifische Optimierung

---

## 🎯 Evaluierungs-Checkliste

Für jeden Upload prüfe folgende Metriken:

### ✅ Grundlegende Funktionalität
- [ ] **Dokument wird erfolgreich hochgeladen**
- [ ] **Mindestens 1 Chunk wird erstellt** (keine "0 Chunks" Fehler)
- [ ] **Chunks sind lesbar und vollständig**

### 📊 RAG-Performance Metriken
- [ ] **Chunk-Größe**: Durchschnitt zwischen 400-800 chars
- [ ] **Chunk-Anzahl**: Angemessen für Dokumentgröße
- [ ] **Quality Score**: > 0.3 für die meisten Chunks
- [ ] **Kein exzessiver Fallback**: Max. 1 Fallback-Chunk pro Dokument

### 🔍 Content-Type Spezifische Tests
- [ ] **Mini-Docs**: Document Type Detection funktioniert
- [ ] **Tabellen**: Werden als Tabellen erkannt und intelligent aufgeteilt
- [ ] **Code**: Code-Blöcke werden nicht zerstückelt
- [ ] **Struktur**: Überschriften und Absätze werden respektiert

### ⚡ Performance & Qualität
- [ ] **Verarbeitungszeit**: < 10 Sekunden pro Dokument
- [ ] **Speicher**: Keine Memory-Leaks bei Upload
- [ ] **Konsistenz**: Mehrfache Uploads produzieren identische Ergebnisse

---

## 🚨 Bekannte Issues zum Testen

### 1. **Single-Chunk Fallback Test**
- **Upload**: `01_mini_kuendigung.pdf`
- **Erwartet**: Mindestens 1 Chunk (vorher: 0 Chunks)
- **Prüfe**: Metadata enthält `fallback` oder `mini_document` Info

### 2. **Tabellen-Intelligence Test**
- **Upload**: `04_table_verkaufsbericht.pdf`
- **Erwartet**: 3-5 Chunks statt 1 großem Chunk
- **Prüfe**: Tabellen-spezifische Quality Tier

### 3. **Über-Fragmentierung Test**
- **Upload**: `02_small_bewerbung.pdf`
- **Erwartet**: 1-2 sinnvolle Chunks statt 6+ Mini-Chunks
- **Prüfe**: Durchschnittliche Chunk-Größe > 400 chars

---

## 📈 Erfolgs-Kriterien

### 🎯 **AUSGEZEICHNET** (90%+ Erfolg)
- Alle 6 PDFs werden korrekt verarbeitet
- Durchschnittliche Chunk-Größe: 500-650 chars
- Keine Single-Chunk Fallbacks bei Medium/Large Docs
- Tabellen werden intelligent aufgeteilt

### ✅ **GUT** (70%+ Erfolg)  
- 5/6 PDFs werden korrekt verarbeitet
- Durchschnittliche Chunk-Größe: 400-800 chars
- Max. 1 Single-Chunk Fallback
- Grundlegende Tabellen-Aufteilung funktioniert

### ⚠️ **VERBESSERUNG NÖTIG** (<70% Erfolg)
- Mehrere PDFs zeigen "0 Chunks" Fehler
- Chunk-Größen außerhalb RAG-optimal Bereich
- Excessive Fallback-Nutzung
- Tabellen werden nicht aufgeteilt

---

## 🔧 Quick Debug Commands

Falls du die Chunks manuell analysieren willst:

```bash
# Teste ein einzelnes PDF
cd backend
python3 -c "
from services.intelligent_chunker import IntelligentChunker, ContentType
import docling

# PDF verarbeiten
doc = docling.document_converter.DocumentConverter().convert('test_pdfs/01_mini_kuendigung.pdf')
content = doc.document.export_to_markdown()

# Chunken
chunker = IntelligentChunker()
chunks = chunker.chunk_content(content, ContentType.PDF)

print(f'Chunks: {len(chunks)}')
for i, chunk in enumerate(chunks):
    print(f'Chunk {i+1}: {len(chunk[\"content\"])} chars - {chunk.get(\"metadata\", {}).get(\"quality_tier\", \"standard\")}')
"
```

---

**🎉 Viel Erfolg beim Evaluieren! Die PDFs decken alle kritischen Chunking-Szenarien ab.**