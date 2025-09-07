'use client'

import { useState, useEffect } from 'react'

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: any[]
  confidence_score?: number
  processing_time?: string
  model_info?: string
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  created_at: Date
  updated_at: Date
}

const STORAGE_KEY = 'streamworks_chat_sessions'
const STORAGE_BACKUP_KEY = 'streamworks_chat_sessions_backup'
const MAX_SESSIONS = 50
const MAX_MESSAGES = 100
const MAX_STORAGE_SIZE = 4 * 1024 * 1024 // 4MB limit to stay safe

export function useChatStorage() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)

  // Load from localStorage on mount with error recovery
  useEffect(() => {
    const loadSessions = () => {
      try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) {
          const parsed = JSON.parse(saved)
          // Validate data structure
          if (Array.isArray(parsed)) {
            const sessionsWithDates = parsed.map((session: any) => ({
              ...session,
              created_at: new Date(session.created_at),
              updated_at: new Date(session.updated_at),
              messages: session.messages?.map((msg: any) => ({
                ...msg,
                timestamp: new Date(msg.timestamp)
              })) || []
            }))
            setSessions(sessionsWithDates)
            return true
          }
        }
        return false
      } catch (error) {
        console.error('Failed to load chat sessions:', error)
        return false
      }
    }

    // Try main storage first, then backup
    if (!loadSessions()) {
      try {
        console.log('Attempting to restore from backup...')
        const backup = localStorage.getItem(STORAGE_BACKUP_KEY)
        if (backup) {
          localStorage.setItem(STORAGE_KEY, backup)
          loadSessions()
        } else {
          setSessions([])
        }
      } catch (error) {
        console.error('Failed to restore from backup:', error)
        setSessions([])
      }
    }
  }, [])

  // Save to localStorage whenever sessions change with error recovery
  useEffect(() => {
    if (sessions.length === 0) return // Don't save empty array on first load
    
    const saveData = () => {
      try {
        const dataString = JSON.stringify(sessions)
        
        // Check if data is too large
        if (dataString.length > MAX_STORAGE_SIZE) {
          console.warn('Chat data exceeding storage limit, cleaning up...')
          // Remove oldest sessions until under limit
          const limitedSessions = sessions.slice(0, Math.floor(MAX_SESSIONS * 0.8))
          const limitedString = JSON.stringify(limitedSessions)
          
          if (limitedString.length <= MAX_STORAGE_SIZE) {
            localStorage.setItem(STORAGE_KEY, limitedString)
            setSessions(limitedSessions)
            return true
          }
        } else {
          // Create backup before saving
          const currentData = localStorage.getItem(STORAGE_KEY)
          if (currentData) {
            localStorage.setItem(STORAGE_BACKUP_KEY, currentData)
          }
          
          localStorage.setItem(STORAGE_KEY, dataString)
          return true
        }
      } catch (error) {
        if (error instanceof DOMException && error.name === 'QuotaExceededError') {
          console.error('Storage quota exceeded, cleaning up older sessions...')
          // Emergency cleanup - keep only recent sessions
          const emergencySessions = sessions.slice(0, 20)
          try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(emergencySessions))
            setSessions(emergencySessions)
            return true
          } catch (cleanupError) {
            console.error('Even emergency cleanup failed:', cleanupError)
          }
        } else {
          console.error('Failed to save chat sessions:', error)
        }
      }
      return false
    }
    
    saveData()
  }, [sessions])

  const createNewSession = (): string => {
    const sessionId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const now = new Date()
    
    const newSession: ChatSession = {
      id: sessionId,
      title: `Neue Unterhaltung`,
      messages: [],
      created_at: now,
      updated_at: now
    }

    setSessions(prev => [newSession, ...prev].slice(0, MAX_SESSIONS))
    setCurrentSessionId(sessionId)
    return sessionId
  }

  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>): void => {
    // Ensure we have a current session
    const targetSessionId = currentSessionId || createNewSession()

    const newMessage: ChatMessage = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    }

    setSessions(prev => {
      // If this is a new session that was just created, add it to the list
      const existingSessionIndex = prev.findIndex(s => s.id === targetSessionId)
      
      if (existingSessionIndex === -1) {
        // Session doesn't exist, this shouldn't happen but let's handle it
        console.error('Session not found:', targetSessionId)
        return prev
      }
      
      return prev.map(session => {
      if (session.id === targetSessionId) {
        const updatedMessages = [...session.messages, newMessage].slice(-MAX_MESSAGES)
        
        // Update title with first user message only
        const newTitle = session.messages.length === 0 && message.type === 'user' 
          ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
          : session.title

        return {
          ...session,
          messages: updatedMessages,
          title: newTitle,
          updated_at: new Date()
        }
      }
      return session
      })
    })
  }

  const getCurrentSession = (): ChatSession | null => {
    return sessions.find(s => s.id === currentSessionId) || null
  }

  const switchToSession = (sessionId: string): void => {
    setCurrentSessionId(sessionId)
  }

  const deleteSession = (sessionId: string): void => {
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null)
    }
  }

  const clearAllSessions = (): void => {
    setSessions([])
    setCurrentSessionId(null)
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(STORAGE_BACKUP_KEY)
  }

  const cleanupEmptySessions = (): void => {
    setSessions(prev => {
      const cleanedSessions = prev.filter(session => session.messages.length > 0)
      return cleanedSessions
    })
  }

  const searchSessions = (query: string): ChatSession[] => {
    if (!query.trim()) return sessions
    
    const lowerQuery = query.toLowerCase().trim()
    return sessions.filter(session => {
      // Search in session title
      if (session.title.toLowerCase().includes(lowerQuery)) {
        return true
      }
      
      // Search in message content
      return session.messages.some(msg => 
        msg.content.toLowerCase().includes(lowerQuery)
      )
    })
  }

  const getSessionStats = () => {
    const totalMessages = sessions.reduce((sum, session) => sum + session.messages.length, 0)
    const totalSessions = sessions.length
    const avgMessagesPerSession = totalSessions > 0 ? Math.round(totalMessages / totalSessions) : 0
    const storageUsed = JSON.stringify(sessions).length
    
    return {
      totalSessions,
      totalMessages,
      avgMessagesPerSession,
      storageUsed,
      storagePercent: Math.round((storageUsed / MAX_STORAGE_SIZE) * 100),
      oldestSession: sessions.length > 0 ? sessions[sessions.length - 1].created_at : null,
      newestSession: sessions.length > 0 ? sessions[0].created_at : null
    }
  }

  const exportSessions = (): string => {
    const exportData = {
      version: '1.0',
      exportDate: new Date().toISOString(),
      sessions: sessions,
      stats: getSessionStats()
    }
    return JSON.stringify(exportData, null, 2)
  }

  const importSessions = (jsonData: string): { success: boolean; message: string; imported: number } => {
    try {
      const data = JSON.parse(jsonData)
      
      // Validate structure
      if (!data.sessions || !Array.isArray(data.sessions)) {
        return { success: false, message: 'Ungültiges Datenformat: sessions array fehlt', imported: 0 }
      }
      
      // Convert dates and validate sessions
      const importedSessions = data.sessions.map((session: any, index: number) => {
        try {
          return {
            ...session,
            id: session.id || `imported_${Date.now()}_${index}`,
            created_at: new Date(session.created_at),
            updated_at: new Date(session.updated_at),
            messages: (session.messages || []).map((msg: any, msgIndex: number) => ({
              ...msg,
              id: msg.id || `msg_${Date.now()}_${msgIndex}`,
              timestamp: new Date(msg.timestamp)
            }))
          }
        } catch (sessionError) {
          console.error(`Error processing session ${index}:`, sessionError)
          return null
        }
      }).filter(Boolean) // Remove null entries
      
      if (importedSessions.length === 0) {
        return { success: false, message: 'Keine gültigen Sessions gefunden', imported: 0 }
      }
      
      // Merge with existing sessions (avoid duplicates)
      const existingIds = new Set(sessions.map(s => s.id))
      const newSessions = importedSessions.filter((s: any) => !existingIds.has(s.id))
      
      if (newSessions.length === 0) {
        return { success: false, message: 'Alle Sessions bereits vorhanden', imported: 0 }
      }
      
      // Add new sessions and sort by date
      const mergedSessions = [...newSessions, ...sessions]
        .sort((a, b) => b.updated_at.getTime() - a.updated_at.getTime())
        .slice(0, MAX_SESSIONS)
      
      setSessions(mergedSessions)
      
      return { 
        success: true, 
        message: `${newSessions.length} Sessions erfolgreich importiert`, 
        imported: newSessions.length 
      }
      
    } catch (error) {
      console.error('Import error:', error)
      return { 
        success: false, 
        message: `Import-Fehler: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`, 
        imported: 0 
      }
    }
  }

  return {
    sessions,
    currentSessionId,
    currentSession: getCurrentSession(),
    createNewSession,
    addMessage,
    switchToSession,
    deleteSession,
    clearAllSessions,
    cleanupEmptySessions,
    searchSessions,
    getSessionStats,
    exportSessions,
    importSessions
  }
}