'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus, Search, X, Trash2, Loader, MessageCircle,
  History, Settings, ChevronRight
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface LangExtractSession {
  session_id: string
  stream_name: string
  job_type?: string
  created_at: string
  last_activity: string
}

interface LangExtractSessionSidebarProps {
  sessions: LangExtractSession[]
  currentSessionId: string | null
  isLoading: boolean
  onCreateSession: () => Promise<void>
  onSwitchSession: (sessionId: string) => Promise<void>
  onDeleteSession: (sessionId: string) => Promise<void>
  onDeleteAllSessions: () => Promise<void>
  className?: string
}

export const LangExtractSessionSidebar: React.FC<LangExtractSessionSidebarProps> = ({
  sessions,
  currentSessionId,
  isLoading,
  onCreateSession,
  onSwitchSession,
  onDeleteSession,
  onDeleteAllSessions,
  className = ""
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [isDeletingSession, setIsDeletingSession] = useState<string | null>(null)
  const [isDeletingAll, setIsDeletingAll] = useState(false)

  // Filter sessions based on search
  const filteredSessions = searchQuery
    ? sessions.filter(session =>
        session.stream_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (session.job_type?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false)
      )
    : sessions

  const handleCreateSession = async () => {
    try {
      await onCreateSession()
    } catch (error) {
      console.error('Failed to create session:', error)
    }
  }

  const handleSwitchSession = async (sessionId: string) => {
    try {
      await onSwitchSession(sessionId)
    } catch (error) {
      console.error('Failed to switch session:', error)
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    if (confirm('⚠️ Möchtest du diese LangExtract Session wirklich löschen?')) {
      try {
        setIsDeletingSession(sessionId)
        await onDeleteSession(sessionId)
      } catch (error) {
        console.error('Failed to delete session:', error)
      } finally {
        setIsDeletingSession(null)
      }
    }
  }

  const handleDeleteAllSessions = async () => {
    if (confirm(`⚠️ Möchtest du wirklich ALLE ${sessions.length} LangExtract Sessions löschen?\n\nDiese Aktion kann nicht rückgängig gemacht werden!`)) {
      try {
        setIsDeletingAll(true)
        await onDeleteAllSessions()
      } catch (error) {
        console.error('Failed to delete all sessions:', error)
      } finally {
        setIsDeletingAll(false)
      }
    }
  }

  const formatTime = (timeString: string) => {
    try {
      const date = new Date(timeString)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / (1000 * 60))
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

      if (diffMins < 1) return 'gerade eben'
      if (diffMins < 60) return `vor ${diffMins}m`
      if (diffHours < 24) return `vor ${diffHours}h`
      if (diffDays < 7) return `vor ${diffDays}d`

      return date.toLocaleDateString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: '2-digit'
      })
    } catch {
      return timeString
    }
  }

  const getJobTypeColor = (jobType?: string) => {
    switch (jobType?.toUpperCase()) {
      case 'SAP': return 'bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-400'
      case 'FILE_TRANSFER': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
      case 'PROCESSING': return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    }
  }


  return (
    <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-full overflow-hidden ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <History className="w-4 h-4" />
            LangExtract Sessions
          </h2>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="p-1.5 h-auto"
              title="Settings"
            >
              <Settings className="w-3 h-3" />
            </Button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Sessions durchsuchen..."
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

        {/* New Session Button */}
        <Button
          onClick={handleCreateSession}
          disabled={isLoading}
          className="w-full flex items-center justify-center space-x-2 px-4 py-3 text-sm font-medium bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Neue Session</span>
        </Button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.length === 0 ? (
          <div className="text-center p-8 text-gray-500 dark:text-gray-400">
            <MessageCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <div className="text-sm">Noch keine Sessions</div>
            <div className="text-xs mt-1">Erstelle eine neue LangExtract Session!</div>
          </div>
        ) : (
          <div className="space-y-2">
            {searchQuery && (
              <div className="text-xs text-gray-500 dark:text-gray-400 px-2">
                {filteredSessions.length} von {sessions.length} Sessions
              </div>
            )}

            {filteredSessions.map((session) => (
              <motion.div
                key={session.session_id}
                layout
                role="button"
                tabIndex={0}
                onClick={() => handleSwitchSession(session.session_id)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    handleSwitchSession(session.session_id)
                  }
                }}
                className={`w-full text-left p-3 rounded-lg transition-colors group cursor-pointer relative ${
                  session.session_id === currentSessionId
                    ? 'bg-primary-50 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-700'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {/* Stream Name */}
                    <div className="font-medium text-gray-900 dark:text-white text-sm truncate">
                      {session.stream_name || 'Unnamed Stream'}
                    </div>

                    {/* Job Type Badge */}
                    {session.job_type && (
                      <Badge
                        variant="secondary"
                        className={`text-xs mt-1 ${getJobTypeColor(session.job_type)}`}
                      >
                        {session.job_type}
                      </Badge>
                    )}


                    {/* Timestamp */}
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {formatTime(session.last_activity)}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-1 ml-2">
                    {session.session_id === currentSessionId && (
                      <ChevronRight className="w-3 h-3 text-primary-600 dark:text-primary-400" />
                    )}

                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteSession(session.session_id)
                      }}
                      disabled={isDeletingSession === session.session_id}
                      className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-all"
                      aria-label={`Session "${session.stream_name}" löschen`}
                    >
                      {isDeletingSession === session.session_id ? (
                        <Loader className="w-3 h-3 text-red-500 animate-spin" />
                      ) : (
                        <Trash2 className="w-3 h-3 text-red-500" />
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Footer with Stats and Actions */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
        {/* Stats */}
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center mb-3">
          {sessions.length} Session{sessions.length !== 1 ? 's' : ''} • LangExtract v2.0
        </div>

        {/* Delete All Button */}
        {sessions.length > 0 && (
          <Button
            onClick={handleDeleteAllSessions}
            disabled={isDeletingAll || isLoading}
            variant="outline"
            size="sm"
            className="w-full flex items-center justify-center space-x-2 text-xs py-2 h-auto text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300 dark:text-red-400 dark:border-red-800 dark:hover:bg-red-900/30"
          >
            {isDeletingAll ? (
              <>
                <Loader className="w-3 h-3 animate-spin" />
                <span>Lösche alle...</span>
              </>
            ) : (
              <>
                <Trash2 className="w-3 h-3" />
                <span>Alle Sessions löschen</span>
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  )
}