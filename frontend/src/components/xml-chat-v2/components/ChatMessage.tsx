/**
 * Chat Message Component
 * Clean, accessible message display with actions
 */

import React from 'react'
import { motion } from 'framer-motion'
import {
  User,
  Bot,
  Info,
  Sparkles,
  Copy,
  Check,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { toast } from 'sonner'

import { ChatMessageProps } from '../types'

export default function ChatMessage({
  message,
  onGenerateXML,
  isGeneratingXML = false
}: ChatMessageProps) {
  const [copied, setCopied] = React.useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      toast.success('Message copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      toast.error('Failed to copy message')
    }
  }

  const getMessageIcon = () => {
    switch (message.role) {
      case 'user':
        return <User className="w-4 h-4" />
      case 'assistant':
        return <Bot className="w-4 h-4" />
      case 'system':
        return <Info className="w-4 h-4" />
      default:
        return null
    }
  }

  const getMessageBgColor = () => {
    switch (message.role) {
      case 'user':
        return 'bg-blue-600'
      case 'assistant':
        return 'bg-gray-700'
      case 'system':
        return 'bg-green-600'
      default:
        return 'bg-gray-500'
    }
  }

  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`group flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`
        w-8 h-8 rounded-full flex items-center justify-center text-white flex-shrink-0
        ${getMessageBgColor()}
        ${isSystem ? 'bg-opacity-80' : ''}
      `}>
        {getMessageIcon()}
      </div>

      {/* Message Content */}
      <div className={`
        flex-1 max-w-2xl
        ${isUser ? 'flex flex-col items-end' : 'flex flex-col items-start'}
      `}>
        {/* Message Bubble */}
        <div className={`
          px-4 py-3 rounded-2xl relative group/message
          ${isUser
            ? 'bg-blue-600 text-white ml-8'
            : isSystem
              ? 'bg-green-50 border border-green-200 text-green-800 mr-8'
              : 'bg-white border border-gray-200 text-gray-900 mr-8'
          }
          ${!isUser && !isSystem ? 'shadow-sm' : ''}
        `}>
          {/* Message Text */}
          <div className="prose prose-sm max-w-none">
            {message.content.split('\n').map((line, index) => (
              <p key={index} className={`
                ${index === 0 ? 'mt-0' : 'mt-2'}
                ${line.trim() === '' ? 'h-2' : ''}
                ${isUser ? 'text-white' : isSystem ? 'text-green-800' : 'text-gray-900'}
              `}>
                {line}
              </p>
            ))}
          </div>

          {/* Generate XML Button */}
          {!isUser && !isSystem && message.metadata?.canGenerateXML && onGenerateXML && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <button
                onClick={onGenerateXML}
                disabled={isGeneratingXML}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-medium rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGeneratingXML ? (
                  <>
                    <Loader2 className="w-3 h-3 animate-spin" />
                    Generating XML...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3 h-3" />
                    Generate XML
                  </>
                )}
              </button>
            </div>
          )}

          {/* System Message Type Indicator */}
          {isSystem && message.metadata?.type === 'xml_generated' && (
            <div className="mt-2 flex items-center gap-2 text-green-700">
              <Sparkles className="w-3 h-3" />
              <span className="text-xs font-medium">XML Generated</span>
            </div>
          )}
        </div>

        {/* Message Actions */}
        <div className="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="p-1 rounded text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            title="Copy message"
          >
            {copied ? (
              <Check className="w-3 h-3 text-green-600" />
            ) : (
              <Copy className="w-3 h-3" />
            )}
          </button>

          {/* Timestamp */}
          <span className="text-xs text-gray-400">
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
        </div>
      </div>
    </motion.div>
  )
}

// ================================
// SYSTEM MESSAGE VARIANTS
// ================================

export function SystemErrorMessage({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-3 px-4 py-3 bg-red-50 border border-red-200 rounded-lg">
      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
      <div className="text-sm text-red-800">{message}</div>
    </div>
  )
}

export function SystemSuccessMessage({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-3 px-4 py-3 bg-green-50 border border-green-200 rounded-lg">
      <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
      <div className="text-sm text-green-800">{message}</div>
    </div>
  )
}