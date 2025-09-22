/**
 * XML Chat Store - Clean Zustand Implementation
 * Simple state management for the new XML chat system
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// Import Smart Chat types
import type { SmartSession, SmartChatMessage, ExtractedParameters } from '../hooks/useSmartChat'

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
      streamType?: StreamType
      nextParameter?: string | null
      completion?: number
      parameterConfidences?: Record<string, number>
      job_type?: string
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
export type StreamType = 'SAP' | 'FILE_TRANSFER' | 'STANDARD'
export type ChatMode = 'legacy' | 'smart'

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

  // ================================
  // SMART CHAT INTEGRATION
  // ================================

  // Chat Mode
  chatMode: ChatMode

  // Smart Session
  smartSession: SmartSession | null
  smartMessages: SmartChatMessage[]

  // Stream Configuration
  selectedStreamType: StreamType | null
  streamTypeSelectionVisible: boolean

  // Parameter Management
  extractedParameters: ExtractedParameters
  missingParameters: string[]
  nextParameter: string | null
  completionPercentage: number

  // Smart Suggestions
  aiSuggestions: string[]
  suggestedQuestions: string[]

  // Smart UI State
  isCreatingSmartSession: boolean
  isSendingSmartMessage: boolean
  isGeneratingSmartXML: boolean
  isLoadingParameters: boolean
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

  // ================================
  // SMART CHAT ACTIONS
  // ================================

  // Chat Mode Management
  setChatMode: (mode: ChatMode) => void
  enableSmartMode: () => void
  enableLegacyMode: () => void

  // Smart Session Management
  setSmartSession: (session: SmartSession | null) => void
  addSmartMessage: (message: SmartChatMessage) => void
  clearSmartMessages: () => void

  // Stream Type Management
  setSelectedStreamType: (type: StreamType | null) => void
  showStreamTypeSelection: () => void
  hideStreamTypeSelection: () => void

  // Parameter Management
  setExtractedParameters: (parameters: ExtractedParameters) => void
  updateExtractedParameter: (key: string, value: any) => void
  setMissingParameters: (parameters: string[]) => void
  setNextParameter: (parameter: string | null) => void
  setCompletionPercentage: (percentage: number) => void

  // Suggestions Management
  setAISuggestions: (suggestions: string[]) => void
  setSuggestedQuestions: (questions: string[]) => void
  addAISuggestion: (suggestion: string) => void

  // Smart UI State
  setCreatingSmartSession: (loading: boolean) => void
  setSendingSmartMessage: (loading: boolean) => void
  setGeneratingSmartXML: (loading: boolean) => void
  setLoadingParameters: (loading: boolean) => void

  // Smart Utilities
  resetSmartState: () => void
  resetParameterState: () => void
}

type XMLChatStore = XMLChatState & XMLChatActions

// ================================
// INITIAL STATE
// ================================

const initialState: XMLChatState = {
  // Legacy state
  sessions: [],
  currentSession: null,
  messages: [],
  generatedXML: null,
  generationStatus: 'idle',
  isLoading: false,
  error: null,

  // Smart Chat state
  chatMode: 'smart', // Default to smart mode
  smartSession: null,
  smartMessages: [],
  selectedStreamType: null,
  streamTypeSelectionVisible: false, // Unified flow - no stream type selection needed
  extractedParameters: {},
  missingParameters: [],
  nextParameter: null,
  completionPercentage: 0,
  aiSuggestions: [],
  suggestedQuestions: [],
  isCreatingSmartSession: false,
  isSendingSmartMessage: false,
  isGeneratingSmartXML: false,
  isLoadingParameters: false
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
        },

        // ================================
        // SMART CHAT ACTIONS
        // ================================

        // Chat Mode Management
        setChatMode: (mode: ChatMode) => {
          set((state) => {
            state.chatMode = mode
          })
        },

        enableSmartMode: () => {
          set((state) => {
            state.chatMode = 'smart'
            state.streamTypeSelectionVisible = !state.selectedStreamType
          })
        },

        enableLegacyMode: () => {
          set((state) => {
            state.chatMode = 'legacy'
            state.streamTypeSelectionVisible = false
          })
        },

        // Smart Session Management
        setSmartSession: (session: SmartSession | null) => {
          set((state) => {
            state.smartSession = session
            if (session) {
              state.completionPercentage = session.completion_percentage || 0
              state.aiSuggestions = session.suggested_questions || []
            }
          })
        },

        addSmartMessage: (message: SmartChatMessage) => {
          set((state) => {
            state.smartMessages.push(message)

            // Update state from message
            state.completionPercentage = message.completion_percentage || 0
            state.aiSuggestions = message.suggested_questions || []
            state.nextParameter = message.next_parameter || null
          })
        },

        clearSmartMessages: () => {
          set((state) => {
            state.smartMessages = []
          })
        },

        // Stream Type Management
        setSelectedStreamType: (type: StreamType | null) => {
          set((state) => {
            if (state.selectedStreamType === type) {
              state.streamTypeSelectionVisible = !type
              return
            }

            state.selectedStreamType = type
            state.streamTypeSelectionVisible = !type

            if (type) {
              state.extractedParameters = {}
              state.missingParameters = []
              state.completionPercentage = 0
              state.nextParameter = null
            }
          })
        },

        showStreamTypeSelection: () => {
          set((state) => {
            state.streamTypeSelectionVisible = false // Unified flow - no stream type selection
          })
        },

        hideStreamTypeSelection: () => {
          set((state) => {
            state.streamTypeSelectionVisible = false
          })
        },

        // Parameter Management
        setExtractedParameters: (parameters: ExtractedParameters) => {
          set((state) => {
            state.extractedParameters = parameters
          })
        },

        updateExtractedParameter: (key: string, value: any) => {
          set((state) => {
            state.extractedParameters[key] = value
          })
        },

        setMissingParameters: (parameters: string[]) => {
          set((state) => {
            state.missingParameters = parameters
          })
        },

        setNextParameter: (parameter: string | null) => {
          set((state) => {
            state.nextParameter = parameter
          })
        },

        setCompletionPercentage: (percentage: number) => {
          set((state) => {
            state.completionPercentage = percentage
          })
        },

        // Suggestions Management
        setAISuggestions: (suggestions: string[]) => {
          set((state) => {
            state.aiSuggestions = suggestions
          })
        },

        setSuggestedQuestions: (questions: string[]) => {
          set((state) => {
            state.suggestedQuestions = questions
          })
        },

        addAISuggestion: (suggestion: string) => {
          set((state) => {
            if (!state.aiSuggestions.includes(suggestion)) {
              state.aiSuggestions.push(suggestion)
            }
          })
        },

        // Smart UI State
        setCreatingSmartSession: (loading: boolean) => {
          set((state) => {
            state.isCreatingSmartSession = loading
          })
        },

        setSendingSmartMessage: (loading: boolean) => {
          set((state) => {
            state.isSendingSmartMessage = loading
          })
        },

        setGeneratingSmartXML: (loading: boolean) => {
          set((state) => {
            state.isGeneratingSmartXML = loading
          })
        },

        setLoadingParameters: (loading: boolean) => {
          set((state) => {
            state.isLoadingParameters = loading
          })
        },

        // Smart Utilities
        resetSmartState: () => {
          set((state) => {
            state.smartSession = null
            state.smartMessages = []
            state.selectedStreamType = null
            state.streamTypeSelectionVisible = false // Unified flow - always hidden
            state.extractedParameters = {}
            state.missingParameters = []
            state.nextParameter = null
            state.completionPercentage = 0
            state.aiSuggestions = []
            state.suggestedQuestions = []
            state.isCreatingSmartSession = false
            state.isSendingSmartMessage = false
            state.isGeneratingSmartXML = false
            state.isLoadingParameters = false
          })
        },

        resetParameterState: () => {
          set((state) => {
            state.extractedParameters = {}
            state.missingParameters = []
            state.nextParameter = null
            state.completionPercentage = 0
          })
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
    isWorking: store.isLoading || store.generationStatus === 'generating',

    // ================================
    // SMART CHAT SELECTORS
    // ================================

    // Chat Mode
    isSmartMode: store.chatMode === 'smart',
    isLegacyMode: store.chatMode === 'legacy',

    // Smart Session
    hasSmartSession: Boolean(store.smartSession),
    smartSessionId: store.smartSession?.session_id || null,
    smartMessageCount: store.smartMessages.length,

    // Stream Type
    hasSelectedStreamType: Boolean(store.selectedStreamType),
    streamTypeSelected: store.selectedStreamType,
    shouldShowStreamTypeSelection: store.streamTypeSelectionVisible,

    // Parameters
    hasExtractedParameters: Object.keys(store.extractedParameters).length > 0,
    parameterCount: Object.keys(store.extractedParameters).length,
    missingParameterCount: store.missingParameters.length,
    isParametersComplete: store.completionPercentage >= 100,
    hasNextParameter: Boolean(store.nextParameter),

    // Suggestions
    hasSuggestions: store.aiSuggestions.length > 0,
    suggestionCount: store.aiSuggestions.length,

    // Smart Loading States
    isSmartWorking: store.isCreatingSmartSession || store.isSendingSmartMessage || store.isGeneratingSmartXML,
    canSendSmartMessage: Boolean(store.smartSession) && !store.isSendingSmartMessage,
    canGenerateSmartXML: Boolean(store.smartSession) && store.completionPercentage >= 100 && !store.isGeneratingSmartXML,

    // UI State
    isSmartEmpty: store.smartMessages.length === 0,
    shouldShowParameterProgress: (Boolean(store.selectedStreamType) || Boolean(store.extractedParameters && Object.keys(store.extractedParameters).length > 0)) && store.smartMessages.length > 0,
    shouldShowSuggestions: Boolean(store.selectedStreamType)
  }
}
