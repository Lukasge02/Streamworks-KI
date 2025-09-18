/**
 * Simple Chat Store using Zustand
 * Basic chat functionality without XML complexity
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// ================================
// TYPES
// ================================

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

// ================================
// STATE
// ================================

interface ChatState {
  // Session management
  sessions: ChatSession[]
  currentSessionId: string | null

  // UI state
  loading: boolean
  error: string | null
  sendingMessage: boolean

  // AI Provider
  aiProvider: 'local' | 'cloud'
}

// ================================
// ACTIONS
// ================================

interface ChatActions {
  // Session management
  setSessions: (sessions: ChatSession[]) => void
  setCurrentSession: (sessionId: string | null) => void
  createSession: () => string
  deleteSession: (sessionId: string) => void

  // Message management
  addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  clearMessages: (sessionId: string) => void

  // AI Provider
  setAiProvider: (provider: 'local' | 'cloud') => void

  // Loading states
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setSendingMessage: (sending: boolean) => void

  // Utils
  getCurrentSession: () => ChatSession | null
  getCurrentMessages: () => ChatMessage[]
  generateMessageId: () => string
}

// ================================
// ZUSTAND STORE
// ================================

export const useChatStore = create<ChatState & ChatActions>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Initial state
        sessions: [],
        currentSessionId: null,
        loading: false,
        error: null,
        sendingMessage: false,
        aiProvider: 'local',

        // Session management
        setSessions: (sessions) =>
          set((state) => {
            state.sessions = sessions
          }),

        setCurrentSession: (sessionId) =>
          set((state) => {
            state.currentSessionId = sessionId
          }),

        createSession: () => {
          const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

          set((state) => {
            const newSession: ChatSession = {
              id: newSessionId,
              title: `Chat ${new Date().toLocaleDateString()}`,
              messages: [],
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString()
            }

            state.sessions.unshift(newSession)
            state.currentSessionId = newSessionId
          })

          return newSessionId
        },

        deleteSession: (sessionId) =>
          set((state) => {
            state.sessions = state.sessions.filter((s) => s.id !== sessionId)
            if (state.currentSessionId === sessionId) {
              state.currentSessionId = state.sessions[0]?.id || null
            }
          }),

        // Message management
        addMessage: (sessionId, messageData) =>
          set((state) => {
            const session = state.sessions.find((s) => s.id === sessionId)
            if (session) {
              const newMessage: ChatMessage = {
                ...messageData,
                id: get().generateMessageId(),
                timestamp: new Date().toISOString()
              }

              session.messages.push(newMessage)
              session.updatedAt = new Date().toISOString()

              // Update title based on first user message
              if (messageData.type === 'user' && session.messages.length === 1) {
                session.title = messageData.content.slice(0, 50) + (messageData.content.length > 50 ? '...' : '')
              }
            }
          }),

        clearMessages: (sessionId) =>
          set((state) => {
            const session = state.sessions.find((s) => s.id === sessionId)
            if (session) {
              session.messages = []
              session.updatedAt = new Date().toISOString()
            }
          }),

        // AI Provider
        setAiProvider: (provider) =>
          set((state) => {
            state.aiProvider = provider
          }),

        // Loading states
        setLoading: (loading) =>
          set((state) => {
            state.loading = loading
          }),

        setError: (error) =>
          set((state) => {
            state.error = error
          }),

        setSendingMessage: (sending) =>
          set((state) => {
            state.sendingMessage = sending
          }),

        // Utils
        getCurrentSession: () => {
          const state = get()
          return state.sessions.find((s) => s.id === state.currentSessionId) || null
        },

        getCurrentMessages: () => {
          const currentSession = get().getCurrentSession()
          return currentSession?.messages || []
        },

        generateMessageId: () => {
          return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        },
      })),
      {
        name: 'chat-store',
        partialize: (state) => ({
          sessions: state.sessions,
          currentSessionId: state.currentSessionId,
          aiProvider: state.aiProvider,
        }),
      }
    ),
    {
      name: 'StreamworksChatStore',
    }
  )
)

// ================================
// SELECTORS
// ================================

export const useChatSelectors = () => {
  const store = useChatStore()

  return {
    // Basic selectors
    sessions: store.sessions,
    currentSession: store.getCurrentSession(),
    currentMessages: store.getCurrentMessages(),
    loading: store.loading,
    error: store.error,
    sendingMessage: store.sendingMessage,
    aiProvider: store.aiProvider,

    // Computed selectors
    hasActiveSessions: store.sessions.length > 0,
    currentSessionTitle: store.getCurrentSession()?.title || 'Neuer Chat',
    sessionCount: store.sessions.length,
  }
}