# StreamWorks-KI API Documentation

## 🌟 Enterprise-Grade RAG + LLM API

### Base URL
```
Production: https://api.streamworks-ki.com
Development: http://localhost:8000
```

### Authentication
```bash
# API Key Header
X-API-Key: your-api-key-here

# JWT Token (wenn implementiert)
Authorization: Bearer <jwt-token>
```

---

## 🚀 Quick Start

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-08T10:30:00Z",
  "version": "2.1.0",
  "architecture": "Mistral 7B + RAG + LoRA",
  "services": {
    "rag": {"status": "healthy", "documents": 1250},
    "mistral_llm": {"status": "healthy", "model": "mistral:7b-instruct"},
    "mistral_rag": {"status": "healthy"},
    "xml_generation": {"status": "healthy", "lora_enabled": true},
    "database": "operational"
  }
}
```

---

## 💬 Chat & Q&A Endpoints

### 1. Standard Chat (RAG + LLM)
**Endpoint:** `POST /api/v1/chat/`

**Request:**
```json
{
  "message": "Wie funktioniert das StreamWorks Client-Update?",
  "conversation_id": "optional-uuid",
  "use_rag": true,
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response:**
```json
{
  "response": "Das StreamWorks Client-Update erfolgt automatisch über...",
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "sources": [
    {
      "filename": "client_update_guide.pdf",
      "page": 3,
      "relevance_score": 0.95,
      "content": "Update-Prozess läuft über..."
    }
  ],
  "processing_time": 2.3,
  "model_used": "mistral:7b-instruct",
  "rag_enabled": true
}
```

### 2. Dual-Mode Chat (RAG + Direct LLM)
**Endpoint:** `POST /api/v1/chat/dual-mode`

**Request:**
```json
{
  "message": "Erkläre mir die Backup-Strategie",
  "conversation_id": "optional-uuid",
  "compare_responses": true
}
```

**Response:**
```json
{
  "rag_response": {
    "response": "Laut Dokumentation verwendet StreamWorks...",
    "sources": [...],
    "processing_time": 1.8
  },
  "direct_llm_response": {
    "response": "Eine typische Backup-Strategie umfasst...",
    "processing_time": 0.9
  },
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "comparison_mode": true
}
```

### 3. Citation-Enhanced Chat
**Endpoint:** `POST /api/v1/chat/with-citations`

**Request:**
```json
{
  "message": "Was sind die Systemanforderungen?",
  "enable_citations": true,
  "citation_style": "numeric"
}
```

**Response:**
```json
{
  "response": "Die Systemanforderungen für StreamWorks sind: Windows 10+ [1], 8GB RAM [2], und .NET Framework 4.8+ [3].",
  "citations": [
    {
      "id": 1,
      "source": "system_requirements.pdf",
      "page": 1,
      "text": "Mindestanforderung: Windows 10 oder höher"
    },
    {
      "id": 2,
      "source": "hardware_specs.pdf", 
      "page": 2,
      "text": "Empfohlener Arbeitsspeicher: 8GB RAM"
    }
  ]
}
```

---

## 🔧 XML Generation Endpoints

### 1. Generate XML from Text
**Endpoint:** `POST /api/v1/xml/generate`

**Request:**
```json
{
  "text": "Der Kunde möchte eine neue Bestellung für 5 Laptops mit Windows 11",
  "xml_type": "order",
  "use_lora": true,
  "temperature": 0.3
}
```

**Response:**
```json
{
  "xml_output": "<?xml version=\"1.0\"?>\n<order>\n  <item>\n    <product>Laptop</product>\n    <quantity>5</quantity>\n    <os>Windows 11</os>\n  </item>\n</order>",
  "confidence": 0.92,
  "lora_model_used": true,
  "processing_time": 1.2,
  "validation": {
    "is_valid": true,
    "errors": []
  }
}
```

### 2. Batch XML Generation
**Endpoint:** `POST /api/v1/xml/generate-batch`

**Request:**
```json
{
  "texts": [
    "Bestellung für 3 Monitore",
    "Reparaturauftrag für Drucker",
    "Anfrage für Software-Lizenz"
  ],
  "xml_type": "mixed",
  "parallel_processing": true
}
```

**Response:**
```json
{
  "results": [
    {
      "input_text": "Bestellung für 3 Monitore",
      "xml_output": "<order>...</order>",
      "confidence": 0.89
    }
  ],
  "total_processed": 3,
  "processing_time": 2.1,
  "parallel_execution": true
}
```

---

## 📚 Training & Document Management

### 1. Upload Training Documents
**Endpoint:** `POST /api/v1/training/upload`

**Request (multipart/form-data):**
```bash
curl -X POST "http://localhost:8000/api/v1/training/upload" \
  -F "file=@document.pdf" \
  -F "category=manual" \
  -F "priority=high"
```

**Response:**
```json
{
  "file_id": "doc_123456",
  "filename": "document.pdf",
  "size": 2048576,
  "pages": 45,
  "category": "manual",
  "processing_status": "queued",
  "estimated_processing_time": "2-3 minutes",
  "upload_time": "2025-07-08T10:30:00Z"
}
```

### 2. Check Processing Status
**Endpoint:** `GET /api/v1/training/status/{file_id}`

**Response:**
```json
{
  "file_id": "doc_123456",
  "status": "processing", // queued, processing, completed, failed
  "progress": 65,
  "current_step": "text_extraction",
  "steps_completed": ["upload", "validation", "text_extraction"],
  "steps_remaining": ["chunking", "embedding", "indexing"],
  "estimated_completion": "2025-07-08T10:33:00Z",
  "error_details": null
}
```

### 3. List Training Files
**Endpoint:** `GET /api/v1/training/files`

**Query Parameters:**
- `page`: Seite (default: 1)
- `limit`: Anzahl pro Seite (default: 20)
- `category`: Filter nach Kategorie
- `status`: Filter nach Status

**Response:**
```json
{
  "files": [
    {
      "file_id": "doc_123456",
      "filename": "user_manual.pdf",
      "category": "manual",
      "status": "completed",
      "upload_date": "2025-07-08T10:00:00Z",
      "size": 2048576,
      "pages": 45,
      "chunks_generated": 123
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 156,
    "pages": 8
  }
}
```

---

## 🔍 Search & Retrieval

### 1. Semantic Search
**Endpoint:** `POST /api/v1/search/semantic`

**Request:**
```json
{
  "query": "Wie installiere ich StreamWorks Client?",
  "top_k": 5,
  "threshold": 0.7,
  "filter": {
    "category": ["manual", "guide"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2025-07-08"
    }
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "doc_789",
      "filename": "installation_guide.pdf",
      "page": 12,
      "chunk_text": "Die Installation des StreamWorks Clients erfolgt...",
      "relevance_score": 0.94,
      "metadata": {
        "category": "manual",
        "version": "2.1",
        "last_updated": "2025-01-15"
      }
    }
  ],
  "query_time": 0.15,
  "total_results": 23,
  "max_score": 0.94
}
```

### 2. Hybrid Search (Semantic + Keyword)
**Endpoint:** `POST /api/v1/search/hybrid`

**Request:**
```json
{
  "query": "StreamWorks Fehlerbehandlung Exception",
  "semantic_weight": 0.7,
  "keyword_weight": 0.3,
  "top_k": 10
}
```

---

## 📊 Monitoring & Analytics

### 1. System Metrics
**Endpoint:** `GET /api/v1/monitoring/metrics`

**Response:**
```json
{
  "overview": {
    "total_requests": 15420,
    "total_errors": 23,
    "active_requests": 3,
    "average_response_time": 1.23,
    "uptime_hours": 168.5
  },
  "endpoints": {
    "/api/v1/chat/": {
      "request_count": 8450,
      "avg_duration": 2.1,
      "error_rate": 0.012
    }
  },
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 67.8,
    "disk_usage_percent": 23.1
  }
}
```

### 2. Performance History
**Endpoint:** `GET /api/v1/monitoring/performance/history?minutes=60`

**Response:**
```json
{
  "history": [
    {
      "timestamp": "2025-07-08T10:30:00Z",
      "cpu_percent": 45.2,
      "memory_percent": 67.8,
      "response_time": 1.23
    }
  ],
  "averages": {
    "avg_cpu": 42.1,
    "avg_memory": 65.4,
    "avg_response_time": 1.31
  }
}
```

---

## 🤖 A/B Testing & Evaluation

### 1. Create A/B Test
**Endpoint:** `POST /api/v1/ab-testing/create`

**Request:**
```json
{
  "test_name": "rag_vs_direct_comparison",
  "description": "Compare RAG vs Direct LLM responses",
  "variants": [
    {
      "name": "rag_enabled",
      "config": {"use_rag": true, "temperature": 0.7}
    },
    {
      "name": "direct_llm",
      "config": {"use_rag": false, "temperature": 0.7}
    }
  ],
  "traffic_split": [50, 50],
  "success_metrics": ["response_quality", "user_satisfaction"]
}
```

### 2. Evaluate Response Quality
**Endpoint:** `POST /api/v1/evaluation/evaluate`

**Request:**
```json
{
  "response": "StreamWorks Client wird automatisch über...",
  "reference_answer": "Der Client aktualisiert sich automatisch...",
  "metrics": ["relevance", "accuracy", "completeness"],
  "context": {
    "query": "Wie funktioniert das Client-Update?",
    "sources_used": ["manual_v2.1.pdf"]
  }
}
```

---

## 🔒 Security & Validation

### 1. Input Validation
Alle Endpoints validieren automatisch:
- **XSS-Schutz**: HTML/Script-Tags werden gefiltert
- **SQL-Injection-Schutz**: Query-Parameter werden sanitisiert
- **File-Upload-Sicherheit**: MIME-Type und Malware-Scanning
- **Rate Limiting**: 100 Requests/Minute pro Client

### 2. Error Responses
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "message",
      "issue": "Message cannot be empty"
    },
    "timestamp": "2025-07-08T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### 3. Rate Limiting
