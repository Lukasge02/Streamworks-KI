# StreamWorks-KI API Dokumentation v3.0

## 🌐 API Übersicht

Die StreamWorks-KI API ist eine RESTful API basierend auf FastAPI, die intelligente KI-Services für StreamWorks Workload-Automatisierung bereitstellt. Die API umfasst Chat-Funktionalitäten mit Conversation Memory, intelligente Suche, Training Data Management und XML-Generierung.

### 🔗 Base URL
```
http://localhost:8000/api/v1/
```

### 📊 API Status
- **Version**: 3.0
- **Protocol**: HTTP/HTTPS
- **Format**: JSON
- **Authentication**: Keine (Development)
- **Rate Limiting**: Keine (Development)

## 🗂️ API Endpoints Übersicht

| Service | Endpoint | Beschreibung |
|---------|----------|--------------|
| **Chat** | `/api/v1/chat/` | Intelligente Q&A mit Conversation Memory |
| **Search** | `/api/v1/search/` | Intelligente Suche und Query Expansion |
| **Conversations** | `/api/v1/conversations/` | Conversation Memory Management |
| **Training** | `/api/v1/training/` | Training Data Upload und Management |
| **XML** | `/api/v1/xml/` | XML Stream Generation |
| **Validation** | `/api/v1/validate/` | XML Schema Validation |

---

## 💬 Chat API

### POST `/api/v1/chat/`
**Intelligenter Chat mit Conversation Memory**

Sendet eine Nachricht an die KI und erhält eine intelligente Antwort basierend auf RAG, Mistral 7B und Conversation Memory.

**Request Body:**
```json
{
  "message": "Wie erstelle ich einen Batch-Job in StreamWorks?",
  "conversation_id": "optional-uuid-session-id"
}
```

**Response:**
```json
{
  "response": "Für einen Batch-Job in StreamWorks müssen Sie zunächst eine XML-Konfiguration erstellen...",
  "mode": "mistral_rag",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "sources_used": 3,
  "model_used": "mistral:7b-instruct",
  "processing_time": 2.34
}
```

**Features:**
- Automatische Session-Erstellung wenn keine `conversation_id` angegeben
- Konversations-Kontext wird automatisch geladen
- Intelligente Query-Erweiterung durch Synonym-Service
- Mistral 7B für deutsche StreamWorks-optimierte Antworten

---

## 🔍 Intelligent Search API

### POST `/api/v1/search/expand`
**Query Expansion mit Synonymen**

Erweitert eine Suchanfrage um Synonyme und kontextuelle Begriffe für bessere Suchergebnisse.

**Request Body:**
```json
{
  "query": "batch fehler"
}
```

**Response:**
```json
{
  "original_query": "batch fehler",
  "expanded_query": "batch fehler stapel verarbeitung error problem issue bug störung",
  "added_terms": ["stapel", "verarbeitung", "error", "problem", "issue", "bug", "störung"]
}
```

### POST `/api/v1/search/suggestions`
**Intelligente Suchvorschläge**

Generiert Suchvorschläge basierend auf partieller Eingabe.

**Request Body:**
```json
{
  "partial_query": "ba"
}
```

**Response:**
```json
{
  "suggestions": ["batch", "backup", "background", "base"],
  "count": 4
}
```

### POST `/api/v1/search/intent`
**Intent Analysis**

Analysiert die Absicht hinter einer Suchquery.

**Request Body:**
```json
{
  "query": "StreamWorks Batch-Job Fehler beheben"
}
```

**Response:**
```json
{
  "primary_intent": "troubleshooting",
  "confidence": 0.85,
  "categories": ["Fehlerbehandlung", "Batch-Verarbeitung"],
  "suggested_refinements": [
    "Spezifizieren Sie den Fehlertyp",
    "Fügen Sie Log-Informationen hinzu"
  ],
  "detected_entities": ["streamworks", "batch", "job"]
}
```

### GET `/api/v1/search/related/{term}`
**Verwandte Begriffe**

Findet verwandte Begriffe zu einem Suchterm.

**Response:**
```json
{
  "term": "batch",
  "related_terms": ["stapel", "verarbeitung", "job", "prozess", "automation"],
  "count": 5
}
```

