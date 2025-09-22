'use client'

import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { CheckCircle, AlertTriangle, Info, Copy, ExternalLink } from 'lucide-react'
import { motion } from 'framer-motion'
import { ConfidenceIndicator } from '../ui/StatusIndicator'
import { RAGMetrics } from './RAGMetrics'

interface EnterpriseResponseProps {
  content: string
  confidence_score?: number
  sources?: Array<{
    id: string
    metadata: {
      doc_id?: string
      original_filename?: string
      page_number?: number
      heading?: string
      section?: string
    }
    relevance_score?: number
  }>
  processing_time?: string
  model_info?: string
  retrieval_context?: {
    total_chunks?: number
    relevant_chunks?: number
    query_type?: string
    mode?: string
  }
  onCopyResponse?: (content: string) => void
  onSourceClick?: (source: any) => void
  compact?: boolean
}

export const EnterpriseResponseFormatter: React.FC<EnterpriseResponseProps> = ({
  content,
  confidence_score,
  sources = [],
  processing_time,
  model_info,
  retrieval_context,
  onCopyResponse,
  onSourceClick,
  compact = false
}) => {
  const [showMetrics, setShowMetrics] = useState(false)
  const getConfidenceColor = (score?: number) => {
    if (!score) return 'text-gray-500'
    if (score >= 0.8) return 'text-emerald-600'
    if (score >= 0.6) return 'text-amber-600'
    return 'text-red-600'
  }

  const getConfidenceIcon = (score?: number) => {
    if (!score) return Info
    if (score >= 0.8) return CheckCircle
    if (score >= 0.6) return AlertTriangle
    return AlertTriangle
  }

  const ConfidenceIcon = getConfidenceIcon(confidence_score)

  return (
    <div className="space-y-4">
      {/* Response Header with Confidence & Timing */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          {confidence_score && (
            <ConfidenceIndicator score={confidence_score} />
          )}
          {processing_time && (
            <div className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-full">
              {processing_time}
            </div>
          )}
          {model_info && (
            <div className="text-xs text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded-full">
              {model_info}
            </div>
          )}
        </div>
      </div>

      {/* Enhanced RAG Metrics Panel */}
      {(confidence_score || processing_time || sources.length > 0) && (
        <RAGMetrics
          confidence_score={confidence_score}
          processing_time={processing_time}
          model_info={model_info}
          sources={sources}
          retrieval_context={retrieval_context}
          expanded={showMetrics}
          onToggleExpand={() => setShowMetrics(!showMetrics)}
        />
      )}

      {/* Formatted Response Content */}
      <div className="prose prose-sm max-w-none dark:prose-invert">
        <ReactMarkdown
          components={{
            // Enhanced typography
            h1: ({ children }) => (
              <h1 className="text-lg font-bold text-gray-900 dark:text-white mb-3 mt-6 first:mt-0 border-b border-gray-200 dark:border-gray-700 pb-2">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-base font-semibold text-gray-800 dark:text-gray-100 mb-2 mt-5 first:mt-0">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2 mt-4 first:mt-0">
                {children}
              </h3>
            ),
            
            // Enhanced lists
            ul: ({ children }) => (
              <ul className="space-y-1 my-3">
                {children}
              </ul>
            ),
            ol: ({ children }) => (
              <ol className="space-y-1 my-3">
                {children}
              </ol>
            ),
            li: ({ children }) => (
              <li className="text-gray-700 dark:text-gray-300 leading-relaxed flex items-start">
                <span className="w-1 h-1 rounded-full bg-primary-500 mt-2 mr-3 flex-shrink-0"></span>
                <span>{children}</span>
              </li>
            ),
            
            // Enhanced paragraphs
            p: ({ children }) => (
              <p className="mb-3 last:mb-0 text-gray-700 dark:text-gray-300 leading-relaxed">
                {children}
              </p>
            ),
            
            // Code blocks with enhanced chart/visualization support
            code: ({ children, className }) => {
              const isBlock = className?.includes('language-')
              const content = String(children).trim()

              // Detect chart/visualization content
              const isChartContent =
                content.includes('█') || // Block characters
                content.includes('▄') || // Half block characters
                content.includes('▀') || // Upper half block
                content.includes('│') || // Box drawing characters
                content.includes('┌') || content.includes('└') ||
                content.includes('├') || content.includes('┤') ||
                /^\s*[▁▂▃▄▅▆▇█]{2,}/.test(content) || // Bar chart pattern
                /^\s*\|[\s\-=│█▄▀]*\|/.test(content) // Table/chart with bars

              if (isBlock) {
                if (isChartContent) {
                  return (
                    <div className="my-4 chart-visualization-container">
                      <code className="block bg-white dark:bg-gray-50 text-gray-900 dark:text-gray-800 rounded-lg p-6 text-sm font-mono leading-relaxed overflow-x-auto border-2 border-blue-200 dark:border-blue-300 shadow-sm">
                        {children}
                      </code>
                    </div>
                  )
                }
                return (
                  <code className="block bg-gray-100 dark:bg-gray-800 rounded-lg p-4 text-sm overflow-x-auto border border-gray-200 dark:border-gray-700">
                    {children}
                  </code>
                )
              }

              // Inline code - check for small chart elements
              if (isChartContent) {
                return (
                  <code className="bg-white dark:bg-gray-50 text-gray-900 dark:text-gray-800 px-2 py-1 rounded text-sm border border-blue-200 dark:border-blue-300 font-mono">
                    {children}
                  </code>
                )
              }

              return (
                <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm border border-gray-200 dark:border-gray-700">
                  {children}
                </code>
              )
            },

            // Pre elements with chart detection
            pre: ({ children }) => {
              const content = String(children).trim()

              // Detect chart/visualization content in pre blocks
              const isChartContent =
                content.includes('█') || // Block characters
                content.includes('▄') || // Half block characters
                content.includes('▀') || // Upper half block
                content.includes('│') || // Box drawing characters
                content.includes('┌') || content.includes('└') ||
                content.includes('├') || content.includes('┤') ||
                /^\s*[▁▂▃▄▅▆▇█]{2,}/.test(content) || // Bar chart pattern
                /^\s*\|[\s\-=│█▄▀]*\|/.test(content) // Table/chart with bars

              if (isChartContent) {
                return (
                  <div className="my-4 chart-visualization-container">
                    <pre className="bg-white dark:bg-gray-50 text-gray-900 dark:text-gray-800 rounded-lg p-6 text-sm font-mono leading-relaxed overflow-x-auto border-2 border-blue-200 dark:border-blue-300 shadow-sm whitespace-pre">
                      {children}
                    </pre>
                  </div>
                )
              }

              return (
                <pre className="bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg p-4 text-sm overflow-x-auto border border-gray-200 dark:border-gray-700 whitespace-pre">
                  {children}
                </pre>
              )
            },

            // Blockquotes
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-primary-500 pl-4 py-2 my-4 bg-primary-50 dark:bg-primary-900/20 rounded-r-lg">
                <div className="text-gray-700 dark:text-gray-300 italic">
                  {children}
                </div>
              </blockquote>
            ),

            // Tables
            table: ({ children }) => (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                  {children}
                </table>
              </div>
            ),
            thead: ({ children }) => (
              <thead className="bg-gray-50 dark:bg-gray-800">
                {children}
              </thead>
            ),
            th: ({ children }) => (
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-200 dark:border-gray-700">
                {children}
              </th>
            ),
            td: ({ children }) => (
              <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-700">
                {children}
              </td>
            )
          }}
        >
          {content}
        </ReactMarkdown>
      </div>

      {/* Enhanced Source References - DISABLED
      {sources.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-6 card-enterprise-elevated bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-800 dark:via-gray-800 dark:to-gray-700 p-5 border-blue-100 dark:border-gray-600"
        >
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 flex items-center">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-6a1 1 0 00-1-1H9a1 1 0 00-1 1v6a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
              </svg>
              Quellen ({sources.length})
            </h4>
            <div className="text-xs text-blue-700 dark:text-blue-300">
              Klicken zum Öffnen
            </div>
          </div>

          <div className="grid gap-3">
            {sources.slice(0, 5).map((source, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
                className="source-card-enterprise border-blue-200 dark:border-gray-600"
                onClick={() => onSourceClick?.(source)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center mb-2">
                      <span className="badge-enterprise-info mr-3 flex-shrink-0">
                        #{index + 1}
                      </span>
                      <h5 className="source-card-title text-sm">
                        {source.metadata.original_filename || source.metadata.doc_id || `Dokument ${source.id}`}
                      </h5>
                      <ExternalLink className="w-3 h-3 text-gray-400 ml-2 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                    </div>

                    <div className="source-card-meta">
                      {source.metadata.page_number && (
                        <span className="flex items-center">
                          📄 Seite {source.metadata.page_number}
                        </span>
                      )}
                      {source.metadata.heading && (
                        <span className="flex items-center truncate">
                          📑 {source.metadata.heading}
                        </span>
                      )}
                    </div>

                    {source.metadata.section && (
                      <p className="source-card-preview mt-2">
                        "{source.metadata.section}"
                      </p>
                    )}
                  </div>

                  {source.relevance_score !== undefined && (
                    <div className="ml-4 flex-shrink-0">
                      <span className="source-card-score">
                        {Math.round((1 - source.relevance_score) * 100)}%
                      </span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}

            {sources.length > 5 && (
              <div className="text-center pt-2">
                <button className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors">
                  +{sources.length - 5} weitere Quellen anzeigen
                </button>
              </div>
            )}
          </div>
        </motion.div>
      )}
      */}
    </div>
  )
}