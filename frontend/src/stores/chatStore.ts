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
  id?: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
  session_id: string
  sources?: any[]
  confidence_score?: number
  processing_time?: number
  model_info?: any
}

export interface ChatSession {
  id: string
  title: string
  user_id: string
  message_count: number
  created_at: string
  updated_at: string
  is_active: boolean
}

// ================================
// STATE
// ================================

interface ChatState {
  // Session management
  sessions: ChatSession[]
  currentSessionId: string | null
  messages: Record<string, ChatMessage[]>

  // UI state
  loading: boolean
  loadingSessions: boolean
  loadingMessages: Record<string, boolean>
  error: string | null
  sendingMessage: boolean

  // AI Provider
  aiProvider: 'local' | 'cloud'

  // Floating Chat Widget
  isFloatingChatOpen: boolean
  hasUnreadMessages: boolean
}

// ================================
// ACTIONS
// ================================

interface ChatActions {
  // Session management
  setSessions: (sessions: ChatSession[]) => void
  setCurrentSession: (sessionId: string | null) => void
  createSession: (session: ChatSession) => string
  deleteSession: (sessionId: string) => void

  // Message management
  setMessages: (sessionId: string, messages: ChatMessage[]) => void
  addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  clearMessages: (sessionId: string) => void

  // AI Provider
  setAiProvider: (provider: 'local' | 'cloud') => void

  // Loading states
  setLoading: (loading: boolean) => void
  setLoadingSessions: (loading: boolean) => void
  setLoadingMessages: (sessionId: string, loading: boolean) => void
  setError: (error: string | null) => void
  setSendingMessage: (sending: boolean) => void

  // Floating Chat Widget
  setFloatingChatOpen: (open: boolean) => void
  setHasUnreadMessages: (hasUnread: boolean) => void
  toggleFloatingChat: () => void

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
        messages: {},
        loading: false,
        loadingSessions: false,
        loadingMessages: {},
        error: null,
        sendingMessage: false,
        aiProvider: 'local',
        isFloatingChatOpen: false,
        hasUnreadMessages: false,

        // Session management
        setSessions: (sessions) =>
          set((state) => {
            state.sessions = sessions
          }),

        setCurrentSession: (sessionId) =>
          set((state) => {
            state.currentSessionId = sessionId
          }),

        createSession: (session) => {
          set((state) => {
            state.sessions.unshift(session)
            state.currentSessionId = session.id
            state.messages[session.id] = []
          })

          return session.id
        },

        deleteSession: (sessionId) =>
          set((state) => {
            state.sessions = state.sessions.filter((s) => s.id !== sessionId)
            delete state.messages[sessionId]
            delete state.loadingMessages[sessionId]
            if (state.currentSessionId === sessionId) {
              state.currentSessionId = state.sessions[0]?.id || null
            }
          }),

        // Message management
        setMessages: (sessionId, messages) =>
          set((state) => {
            state.messages[sessionId] = messages
          }),

        addMessage: (sessionId, messageData) =>
          set((state) => {
            if (!state.messages[sessionId]) {
              state.messages[sessionId] = []
            }

            const newMessage: ChatMessage = {
              ...messageData,
              id: get().generateMessageId(),
              timestamp: new Date().toISOString()
            }

            state.messages[sessionId].push(newMessage)

            // Update session if it exists
            const session = state.sessions.find((s) => s.id === sessionId)
            if (session) {
              session.updated_at = new Date().toISOString()
              session.message_count = state.messages[sessionId].length

              // Update title based on first user message
              if (messageData.type === 'user' && state.messages[sessionId].length === 1) {
                session.title = messageData.content.slice(0, 50) + (messageData.content.length > 50 ? '...' : '')
              }
            }
          }),

        clearMessages: (sessionId) =>
          set((state) => {
            state.messages[sessionId] = []
            const session = state.sessions.find((s) => s.id === sessionId)
            if (session) {
              session.updated_at = new Date().toISOString()
              session.message_count = 0
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

        setLoadingSessions: (loading) =>
          set((state) => {
            state.loadingSessions = loading
          }),

        setLoadingMessages: (sessionId, loading) =>
          set((state) => {
            state.loadingMessages[sessionId] = loading
          }),

        setError: (error) =>
          set((state) => {
            state.error = error
          }),

        setSendingMessage: (sending) =>
          set((state) => {
            state.sendingMessage = sending
          }),

        // Floating Chat Widget
        setFloatingChatOpen: (open) =>
          set((state) => {
            state.isFloatingChatOpen = open
            if (open) {
              state.hasUnreadMessages = false
            }
          }),

        setHasUnreadMessages: (hasUnread) =>
          set((state) => {
            state.hasUnreadMessages = hasUnread
          }),

        toggleFloatingChat: () =>
          set((state) => {
            state.isFloatingChatOpen = !state.isFloatingChatOpen
            if (state.isFloatingChatOpen) {
              state.hasUnreadMessages = false
            }
          }),

        // Utils
        getCurrentSession: () => {
          const state = get()
          return state.sessions.find((s) => s.id === state.currentSessionId) || null
        },

        getCurrentMessages: () => {
          const state = get()
          return state.currentSessionId ? state.messages[state.currentSessionId] || [] : []
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
          messages: state.messages,
          aiProvider: state.aiProvider,
          isFloatingChatOpen: state.isFloatingChatOpen,
          hasUnreadMessages: state.hasUnreadMessages,
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
  const currentMessages = store.getCurrentMessages()

  return {
    // Basic selectors
    sessions: store.sessions,
    currentSession: store.getCurrentSession(),
    currentMessages,
    loading: store.loading,
    loadingSessions: store.loadingSessions,
    error: store.error,
    sendingMessage: store.sendingMessage,
    isSendingMessage: store.sendingMessage,
    aiProvider: store.aiProvider,

    // Floating Chat Widget selectors
    isFloatingChatOpen: store.isFloatingChatOpen,
    hasUnreadMessages: store.hasUnreadMessages,

    // Computed selectors
    hasActiveSessions: store.sessions.length > 0,
    currentSessionTitle: store.getCurrentSession()?.title || 'Neuer Chat',
    sessionCount: store.sessions.length,
    totalMessages: Object.values(store.messages).reduce((total, msgs) => total + msgs.length, 0),

    // UI state selectors
    isAnyLoading: store.loading || store.loadingSessions || store.sendingMessage,
    canSendMessage: !store.sendingMessage && !store.loading,
    shouldShowEmptyState: store.sessions.length === 0 && !store.loadingSessions,
  }
}