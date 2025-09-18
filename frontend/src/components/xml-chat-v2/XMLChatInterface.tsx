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
import { useXMLChatStore } from './store/xmlChatStore'
import { useXMLGeneration } from './hooks/useXMLGeneration'

// Components
import ChatMessage from './components/ChatMessage'
import XMLPreview from './components/XMLPreview'
import ChatInput from './components/ChatInput'
import SessionManager from './components/SessionManager'

// Types
import { XMLChatMessage, XMLGenerationStatus } from './types'

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
    generationStatus
  } = useXMLChatStore()

  // Hooks
  const { generateXMLFromChat, isLoading: isXMLGenerating } = useXMLGeneration()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  // Handle message submission
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isGenerating) return

    const userMessage: XMLChatMessage = {
      id: crypto.randomUUID(),
      sessionId: currentSession?.id || '',
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    }

    // Add user message
    addMessage(userMessage)
    setInputValue('')
    setIsGenerating(true)

    try {
      // Simulate AI response (replace with actual API call)
      await new Promise(resolve => setTimeout(resolve, 1000))

      const aiResponse: XMLChatMessage = {
        id: crypto.randomUUID(),
        sessionId: currentSession?.id || '',
        role: 'assistant',
        content: generateAIResponse(inputValue),
        timestamp: new Date().toISOString(),
        metadata: {
          canGenerateXML: shouldOfferXMLGeneration(inputValue)
        }
      }

      addMessage(aiResponse)

      // Auto-generate XML if this looks like a complete request
      if (shouldAutoGenerateXML(inputValue)) {
        handleGenerateXML()
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
    if (!currentSession || messages.length === 0) return

    try {
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
    <div className="flex h-screen bg-gray-50">
      {/* Chat Panel */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">XML Assistant</h1>
                <p className="text-sm text-gray-500">Describe what you need, and I'll generate the XML</p>
              </div>
            </div>
            <SessionManager />
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MessageSquare className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Welcome to XML Assistant
                </h3>
                <p className="text-gray-500 mb-6">
                  Describe what kind of XML you need, and I'll help you create it.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-md mx-auto">
                  <button
                    className="p-3 text-left bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                    onClick={() => setInputValue("Create a job definition XML for data processing")}
                  >
                    <div className="font-medium text-sm text-gray-900">Data Processing Job</div>
                    <div className="text-xs text-gray-500">Standard job definition</div>
                  </button>
                  <button
                    className="p-3 text-left bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                    onClick={() => setInputValue("Generate XML for SAP interface configuration")}
                  >
                    <div className="font-medium text-sm text-gray-900">SAP Interface</div>
                    <div className="text-xs text-gray-500">SAP integration setup</div>
                  </button>
                </div>
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
        <div className="bg-white border-t border-gray-200 p-6">
          <div className="max-w-3xl mx-auto">
            <ChatInput
              ref={inputRef}
              value={inputValue}
              onChange={setInputValue}
              onSend={handleSendMessage}
              onKeyDown={handleKeyDown}
              disabled={isGenerating}
              placeholder="Describe the XML you need..."
            />
            <div className="text-xs text-gray-500 mt-2 text-center">
              Press Ctrl+Enter to send • Ask me to create any kind of XML configuration
            </div>
          </div>
        </div>
      </div>

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