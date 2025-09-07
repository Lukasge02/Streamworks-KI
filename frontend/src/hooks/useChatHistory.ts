import { useState, useEffect } from 'react'
import { createDefaultSessionTitle } from '../utils/timeUtils'

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: any[]
  confidence_score?: number
  processing_time?: string
  session_id?: string
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  created_at: Date
  updated_at: Date
}

const STORAGE_KEY = 'streamworks_chat_history'
const MAX_SESSIONS = 50
const MAX_MESSAGES_PER_SESSION = 100

export const useChatHistory = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [draftSession, setDraftSession] = useState<ChatSession | null>(null)

  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem(STORAGE_KEY)
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory)
        const sessionsWithDates = parsed.map((session: any) => ({
          ...session,
          created_at: new Date(session.created_at),
          updated_at: new Date(session.updated_at),
          messages: session.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        }))
        setSessions(sessionsWithDates)
      } catch (error) {
        console.error('Failed to load chat history:', error)
      }
    }
  }, [])

  // Save to localStorage whenever sessions change (but not draft sessions)
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
    }
  }, [sessions])

  const createSession = (title?: string, saveImmediately: boolean = false): string => {
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const now = new Date()
    const defaultTitle = title || createDefaultSessionTitle()
    
    const newSession: ChatSession = {
      id: sessionId,
      title: defaultTitle,
      messages: [],
      created_at: now,
      updated_at: now
    }

    if (saveImmediately) {
      // Save to persistent sessions immediately
      setSessions(prev => {
        // Keep only the most recent sessions
        const updated = [newSession, ...prev].slice(0, MAX_SESSIONS)
        return updated
      })
      setDraftSession(null)
    } else {
      // Create as draft session (not saved to localStorage yet)
      setDraftSession(newSession)
    }
    
    setCurrentSessionId(sessionId)
    return sessionId
  }

  const getCurrentSession = (): ChatSession | null => {
    if (!currentSessionId) return null
    // Check draft session first, then saved sessions
    if (draftSession && draftSession.id === currentSessionId) {
      return draftSession
    }
    return sessions.find(s => s.id === currentSessionId) || null
  }

  const addMessage = (message: Omit<ChatMessage, 'id'>) => {
    if (!currentSessionId) {
      const newSessionId = createSession(undefined, false) // Create as draft first
      setCurrentSessionId(newSessionId)
    }

    const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const newMessage: ChatMessage = {
      ...message,
      id: messageId,
      session_id: currentSessionId!
    }

    // If this is the first user message and we have a draft session, save it to persistent storage
    if (draftSession && draftSession.id === currentSessionId && message.type === 'user' && draftSession.messages.length === 0) {
      // This is the first user message - save the draft session to persistent storage
      const updatedMessages = [newMessage]
      const finalSession: ChatSession = {
        ...draftSession,
        messages: updatedMessages,
        updated_at: new Date(),
        title: message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
      }
      
      setSessions(prev => {
        const updated = [finalSession, ...prev].slice(0, MAX_SESSIONS)
        return updated
      })
      setDraftSession(null)
      return
    }

    // Update existing session (either draft or saved)
    if (draftSession && draftSession.id === currentSessionId) {
      // Update draft session
      const updatedMessages = [...draftSession.messages, newMessage].slice(-MAX_MESSAGES_PER_SESSION)
      setDraftSession({
        ...draftSession,
        messages: updatedMessages,
        updated_at: new Date()
      })
    } else {
      // Update saved session
      setSessions(prev => prev.map(session => {
        if (session.id === currentSessionId) {
          const updatedMessages = [...session.messages, newMessage].slice(-MAX_MESSAGES_PER_SESSION)
          
          return {
            ...session,
            messages: updatedMessages,
            updated_at: new Date(),
            // Auto-update session title based on first user message
            title: session.messages.length === 0 && message.type === 'user' 
              ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
              : session.title
          }
        }
        return session
      }))
    }
  }

  const deleteSession = (sessionId: string) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (draftSession && draftSession.id === sessionId) {
      setDraftSession(null)
    }
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null)
    }
  }

  const clearHistory = () => {
    setSessions([])
    setDraftSession(null)
    setCurrentSessionId(null)
    localStorage.removeItem(STORAGE_KEY)
  }

  const switchToSession = (sessionId: string) => {
    setCurrentSessionId(sessionId)
  }

  const updateSessionTitle = (sessionId: string, newTitle: string) => {
    if (draftSession && draftSession.id === sessionId) {
      setDraftSession({
        ...draftSession,
        title: newTitle,
        updated_at: new Date()
      })
    } else {
      setSessions(prev => prev.map(session => 
        session.id === sessionId 
          ? { ...session, title: newTitle, updated_at: new Date() }
          : session
      ))
    }
  }

  const searchSessions = (query: string): ChatSession[] => {
    const allSessions = draftSession ? [draftSession, ...sessions] : sessions
    if (!query.trim()) return allSessions

    const lowerQuery = query.toLowerCase()
    return allSessions.filter(session => 
      session.title.toLowerCase().includes(lowerQuery) ||
      session.messages.some(msg => 
        msg.content.toLowerCase().includes(lowerQuery)
      )
    )
  }

  const getSessionStats = () => {
    const allSessions = draftSession ? [draftSession, ...sessions] : sessions
    const totalMessages = allSessions.reduce((sum, session) => sum + session.messages.length, 0)
    const totalSessions = allSessions.length
    const avgMessagesPerSession = totalSessions > 0 ? Math.round(totalMessages / totalSessions) : 0
    
    return {
      totalSessions,
      totalMessages,
      avgMessagesPerSession,
      oldestSession: allSessions.length > 0 ? allSessions[allSessions.length - 1].created_at : null,
      newestSession: allSessions.length > 0 ? allSessions[0].created_at : null
    }
  }

  // Get all sessions (including draft) for sidebar display
  const getAllSessions = (): ChatSession[] => {
    return draftSession ? [draftSession, ...sessions] : sessions
  }

  return {
    sessions: getAllSessions(), // Return all sessions including draft for sidebar
    currentSessionId,
    currentSession: getCurrentSession(),
    createSession,
    addMessage,
    deleteSession,
    clearHistory,
    switchToSession,
    updateSessionTitle,
    searchSessions,
    getSessionStats
  }
}