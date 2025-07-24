# 📁 Document Management Features

## Feature Overview & Purpose

The StreamWorks-KI Document Management System provides enterprise-grade document processing, storage, and organization capabilities. It supports multiple file formats, implements intelligent document conversion, and maintains comprehensive metadata for efficient retrieval and analysis.

### Key Capabilities
- **Multi-Format Support**: PDF, TXT, MD, JSON, XML, DOCX, XLSX processing
- **PostgreSQL Storage**: Enterprise database with full ACID compliance
- **Intelligent Conversion**: Document-to-Markdown transformation with metadata preservation
- **Hierarchical Organization**: Categories → Folders → Files structure
- **Batch Processing**: Concurrent document processing with progress tracking
- **Search & Filter**: Full-text search with advanced filtering capabilities

## Technical Implementation Details

### Architecture Overview
```
File Upload → Validation → Processing → Storage → Indexing → Search
```

### Core Components

#### 1. Document Service (`app/services/document_service.py`)
- **Primary Service**: Core document processing and conversion engine
- **PostgreSQL Integration**: Async database operations with SQLAlchemy 2.0
- **Conversion Pipeline**: PDF/TXT to Markdown with metadata extraction
- **Background Processing**: Async task management for large files

#### 2. Enterprise File Manager (`app/services/enterprise_file_manager.py`)
- **File Operations**: Upload, download, delete, move operations
- **Storage Management**: Unified storage system with path abstraction
- **Metadata Tracking**: Comprehensive file information and statistics
- **Security Validation**: MIME type checking and file size limits

#### 3. Multi-Format Processor (`app/services/multi_format_processor.py`)
- **Format Detection**: Automatic file type identification
- **Conversion Engine**: Specialized processors for each format
- **Content Extraction**: Text extraction with structure preservation
- **Error Recovery**: Graceful handling of corrupted or invalid files

### Database Schema

#### Document Table Structure
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_format VARCHAR(10) NOT NULL,
    file_size BIGINT NOT NULL,
    file_path TEXT NOT NULL,
    converted_content TEXT,
    metadata JSONB,
    category_id INTEGER REFERENCES categories(id),
    folder_id INTEGER REFERENCES folders(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_status VARCHAR(20) DEFAULT 'pending',
    conversion_log TEXT
);
```

#### Categories and Folders
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    parent_folder_id INTEGER REFERENCES folders(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, category_id, parent_folder_id)
);
```

### Processing Pipeline

#### Document Conversion Flow
```python
async def convert_document(file_path: str, content: bytes) -> ConversionResult:
    # 1. Format detection
    file_format = detect_format(file_path, content)
    
    # 2. Content extraction
    if file_format == 'pdf':
        text_content = extract_pdf_text(content)
    elif file_format == 'docx':
        text_content = extract_docx_text(content)
    
    # 3. Markdown conversion
    markdown_content = convert_to_markdown(text_content)
    
    # 4. Metadata extraction
    metadata = extract_metadata(content, file_format)
    
    # 5. Database logging
    await log_conversion_performance(file_path, processing_time, metadata)
    
    return ConversionResult(
        content=markdown_content,
        metadata=metadata,
        processing_time=processing_time
    )
```

#### Batch Processing Implementation
```python
async def process_batch(file_list: List[FileInfo]) -> BatchResult:
    semaphore = asyncio.Semaphore(5)  # Limit concurrent processing
    
    async def process_single(file_info: FileInfo):
        async with semaphore:
            return await convert_document(file_info.path, file_info.content)
    
    # Process files concurrently
    tasks = [process_single(file) for file in file_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return BatchResult(
        successful=len([r for r in results if not isinstance(r, Exception)]),
        failed=len([r for r in results if isinstance(r, Exception)]),
        results=results
    )
```

## API Endpoints

### Document Upload

#### `POST /api/v1/documents/upload`
**Purpose**: Upload and process single document

**Request Body** (multipart/form-data):
```
file: <binary_file_data>
category_id: integer
folder_id: integer (optional)
```

**Response**:
```json
{
  "id": 123,
  "filename": "document.pdf",
  "original_format": "pdf",
  "file_size": 2048576,
  "processing_status": "completed",
  "converted_content": "# Document Title\n\nContent...",
  "metadata": {
    "pages": 15,
    "author": "StreamWorks Team",
    "creation_date": "2025-01-23T10:00:00Z"
  },
  "processing_time": 3.2
}
```

#### `POST /api/v1/documents/batch-upload`
**Purpose**: Upload multiple documents for batch processing

**Request Body** (multipart/form-data):
```
files[]: <multiple_binary_files>
category_id: integer
folder_id: integer (optional)
```

**Response**:
```json
{
  "batch_id": "batch_20250123_140532",
  "total_files": 25,
  "successful": 23,
  "failed": 2,
  "processing_time": 45.7,
  "results": [
    {
      "filename": "doc1.pdf",
      "status": "success",
      "document_id": 124
    },
    {
      "filename": "doc2.pdf",
      "status": "error",
      "error": "Corrupted PDF file"
    }
  ]
}
```

