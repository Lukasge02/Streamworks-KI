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
  AlertCircle,
  History,
  Plus,
  Search,
  BarChart3,
  Trash2,
  X,
  Clock
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
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showStats, setShowStats] = useState(false)
  const [isClient, setIsClient] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Store
  const {
    currentSession,
    sessions,
    messages,
    addMessage,
    updateMessage,
    createNewSession,
    switchToSession,
    deleteSession,
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

  // Client-side hydration protection
  useEffect(() => {
    setIsClient(true)
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

        // Auto-detect stream type from JobCategory if we have parameters but no type selected
        if (Object.keys(liveExtractedParameters).length > 0 && !selectedStreamType) {
          // Check if parameters contain JobCategory information
          if (liveExtractedParameters?.JobCategory) {
            const jobCategory = liveExtractedParameters.JobCategory
            let detectedType: StreamType | null = null

            if (jobCategory === 'SAP') {
              detectedType = 'SAP'
            } else if (jobCategory === 'DataTransfer' || jobCategory === 'FILE_TRANSFER') {
              detectedType = 'FILE_TRANSFER'
            } else if (jobCategory === 'STANDARD') {
              detectedType = 'STANDARD'
            }

            if (detectedType) {
              console.log(`🎯 Auto-selecting ${detectedType} stream type based on JobCategory: ${jobCategory}`)
              setSelectedStreamType(detectedType)
            }
          }
        }
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
          // Handle hierarchical session type mapping
          let detectedType: StreamType | null = null

          // Check if we have a JobCategory from extracted parameters
          if (response.extracted_parameters?.JobCategory) {
            const jobCategory = response.extracted_parameters.JobCategory
            if (jobCategory === 'SAP') {
              detectedType = 'SAP'
            } else if (jobCategory === 'DataTransfer' || jobCategory === 'FILE_TRANSFER') {
              detectedType = 'FILE_TRANSFER'
            } else if (jobCategory === 'STANDARD') {
              detectedType = 'STANDARD'
            }
          }

          // Fallback to old logic if no JobCategory detected
          if (!detectedType) {
            if (response.metadata.job_type === 'STREAM_CONFIGURATION') {
              // Don't default to STANDARD, wait for JobCategory
              detectedType = null
            } else if (['SAP', 'FILE_TRANSFER', 'STANDARD'].includes(response.metadata.job_type)) {
              detectedType = response.metadata.job_type as StreamType
            }
          }

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

  // Session management handlers
  const handleNewChat = () => {
    createNewSession()
    setSearchQuery('')
  }

  const handleSessionSelect = (sessionId: string) => {
    switchToSession(sessionId)
  }

  const handleDeleteSession = (sessionId: string) => {
    if (confirm('⚠️ Möchtest du diesen Chat wirklich löschen?')) {
      deleteSession(sessionId)
    }
  }

  const handleClearAllChats = () => {
    if (!sessions.length) return

    const chatCount = sessions.length
    if (confirm(`⚠️ Möchtest du wirklich alle ${chatCount} Chat-Verläufe löschen? Diese Aktion kann nicht rückgängig gemacht werden.`)) {
      sessions.forEach(session => deleteSession(session.id))
      toast.success(`✅ Alle ${chatCount} Chat-Verläufe wurden erfolgreich gelöscht`)
    }
  }

  // Filter sessions based on search
  const filteredSessions = searchQuery
    ? sessions.filter(session =>
        session.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : sessions

  // Format time utility
  const formatTimeForDisplay = (timestamp: string, isClient: boolean) => {
    if (!isClient) return ''
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Gerade eben'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="flex h-full w-full bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 overflow-hidden">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 350, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="bg-white/90 backdrop-blur-sm border-r border-slate-200/60 flex flex-col h-full overflow-hidden shadow-lg"
          >
            {/* Sidebar Header */}
            <div className="px-4 py-3 border-b border-slate-200/60">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-slate-900">
                  Chat-Verlauf
                </h2>
                <button
                  onClick={() => setShowStats(!showStats)}
                  className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
                  title="Statistiken"
                >
                  <BarChart3 className="w-4 h-4 text-slate-600" />
                </button>
              </div>

              {/* Search Bar */}
              <div className="relative mb-3">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Chats durchsuchen..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-sm border border-slate-200 rounded-lg bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 rounded hover:bg-slate-200"
                  >
                    <X className="w-3 h-3 text-slate-400" />
                  </button>
                )}
              </div>

              {/* New Chat Button */}
              <button
                onClick={handleNewChat}
                disabled={isGenerating || isSmartWorking}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 text-sm font-medium bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors shadow-sm"
              >
                <Plus className="w-4 h-4" />
                <span>Neuer Chat</span>
              </button>

              {/* Stats Panel */}
              <AnimatePresence>
                {showStats && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-3 p-3 bg-slate-50 rounded-lg text-xs"
                  >
                    <div className="grid grid-cols-2 gap-2 text-slate-600">
                      <div>Sessions: {sessions.length}</div>
                      <div>Nachrichten: {messages.length}</div>
                      <div>AI Mode: ⚡ Smart</div>
                      <div>Status: {isGenerating || isSmartWorking ? 'Laden...' : 'Bereit'}</div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Sessions List */}
            <div className="flex-1 overflow-y-auto p-2">
              {sessions.length === 0 ? (
                <div className="text-center p-8 text-slate-500">
                  <MessageSquare className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                  <div className="text-sm">Noch keine Chat-Verläufe</div>
                  <div className="text-xs mt-1">Erstelle einen neuen Chat!</div>
                </div>
              ) : (
                <div className="space-y-2">
                  {searchQuery && (
                    <div className="text-xs text-slate-500 px-2">
                      {filteredSessions.length} von {sessions.length} Sessions
                    </div>
                  )}

                  {filteredSessions.map((session) => (
                    <motion.div
                      key={session.id}
                      layout
                      role="button"
                      tabIndex={0}
                      onClick={() => handleSessionSelect(session.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault()
                          handleSessionSelect(session.id)
                        }
                      }}
                      className={`w-full text-left p-3 rounded-lg transition-colors group cursor-pointer ${
                        session.id === currentSession?.id
                          ? 'bg-blue-50 border border-blue-200 shadow-sm'
                          : 'hover:bg-slate-50 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="truncate font-medium text-slate-900 text-sm flex-1">
                          {session.title}
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteSession(session.id)
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-100 transition-all"
                          aria-label={`Chat "${session.title}" löschen`}
                        >
                          <Trash2 className="w-3 h-3 text-red-500" />
                        </button>
                      </div>
                      <div className="flex items-center justify-between text-xs text-slate-500">
                        <span>{formatTimeForDisplay(session.updatedAt, isClient)}</span>
                        <span>{session.messageCount} Nachrichten</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer with Delete All Chats */}
            <div className="p-4 border-t border-slate-200/60 bg-slate-50/50">
              <button
                onClick={handleClearAllChats}
                disabled={!sessions.length}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-xs text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Alle Chats löschen"
              >
                <Trash2 className="w-3 h-3" />
                <span>Alle Chats löschen</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Panel */}
      <div className="flex-1 relative min-w-0 h-full">
        {/* Header - Fixed at top */}
        <div className="absolute top-0 left-0 right-0 z-10 bg-gradient-to-r from-white/95 via-blue-50/90 to-indigo-50/95 backdrop-blur-lg border-b border-gradient-to-r from-slate-200/40 via-blue-200/30 to-indigo-200/40 px-8 py-5 shadow-xl shadow-blue-500/5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-3 rounded-xl bg-white/80 hover:bg-white shadow-lg hover:shadow-xl border border-slate-200/50 transition-all duration-200 group"
                title="Chat-Verlauf ein/ausblenden"
              >
                <History className="w-5 h-5 text-slate-600 group-hover:text-blue-600 transition-colors" />
              </motion.button>

              <div className="flex items-center gap-4">
                <motion.div
                  whileHover={{ scale: 1.05, rotate: 5 }}
                  className="w-12 h-12 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl shadow-blue-500/20"
                >
                  <Sparkles className="w-6 h-6 text-white" />
                </motion.div>

                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-800 via-blue-800 to-indigo-800 bg-clip-text text-transparent leading-tight">
                    StreamWorks Assistant
                  </h1>
                  <p className="text-sm text-slate-600 mt-0.5 leading-tight">
                    Intelligente StreamWorks-Streams durch natürliche Sprache erstellen
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-white text-sm font-semibold rounded-full shadow-lg shadow-emerald-500/20"
              >
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                <span>Smart Mode</span>
              </motion.div>

              <div className="flex items-center gap-2 px-3 py-1.5 bg-white/60 border border-slate-200/50 rounded-lg text-xs text-slate-600">
                <Clock className="w-4 h-4" />
                <span>{isClient ? new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) : '--:--'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Messages - Fixed positioned content area */}
        <div className="absolute top-20 bottom-32 left-0 right-0 overflow-y-auto px-8 py-6 bg-gradient-to-b from-white/50 to-slate-50/80">
          <div className="max-w-6xl mx-auto space-y-6">
            {messages.length === 0 ? (
              <div className="space-y-4">
                {/* Welcome Header */}
                <div className="text-center py-8">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="space-y-4"
                  >
                    <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-blue-500/20 mb-6">
                      <FileCode className="w-10 h-10 text-white" />
                    </div>
                    <h3 className="text-3xl font-bold bg-gradient-to-r from-slate-800 via-blue-800 to-indigo-800 bg-clip-text text-transparent mb-3">
                      Stream erstellen
                    </h3>
                    <p className="text-slate-600 max-w-2xl mx-auto text-lg leading-relaxed">
                      Beschreiben Sie Ihren gewünschten Stream in natürlicher Sprache und lassen Sie die KI eine maßgeschneiderte Konfiguration erstellen
                    </p>
                  </motion.div>
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
                  {messages.map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 30, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -30, scale: 0.95 }}
                      transition={{
                        duration: 0.4,
                        ease: "easeOut",
                        delay: index * 0.1
                      }}
                      whileHover={{ scale: 1.01 }}
                      className="will-change-transform"
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
                    initial={{ opacity: 0, y: 20, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.9 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className="flex items-center gap-4 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200/50 shadow-lg shadow-blue-500/5"
                  >
                    <motion.div
                      animate={{
                        scale: [1, 1.1, 1],
                        rotate: [0, 180, 360]
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                      className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg"
                    >
                      <Bot className="w-6 h-6 text-white" />
                    </motion.div>
                    <div className="flex items-center gap-3">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      >
                        <Loader2 className="w-5 h-5 text-blue-600" />
                      </motion.div>
                      <span className="text-lg font-medium bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent">
                        KI analysiert Ihre Anfrage...
                      </span>
                    </div>
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </>
            )}

            {/* Bottom spacing to prevent content from hiding behind input */}
            <div className="h-8"></div>
          </div>
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-white/95 via-blue-50/90 to-indigo-50/95 backdrop-blur-lg border-t border-gradient-to-r from-slate-200/40 via-blue-200/30 to-indigo-200/40 p-6 shadow-2xl shadow-blue-500/10">
          <div className="max-w-5xl mx-auto">
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
            <div className="text-center mt-3">
              <div className="flex items-center justify-center gap-6 text-sm text-slate-600">
                <div className="flex items-center gap-2">
                  <kbd className="px-2 py-1 bg-slate-200 text-slate-700 text-xs rounded border border-slate-300 font-mono">Strg</kbd>
                  <span className="text-slate-400">+</span>
                  <kbd className="px-2 py-1 bg-slate-200 text-slate-700 text-xs rounded border border-slate-300 font-mono">Enter</kbd>
                  <span className="text-slate-500">zum Senden</span>
                </div>
                {selectedStreamType && (
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="font-medium">{selectedStreamType}</span>
                    {Object.keys(extractedParameters).length > 0 && (
                      <>
                        <div className="w-1 h-1 bg-slate-400 rounded-full"></div>
                        <span className="text-slate-500">{Object.keys(extractedParameters).length} Parameter</span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Parameter Overview Panel - Show when parameters exist (unified stream flow) */}
      {Object.keys(extractedParameters).length > 0 && !generatedXML && (
        <ParameterOverview
          streamType={selectedStreamType || "STANDARD"}
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