### GET `/api/v1/search/health`
**Service Health Check**

**Response:**
```json
{
  "status": "healthy",
  "service": "intelligent_search",
  "features": {
    "query_expansion": true,
    "search_suggestions": true,
    "intent_analysis": true,
    "related_terms": true
  },
  "test_results": {
    "query_expansion_working": true,
    "suggestions_working": true
  }
}
```

---

## 🗣️ Conversation Memory API

### GET `/api/v1/conversations/`
**Liste aller Conversations (Admin)**

Holt eine Liste aller Conversation Sessions für Admin-Zwecke.

**Query Parameters:**
- `limit` (optional): Maximale Anzahl Sessions (default: 50)

**Response:**
```json
{
  "conversations": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "message_count": 15,
      "duration_minutes": 45,
      "created_at": "2025-07-04T10:00:00Z",
      "last_activity": "2025-07-04T10:45:00Z",
      "main_topics": ["batch", "fehler", "konfiguration"],
      "first_question": "Wie erstelle ich einen Batch-Job?",
      "last_question": "Wie behebe ich den Fehler XY?"
    }
  ],
  "total_count": 1
}
```

### GET `/api/v1/conversations/{session_id}/summary`
**Conversation Summary**

Holt eine Zusammenfassung einer spezifischen Conversation.

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_count": 15,
  "duration_minutes": 45,
  "created_at": "2025-07-04T10:00:00Z",
  "last_activity": "2025-07-04T10:45:00Z",
  "main_topics": ["batch", "fehler", "konfiguration"],
  "first_question": "Wie erstelle ich einen Batch-Job?",
  "last_question": "Wie behebe ich den Fehler XY?"
}
```

### GET `/api/v1/conversations/{session_id}/context`
**Conversation Context**

Holt den Konversations-Kontext für eine Session.

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "context": "Vorherige Frage 1: Wie erstelle ich einen Batch-Job?\nVorherige Antwort 1: Für einen Batch-Job...",
  "context_length": 450,
  "message_count": 3
}
```

### DELETE `/api/v1/conversations/{session_id}`
**Conversation löschen**

Löscht eine spezifische Conversation Session.

