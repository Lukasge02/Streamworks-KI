/**
 * Enterprise Chat API Service
 * Professional chat management with user-based storage
 */

export interface ChatSession {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  confidence_score?: number
  processing_time?: string
  sources?: any[]
  created_at: string
}

export interface ChatResponse {
  session_id: string
  message_id: string
  answer: string
  confidence_score?: number
  processing_time?: string
  sources?: any[]
}

class ChatApiService {
  private baseUrl = '/api/chat'
  private userId = 'default-user' // For now, could be dynamic later

  async createSession(title?: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': this.userId
      },
      body: JSON.stringify({ title })
    })

    if (!response.ok) {
      throw new Error('Failed to create session')
    }

    const data = await response.json()
    return data.session_id
  }

  async getUserSessions(): Promise<ChatSession[]> {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      headers: {
        'X-User-ID': this.userId
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch sessions')
    }

    return response.json()
  }

  async getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/messages`, {
      headers: {
        'X-User-ID': this.userId
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch messages')
    }

    return response.json()
  }

  async sendMessage(sessionId: string, query: string): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': this.userId
      },
      body: JSON.stringify({ query })
    })

    if (!response.ok) {
      throw new Error('Failed to send message')
    }

    return response.json()
  }

  async updateSessionTitle(sessionId: string, title: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': this.userId
      },
      body: JSON.stringify({ title })
    })

    if (!response.ok) {
      throw new Error('Failed to update session')
    }
  }

  async deleteSession(sessionId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'X-User-ID': this.userId
      }
    })

    if (!response.ok) {
      throw new Error('Failed to delete session')
    }
  }

  async getUserStats(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/stats`, {
      headers: {
        'X-User-ID': this.userId
      }
    })

    if (!response.ok) {
      throw new Error('Failed to fetch stats')
    }

    return response.json()
  }

  async searchMessages(query: string): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/search?q=${encodeURIComponent(query)}`, {
      headers: {
        'X-User-ID': this.userId
      }
    })

    if (!response.ok) {
      throw new Error('Failed to search messages')
    }

    return response.json()
  }

}

export const chatApiService = new ChatApiService()