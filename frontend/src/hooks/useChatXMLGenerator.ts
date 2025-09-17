/**
 * Chat XML Generator React Query Hook
 * Manages XML chat sessions, messages, and API communication
 * Integrates with chatStore for state management
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useChatStore, XMLChatSession, XMLChatMessage, ParameterStatus } from '@/stores/chatStore'

// ================================
// API TYPES
// ================================

interface CreateXMLSessionRequest {
  user_id?: string
  initial_context?: string
  job_type?: 'STANDARD' | 'SAP' | 'FILE_TRANSFER' | 'CUSTOM'
}

interface CreateXMLSessionResponse {
  session_id: string
  status: string
  message: string
}

interface SendXMLMessageRequest {
  session_id: string
  message: string
  context?: Record<string, any>
}

interface SendXMLMessageResponse {
  response: string
  updated_params: Record<string, any>
  parameter_statuses: ParameterStatus[]
  completion_percentage: number
  next_required_params: string[]
  session_status: XMLChatSession['status']
  suggestions?: string[]
  validation_errors?: string[]
}

interface GenerateXMLRequest {
  session_id: string
  force_generation?: boolean
}

interface GenerateXMLResponse {
  xml_content: string
  is_valid: boolean
  validation_errors?: string[]
  template_used: string
  generation_time: number
}

interface XMLSessionStatusResponse {
  session: XMLChatSession
  messages: XMLChatMessage[]
  parameter_progress: {
    total_parameters: number
    required_parameters: number
    completed_parameters: number
    completion_percentage: number
  }
}

// ================================
// API SERVICE
// ================================

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

class XMLChatApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}/api/xml-generator/chat-xml${endpoint}`

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          error: `HTTP ${response.status}`,
          detail: response.statusText
        }))
        throw new Error(errorData.error || errorData.detail || 'Request failed')
      }

      return await response.json()
    } catch (error: any) {
      console.error('XMLChat API Error:', error)
      throw error
    }
  }

  // Session Management
  async createSession(data: CreateXMLSessionRequest): Promise<CreateXMLSessionResponse> {
    return this.request<CreateXMLSessionResponse>('/session', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async getSession(sessionId: string): Promise<XMLSessionStatusResponse> {
    return this.request<XMLSessionStatusResponse>(`/session/${sessionId}`)
  }

  async deleteSession(sessionId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/session/${sessionId}`, {
      method: 'DELETE'
    })
  }

  // Message Communication
  async sendMessage(data: SendXMLMessageRequest): Promise<SendXMLMessageResponse> {
    return this.request<SendXMLMessageResponse>('/message', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // XML Generation
  async generateXML(data: GenerateXMLRequest): Promise<GenerateXMLResponse> {
    return this.request<GenerateXMLResponse>('/generate', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // Parameter Management
  async getParameterStatuses(sessionId: string): Promise<ParameterStatus[]> {
    return this.request<ParameterStatus[]>(`/session/${sessionId}/parameters`)
  }

  async validateParameters(sessionId: string): Promise<{
    is_valid: boolean
    errors: string[]
    missing_required: string[]
  }> {
    return this.request(`/session/${sessionId}/validate`)
  }
}

const xmlChatApi = new XMLChatApiService()

// ================================
// REACT QUERY KEYS
// ================================

export const xmlChatKeys = {
  all: ['xmlChat'] as const,
  sessions: () => [...xmlChatKeys.all, 'sessions'] as const,
  session: (id: string) => [...xmlChatKeys.all, 'session', id] as const,
  parameters: (sessionId: string) => [...xmlChatKeys.all, 'parameters', sessionId] as const,
  validation: (sessionId: string) => [...xmlChatKeys.all, 'validation', sessionId] as const,
}

// ================================
// MAIN HOOK
// ================================

export const useChatXMLGenerator = () => {
  const queryClient = useQueryClient()
  const {
    xmlChatSessions,
    currentXMLSessionId,
    isSendingXMLMessage,
    isGeneratingXML,
    createXMLChatSession,
    addXMLMessage,
    updateXMLSessionParams,
    updateXMLSessionParameterStatuses,
    updateXMLSessionStatus,
    updateXMLPreview,
    deleteXMLSession,
    setSendingXMLMessage,
    setGeneratingXML,
    setCurrentXMLSession,
    setError,
  } = useChatStore()

  // ================================
  // SESSION MANAGEMENT
  // ================================

  // Create new XML chat session
  const createSession = useMutation({
    mutationFn: async (data: CreateXMLSessionRequest) => {
      // Create local session first for immediate UI feedback
      const localSessionId = await createXMLChatSession(data.job_type)

      try {
        // Create session on backend
        const response = await xmlChatApi.createSession({
          ...data,
          user_id: data.user_id || 'default-user'
        })

        // Update local session with backend ID if different
        if (response.session_id !== localSessionId) {
          // TODO: Handle ID mismatch - for now use local ID
          console.warn('Backend session ID differs from local ID')
        }

        return { sessionId: localSessionId, ...response }
      } catch (error) {
        // Rollback local session creation on error
        deleteXMLSession(localSessionId)
        throw error
      }
    },
    onSuccess: (data) => {
      console.log('✅ XML Chat session created:', data.sessionId)
      // Invalidate sessions query
      queryClient.invalidateQueries({ queryKey: xmlChatKeys.sessions() })
    },
    onError: (error) => {
      console.error('❌ Failed to create XML Chat session:', error)
      setError(`Failed to create session: ${error.message}`)
    }
  })

  // Get session details
  const useSession = (sessionId: string | null) => {
    return useQuery({
      queryKey: xmlChatKeys.session(sessionId || ''),
      queryFn: () => xmlChatApi.getSession(sessionId!),
      enabled: !!sessionId,
      staleTime: 1000 * 30, // 30 seconds
      refetchOnWindowFocus: false,
    })
  }

  // Delete session
  const deleteSessionMutation = useMutation({
    mutationFn: async (sessionId: string) => {
      // Optimistically delete from local state
      deleteXMLSession(sessionId)

      try {
        return await xmlChatApi.deleteSession(sessionId)
      } catch (error) {
        // TODO: Rollback optimistic delete
        console.error('Failed to delete session on backend:', error)
        throw error
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: xmlChatKeys.sessions() })
    },
    onError: (error, sessionId) => {
      setError(`Failed to delete session: ${error.message}`)
    }
  })

  // ================================
  // MESSAGE COMMUNICATION
  // ================================

  // Send message to XML chat
  const sendMessage = useMutation({
    mutationFn: async ({ sessionId, message, context = {} }: {
      sessionId: string
      message: string
      context?: Record<string, any>
    }) => {
      setSendingXMLMessage(true)

      // Add user message to local state immediately
      addXMLMessage(sessionId, {
        type: 'user',
        content: message,
        session_id: sessionId
      })

      try {
        const response = await xmlChatApi.sendMessage({
          session_id: sessionId,
          message,
          context
        })

        // Add assistant response to local state
        addXMLMessage(sessionId, {
          type: 'assistant',
          content: response.response,
          session_id: sessionId,
          metadata: {
            extractedParams: response.updated_params,
            suggestions: response.suggestions,
            validationErrors: response.validation_errors,
            parameterUpdates: response.updated_params
          }
        })

        // Update session state
        updateXMLSessionParams(sessionId, response.updated_params)
        updateXMLSessionParameterStatuses(sessionId, response.parameter_statuses)
        updateXMLSessionStatus(sessionId, response.session_status)

        return response
      } catch (error) {
        // Add error message to chat
        addXMLMessage(sessionId, {
          type: 'system',
          content: `Fehler: ${error.message}`,
          session_id: sessionId,
          metadata: {
            validationErrors: [error.message]
          }
        })
        throw error
      } finally {
        setSendingXMLMessage(false)
      }
    },
    onError: (error) => {
      console.error('❌ Failed to send XML chat message:', error)
      setError(`Failed to send message: ${error.message}`)
    }
  })

  // ================================
  // XML GENERATION
  // ================================

  // Generate XML from current session parameters
  const generateXML = useMutation({
    mutationFn: async ({ sessionId, forceGeneration = false }: {
      sessionId: string
      forceGeneration?: boolean
    }) => {
      setGeneratingXML(true)
      updateXMLSessionStatus(sessionId, 'GENERATING')

      try {
        const response = await xmlChatApi.generateXML({
          session_id: sessionId,
          force_generation: forceGeneration
        })

        // Update XML preview in local state
        updateXMLPreview(sessionId, response.xml_content, response.is_valid)

        // Add success message to chat
        addXMLMessage(sessionId, {
          type: 'assistant',
          content: response.is_valid
            ? '✅ XML erfolgreich generiert! Du kannst es jetzt herunterladen oder kopieren.'
            : '⚠️ XML generiert, aber enthält Validierungsfehler. Bitte überprüfe die Parameter.',
          session_id: sessionId,
          metadata: {
            validationErrors: response.validation_errors
          }
        })

        return response
      } catch (error) {
        updateXMLSessionStatus(sessionId, 'ERROR')

        // Add error message to chat
        addXMLMessage(sessionId, {
          type: 'system',
          content: `❌ XML-Generierung fehlgeschlagen: ${error.message}`,
          session_id: sessionId,
          metadata: {
            validationErrors: [error.message]
          }
        })

        throw error
      } finally {
        setGeneratingXML(false)
      }
    },
    onError: (error) => {
      console.error('❌ Failed to generate XML:', error)
      setError(`Failed to generate XML: ${error.message}`)
    }
  })

  // ================================
  // PARAMETER VALIDATION
  // ================================

  // Get parameter statuses
  const useParameterStatuses = (sessionId: string | null) => {
    return useQuery({
      queryKey: xmlChatKeys.parameters(sessionId || ''),
      queryFn: () => xmlChatApi.getParameterStatuses(sessionId!),
      enabled: !!sessionId,
      staleTime: 1000 * 10, // 10 seconds
    })
  }

  // Validate current parameters
  const validateParameters = useMutation({
    mutationFn: (sessionId: string) => xmlChatApi.validateParameters(sessionId),
    onSuccess: (data, sessionId) => {
      if (!data.is_valid) {
        // Add validation feedback to chat
        addXMLMessage(sessionId, {
          type: 'system',
          content: `⚠️ Parameter-Validierung: ${data.errors.length} Fehler gefunden. Fehlende Pflichtfelder: ${data.missing_required.join(', ')}`,
          session_id: sessionId,
          metadata: {
            validationErrors: data.errors
          }
        })
      }
    }
  })

  // ================================
  // UTILITY FUNCTIONS
  // ================================

  const getCurrentSession = () => {
    return xmlChatSessions.find(s => s.id === currentXMLSessionId) || null
  }

  const switchToSession = (sessionId: string) => {
    setCurrentXMLSession(sessionId)
  }

  const createNewSession = async (jobType?: XMLChatSession['jobType']) => {
    const result = await createSession.mutateAsync({
      job_type: jobType,
      initial_context: jobType ? `Erstelle ${jobType} Job` : 'Neuer XML Chat'
    })
    return result.sessionId
  }

  // ================================
  // RETURN INTERFACE
  // ================================

  return {
    // State
    sessions: xmlChatSessions,
    currentSessionId: currentXMLSessionId,
    currentSession: getCurrentSession(),
    isLoading: isSendingXMLMessage || isGeneratingXML,
    isSendingMessage: isSendingXMLMessage,
    isGeneratingXML,

    // Actions
    createNewSession,
    switchToSession,
    sendMessage: sendMessage.mutate,
    generateXML: generateXML.mutate,
    deleteSession: deleteSessionMutation.mutate,
    validateParameters: validateParameters.mutate,

    // Mutation objects (for advanced usage)
    createSessionMutation: createSession,
    sendMessageMutation: sendMessage,
    generateXMLMutation: generateXML,
    deleteSessionMutation,
    validateParametersMutation: validateParameters,

    // Queries
    useSession,
    useParameterStatuses,

    // Utilities
    getCurrentSession,
    queryClient,
  }
}

export default useChatXMLGenerator