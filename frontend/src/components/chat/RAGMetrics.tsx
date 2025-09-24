'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart3, Clock, Zap, FileText, Database, Brain,
  ChevronDown, ChevronUp, Info, TrendingUp, Target, Activity, AlertTriangle
} from 'lucide-react'
import { ConfidenceIndicator } from '../ui/StatusIndicator'
import { usePerformanceMetrics } from '../../hooks/usePerformanceMetrics'
import { performanceApi } from '../../services/performance.api'

interface RAGMetricsProps {
  confidence_score?: number
  processing_time?: string
  model_info?: string
  sources?: Array<{
    id: string
    metadata: {
      doc_id?: string
      original_filename?: string
      page_number?: number
      heading?: string
      section?: string
    }
    relevance_score?: number
  }>
  retrieval_context?: {
    total_chunks?: number
    relevant_chunks?: number
    query_type?: string
    mode?: string
  }
  expanded?: boolean
  onToggleExpand?: () => void
}

export const RAGMetrics: React.FC<RAGMetricsProps> = ({
  confidence_score,
  processing_time,
  model_info,
  sources = [],
  retrieval_context,
  expanded = false,
  onToggleExpand
}) => {
  const [showDetails, setShowDetails] = useState(false)

  // Use real performance metrics with unified API
  const {
    dashboardMetrics,
    metrics,
    isLoading,
    isConnected,
    responseTime,
    cacheHitRate,
    sourceQuality: performanceSourceQuality,
    systemHealth,
    activeBottlenecks
  } = usePerformanceMetrics({
    autoRefresh: true,
    refreshInterval: 5000
  })

  // Use real-time performance data with fallbacks to props
  const realProcessingTime = dashboardMetrics?.dashboard_metrics.processing_time.current_ms ||
                            (processing_time ? (
                              typeof processing_time === 'string'
                                ? parseFloat(processing_time.replace('ms', '').replace('s', '000'))
                                : processing_time
                            ) : 0)

  const realSourceQuality = performanceSourceQuality ||
                           (sources.length > 0 ? ((1 - (sources.reduce((sum, source) =>
                           sum + (source.relevance_score || 0.5), 0) / sources.length)) * 100) : 0)

  const realCacheHitRate = cacheHitRate

  const getPerformanceGrade = (timeMs: number) => {
    if (timeMs === 0) return { grade: isLoading ? 'Laden...' : 'N/A', color: 'text-gray-500' }
    if (timeMs < 1000) return { grade: 'Exzellent', color: 'text-emerald-600' }
    if (timeMs < 2000) return { grade: 'Gut', color: 'text-green-600' }
    if (timeMs < 5000) return { grade: 'Mittel', color: 'text-amber-600' }
    return { grade: 'Langsam', color: 'text-red-600' }
  }

  const getQualityGrade = (quality: number) => {
    if (quality === 0) return { label: isLoading ? 'Laden...' : 'Keine Daten', color: 'text-gray-500' }
    if (quality >= 80) return { label: 'Hoch', color: 'text-emerald-600' }
    if (quality >= 60) return { label: 'Mittel', color: 'text-amber-600' }
    return { label: 'Niedrig', color: 'text-red-600' }
  }

  const getCacheGrade = (hitRate: number) => {
    if (hitRate === 0) return { label: isLoading ? 'Laden...' : 'N/A', color: 'text-gray-500' }
    if (hitRate >= 95) return { label: 'Exzellent', color: 'text-emerald-600' }
    if (hitRate >= 85) return { label: 'Gut', color: 'text-green-600' }
    if (hitRate >= 70) return { label: 'Mittel', color: 'text-amber-600' }
    return { label: 'Niedrig', color: 'text-red-600' }
  }

  const performance = getPerformanceGrade(realProcessingTime)
  const qualityGrade = getQualityGrade(realSourceQuality)
  const cacheGrade = getCacheGrade(realCacheHitRate)

  const MetricCard: React.FC<{
    icon: React.ReactNode
    label: string
    value: string | React.ReactNode
    color?: string
    tooltip?: string
  }> = ({ icon, label, value, color, tooltip }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center space-x-2">
          <div className={`p-1 rounded-md ${color || 'bg-gray-100 dark:bg-gray-700'}`}>
            {icon}
          </div>
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
            {label}
          </span>
        </div>
        {tooltip && (
          <div className="group relative">
            <Info className="w-3 h-3 text-gray-400 cursor-help" />
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
              {tooltip}
            </div>
          </div>
        )}
      </div>
      <div className={`text-sm font-semibold ${color || 'text-gray-900 dark:text-white'}`}>
        {value}
      </div>
    </div>
  )

  return (
    <div className="bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
           onClick={() => onToggleExpand?.()}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <BarChart3 className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                Enhanced RAG Metriken
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {isConnected ? 'Live Performance & Source Tracking' : 'Verbindung wird aufgebaut...'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Connection status indicator */}
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}
                 title={isConnected ? 'Live-Daten' : 'Offline'} />

            {/* Confidence score */}
            {confidence_score && (
              <ConfidenceIndicator score={confidence_score} />
            )}

            {/* System health indicator */}
            {systemHealth !== 'unknown' && (
              <div className={`px-2 py-1 rounded text-xs font-medium ${
                systemHealth === 'excellent' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300' :
                systemHealth === 'good' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
              }`}>
                {systemHealth === 'excellent' ? '🟢' : systemHealth === 'good' ? '🟡' : '🔴'}
                {systemHealth === 'excellent' ? 'Optimal' : systemHealth === 'good' ? 'Gut' : 'Degradiert'}
              </div>
            )}

            {expanded ? (
              <ChevronUp className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-gray-200 dark:border-gray-700"
          >
            <div className="p-4 space-y-4">
              {/* Key Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <MetricCard
                  icon={<Zap className="w-3 h-3 text-amber-600" />}
                  label="Verarbeitungszeit"
                  value={
                    <div>
                      <div>{performanceApi.formatDuration(realProcessingTime)}</div>
                      <div className={`text-xs ${performance.color}`}>
                        {performance.grade}
                      </div>
                    </div>
                  }
                  tooltip="Zeit für RAG-Pipeline-Verarbeitung"
                />

                <MetricCard
                  icon={<Target className="w-3 h-3 text-blue-600" />}
                  label="Quellenqualität"
                  value={
                    <div>
                      <div>{Math.round(realSourceQuality)}%</div>
                      <div className={`text-xs ${qualityGrade.color}`}>{qualityGrade.label}</div>
                    </div>
                  }
                  tooltip="Durchschnittliche Relevanz der abgerufenen Quellen"
                />

                <MetricCard
                  icon={<Activity className="w-3 h-3 text-green-600" />}
                  label="Cache Hit-Rate"
                  value={
                    <div>
                      <div>{Math.round(realCacheHitRate)}%</div>
                      <div className={`text-xs ${cacheGrade.color}`}>{cacheGrade.label}</div>
                    </div>
                  }
                  tooltip="Cache-Effizienz für wiederholte Anfragen"
                />

                <MetricCard
                  icon={<Brain className="w-3 h-3 text-purple-600" />}
                  label="Komponenten"
                  value={
                    <div>
                      <div>{dashboardMetrics ? Object.keys(dashboardMetrics.dashboard_metrics.system_health.components).length : (sources.length || 0)}</div>
                      <div className="text-xs text-gray-500">
                        {activeBottlenecks > 0 ? `${activeBottlenecks} Engpässe` : 'Gesund'}
                      </div>
                    </div>
                  }
                  tooltip="Anzahl aktiver Systemkomponenten"
                />
              </div>

              {/* Detailed Metrics */}
              {(retrieval_context || sources.length > 0) && (
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
                  <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    Detaillierte Metriken
                  </h4>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {retrieval_context && (
                      <div className="space-y-2">
                        {retrieval_context.total_chunks && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">Gesamt-Chunks:</span>
                            <span className="font-medium text-gray-900 dark:text-white">
                              {retrieval_context.total_chunks}
                            </span>
                          </div>
                        )}
                        {retrieval_context.relevant_chunks && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">Relevante Chunks:</span>
                            <span className="font-medium text-gray-900 dark:text-white">
                              {retrieval_context.relevant_chunks}
                            </span>
                          </div>
                        )}
                        {retrieval_context.mode && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">Abrufmodus:</span>
                            <span className="font-medium text-gray-900 dark:text-white capitalize">
                              {retrieval_context.mode}
                            </span>
                          </div>
                        )}
                        {retrieval_context.query_type && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">Abfragetyp:</span>
                            <span className="font-medium text-gray-900 dark:text-white capitalize">
                              {retrieval_context.query_type}
                            </span>
                          </div>
                        )}
                      </div>
                    )}

                    {sources.length > 0 && (
                      <div className="space-y-2">
                        <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Verwendete Quellen ({sources.length})
                        </div>
                        {sources.slice(0, 3).map((source, index) => {
                          const filename = source.metadata?.original_filename || 'Unknown Document'
                          const relevanceScore = source.relevance_score || source.score || 0
                          const relevancePercentage = Math.round(relevanceScore * 100)

                          return (
                            <div key={source.id || index} className="flex items-center justify-between text-xs bg-gray-50 dark:bg-gray-800 p-2 rounded">
                              <div className="flex-1 mr-2">
                                <div className="text-gray-600 dark:text-gray-400 truncate font-medium">
                                  {filename}
                                </div>
                                {source.metadata?.page_number && (
                                  <div className="text-gray-500 text-xs">
                                    Seite {source.metadata.page_number}
                                  </div>
                                )}
                              </div>
                              <div className="text-right">
                                <div className={`font-medium ${
                                  relevancePercentage >= 80 ? 'text-emerald-600' :
                                  relevancePercentage >= 60 ? 'text-amber-600' :
                                  'text-red-600'
                                }`}>
                                  {relevancePercentage}%
                                </div>
                                <div className="text-gray-400 text-xs">
                                  Relevanz
                                </div>
                              </div>
                            </div>
                          )
                        })}
                        {sources.length > 3 && (
                          <div className="text-xs text-gray-500 dark:text-gray-400 text-center py-1">
                            +{sources.length - 3} weitere Quellen
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Performance Insights */}
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                <h4 className="text-xs font-semibold text-blue-800 dark:text-blue-200 mb-2 flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  Smart Performance Insights
                </h4>
                <div className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                  {/* Real-time performance insights */}
                  {realProcessingTime > 2000 && (
                    <div className="flex items-center">
                      <AlertTriangle className="w-3 h-3 mr-1 text-amber-500" />
                      Verarbeitungszeit ({performanceApi.formatDuration(realProcessingTime)}) über Zielwert (2s)
                    </div>
                  )}
                  {realCacheHitRate < 85 && (
                    <div className="flex items-center">
                      <Database className="w-3 h-3 mr-1 text-blue-500" />
                      Cache-Effizienz ({Math.round(realCacheHitRate)}%) kann verbessert werden
                    </div>
                  )}
                  {realSourceQuality < 70 && realSourceQuality > 0 && (
                    <div className="flex items-center">
                      <Target className="w-3 h-3 mr-1 text-orange-500" />
                      Quellenqualität ({Math.round(realSourceQuality)}%) benötigt Optimierung
                    </div>
                  )}
                  {confidence_score && confidence_score < 0.7 && (
                    <div className="flex items-center">
                      <Brain className="w-3 h-3 mr-1 text-purple-500" />
                      Niedriges Vertrauen ({Math.round(confidence_score * 100)}%) - mehr Kontext benötigt
                    </div>
                  )}
                  {activeBottlenecks > 0 && (
                    <div className="flex items-center">
                      <AlertTriangle className="w-3 h-3 mr-1 text-red-500" />
                      {activeBottlenecks} aktive Engpässe erkannt - Performance wird beeinträchtigt
                    </div>
                  )}
                  {!isConnected && (
                    <div className="flex items-center">
                      <AlertTriangle className="w-3 h-3 mr-1 text-red-500" />
                      Keine Live-Verbindung - Metriken möglicherweise veraltet
                    </div>
                  )}

                  {/* Positive insights */}
                  {realProcessingTime > 0 && realProcessingTime <= 1000 && realCacheHitRate >= 90 && realSourceQuality >= 80 && (
                    <div className="flex items-center text-emerald-600">
                      <Activity className="w-3 h-3 mr-1" />
                      System läuft optimal - alle Metriken im grünen Bereich
                    </div>
                  )}

                  {/* No issues found */}
                  {realProcessingTime <= 2000 && realCacheHitRate >= 85 && (realSourceQuality >= 70 || realSourceQuality === 0) && activeBottlenecks === 0 && isConnected && (
                    <div className="flex items-center text-green-600">
                      <FileText className="w-3 h-3 mr-1" />
                      Keine Performance-Probleme erkannt - System arbeitet effizient
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default RAGMetrics