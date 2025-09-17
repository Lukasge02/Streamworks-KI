/**
 * Memory Visualization Panel
 * Shows what the AI has already understood from the conversation
 * Provides transparency and prevents repetitive questions
 */

import React from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, CheckCircle, Clock, AlertCircle, Zap, Settings } from 'lucide-react'

// ================================
// TYPES
// ================================

export interface RecognizedEntity {
  field: string
  value: any
  confidence: number
  extractedFrom: string
  timestamp: string
  phase?: string
  method?: string  // 'template', 'llm_enhanced', 'hybrid', etc.
}

export interface MemoryVisualizationProps {
  entities: RecognizedEntity[]
  currentPhase: string
  completionPercentage: number
  className?: string
}

// ================================
// HELPER FUNCTIONS
// ================================

const formatEntityLabel = (field: string): string => {
  const labelMap: Record<string, string> = {
    'jobForm.sapSystem': 'SAP System',
    'jobForm.reportName': 'Report Name',
    'jobForm.sourcePath': 'Source Path',
    'jobForm.targetPath': 'Target Path',
    'jobForm.scriptPath': 'Script Path',
    'jobForm.agentName': 'Agent Name',
    'streamProperties.streamName': 'Stream Name',
    'streamProperties.description': 'Description',
    'streamProperties.environment': 'Environment',
    'scheduling.startTime': 'Start Time',
    'scheduling.frequency': 'Frequency',
  }

  return labelMap[field] || field.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())
}

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20'
  if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20'
  return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20'
}

const getConfidenceIcon = (confidence: number) => {
  if (confidence >= 0.8) return <CheckCircle className="w-3 h-3" />
  if (confidence >= 0.6) return <Clock className="w-3 h-3" />
  return <AlertCircle className="w-3 h-3" />
}

const getMethodIcon = (method?: string) => {
  if (method?.includes('llm_enhanced') || method?.includes('openai')) {
    return <Zap className="w-3 h-3 text-blue-500" title="OpenAI Enhanced" />
  }
  if (method?.includes('hybrid')) {
    return <Brain className="w-3 h-3 text-purple-500" title="Hybrid Recognition" />
  }
  return <Settings className="w-3 h-3 text-gray-500" title="Template Based" />
}

const getMethodLabel = (method?: string): string => {
  if (method?.includes('llm_enhanced') || method?.includes('openai')) return 'OpenAI'
  if (method?.includes('hybrid')) return 'Hybrid'
  if (method?.includes('template')) return 'Pattern'
  return method || 'Auto'
}

// ================================
// COMPONENT
// ================================

