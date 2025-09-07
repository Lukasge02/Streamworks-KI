'use client'

import { useState, useEffect } from 'react'
import { 
  Wand2, Search, Upload, Layers, Target, 
  FileText, CheckCircle, Zap, Plus, AlertCircle, Brain, Sparkles,
  Edit, Calendar, PlusCircle
} from 'lucide-react'
import { XMLStreamAPI } from '@/services/xmlStreamApi'
import { XMLStreamDocument, XMLStreamFilter } from '@/types/xml-stream.types'
import { XMLUploadModal } from './XMLUploadModal'
import { StreamBuilder } from '../stream/StreamBuilder'
import { StreamFormAdvanced } from '../stream/StreamFormAdvanced'
import { XMLStreamSkeleton } from '@/components/ui/LoadingSkeleton'

interface XMLGeneratorProps {
  className?: string
}

export function XMLGenerator({ className }: XMLGeneratorProps) {
  const [activeTab, setActiveTab] = useState<'library' | 'new' | 'modify'>('library')
  const [requirements, setRequirements] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Real data from backend
  const [streams, setStreams] = useState<XMLStreamDocument[]>([])
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showUploadModal, setShowUploadModal] = useState(false)

  // Load real XML streams from backend
  useEffect(() => {
    loadXMLStreams()
  }, [])

  const loadXMLStreams = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Try to load real streams from backend
      const realStreams = await XMLStreamAPI.getXMLStreams({
        search: searchQuery,
        customer_category: 'all',
        stream_type: 'all',
        complexity_range: { min: 0, max: 10 },
        job_count_range: { min: 0, max: 100 },
        patterns: [],
        validation_status: 'all',
        dateRange: {}
      })
      
      setStreams(realStreams)
      setBackendConnected(true)
      
    } catch (err) {
      console.warn('Backend not available, using mock data:', err)
      setBackendConnected(false)
      
      // Fallback to enhanced mock data that looks like real data
      setStreams([
        {
          id: 'mock-1',
          filename: 'daily_file_processing.xml',
          doctype: 'xml-streams',
          category: 'xml',
          chunk_count: 12,
          status: 'ready',
          upload_date: new Date().toISOString(),
          size_bytes: 15420,
          tags: ['processing', 'demo'],
          visibility: ['internal'],
          language: 'en',
          xml_metadata: {
            stream_name: 'Daily File Processing',
            customer_category: 'Demo',
            job_count: 12,
            dependency_count: 8,
            complexity_score: 3,
            patterns: ['file-processing', 'validation', 'error-handling'],
            anti_patterns: [],
            stream_type: 'processing',
            validation_results: [
              { level: 'syntax', status: 'valid', message: 'XML syntax valid', severity: 'low' },
              { level: 'schema', status: 'valid', message: 'Schema validation passed', severity: 'low' }
            ],
            chunking_strategy: 'hybrid',
            last_modified: new Date().toISOString()
          },
          rag_indexed: true,
          similarity_score: 0.95,
          generation_source: 'uploaded'
        } as XMLStreamDocument,
        {
          id: 'mock-2',
          filename: 'database_sync_stream.xml', 
          doctype: 'xml-streams',
          category: 'xml',
          chunk_count: 8,
          status: 'ready',
          upload_date: new Date().toISOString(),
          size_bytes: 12800,
          tags: ['integration', 'database'],
          visibility: ['internal'],
          language: 'en',
          xml_metadata: {
            stream_name: 'Database Sync Stream',
            customer_category: 'Production',
            job_count: 8,
            dependency_count: 12,
            complexity_score: 5,
            patterns: ['database-sync', 'transaction-handling', 'rollback'],
            anti_patterns: ['blocking-operations'],
            stream_type: 'integration',
            validation_results: [
              { level: 'syntax', status: 'valid', message: 'XML syntax valid', severity: 'low' },
              { level: 'business_logic', status: 'warning', message: 'Potential performance issue detected', severity: 'medium' }
            ],
            chunking_strategy: 'functional',
            last_modified: new Date().toISOString()
          },
          rag_indexed: true,
          similarity_score: 0.87,
          generation_source: 'uploaded'
        } as XMLStreamDocument,
        {
          id: 'mock-3',
          filename: 'monitoring_stream.xml',
          doctype: 'xml-streams', 
          category: 'xml',
          chunk_count: 15,
          status: 'ready',
          upload_date: new Date().toISOString(),
          size_bytes: 18950,
          tags: ['monitoring', 'alerts'],
          visibility: ['internal'],
          language: 'en',
          xml_metadata: {
            stream_name: 'System Monitoring Stream',
            customer_category: 'Beta',
            job_count: 15,
            dependency_count: 10,
            complexity_score: 7,
            patterns: ['monitoring', 'alerting', 'metrics-collection', 'dashboard-updates'],
            anti_patterns: [],
            stream_type: 'monitoring',
            validation_results: [
              { level: 'syntax', status: 'valid', message: 'XML syntax valid', severity: 'low' },
              { level: 'schema', status: 'valid', message: 'Schema validation passed', severity: 'low' },
              { level: 'streamworks_compatibility', status: 'valid', message: 'StreamWorks compatible', severity: 'low' }
            ],
            chunking_strategy: 'hierarchical',
            last_modified: new Date().toISOString()
          },
          rag_indexed: true,
          similarity_score: 0.92,
          generation_source: 'uploaded'
        } as XMLStreamDocument
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!requirements.trim()) return

    try {
      setLoading(true)
      setError(null)

      if (backendConnected) {
        // Real API call to backend
        const result = await XMLStreamAPI.generateXMLStream({
          user_query: requirements,
          selected_templates: [],
          customer_environment: 'Demo',
          complexity_preference: 'advanced',
          validation_requirements: ['syntax', 'schema', 'streamworks_compatibility'],
          constraints: {
            max_jobs: 50,
            max_dependencies: 100,
            performance_target: 5.0
          }
        })
        
        alert('XML Stream erfolgreich generiert!\n\nGenerated XML length: ' + result.xml_content.length + ' characters')
        
        // Refresh the streams list
        await loadXMLStreams()
        
      } else {
        // Fallback demo behavior
        await new Promise(resolve => setTimeout(resolve, 1500))
        alert('XML Stream erfolgreich generiert! (Demo Mode - Backend offline)\n\nIn production this would:\n• Generate real StreamWorks XML\n• Validate against schemas\n• Add to stream library')
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (query: string) => {
    setSearchQuery(query)
    if (backendConnected) {
      await loadXMLStreams()
    }
  }

  const renderLibraryTab = () => (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          XML Stream Library
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Verwalten und durchsuchen Sie Ihre StreamWorks XML-Konfigurationen
        </p>
      </div>

      {/* Backend Connection Status */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {backendConnected === null ? (
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full text-sm bg-yellow-100 text-yellow-800">
              <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></div>
              <span>Backend verbinden...</span>
            </div>
          ) : backendConnected ? (
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <span>Backend Online - Echte Daten</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full text-sm bg-orange-100 text-orange-800">
              <div className="w-2 h-2 rounded-full bg-orange-500"></div>
              <span>Demo Modus - Backend offline</span>
            </div>
          )}
        </div>
        <div className="text-sm text-gray-500">
          {streams.length} Streams verfügbar
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6 relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Nach Stream-Namen oder Patterns suchen..."
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <div>
            <p className="text-red-800 font-medium">Fehler</p>
            <p className="text-red-600 text-sm">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-600"
          >
            ✕
          </button>
        </div>
      )}

      {/* Stream Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded mb-2"></div>
                <div className="h-2 bg-gray-200 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {streams.map((stream) => {
            const hasErrors = stream.xml_metadata.validation_results.some(r => r.status === 'error')
            const hasWarnings = stream.xml_metadata.validation_results.some(r => r.status === 'warning')
            
            return (
              <div
                key={stream.id}
                className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer group"
                onClick={() => {
                  alert(`Stream Details:\n\nName: ${stream.xml_metadata.stream_name}\nJobs: ${stream.xml_metadata.job_count}\nKomplexität: ${stream.xml_metadata.complexity_score}\nPatterns: ${stream.xml_metadata.patterns.join(', ')}\nRAG Indiziert: ${stream.rag_indexed ? 'Ja' : 'Nein'}`)
                }}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">🌊</span>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      stream.xml_metadata.customer_category === 'Production' ? 'bg-red-100 text-red-700' :
                      stream.xml_metadata.customer_category === 'Beta' ? 'bg-purple-100 text-purple-700' :
                      stream.xml_metadata.customer_category === 'Demo' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {stream.xml_metadata.customer_category}
                    </div>
                    {stream.rag_indexed && (
                      <div className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs">
                        RAG
                      </div>
                    )}
                  </div>
                  <span className={`text-lg ${
                    hasErrors ? 'text-red-600' : hasWarnings ? 'text-yellow-600' : 'text-green-600'
                  }`}>
                    {hasErrors ? '❌' : hasWarnings ? '⚠️' : '✅'}
                  </span>
                </div>

                <h3 className="font-medium text-gray-900 dark:text-white mb-1">
                  {stream.xml_metadata.stream_name}
                </h3>
                
                <p className="text-xs text-gray-500 mb-3 truncate">
                  {stream.filename}
                </p>

                {/* Patterns */}
                {stream.xml_metadata.patterns.length > 0 && (
                  <div className="mb-3 flex flex-wrap gap-1">
                    {stream.xml_metadata.patterns.slice(0, 2).map((pattern, idx) => (
                      <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        {pattern}
                      </span>
                    ))}
                    {stream.xml_metadata.patterns.length > 2 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        +{stream.xml_metadata.patterns.length - 2}
                      </span>
                    )}
                  </div>
                )}
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{stream.xml_metadata.job_count} Jobs</span>
                  <span className={`px-2 py-1 rounded ${
                    stream.xml_metadata.complexity_score < 4 ? 'bg-green-100 text-green-600' :
                    stream.xml_metadata.complexity_score < 7 ? 'bg-yellow-100 text-yellow-600' :
                    'bg-red-100 text-red-600'
                  }`}>
                    K{stream.xml_metadata.complexity_score}
                  </span>
                </div>

                {/* Hover overlay */}
                <div className="absolute inset-0 bg-blue-500 bg-opacity-0 group-hover:bg-opacity-5 rounded-lg transition-all duration-200 pointer-events-none"></div>
              </div>
            )
          })}
        </div>
      )}

      {/* Action Buttons */}
      {streams.length > 0 && (
        <div className="text-center py-8 mt-8 border-2 border-dashed border-gray-300 rounded-lg">
          <FileText className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Weitere Aktionen
          </h3>
          <p className="text-gray-500 mb-4">
            Laden Sie weitere XML Streams hoch oder verbinden Sie sich mit dem Backend
          </p>
          <div className="flex justify-center space-x-3">
            <button
              onClick={() => setShowUploadModal(true)}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
            >
              <Upload className="w-4 h-4" />
              <span>XML hochladen</span>
            </button>
            <button
              onClick={() => loadXMLStreams()}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg"
            >
              <Plus className="w-4 h-4" />
              <span>Backend verbinden</span>
            </button>
          </div>
        </div>
      )}

      {/* Empty State */}
      {streams.length === 0 && !loading && (
        <div className="text-center py-12 mt-8 border-2 border-dashed border-gray-300 rounded-lg">
          <FileText className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Keine XML Streams gefunden
          </h3>
          <p className="text-gray-500 mb-4">
            {backendConnected === false 
              ? 'Backend offline - Demo-Daten werden geladen...'
              : 'Laden Sie Ihren ersten XML Stream hoch oder verbinden Sie sich mit dem Backend'
            }
          </p>
          <div className="flex justify-center space-x-3">
            <button
              onClick={() => setShowUploadModal(true)}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
            >
              <Upload className="w-4 h-4" />
              <span>XML hochladen</span>
            </button>
            {backendConnected === false && (
              <button
                onClick={() => loadXMLStreams()}
                className="inline-flex items-center space-x-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg"
              >
                <Plus className="w-4 h-4" />
                <span>Backend verbinden</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )

  const renderBuilderTab = () => (
    <div className="h-full">
      <StreamFormAdvanced />
    </div>
  )

  const renderNewStreamTab = () => (
    <div className="h-full">
      <StreamBuilder />
    </div>
  )

  const renderModifyStreamTab = () => (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Bestehenden Stream ändern
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Finden Sie einen Stream und nehmen Sie Änderungen vor
        </p>
      </div>

      {/* Stream Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Stream suchen (z.B. EGK-P-BSI-010, DMG-P-PA1-PUR-0013)..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Job hinzufügen</h3>
          <p className="text-blue-700 dark:text-blue-300 text-sm">
            Fügen Sie einen neuen Job nach einem bestehenden Job hinzu
          </p>
        </div>
        <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
          <h3 className="font-semibold text-orange-900 dark:text-orange-100 mb-2">Parameter ändern</h3>
          <p className="text-orange-700 dark:text-orange-300 text-sm">
            User, Server, Script-Pfad oder andere Parameter anpassen
          </p>
        </div>
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
          <h3 className="font-semibold text-green-900 dark:text-green-100 mb-2">Scheduling ändern</h3>
          <p className="text-green-700 dark:text-green-300 text-sm">
            Zeiten, Intervalle oder Abhängigkeiten anpassen
          </p>
        </div>
      </div>

      {/* Stream Results */}
      {streams.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Gefundene Streams ({streams.length})
          </h3>
          <div className="space-y-3">
            {streams.map((stream) => (
              <div key={stream.id} className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 hover:border-blue-500 cursor-pointer transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">
                      {stream.xml_metadata.stream_name}
                    </h4>
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                      {stream.xml_metadata.job_count} Jobs • {stream.xml_metadata.customer_category}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">
                      Bearbeiten
                    </button>
                    <button className="px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600">
                      Ansehen
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )




  return (
    <div className={`flex flex-col h-full bg-gray-50 dark:bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              Stream Formular
            </h1>
          </div>
          
          {/* Navigation Tabs in Header */}
          <div className="flex items-center space-x-4">
            {[
              { id: 'library', label: 'Stream Library', icon: Layers },
              { id: 'new', label: 'Neuer Stream', icon: PlusCircle },
              { id: 'modify', label: 'Stream ändern', icon: Edit },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === id
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{label}</span>
              </button>
            ))}
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center space-x-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm"
            >
              <Upload className="w-4 h-4" />
              <span>Upload</span>
            </button>
          </div>
        </div>
      </div>


      {/* Content */}
      <div className="flex-1 overflow-auto">
        {activeTab === 'library' && renderLibraryTab()}
        {activeTab === 'new' && renderNewStreamTab()}
        {activeTab === 'modify' && renderModifyStreamTab()}
      </div>

      {/* Upload Modal */}
      <XMLUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUploadComplete={() => {
          setShowUploadModal(false)
          loadXMLStreams() // Refresh the streams list
        }}
      />
    </div>
  )
}