**Response:**
```json
{
  "success": true,
  "message": "Conversation 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

### POST `/api/v1/conversations/cleanup`
**Alte Conversations bereinigen**

Bereinigt alte/inaktive Conversation Sessions.

**Response:**
```json
{
  "cleaned_sessions": 5,
  "remaining_sessions": 20
}
```

### GET `/api/v1/conversations/stats`
**Conversation Statistiken**

Holt umfassende Statistiken über alle Conversations.

**Response:**
```json
{
  "total_sessions": 25,
  "active_sessions_24h": 8,
  "total_messages": 150,
  "average_messages_per_session": 6.0,
  "storage_size_bytes": 524288,
  "storage_size_mb": 0.5,
  "storage_path": "/data/conversations",
  "session_timeout_hours": 24,
  "max_messages_per_session": 50,
  "context_window_size": 3
}
```

---

## 📚 Training Data API

### POST `/api/v1/training/upload`
**File Upload (Single/Batch)**

Lädt Training Data Dateien hoch (TXT, MD, CSV, BAT, PS1, XML, XSD).

**Request:** Multipart Form Data
- `file`: File(s) to upload
- `category`: "help_data" oder "stream_templates"

**Response:**
```json
{
  "id": "file-uuid",
  "filename": "uuid_streamworks_guide.txt",
  "display_name": "streamworks_guide.txt",
  "category": "help_data",
  "file_path": "data/training_data/originals/help_data/uuid_streamworks_guide.txt",
  "upload_date": "2025-07-04T12:00:00Z",
  "file_size": 15420,
  "status": "ready",
  "is_indexed": false,
  "chunk_count": 0
}
```

### GET `/api/v1/training/files`
**Liste Training Files**

Holt eine Liste aller Training Data Dateien.

**Query Parameters:**
- `category` (optional): Filter nach Kategorie
- `status` (optional): Filter nach Status

**Response:**
```json
[
  {
    "id": "file-uuid",
    "filename": "uuid_streamworks_guide.txt",
    "display_name": "streamworks_guide.txt",
    "category": "help_data",
    "file_path": "data/training_data/originals/help_data/uuid_streamworks_guide.txt",
    "upload_date": "2025-07-04T12:00:00Z",
    "file_size": 15420,
    "status": "ready",
    "is_indexed": true,
    "indexed_at": "2025-07-04T12:01:00Z",
    "chunk_count": 8,
    "index_status": "indexed"
  }
]
```

### DELETE `/api/v1/training/files/{file_id}`
**Training File löschen**

Löscht eine Training Data Datei und zugehörige optimierte Dateien.

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

### GET `/api/v1/training/files/{file_id}/conversion-status`
**TXT→MD Conversion Status**

Holt den Status der TXT zu MD Konvertierung.

**Response:**
```json
{
  "file_id": "file-uuid",
  "filename": "uuid_guide.txt",
  "original_format": "txt",
  "optimized_format": "md",
  "conversion_status": "completed",
  "processed_file_path": "data/training_data/optimized/help_data/uuid_guide_optimized.md",
  "conversion_error": null,
  "file_status": "ready"
}
```

### GET `/api/v1/training/files/{file_id}/optimized-content`
**Optimized Content abrufen**

Holt den Inhalt der optimierten Markdown-Datei.

**Response:**
```json
{
  "file_id": "file-uuid",
  "original_filename": "uuid_guide.txt",
  "optimized_filename": "uuid_guide_optimized.md",
  "optimized_content": "# StreamWorks Guide\n\n**Automatisch generiert aus**: guide.txt...",
  "conversion_metadata": "{\"converter_version\": \"1.0.0\"}",
  "file_size": 18500,
  "conversion_status": "completed"
}
```

### GET `/api/v1/training/conversion-stats`
**Conversion Statistiken**

Holt Statistiken über TXT zu MD Konvertierungen.

**Response:**
```json
{
  "total_txt_files": 20,
  "conversions_completed": 18,
  "conversions_failed": 1,
  "conversions_pending": 1,
  "optimized_files_created": 18,
  "success_rate": 90.0
}
```

### POST `/api/v1/training/files/{file_id}/index`
**File zu ChromaDB indexieren**

Indexiert eine Training Data Datei zur ChromaDB für RAG.

**Response:**
```json
{
  "file_id": "file-uuid",
  "filename": "streamworks_guide.txt",
  "chunk_count": 8,
  "indexed_at": "2025-07-04T12:01:00Z",
  "status": "success"
}
```

### GET `/api/v1/training/chromadb-stats`
**ChromaDB Statistiken**

Holt Statistiken über die Vector Database.

**Response:**
```json
{
  "indexed_files": 15,
  "total_chunks": 120,
  "collection_documents": 120,
  "by_category": {
    "help_data": 12,
    "stream_templates": 3
  },
  "vector_db_path": "data/vector_db/",
  "embedding_model": "all-MiniLM-L6-v2"
}
```

---

## 🌊 XML Generation API

### POST `/api/v1/xml/generate`
**XML Stream Generation**

Generiert StreamWorks XML-Konfiguration basierend auf Benutzer-Input.

**Request Body:**
```json
{
  "stream_name": "Daily_Data_Processing",
  "job_name": "ProcessCustomerData",
  "start_time": "02:00",
  "data_source": "/data/input/customers.csv",
  "output_path": "/data/output/processed/",
  "schedule": "daily",
  "description": "Verarbeitung der täglichen Kundendaten"
}
```

**Response:**
```json
{
  "xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<stream name=\"Daily_Data_Processing\">...",
  "config": {
    "stream_name": "Daily_Data_Processing",
    "job_name": "ProcessCustomerData",
    "start_time": "02:00",
    "data_source": "/data/input/customers.csv",
    "output_path": "/data/output/processed/",
    "schedule": "daily"
  },
  "validation_status": "valid",
  "generated_at": "2025-07-04T12:00:00Z"
}
```

### GET `/api/v1/xml/health`
**XML Service Health**

**Response:**
```json
{
  "status": "healthy",
  "service": "xml_generation",
  "features": {
    "template_generation": true,
    "validation": true,
    "ai_enhancement": false
  }
}
```

---

## ✅ XML Validation API

### POST `/api/v1/validate/xml`
**XML Schema Validation**

Validiert XML gegen StreamWorks XSD Schema.

**Request Body:**
```json
{
  "xml_content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<stream>..."
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "schema_version": "1.0",
  "validated_at": "2025-07-04T12:00:00Z"
}
```

---

## 🔧 Health Check Endpoints

### GET `/`
**System Health Check**

Überprüft den allgemeinen System-Status.

**Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "environment": "development",
  "services": {
    "rag_service": "healthy",
    "mistral_llm": "healthy",
    "intelligent_search": "healthy",
    "conversation_memory": "healthy",
    "training_service": "healthy"
  },
  "uptime": "2h 30m",
  "timestamp": "2025-07-04T12:00:00Z"
}
```

