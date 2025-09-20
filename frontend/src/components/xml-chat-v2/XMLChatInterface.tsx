/**
 * Modern XML Chat Interface - Clean Redesign
 * ChatGPT/Claude-like experience for XML generation
 */

'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Send,
  Bot,
  User,
  Download,
  Copy,
  Sparkles,
  Code2,
  MessageSquare,
  FileCode,
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { toast } from 'sonner'

// Store and hooks
import { useXMLChatStore, useXMLChatSelectors, type StreamType } from './store/xmlChatStore'
import { useXMLGeneration } from './hooks/useXMLGeneration'
import { useSmartChat } from './hooks/useSmartChat'

// Components
import ChatMessage from './components/ChatMessage'
import XMLPreview from './components/XMLPreview'
import ChatInput from './components/ChatInput'
import SessionManager from './components/SessionManager'
import StreamTypeSelector from './components/StreamTypeSelector'
import ParameterProgress from './components/ParameterProgress'
import SmartSuggestions from './components/SmartSuggestions'
import ParameterOverview from './components/ParameterOverview'

// Types
import { XMLChatMessage, XMLGenerationStatus } from './store/xmlChatStore'

// ================================
// MAIN COMPONENT
// ================================

export default function XMLChatInterface() {
  const [inputValue, setInputValue] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Store
  const {
    currentSession,
    messages,
    addMessage,
    updateMessage,
    createNewSession,
    generatedXML,
    setGeneratedXML,
    generationStatus,
    selectedStreamType,
    setSelectedStreamType,
    extractedParameters,
    setExtractedParameters,
    completionPercentage,
    setCompletionPercentage,
    aiSuggestions,
    setAISuggestions,
    nextParameter,
    setNextParameter,
    setSmartSession
  } = useXMLChatStore()

  // Store Selectors
  const {
    isSmartMode,
    isSmartWorking,
    shouldShowStreamTypeSelection,
    hasSelectedStreamType,
    shouldShowParameterProgress,
    shouldShowSuggestions
  } = useXMLChatSelectors()

  // Hooks
  const { generateXMLFromChat, isLoading: isXMLGenerating } = useXMLGeneration()
  const {
    createSession: createSmartSession,
    sendSmartMessage,
    generateXML: generateSmartXML,
    isCreatingSession,
    isSendingMessage,
    isGeneratingXML: isGeneratingSmartXML,
    extractedParameters: liveExtractedParameters,
    currentSession: smartSession,
    lastResponse
  } = useSmartChat()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  // Keep store smart session in sync with hook state
  useEffect(() => {
    if (isSmartMode) {
      setSmartSession(smartSession ?? null)
    } else {
      setSmartSession(null)
    }
  }, [isSmartMode, smartSession, setSmartSession])

  // Create smart session when stream type is selected
  useEffect(() => {
    if (isSmartMode && selectedStreamType && !smartSession) {
      createSmartSession({ job_type: selectedStreamType })
    }
  }, [selectedStreamType, isSmartMode, smartSession, createSmartSession])

  // Sync extracted parameters from smart chat hook into store
  useEffect(() => {
    if (isSmartMode && liveExtractedParameters) {
      // Only update if parameters have actually changed
      const paramsChanged = JSON.stringify(extractedParameters) !== JSON.stringify(liveExtractedParameters)
      if (paramsChanged) {
        console.log('🔄 Updating extracted parameters:', liveExtractedParameters)
        setExtractedParameters(liveExtractedParameters)
      }
    }
  }, [isSmartMode, liveExtractedParameters, extractedParameters, setExtractedParameters])

  // Also sync parameters from lastResponse immediately
  useEffect(() => {
    if (isSmartMode && smartSession && lastResponse?.extracted_parameters) {
      const responseParams = lastResponse.extracted_parameters
      console.log('📥 Parameters from lastResponse:', responseParams)

      // Always use the latest parameters from the API response
      console.log('🔄 Setting parameters from lastResponse:', responseParams)
      setExtractedParameters(responseParams)
    }
  }, [isSmartMode, smartSession, lastResponse?.extracted_parameters, setExtractedParameters])

  // Sync completion percentage from smart session status
  useEffect(() => {
    if (isSmartMode && smartSession) {
      setCompletionPercentage(smartSession.completion_percentage)
    }
  }, [isSmartMode, smartSession, setCompletionPercentage])

  // Handle message submission
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isGenerating || isSmartWorking) return

    const messageContent = inputValue.trim()
    setInputValue('')
    setIsGenerating(true)

    try {
      if (isSmartMode) {
        // Ensure smart session exists
        let activeSession = smartSession
        if (!activeSession) {
          const createdSession = await createSmartSession({
            job_type: selectedStreamType || undefined
          })
          activeSession = createdSession
          setSmartSession(createdSession)

          if (createdSession.message) {
            const welcomeMessage: XMLChatMessage = {
              id: crypto.randomUUID(),
              sessionId: createdSession.session_id,
              role: 'assistant',
              content: createdSession.message,
              timestamp: createdSession.created_at || new Date().toISOString(),
              metadata: {
                type: 'info'
              }
            }
            addMessage(welcomeMessage)
          }
        }

        if (!activeSession) {
          throw new Error('Konnte keine Smart-Session erstellen')
        }

        const userMessage: XMLChatMessage = {
          id: crypto.randomUUID(),
          sessionId: activeSession.session_id,
          role: 'user',
          content: messageContent,
          timestamp: new Date().toISOString(),
          metadata: selectedStreamType ? { streamType: selectedStreamType } : undefined
        }

        addMessage(userMessage)

        const response = await sendSmartMessage(messageContent, activeSession.session_id)

        if (response.metadata?.job_type) {
          const detectedType = response.metadata.job_type as StreamType
          if (detectedType && detectedType !== selectedStreamType) {
            setSelectedStreamType(detectedType)
          }
        }

        const assistantMessage: XMLChatMessage = {
          id: response.session_id ? `${response.session_id}-${crypto.randomUUID()}` : crypto.randomUUID(),
          sessionId: response.session_id || activeSession.session_id,
          role: 'assistant',
          content: response.response_message,
          timestamp: response.timestamp || new Date().toISOString(),
          metadata: {
            type: 'info',
            parameters: response.extracted_parameters,
            nextParameter: response.next_parameter,
            completion: response.completion_percentage,
            parameterConfidences: response.parameter_confidences,
            job_type: response.metadata?.job_type
          }
        }

        addMessage(assistantMessage)

        // Update extracted parameters immediately
        if (response.extracted_parameters) {
          console.log('🆕 New parameters from response:', response.extracted_parameters)

          // Always use the latest parameters from response
          setExtractedParameters(response.extracted_parameters)

          console.log('🔄 Updated total parameters:', response.extracted_parameters)
        }
        setAISuggestions(response.suggested_questions || [])
        setNextParameter(response.next_parameter || null)
        setCompletionPercentage(response.completion_percentage || 0)
      } else {
        // Legacy mode - generic XML generation
        const userMessage: XMLChatMessage = {
          id: crypto.randomUUID(),
          sessionId: currentSession?.id || '',
          role: 'user',
          content: messageContent,
          timestamp: new Date().toISOString()
        }

        const aiResponse: XMLChatMessage = {
          id: crypto.randomUUID(),
          sessionId: currentSession?.id || '',
          role: 'assistant',
          content: generateAIResponse(messageContent),
          timestamp: new Date().toISOString(),
          metadata: {
            canGenerateXML: shouldOfferXMLGeneration(messageContent)
          }
        }

        addMessage(userMessage)
        addMessage(aiResponse)

        // Auto-generate XML if this looks like a complete request
        if (shouldAutoGenerateXML(messageContent)) {
          handleGenerateXML()
        }
      }

    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message')
    } finally {
      setIsGenerating(false)
    }
  }

  // Handle XML generation
  const handleGenerateXML = async () => {
    if (messages.length === 0) return

    try {
      if (isSmartMode && selectedStreamType) {
        // Use smart XML generation for StreamWorks
        const xmlContent = await generateSmartXML()

        setGeneratedXML(xmlContent)
        toast.success('StreamWorks XML erfolgreich generiert!')

        const systemMessage: XMLChatMessage = {
          id: crypto.randomUUID(),
          sessionId: smartSession?.session_id || currentSession?.id || '',
          role: 'system',
          content: `Ihr ${selectedStreamType} StreamWorks-Stream wurde erfolgreich generiert! Sie können das XML rechts in der Vorschau betrachten und herunterladen.`,
          timestamp: new Date().toISOString(),
          metadata: {
            type: 'xml_generated',
            ...(selectedStreamType ? { streamType: selectedStreamType } : {})
          }
        }
        addMessage(systemMessage)
      } else {
        // Legacy XML generation
        if (!currentSession) return

        const conversationContext = messages
          .filter(msg => msg.role !== 'system')
          .map(msg => `${msg.role}: ${msg.content}`)
          .join('\n')

        const result = await generateXMLFromChat(conversationContext)

        if (result.success && result.xml) {
          setGeneratedXML(result.xml)
          toast.success('XML generated successfully!')

          // Add system message about successful generation
          const systemMessage: XMLChatMessage = {
            id: crypto.randomUUID(),
            sessionId: currentSession.id,
            role: 'system',
            content: 'XML has been generated based on your requirements. You can preview and download it using the panel on the right.',
            timestamp: new Date().toISOString(),
            metadata: {
              type: 'xml_generated'
            }
          }
          addMessage(systemMessage)
        }
      }
    } catch (error) {
      console.error('Error generating XML:', error)
      toast.error('Failed to generate XML')
    }
  }

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex h-full bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 overflow-hidden">
      {/* Chat Panel */}
      <div className="flex-1 flex flex-col min-w-0 h-full">
        {/* Header */}
        <div className="flex-shrink-0 bg-white/80 backdrop-blur-sm border-b border-slate-200/60 px-6 py-5 shadow-sm">
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                  StreamWorks Assistant
                </h1>
                <p className="text-sm text-slate-600 font-medium">
                  Intelligente StreamWorks-Streams durch natürliche Sprache erstellen
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="px-3 py-1.5 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-full">
                Smart Mode
              </div>
              <SessionManager />
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4 min-h-0">
          <div className="max-w-5xl mx-auto space-y-4">
            {messages.length === 0 ? (
              <div className="space-y-4">
                {/* Welcome Header */}
                <div className="text-center py-4">
                  <h3 className="text-xl font-semibold text-slate-800 mb-2">
                    Stream erstellen
                  </h3>
                  <p className="text-slate-600 max-w-xl mx-auto text-sm">
                    Beschreiben Sie Ihren gewünschten Stream in natürlicher Sprache
                  </p>
                </div>

                {/* Stream Type Selector */}
                <StreamTypeSelector
                  selectedType={selectedStreamType}
                  onSelect={setSelectedStreamType}
                  isVisible={shouldShowStreamTypeSelection}
                />

                {/* Smart Suggestions */}
                {shouldShowSuggestions && (
                  <SmartSuggestions
                    suggestions={aiSuggestions}
                    streamType={selectedStreamType}
                    nextParameter={nextParameter ?? undefined}
                    completionPercentage={completionPercentage}
                    onSuggestionClick={(suggestion) => setInputValue(suggestion)}
                  />
                )}
              </div>
            ) : (
              <>
                <AnimatePresence initial={false}>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ChatMessage
                        message={message}
                        onGenerateXML={handleGenerateXML}
                        isGeneratingXML={isXMLGenerating}
                      />
                    </motion.div>
                  ))}
                </AnimatePresence>

                {/* Parameter Progress */}
                {shouldShowParameterProgress && (
                  <ParameterProgress
                    streamType={selectedStreamType}
                    extractedParameters={extractedParameters}
                    completionPercentage={completionPercentage}
                    nextParameter={nextParameter ?? undefined}
                  />
                )}

                {/* Smart Suggestions in Chat */}
                {shouldShowSuggestions && messages.length > 0 && (
                  <SmartSuggestions
                    suggestions={aiSuggestions}
                    streamType={selectedStreamType}
                    nextParameter={nextParameter ?? undefined}
                    completionPercentage={completionPercentage}
                    onSuggestionClick={(suggestion) => setInputValue(suggestion)}
                  />
                )}

                {/* Loading indicator */}
                {isGenerating && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-3 text-gray-500"
                  >
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Thinking...</span>
                    </div>
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="flex-shrink-0 bg-white/90 backdrop-blur-sm border-t border-slate-200/60 p-4 shadow-lg">
          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <ChatInput
                ref={inputRef}
                value={inputValue}
                onChange={setInputValue}
                onSend={handleSendMessage}
                onKeyDown={handleKeyDown}
                disabled={isGenerating || isSmartWorking}
                placeholder={isSmartMode
                  ? (selectedStreamType
                      ? `Beschreiben Sie Ihren ${selectedStreamType} Stream (z.B. "SAP Kalender Export von ZTV nach PA1")...`
                      : "Wählen Sie zuerst einen Stream-Typ oben aus..."
                    )
                  : "Beschreiben Sie die gewünschte XML-Konfiguration..."
                }
              />
              {(isGenerating || isSmartWorking) && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                </div>
              )}
            </div>
            <div className="text-center mt-1">
              <div className="text-xs text-slate-500">
                Strg+Enter zum Senden
                {selectedStreamType && (
                  <span className="ml-2">
                    • {selectedStreamType}
                    {Object.keys(extractedParameters).length > 0 && (
                      <span> • {Object.keys(extractedParameters).length} Parameter</span>
                    )}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Parameter Overview Panel */}
      {selectedStreamType && !generatedXML && (
        <ParameterOverview
          streamType={selectedStreamType}
          extractedParameters={extractedParameters}
          completionPercentage={completionPercentage}
          nextParameter={nextParameter ?? undefined}
        />
      )}

      {/* XML Preview Panel */}
      {generatedXML && (
        <XMLPreview
          xml={generatedXML}
          status={generationStatus}
          onClose={() => setGeneratedXML(null)}
        />
      )}
    </div>
  )
}

