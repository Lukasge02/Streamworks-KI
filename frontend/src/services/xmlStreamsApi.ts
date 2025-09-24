/**
 * API Service für XML Stream Management
 * Provides typed API methods for CRUD operations on XML streams
 */
export interface XMLStream {
  id: string
  stream_name: string
  description: string | null
  xml_content: string | null
  wizard_data: Record<string, any> | null
  job_type: 'standard' | 'sap' | 'file_transfer' | 'custom' | null
  status: 'draft' | 'zur_freigabe' | 'freigegeben' | 'abgelehnt' | 'published' | 'complete' // complete is legacy
  created_by: string
  created_at: string
  updated_at: string
  last_generated_at: string | null
  tags: string[]
  is_favorite: boolean
  version: number
  template_id: string | null
}

export interface StreamFilters {
  search?: string
  job_types?: string[]
  statuses?: string[]
  tags?: string[]
  is_favorite?: boolean
  created_after?: string
  created_before?: string
}

export interface StreamListResponse {
  streams: XMLStream[]
  total_count: number
  limit: number
  offset: number
  has_more: boolean
}

export interface CreateStreamRequest {
  stream_name: string
  description?: string
  xml_content?: string
  wizard_data?: Record<string, any>
  job_type?: string
  status?: string
  tags?: string[]
  is_favorite?: boolean
}

export interface UpdateStreamRequest {
  stream_name?: string
  description?: string
  xml_content?: string
  wizard_data?: Record<string, any>
  job_type?: string
  status?: string
  tags?: string[]
  is_favorite?: boolean
}

export interface AutoSaveRequest {
  wizard_data?: Record<string, any>
  xml_content?: string
}

export interface StreamStats {
  total_streams: number
  draft_streams: number
  complete_streams: number
  published_streams: number
  favorite_streams: number
  recent_streams: number
  job_type_distribution: Record<string, number>
}

/**
 * Helper function to serialize error objects into readable strings
 */
function serializeError(error: any): string {
  if (typeof error === 'string') {
    return error
  }

  if (typeof error === 'object' && error !== null) {
    // Handle different error object formats
    if (error.message) {
      return error.message
    }

    if (error.error && typeof error.error === 'string') {
      return error.error
    }

    if (error.detail) {
      if (typeof error.detail === 'string') {
        return error.detail
      }

      if (typeof error.detail === 'object') {
        // Recursively serialize nested error objects
        return serializeError(error.detail)
      }
    }

    // Handle array of errors
    if (Array.isArray(error)) {
      return error.map(e => serializeError(e)).join('; ')
    }

    // Last resort: JSON stringify with fallback
    try {
      return JSON.stringify(error)
    } catch {
      return 'Unknown error format'
    }
  }

  return String(error)
}

class XMLStreamsApi {
  private baseUrl: string

  constructor(baseUrl = '/api/streamworks/sessions') {
    this.baseUrl = baseUrl
  }

