# API Documentation: RAG-System Integration

## Übersicht

Dieses Dokument beschreibt die Integration des RAG-Systems in bestehende Anwendungen. Das System ermöglicht semantische Suche und intelligente Dokumentenverarbeitung.

## Quick Start

### Installation

```bash
pip install rag-system
pip install -r requirements.txt
```

### Basis-Konfiguration

```python
from rag_system import RAGProcessor, EmbeddingService

# Initialisierung
processor = RAGProcessor(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size=512,
    overlap_ratio=0.1
)

# Dokument verarbeiten
result = processor.process_document("path/to/document.pdf")
```

## API Endpoints

### Document Processing

#### `POST /api/documents/upload`

Upload und Verarbeitung eines neuen Dokuments.

**Request Body:**
```json
{
  "file": "binary_file_data",
  "metadata": {
    "title": "Document Title",
    "category": "technical",
    "tags": ["ai", "machine-learning"]
  },
  "processing_options": {
    "chunk_size": 512,
    "extract_tables": true,
    "language": "de"
  }
}
```

**Response:**
```json
{
  "document_id": "doc_123456789",
  "status": "processed",
  "chunks_created": 25,
  "processing_time": 3.2,
  "metadata": {
    "size": 1024000,
    "pages": 15,
    "language_detected": "german"
  }
}
```

#### `GET /api/documents/{document_id}`

Abrufen der Dokumentinformationen und Chunks.

**Parameters:**
- `document_id` (string, required): Eindeutige Dokument-ID
- `include_chunks` (boolean, optional): Chunks in Response einschließen

### Search Operations

#### `POST /api/search/semantic`

Semantische Suche über alle verarbeiteten Dokumente.

**Request Body:**
```json
{
  "query": "Wie funktioniert Machine Learning?",
  "max_results": 10,
  "similarity_threshold": 0.7,
  "filters": {
    "category": ["technical", "research"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    }
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "doc_123456789",
      "chunk_id": "chunk_987654321",
      "similarity_score": 0.89,
      "content": "Machine Learning ist ein Teilbereich...",
      "metadata": {
        "page": 5,
        "section": "Grundlagen"
      }
    }
  ],
  "total_results": 15,
  "processing_time": 0.156
}
```

## Konfigurationsoptionen

### Chunking-Parameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `chunk_size` | integer | 512 | Zielgröße für Text-Chunks in Zeichen |
| `overlap_ratio` | float | 0.1 | Überlappung zwischen Chunks (0.0-0.5) |
| `min_chunk_size` | integer | 100 | Minimale Chunk-Größe |
| `max_chunk_size` | integer | 1000 | Maximale Chunk-Größe |

### Embedding-Modelle

Unterstützte Modelle:

1. **sentence-transformers/all-MiniLM-L6-v2**
   - Sprachen: Multilingual
   - Dimensionen: 384
   - Performance: Schnell
   - Empfohlen für: Allgemeine Anwendungen

2. **sentence-transformers/all-mpnet-base-v2**
   - Sprachen: Englisch
   - Dimensionen: 768
   - Performance: Hoch
   - Empfohlen für: Präzise semantische Suche

3. **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**
   - Sprachen: 50+ Sprachen
   - Dimensionen: 384
   - Performance: Mittel
   - Empfohlen für: Mehrsprachige Anwendungen

## Error Handling

### Häufige Fehler

#### 400 Bad Request
```json
{
  "error": "invalid_chunk_size",
  "message": "Chunk size must be between 100 and 2000 characters",
  "details": {
    "provided_value": 50,
    "valid_range": [100, 2000]
  }
}
```

#### 422 Unprocessable Entity
```json
{
  "error": "document_processing_failed",
  "message": "Unable to extract text from document",
  "details": {
    "file_type": "pdf",
    "error_code": "corrupted_file"
  }
}
```

## Performance Optimierung

### Best Practices

1. **Chunk-Größe**: Wählen Sie 400-800 Zeichen für optimale RAG-Performance
2. **Batch Processing**: Verarbeiten Sie mehrere Dokumente gleichzeitig
3. **Caching**: Nutzen Sie Redis für häufig abgerufene Embeddings
4. **Monitoring**: Überwachen Sie Response-Zeiten und Accuracy-Metriken

### Monitoring Metriken

- **Durchsatz**: Dokumente pro Minute
- **Latenz**: Durchschnittliche Verarbeitungszeit
- **Accuracy**: Semantische Suchrelevanz (0-1)
- **Cache Hit Rate**: Embedding Cache Effizienz

## Support

Bei Fragen oder Problemen:

- **Email**: support@rag-system.com
- **Dokumentation**: https://docs.rag-system.com
- **GitHub**: https://github.com/company/rag-system
- **Community Forum**: https://forum.rag-system.com

---

*Letzte Aktualisierung: 15. März 2024*
*Version: 2.1.0*