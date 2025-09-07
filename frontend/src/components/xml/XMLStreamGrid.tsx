'use client'

import { useState, useMemo } from 'react'
import { Search, Filter, Grid, List, Upload, Plus, MoreHorizontal } from 'lucide-react'
import { XMLStreamDocument, XMLStreamFilter, CustomerCategory } from '@/types/xml-stream.types'
import { XML_CUSTOMER_CATEGORIES, XML_STREAM_TYPES } from '@/types/xml-stream.types'

interface XMLStreamGridProps {
  streams: XMLStreamDocument[]
  filter: XMLStreamFilter
  onFilterChange: (filter: XMLStreamFilter) => void
  onStreamSelect: (stream: XMLStreamDocument) => void
  onStreamUpload: () => void
  loading?: boolean
}

export function XMLStreamGrid({
  streams,
  filter,
  onFilterChange,
  onStreamSelect,
  onStreamUpload,
  loading = false
}: XMLStreamGridProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showFilters, setShowFilters] = useState(false)

  const filteredStreams = useMemo(() => {
    return streams.filter(stream => {
      // Search filter
      if (filter.search) {
        const searchLower = filter.search.toLowerCase()
        const matchesSearch = 
          stream.filename.toLowerCase().includes(searchLower) ||
          stream.xml_metadata.stream_name.toLowerCase().includes(searchLower) ||
          stream.xml_metadata.patterns.some(pattern => 
            pattern.toLowerCase().includes(searchLower)
          )
        if (!matchesSearch) return false
      }

      // Customer category filter
      if (filter.customer_category && filter.customer_category !== 'all') {
        if (stream.xml_metadata.customer_category !== filter.customer_category) {
          return false
        }
      }

      // Stream type filter
      if (filter.stream_type && filter.stream_type !== 'all') {
        if (stream.xml_metadata.stream_type !== filter.stream_type) {
          return false
        }
      }

      // Complexity range filter
      if (filter.complexity_range) {
        const complexity = stream.xml_metadata.complexity_score
        if (complexity < filter.complexity_range.min || complexity > filter.complexity_range.max) {
          return false
        }
      }

      // Job count range filter
      if (filter.job_count_range) {
        const jobCount = stream.xml_metadata.job_count
        if (jobCount < filter.job_count_range.min || jobCount > filter.job_count_range.max) {
          return false
        }
      }

      // Validation status filter
      if (filter.validation_status && filter.validation_status !== 'all') {
        const hasErrors = stream.xml_metadata.validation_results.some(r => r.status === 'error')
        const hasWarnings = stream.xml_metadata.validation_results.some(r => r.status === 'warning')
        
        if (filter.validation_status === 'error' && !hasErrors) return false
        if (filter.validation_status === 'warning' && !hasWarnings) return false
        if (filter.validation_status === 'valid' && (hasErrors || hasWarnings)) return false
      }

      // RAG indexed filter
      if (filter.rag_indexed !== undefined) {
        if (stream.rag_indexed !== filter.rag_indexed) return false
      }

      return true
    })
  }, [streams, filter])

  const getCustomerCategoryColor = (category: CustomerCategory) => {
    const categoryConfig = XML_CUSTOMER_CATEGORIES.find(c => c.value === category)
    return categoryConfig?.color || 'gray'
  }

  const getStreamTypeIcon = (type: string) => {
    const typeConfig = XML_STREAM_TYPES.find(t => t.value === type)
    return typeConfig?.icon || '⚙️'
  }

  const getComplexityColor = (score: number) => {
    if (score < 3) return 'text-green-600 bg-green-100'
    if (score < 6) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getValidationStatus = (validationResults: any[]) => {
    const hasErrors = validationResults.some(r => r.status === 'error')
    const hasWarnings = validationResults.some(r => r.status === 'warning')
    
    if (hasErrors) return { status: 'error', color: 'text-red-600', icon: '❌' }
    if (hasWarnings) return { status: 'warning', color: 'text-yellow-600', icon: '⚠️' }
    return { status: 'valid', color: 'text-green-600', icon: '✅' }
  }

  return (
    <div className="space-y-4">
      {/* Header with Search and Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            XML Streams
          </h2>
          <span className="text-sm text-gray-500">
            {filteredStreams.length} von {streams.length}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onStreamUpload}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            <Upload className="w-4 h-4" />
            <span>Upload</span>
          </button>

          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-lg border transition-colors ${
              showFilters
                ? 'bg-blue-50 border-blue-300 text-blue-600'
                : 'border-gray-300 hover:bg-gray-50'
            }`}
          >
            <Filter className="w-4 h-4" />
          </button>

          <div className="flex border rounded-lg">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 transition-colors ${
                viewMode === 'grid'
                  ? 'bg-blue-50 text-blue-600'
                  : 'hover:bg-gray-50'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 transition-colors ${
                viewMode === 'list'
                  ? 'bg-blue-50 text-blue-600'
                  : 'hover:bg-gray-50'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
        <input
          type="text"
          placeholder="Nach Stream-Namen, Patterns oder Inhalten suchen..."
          value={filter.search}
          onChange={(e) => onFilterChange({ ...filter, search: e.target.value })}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Customer Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Kundenkategorie
              </label>
              <select
                value={filter.customer_category || 'all'}
                onChange={(e) => onFilterChange({ 
                  ...filter, 
                  customer_category: e.target.value as CustomerCategory | 'all'
                })}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Alle Kategorien</option>
                {XML_CUSTOMER_CATEGORIES.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Stream Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Stream-Typ
              </label>
              <select
                value={filter.stream_type || 'all'}
                onChange={(e) => onFilterChange({ 
                  ...filter, 
                  stream_type: e.target.value as any
                })}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Alle Typen</option>
                {XML_STREAM_TYPES.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.icon} {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Validation Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Validierungsstatus
              </label>
              <select
                value={filter.validation_status || 'all'}
                onChange={(e) => onFilterChange({ 
                  ...filter, 
                  validation_status: e.target.value as any
                })}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Alle Status</option>
                <option value="valid">✅ Gültig</option>
                <option value="warning">⚠️ Warnungen</option>
                <option value="error">❌ Fehler</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      )}

      {/* Stream Grid/List */}
      {!loading && (
        <div className={
          viewMode === 'grid'
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
            : 'space-y-3'
        }>
          {filteredStreams.map(stream => {
            const validation = getValidationStatus(stream.xml_metadata.validation_results)
            
            if (viewMode === 'grid') {
              return (
                <div
                  key={stream.id}
                  onClick={() => onStreamSelect(stream)}
                  className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">
                        {getStreamTypeIcon(stream.xml_metadata.stream_type)}
                      </span>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium bg-${getCustomerCategoryColor(stream.xml_metadata.customer_category)}-100 text-${getCustomerCategoryColor(stream.xml_metadata.customer_category)}-700`}>
                        {stream.xml_metadata.customer_category}
                      </div>
                    </div>
                    <span className={`text-lg ${validation.color}`}>
                      {validation.icon}
                    </span>
                  </div>

                  <h3 className="font-medium text-gray-900 dark:text-white mb-1 truncate">
                    {stream.xml_metadata.stream_name}
                  </h3>
                  
                  <p className="text-sm text-gray-500 mb-3 truncate">
                    {stream.filename}
                  </p>

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{stream.xml_metadata.job_count} Jobs</span>
                    <span className={`px-2 py-1 rounded ${getComplexityColor(stream.xml_metadata.complexity_score)}`}>
                      Komplexität {stream.xml_metadata.complexity_score}
                    </span>
                  </div>

                  {stream.xml_metadata.patterns.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
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
                </div>
              )
            } else {
              return (
                <div
                  key={stream.id}
                  onClick={() => onStreamSelect(stream)}
                  className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-sm transition-shadow cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <span className="text-lg">
                        {getStreamTypeIcon(stream.xml_metadata.stream_type)}
                      </span>
                      <div>
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          {stream.xml_metadata.stream_name}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {stream.filename}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className={`px-2 py-1 rounded-full text-xs font-medium bg-${getCustomerCategoryColor(stream.xml_metadata.customer_category)}-100 text-${getCustomerCategoryColor(stream.xml_metadata.customer_category)}-700`}>
                        {stream.xml_metadata.customer_category}
                      </div>
                      <span className="text-sm text-gray-500">
                        {stream.xml_metadata.job_count} Jobs
                      </span>
                      <span className={`px-2 py-1 rounded text-xs ${getComplexityColor(stream.xml_metadata.complexity_score)}`}>
                        K{stream.xml_metadata.complexity_score}
                      </span>
                      <span className={`text-lg ${validation.color}`}>
                        {validation.icon}
                      </span>
                    </div>
                  </div>
                </div>
              )
            }
          })}
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredStreams.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Grid className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Keine XML Streams gefunden
          </h3>
          <p className="text-gray-500 mb-4">
            {streams.length === 0 
              ? 'Laden Sie Ihren ersten XML Stream hoch, um zu beginnen.'
              : 'Passen Sie Ihre Filterkriterien an oder laden Sie neue Streams hoch.'
            }
          </p>
          <button
            onClick={onStreamUpload}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>XML Stream hochladen</span>
          </button>
        </div>
      )}
    </div>
  )
}