**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1625750400
```

---

## 📝 Status Codes

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| 200 | OK | Request erfolgreich |
| 201 | Created | Resource erstellt |
| 400 | Bad Request | Ungültige Parameter |
| 401 | Unauthorized | Authentifizierung erforderlich |
| 403 | Forbidden | Zugriff verweigert |
| 404 | Not Found | Resource nicht gefunden |
| 429 | Too Many Requests | Rate Limit überschritten |
| 500 | Internal Server Error | Server-Fehler |
| 503 | Service Unavailable | Service temporär nicht verfügbar |

---

## 🔧 SDK & Client Libraries

### Python SDK
```python
from streamworks_ki import StreamWorksClient

client = StreamWorksClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Chat
response = client.chat("Wie installiere ich StreamWorks?")
print(response.message)

# Upload Document
result = client.upload_document("manual.pdf", category="guide")
print(f"Upload ID: {result.file_id}")

# Search
results = client.semantic_search("Installation Anleitung", top_k=5)
for result in results:
    print(f"Score: {result.score}, Text: {result.text}")
```

### JavaScript SDK
```javascript
import { StreamWorksClient } from '@streamworks/ki-sdk';

const client = new StreamWorksClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Chat
const response = await client.chat({
  message: 'Wie installiere ich StreamWorks?',
  useRag: true
});

console.log(response.message);
```

---

## 🚀 Performance Guidelines

### Request Optimization
- **Batch Requests**: Nutzen Sie Batch-Endpoints für Multiple-Operationen
- **Async Processing**: Verwenden Sie Webhooks für lange Operationen
- **Caching**: Implementieren Sie Client-seitiges Caching für häufige Queries
- **Compression**: Aktivieren Sie gzip für große Responses

### Response Times (Zielwerte)
- **Chat (with RAG)**: < 3 Sekunden
- **Search**: < 500ms
- **XML Generation**: < 2 Sekunden
- **Document Upload**: < 5 Sekunden (für < 10MB)
- **Health Check**: < 100ms

---

**API Version**: 2.1.0  
**Last Updated**: 2025-07-08  
**Support**: api-support@streamworks-ki.com