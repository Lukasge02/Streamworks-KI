/**
 * Enhanced Chat Message mit Source Grounding Integration
 * Revolutionäres Chat Message Component mit LangExtract Parameter Highlighting
 */

'use client'

import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bot,
  User,
  Target,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  Edit,
  Eye,
  Zap,
  MapPin,
  Info,
  ChevronDown,
  ChevronUp,
  Settings,
  FileText,
  Sparkles,
  Clock
} from 'lucide-react'

// Import Source Grounding Components
import {
  SourceHighlightedText,
  ParameterProvenancePanel,
  ParameterCorrectionModal,
  type SourceGroundedParameter,
  type EnhancedExtractionResult
} from '../source-grounding'

// Types
interface XMLChatMessage {
  id: string
  sessionId: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: {
    type?: string
    parameters?: any
    nextParameter?: string
    completion?: number
    parameterConfidences?: Record<string, number>
    job_type?: string
    streamType?: string
  }
}

interface EnhancedChatMessageProps {
  message: XMLChatMessage
  extractionResult?: EnhancedExtractionResult
  onParameterEdit?: (parameter: SourceGroundedParameter) => void
  onParameterConfirm?: (parameterName: string) => void
  onParameterDelete?: (parameterName: string) => void
  onViewInContext?: (parameter: SourceGroundedParameter) => void
  showSourceGrounding?: boolean
  interactive?: boolean
  className?: string
}

// Parameter Summary Component
interface ParameterSummaryProps {
  parameters: SourceGroundedParameter[]
  onParameterEdit?: (parameter: SourceGroundedParameter) => void
  onParameterConfirm?: (parameterName: string) => void
  expanded?: boolean
  onToggleExpanded?: () => void
}

