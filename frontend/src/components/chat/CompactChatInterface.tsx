/**
 * Compact Chat Interface
 * Simplified version of ModernChatInterface for floating widget
 * Optimized for small screen space while maintaining full functionality
 */

'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Sparkles, Loader } from 'lucide-react'
import { useChatStore, useChatSelectors } from '@/stores/chatStore'
import { useChatContext } from './ChatProvider'
import { formatTimeForDisplay } from '@/utils/timeUtils'
import { EnterpriseResponseFormatter } from './EnterpriseResponseFormatter'
import TypingIndicator from './TypingIndicator'
import { ContextualSuggestions } from './ContextualSuggestions'

interface CompactChatInterfaceProps {
  onClose?: () => void
  containerHeight?: string
}

export const CompactChatInterface: React.FC<CompactChatInterfaceProps> = ({
  onClose,
  containerHeight = 'calc(500px - 64px)'
}) => {
  const [input, setInput] = useState('')
  const [isClient, setIsClient] = useState(false)
  const [welcomeTimestamp] = useState(() => new Date().toISOString())
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Store state
  const {
    currentSessionId,
    error,
    setError,
  } = useChatStore()

  // Computed selectors
  const {
    currentMessages,
    canSendMessage,
    isSendingMessage,
  } = useChatSelectors()

  // Business logic
  const {
    createNewSession,
    sendMessage,
  } = useChatContext()

  // ================================
  // EFFECTS
  // ================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentMessages])

  useEffect(() => {
    setIsClient(true)
  }, [])

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [error, setError])

  // Auto-create session if none exists
  useEffect(() => {
    if (!currentSessionId) {
      createNewSession('Floating Chat')
    }
  }, [currentSessionId, createNewSession])

  // ================================
  // HANDLERS
  // ================================

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !canSendMessage) return

    const query = input.trim()
    setInput('')

    try {
      await sendMessage(query)
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion)
    // Auto-send the suggestion
    if (canSendMessage) {
      sendMessage(suggestion).catch(error => {
        console.error('Failed to send suggestion:', error)
        setInput(suggestion) // Restore input if sending fails
      })
    }
  }

  // Welcome message for empty sessions
  const welcomeMessage = {
    id: 'welcome-compact',
    type: 'assistant' as const,
    content: '👋 Hallo! Ich bin dein Streamworks Assistant. Wie kann ich dir helfen?',
    created_at: welcomeTimestamp,
    session_id: currentSessionId || '',
    sequence_number: 0,
    confidence_score: undefined,
    sources: undefined,
    processing_time: undefined,
    model_info: undefined,
    retrieval_context: undefined,
  }

  const displayMessages = currentMessages.length > 0 ? currentMessages : [welcomeMessage]
  const hasUserMessages = currentMessages.some(msg => msg.type === 'user')

  return (
    <div className="flex flex-col h-full" style={{ height: containerHeight }}>
      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-2 left-2 right-2 bg-red-500 text-white px-3 py-2 rounded-lg text-xs z-10"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {displayMessages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} gap-2`}
            >
              {/* Avatar */}
              {message.type === 'assistant' && (
                <div className="w-7 h-7 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
              )}

              {/* Message Content */}
              <div className={`max-w-[85%] ${message.type === 'user' ? 'order-first' : ''}`}>
                {/* Timestamp */}
                <div className={`text-xs text-gray-400 mb-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                  {formatTimeForDisplay(message.created_at, isClient)}
                </div>

                {/* Message Bubble */}
                <div className={`p-3 rounded-2xl text-sm ${
                  message.type === 'user'
                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                }`}>
                  {message.type === 'assistant' ? (
                    <EnterpriseResponseFormatter
                      content={message.content}
                      confidence_score={message.confidence_score}
                      sources={message.sources}
                      processing_time={message.processing_time}
                      model_info={message.model_info}
                      retrieval_context={message.retrieval_context}
                      onCopyResponse={() => navigator.clipboard.writeText(message.content)}
                      onSourceClick={() => {}} // Simplified for compact view
                      compact={true} // Add compact prop
                    />
                  ) : (
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  )}
                </div>
              </div>

              {/* User Avatar */}
              {message.type === 'user' && (
                <div className="w-7 h-7 bg-gradient-to-br from-primary-600 to-primary-700 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading Indicator */}
        {isSendingMessage && (
          <TypingIndicator className="mb-2" />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Contextual Suggestions */}
      {!hasUserMessages && (
        <ContextualSuggestions
          onSuggestionClick={handleSuggestionClick}
          showHeader={false}
          className="border-t-0"
        />
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-3">
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Nachricht eingeben..."
            disabled={!canSendMessage}
            className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 disabled:opacity-50"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage(e)
              }
            }}
          />
          <button
            type="submit"
            disabled={!canSendMessage || !input.trim()}
            className="px-3 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center flex-shrink-0"
          >
            {isSendingMessage ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default CompactChatInterface