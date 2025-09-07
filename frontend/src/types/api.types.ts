/**
 * API Types for StreamWorks Document Management
 * Modern TypeScript definitions matching backend schema
 */

// Base Types
export interface Folder {
  id: string
  name: string
  description?: string
  parent_id?: string
  path: string[]
  created_at: string
  updated_at: string
  document_count: number
  children_count: number
}

export interface FolderTree extends Folder {
  children: FolderTree[]
  documents: Document[]
}

export interface FolderCreate {
  name: string
  description?: string
  parent_id?: string
}

export interface FolderUpdate {
  name?: string
  description?: string
  parent_id?: string
}

export type DocumentStatus = 
  | 'pending'
  | 'uploading' 
  | 'analyzing'
  | 'processing' 
  | 'ready' 
  | 'completed'
  | 'skipped'
  | 'error'

export interface Document {
  id: string
  filename: string
  original_filename: string
  folder_id: string
  file_hash: string
  file_size: number
  mime_type: string
  status: DocumentStatus
  error_message?: string
  created_at: string
  updated_at: string
  processed_at?: string
  tags: string[]
  description?: string
}

export interface DocumentWithFolder extends Document {
  folder?: {
    id: string
    name: string
    path: string[]
  }
}

export interface DocumentCreate {
  filename: string
  folder_id: string
  tags: string[]
  description?: string
}

export interface DocumentUpdate {
  filename?: string
  folder_id?: string
  tags?: string[]
  description?: string
}

// Upload Types
export interface UploadRequest {
  file: File
  folder_id: string
  job_id?: string
  tags?: string[]
  description?: string
}

export interface UploadResponse {
  document: Document
  message: string
  upload_time: number
}

// Filter and Sort Types
export interface DocumentFilter {
  folder_id?: string
  status?: DocumentStatus
  mime_types?: string[]
  tags?: string[]
  date_from?: string
  date_to?: string
  search_query?: string
}

export type DocumentSort = 
  | 'created_asc'
  | 'created_desc' 
  | 'name_asc'
  | 'name_desc'
  | 'size_asc'
  | 'size_desc'

// Bulk Operations
export interface BulkDeleteRequest {
  document_ids: string[]
}

export interface BulkDeleteResponse {
  deleted: string[]
  failed: Array<{ id: string; error: string }>
  total_requested: number
  total_deleted: number
  total_failed: number
}

export interface BulkMoveRequest {
  document_ids: string[]
  target_folder_id: string
}

export interface BulkMoveResponse {
  moved: string[]
  failed: Array<{ id: string; error: string }>
  total_requested: number
  total_moved: number
  total_failed: number
}

export interface BulkReprocessRequest {
  document_ids: string[]
}

export interface BulkReprocessResponse {
  reprocessed: string[]
  failed: Array<{ id: string; error: string }>
  total_requested: number
  total_reprocessed: number
  total_failed: number
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  has_next: boolean
  has_prev: boolean
}

// Statistics
export interface SystemStats {
  total_documents: number
  total_folders: number
  total_size_bytes: number
  average_size_bytes: number
  timestamp: string
}

// API Response Types
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

export interface ApiError {
  error: string
  detail?: string
  status_code?: number
}

// UI State Types
export interface SelectionState {
  selectedDocuments: Set<string>
  selectedFolders: Set<string>
  selectionMode: boolean
}

export interface ViewState {
  currentFolder?: string
  viewMode: 'grid' | 'list'
  sortBy: DocumentSort
  filter: DocumentFilter
  searchQuery: string
  isGlobalView: boolean // True when showing all documents across folders
}

export interface UploadState {
  isUploading: boolean
  uploadProgress: Record<string, number> // filename -> progress
  uploadErrors: Record<string, string>   // filename -> error
}

// Component Props Types
export interface FolderTreeProps {
  folders: FolderTree[]
  selectedFolder?: string
  isGlobalView?: boolean
  onFolderSelect: (folderId: string) => void
  onGlobalViewSelect: () => void
  onFolderCreate: (parentId: string | null) => void
  onFolderDelete: (folderId: string) => void
  expandedFolders: Set<string>
  onToggleExpand: (folderId: string) => void
}

export interface DocumentGridProps {
  documents: DocumentWithFolder[]
  loading: boolean
  selectedDocuments: Set<string>
  onDocumentSelect: (documentId: string) => void
  onDocumentOpen: (documentId: string) => void
  onDocumentDelete: (documentId: string) => void
  viewMode: 'grid' | 'list'
  showFolderInfo?: boolean
}

export interface UploadDropzoneProps {
  folderId: string
  onUploadComplete: (documents: Document[]) => void
  onUploadError: (error: string) => void
  accept?: string[]
  maxFiles?: number
  maxSize?: number
}

export interface ActionToolbarProps {
  selectedCount: number
  totalCount: number
  onBulkDelete: () => void
  onBulkMove: () => void
  onSelectAll: () => void
  onClearSelection: () => void
  onToggleViewMode: () => void
  viewMode: 'grid' | 'list'
}

// Form Types
export interface FolderFormData {
  name: string
  description: string
  parent_id: string | null
}

export interface DocumentFormData {
  filename: string
  folder_id: string
  tags: string[]
  description: string
}

// Hook Return Types
export interface UseFoldersReturn {
  folders: Folder[]
  folderTree: FolderTree[]
  loading: boolean
  error: string | null
  createFolder: (data: FolderCreate) => Promise<Folder>
  updateFolder: (id: string, data: FolderUpdate) => Promise<Folder>
  deleteFolder: (id: string, force?: boolean) => Promise<void>
  refreshFolders: () => Promise<void>
}

export interface UseDocumentsReturn {
  documents: DocumentWithFolder[]
  loading: boolean
  error: string | null
  uploadDocuments: (uploads: UploadRequest[]) => Promise<Document[]>
  deleteDocument: (id: string) => Promise<void>
  bulkDeleteDocuments: (ids: string[]) => Promise<BulkDeleteResponse>
  bulkMoveDocuments: (ids: string[], folderId: string) => Promise<BulkMoveResponse>
  bulkReprocessDocuments: (ids: string[]) => Promise<BulkReprocessResponse>
  refreshDocuments: () => Promise<void>
}

// Document Viewer Types
export interface DocumentChunk {
  id: string
  document_id: string
  chunk_index: number
  content: string
  content_preview?: string
  heading?: string
  section_name?: string
  page_number?: number
  chunk_type: 'text' | 'table' | 'image' | 'code' | 'list' | 'title' | 'section_header'
  metadata?: Record<string, any>
  word_count?: number
  char_count?: number
  created_at: string
  updated_at?: string
  // Legacy field name for backward compatibility
  content_type?: 'text' | 'table' | 'image' | 'code' | 'list' | 'title' | 'section_header'
  coordinates?: {
    x: number
    y: number
    width: number
    height: number
  }
}

export interface DocumentViewerState {
  isOpen: boolean
  currentDocumentId: string | null
  documents: DocumentWithFolder[]
  currentIndex: number
}

export interface DocumentViewerProps {
  isOpen: boolean
  onClose: () => void
  documents: DocumentWithFolder[]
  initialDocumentId: string
  onNavigate?: (documentId: string) => void
}