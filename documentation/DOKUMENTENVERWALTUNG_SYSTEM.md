# Dokumentenverwaltung System

> **Enterprise Document Management für das Streamworks-KI System**
> Umfassende Dokumentenverwaltung mit automatischer Verarbeitung, RAG-Integration und Analytics

---

## 1. Überblick der Dokumentenverwaltung

### 1.1 Systemkonzept

Das Dokumentenverwaltungssystem von Streamworks-KI ist weit mehr als ein einfacher Datei-Upload. Es handelt sich um eine **intelligente Dokumentenplattform**, die automatisch hochgeladene Dokumente analysiert, verarbeitet und für die RAG-basierte Suche verfügbar macht.

**Kernfunktionalitäten:**
- **Automatische Dokumentenverarbeitung**: Upload → Analyse → Chunking → Embedding → RAG-Integration
- **Layout-aware Text-Extraktion**: Erhaltung der Dokumentstruktur bei PDF, Word, Markdown
- **Intelligente Ordnerstruktur**: Hierarchische Organisation mit Drag-and-Drop
- **Real-time Processing**: Live-Updates während der Dokumentenverarbeitung
- **Advanced Analytics**: Detaillierte Statistiken und Verarbeitungsmetriken
- **Bulk Operations**: Massenoperationen für Enterprise-Anforderungen

### 1.2 Integration in das Gesamtsystem

**Nahtlose RAG-Integration:**
- Hochgeladene Dokumente werden automatisch für das RAG-System verfügbar
- Benutzer können sofort nach Inhalten aus neuen Dokumenten suchen
- LangExtract-Sessions profitieren von aktuellem Dokumentenwissen

**Multi-Modal Document Support:**
- **PDF**: Layout-erhaltende Extraktion mit OCR-Fallback
- **Microsoft Office**: Word, Excel, PowerPoint Unterstützung
- **Text-basiert**: Markdown, Plain Text, Code-Dateien
- **Bilder**: OCR-basierte Textextraktion aus Screenshots und Scans

---

## 2. Backend-Architektur der Dokumentenverwaltung

### 2.1 Service-Layer Architecture

**Modularer Aufbau mit klaren Verantwortlichkeiten:**

```
backend/routers/documents/
├── crud.py                 # CRUD Operations (Create, Read, Update, Delete)
├── bulk_operations.py      # Massenoperationen für Enterprise-Use
├── analytics.py           # Statistiken und AI-Summaries
└── chunks.py              # Chunk-Management für RAG-System
```

**DocumentService als zentrale Orchestrierung:**
```python
class DocumentService:
    """
    Zentrale Orchestrierung aller Dokumentenoperationen
    Koordiniert Upload, Processing, Storage und Retrieval
    """

    def __init__(self):
        self.storage_service = FileStorageService()
        self.processor = DocumentProcessor()
        self.embedder = EmbeddingService()
        self.qdrant_client = QdrantClient()

    async def upload_document(self, file, folder_id, **metadata):
        # 1. File validation und security checks
        # 2. Unique filename generation mit collision handling
        # 3. Secure file storage mit hash verification
        # 4. Database record creation
        # 5. Asynchrone processing queue
        # 6. Progress tracking für UI feedback
```

### 2.2 Secure File Storage System

**Content-Addressed Storage:**
Das System verwendet eine **content-addressed storage** Strategie für optimale Speichernutzung und Sicherheit:

```python
def generate_storage_path(file_hash: str) -> Path:
    """
    Generiert sicheren Speicherpfad basierend auf File-Hash

    Beispiel: SHA256 'a1b2c3d4...' wird zu:
    storage/documents/a1/b2/a1b2c3d4_original_filename.pdf
    """
    prefix = file_hash[:2]
    subdir = file_hash[2:4]
    return Path(f"storage/documents/{prefix}/{subdir}/{file_hash}_{filename}")
```

