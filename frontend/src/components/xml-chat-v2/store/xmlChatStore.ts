/**
 * XML Chat Store - Clean Zustand Implementation
 * Simple state management for the new XML chat system
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// ================================
// TYPES
// ================================

export interface XMLChatMessage {
  id: string
  sessionId: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: {
    canGenerateXML?: boolean
    type?: 'xml_generated' | 'error' | 'info'
    parameters?: Record<string, any>
  }
}

export interface XMLChatSession {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messageCount: number
  hasGeneratedXML: boolean
}

export type XMLGenerationStatus = 'idle' | 'generating' | 'success' | 'error'

interface XMLChatState {
  // Sessions
  sessions: XMLChatSession[]
  currentSession: XMLChatSession | null

  // Messages
  messages: XMLChatMessage[]

  // XML Generation
  generatedXML: string | null
  generationStatus: XMLGenerationStatus

  // UI State
  isLoading: boolean
  error: string | null
}

interface XMLChatActions {
  // Session Management
  createNewSession: (title?: string) => XMLChatSession
  switchToSession: (sessionId: string) => void
  deleteSession: (sessionId: string) => void
  updateSessionTitle: (sessionId: string, title: string) => void

  // Message Management
  addMessage: (message: XMLChatMessage) => void
  updateMessage: (messageId: string, content: string) => void
  clearMessages: () => void

  // XML Generation
  setGeneratedXML: (xml: string | null) => void
  setGenerationStatus: (status: XMLGenerationStatus) => void

  // Utility
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

type XMLChatStore = XMLChatState & XMLChatActions

// ================================
// INITIAL STATE
// ================================

const initialState: XMLChatState = {
  sessions: [],
  currentSession: null,
  messages: [],
  generatedXML: null,
  generationStatus: 'idle',
  isLoading: false,
  error: null
}

// ================================
// STORE IMPLEMENTATION
// ================================

export const useXMLChatStore = create<XMLChatStore>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialState,

        // ================================
        // SESSION MANAGEMENT
        // ================================

        createNewSession: (title?: string) => {
          const session: XMLChatSession = {
            id: crypto.randomUUID(),
            title: title || `Chat ${new Date().toLocaleDateString()}`,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            messageCount: 0,
            hasGeneratedXML: false
          }

          set((state) => {
            state.sessions.unshift(session)
            state.currentSession = session
            state.messages = []
            state.generatedXML = null
            state.generationStatus = 'idle'
            state.error = null
          })

          return session
        },

        switchToSession: (sessionId: string) => {
          set((state) => {
            const session = state.sessions.find(s => s.id === sessionId)
            if (session) {
              state.currentSession = session
              // In a real app, you'd load messages from API/storage here
              state.messages = []
              state.generatedXML = null
              state.generationStatus = 'idle'
              state.error = null
            }
          })
        },

        deleteSession: (sessionId: string) => {
          set((state) => {
            state.sessions = state.sessions.filter(s => s.id !== sessionId)

            // If we deleted the current session, switch to the first available
            if (state.currentSession?.id === sessionId) {
              state.currentSession = state.sessions[0] || null
              state.messages = []
              state.generatedXML = null
              state.generationStatus = 'idle'
            }
          })
        },

        updateSessionTitle: (sessionId: string, title: string) => {
          set((state) => {
            const session = state.sessions.find(s => s.id === sessionId)
            if (session) {
              session.title = title
              session.updatedAt = new Date().toISOString()
            }

            if (state.currentSession?.id === sessionId) {
              state.currentSession.title = title
              state.currentSession.updatedAt = new Date().toISOString()
            }
          })
        },

        // ================================
        // MESSAGE MANAGEMENT
        // ================================

        addMessage: (message: XMLChatMessage) => {
          set((state) => {
            state.messages.push(message)

            // Update session
            if (state.currentSession) {
              state.currentSession.messageCount = state.messages.length
              state.currentSession.updatedAt = new Date().toISOString()

              // Update in sessions array
              const sessionIndex = state.sessions.findIndex(s => s.id === state.currentSession?.id)
              if (sessionIndex !== -1) {
                state.sessions[sessionIndex] = { ...state.currentSession }
              }
            }
          })
        },

        updateMessage: (messageId: string, content: string) => {
          set((state) => {
            const message = state.messages.find(m => m.id === messageId)
            if (message) {
              message.content = content
              message.timestamp = new Date().toISOString()
            }
          })
        },

        clearMessages: () => {
          set((state) => {
            state.messages = []
            state.generatedXML = null
            state.generationStatus = 'idle'

            if (state.currentSession) {
              state.currentSession.messageCount = 0
              state.currentSession.hasGeneratedXML = false
            }
          })
        },

        // ================================
        // XML GENERATION
        // ================================

        setGeneratedXML: (xml: string | null) => {
          set((state) => {
            state.generatedXML = xml

            if (xml && state.currentSession) {
              state.currentSession.hasGeneratedXML = true
              state.currentSession.updatedAt = new Date().toISOString()

              // Update in sessions array
              const sessionIndex = state.sessions.findIndex(s => s.id === state.currentSession?.id)
              if (sessionIndex !== -1) {
                state.sessions[sessionIndex] = { ...state.currentSession }
              }
            }
          })
        },

        setGenerationStatus: (status: XMLGenerationStatus) => {
          set((state) => {
            state.generationStatus = status
          })
        },

        // ================================
        // UTILITY
        // ================================

        setLoading: (loading: boolean) => {
          set((state) => {
            state.isLoading = loading
          })
        },

        setError: (error: string | null) => {
          set((state) => {
            state.error = error
          })
        },

        reset: () => {
          set(() => ({ ...initialState }))
        }
      })),
      {
        name: 'xml-chat-storage',
        partialize: (state) => ({
          sessions: state.sessions,
          currentSession: state.currentSession
          // Don't persist messages, XML, or UI state
        })
      }
    ),
    { name: 'xml-chat-store' }
  )
)

// ================================
// SELECTORS
// ================================

export const useXMLChatSelectors = () => {
  const store = useXMLChatStore()

  return {
    // Current session info
    hasCurrentSession: Boolean(store.currentSession),
    currentSessionTitle: store.currentSession?.title || '',
    messageCount: store.messages.length,

    // XML status
    hasGeneratedXML: Boolean(store.generatedXML),
    canGenerateXML: store.messages.some(m => m.role === 'user') && !store.isLoading,

    // UI state
    isEmpty: store.messages.length === 0,
    isWorking: store.isLoading || store.generationStatus === 'generating'
  }
}