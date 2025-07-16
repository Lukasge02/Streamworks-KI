# StreamWorks-KI API Documentation

## 🌟 Enterprise-Grade RAG + LLM API

### Base URL
```
Production: https://api.streamworks-ki.com
Development: http://localhost:8000
```

### Authentication
```bash
# API Key Header (if implemented)
X-API-Key: your-api-key-here

# JWT Token (if implemented)
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
  "timestamp": "2025-07-16T12:00:00Z",
  "version": "2.1.0",
  "architecture": "Mistral 7B + RAG",
  "services": {
    "rag": {"status": "available"},
    "mistral_llm": {"status": "ready"},
    "mistral_rag": {"status": "available"},
    "database": "operational"
  }
}
```

---

## 📋 API Endpoints

### 1. **Q&A Service** - `/api/v1/qa/`

#### Ask Question
**POST** `/api/v1/qa/ask`

Intelligente Frage-Antwort basierend auf RAG-System.

**Request:**
```json
{
  "question": "Wie konfiguriere ich den StreamWorks Agent?",
  "context_limit": 5,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "answer": "Um den StreamWorks Agent zu konfigurieren...",
  "sources": [
    {
      "filename": "SW-Agent-Configuration.pdf",
      "chunk_id": "chunk_123",
      "relevance_score": 0.95
    }
  ],
  "response_time": 2.3,
  "model_used": "mistral:7b"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Wie konfiguriere ich den StreamWorks Agent?",
    "context_limit": 5
  }'
```

---

### 2. **Document Management** - `/api/v1/files/`

#### Upload Document
**POST** `/api/v1/files/upload`

Lädt ein Dokument hoch und indexiert es für das RAG-System.

**Request (multipart/form-data):**
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -F "file=@document.pdf" \
  -F "category_slug=qa_docs" \
  -F "folder_slug=help_documents"