**Vorteile dieses Ansatzes:**
- **Deduplication**: Identische Dateien werden nur einmal gespeichert
- **Integrity**: Hash-basierte Verifizierung gegen Korruption
- **Security**: Pfade sind nicht erratbar, keine directory traversal Angriffe
- **Scalability**: Gleichmäßige Verteilung über Unterverzeichnisse

### 2.3 Asynchrone Dokumentenverarbeitung

**Multi-Stage Processing Pipeline:**

```python
class DocumentProcessor:
    """
    Mehrstufige Dokumentenverarbeitung mit Fehlerbehandlung
    """

    async def process_document(self, document_id: str) -> ProcessingResult:
        """
        Vollständige Dokumentenverarbeitung in definierten Phasen
        """

        # Phase 1: Content Extraction
        try:
            content = await self._extract_content(document)
            await self._update_status(document_id, "extracting")
        except Exception as e:
            return await self._handle_processing_error(document_id, "extraction", e)

        # Phase 2: Layout-Aware Chunking
        try:
            chunks = await self._chunk_content(content, document.mime_type)
            await self._update_status(document_id, "chunking")
        except Exception as e:
            return await self._handle_processing_error(document_id, "chunking", e)

        # Phase 3: Embedding Generation
        try:
            embeddings = await self._generate_embeddings(chunks)
            await self._update_status(document_id, "embedding")
        except Exception as e:
            return await self._handle_processing_error(document_id, "embedding", e)

        # Phase 4: Vector Storage
        try:
            await self._store_in_qdrant(document_id, chunks, embeddings)
            await self._update_status(document_id, "ready")
        except Exception as e:
            return await self._handle_processing_error(document_id, "storage", e)

        return ProcessingResult(
            status="completed",
            chunk_count=len(chunks),
            processing_time=time.time() - start_time
        )
```

**Status-Tracking für Transparency:**
- **uploading**: File wird hochgeladen
- **uploaded**: File ist gespeichert, wartet auf Verarbeitung
- **extracting**: Text wird aus Dokument extrahiert
- **chunking**: Dokument wird in Chunks aufgeteilt
- **embedding**: Embeddings werden generiert
- **storing**: Chunks werden in Qdrant gespeichert
- **ready**: Dokument ist vollständig verarbeitet und suchbar
- **error**: Fehler in einem Verarbeitungsschritt

### 2.4 Advanced Content Extraction

**Multi-Engine Approach für optimale Textqualität:**

```python
class ContentExtractionEngine:
    """
    Mehrschichtiger Ansatz für verschiedene Dokumenttypen
    """

    def __init__(self):
        self.extractors = {
            'application/pdf': PDFExtractor(),
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': WordExtractor(),
            'text/markdown': MarkdownExtractor(),
            'text/plain': PlainTextExtractor(),
            'image/*': OCRExtractor()
        }

    async def extract_content(self, file_path: Path, mime_type: str) -> ExtractedContent:
        """
        Wählt optimalen Extractor basierend auf MIME-Type
        """

        # Primary extraction
        primary_extractor = self.extractors.get(mime_type)
        if primary_extractor:
            try:
                content = await primary_extractor.extract(file_path)
                return content
            except Exception as e:
                logger.warning(f"Primary extraction failed: {e}")

        # Fallback to OCR for any visual document
        if mime_type.startswith('image/') or mime_type == 'application/pdf':
            try:
                ocr_extractor = self.extractors['image/*']
                content = await ocr_extractor.extract(file_path)
                content.extraction_method = "ocr_fallback"
                return content
            except Exception as e:
                logger.error(f"OCR fallback failed: {e}")

        # Last resort: treat as binary and extract minimal metadata
        return ExtractedContent(
            text="",
            metadata={"extraction_method": "failed", "file_size": file_path.stat().st_size},
            error="Could not extract text content"
        )
```

