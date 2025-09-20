/**
 * DocumentViewerModal Component
 * Large modal for viewing documents with chunks, metadata, and navigation
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import { 
  XMarkIcon, 
  ChevronLeftIcon, 
  ChevronRightIcon,
  DocumentTextIcon,
  ClockIcon,
  ScaleIcon,
  CalendarDaysIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import { Modal } from '@/components/ui/modal'
import { DocumentWithFolder, DocumentChunk } from '@/types/api.types'
import { apiService } from '@/services/api.service'
import { useDocuments } from '@/hooks/useDocuments'
import { formatUploadDate, formatProcessingDate } from '@/lib/translations'
import { cn } from '@/lib/utils'
import dynamic from 'next/dynamic'

// Dynamic imports for components that require DOM APIs
const Panel = dynamic(() => import('react-resizable-panels').then(mod => ({ default: mod.Panel })), { ssr: false })
const PanelGroup = dynamic(() => import('react-resizable-panels').then(mod => ({ default: mod.PanelGroup })), { ssr: false })
const PanelResizeHandle = dynamic(() => import('react-resizable-panels').then(mod => ({ default: mod.PanelResizeHandle })), { ssr: false })

// Simple PDF viewer - completely client-side
const SimplePDFViewer = dynamic(
  () => import('./SimplePDFViewer').then(mod => ({ default: mod.SimplePDFViewer })), 
  { 
    ssr: false
  }
)

interface DocumentViewerModalProps {
  isOpen: boolean
  onClose: () => void
  initialDocumentId: string
  onNavigate?: (documentId: string) => void
}

function formatFileSize(bytes: number): string {
  const sizes = ['B', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`
}

function getFileIcon(mimeType: string) {
  if (mimeType.startsWith('image/')) return '🖼️'
  if (mimeType.startsWith('video/')) return '🎥'
  if (mimeType.startsWith('audio/')) return '🎵'
  if (mimeType.includes('pdf')) return '📄'
  if (mimeType.includes('word')) return '📝'
  if (mimeType.includes('excel')) return '📊'
  if (mimeType.includes('powerpoint')) return '📽️'
  return '📄'
}

export function DocumentViewerModal({
  isOpen,
  onClose,
  initialDocumentId,
  onNavigate
}: DocumentViewerModalProps) {
  const [currentDocumentId, setCurrentDocumentId] = useState(initialDocumentId)
  const [chunks, setChunks] = useState<DocumentChunk[]>([])
  const [chunksLoading, setChunksLoading] = useState(false)
  const [chunksError, setChunksError] = useState<string | null>(null)
  const [currentDocumentDetails, setCurrentDocumentDetails] = useState<DocumentWithFolder | null>(null)
  const [documentLoading, setDocumentLoading] = useState(false)
  const [aiSummary, setAiSummary] = useState<any>(null)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [summaryError, setSummaryError] = useState<string | null>(null)

  // Load all documents (ungefiltert) for navigation
  const { documents } = useDocuments({
    isGlobalView: true, // Load all documents
    sort: 'created_desc'
  })
  
  // Find current document and index
  const currentIndex = documents.findIndex(d => d.id === currentDocumentId)
  const currentDocument = currentIndex >= 0 ? documents[currentIndex] : null
  // Use detailed document if available, otherwise fall back to list item
  const displayDocument = currentDocumentDetails || currentDocument

  // Update current document ID when initialDocumentId changes
  useEffect(() => {
    if (isOpen && initialDocumentId) {
      setCurrentDocumentId(initialDocumentId)
    }
  }, [isOpen, initialDocumentId])

  // Load document details and chunks when document changes
  useEffect(() => {
    const loadDocumentData = async () => {
      if (currentDocumentId && isOpen) {
        // Only reset chunks, keep other states to prevent flashing
        setChunks([])
        setChunksError(null)
        
        // Never show loading state - we already have document data from the list
        setDocumentLoading(false)

        try {
          // Load chunks immediately
          loadDocumentChunks(currentDocumentId)
          
          // Load AI summary immediately
          loadAiSummary(currentDocumentId)
          
          // Load document details in background silently
          const documentDetails = await apiService.getDocument(currentDocumentId)
          setCurrentDocumentDetails(documentDetails)
        } catch (error) {
          console.error('Error loading document details:', error)
          // Keep using the basic document from list if detailed fetch fails
        }
      }
    }

    loadDocumentData()
  }, [currentDocumentId, isOpen])

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setChunks([])
      setChunksError(null)
      setChunksLoading(false)
      setAiSummary(null)
      setSummaryError(null)
      setSummaryLoading(false)
    }
  }, [isOpen])

  const loadDocumentChunks = async (documentId: string) => {
    setChunksLoading(true)
    setChunksError(null)
    
    try {
      console.log('Loading chunks for document ID:', documentId)
      const response = await apiService.getDocumentChunks(documentId, undefined, 1, 100)
      console.log('Chunks API response:', response)
      
      const chunks = Array.isArray(response?.items) ? response.items : []
      setChunks(chunks)
      
      if (chunks.length === 0) {
        setChunksError('Dieses Dokument hat noch keine Chunks.\n\nMögliche Gründe:\n• Das Dokument wird noch verarbeitet\n• Das Dokument konnte nicht analysiert werden\n• Das Dokument ist leer oder nicht unterstützt')
      }
    } catch (error) {
      console.error('Chunks API error:', error)
      
      if (error instanceof Error && error.message.includes('404')) {
        setChunksError('Dokument nicht gefunden oder noch nicht verarbeitet')
      } else if (error instanceof Error && error.message.includes('500')) {
        setChunksError('Server-Fehler beim Laden der Chunks')
      } else if (error instanceof Error) {
        setChunksError(`API-Fehler: ${error.message}`)
      } else {
        setChunksError('Chunks konnten nicht geladen werden - Backend möglicherweise nicht erreichbar')
      }
      
      setChunks([])
    } finally {
      setChunksLoading(false)
    }
  }

  const loadAiSummary = async (documentId: string) => {
    setSummaryLoading(true)
    setSummaryError(null)
    
    try {
      console.log('Loading AI summary for document ID:', documentId)
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
      const response = await fetch(`${backendUrl}/api/v1/documents/${documentId}/summary`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('AI Summary API response:', data)
      
      setAiSummary(data.summary_data)
      
    } catch (error) {
      console.error('AI Summary API error:', error)
      
      if (error instanceof Error) {
        if (error.message.includes('404')) {
          setSummaryError('Dokument nicht gefunden')
        } else if (error.message.includes('500')) {
          setSummaryError('KI-Service nicht verfügbar. Stellen Sie sicher, dass Ollama läuft.')
        } else {
          setSummaryError(`Fehler beim Laden der Zusammenfassung: ${error.message}`)
        }
      } else {
        setSummaryError('KI-Zusammenfassung nicht verfügbar - Backend oder Ollama nicht erreichbar')
      }
      
      setAiSummary(null)
    } finally {
      setSummaryLoading(false)
    }
  }

  const handlePrevious = useCallback(() => {
    if (currentIndex > 0 && documents.length > 0) {
      const newDocumentId = documents[currentIndex - 1].id
      setCurrentDocumentId(newDocumentId)
      // Notify parent immediately
      if (onNavigate) {
        onNavigate(newDocumentId)
      }
    }
  }, [currentIndex, documents, onNavigate])

  const handleNext = useCallback(() => {
    if (currentIndex >= 0 && currentIndex < documents.length - 1) {
      const newDocumentId = documents[currentIndex + 1].id
      setCurrentDocumentId(newDocumentId)
      // Notify parent immediately
      if (onNavigate) {
        onNavigate(newDocumentId)
      }
    }
  }, [currentIndex, documents, onNavigate])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return
      
      if (e.key === 'ArrowLeft' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault()
        handlePrevious()
      } else if (e.key === 'ArrowRight' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault()
        handleNext()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, handlePrevious, handleNext])

  if (!displayDocument || !currentDocumentId) {
    return null
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="full"
      showCloseButton={false}
      className="max-w-[98vw] max-h-[98vh] h-[98vh]"
    >
      <div className="h-full flex flex-col">
        {/* Header with Navigation and Metadata */}
        <div className="flex-shrink-0 border-b border-gray-200 dark:border-gray-700">
          {/* Top Bar - Navigation */}
          <div className="flex items-center justify-between px-6 py-3 bg-gray-50 dark:bg-gray-800/50">
            <div className="flex items-center space-x-4">
              {/* Navigation Controls */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={handlePrevious}
                  disabled={currentIndex === 0}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Vorheriges Dokument"
                >
                  <ChevronLeftIcon className="w-5 h-5" />
                </button>
                
                <span className="text-sm text-gray-600 dark:text-gray-400 min-w-[80px] text-center">
                  {currentIndex + 1} von {documents.length}
                </span>
                
                <button
                  onClick={handleNext}
                  disabled={currentIndex === documents.length - 1}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Nächstes Dokument"
                >
                  <ChevronRightIcon className="w-5 h-5" />
                </button>
              </div>

              <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />

              {/* Document Title */}
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{getFileIcon(displayDocument.mime_type)}</div>
                <div>
                  <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate max-w-[300px]">
                    {displayDocument.original_filename}
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {displayDocument.folder?.name}
                  </p>
                </div>
              </div>
            </div>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              title="Schließen"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Metadata Bar */}
          <div className="flex items-center justify-between px-6 py-3 bg-white dark:bg-gray-800 text-sm">
            <div className="flex items-center space-x-6">
              {/* File Size */}
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                <ScaleIcon className="w-4 h-4" />
                <span>{formatFileSize(displayDocument.file_size)}</span>
              </div>

              {/* Created Date */}
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                <CalendarDaysIcon className="w-4 h-4" />
                <span>
                  {formatUploadDate(displayDocument.created_at)}
                </span>
              </div>

              {/* Processing Time */}
              {displayDocument.processed_at && (
                <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                  <ClockIcon className="w-4 h-4" />
                  <span>
                    Verarbeitet {formatProcessingDate(displayDocument.processed_at)}
                  </span>
                </div>
              )}

              {/* Chunk Count */}
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                <DocumentTextIcon className="w-4 h-4" />
                <span>{chunks?.length ?? 0} Chunks</span>
              </div>
            </div>

            {/* Status Badge */}
            <div className="flex items-center space-x-2">
              <span className={cn(
                "inline-flex px-2 py-1 text-xs font-medium rounded-full",
                {
                  'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': displayDocument.status === 'ready',
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400': displayDocument.status === 'processing',
                  'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': displayDocument.status === 'error',
                  'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400': !['ready', 'processing', 'error'].includes(displayDocument.status as string)
                }
              )}>
                {displayDocument.status}
              </span>
            </div>
          </div>

          {/* AI Summary Section */}
          <AiSummarySection 
            summary={aiSummary}
            loading={summaryLoading}
            error={summaryError}
            onRetry={() => loadAiSummary(currentDocumentId || '')}
          />
        </div>

        {/* Content Area - Split View */}
        <div className="flex-1 min-h-0">
          <PanelGroup direction="horizontal">
            {/* Left Panel - Document Preview */}
            <Panel defaultSize={50} minSize={30}>
              <DocumentPreview document={displayDocument} />
            </Panel>

            <PanelResizeHandle className="w-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors" />

            {/* Right Panel - Chunks */}
            <Panel defaultSize={50} minSize={30}>
              <ChunksPanel
                chunks={chunks}
                loading={chunksLoading}
                error={chunksError}
                onRetry={() => loadDocumentChunks(currentDocumentId || '')}
              />
            </Panel>
          </PanelGroup>
        </div>
      </div>
    </Modal>
  )
}