### Document Retrieval

#### `GET /api/v1/documents/{document_id}`
**Purpose**: Retrieve specific document details

**Response**:
```json
{
  "id": 123,
  "filename": "document.pdf",
  "original_format": "pdf",
  "file_size": 2048576,
  "file_path": "/storage/documents/2025/01/document.pdf",
  "converted_content": "# Document Title\n\nContent...",
  "metadata": {...},
  "category": {
    "id": 1,
    "name": "Technical Documentation"
  },
  "folder": {
    "id": 5,
    "name": "User Guides"
  },
  "created_at": "2025-01-23T10:00:00Z",
  "updated_at": "2025-01-23T10:03:15Z"
}
```

#### `GET /api/v1/documents/search`
**Purpose**: Search documents with filters

**Query Parameters**:
- `q`: Search query (full-text search)
- `category_id`: Filter by category
- `folder_id`: Filter by folder
- `format`: Filter by file format
- `limit`: Results per page (default: 20)
- `offset`: Pagination offset

**Response**:
```json
{
  "total": 156,
  "limit": 20,
  "offset": 0,
  "documents": [
    {
      "id": 123,
      "filename": "document.pdf",
      "snippet": "...relevant text excerpt...",
      "relevance_score": 0.92,
      "metadata": {...}
    }
  ]
}
```

### Category & Folder Management

#### `POST /api/v1/categories`
**Purpose**: Create new document category

**Request Body**:
```json
{
  "name": "Technical Documentation",
  "description": "All technical documentation and guides"
}
```

#### `POST /api/v1/folders`
**Purpose**: Create new folder within category

**Request Body**:
```json
{
  "name": "User Guides",
  "category_id": 1,
  "parent_folder_id": null
}
```

#### `GET /api/v1/categories/{category_id}/structure`
**Purpose**: Get hierarchical folder structure

**Response**:
```json
{
  "category": {
    "id": 1,
    "name": "Technical Documentation"
  },
  "folders": [
    {
      "id": 5,
      "name": "User Guides",
      "document_count": 23,
      "subfolders": [
        {
          "id": 8,
          "name": "Advanced Features",
          "document_count": 7
        }
      ]
    }
  ],
  "total_documents": 156
}
```

## Configuration Options

### File Processing Settings

#### Upload Limits
```bash
# File size limits
MAX_FILE_SIZE_MB=50
MAX_BATCH_SIZE=25
MAX_CONCURRENT_UPLOADS=5

# Supported formats
ALLOWED_FORMATS="pdf,txt,md,json,xml,docx,xlsx"
MIME_TYPE_VALIDATION=true
```

#### Storage Configuration
```bash
# Storage paths
STORAGE_ROOT="/data/storage"
DOCUMENTS_PATH="/data/storage/documents"
CONVERTED_PATH="/data/storage/converted"
TEMP_PATH="/data/storage/temp"

# File organization
ORGANIZE_BY_DATE=true
DATE_FORMAT="YYYY/MM"
PRESERVE_ORIGINAL=true
```

### Database Settings

#### PostgreSQL Configuration
```bash
# Connection settings
DATABASE_URL="postgresql://user:pass@localhost:5432/streamworks_ki"
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30

# Performance tuning
DB_STATEMENT_TIMEOUT=60000
DB_LOCK_TIMEOUT=30000
DB_QUERY_CACHE=true
```

#### Indexing Configuration
```sql
-- Full-text search index
CREATE INDEX idx_documents_content_fts 
ON documents USING gin(to_tsvector('german', converted_content));

-- Metadata search index
CREATE INDEX idx_documents_metadata_gin 
ON documents USING gin(metadata);

-- Category/Folder indexes
CREATE INDEX idx_documents_category_folder 
ON documents(category_id, folder_id);
```

### Processing Pipeline Settings

#### Conversion Parameters
```bash
# PDF processing
PDF_MAX_PAGES=500
PDF_OCR_ENABLED=false
PDF_IMAGE_EXTRACTION=true

# Document formatting
MARKDOWN_PRESERVE_FORMATTING=true
MARKDOWN_INCLUDE_METADATA=true
MARKDOWN_MAX_LINE_LENGTH=120

# Content cleaning
REMOVE_HEADERS_FOOTERS=true
NORMALIZE_WHITESPACE=true
EXTRACT_LINKS=true
```

## Performance Characteristics

### Processing Performance
- **Single Document**: 2-5 seconds average
- **Batch Processing** (25 files): 30-60 seconds
- **Concurrent Limit**: 5 simultaneous conversions
- **Memory Usage**: 200-500MB per conversion

### Storage Efficiency
- **Compression Ratio**: 60-80% for converted content
- **Metadata Overhead**: <5% of total storage
- **Index Size**: 15-20% of document content size
- **Query Performance**: <200ms for most searches

