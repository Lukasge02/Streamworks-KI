/**
 * Floating Chat Widget
 * Persistent chat assistant available on all pages
 * Minimizes to floating button, expands to compact chat interface
 */

'use client'

import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, X, Minimize2, Maximize2, Bot, Plus } from 'lucide-react'
import { CompactChatInterface } from './CompactChatInterface'
import { useChatStore } from '@/stores/chatStore'
import { useChatContext } from './ChatProvider'

interface FloatingChatWidgetProps {
  className?: string
}

export const FloatingChatWidget: React.FC<FloatingChatWidgetProps> = ({
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [hasUnreadMessages, setHasUnreadMessages] = useState(false)
  const widgetRef = useRef<HTMLDivElement>(null)

  const { sessions, currentSessionId } = useChatStore()
  const { createNewSession } = useChatContext()

  // Handle click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (widgetRef.current && !widgetRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  // Handle escape key to close
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        setIsOpen(false)
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen])

  // Mock unread messages logic (you can enhance this)
  useEffect(() => {
    // Simple logic: show badge if there are sessions but widget is closed
    setHasUnreadMessages(sessions.length > 0 && !isOpen)
  }, [sessions.length, isOpen])

  const toggleChat = () => {
    setIsOpen(!isOpen)
    if (!isOpen) {
      setHasUnreadMessages(false)
    }
  }

  const handleNewChat = async () => {
    try {
      await createNewSession('Floating Chat')
    } catch (error) {
      console.error('Failed to create new chat:', error)
    }
  }

  return (
    <div ref={widgetRef} className={`fixed bottom-6 right-6 z-50 ${className}`}>
      <AnimatePresence mode="wait">
        {isOpen ? (
          // Expanded Chat Interface
          <motion.div
            key="chat-expanded"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden"
            style={{ width: '420px', height: '550px' }}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-3 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-7 h-7 bg-white/20 rounded-lg flex items-center justify-center">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">StreamWorks Assistant</h3>
                    <p className="text-xs text-blue-100">Immer für Sie da</p>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={handleNewChat}
                    className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                    title="Neuer Chat"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                    title="Minimieren"
                  >
                    <Minimize2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                    title="Schließen"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Chat Content */}
            <div className="h-full">
              <CompactChatInterface
                onClose={() => setIsOpen(false)}
                containerHeight="calc(550px - 54px)"
              />
            </div>
          </motion.div>
        ) : (
          // Minimized Floating Button
          <motion.button
            key="chat-minimized"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={toggleChat}
            className="relative w-14 h-14 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-full shadow-2xl flex items-center justify-center transition-all duration-200 group"
            title="Chat öffnen"
          >
            <MessageCircle className="w-6 h-6 group-hover:scale-110 transition-transform" />

            {/* Notification Badge */}
            <AnimatePresence>
              {hasUnreadMessages && (
                <motion.div
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0 }}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
                >
                  !
                </motion.div>
              )}
            </AnimatePresence>

            {/* Pulse Effect */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 animate-ping opacity-20"></div>
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  )
}

export default FloatingChatWidget