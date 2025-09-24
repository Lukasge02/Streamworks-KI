'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText, ExternalLink, Eye, Star, Clock, Hash,
  ChevronRight, ChevronDown, Download, Share, Bookmark
} from 'lucide-react'
import { toast } from 'sonner'

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
  file_size?: number
  upload_date?: string
  last_modified?: string
}

interface SourcesDisplayProps {
  sources: SourceReference[]
  onSourceClick?: (source: SourceReference) => void
  maxVisible?: number
  showRelevanceScores?: boolean
  showSnippets?: boolean
  showMetadata?: boolean
  compact?: boolean
  className?: string
}

// Navigation function for documents
const navigateToDocument = async (source: SourceReference): Promise<string> => {
  try {
    const response = await fetch('/api/rag-metrics/navigate-to-source', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        document_id: source.document_id,
        page_number: source.page_number,
        chunk_id: source.chunk_id,
        highlight_text: source.snippet.substring(0, 50)
      })
    })

    if (!response.ok) {
      throw new Error('Failed to generate navigation URL')
    }

    const result = await response.json()
    if (result.success) {
      return result.document_url
    } else {
      throw new Error(result.error || 'Navigation failed')
    }
  } catch (error) {
    console.error('Navigation error:', error)
    // Fallback to basic URL
    return `/documents/${source.document_id}${source.page_number ? `?page=${source.page_number}` : ''}`
  }
}

