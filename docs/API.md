# 🔌 API Documentation

> **Complete REST API reference for StreamWorks Document Management System**  
> Interactive docs available at: `http://localhost:8000/docs`

---

## 🎯 **API Overview**

StreamWorks provides a RESTful API built with **FastAPI**, featuring:

- **Automatic Documentation** - Interactive Swagger UI at `/docs`
- **Type Safety** - Pydantic models for request/response validation
- **Async Operations** - Non-blocking I/O for high performance
- **Error Handling** - Consistent error responses with details
- **File Operations** - Streaming uploads and downloads

### **Base URL**
```
Development: http://localhost:8000
Production:  https://your-domain.com/api
```

### **Response Format**
All API responses follow a consistent JSON structure:

```json
// Success Response
{
  "data": { ... },           // Response payload
  "message": "Success",      // Human-readable message  
  "timestamp": "2025-09-05T21:30:00Z"
}

// Error Response  
{
  "error": "ValidationError",
  "detail": "Field 'name' is required",
  "timestamp": "2025-09-05T21:30:00Z"
}
```

---

## 📁 **Folder Management**

### **List All Folders**
```http
GET /folders/
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Documents",
      "parent_id": null,
      "description": "Root folder for documents",
      "created_at": "2025-09-05T10:00:00Z",
      "updated_at": "2025-09-05T10:00:00Z",
      "children": [
        {
          "id": 2,
          "name": "Projects",
          "parent_id": 1,
          "description": "Project documents",
          "created_at": "2025-09-05T11:00:00Z", 
          "updated_at": "2025-09-05T11:00:00Z",
          "children": []
        }
      ]
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
  "parent_id": 1,
  "description": "Optional description"
}
```

**Response:**
```json
{
  "data": {
    "id": 3,
    "name": "New Folder",
    "parent_id": 1,
    "description": "Optional description",
    "created_at": "2025-09-05T12:00:00Z",
    "updated_at": "2025-09-05T12:00:00Z"
  },
  "message": "Folder created successfully"
}
```

**Validation Rules:**
- `name`: Required, 1-255 characters
- `parent_id`: Optional, must be valid folder ID
- `description`: Optional, max 1000 characters

### **Get Folder Details**
```http
GET /folders/{folder_id}
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "Documents", 
    "parent_id": null,
    "description": "Root folder",
    "created_at": "2025-09-05T10:00:00Z",
    "updated_at": "2025-09-05T10:00:00Z",
    "document_count": 5,
    "child_folder_count": 2
  }
}
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
DELETE /folders/{folder_id}
```

⚠️ **Warning**: Deletes folder and all contents (documents and subfolders)

**Response:**
```json
{
  "message": "Folder deleted successfully",
  "deleted_items": {
    "folders": 3,
    "documents": 7
  }
}
```

### **List Documents in Folder**
```http
GET /folders/{folder_id}/documents
```

**Query Parameters:**
- `limit`: Number of documents to return (default: 50)
- `offset`: Skip number of documents (default: 0)
- `sort`: Sort field (`name`, `created_at`, `file_size`)
- `order`: Sort order (`asc`, `desc`)

---

## 📄 **Document Management**

### **List All Documents**
```http
GET /documents/
```

**Query Parameters:**
- `folder_id`: Filter by folder ID
- `filename`: Search by filename (partial match)
- `mime_type`: Filter by MIME type
- `limit`: Number of results (default: 50, max: 100)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "filename": "report.pdf",
      "original_name": "Monthly Report.pdf",
      "folder_id": 2,
      "file_path": "/storage/documents/2025/09/report_abc123.pdf",
      "file_size": 2048576,
      "mime_type": "application/pdf",
      "created_at": "2025-09-05T14:30:00Z",
      "updated_at": "2025-09-05T14:30:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### **Upload Documents**
```http
POST /documents/upload
Content-Type: multipart/form-data

files: [File objects]
folder_id: 2 (optional)
```

**Example with curl:**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx" \
  -F "folder_id=2"
```

**Response:**
```json
{
  "data": {
    "uploaded": [
      {
        "id": 1,
        "filename": "document1.pdf",
        "original_name": "document1.pdf",
        "file_size": 1024000,
        "mime_type": "application/pdf"
      }
    ],
    "failed": [
      {
        "filename": "document2.docx",
        "error": "File too large"
      }
    ]
  },
  "message": "Upload completed"
}
```

**Upload Restrictions:**
- **Max file size**: 100MB per file
- **Allowed types**: PDF, DOCX, TXT, JPG, PNG, ZIP
- **Max files per request**: 20 files
- **Total request size**: 500MB

### **Get Document Metadata**
```http
GET /documents/{document_id}
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "filename": "report.pdf",
    "original_name": "Monthly Report.pdf",
    "folder_id": 2,
    "folder_name": "Projects",
    "file_path": "/storage/documents/2025/09/report_abc123.pdf",
    "file_size": 2048576,
    "file_size_formatted": "2.0 MB",
    "mime_type": "application/pdf",
    "created_at": "2025-09-05T14:30:00Z",
    "updated_at": "2025-09-05T14:30:00Z"
  }
}
```

### **Download Document**
```http
GET /documents/{document_id}/download
```

**Response:** 
- **Content-Type**: Original MIME type
- **Content-Disposition**: `attachment; filename="original_name.ext"`
- **Body**: File content (streaming response)

**Example with curl:**
```bash
curl -X GET "http://localhost:8000/documents/1/download" \
  -o "downloaded_file.pdf"
