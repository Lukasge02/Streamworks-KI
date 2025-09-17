/**
 * Chat XML Interface
 * 3-Panel Layout: Parameter Status | Chat Interface | XML Preview
 * Specialized for XML generation through conversational AI
 */

'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Send, Bot, User, Clock, Loader, Settings,
  Zap, Code, MessageCircle, PanelLeftOpen, PanelRightOpen,
  Download, Copy, Play, Pause, RotateCcw,
  CheckCircle, AlertTriangle, Clock3, XCircle
} from 'lucide-react'

// ================================
// TYPES
// ================================

interface XMLChatMessage {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: {
    extractedParams?: Record<string, any>
    validationErrors?: string[]
    suggestions?: string[]
  }
}

interface XMLChatSession {
  id: string
  jobType?: 'STANDARD' | 'SAP' | 'FILE_TRANSFER' | 'CUSTOM'
  status: 'CREATED' | 'COLLECTING_PARAMS' | 'GENERATING' | 'COMPLETED' | 'ERROR'
  extractedParams: Record<string, any>
  messages: XMLChatMessage[]
  createdAt: string
  updatedAt: string
}

interface ParameterStatus {
  name: string
  type: string
  required: boolean
  status: 'MISSING' | 'PARTIAL' | 'COMPLETE' | 'INVALID'
  value?: any
  description?: string
  chatPrompt?: string
}

// ================================
// MAIN COMPONENT
// ================================

