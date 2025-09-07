/**
 * Local Chat API Service for 100% Local RAG Pipeline
 * Handles communication with the local Ollama-based RAG system
 */

export interface LocalChatQuery {
  query: string
  mode?: 'fast' | 'accurate' | 'comprehensive'
}

export interface LocalChatResponse {
  answer: string
  confidence: number
  sources: LocalSource[]
  chunks_used: number
  model_used: string
  processing_time: number
  response_time: string
  metadata: LocalResponseMetadata
}

export interface LocalSource {
  id: string
  content: string
  metadata: {
    original_filename?: string
    page_number?: number
    heading?: string
    doc_id?: string
  }
  score: number
}

export interface LocalResponseMetadata {
  mode: string
  retrieved_chunks: number
  total_tokens: number
  model_used: string
  provider: string
}

class LocalChatApiService {
  private baseUrl = '/api/chat'
  private localEndpoint = '/local-only'
  private userId = 'default-user' // Consistent with existing service

  async sendLocalMessage(query: string, mode: 'fast' | 'accurate' | 'comprehensive' = 'accurate'): Promise<LocalChatResponse> {
    const response = await fetch(`${this.baseUrl}${this.localEndpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': this.userId
      },
      body: JSON.stringify({
        query,
        mode
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Local RAG API Error ${response.status}: ${errorText}`)
    }

    return response.json()
  }

  async checkLocalHealth(): Promise<any> {
    const response = await fetch(`${this.baseUrl}${this.localEndpoint}/health`, {
      headers: {
        'X-User-ID': this.userId
      }
    })

    if (!response.ok) {
      throw new Error(`Local RAG Health Check Failed: ${response.status}`)
    }

    return response.json()
  }

  // Convert local response to standard chat format for UI compatibility
  formatForChatInterface(localResponse: LocalChatResponse): {
    answer: string
    confidence_score: number
    processing_time: string
    sources: any[]
  } {
    return {
      answer: localResponse.answer,
      confidence_score: localResponse.confidence,
      processing_time: localResponse.response_time,
      sources: localResponse.sources.map(source => ({
        id: source.id,
        metadata: {
          doc_id: source.metadata.doc_id,
          original_filename: source.metadata.original_filename,
          page_number: source.metadata.page_number,
          heading: source.metadata.heading,
          section: source.content,
        },
        relevance_score: source.score,
        similarity_score: source.score,
        content_preview: source.content.substring(0, 200) + '...',
      }))
    }
  }
}

export const localChatApiService = new LocalChatApiService()