```

### **Delete Document**
```http
DELETE /documents/{document_id}
```

**Response:**
```json
{
  "message": "Document deleted successfully",
  "deleted_file": "report.pdf"
}
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
  "service": "StreamWorks Document Management"
}
```

### **Database Health Check**
```http
GET /health/database
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### **Detailed Health Check**
```http
GET /health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "storage": "healthy"
  },
  "version": "2.0.0",
  "timestamp": "2025-09-05T21:28:00Z"
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
    "type": "PostgreSQL (Supabase)",
    "version": "15.1"
  },
  "statistics": {
    "total_folders": 5,
    "total_documents": 42
  },
  "features": [
    "Hierarchical folder structure",
    "Enterprise document management",
    "RESTful API",
    "File upload/download",
    "Bulk operations",
    "Search and filtering"
  ]
}
```

---

## ❌ **Error Codes & Handling**

### **HTTP Status Codes**

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (duplicate name) |
| 413 | Payload Too Large | File size exceeds limit |
| 415 | Unsupported Media Type | Invalid file type |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### **Error Response Format**

```json
{
  "error": "ValidationError",
  "detail": "Field 'name' is required and must be between 1-255 characters",
  "field": "name",
  "timestamp": "2025-09-05T21:30:00Z"
}
```

### **Common Error Scenarios**

**Folder Not Found:**
```json
{
  "error": "NotFound",
  "detail": "Folder with ID 999 not found"
}
```

**Invalid Parent Folder:**
```json
{
  "error": "ValidationError", 
  "detail": "Cannot create folder: parent folder does not exist"
}
```

**File Too Large:**
```json
{
  "error": "PayloadTooLarge",
  "detail": "File size 150MB exceeds maximum limit of 100MB"
}
```

**Duplicate Folder Name:**
```json
{
  "error": "Conflict",
  "detail": "Folder with name 'Projects' already exists in parent folder"
}
```

---

## 🔐 **Authentication & Authorization**

> **Note**: Authentication is prepared but not yet implemented in the current version.

### **Planned Authentication Flow**

```http
# Login
POST /auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}

# Authenticated Request
GET /documents/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📊 **Rate Limiting & Quotas**

### **Current Limits** (Development)
- **File Upload**: 20 files per request
- **Request Size**: 500MB total
- **Individual File**: 100MB maximum
- **API Requests**: No rate limiting in development

### **Planned Production Limits**
- **API Requests**: 1000 requests per hour per IP
- **File Uploads**: 100 files per hour per user  
- **Storage Quota**: 10GB per user account

---

## 🚀 **API Client Examples**

### **JavaScript/TypeScript**

```typescript
// API Client Setup
class StreamWorksAPI {
  private baseURL = 'http://localhost:8000';
  
  async createFolder(data: FolderCreate): Promise<Folder> {
    const response = await fetch(`${this.baseURL}/folders/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }
  
  async uploadFiles(files: File[], folderId?: number): Promise<UploadResponse> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    if (folderId) formData.append('folder_id', folderId.toString());
    
    const response = await fetch(`${this.baseURL}/documents/upload`, {
      method: 'POST',
      body: formData
    });
    
    return response.json();
  }
}
```

### **Python Client**

```python
import httpx
from typing import List, Optional

class StreamWorksClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def create_folder(self, name: str, parent_id: Optional[int] = None, 
                           description: Optional[str] = None) -> dict:
        data = {"name": name}
        if parent_id: data["parent_id"] = parent_id
        if description: data["description"] = description
        
        response = await self.client.post(f"{self.base_url}/folders/", json=data)
        response.raise_for_status()
        return response.json()
    
    async def upload_files(self, file_paths: List[str], folder_id: Optional[int] = None) -> dict:
        files = [("files", open(path, "rb")) for path in file_paths]
        data = {"folder_id": folder_id} if folder_id else {}
        
        response = await self.client.post(
            f"{self.base_url}/documents/upload", 
            files=files, 
            data=data
        )
        response.raise_for_status()
        return response.json()
```

---

## 🔗 **API Resources**

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Redoc Documentation**: http://localhost:8000/redoc
- **Health Checks**: http://localhost:8000/health

---

**Complete API reference for enterprise document management** 🔌