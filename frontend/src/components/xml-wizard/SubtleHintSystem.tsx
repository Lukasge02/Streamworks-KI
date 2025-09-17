'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import {
  Info,
  Code,
  FileText,
  CheckCircle,
  Lightbulb
} from 'lucide-react'
// Temporary type definition - will be moved to new service
type ContextualHint = {
  id: string
  type: 'format' | 'example' | 'context' | 'validation'
  text: string
  icon?: string
  example?: string
  interactive?: boolean
}

interface SubtleHintSystemProps {
  hints: ContextualHint[]
  onHintUsage?: (hint: ContextualHint) => void
}

/**
 * Subtle Hint System - Non-intrusive guidance for XML Stream Creation
 *
 * Features:
 * - Contextual hints instead of pushy suggestion buttons
 * - Visual hierarchy with icons and colors
 * - Optional interactive elements for format examples
 * - Elegant design that doesn't overwhelm users
 */
export const SubtleHintSystem: React.FC<SubtleHintSystemProps> = ({
  hints,
  onHintUsage
}) => {
  if (!hints || hints.length === 0) {
    return null
  }

  const getHintIcon = (type: ContextualHint['type']) => {
    switch (type) {
      case 'format':
        return <Code className="w-4 h-4" />
      case 'example':
        return <FileText className="w-4 h-4" />
      case 'context':
        return <Info className="w-4 h-4" />
      case 'validation':
        return <CheckCircle className="w-4 h-4" />
      default:
        return <Lightbulb className="w-4 h-4" />
    }
  }

  const getHintColor = (type: ContextualHint['type']) => {
    switch (type) {
      case 'format':
        return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800'
      case 'example':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800'
      case 'context':
        return 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/10 border-purple-200 dark:border-purple-800'
      case 'validation':
        return 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/10 border-orange-200 dark:border-orange-800'
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/10 border-gray-200 dark:border-gray-800'
    }
  }

  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="w-4 h-4 text-amber-500" />
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Hilfreiche Hinweise
        </span>
      </div>

      <div className="space-y-2">
        {hints.map((hint) => (
          <Card
            key={hint.id}
            className={`border transition-all duration-200 hover:shadow-sm ${getHintColor(hint.type)}`}
          >
            <CardContent className="p-3">
              <div className="flex items-start gap-3">
                {/* Hint Icon */}
                <div className={`mt-0.5 ${getHintColor(hint.type)}`}>
                  {hint.icon ? (
                    <span className="text-base" role="img" aria-label="hint">
                      {hint.icon}
                    </span>
                  ) : (
                    getHintIcon(hint.type)
                  )}
                </div>

                {/* Hint Content */}
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed">
                    {hint.text}
                  </div>

                  {/* Optional Example */}
                  {hint.example && (
                    <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-800 rounded text-xs font-mono text-gray-600 dark:text-gray-400">
                      {hint.example}
                    </div>
                  )}

                  {/* Subtle Interactive Element */}
                  {hint.interactive && onHintUsage && (
                    <div className="mt-2">
                      <button
                        onClick={() => onHintUsage(hint)}
                        className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 underline decoration-dotted transition-colors"
                      >
                        Als Beispiel verwenden
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

/**
 * Hook for processing legacy suggestions into contextual hints
 */
export const useLegacySuggestionTransform = (suggestions: string[]): ContextualHint[] => {
  return React.useMemo(() => {
    return suggestions.map((suggestion, index) => {
      // Smart categorization based on content
      let type: ContextualHint['type'] = 'context'
      let icon = '💡'

      if (suggestion.includes('Format') || suggestion.includes('Zeichen') || suggestion.includes('Pfad')) {
        type = 'format'
        icon = '📝'
      } else if (suggestion.includes('Beispiel') || suggestion.includes('z.B.')) {
        type = 'example'
        icon = '📋'
      } else if (suggestion.includes('Validation') || suggestion.includes('Prüfung')) {
        type = 'validation'
        icon = '✅'
      }

      return {
        id: `hint-${index}`,
        type,
        text: suggestion,
        icon,
        interactive: false // Non-intrusive by default
      }
    })
  }, [suggestions])
}