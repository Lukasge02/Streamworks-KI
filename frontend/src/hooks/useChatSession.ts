'use client'

import { useState, useEffect } from 'react'

const USER_ID = 'default-user' // Consistent user ID
const API_BASE = '/api/chat'

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: any[]
  confidence_score?: number
  processing_time?: string
  model_info?: string
  sequence_number?: number
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  created_at: Date
  updated_at: Date
  message_count: number
  is_active: boolean
}

export function useChatSession() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load sessions from API on mount
  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(`${API_BASE}/sessions`, {
        headers: {
          'X-User-ID': USER_ID
        }
      })
      
      if (!response.ok) {
        throw new Error(`Failed to load sessions: ${response.statusText}`)
      }
      
      const sessionsData = await response.json()
      
      // Convert API response to ChatSession format
      const formattedSessions: ChatSession[] = sessionsData.map((session: any) => ({
        id: session.id,
        title: session.title,
        created_at: new Date(session.created_at),
        updated_at: new Date(session.updated_at),
        message_count: session.message_count,
        is_active: session.is_active,
        messages: [] // Messages loaded separately when session is selected
      }))
      
      setSessions(formattedSessions)
      
      // Auto-select the most recent session if none selected
      if (!currentSessionId && formattedSessions.length > 0) {
        setCurrentSessionId(formattedSessions[0].id)
      }
      
    } catch (err) {
      console.error('Failed to load sessions:', err)
      setError(err instanceof Error ? err.message : 'Failed to load sessions')
    } finally {
      setIsLoading(false)
    }
  }

  const createNewSession = async (title?: string): Promise<string | null> => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': USER_ID
        },
        body: JSON.stringify({
          title: title || `Chat ${new Date().toLocaleString()}`
        })
      })
      
      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.statusText}`)
      }
      
      const { session_id } = await response.json()
      
      // Reload sessions to get the new one
      await loadSessions()
      setCurrentSessionId(session_id)
      
      return session_id
      
    } catch (err) {
      console.error('Failed to create session:', err)
      setError(err instanceof Error ? err.message : 'Failed to create session')
      return null
    } finally {
      setIsLoading(false)
    }
  }

  const loadSessionMessages = async (sessionId: string): Promise<ChatMessage[]> => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}/messages`, {
        headers: {
          'X-User-ID': USER_ID
        }
      })
      
      if (!response.ok) {
        throw new Error(`Failed to load messages: ${response.statusText}`)
      }
      
      const messagesData = await response.json()
      
      // Convert API response to ChatMessage format
      const formattedMessages: ChatMessage[] = messagesData.map((msg: any) => ({
        id: msg.id,
        type: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: new Date(msg.created_at),
        sources: msg.sources || [],
        confidence_score: msg.confidence_score,
        processing_time: msg.processing_time_ms ? `${msg.processing_time_ms}ms` : undefined,
        model_info: msg.model_used,
        sequence_number: msg.sequence_number
      }))
      
      return formattedMessages.sort((a, b) => (a.sequence_number || 0) - (b.sequence_number || 0))
      
    } catch (err) {
      console.error('Failed to load messages:', err)
      setError(err instanceof Error ? err.message : 'Failed to load messages')
      return []
    }
  }

  const sendMessage = async (content: string): Promise<boolean> => {
    if (!currentSessionId) {
      console.error('No current session')
      return false
    }
    
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await fetch(`${API_BASE}/sessions/${currentSessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': USER_ID
        },
        body: JSON.stringify({
          query: content,
          processing_mode: 'accurate'
        })
      })
      
      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.statusText}`)
      }
      
      // Reload messages for current session
      if (currentSessionId) {
        const messages = await loadSessionMessages(currentSessionId)
        setSessions(prev => prev.map(session => 
          session.id === currentSessionId 
            ? { ...session, messages, message_count: messages.length }
            : session
        ))
      }
      
      return true
      
    } catch (err) {
      console.error('Failed to send message:', err)
      setError(err instanceof Error ? err.message : 'Failed to send message')
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const switchToSession = async (sessionId: string) => {
    try {
      setCurrentSessionId(sessionId)
      
      // Load messages for this session if not already loaded
      const session = sessions.find(s => s.id === sessionId)
      if (session && session.messages.length === 0) {
        const messages = await loadSessionMessages(sessionId)
        setSessions(prev => prev.map(s => 
          s.id === sessionId 
            ? { ...s, messages }
            : s
        ))
      }
      
    } catch (err) {
      console.error('Failed to switch session:', err)
      setError(err instanceof Error ? err.message : 'Failed to switch session')
    }
  }

  const deleteSession = async (sessionId: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'X-User-ID': USER_ID
        }
      })
      
      if (!response.ok) {
        throw new Error(`Failed to delete session: ${response.statusText}`)
      }
      
      // Remove from local state
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      
      // If deleted session was current, switch to another
      if (currentSessionId === sessionId) {
        const remainingSessions = sessions.filter(s => s.id !== sessionId)
        setCurrentSessionId(remainingSessions.length > 0 ? remainingSessions[0].id : null)
      }
      
      return true
      
    } catch (err) {
      console.error('Failed to delete session:', err)
      setError(err instanceof Error ? err.message : 'Failed to delete session')
      return false
    }
  }

  const updateSessionTitle = async (sessionId: string, title: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': USER_ID
        },
        body: JSON.stringify({ title })
      })
      
      if (!response.ok) {
        throw new Error(`Failed to update session: ${response.statusText}`)
      }
      
      // Update local state
      setSessions(prev => prev.map(session => 
        session.id === sessionId 
          ? { ...session, title }
          : session
      ))
      
      return true
      
    } catch (err) {
      console.error('Failed to update session:', err)
      setError(err instanceof Error ? err.message : 'Failed to update session')
      return false
    }
  }

  // Get current session
  const currentSession = sessions.find(s => s.id === currentSessionId) || null

  // Search sessions by title or content (client-side for now)
  const searchSessions = (query: string): ChatSession[] => {
    if (!query.trim()) return sessions
    
    const lowerQuery = query.toLowerCase().trim()
    return sessions.filter(session => {
      // Search in session title
      if (session.title.toLowerCase().includes(lowerQuery)) {
        return true
      }
      
      // Search in message content (only loaded messages)
      return session.messages.some(msg => 
        msg.content.toLowerCase().includes(lowerQuery)
      )
    })
  }

  // Get session statistics
  const getSessionStats = () => {
    const totalMessages = sessions.reduce((sum, session) => sum + session.message_count, 0)
    const totalSessions = sessions.length
    const avgMessagesPerSession = totalSessions > 0 ? Math.round(totalMessages / totalSessions) : 0
    
    return {
      totalSessions,
      totalMessages,
      avgMessagesPerSession,
      storagePercent: 0, // Not applicable for API-based storage
      oldestSession: sessions.length > 0 ? sessions[sessions.length - 1].created_at : null,
      newestSession: sessions.length > 0 ? sessions[0].created_at : null
    }
  }

  return {
    // State
    sessions,
    currentSessionId,
    currentSession,
    isLoading,
    error,
    
    // Actions
    loadSessions,
    createNewSession,
    sendMessage,
    switchToSession,
    deleteSession,
    updateSessionTitle,
    searchSessions,
    getSessionStats,
    
    // Utility
    loadSessionMessages
  }
}