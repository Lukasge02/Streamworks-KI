# 🔌 API Reference

> **Vollständige REST API Dokumentation für Streamworks-KI RAG System**  
> Interactive docs: `http://localhost:8000/docs`

---

## 🎯 **API Overview**

Das Streamworks-KI System bietet eine **moderne FastAPI-basierte REST API** mit:

- **🔄 Async Operations** - Non-blocking I/O für optimale Performance
- **📖 Auto-Documentation** - Interactive Swagger UI unter `/docs`
- **🛡️ Type Safety** - Pydantic Models für Request/Response Validation
- **⚡ WebSocket Support** - Real-time Updates für Chat und Upload
- **🗂️ File Operations** - Streaming Upload/Download für große Dateien

### **Base URL**
```
Development: http://localhost:8000
Production:  https://your-domain.com/api
```

### **Response Format**
```json
// Success Response
{
  "id": "uuid",
  "data": { ... },
  "status": "success",
  "timestamp": "2025-01-01T00:00:00Z"
}

// Error Response  
{
  "error": "error_code",
  "detail": "Human readable error message",
  "status": "error", 
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## 📁 **Folder Management API**

Hierarchische Ordnerverwaltung für Enterprise Dokumentenorganisation.

### **List All Folders**
```http
GET /folders/
```

**Response:**
```json
{
  "folders": [
    {
      "id": "folder-uuid",
      "name": "Documents",
      "description": "Main documents folder",
      "parent_id": null,
      "children": [
        {
          "id": "sub-folder-uuid", 
          "name": "Subfolder",
          "parent_id": "folder-uuid",
          "children": []
        }
      ],
      "document_count": 15,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### **Create Folder**
```http
POST /folders/
Content-Type: application/json

{
  "name": "New Folder",
  "description": "Folder description (optional)",
  "parent_id": "parent-folder-uuid" // optional for root
}
```

**Response:**
```json
{
  "id": "new-folder-uuid",
  "name": "New Folder", 
  "description": "Folder description",
  "parent_id": "parent-folder-uuid",
  "created_at": "2025-01-01T00:00:00Z"
}
```

### **Get Folder Details**
```http
GET /folders/{folder_id}
```

### **Update Folder**
```http
PUT /folders/{folder_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

### **Delete Folder**
```http
DELETE /folders/{folder_id}?force=false
```
**Query Parameters:**
- `force` (bool): Delete folder even if it contains documents

### **List Documents in Folder**
```http
GET /folders/{folder_id}/documents?page=1&limit=20
```

---

## 📄 **Document Management API**

Enterprise Dokumentenverarbeitung mit Multi-Format Support.

### **List All Documents**
```http
GET /documents/?page=1&limit=20&folder_id=uuid&search=query
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)  
- `folder_id` (uuid): Filter by folder
- `search` (str): Search in filename/content

**Response:**
```json
{
  "documents": [
    {
      "id": "doc-uuid",
      "filename": "document.pdf",
      "original_name": "Original Document.pdf",
      "folder_id": "folder-uuid", 
      "folder_name": "Documents",
      "file_size": 2048576,
      "mime_type": "application/pdf",
      "status": "processed",
      "created_at": "2025-01-01T00:00:00Z",
      "processed_at": "2025-01-01T00:01:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "pages": 3,
  "has_next": true
}
```

### **Upload Documents**
```http
POST /documents/upload
Content-Type: multipart/form-data

folder_id: folder-uuid (optional)
files: file1.pdf, file2.docx, file3.txt
```

**Response:**
```json
{
  "upload_job_id": "job-uuid",
  "uploaded_files": [
    {
      "id": "doc-uuid-1",
      "filename": "file1.pdf",
      "status": "processing"
    }
  ],
  "failed_files": [],
  "message": "Upload initiated. Use WebSocket for progress."
}
```

### **Get Document Details**
```http
GET /documents/{document_id}
```

**Response:**
```json
{
  "id": "doc-uuid",
  "filename": "document.pdf",
  "original_name": "Original Document.pdf",
  "folder_id": "folder-uuid",
  "folder_path": "/Documents/Subfolder",
  "file_size": 2048576,
  "mime_type": "application/pdf", 
  "status": "processed",
  "processing_metadata": {
    "pages": 10,
    "chunks": 25,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "processing_time": 12.5
  },
  "created_at": "2025-01-01T00:00:00Z",
  "processed_at": "2025-01-01T00:01:00Z"
}
```

### **Download Document**
```http
GET /documents/{document_id}/download
```

**Response:** Binary file stream with appropriate headers

### **Delete Document**
```http
DELETE /documents/{document_id}
```

### **Bulk Operations**
```http
POST /documents/bulk-delete
Content-Type: application/json

{
  "document_ids": ["doc-uuid-1", "doc-uuid-2", "doc-uuid-3"]
}
```

```http
POST /documents/bulk-move
Content-Type: application/json

{
  "document_ids": ["doc-uuid-1", "doc-uuid-2"],
  "target_folder_id": "target-folder-uuid"
}
```

---

## 💬 **Chat & RAG API**

Intelligente Dokumenten-Fragenbeantwortung mit RAG Pipeline.

### **Start Chat Session**
```http
POST /chat/sessions
Content-Type: application/json

{
  "name": "My Chat Session",
  "folder_id": "folder-uuid" // optional: limit to specific folder
}
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "name": "My Chat Session",
  "folder_id": "folder-uuid",
  "created_at": "2025-01-01T00:00:00Z"
}
```

### **Send Message**
```http
POST /chat/sessions/{session_id}/messages
Content-Type: application/json

{
  "message": "What are the key features of the RAG system?",
  "use_local_ai": true,
  "include_sources": true,
  "max_results": 5
}
```

**Response (Streaming):**
```json
// Message chunks streamed via Server-Sent Events
{
  "type": "message_start",
  "message_id": "msg-uuid",
  "timestamp": "2025-01-01T00:00:00Z"
}

{
  "type": "content_chunk", 
  "content": "The RAG system features include...",
  "chunk_id": 1
}

{
  "type": "sources",
  "sources": [
    {
      "document_id": "doc-uuid",
      "document_name": "RAG_Documentation.pdf", 
      "page": 5,
      "similarity_score": 0.92,
      "excerpt": "Key features include semantic search..."
    }
  ]
}

{
  "type": "message_complete",
  "message_id": "msg-uuid",
  "total_chunks": 5,
  "sources_count": 3
}
```

### **Get Chat History**
```http
GET /chat/sessions/{session_id}/messages?page=1&limit=50
```

### **Search Documents**
```http
POST /chat/search
Content-Type: application/json

{
  "query": "semantic search algorithms",
  "folder_id": "folder-uuid", // optional
  "max_results": 10,
  "similarity_threshold": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "doc-uuid",
      "document_name": "ML_Algorithms.pdf",
      "chunk_id": "chunk-uuid",  
      "content": "Semantic search algorithms use...",
      "page": 15,
      "similarity_score": 0.94,
      "metadata": {
        "section": "Chapter 3: Search Algorithms",
        "chunk_index": 45
      }
    }
  ],
  "query_embedding_time": 0.05,
  "search_time": 0.12,
  "total_documents_searched": 150
}
```

---

## 🔄 **WebSocket APIs**

Real-time Updates für Upload Progress und Chat Streaming.

### **Upload Progress WebSocket**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/upload-progress/{job_id}');

ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  /*
  {
    "job_id": "job-uuid",
    "file_name": "document.pdf", 
    "stage": "processing", // uploading, processing, embedding, complete
    "progress": 75,
    "message": "Extracting text from PDF...",
    "error": null
  }
  */
};
```

### **Chat Streaming WebSocket**  
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/{session_id}');

ws.send(JSON.stringify({
  "message": "Your question here",
  "use_local_ai": true
}));

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  /*
  {
    "type": "content_chunk",
    "content": "Response text...",
    "message_id": "msg-uuid",
    "chunk_id": 1
  }
  */
};
```

### **Document Sync WebSocket**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/documents');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  /*
  {
    "type": "document_uploaded", // document_uploaded, document_deleted, folder_created
    "document_id": "doc-uuid",
    "folder_id": "folder-uuid",
    "timestamp": "2025-01-01T00:00:00Z"
  }
  */
};
```

---

## 🏥 **System Health & Monitoring**

### **Basic Health Check**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "StreamWorks Document Management",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### **Database Health**
```http
GET /health/database
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "connection_pool": {
    "active": 5,
    "idle": 3,
    "total": 8
  }
}
```

### **Detailed System Status**
```http
GET /health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "storage": "healthy", 
    "vectorstore": "healthy",
    "embedding_service": "healthy"
  },
  "metrics": {
    "response_time_avg": 45,
    "memory_usage": "512MB",
    "cpu_usage": "15%",
    "disk_usage": "2.1GB"
  },
  "version": "2.0.0"
}
```

### **System Information**
```http
GET /system/info
```

**Response:**
```json
{
  "service": "StreamWorks Document Management",
  "version": "2.0.0",
  "database": {
    "type": "PostgreSQL",
    "version": "15.4"
  },
  "statistics": {
    "total_folders": 25,
    "total_documents": 342,
    "total_storage_used": "1.8GB",
    "active_chat_sessions": 3
  },
  "features": [
    "Hierarchical folder structure",
    "Enterprise document management", 
    "RAG-based chat system",
    "Real-time WebSocket updates",
    "Multi-format document processing"
  ]
}
```

---

## ⚠️ **Error Handling**

### **HTTP Status Codes**
- `200` - Success
- `201` - Created  
- `400` - Bad Request (invalid input)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

### **Error Response Format**
```json
{
  "error": "VALIDATION_ERROR",
  "detail": "Field 'name' is required",
  "status": "error",
  "timestamp": "2025-01-01T00:00:00Z",
  "path": "/folders/",
  "method": "POST"
}
```

### **Common Error Codes**
- `VALIDATION_ERROR` - Request validation failed
- `NOT_FOUND` - Resource not found  
- `DUPLICATE_NAME` - Name already exists
- `FILE_TOO_LARGE` - File exceeds size limit
- `UNSUPPORTED_FORMAT` - File format not supported
- `PROCESSING_FAILED` - Document processing error
- `STORAGE_ERROR` - File system error

---

## 📊 **Rate Limiting**

```http
Rate-Limit-Limit: 1000
Rate-Limit-Remaining: 999
Rate-Limit-Reset: 1640995200
```

**Limits:**
- **API Calls**: 1000 per hour per IP
- **File Uploads**: 100MB per request, 1GB per hour
- **Chat Messages**: 60 per minute per session
- **WebSocket Connections**: 10 concurrent per IP

---

## 🔧 **Code Examples**

### **Python Client**
```python
import requests
import json

