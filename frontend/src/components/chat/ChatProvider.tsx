/**
 * Modern Chat Provider
 * Manages chat data loading, real-time sync, and business logic
 * Clean separation from UI components
 */

'use client'

import React, { createContext, useContext, useEffect, ReactNode } from 'react'
import { useChatStore } from '../../stores/chatStore'
import { modernChatService } from '../../services/modernChatService'

// ================================
// CONTEXT
// ================================

interface ChatContextType {
  // Business logic methods
  loadSessions: () => Promise<void>
  loadMessages: (sessionId: string) => Promise<void>
  createNewSession: (title?: string) => Promise<string>
  sendMessage: (query: string) => Promise<void>
  switchSession: (sessionId: string) => Promise<void>
  deleteSessionById: (sessionId: string) => Promise<void>
  
  // Utilities
  refreshData: () => Promise<void>
  checkHealth: () => Promise<void>
}

const ChatContext = createContext<ChatContextType | null>(null)

// ================================
// PROVIDER COMPONENT
// ================================

interface ChatProviderProps {
  children: ReactNode
  userId?: string
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ 
  children, 
  userId = 'default-user' 
}) => {
  const {
    sessions,
    currentSessionId,
    aiProvider,
    setLoading,
    setError,
    setLoadingSessions,
    setLoadingMessages,
    setSendingMessage,
    setSessions,
    setMessages,
    setCurrentSession,
    createSession,
    addMessage,
    deleteSession,
  } = useChatStore()

  // Set user ID in service
  useEffect(() => {
    modernChatService.setUserId(userId)
  }, [userId])

  // ================================
  // BUSINESS LOGIC METHODS
  // ================================

  const loadSessions = async (): Promise<void> => {
    try {
      setLoadingSessions(true)
      setError(null)
      
      const response = await modernChatService.getSessions()
      setSessions(response.sessions)
      
      // Auto-select first session if none selected
      if (!currentSessionId && response.sessions.length > 0) {
        setCurrentSession(response.sessions[0].id)
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load sessions'
      setError(errorMessage)
      console.error('Failed to load sessions:', error)
    } finally {
      setLoadingSessions(false)
    }
  }

  const loadMessages = async (sessionId: string): Promise<void> => {
    try {
      setLoadingMessages(sessionId, true)
      setError(null)
      
      const response = await modernChatService.getSessionMessages(sessionId)
      setMessages(sessionId, response.messages)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load messages'
      setError(errorMessage)
      console.error('Failed to load messages:', error)
    } finally {
      setLoadingMessages(sessionId, false)
    }
  }

  const createNewSession = async (title: string = 'Neue Unterhaltung'): Promise<string> => {
    try {
      setLoading(true)
      setError(null)
      
      // Create in backend - this returns the authoritative session with UUID
      const newSession = await modernChatService.createSession({ title, user_id: userId })
      
      // Add to local store using backend's session ID (no duplicate creation)
      const now = new Date().toISOString()
      const storeSession = {
        id: newSession.id,
        title: newSession.title,
        user_id: newSession.user_id,
        message_count: newSession.message_count,
        created_at: newSession.created_at,
        updated_at: newSession.updated_at,
        is_active: newSession.is_active,
      }
      
      // Update store state directly (don't create new ID)
      setSessions([storeSession, ...sessions])
      setCurrentSession(newSession.id)
      setMessages(newSession.id, [])
      
      return newSession.id
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create session'
      setError(errorMessage)
      console.error('Failed to create session:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async (query: string): Promise<void> => {
    try {
      setSendingMessage(true)
      setError(null)

      // Auto-create session if none exists
      let sessionId = currentSessionId
      if (!sessionId) {
        sessionId = await createNewSession()
      }

      // Add user message immediately to UI
      addMessage(sessionId, {
        type: 'user',
        content: query,
        session_id: sessionId,
      })

      // Send to AI service
      const response = await modernChatService.sendMessage({
        session_id: sessionId,
        query,
        provider: aiProvider,
        mode: 'accurate',
      })

      // Add AI response to UI
      addMessage(sessionId, {
        type: 'assistant',
        content: response.answer,
        session_id: sessionId,
        sources: response.sources,
        confidence_score: response.confidence_score,
        processing_time: response.processing_time,
        model_info: response.model_info,
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message'
      setError(errorMessage)

      // Add error message to UI
      const sessionId = currentSessionId
      if (sessionId) {
        addMessage(sessionId, {
          type: 'assistant',
          content: `Es tut mir leid, es gab einen Fehler: ${errorMessage}`,
          session_id: sessionId,
        })
      }

      console.error('Failed to send message:', error)
    } finally {
      setSendingMessage(false)
    }
  }

  const switchSession = async (sessionId: string): Promise<void> => {
    try {
      setCurrentSession(sessionId)

      // Load messages if not already loaded
      const store = useChatStore.getState()
      if (!store.messages || !store.messages[sessionId]) {
        await loadMessages(sessionId)
      }
    } catch (error) {
      console.error('Failed to switch session:', error)
    }
  }

  const deleteSessionById = async (sessionId: string): Promise<void> => {
    try {
      setLoading(true)
      
      // Delete from backend
      await modernChatService.deleteSession(sessionId)
      
      // Delete from local store
      deleteSession(sessionId)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete session'
      setError(errorMessage)
      console.error('Failed to delete session:', error)
    } finally {
      setLoading(false)
    }
  }

  // ================================
  // UTILITIES
  // ================================

  const refreshData = async (): Promise<void> => {
    await loadSessions()
    if (currentSessionId) {
      await loadMessages(currentSessionId)
    }
  }

  const checkHealth = async (): Promise<void> => {
    try {
      const health = await modernChatService.checkHealth()
      console.log('Health check:', health)
    } catch (error) {
      console.error('Health check failed:', error)
    }
  }

  // ================================
  // INITIALIZATION
  // ================================

  useEffect(() => {
    // Load sessions on mount
    loadSessions()
    
    // Check health periodically
    const healthInterval = setInterval(checkHealth, 60000) // Every minute
    
    return () => clearInterval(healthInterval)
  }, [])

  // Load messages when session switches
  useEffect(() => {
    if (currentSessionId) {
      const store = useChatStore.getState()
      if (!store.messages || !store.messages[currentSessionId]) {
        loadMessages(currentSessionId)
      }
    }
  }, [currentSessionId])

  // ================================
  // CONTEXT VALUE
  // ================================

  const contextValue: ChatContextType = {
    loadSessions,
    loadMessages,
    createNewSession,
    sendMessage,
    switchSession,
    deleteSessionById,
    refreshData,
    checkHealth,
  }

  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  )
}

// ================================
// HOOK
// ================================

export const useChatContext = (): ChatContextType => {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider')
  }
  return context
}

export default ChatProvider