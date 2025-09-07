'use client'

import { useState } from 'react'
import { 
  FileText, Eye, Download, Edit, Share2, Trash2, 
  AlertCircle, CheckCircle, AlertTriangle, Copy,
  ZoomIn, ZoomOut, Code, FileCode
} from 'lucide-react'
import { XMLStreamDocument, XMLValidationResult } from '@/types/xml-stream.types'
import { XML_CUSTOMER_CATEGORIES, XML_STREAM_TYPES } from '@/types/xml-stream.types'

interface XMLStreamPreviewProps {
  stream: XMLStreamDocument
  xmlContent?: string
  onClose: () => void
  onEdit?: () => void
  onDownload?: () => void
  onDelete?: () => void
  loading?: boolean
}

export function XMLStreamPreview({
  stream,
  xmlContent,
  onClose,
  onEdit,
  onDownload,
  onDelete,
  loading = false
}: XMLStreamPreviewProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'content' | 'validation'>('overview')
  const [zoom, setZoom] = useState(100)

  const customerCategory = XML_CUSTOMER_CATEGORIES.find(c => c.value === stream.xml_metadata.customer_category)
  const streamType = XML_STREAM_TYPES.find(t => t.value === stream.xml_metadata.stream_type)

  const getValidationStatusSummary = () => {
    const results = stream.xml_metadata.validation_results
    const errors = results.filter(r => r.status === 'error')
    const warnings = results.filter(r => r.status === 'warning')
    const valid = results.filter(r => r.status === 'valid')

    return { errors, warnings, valid }
  }

  const getComplexityInfo = (score: number) => {
    if (score < 3) return { label: 'Niedrig', color: 'text-green-600 bg-green-100', description: 'Einfache Struktur' }
    if (score < 6) return { label: 'Mittel', color: 'text-yellow-600 bg-yellow-100', description: 'Moderate Komplexität' }
    if (score < 8) return { label: 'Hoch', color: 'text-orange-600 bg-orange-100', description: 'Komplexe Struktur' }
    return { label: 'Sehr Hoch', color: 'text-red-600 bg-red-100', description: 'Hochkomplexe Struktur' }
  }

  const formatXML = (xml: string) => {
    // Simple XML formatting - in production, use a proper XML formatter
    return xml
      .replace(/></g, '>\n<')
      .replace(/^\s*\n/gm, '')
      .split('\n')
      .map(line => line.trim())
      .join('\n')
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const { errors, warnings, valid } = getValidationStatusSummary()
  const complexity = getComplexityInfo(stream.xml_metadata.complexity_score)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-6xl h-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">{streamType?.icon || '🌊'}</span>
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  {stream.xml_metadata.stream_name}
                </h2>
                <p className="text-sm text-gray-500">
                  {stream.filename}
                </p>
              </div>
            </div>
            
            <div className={`px-3 py-1 rounded-full text-sm font-medium bg-${customerCategory?.color}-100 text-${customerCategory?.color}-700`}>
              {customerCategory?.label}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {onEdit && (
              <button
                onClick={onEdit}
                className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Bearbeiten"
              >
                <Edit className="w-5 h-5" />
              </button>
            )}
            
            {onDownload && (
              <button
                onClick={onDownload}
                className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                title="Herunterladen"
              >
                <Download className="w-5 h-5" />
              </button>
            )}

            <button
              onClick={() => copyToClipboard(window.location.href)}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Link teilen"
            >
              <Share2 className="w-5 h-5" />
            </button>

            {onDelete && (
              <button
                onClick={onDelete}
                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Löschen"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            )}

            <button
              onClick={onClose}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Schließen"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <div className="flex">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Eye className="w-4 h-4" />
                <span>Übersicht</span>
              </div>
            </button>

            <button
              onClick={() => setActiveTab('content')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'content'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <FileCode className="w-4 h-4" />
                <span>XML Inhalt</span>
              </div>
            </button>

            <button
              onClick={() => setActiveTab('validation')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'validation'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4" />
                <span>Validierung</span>
                {errors.length > 0 && (
                  <span className="bg-red-100 text-red-600 px-2 py-1 rounded-full text-xs">
                    {errors.length}
                  </span>
                )}
                {warnings.length > 0 && errors.length === 0 && (
                  <span className="bg-yellow-100 text-yellow-600 px-2 py-1 rounded-full text-xs">
                    {warnings.length}
                  </span>
                )}
              </div>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          )}

          {!loading && activeTab === 'overview' && (
            <div className="p-6 overflow-y-auto h-full space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Stream-Informationen
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Typ:</span>
                      <span className="font-medium flex items-center space-x-2">
                        <span>{streamType?.icon}</span>
                        <span>{streamType?.label}</span>
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Jobs:</span>
                      <span className="font-medium">{stream.xml_metadata.job_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Abhängigkeiten:</span>
                      <span className="font-medium">{stream.xml_metadata.dependency_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Komplexität:</span>
                      <span className={`px-2 py-1 rounded text-sm ${complexity.color}`}>
                        {complexity.label} ({stream.xml_metadata.complexity_score})
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">RAG Indiziert:</span>
                      <span className={`font-medium ${stream.rag_indexed ? 'text-green-600' : 'text-red-600'}`}>
                        {stream.rag_indexed ? 'Ja' : 'Nein'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Validierungsstatus
                  </h3>
                  <div className="space-y-3">
                    {errors.length > 0 && (
                      <div className="flex items-center space-x-3 text-red-600">
                        <AlertCircle className="w-5 h-5" />
                        <span>{errors.length} Fehler</span>
                      </div>
                    )}
                    {warnings.length > 0 && (
                      <div className="flex items-center space-x-3 text-yellow-600">
                        <AlertTriangle className="w-5 h-5" />
                        <span>{warnings.length} Warnungen</span>
                      </div>
                    )}
                    {valid.length > 0 && (
                      <div className="flex items-center space-x-3 text-green-600">
                        <CheckCircle className="w-5 h-5" />
                        <span>{valid.length} Gültige Prüfungen</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Patterns */}
              {stream.xml_metadata.patterns.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Erkannte Patterns
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {stream.xml_metadata.patterns.map((pattern, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                      >
                        {pattern}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Anti-patterns */}
              {stream.xml_metadata.anti_patterns.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Anti-Patterns
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {stream.xml_metadata.anti_patterns.map((pattern, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm"
                      >
                        {pattern}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {!loading && activeTab === 'content' && (
            <div className="h-full flex flex-col">
              {/* Content Controls */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">XML Inhalt</span>
                  {xmlContent && (
                    <span className="text-xs text-gray-500">
                      {xmlContent.length.toLocaleString()} Zeichen
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setZoom(Math.max(50, zoom - 10))}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                    title="Verkleinern"
                  >
                    <ZoomOut className="w-4 h-4" />
                  </button>
                  
                  <div className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded text-sm">
                    {zoom}%
                  </div>
                  
                  <button
                    onClick={() => setZoom(Math.min(200, zoom + 10))}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                    title="Vergrößern"
                  >
                    <ZoomIn className="w-4 h-4" />
                  </button>
                  
                  {xmlContent && (
                    <button
                      onClick={() => copyToClipboard(xmlContent)}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                      title="Kopieren"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Content Display */}
              <div className="flex-1 overflow-auto p-4">
                {xmlContent ? (
                  <pre
                    className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg text-sm font-mono overflow-auto"
                    style={{ fontSize: `${zoom}%` }}
                  >
                    <code className="language-xml">
                      {formatXML(xmlContent)}
                    </code>
                  </pre>
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-500">
                    <div className="text-center">
                      <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                      <p>XML Inhalt wird geladen...</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {!loading && activeTab === 'validation' && (
            <div className="p-6 overflow-y-auto h-full">
              <div className="space-y-6">
                {errors.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-red-600 mb-4 flex items-center space-x-2">
                      <AlertCircle className="w-5 h-5" />
                      <span>Fehler ({errors.length})</span>
                    </h3>
                    <div className="space-y-3">
                      {errors.map((error, idx) => (
                        <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-medium text-red-800">
                              {error.level}
                            </span>
                            <span className={`px-2 py-1 rounded text-xs ${
                              error.severity === 'critical' ? 'bg-red-200 text-red-800' :
                              error.severity === 'high' ? 'bg-red-100 text-red-700' :
                              'bg-red-50 text-red-600'
                            }`}>
                              {error.severity}
                            </span>
                          </div>
                          <p className="text-red-700 mb-2">{error.message}</p>
                          {error.line_number && (
                            <p className="text-sm text-red-600">Zeile: {error.line_number}</p>
                          )}
                          {error.xpath && (
                            <p className="text-sm text-red-600 font-mono">XPath: {error.xpath}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {warnings.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-yellow-600 mb-4 flex items-center space-x-2">
                      <AlertTriangle className="w-5 h-5" />
                      <span>Warnungen ({warnings.length})</span>
                    </h3>
                    <div className="space-y-3">
                      {warnings.map((warning, idx) => (
                        <div key={idx} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-medium text-yellow-800">
                              {warning.level}
                            </span>
                            <span className={`px-2 py-1 rounded text-xs ${
                              warning.severity === 'high' ? 'bg-yellow-200 text-yellow-800' :
                              warning.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-yellow-50 text-yellow-600'
                            }`}>
                              {warning.severity}
                            </span>
                          </div>
                          <p className="text-yellow-700 mb-2">{warning.message}</p>
                          {warning.line_number && (
                            <p className="text-sm text-yellow-600">Zeile: {warning.line_number}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {valid.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-green-600 mb-4 flex items-center space-x-2">
                      <CheckCircle className="w-5 h-5" />
                      <span>Gültige Prüfungen ({valid.length})</span>
                    </h3>
                    <div className="space-y-3">
                      {valid.map((validation, idx) => (
                        <div key={idx} className="bg-green-50 border border-green-200 rounded-lg p-4">
                          <div className="flex items-center space-x-2">
                            <CheckCircle className="w-4 h-4 text-green-600" />
                            <span className="font-medium text-green-800">
                              {validation.level}
                            </span>
                          </div>
                          <p className="text-green-700 mt-1">{validation.message}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {errors.length === 0 && warnings.length === 0 && valid.length === 0 && (
                  <div className="text-center py-12">
                    <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      Keine Validierungsergebnisse
                    </h3>
                    <p className="text-gray-500">
                      Starten Sie eine Validierung, um Ergebnisse zu sehen.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}