# Upload document
files = {'files': open('document.pdf', 'rb')}
response = requests.post(
    'http://localhost:8000/documents/upload',
    files=files,
    data={'folder_id': 'folder-uuid'}
)

# Chat with documents
chat_data = {
    "message": "What is the main topic of this document?",
    "use_local_ai": True
}
response = requests.post(
    'http://localhost:8000/chat/sessions/session-uuid/messages',
    json=chat_data
)
```

### **JavaScript/TypeScript Client**
```typescript
// Upload with progress
const uploadFile = async (file: File, folderId?: string) => {
  const formData = new FormData();
  formData.append('files', file);
  if (folderId) formData.append('folder_id', folderId);
  
  const response = await fetch('/documents/upload', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};

// Stream chat response
const streamChatResponse = async (sessionId: string, message: string) => {
  const response = await fetch(`/chat/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, use_local_ai: true })
  });
  
  const reader = response.body?.getReader();
  // Process streaming response...
};
```

### **cURL Examples**
```bash
# Create folder
curl -X POST "http://localhost:8000/folders/" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Folder", "description": "Test folder"}'

# Upload document  
curl -X POST "http://localhost:8000/documents/upload" \
  -F "files=@document.pdf" \
  -F "folder_id=folder-uuid"

# Search documents
curl -X POST "http://localhost:8000/chat/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "max_results": 5}'
```

---

## 🛡️ **Security**

### **Authentication** (Ready for Integration)
```http
Authorization: Bearer <jwt_token>
```

### **CORS Configuration**
```python
# Configured origins
ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://localhost:3001", 
  "https://your-production-domain.com"
]
```

### **File Upload Security**
- File type validation
- Size limits (100MB per file)
- Virus scanning (configurable)
- Secure storage paths
- MIME type verification

---

**🔗 Interactive Documentation**: http://localhost:8000/docs  
**📧 Support**: [GitHub Issues](https://github.com/your-repo/issues)

*Vollständige API-Referenz für Enterprise RAG System - Version 2.0.0*