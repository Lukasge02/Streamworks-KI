/**
 * LangExtract Chat Hook for XML Chat V2
 * Modern hook using the new LangExtract-First StreamWorks API
 */

import { useState, useCallback, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { apiService } from '@/services/api.service'
import type {
  LangExtractSession,
  LangExtractRequest,
  LangExtractResponse,
  SourceGroundingData,
  SourceGroundedParameter,
  ParameterCorrectionRequest,
  LangExtractXMLGenerationRequest
} from '@/types/api.types'

// ================================
// TYPES FOR LANGEXTRACT CHAT
// ================================

export interface LangExtractChatMessage {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  source_grounding?: SourceGroundingData
  extracted_parameters?: {
    stream: Record<string, any>
    job: Record<string, any>
  }
  suggested_questions?: string[]
  processing_time?: number
}

export interface LangExtractChatState {
  session: LangExtractSession | null
  messages: LangExtractChatMessage[]
  isLoading: boolean
  error: string | null
  isTyping: boolean
}

export interface UseLangExtractChatResult {
  // State
  session: LangExtractSession | null
  messages: LangExtractChatMessage[]
  isLoading: boolean
  error: string | null
  isTyping: boolean

  // Actions
  createSession: (jobType?: string) => Promise<void>
  sendMessage: (message: string) => Promise<void>
  correctParameter: (request: ParameterCorrectionRequest) => Promise<void>
  generateXML: (forceGeneration?: boolean) => Promise<string | null>
  resetSession: () => void

  // Data
  allParameters: Record<string, any>
  streamParameters: Record<string, any>
  jobParameters: Record<string, any>
  completionPercentage: number
  criticalMissing: string[]
  sourceGroundedParameters: SourceGroundedParameter[]
}

// ================================
// MAIN HOOK
// ================================

export function useLangExtractChat(): UseLangExtractChatResult {
  const queryClient = useQueryClient()

  // State
  const [state, setState] = useState<LangExtractChatState>({
    session: null,
    messages: [],
    isLoading: false,
    error: null,
    isTyping: false
  })

  // Session creation mutation
  const createSessionMutation = useMutation({
    mutationFn: async (jobType?: string) => {
      const result = await apiService.createLangExtractSession(jobType)
      return result
    },
    onSuccess: (data) => {
      // Create initial session object
      const session: LangExtractSession = {
        session_id: data.session_id,
        job_type: undefined,
        state: 'stream_configuration',
        stream_parameters: {},
        job_parameters: {},
        completion_percentage: 0,
        critical_missing: [],
        created_at: new Date().toISOString(),
        last_activity: new Date().toISOString(),
        metadata: {}
      }

      // Add welcome message
      const welcomeMessage: LangExtractChatMessage = {
        id: 'welcome-' + Date.now(),
        type: 'assistant',
        content: data.message,
        timestamp: new Date().toISOString(),
        suggested_questions: data.suggested_questions
      }

      setState(prev => ({
        ...prev,
        session,
        messages: [welcomeMessage],
        error: null
      }))

      toast.success('Session erfolgreich erstellt!')
    },
    onError: (error) => {
      setState(prev => ({ ...prev, error: error.message }))
      toast.error('Fehler beim Erstellen der Session: ' + error.message)
    }
  })

  // Message sending mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (message: string): Promise<LangExtractResponse> => {
      if (!state.session) {
        throw new Error('Keine aktive Session')
      }

      const request: LangExtractRequest = {
        message,
        session_id: state.session.session_id
      }

      return apiService.sendLangExtractMessage(request)
    },
    onMutate: (message: string) => {
      // Add user message immediately
      const userMessage: LangExtractChatMessage = {
        id: 'user-' + Date.now(),
        type: 'user',
        content: message,
        timestamp: new Date().toISOString()
      }

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isTyping: true,
        error: null
      }))
    },
    onSuccess: (response: LangExtractResponse) => {
      // Create assistant response message
      const assistantMessage: LangExtractChatMessage = {
        id: 'assistant-' + Date.now(),
        type: 'assistant',
        content: response.response_message,
        timestamp: response.timestamp,
        source_grounding: response.source_grounding_data,
        extracted_parameters: {
          stream: response.extracted_stream_parameters,
          job: response.extracted_job_parameters
        },
        suggested_questions: response.suggested_questions,
        processing_time: response.processing_time
      }

      // Update session with new data
      const updatedSession: LangExtractSession = {
        ...state.session!,
        job_type: response.job_type,
        state: response.session_state as any,
        stream_parameters: {
          ...state.session!.stream_parameters,
          ...response.extracted_stream_parameters
        },
        job_parameters: {
          ...state.session!.job_parameters,
          ...response.extracted_job_parameters
        },
        completion_percentage: response.completion_percentage,
        last_activity: response.timestamp
      }

      setState(prev => ({
        ...prev,
        session: updatedSession,
        messages: [...prev.messages, assistantMessage],
        isTyping: false
      }))

      // Show warning if extraction needs review
      if (response.needs_review) {
        toast.warning('Die Parameter-Extraktion sollte überprüft werden')
      }

      // Show success for extracted parameters
      const totalExtracted = Object.keys(response.extracted_stream_parameters).length +
                            Object.keys(response.extracted_job_parameters).length
      if (totalExtracted > 0) {
        toast.success(`${totalExtracted} Parameter extrahiert`)
      }
    },
    onError: (error) => {
      setState(prev => ({
        ...prev,
        error: error.message,
        isTyping: false
      }))
      toast.error('Fehler beim Senden der Nachricht: ' + error.message)
    }
  })

  // Parameter correction mutation
  const correctParameterMutation = useMutation({
    mutationFn: async (request: ParameterCorrectionRequest) => {
      return apiService.correctLangExtractParameter(request)
    },
    onSuccess: (response) => {
      // Update session parameters
      if (state.session) {
        const updatedSession = { ...state.session }

        // Update the corrected parameter
        if (response.parameter_name in updatedSession.stream_parameters) {
          updatedSession.stream_parameters[response.parameter_name] =
            (correctParameterMutation.variables as ParameterCorrectionRequest).new_value
        } else if (response.parameter_name in updatedSession.job_parameters) {
          updatedSession.job_parameters[response.parameter_name] =
            (correctParameterMutation.variables as ParameterCorrectionRequest).new_value
        }

        setState(prev => ({ ...prev, session: updatedSession }))
      }

      toast.success(`Parameter "${response.parameter_name}" korrigiert`)
    },
    onError: (error) => {
      toast.error('Fehler beim Korrigieren des Parameters: ' + error.message)
    }
  })

  // XML generation mutation
  const generateXMLMutation = useMutation({
    mutationFn: async (forceGeneration = false) => {
      if (!state.session) {
        throw new Error('Keine aktive Session')
      }

      const request: LangExtractXMLGenerationRequest = {
        session_id: state.session.session_id,
        force_generation: forceGeneration
      }

      return apiService.generateLangExtractXML(request)
    },
    onSuccess: (response) => {
      if (response.generation_successful) {
        toast.success('XML erfolgreich generiert!')
        return response.xml_content
      } else {
        toast.error('XML-Generierung fehlgeschlagen: ' + response.validation_errors.join(', '))
        return null
      }
    },
    onError: (error) => {
      toast.error('Fehler bei der XML-Generierung: ' + error.message)
      return null
    }
  })

  // Actions
  const createSession = useCallback(async (jobType?: string) => {
    setState(prev => ({ ...prev, isLoading: true }))
    try {
      await createSessionMutation.mutateAsync(jobType)
    } finally {
      setState(prev => ({ ...prev, isLoading: false }))
    }
  }, [createSessionMutation])

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return
    await sendMessageMutation.mutateAsync(message.trim())
  }, [sendMessageMutation])

  const correctParameter = useCallback(async (request: ParameterCorrectionRequest) => {
    await correctParameterMutation.mutateAsync(request)
  }, [correctParameterMutation])

  const generateXML = useCallback(async (forceGeneration = false) => {
    const result = await generateXMLMutation.mutateAsync(forceGeneration)
    return result
  }, [generateXMLMutation])

  const resetSession = useCallback(() => {
    setState({
      session: null,
      messages: [],
      isLoading: false,
      error: null,
      isTyping: false
    })
    queryClient.clear()
  }, [queryClient])

  // Computed values
  const allParameters = {
    ...state.session?.stream_parameters,
    ...state.session?.job_parameters
  }

  const sourceGroundedParameters: SourceGroundedParameter[] =
    state.messages
      .flatMap(msg => msg.source_grounding?.highlighted_ranges || [])
      .map(([start, end, paramName], index) => ({
        name: paramName,
        value: allParameters[paramName],
        confidence: 0.8, // Default confidence
        character_offsets: [start, end],
        user_confirmed: false
      }))

  return {
    // State
    session: state.session,
    messages: state.messages,
    isLoading: state.isLoading || createSessionMutation.isPending ||
             sendMessageMutation.isPending || generateXMLMutation.isPending,
    error: state.error,
    isTyping: state.isTyping,

    // Actions
    createSession,
    sendMessage,
    correctParameter,
    generateXML,
    resetSession,

    // Data
    allParameters,
    streamParameters: state.session?.stream_parameters || {},
    jobParameters: state.session?.job_parameters || {},
    completionPercentage: state.session?.completion_percentage || 0,
    criticalMissing: state.session?.critical_missing || [],
    sourceGroundedParameters
  }
}

export default useLangExtractChat