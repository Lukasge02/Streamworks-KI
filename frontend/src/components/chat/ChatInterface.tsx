'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Clock, Loader, Settings, History, Plus, Search, BarChart3, Trash2, X } from 'lucide-react'
// Using Session API for OpenAI + EmbeddingGemma hybrid RAG
import { useChatSession, ChatMessage } from '../../hooks/useChatSession'

// Consistent user ID across all services
const USER_ID = 'default-user'
import { formatTimeForDisplay } from '../../utils/timeUtils'
import { EnterpriseResponseFormatter } from './EnterpriseResponseFormatter'
import { SourcePreviewModal } from './SourcePreviewModal'
import { MessageActions } from './MessageActions'
import { EnterpriseInputArea } from './EnterpriseInputArea'
// Toast context temporarily disabled

export const ChatInterface = () => {
  const chatSession = useChatSession()
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isClient, setIsClient] = useState(false)
  const [selectedSource, setSelectedSource] = useState<any>(null)
  const [sourcePreviewOpen, setSourcePreviewOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [showStats, setShowStats] = useState(false)
  // Using OpenAI + EmbeddingGemma hybrid setup (configured in backend)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setIsClient(true)
  }, [])

  // Create new session if none exists
  useEffect(() => {
    if (isClient && chatSession.sessions.length === 0 && !chatSession.currentSessionId && !chatSession.isLoading) {
      chatSession.createNewSession()
    }
  }, [isClient, chatSession.sessions.length, chatSession.currentSessionId, chatSession.isLoading])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatSession.currentSession?.messages])

  const createConfidenceBadge = (score: number) => {
    if (score >= 0.8) return { level: 'high', color: 'emerald', description: 'Sehr zuverlässig' }
    if (score >= 0.6) return { level: 'medium', color: 'amber', description: 'Teilweise zuverlässig' }
    return { level: 'low', color: 'rose', description: 'Weniger zuverlässig' }
  }

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading || chatSession.isLoading) return

    const userMessageContent = input.trim()
    setInput('')
    setIsLoading(true)

    try {
      // Use Session API which handles OpenAI + EmbeddingGemma
      const success = await chatSession.sendMessage(userMessageContent)
      
      if (!success) {
        throw new Error('Failed to send message')
      }
      
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unbekannter Fehler'
      
      // Show error to user - in a real implementation, you might want to show a toast
      alert(`Fehler: ${errorMessage}`)
      
    } finally {
      setIsLoading(false)
    }
  }

  const handleSourceClick = (source: any) => {
    setSelectedSource(source)
    setSourcePreviewOpen(true)
  }

  const handleNewChat = () => {
    chatSession.createNewSession()
    setSearchQuery('') // Clear search when creating new chat
  }



  const handleClearAllChats = async () => {
    if (confirm('⚠️ Möchtest du wirklich alle Chat-Verläufe löschen? Diese Aktion kann nicht rückgängig gemacht werden.')) {
      // Delete all sessions one by one (API doesn't have a bulk delete yet)
      for (const session of chatSession.sessions) {
        await chatSession.deleteSession(session.id)
      }
      alert('Alle Chat-Verläufe wurden gelöscht')
    }
  }

  const handleSessionSelect = (sessionId: string) => {
    chatSession.switchToSession(sessionId)
  }

  const filteredSessions = searchQuery ? chatSession.searchSessions(searchQuery) : chatSession.sessions
  const stats = chatSession.getSessionStats()
  
  const welcomeMessage = {
    id: 'welcome',
    type: 'assistant' as const,
    content: 'Hallo! Ich bin der Streamworks RAG Assistant. Ich kann Fragen zu deinen Dokumenten beantworten und dir bei Streamworks-spezifischen Konfigurationen helfen. Was möchtest du wissen?',
    timestamp: new Date()
  }
  
  const currentMessages = (chatSession.currentSession?.messages?.length ?? 0) > 0 
    ? chatSession.currentSession?.messages ?? []
    : [welcomeMessage]
    
  // Check if there are any user messages in current session
  const hasUserMessages = chatSession.currentSession?.messages?.some(msg => msg.type === 'user') || false

  // Remove debug output for production
  // console.log('Debug - Current Session:', chatStorage.currentSession)
  // console.log('Debug - Current Messages:', currentMessages)
  // console.log('Debug - All Sessions:', chatStorage.sessions)

  return (
    <div className="h-full flex bg-gray-50 dark:bg-gray-900">
      {/* Simple Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: 320 }}
            exit={{ width: 0 }}
            className="bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-full overflow-hidden"
          >
            {/* Enhanced Sidebar Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-semibold text-gray-900 dark:text-white">Chat-Verlauf</h2>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => setShowStats(!showStats)}
                    className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    title="Statistiken"
                  >
                    <BarChart3 className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                  </button>
                </div>
              </div>
              
              {/* Search Bar */}
              <div className="relative mb-3">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Chats durchsuchen..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              
              {/* Action Buttons */}
              <div className="mb-3">
                <button
                  onClick={handleNewChat}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors shadow-sm"
                  title="Neuen Chat starten"
                >
                  <Plus className="w-4 h-4" />
                  <span>Neuer Chat</span>
                </button>
              </div>
              
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
                      <div>Sessions: {stats.totalSessions}</div>
                      <div>Nachrichten: {stats.totalMessages}</div>
                      <div>Durchschnitt: {stats.avgMessagesPerSession}</div>
                      <div>Speicher: {stats.storagePercent}%</div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Enhanced Sessions List */}
            <div className="flex-1 overflow-y-auto p-2 scrollbar-thin">
              {searchQuery && (
                <div className="mb-2 px-2 text-xs text-gray-500 dark:text-gray-400">
                  {filteredSessions.length} von {chatSession.sessions.length} Sessions gefunden
                </div>
              )}
              
              {chatSession.isLoading ? (
                <div className="text-center p-8 text-gray-500 dark:text-gray-400">
                  <div className="text-4xl mb-2">⏳</div>
                  <div className="text-sm">Lade Chat-Verläufe...</div>
                </div>
              ) : filteredSessions.length === 0 ? (
                <div className="text-center p-8 text-gray-500 dark:text-gray-400">
                  <div className="text-4xl mb-2">{searchQuery ? '🔍' : '💬'}</div>
                  <div className="text-sm">
                    {searchQuery ? 'Keine passenden Chats gefunden' : 'Noch keine Chat-Verläufe'}
                  </div>
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery('')}
                      className="mt-2 text-blue-600 dark:text-blue-400 text-sm hover:underline"
                    >
                      Suche zurücksetzen
                    </button>
                  )}
                </div>
              ) : (
                filteredSessions.map((session) => (
                  <motion.button
                    key={session.id}
                    layout
                    onClick={() => handleSessionSelect(session.id)}
                    className={`w-full text-left p-3 rounded-lg mb-2 transition-colors group ${
                      session.id === chatSession.currentSessionId
                        ? 'bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="truncate font-medium text-gray-900 dark:text-white text-sm flex-1">
                        {session.title}
                      </div>
                      <button
                        onClick={async (e) => {
                          e.stopPropagation()
                          if (confirm('Diesen Chat löschen?')) {
                            await chatSession.deleteSession(session.id)
                          }
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-all"
                        title="Chat löschen"
                      >
                        <Trash2 className="w-3 h-3 text-red-500" />
                      </button>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>{formatTimeForDisplay(session.updated_at, isClient)}</span>
                      <span>{session.messages.length} Nachrichten</span>
                    </div>
                  </motion.button>
                ))
              )}
            </div>
            
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Fixed Header */}
        <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <History className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                  Streamworks Assistant
                  <span className="ml-2 w-2 h-2 bg-green-500 rounded-full"></span>
                </h1>
              </div>
            </div>
            
            {/* OpenAI + EmbeddingGemma hybrid RAG active */}
          </div>
        </div>

        {/* Scrollable Messages Container */}
        <div className="flex-1 overflow-y-auto scrollbar-thin p-6 space-y-6 min-h-0">
          <div className="space-y-6">
          <AnimatePresence>
            {currentMessages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-3xl ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                  <div className={`flex items-start space-x-3 ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    {/* Avatar */}
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      message.type === 'user' 
                        ? 'bg-primary-600' 
                        : 'bg-blue-600'
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
                        {message.type === 'assistant' ? (
                          <EnterpriseResponseFormatter
                            content={message.content}
                            confidence_score={'confidence_score' in message ? message.confidence_score : undefined}
                            sources={'sources' in message ? message.sources : undefined}
                            processing_time={'processing_time' in message ? message.processing_time : undefined}
                            model_info={'model_info' in message ? message.model_info : undefined}
                            onCopyResponse={() => navigator.clipboard.writeText(message.content)}
                            onSourceClick={handleSourceClick}
                          />
                        ) : (
                          <div className="text-sm leading-relaxed">
                            <p>{message.content}</p>
                          </div>
                        )}
                      </div>

                      {/* Message Metadata */}
                      <div className="mt-2 flex items-center justify-between">
                        <div className="flex items-center space-x-3 text-xs text-gray-500">
                          <span className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>{formatTimeForDisplay(message.timestamp, isClient)}</span>
                          </span>
                        </div>
                        
                        {/* Message Actions */}
                        {message.type === 'assistant' && (
                          <MessageActions
                            message={message}
                            onCopy={() => navigator.clipboard.writeText(message.content)}
                            onFeedback={(id, feedback) => console.log('Feedback:', id, feedback)}
                            onExport={(msg) => console.log('Export:', msg)}
                          />
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading Indicator */}
          {(isLoading || chatSession.isLoading) && (
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

          {/* Error Display */}
          {chatSession.error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 max-w-2xl">
                <div className="text-red-800 dark:text-red-200 text-sm">
                  <strong>Fehler:</strong> {chatSession.error}
                </div>
              </div>
            </motion.div>
          )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Fixed Input Area */}
        <div className="flex-shrink-0 overflow-hidden">
          <EnterpriseInputArea
            input={input}
            setInput={setInput}
            isLoading={isLoading}
            onSubmit={sendMessage}
            onSuggestionClick={setInput}
            placeholder="Stelle eine Frage zu deinen Streamworks Dokumenten..."
            showSuggestions={!hasUserMessages}
          />
        </div>

        {/* Footer with Delete All Chats */}
        <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex justify-center">
            <button
              onClick={handleClearAllChats}
              className="flex items-center space-x-2 px-4 py-2 text-sm text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              title="Alle Chats löschen"
            >
              <Trash2 className="w-4 h-4" />
              <span>Alle Chats löschen</span>
            </button>
          </div>
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