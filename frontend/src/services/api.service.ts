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
  ApiError
} from '@/types/api.types'

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
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

    return response.json()
  }

  private async uploadRequest<T>(
    endpoint: string,
    formData: FormData
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
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

    return response.json()
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