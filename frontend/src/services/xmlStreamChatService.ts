/**
 * XML Stream Chat Service
 * Handles conversational AI for XML stream creation
 * Integrates with backend XMLStreamConversationService
 */

// ================================
// TYPES
// ================================

export interface XMLStreamConversationState {
  phase: 'initialization' | 'job_configuration' | 'stream_properties' | 'scheduling' | 'validation' | 'creation' | 'completed' | 'error'
  job_type?: 'sap' | 'file_transfer' | 'standard' | 'custom'
  collected_data: Record<string, any>
  missing_required_fields: string[]
  validation_errors: Array<{
    type: string
    field: string
    message: string
    suggestions?: string[]
  }>
  stream_id?: string
  xml_content?: string
  completion_percentage: number
  last_user_message?: string
  context_history?: Array<{
    role: string
    content: string
    timestamp: string
  }>
}

export interface XMLStreamConversationRequest {
  message: string
  session_id: string
  current_state?: XMLStreamConversationState
}

export interface XMLStreamConversationResponse {
  message: string
  suggestions: string[]
  state: XMLStreamConversationState
  requires_user_input: boolean
  action_taken?: string
  errors: string[]
}

// ================================
// XML STREAM CHAT SERVICE
// ================================

class XMLStreamChatService {
  private baseUrl = '/api/chat'
  private userId: string

  constructor(userId: string = 'default-user') {
    this.userId = userId
  }

  /**
   * Process conversation message for XML stream creation
   */
  async processConversation(
    request: XMLStreamConversationRequest
  ): Promise<XMLStreamConversationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/xml-stream-conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': this.userId,
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(`Conversation failed: ${response.status} ${errorData.detail}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('XML Stream conversation error:', error)
      throw error
    }
  }

  /**
   * Get current conversation state for a session
   */
  async getConversationState(sessionId: string): Promise<XMLStreamConversationState | null> {
    try {
      const response = await fetch(`${this.baseUrl}/xml-stream-conversation/${sessionId}/state`, {
        headers: {
          'X-User-ID': this.userId,
        },
      })

      if (!response.ok) {
        if (response.status === 404) {
          return null // No state found
        }
        throw new Error(`Failed to get state: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Get conversation state error:', error)
      return null
    }
  }

  /**
   * Start a new XML stream conversation
   */
  async startNewConversation(sessionId: string): Promise<XMLStreamConversationResponse> {
    const initialState: XMLStreamConversationState = {
      phase: 'initialization',
      collected_data: {},
      missing_required_fields: [],
      validation_errors: [],
      completion_percentage: 0.0,
      context_history: []
    }

    return this.processConversation({
      message: "Ich möchte einen neuen XML Stream erstellen",
      session_id: sessionId,
      current_state: initialState
    })
  }

  /**
   * Continue existing conversation
   */
  async continueConversation(
    sessionId: string,
    message: string,
    currentState?: XMLStreamConversationState
  ): Promise<XMLStreamConversationResponse> {
    // Get current state if not provided
    let state = currentState
    if (!state) {
      state = await this.getConversationState(sessionId)
    }

    return this.processConversation({
      message,
      session_id: sessionId,
      current_state: state || undefined
    })
  }

  /**
   * Check if message is related to XML stream creation
   */
  isXMLStreamMessage(message: string): boolean {
    const xmlStreamKeywords = [
      'stream', 'xml', 'job', 'sap', 'file', 'transfer', 'script', 'agent',
      'erstellen', 'konfigurieren', 'schedule', 'zeitplan', 'ausführen'
    ]

    const messageLower = message.toLowerCase()
    return xmlStreamKeywords.some(keyword => messageLower.includes(keyword))
  }

  /**
   * Get completion progress as percentage and description
   */
  getProgressInfo(state: XMLStreamConversationState): {
    percentage: number
    description: string
    phase: string
  } {
    const phaseDescriptions = {
      'initialization': 'Stream wird initialisiert...',
      'job_configuration': 'Job wird konfiguriert...',
      'stream_properties': 'Stream-Eigenschaften werden definiert...',
      'scheduling': 'Zeitplan wird erstellt...',
      'validation': 'Konfiguration wird validiert...',
      'creation': 'Stream wird erstellt...',
      'completed': 'Stream erfolgreich erstellt!',
      'error': 'Fehler bei der Stream-Erstellung'
    }

    return {
      percentage: Math.round(state.completion_percentage * 100),
      description: phaseDescriptions[state.phase] || 'Verarbeitung...',
      phase: state.phase
    }
  }

  /**
   * Extract entities and structured data from conversation state
   */
  getExtractedEntities(state: XMLStreamConversationState): {
    jobType?: string
    streamName?: string
    entities: Array<{
      field: string
      value: any
      confidence?: number
    }>
  } {
    const entities = []

    // Extract job form data
    if (state.collected_data.jobForm) {
      Object.entries(state.collected_data.jobForm).forEach(([key, value]) => {
        if (value) {
          entities.push({
            field: `jobForm.${key}`,
            value,
            confidence: 0.8
          })
        }
      })
    }

    // Extract stream properties
    if (state.collected_data.streamProperties) {
      Object.entries(state.collected_data.streamProperties).forEach(([key, value]) => {
        if (value) {
          entities.push({
            field: `streamProperties.${key}`,
            value,
            confidence: 0.9
          })
        }
      })
    }

    return {
      jobType: state.job_type,
      streamName: state.collected_data.streamProperties?.streamName,
      entities
    }
  }

  /**
   * Get validation issues in user-friendly format
   */
  getValidationIssues(state: XMLStreamConversationState): Array<{
    field: string
    message: string
    severity: 'error' | 'warning' | 'info'
    suggestions: string[]
  }> {
    return state.validation_errors.map(error => ({
      field: error.field,
      message: error.message,
      severity: error.type === 'missing_field' ? 'error' : 'warning',
      suggestions: error.suggestions || []
    }))
  }

  /**
   * Check if conversation is complete and stream can be created
   */
  canCreateStream(state: XMLStreamConversationState): boolean {
    return (
      state.phase === 'creation' ||
      (state.completion_percentage >= 0.8 && state.validation_errors.length === 0)
    )
  }

  /**
   * Update user ID for API calls
   */
  setUserId(userId: string): void {
    this.userId = userId
  }

  getUserId(): string {
    return this.userId
  }
}

// ================================
// SINGLETON EXPORT
// ================================

export const xmlStreamChatService = new XMLStreamChatService()
export default xmlStreamChatService