**PDF-Specific Optimizations:**
```python
class PDFExtractor:
    """
    Spezialisierte PDF-Extraktion mit Layout-Erhaltung
    """

    async def extract(self, pdf_path: Path) -> ExtractedContent:
        """
        Multi-Layer PDF extraction für beste Qualität
        """

        # Layer 1: Modern PDF libraries (pdfplumber, PyMuPDF)
        try:
            content = await self._extract_with_pdfplumber(pdf_path)
            if self._is_high_quality_extraction(content):
                return content
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")

        # Layer 2: OCR für gescannte PDFs
        try:
            content = await self._extract_with_ocr(pdf_path)
            content.metadata["extraction_method"] = "ocr"
            return content
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")

        # Layer 3: Basic text extraction als Fallback
        return await self._basic_text_extraction(pdf_path)

    def _is_high_quality_extraction(self, content: ExtractedContent) -> bool:
        """
        Qualitätsbewertung der Extraktion
        """
        text = content.text

        # Heuristiken für gute Extraktion:
        # - Mindestens 100 Zeichen
        # - Weniger als 50% Sonderzeichen
        # - Erkennbare Wortstrukturen

        if len(text) < 100:
            return False

        # Anteil an Buchstaben und Zahlen
        alphanumeric_ratio = sum(c.isalnum() or c.isspace() for c in text) / len(text)

        return alphanumeric_ratio > 0.5
```

---

## 3. Frontend-Komponenten der Dokumentenverwaltung

### 3.1 DocumentManager - Hauptkomponente

**Enterprise-Grade User Interface:**

Die `DocumentManager` Komponente bildet das Herzstück der Dokumentenverwaltung und kombiniert mehrere spezialisierte Sub-Komponenten zu einer kohärenten Benutzeroberfläche.

**Hauptfeatures:**
- **Dual-Panel Layout**: Ordnerstruktur links, Dokumentenliste rechts
- **Drag & Drop**: Intuitive Datei- und Ordneroperationen
- **Real-time Updates**: Live-Status während Dokumentenverarbeitung
- **Bulk Selection**: Mehrfachauswahl für Massenoperationen
- **Advanced Search**: Volltextsuche über alle Dokumente
- **View Modes**: Grid- und Listenansicht mit verschiedenen Sortierungen

**Component Architecture:**
```typescript
interface DocumentManagerProps {
  defaultView?: 'global' | 'folder'  // Ansichtsmodus
}

export function DocumentManager({ defaultView }: DocumentManagerProps) {
  // State Management
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null)
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set())
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<DocumentSort>(DocumentSort.CREATED_DESC)

  // Real-time data hooks
  const { documents, isLoading: documentsLoading } = useDocuments({
    folderId: selectedFolderId,
    search: searchQuery,
    sort: sortBy
  })

  const { folders, createFolder, deleteFolder } = useFolders()

  // ... Component render logic
}
```

### 3.2 Spezialisierte UI-Komponenten

**FolderTree - Hierarchische Navigation:**
```typescript
interface FolderTreeProps {
  folders: Folder[]
  selectedFolderId: string | null
  onFolderSelect: (folderId: string | null) => void
  onFolderCreate: (parentId: string | null, name: string) => void
  onFolderDelete: (folderId: string) => void
}

function FolderTree({ folders, selectedFolderId, onFolderSelect }: FolderTreeProps) {
  // Rekursive Render-Logik für verschachtelte Ordner
  const renderFolderNode = (folder: Folder, level: number = 0) => (
    <div key={folder.id} style={{ marginLeft: `${level * 20}px` }}>
      <FolderNode
        folder={folder}
        isSelected={selectedFolderId === folder.id}
        onSelect={() => onFolderSelect(folder.id)}
        onContextMenu={(e) => showFolderContextMenu(e, folder)}
      />
      {folder.children?.map(child => renderFolderNode(child, level + 1))}
    </div>
  )

  return (
    <div className="folder-tree">
      {/* "Alle Dokumente" root option */}
      <FolderNode
        folder={{ id: null, name: "Alle Dokumente", path: "/" }}
        isSelected={selectedFolderId === null}
        onSelect={() => onFolderSelect(null)}
      />
      {folders.map(folder => renderFolderNode(folder))}
    </div>
  )
}
```

