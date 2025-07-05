# 🌐 API Documentation - StreamWorks-KI

**Version**: 2.0+ | **Base URL**: `http://localhost:8000` | **Last Updated**: 2025-07-05

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Smart Search APIs](#smart-search-apis)
4. [Document Processing APIs](#document-processing-apis)
5. [Chat & Generation APIs](#chat--generation-apis)
6. [Health & Monitoring APIs](#health--monitoring-apis)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Examples & Tutorials](#examples--tutorials)

---

## 🔍 Overview

The StreamWorks-KI API provides intelligent document processing, advanced search capabilities, and natural language interaction for StreamWorks automation. The API is built with FastAPI and follows RESTful principles with comprehensive OpenAPI documentation.

### **Key Features**
- **🧠 Smart Search**: 5 intelligent search strategies with auto-selection
- **📄 Multi-Format Processing**: 39+ supported file formats
- **🤖 RAG-Powered Chat**: Context-aware responses with citations
- **⚡ XML Generation**: Template-based StreamWorks configuration creation
- **📊 Performance Monitoring**: Comprehensive metrics and analytics

### **API Specifications**
- **Protocol**: HTTP/HTTPS
- **Format**: JSON
- **Documentation**: OpenAPI 3.0 (Swagger UI at `/docs`)
- **Rate Limiting**: Implemented per endpoint
- **CORS**: Configured for cross-origin requests

---

## 🔐 Authentication

**Current Status**: Open API (Authentication planned for production)

```http
# Headers (Future implementation)
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
Content-Type: application/json
```

---

## 🔍 Smart Search APIs

### **POST /api/v1/search/smart**
Intelligent search with automatic query classification and strategy selection.

#### **Request**
```http
POST /api/v1/search/smart
Content-Type: application/json

{
  "query": "How to create XML stream for daily batch processing?",
  "top_k": 5,
  "include_analysis": true
}
```

#### **Parameters**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ | - | Search query (1-1000 characters) |
| `top_k` | integer | ❌ | 5 | Number of results (1-20) |
| `include_analysis` | boolean | ❌ | true | Include query analysis in response |

#### **Response**
```json
{
  "results": [
    {
      "content": "StreamWorks XML stream configuration for batch processing...",
      "score": 0.95,
      "explanation": "Matches XML generation intent and contains batch processing concepts",
      "metadata": {
        "document_category": "xml_config",
        "file_format": "xml",
        "chunk_type": "xml_element",
        "processing_method": "element_based",
        "source_file": "stream_template.xml"
      },
      "relevance_factors": [
        "Matches XML/configuration intent",
        "Contains data processing content",
        "Source format: xml"
      ]
    }
  ],
  "total_results": 5,
  "search_strategy": "filtered",
  "response_time_ms": 125.7,
  "query_analysis": {
    "primary_intent": "xml_generation",
    "intent_confidence": 0.9,
    "complexity_level": "intermediate",
    "detected_concepts": ["xml_workflow", "data_processing"],
    "preferred_doc_types": ["xml_config", "schema_def", "code_script"],
    "enhancement_suggestions": [],
    "suggested_filters": {
      "document_types": ["xml_config", "schema_def"],
      "file_formats": ["xml", "xsd"],
      "complexity_range": [3, 7]
    }
  }
}
```

#### **Status Codes**
- `200` - Success
- `400` - Invalid query parameters
- `429` - Rate limit exceeded
- `500` - Internal server error

---

### **POST /api/v1/search/advanced**
Advanced search with custom filters and explicit control.

#### **Request**
```http
POST /api/v1/search/advanced
Content-Type: application/json

{
  "query": "XML template configuration",
  "top_k": 10,
  "filters": {
    "document_types": ["xml_config", "schema_def"],
    "file_formats": ["xml", "xsd"],
    "chunk_types": ["xml_element"],
    "source_categories": ["StreamWorks Hilfe"],
    "complexity_min": 3,
    "complexity_max": 8
  },
  "include_analysis": true
}
```

#### **Filter Parameters**
| Filter | Type | Description |
|--------|------|-------------|
| `document_types` | array[string] | Filter by document categories |
| `file_formats` | array[string] | Filter by file formats |
| `chunk_types` | array[string] | Filter by chunk processing types |
| `source_categories` | array[string] | Filter by source categories |
| `processing_methods` | array[string] | Filter by processing methods |
| `complexity_min` | integer | Minimum complexity (1-10) |
| `complexity_max` | integer | Maximum complexity (1-10) |

#### **Available Filter Values**
```http
GET /api/v1/search/filters/options
```

Response:
```json
{
  "document_types": [
    "help_docs", "xml_config", "schema_def", "qa_faq", 
    "code_script", "office_doc", "structured_data", 
    "configuration", "api_docs", "email_comm", 
    "web_content", "log_file"
  ],
  "file_formats": [
    "txt", "md", "pdf", "docx", "csv", "json", "yaml", 
    "xml", "xsd", "py", "js", "sql", "html", "ini"
  ],
  "chunk_types": [
    "default_recursive", "function_based", "header_based", 
    "element_based", "structure_based", "row_based", 
    "section_based", "xml_element", "json_object_key", 
    "csv_rows", "html_section", "markdown_section"
  ],
  "processing_methods": [
    "multi_format_processor", "default_recursive", 
    "function_based", "structure_based", "element_based", 
    "row_based", "header_based"
  ],
  "source_categories": ["Testdaten", "StreamWorks Hilfe", "SharePoint"],
  "complexity_range": {
    "min": 1,
    "max": 10,
    "levels": {
      "basic": "1-3",
      "intermediate": "3-7",
      "advanced": "6-10"
    }
  }
}
```

---

### **POST /api/v1/search/analyze-query**
Analyze a query to understand intent, complexity, and suggested search strategy.

#### **Request**
```http
POST /api/v1/search/analyze-query
Content-Type: application/json

{
  "query": "Warum funktioniert mein XML Stream nicht?"
}
```

#### **Response**
```json
{
  "query": "Warum funktioniert mein XML Stream nicht?",
  "analysis": {
    "primary_intent": "troubleshooting",
    "intent_confidence": 0.85,
    "complexity_level": "intermediate",
    "detected_concepts": ["xml_workflow"],
    "preferred_doc_types": ["qa_faq", "help_docs", "log_file"],
    "search_strategy": "contextual",
    "enhancement_suggestions": [
      "Try including specific error messages or symptoms"
    ],
    "suggested_filters": {
      "document_types": ["qa_faq", "help_docs", "log_file"],
      "file_formats": ["xml", "log", "txt"],
      "complexity_range": [3, 7]
    },
    "query_metadata": {
      "word_count": 6,
      "character_count": 38,
      "technical_terms": 1,
      "question_type": "explanatory"
    }
  },
  "recommendations": {
    "optimal_strategy": "contextual",
    "suggested_document_types": ["qa_faq", "help_docs", "log_file"],
    "enhancement_tips": [
      "Try including specific error messages or symptoms"
    ]
  },
  "analysis_timestamp": "2025-07-05T10:30:45.123456"
}
```

---

### **GET /api/v1/search/strategies**
Get available search strategies and their descriptions.

#### **Response**
```json
{
  "available_strategies": {
    "semantic_only": {
      "name": "Semantic Only",
      "description": "Pure vector similarity search using embeddings",
      "best_for": ["Simple queries", "General information requests"],
      "performance": "Fast"
    },
    "filtered": {
      "name": "Filtered Search",
      "description": "Metadata-based filtering with semantic search",
      "best_for": ["Specific document types", "Technical queries"],
      "performance": "Medium"
    },
    "hybrid": {
      "name": "Hybrid Search",
      "description": "Combination of semantic, keyword, and filtered search",
      "best_for": ["Complex queries", "Multi-faceted information needs"],
      "performance": "Comprehensive"
    },
    "contextual": {
      "name": "Contextual Search",
      "description": "Query expansion with domain-specific context",
      "best_for": ["Troubleshooting", "Ambiguous queries"],
      "performance": "Intelligent"
    },
    "concept_based": {
      "name": "Concept-Based Search",
      "description": "Focus on domain-specific concepts and terminology",
      "best_for": ["API usage", "Technical documentation"],
      "performance": "Specialized"
    }
  },
  "default_strategy": "semantic_only",
  "auto_selection": "Smart search automatically selects optimal strategy based on query analysis"
}
```

---

### **GET /api/v1/search/smart/statistics**
Get comprehensive smart search performance statistics.

#### **Response**
```json
{
  "smart_search": {
    "total_searches": 1247,
    "successful_searches": 1198,
    "failed_searches": 49,
    "strategy_usage": {
      "semantic_only": 456,
      "filtered": 298,
      "hybrid": 234,
      "contextual": 156,
      "concept_based": 103
    },
    "average_response_time": 0.187,
    "filter_effectiveness": {
      "document_types": 0.82,
      "file_formats": 0.75,
      "complexity_range": 0.68
    },
    "strategy_distribution": {
      "semantic_only": 36.6,
      "filtered": 23.9,
      "hybrid": 18.8,
      "contextual": 12.5,
      "concept_based": 8.3
    }
  },
  "system_info": {
    "total_search_endpoints": 8,
    "available_strategies": 5,
    "smart_search_enabled": true,
    "last_updated": "2025-07-05T10:30:45.123456"
  }
}
```

---

## 📄 Document Processing APIs

### **POST /api/v1/training/upload-file**
Upload and process a single document file.

#### **Request**
```http
POST /api/v1/training/upload-file
Content-Type: multipart/form-data

file: <file_binary>
source_category: "StreamWorks Hilfe"
```

#### **Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | ✅ | Document file (max 50MB) |
| `source_category` | string | ❌ | Source category ("Testdaten", "StreamWorks Hilfe", "SharePoint") |

#### **Response**
```json
{
  "success": true,
  "file_id": "abc123def456",
  "filename": "streamworks_guide.pdf",
  "file_size": 1048576,
  "processing_result": {
    "success": true,
    "file_format": "pdf",
    "document_category": "help_docs",
    "processing_method": "default_recursive",
    "chunk_count": 24,
    "metadata": {
      "original_size": 1048576,
      "chunk_sizes": [1024, 1156, 987, 1200]
    }
  },
  "indexing_status": "completed",
  "vector_ids": ["vec_1", "vec_2", "vec_3"],
  "processing_time_ms": 3450.7,
  "message": "File processed and indexed successfully"
}
```

---

### **POST /api/v1/training/batch-upload**
Upload and process multiple files in batch.

#### **Request**
```http
POST /api/v1/training/batch-upload
Content-Type: multipart/form-data

files: [<file1>, <file2>, <file3>]
source_category: "StreamWorks Hilfe"
```

#### **Response**
```json
{
  "success": true,
  "total_files": 3,
  "successful_uploads": 3,
  "failed_uploads": 0,
  "results": [
    {
      "filename": "config_guide.xml",
      "file_id": "xml_001",
      "success": true,
      "chunk_count": 12,
      "processing_time_ms": 1234.5
    },
    {
      "filename": "api_docs.md",
      "file_id": "md_002", 
      "success": true,
      "chunk_count": 8,
      "processing_time_ms": 987.3
    },
    {
      "filename": "script.py",
      "file_id": "py_003",
      "success": true,
      "chunk_count": 15,
      "processing_time_ms": 1567.8
    }
  ],
  "total_processing_time_ms": 3789.6,
  "total_chunks_created": 35,
  "indexing_status": "completed"
}
```

---

### **GET /api/v1/training/files**
Get list of uploaded training files with filtering and pagination.

#### **Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Number of files to return (1-100) |
| `offset` | integer | 0 | Offset for pagination |
| `status` | string | all | Filter by processing status |
| `format` | string | all | Filter by file format |
| `category` | string | all | Filter by document category |

#### **Request**
```http
GET /api/v1/training/files?limit=20&offset=0&status=completed&format=xml
```

#### **Response**
```json
{
  "files": [
    {
      "id": "file_123",
      "filename": "stream_config.xml",
      "file_size": 2048,
      "file_format": "xml",
      "document_category": "xml_config",
      "source_category": "StreamWorks Hilfe",
      "processing_status": "completed",
      "chunk_count": 8,
      "is_indexed": true,
      "uploaded_at": "2025-07-05T09:15:30.123456",
      "processed_at": "2025-07-05T09:15:33.567890"
    }
  ],
  "total_count": 156,
  "limit": 20,
  "offset": 0,
  "has_more": true,
  "filters_applied": {
    "status": "completed",
    "format": "xml"
  }
}
```

---

### **GET /api/v1/training/supported-formats**
Get all supported file formats and their processing capabilities.

#### **Response**
```json
{
  "supported_formats": [
    {
      "format": "xml",
      "extensions": [".xml"],
      "category": "XML Family",
      "chunking_strategy": "element_based",
      "processing_method": "xml_parser",
      "supports_metadata": true,
      "max_file_size_mb": 50
    },
    {
      "format": "py",
      "extensions": [".py"],
      "category": "Code & Scripts", 
      "chunking_strategy": "function_based",
      "processing_method": "code_parser",
      "supports_metadata": true,
      "max_file_size_mb": 10
    }
  ],
  "total_formats": 39,
  "categories": [
    "Text & Documentation",
    "Office Documents",
    "Structured Data",
    "XML Family",
    "Code & Scripts",
    "Web & Markup",
    "Configuration",
    "Email"
  ]
}
```

---

### **GET /api/v1/training/processing-stats**
Get comprehensive document processing statistics.

#### **Response**
```json
{
  "overview": {
    "total_files": 342,
    "total_chunks": 8756,
    "total_size_mb": 245.7,
    "indexed_files": 338,
    "pending_files": 4
  },
  "file_formats": {
    "xml": 45,
    "pdf": 67,
    "txt": 89,
    "py": 23,
    "json": 34,
    "md": 56,
    "others": 28
  },
  "document_categories": {
    "help_docs": 123,
    "xml_config": 67,
    "code_script": 45,
    "api_docs": 34,
    "qa_faq": 29,
    "others": 44
  },
  "processing_status": {
    "completed": 338,
    "pending": 3,
    "processing": 1,
    "failed": 0
  },
  "performance": {
    "avg_processing_time_ms": 1234.5,
    "avg_chunks_per_file": 25.6,
    "success_rate_percent": 99.7
  },
  "recent_activity": {
    "last_upload": "2025-07-05T10:25:30.123456",
    "uploads_last_24h": 12,
    "processing_queue_size": 1
  }
}
```

---

## 🤖 Chat & Generation APIs

### **POST /api/v1/chat/**
Intelligent chat with context-aware responses and citations.

#### **Request**
```http
POST /api/v1/chat/
Content-Type: application/json

{
  "message": "Wie erstelle ich einen XML Stream für tägliche Batch-Verarbeitung?",
  "session_id": "session_abc123",
  "include_sources": true,
  "max_tokens": 1000
}
```

#### **Parameters**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | string | ✅ | - | User message/question |
| `session_id` | string | ❌ | auto | Session ID for conversation context |
| `include_sources` | boolean | ❌ | true | Include source citations |
| `max_tokens` | integer | ❌ | 1000 | Maximum response length |

#### **Response**
```json
{
  "response": "Um einen XML Stream für tägliche Batch-Verarbeitung zu erstellen, benötigen Sie eine StreamWorks-Konfigurationsdatei...",
  "sources": [
    {
      "id": "ref_1",
      "title": "StreamWorks XML Configuration Guide",
      "source_type": "xml_config",
      "source_path": "config/stream_template.xml",
      "excerpt": "<stream name=\"DailyBatch\" schedule=\"0 2 * * *\">...",
      "relevance_score": 0.95,
      "display_name": "📚 StreamWorks Help - XML Configuration Guide",
      "icon": "📚"
    }
  ],
  "conversation_id": "conv_456def789",
  "session_id": "session_abc123",
  "response_metadata": {
    "intent_detected": "xml_generation",
    "strategy_used": "filtered",
    "sources_used": 3,
    "response_time_ms": 2345.7,
    "token_count": 467
  },
  "suggestions": [
    "Möchten Sie ein konkretes XML-Template erstellen?",
    "Benötigen Sie Hilfe bei der Zeitplan-Konfiguration?",
    "Soll ich Ihnen Fehlerbehandlung-Optionen zeigen?"
  ]
}
```

---

### **POST /api/v1/streams/generate-stream**
Generate XML stream configuration based on parameters.

#### **Request**
```http
POST /api/v1/streams/generate-stream
Content-Type: application/json

{
  "stream_name": "DailyProcessing",
  "job_name": "ProcessData",
  "data_source": "/data/input",
  "output_path": "/data/output", 
  "schedule": "daily",
  "processing_type": "batch",
  "parameters": {
    "timeout": 3600,
    "retry_count": 3,
    "notification_email": "admin@company.com"
  }
}
```

#### **Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `stream_name` | string | ✅ | Name of the stream |
| `job_name` | string | ✅ | Name of the job |
| `data_source` | string | ✅ | Input data path |
| `output_path` | string | ✅ | Output data path |
| `schedule` | string | ✅ | Schedule type or cron expression |
| `processing_type` | string | ❌ | Processing type (batch/realtime) |
| `parameters` | object | ❌ | Additional configuration parameters |

#### **Response**
```json
{
  "xml_content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<stream name=\"DailyProcessing\" xmlns=\"http://streamworks.com/schema\">\n  <job name=\"ProcessData\">\n    <source path=\"/data/input\"/>\n    <target path=\"/data/output\"/>\n    <schedule>0 2 * * *</schedule>\n    <parameters>\n      <timeout>3600</timeout>\n      <retry_count>3</retry_count>\n      <notification_email>admin@company.com</notification_email>\n    </parameters>\n  </job>\n</stream>",
  "template_used": "batch_processing_template",
  "validation_result": {
    "valid": true,
    "warnings": [],
    "suggestions": [
      "Consider adding error handling configuration",
      "Add monitoring configuration for production use"
    ]
  },
  "metadata": {
    "generated_at": "2025-07-05T10:30:45.123456",
    "template_version": "2.0",
    "estimated_complexity": "intermediate"
  }
}
```

---

### **POST /api/v1/xml/validate**
Validate XML content against StreamWorks schema.

#### **Request**
```http
POST /api/v1/xml/validate
Content-Type: application/json

{
  "xml_content": "<?xml version=\"1.0\"?><stream name=\"test\">...</stream>",
  "schema_type": "stream_configuration",
  "strict_validation": true
}
```

#### **Response**
```json
{
  "valid": false,
  "errors": [
    {
      "line": 5,
      "column": 23,
      "message": "Missing required attribute 'version'",
      "severity": "error",
      "element": "stream"
    }
  ],
  "warnings": [
    {
      "line": 8,
      "column": 15,
      "message": "Deprecated element 'old_parameter'",
      "severity": "warning",
      "suggestion": "Use 'new_parameter' instead"
    }
  ],
  "schema_version": "2.0",
  "validation_time_ms": 45.7
}
```

---

## 🏥 Health & Monitoring APIs

### **GET /api/v1/health**
Overall system health check.

#### **Response**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-05T10:30:45.123456",
  "version": "2.0.0",
  "uptime_seconds": 86400,
  "components": {
    "database": "healthy",
    "vector_db": "healthy", 
    "llm_service": "healthy",
    "cache": "healthy",
    "disk_space": "healthy"
  },
  "performance": {
    "avg_response_time_ms": 187.5,
    "requests_per_minute": 45,
    "error_rate_percent": 0.02
  }
}
```

---

### **GET /api/v1/search/smart/health**
Smart search system health check.

#### **Response**
```json
{
  "status": "healthy",
  "smart_search_available": true,
  "query_classifier_working": true,
  "total_searches_performed": 1247,
  "average_response_time_ms": 125.7,
  "available_strategies": 5,
  "features": {
    "query_classification": true,
    "intent_detection": true,
    "complexity_assessment": true,
    "automatic_strategy_selection": true,
    "advanced_filtering": true,
    "performance_tracking": true
  },
  "timestamp": "2025-07-05T10:30:45.123456"
}
```

---

### **GET /metrics**
Prometheus metrics endpoint.

#### **Response**
```
# HELP search_requests_total Total number of search requests
# TYPE search_requests_total counter
search_requests_total{strategy="semantic_only",intent="general_info",status="success"} 456

# HELP search_duration_seconds Time spent on search requests
# TYPE search_duration_seconds histogram
search_duration_seconds_bucket{strategy="semantic_only",intent="general_info",le="0.01"} 12
search_duration_seconds_bucket{strategy="semantic_only",intent="general_info",le="0.05"} 45
search_duration_seconds_bucket{strategy="semantic_only",intent="general_info",le="0.1"} 123

# HELP vector_db_documents_total Number of documents in vector database
# TYPE vector_db_documents_total gauge
vector_db_documents_total 8756

# HELP errors_total Total number of errors
# TYPE errors_total counter
errors_total{error_type="search_timeout",service="smart_search"} 3
```

---

## ❌ Error Handling

### **Error Response Format**

All API errors follow a consistent structure:

```json
{
  "error": {
    "code": "E4001",
    "type": "INVALID_QUERY",
    "message": "Query is invalid or empty",
    "details": "Query must be between 1 and 1000 characters",
    "timestamp": "2025-07-05T10:30:45.123456",
    "request_id": "req_abc123def456",
    "retryable": false
  }
}
```

### **Error Codes**

#### **Client Errors (400-499)**
| Code | Type | Status | Description | Retryable |
|------|------|--------|-------------|-----------|
| E4001 | INVALID_QUERY | 400 | Query is invalid or empty | ❌ |
| E4002 | QUERY_TOO_LONG | 400 | Query exceeds maximum length | ❌ |
| E4003 | INVALID_FILTER | 400 | Filter parameters are invalid | ❌ |
| E4004 | FILE_TOO_LARGE | 400 | Uploaded file exceeds size limit | ❌ |
| E4005 | UNSUPPORTED_FORMAT | 400 | File format not supported | ❌ |
| E4029 | RATE_LIMIT_EXCEEDED | 429 | Too many requests | ✅ |

#### **Server Errors (500-599)**
| Code | Type | Status | Description | Retryable |
|------|------|--------|-------------|-----------|
| E5001 | SEARCH_SERVICE_ERROR | 500 | Search service unavailable | ✅ (30s) |
| E5002 | LLM_SERVICE_ERROR | 500 | Language model unavailable | ✅ (60s) |
| E5003 | VECTOR_DB_ERROR | 500 | Vector database connection failed | ✅ (15s) |
| E5004 | PROCESSING_ERROR | 500 | Document processing failed | ✅ (30s) |
| E5000 | UNKNOWN_ERROR | 500 | Unknown error occurred | ❌ |

### **Circuit Breaker Responses**

When services are temporarily unavailable:

```json
{
  "error": {
    "code": "E5001",
    "type": "SEARCH_SERVICE_ERROR",
    "message": "Search service temporarily unavailable due to circuit breaker",
    "details": "Service will be retried automatically in 30 seconds",
    "timestamp": "2025-07-05T10:30:45.123456",
    "retryable": true,
    "retry_after_seconds": 30,
    "circuit_breaker_state": "OPEN"
  }
}
```

---

## 🚦 Rate Limiting

### **Rate Limits by Endpoint**

| Endpoint | Rate Limit | Burst | Window |
|----------|------------|-------|---------|
| `/api/v1/search/*` | 30/min | 5 | Per IP |
| `/api/v1/training/upload-file` | 10/min | 2 | Per IP |
| `/api/v1/training/batch-upload` | 5/min | 1 | Per IP |
| `/api/v1/chat/` | 20/min | 3 | Per IP |
| `/api/v1/streams/generate-stream` | 15/min | 2 | Per IP |

### **Rate Limit Headers**

```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1625097600
X-RateLimit-Window: 60
```

### **Rate Limit Exceeded Response**

```json
{
  "error": {
    "code": "E4029",
    "type": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": "Maximum 30 requests per minute allowed",
    "retry_after_seconds": 45,
    "limit": 30,
    "window_seconds": 60
  }
}
```

---

## 📚 Examples & Tutorials

### **Example 1: Basic Smart Search**

```javascript
// JavaScript/TypeScript example
const searchQuery = async (query) => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/search/smart', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        top_k: 5,
        include_analysis: true
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Search results:', data.results);
    console.log('Strategy used:', data.search_strategy);
    
    return data;
  } catch (error) {
    console.error('Search failed:', error);
    throw error;
  }
};

// Usage
searchQuery("How to create XML stream configuration?")
  .then(results => {
    results.results.forEach((result, index) => {
      console.log(`Result ${index + 1}:`, result.content.substring(0, 100));
      console.log('Relevance factors:', result.relevance_factors);
    });
  });
```

### **Example 2: Advanced Search with Filters**

```python
# Python example
import requests
import json

def advanced_search(query, filters=None):
    url = "http://localhost:8000/api/v1/search/advanced"
    
    payload = {
        "query": query,
        "top_k": 10,
        "include_analysis": True
    }
    
    if filters:
        payload["filters"] = filters
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage with filters
filters = {
    "document_types": ["xml_config", "help_docs"],
    "file_formats": ["xml", "txt"],
    "complexity_min": 3,
    "complexity_max": 7
}

results = advanced_search(
    "StreamWorks batch processing configuration",
    filters=filters
)

if results:
    print(f"Found {results['total_results']} results")
    print(f"Strategy: {results['search_strategy']}")
    
    for result in results['results']:
        print(f"\nContent: {result['content'][:100]}...")
        print(f"Score: {result['score']:.3f}")
        print(f"Format: {result['metadata']['file_format']}")
```

### **Example 3: File Upload and Processing**

```python
# Python file upload example
import requests
from pathlib import Path

def upload_document(file_path, source_category="Testdaten"):
    url = "http://localhost:8000/api/v1/training/upload-file"
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'rb') as file:
        files = {'file': (file_path.name, file, 'application/octet-stream')}
        data = {'source_category': source_category}
        
        try:
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Upload failed: {e}")
            return None

# Usage
result = upload_document("./documents/streamworks_guide.pdf", "StreamWorks Hilfe")

if result and result['success']:
    print(f"Upload successful!")
    print(f"File ID: {result['file_id']}")
    print(f"Format detected: {result['processing_result']['file_format']}")
    print(f"Chunks created: {result['processing_result']['chunk_count']}")
    print(f"Processing time: {result['processing_time_ms']:.1f}ms")
else:
    print("Upload failed")
```

### **Example 4: Chat Conversation**

```javascript
// JavaScript chat example
class StreamWorksChat {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = this.generateSessionId();
  }

  generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9);
  }

  async sendMessage(message, includeSources = true) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: this.sessionId,
          include_sources: includeSources,
          max_tokens: 1000
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Chat request failed:', error);
      throw error;
    }
  }

  formatResponse(response) {
    let formatted = `🤖 StreamWorks-KI: ${response.response}\n\n`;
    
    if (response.sources && response.sources.length > 0) {
      formatted += "📚 Quellen:\n";
      response.sources.forEach((source, index) => {
        formatted += `${index + 1}. ${source.display_name}\n`;
        formatted += `   📁 ${source.source_path}\n`;
        formatted += `   📝 ${source.excerpt.substring(0, 100)}...\n\n`;
      });
    }

    if (response.suggestions && response.suggestions.length > 0) {
      formatted += "💡 Vorschläge:\n";
      response.suggestions.forEach((suggestion, index) => {
        formatted += `${index + 1}. ${suggestion}\n`;
      });
    }

    return formatted;
  }
}

// Usage
const chat = new StreamWorksChat();

async function chatExample() {
  try {
    const response = await chat.sendMessage(
      "Wie konfiguriere ich einen XML Stream für tägliche Batch-Verarbeitung?"
    );
    
    console.log(chat.formatResponse(response));
    console.log(`\n📊 Metadata:`);
    console.log(`Intent: ${response.response_metadata.intent_detected}`);
    console.log(`Strategy: ${response.response_metadata.strategy_used}`);
    console.log(`Response time: ${response.response_metadata.response_time_ms}ms`);
    
  } catch (error) {
    console.error('Chat failed:', error);
  }
}

chatExample();
```

### **Example 5: XML Stream Generation**

```python
# Python XML generation example
import requests
import json

def generate_xml_stream(stream_config):
    url = "http://localhost:8000/api/v1/streams/generate-stream"
    
    try:
        response = requests.post(url, json=stream_config)
        response.raise_for_status()
        
        result = response.json()
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"XML generation failed: {e}")
        return None

# Configuration for daily batch processing
config = {
    "stream_name": "DailyDataProcessing",
    "job_name": "ProcessCustomerData",
    "data_source": "/data/input/customers",
    "output_path": "/data/output/processed",
    "schedule": "daily",
    "processing_type": "batch",
    "parameters": {
        "timeout": 7200,  # 2 hours
        "retry_count": 3,
        "notification_email": "dataops@company.com",
        "batch_size": 1000,
        "parallel_workers": 4
    }
}

# Generate XML
result = generate_xml_stream(config)

if result:
    print("✅ XML Stream generated successfully!")
    print(f"Template used: {result['template_used']}")
    print(f"Validation: {'✅ Valid' if result['validation_result']['valid'] else '❌ Invalid'}")
    
    # Save XML to file
    with open(f"{config['stream_name']}.xml", 'w', encoding='utf-8') as f:
        f.write(result['xml_content'])
    
    print(f"XML saved to {config['stream_name']}.xml")
    
    if result['validation_result']['suggestions']:
        print("\n💡 Suggestions:")
        for suggestion in result['validation_result']['suggestions']:
            print(f"- {suggestion}")
else:
    print("❌ XML generation failed")
```

---

## 🔄 API Versioning

The API uses URL path versioning:
- **Current version**: `v1`
- **Base path**: `/api/v1/`
- **Deprecation policy**: 6 months notice before removing versions
- **Migration guide**: Available in documentation for version changes

---

## 🌐 CORS Policy

```javascript
// Allowed origins
const allowedOrigins = [
  "http://localhost:3000",      // Development
  "https://streamworks-ki.com", // Production
];

// Allowed methods
const allowedMethods = ["GET", "POST", "PUT", "DELETE"];

// Allowed headers
const allowedHeaders = ["Content-Type", "Authorization", "X-API-Key"];
```

---

## 📞 Support

For API support and questions:
- **Documentation**: http://localhost:8000/docs (Swagger UI)
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/api/v1/health
- **Metrics**: http://localhost:8000/metrics

---

**Last Updated**: 2025-07-05  
**Version**: 2.0+  
**Status**: Production Ready