/**
 * Parameter Provenance Panel
 * Zeigt detaillierte Herkunftsinformationen für alle extrahierten Parameter
 */

'use client'

import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Target,
  MapPin,
  BarChart3,
  Filter,
  CheckCircle,
  AlertTriangle,
  Info,
  Edit3,
  Trash2,
  Eye,
  Zap,
  Clock,
  User,
  Settings,
  FileText
} from 'lucide-react'

// Types
interface SourceGroundedParameter {
  name: string
  value: any
  confidence: number
  source_text: string
  character_offsets: [number, number]
  scope: 'stream' | 'job'
  extraction_method: 'langextract' | 'unified' | 'hybrid'
  data_type: string
  user_confirmed: boolean
  extracted_at: string
  tooltip_info?: string
}

interface ParameterProvenancePanelProps {
  parameters: SourceGroundedParameter[]
  fullText: string
  onParameterEdit?: (parameter: SourceGroundedParameter) => void
  onParameterDelete?: (parameterName: string) => void
  onParameterConfirm?: (parameterName: string) => void
  onViewInContext?: (parameter: SourceGroundedParameter) => void
  showMetrics?: boolean
  className?: string
}

type FilterType = 'all' | 'stream' | 'job' | 'high_confidence' | 'needs_review' | 'confirmed'
type SortType = 'name' | 'confidence' | 'extracted_at' | 'scope'

// Helper functions
const getConfidenceLevel = (confidence: number): 'high' | 'medium' | 'low' | 'very_low' => {
  if (confidence >= 0.9) return 'high'
  if (confidence >= 0.7) return 'medium'
  if (confidence >= 0.5) return 'low'
  return 'very_low'
}

const getConfidenceColor = (confidence: number) => {
  const level = getConfidenceLevel(confidence)
  switch (level) {
    case 'high': return 'text-green-600 bg-green-50 border-green-200'
    case 'medium': return 'text-blue-600 bg-blue-50 border-blue-200'
    case 'low': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'very_low': return 'text-red-600 bg-red-50 border-red-200'
  }
}

const getScopeIcon = (scope: string) => {
  return scope === 'stream' ? Settings : FileText
}

const getScopeColor = (scope: string) => {
  return scope === 'stream'
    ? 'text-blue-600 bg-blue-50 border-blue-200'
    : 'text-purple-600 bg-purple-50 border-purple-200'
}

// Individual Parameter Card Component
interface ParameterCardProps {
  parameter: SourceGroundedParameter
  fullText: string
  onEdit?: (parameter: SourceGroundedParameter) => void
  onDelete?: (parameterName: string) => void
  onConfirm?: (parameterName: string) => void
  onViewInContext?: (parameter: SourceGroundedParameter) => void
}

