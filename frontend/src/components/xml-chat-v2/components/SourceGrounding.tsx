/**
 * Source Grounding Component for LangExtract
 * Displays highlighted parameter sources with confidence indicators
 */

import React from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Check, X, Eye, EyeOff } from 'lucide-react'
import type { SourceGroundingData, SourceGroundedParameter } from '@/types/api.types'

interface SourceGroundingProps {
  sourceGrounding?: SourceGroundingData
  sourceGroundedParameters: SourceGroundedParameter[]
  onParameterConfirm: (parameterName: string, confirmed: boolean) => void
  className?: string
}

export function SourceGrounding({
  sourceGrounding,
  sourceGroundedParameters,
  onParameterConfirm,
  className = ''
}: SourceGroundingProps) {
  const [showFullText, setShowFullText] = React.useState(false)

  if (!sourceGrounding && sourceGroundedParameters.length === 0) {
    return null
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800 border-green-300'
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    return 'bg-red-100 text-red-800 border-red-300'
  }

  const getQualityColor = (quality: 'high' | 'medium' | 'low') => {
    switch (quality) {
      case 'high': return 'bg-green-500'
      case 'medium': return 'bg-yellow-500'
      case 'low': return 'bg-red-500'
    }
  }

  const renderHighlightedText = () => {
    if (!sourceGrounding) return null

    const { full_text, highlighted_ranges } = sourceGrounding
    let lastIndex = 0
    const elements: React.ReactNode[] = []

    // Sort ranges by start position
    const sortedRanges = [...highlighted_ranges].sort((a, b) => a[0] - b[0])

    sortedRanges.forEach(([start, end, paramName], index) => {
      // Add text before highlight
      if (start > lastIndex) {
        elements.push(
          <span key={`text-${index}`} className="text-gray-700">
            {full_text.slice(lastIndex, start)}
          </span>
        )
      }

      // Add highlighted parameter
      const parameter = sourceGroundedParameters.find(p => p.name === paramName)
      const confidence = parameter?.confidence || 0

      elements.push(
        <span
          key={`highlight-${index}`}
          className={`px-1 py-0.5 rounded text-sm font-medium ${getConfidenceColor(confidence)}`}
          title={`${paramName}: ${parameter?.value} (${Math.round(confidence * 100)}% Konfidenz)`}
        >
          {full_text.slice(start, end)}
        </span>
      )

      lastIndex = end
    })

    // Add remaining text
    if (lastIndex < full_text.length) {
      elements.push(
        <span key="text-end" className="text-gray-700">
          {full_text.slice(lastIndex)}
        </span>
      )
    }

    return elements
  }

  return (
    <Card className={`border-blue-200 bg-blue-50/50 ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-blue-900">
            Source Grounding
          </CardTitle>
          <div className="flex items-center gap-2">
            {sourceGrounding && (
              <div className="flex items-center gap-1">
                <div
                  className={`w-2 h-2 rounded-full ${getQualityColor(sourceGrounding.extraction_quality)}`}
                  title={`Extraktionsqualität: ${sourceGrounding.extraction_quality}`}
                />
                <span className="text-xs text-gray-600">
                  {Math.round(sourceGrounding.overall_confidence * 100)}%
                </span>
              </div>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFullText(!showFullText)}
              className="h-6 w-6 p-0"
            >
              {showFullText ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Highlighted Source Text */}
        {sourceGrounding && showFullText && (
          <div className="mb-4 p-3 bg-white rounded border text-sm leading-relaxed">
            {renderHighlightedText()}
          </div>
        )}

        {/* Parameter List */}
        {sourceGroundedParameters.length > 0 && (
          <div className="space-y-2">
            <div className="text-xs font-medium text-gray-600 mb-2">
              Extrahierte Parameter ({sourceGroundedParameters.length})
            </div>

            {sourceGroundedParameters.map((param, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-white rounded border"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm text-gray-900">
                      {param.name}
                    </span>
                    <Badge
                      variant="outline"
                      className={`text-xs ${getConfidenceColor(param.confidence)}`}
                    >
                      {Math.round(param.confidence * 100)}%
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-600 truncate">
                    {typeof param.value === 'object'
                      ? JSON.stringify(param.value)
                      : String(param.value)
                    }
                  </div>
                </div>

                <div className="flex items-center gap-1 ml-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onParameterConfirm(param.name, true)}
                    className={`h-6 w-6 p-0 ${
                      param.user_confirmed
                        ? 'text-green-600 bg-green-100'
                        : 'text-gray-400 hover:text-green-600'
                    }`}
                    title="Parameter bestätigen"
                  >
                    <Check className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onParameterConfirm(param.name, false)}
                    className="h-6 w-6 p-0 text-gray-400 hover:text-red-600"
                    title="Parameter ablehnen"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Quality Indicator */}
        {sourceGrounding && (
          <div className="mt-3 pt-3 border-t border-blue-200">
            <div className="flex items-center justify-between text-xs text-gray-600">
              <span>Extraktionsqualität</span>
              <div className="flex items-center gap-1">
                <span className="capitalize">{sourceGrounding.extraction_quality}</span>
                <div
                  className={`w-2 h-2 rounded-full ${getQualityColor(sourceGrounding.extraction_quality)}`}
                />
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default SourceGrounding