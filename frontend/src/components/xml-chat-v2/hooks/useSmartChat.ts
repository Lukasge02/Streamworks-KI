/**
 * Smart Chat Hook for XML Chat V2
 * Integrates with StreamWorks Smart Parameter Extraction APIs
 */

import { useState, useCallback, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

// ================================
// TYPES
// ================================

// Hierarchical Session Types
export interface JobConfiguration {
  job_type: string
  job_name: string
  parameters: Record<string, any>
  completion_percentage: number
}

export interface CompletionStatus {
  stream_complete: boolean
  jobs_complete: boolean
  overall_percentage: number
}

export interface HierarchicalSession {
  session_id: string
  session_type: 'STREAM_CONFIGURATION' | 'JOB_ONLY'
  stream_parameters: Record<string, any>
  jobs: JobConfiguration[]
  completion_status: CompletionStatus
  status: string
  dialog_state: string
  message: string
  suggested_questions: string[]
  created_at: string
}

// Legacy support for backwards compatibility
export interface SmartSession {
  session_id: string
  job_type?: string
  status: string
  dialog_state: string
  completion_percentage: number
  message: string
  suggested_questions: string[]
  created_at: string
}

export interface SmartChatMessage {
  session_id: string
  response_message: string
  dialog_state: string
  priority: string
  extracted_parameters: Record<string, any>
  parameter_confidences?: Record<string, number>
  next_parameter?: string
  completion_percentage: number
  suggested_questions: string[]
  validation_issues: string[]
  timestamp: string
  metadata?: Record<string, any>

  // LangExtract Source Grounding Data
  source_grounding_data?: {
    highlighted_ranges: Array<[number, number, string]>
    parameter_sources: Array<{
      name: string
      source_text: string
      character_offsets: [number, number]
      confidence: number
      highlight_color: string
    }>
    full_text: string
    extraction_quality: string
    overall_confidence: number
  }
  source_grounded_parameters?: Array<{
    name: string
    value: any
    confidence: number
    source_text: string
    character_offsets: [number, number]
    context_preview: string
    highlight_color: string
  }>
  extraction_quality?: string
  needs_review?: boolean
}

// Enhanced Parameters Interface
export interface HierarchicalParameters {
  streamParameters: Record<string, any>
  jobs: JobConfiguration[]
  completionStatus: CompletionStatus
}

export interface ExtractedParameters {
  [key: string]: any
}

export interface SendMessageRequest {
  message: string
}

export interface CreateSessionRequest {
  initial_message?: string
  job_type?: 'SAP' | 'FILE_TRANSFER' | 'STANDARD'
}

// ================================
// API FUNCTIONS
// ================================

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
const SMART_API = `${API_BASE}/api/chat-xml/smart`

async function createSmartSession(request: CreateSessionRequest): Promise<SmartSession> {
  const response = await fetch(`${SMART_API}/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Session creation failed' }))
    throw new Error(error.error || 'Failed to create session')
  }

  return response.json()
}

async function sendSmartMessage(sessionId: string, request: SendMessageRequest): Promise<SmartChatMessage> {
  const response = await fetch(`${SMART_API}/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Message sending failed' }))
    throw new Error(error.error || 'Failed to send message')
  }

  return response.json()
}

async function getSessionStatus(sessionId: string): Promise<SmartSession> {
  const response = await fetch(`${SMART_API}/sessions/${sessionId}/status`)

  if (!response.ok) {
    throw new Error('Failed to get session status')
  }

  return response.json()
}

async function getExtractedParameters(sessionId: string): Promise<ExtractedParameters> {
  const response = await fetch(`${SMART_API}/sessions/${sessionId}/parameters`)

  if (!response.ok) {
    throw new Error('Failed to get extracted parameters')
  }

  const data = await response.json()
  console.log('📥 Raw parameters response:', data)

  // Return parameters from the response data structure
  if (data && typeof data === 'object') {
    if ('parameters' in data) {
      console.log('✅ Found parameters in response:', data.parameters)
      return data.parameters as ExtractedParameters
    }
    if ('raw_parameters' in data) {
      console.log('✅ Found raw_parameters in response:', data.raw_parameters)
      return data.raw_parameters as ExtractedParameters
    }
  }

  console.log('⚠️ No parameters found, returning empty object')
  return {}
}

// New Hierarchical API Functions
async function getHierarchicalSession(sessionId: string): Promise<HierarchicalSession> {
  const response = await fetch(`${SMART_API}/sessions/${sessionId}/hierarchical`)

  if (!response.ok) {
    throw new Error('Failed to get hierarchical session')
  }

  const data = await response.json()
  console.log('🏗️ Hierarchical session response:', data)
  return data as HierarchicalSession
}

async function getHierarchicalParameters(sessionId: string): Promise<HierarchicalParameters> {
  const response = await fetch(`${SMART_API}/sessions/${sessionId}/hierarchical-parameters`)

  if (!response.ok) {
    throw new Error('Failed to get hierarchical parameters')
  }

  const data = await response.json()
  console.log('📊 Hierarchical parameters response:', data)

  return {
    streamParameters: data.stream_parameters || {},
    jobs: data.jobs || [],
    completionStatus: data.completion_status || {
      stream_complete: false,
      jobs_complete: false,
      overall_percentage: 0
    }
  }
}

async function generateXMLFromSession(sessionId: string): Promise<{ success: boolean; xml?: string; error?: string }> {
  const response = await fetch(`${SMART_API}/sessions/${sessionId}/generate-xml`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'XML generation failed' }))
    throw new Error(error.error || 'Failed to generate XML')
  }

  return response.json()
}

