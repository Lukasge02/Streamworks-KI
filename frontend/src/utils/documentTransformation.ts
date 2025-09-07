/**
 * Unified Document Transformation Utilities
 * Eliminates duplicate code for document format conversions
 */

export interface SupabaseDocument {
  id: number
  filename: string
  mime_type: string
  file_size: number
  total_chunks: number
  status: string
  language: string
  created_at: string
  updated_at: string
  original_path?: string
  title?: string
  description?: string
}

export interface UnifiedDocument {
  id: string
  filename: string
  original_filename: string
  doctype: string
  category: string
  upload_date: string
  size_bytes: number
  chunk_count: number
  status: string
  tags: string[]
  visibility: string
  language: string
  created_at: string
  updated_at: string
  file_path: string
  title: string
  description: string
}

export interface WebSocketDocumentEvent {
  type: 'document_added' | 'document_updated' | 'document_deleted'
  data: UnifiedDocument | { id: string }
  timestamp: string
  source: 'supabase' | 'local' | 'api'
}

class DocumentTransformationService {
  private static instance: DocumentTransformationService

  static getInstance(): DocumentTransformationService {
    if (!DocumentTransformationService.instance) {
      DocumentTransformationService.instance = new DocumentTransformationService()
    }
    return DocumentTransformationService.instance
  }

  /**
   * Transform Supabase document to unified format
   */
  supabaseToUnified(doc: SupabaseDocument): UnifiedDocument {
    return {
      id: doc.id.toString(),
      filename: doc.filename,
      original_filename: doc.filename,
      doctype: this.extractDocumentType(doc.mime_type),
      category: 'supabase',
      upload_date: doc.created_at,
      size_bytes: doc.file_size,
      chunk_count: doc.total_chunks,
      status: doc.status,
      tags: [],
      visibility: 'internal',
      language: doc.language,
      created_at: doc.created_at,
      updated_at: doc.updated_at,
      file_path: doc.original_path || '',
      title: doc.title || '',
      description: doc.description || ''
    }
  }

  /**
   * Transform multiple Supabase documents
   */
  supabaseArrayToUnified(docs: SupabaseDocument[]): UnifiedDocument[] {
    return docs.map(doc => this.supabaseToUnified(doc))
  }

  /**
   * Create WebSocket event for document operations
   */
  createWebSocketEvent(
    type: WebSocketDocumentEvent['type'],
    document: SupabaseDocument | { id: number },
    source: WebSocketDocumentEvent['source'] = 'supabase'
  ): WebSocketDocumentEvent {
    const timestamp = new Date().toISOString()
    
    if (type === 'document_deleted') {
      return {
        type,
        data: { id: (document as { id: number }).id.toString() },
        timestamp,
        source
      }
    }

    const unifiedDoc = this.supabaseToUnified(document as SupabaseDocument)
    return {
      type,
      data: unifiedDoc,
      timestamp,
      source
    }
  }

  /**
   * Extract document type from MIME type
   */
  private extractDocumentType(mimeType: string): string {
    const typeMap: Record<string, string> = {
      'application/pdf': 'pdf',
      'text/plain': 'text',
      'text/markdown': 'markdown',
      'application/msword': 'doc',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
      'text/html': 'html',
      'application/xml': 'xml',
      'text/xml': 'xml',
      'application/json': 'json'
    }

    // Direct match
    if (typeMap[mimeType]) {
      return typeMap[mimeType]
    }

    // Pattern matching
    if (mimeType.includes('pdf')) return 'pdf'
    if (mimeType.includes('text')) return 'text'
    if (mimeType.includes('word') || mimeType.includes('doc')) return 'doc'
    if (mimeType.includes('xml')) return 'xml'
    if (mimeType.includes('json')) return 'json'
    
    return 'unknown'
  }

  /**
   * Validate document data integrity
   */
  validateDocument(doc: UnifiedDocument): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!doc.id || doc.id.length === 0) {
      errors.push('Document ID is required')
    }

    if (!doc.filename || doc.filename.length === 0) {
      errors.push('Filename is required')
    }

    if (doc.size_bytes < 0) {
      errors.push('File size cannot be negative')
    }

    if (doc.chunk_count < 0) {
      errors.push('Chunk count cannot be negative')
    }

    if (!['pdf', 'text', 'doc', 'docx', 'html', 'xml', 'json', 'markdown', 'unknown'].includes(doc.doctype)) {
      errors.push('Invalid document type')
    }

    try {
      new Date(doc.created_at)
    } catch {
      errors.push('Invalid created_at date format')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  /**
   * Compare two documents for changes
   */
  compareDocuments(oldDoc: UnifiedDocument, newDoc: UnifiedDocument): {
    hasChanges: boolean
    changes: string[]
  } {
    const changes: string[] = []
    
    const compareFields = [
      'filename', 'status', 'chunk_count', 'title', 'description', 'size_bytes'
    ] as const

    compareFields.forEach(field => {
      if (oldDoc[field] !== newDoc[field]) {
        changes.push(`${field}: ${oldDoc[field]} → ${newDoc[field]}`)
      }
    })

    return {
      hasChanges: changes.length > 0,
      changes
    }
  }

  /**
   * Generate document summary for display
   */
  generateDocumentSummary(doc: UnifiedDocument): {
    displayName: string
    subtitle: string
    metadata: string[]
    statusColor: 'green' | 'yellow' | 'red' | 'blue' | 'gray'
  } {
    const displayName = doc.title || doc.filename
    const subtitle = `${doc.doctype.toUpperCase()} • ${this.formatFileSize(doc.size_bytes)}`
    
    const metadata = [
      `${doc.chunk_count} chunks`,
      `Updated ${this.formatRelativeTime(doc.updated_at)}`,
      `Language: ${doc.language}`
    ]

    const statusColor = this.getStatusColor(doc.status)

    return { displayName, subtitle, metadata, statusColor }
  }

  /**
   * Format file size for display
   */
  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B'
    
    const units = ['B', 'KB', 'MB', 'GB']
    const k = 1024
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${units[i]}`
  }

  /**
   * Format relative time for display
   */
  private formatRelativeTime(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffMinutes < 1) return 'just now'
    if (diffMinutes < 60) return `${diffMinutes}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    
    return date.toLocaleDateString()
  }

  /**
   * Get status color for UI
   */
  private getStatusColor(status: string): 'green' | 'yellow' | 'red' | 'blue' | 'gray' {
    const colorMap: Record<string, 'green' | 'yellow' | 'red' | 'blue' | 'gray'> = {
      'completed': 'green',
      'processing': 'yellow',
      'failed': 'red',
      'pending': 'blue',
      'unknown': 'gray'
    }
    
    return colorMap[status.toLowerCase()] || 'gray'
  }
}

// Export singleton instance
export const documentTransformer = DocumentTransformationService.getInstance()

// Export convenience functions
export const supabaseToUnified = (doc: SupabaseDocument) => documentTransformer.supabaseToUnified(doc)
export const createDocumentEvent = (
  type: WebSocketDocumentEvent['type'], 
  doc: SupabaseDocument | { id: number }, 
  source?: WebSocketDocumentEvent['source']
) => documentTransformer.createWebSocketEvent(type, doc, source)
export const validateDocument = (doc: UnifiedDocument) => documentTransformer.validateDocument(doc)
export const compareDocuments = (oldDoc: UnifiedDocument, newDoc: UnifiedDocument) => 
  documentTransformer.compareDocuments(oldDoc, newDoc)
export const generateDocumentSummary = (doc: UnifiedDocument) => 
  documentTransformer.generateDocumentSummary(doc)