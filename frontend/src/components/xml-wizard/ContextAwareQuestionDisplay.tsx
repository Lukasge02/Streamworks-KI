'use client'

import React from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Brain,
  MessageSquare,
  ArrowRight,
  CheckCircle,
  Lightbulb,
  Zap
} from 'lucide-react'

// ================================
// TYPES
// ================================

export interface ContextAwareQuestionProps {
  originalQuestion: string
  contextAwareQuestion: string
  knownContext: Record<string, any>
  fieldBeingAsked: string
  isVisible?: boolean
  className?: string
}

// ================================
// COMPONENT
// ================================

/**
 * Context-Aware Question Display Component
 *
 * Demonstrates how AI questions evolve based on known context
 * - Shows the difference between generic vs context-aware questions
 * - Highlights referenced context information
 * - Provides transparency in AI reasoning
 */
export const ContextAwareQuestionDisplay: React.FC<ContextAwareQuestionProps> = ({
  originalQuestion,
  contextAwareQuestion,
  knownContext,
  fieldBeingAsked,
  isVisible = true,
  className = ''
}) => {
  const [showComparison, setShowComparison] = React.useState(false)

  const formatFieldLabel = (field: string): string => {
    const labelMap: Record<string, string> = {
      'jobForm.sapSystem': 'SAP System',
      'jobForm.reportName': 'Report Name',
      'jobForm.sourcePath': 'Quell-Pfad',
      'jobForm.targetPath': 'Ziel-Pfad',
      'jobForm.scriptPath': 'Script-Pfad',
      'jobForm.agentName': 'Agent Name',
      'streamProperties.streamName': 'Stream Name',
      'streamProperties.description': 'Beschreibung'
    }

    return labelMap[field] || field.replace(/([A-Z])/g, ' $1')
  }

  const getReferencedContext = (contextAwareQuestion: string, knownContext: Record<string, any>): string[] => {
    const referenced = []

    for (const [key, value] of Object.entries(knownContext)) {
      if (contextAwareQuestion.includes(String(value))) {
        referenced.push(`${key}: "${value}"`)
      }
    }

    return referenced
  }

  const referencedContext = getReferencedContext(contextAwareQuestion, knownContext)
  const hasContextualImprovement = originalQuestion !== contextAwareQuestion

  if (!isVisible) {
    return null
  }

  return (
    <div className={`context-aware-question-display ${className}`}>
      <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/10 dark:to-indigo-900/10 dark:border-blue-800">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <h4 className="font-medium text-blue-900 dark:text-blue-100">
                🧠 Context-Aware Frage
              </h4>
              <Badge variant="outline" className="text-xs border-blue-300 text-blue-700 dark:border-blue-600 dark:text-blue-300">
                Phase 2.2
              </Badge>
            </div>

            {hasContextualImprovement && (
              <button
                onClick={() => setShowComparison(!showComparison)}
                className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 underline decoration-dotted transition-colors"
              >
                {showComparison ? 'Vergleich ausblenden' : 'Vergleich zeigen'}
              </button>
            )}
          </div>
        </CardHeader>

        <CardContent>
          <div className="space-y-4">

            {/* Field Being Asked */}
            <div className="flex items-center gap-2 text-sm text-blue-800 dark:text-blue-200">
              <MessageSquare className="w-4 h-4" />
              <span className="font-medium">Gefragtes Feld:</span>
              <span className="bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded text-xs">
                {formatFieldLabel(fieldBeingAsked)}
              </span>
            </div>

            {/* Context-Aware Question */}
            <div className="bg-white dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-800">
              <div className="flex items-start gap-2 mb-2">
                <Zap className="w-4 h-4 text-blue-500 mt-0.5" />
                <div className="text-sm font-medium text-blue-900 dark:text-blue-100">
                  Context-bewusste Frage:
                </div>
              </div>
              <div className="text-blue-800 dark:text-blue-200 font-medium">
                {contextAwareQuestion}
              </div>
            </div>

            {/* Referenced Context Information */}
            {referencedContext.length > 0 && (
              <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg border border-green-200 dark:border-green-800">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                  <span className="text-sm font-medium text-green-800 dark:text-green-200">
                    Referenzierter Kontext:
                  </span>
                </div>
                <div className="space-y-1">
                  {referencedContext.map((context, index) => (
                    <div key={index} className="text-xs text-green-700 dark:text-green-300 bg-green-100 dark:bg-green-800 px-2 py-1 rounded">
                      {context}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Comparison View */}
            {showComparison && hasContextualImprovement && (
              <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="space-y-3">
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
                    Vergleich: Generisch vs Context-bewusst
                  </div>

                  {/* Original Question */}
                  <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded border border-red-200 dark:border-red-800">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="text-xs font-medium text-red-700 dark:text-red-300">
                        ❌ Generische Frage (ohne Kontext):
                      </div>
                    </div>
                    <div className="text-sm text-red-600 dark:text-red-400">
                      {originalQuestion}
                    </div>
                  </div>

                  <div className="flex justify-center">
                    <ArrowRight className="w-5 h-5 text-gray-400" />
                  </div>

                  {/* Context-Aware Question */}
                  <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded border border-green-200 dark:border-green-800">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="text-xs font-medium text-green-700 dark:text-green-300">
                        ✅ Context-bewusste Frage (mit bekannten Daten):
                      </div>
                    </div>
                    <div className="text-sm text-green-600 dark:text-green-400">
                      {contextAwareQuestion}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Benefits */}
            <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  Vorteile context-bewusster Fragen:
                </span>
              </div>
              <ul className="text-xs text-blue-700 dark:text-blue-300 space-y-1 ml-6">
                <li>• Referenziert bereits bekannte Informationen</li>
                <li>• Reduziert kognitive Last für den Benutzer</li>
                <li>• Zeigt Verständnis des bisherigen Gesprächs</li>
                <li>• Macht den Zusammenhang zwischen Daten deutlich</li>
              </ul>
            </div>

            {/* Technical Implementation Note */}
            <div className="text-center text-xs text-gray-500 dark:text-gray-400 mt-3">
              💡 Phase 2.2: Context-Aware Questions • 🧠 Anti-Repetitive • ⚡ Smart AI
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

/**
 * Hook to manage context-aware question display state
 */
export const useContextAwareQuestionDisplay = () => {
  const [currentDisplay, setCurrentDisplay] = React.useState<ContextAwareQuestionProps | null>(null)

  const showContextAwareQuestion = (props: ContextAwareQuestionProps) => {
    setCurrentDisplay(props)
  }

  const hideContextAwareQuestion = () => {
    setCurrentDisplay(null)
  }

  return {
    currentDisplay,
    showContextAwareQuestion,
    hideContextAwareQuestion
  }
}

export default ContextAwareQuestionDisplay