async function generateHierarchicalXML(sessionId: string): Promise<{ success: boolean; xml?: string; error?: string }> {
  const response = await fetch(`${SMART_API}/sessions/${sessionId}/generate-hierarchical-xml`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Hierarchical XML generation failed' }))
    throw new Error(error.error || 'Failed to generate hierarchical XML')
  }

  return response.json()
}

// ================================
// CUSTOM HOOK
// ================================

export interface UseSmartChatReturn {
  // Session Management (Legacy)
  currentSession: SmartSession | null
  isCreatingSession: boolean
  createSession: (request: CreateSessionRequest) => Promise<SmartSession>

  // Hierarchical Session Management
  hierarchicalSession: HierarchicalSession | null
  isLoadingHierarchical: boolean
  refreshHierarchicalSession: () => void

  // Messaging
  sendSmartMessage: (message: string, sessionIdOverride?: string) => Promise<SmartChatMessage>
  isSendingMessage: boolean
  lastResponse: SmartChatMessage | null

  // Parameters (Legacy)
  extractedParameters: ExtractedParameters
  isLoadingParameters: boolean
  refreshParameters: () => void

  // Hierarchical Parameters
  hierarchicalParameters: HierarchicalParameters
  isLoadingHierarchicalParameters: boolean
  refreshHierarchicalParameters: () => void

  // XML Generation
  generateXML: () => Promise<string>
  generateHierarchicalXML: () => Promise<string>
  isGeneratingXML: boolean

  // Session Status
  refreshStatus: () => void
  isLoadingStatus: boolean

  // Utility
  reset: () => void
  error: string | null
}

