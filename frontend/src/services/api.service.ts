/**
 * Modern API Service for StreamWorks Document Management
 * Enterprise-grade HTTP client with TypeScript support
 */

import {
  Folder,
  FolderTree,
  FolderCreate,
  FolderUpdate,
  Document,
  DocumentWithFolder,
  DocumentUpdate,
  UploadRequest,
  UploadResponse,
  DocumentFilter,
  DocumentSort,
  BulkDeleteRequest,
  BulkDeleteResponse,
  BulkMoveRequest,
  BulkMoveResponse,
  BulkReprocessRequest,
  BulkReprocessResponse,
  DocumentChunk,
  SystemStats,
  ApiError,
  // XML Chat API Types
  XMLChatSessionRequest,
  XMLChatSessionResponse,
  XMLChatSessionDetails,
  XMLChatMessageRequest,
  XMLChatMessageResponse,
  XMLGenerationRequest,
  XMLGenerationResponse,
  XMLParameterStatus,
  XMLParameterValidation,
  XMLChatSystemStatus
} from '@/types/api.types'

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retryCount: number = 0
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    const maxRetries = 3

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          error: `HTTP ${response.status}`,
          detail: response.statusText
        }))
        throw new Error(errorData.error || errorData.detail || 'Request failed')
      }

      // Handle responses with no content (204 No Content)
      if (response.status === 204 || response.headers.get('content-length') === '0') {
        return null as T
      }

      // Validate response completeness before parsing
      const responseText = await response.text()
      if (!responseText || responseText.trim().length === 0) {
        throw new Error('Empty response received')
      }

      try {
        return JSON.parse(responseText)
      } catch (parseError) {
        console.error('JSON parse error:', parseError, 'Response:', responseText)
        throw new Error('Invalid JSON response')
      }

    } catch (error: any) {
      // Check for chunked encoding errors or network issues
      const isRetryableError =
        error.message?.includes('ERR_INCOMPLETE_CHUNKED_ENCODING') ||
        error.message?.includes('Empty response received') ||
        error.message?.includes('Invalid JSON response') ||
        error.name === 'TypeError' || // Network errors
        error.name === 'AbortError'

      if (isRetryableError && retryCount < maxRetries) {
        console.warn(`Request failed, retrying (${retryCount + 1}/${maxRetries}):`, error.message)

        // Exponential backoff: 500ms, 1s, 2s
        const delay = Math.pow(2, retryCount) * 500
        await new Promise(resolve => setTimeout(resolve, delay))

        return this.request<T>(endpoint, options, retryCount + 1)
      }

      throw error
    }
  }

  private async uploadRequest<T>(
    endpoint: string,
    formData: FormData,
    retryCount: number = 0
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    const maxRetries = 2 // Fewer retries for uploads

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          error: `HTTP ${response.status}`,
          detail: response.statusText
        }))
        throw new Error(errorData.error || errorData.detail || 'Upload failed')
      }

      // Validate response completeness before parsing
      const responseText = await response.text()
      if (!responseText || responseText.trim().length === 0) {
        throw new Error('Empty upload response received')
      }

      try {
        return JSON.parse(responseText)
      } catch (parseError) {
        console.error('Upload JSON parse error:', parseError, 'Response:', responseText)
        throw new Error('Invalid JSON upload response')
      }

    } catch (error: any) {
      // Check for retryable upload errors
      const isRetryableError =
        error.message?.includes('ERR_INCOMPLETE_CHUNKED_ENCODING') ||
        error.message?.includes('Empty upload response received') ||
        error.message?.includes('Invalid JSON upload response') ||
        (error.name === 'TypeError' && !error.message?.includes('Failed to fetch')) // Network errors but not auth issues

      if (isRetryableError && retryCount < maxRetries) {
        console.warn(`Upload failed, retrying (${retryCount + 1}/${maxRetries}):`, error.message)

        // Shorter delay for uploads: 1s, 2s
        const delay = (retryCount + 1) * 1000
        await new Promise(resolve => setTimeout(resolve, delay))

        return this.uploadRequest<T>(endpoint, formData, retryCount + 1)
      }

      throw error
    }
  }

  // Folder Methods
  async getFolders(parentId?: string): Promise<Folder[]> {
    const params = new URLSearchParams()
    if (parentId) params.set('parent_id', parentId)
    
    return this.request<Folder[]>(`/api/v1/folders/?${params}`)
  }

  async getFolderTree(rootId?: string, maxDepth: number = 10): Promise<FolderTree[]> {
    const params = new URLSearchParams()
    if (rootId) params.set('root_id', rootId)
    params.set('max_depth', maxDepth.toString())
    
    return this.request<FolderTree[]>(`/api/v1/folders/tree?${params}`)
  }

  async getFolder(id: string): Promise<Folder> {
    return this.request<Folder>(`/api/v1/folders/${id}`)
  }

  async createFolder(data: FolderCreate): Promise<Folder> {
    return this.request<Folder>('/api/v1/folders/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateFolder(id: string, data: FolderUpdate): Promise<Folder> {
    return this.request<Folder>(`/api/v1/folders/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteFolder(id: string, force: boolean = false): Promise<void> {
    const params = new URLSearchParams()
    if (force) params.set('force', 'true')
    
    await this.request(`/api/v1/folders/${id}?${params}`, {
      method: 'DELETE',
    })
  }

  async searchFolders(query: string, limit: number = 50): Promise<Folder[]> {
    const params = new URLSearchParams()
    params.set('q', query)
    params.set('limit', limit.toString())
    
    return this.request<Folder[]>(`/api/v1/folders/search?${params}`)
  }

  // Document Methods
  async getDocuments(
    folderId?: string,
    filter?: DocumentFilter,
    sort: DocumentSort = 'created_desc',
    page: number = 1,
    perPage: number = 50
  ): Promise<DocumentWithFolder[]> {
    const params = new URLSearchParams()
    
    if (folderId) params.set('folder_id', folderId)
    if (filter?.status) params.set('status', filter.status)
    if (filter?.search_query) params.set('search', filter.search_query)
    if (filter?.tags?.length) params.set('tags', filter.tags.join(','))
    
    params.set('sort', sort)
    params.set('page', page.toString())
    params.set('per_page', perPage.toString())
    
    return this.request<DocumentWithFolder[]>(`/api/v1/documents/?${params}`)
  }

  async getDocumentsByFolder(
    folderId: string,
    sort: DocumentSort = 'created_desc',
    page: number = 1,
    perPage: number = 50
  ): Promise<DocumentWithFolder[]> {
    const params = new URLSearchParams()
    params.set('sort', sort)
    params.set('page', page.toString())
    params.set('per_page', perPage.toString())
    
    return this.request<DocumentWithFolder[]>(`/api/v1/documents/folder/${folderId}?${params}`)
  }

  async getDocument(id: string): Promise<DocumentWithFolder> {
    return this.request<DocumentWithFolder>(`/api/v1/documents/${id}`)
  }

  async uploadDocument(data: UploadRequest): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', data.file)
    
    // Build query parameters
    const params = new URLSearchParams()
    params.set('folder_id', data.folder_id)
    
    if (data.job_id) {
      params.set('job_id', data.job_id)
    }
    
    if (data.tags?.length) {
      params.set('tags', data.tags.join(','))
    }
    
    if (data.description) {
      params.set('description', data.description)
    }
    
    return this.uploadRequest<UploadResponse>(`/api/v1/documents/upload?${params}`, formData)
  }

  async updateDocument(id: string, data: DocumentUpdate): Promise<Document> {
    return this.request<Document>(`/api/v1/documents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteDocument(id: string): Promise<void> {
    await this.request(`/api/v1/documents/${id}`, {
      method: 'DELETE',
    })
  }

  async downloadDocument(id: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/v1/documents/${id}/download`)
    
    if (!response.ok) {
      throw new Error('Download failed')
    }
    
    return response.blob()
  }

  async bulkDeleteDocuments(request: BulkDeleteRequest): Promise<BulkDeleteResponse> {
    return this.request<BulkDeleteResponse>('/api/v1/documents/bulk-delete', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async bulkMoveDocuments(request: BulkMoveRequest): Promise<BulkMoveResponse> {
    return this.request<BulkMoveResponse>('/api/v1/documents/bulk-move', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async bulkReprocessDocuments(request: BulkReprocessRequest): Promise<BulkReprocessResponse> {
    return this.request<BulkReprocessResponse>('/api/v1/documents/bulk-reprocess', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  // Document Chunks Methods
  async getDocumentChunks(
    documentId: string,
    chunkType?: string,
    page: number = 1,
    perPage: number = 50
  ): Promise<{ items: DocumentChunk[]; total: number; page: number; per_page: number; has_next: boolean; has_prev: boolean }> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString()
    })
    
    if (chunkType) {
      params.append('chunk_type', chunkType)
    }

    const backendResponse = await this.request<{ 
      chunks: DocumentChunk[]; 
      total_chunks: number; 
      page: number; 
      per_page: number; 
      document_id: string 
    }>(`/api/v1/documents/${documentId}/chunks?${params.toString()}`)
    
    // Transform backend response to match expected frontend format
    return {
      items: backendResponse.chunks || [],
      total: backendResponse.total_chunks || 0,
      page: backendResponse.page || 1,
      per_page: backendResponse.per_page || 50,
      has_next: false, // Backend doesn't provide this info yet
      has_prev: backendResponse.page > 1
    }
  }

  async getDocumentChunk(documentId: string, chunkId: string): Promise<DocumentChunk> {
    return this.request<DocumentChunk>(`/api/v1/documents/${documentId}/chunks/${chunkId}`)
  }

  // XML Chat Methods - Updated to match backend endpoints
  async createXMLChatSession(request: XMLChatSessionRequest): Promise<XMLChatSessionResponse> {
    return this.request<XMLChatSessionResponse>('/api/chat-xml/sessions', {
      method: 'POST',
      body: JSON.stringify({
        user_id: request.user_id,
        initial_message: request.initial_context
      }),
    })
  }

  async getXMLChatSession(sessionId: string): Promise<XMLChatSessionDetails> {
    return this.request<XMLChatSessionDetails>(`/api/chat-xml/sessions/${sessionId}/status`)
  }

  async sendXMLChatMessage(request: XMLChatMessageRequest): Promise<XMLChatMessageResponse> {
    return this.request<XMLChatMessageResponse>(`/api/chat-xml/sessions/${request.session_id}/messages`, {
      method: 'POST',
      body: JSON.stringify({
        message: request.message,
        context: request.context
      }),
    })
  }

  async generateXMLFromChat(request: XMLGenerationRequest): Promise<XMLGenerationResponse> {
    return this.request<XMLGenerationResponse>(`/api/chat-xml/sessions/${request.session_id}/generate-xml`, {
      method: 'POST'
    })
  }

  async getXMLChatParameters(sessionId: string): Promise<XMLParameterStatus[]> {
    return this.request<XMLParameterStatus[]>(`/api/chat-xml/sessions/${sessionId}/parameters`)
  }

  async validateXMLChatParameters(sessionId: string, parameters: Record<string, any>): Promise<XMLParameterValidation> {
    // Backend uses parameter collection endpoint for validation
    return this.request<XMLParameterValidation>(`/api/chat-xml/sessions/${sessionId}/parameters`, {
      method: 'POST',
      body: JSON.stringify({ parameters })
    })
  }

  async deleteXMLChatSession(sessionId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/chat-xml/sessions/${sessionId}`, {
      method: 'DELETE',
    })
  }

  async getXMLChatStatus(): Promise<XMLChatSystemStatus> {
    return this.request<XMLChatSystemStatus>('/api/chat-xml/health')
  }

  // System Methods
  async getSystemStats(): Promise<SystemStats> {
    return this.request<SystemStats>('/api/v1/documents/stats/overview')
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health')
  }

  async getSystemInfo(): Promise<any> {
    return this.request('/system/info')
  }
}

// Export singleton instance
export const apiService = new ApiService()
export default apiService