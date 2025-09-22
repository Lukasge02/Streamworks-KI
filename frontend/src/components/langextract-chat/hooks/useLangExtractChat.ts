import { useState, useCallback, useEffect } from 'react'
import apiService from '@/services/api.service'

interface Message {
  role: 'user' | 'assistant'
  content: string
  extractedParameters?: Record<string, any>
  sourceGrounding?: Array<{
    parameter: string
    source: string
    confidence: number
  }>
  timestamp: string
}

interface LangExtractResponse {
  session_id: string
  message: string
  response_message?: string
  extracted_stream_parameters: Record<string, any>
  extracted_job_parameters: Record<string, any>
  completion_percentage: number
  critical_missing: string[]
  source_grounding_data?: Array<{
    parameter: string
    source_text: string
    confidence: number
    start_idx: number
    end_idx: number
  }> | null
  suggested_questions?: string[]
  processing_time?: number
}

interface LangExtractSession {
  session_id: string
  stream_name: string
  job_type?: string
  completion_percentage: number
  created_at: string
  last_activity: string
}

export const useLangExtractChat = () => {
  const [session, setSession] = useState<string | null>(null)
  const [sessions, setSessions] = useState<LangExtractSession[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingSessions, setIsLoadingSessions] = useState(false)
  const [streamParameters, setStreamParameters] = useState<Record<string, any>>({})
  const [jobParameters, setJobParameters] = useState<Record<string, any>>({})
  const [completionPercentage, setCompletionPercentage] = useState(0)
  const [criticalMissing, setCriticalMissing] = useState<string[]>([])

  // Load sessions on component mount
  const loadSessions = useCallback(async () => {
    try {
      setIsLoadingSessions(true)
      const response = await apiService.get<{
        sessions: LangExtractSession[]
        total_count: number
      }>('/api/streamworks/sessions')

      setSessions(response.data.sessions)
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setIsLoadingSessions(false)
    }
  }, [])

  // Load sessions on mount and auto-select most recent
  useEffect(() => {
    const initializeApp = async () => {
      await loadSessions()
    }
    initializeApp()
  }, [loadSessions])

  const createSession = useCallback(async (jobType?: string) => {
    try {
      setIsLoading(true)
      const response = await apiService.post<{ session_id: string; message: string; completion_percentage?: number }>('/api/streamworks/sessions', {
        job_type: jobType
      })

      setSession(response.data.session_id)

      // Add welcome message
      setMessages([{
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date().toISOString()
      }])

      setCompletionPercentage(response.data.completion_percentage || 0)

      // Reload sessions to include new session
      loadSessions()

      return response.data.session_id
    } catch (error) {
      console.error('Failed to create session:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [loadSessions])

  const switchSession = useCallback(async (sessionId: string) => {
    try {
      setIsLoading(true)

      // Clear current state
      setMessages([])
      setStreamParameters({})
      setJobParameters({})
      setCompletionPercentage(0)
      setCriticalMissing([])

      // Switch to new session
      setSession(sessionId)

      // Load session data will be handled after getParameters is defined
      // This will be called later in the flow

      return sessionId
    } catch (error) {
      console.error('Failed to switch session:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Auto-select most recent session if no current session
  useEffect(() => {
    if (sessions.length > 0 && !session) {
      // Sort sessions by last_activity and select the most recent
      const sortedSessions = [...sessions].sort((a, b) =>
        new Date(b.last_activity).getTime() - new Date(a.last_activity).getTime()
      )
      const mostRecentSession = sortedSessions[0]

      if (mostRecentSession) {
        switchSession(mostRecentSession.session_id)
      }
    }
  }, [sessions, session, switchSession])

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await apiService.delete(`/api/streamworks/sessions/${sessionId}`)

      // Remove from local state
      setSessions(prev => prev.filter(s => s.session_id !== sessionId))

      // If deleting current session, clear it
      if (session === sessionId) {
        setSession(null)
        setMessages([])
        setStreamParameters({})
        setJobParameters({})
        setCompletionPercentage(0)
        setCriticalMissing([])
      }

      return true
    } catch (error) {
      console.error('Failed to delete session:', error)
      throw error
    }
  }, [session])

  const sendMessage = useCallback(async (message: string) => {
    if (!session) {
      console.error('No active session')
      return
    }

    try {
      setIsLoading(true)

      // Add user message immediately
      const userMessage: Message = {
        type: 'user',
        content: message,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])

      // Send to API
      const response = await apiService.post<LangExtractResponse>(
        `/api/streamworks/sessions/${session}/messages`,
        { message }
      )

      // Update parameters
      if (response.data.extracted_stream_parameters) {
        setStreamParameters(prev => ({
          ...prev,
          ...response.data.extracted_stream_parameters
        }))
      }

      if (response.data.extracted_job_parameters) {
        setJobParameters(prev => ({
          ...prev,
          ...response.data.extracted_job_parameters
        }))
      }

      // Update completion and missing
      setCompletionPercentage(response.data.completion_percentage)
      setCriticalMissing(response.data.critical_missing)

      // Add assistant response
      const assistantMessage: Message = {
        type: 'assistant',
        content: response.data.response_message || response.data.message || 'Keine Antwort erhalten',
        extracted_parameters: {
          stream: response.data.extracted_stream_parameters || {},
          job: response.data.extracted_job_parameters || {}
        },
        sourceGrounding: Array.isArray(response.data.source_grounding_data)
          ? response.data.source_grounding_data.map((sg: any) => ({
              parameter: sg.parameter,
              source: sg.source_text,
              confidence: sg.confidence
            }))
          : [],
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMessage])

      // Reload sessions to update last_activity timestamps
      loadSessions()

      return response.data
    } catch (error) {
      console.error('Failed to send message:', error)

      // Add error message
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: 'Entschuldigung, es gab einen Fehler bei der Verarbeitung Ihrer Nachricht.',
        timestamp: new Date().toISOString()
      }])

      throw error
    } finally {
      setIsLoading(false)
    }
  }, [session])

  const generateXML = useCallback(async (forceGeneration = false) => {
    if (!session) {
      console.error('No active session')
      return
    }

    try {
      setIsLoading(true)

      const response = await apiService.post(
        `/api/streamworks/sessions/${session}/generate-xml`,
        { force_generation: forceGeneration }
      )

      return response.data
    } catch (error) {
      console.error('Failed to generate XML:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [session])

  const getParameters = useCallback(async () => {
    if (!session) {
      console.error('No active session')
      return
    }

    try {
      const response = await apiService.get<{
        stream_parameters: Record<string, any>
        job_parameters: Record<string, any>
        completion_percentage: number
        critical_missing: string[]
      }>(
        `/api/streamworks/sessions/${session}/parameters`
      )

      setStreamParameters(response.data.stream_parameters)
      setJobParameters(response.data.job_parameters)
      setCompletionPercentage(response.data.completion_percentage)
      setCriticalMissing(response.data.critical_missing)

      return response.data
    } catch (error) {
      console.error('Failed to get parameters:', error)
      throw error
    }
  }, [session])

  const correctParameter = useCallback(async (
    parameterName: string,
    newValue: any,
    reason?: string
  ) => {
    if (!session) {
      console.error('No active session')
      return
    }

    try {
      setIsLoading(true)

      const response = await apiService.post(
        `/api/streamworks/sessions/${session}/parameters/correct`,
        {
          parameter_name: parameterName,
          new_value: newValue,
          reason
        }
      )

      // Update local state
      if (parameterName in streamParameters) {
        setStreamParameters(prev => ({
          ...prev,
          [parameterName]: newValue
        }))
      } else if (parameterName in jobParameters) {
        setJobParameters(prev => ({
          ...prev,
          [parameterName]: newValue
        }))
      }

      return response.data
    } catch (error) {
      console.error('Failed to correct parameter:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [session, streamParameters, jobParameters])

  return {
    session,
    sessions,
    messages,
    isLoading,
    isLoadingSessions,
    streamParameters,
    jobParameters,
    completionPercentage,
    criticalMissing,
    createSession,
    switchSession,
    deleteSession,
    loadSessions,
    sendMessage,
    generateXML,
    getParameters,
    correctParameter
  }
}