// ================================
// HELPER FUNCTIONS
// ================================

function generateAIResponse(userInput: string): string {
  const input = userInput.toLowerCase()

  if (input.includes('job') || input.includes('processing')) {
    return "I'll help you create a job definition XML. To generate the most accurate configuration, I need to understand:\n\n- What type of data processing job is this?\n- What are the input and output requirements?\n- Are there any specific parameters or scheduling needs?\n\nCould you provide more details about your job requirements?"
  }

  if (input.includes('sap')) {
    return "I can help you create SAP interface XML configurations. For the best results, please tell me:\n\n- Which SAP modules are involved?\n- What type of data exchange is needed?\n- Are there specific field mappings or transformations required?\n\nThe more details you provide, the more accurate the XML will be."
  }

  if (input.includes('file') || input.includes('transfer')) {
    return "I'll create a file transfer XML configuration for you. To ensure accuracy:\n\n- What file types need to be transferred?\n- What are the source and destination locations?\n- Any encryption or validation requirements?\n\nOnce I have these details, I can generate a complete XML configuration."
  }

  return "I understand you need help with XML generation. Could you provide more specific details about:\n\n- The type of XML configuration you need\n- The business purpose or use case\n- Any specific requirements or constraints\n\nThis will help me create exactly what you're looking for."
}

function shouldOfferXMLGeneration(input: string): boolean {
  const triggers = ['create', 'generate', 'build', 'make', 'need']
  const xmlTerms = ['xml', 'config', 'job', 'interface', 'definition']

  return triggers.some(trigger => input.toLowerCase().includes(trigger)) &&
         xmlTerms.some(term => input.toLowerCase().includes(term))
}

function shouldAutoGenerateXML(input: string): boolean {
  // Auto-generate when user provides comprehensive requirements
  return input.length > 100 &&
         (input.includes('job') || input.includes('interface')) &&
         (input.includes('process') || input.includes('transfer'))
}
