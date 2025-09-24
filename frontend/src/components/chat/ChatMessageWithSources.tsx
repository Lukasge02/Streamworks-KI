'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare, User, Bot, Clock, Target, Zap,
  ChevronDown, ChevronUp, ExternalLink, Share2
} from 'lucide-react'
import { EnhancedRAGMetrics } from './EnhancedRAGMetrics'
import { SourcesDisplay } from './SourcesDisplay'
import { useDocumentNavigation } from '../../hooks/useDocumentNavigation'

// Types
interface SourceReference {
  document_id: string
  filename: string
  page_number?: number
  section?: string
  relevance_score: number
  snippet: string
  chunk_index: number
  confidence: number
  doc_type?: string
  chunk_id?: string
}

interface RAGMetrics {
  response_time_ms: number
  source_retrieval_time_ms: number
  llm_generation_time_ms: number
  cache_hit: boolean
  total_chunks_searched: number
  relevant_chunks_found: number
  query_complexity: string
  retrieval_method: string
}

interface ChatMessageWithSourcesProps {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  sources?: SourceReference[]
  metrics?: RAGMetrics
  confidence_score?: number
  timestamp: string
  isStreaming?: boolean
  showSources?: boolean
  showMetrics?: boolean
  className?: string
}

export const ChatMessageWithSources: React.FC<ChatMessageWithSourcesProps> = ({
  id,
  role,
  content,
  sources = [],
  metrics,
  confidence_score,
  timestamp,
  isStreaming = false,
  showSources = true,
  showMetrics = true,
  className = ''
}) => {
  const [showSourcesExpanded, setShowSourcesExpanded] = useState(false)
  const [showMetricsExpanded, setShowMetricsExpanded] = useState(false)
  const { navigateToSource, isNavigating } = useDocumentNavigation()

  const handleSourceClick = async (source: SourceReference) => {
    await navigateToSource(source, {
      openInNewTab: true,
      focusChunk: true,
      showContext: true
    })
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getConfidenceColor = (score?: number) => {
    if (!score) return 'text-gray-500'
    if (score >= 0.8) return 'text-emerald-600'
    if (score >= 0.6) return 'text-amber-600'
    return 'text-red-600'
  }

  const getPerformanceStatus = (metrics?: RAGMetrics) => {
    if (!metrics) return 'unknown'
    if (metrics.response_time_ms < 1000) return 'excellent'
    if (metrics.response_time_ms < 2000) return 'good'
    if (metrics.response_time_ms < 5000) return 'acceptable'
    return 'poor'
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex space-x-3 ${className}`}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          role === 'user'
            ? 'bg-blue-500 text-white'
            : role === 'assistant'
            ? 'bg-emerald-500 text-white'
            : 'bg-gray-500 text-white'
        }`}>
          {role === 'user' ? (
            <User className="w-4 h-4" />
          ) : role === 'assistant' ? (
            <Bot className="w-4 h-4" />
          ) : (
            <MessageSquare className="w-4 h-4" />
          )}
        </div>
      </div>

      {/* Message Content */}
      <div className="flex-1 space-y-3">
        {/* Message Header */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-900 dark:text-white">
            {role === 'user' ? 'Du' : role === 'assistant' ? 'Streamworks AI' : 'System'}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
            <Clock className="w-3 h-3 mr-1" />
            {formatTimestamp(timestamp)}
          </span>
          {confidence_score && (
            <span className={`text-xs font-medium ${getConfidenceColor(confidence_score)}`}>
              <Target className="w-3 h-3 inline mr-1" />
              {Math.round(confidence_score * 100)}% Vertrauen
            </span>
          )}
          {metrics && (
            <span className={`text-xs font-medium ${
              getPerformanceStatus(metrics) === 'excellent' ? 'text-emerald-600' :
              getPerformanceStatus(metrics) === 'good' ? 'text-green-600' :
              getPerformanceStatus(metrics) === 'acceptable' ? 'text-amber-600' : 'text-red-600'
            }`}>
              <Zap className="w-3 h-3 inline mr-1" />
              {Math.round(metrics.response_time_ms)}ms
            </span>
          )}
        </div>

        {/* Message Text */}
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <div className="text-gray-900 dark:text-white whitespace-pre-wrap">
            {content}
            {isStreaming && (
              <motion.span
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.8, repeat: Infinity }}
                className="inline-block w-2 h-4 bg-blue-500 ml-1"
              />
            )}
          </div>
        </div>

        {/* Sources Section */}
        {role === 'assistant' && showSources && sources.length > 0 && (
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium text-gray-900 dark:text-white flex items-center">
                📚 Verwendete Quellen ({sources.length})
              </h4>
              <button
                onClick={() => setShowSourcesExpanded(!showSourcesExpanded)}
                className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 flex items-center"
              >
                {showSourcesExpanded ? (
                  <>
                    <ChevronUp className="w-3 h-3 mr-1" />
                    Weniger
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3 mr-1" />
                    Details
                  </>
                )}
              </button>
            </div>

            {/* Quick Sources Summary */}
            {!showSourcesExpanded && (
              <div className="space-y-2">
                {sources.slice(0, 3).map((source, index) => (
                  <div
                    key={`${source.document_id}-${index}`}
                    className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700 cursor-pointer hover:shadow-sm transition-shadow"
                    onClick={() => handleSourceClick(source)}
                  >
                    <div className="flex items-center space-x-2 flex-1 min-w-0">
                      <span className="text-sm">📄</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {source.filename}
                      </span>
                      {source.page_number && (
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          S. {source.page_number}
                        </span>
                      )}
                      <span className="text-xs text-emerald-600 dark:text-emerald-400">
                        {Math.round(source.relevance_score * 100)}%
                      </span>
                    </div>
                    <ExternalLink className="w-3 h-3 text-gray-400" />
                  </div>
                ))}
                {sources.length > 3 && (
                  <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                    +{sources.length - 3} weitere Quellen
                  </div>
                )}
              </div>
            )}

            {/* Detailed Sources */}
            <AnimatePresence>
              {showSourcesExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <SourcesDisplay
                    sources={sources}
                    onSourceClick={handleSourceClick}
                    showRelevanceScores={true}
                    showSnippets={true}
                    showMetadata={true}
                    compact={true}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Performance Metrics */}
        {role === 'assistant' && showMetrics && (metrics || sources.length > 0) && (
          <div className="mt-3">
            <EnhancedRAGMetrics
              sources={sources}
              expanded={showMetricsExpanded}
              onToggleExpand={() => setShowMetricsExpanded(!showMetricsExpanded)}
              showSources={false} // Sources are handled separately above
              onSourceClick={handleSourceClick}
            />
          </div>
        )}

        {/* Message Actions */}
        <div className="flex items-center space-x-2 pt-2">
          {role === 'assistant' && (
            <>
              <button
                className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 flex items-center"
                onClick={() => {
                  navigator.clipboard.writeText(content)
                  // Could add toast notification here
                }}
              >
                <Share2 className="w-3 h-3 mr-1" />
                Kopieren
              </button>

              {sources.length > 0 && (
                <button
                  className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 flex items-center"
                  onClick={() => setShowSourcesExpanded(!showSourcesExpanded)}
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  Quellen ({sources.length})
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default ChatMessageWithSources