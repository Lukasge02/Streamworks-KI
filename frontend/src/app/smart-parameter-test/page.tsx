/**
 * Smart Parameter Collection - Test Page (Fixed Version)
 * Teste das neue MVP System für intelligente Parameter-Sammlung
 */

'use client'

import React, { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster, toast } from 'sonner'
import { Send, Download, RefreshCw, CheckCircle, AlertCircle, X, Eye } from 'lucide-react'

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
    },
  },
})

// API Base URL
const API_BASE = 'http://localhost:8000/api/chat-xml/smart'

// Types
interface SmartSession {
  session_id: string
  job_type?: string
  status: string
  dialog_state: string
  completion_percentage: number
  message: string
  suggested_questions: string[]
  created_at: string
}

interface ChatMessage {
  session_id: string
  response_message: string
  dialog_state: string
  priority: string
  extracted_parameters: string[]
  next_parameter?: string
  completion_percentage: number
  suggested_questions: string[]
  validation_issues: string[]
  timestamp: string
}

interface ParameterExport {
  session_id: string
  job_type?: string
  parameters: Record<string, any>
  completion_percentage: number
  validation_status: string
  export_timestamp: string
}

// Main Component
function SmartParameterTest() {
  const [session, setSession] = useState<SmartSession | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [parameters, setParameters] = useState<ParameterExport | null>(null)
  const [showParameterPanel, setShowParameterPanel] = useState(false)

  // Create new session
  const createSession = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${API_BASE}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'test_user_' + Date.now()
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const sessionData: SmartSession = await response.json()
      setSession(sessionData)
      setMessages([])
      setParameters(null)
      setShowParameterPanel(false)

      toast.success('Neue Session erstellt!')
    } catch (error) {
      toast.error('Fehler beim Erstellen der Session: ' + (error as Error).message)
      console.error('Session creation error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Send message
  const sendMessage = async () => {
    if (!session || !inputMessage.trim() || isLoading) return

    try {
      setIsLoading(true)
      const response = await fetch(`${API_BASE}/sessions/${session.session_id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          extract_parameters: true
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const messageData: ChatMessage = await response.json()
      setMessages(prev => [...prev, messageData])
      setInputMessage('')

      // Update session completion
      if (session) {
        setSession({
          ...session,
          completion_percentage: messageData.completion_percentage,
          dialog_state: messageData.dialog_state
        })
      }

      // Auto-update parameters after each message
      if (messageData.extracted_parameters.length > 0) {
        setTimeout(() => {
          exportParameters()
          setShowParameterPanel(true)
        }, 500)
        toast.success(`${messageData.extracted_parameters.length} Parameter extrahiert: ${messageData.extracted_parameters.join(', ')}`)
      }

    } catch (error) {
      toast.error('Fehler beim Senden: ' + (error as Error).message)
      console.error('Message send error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Export parameters
  const exportParameters = async () => {
    if (!session) return

    try {
      const response = await fetch(`${API_BASE}/sessions/${session.session_id}/parameters`)
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const paramData: ParameterExport = await response.json()
      setParameters(paramData)

      toast.success('Parameter exportiert!')
    } catch (error) {
      toast.error('Export Fehler: ' + (error as Error).message)
      console.error('Export error:', error)
    }
  }

  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              🚀 Smart Parameter Collection - MVP Test
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Teste die intelligente Parameter-Extraktion aus Chat-Nachrichten
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={createSession}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Neue Session
            </button>
            {session && (
              <button
                onClick={() => {
                  exportParameters()
                  setShowParameterPanel(true)
                }}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Eye className="w-4 h-4" />
                Parameter anzeigen
              </button>
            )}
          </div>
        </div>

        {/* Session Info */}
        {session && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-blue-900">
                  Session: {session.session_id.slice(0, 8)}...
                </span>
                <span className="ml-4 text-sm text-blue-700">
                  Job-Type: {session.job_type || 'Noch nicht bestimmt'}
                </span>
                <span className="ml-4 text-sm text-blue-700">
                  Status: {session.dialog_state}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-32 bg-blue-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${session.completion_percentage}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-blue-900">
                  {Math.round(session.completion_percentage)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="relative">
        {/* Chat Area */}
        <div className={`transition-all duration-300 ${showParameterPanel ? 'pr-96' : ''}`}>
          <div className="h-[calc(100vh-140px)] flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 pb-32">
              {!session ? (
                <div className="text-center py-12">
                  <div className="text-gray-500 mb-4">
                    Klicke auf "Neue Session" um zu beginnen
                  </div>
                  <div className="text-sm text-gray-400 max-w-md mx-auto">
                    <strong>Test Nachrichten:</strong><br/>
                    "Ich möchte einen Standard-Stream namens TestStream mit 10 maximalen Läufen erstellen"<br/>
                    "SAP Report RBDAGAIN auf PA1_100 mit Batch_PUR User"
                  </div>
                </div>
              ) : (
                <div className="space-y-4 max-w-4xl mx-auto">
                  {/* Initial Message */}
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm">
                      AI
                    </div>
                    <div className="flex-1 bg-white rounded-lg p-4 shadow-sm">
                      <p className="text-gray-900">{session.message}</p>
                      {session.suggested_questions.length > 0 && (
                        <div className="mt-3 space-y-2">
                          {session.suggested_questions.map((question, idx) => (
                            <button
                              key={idx}
                              onClick={() => setInputMessage(question)}
                              className="block w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                            >
                              💡 {question}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Chat Messages */}
                  {messages.map((msg, idx) => (
                    <div key={idx} className="space-y-4">
                      {/* User Message */}
                      <div className="flex items-start gap-3 justify-end">
                        <div className="bg-blue-600 text-white rounded-lg p-4 max-w-md">
                          <p>User message would go here</p>
                        </div>
                        <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-white text-sm">
                          U
                        </div>
                      </div>

                      {/* AI Response */}
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm">
                          AI
                        </div>
                        <div className="flex-1 bg-white rounded-lg p-4 shadow-sm">
                          <p className="text-gray-900">{msg.response_message}</p>

                          {/* Extracted Parameters */}
                          {msg.extracted_parameters.length > 0 && (
                            <div className="mt-3 p-3 bg-green-50 rounded-lg">
                              <div className="flex items-center gap-2 text-green-800 text-sm font-medium mb-2">
                                <CheckCircle className="w-4 h-4" />
                                Parameter extrahiert:
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {msg.extracted_parameters.map((param, pidx) => (
                                  <span key={pidx} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                                    {param}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Validation Issues */}
                          {msg.validation_issues.length > 0 && (
                            <div className="mt-3 p-3 bg-red-50 rounded-lg">
                              <div className="flex items-center gap-2 text-red-800 text-sm font-medium mb-2">
                                <AlertCircle className="w-4 h-4" />
                                Validierungsfehler:
                              </div>
                              <ul className="text-red-700 text-sm space-y-1">
                                {msg.validation_issues.map((issue, iidx) => (
                                  <li key={iidx}>• {issue}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Suggested Questions */}
                          {msg.suggested_questions.length > 0 && (
                            <div className="mt-3 space-y-2">
                              {msg.suggested_questions.map((question, qidx) => (
                                <button
                                  key={qidx}
                                  onClick={() => setInputMessage(question)}
                                  className="block w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                  💡 {question}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Input Area - Fixed at bottom */}
            {session && (
              <div className="absolute bottom-0 left-0 right-0 border-t border-gray-200 bg-white p-6 z-10">
                <div className="max-w-4xl mx-auto">
                  <div className="flex gap-3">
                    <textarea
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Beschreibe den Job den du erstellen möchtest..."
                      className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      rows={2}
                      disabled={isLoading}
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!inputMessage.trim() || isLoading}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      Senden
                    </button>
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    <strong>Test-Beispiele:</strong> "Ich möchte einen Standard-Stream namens TestStream mit 10 maximalen Läufen erstellen"
                    oder "SAP Report RBDAGAIN auf PA1_100 System mit Batch_PUR User"
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Parameter Display - Fixed Right Sidebar */}
        <div className={`fixed top-0 right-0 w-96 h-full bg-white border-l border-gray-200 overflow-y-auto z-20 transition-transform duration-300 ${showParameterPanel ? 'translate-x-0' : 'translate-x-full'}`}>
          <div className="p-6">
            {/* Close Button */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Parameter Panel</h3>
              <button
                onClick={() => setShowParameterPanel(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {!parameters ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-sm">Keine Parameter geladen</div>
                <button
                  onClick={exportParameters}
                  disabled={!session}
                  className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
                >
                  Parameter laden
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Parameter Export</h3>
                  <span className={`px-2 py-1 text-xs rounded ${
                    parameters.validation_status === 'valid'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {parameters.validation_status}
                  </span>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Job-Type</label>
                    <div className="text-sm text-gray-900">{parameters.job_type || 'Nicht gesetzt'}</div>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-700">Vervollständigung</label>
                    <div className="text-sm text-gray-900">{Math.round(parameters.completion_percentage)}%</div>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-700">Parameter</label>
                    <div className="bg-gray-50 rounded-lg p-3 text-xs font-mono max-h-96 overflow-y-auto">
                      <pre>{JSON.stringify(parameters.parameters, null, 2)}</pre>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(JSON.stringify(parameters.parameters, null, 2))
                      toast.success('Parameter in Zwischenablage kopiert!')
                    }}
                    className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm transition-colors"
                  >
                    JSON kopieren
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Main App
export default function SmartParameterTestPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <SmartParameterTest />
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}
