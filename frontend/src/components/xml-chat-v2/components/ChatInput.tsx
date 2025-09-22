/**
 * Chat Input Component
 * Modern, auto-resizing input with keyboard shortcuts
 */

import React, { forwardRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'

import { ChatInputProps, CHAT_LIMITS } from '../types'

const ChatInput = forwardRef<HTMLTextAreaElement, ChatInputProps>(({
  value,
  onChange,
  onSend,
  onKeyDown,
  disabled = false,
  placeholder = "Type your message..."
}, ref) => {
  const [rows, setRows] = React.useState(1)
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)

  // Merge refs
  React.useImperativeHandle(ref, () => textareaRef.current!)

  // Fixed height to prevent any layout shifts
  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    // Always maintain fixed height to prevent ANY shifting
    const fixedHeight = 44
    textarea.style.height = `${fixedHeight}px`
    textarea.style.overflowY = value.split('\n').length > 1 || textarea.scrollHeight > fixedHeight ? 'auto' : 'hidden'
  }, [value])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (onKeyDown) {
      onKeyDown(e)
    }

    // Handle Enter key
    if (e.key === 'Enter' && !e.shiftKey && !(e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      if (!disabled && value.trim()) {
        onSend()
      }
    }
  }

  const canSend = !disabled && value.trim().length > 0 && value.length <= CHAT_LIMITS.MAX_MESSAGE_LENGTH
  const isAtLimit = value.length >= CHAT_LIMITS.MAX_MESSAGE_LENGTH

  return (
    <div className="relative">
      {/* Input Container */}
      <div className={`
        relative bg-white border rounded-2xl transition-all
        ${disabled ? 'border-gray-200' : 'border-gray-300 focus-within:border-blue-500'}
        ${isAtLimit ? 'border-red-300 focus-within:border-red-500' : ''}
      `}>
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          className={`
            w-full px-4 py-3 pr-12 resize-none border-0 outline-none rounded-2xl
            placeholder-gray-400 text-gray-900 overflow-hidden
            ${disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-transparent'}
          `}
          style={{
            height: '44px', // Fixed height - no resizing
            minHeight: '44px',
            maxHeight: '44px',
            lineHeight: '20px',
            resize: 'none' // Disable manual resize
          }}
        />

        {/* Send Button */}
        <button
          onClick={onSend}
          disabled={!canSend}
          className={`
            absolute right-2 bottom-2 w-8 h-8 rounded-lg flex items-center justify-center transition-all
            ${canSend
              ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }
          `}
          title={disabled ? 'Please wait...' : 'Send message (Enter)'}
        >
          {disabled ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Character Counter */}
      {value.length > CHAT_LIMITS.MAX_MESSAGE_LENGTH * 0.8 && (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className={`
            absolute right-14 bottom-2 px-2 py-1 text-xs rounded
            ${isAtLimit
              ? 'bg-red-100 text-red-700'
              : 'bg-gray-100 text-gray-600'
            }
          `}
        >
          {CHAT_LIMITS.MAX_MESSAGE_LENGTH - value.length}
        </motion.div>
      )}

    </div>
  )
})

ChatInput.displayName = 'ChatInput'

export default ChatInput

// ================================
// QUICK PROMPTS
// ================================

const QUICK_PROMPTS = [
  {
    emoji: '⚡',
    label: 'Data Job',
    text: 'Create a job definition XML for data processing'
  },
  {
    emoji: '🔗',
    label: 'SAP Interface',
    text: 'Generate XML for SAP interface configuration'
  },
  {
    emoji: '📁',
    label: 'File Transfer',
    text: 'Set up XML for file transfer job'
  },
  {
    emoji: '🛠️',
    label: 'Custom Config',
    text: 'Help me create a custom XML configuration'
  }
]