export function useSmartChat(): UseSmartChatReturn {
  const [currentSession, setCurrentSession] = useState<SmartSession | null>(null)
  const [hierarchicalSession, setHierarchicalSession] = useState<HierarchicalSession | null>(null)
  const [lastResponse, setLastResponse] = useState<SmartChatMessage | null>(null)
  const [error, setError] = useState<string | null>(null)

  const queryClient = useQueryClient()

  // Session Creation
  const createSessionMutation = useMutation({
    mutationFn: createSmartSession,
    onSuccess: (session) => {
      setCurrentSession(session)
      setError(null)
      toast.success('Smart Chat Session erstellt!')
    },
    onError: (error: Error) => {
      setError(error.message)
      toast.error(`Session creation failed: ${error.message}`)
    }
  })

  // Message Sending
  const sendMessageMutation = useMutation({
    mutationFn: ({ sessionId, message }: { sessionId: string; message: string }) =>
      sendSmartMessage(sessionId, { message }),
    onSuccess: (response) => {
      setLastResponse(response)
      setError(null)

      console.log('📨 Message sent successfully:', response)

      // Refresh extracted parameters after each message
      if (response.session_id) {
        console.log('🔄 Invalidating parameter queries for session:', response.session_id)
        queryClient.invalidateQueries({ queryKey: ['parameters', response.session_id] })
        queryClient.invalidateQueries({ queryKey: ['hierarchical-parameters', response.session_id] })
        queryClient.invalidateQueries({ queryKey: ['hierarchical-session', response.session_id] })
        queryClient.invalidateQueries({ queryKey: ['session-status', response.session_id] })

        // Force a refetch of parameters immediately
        setTimeout(() => {
          queryClient.refetchQueries({ queryKey: ['parameters', response.session_id] })
          queryClient.refetchQueries({ queryKey: ['hierarchical-parameters', response.session_id] })
          queryClient.refetchQueries({ queryKey: ['hierarchical-session', response.session_id] })
        }, 100)
      }
    },
    onError: (error: Error) => {
      setError(error.message)
      toast.error(`Message failed: ${error.message}`)
    }
  })

  // XML Generation
  const generateXMLMutation = useMutation({
    mutationFn: (sessionId: string) => generateXMLFromSession(sessionId),
    onSuccess: (result) => {
      if (result.success && result.xml) {
        toast.success('XML erfolgreich generiert!')
      } else {
        toast.error(result.error || 'XML generation failed')
      }
    },
    onError: (error: Error) => {
      setError(error.message)
      toast.error(`XML generation failed: ${error.message}`)
    }
  })

  // Hierarchical XML Generation
  const generateHierarchicalXMLMutation = useMutation({
    mutationFn: (sessionId: string) => generateHierarchicalXML(sessionId),
    onSuccess: (result) => {
      if (result.success && result.xml) {
        toast.success('Hierarchical XML erfolgreich generiert!')
      } else {
        toast.error(result.error || 'Hierarchical XML generation failed')
      }
    },
    onError: (error: Error) => {
      setError(error.message)
      toast.error(`Hierarchical XML generation failed: ${error.message}`)
    }
  })

  const sessionId = currentSession?.session_id || hierarchicalSession?.session_id

  // Parameters Query - Intelligent refreshing only when needed
  const parametersQuery = useQuery<ExtractedParameters>({
    queryKey: ['parameters', sessionId],
    enabled: Boolean(sessionId),
    staleTime: 5000, // 5 seconds freshness
    gcTime: 30000, // 30 seconds cache
    refetchOnWindowFocus: false, // Don't spam on focus
    // Only refetch on message send, not continuously
    queryFn: ({ queryKey }) => {
      console.log('🔍 Fetching parameters for session:', queryKey[1])
      return getExtractedParameters(queryKey[1] as string)
    }
  })

  // Hierarchical Parameters Query
  const hierarchicalParametersQuery = useQuery<HierarchicalParameters>({
    queryKey: ['hierarchical-parameters', sessionId],
    enabled: Boolean(sessionId),
    staleTime: 5000, // 5 seconds freshness
    gcTime: 30000, // 30 seconds cache
    refetchOnWindowFocus: false,
    queryFn: ({ queryKey }) => {
      console.log('🏗️ Fetching hierarchical parameters for session:', queryKey[1])
      return getHierarchicalParameters(queryKey[1] as string)
    }
  })

  // Hierarchical Session Query
  const hierarchicalSessionQuery = useQuery<HierarchicalSession>({
    queryKey: ['hierarchical-session', sessionId],
    enabled: Boolean(sessionId),
    staleTime: 5000,
    gcTime: 30000,
    refetchOnWindowFocus: false,
    queryFn: ({ queryKey }) => {
      console.log('🏗️ Fetching hierarchical session for session:', queryKey[1])
      return getHierarchicalSession(queryKey[1] as string)
    }
  })

  // Session Status Query
  const statusQuery = useQuery<SmartSession>({
    queryKey: ['session-status', sessionId],
    enabled: Boolean(sessionId),
    queryFn: ({ queryKey }) => getSessionStatus(queryKey[1] as string)
  })

  useEffect(() => {
    if (statusQuery.data) {
      setCurrentSession(statusQuery.data)
    }
  }, [statusQuery.data])

  useEffect(() => {
    if (hierarchicalSessionQuery.data) {
      setHierarchicalSession(hierarchicalSessionQuery.data)
    }
  }, [hierarchicalSessionQuery.data])

  // Public Methods
  const createSession = useCallback(async (request: CreateSessionRequest) => {
    return createSessionMutation.mutateAsync(request)
  }, [createSessionMutation])

  const sendMessage = useCallback(async (message: string, sessionOverride?: string) => {
    const targetSessionId = sessionOverride ?? sessionId
    if (!targetSessionId) {
      throw new Error('No active session')
    }
    return sendMessageMutation.mutateAsync({
      sessionId: targetSessionId,
      message
    })
  }, [sessionId, sendMessageMutation])

  const generateXML = useCallback(async () => {
    if (!currentSession) {
      throw new Error('No active session')
    }
    const result = await generateXMLMutation.mutateAsync(currentSession.session_id)
    if (result.success && result.xml) {
      return result.xml
    }
    throw new Error(result.error || 'XML generation failed')
  }, [currentSession, generateXMLMutation])

  const generateHierarchicalXMLFunc = useCallback(async () => {
    const activeSession = hierarchicalSession || currentSession
    if (!activeSession) {
      throw new Error('No active session')
    }
    const result = await generateHierarchicalXMLMutation.mutateAsync(activeSession.session_id)
    if (result.success && result.xml) {
      return result.xml
    }
    throw new Error(result.error || 'Hierarchical XML generation failed')
  }, [hierarchicalSession, currentSession, generateHierarchicalXMLMutation])

  const reset = useCallback(() => {
    setCurrentSession(null)
    setHierarchicalSession(null)
    setLastResponse(null)
    setError(null)
    queryClient.clear()
  }, [queryClient])

  return {
    // Session Management (Legacy)
    currentSession,
    isCreatingSession: createSessionMutation.isPending,
    createSession,

    // Hierarchical Session Management
    hierarchicalSession,
    isLoadingHierarchical: hierarchicalSessionQuery.isFetching,
    refreshHierarchicalSession: () => hierarchicalSessionQuery.refetch(),

    // Messaging
    sendSmartMessage: sendMessage,
    isSendingMessage: sendMessageMutation.isPending,
    lastResponse,

    // Parameters (Legacy)
    extractedParameters: parametersQuery.data ?? {},
    isLoadingParameters: parametersQuery.isFetching,
    refreshParameters: () => parametersQuery.refetch(),

    // Hierarchical Parameters
    hierarchicalParameters: hierarchicalParametersQuery.data ?? {
      streamParameters: {},
      jobs: [],
      completionStatus: {
        stream_complete: false,
        jobs_complete: false,
        overall_percentage: 0
      }
    },
    isLoadingHierarchicalParameters: hierarchicalParametersQuery.isFetching,
    refreshHierarchicalParameters: () => hierarchicalParametersQuery.refetch(),

    // XML Generation
    generateXML,
    generateHierarchicalXML: generateHierarchicalXMLFunc,
    isGeneratingXML: generateXMLMutation.isPending || generateHierarchicalXMLMutation.isPending,

    // Session Status
    refreshStatus: () => statusQuery.refetch(),
    isLoadingStatus: statusQuery.isFetching,

    // Utility
    reset,
    error
  }
}
