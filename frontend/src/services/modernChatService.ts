/**
 * Modern Chat Service API
 * Unified interface for Supabase + OpenAI RAG integration
 * Clean, simple architecture using Session API
 */

import { ChatSession, ChatMessage } from '../stores/chatStore'

// ================================
// TYPES
// ================================

export interface CreateSessionRequest {
  title: string
  user_id?: string
}

export interface SendMessageRequest {
  session_id: string
  query: string
  mode?: 'fast' | 'accurate' | 'comprehensive'
}

export interface ChatResponse {
  message_id: string
  answer: string
  confidence_score?: number
  processing_time?: string
  model_info?: string
  sources?: any[]
}

export interface SessionsResponse {
  sessions: ChatSession[]
  total: number
}

export interface MessagesResponse {
  messages: ChatMessage[]
  total: number
}

// ================================
// MODERN CHAT SERVICE
// ================================

class ModernChatService {
  private baseUrl = '/api/chat'
  private userId: string

  constructor(userId: string = 'default-user') {
    this.userId = userId
  }

  // ================================
  // SESSION MANAGEMENT
  // ================================

  async createSession(request: CreateSessionRequest): Promise<ChatSession> {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': request.user_id || this.userId,
      },
      body: JSON.stringify({
        title: request.title,
      }),
    })

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    
    return {
      id: data.session_id,
      title: request.title,
      user_id: request.user_id || this.userId,
      message_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true,
    }
  }

  async getSessions(): Promise<SessionsResponse> {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      headers: {
        'X-User-ID': this.userId,
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to get sessions: ${response.status} ${response.statusText}`)
    }

    const sessions = await response.json()
    
    return {
      sessions: sessions.map((session: any) => ({
        id: session.id,
        title: session.title,
        user_id: session.user_id,
        message_count: session.message_count || 0,
        created_at: session.created_at,
        updated_at: session.updated_at,
        is_active: session.is_active,
      })),
      total: sessions.length,
    }
  }

  async getSessionMessages(sessionId: string): Promise<MessagesResponse> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/messages`, {
      headers: {
        'X-User-ID': this.userId,
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to get messages: ${response.status} ${response.statusText}`)
    }

    const messages = await response.json()
    
    return {
      messages: messages.map((msg: any) => ({
        id: msg.id,
        session_id: sessionId,
        type: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.content,
        sources: msg.sources,
        confidence_score: msg.confidence_score,
        processing_time: msg.processing_time_ms ? `${msg.processing_time_ms}ms` : undefined,
        model_info: msg.model_info,
        created_at: msg.created_at,
        sequence_number: msg.sequence_number || 0,
      })) as ChatMessage[],
      total: messages.length,
    }
  }

  async updateSessionTitle(sessionId: string, title: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': this.userId,
      },
      body: JSON.stringify({ title }),
    })

    if (!response.ok) {
      throw new Error(`Failed to update session: ${response.status} ${response.statusText}`)
    }
  }

  async deleteSession(sessionId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'X-User-ID': this.userId,
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to delete session: ${response.status} ${response.statusText}`)
    }
  }

  // ================================
  // MESSAGE HANDLING
  // ================================

  async sendMessage(request: SendMessageRequest): Promise<ChatResponse> {
    const startTime = Date.now()

    try {
      // Use OpenAI RAG API via backend Session API
      const response = await fetch(`${this.baseUrl}/sessions/${request.session_id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': this.userId,
        },
        body: JSON.stringify({
          query: request.query,
          mode: request.mode || 'accurate'
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`OpenAI RAG failed: ${response.status} ${errorText}`)
      }

      const data = await response.json()
      const endTime = Date.now()

      return {
        message_id: data.message_id,
        answer: data.answer,
        confidence_score: data.confidence_score,
        processing_time: data.processing_time || `${endTime - startTime}ms`,
        model_info: data.model_info || 'OpenAI + EmbeddingGemma',
        sources: data.sources,
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      throw new Error(`Failed to send message: ${errorMessage}`)
    }
  }


  // ================================
  // HEALTH & UTILITIES
  // ================================

  async checkHealth(): Promise<{ status: string; providers: Record<string, any> }> {
    try {
      // Check OpenAI RAG API health via backend
      const response = await fetch(`${this.baseUrl}/health`, {
        headers: { 'X-User-ID': this.userId },
      })
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`)
      }
      
      const healthData = await response.json()

      return {
        status: 'healthy',
        providers: {
          openai_rag: healthData,
        },
      }
    } catch (error) {
      return {
        status: 'error',
        providers: {
          error: error instanceof Error ? error.message : 'Health check failed',
        },
      }
    }
  }

  // Update user ID (for session management)
  setUserId(userId: string): void {
    this.userId = userId
  }

  getUserId(): string {
    return this.userId
  }
}

// ================================
// SINGLETON EXPORT
// ================================

export const modernChatService = new ModernChatService()
export default modernChatService