### Scalability Metrics
- **Document Capacity**: 100,000+ documents
- **Concurrent Users**: 50+ simultaneous operations
- **Search Performance**: Sub-second response times
- **Storage Growth**: Linear with document count

## Troubleshooting Guide

### Common Issues

#### 1. File Upload Failures
**Symptoms**: Upload timeouts or rejection errors
**Causes**:
- File size exceeds limits
- Unsupported file format
- Corrupted file data
- Network connectivity issues

**Solutions**:
```bash
# Check file size and format
ls -lh document.pdf
file document.pdf

# Verify API endpoint
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@document.pdf" \
  -F "category_id=1"

# Check server logs
docker logs streamworks-ki-backend | grep -i upload
```

#### 2. Conversion Errors
**Symptoms**: Documents fail to convert to Markdown
**Causes**:
- Corrupted or password-protected files
- Unsupported PDF features
- Memory limitations
- Missing dependencies

**Solutions**:
```bash
# Test PDF manually
python -c "
import pypdf
with open('document.pdf', 'rb') as f:
    reader = pypdf.PdfReader(f)
    print(f'Pages: {len(reader.pages)}')
"

# Check conversion logs
tail -f backend/data/conversion.log

# Verify storage space
df -h /data/storage
```

#### 3. Search Performance Issues
**Symptoms**: Slow document search responses
**Causes**:
- Missing database indexes
- Large result sets
- Complex query patterns
- Database connection limits

**Solutions**:
```sql
-- Check index usage
EXPLAIN ANALYZE SELECT * FROM documents 
WHERE to_tsvector('german', converted_content) @@ plainto_tsquery('StreamWorks');

-- Rebuild indexes if needed
REINDEX INDEX idx_documents_content_fts;

-- Optimize database
VACUUM ANALYZE documents;
```

#### 4. Storage Space Issues
**Symptoms**: Disk space warnings or upload failures
**Causes**:
- Accumulated temporary files
- Large document collections
- Insufficient cleanup

**Solutions**:
```bash
# Check storage usage
du -sh /data/storage/*

# Clean temporary files
find /data/storage/temp -type f -mtime +1 -delete

# Archive old documents
python backend/scripts/admin/archive_old_documents.py --days 365
```

### Debug Mode

#### Enable Document Processing Debug
```bash
export LOG_LEVEL=DEBUG
export DOCUMENT_DEBUG_MODE=true
export SAVE_CONVERSION_INTERMEDIATES=true
```

#### Debug Specific Conversions
```python
# Test document conversion
from app.services.document_service import document_service

# Enable debug output
document_service.debug = True

# Test conversion
with open('test.pdf', 'rb') as f:
    result = await document_service.convert_pdf_to_markdown(
        'test.pdf', f.read()
    )
    print(f"Conversion result: {result}")
```

### Performance Monitoring

#### Key Metrics to Track
- Document processing queue length
- Conversion success/failure rates
- Storage utilization trends
- Search query performance
- Database connection pool usage

#### Monitoring Commands
```bash
# Processing statistics
curl -X GET "http://localhost:8000/api/v1/documents/stats"

# Storage metrics
curl -X GET "http://localhost:8000/api/v1/system/storage"

# Database performance
curl -X GET "http://localhost:8000/api/v1/system/database"
```

## Future Enhancement Ideas

### Short-term Improvements (1-3 months)
1. **Enhanced OCR**: Text extraction from scanned PDFs and images
2. **Version Control**: Document versioning with diff tracking
3. **Duplicate Detection**: Automatic identification of duplicate documents
4. **Advanced Metadata**: Automatic tagging and classification

### Medium-term Enhancements (3-6 months)
1. **Document Relationships**: Link detection and graph visualization
2. **Collaborative Features**: Comments, annotations, and sharing
3. **Workflow Integration**: Approval processes and status tracking
4. **Advanced Search**: Semantic search with embedding-based similarity

### Long-term Vision (6+ months)
1. **AI-Powered Processing**: 
   - Automatic summarization
   - Key information extraction
   - Content categorization
2. **Integration Ecosystem**:
   - SharePoint/Google Drive sync
   - Email attachment processing
   - API webhooks for external systems
3. **Enterprise Features**:
   - Multi-tenant support
   - Advanced permissions
   - Audit logging and compliance

### Technical Roadmap

#### Infrastructure Improvements
- **Distributed Storage**: Object storage (S3/MinIO) integration
- **CDN Integration**: Fast document delivery worldwide
- **Microservices**: Split processing into specialized services
- **Event Streaming**: Real-time document processing events

#### AI/ML Enhancements
- **Smart Classification**: ML-based document categorization
- **Content Analysis**: Entity extraction and sentiment analysis
- **Recommendation Engine**: Suggest related documents
- **Quality Scoring**: Automatic document quality assessment

---

**Last Updated**: 2025-01-23  
**Version**: 2.0.0  
**Maintainer**: StreamWorks-KI Development Team  
**Related Documents**: [API Reference](api_reference.md), [Q&A System](qa_system.md)