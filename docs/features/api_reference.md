# StreamWorks-KI API Reference

**Version**: 1.0.0  
**Last Updated**: 2025-07-24  
**Base URL**: `http://localhost:8000/api/v1`

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Q&A System API](#qa-system-api)
3. [Document Management API](#document-management-api)
4. [Analytics API](#analytics-api)
5. [Category & Folder Management](#category--folder-management)
6. [Training Data API](#training-data-api)
7. [XML Generation API](#xml-generation-api)
8. [Chat API](#chat-api)
9. [Error Handling](#error-handling)
10. [Rate Limiting & Security](#rate-limiting--security)
11. [SDK Examples](#sdk-examples)

---

## API Overview

### Base URL
All API endpoints are prefixed with:
```
http://localhost:8000/api/v1
```

### Authentication
Currently, the API does not require authentication. In production environments, implement appropriate authentication mechanisms.

### Common Headers
```http
Content-Type: application/json
Accept: application/json
```

### Response Format
All responses follow a consistent JSON structure:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2025-01-24T10:30:00Z"
}
```

---

## Q&A System API

The Q&A system uses RAG (Retrieval-Augmented Generation) to provide accurate answers based on indexed documents.

### Ask a Question

**POST** `/qa/ask`

Ask a question about StreamWorks and get an AI-powered response.

#### Request Body
```json
{
  "question": "Wie konfiguriere ich einen Datenstream in StreamWorks?"
}
```

#### Parameters
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| question | string | Yes | The question to ask (3-500 characters) |

#### Response
```json
{
  "question": "Wie konfiguriere ich einen Datenstream in StreamWorks?",
  "answer": "Um einen Datenstream in StreamWorks zu konfigurieren...",
  "sources": [
    "streamworks_manual_v2.pdf",
    "configuration_guide.md"
  ],
  "processing_time": 2.45,
  "confidence": 0.92,
  "documents_analyzed": 15,
  "embedding_time": 0.49,
  "retrieval_time": 0.73,
  "generation_time": 1.23,
  "quality_score": 0.92,
  "language_detected": "de",
  "question_type": "standard",
  "response_format": "production"
}
```

#### Status Codes
- `200 OK` - Question answered successfully
- `400 Bad Request` - Invalid question format
- `500 Internal Server Error` - Processing error

#### Example
```bash
curl -X POST "http://localhost:8000/api/v1/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Was ist StreamWorks?"
  }'
```

### Get Q&A Health Status

**GET** `/qa/health`

Check the health status of the Q&A service.

#### Response
```json
{
  "status": "production_ready",
  "ready": true,
  "embedding_model": "multilingual-e5-large",
  "mistral_model": "mistral:7b-instruct",
  "collection": "streamworks_docs"
}
```

### Get Service Statistics

**GET** `/qa/stats`

Get comprehensive statistics about the Q&A service.

#### Response
```json
{
  "status": "success",
  "service": "Unified RAG Service",
  "ready": true,
  "collection_size": 1250
}
```

---

## Document Management API

Manage document conversion and processing for the knowledge base.

### Upload and Convert Document

**POST** `/documents/upload`

Upload a document and convert it to markdown format.

#### Request
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

#### Parameters
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | Yes | The document to upload (PDF, TXT, MD) |
| category | string | No | Document category (default: "general") |

#### Response
```json
{
  "success": true,
  "message": "Document converted successfully",
  "document_id": "doc_123456",
  "original_filename": "manual.pdf",
  "output_path": "/data/documents/converted/manual.md",
  "processing_time": 3.45,
  "pages_processed": 25,
  "file_size": 2048576
}
```

#### Status Codes
- `200 OK` - Document uploaded and converted successfully
- `400 Bad Request` - Invalid file or format
- `422 Unprocessable Entity` - Conversion failed
- `500 Internal Server Error` - Server error

### Batch Convert Documents

**POST** `/documents/batch-convert`

Convert all existing PDF and TXT files in the system.

#### Request Body
```json
{
  "overwrite": false
}
```

#### Parameters
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| overwrite | boolean | No | Whether to overwrite existing conversions |

#### Response
```json
{
  "success": true,
  "message": "Batch conversion started (overwrite=false)",
  "note": "Check logs for progress updates"
}
```

### Get Conversion Statistics

**GET** `/documents/conversion-stats`

Get statistics about document conversions.

#### Response
```json
{
  "service_stats": {
    "total_files": 150,
    "successful_conversions": 145,
    "failed_conversions": 5,
    "success_rate": "96.7%",
    "total_processing_time": "450.32s",
    "average_processing_time": "3.10s",
    "total_size_mb": "125.45 MB"
  }
}
```

---

## Analytics API

Comprehensive analytics for system performance and usage.

### Document Processing Analytics

**GET** `/analytics/document-processing`

Get detailed document processing performance statistics.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| days | integer | No | Number of days to analyze (default: 30) |
| file_type | string | No | Filter by file type (.pdf, .txt, .md) |

#### Response
```json
{
  "total_documents": 1250,
  "avg_processing_time": 2.45,
  "max_processing_time": 15.3,
  "min_processing_time": 0.5,
  "success_rate": 98.5,
  "total_processing_hours": 3.06,
  "documents_per_hour": 408.5,
  "file_type_breakdown": {
    "PDF": 750,
    "TXT": 300,
    "MD": 200
  },
  "performance_trends": [
    {
      "date": "2025-01-20",
      "documents_count": 45,
      "avg_processing_time": 2.3,
      "success_rate": 100.0
    }
  ]
}
```

### Batch Processing Statistics

**GET** `/analytics/batch-statistics`

Analyze batch processing performance.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| days | integer | No | Number of days to analyze (default: 30) |

#### Response
```json
{
  "total_batches": 25,
  "avg_batch_size": 50,
  "avg_batch_time": 125.5,
  "total_files_processed": 1250,
  "batch_success_rate": 96.0,
  "concurrent_processing_efficiency": 85.5,
  "batch_trends": [
    {
      "date": "2025-01-20",
      "batches_count": 3,
      "avg_processing_time": 120.5,
      "success_rate": 100.0,
      "files_processed": 150
    }
  ]
}
```

### System Metrics

**GET** `/analytics/system-metrics`

Get detailed system performance metrics.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| days | integer | No | Number of days to analyze (default: 7) |

#### Response
```json
{
  "cpu_performance": {
    "avg_pages_per_conversion": 25.5,
    "avg_processing_time": 2.45,
    "peak_processing_time": 15.3,
    "min_processing_time": 0.5,
    "cpu_efficiency_score": 85.5
  },
  "memory_usage": {
    "avg_file_size_mb": 1.5,
    "max_file_size_mb": 50.0,
    "total_data_processed_gb": 2.5,
    "memory_efficiency_score": 85.0
  },
  "database_performance": {
    "total_database_operations": 5000,
    "avg_query_time_ms": 2.5,
    "database_health_score": 90.0,
    "connection_pool_efficiency": 95.0
  },
  "error_analysis": {
    "total_errors": 15,
    "unique_error_types": 3,
    "error_rate": 0.3,
    "most_common_errors": []
  },
  "system_health_score": 88.5,
  "uptime_statistics": {
    "system_uptime_days": 7,
    "active_processing_days": 7,
    "uptime_percentage": 100.0,
    "first_activity": "2025-01-17T08:00:00Z",
    "last_activity": "2025-01-24T10:30:00Z"
  }
}
```

### Export Analytics Data

**GET** `/analytics/export/csv`

Export analytics data as CSV for further analysis.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| metric_type | string | Yes | Type of metrics (document, batch, system) |
| days | integer | No | Number of days to export (default: 30) |

#### Response
Returns a CSV file with the requested data.

#### Example
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/export/csv?metric_type=document&days=30" \
  -o analytics_export.csv
```

---

## Category & Folder Management

Organize documents into categories and folders.

### Categories API

#### List Categories

**GET** `/categories`

Get all document categories with file counts.

##### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| include_inactive | boolean | No | Include inactive categories (default: false) |

##### Response
```json
[
  {
    "id": "cat_123",
    "name": "Q&A Documentation",
    "slug": "qa",
    "description": "StreamWorks Q&A system documentation",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-20T15:30:00Z",
    "file_count": 45,
    "is_active": true
  }
]
```

#### Create Category

**POST** `/categories`

Create a new document category.

##### Request Body
```json
{
  "name": "API Documentation",
  "description": "StreamWorks API reference and guides"
}
```

##### Response
```json
{
  "id": "cat_456",
  "name": "API Documentation",
  "slug": "api-documentation",
  "description": "StreamWorks API reference and guides",
  "created_at": "2025-01-24T10:30:00Z",
  "updated_at": "2025-01-24T10:30:00Z",
  "file_count": 0,
  "is_active": true
}
```

#### Update Category

**PUT** `/categories/{category_id}`

Update an existing category.

##### Request Body
```json
{
  "name": "Updated API Documentation",
  "description": "Updated description"
}
```

#### Delete Category

**DELETE** `/categories/{category_id}`

Delete a category (soft delete by default).

##### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| force | boolean | No | Force delete with all files (default: false) |

### Folders API

#### List Folders

**GET** `/categories/{category_id}/folders`

Get all folders in a category.

##### Response
```json
[
  {
    "id": "folder_123",
    "name": "Version 2.0",
    "slug": "version-2-0",
    "description": "Documentation for version 2.0",
    "category_id": "cat_123",
    "category_name": "Q&A Documentation",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-20T15:30:00Z",
    "file_count": 15,
    "is_active": true
  }
]
```

#### Create Folder

**POST** `/categories/{category_id}/folders`

Create a new folder in a category.

##### Request Body
```json
{
  "name": "Version 3.0",
  "description": "Documentation for version 3.0"
}
```

### Simple Folders API

#### Get Folders (Simple)

**GET** `/simple-folders/categories/{category_slug}/folders`

Get folders for a category using slug.

##### Response
```json
{
  "folders": [
    {
      "id": "folder_123",
      "name": "StreamWorks Basics",
      "slug": "streamworks-basics",
      "parent_folder_id": null,
      "file_count": 0,
      "subfolder_count": 0
    }
  ]
}
```

#### Create Folder (Simple)

**POST** `/simple-folders/categories/{category_slug}/folders`

Create a folder using category slug.

##### Form Data
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Folder name |
| parent_id | string | No | Parent folder ID |

#### Delete Folder

**DELETE** `/simple-folders/folders/{folder_id}`

Delete a folder and its contents.

---

## Training Data API

Manage training data for the RAG system.

### Upload Training Files

#### Single File Upload

**POST** `/training/upload`

Upload a single training file with category and folder organization.

##### Form Data
| Field | Type | Required | Description |
|------------|------|----------|-------------|
| file | file | Yes | The file to upload |
| category_slug | string | Yes | Category slug (e.g., 'qa', 'stream-xml') |
| folder_id | string | No | Optional folder ID |
| folder_slug | string | No | Optional folder slug (legacy) |

##### Response
```json
{
  "message": "File uploaded successfully",
  "id": "file_123",
  "filename": "manual.pdf",
  "category": "Q&A Documentation",
  "folder": "Version 2.0",
  "size": 2048576,
  "status": "pending"
}
```

#### Batch Upload

**POST** `/training/upload-batch`

Upload multiple training files at once.

##### Form Data
| Field | Type | Required | Description |
|------------|------|----------|-------------|
| files | file[] | Yes | Multiple files to upload |
| source_category | string | Yes | Source category (Testdaten, StreamWorks Hilfe, SharePoint) |
| description | string | No | Optional description |

##### Response
```json
{
  "message": "Batch upload completed: 10 successful, 2 failed",
  "uploaded_files": 10,
  "failed_files": 2,
  "source_category": "StreamWorks Hilfe",
  "details": {
    "successful": ["doc1.pdf", "doc2.txt"],
    "failed": [
      {
        "filename": "doc3.exe",
        "error": "Invalid file extension"
      }
    ]
  }
}
```

### List Training Files

**GET** `/training/files`

Get list of all training files.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | string | No | Filter by category |
| status | string | No | Filter by status |

#### Response
```json
[
  {
    "id": "file_123",
    "filename": "manual.pdf",
    "category": "help_data",
    "file_path": "/data/training_data/manual.pdf",
    "file_size": 2048576,
    "upload_date": "2025-01-20T10:00:00Z",
    "status": "processed",
    "processing_time": 2.5,
    "chromadb_indexed": true,
    "chunk_count": 25,
    "error_message": null
  }
]
```

### Delete Training File

**DELETE** `/training/files/{file_id}`

Delete a training file.

#### Response
```json
{
  "message": "File deleted successfully"
}
```

### Process Training File

**POST** `/training/process/{file_id}`

Process a training file for indexing.

#### Response
```json
{
  "message": "File processing started",
  "file_id": "file_123"
}
```

### Index to ChromaDB

#### Single File

**POST** `/training/index/{file_id}`

Index a single file to ChromaDB.

#### Response
```json
{
  "success": true,
  "file_id": "file_123",
  "chunks_created": 25,
  "processing_time": 3.5
}
```

#### Batch Index

**POST** `/training/index/batch`

Index multiple files to ChromaDB.

##### Request Body
```json
{
  "file_ids": ["file_123", "file_456", "file_789"]
}
```

### Get Supported Formats

**GET** `/training/formats/supported`

Get list of all supported file formats.

#### Response
```json
{
  "supported_formats": [
    ".txt", ".md", ".rtf", ".log",
    ".pdf", ".docx", ".doc", ".odt",
    ".csv", ".tsv", ".xlsx", ".xls", 
    ".json", ".jsonl", ".yaml", ".yml",
    ".xml", ".xsd", ".html", ".py", ".js"
  ],
  "document_categories": [
    "text", "office", "data", "code", "markup"
  ],
  "total_formats": 40,
  "total_categories": 5,
  "processing_stats": {
    "total_processed": 1250,
    "formats_processed": {
      "pdf": 750,
      "txt": 300,
      "md": 200
    }
  }
}
```

### Analyze File Format

**POST** `/training/analyze-file`

Analyze a file without uploading it.

##### Form Data
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | Yes | File to analyze |

##### Response
```json
{
  "filename": "document.pdf",
  "file_size": 2048576,
  "detected_format": "pdf",
  "document_category": "office",
  "is_supported": true,
  "processing_method": "pdf_processor",
  "content_preview": "This is the beginning of the document...",
  "analysis_timestamp": "2025-01-24T10:30:00Z"
}
```

---

## XML Generation API

Generate StreamWorks XML configurations using AI.

### Generate from Chat

**POST** `/xml/generate-from-chat`

Generate XML from natural language description.

#### Request Body
```json
{
  "prompt": "Erstelle eine XML-Konfiguration für einen täglichen Datenexport von SAP nach Salesforce",
  "context": "streamworks",
  "template_id": null
}
```

#### Response
```json
{
  "xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<streamworks-config>...</streamworks-config>",
  "validation": {
    "isValid": true,
    "errors": [],
    "warnings": []
  },
  "metadata": {
    "generation_method": "chat",
    "timestamp": "2025-01-24T10:30:00Z",
    "prompt_length": 85,
    "model": "mistral-7b"
  }
}
```

### Generate from Form

**POST** `/xml/generate-from-form`

Generate XML from structured form input.

#### Request Body
```json
{
  "streamName": "SAP Customer Sync",
  "description": "Daily customer data synchronization",
  "sourceSystem": "SAP",
  "targetSystem": "Salesforce",
  "dataFormat": "JSON",
  "schedule": "daily"
}
```

#### Response
Similar to chat generation with structured XML output.

### Generate from Template

**POST** `/xml/generate-from-template`

Generate XML using predefined templates.

#### Request Body
```json
{
  "template_id": "customer-sync",
  "parameters": {
    "source": "SAP",
    "target": "Salesforce",
    "schedule": "0 2 * * *"
  }
}
```

### Validate XML

**POST** `/xml/validate`

Validate XML content.

#### Request Body
```json
{
  "xml_content": "<?xml version=\"1.0\"?>..."
}
```

#### Response
```json
{
  "isValid": true,
  "errors": [],
  "warnings": ["XML should use StreamWorks namespace"]
}
```

### Get Templates

**GET** `/xml/templates`

Get available XML templates.

#### Response
```json
{
  "templates": [
    {
      "id": "customer-sync",
      "name": "Customer Data Sync",
      "description": "Template for customer data synchronization",
      "parameters": ["source", "target", "schedule"]
    }
  ]
}
```

---

## Chat API

Interactive chat interface with hybrid RAG/LLM capabilities.

### Send Message

**POST** `/chat/`

Send a message to the chat service.

#### Request Body
```json
{
  "message": "Wie konfiguriere ich StreamWorks?",
  "conversation_id": "conv_123",
  "mode": "hybrid",
  "context_window": 5
}
```

#### Parameters
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | Message content (1-4000 chars) |
| conversation_id | string | No | Existing conversation ID |
| mode | string | No | Chat mode: chat, rag, hybrid (default: hybrid) |
| context_window | integer | No | Context messages to include (0-20, default: 5) |

#### Response
```json
{
  "response": "Um StreamWorks zu konfigurieren...",
  "conversation_id": "conv_123",
  "message_id": "msg_456",
  "sources": ["config_guide.pdf", "setup_manual.md"],
  "mode_used": "hybrid",
  "processing_time": 2.5,
  "metadata": {
    "tokens_used": 450,
    "context_retrieved": true
  }
}
```

### List Conversations

**GET** `/chat/conversations`

Get list of all conversations.

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Results per page (default: 20) |
| offset | integer | No | Pagination offset (default: 0) |

#### Response
```json
{
  "conversations": [
    {
      "id": "conv_123",
      "title": "StreamWorks Configuration",
      "created_at": "2025-01-20T10:00:00Z",
      "updated_at": "2025-01-20T11:30:00Z",
      "message_count": 10,
      "metadata": {}
    }
  ],
  "total": 25,
  "limit": 20,
  "offset": 0
}
```

### Get Conversation

**GET** `/chat/conversations/{conversation_id}`

Get a specific conversation with all messages.

#### Response
```json
{
  "id": "conv_123",
  "title": "StreamWorks Configuration",
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T11:30:00Z",
  "messages": [
    {
      "id": "msg_123",
      "role": "user",
      "content": "Wie konfiguriere ich StreamWorks?",
      "timestamp": "2025-01-20T10:00:00Z",
      "metadata": {}
    },
    {
      "id": "msg_124",
      "role": "assistant",
      "content": "Um StreamWorks zu konfigurieren...",
      "timestamp": "2025-01-20T10:00:05Z",
      "metadata": {
        "sources": ["config_guide.pdf"]
      }
    }
  ],
  "metadata": {}
}
```

### Delete Conversation

**DELETE** `/chat/conversations/{conversation_id}`

Delete a conversation.

#### Response
```json
{
  "message": "Conversation deleted successfully"
}
```

### Create Conversation

**POST** `/chat/conversations`

Create a new conversation.

#### Request Body
```json
{
  "title": "New StreamWorks Discussion"
}
```

#### Response
```json
{
  "id": "conv_789",
  "title": "New StreamWorks Discussion",
  "created_at": "2025-01-24T10:30:00Z",
  "message": "Conversation created successfully"
}
```

---

## Error Handling

The API uses standard HTTP status codes and consistent error responses.

### Error Response Format
```json
{
  "detail": "Detailed error message",
  "status_code": 400,
  "error_type": "ValidationError",
  "timestamp": "2025-01-24T10:30:00Z"
}
```

### Common Status Codes
| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 413 | Payload Too Large | File size exceeds limit |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Types
- **ValidationError**: Input validation failed
- **NotFoundError**: Requested resource not found
- **ConflictError**: Resource conflict (duplicate)
- **ProcessingError**: Processing or conversion failed
- **RateLimitError**: Too many requests
- **InternalError**: Unexpected server error

---

## Rate Limiting & Security

### Rate Limits
Currently, no rate limiting is implemented. In production:
- General API: 100 requests per minute
- File uploads: 10 requests per minute
- Analytics exports: 5 requests per minute

### Security Headers
Recommended security headers for production:
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### File Upload Limits
- Maximum file size: 50MB
- Maximum files per batch: 20
- Allowed extensions: See supported formats endpoint

### Input Validation
All inputs are validated using Pydantic schemas with:
- Type checking
- Length limits
- Pattern matching for specific fields
- SQL injection prevention
- XSS protection

---

## SDK Examples

### Python
```python
import requests
import json

class StreamWorksAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def ask_question(self, question):
        """Ask a question to the Q&A system"""
        response = self.session.post(
            f"{self.base_url}/qa/ask",
            json={"question": question}
        )
        response.raise_for_status()
        return response.json()
    
    def upload_file(self, file_path, category_slug, folder_id=None):
        """Upload a training file"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'category_slug': category_slug,
                'folder_id': folder_id
            }
            response = self.session.post(
                f"{self.base_url}/training/upload",
                files=files,
                data=data
            )
        response.raise_for_status()
        return response.json()
    
    def generate_xml(self, prompt):
        """Generate XML from natural language"""
        response = self.session.post(
            f"{self.base_url}/xml/generate-from-chat",
            json={"prompt": prompt}
        )
        response.raise_for_status()
        return response.json()

# Usage example
api = StreamWorksAPI()
result = api.ask_question("Was ist StreamWorks?")
print(result['answer'])
```

### JavaScript/TypeScript
```typescript
interface StreamWorksAPI {
  baseUrl: string;
  askQuestion(question: string): Promise<QAResponse>;
  uploadFile(file: File, categorySlug: string, folderId?: string): Promise<UploadResponse>;
  generateXML(prompt: string): Promise<XMLResponse>;
}

class StreamWorksClient implements StreamWorksAPI {
  constructor(public baseUrl: string = "http://localhost:8000/api/v1") {}

  async askQuestion(question: string): Promise<QAResponse> {
    const response = await fetch(`${this.baseUrl}/qa/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }

  async uploadFile(file: File, categorySlug: string, folderId?: string): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category_slug', categorySlug);
    if (folderId) {
      formData.append('folder_id', folderId);
    }

    const response = await fetch(`${this.baseUrl}/training/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  async generateXML(prompt: string): Promise<XMLResponse> {
    const response = await fetch(`${this.baseUrl}/xml/generate-from-chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error(`XML generation failed: ${response.statusText}`);
    }

    return response.json();
  }
}

// Usage
const client = new StreamWorksClient();
const answer = await client.askQuestion("Was ist StreamWorks?");
console.log(answer.answer);
```

### cURL Examples

#### Ask a Question
```bash
curl -X POST "http://localhost:8000/api/v1/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Wie konfiguriere ich einen Datenstream?"
  }'
```

#### Upload a File
```bash
curl -X POST "http://localhost:8000/api/v1/training/upload" \
  -F "file=@document.pdf" \
  -F "category_slug=qa" \
  -F "folder_id=folder_123"
```

#### Generate XML
```bash
curl -X POST "http://localhost:8000/api/v1/xml/generate-from-chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create XML config for daily SAP to Salesforce sync"
  }'
```

#### Get Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/document-processing?days=7"
```

#### Chat Interaction
```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Erkläre mir StreamWorks",
    "mode": "hybrid"
  }'
```

---

## API Versioning

The API uses URL versioning:
- Current version: `/api/v1`
- Future versions will be available at `/api/v2`, etc.

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support

For API support and questions:
- Documentation: This document
- Interactive Docs: `/docs`
- Health Endpoints: Each service has a `/health` endpoint

---

*Last Updated: 2025-07-24*  
*Version: 1.0.0*  
*StreamWorks-KI Enterprise API*