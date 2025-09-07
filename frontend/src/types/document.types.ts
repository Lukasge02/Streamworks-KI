export interface Document {
  id: string
  filename: string
  original_filename: string
  doctype: 'manual' | 'xml' | 'faq' | 'general'
  category: string
  folder_id?: string  // OPTIONAL - default folder for now
  upload_date: string
  size_bytes: number
  chunk_count: number
  vector_count?: number
  status: ProcessingStatus
  tags: string[]
  visibility: 'internal' | 'external' | 'public'
  metadata?: {
    pages?: number
    author?: string
    title?: string
    language?: string
  }
  processing_time?: number
  error_message?: string
}

export type ProcessingStatus = 
  | 'uploading' 
  | 'processing' 
  | 'chunking' 
  | 'embedding' 
  | 'indexed'
  | 'ready' 
  | 'error'
  | 'cancelled'

export interface UploadJobProgress {
  job_id: string
  filename: string
  status: ProcessingStatus
  progress_percentage: number
  current_stage: string
  stage_details?: string
  total_stages: number
  current_stage_index: number
  started_at: string
  updated_at: string
  error_message?: string
  file_size_bytes: number
  document_id?: string
}

export interface DocumentEvent {
  type: 'document_added' | 'document_deleted' | 'document_updated' | 'upload_progress'
  data: Document | UploadJobProgress
  timestamp: string
  source: 'websocket' | 'api' | 'optimistic'
}

export interface Folder {
  id: string
  name: string
  parent_id?: string
  category: string
  created_at: string
  document_count: number
  path: string[]
}

export interface DocumentFilter {
  category?: string
  doctype?: string
  status?: ProcessingStatus
  tags?: string[]
  search?: string
  folder_id?: string
}

export interface DocumentUploadRequest {
  file: File
  doctype: Document['doctype']
  category: string
  tags: string[]
  folder_id?: string  // OPTIONAL - default folder for now
  visibility: Document['visibility']
}

// Alias for backward compatibility
export interface DocumentUpload extends DocumentUploadRequest {
  language: string
  visibility: VisibilityOptions
}

export interface VisibilityOptions {
  internal: boolean
  external: boolean
  public: boolean
}

export interface OptimisticOperation {
  id: string
  type: 'create' | 'update' | 'delete'
  entity: 'document' | 'folder'
  data: any
  rollback: () => void
  timestamp: string
}

export interface DocumentStats {
  total_documents: number
  total_chunks: number
  total_size_bytes: number
  documents_by_type: Record<string, number>
  documents_by_status: Record<string, number>
}

export interface UploadJobStatus {
  job_id: string
  filename: string
  status: ProcessingStatus
  progress: number
  current_stage: string
  stage_details?: string
  error_message?: string
  document_id?: string
}

export interface BatchUploadRequest {
  files: Array<{
    file: File
    doctype: Document['doctype']
    tags: string[]
    language: string
    folder_id: string
  }>
  concurrentUploads?: number
  priority?: 'normal' | 'high'
}

export interface DocumentPreview {
  id: string
  filename: string
  content_preview: string
  metadata: Record<string, any>
  chunk_count: number
}