/**
 * ContextualSuggestions Component
 * Shows contextual suggestions based on current page location
 */

'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { Lightbulb, MessageSquare } from 'lucide-react'
import { usePageContext } from '@/hooks/usePageContext'

interface ContextualSuggestionsProps {
  onSuggestionClick: (suggestion: string) => void
  className?: string
  showHeader?: boolean
}

export const ContextualSuggestions: React.FC<ContextualSuggestionsProps> = ({
  onSuggestionClick,
  className = '',
  showHeader = true
}) => {
  const { suggestions, pageTitle, pageCategory } = usePageContext()

  if (!suggestions || suggestions.length === 0) {
    return null
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'question': return 'bg-blue-50 hover:bg-blue-100 border-blue-200 text-blue-700'
      case 'action': return 'bg-green-50 hover:bg-green-100 border-green-200 text-green-700'
      case 'help': return 'bg-amber-50 hover:bg-amber-100 border-amber-200 text-amber-700'
      default: return 'bg-gray-50 hover:bg-gray-100 border-gray-200 text-gray-700'
    }
  }

  return (
    <div className={`p-2 ${className}`}>
      <div className="space-y-1">
        {suggestions.slice(0, 4).map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onSuggestionClick(suggestion.text)}
            className={`w-full text-left px-2 py-1.5 text-xs rounded-md border transition-all duration-150 group ${getCategoryColor(suggestion.category || 'question')}`}
          >
            <div className="flex items-center space-x-2">
              {/* Icon */}
              <div className="flex-shrink-0">
                {suggestion.icon ? (
                  <span className="text-xs">{suggestion.icon}</span>
                ) : (
                  <MessageSquare className="w-3 h-3 opacity-60" />
                )}
              </div>

              {/* Text */}
              <span className="font-medium">
                {suggestion.text}
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Show more indicator */}
      {suggestions.length > 4 && (
        <div className="mt-1.5 text-center">
          <p className="text-xs text-gray-400 dark:text-gray-500">
            +{suggestions.length - 4} weitere Vorschläge verfügbar
          </p>
        </div>
      )}

      {/* Footer hint */}
      <div className="mt-2 pt-1.5 border-t border-gray-100 dark:border-gray-700">
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center">
          💡 Du kannst auch direkt deine eigene Frage stellen
        </p>
      </div>
    </div>
  )
}

export default ContextualSuggestions