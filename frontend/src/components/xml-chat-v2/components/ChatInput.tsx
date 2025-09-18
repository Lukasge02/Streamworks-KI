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

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto'
    const scrollHeight = textarea.scrollHeight

    // Calculate number of rows (assuming 24px line height)
    const lineHeight = 24
    const newRows = Math.min(Math.max(Math.ceil(scrollHeight / lineHeight), 1), 6)

    setRows(newRows)
    textarea.style.height = `${newRows * lineHeight}px`
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
        ${disabled ? 'border-gray-200' : 'border-gray-300 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10'}
        ${isAtLimit ? 'border-red-300 focus-within:border-red-500 focus-within:ring-red-500/10' : ''}
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
            placeholder-gray-400 text-gray-900
            ${disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-transparent'}
          `}
          style={{
            minHeight: '24px',
            maxHeight: '144px' // 6 lines
          }}
          rows={rows}
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

      {/* Quick Actions */}
      {value.length === 0 && !disabled && (
        <div className="mt-3 flex flex-wrap gap-2">
          {QUICK_PROMPTS.map((prompt) => (
            <button
              key={prompt.text}
              onClick={() => onChange(prompt.text)}
              className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              {prompt.emoji} {prompt.label}
            </button>
          ))}
        </div>
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