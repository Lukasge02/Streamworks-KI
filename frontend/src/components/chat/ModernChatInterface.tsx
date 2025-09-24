/**
 * Modern Chat Interface
 * Clean, maintainable chat UI using new architecture
 * Replaces the complex 526-line ChatInterface.tsx
 */

'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Send, Bot, User, Clock, Loader, History, Plus, Search,
  BarChart3, Trash2, X, Zap, Cloud, MessageCircle, Sparkles
} from 'lucide-react'
import { EnhancedButton } from '@/components/ui/EnhancedButton'
import { EnhancedInput } from '@/components/ui/EnhancedInput'
import TypingIndicator from './TypingIndicator'

import { useChatStore, useChatSelectors } from '../../stores/chatStore'
import { useChatContext } from './ChatProvider'
import { formatTimeForDisplay } from '../../utils/timeUtils'
import { EnterpriseResponseFormatter } from './EnterpriseResponseFormatter'
import { SourcePreviewModal } from './SourcePreviewModal'
import { MessageActions } from './MessageActions'

// ================================
// MAIN COMPONENT
// ================================

export const ModernChatInterface: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [input, setInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [showStats, setShowStats] = useState(false)
  const [selectedSource, setSelectedSource] = useState<any>(null)
  const [sourcePreviewOpen, setSourcePreviewOpen] = useState(false)
  const [isClient, setIsClient] = useState(false)
  const [welcomeTimestamp] = useState(() => new Date().toISOString())
  const [isDeletingAllChats, setIsDeletingAllChats] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Store state
  const {
    sessions,
    currentSessionId,
    aiProvider,
    error,
    setAiProvider,
    setError,
  } = useChatStore()

  // Computed selectors
  const {
    currentSession,
    currentMessages,
    hasActiveSessions,
    isAnyLoading,
    canSendMessage,
    shouldShowEmptyState,
    sessionCount,
    totalMessages,
    isSendingMessage,
  } = useChatSelectors()

  // Business logic
  const {
    createNewSession,
    sendMessage,
    switchSession,
    deleteSessionById,
  } = useChatContext()

  // ================================
  // EFFECTS
  // ================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentMessages])

  // Client-side hydration protection
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Clear errors after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [error, setError])

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

  const handleNewChat = async () => {
    try {
      await createNewSession()
      setSearchQuery('')
    } catch (error) {
      console.error('Failed to create new chat:', error)
    }
  }

  const handleSessionSelect = async (sessionId: string) => {
    try {
      await switchSession(sessionId)
    } catch (error) {
      console.error('Failed to switch session:', error)
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    if (confirm('⚠️ Möchtest du diesen Chat wirklich löschen?')) {
      try {
        await deleteSessionById(sessionId)
      } catch (error) {
        console.error('Failed to delete session:', error)
      }
    }
  }

  const handleClearAllChats = async () => {
    if (!sessions.length) return

    const chatCount = sessions.length
    if (confirm(`⚠️ Möchtest du wirklich alle ${chatCount} Chat-Verläufe löschen? Diese Aktion kann nicht rückgängig gemacht werden.`)) {
      setIsDeletingAllChats(true)

      try {
        // Create array of all delete promises for parallel execution
        const deletePromises = sessions.map(session =>
          deleteSessionById(session.id)
        )

        // Execute all deletions in parallel
        await Promise.all(deletePromises)

        alert(`✅ Alle ${chatCount} Chat-Verläufe wurden erfolgreich gelöscht`)
      } catch (error) {
        console.error('Failed to delete all sessions:', error)

        // Better error handling - check if some deletions succeeded
        const remainingSessions = sessions.length
        if (remainingSessions < chatCount) {
          alert(`⚠️ Teilweise erfolgreich: ${chatCount - remainingSessions} von ${chatCount} Chats gelöscht. Bitte versuche es erneut.`)
        } else {
          alert('❌ Fehler beim Löschen der Chat-Verläufe. Bitte versuche es erneut.')
        }
      } finally {
        setIsDeletingAllChats(false)
      }
    }
  }

  const handleSourceClick = (source: any) => {
    setSelectedSource(source)
    setSourcePreviewOpen(true)
  }

  // Filter sessions based on search
  const filteredSessions = searchQuery 
    ? sessions.filter(session => 
        session.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : sessions

  // Welcome message for empty sessions
  const welcomeMessage = {
    id: 'welcome',
    type: 'assistant' as const,
    content: 'Hallo! Ich bin der Streamworks RAG Assistant. Ich kann Fragen zu deinen Dokumenten beantworten und dir bei Streamworks-spezifischen Konfigurationen helfen. Was möchtest du wissen?',
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

  // ================================
  // RENDER
  // ================================

  return (
    <div className="h-full flex bg-gray-50 dark:bg-gray-900">
      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50"
          >
            <div className="flex items-center space-x-2">
              <X className="w-4 h-4" />
              <span className="text-sm font-medium">{error}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: 320 }}
            exit={{ width: 0 }}
            className="bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-full overflow-hidden"
          >
            {/* Sidebar Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-semibold text-gray-900 dark:text-white">
                  Chat-Verlauf
                </h2>
                <button
                  onClick={() => setShowStats(!showStats)}
                  className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  title="Statistiken"
                >
                  <BarChart3 className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                </button>
              </div>

              {/* Search Bar */}
              <div className="relative mb-3">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Chats durchsuchen..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
                  >
                    <X className="w-3 h-3 text-gray-400" />
                  </button>
                )}
              </div>

              {/* New Chat Button */}
              <button
                onClick={handleNewChat}
                disabled={isAnyLoading}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 text-sm font-medium bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg transition-colors shadow-sm"
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
                    className="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg text-xs"
                  >
                    <div className="grid grid-cols-2 gap-2 text-gray-600 dark:text-gray-300">
                      <div>Sessions: {sessionCount}</div>
                      <div>Nachrichten: {totalMessages}</div>
                      <div>AI Mode: {aiProvider === 'local' ? '⚡ Lokal' : '☁️ Cloud'}</div>
                      <div>Status: {isAnyLoading ? 'Laden...' : 'Bereit'}</div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Sessions List */}
            <div className="flex-1 overflow-y-auto p-2">
              {shouldShowEmptyState ? (
                <div className="text-center p-8 text-gray-500 dark:text-gray-400">
                  <MessageCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <div className="text-sm">Noch keine Chat-Verläufe</div>
                  <div className="text-xs mt-1">Erstelle einen neuen Chat!</div>
                </div>
              ) : (
                <div className="space-y-2">
                  {searchQuery && (
                    <div className="text-xs text-gray-500 dark:text-gray-400 px-2">
                      {filteredSessions.length} von {sessionCount} Sessions
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
                        session.id === currentSessionId
                          ? 'bg-primary-50 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-700'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="truncate font-medium text-gray-900 dark:text-white text-sm flex-1">
                          {session.title}
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteSession(session.id)
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-all"
                          aria-label={`Chat "${session.title}" löschen`}
                        >
                          <Trash2 className="w-3 h-3 text-red-500" />
                        </button>
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                        <span>{formatTimeForDisplay(session.updated_at, isClient)}</span>
                        <span>{session.message_count} Nachrichten</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer with Delete All Chats */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
              <button
                onClick={handleClearAllChats}
                disabled={isDeletingAllChats || !sessions.length}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-xs text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
                title={isDeletingAllChats ? `Lösche ${sessions.length} Chats...` : "Alle Chats löschen"}
              >
                {isDeletingAllChats ? (
                  <>
                    <Loader className="w-3 h-3 animate-spin" />
                    <span>Lösche {sessions.length} Chats...</span>
                  </>
                ) : (
                  <>
                    <Trash2 className="w-3 h-3" />
                    <span>Alle Chats löschen</span>
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Header */}
        <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <History className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
              <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                  Streamworks Assistant
                  <span className="ml-2 text-xs bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-400 px-2 py-1 rounded">
                    LlamaIndex RAG
                  </span>
                  <span className="ml-2 w-2 h-2 bg-green-500 rounded-full"></span>
                </h1>
              </div>
            </div>

            {/* Mode Display */}
            <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg px-3 py-2">
              <Zap className="w-4 h-4 text-primary-600 dark:text-primary-400" />
              <span className="ml-2 text-sm font-medium text-gray-900 dark:text-white">
                Modern RAG
              </span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <AnimatePresence>
            {displayMessages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`w-full flex gap-4 mb-4 ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}>
                    {/* Avatar with Labels */}
                    <div className="flex flex-col items-center gap-1 flex-shrink-0">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center shadow-lg ${
                        message.type === 'user'
                          ? 'bg-gradient-to-br from-primary-600 to-primary-700'
                          : 'bg-gradient-to-br from-primary-500 to-primary-700'
                      }`}>
                        {message.type === 'user' ? (
                          <span className="text-sm font-bold text-white">Du</span>
                        ) : (
                          <Sparkles className="w-5 h-5 text-white" />
                        )}
                      </div>
                      <span className="text-xs text-gray-500 font-medium">
                        {message.type === 'user' ? 'Du' : 'SKI'}
                      </span>
                    </div>

                    {/* Message Content */}
                    <div className={`flex flex-col max-w-[75%] ${
                      message.type === 'user' ? 'items-end' : 'items-start'
                    } group`}>
                      {/* Timestamp */}
                      <span className="text-xs text-gray-400 mb-1">
                        {formatTimeForDisplay(message.created_at, isClient)}
                      </span>

                      <div className={`p-4 rounded-xl shadow-sm ${
                        message.type === 'user'
                          ? 'bg-gradient-to-br from-primary-600 to-primary-700 text-white'
                          : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
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
                            onSourceClick={handleSourceClick}
                          />
                        ) : (
                          <div className="text-sm leading-relaxed">
                            <p className="whitespace-pre-wrap">{message.content}</p>
                          </div>
                        )}
                      </div>

                      {/* Message Actions */}
                      {message.type === 'assistant' && (
                        <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <MessageActions
                            message={message}
                            onCopy={() => navigator.clipboard.writeText(message.content)}
                            onFeedback={(id, feedback) => console.log('Feedback:', id, feedback)}
                            onExport={(msg) => console.log('Export:', msg)}
                          />
                        </div>
                      )}
                    </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading Indicator */}
          {isSendingMessage && (
            <TypingIndicator className="mb-4" />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="flex-shrink-0 p-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          <form onSubmit={handleSendMessage} className="flex space-x-4">
            <div className="flex-1">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Stelle eine Frage zu deinen Streamworks Dokumenten..."
                disabled={!canSendMessage}
                rows={1}
                className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 disabled:opacity-50"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage(e)
                  }
                }}
              />
            </div>
            <EnhancedButton
              type="submit"
              disabled={!canSendMessage || !input.trim()}
              variant="primary"
              icon={<Send className="w-4 h-4" />}
              loading={isSendingMessage}
              className="px-6 py-3"
            >
              Senden
            </EnhancedButton>
          </form>
          
          {!hasUserMessages && (
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                onClick={() => setInput('Was ist Streamworks?')}
                className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Was ist Streamworks?
              </button>
              <button
                onClick={() => setInput('Wie funktioniert Job Scheduling?')}
                className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Job Scheduling?
              </button>
              <button
                onClick={() => setInput('Erkläre mir XML Templates')}
                className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                XML Templates?
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Source Preview Modal */}
      <SourcePreviewModal
        source={selectedSource}
        isOpen={sourcePreviewOpen}
        onClose={() => {
          setSourcePreviewOpen(false)
          setSelectedSource(null)
        }}
      />
    </div>
  )
}

export default ModernChatInterface