const ParameterCard: React.FC<ParameterCardProps> = ({
  parameter,
  fullText,
  onEdit,
  onDelete,
  onConfirm,
  onViewInContext
}) => {
  const [expanded, setExpanded] = useState(false)

  const confidenceLevel = getConfidenceLevel(parameter.confidence)
  const ScopeIcon = getScopeIcon(parameter.scope)

  // Generate context preview
  const contextPreview = useMemo(() => {
    const [start, end] = parameter.character_offsets
    const contextStart = Math.max(0, start - 20)
    const contextEnd = Math.min(fullText.length, end + 20)
    const preview = fullText.slice(contextStart, contextEnd)

    return {
      before: preview.slice(0, start - contextStart),
      highlighted: preview.slice(start - contextStart, end - contextStart),
      after: preview.slice(end - contextStart)
    }
  }, [parameter.character_offsets, fullText])

  return (
    <motion.div
      className={`
        border-2 rounded-xl p-4 bg-white transition-all duration-300
        ${parameter.user_confirmed
          ? 'border-green-300 bg-green-50/30'
          : 'border-gray-200 hover:border-gray-300'
        }
        ${confidenceLevel === 'very_low' ? 'border-red-200 bg-red-50/20' : ''}
      `}
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.01 }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg border ${getScopeColor(parameter.scope)}`}>
            <ScopeIcon className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{parameter.name}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className={`
                px-2 py-1 text-xs rounded-full border font-medium
                ${getScopeColor(parameter.scope)}
              `}>
                {parameter.scope}
              </span>
              <span className="text-xs text-gray-500">
                {parameter.data_type}
              </span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1">
          {!parameter.user_confirmed && (
            <button
              onClick={() => onConfirm?.(parameter.name)}
              className="p-1.5 text-green-600 hover:bg-green-50 rounded-md transition-colors"
              title="Parameter bestätigen"
            >
              <CheckCircle className="w-4 h-4" />
            </button>
          )}

          <button
            onClick={() => onEdit?.(parameter)}
            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            title="Parameter bearbeiten"
          >
            <Edit3 className="w-4 h-4" />
          </button>

          <button
            onClick={() => onViewInContext?.(parameter)}
            className="p-1.5 text-gray-600 hover:bg-gray-50 rounded-md transition-colors"
            title="Im Kontext anzeigen"
          >
            <Eye className="w-4 h-4" />
          </button>

          <button
            onClick={() => onDelete?.(parameter.name)}
            className="p-1.5 text-red-600 hover:bg-red-50 rounded-md transition-colors"
            title="Parameter löschen"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Value */}
      <div className="mb-3">
        <div className="text-sm text-gray-600 mb-1">Wert:</div>
        <div className="font-mono text-sm bg-gray-50 p-2 rounded-lg border">
          {typeof parameter.value === 'object'
            ? JSON.stringify(parameter.value, null, 2)
            : String(parameter.value)
          }
        </div>
      </div>

      {/* Confidence */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm text-gray-600">Konfidenz:</span>
          <span className={`
            text-sm font-semibold
            ${confidenceLevel === 'high' ? 'text-green-600' :
              confidenceLevel === 'medium' ? 'text-blue-600' :
              confidenceLevel === 'low' ? 'text-yellow-600' :
              'text-red-600'
            }
          `}>
            {(parameter.confidence * 100).toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div
            className={`
              h-2 rounded-full transition-all duration-500
              ${confidenceLevel === 'high' ? 'bg-green-500' :
                confidenceLevel === 'medium' ? 'bg-blue-500' :
                confidenceLevel === 'low' ? 'bg-yellow-500' :
                'bg-red-500'
              }
            `}
            initial={{ width: 0 }}
            animate={{ width: `${parameter.confidence * 100}%` }}
            transition={{ delay: 0.2, duration: 0.8 }}
          />
        </div>
      </div>

      {/* Source Context */}
      <div className="mb-3">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          <MapPin className="w-4 h-4" />
          Quelle anzeigen
          <motion.div
            animate={{ rotate: expanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            ▼
          </motion.div>
        </button>

        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden mt-2"
            >
              <div className="bg-gray-50 p-3 rounded-lg border text-sm">
                <div className="mb-2">
                  <span className="text-gray-500">Kontext:</span>
                </div>
                <div className="font-mono text-xs leading-relaxed">
                  <span className="text-gray-500">{contextPreview.before}</span>
                  <span className="bg-yellow-200 px-1 py-0.5 rounded font-semibold">
                    {contextPreview.highlighted}
                  </span>
                  <span className="text-gray-500">{contextPreview.after}</span>
                </div>
                <div className="mt-2 text-xs text-gray-400">
                  Position: {parameter.character_offsets[0]}-{parameter.character_offsets[1]}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Metadata */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <Zap className="w-3 h-3" />
            {parameter.extraction_method}
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {new Date(parameter.extracted_at).toLocaleTimeString('de-DE')}
          </div>
        </div>

        {parameter.user_confirmed && (
          <div className="flex items-center gap-1 text-green-600">
            <User className="w-3 h-3" />
            Bestätigt
          </div>
        )}
      </div>
    </motion.div>
  )
}

// Main Panel Component
const ParameterProvenancePanel: React.FC<ParameterProvenancePanelProps> = ({
  parameters,
  fullText,
  onParameterEdit,
  onParameterDelete,
  onParameterConfirm,
  onViewInContext,
  showMetrics = true,
  className = ''
}) => {
  const [filter, setFilter] = useState<FilterType>('all')
  const [sortBy, setSortBy] = useState<SortType>('confidence')
  const [searchTerm, setSearchTerm] = useState('')

  // Filter and sort parameters
  const filteredAndSortedParameters = useMemo(() => {
    let filtered = parameters

    // Apply filters
    switch (filter) {
      case 'stream':
        filtered = filtered.filter(p => p.scope === 'stream')
        break
      case 'job':
        filtered = filtered.filter(p => p.scope === 'job')
        break
      case 'high_confidence':
        filtered = filtered.filter(p => p.confidence >= 0.8)
        break
      case 'needs_review':
        filtered = filtered.filter(p => p.confidence < 0.7 || !p.user_confirmed)
        break
      case 'confirmed':
        filtered = filtered.filter(p => p.user_confirmed)
        break
    }

    // Apply search
    if (searchTerm) {
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        String(p.value).toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.source_text.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name)
        case 'confidence':
          return b.confidence - a.confidence
        case 'extracted_at':
          return new Date(b.extracted_at).getTime() - new Date(a.extracted_at).getTime()
        case 'scope':
          return a.scope.localeCompare(b.scope)
        default:
          return 0
      }
    })

    return filtered
  }, [parameters, filter, sortBy, searchTerm])

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!showMetrics) return null

    const total = parameters.length
    const confirmed = parameters.filter(p => p.user_confirmed).length
    const highConfidence = parameters.filter(p => p.confidence >= 0.8).length
    const needsReview = parameters.filter(p => p.confidence < 0.7 || !p.user_confirmed).length
    const avgConfidence = total > 0 ? parameters.reduce((sum, p) => sum + p.confidence, 0) / total : 0

    const streamParams = parameters.filter(p => p.scope === 'stream').length
    const jobParams = parameters.filter(p => p.scope === 'job').length

    return {
      total,
      confirmed,
      highConfidence,
      needsReview,
      avgConfidence,
      streamParams,
      jobParams
    }
  }, [parameters, showMetrics])

  if (parameters.length === 0) {
    return (
      <div className={`bg-white rounded-xl border-2 border-dashed border-gray-300 p-8 text-center ${className}`}>
        <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-600 mb-2">Keine Parameter extrahiert</h3>
        <p className="text-gray-500">
          Beschreiben Sie Ihren Stream, um Parameter automatisch zu extrahieren.
        </p>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-xl border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Parameter-Herkunft</h2>
              <p className="text-gray-600">Detaillierte Übersicht aller extrahierten Parameter</p>
            </div>
          </div>

          {metrics && (
            <div className="flex items-center gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{metrics.total}</div>
                <div className="text-xs text-gray-500">Total</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{metrics.confirmed}</div>
                <div className="text-xs text-gray-500">Bestätigt</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{metrics.needsReview}</div>
                <div className="text-xs text-gray-500">Review</div>
              </div>
            </div>
          )}
        </div>

        {/* Metrics Bar */}
        {metrics && (
          <motion.div
            className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-gray-50 rounded-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="text-center">
              <BarChart3 className="w-5 h-5 text-blue-500 mx-auto mb-1" />
              <div className="text-sm font-semibold text-gray-900">
                {(metrics.avgConfidence * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">Ø Konfidenz</div>
            </div>
            <div className="text-center">
              <Settings className="w-5 h-5 text-blue-500 mx-auto mb-1" />
              <div className="text-sm font-semibold text-gray-900">{metrics.streamParams}</div>
              <div className="text-xs text-gray-500">Stream</div>
            </div>
            <div className="text-center">
              <FileText className="w-5 h-5 text-purple-500 mx-auto mb-1" />
              <div className="text-sm font-semibold text-gray-900">{metrics.jobParams}</div>
              <div className="text-xs text-gray-500">Job</div>
            </div>
            <div className="text-center">
              <CheckCircle className="w-5 h-5 text-green-500 mx-auto mb-1" />
              <div className="text-sm font-semibold text-gray-900">{metrics.highConfidence}</div>
              <div className="text-xs text-gray-500">Hoch</div>
            </div>
            <div className="text-center">
              <AlertTriangle className="w-5 h-5 text-red-500 mx-auto mb-1" />
              <div className="text-sm font-semibold text-gray-900">{metrics.needsReview}</div>
              <div className="text-xs text-gray-500">Review</div>
            </div>
          </motion.div>
        )}

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-4 mt-4">
          {/* Search */}
          <div className="flex-1 min-w-64">
            <input
              type="text"
              placeholder="Parameter suchen..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as FilterType)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Alle anzeigen</option>
            <option value="stream">Stream Parameter</option>
            <option value="job">Job Parameter</option>
            <option value="high_confidence">Hohe Konfidenz</option>
            <option value="needs_review">Review erforderlich</option>
            <option value="confirmed">Bestätigt</option>
          </select>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortType)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="confidence">Nach Konfidenz</option>
            <option value="name">Nach Name</option>
            <option value="extracted_at">Nach Zeit</option>
            <option value="scope">Nach Bereich</option>
          </select>
        </div>
      </div>

      {/* Parameter Cards */}
      <div className="p-6">
        {filteredAndSortedParameters.length === 0 ? (
          <div className="text-center py-8">
            <Filter className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-600 mb-2">Keine Parameter gefunden</h3>
            <p className="text-gray-500">Versuchen Sie andere Filter-Einstellungen.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            <AnimatePresence>
              {filteredAndSortedParameters.map((parameter, index) => (
                <ParameterCard
                  key={`${parameter.name}-${index}`}
                  parameter={parameter}
                  fullText={fullText}
                  onEdit={onParameterEdit}
                  onDelete={onParameterDelete}
                  onConfirm={onParameterConfirm}
                  onViewInContext={onViewInContext}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  )
}

export default ParameterProvenancePanel
export type { SourceGroundedParameter, FilterType, SortType }