**DocumentGrid - Responsive Dokumentenanzeige:**
```typescript
interface DocumentGridProps {
  documents: Document[]
  viewMode: 'grid' | 'list'
  selectedIds: Set<string>
  onSelectionChange: (ids: Set<string>) => void
  onDocumentOpen: (document: Document) => void
}

function DocumentGrid({ documents, viewMode, selectedIds, onSelectionChange }: DocumentGridProps) {
  const handleDocumentClick = (document: Document, event: MouseEvent) => {
    if (event.ctrlKey || event.metaKey) {
      // Multi-select logic
      const newSelection = new Set(selectedIds)
      if (newSelection.has(document.id)) {
        newSelection.delete(document.id)
      } else {
        newSelection.add(document.id)
      }
      onSelectionChange(newSelection)
    } else {
      // Single select
      onSelectionChange(new Set([document.id]))
    }
  }

  if (viewMode === 'grid') {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {documents.map(document => (
          <DocumentCard
            key={document.id}
            document={document}
            isSelected={selectedIds.has(document.id)}
            onClick={(e) => handleDocumentClick(document, e)}
          />
        ))}
      </div>
    )
  } else {
    return (
      <DocumentTable
        documents={documents}
        selectedIds={selectedIds}
        onSelectionChange={onSelectionChange}
      />
    )
  }
}
```

### 3.3 Upload-System mit Progress-Tracking

**Professional Upload Modal:**
```typescript
interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  targetFolderId: string | null
  onUploadComplete: (documents: Document[]) => void
}

function UploadModal({ isOpen, onClose, targetFolderId, onUploadComplete }: UploadModalProps) {
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const handleFileDrop = (files: FileList) => {
    const newFiles: UploadFile[] = Array.from(files).map(file => ({
      id: generateId(),
      file,
      name: file.name,
      size: file.size,
      status: 'pending',
      progress: 0
    }))

    setUploadFiles(prev => [...prev, ...newFiles])
  }

  const startUpload = async () => {
    setIsUploading(true)

    for (const uploadFile of uploadFiles) {
      if (uploadFile.status !== 'pending') continue

      try {
        // Update status to uploading
        updateFileStatus(uploadFile.id, 'uploading', 0)

        // Create FormData
        const formData = new FormData()
        formData.append('file', uploadFile.file)

        // Upload with progress tracking
        const response = await apiService.post('/documents/upload', formData, {
          params: { folder_id: targetFolderId },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            updateFileStatus(uploadFile.id, 'uploading', progress)
          }
        })

        // Update to completed
        updateFileStatus(uploadFile.id, 'completed', 100)

      } catch (error) {
        updateFileStatus(uploadFile.id, 'error', 0, error.message)
      }
    }

    setIsUploading(false)
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="upload-modal">
        <DropZone onDrop={handleFileDrop} />
        <UploadFileList files={uploadFiles} />
        <UploadActions onStart={startUpload} isUploading={isUploading} />
      </div>
    </Modal>
  )
}
```

**Real-time Progress Updates:**
```typescript
function UploadFileList({ files }: { files: UploadFile[] }) {
  return (
    <div className="upload-file-list">
      {files.map(file => (
        <div key={file.id} className="upload-file-item">
          <div className="file-info">
            <span className="file-name">{file.name}</span>
            <span className="file-size">{formatFileSize(file.size)}</span>
          </div>

          <div className="upload-progress">
            {file.status === 'uploading' && (
              <ProgressBar progress={file.progress} />
            )}
            {file.status === 'completed' && (
              <CheckIcon className="w-5 h-5 text-green-500" />
            )}
            {file.status === 'error' && (
              <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
            )}
          </div>

          {file.error && (
            <div className="error-message text-red-600 text-sm">
              {file.error}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

---

## 4. Advanced Features und Enterprise-Funktionalitäten

### 4.1 Bulk Operations für Enterprise-Use

**Massenoperationen für Effizienz:**

Das System unterstützt umfangreiche Bulk-Operationen, die in Enterprise-Umgebungen essentiell sind:

```python
# backend/routers/documents/bulk_operations.py