  /**
   * Get list of LangExtract sessions formatted as XML streams
   */
  async listStreams(
    filters: StreamFilters = {},
    sortBy: string = 'updated_desc',
    limit: number = 50,
    offset: number = 0
  ): Promise<StreamListResponse> {
    const params = new URLSearchParams()

    if (filters.search) params.append('search', filters.search)
    if (filters.job_types) params.append('job_types', filters.job_types.join(','))
    if (filters.statuses) params.append('statuses', filters.statuses.join(','))
    // Note: LangExtract sessions don't have tags/favorites, so we skip those filters

    params.append('sort_by', sortBy)
    params.append('limit', String(limit))
    params.append('offset', String(offset))

    const response = await fetch(`${this.baseUrl}/as-streams?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch sessions as streams: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Get a specific session formatted as stream by ID
   */
  async getStream(streamId: string): Promise<XMLStream> {
    const response = await fetch(`${this.baseUrl}/${streamId}`)
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Session not found')
      }
      throw new Error(`Failed to fetch session: ${response.statusText}`)
    }

    const sessionData = await response.json()

    // Convert session data to stream format for consistency
    const sessionParams = sessionData.session_data?.stream_parameters || {}
    const jobParams = sessionData.session_data?.jobs?.[0]?.parameters || {}

    return {
      id: sessionData.session_id,
      stream_name: sessionParams.StreamName || sessionParams.streamName || `Session ${sessionData.session_id.slice(0, 8)}`,
      description: sessionParams.ShortDescription || sessionParams.description || "LangExtract Session",
      xml_content: null,
      wizard_data: {
        stream_parameters: sessionParams,
        job_parameters: jobParams,
        session_source: "langextract"
      },
      job_type: sessionData.job_type || 'standard',
      status: (Object.keys(sessionParams).length + Object.keys(jobParams).length) >= 2 ? 'complete' : 'draft',
      created_by: "langextract_system",
      created_at: sessionData.created_at || new Date().toISOString(),
      updated_at: sessionData.last_message_at || sessionData.created_at || new Date().toISOString(),
      last_generated_at: null,
      tags: [`job-${sessionData.job_type || 'standard'}`, "langextract"],
      is_favorite: false,
      version: 1,
      template_id: null
    }
  }

  /**
   * Create a new LangExtract session (formatted as stream)
   */
  async createStream(data: CreateStreamRequest): Promise<XMLStream> {
    // Create new LangExtract session instead of XML stream
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        job_type: data.job_type || 'standard'
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to create session: ${response.statusText}`)
    }

    const sessionResponse = await response.json()

