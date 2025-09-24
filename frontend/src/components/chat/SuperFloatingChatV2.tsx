/**
 * Super Floating Chat Widget V2
 * NUCLEAR OPTION - Completely new component name to force reload
 * Enhanced 420x550px version with debug enforcement
 */

'use client'

import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, X, Bot, Plus } from 'lucide-react'
import { CompactChatInterface } from './CompactChatInterface'
import { useChatStore } from '@/stores/chatStore'
import { useChatContext } from './ChatProvider'

interface SuperFloatingChatV2Props {
  className?: string
}

export const SuperFloatingChatV2: React.FC<SuperFloatingChatV2Props> = ({
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [hasUnreadMessages, setHasUnreadMessages] = useState(false)
  const widgetRef = useRef<HTMLDivElement>(null)

  const {
    sessions,
    currentSessionId,
    hasUnreadMessages: storeHasUnreadMessages,
    setHasUnreadMessages: setStoreHasUnreadMessages,
    setFloatingChatOpen
  } = useChatStore()
  const { createNewSession } = useChatContext()

  // Component Mount Tracking
  useEffect(() => {
    console.log('✨ SuperFloatingChatV2 - Premium Version Loaded')
  }, [])

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

  // Use store hasUnreadMessages state instead of local state
  useEffect(() => {
    // Sync local state with store state
    setHasUnreadMessages(storeHasUnreadMessages && !isOpen)
  }, [storeHasUnreadMessages, isOpen])

  const toggleChat = () => {
    const newState = !isOpen
    setIsOpen(newState)

    // Sync with store floating chat state
    setFloatingChatOpen(newState)

    if (newState) {
      // Clear unread messages when opening chat
      setHasUnreadMessages(false)
      setStoreHasUnreadMessages(false)
    }
  }

  const handleNewChat = async () => {
    try {
      await createNewSession('Neuer Chat')
      // Optional: Show success toast here
    } catch (error) {
      console.error('Failed to create new chat:', error)
    }
  }

  return (
    <div ref={widgetRef} className={`fixed bottom-6 right-6 z-50 ${className}`}>
      <AnimatePresence mode="wait">
        {isOpen ? (
          // Expanded Chat Interface - Premium Design
          <motion.div
            key="super-chat-expanded"
            initial={{ opacity: 0, scale: 0.95, y: 30 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 30 }}
            transition={{
              duration: 0.3,
              ease: [0.4, 0.0, 0.2, 1],
              type: "spring",
              stiffness: 300,
              damping: 30
            }}
            className="relative bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 dark:border-gray-700/50 overflow-hidden"
            style={{
              width: '480px',
              height: '650px',
              background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.95) 100%)',
              backdropFilter: 'blur(20px)',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.2)'
            }}
          >
            {/* Premium Header with Glassmorphism */}
            <div className="relative">
              {/* Background Gradient */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-blue-800 opacity-90"></div>
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent backdrop-blur-sm"></div>

              {/* Header Content */}
              <div className="relative p-4 text-white">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {/* Animated AI Avatar */}
                    <motion.div
                      className="w-9 h-9 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/30"
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      <Bot className="w-5 h-5 text-white" />
                    </motion.div>
                    <div>
                      <h3 className="font-bold text-base tracking-tight">SKI</h3>
                      <p className="text-xs text-white/80 font-medium">Dein intelligenter Assistent</p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-2">
                    {/* New Chat Button */}
                    <motion.button
                      onClick={handleNewChat}
                      className="group flex items-center space-x-1 px-3 py-2 hover:bg-white/20 rounded-xl transition-all duration-200 border border-white/20 hover:border-white/40 backdrop-blur-sm"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      title="Neuer Chat"
                    >
                      <Plus className="w-4 h-4 text-white group-hover:rotate-90 transition-transform duration-200" />
                      <span className="text-xs font-medium text-white/90">Neuer Chat</span>
                    </motion.button>

                    {/* Close Button */}
                    <motion.button
                      onClick={() => setIsOpen(false)}
                      className="group p-2 hover:bg-red-500/20 rounded-xl transition-all duration-200 border border-white/20 hover:border-red-400/50 backdrop-blur-sm"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      title="Schließen"
                    >
                      <X className="w-4 h-4 text-white group-hover:text-red-200 transition-colors duration-200" />
                    </motion.button>
                  </div>
                </div>
              </div>
            </div>

            {/* Chat Content with Perfect Integration */}
            <div className="flex-1 overflow-hidden">
              <CompactChatInterface
                onClose={() => setIsOpen(false)}
                containerHeight="calc(650px - 80px)"
              />
            </div>
          </motion.div>
        ) : (
          // Premium Floating Button
          <motion.button
            key="super-chat-minimized"
            initial={{ opacity: 0, scale: 0.5, rotate: -180 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            exit={{ opacity: 0, scale: 0.5, rotate: 180 }}
            whileHover={{
              scale: 1.1,
              boxShadow: "0 20px 40px -8px rgba(59, 130, 246, 0.5)"
            }}
            whileTap={{ scale: 0.9 }}
            onClick={toggleChat}
            className="relative w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 text-white rounded-2xl shadow-2xl flex items-center justify-center transition-all duration-300 group border-2 border-white/20 backdrop-blur-sm"
            style={{
              background: 'linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)',
              boxShadow: '0 20px 40px -8px rgba(59, 130, 246, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1)'
            }}
            title="Streamworks AI Chat öffnen"
          >
            <MessageCircle className="w-7 h-7 group-hover:scale-110 transition-all duration-200 drop-shadow-lg" />

            {/* Notification Badge */}
            <AnimatePresence>
              {hasUnreadMessages && (
                <motion.div
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0 }}
                  className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
                >
                  !!
                </motion.div>
              )}
            </AnimatePresence>

          </motion.button>
        )}
      </AnimatePresence>
    </div>
  )
}

export default SuperFloatingChatV2