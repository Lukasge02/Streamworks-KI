'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  History, 
  Search, 
  Plus, 
  Trash2, 
  Edit2, 
  MessageSquare, 
  Calendar,
  Clock,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { EnterpriseChatSession } from '../../hooks/useEnterpriseChat'
import { ChatSession } from '@/services/chatApiService'
import { formatRelativeTimeForDisplay } from '../../utils/timeUtils'

interface ChatSidebarProps {
  isOpen: boolean
  onToggle: () => void
  onSessionSelect: (session: EnterpriseChatSession) => void
  onNewChat?: () => void
  enterpriseChat: {
    sessions: EnterpriseChatSession[]
    currentSessionId: string | null
    createSession: (title?: string) => string
    deleteSession: (sessionId: string) => void
    clearHistory: () => void
    updateSessionTitle: (sessionId: string, newTitle: string) => void
    searchSessions: (query: string) => EnterpriseChatSession[]
    getStats: () => any
  }
}

export const ChatSidebar = ({ isOpen, onToggle, onSessionSelect, onNewChat, enterpriseChat }: ChatSidebarProps) => {
  const {
    sessions,
    currentSessionId,
    createSession,
    deleteSession,
    clearHistory,
    updateSessionTitle,
    searchSessions,
    getStats
  } = enterpriseChat
  
  const [searchQuery, setSearchQuery] = useState('')
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [showStats, setShowStats] = useState(false)
  const [deleteConfirmSession, setDeleteConfirmSession] = useState<string | null>(null)
  const [showClearHistoryConfirm, setShowClearHistoryConfirm] = useState(false)
  const [isClient, setIsClient] = useState(false)

  const filteredSessions = searchQuery ? searchSessions(searchQuery) : sessions
  const stats = getStats()

  const handleNewSession = () => {
    if (onNewChat) {
      onNewChat()
    } else {
      const sessionId = createSession()
      const newSession = sessions.find(s => s.id === sessionId)
      if (newSession) {
        onSessionSelect(newSession)
      }
    }
  }

  const handleEditTitle = (session: EnterpriseChatSession) => {
    setEditingSessionId(session.id)
    setEditTitle(session.title)
  }

  const handleSaveTitle = () => {
    if (editingSessionId && editTitle.trim()) {
      updateSessionTitle(editingSessionId, editTitle.trim())
    }
    setEditingSessionId(null)
    setEditTitle('')
  }

  const handleDeleteSession = (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation()
    setDeleteConfirmSession(sessionId)
  }

  const confirmDeleteSession = () => {
    if (deleteConfirmSession) {
      deleteSession(deleteConfirmSession)
      setDeleteConfirmSession(null)
    }
  }

  const confirmClearHistory = () => {
    clearHistory()
    setShowClearHistoryConfirm(false)
  }

  useEffect(() => {
    setIsClient(true)
  }, [])

  return (
    <>
      {/* Centered Expand Tab with subtle colors */}
      {!isOpen && (
        <div 
          onClick={onToggle}
          className="absolute top-1/2 -translate-y-1/2 left-0 z-50 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm border border-gray-200/50 dark:border-gray-600/50 text-gray-600 dark:text-gray-300 rounded-r-xl shadow-lg hover:bg-white dark:hover:bg-gray-800 hover:shadow-xl hover:border-gray-300 dark:hover:border-gray-500 transition-all duration-300 cursor-pointer group"
          title="Chat-Verlauf einblenden"
        >
          <div className="flex flex-col items-center py-4 px-2">
            <History className="w-5 h-5 mb-2 group-hover:scale-110 transition-transform" />
            <div className="writing-mode-vertical text-xs font-medium tracking-wider" style={{writingMode: 'vertical-rl', textOrientation: 'mixed'}}>
              CHATS
            </div>
            <ChevronRight className="w-4 h-4 mt-2 group-hover:translate-x-1 transition-transform" />
          </div>
        </div>
      )}

      {/* Sidebar - Modern glass-morphism design */}
      <motion.div
        initial={false}
        animate={{ x: isOpen ? 0 : -320 }}
        transition={{ duration: 0.4, ease: [0.4, 0.0, 0.2, 1] }}
        className="absolute left-0 top-0 h-full w-80 bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border-r border-gray-200/50 dark:border-gray-700/50 z-40 flex flex-col shadow-2xl"
      >
            {/* Header - Enhanced with gradient */}
            <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 dark:from-blue-900/20 dark:to-indigo-900/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg mr-3">
                    <History className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  Chat-Verlauf
                </h2>
                <button
                  onClick={() => setShowStats(!showStats)}
                  className="p-2 text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all"
                  title="Statistiken"
                >
                  <BarChart3 className="w-5 h-5" />
                </button>
              </div>

              {/* Stats - Enhanced design */}
              {showStats && (
                <motion.div
                  initial={{ opacity: 0, height: 0, y: -10 }}
                  animate={{ opacity: 1, height: 'auto', y: 0 }}
                  exit={{ opacity: 0, height: 0, y: -10 }}
                  className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl border border-blue-200/50 dark:border-blue-700/50"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-white/60 dark:bg-gray-800/60 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.totalSessions}</div>
                      <div className="text-xs font-medium text-gray-600 dark:text-gray-400">Sessions</div>
                    </div>
                    <div className="text-center p-3 bg-white/60 dark:bg-gray-800/60 rounded-lg">
                      <div className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.totalMessages}</div>
                      <div className="text-xs font-medium text-gray-600 dark:text-gray-400">Nachrichten</div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Search - Enhanced with modern styling */}
              <div className="relative group">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                <input
                  type="text"
                  placeholder="Chats durchsuchen..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                />
              </div>

              {/* New Chat Button - Enhanced gradient style */}
              <button
                onClick={handleNewSession}
                className="w-full mt-4 py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl transition-all duration-200 flex items-center justify-center text-sm font-semibold shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98]"
              >
                <Plus className="w-5 h-5 mr-2" />
                Neuer Chat
              </button>
            </div>

            {/* Sessions List - Enhanced spacing */}
            <div className="flex-1 overflow-y-auto p-4">
              <AnimatePresence>
                {filteredSessions.map((session) => (
                  <motion.div
                    key={session.id}
                    layout
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`group p-4 mb-3 rounded-xl cursor-pointer transition-all duration-200 hover:bg-gray-50 dark:hover:bg-gray-800/50 hover:shadow-md hover:scale-[1.01] ${
                      session.id === currentSessionId 
                        ? 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border border-blue-200 dark:border-blue-700/50 shadow-sm' 
                        : 'border border-transparent'
                    }`}
                    onClick={() => onSessionSelect(session)}
                  >
                    {editingSessionId === session.id ? (
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onBlur={handleSaveTitle}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveTitle()
                          if (e.key === 'Escape') setEditingSessionId(null)
                        }}
                        className="w-full p-1 text-sm bg-transparent border-b border-blue-500 focus:outline-none"
                        autoFocus
                      />
                    ) : (
                      <>
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate mb-2">
                              {session.title}
                            </h3>
                            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                              <div className="flex items-center">
                                <MessageSquare className="w-3 h-3 mr-1" />
                                <span>{session.messages.length}</span>
                              </div>
                              <div className="flex items-center">
                                <Clock className="w-3 h-3 mr-1" />
                                <span>{formatRelativeTimeForDisplay(session.updated_at, isClient)}</span>
                              </div>
                            </div>
                            {session.messages.length > 0 && (
                              <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 truncate bg-gray-50 dark:bg-gray-800/50 px-2 py-1 rounded-md">
                                {session.messages[session.messages.length - 1].content}
                              </p>
                            )}
                          </div>
                          <div className="flex opacity-0 group-hover:opacity-100 transition-all duration-200 ml-2 gap-1">
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleEditTitle(session)
                              }}
                              className="p-1.5 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all"
                              title="Umbenennen"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={(e) => handleDeleteSession(session.id, e)}
                              className="p-1.5 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
                              title="Löschen"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      </>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {filteredSessions.length === 0 && (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
                    <MessageSquare className="w-8 h-8 opacity-50" />
                  </div>
                  <p className="text-sm font-medium mb-1">
                    {searchQuery ? 'Keine Ergebnisse gefunden' : 'Noch keine Unterhaltungen'}
                  </p>
                  <p className="text-xs">
                    {searchQuery ? 'Versuche andere Suchbegriffe' : 'Starte einen neuen Chat'}
                  </p>
                </div>
              )}
            </div>

            {/* Footer - Enhanced styling */}
            <div className="p-4 border-t border-gray-200/50 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-800/30">
              <button
                onClick={() => setShowClearHistoryConfirm(true)}
                className="w-full py-3 px-4 text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-all duration-200 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed border border-red-200/50 dark:border-red-800/50 hover:border-red-300 dark:hover:border-red-700"
                disabled={sessions.length === 0}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Verlauf löschen ({sessions.length})
              </button>
            </div>

        {/* Collapse Tab - Positioned at right edge, vertically centered */}
        <div 
          onClick={onToggle}
          className="absolute top-1/2 -translate-y-1/2 right-0 z-50 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm border border-gray-200/50 dark:border-gray-600/50 text-gray-600 dark:text-gray-300 rounded-l-xl shadow-lg hover:bg-white dark:hover:bg-gray-800 hover:shadow-xl hover:border-gray-300 dark:hover:border-gray-500 transition-all duration-300 cursor-pointer group"
          title="Chat-Verlauf ausblenden"
        >
          <div className="flex flex-col items-center py-4 px-2">
            <ChevronLeft className="w-4 h-4 mb-2 group-hover:translate-x-[-2px] transition-transform" />
            <div className="writing-mode-vertical text-xs font-medium tracking-wider" style={{writingMode: 'vertical-rl', textOrientation: 'mixed'}}>
              CHATS
            </div>
            <History className="w-5 h-5 mt-2 group-hover:scale-110 transition-transform" />
          </div>
        </div>
      </motion.div>

      {/* Overlay - for smaller screens when sidebar is open */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onToggle}
          className="absolute inset-0 bg-black bg-opacity-50 z-30 xl:hidden"
        />
      )}

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {deleteConfirmSession && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 z-50"
              onClick={() => setDeleteConfirmSession(null)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white dark:bg-gray-800 rounded-xl shadow-2xl z-50 p-6"
            >
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mr-3">
                  <Trash2 className="w-5 h-5 text-red-600 dark:text-red-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Chat löschen
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                Möchtest du diese Unterhaltung wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => setDeleteConfirmSession(null)}
                  className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
                >
                  Abbrechen
                </button>
                <button
                  onClick={confirmDeleteSession}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Löschen
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Clear History Confirmation Modal */}
      <AnimatePresence>
        {showClearHistoryConfirm && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 z-50"
              onClick={() => setShowClearHistoryConfirm(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white dark:bg-gray-800 rounded-xl shadow-2xl z-50 p-6"
            >
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mr-3">
                  <Trash2 className="w-5 h-5 text-red-600 dark:text-red-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Gesamten Verlauf löschen
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                Möchtest du wirklich alle Chat-Unterhaltungen löschen? Diese Aktion kann nicht rückgängig gemacht werden und betrifft alle gespeicherten Chats.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowClearHistoryConfirm(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
                >
                  Abbrechen
                </button>
                <button
                  onClick={confirmClearHistory}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Alle löschen
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}