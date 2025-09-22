/**
 * Source Highlighted Text Component
 * Revolutionäre Text-Darstellung mit Source Grounding für Parameter-Extraktion
 */

'use client'

import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Info,
  CheckCircle,
  AlertCircle,
  Edit,
  Eye,
  Target,
  Zap
} from 'lucide-react'

// Types
interface SourceGroundedParameter {
  name: string
  value: any
  confidence: number
  source_text: string
  character_offsets: [number, number]
  highlight_color?: string
  tooltip_info?: string
  scope: 'stream' | 'job'
  extraction_method: 'langextract' | 'unified' | 'hybrid'
}

interface HighlightRange {
  start: number
  end: number
  parameter_name: string
  color?: string
}

interface SourceHighlightedTextProps {
  text: string
  parameters: SourceGroundedParameter[]
  onParameterClick?: (parameter: SourceGroundedParameter) => void
  onParameterHover?: (parameter: SourceGroundedParameter | null) => void
  onParameterEdit?: (parameter: SourceGroundedParameter) => void
  showConfidence?: boolean
  showTooltips?: boolean
  highlightMode?: 'confidence' | 'scope' | 'all'
  interactive?: boolean
  className?: string
}

interface HighlightedSpanProps {
  text: string
  parameter: SourceGroundedParameter
  onClick?: () => void
  onHover?: (hover: boolean) => void
  onEdit?: () => void
  showConfidence?: boolean
  interactive?: boolean
}

// Confidence-based color mapping
const getConfidenceColor = (confidence: number, scope: string) => {
  const alpha = confidence * 0.3 + 0.1 // 0.1 to 0.4 opacity

  if (confidence >= 0.9) {
    return scope === 'stream'
      ? `rgba(34, 197, 94, ${alpha})` // Green for high confidence stream
      : `rgba(59, 130, 246, ${alpha})` // Blue for high confidence job
  } else if (confidence >= 0.7) {
    return scope === 'stream'
      ? `rgba(168, 85, 247, ${alpha})` // Purple for medium confidence stream
      : `rgba(147, 51, 234, ${alpha})` // Purple for medium confidence job
  } else if (confidence >= 0.5) {
    return `rgba(251, 191, 36, ${alpha})` // Amber for low confidence
  } else {
    return `rgba(239, 68, 68, ${alpha})` // Red for very low confidence
  }
}

const getConfidenceBorderColor = (confidence: number) => {
  if (confidence >= 0.9) return '#10b981' // Green
  if (confidence >= 0.7) return '#3b82f6' // Blue
  if (confidence >= 0.5) return '#f59e0b' // Amber
  return '#ef4444' // Red
}

const getConfidenceIcon = (confidence: number) => {
  if (confidence >= 0.9) return CheckCircle
  if (confidence >= 0.7) return Info
  if (confidence >= 0.5) return AlertCircle
  return AlertCircle
}

