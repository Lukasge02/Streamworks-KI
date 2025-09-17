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

// XML Chat specific types
export interface XMLChatMessage {
  id: string
  session_id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: {
    extractedParams?: Record<string, any>
    validationErrors?: string[]
    suggestions?: string[]
    parameterUpdates?: Record<string, any>
  }
}

export interface XMLChatSession {
  id: string
  title: string
  user_id: string
  jobType?: 'STANDARD' | 'SAP' | 'FILE_TRANSFER' | 'CUSTOM'
  status: 'CREATED' | 'COLLECTING_PARAMS' | 'GENERATING' | 'COMPLETED' | 'ERROR'
  extractedParams: Record<string, any>
  parameterStatuses: ParameterStatus[]
  xmlPreview?: string
  xmlValid: boolean
  messages: XMLChatMessage[]
  createdAt: string
  updatedAt: string
  completionPercentage: number
}

export interface ParameterStatus {
  name: string
  type: string
  required: boolean
  status: 'MISSING' | 'PARTIAL' | 'COMPLETE' | 'INVALID'
  value?: any
  description?: string
  chatPrompt?: string
  validationError?: string
}

// Regular Chat types (existing)

export interface ChatMessage {
  id: string
  session_id: string
  type: 'user' | 'assistant'
  content: string
  sources?: ChatSource[]
  confidence_score?: number
  processing_time?: string
  model_info?: string
  retrieval_context?: {
    total_chunks?: number
    relevant_chunks?: number
    query_type?: string
    mode?: string
  }
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
  // Regular chat state (existing)
  sessions: ChatSession[]
  currentSessionId: string | null
  messages: Record<string, ChatMessage[]> // sessionId -> messages

  // XML Chat state (new)
  xmlChatSessions: XMLChatSession[]
  currentXMLSessionId: string | null

  // UI state
  isLoading: boolean
  error: string | null
  aiProvider: 'local' | 'cloud'

  // Loading states
  isLoadingSessions: boolean
  isLoadingMessages: Record<string, boolean>
  isSendingMessage: boolean

  // XML Chat loading states
  isLoadingXMLSessions: boolean
  isSendingXMLMessage: boolean
  isGeneratingXML: boolean
}

export interface ChatActions {
  // Regular chat session management (existing)
  setSessions: (sessions: ChatSession[]) => void
  setCurrentSession: (sessionId: string | null) => void
  createSession: (title: string) => Promise<string>
  updateSessionTitle: (sessionId: string, title: string) => void
  deleteSession: (sessionId: string) => void

  // Regular chat message management (existing)
  setMessages: (sessionId: string, messages: ChatMessage[]) => void
  addMessage: (sessionId: string, message: Omit<ChatMessage, 'id' | 'created_at' | 'sequence_number'>) => void
  clearMessages: (sessionId: string) => void

  // XML Chat session management (new)
  setXMLChatSessions: (sessions: XMLChatSession[]) => void
  setCurrentXMLSession: (sessionId: string | null) => void
  createXMLChatSession: (jobType?: XMLChatSession['jobType']) => Promise<string>
  updateXMLSessionStatus: (sessionId: string, status: XMLChatSession['status']) => void
  updateXMLSessionParams: (sessionId: string, params: Record<string, any>) => void
  updateXMLSessionParameterStatuses: (sessionId: string, statuses: ParameterStatus[]) => void
  updateXMLPreview: (sessionId: string, xmlContent: string, isValid: boolean) => void
  deleteXMLSession: (sessionId: string) => void

  // XML Chat message management (new)
  addXMLMessage: (sessionId: string, message: Omit<XMLChatMessage, 'id' | 'timestamp'>) => void
  clearXMLMessages: (sessionId: string) => void

  // AI Provider
  setAiProvider: (provider: 'local' | 'cloud') => void

  // Loading states
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setLoadingSessions: (loading: boolean) => void
  setLoadingMessages: (sessionId: string, loading: boolean) => void
  setSendingMessage: (sending: boolean) => void

  // XML Chat loading states (new)
  setLoadingXMLSessions: (loading: boolean) => void
  setSendingXMLMessage: (sending: boolean) => void
  setGeneratingXML: (generating: boolean) => void

  // Utils
  getCurrentMessages: () => ChatMessage[]
  getCurrentSession: () => ChatSession | null
  generateMessageId: () => string

  // XML Chat utils (new)
  getCurrentXMLSession: () => XMLChatSession | null
  getCurrentXMLMessages: () => XMLChatMessage[]
  getXMLSessionProgress: (sessionId: string) => number
}

// ================================
// ZUSTAND STORE
// ================================

