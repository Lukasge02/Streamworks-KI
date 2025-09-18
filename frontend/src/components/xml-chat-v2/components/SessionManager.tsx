/**
 * Session Manager Component
 * Simple session management with history
 */

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  MessageSquare,
  MoreHorizontal,
  Trash2,
  Edit2,
  Check,
  X,
  Clock,
  FileCode,
  ChevronDown
} from 'lucide-react'
import { toast } from 'sonner'

import { useXMLChatStore, useXMLChatSelectors } from '../store/xmlChatStore'
import { SessionManagerProps } from '../types'

export default function SessionManager({ className = '' }: SessionManagerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')

  const {
    sessions,
    currentSession,
    createNewSession,
    switchToSession,
    deleteSession,
    updateSessionTitle
  } = useXMLChatStore()

  const { hasCurrentSession } = useXMLChatSelectors()

  const handleNewSession = () => {
    createNewSession()
    setIsOpen(false)
    toast.success('New chat session created')
  }

  const handleSwitchSession = (sessionId: string) => {
    switchToSession(sessionId)
    setIsOpen(false)
  }

  const handleDeleteSession = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    deleteSession(sessionId)
    toast.success('Session deleted')
  }

  const handleEditStart = (session: any, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingSessionId(session.id)
    setEditTitle(session.title)
  }

  const handleEditSave = (sessionId: string) => {
    if (editTitle.trim()) {
      updateSessionTitle(sessionId, editTitle.trim())
      toast.success('Session renamed')
    }
    setEditingSessionId(null)
    setEditTitle('')
  }

  const handleEditCancel = () => {
    setEditingSessionId(null)
    setEditTitle('')
  }

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div className={`relative ${className}`}>
      {/* Current Session Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
      >
        <MessageSquare className="w-4 h-4 text-gray-600" />
        <span className="text-sm font-medium text-gray-900 max-w-32 truncate">
          {currentSession?.title || 'New Chat'}
        </span>
        <ChevronDown className={`w-3 h-3 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Sessions Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />

            {/* Dropdown Panel */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute top-full right-0 mt-2 w-80 bg-white border border-gray-200 rounded-xl shadow-lg z-50 overflow-hidden"
            >
              {/* Header */}
              <div className="p-4 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-900">Chat Sessions</h3>
                  <button
                    onClick={handleNewSession}
                    className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Plus className="w-3 h-3" />
                    New Chat
                  </button>
                </div>
              </div>

              {/* Sessions List */}
              <div className="max-h-96 overflow-y-auto">
                {sessions.length === 0 ? (
                  <div className="p-6 text-center text-gray-500">
                    <MessageSquare className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                    <p className="text-sm">No chat sessions yet</p>
                  </div>
                ) : (
                  <div className="p-2">
                    {sessions.map((session) => (
                      <div
                        key={session.id}
                        className={`
                          group relative p-3 rounded-lg cursor-pointer transition-colors
                          ${currentSession?.id === session.id
                            ? 'bg-blue-50 border border-blue-200'
                            : 'hover:bg-gray-50'
                          }
                        `}
                        onClick={() => handleSwitchSession(session.id)}
                      >
                        {/* Session Content */}
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            {editingSessionId === session.id ? (
                              <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                                <input
                                  type="text"
                                  value={editTitle}
                                  onChange={(e) => setEditTitle(e.target.value)}
                                  className="flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                                  autoFocus
                                  onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleEditSave(session.id)
                                    if (e.key === 'Escape') handleEditCancel()
                                  }}
                                />
                                <button
                                  onClick={() => handleEditSave(session.id)}
                                  className="p-1 text-green-600 hover:bg-green-100 rounded"
                                >
                                  <Check className="w-3 h-3" />
                                </button>
                                <button
                                  onClick={handleEditCancel}
                                  className="p-1 text-red-600 hover:bg-red-100 rounded"
                                >
                                  <X className="w-3 h-3" />
                                </button>
                              </div>
                            ) : (
                              <>
                                <div className="flex items-center gap-2">
                                  <h4 className="font-medium text-sm text-gray-900 truncate">
                                    {session.title}
                                  </h4>
                                  {session.hasGeneratedXML && (
                                    <FileCode className="w-3 h-3 text-green-600 flex-shrink-0" />
                                  )}
                                </div>
                                <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                                  <span className="flex items-center gap-1">
                                    <Clock className="w-3 h-3" />
                                    {formatRelativeTime(session.updatedAt)}
                                  </span>
                                  {session.messageCount > 0 && (
                                    <span>{session.messageCount} messages</span>
                                  )}
                                </div>
                              </>
                            )}
                          </div>

                          {/* Actions */}
                          {editingSessionId !== session.id && (
                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button
                                onClick={(e) => handleEditStart(session, e)}
                                className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded"
                                title="Rename session"
                              >
                                <Edit2 className="w-3 h-3" />
                              </button>
                              {sessions.length > 1 && (
                                <button
                                  onClick={(e) => handleDeleteSession(session.id, e)}
                                  className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-100 rounded"
                                  title="Delete session"
                                >
                                  <Trash2 className="w-3 h-3" />
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}