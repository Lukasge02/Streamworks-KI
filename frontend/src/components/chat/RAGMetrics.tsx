'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart3, Clock, Zap, FileText, Database, Brain,
  ChevronDown, ChevronUp, Info, TrendingUp, Target
} from 'lucide-react'
import { ConfidenceIndicator } from '../ui/StatusIndicator'

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

  const getPerformanceGrade = (time?: string) => {
    if (!time) return { grade: 'N/A', color: 'text-gray-500' }

    const timeMs = parseFloat(time.replace('ms', '').replace('s', '000'))
    if (timeMs < 1000) return { grade: 'Exzellent', color: 'text-emerald-600' }
    if (timeMs < 3000) return { grade: 'Gut', color: 'text-green-600' }
    if (timeMs < 5000) return { grade: 'Mittel', color: 'text-amber-600' }
    return { grade: 'Langsam', color: 'text-red-600' }
  }

  const getSourceQuality = () => {
    if (sources.length === 0) return { score: 0, label: 'Keine Quellen' }

    const avgRelevance = sources.reduce((sum, source) =>
      sum + (source.relevance_score || 0.5), 0) / sources.length

    const quality = 1 - avgRelevance // Invert so higher is better

    if (quality >= 0.8) return { score: Math.round(quality * 100), label: 'Hoch' }
    if (quality >= 0.6) return { score: Math.round(quality * 100), label: 'Mittel' }
    return { score: Math.round(quality * 100), label: 'Niedrig' }
  }

  const performance = getPerformanceGrade(processing_time)
  const sourceQuality = getSourceQuality()

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
                RAG Performance Metriken
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Echtzeit-Analyse der Abruf- und Verarbeitungsqualität
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {confidence_score && (
              <ConfidenceIndicator score={confidence_score} />
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
                      <div>{processing_time || 'N/A'}</div>
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
                      <div>{sourceQuality.score}%</div>
                      <div className="text-xs text-gray-500">{sourceQuality.label}</div>
                    </div>
                  }
                  tooltip="Durchschnittliche Relevanz der abgerufenen Quellen"
                />

                <MetricCard
                  icon={<FileText className="w-3 h-3 text-green-600" />}
                  label="Quellenanzahl"
                  value={sources.length}
                  tooltip="Anzahl der für die Antwort verwendeten Dokumente"
                />

                <MetricCard
                  icon={<Brain className="w-3 h-3 text-purple-600" />}
                  label="Modell"
                  value={model_info?.split('-')[0] || 'N/A'}
                  tooltip="Verwendetes KI-Modell"
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
                          Top Quellen
                        </div>
                        {sources.slice(0, 3).map((source, index) => (
                          <div key={index} className="flex items-center justify-between text-xs">
                            <span className="text-gray-600 dark:text-gray-400 truncate flex-1 mr-2">
                              {source.metadata.original_filename || `Quelle ${index + 1}`}
                            </span>
                            <span className="font-medium text-gray-900 dark:text-white">
                              {source.relevance_score !== undefined
                                ? `${Math.round((1 - source.relevance_score) * 100)}%`
                                : 'N/A'}
                            </span>
                          </div>
                        ))}
                        {sources.length > 3 && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">
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
                <h4 className="text-xs font-semibold text-blue-800 dark:text-blue-200 mb-2">
                  Performance Insights
                </h4>
                <div className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                  {parseFloat(processing_time?.replace('ms', '').replace('s', '000') || '0') > 3000 && (
                    <div>• Die Verarbeitungszeit ist über dem Zielwert von 3s</div>
                  )}
                  {confidence_score && confidence_score < 0.7 && (
                    <div>• Das Vertrauen in die Antwort ist niedrig - erwäge zusätzliche Quellen</div>
                  )}
                  {sources.length === 0 && (
                    <div>• Keine Quellen gefunden - Antwort basiert auf Modellwissen</div>
                  )}
                  {sourceQuality.score < 60 && (
                    <div>• Die Quellenqualität könnte verbessert werden</div>
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