export const MemoryVisualizationPanel: React.FC<MemoryVisualizationProps> = ({
  entities,
  currentPhase,
  completionPercentage,
  className = ''
}) => {
  // ✅ Enhanced: Animation states for real-time updates
  const [animatedEntities, setAnimatedEntities] = React.useState<Set<string>>(new Set())
  const [prevEntityCount, setPrevEntityCount] = React.useState(0)

  // Track new entities for animation
  React.useEffect(() => {
    if (entities.length > prevEntityCount) {
      // New entities added - animate them
      const newAnimatedSet = new Set<string>()
      entities.slice(prevEntityCount).forEach(entity => {
        newAnimatedSet.add(entity.field)
      })
      setAnimatedEntities(newAnimatedSet)

      // Clear animations after 2 seconds
      setTimeout(() => setAnimatedEntities(new Set()), 2000)
    }
    setPrevEntityCount(entities.length)
  }, [entities.length, prevEntityCount])

  // ✅ Enhanced: Better source attribution formatting
  const formatSourceAttribution = (extractedFrom: string, maxLength: number = 40) => {
    if (!extractedFrom || extractedFrom === 'Previous conversation') {
      return 'aus vorheriger Unterhaltung'
    }

    const cleaned = extractedFrom.trim()
    if (cleaned.length <= maxLength) {
      return `"${cleaned}"`
    }

    return `"${cleaned.substring(0, maxLength)}..."`
  }
  // Group entities by category
  const groupedEntities = entities.reduce((groups, entity) => {
    const category = entity.field.includes('jobForm') ? 'Job Configuration' :
                    entity.field.includes('streamProperties') ? 'Stream Properties' :
                    entity.field.includes('scheduling') ? 'Scheduling' :
                    'Other'

    if (!groups[category]) groups[category] = []
    groups[category].push(entity)
    return groups
  }, {} as Record<string, RecognizedEntity[]>)

  const isEmpty = entities.length === 0

  return (
    <Card className={`memory-visualization-panel ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🧠 Was ich bereits verstanden habe
          </h3>
        </div>

        {/* Progress Indicator */}
        <div className="mt-2">
          <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
            <span>Fortschritt</span>
            <span>{Math.round(completionPercentage * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-purple-600 dark:bg-purple-400 h-2 rounded-full transition-all duration-300"
              style={{ width: `${completionPercentage * 100}%` }}
            />
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Phase: {currentPhase.replace('_', ' ')}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {isEmpty ? (
          <div className="text-center py-6 text-gray-500 dark:text-gray-400">
            <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">
              Noch keine Informationen erkannt.
            </p>
            <p className="text-xs mt-1">
              Beschreiben Sie Ihren gewünschten Stream...
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {Object.entries(groupedEntities).map(([category, categoryEntities]) => (
              <div key={category} className="entity-group">
                <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2 border-b border-gray-200 dark:border-gray-700 pb-1">
                  {category}
                </div>

                <div className="space-y-2">
                  {categoryEntities.map((entity, index) => {
                    const isNewEntity = animatedEntities.has(entity.field)
                    return (
                      <div
                        key={`${entity.field}-${index}`}
                        className={`entity-card bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 border transition-all duration-300 ${
                          isNewEntity
                            ? 'border-green-300 dark:border-green-600 bg-green-50 dark:bg-green-900/20 animate-pulse'
                            : 'border-gray-200 dark:border-gray-700'
                        }`}
                      >
                      {/* Entity Label & Value */}
                      <div className="flex items-center justify-between mb-2">
                        <div className="entity-label text-sm font-medium text-gray-800 dark:text-gray-200">
                          {formatEntityLabel(entity.field)}
                        </div>

                        {/* Confidence & Method Badges */}
                        <div className="flex items-center gap-2">
                          {/* Method Badge */}
                          <Badge
                            variant="outline"
                            className="text-xs border-gray-300 dark:border-gray-600"
                          >
                            <div className="flex items-center gap-1">
                              {getMethodIcon(entity.method)}
                              {getMethodLabel(entity.method)}
                            </div>
                          </Badge>

                          {/* Confidence Badge */}
                          <Badge
                            variant="secondary"
                            className={`text-xs ${getConfidenceColor(entity.confidence)}`}
                          >
                            <div className="flex items-center gap-1">
                              {getConfidenceIcon(entity.confidence)}
                              {Math.round(entity.confidence * 100)}%
                            </div>
                          </Badge>
                        </div>
                      </div>

                      {/* Entity Value */}
                      <div className="entity-value text-sm font-mono bg-white dark:bg-gray-900 px-2 py-1 rounded border text-gray-900 dark:text-gray-100">
                        {String(entity.value)}
                      </div>

                      {/* Enhanced: Entity Meta Information with better source attribution */}
                      <div className="entity-meta mt-2 text-xs text-gray-500 dark:text-gray-400">
                        <div className="flex items-center justify-between">
                          <span
                            title={`Extrahiert aus: "${entity.extractedFrom}"`}
                            className="flex-1 mr-2"
                          >
                            <span className="text-gray-400">von:</span> {formatSourceAttribution(entity.extractedFrom)}
                          </span>
                          <span className="text-gray-400 shrink-0">
                            {new Date(entity.timestamp).toLocaleTimeString('de-DE', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>

                        {/* ✅ New: Show entity freshness indicator */}
                        {isNewEntity && (
                          <div className="mt-1 text-green-600 dark:text-green-400 text-xs font-medium">
                            ✨ Neu hinzugefügt
                          </div>
                        )}
                      </div>
                    </div>
                  )})}
                </div>
              </div>
            ))}

            {/* Enhanced Summary with real-time statistics */}
            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="text-center">
                  <div className="font-medium text-gray-900 dark:text-gray-100">
                    {entities.length}
                  </div>
                  <div className="text-gray-500 dark:text-gray-400">Parameter</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-gray-900 dark:text-gray-100">
                    {Math.round(completionPercentage * 100)}%
                  </div>
                  <div className="text-gray-500 dark:text-gray-400">Vollständig</div>
                </div>
                <div className="text-center">
                  <div className="font-medium text-gray-900 dark:text-gray-100">
                    {Math.round((entities.reduce((sum, e) => sum + e.confidence, 0) / entities.length || 0) * 100)}%
                  </div>
                  <div className="text-gray-500 dark:text-gray-400">Vertrauen</div>
                </div>
              </div>

              {/* Real-time update indicator */}
              <div className="text-center mt-2 text-xs text-gray-500 dark:text-gray-400">
                🧠 Anti-Duplicate • ⚡ Real-time Updates • 🎯 Transparent AI
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ================================
// HOOKS & UTILITIES
// ================================

export const useMemoryVisualization = (conversationState: any) => {
  // ✅ Enhanced: Real-time updates with dependency tracking
  const [lastUpdateTime, setLastUpdateTime] = React.useState<number>(Date.now())

  const entities = React.useMemo(() => {
    if (!conversationState?.collected_data) return []

    // Track when the memory state was last updated
    setLastUpdateTime(Date.now())

    const extractEntities = (data: any, prefix = ''): RecognizedEntity[] => {
      const result: RecognizedEntity[] = []

      Object.entries(data).forEach(([key, value]) => {
        const fullKey = prefix ? `${prefix}.${key}` : key

        if (typeof value === 'object' && value !== null) {
          result.push(...extractEntities(value, fullKey))
        } else {
          // ✅ Enhanced: Better source attribution and metadata
          const entity: RecognizedEntity = {
            field: fullKey,
            value,
            confidence: conversationState.entity_confidences?.[fullKey] || 0.85,
            extractedFrom: conversationState.entity_sources?.[fullKey] ||
                          conversationState.last_user_message ||
                          'Previous conversation',
            timestamp: conversationState.entity_timestamps?.[fullKey] || new Date().toISOString(),
            phase: conversationState.phase,
            method: conversationState.entity_methods?.[fullKey] || 'auto'
          }

          result.push(entity)
        }
      })

      return result
    }

    return extractEntities(conversationState.collected_data)
  }, [conversationState])

  // ✅ Enhanced: Return additional real-time metadata
  return {
    entities,
    currentPhase: conversationState?.phase || 'initialization',
    completionPercentage: conversationState?.completion_percentage || 0,
    lastUpdateTime,
    totalEntities: entities.length,
    entityCountByMethod: entities.reduce((counts, entity) => {
      const method = entity.method || 'auto'
      counts[method] = (counts[method] || 0) + 1
      return counts
    }, {} as Record<string, number>),
    averageConfidence: entities.length > 0
      ? entities.reduce((sum, entity) => sum + entity.confidence, 0) / entities.length
      : 0
  }
}

export default MemoryVisualizationPanel