```

**Response:**
```json
{
  "id": "12345-67890",
  "filename": "document.pdf",
  "category_slug": "qa_docs",
  "category_name": "Q&A Documents",
  "file_size": 1024000,
  "upload_date": "2025-07-16T12:00:00Z",
  "status": "ready_for_indexing"
}
```

#### List Files
**GET** `/api/v1/files/`

**Query Parameters:**
- `category_slug` (optional): Filter by category
- `folder_slug` (optional): Filter by folder

**Response:**
```json
{
  "files": [
    {
      "id": "12345-67890",
      "filename": "document.pdf",
      "category_slug": "qa_docs",
      "category_name": "Q&A Documents",
      "file_size": 1024000,
      "upload_date": "2025-07-16T12:00:00Z",
      "status": "indexed",
      "chunk_count": 45,
      "indexed_at": "2025-07-16T12:05:00Z"
    }
  ],
  "total_files": 1,
  "total_size": 1024000
}
```

#### Delete File
**DELETE** `/api/v1/files/{file_id}`

**Response:**
```json
{
  "message": "File deleted successfully"
}
```

---

### 3. **Categories Management** - `/api/v1/categories/`

#### List Categories
**GET** `/api/v1/categories/`

**Response:**
```json
{
  "categories": [
    {
      "id": "1",
      "slug": "qa_docs",
      "name": "Q&A Documents",
      "description": "Support and help documents",
      "folder_count": 3,
      "file_count": 25,
      "created_at": "2025-07-16T12:00:00Z"
    }
  ]
}
```

#### Create Category
**POST** `/api/v1/categories/`

**Request:**
```json
{
  "name": "New Category",
  "description": "Category description",
  "slug": "new_category"
}
```

#### Get Category Folders
**GET** `/api/v1/categories/{category_slug}/folders`

**Response:**
```json
{
  "folders": [
    {
      "id": "1",
      "slug": "help_documents",
      "name": "Help Documents",
      "description": "User help documentation",
      "file_count": 10
    }
  ]
}
```

---

### 4. **Chunks Analysis** - `/api/v1/chunks/`

#### Get Chunk Analysis
**GET** `/api/v1/chunks/analysis`

**Response:**
```json
{
  "total_chunks": 1234,
  "total_files": 56,
  "average_chunk_size": 512,
  "embedding_model": "intfloat/multilingual-e5-large",
  "vector_db_size": "45.6 MB",
  "last_indexed": "2025-07-16T12:00:00Z"
}
```

#### Get File Analysis
**GET** `/api/v1/chunks/files`

**Response:**
```json
{
  "files": [
    {
      "filename": "document.pdf",
      "chunk_count": 45,
      "file_size": 1024000,
      "indexed_at": "2025-07-16T12:05:00Z",
      "embedding_model": "intfloat/multilingual-e5-large",
      "categories": ["qa_docs"]
    }
  ]
}
```

---

### 5. **System Status** - `/api/v1/status`

#### System Status
**GET** `/api/v1/status`

**Response:**
```json
{
  "backend_version": "2.1.0",
  "architecture": "Mistral 7B + RAG",
  "features": {
    "mistral_rag_qa": true,
    "german_optimization": true,
    "document_upload": true,
    "vector_search": true,
    "performance_monitoring": true
  },
  "models": {
    "mistral_model": "mistral:7b",
    "embedding_model": "intfloat/multilingual-e5-large",
    "vector_db_path": "./data/vector_db"
  },
  "mistral_parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2048
  }
}
```

---

### 6. **Performance Metrics** - `/api/v1/metrics`

#### Get Metrics
**GET** `/api/v1/metrics`

**Response:**
```json
{
  "timestamp": "2025-07-16T12:00:00Z",
  "status": "monitoring_active",
  "endpoints_monitored": [
    "/api/v1/qa/ask",
    "/api/v1/files/upload",
    "/health"
  ],
  "monitoring_features": [
    "Request timing",
    "Error tracking",
    "Slow request detection",
    "System resource monitoring"
  ]
}
```

---

## 🔧 Error Handling

### Error Response Format
```json
{
  "error": "Invalid request format",
  "detail": "The 'question' field is required",
  "status_code": 400,
  "timestamp": "2025-07-16T12:00:00Z"
}
```

### Common Error Codes
- **400 Bad Request**: Invalid request format or missing parameters
- **401 Unauthorized**: Invalid or missing authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **413 Payload Too Large**: File too large for upload
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Service temporarily unavailable

---

## 📊 Rate Limits

### Default Limits
- **Q&A Requests**: 60 per minute
- **File Uploads**: 10 per minute
- **General API**: 100 per minute

### Rate Limit Headers
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642781400
```

---

## 🔒 Security

### Input Validation
- All inputs are validated using Pydantic models
- File uploads are scanned for malicious content
- SQL injection protection through parameterized queries

### Content Security
- Maximum file size: 50MB
- Allowed file types: PDF, DOCX, TXT, MD, CSV, JSON
- Content filtering to prevent injection attacks

---

## 📈 Performance

### Response Times
- **Health Check**: < 100ms
- **Q&A Query**: < 3s (depends on context complexity)
- **File Upload**: < 1s (indexing happens in background)
- **File List**: < 500ms
- **Category Operations**: < 300ms

### Pagination
Large result sets are paginated:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 123,
    "total_pages": 3
  }
}
```

---

## 🧪 Testing

### Test Endpoints
```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Ask question
curl -X POST "http://localhost:8000/api/v1/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'

# Upload file
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -F "file=@test.pdf" \
  -F "category_slug=qa_docs"
```

### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

---

## 🔄 Updates

### Version 2.1.0 (Current)
- Updated architecture documentation
- Removed deprecated XML generation endpoints
- Added proper error handling documentation
- Enhanced file management endpoints
- Improved response time specifications

### Deprecated Endpoints
- `/api/v1/xml/generate` - Removed (XML generation not implemented)
- `/api/v1/lora/finetune` - Removed (LoRA fine-tuning not implemented)

---

## 📞 Support

For technical support:
- **API Issues**: Check `/docs` for interactive documentation
- **Performance Issues**: Monitor `/api/v1/metrics`
- **File Upload Issues**: Check file size and format requirements
- **Authentication Issues**: Verify API key format and permissions