@router.post("/bulk-delete")
async def bulk_delete_documents(request: BulkDeleteRequest):
    """
    Löscht mehrere Dokumente in einem Batch-Vorgang
    Optimiert für große Mengen mit Progress-Tracking
    """
    result = {
        "requested": len(request.document_ids),
        "deleted": [],
        "failed": [],
        "total_deleted": 0
    }

    for document_id in request.document_ids:
        try:
            success = await doc_service.delete_document(db, document_id)
            if success:
                result["deleted"].append(str(document_id))
            else:
                result["failed"].append({
                    "id": str(document_id),
                    "error": "Document not found"
                })
        except Exception as e:
            result["failed"].append({
                "id": str(document_id),
                "error": str(e)
            })

    result["total_deleted"] = len(result["deleted"])
    return result

@router.post("/bulk-move")
async def bulk_move_documents(request: BulkMoveRequest):
    """
    Verschiebt mehrere Dokumente in einen Zielordner
    Atomare Operation mit Rollback bei Fehlern
    """
    # Validiere Zielordner existiert
    target_folder = await folder_service.get_folder_by_id(db, request.target_folder_id)
    if not target_folder:
        raise HTTPException(400, "Target folder not found")

    # Transactional move operation
    async with db.begin():
        for document_id in request.document_ids:
            await doc_service.move_document(db, document_id, request.target_folder_id)

@router.post("/bulk-reprocess")
async def bulk_reprocess_documents(request: BulkReprocessRequest):
    """
    Startet Neuverarbeitung für mehrere Dokumente
    Nützlich nach Updates der Processing-Pipeline
    """
    results = {
        "reprocessed": [],
        "failed": [],
        "total_requested": len(request.document_ids)
    }

    for document_id in request.document_ids:
        try:
            # Reset document status
            await doc_service.reset_document_processing(db, document_id)

            # Queue for reprocessing
            await processing_queue.enqueue_document(document_id)

            results["reprocessed"].append(str(document_id))

        except Exception as e:
            results["failed"].append({
                "id": str(document_id),
                "error": str(e)
            })

    return results
```

### 4.2 Advanced Analytics und Monitoring

**Comprehensive Document Analytics:**

```python
# backend/routers/documents/analytics.py

@router.get("/stats/overview")
async def get_document_stats():
    """
    Umfassende Dokumentenstatistiken für Dashboard
    """
    stats = await db.execute("""
        SELECT
            COUNT(*) as total_documents,
            SUM(file_size) as total_size_bytes,
            AVG(file_size) as average_size_bytes,
            SUM(chunk_count) as total_chunks,
            AVG(chunk_count) as avg_chunks_per_doc,
            COUNT(CASE WHEN status = 'ready' THEN 1 END) as ready_documents,
            COUNT(CASE WHEN status = 'error' THEN 1 END) as failed_documents,
            COUNT(CASE WHEN created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as recent_uploads
        FROM documents
    """)

    return {
        "document_metrics": {
            "total_documents": stats.total_documents,
            "total_size_gb": stats.total_size_bytes / (1024**3),
            "average_size_mb": stats.average_size_bytes / (1024**2),
            "processing_success_rate": stats.ready_documents / stats.total_documents if stats.total_documents > 0 else 0
        },
        "chunk_metrics": {
            "total_chunks": stats.total_chunks,
            "average_chunks_per_document": stats.avg_chunks_per_doc,
            "estimated_embeddings": stats.total_chunks  # 1:1 ratio
        },
        "activity_metrics": {
            "recent_uploads_24h": stats.recent_uploads,
            "failed_processing": stats.failed_documents,
            "health_score": (stats.ready_documents / stats.total_documents) * 100 if stats.total_documents > 0 else 100
        }
    }

