'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
// Removed Tabs import - using side-by-side layout instead
import {
  Send,
  Sparkles,
  Code2,
  FileText,
  CheckCircle2,
  AlertCircle,
  Activity,
  Zap,
  Target,
  Brain,
  Bot,
  History
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useLangExtractChat } from './hooks/useLangExtractChat'
import ParameterOverview from './components/ParameterOverview'
import TypingIndicator from './components/TypingIndicator'
import { LangExtractSessionSidebar } from './components/LangExtractSessionSidebar'
import { cn } from '@/lib/utils'

export const LangExtractInterface: React.FC = () => {
  const [message, setMessage] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const {
    session,
    sessions,
    messages,
    isLoading,
    isLoadingSessions,
    streamParameters,
    jobParameters,
    completionPercentage,
    criticalMissing,
    sendMessage,
    createSession,
    switchSession,
    deleteSession,
    deleteAllSessions,
    generateXML
  } = useLangExtractChat()

  // Auto session creation is now handled in the hook
  // No need for manual session creation here

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !isLoading) {
      await sendMessage(message)
      setMessage('')
      // Scroll to bottom after sending message
      setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setMessage(suggestion)
    textareaRef.current?.focus()
  }

  return (
    <div className="h-full flex bg-gradient-to-br from-gray-50 via-white to-blue-50/20 overflow-hidden">
      {/* Session Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: 320 }}
            exit={{ width: 0 }}
            className="overflow-hidden"
          >
            <LangExtractSessionSidebar
              sessions={sessions}
              currentSessionId={session}
              isLoading={isLoadingSessions}
              onCreateSession={createSession}
              onSwitchSession={switchSession}
              onDeleteSession={deleteSession}
              onDeleteAllSessions={deleteAllSessions}
              className="w-80"
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b bg-white/80 backdrop-blur-sm px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <History className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                SKI Streams Erstellen
              </h1>
              <p className="text-sm text-gray-500">Stream Parameter Extraktion mit KI</p>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex items-center gap-4">
            {session && (
              <Badge variant="outline" className="flex items-center gap-1">
                <Activity className="w-3 h-3" />
                Aktiv
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Main Content - Side-by-side Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Chat */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden border-r border-gray-200">
          {/* Chat Header */}
          <div className="px-6 py-3 bg-white border-b border-gray-200">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-blue-600" />
              <h2 className="font-semibold text-gray-900">Chat</h2>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            <div className="max-w-none">
              <div className="space-y-4">
                {messages && messages.map((msg, index) => {
                  const messageTime = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString('de-DE', {
                    hour: '2-digit',
                    minute: '2-digit'
                  }) : ''

                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      className={cn(
                        "flex gap-4 mb-4",
                        msg.type === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      {/* AI Avatar and Label */}
                      {msg.type === 'assistant' && (
                        <div className="flex flex-col items-center gap-1 flex-shrink-0">
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                            <Sparkles className="w-5 h-5 text-white" />
                          </div>
                          <span className="text-xs text-gray-500 font-medium">SKI</span>
                        </div>
                      )}

                      {/* Message Content */}
                      <div className="flex flex-col max-w-[75%]">
                        {/* Timestamp */}
                        {messageTime && (
                          <span className={cn(
                            "text-xs text-gray-400 mb-1",
                            msg.type === 'user' ? 'text-right' : 'text-left'
                          )}>
                            {messageTime}
                          </span>
                        )}

                        {/* Message Bubble */}
                        <div className={cn(
                          "rounded-xl p-4 shadow-sm",
                          msg.type === 'user'
                            ? "bg-gradient-to-br from-blue-600 to-indigo-700 text-white"
                            : "bg-white text-gray-800 border border-gray-200"
                        )}>
                          <p className={cn(
                            "whitespace-pre-wrap leading-relaxed",
                            msg.type === 'user' ? "text-white" : "text-gray-800"
                          )}>{msg.content}</p>

                          {/* Extracted Parameters */}
                          {msg.extracted_parameters && (Object.keys(msg.extracted_parameters.stream).length > 0 || Object.keys(msg.extracted_parameters.job).length > 0) && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <p className="text-xs font-medium mb-2 text-gray-600">
                                Extrahierte Parameter:
                              </p>
                              <div className="flex flex-wrap gap-1">
                                {Object.entries({...msg.extracted_parameters.stream, ...msg.extracted_parameters.job}).map(([key, value]) => (
                                  <Badge key={key} variant="secondary" className="text-xs">
                                    {key}: {String(value)}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* User Avatar and Label */}
                      {msg.type === 'user' && (
                        <div className="flex flex-col items-center gap-1 flex-shrink-0">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                            <span className="text-sm font-bold text-white">Sie</span>
                          </div>
                          <span className="text-xs text-gray-500 font-medium">Sie</span>
                        </div>
                      )}
                    </motion.div>
                  )
                })}

                {/* Loading Indicator */}
                {isLoading && (
                  <TypingIndicator className="mb-4" />
                )}

                {/* Welcome suggestions */}
                {messages && messages.length === 1 && (
                  <div className="mt-6">
                    <div className="grid grid-cols-1 gap-3">
                      <Button
                        variant="outline"
                        className="h-auto p-4 text-left justify-start bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 border-blue-200 transition-all duration-200"
                        onClick={() => handleSuggestionClick("Ich möchte einen SAP Export erstellen")}
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                            <span className="text-white text-lg">💾</span>
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">SAP Datenexport</div>
                            <div className="text-xs text-gray-600">Datenbank-Export konfigurieren</div>
                          </div>
                        </div>
                      </Button>
                      <Button
                        variant="outline"
                        className="h-auto p-4 text-left justify-start bg-gradient-to-r from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 border-green-200 transition-all duration-200"
                        onClick={() => handleSuggestionClick("Ich brauche einen Datentransfer zwischen Servern")}
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                            <span className="text-white text-lg">🔄</span>
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">Datentransfer</div>
                            <div className="text-xs text-gray-600">Server-zu-Server Transfer</div>
                          </div>
                        </div>
                      </Button>
                      <Button
                        variant="outline"
                        className="h-auto p-4 text-left justify-start bg-gradient-to-r from-purple-50 to-violet-50 hover:from-purple-100 hover:to-violet-100 border-purple-200 transition-all duration-200"
                        onClick={() => handleSuggestionClick("Erstelle einen Standard-Verarbeitungsjob")}
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                            <span className="text-white text-lg">⚙️</span>
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">Standard Job</div>
                            <div className="text-xs text-gray-600">Verarbeitungsjob erstellen</div>
                          </div>
                        </div>
                      </Button>
                    </div>
                  </div>
                )}

                {/* Scroll anchor */}
                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>

          {/* Input Area - Fixed at bottom */}
          <div className="flex-shrink-0 mt-auto bg-gradient-to-r from-white/95 via-blue-50/90 to-indigo-50/95 backdrop-blur-lg border-t border-gray-200 p-4 shadow-lg">
            <div className="max-w-none px-2">
              <form onSubmit={handleSubmit} className="flex gap-3">
                <Textarea
                  ref={textareaRef}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Beschreiben Sie Ihren StreamWorks Stream..."
                  className="flex-1 min-h-[60px] max-h-[120px] resize-none bg-white"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit(e)
                    }
                  }}
                  disabled={isLoading || !session}
                />

                <Button
                  type="submit"
                  disabled={!message.trim() || isLoading || !session}
                  className="self-end"
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </form>

              {criticalMissing && criticalMissing.length > 0 && (
                <div className="mt-3 p-2 bg-yellow-50 rounded-lg border border-yellow-200">
                  <p className="text-xs text-yellow-800">
                    <AlertCircle className="w-3 h-3 inline mr-1" />
                    Fehlende kritische Parameter: {criticalMissing.join(', ')}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel - Parameters */}
        <div className="w-[520px] bg-gray-50 overflow-hidden flex flex-col">
          {/* Parameter Header */}
          <div className="px-6 py-3 bg-white border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-blue-500" />
                <h2 className="font-semibold text-gray-900">Parameter Übersicht</h2>
              </div>
              <div className="text-xs text-gray-500">
                {Object.keys({...streamParameters, ...jobParameters}).length} Parameter extrahiert
              </div>
            </div>
          </div>

          {/* Parameter Content */}
          <div className="flex-1 overflow-hidden">
            <ParameterOverview
              streamParameters={streamParameters || {}}
              jobParameters={jobParameters || {}}
              criticalMissing={criticalMissing || []}
              completionPercentage={completionPercentage || 0}
              currentSessionId={session}
              sessions={sessions}
              className="h-full"
            />
          </div>
        </div>
      </div>
      </div>
    </div>
  )
}