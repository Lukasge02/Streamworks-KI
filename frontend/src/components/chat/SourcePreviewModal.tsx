'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Download, ExternalLink, FileText, Copy, Search } from 'lucide-react'

interface SourcePreviewModalProps {
  source: {
    id: string
    metadata: {
      doc_id?: string
      original_filename?: string
      page_number?: number
      heading?: string
      section?: string
    }
    relevance_score?: number
  } | null
  isOpen: boolean
  onClose: () => void
}

export const SourcePreviewModal: React.FC<SourcePreviewModalProps> = ({
  source,
  isOpen,
  onClose
}) => {
  const [previewData, setPreviewData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // Removed activeTab - simplified to single view

  useEffect(() => {
    if (isOpen && source) {
      console.log('FULL SOURCE OBJECT:', JSON.stringify(source, null, 2))
      
      // Try multiple ways to find the doc_id
      let docId = source.metadata?.doc_id || 
                  (source.metadata as any)?.source_file || 
                  source.id ||
                  (source as any).source_file
      
      console.log('TRYING TO LOAD DOC_ID:', docId)
      
      if (docId) {
        // Clean doc_id - remove .pdf extension if it exists
        const cleanDocId = docId.replace(/\.pdf$/, '')
        console.log('CLEANED DOC_ID:', cleanDocId)
        loadDocumentPreview(cleanDocId)
      } else {
        console.log('NO VALID DOC_ID FOUND IN SOURCE')
        setError('Keine Dokument-ID gefunden')
      }
    }
  }, [isOpen, source])

  const loadDocumentPreview = async (docId: string) => {
    setLoading(true)
    setError(null)
    
    try {
      // Load document data from main documents endpoint which has everything
      const response = await fetch('/api/documents')
      
      if (response.ok) {
        const documents = await response.json()
        // Find document - prefer the one WITH ai_summary
        const docs = documents.filter((d: any) => d.id === docId)
        const doc = docs.length > 0 ? docs.find((d: any) => d.ai_summary) || docs.find((d: any) => d.original_filename && d.original_filename !== d.id + '.pdf') || docs[0] : null
        
        if (doc) {
          console.log('FOUND DOC:', doc)
          console.log('AI_SUMMARY:', doc.ai_summary)
          
          setPreviewData({
            document_id: doc.id,
            filename: doc.original_filename || doc.filename,
            doctype: doc.doctype,
            category: doc.category,
            file_size_bytes: doc.size_bytes,
            chunk_count: doc.chunk_count,
            status: doc.status,
            created_at: doc.upload_date,
            preview_text: doc.preview_text || 'PDF-Dokument verfügbar',
            metadata: {
              original_filename: doc.original_filename,
              path: doc.path,
              folder_id: doc.folder_id
            },
            ai_summary: doc.ai_summary
          })
        } else {
          setError('Dokument nicht in der Datenbank gefunden')
        }
      } else {
        setError('Fehler beim Laden der Dokumentliste')
      }
    } catch (err) {
      setError('Fehler beim Laden der Vorschau')
      console.error('Preview loading error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (!source?.metadata?.doc_id) return

    try {
      const response = await fetch(`/api/documents/${source.metadata.doc_id}/file`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = source.metadata.original_filename || 'document.pdf'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      }
    } catch (err) {
      console.error('Download error:', err)
    }
  }

  const handleViewInNewTab = () => {
    if (!source?.metadata?.doc_id) return
    window.open(`/api/documents/${source.metadata.doc_id}/file`, '_blank')
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  if (!isOpen || !source) return null

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-[95vw] h-[95vh] overflow-hidden border border-gray-200 dark:border-gray-700"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center shadow-sm">
                <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white truncate max-w-md">
                  {previewData?.filename || source.metadata.original_filename || source.metadata.doc_id}
                </h2>
                <div className="flex items-center space-x-3 text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {source.metadata.page_number && (
                    <span className="flex items-center"><FileText className="w-3 h-3 mr-1" />Seite {source.metadata.page_number}</span>
                  )}
                  {source.relevance_score && typeof source.relevance_score === 'number' && source.relevance_score > 0 && (
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300">
                      {Math.round(source.relevance_score * 100)}% relevant
                    </span>
                  )}
                  {previewData?.doctype && (
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                      {previewData.doctype.toUpperCase()}
                    </span>
                  )}
                  {previewData?.metadata?.path && (
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300">
                      📁 {previewData.metadata.path.split('/').slice(0, -1).join('/')}
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleDownload}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Herunterladen"
              >
                <Download className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              <button
                onClick={handleViewInNewTab}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="In neuem Tab öffnen"
              >
                <ExternalLink className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              <button
                onClick={onClose}
                className="p-2 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400" />
              </button>
            </div>
          </div>

          {/* AI Summary Bar */}
          {previewData?.ai_summary?.summary && (
            <div className="border-b border-gray-200 dark:border-gray-700 bg-blue-50 dark:bg-blue-900/20 px-6 py-4">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-600 dark:text-blue-300 text-xs font-bold">AI</span>
                </div>
                <div className="flex-1">
                  <div className="text-xs text-blue-600 dark:text-blue-400 font-medium mb-1">AI-Zusammenfassung</div>
                  <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
                    {previewData.ai_summary.summary}
                  </p>
                  {previewData.ai_summary.key_points && previewData.ai_summary.key_points.length > 0 && (
                    <div className="mt-2">
                      <div className="text-xs text-blue-600 dark:text-blue-400 font-medium mb-1">Kernpunkte:</div>
                      <ul className="text-xs text-blue-700 dark:text-blue-300 list-disc list-inside space-y-1">
                        {previewData.ai_summary.key_points.map((point: string, index: number) => (
                          <li key={index}>{point}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Main Content - Side by Side Layout */}
          <div className="flex-1 flex overflow-hidden h-full">
            {loading ? (
              <div className="flex items-center justify-center w-full h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
              </div>
            ) : error ? (
              <div className="flex items-center justify-center w-full h-64 text-red-500">
                <div className="text-center">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>{error}</p>
                </div>
              </div>
            ) : (
              <>
                {/* Left Side - Document Viewer */}
                <div className="flex-1 border-r border-gray-200 dark:border-gray-700 overflow-hidden h-full flex flex-col bg-gray-100 dark:bg-gray-900">
                  <div className="p-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white flex items-center">
                      <FileText className="w-4 h-4 mr-2" />
                      PDF Dokument
                    </h3>
                  </div>
                  
                  {/* PDF Viewer */}
                  <div className="flex-1 bg-gray-100 dark:bg-gray-900 relative">
                      {source?.metadata?.doc_id ? (
                        <iframe
                          src={`/api/documents/${source.metadata.doc_id.replace(/\.pdf$/, '')}/file`}
                          className="w-full h-full border-0"
                          title={source.metadata.original_filename || 'PDF Dokument'}
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full">
                          <div className="text-center">
                            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-500 dark:text-gray-400 font-medium">Dokument nicht verfügbar</p>
                            <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                              Dokument-ID: {source?.id || 'Unbekannt'}
                            </p>
                            <div className="mt-4 space-y-2">
                              <div className="text-xs text-gray-500">
                                Debug-Info:
                              </div>
                              <div className="text-xs font-mono bg-gray-200 dark:bg-gray-700 p-2 rounded">
                                doc_id: {source?.metadata?.doc_id || 'fehlt'}<br/>
                                id: {source?.id || 'fehlt'}<br/>
                                filename: {source?.metadata?.original_filename || 'fehlt'}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                  </div>
                </div>
                
                {/* Right Side - Relevant Text Section */}
                <div className="w-1/2 p-6 bg-yellow-50 dark:bg-yellow-900/10 overflow-y-auto h-full flex flex-col">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-4 flex items-center">
                    <Search className="w-4 h-4 mr-2 text-yellow-600" />
                    Relevanter Abschnitt
                    {source.relevance_score && typeof source.relevance_score === 'number' && source.relevance_score > 0 && (
                      <span className="ml-2 text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded">
                        {Math.round(source.relevance_score * 100)}% relevant
                      </span>
                    )}
                  </h3>
                  
                  {source.metadata.heading && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Überschrift:</h4>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">{source.metadata.heading}</p>
                    </div>
                  )}
                  
                  {source.metadata.section && source.metadata.section.trim() ? (
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800 shadow-sm">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Textabschnitt aus der Quelle:
                        </span>
                        <button
                          onClick={() => copyToClipboard(source.metadata.section || '')}
                          className="p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                          title="Text kopieren"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="max-h-64 overflow-y-auto">
                        <p className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed border-l-4 border-yellow-400 pl-3 italic whitespace-pre-wrap">
                          „{source.metadata.section}“
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Search className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Kein spezifischer Textabschnitt verfügbar
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                        Das Dokument kann über die PDF-Ansicht eingesehen werden
                      </p>
                    </div>
                  )}

                </div>
              </>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}