    // Return in stream format
    return {
      id: sessionResponse.session_id,
      stream_name: data.stream_name || "New Session",
      description: data.description || "New LangExtract Session",
      xml_content: null,
      wizard_data: {
        stream_parameters: {},
        job_parameters: {},
        session_source: "langextract"
      },
      job_type: sessionResponse.job_type || 'standard',
      status: 'draft',
      created_by: "langextract_system",
      created_at: sessionResponse.created_at || new Date().toISOString(),
      updated_at: sessionResponse.created_at || new Date().toISOString(),
      last_generated_at: null,
      tags: [`job-${sessionResponse.job_type || 'standard'}`, "langextract"],
      is_favorite: false,
      version: 1,
      template_id: null
    }
  }

  /**
   * Update an existing stream
   */
  async updateStream(
    streamId: string,
    data: UpdateStreamRequest,
    createVersion: boolean = true
  ): Promise<XMLStream> {
    console.log('📤 XMLStreamsApi.updateStream - Request started:', {
      streamId,
      data,
      createVersion,
      baseUrl: this.baseUrl
    })

    const params = new URLSearchParams()
    params.append('create_version', String(createVersion))

    const url = `${this.baseUrl}/${streamId}?${params}`
    const requestPayload = JSON.stringify(data)

    console.log('🌐 Making PUT request to:', url)
    console.log('📋 Request payload:', requestPayload)

    try {
      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: requestPayload,
      })

      console.log('📡 Response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries())
      })

      if (!response.ok) {
        let errorData: any = {}
        let rawErrorText: string = ''

        try {
          // First try to get the raw response text
          rawErrorText = await response.text()
          console.error('❌ Raw error response:', {
            status: response.status,
            statusText: response.statusText,
            rawText: rawErrorText
          })

          // Try to parse as JSON if it looks like JSON
          if (rawErrorText.trim().startsWith('{') || rawErrorText.trim().startsWith('[')) {
            errorData = JSON.parse(rawErrorText)
            console.error('❌ Parsed error data:', errorData)
          } else {
            // If it's not JSON, use the raw text
            errorData = { detail: rawErrorText }
          }
        } catch (parseError) {
          console.error('❌ Failed to parse error response:', parseError)
          errorData = { detail: rawErrorText || `HTTP ${response.status}: ${response.statusText}` }
        }

        // Use the helper function to serialize the error properly
        const errorMessage = serializeError(errorData.detail) ||
                            serializeError(errorData) ||
                            rawErrorText ||
                            `Failed to update stream: HTTP ${response.status} ${response.statusText}`

        console.error('❌ Final error message:', errorMessage)
        throw new Error(errorMessage)
      }

      const result = await response.json()
      console.log('✅ XMLStreamsApi.updateStream - Success:', result)
      return result

    } catch (error) {
      console.error('❌ XMLStreamsApi.updateStream - Network or parsing error:', {
        error,
        name: (error as Error)?.name,
        message: (error as Error)?.message,
        stack: (error as Error)?.stack
      })
      throw error
    }
  }

  /**
   * Auto-save stream data (lightweight updates)
   */
  async autoSaveStream(streamId: string, data: AutoSaveRequest): Promise<XMLStream> {
    const response = await fetch(`${this.baseUrl}/${streamId}/auto-save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to auto-save stream: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Delete a LangExtract session (formatted as stream deletion)
   */
  async deleteStream(streamId: string): Promise<void> {
    // For now, we'll throw an error since LangExtract sessions deletion
    // should be handled through the LangExtract interface
    throw new Error('Deletion of LangExtract sessions is not supported through stream interface. Please use the LangExtract chat interface.')
  }

  /**
   * Duplicate a stream
   */
  async duplicateStream(streamId: string, newName?: string): Promise<XMLStream> {
    const response = await fetch(`${this.baseUrl}/${streamId}/duplicate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ new_name: newName }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to duplicate stream: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Toggle favorite status
   */
  async toggleFavorite(streamId: string): Promise<XMLStream> {
    const response = await fetch(`${this.baseUrl}/${streamId}/favorite`, {
      method: 'POST',
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to toggle favorite: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Get stream statistics
   */
  async getStats(): Promise<StreamStats> {
    const response = await fetch(`${this.baseUrl}/stats`)
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`)
    }
    
    return response.json()
  }

  /**
   * Export stream
   */
  async exportStream(streamId: string, format: 'xml' | 'json' = 'xml'): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/${streamId}/export?format=${format}`)
    if (!response.ok) {
      throw new Error(`Failed to export stream: ${response.statusText}`)
    }
    
    return response.blob()
  }

  /**
   * Bulk delete streams
   */
  async bulkDeleteStreams(streamIds: string[]): Promise<{ processed: number; total: number }> {
    const response = await fetch(`${this.baseUrl}/bulk-action`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stream_ids: streamIds,
        action: 'delete',
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to bulk delete streams: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Bulk toggle favorite streams
   */
  async bulkToggleFavorite(streamIds: string[]): Promise<{ processed: number; total: number }> {
    const response = await fetch(`${this.baseUrl}/bulk-action`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stream_ids: streamIds,
        action: 'toggle_favorite',
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to bulk toggle favorites: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Submit stream for expert review
   */
  async submitForReview(streamId: string): Promise<XMLStream> {
    const response = await fetch(`${this.baseUrl}/${streamId}/submit-for-review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to submit for review: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Approve stream (expert action)
   */
  async approveStream(streamId: string): Promise<XMLStream> {
    const response = await fetch(`${this.baseUrl}/${streamId}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to approve stream: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Reject stream (expert action)
   */
  async rejectStream(streamId: string, reason: string): Promise<XMLStream> {
    const response = await fetch(`${this.baseUrl}/${streamId}/reject`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ reason }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to reject stream: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Publish approved stream (expert action)
   */
  async publishStream(streamId: string): Promise<XMLStream> {
    const response = await fetch(`${this.baseUrl}/${streamId}/publish`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Failed to publish stream: ${response.statusText}`)
    }

    return response.json()
  }
}

// Singleton instance
export const xmlStreamsApi = new XMLStreamsApi()
export default xmlStreamsApi