/**
 * Modern Chat Store using Zustand
 * Single Source of Truth for all chat state
 * Replaces complex localStorage + Supabase hybrid approach
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// ================================
// TYPES
// ================================

export interface ChatMessage {
  id: string
  session_id: string
  type: 'user' | 'assistant'
  content: string
  sources?: ChatSource[]
  confidence_score?: number
  processing_time?: string
  model_info?: string
  created_at: string
  sequence_number: number
}

export interface ChatSource {
  id: string
  metadata: {
    doc_id?: string
    original_filename?: string
    page_number?: number
    heading?: string
    section?: string
  }
  relevance_score?: number
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

export interface ChatState {
  // Current state
  sessions: ChatSession[]
  currentSessionId: string | null
  messages: Record<string, ChatMessage[]> // sessionId -> messages
  
  // UI state
  isLoading: boolean
  error: string | null
  aiProvider: 'local' | 'cloud'
  
  // Loading states
  isLoadingSessions: boolean
  isLoadingMessages: Record<string, boolean>
  isSendingMessage: boolean
}

export interface ChatActions {
  // Session management
  setSessions: (sessions: ChatSession[]) => void
  setCurrentSession: (sessionId: string | null) => void
  createSession: (title: string) => Promise<string>
  updateSessionTitle: (sessionId: string, title: string) => void
  deleteSession: (sessionId: string) => void
  
  // Message management
  setMessages: (sessionId: string, messages: ChatMessage[]) => void
  addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'created_at' | 'sequence_number'>) => void
  clearMessages: (sessionId: string) => void
  
  // AI Provider
  setAiProvider: (provider: 'local' | 'cloud') => void
  
  // Loading states
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setLoadingSessions: (loading: boolean) => void
  setLoadingMessages: (sessionId: string, loading: boolean) => void
  setSendingMessage: (sending: boolean) => void
  
  // Utils
  getCurrentMessages: () => ChatMessage[]
  getCurrentSession: () => ChatSession | null
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
        isLoading: false,
        error: null,
        aiProvider: 'local', // Default to local AI
        isLoadingSessions: false,
        isLoadingMessages: {},
        isSendingMessage: false,

        // Session management
        setSessions: (sessions) =>
          set((state) => {
            state.sessions = sessions
          }),

        setCurrentSession: (sessionId) =>
          set((state) => {
            state.currentSessionId = sessionId
          }),

        createSession: async (title) => {
          const sessionId = crypto.randomUUID()
          const now = new Date().toISOString()
          
          const newSession: ChatSession = {
            id: sessionId,
            title,
            user_id: 'default-user',
            message_count: 0,
            created_at: now,
            updated_at: now,
            is_active: true,
          }

          set((state) => {
            state.sessions.unshift(newSession)
            state.currentSessionId = sessionId
            state.messages[sessionId] = []
          })

          return sessionId
        },

        updateSessionTitle: (sessionId, title) =>
          set((state) => {
            const session = state.sessions.find((s) => s.id === sessionId)
            if (session) {
              session.title = title
              session.updated_at = new Date().toISOString()
            }
          }),

        deleteSession: (sessionId) =>
          set((state) => {
            state.sessions = state.sessions.filter((s) => s.id !== sessionId)
            delete state.messages[sessionId]
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
            const messageId = get().generateMessageId()
            const now = new Date().toISOString()
            const existingMessages = state.messages[sessionId] || []
            
            const newMessage: ChatMessage = {
              ...messageData,
              id: messageId,
              session_id: sessionId,
              created_at: now,
              sequence_number: existingMessages.length + 1,
            }

            state.messages[sessionId] = [...existingMessages, newMessage]
            
            // Update session message count and title
            const session = state.sessions.find((s) => s.id === sessionId)
            if (session) {
              session.message_count = state.messages[sessionId].length
              session.updated_at = now
              
              // Auto-generate title from first user message
              if (messageData.type === 'user' && session.message_count === 1) {
                session.title = messageData.content.slice(0, 50) + 
                  (messageData.content.length > 50 ? '...' : '')
              }
            }
          }),

        clearMessages: (sessionId) =>
          set((state) => {
            state.messages[sessionId] = []
            const session = state.sessions.find((s) => s.id === sessionId)
            if (session) {
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
            state.isLoading = loading
          }),

        setError: (error) =>
          set((state) => {
            state.error = error
          }),

        setLoadingSessions: (loading) =>
          set((state) => {
            state.isLoadingSessions = loading
          }),

        setLoadingMessages: (sessionId, loading) =>
          set((state) => {
            state.isLoadingMessages[sessionId] = loading
          }),

        setSendingMessage: (sending) =>
          set((state) => {
            state.isSendingMessage = sending
          }),

        // Utils
        getCurrentMessages: () => {
          const state = get()
          return state.currentSessionId ? state.messages[state.currentSessionId] || [] : []
        },

        getCurrentSession: () => {
          const state = get()
          return state.sessions.find((s) => s.id === state.currentSessionId) || null
        },

        generateMessageId: () => {
          return crypto.randomUUID()
        },
      })),
      {
        name: 'streamworks-chat-store',
        // Only persist essential data, not loading states
        partialize: (state) => ({
          currentSessionId: state.currentSessionId,
          aiProvider: state.aiProvider,
        }),
      }
    ),
    {
      name: 'StreamWorks Chat Store',
    }
  )
)

// ================================
// COMPUTED SELECTORS
// ================================

export const useChatSelectors = () => {
  const store = useChatStore()
  
  return {
    // Basic selectors
    currentSession: store.getCurrentSession(),
    currentMessages: store.getCurrentMessages(),
    hasActiveSessions: store.sessions.length > 0,
    isAnyLoading: store.isLoading || store.isLoadingSessions || store.isSendingMessage,
    
    // Computed values
    sessionCount: store.sessions.length,
    totalMessages: Object.values(store.messages).reduce((sum, msgs) => sum + msgs.length, 0),
    
    // UI state helpers
    canSendMessage: !store.isSendingMessage && store.currentSessionId !== null,
    shouldShowEmptyState: store.sessions.length === 0 && !store.isLoadingSessions,
  }
}