export const useChatStore = create<ChatState & ChatActions>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Initial state (existing)
        sessions: [],
        currentSessionId: null,
        messages: {},

        // XML Chat initial state (new)
        xmlChatSessions: [],
        currentXMLSessionId: null,

        // UI state
        isLoading: false,
        error: null,
        aiProvider: 'local', // Default to local AI

        // Loading states
        isLoadingSessions: false,
        isLoadingMessages: {},
        isSendingMessage: false,

        // XML Chat loading states (new)
        isLoadingXMLSessions: false,
        isSendingXMLMessage: false,
        isGeneratingXML: false,

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

        // XML Chat session management (new)
        setXMLChatSessions: (sessions) =>
          set((state) => {
            state.xmlChatSessions = sessions
          }),

        setCurrentXMLSession: (sessionId) =>
          set((state) => {
            state.currentXMLSessionId = sessionId
          }),

        createXMLChatSession: async (jobType) => {
          const sessionId = crypto.randomUUID()
          const now = new Date().toISOString()

          const newSession: XMLChatSession = {
            id: sessionId,
            title: `XML Chat ${jobType || 'Session'}`,
            user_id: 'default-user',
            jobType,
            status: 'CREATED',
            extractedParams: {},
            parameterStatuses: [],
            xmlValid: false,
            messages: [],
            createdAt: now,
            updatedAt: now,
            completionPercentage: 0,
          }

          set((state) => {
            state.xmlChatSessions.unshift(newSession)
            state.currentXMLSessionId = sessionId
          })

          return sessionId
        },

        updateXMLSessionStatus: (sessionId, status) =>
          set((state) => {
            const session = state.xmlChatSessions.find((s) => s.id === sessionId)
            if (session) {
              session.status = status
              session.updatedAt = new Date().toISOString()
            }
          }),

        updateXMLSessionParams: (sessionId, params) =>
          set((state) => {
            const session = state.xmlChatSessions.find((s) => s.id === sessionId)
            if (session) {
              session.extractedParams = { ...session.extractedParams, ...params }
              session.updatedAt = new Date().toISOString()
              // Recalculate completion percentage
              const requiredParams = session.parameterStatuses.filter(p => p.required)
              const completedParams = requiredParams.filter(p => p.status === 'COMPLETE')
              session.completionPercentage = requiredParams.length > 0
                ? Math.round((completedParams.length / requiredParams.length) * 100)
                : 0
            }
          }),

        updateXMLSessionParameterStatuses: (sessionId, statuses) =>
          set((state) => {
            const session = state.xmlChatSessions.find((s) => s.id === sessionId)
            if (session) {
              session.parameterStatuses = statuses
              session.updatedAt = new Date().toISOString()
              // Recalculate completion percentage
              const requiredParams = statuses.filter(p => p.required)
              const completedParams = requiredParams.filter(p => p.status === 'COMPLETE')
              session.completionPercentage = requiredParams.length > 0
                ? Math.round((completedParams.length / requiredParams.length) * 100)
                : 0
            }
          }),

        updateXMLPreview: (sessionId, xmlContent, isValid) =>
          set((state) => {
            const session = state.xmlChatSessions.find((s) => s.id === sessionId)
            if (session) {
              session.xmlPreview = xmlContent
              session.xmlValid = isValid
              session.updatedAt = new Date().toISOString()
              if (isValid) {
                session.status = 'COMPLETED'
              }
            }
          }),

        deleteXMLSession: (sessionId) =>
          set((state) => {
            state.xmlChatSessions = state.xmlChatSessions.filter((s) => s.id !== sessionId)
            if (state.currentXMLSessionId === sessionId) {
              state.currentXMLSessionId = state.xmlChatSessions[0]?.id || null
            }
          }),

        // XML Chat message management (new)
        addXMLMessage: (sessionId, messageData) =>
          set((state) => {
            const messageId = get().generateMessageId()
            const now = new Date().toISOString()

            const newMessage: XMLChatMessage = {
              ...messageData,
              id: messageId,
              session_id: sessionId,
              timestamp: now,
            }

            const session = state.xmlChatSessions.find((s) => s.id === sessionId)
            if (session) {
              session.messages.push(newMessage)
              session.updatedAt = now

              // Auto-generate title from first user message
              if (messageData.type === 'user' && session.messages.length === 1) {
                session.title = messageData.content.slice(0, 50) +
                  (messageData.content.length > 50 ? '...' : '')
              }

              // Update extracted parameters if provided in metadata
              if (messageData.metadata?.extractedParams) {
                session.extractedParams = {
                  ...session.extractedParams,
                  ...messageData.metadata.extractedParams
                }
              }

              // Update parameter statuses if provided in metadata
              if (messageData.metadata?.parameterUpdates) {
                session.parameterStatuses = session.parameterStatuses.map(param => {
                  if (messageData.metadata?.parameterUpdates?.[param.name]) {
                    return {
                      ...param,
                      value: messageData.metadata.parameterUpdates[param.name],
                      status: 'COMPLETE' as const
                    }
                  }
                  return param
                })
              }
            }
          }),

        clearXMLMessages: (sessionId) =>
          set((state) => {
            const session = state.xmlChatSessions.find((s) => s.id === sessionId)
            if (session) {
              session.messages = []
              session.updatedAt = new Date().toISOString()
            }
          }),

        // XML Chat loading states (new)
        setLoadingXMLSessions: (loading) =>
          set((state) => {
            state.isLoadingXMLSessions = loading
          }),

        setSendingXMLMessage: (sending) =>
          set((state) => {
            state.isSendingXMLMessage = sending
          }),

        setGeneratingXML: (generating) =>
          set((state) => {
            state.isGeneratingXML = generating
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

        // XML Chat utils (new)
        getCurrentXMLSession: () => {
          const state = get()
          return state.xmlChatSessions.find((s) => s.id === state.currentXMLSessionId) || null
        },

        getCurrentXMLMessages: () => {
          const state = get()
          const session = state.xmlChatSessions.find((s) => s.id === state.currentXMLSessionId)
          return session?.messages || []
        },

        getXMLSessionProgress: (sessionId) => {
          const state = get()
          const session = state.xmlChatSessions.find((s) => s.id === sessionId)
          return session?.completionPercentage || 0
        },
      })),
      {
        name: 'streamworks-chat-store',
        // Only persist essential data, not loading states
        partialize: (state) => ({
          currentSessionId: state.currentSessionId,
          currentXMLSessionId: state.currentXMLSessionId,
          aiProvider: state.aiProvider,
          xmlChatSessions: state.xmlChatSessions,
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
    // Basic selectors (existing)
    currentSession: store.getCurrentSession(),
    currentMessages: store.getCurrentMessages(),
    hasActiveSessions: store.sessions.length > 0,
    isAnyLoading: store.isLoading || store.isLoadingSessions || store.isSendingMessage,

    // Computed values (existing)
    sessionCount: store.sessions.length,
    totalMessages: Object.values(store.messages).reduce((sum, msgs) => sum + msgs.length, 0),

    // UI state helpers (existing)
    canSendMessage: !store.isSendingMessage && store.currentSessionId !== null,
    shouldShowEmptyState: store.sessions.length === 0 && !store.isLoadingSessions,
  }
}

// XML Chat specific selectors
export const useXMLChatSelectors = () => {
  const store = useChatStore()

  return {
    // Basic XML Chat selectors
    currentXMLSession: store.getCurrentXMLSession(),
    currentXMLMessages: store.getCurrentXMLMessages(),
    hasActiveXMLSessions: store.xmlChatSessions.length > 0,
    isAnyXMLLoading: store.isLoadingXMLSessions || store.isSendingXMLMessage || store.isGeneratingXML,

    // Computed values
    xmlSessionCount: store.xmlChatSessions.length,
    totalXMLMessages: store.xmlChatSessions.reduce((sum, session) => sum + session.messages.length, 0),

    // UI state helpers
    canSendXMLMessage: !store.isSendingXMLMessage && store.currentXMLSessionId !== null,
    shouldShowXMLEmptyState: store.xmlChatSessions.length === 0 && !store.isLoadingXMLSessions,

    // XML-specific helpers
    currentSessionProgress: store.currentXMLSessionId ? store.getXMLSessionProgress(store.currentXMLSessionId) : 0,
    currentSessionStatus: store.getCurrentXMLSession()?.status || 'CREATED',
    currentSessionJobType: store.getCurrentXMLSession()?.jobType,
    currentSessionParameters: store.getCurrentXMLSession()?.extractedParams || {},
    currentSessionParameterStatuses: store.getCurrentXMLSession()?.parameterStatuses || [],
    hasXMLPreview: !!store.getCurrentXMLSession()?.xmlPreview,
    isXMLValid: store.getCurrentXMLSession()?.xmlValid || false,
    xmlPreviewContent: store.getCurrentXMLSession()?.xmlPreview || '',

    // Progress helpers
    requiredParametersCount: store.getCurrentXMLSession()?.parameterStatuses.filter(p => p.required).length || 0,
    completedParametersCount: store.getCurrentXMLSession()?.parameterStatuses.filter(p => p.required && p.status === 'COMPLETE').length || 0,
    missingParametersCount: store.getCurrentXMLSession()?.parameterStatuses.filter(p => p.required && p.status === 'MISSING').length || 0,

    // Validation helpers
    hasValidationErrors: store.getCurrentXMLSession()?.parameterStatuses.some(p => p.status === 'INVALID') || false,
    canGenerateXML: (store.getCurrentXMLSession()?.parameterStatuses.filter(p => p.required && p.status === 'COMPLETE').length || 0) >= (store.getCurrentXMLSession()?.parameterStatuses.filter(p => p.required).length || 1),
  }
}