@router.get("/{document_id}/summary")
async def get_document_summary(document_id: UUID, force_refresh: bool = False):
    """
    KI-generierte Dokumentenzusammenfassung
    Cached für Performance, regenerierbar on-demand
    """

    # Check for cached summary
    if not force_refresh:
        cached_summary = await cache.get(f"doc_summary:{document_id}")
        if cached_summary:
            return {
                "summary": cached_summary,
                "cached": True,
                "generated_at": cached_summary.get("timestamp")
            }

    # Generate new summary
    document = await doc_service.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(404, "Document not found")

    # Get document chunks for summarization
    chunks = await doc_service.get_document_chunks(db, document_id)
    full_text = "\n".join([chunk.content for chunk in chunks])

    # Generate AI summary
    summary_result = await ai_summarizer.generate_summary(
        text=full_text,
        document_type=document.mime_type,
        max_length=500,
        focus_areas=["key_points", "technical_details", "actionable_items"]
    )

    # Cache result
    await cache.set(f"doc_summary:{document_id}", summary_result, ttl=3600)  # 1 hour

    return {
        "summary": summary_result,
        "cached": False,
        "generated_at": datetime.now().isoformat()
    }
```

### 4.3 Integration mit Supabase für Enhanced Analytics

**Erweiterte Analytics durch Supabase Mirror:**

```python
@router.get("/{document_id}/supabase-analytics")
async def get_document_supabase_analytics(document_id: UUID):
    """
    Detaillierte Dokumentenanalyse aus Supabase Mirror
    Ideal für UI-Debugging und erweiterte Metriken
    """

    try:
        from services.supabase_mirror_service import get_document_analytics

        analytics = await get_document_analytics(str(document_id))

        if analytics:
            return {
                "success": True,
                "document_id": str(document_id),
                "analytics": analytics,
                "ui_debug_info": {
                    "total_chunks": analytics.get("chunk_summary", {}).get("total_chunks", 0),
                    "total_words": analytics.get("chunk_summary", {}).get("total_words", 0),
                    "processing_engine": analytics.get("document_stats", {}).get("processing_engine", "unknown"),
                    "embedding_model": analytics.get("document_stats", {}).get("embedding_model", "unknown"),
                    "chunk_size_distribution": analytics.get("chunk_analysis", {}),
                    "processing_timeline": analytics.get("processing_stats", {})
                }
            }
        else:
            return {
                "success": False,
                "message": "No analytics data found - document may not be processed yet"
            }

    except ImportError:
        raise HTTPException(503, "Supabase mirror service not available")