const ParameterSummary: React.FC<ParameterSummaryProps> = ({
  parameters,
  onParameterEdit,
  onParameterConfirm,
  expanded = false,
  onToggleExpanded
}) => {
  if (parameters.length === 0) return null

  const streamParams = parameters.filter(p => p.scope === 'stream')
  const jobParams = parameters.filter(p => p.scope === 'job')
  const avgConfidence = parameters.reduce((sum, p) => sum + p.confidence, 0) / parameters.length
  const highConfidenceCount = parameters.filter(p => p.confidence >= 0.8).length
  const needsReviewCount = parameters.filter(p => p.confidence < 0.7 || !p.user_confirmed).length

  return (
    <motion.div
      className="mt-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      {/* Summary Header */}
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500 rounded-lg">
              <Target className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">
                {parameters.length} Parameter extrahiert
              </h4>
              <p className="text-sm text-gray-600">
                {streamParams.length} Stream • {jobParams.length} Job-spezifisch
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Confidence Indicator */}
            <div className="text-center">
              <div className={`
                text-lg font-bold
                ${avgConfidence >= 0.8 ? 'text-green-600' :
                  avgConfidence >= 0.6 ? 'text-yellow-600' :
                  'text-red-600'
                }
              `}>
                {(avgConfidence * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500">Ø Konfidenz</div>
            </div>

            {/* Expand/Collapse Button */}
            {onToggleExpanded && (
              <button
                onClick={onToggleExpanded}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-white rounded-lg transition-colors"
              >
                {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-white rounded-lg border">
            <CheckCircle className="w-5 h-5 text-green-500 mx-auto mb-1" />
            <div className="font-semibold text-gray-900">{highConfidenceCount}</div>
            <div className="text-xs text-gray-500">Hohe Konfidenz</div>
          </div>
          <div className="text-center p-3 bg-white rounded-lg border">
            <AlertTriangle className="w-5 h-5 text-yellow-500 mx-auto mb-1" />
            <div className="font-semibold text-gray-900">{needsReviewCount}</div>
            <div className="text-xs text-gray-500">Review nötig</div>
          </div>
          <div className="text-center p-3 bg-white rounded-lg border">
            <BarChart3 className="w-5 h-5 text-blue-500 mx-auto mb-1" />
            <div className="font-semibold text-gray-900">{parameters.length}</div>
            <div className="text-xs text-gray-500">Gesamt</div>
          </div>
        </div>

        {/* Parameter Quick List */}
        {!expanded && parameters.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {parameters.slice(0, 6).map((param, index) => (
              <motion.button
                key={param.name}
                onClick={() => onParameterEdit?.(param)}
                className={`
                  px-3 py-1 rounded-full text-xs font-medium border-2 transition-all duration-200
                  ${param.scope === 'stream'
                    ? 'bg-blue-50 text-blue-700 border-blue-200 hover:border-blue-400'
                    : 'bg-purple-50 text-purple-700 border-purple-200 hover:border-purple-400'
                  }
                  ${param.confidence >= 0.8 ? 'ring-2 ring-green-200' : ''}
                  ${param.confidence < 0.7 ? 'ring-2 ring-yellow-200' : ''}
                `}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                {param.name}
                <span className="ml-1 opacity-75">
                  {(param.confidence * 100).toFixed(0)}%
                </span>
              </motion.button>
            ))}
            {parameters.length > 6 && (
              <span className="px-3 py-1 text-xs text-gray-500">
                +{parameters.length - 6} weitere...
              </span>
            )}
          </div>
        )}
      </div>

      {/* Expanded Parameter List */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-blue-200 bg-white"
          >
            <div className="p-4">
              <ParameterProvenancePanel
                parameters={parameters}
                fullText="" // Would need to be passed from parent
                onParameterEdit={onParameterEdit}
                onParameterConfirm={onParameterConfirm}
                showMetrics={false}
                className="border-0 bg-transparent"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Extraction Quality Indicator
interface ExtractionQualityProps {
  quality: string
  confidence: number
  extractionTime: number
}

const ExtractionQualityIndicator: React.FC<ExtractionQualityProps> = ({
  quality,
  confidence,
  extractionTime
}) => {
  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'high': return 'text-green-600 bg-green-50 border-green-200'
      case 'medium': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'low': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'needs_review': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getQualityIcon = (quality: string) => {
    switch (quality) {
      case 'high': return CheckCircle
      case 'medium': return Info
      case 'low': return AlertTriangle
      case 'needs_review': return AlertTriangle
      default: return Info
    }
  }

  const QualityIcon = getQualityIcon(quality)

  return (
    <div className={`
      inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border
      ${getQualityColor(quality)}
    `}>
      <QualityIcon className="w-3 h-3" />
      <span className="capitalize">{quality}</span>
      <span className="opacity-75">•</span>
      <span>{(confidence * 100).toFixed(0)}%</span>
      <span className="opacity-75">•</span>
      <Clock className="w-3 h-3" />
      <span>{extractionTime.toFixed(1)}s</span>
    </div>
  )
}

// Main Enhanced Chat Message Component
const EnhancedChatMessage: React.FC<EnhancedChatMessageProps> = ({
  message,
  extractionResult,
  onParameterEdit,
  onParameterConfirm,
  onParameterDelete,
  onViewInContext,
  showSourceGrounding = true,
  interactive = true,
  className = ''
}) => {
  const [expanded, setExpanded] = useState(false)
  const [selectedParameter, setSelectedParameter] = useState<SourceGroundedParameter | null>(null)
  const [showCorrectionModal, setShowCorrectionModal] = useState(false)

  // Combine all parameters
  const allParameters = useMemo(() => {
    if (!extractionResult) return []
    return [...extractionResult.stream_parameters, ...extractionResult.job_parameters]
  }, [extractionResult])

  // Check if this is a user message with source grounding
  const isUserWithGrounding = message.role === 'user' && extractionResult && allParameters.length > 0

  const handleParameterClick = (parameter: SourceGroundedParameter) => {
    setSelectedParameter(parameter)
    if (interactive) {
      onViewInContext?.(parameter)
    }
  }

  const handleParameterEdit = (parameter: SourceGroundedParameter) => {
    setSelectedParameter(parameter)
    setShowCorrectionModal(true)
  }

  const handleCorrectionSave = (parameterName: string, newValue: any, reason?: string) => {
    // This would call the parent's onParameterEdit
    if (selectedParameter) {
      const updatedParameter = { ...selectedParameter, value: newValue }
      onParameterEdit?.(updatedParameter)
    }
    setShowCorrectionModal(false)
    setSelectedParameter(null)
  }

  const roleConfig = {
    user: {
      icon: User,
      bgColor: 'bg-blue-600',
      textColor: 'text-white',
      alignment: 'flex-row-reverse',
      bubbleColor: 'bg-blue-600 text-white'
    },
    assistant: {
      icon: Bot,
      bgColor: 'bg-gradient-to-br from-purple-600 to-indigo-600',
      textColor: 'text-white',
      alignment: 'flex-row',
      bubbleColor: 'bg-white text-gray-900 border border-gray-200'
    },
    system: {
      icon: Settings,
      bgColor: 'bg-gray-600',
      textColor: 'text-white',
      alignment: 'flex-row',
      bubbleColor: 'bg-gray-100 text-gray-700 border border-gray-300'
    }
  }

  const config = roleConfig[message.role]
  const RoleIcon = config.icon

  return (
    <motion.div
      className={`flex items-start gap-4 p-6 ${config.alignment} ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Avatar */}
      <motion.div
        className={`
          flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-lg
          ${config.bgColor}
        `}
        whileHover={{ scale: 1.1 }}
        transition={{ type: "spring", stiffness: 300 }}
      >
        <RoleIcon className={`w-5 h-5 ${config.textColor}`} />
      </motion.div>

      {/* Message Content */}
      <div className="flex-1 max-w-4xl">
        {/* Message Bubble */}
        <motion.div
          className={`
            p-4 rounded-2xl shadow-sm
            ${config.bubbleColor}
            ${message.role === 'user' ? 'rounded-tr-md' : 'rounded-tl-md'}
          `}
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.3 }}
        >
          {/* Source Highlighted Content for User Messages */}
          {isUserWithGrounding && showSourceGrounding ? (
            <div className="space-y-3">
              <div className="text-sm text-blue-600 font-medium mb-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Parameter-Extraktion erkannt:
              </div>
              <SourceHighlightedText
                text={message.content}
                parameters={allParameters}
                onParameterClick={handleParameterClick}
                onParameterEdit={handleParameterEdit}
                showConfidence={true}
                interactive={interactive}
                className="text-base leading-relaxed"
              />
            </div>
          ) : (
            <div className="text-base leading-relaxed">
              {message.content}
            </div>
          )}

          {/* Extraction Quality Indicator */}
          {extractionResult && message.role === 'user' && (
            <div className="mt-3 flex items-center justify-between">
              <ExtractionQualityIndicator
                quality={extractionResult.extraction_quality}
                confidence={extractionResult.overall_confidence}
                extractionTime={extractionResult.extraction_duration}
              />

              {extractionResult.detected_job_type && (
                <div className="flex items-center gap-2 text-xs text-blue-600">
                  <FileText className="w-3 h-3" />
                  <span>{extractionResult.detected_job_type}</span>
                  <span className="opacity-75">
                    ({(extractionResult.job_type_confidence * 100).toFixed(0)}%)
                  </span>
                </div>
              )}
            </div>
          )}
        </motion.div>

        {/* Parameter Summary (for messages with extractions) */}
        {isUserWithGrounding && (
          <ParameterSummary
            parameters={allParameters}
            onParameterEdit={handleParameterEdit}
            onParameterConfirm={onParameterConfirm}
            expanded={expanded}
            onToggleExpanded={() => setExpanded(!expanded)}
          />
        )}

        {/* Assistant Message Metadata */}
        {message.role === 'assistant' && message.metadata && (
          <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              <span>{new Date(message.timestamp).toLocaleTimeString('de-DE')}</span>
            </div>

            {message.metadata.job_type && (
              <div className="flex items-center gap-1">
                <Settings className="w-3 h-3" />
                <span>{message.metadata.job_type}</span>
              </div>
            )}

            {message.metadata.completion && (
              <div className="flex items-center gap-1">
                <BarChart3 className="w-3 h-3" />
                <span>{message.metadata.completion}% vollständig</span>
              </div>
            )}
          </div>
        )}

        {/* Timestamp for other message types */}
        {message.role !== 'assistant' && (
          <div className="mt-2 text-xs text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString('de-DE')}
          </div>
        )}
      </div>

      {/* Parameter Correction Modal */}
      <ParameterCorrectionModal
        isOpen={showCorrectionModal}
        parameter={selectedParameter}
        fullText={message.content}
        onClose={() => {
          setShowCorrectionModal(false)
          setSelectedParameter(null)
        }}
        onSave={handleCorrectionSave}
        onCancel={() => {
          setShowCorrectionModal(false)
          setSelectedParameter(null)
        }}
      />
    </motion.div>
  )
}

export default EnhancedChatMessage
export type { EnhancedChatMessageProps, XMLChatMessage }