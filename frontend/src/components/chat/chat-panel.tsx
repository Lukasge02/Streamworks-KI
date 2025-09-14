'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Loader2, FileText, ExternalLink, Settings, Filter, Zap } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Source[]
  processingTime?: number
  chunkCount?: number
  reranked?: boolean
  validation?: ValidationResult
}

interface Source {
  id: string
  content_preview: string
  similarity_score: number
  source_file: string
  page_number?: number
  heading: string
  doctype: string
  content_type: string
}

interface ValidationResult {
  enabled: boolean
  valid?: boolean
  message: string
  errors?: Array<{
    line: number
    column: number
    message: string
    level: string
  }>
}

interface ChatFilters {
  doctype?: string
  top_k: number
  enable_xsd_validation: boolean
  rerank: boolean
}

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<ChatFilters>({
    top_k: 5,
    enable_xsd_validation: false,
    rerank: false
  })
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Math.random().toString(36).substring(2, 15),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const payload = {
        query: input.trim(),
        filters: filters.doctype ? { doctype: filters.doctype } : undefined,
        enable_xsd_validation: filters.enable_xsd_validation,
        top_k: filters.top_k,
        rerank: filters.rerank
      }

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Chat request failed')
      }

      const result = await response.json()

      const assistantMessage: ChatMessage = {
        id: Math.random().toString(36).substring(2, 15),
        type: 'assistant',
        content: result.answer,
        timestamp: new Date(),
        sources: result.sources,
        processingTime: result.processing_time,
        chunkCount: result.chunk_count,
        reranked: result.reranked,
        validation: result.validation
      }

      setMessages(prev => [...prev, assistantMessage])

      // Toast notification (replace with actual toast implementation)
      console.log('Success:', `Antwort erhalten - ${result.processing_time}s, ${result.chunk_count} sources${result.reranked ? ' (reranked)' : ''}`)

    } catch (error) {
      const errorMessage: ChatMessage = {
        id: Math.random().toString(36).substring(2, 15),
        type: 'assistant',
        content: `Fehler beim Verarbeiten der Anfrage: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, errorMessage])

      // Toast notification (replace with actual toast implementation)
      console.error('Chat Fehler:', error instanceof Error ? error.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <div className="h-full flex flex-col max-w-6xl mx-auto">
      {/* Chat Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              RAG Chat
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Fragen Sie zu Ihren Dokumenten
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`btn-ghost btn text-sm ${showFilters ? 'bg-primary-100 dark:bg-primary-900/20' : ''}`}
            >
              <Filter className="w-4 h-4 mr-1" />
              Filter
            </button>
            <button
              onClick={clearChat}
              className="btn-ghost btn text-sm"
              disabled={messages.length === 0}
            >
              Clear
            </button>
          </div>
        </div>

        {/* Filters */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-4 overflow-hidden"
            >
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Dokumenttyp
                  </label>
                  <select
                    value={filters.doctype || ''}
                    onChange={(e) => setFilters(prev => ({ ...prev, doctype: e.target.value || undefined }))}
                    className="input text-sm"
                  >
                    <option value="">Alle</option>
                    <option value="general">General</option>
                    <option value="xml">XML</option>
                    <option value="technical">Technical</option>
                    <option value="manual">Manual</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Top-K Results
                  </label>
                  <select
                    value={filters.top_k}
                    onChange={(e) => setFilters(prev => ({ ...prev, top_k: parseInt(e.target.value) }))}
                    className="input text-sm"
                  >
                    <option value="3">3</option>
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="20">20</option>
                  </select>
                </div>

                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={filters.rerank}
                      onChange={(e) => setFilters(prev => ({ ...prev, rerank: e.target.checked }))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-xs text-gray-700 dark:text-gray-300">
                      <Zap className="w-3 h-3 inline mr-1" />
                      Reranking
                    </span>
                  </label>
                </div>

                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={filters.enable_xsd_validation}
                      onChange={(e) => setFilters(prev => ({ ...prev, enable_xsd_validation: e.target.checked }))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-xs text-gray-700 dark:text-gray-300">XSD Validation</span>
                  </label>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="text-gray-400 dark:text-gray-600 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Bereit für Ihre Fragen
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              Stellen Sie Fragen zu Ihren hochgeladenen Dokumenten
            </p>
          </motion.div>
        )}

        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-3xl rounded-lg p-4 ${
              message.type === 'user'
                ? 'bg-primary-600 text-white'
                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
            }`}>
              {/* Message Content */}
              <div className={`prose prose-sm max-w-none ${
                message.type === 'user' 
                  ? 'prose-invert' 
                  : 'prose-gray dark:prose-invert'
              }`}>
                {message.type === 'user' ? (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                )}
              </div>

              {/* Message Metadata */}
              {message.type === 'assistant' && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <div className="flex items-center space-x-3">
                      {message.processingTime && (
                        <span>⚡ {message.processingTime}s</span>
                      )}
                      {message.chunkCount && (
                        <span>📄 {message.chunkCount} sources</span>
                      )}
                      {message.reranked && (
                        <span className="text-orange-600">🔄 reranked</span>
                      )}
                    </div>
                    <span>{message.timestamp.toLocaleTimeString()}</span>
                  </div>

                  {/* XSD Validation */}
                  {message.validation && message.validation.enabled && (
                    <div className={`mt-2 p-2 rounded text-xs ${
                      message.validation.valid
                        ? 'bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-200'
                        : 'bg-red-50 text-red-800 dark:bg-red-900/20 dark:text-red-200'
                    }`}>
                      <span className="font-medium">XSD Validation:</span> {message.validation.message}
                    </div>
                  )}

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3">
                      <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Sources ({message.sources.length})
                      </h4>
                      <div className="space-y-2">
                        {message.sources.map((source, idx) => (
                          <div
                            key={source.id}
                            className="p-2 bg-gray-50 dark:bg-gray-700/50 rounded text-xs"
                          >
                            <div className="flex items-start justify-between mb-1">
                              <div className="flex items-center space-x-2">
                                <FileText className="w-3 h-3 text-gray-400" />
                                <span className="font-medium text-gray-900 dark:text-gray-100">
                                  {source.source_file}
                                </span>
                                {source.page_number && (
                                  <span className="text-gray-500">
                                    (Page {source.page_number})
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center space-x-2">
                                <span className="badge badge-primary">
                                  {source.doctype}
                                </span>
                                <span className="text-primary-600 font-medium">
                                  {(source.similarity_score * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                            {source.heading && (
                              <div className="text-gray-700 dark:text-gray-300 mb-1 font-medium">
                                {source.heading}
                              </div>
                            )}
                            <p className="text-gray-600 dark:text-gray-400 line-clamp-2">
                              {source.content_preview}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        ))}

        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 max-w-xs">
              <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Verarbeite Anfrage...</span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Fragen Sie zu Ihren Dokumenten..."
            className="textarea flex-1 resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-primary btn self-end"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
      </div>
    </div>
  )
}