```

---

## 5. Security und Compliance

### 5.1 File Security Measures

**Multi-Layer Security Approach:**

```python
class DocumentSecurityService:
    """
    Umfassende Sicherheitsmaßnahmen für Dokumentenverarbeitung
    """

    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain',
        'text/markdown',
        'image/png',
        'image/jpeg'
    }

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    async def validate_upload(self, file: UploadFile) -> ValidationResult:
        """
        Comprehensive file validation vor dem Upload
        """

        # 1. Size validation
        if file.size > self.MAX_FILE_SIZE:
            raise ValidationError(f"File too large: {file.size} bytes (max: {self.MAX_FILE_SIZE})")

        # 2. MIME type validation
        detected_mime = await self._detect_mime_type(file)
        if detected_mime not in self.ALLOWED_MIME_TYPES:
            raise ValidationError(f"File type not allowed: {detected_mime}")

        # 3. Content validation (malware scan)
        is_safe = await self._scan_for_malware(file)
        if not is_safe:
            raise SecurityError("File contains potentially malicious content")

        # 4. Filename sanitization
        safe_filename = self._sanitize_filename(file.filename)

        return ValidationResult(
            is_valid=True,
            safe_filename=safe_filename,
            detected_mime_type=detected_mime,
            sanitized=True
        )

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes filename gegen path traversal und injection
        """
        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')

        # Remove dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext

        return filename

    async def _scan_for_malware(self, file: UploadFile) -> bool:
        """
        Basic malware detection durch Content-Analyse
        """

        # Read first few bytes for magic number check
        file.seek(0)
        header = await file.read(1024)
        file.seek(0)

        # Check for known malicious patterns
        malicious_patterns = [
            b'MZ',  # PE executable header
            b'\x7fELF',  # Linux executable header
            b'#!/bin/sh',  # Shell script
            b'#!/bin/bash',  # Bash script
        ]

        for pattern in malicious_patterns:
            if header.startswith(pattern):
                return False

        # Additional checks für embedded scripts in PDFs
        if b'/JavaScript' in header or b'/JS' in header:
            return False

        return True
```

### 5.2 Access Control und Permissions

**Role-Based Document Access:**

```python
class DocumentPermissionService:
    """
    Granulare Berechtigungskontrolle für Dokumente
    """

    async def check_document_access(self,
                                  user_id: str,
                                  document_id: str,
                                  permission: DocumentPermission) -> bool:
        """
        Prüft ob User berechtigt ist, Operation auf Dokument auszuführen
        """

        # 1. Get user roles
        user_roles = await self.auth_service.get_user_roles(user_id)

        # 2. Admin has all permissions
        if 'ADMIN' in user_roles:
            return True

        # 3. Get document and folder permissions
        document = await self.doc_service.get_document_by_id(document_id)
        if not document:
            return False

        folder_permissions = await self.folder_service.get_folder_permissions(
            document.folder_id, user_id
        )

        # 4. Check specific permission
        return self._evaluate_permission(user_roles, folder_permissions, permission)

    def _evaluate_permission(self,
                           user_roles: List[str],
                           folder_permissions: List[str],
                           required_permission: DocumentPermission) -> bool:
        """
        Evaluiert Berechtigung basierend auf Rollen und Ordner-Permissions
        """

        permission_hierarchy = {
            DocumentPermission.VIEW: ['documents.read'],
            DocumentPermission.DOWNLOAD: ['documents.read', 'documents.download'],
            DocumentPermission.EDIT: ['documents.read', 'documents.edit'],
            DocumentPermission.DELETE: ['documents.read', 'documents.delete'],
            DocumentPermission.MANAGE: ['documents.*']
        }

        required_perms = permission_hierarchy[required_permission]

        # Check if user has any of the required permissions
        for perm in required_perms:
            if perm in folder_permissions:
                return True

            # Check wildcard permissions
            if perm.endswith('.*') and any(
                fp.startswith(perm[:-1]) for fp in folder_permissions
            ):
                return True

        return False
```

---

## 6. Performance-Optimierungen

### 6.1 Caching Strategies

**Multi-Level Caching für optimale Performance:**

```python
class DocumentCacheService:
    """
    Intelligentes Caching auf mehreren Ebenen
    """

    def __init__(self):
        self.redis_client = redis.Redis()
        self.memory_cache = {}
        self.file_cache = FileSystemCache()

    async def get_document_content(self, document_id: str) -> Optional[str]:
        """
        Hierarchisches Content-Caching
        """

        # Level 1: Memory Cache (fastest)
        if document_id in self.memory_cache:
            return self.memory_cache[document_id]

        # Level 2: Redis Cache (fast)
        cached_content = await self.redis_client.get(f"doc_content:{document_id}")
        if cached_content:
            content = cached_content.decode('utf-8')
            self.memory_cache[document_id] = content  # Promote to memory
            return content

        # Level 3: Database (slower)
        content = await self._fetch_from_database(document_id)
        if content:
            # Cache at all levels
            self.memory_cache[document_id] = content
            await self.redis_client.setex(f"doc_content:{document_id}", 3600, content)

        return content

    async def invalidate_document_cache(self, document_id: str):
        """
        Invalidiert Cache bei Dokumentenänderungen
        """
        # Clear all cache levels
        self.memory_cache.pop(document_id, None)
        await self.redis_client.delete(f"doc_content:{document_id}")
        await self.redis_client.delete(f"doc_metadata:{document_id}")
        await self.redis_client.delete(f"doc_summary:{document_id}")
```

### 6.2 Optimized Database Queries

**Efficient Data Retrieval:**

```python
class OptimizedDocumentQueries:
    """
    Optimierte Datenbankabfragen für große Dokumentenmengen
    """

    async def get_documents_with_pagination(self,
                                          folder_id: Optional[str] = None,
                                          search_query: Optional[str] = None,
                                          sort: DocumentSort = DocumentSort.CREATED_DESC,
                                          page: int = 1,
                                          per_page: int = 50) -> PaginatedDocuments:
        """
        Hochoptimierte Dokumentenabfrage mit Pagination
        """

        # Build dynamic query with proper indexing
        query = select(Document).options(
            selectinload(Document.folder),  # Eager loading für N+1 Problem
            selectinload(Document.tags)
        )

        # Apply filters
        if folder_id:
            query = query.where(Document.folder_id == folder_id)

        if search_query:
            # Full-text search mit PostgreSQL
            search_vector = func.to_tsvector('german', Document.filename + ' ' + Document.description)
            search_term = func.plainto_tsquery('german', search_query)
            query = query.where(search_vector.match(search_term))

        # Apply sorting with optimized indexes
        sort_mapping = {
            DocumentSort.CREATED_DESC: Document.created_at.desc(),
            DocumentSort.CREATED_ASC: Document.created_at.asc(),
            DocumentSort.NAME_ASC: Document.filename.asc(),
            DocumentSort.NAME_DESC: Document.filename.desc(),
            DocumentSort.SIZE_ASC: Document.file_size.asc(),
            DocumentSort.SIZE_DESC: Document.file_size.desc()
        }

        query = query.order_by(sort_mapping[sort])

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        # Execute with count query for total
        total_query = select(func.count(Document.id))
        if folder_id:
            total_query = total_query.where(Document.folder_id == folder_id)
        if search_query:
            total_query = total_query.where(search_vector.match(search_term))

        # Execute both queries
        results = await db.execute(query)
        total_result = await db.execute(total_query)

        documents = results.scalars().all()
        total_count = total_result.scalar()

        return PaginatedDocuments(
            documents=documents,
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=(total_count + per_page - 1) // per_page
        )
```

---

## Fazit

Das Dokumentenverwaltungssystem von Streamworks-KI ist ein **hochmodernes, Enterprise-taugliches System**, das weit über einfache Datei-Uploads hinausgeht. Es kombiniert **intelligente Dokumentenverarbeitung**, **automatische RAG-Integration**, **umfassende Analytics** und **robuste Sicherheitsmaßnahmen** zu einer einheitlichen Plattform.

**Kern-Innovationen:**
1. **Automatische Pipeline**: Upload → Verarbeitung → Chunking → Embedding → RAG-Verfügbarkeit
2. **Layout-Aware Processing**: Erhaltung der Dokumentstruktur für bessere Qualität
3. **Real-time Updates**: Live-Feedback während Verarbeitung
4. **Enterprise Features**: Bulk-Operationen, erweiterte Analytics, Role-Based Access
5. **Performance-Optimiert**: Multi-Level Caching, optimierte Queries, Content-Addressed Storage

Das System bildet die **Wissensgrundlage** für das gesamte RAG-System und ermöglicht es Benutzern, ihre eigenen Dokumente nahtlos in die KI-gestützte Arbeitsweise zu integrieren. Durch die **deutsche Sprachoptimierung** und **StreamWorks-spezifische Anpassungen** wird eine optimale Benutzererfahrung für die Zielgruppe gewährleistet.