// Individual Highlighted Span Component
const HighlightedSpan: React.FC<HighlightedSpanProps> = ({
  text,
  parameter,
  onClick,
  onHover,
  onEdit,
  showConfidence = true,
  interactive = true
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const [showTooltip, setShowTooltip] = useState(false)

  const backgroundColor = useMemo(() =>
    getConfidenceColor(parameter.confidence, parameter.scope),
    [parameter.confidence, parameter.scope]
  )

  const borderColor = useMemo(() =>
    getConfidenceBorderColor(parameter.confidence),
    [parameter.confidence]
  )

  const ConfidenceIcon = getConfidenceIcon(parameter.confidence)

  const handleMouseEnter = () => {
    setIsHovered(true)
    setShowTooltip(true)
    onHover?.(true)
  }

  const handleMouseLeave = () => {
    setIsHovered(false)
    setShowTooltip(false)
    onHover?.(false)
  }

  const handleClick = () => {
    if (interactive && onClick) {
      onClick()
    }
  }

  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onEdit?.()
  }

  return (
    <span className="relative inline-block">
      <motion.span
        className={`
          relative inline-block px-1 py-0.5 rounded-sm border-2 transition-all duration-200
          ${interactive ? 'cursor-pointer' : 'cursor-default'}
          ${isHovered ? 'scale-105 shadow-lg z-10' : 'z-0'}
        `}
        style={{
          backgroundColor,
          borderColor,
          borderStyle: isHovered ? 'solid' : 'dashed'
        }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        whileHover={interactive ? { scale: 1.02 } : undefined}
        whileTap={interactive ? { scale: 0.98 } : undefined}
      >
        {text}

        {/* Confidence Indicator */}
        {showConfidence && (
          <motion.div
            className="absolute -top-1 -right-1"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1 }}
          >
            <ConfidenceIcon
              className={`w-3 h-3 ${
                parameter.confidence >= 0.7 ? 'text-green-600' :
                parameter.confidence >= 0.5 ? 'text-yellow-600' :
                'text-red-600'
              }`}
            />
          </motion.div>
        )}

        {/* Edit Button on Hover */}
        {interactive && isHovered && onEdit && (
          <motion.button
            className="absolute -top-1 -left-1 w-4 h-4 bg-blue-500 text-white rounded-full flex items-center justify-center"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            onClick={handleEditClick}
            title="Parameter bearbeiten"
          >
            <Edit className="w-2 h-2" />
          </motion.button>
        )}
      </motion.span>

      {/* Enhanced Tooltip */}
      <AnimatePresence>
        {showTooltip && (
          <motion.div
            className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-50"
            initial={{ opacity: 0, y: 10, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.8 }}
            transition={{ duration: 0.2 }}
          >
            <div className="bg-white border border-gray-200 rounded-lg shadow-xl p-3 min-w-64 max-w-80">
              {/* Parameter Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-blue-500" />
                  <span className="font-semibold text-gray-900">{parameter.name}</span>
                  <span className={`
                    px-2 py-1 text-xs rounded-full font-medium
                    ${parameter.scope === 'stream'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-purple-100 text-purple-800'
                    }
                  `}>
                    {parameter.scope}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Zap className="w-3 h-3 text-gray-400" />
                  <span className="text-xs text-gray-500">{parameter.extraction_method}</span>
                </div>
              </div>

              {/* Parameter Value */}
              <div className="mb-2">
                <div className="text-sm text-gray-600">Wert:</div>
                <div className="font-mono text-sm bg-gray-50 p-1 rounded border">
                  {typeof parameter.value === 'object'
                    ? JSON.stringify(parameter.value, null, 2)
                    : String(parameter.value)
                  }
                </div>
              </div>

              {/* Confidence Score */}
              <div className="mb-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Konfidenz:</span>
                  <span className={`
                    font-semibold text-sm
                    ${parameter.confidence >= 0.7 ? 'text-green-600' :
                      parameter.confidence >= 0.5 ? 'text-yellow-600' :
                      'text-red-600'
                    }
                  `}>
                    {(parameter.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                  <div
                    className={`
                      h-1.5 rounded-full transition-all duration-300
                      ${parameter.confidence >= 0.7 ? 'bg-green-500' :
                        parameter.confidence >= 0.5 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }
                    `}
                    style={{ width: `${parameter.confidence * 100}%` }}
                  />
                </div>
              </div>

              {/* Source Information */}
              <div className="mb-2">
                <div className="text-sm text-gray-600 mb-1">Quelle:</div>
                <div className="text-xs text-gray-500 bg-gray-50 p-1 rounded border">
                  ""{parameter.source_text}""
                  <div className="mt-1 text-gray-400">
                    Position: {parameter.character_offsets[0]}-{parameter.character_offsets[1]}
                  </div>
                </div>
              </div>

              {/* Additional Info */}
              {parameter.tooltip_info && (
                <div className="text-xs text-gray-500 border-t pt-2">
                  <Eye className="w-3 h-3 inline mr-1" />
                  {parameter.tooltip_info}
                </div>
              )}

              {/* Actions */}
              {interactive && (
                <div className="flex gap-2 mt-3 pt-2 border-t">
                  <button
                    onClick={handleClick}
                    className="flex-1 px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                  >
                    Details
                  </button>
                  {onEdit && (
                    <button
                      onClick={handleEditClick}
                      className="flex-1 px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
                    >
                      Bearbeiten
                    </button>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  )
}

// Main Source Highlighted Text Component
const SourceHighlightedText: React.FC<SourceHighlightedTextProps> = ({
  text,
  parameters,
  onParameterClick,
  onParameterHover,
  onParameterEdit,
  showConfidence = true,
  showTooltips = true,
  highlightMode = 'all',
  interactive = true,
  className = ''
}) => {
  const [hoveredParameter, setHoveredParameter] = useState<string | null>(null)

  // Create highlight ranges and merge overlapping ones
  const highlightRanges = useMemo(() => {
    const ranges: HighlightRange[] = parameters.map(param => ({
      start: param.character_offsets[0],
      end: param.character_offsets[1],
      parameter_name: param.name,
      color: param.highlight_color
    }))

    // Sort by start position
    ranges.sort((a, b) => a.start - b.start)

    // Merge overlapping ranges
    const merged: HighlightRange[] = []
    for (const range of ranges) {
      if (merged.length === 0 || merged[merged.length - 1].end < range.start) {
        merged.push(range)
      } else {
        // Merge with previous range
        const prev = merged[merged.length - 1]
        prev.end = Math.max(prev.end, range.end)
        prev.parameter_name += `, ${range.parameter_name}`
      }
    }

    return merged
  }, [parameters])

  // Render highlighted text
  const renderHighlightedText = () => {
    if (parameters.length === 0) {
      return <span className="text-gray-800">{text}</span>
    }

    const elements: React.ReactNode[] = []
    let currentIndex = 0

    // Sort parameters by start position
    const sortedParameters = [...parameters].sort(
      (a, b) => a.character_offsets[0] - b.character_offsets[0]
    )

    sortedParameters.forEach((param, index) => {
      const [start, end] = param.character_offsets

      // Add text before highlight
      if (currentIndex < start) {
        elements.push(
          <span key={`text-${index}`} className="text-gray-800">
            {text.slice(currentIndex, start)}
          </span>
        )
      }

      // Add highlighted span
      const highlightedText = text.slice(start, end)
      if (highlightedText) {
        elements.push(
          <HighlightedSpan
            key={`highlight-${param.name}-${index}`}
            text={highlightedText}
            parameter={param}
            onClick={() => onParameterClick?.(param)}
            onHover={(hover) => {
              setHoveredParameter(hover ? param.name : null)
              onParameterHover?.(hover ? param : null)
            }}
            onEdit={() => onParameterEdit?.(param)}
            showConfidence={showConfidence}
            interactive={interactive}
          />
        )
      }

      currentIndex = Math.max(currentIndex, end)
    })

    // Add remaining text
    if (currentIndex < text.length) {
      elements.push(
        <span key="text-end" className="text-gray-800">
          {text.slice(currentIndex)}
        </span>
      )
    }

    return elements
  }

  return (
    <div className={`relative leading-relaxed ${className}`}>
      <div className="text-sm">
        {renderHighlightedText()}
      </div>

      {/* Parameter Count Indicator */}
      {parameters.length > 0 && (
        <motion.div
          className="absolute -top-2 -right-2 bg-blue-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          {parameters.length}
        </motion.div>
      )}

      {/* Hovered Parameter Info */}
      {hoveredParameter && (
        <motion.div
          className="absolute -bottom-8 left-0 right-0 text-center"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          <div className="bg-gray-800 text-white text-xs px-2 py-1 rounded-md">
            Parameter: {hoveredParameter}
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default SourceHighlightedText
export type { SourceGroundedParameter, HighlightRange }