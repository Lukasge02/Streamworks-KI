'use client'

import React, { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
// import { ScrollArea } from '@/components/ui/scroll-area' // Temporarily disabled
import {
  Bot,
  User,
  Send,
  ArrowLeft,
  MessageSquare,
  Loader2,
  Sparkles,
  Save,
  CheckCircle,
  BarChart3,
  Clock,
  Target,
  AlertTriangle,
  Info
} from 'lucide-react'
import { WizardDataRenderer } from '@/components/xml-streams/WizardDataRenderer'
import { WizardFormData } from './types/wizard.types'
import {
  xmlStreamChatService,
  XMLStreamConversationState,
  XMLStreamConversationResponse
} from '@/services/xmlStreamChatService'
import { toast } from 'sonner'

interface ChatMessage {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: Date
}

interface ChatStreamCreatorProps {
  className?: string
}

export const ChatStreamCreator: React.FC<ChatStreamCreatorProps> = ({
  className = ''
}) => {
  const router = useRouter()
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'bot',
      content: 'Hallo! Ich helfe Ihnen dabei, einen neuen XML Stream zu erstellen. Beschreiben Sie einfach, was für einen Job Sie konfigurieren möchten. Zum Beispiel:\n\n• "Erstelle einen SAP Job für System P01 mit Report Z_PROG_01"\n• "Täglicher File Transfer von Server A nach Server B"\n• "Standard Job der täglich um 6 Uhr morgens läuft"',
      timestamp: new Date()
    }
  ])

  // Progress display helper
  const getProgressInfo = () => {
    if (!conversationState) return null
    return xmlStreamChatService.getProgressInfo(conversationState)
  }

  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamName, setStreamName] = useState('')
  const [wizardData, setWizardData] = useState<WizardFormData | null>(null)
  const [conversationState, setConversationState] = useState<XMLStreamConversationState | null>(null)
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([])
  const [sessionId] = useState(() => `xml-chat-${Date.now()}`)
  const [isInitialized, setIsInitialized] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize conversation when component loads
  useEffect(() => {
    const initializeConversation = async () => {
      if (isInitialized) return

      try {
        // Try to get existing conversation state
        let state = await xmlStreamChatService.getConversationState(sessionId)

        if (!state) {
          // Start new conversation
          console.log('🎆 Starting new XML Stream conversation')
          const response = await xmlStreamChatService.startNewConversation(sessionId)
          state = response.state

          // Add initial bot message if provided
          if (response.message && response.message !== messages[0]?.content) {
            const botMessage: ChatMessage = {
              id: 'init-' + Date.now(),
              type: 'bot',
              content: response.message,
              timestamp: new Date()
            }
            setMessages(prev => [...prev, botMessage])
          }

          // Set initial suggestions
          if (response.suggestions?.length > 0) {
            setSuggestedQuestions(response.suggestions)
          }
        } else {
          console.log('🔄 Resuming existing XML Stream conversation')
        }

        // Update states
        setConversationState(state)
        if (state) {
          const extractedData = xmlStreamChatService.getExtractedEntities(state)
          if (extractedData?.entities?.length > 0) {
            // Transform entities back to wizard format
            const newWizardData: Partial<WizardFormData> = {}
            extractedData.entities.forEach(entity => {
              const [section, field] = entity.field.split('.')
              if (section && field) {
                if (!newWizardData[section as keyof WizardFormData]) {
                  newWizardData[section as keyof WizardFormData] = {} as any
                }
                ;(newWizardData[section as keyof WizardFormData] as any)[field] = entity.value
              }
            })
            setWizardData(newWizardData as WizardFormData)
          }

          // Set stream name if available
          if (extractedData?.streamName) {
            setStreamName(extractedData.streamName)
          }
        }

        setIsInitialized(true)
      } catch (error) {
        console.error('Conversation initialization error:', error)
        toast.error('Fehler bei der Initialisierung des Chats')
      }
    }

    initializeConversation()
  }, [sessionId, isInitialized, messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Call backend API for entity extraction
      await callEntityExtractionAPI(inputMessage)
    } catch (error) {
      console.error('Chat processing error:', error)
      toast.error('Fehler bei der Verarbeitung der Nachricht')
    } finally {
      setIsLoading(false)
    }
  }

  const callEntityExtractionAPI = async (userInput: string) => {
    try {
      // Use new XML Stream Conversation Service
      const response = await xmlStreamChatService.continueConversation(
        sessionId,
        userInput,
        conversationState || undefined
      )

      console.log('🤖 XML Stream Conversation Response:', response)

      // Update conversation state
      if (response.state) {
        setConversationState(response.state)

        // Extract wizard data from conversation state
        const extractedData = xmlStreamChatService.getExtractedEntities(response.state)
        if (extractedData?.entities?.length > 0) {
          console.log('📊 Updating wizard data from entities:', extractedData)

          try {
            // Transform entities back to wizard format
            const newWizardData: Partial<WizardFormData> = { ...wizardData }

            extractedData.entities.forEach(entity => {
              if (entity?.field) {
                const [section, field] = entity.field.split('.')
                if (section && field) {
                  if (!newWizardData[section as keyof WizardFormData]) {
                    newWizardData[section as keyof WizardFormData] = {} as any
                  }
                  ;(newWizardData[section as keyof WizardFormData] as any)[field] = entity.value
                }
              }
            })

            setWizardData(newWizardData as WizardFormData)
          } catch (error) {
            console.error('Error transforming wizard data:', error)
          }
        }
      }

      // Update suggested questions
      if (response.suggestions?.length > 0) {
        setSuggestedQuestions(response.suggestions)
      }

      // Add bot response
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response.message,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])

      // Handle special cases
      if (response.action_taken === 'stream_created' && response.state?.stream_id) {
        toast.success(`Stream erfolgreich erstellt! ID: ${response.state.stream_id}`)
      }

      if (response.errors?.length > 0) {
        response.errors.forEach(error => {
          toast.error(`Validierungsfehler: ${error}`)
        })
      }

    } catch (error) {
      console.error('XML Stream conversation error:', error)

      // Fallback to simple message
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: 'Entschuldigung, es gab ein Problem bei der Verarbeitung Ihrer Nachricht. Bitte versuchen Sie es erneut.',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSuggestedQuestion = (question: string) => {
    setInputMessage(question)
    // Optional: Auto-send the suggested question
    // handleSendMessage()
  }

  const handleSaveStream = async () => {
    if (!wizardData || !conversationState) {
      toast.error('Bitte konfigurieren Sie den Stream über den Chat')
      return
    }

    try {
      // Check if we can create the stream
      if (xmlStreamChatService.canCreateStream(conversationState)) {
        // Continue conversation with save request
        await xmlStreamChatService.continueConversation(
          sessionId,
          "Bitte speichere den Stream als Entwurf",
          conversationState
        )
      } else {
        toast.warning('Stream ist noch nicht vollständig konfiguriert')
      }
    } catch (error) {
      console.error('Save error:', error)
      toast.error('Fehler beim Speichern')
    }
  }

  const handleSubmitForReview = async () => {
    if (!wizardData || !conversationState) {
      toast.error('Bitte konfigurieren Sie den Stream über den Chat')
      return
    }

    try {
      // Check if we can create the stream
      if (xmlStreamChatService.canCreateStream(conversationState)) {
        // Continue conversation with submit request
        const response = await xmlStreamChatService.continueConversation(
          sessionId,
          "Bitte erstelle den Stream final und reiche ihn zur Freigabe ein",
          conversationState
        )

        if (response.state?.stream_id) {
          toast.success('Stream erfolgreich zur Freigabe eingereicht!')
          // Optional: Redirect to stream overview or edit page
          // router.push(`/xml/view/${response.state.stream_id}`)
        }
      } else {
        toast.warning('Stream ist noch nicht vollständig konfiguriert. Bitte vervollständigen Sie die Konfiguration über den Chat.')
      }
    } catch (error) {
      console.error('Submit error:', error)
      toast.error('Fehler beim Einreichen')
    }
  }

  return (
    <div className={`h-screen flex flex-col bg-gray-50 dark:bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/xml')}
              className="mr-2"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>

            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <MessageSquare className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Chat Stream Creator
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Erstellen Sie Streamworks-XML über natürliche Sprache
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Input
              placeholder="Stream Name..."
              value={streamName}
              onChange={(e) => setStreamName(e.target.value)}
              className="w-48"
            />
          </div>
        </div>
      </div>

      {/* Main Content - Split Layout */}
      <div className="flex-1 flex min-h-0">
        {/* Left: Chat Interface */}
        <div className="flex-1 flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
          {/* Chat Messages */}
          <div className="flex-1 p-4 overflow-auto">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] p-3 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {message.type === 'bot' && (
                        <Bot className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      )}
                      {message.type === 'user' && (
                        <User className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      )}
                      <div className="whitespace-pre-wrap text-sm">
                        {message.content}
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Bot className="w-4 h-4" />
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        Verarbeite Ihre Anfrage...
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Conversation Progress & Suggested Questions */}
          <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            {/* Progress Bar */}
            {conversationState && (() => {
              const progressInfo = getProgressInfo()
              return progressInfo && (
                <div className="mb-3">
                  <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                    <div className="flex items-center gap-1">
                      <BarChart3 className="w-4 h-4" />
                      <span>{progressInfo.description}</span>
                    </div>
                    <span>{progressInfo.percentage}% vollständig</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        progressInfo.phase === 'completed'
                          ? 'bg-green-600'
                          : progressInfo.phase === 'error'
                          ? 'bg-red-600'
                          : 'bg-blue-600'
                      }`}
                      style={{ width: `${progressInfo.percentage}%` }}
                    />
                  </div>
                </div>
              )
            })()}

            {/* Validation Issues */}
            {conversationState && conversationState.validation_errors?.length > 0 && (
              <div className="mb-3">
                <div className="flex items-center gap-1 text-xs text-orange-600 dark:text-orange-400 mb-2">
                  <AlertTriangle className="w-3 h-3" />
                  <span>Noch zu konfigurieren:</span>
                </div>
                <div className="space-y-1">
                  {xmlStreamChatService.getValidationIssues(conversationState)?.map((issue, index) => (
                    <div key={index} className="flex items-start gap-2 text-xs text-gray-600 dark:text-gray-400">
                      <div className={`w-2 h-2 rounded-full mt-1 flex-shrink-0 ${
                        issue.severity === 'error' ? 'bg-red-500' :
                        issue.severity === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`} />
                      <div>
                        <span className="font-medium">{issue.field}:</span>
                        <span className="ml-1">{issue.message}</span>
                        {issue.suggestions?.length > 0 && (
                          <div className="mt-1 flex flex-wrap gap-1">
                            {issue.suggestions?.map((suggestion, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleSuggestedQuestion(suggestion)}
                                className="px-2 py-0.5 text-xs bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded border"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Fields Info */}
            {conversationState && conversationState.missing_required_fields?.length > 0 && (
              <div className="mb-3">
                <div className="flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 mb-2">
                  <Info className="w-3 h-3" />
                  <span>Erforderliche Felder:</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {conversationState.missing_required_fields?.map((field, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded border border-blue-200 dark:border-blue-700"
                    >
                      {field}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Suggested Questions */}
            {suggestedQuestions?.length > 0 && (
              <div className="mb-3">
                <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-2">
                  <Target className="w-3 h-3" />
                  <span>Vorschläge:</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {suggestedQuestions?.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestedQuestion(question)}
                      className="px-3 py-1 text-xs bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full transition-colors cursor-pointer border border-blue-200 dark:border-blue-700"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex gap-2">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Beschreiben Sie Ihren gewünschten Stream..."
                className="flex-1"
                disabled={isLoading}
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                size="icon"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Drücken Sie Enter zum Senden. Beschreiben Sie einfach, welchen Job Sie erstellen möchten.
            </p>
          </div>
        </div>

        {/* Right: Stream Preview */}
        <div className="w-1/2 flex flex-col bg-gray-50 dark:bg-gray-900">
          {/* Preview Header */}
          <div className="bg-white dark:bg-gray-800 px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-600" />
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Stream-Konfiguration
                </h2>
              </div>

              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSaveStream}
                  disabled={!wizardData}
                >
                  <Save className="w-4 h-4 mr-2" />
                  Als Entwurf
                </Button>
                <Button
                  size="sm"
                  onClick={handleSubmitForReview}
                  disabled={!wizardData}
                >
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Zur Freigabe
                </Button>
              </div>
            </div>
          </div>

          {/* Preview Content */}
          <div className="flex-1 p-6 overflow-auto">
            {wizardData ? (
              <WizardDataRenderer
                stream={{
                  id: 'chat-preview',
                  stream_name: streamName || 'Chat Stream',
                  description: 'Via Chat erstellt',
                  xml_content: null,
                  wizard_data: wizardData,
                  job_type: wizardData.jobType || 'standard',
                  status: 'draft',
                  created_by: 'User',
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                  last_generated_at: null,
                  tags: [],
                  is_favorite: false,
                  version: 1,
                  template_id: null
                }}
              />
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    Noch keine Konfiguration
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    Beschreiben Sie im Chat, welchen Stream Sie erstellen möchten.
                    Die Konfiguration wird hier live angezeigt.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}