export const SourcesDisplay: React.FC<SourcesDisplayProps> = ({
  sources,
  onSourceClick,
  maxVisible = 5,
  showRelevanceScores = true,
  showSnippets = true,
  showMetadata = false,
  compact = false,
  className = ''
}) => {
  const [showAll, setShowAll] = useState(false)
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set())

  const visibleSources = showAll ? sources : sources.slice(0, maxVisible)
  const hasMore = sources.length > maxVisible

  const handleSourceClick = async (source: SourceReference) => {
    try {
      if (onSourceClick) {
        onSourceClick(source)
      } else {
        // Default navigation behavior
        const url = await navigateToDocument(source)
        window.open(url, '_blank')
        toast.success(`Öffne Dokument: ${source.filename}`)
      }
    } catch (error) {
      toast.error('Fehler beim Öffnen des Dokuments')
    }
  }

  const toggleExpanded = (sourceId: string) => {
    const newExpanded = new Set(expandedSources)
    if (newExpanded.has(sourceId)) {
      newExpanded.delete(sourceId)
    } else {
      newExpanded.add(sourceId)
    }
    setExpandedSources(newExpanded)
  }

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30'
    if (score >= 0.6) return 'text-amber-600 bg-amber-100 dark:bg-amber-900/30'
    return 'text-red-600 bg-red-100 dark:bg-red-900/30'
  }

  const getFileTypeIcon = (docType?: string, filename?: string) => {
    const ext = docType || filename?.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'pdf':
        return '📄'
      case 'docx':
      case 'doc':
        return '📝'
      case 'xlsx':
      case 'xls':
        return '📊'
      case 'pptx':
      case 'ppt':
        return '📋'
      case 'txt':
        return '📄'
      default:
        return '📄'
    }
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return null
    const kb = bytes / 1024
    const mb = kb / 1024
    if (mb >= 1) return `${mb.toFixed(1)} MB`
    return `${kb.toFixed(1)} KB`
  }

  const SourceCard: React.FC<{ source: SourceReference; index: number }> = ({ source, index }) => {
    const sourceId = `${source.document_id}-${source.chunk_id || index}`
    const isExpanded = expandedSources.has(sourceId)

    return (
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.1 }}
        className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-md transition-all duration-200 ${compact ? 'p-3' : 'p-4'}`}
      >
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3 flex-1 min-w-0">
            {/* File Icon */}
            <div className="flex-shrink-0 text-lg">
              {getFileTypeIcon(source.doc_type, source.filename)}
            </div>

            {/* Main Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {source.filename}
                </h4>
                {showRelevanceScores && (
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRelevanceColor(source.relevance_score)}`}>
                    {Math.round(source.relevance_score * 100)}%
                  </span>
                )}
              </div>

              {/* Metadata */}
              <div className="flex items-center space-x-3 text-xs text-gray-500 dark:text-gray-400 mb-2">
                {source.section && (
                  <span className="flex items-center">
                    <Hash className="w-3 h-3 mr-1" />
                    {source.section}
                  </span>
                )}
                {source.page_number && (
                  <span>Seite {source.page_number}</span>
                )}
                <span>Chunk {source.chunk_index}</span>
              </div>

              {/* Snippet */}
              {showSnippets && (
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  <p className={`${isExpanded ? '' : 'line-clamp-2'}`}>
                    {source.snippet}
                  </p>
                  {source.snippet.length > 100 && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleExpanded(sourceId)
                      }}
                      className="text-blue-600 hover:text-blue-700 dark:text-blue-400 text-xs mt-1 flex items-center"
                    >
                      {isExpanded ? (
                        <>
                          <ChevronDown className="w-3 h-3 mr-1" />
                          Weniger anzeigen
                        </>
                      ) : (
                        <>
                          <ChevronRight className="w-3 h-3 mr-1" />
                          Mehr anzeigen
                        </>
                      )}
                    </button>
                  )}
                </div>
              )}

              {/* Extended Metadata */}
              <AnimatePresence>
                {showMetadata && isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700"
                  >
                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-500 dark:text-gray-400">
                      {source.confidence && (
                        <div>
                          <span className="font-medium">Vertrauen:</span> {Math.round(source.confidence * 100)}%
                        </div>
                      )}
                      {source.file_size && (
                        <div>
                          <span className="font-medium">Größe:</span> {formatFileSize(source.file_size)}
                        </div>
                      )}
                      {source.upload_date && (
                        <div>
                          <span className="font-medium">Hochgeladen:</span> {new Date(source.upload_date).toLocaleDateString('de-DE')}
                        </div>
                      )}
                      {source.last_modified && (
                        <div>
                          <span className="font-medium">Geändert:</span> {new Date(source.last_modified).toLocaleDateString('de-DE')}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-1 ml-2 flex-shrink-0">
            {/* View in context button */}
            <button
              onClick={() => handleSourceClick(source)}
              className="p-1.5 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 rounded transition-colors"
              title="Dokument öffnen"
            >
              <ExternalLink className="w-4 h-4" />
            </button>

            {/* Expand metadata button */}
            {showMetadata && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  toggleExpanded(sourceId)
                }}
                className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
                title="Details anzeigen"
              >
                <Eye className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </motion.div>
    )
  }

  if (!sources || sources.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 dark:text-gray-400 ${className}`}>
        <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Keine Quellen verfügbar</p>
      </div>
    )
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className={`font-medium text-gray-900 dark:text-white flex items-center ${compact ? 'text-sm' : 'text-base'}`}>
          <FileText className={`mr-2 ${compact ? 'w-4 h-4' : 'w-5 h-5'}`} />
          Verwendete Quellen ({sources.length})
        </h3>

        {/* Quick actions */}
        <div className="flex items-center space-x-2">
          {showRelevanceScores && (
            <div className="flex items-center space-x-1 text-xs text-gray-500 dark:text-gray-400">
              <Star className="w-3 h-3" />
              <span>Relevanz</span>
            </div>
          )}
        </div>
      </div>

      {/* Sources List */}
      <div className="space-y-3">
        {visibleSources.map((source, index) => (
          <SourceCard
            key={`${source.document_id}-${source.chunk_id || index}`}
            source={source}
            index={index}
          />
        ))}
      </div>

      {/* Show More/Less Button */}
      {hasMore && (
        <div className="text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors flex items-center mx-auto"
          >
            {showAll ? (
              <>
                <ChevronDown className="w-4 h-4 mr-1" />
                Weniger anzeigen
              </>
            ) : (
              <>
                <ChevronRight className="w-4 h-4 mr-1" />
                {sources.length - maxVisible} weitere Quellen anzeigen
              </>
            )}
          </button>
        </div>
      )}

      {/* Summary */}
      {sources.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 text-sm">
          <div className="flex items-center justify-between text-gray-600 dark:text-gray-400">
            <span>
              Durchschnittliche Relevanz: {Math.round((sources.reduce((sum, s) => sum + s.relevance_score, 0) / sources.length) * 100)}%
            </span>
            <span>
              {sources.filter(s => s.relevance_score >= 0.8).length} hochrelevante Quellen
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default SourcesDisplay