export const ChatXMLInterface: React.FC = () => {
  // Panel visibility states
  const [rightPanelOpen, setRightPanelOpen] = useState(true)

  // Chat states
  const [input, setInput] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [currentSession, setCurrentSession] = useState<XMLChatSession | null>(null)
  const [parameterStatuses, setParameterStatuses] = useState<ParameterStatus[]>([])
  const [xmlPreview, setXmlPreview] = useState('')
  const [xmlValid, setXmlValid] = useState(false)

  // Provider state
  const [aiProvider, setAiProvider] = useState<'local' | 'cloud'>('local')
  const [isClient, setIsClient] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  // ================================
  // EFFECTS
  // ================================

  useEffect(() => {
    setIsClient(true)
    // Initialize demo session
    initializeDemoSession()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentSession?.messages])

  // ================================
  // HANDLERS
  // ================================

  const initializeDemoSession = () => {
    const demoSession: XMLChatSession = {
      id: crypto.randomUUID(),
      status: 'CREATED',
      extractedParams: {},
      messages: [{
        id: crypto.randomUUID(),
        type: 'assistant',
        content: 'Hallo! Ich helfe dir bei der XML-Generierung für StreamWorks. Welchen Job-Typ möchtest du erstellen? (STANDARD, SAP, FILE_TRANSFER, CUSTOM)',
        timestamp: new Date().toISOString()
      }],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }

    setCurrentSession(demoSession)
    setParameterStatuses(getDemoParameterStatuses())
  }

  const getDemoParameterStatuses = (): ParameterStatus[] => [
    {
      name: 'stream_name',
      type: 'string',
      required: true,
      status: 'MISSING',
      description: 'Name des Stream-Jobs',
      chatPrompt: 'Wie soll der Stream heißen?'
    },
    {
      name: 'job_type',
      type: 'enum',
      required: true,
      status: 'MISSING',
      description: 'Typ des Jobs (STANDARD, SAP, FILE_TRANSFER, CUSTOM)',
      chatPrompt: 'Welchen Job-Typ möchtest du erstellen?'
    },
    {
      name: 'schedule_rule',
      type: 'string',
      required: false,
      status: 'MISSING',
      description: 'Zeitplan für die Ausführung',
      chatPrompt: 'Wann soll der Job ausgeführt werden?'
    }
  ]

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !currentSession) return

    const userMessage: XMLChatMessage = {
      id: crypto.randomUUID(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    }

    // Add user message to session
    setCurrentSession(prev => prev ? {
      ...prev,
      messages: [...prev.messages, userMessage],
      updatedAt: new Date().toISOString()
    } : null)

    setInput('')
    setIsGenerating(true)

    // Simulate AI response after delay
    setTimeout(() => {
      const assistantMessage: XMLChatMessage = {
        id: crypto.randomUUID(),
        type: 'assistant',
        content: `Verstehe! Du möchtest "${input}". Lass mich das für dich verarbeiten und weitere Parameter sammeln.`,
        timestamp: new Date().toISOString(),
        metadata: {
          extractedParams: { stream_name: input.includes('stream') ? input : undefined },
          suggestions: ['Möchtest du einen STANDARD Job erstellen?']
        }
      }

      setCurrentSession(prev => prev ? {
        ...prev,
        messages: [...prev.messages, assistantMessage],
        updatedAt: new Date().toISOString()
      } : null)

      setIsGenerating(false)
    }, 1500)
  }

  const handleGenerateXML = () => {
    console.log('🚀 Generate XML clicked')
    setXmlPreview(`<?xml version="1.0" encoding="UTF-8"?>
<stream>
  <streamName>Demo Stream</streamName>
  <jobType>STANDARD</jobType>
  <scheduleRule>0 9 * * 1-5</scheduleRule>
</stream>`)
    setXmlValid(true)
  }

  const getStatusBadgeColor = (status: ParameterStatus['status']) => {
    switch (status) {
      case 'COMPLETE': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'PARTIAL': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'INVALID': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
    }
  }

  const getStatusIcon = (status: ParameterStatus['status']) => {
    switch (status) {
      case 'COMPLETE': return <CheckCircle className="w-4 h-4" />
      case 'PARTIAL': return <Clock3 className="w-4 h-4" />
      case 'INVALID': return <XCircle className="w-4 h-4" />
      default: return <AlertTriangle className="w-4 h-4" />
    }
  }

  // ================================
  // RENDER
  // ================================

  return (
    <div className="h-full flex bg-gray-50 dark:bg-gray-900">
      {/* Main Panel: Chat Interface */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Header */}
        <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>

              <div>
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                  XML Chat Generator
                  <span className="ml-2 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 px-2 py-1 rounded">
                    Interactive
                  </span>
                  <span className="ml-2 w-2 h-2 bg-green-500 rounded-full"></span>
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* AI Provider Switch */}
              <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                <button
                  onClick={() => setAiProvider('local')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    aiProvider === 'local'
                      ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-300'
                  }`}
                >
                  <Zap className="w-4 h-4 inline mr-1" />
                  Lokal
                </button>
                <button
                  onClick={() => setAiProvider('cloud')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    aiProvider === 'cloud'
                      ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-300'
                  }`}
                >
                  ☁️ Cloud
                </button>
              </div>

              {!rightPanelOpen && (
                <button
                  onClick={() => setRightPanelOpen(true)}
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  title="Parameter Panel öffnen"
                >
                  <PanelRightOpen className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Messages Area - Scrollable Only */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <AnimatePresence>
            {currentSession?.messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-3xl ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                  <div className={`flex items-start space-x-3 ${
                    message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}>
                    {/* Avatar */}
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      message.type === 'user' ? 'bg-blue-600' : 'bg-blue-600'
                    }`}>
                      {message.type === 'user' ? (
                        <User className="w-5 h-5 text-white" />
                      ) : (
                        <Bot className="w-5 h-5 text-white" />
                      )}
                    </div>

                    {/* Message Content */}
                    <div className={`flex-1 ${message.type === 'user' ? 'text-right' : ''} group`}>
                      <div className={`inline-block p-4 rounded-xl shadow-sm ${
                        message.type === 'user'
                          ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                          : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
                      }`}>
                        <div className="text-sm leading-relaxed">
                          <p>{message.content}</p>
                        </div>

                        {/* Message Metadata */}
                        {message.metadata && (
                          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                            {message.metadata.extractedParams && (
                              <div className="text-xs">
                                <span className="font-medium">Extrahierte Parameter:</span>
                                <pre className="mt-1 text-green-600 dark:text-green-400">
                                  {JSON.stringify(message.metadata.extractedParams, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Timestamp */}
                      <div className="mt-2 text-xs text-gray-500 flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading Indicator */}
          {isGenerating && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Loader className="w-5 h-5 text-white animate-spin" />
                </div>
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area - Fixed at Bottom */}
        <div className="flex-shrink-0 p-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          <form onSubmit={handleSendMessage} className="flex space-x-4">
            <div className="flex-1">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Beschreibe deinen XML-Stream oder beantworte die Fragen..."
                disabled={isGenerating}
                rows={1}
                className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 disabled:opacity-50"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage(e)
                  }
                }}
              />
            </div>
            <button
              type="submit"
              disabled={isGenerating || !input.trim()}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center space-x-2"
            >
              <Send className="w-4 h-4" />
              <span>Senden</span>
            </button>
          </form>

          {/* Quick Actions */}
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              onClick={() => setInput('Ich möchte einen STANDARD Job erstellen für tägliche Datenverarbeitung')}
              className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              📊 Standard Job
            </button>
            <button
              onClick={() => setInput('Ich brauche einen SAP Job für PA1_100 System')}
              className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              🏢 SAP Job
            </button>
            <button
              onClick={() => setInput('File Transfer von SFTP zu lokaler Datenbank')}
              className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              📂 File Transfer
            </button>
            <button
              onClick={handleGenerateXML}
              className="px-3 py-1 text-sm bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors"
            >
              🚀 XML generieren
            </button>
          </div>
        </div>
      </div>

      {/* Right Panel: Parameter Status */}
      <AnimatePresence>
        {rightPanelOpen && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: 320 }}
            exit={{ width: 0 }}
            className="bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col h-full overflow-hidden"
          >
            {/* Panel Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-semibold text-gray-900 dark:text-white">
                  Parameter Status
                </h2>
                <button
                  onClick={() => setRightPanelOpen(false)}
                  className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  title="Panel schließen"
                >
                  <PanelRightOpen className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                </button>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: '33%' }}
                />
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                1 von 3 Pflichtfeldern (33%)
              </div>
            </div>

            {/* Parameter List - Scrollable */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
              {parameterStatuses.map((param) => (
                <div
                  key={param.name}
                  className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm text-gray-900 dark:text-white">
                      {param.name}
                      {param.required && <span className="text-red-500 ml-1">*</span>}
                    </span>
                    <div className={`px-2 py-1 rounded-full text-xs flex items-center gap-1 ${getStatusBadgeColor(param.status)}`}>
                      {getStatusIcon(param.status)}
                      {param.status}
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                    {param.description}
                  </p>
                  {param.value && (
                    <div className="text-xs text-green-600 dark:text-green-400 font-mono bg-green-50 dark:bg-green-900/20 p-2 rounded">
                      {JSON.stringify(param.value)}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Generation Actions - Fixed at Bottom */}
            <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
              <button
                onClick={handleGenerateXML}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Play className="w-4 h-4" />
                XML Generieren
              </button>
              {xmlValid && xmlPreview && (
                <>
                  <button
                    onClick={() => navigator.clipboard.writeText(xmlPreview)}
                    className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                    XML Kopieren
                  </button>
                  <button
                    onClick={() => {
                      const blob = new Blob([xmlPreview], { type: 'application/xml' })
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'stream.xml'
                      a.click()
                    }}
                    className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    XML Download
                  </button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default ChatXMLInterface