---

## 📊 Error Handling

### Standard Error Response

Alle API Endpoints verwenden ein konsistentes Error-Format:

```json
{
  "detail": "Beschreibung des Fehlers",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-07-04T12:00:00Z",
  "path": "/api/v1/chat/",
  "request_id": "req_123_456"
}
```

### HTTP Status Codes

| Code | Bedeutung | Verwendung |
|------|-----------|------------|
| `200` | OK | Erfolgreiche Anfrage |
| `201` | Created | Ressource erfolgreich erstellt |
| `400` | Bad Request | Ungültige Anfrage-Parameter |
| `404` | Not Found | Ressource nicht gefunden |
| `422` | Unprocessable Entity | Validierungsfehler |
| `500` | Internal Server Error | Server-Fehler |

### Häufige Fehlercodes

- `CONVERSATION_NOT_FOUND`: Session-ID existiert nicht
- `FILE_NOT_FOUND`: Training Data Datei nicht gefunden
- `UPLOAD_SIZE_EXCEEDED`: Datei zu groß
- `INVALID_FILE_TYPE`: Nicht unterstützter Dateityp
- `MISTRAL_SERVICE_UNAVAILABLE`: Mistral LLM nicht verfügbar
- `CHROMADB_ERROR`: Vector Database Fehler

---

## 🚀 Rate Limiting & Performance

### Request Limits (Production)

| Endpoint | Limit | Zeitfenster |
|----------|-------|-------------|
| Chat API | 60 requests | 1 Minute |
| Search API | 100 requests | 1 Minute |
| Upload API | 10 requests | 1 Minute |
| Training API | 30 requests | 1 Minute |

### Performance Metriken

**Typische Response Times:**
- Chat API: 1-3 Sekunden
- Search API: 50-200ms
- Training API: 100-500ms
- File Upload: Variable (abhängig von Dateigröße)

### Request Headers

**Empfohlene Headers:**
```http
Content-Type: application/json
Accept: application/json
User-Agent: StreamWorks-KI-Client/1.0
```

**Response Headers:**
```http
X-Process-Time: 1.234
X-Request-ID: req_123_456
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1625097600
```

---

## 🔐 Authentication & Security

### Development Mode
- **Authentication**: Keine
- **CORS**: Erlaubt alle Origins
- **Rate Limiting**: Deaktiviert

### Production Mode (Geplant)
- **Authentication**: JWT Tokens
- **CORS**: Spezifische Origins
- **Rate Limiting**: Aktiviert
- **Request Validation**: Erweitert

---

## 📝 Changelog

### Version 3.0 (Juli 2025)
- ✅ Intelligent Search API hinzugefügt
- ✅ Conversation Memory API implementiert
- ✅ Enhanced Training Data API
- ✅ TXT→MD Conversion Endpoints
- ✅ Advanced Health Checks
- ✅ Performance Monitoring Headers

### Version 2.0 (Juni 2025)
- ✅ RAG + Mistral Integration
- ✅ Training Data Management
- ✅ File Upload System
- ✅ XML Generation API

### Version 1.0 (Mai 2025)
- ✅ Basic Chat API
- ✅ XML Validation
- ✅ Health Checks

---

**Version:** 3.0  
**Letztes Update:** Juli 2025  
**Autor:** Ravel-Lukas Geck  
**Projekt:** StreamWorks-KI Bachelorarbeit