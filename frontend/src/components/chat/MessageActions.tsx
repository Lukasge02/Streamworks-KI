'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Copy, ThumbsUp, ThumbsDown, Share2, Download, CheckCircle, X } from 'lucide-react'

interface MessageActionsProps {
  message: {
    id: string
    type: 'user' | 'assistant'
    content: string
    sources?: Array<any>
    confidence_score?: number
    processing_time?: string
  }
  onCopy?: (content: string) => void
  onFeedback?: (messageId: string, feedback: 'positive' | 'negative') => void
  onExport?: (message: any) => void
}

export const MessageActions: React.FC<MessageActionsProps> = ({
  message,
  onCopy,
  onFeedback,
  onExport
}) => {
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(null)
  const [showExportMenu, setShowExportMenu] = useState(false)

  const handleCopy = async () => {
    if (onCopy) {
      onCopy(message.content)
    } else {
      await navigator.clipboard.writeText(message.content)
    }
    
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleFeedback = (type: 'positive' | 'negative') => {
    setFeedback(type)
    onFeedback?.(message.id, type)
  }

  const handleExport = (format: 'text' | 'markdown' | 'json') => {
    if (onExport) {
      onExport({ ...message, exportFormat: format })
    } else {
      // Default export behavior
      const exportData = {
        content: message.content,
        sources: message.sources,
        confidence_score: message.confidence_score,
        processing_time: message.processing_time,
        timestamp: new Date().toISOString()
      }

      let exportContent = ''
      let filename = `streamworks-response-${Date.now()}`

      switch (format) {
        case 'text':
          exportContent = message.content
          filename += '.txt'
          break
        case 'markdown':
          exportContent = `# Streamworks AI Response\n\n${message.content}`
          if (message.sources && message.sources.length > 0) {
            exportContent += '\n\n## Quellen\n'
            message.sources.forEach((source, index) => {
              exportContent += `${index + 1}. ${source.metadata?.original_filename || source.id}\n`
            })
          }
          filename += '.md'
          break
        case 'json':
          exportContent = JSON.stringify(exportData, null, 2)
          filename += '.json'
          break
      }

      const blob = new Blob([exportContent], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    }
    
    setShowExportMenu(false)
  }

  if (message.type !== 'assistant') return null

  return (
    <div className="flex items-center space-x-1 mt-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
      {/* Copy Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleCopy}
        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 relative"
        title="Antwort kopieren"
      >
        {copied ? (
          <CheckCircle className="w-4 h-4 text-green-500" />
        ) : (
          <Copy className="w-4 h-4" />
        )}
        
        {copied && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap"
          >
            Kopiert!
          </motion.div>
        )}
      </motion.button>

      {/* Thumbs Up */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => handleFeedback('positive')}
        className={`p-2 rounded-lg transition-all duration-200 ${
          feedback === 'positive'
            ? 'text-green-600 bg-green-100 dark:bg-green-900/30'
            : 'text-gray-400 hover:text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20'
        }`}
        title="Hilfreiche Antwort"
      >
        <ThumbsUp className="w-4 h-4" />
      </motion.button>

      {/* Thumbs Down */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => handleFeedback('negative')}
        className={`p-2 rounded-lg transition-all duration-200 ${
          feedback === 'negative'
            ? 'text-red-600 bg-red-100 dark:bg-red-900/30'
            : 'text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20'
        }`}
        title="Nicht hilfreiche Antwort"
      >
        <ThumbsDown className="w-4 h-4" />
      </motion.button>

      {/* Export Menu */}
      <div className="relative">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowExportMenu(!showExportMenu)}
          className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200"
          title="Exportieren"
        >
          <Download className="w-4 h-4" />
        </motion.button>

        {showExportMenu && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            className="absolute bottom-full mb-2 right-0 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50 min-w-[120px]"
          >
            <button
              onClick={() => handleExport('text')}
              className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              Als Text (.txt)
            </button>
            <button
              onClick={() => handleExport('markdown')}
              className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              Als Markdown (.md)
            </button>
            <button
              onClick={() => handleExport('json')}
              className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              Als JSON (.json)
            </button>
          </motion.div>
        )}

        {/* Overlay to close menu */}
        {showExportMenu && (
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowExportMenu(false)}
          />
        )}
      </div>

      {/* Share Button (Enterprise Feature) */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 opacity-50 cursor-not-allowed"
        title="Teilen (Coming Soon)"
        disabled
      >
        <Share2 className="w-4 h-4" />
      </motion.button>
    </div>
  )
}