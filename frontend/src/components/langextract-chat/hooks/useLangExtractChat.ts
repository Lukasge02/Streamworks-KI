import { useState, useCallback, useEffect } from 'react'
import apiService from '@/services/api.service'

interface Message {
  role: 'user' | 'assistant'
  type: 'user' | 'assistant'  // Support both role and type for compatibility
  content: string
  extracted_parameters?: Record<string, any>
  sourceGrounding?: Array<{
    parameter: string
    source: string
    confidence: number
  }>
  timestamp: string
}

interface LangExtractResponse {
  session_id: string
  message?: string
  response_message?: string
  extracted_stream_parameters: Record<string, any>
  extracted_job_parameters: Record<string, any>
  completion_percentage?: number
  critical_missing?: string[]
  job_type?: string
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
  const [criticalMissing, setCriticalMissing] = useState<string[] | null>(null)
  const [parametersLoaded, setParametersLoaded] = useState(false)
  const [detectedJobType, setDetectedJobType] = useState<string | null>(null)

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

      // 🎯 FIX: ZUERST State komplett leeren (als wäre Session bereits gewechselt)
      setMessages([])
      setStreamParameters({})
      setJobParameters({})
      setCompletionPercentage(0)
      setCriticalMissing(null)
      setParametersLoaded(false)
      setDetectedJobType(null)

      // 🎯 FIX: DANN API-Call für neue Session
      const response = await apiService.createLangExtractSession(jobType)

      // 🎯 FIX: DANN neue Session setzen
      setSession(response.session_id)

      // 🎯 FIX: DANN Welcome Message hinzufügen (ist jetzt in neuer Session)
      setMessages([{
        role: 'assistant',
        type: 'assistant',
        content: response.message || 'Neue Session erstellt',
        timestamp: new Date().toISOString()
      }])

      setCompletionPercentage(response.completion_percentage || 0)

      // Reload sessions to include new session
      loadSessions()

      return response.session_id
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

      // 🎯 FIX: SOFORT State komplett leeren (UI reagiert sofort)
      setMessages([])
      setStreamParameters({})      // ✅ Parameter UI wird sofort geleert
      setJobParameters({})         // ✅ Parameter UI wird sofort geleert
      setCompletionPercentage(0)   // ✅ Completion wird sofort zurückgesetzt
      setCriticalMissing(null)     // ✅ Nicht leer, sondern null (lädt noch)
      setParametersLoaded(false)   // ✅ Markiere als "lädt noch"
      setDetectedJobType(null)     // ✅ Job Type zurücksetzen

      // Switch to new session
      setSession(sessionId)

      // Load session messages
      try {
        const messagesResponse = await apiService.getLangExtractMessages(sessionId)
        const loadedMessages = messagesResponse.messages.map(msg => ({
          role: msg.type as 'user' | 'assistant',
          type: msg.type as 'user' | 'assistant',
          content: msg.content,
          timestamp: msg.timestamp
        }))
        setMessages(loadedMessages)
        console.log(`✅ Loaded ${loadedMessages.length} messages for session ${sessionId}`)
      } catch (error) {
        console.error('Failed to load session messages:', error)
        // Continue with empty messages if loading fails
      }

      // Load session parameters
      try {
        const parametersResponse = await apiService.getLangExtractParameters(sessionId)

        // 🧹 PHASE 2 FIX: Clean parameters when loading session
        const cleanedStreamParams = filterCleanParameters(parametersResponse.stream_parameters || {})
        const cleanedJobParams = filterCleanParameters(parametersResponse.job_parameters || {})

        setStreamParameters(cleanedStreamParams)
        setJobParameters(cleanedJobParams)
        setCompletionPercentage(parametersResponse.completion_percentage || 0)
        setCriticalMissing(parametersResponse.critical_missing || ['PARAMETERS_NOT_LOADED'])
        setDetectedJobType(parametersResponse.job_type || null)
        setParametersLoaded(true)
        console.log(`✅ Loaded parameters for session ${sessionId}`, {
          streamParams: Object.keys(cleanedStreamParams),
          jobParams: Object.keys(cleanedJobParams),
          criticalMissing: parametersResponse.critical_missing || ['PARAMETERS_NOT_LOADED'],
          detectedJobType: parametersResponse.job_type
        })
      } catch (error) {
        console.error('Failed to load session parameters:', error)
        // Mark as loaded but with error state
        setCriticalMissing(['LOADING_ERROR'])
        setParametersLoaded(true)
      }

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
      await apiService.deleteLangExtractSession(sessionId)

      // Remove from local state
      setSessions(prev => prev.filter(s => s.session_id !== sessionId))

      // If deleting current session, clear it
      if (session === sessionId) {
        setSession(null)
        setMessages([])
        setStreamParameters({})
        setJobParameters({})
        setCompletionPercentage(0)
        setCriticalMissing(null)
        setParametersLoaded(false)
        setDetectedJobType(null)
      }

