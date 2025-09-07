import { useState, useEffect } from 'react'

export interface EnterpriseMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: any[]
  confidence_score?: number
  processing_time?: string
  session_id?: string
}

export interface EnterpriseChatSession {
  id: string
  title: string
  messages: EnterpriseMessage[]
  created_at: Date
  updated_at: Date
  user_id: string
}

const STORAGE_KEY = 'streamworks_enterprise_chat'
const MAX_SESSIONS = 100
const MAX_MESSAGES_PER_SESSION = 200

export const useEnterpriseChat = (userId: string = 'default-user') => {
  const [sessions, setSessions] = useState<EnterpriseChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Load sessions from storage on mount
  useEffect(() => {
    const loadSessions = () => {
      try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) {
          const parsed = JSON.parse(saved)
          const userSessions = parsed.filter((s: any) => s.user_id === userId)
          const sessionsWithDates = userSessions.map((session: any) => ({
            ...session,
            created_at: new Date(session.created_at),
            updated_at: new Date(session.updated_at),
            messages: session.messages.map((msg: any) => ({
              ...msg,
              timestamp: new Date(msg.timestamp)
            }))
          }))
          setSessions(sessionsWithDates)
        }
      } catch (error) {
        console.error('Failed to load chat sessions:', error)
        setSessions([])
      }
    }

    loadSessions()
  }, [userId])

  // Save sessions to storage whenever they change
  useEffect(() => {
    try {
      // Load existing sessions for all users
      const saved = localStorage.getItem(STORAGE_KEY)
      const allSessions = saved ? JSON.parse(saved) : []
      
      // Remove old sessions for current user and add current sessions
      const otherUserSessions = allSessions.filter((s: any) => s.user_id !== userId)
      const updatedSessions = [...otherUserSessions, ...sessions]
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSessions))
    } catch (error) {
      console.error('Failed to save chat sessions:', error)
    }
  }, [sessions, userId])

  const createSession = (title?: string): string => {
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const now = new Date()
    
    const newSession: EnterpriseChatSession = {
      id: sessionId,
      title: title || `Chat ${now.toLocaleDateString()} ${now.toLocaleTimeString()}`,
      messages: [],
      created_at: now,
      updated_at: now,
      user_id: userId
    }

    setSessions(prev => {
      const updated = [newSession, ...prev].slice(0, MAX_SESSIONS)
      return updated
    })
    
    setCurrentSessionId(sessionId)
    return sessionId
  }

  const getCurrentSession = (): EnterpriseChatSession | null => {
    if (!currentSessionId) return null
    return sessions.find(s => s.id === currentSessionId) || null
  }

  const addMessage = async (message: Omit<EnterpriseMessage, 'id' | 'timestamp' | 'session_id'>) => {
    if (!currentSessionId) {
      const newSessionId = createSession()
      setCurrentSessionId(newSessionId)
    }

    const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const newMessage: EnterpriseMessage = {
      ...message,
      id: messageId,
      timestamp: new Date(),
      session_id: currentSessionId!
    }

    setSessions(prev => prev.map(session => {
      if (session.id === currentSessionId) {
        const updatedMessages = [...session.messages, newMessage].slice(-MAX_MESSAGES_PER_SESSION)
        
        return {
          ...session,
          messages: updatedMessages,
          updated_at: new Date(),
          // Auto-update session title based on first user message
          title: session.messages.length === 0 && message.type === 'user' 
            ? message.content.slice(0, 60) + (message.content.length > 60 ? '...' : '')
            : session.title
        }
      }
      return session
    }))

    return newMessage
  }

  const sendMessage = async (query: string) => {
    setIsLoading(true)
    
    try {
      // Add user message
      await addMessage({
        type: 'user',
        content: query
      })

      // Get AI response using the existing API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
      })

      if (!response.ok) {
        throw new Error('Failed to get AI response')
      }

      const data = await response.json()

      // Add assistant message
      await addMessage({
        type: 'assistant',
        content: data.answer || 'Entschuldigung, ich konnte keine passende Antwort finden.',
        sources: data.sources,
        confidence_score: data.confidence_score ? Math.round(data.confidence_score * 100) : undefined,
        processing_time: data.processing_time
      })

    } catch (error) {
      console.error('Error sending message:', error)
      
      await addMessage({
        type: 'assistant',
        content: 'Es tut mir leid, es gab einen Fehler bei der Verarbeitung deiner Anfrage.'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const switchToSession = (sessionId: string) => {
    setCurrentSessionId(sessionId)
  }

  const deleteSession = (sessionId: string) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null)
    }
  }

  const updateSessionTitle = (sessionId: string, newTitle: string) => {
    setSessions(prev => prev.map(session => 
      session.id === sessionId 
        ? { ...session, title: newTitle, updated_at: new Date() }
        : session
    ))
  }

  const clearHistory = () => {
    setSessions([])
    setCurrentSessionId(null)
    localStorage.removeItem(STORAGE_KEY)
  }

  const searchSessions = (query: string): EnterpriseChatSession[] => {
    if (!query.trim()) return sessions

    const lowerQuery = query.toLowerCase()
    return sessions.filter(session => 
      session.title.toLowerCase().includes(lowerQuery) ||
      session.messages.some(msg => 
        msg.content.toLowerCase().includes(lowerQuery)
      )
    )
  }

  const getStats = () => {
    const totalMessages = sessions.reduce((sum, session) => sum + session.messages.length, 0)
    const totalSessions = sessions.length
    const avgMessagesPerSession = totalSessions > 0 ? Math.round(totalMessages / totalSessions) : 0
    
    return {
      totalSessions,
      totalMessages,
      avgMessagesPerSession,
      oldestSession: sessions.length > 0 ? sessions[sessions.length - 1].created_at : null,
      newestSession: sessions.length > 0 ? sessions[0].created_at : null,
      user_id: userId
    }
  }

  return {
    sessions,
    currentSessionId,
    currentSession: getCurrentSession(),
    isLoading,
    createSession,
    addMessage,
    sendMessage,
    switchToSession,
    deleteSession,
    updateSessionTitle,
    clearHistory,
    searchSessions,
    getStats
  }
}