// Document Preview Component - Direct Implementation
function DocumentPreview({ document }: { document: DocumentWithFolder }) {
  // Simple state - no complex loading logic
  const [previewError, setPreviewError] = useState<string | null>(null)

  const isPDF = document.mime_type.includes('pdf')
  const isImage = document.mime_type.startsWith('image/')
  const isText = document.mime_type.startsWith('text/')
  
  const downloadUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/v1/documents/${document.id}/download`
  const inlineViewUrl = `${downloadUrl}?inline=true`

  // No complex loading logic needed

  const handleDownload = () => {
    window.open(downloadUrl, '_blank')
  }
  
  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      <div className="flex-shrink-0 px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            Dokumentvorschau
          </h3>
          <button
            onClick={handleDownload}
            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Herunterladen
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-4">
        {isPDF ? (
          <SimplePDFViewer 
            documentId={document.id}
            fileName={document.original_filename}
          />
        ) : null}
        
        {isImage && (
          <div className="h-full flex items-center justify-center">
            <img 
              src={downloadUrl}
              alt={document.original_filename}
              className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
              onError={() => setPreviewError('Bild konnte nicht geladen werden')}
            />
            {previewError && (
              <div className="text-center">
                <div className="text-4xl mb-2">🖼️</div>
                <p className="text-gray-600 mb-2">{previewError}</p>
                <button onClick={handleDownload} className="px-4 py-2 bg-blue-600 text-white rounded">
                  Datei herunterladen
                </button>
              </div>
            )}
          </div>
        )}
        
        {!isPDF && !isImage && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">{getFileIcon(document.mime_type)}</div>
              <h4 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                {document.original_filename}
              </h4>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {formatFileSize(document.file_size)} • {document.mime_type}
              </p>
              <button
                onClick={handleDownload}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Datei herunterladen
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Chunk Content Component with different formatting based on content type
function ChunkContent({ chunk }: { chunk: DocumentChunk }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const isLongContent = chunk.content.length > 300
  const displayContent = isExpanded || !isLongContent ? chunk.content : `${chunk.content.substring(0, 300)}...`

  // Use chunk_type (new) or fall back to content_type (legacy)
  const contentType = chunk.chunk_type || chunk.content_type || 'text'

  const getContentIcon = (type: string) => {
    switch (type) {
      case 'title': return '📝'
      case 'section_header': return '📑'
      case 'table': return '📊'
      case 'image': return '🖼️'
      case 'code': return '💻'
      case 'list': return '📋'
      default: return '📄'
    }
  }

  return (
    <div>
      <div className="flex items-start space-x-2">
        <span className="text-sm">{getContentIcon(contentType)}</span>
        <div className="flex-1">
          {contentType === 'code' ? (
            <pre className="text-sm bg-gray-100 dark:bg-gray-900 p-3 rounded-lg overflow-x-auto">
              <code className="text-gray-800 dark:text-gray-200">
                {displayContent}
              </code>
            </pre>
          ) : contentType === 'table' ? (
            <div className="text-sm bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border-l-4 border-blue-400">
              <div className="font-medium text-blue-800 dark:text-blue-300 mb-2">Tabellendaten:</div>
              <div className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                {displayContent}
              </div>
            </div>
          ) : contentType === 'title' || contentType === 'section_header' ? (
            <div className="text-sm">
              <div className={contentType === 'title' ? 'text-lg font-bold text-gray-900 dark:text-gray-100' : 'text-base font-semibold text-gray-800 dark:text-gray-200'}>
                {displayContent}
              </div>
            </div>
          ) : (
            <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
              {displayContent}
            </div>
          )}
          
          {isLongContent && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-2 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
            >
              {isExpanded ? 'Weniger anzeigen' : 'Mehr anzeigen'}
            </button>
          )}
        </div>
      </div>
      
      {chunk.coordinates && (
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded">
          Position: x={chunk.coordinates.x}, y={chunk.coordinates.y}, 
          Größe: {chunk.coordinates.width}×{chunk.coordinates.height}
        </div>
      )}
    </div>
  )
}

// Chunks Panel Component
function ChunksPanel({ 
  chunks, 
  loading, 
  error, 
  onRetry 
}: { 
  chunks: DocumentChunk[]
  loading: boolean
  error: string | null
  onRetry: () => void
}) {
  const [selectedChunkType, setSelectedChunkType] = useState<string>('all')
  
  const chunkTypes = ['all', 'text', 'table', 'image', 'code', 'list', 'title', 'section_header']
  const filteredChunks = selectedChunkType === 'all' 
    ? (chunks ?? []) 
    : (chunks ?? []).filter(chunk => (chunk.chunk_type || chunk.content_type) === selectedChunkType)

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Chunks werden geladen...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
        {/* Header auch bei Fehlern anzeigen */}
        <div className="flex-shrink-0 px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            Dokument-Chunks
          </h3>
          <p className="text-xs text-red-500 dark:text-red-400 mt-1">
            Fehler beim Laden
          </p>
        </div>
        
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center max-w-md">
            <div className="text-6xl mb-4">⚠️</div>
            <h4 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">
              Chunks konnten nicht geladen werden
            </h4>
            
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
              <p className="text-sm text-red-800 dark:text-red-200 whitespace-pre-line">
                {error}
              </p>
            </div>
            
            <div className="space-y-3">
              <button
                onClick={onRetry}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium transition-colors"
              >
                🔄 Erneut versuchen
              </button>
              
              <details className="text-left">
                <summary className="cursor-pointer text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                  Problemlösung anzeigen
                </summary>
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 space-y-2">
                  <p><strong>Mögliche Ursachen:</strong></p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>Backend-Server ist nicht erreichbar</li>
                    <li>Dokument wurde noch nicht verarbeitet</li>
                    <li>API-Endpoint existiert nicht</li>
                    <li>Netzwerkverbindungsprobleme</li>
                  </ul>
                  <p className="pt-2"><strong>Lösungsansätze:</strong></p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>Backend-Server starten/neustarten</li>
                    <li>Warten bis Dokumentverarbeitung abgeschlossen</li>
                    <li>Browser-Cache leeren und Seite neu laden</li>
                  </ul>
                </div>
              </details>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Chunks Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            Dokument-Chunks
          </h3>
          
          {/* Chunk Type Filter */}
          <select
            value={selectedChunkType}
            onChange={(e) => setSelectedChunkType(e.target.value)}
            className="text-xs border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            {chunkTypes.map(type => (
              <option key={type} value={type}>
                {type === 'all' ? 'Alle' : type}
              </option>
            ))}
          </select>
        </div>
        
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {filteredChunks?.length ?? 0} von {chunks?.length ?? 0} Chunks
        </p>
      </div>

      {/* Chunks List */}
      <div className="flex-1 overflow-y-auto">
        {filteredChunks.length === 0 ? (
          <div className="flex items-center justify-center h-32">
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              {selectedChunkType === 'all' ? 'Keine Chunks verfügbar' : `Keine ${selectedChunkType}-Chunks gefunden`}
            </p>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {filteredChunks.map((chunk, index) => (
              <div
                key={chunk.id}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded">
                    {chunk.chunk_type || chunk.content_type || 'text'}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    #{chunk.chunk_index}
                    {chunk.page_number && ` • Seite ${chunk.page_number}`}
                  </span>
                </div>
                
                <ChunkContent chunk={chunk} />
                
                {chunk.metadata && Object.keys(chunk.metadata).length > 0 && (
                  <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    <details>
                      <summary className="cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
                        Metadaten
                      </summary>
                      <pre className="mt-1 text-xs bg-gray-50 dark:bg-gray-700 p-2 rounded overflow-x-auto">
                        {JSON.stringify(chunk.metadata, null, 2)}
                      </pre>
                    </details>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// AI Summary Section Component
function AiSummarySection({ 
  summary, 
  loading, 
  error, 
  onRetry 
}: { 
  summary: any
  loading: boolean
  error: string | null
  onRetry: () => void
}) {
  const [expanded, setExpanded] = useState(false)

  if (loading) {
    return (
      <div className="px-6 py-4 bg-blue-50 dark:bg-blue-900/20 border-t border-blue-200 dark:border-blue-800">
        <div className="flex items-center space-x-3">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 dark:border-blue-400"></div>
          <div className="flex-1">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              <span className="font-medium">KI-Zusammenfassung wird generiert...</span>
            </p>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              Dies kann einen Moment dauern. Die lokale KI analysiert das Dokument.
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-6 py-4 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800">
        <div className="flex items-start space-x-3">
          <SparklesIcon className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-red-700 dark:text-red-300">
              <span className="font-medium">KI-Zusammenfassung nicht verfügbar</span>
            </p>
            <p className="text-xs text-red-600 dark:text-red-400 mt-1">
              {error}
            </p>
            <button
              onClick={onRetry}
              className="mt-2 text-xs text-red-700 dark:text-red-300 hover:text-red-900 dark:hover:text-red-100 underline"
            >
              Erneut versuchen
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!summary) {
    return (
      <div className="px-6 py-3 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <SparklesIcon className="w-5 h-5 text-gray-400" />
          <div className="flex-1">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Keine KI-Zusammenfassung verfügbar
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="px-6 py-3 bg-blue-50 dark:bg-blue-900/20 border-t border-blue-200 dark:border-blue-800">
      <div className="flex items-center space-x-3">
        <SparklesIcon className="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-blue-700 dark:text-blue-300 mb-1">
            KI-Zusammenfassung
          </p>
          <div className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed line-clamp-3">
            {summary.summary}
          </div>
        </div>
      </div>
    </div>
  )
}

// Export as default for dynamic imports
export default DocumentViewerModal