      return true
    } catch (error) {
      console.error('Failed to delete session:', error)
      throw error
    }
  }, [session])

  const deleteAllSessions = useCallback(async () => {
    try {
      setIsLoading(true)

      const result = await apiService.deleteAllLangExtractSessions()

      // Clear all local state
      setSessions([])
      setSession(null)
      setMessages([])
      setStreamParameters({})
      setJobParameters({})
      setCompletionPercentage(0)
      setCriticalMissing(null)
      setParametersLoaded(false)
      setDetectedJobType(null)

      console.log(`✅ Deleted ${result.deleted_count}/${result.total_sessions} sessions`)

      return result
    } catch (error) {
      console.error('Failed to delete all sessions:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  const sendMessage = useCallback(async (message: string) => {
    if (!session) {
      console.error('No active session')
      return
    }

    try {
      setIsLoading(true)

      // Add user message immediately
      const userMessage: Message = {
        role: 'user',
        type: 'user',
        content: message,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])

      // Send to API
      const response = await apiService.sendLangExtractMessage({
        session_id: session,
        message: message
      })

      // 🧹 PHASE 2 FIX: Filter and clean parameters before updating state
      if (response.extracted_stream_parameters) {
        const cleanedStreamParams = filterCleanParameters(response.extracted_stream_parameters)
        setStreamParameters(prev => ({
          ...prev,
          ...cleanedStreamParams
        }))
      }

      if (response.extracted_job_parameters) {
        const cleanedJobParams = filterCleanParameters(response.extracted_job_parameters)
        setJobParameters(prev => ({
          ...prev,
          ...cleanedJobParams
        }))
      }

      // Update completion, missing, and job type
      setCompletionPercentage(response.completion_percentage || 0)
      setCriticalMissing(response.critical_missing || [])

      // 🎯 Update Job Type from Backend Detection (88.9% Accuracy)
      if (response.job_type && response.job_type !== detectedJobType) {
        console.log('🎯 Job Type updated from Backend:', {
          previous: detectedJobType,
          new: response.job_type,
          source: 'Message Response'
        })
        setDetectedJobType(response.job_type)
      }

      // Keep parametersLoaded true during message processing

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        type: 'assistant',
        content: response.response_message || 'Keine Antwort erhalten',
        extracted_parameters: {
          stream: response.extracted_stream_parameters || {},
          job: response.extracted_job_parameters || {}
        },
        sourceGrounding: Array.isArray(response.source_grounding_data)
          ? response.source_grounding_data.map((sg: any) => ({
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

      return response
    } catch (error) {
      console.error('Failed to send message:', error)

      // Add error message
      setMessages(prev => [...prev, {
        role: 'assistant',
        type: 'assistant',
        content: 'Entschuldigung, es gab einen Fehler bei der Verarbeitung Ihrer Nachricht.',
        timestamp: new Date().toISOString()
      }])

      throw error
    } finally {
      setIsLoading(false)
    }
  }, [session])

  const generateXML = useCallback(async (forceGeneration = false, jobType?: string) => {
    if (!session) {
      console.error('No active session')
      return
    }

    try {
      setIsLoading(true)

      const response = await apiService.generateLangExtractXML({
        session_id: session,
        job_type: jobType,
        force_generation: forceGeneration
      })

      return response
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
    parametersLoaded,
    criticalMissing,
    detectedJobType,
    createSession,
    switchSession,
    deleteSession,
    deleteAllSessions,
    loadSessions,
    sendMessage,
    generateXML,
    getParameters,
    correctParameter
  }
}

/**
 * 🧹 PHASE 2 FIX: Filter out LangExtract technical artifacts from parameters
 */
function filterCleanParameters(parameters: Record<string, any>): Record<string, any> {
  const cleaned: Record<string, any> = {}

  // Technical fields that should never be shown to users
  const blacklistFields = new Set([
    'extractions',
    'text',
    '_document_id',
    'extraction_class',
    'extraction_text',
    'confidence',
    'highlighted_ranges',
    'source_grounding',
    'metadata',
    '__dict__',
    '__class__',
    'api_calls_made',
    'extraction_duration',
    'warnings',
    'extraction_errors',
    'processing_time'
  ])

  for (const [key, value] of Object.entries(parameters)) {
    // Skip blacklisted technical fields
    if (blacklistFields.has(key.toLowerCase())) {
      continue
    }

    // Skip empty or invalid values
    if (value === null || value === undefined || value === '') {
      continue
    }

    // Skip object references like "[object Object],[object Object]..."
    if (typeof value === 'string' && value.toLowerCase().includes('[object')) {
      continue
    }

    // Only include clean, user-relevant parameters
    cleaned[key] = value
  }

  console.log(`🧹 Filtered ${Object.keys(parameters).length} → ${Object.keys(cleaned).length} parameters`)
  return cleaned
}