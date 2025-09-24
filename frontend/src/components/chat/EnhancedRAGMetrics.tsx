'use client'

import React, { useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import {
  BarChart3,
  RefreshCw,
  Activity,
  Clock,
  Target,
  Database,
  TrendingUp,
  AlertTriangle,
  Layers,
  FileText,
  ArrowUpRight,
} from 'lucide-react'

import {
  RagActivityResponse,
  RagLiveMetricsResponse,
  RagSourceInsightsResponse,
} from '../../types/ragMetrics'

interface SourceReference {
  document_id: string
  filename: string
  page_number?: number
  section?: string
  relevance_score: number
  snippet: string
  chunk_index: number
  confidence: number
  doc_type?: string
  chunk_id?: string
}

interface EnhancedRAGMetricsProps {
  sources?: SourceReference[]
  expanded?: boolean
  onToggleExpand?: () => void
  showSources?: boolean
  onSourceClick?: (source: SourceReference) => void
}

const statusStyles: Record<string, string> = {
  initializing: 'bg-gray-100 text-gray-700 dark:bg-gray-800/60 dark:text-gray-300',
  ok: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
  degraded: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  error: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
}

const statusLabels: Record<string, string> = {
  initializing: 'Initialisierung',
  ok: 'Stabil',
  degraded: 'Beeinträchtigt',
  error: 'Fehler',
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    let detail = 'Unbekannter Fehler'
    try {
      const payload = await response.json()
      detail = payload?.detail || payload?.message || detail
    } catch (error) {
      // response did not contain JSON content
    }
    throw new Error(detail)
  }
  return response.json()
}

const formatPercent = (value: number, fractionDigits = 0): string =>
  `${(value * 100).toFixed(fractionDigits)}%`

const formatMs = (value: number): string => `${Math.round(value)}ms`

export const EnhancedRAGMetrics: React.FC<EnhancedRAGMetricsProps> = ({
  sources = [],
  expanded = false,
  onToggleExpand,
  showSources = true,
  onSourceClick,
}) => {
  const {
    data: liveMetrics,
    isLoading: liveLoading,
    error: liveError,
    refetch: refetchLive,
  } = useQuery<RagLiveMetricsResponse>({
    queryKey: ['rag-metrics', 'live'],
    queryFn: () => fetchJson<RagLiveMetricsResponse>('/api/rag-metrics/live?window_minutes=15'),
    refetchInterval: 15000,
  })

  const {
    data: sourceAnalytics,
    isLoading: sourcesLoading,
    error: sourcesError,
    refetch: refetchSources,
  } = useQuery<RagSourceInsightsResponse>({
    queryKey: ['rag-metrics', 'sources'],
    queryFn: () => fetchJson<RagSourceInsightsResponse>('/api/rag-metrics/sources?limit=8&window_hours=24'),
    refetchInterval: 60000,
  })

  const {
    data: activityTimeline,
    isLoading: activityLoading,
    error: activityError,
    refetch: refetchActivity,
  } = useQuery<RagActivityResponse>({
    queryKey: ['rag-metrics', 'activity'],
    queryFn: () => fetchJson<RagActivityResponse>('/api/rag-metrics/activity?window_minutes=120&bucket_minutes=10'),
    refetchInterval: 60000,
  })

  const successRate = useMemo(() => {
    if (!liveMetrics || liveMetrics.totals.queries === 0) {
      return 0
    }
    return liveMetrics.totals.successful / liveMetrics.totals.queries
  }, [liveMetrics])

  const failureRate = useMemo(() => {
    if (!liveMetrics || liveMetrics.totals.queries === 0) {
      return 0
    }
    return liveMetrics.totals.failed / liveMetrics.totals.queries
  }, [liveMetrics])

  const handleRefresh = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation()
    await Promise.all([refetchLive(), refetchSources(), refetchActivity()])
    toast.success('RAG Metriken aktualisiert')
  }

  const renderSourceList = () => {
    if (!showSources || sources.length === 0) {
      return null
    }

    return (
      <div className="space-y-2">
        {sources.map((source, index) => (
          <div
            key={`${source.document_id}-${index}`}
            className="flex items-start justify-between rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-sm"
          >
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-900 dark:text-white truncate">
                {source.filename}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {(source.section || 'Unbekannter Abschnitt')}
                {source.page_number && ` • Seite ${source.page_number}`}
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 line-clamp-2">
                {source.snippet || 'Kein Auszug verfügbar'}
              </p>
            </div>
            <div className="flex flex-col items-end ml-3">
              <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                {Math.round(source.relevance_score * 100)}%
              </span>
              <button
                className="mt-2 text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                onClick={() => onSourceClick?.(source)}
              >
                Details
              </button>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const statusClass = statusStyles[liveMetrics?.status ?? 'initializing']
  const statusLabel = statusLabels[liveMetrics?.status ?? 'initializing']

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900/70 overflow-hidden">
      <button
        type="button"
        onClick={onToggleExpand}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">
              RAG System Insights
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Aktualisiert: {liveMetrics ? new Date(liveMetrics.updated_at).toLocaleTimeString('de-DE') : 'keine Daten'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`px-2 py-1 rounded text-xs font-medium ${statusClass}`}>
            {statusLabel}
          </span>
          <button
            onClick={handleRefresh}
            className="p-2 rounded-md text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
          >
            <RefreshCw className={liveLoading ? 'w-4 h-4 animate-spin' : 'w-4 h-4'} />
          </button>
          <div className="text-gray-400 dark:text-gray-500">
            {expanded ? '▾' : '▸'}
          </div>
        </div>
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
          >
            <div className="p-4 space-y-6 border-t border-gray-200 dark:border-gray-800">
              {liveError && (
                <div className="flex items-center space-x-2 rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-3 text-sm text-red-700 dark:text-red-300">
                  <AlertTriangle className="w-4 h-4" />
                  <span>{liveError.message}</span>
                </div>
              )}

              {liveLoading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {Array.from({ length: 4 }).map((_, index) => (
                    <div key={index} className="h-24 rounded-lg bg-gray-100 dark:bg-gray-800 animate-pulse" />
                  ))}
                </div>
              ) : liveMetrics ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    <MetricCard
                      icon={<Activity className="w-4 h-4 text-emerald-500" />}
                      title="Durchschnittliche Antwortzeit"
                      value={formatMs(liveMetrics.latency.average_ms)}
                      subtitle={`P95 ${formatMs(liveMetrics.latency.p95_ms)}`}
                    />
                    <MetricCard
                      icon={<Target className="w-4 h-4 text-blue-500" />}
                      title="Erfolgsquote"
                      value={formatPercent(successRate, 0)}
                      subtitle={`${liveMetrics.totals.successful} von ${liveMetrics.totals.queries} Anfragen`}
                    />
                    <MetricCard
                      icon={<Database className="w-4 h-4 text-amber-500" />}
                      title="Cache Hit Rate"
                      value={formatPercent(liveMetrics.totals.cache_hit_rate, 0)}
                      subtitle={`Fehlerquote ${formatPercent(failureRate, 0)}`}
                    />
                    <MetricCard
                      icon={<Layers className="w-4 h-4 text-purple-500" />}
                      title="Quellenabdeckung"
                      value={`${liveMetrics.quality.unique_sources} Dokumente`
                      }
                      subtitle={`Ø ${liveMetrics.quality.avg_sources_per_query.toFixed(1)} Quellen / Antwort`}
                    />
                  </div>

                  {liveMetrics.status === 'initializing' && (
                    <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/40 p-4 text-sm text-gray-600 dark:text-gray-300">
                      Noch keine RAG-Anfragen aufgezeichnet. Stelle eine Frage, um aktuelle Metriken zu generieren.
                    </div>
                  )}
                </div>
              ) : null}

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <section>
                  <SectionHeader
                    icon={<TrendingUp className="w-4 h-4" />}
                    title="Aktivitätsverlauf"
                    description="Letzte 2 Stunden in 10-Minuten-Buckets"
                    isLoading={activityLoading}
                    error={activityError}
                  />

                  {activityTimeline && activityTimeline.buckets.length > 0 ? (
                    <div className="space-y-2">
                      {activityTimeline.buckets.slice(-6).map((bucket) => {
                        const width = Math.min(bucket.total_queries * 12, 160)
                        return (
                          <div
                            key={bucket.start}
                            className="flex items-center space-x-3 text-xs text-gray-600 dark:text-gray-300"
                          >
                            <span className="w-24 text-gray-500 dark:text-gray-400">
                              {new Date(bucket.start).toLocaleTimeString('de-DE', {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                            <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                              <div
                                className="h-2 rounded-full bg-blue-500"
                                style={{ width: `${width}px` }}
                              />
                            </div>
                            <span className="w-12 text-right">
                              {bucket.total_queries}
                            </span>
                            <span className="w-16 text-right text-gray-400">
                              {formatMs(bucket.avg_response_time_ms)}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <EmptyState message="Keine Aktivitätsdaten vorhanden" />
                  )}
                </section>

                <section>
                  <SectionHeader
                    icon={<FileText className="w-4 h-4" />}
                    title="Top Quellen"
                    description="Meistverwendete Dokumente (24h)"
                    isLoading={sourcesLoading}
                    error={sourcesError}
                  />

                  {sourceAnalytics && sourceAnalytics.top_documents.length > 0 ? (
                    <div className="space-y-2">
                      {sourceAnalytics.top_documents.map((doc) => (
                        <div
                          key={doc.document_id}
                          className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-3"
                        >
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                              {doc.filename}
                            </p>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {doc.usage_count}x
                            </span>
                          </div>
                          <div className="mt-2 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                            <span>Relevanz {formatPercent(doc.avg_relevance, 0)}</span>
                            <span>Vertrauen {formatPercent(doc.avg_confidence, 0)}</span>
                            <span>
                              {doc.last_used
                                ? new Date(doc.last_used).toLocaleTimeString('de-DE', {
                                    hour: '2-digit',
                                    minute: '2-digit',
                                  })
                                : 'nie'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <EmptyState message="Noch keine Dokumentnutzung erfasst" />
                  )}
                </section>
              </div>

              {renderSourceList()}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

const MetricCard: React.FC<{
  icon: React.ReactNode
  title: string
  value: string
  subtitle?: string
}> = ({ icon, title, value, subtitle }) => (
  <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
    <div className="flex items-center justify-between">
      <div className="p-2 rounded-md bg-gray-100 dark:bg-gray-900 text-gray-600 dark:text-gray-300">
        {icon}
      </div>
      <ArrowUpRight className="w-4 h-4 text-gray-300" />
    </div>
    <div className="mt-3">
      <p className="text-xs uppercase tracking-wide text-gray-400 dark:text-gray-500">
        {title}
      </p>
      <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
        {value}
      </p>
      {subtitle && (
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{subtitle}</p>
      )}
    </div>
  </div>
)

const SectionHeader: React.FC<{
  icon: React.ReactNode
  title: string
  description?: string
  isLoading?: boolean
  error?: Error | null
}> = ({ icon, title, description, isLoading, error }) => (
  <div className="flex items-center justify-between mb-3">
    <div>
      <div className="flex items-center space-x-2">
        <span className="text-gray-500 dark:text-gray-400">{icon}</span>
        <p className="text-sm font-semibold text-gray-900 dark:text-white">{title}</p>
      </div>
      {description && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{description}</p>
      )}
    </div>
    <div className="text-xs text-gray-400 dark:text-gray-500">
      {isLoading && 'Laden…'}
      {error && <span className="text-red-500">{error.message}</span>}
    </div>
  </div>
)

const EmptyState: React.FC<{ message: string }> = ({ message }) => (
  <div className="rounded-lg border border-dashed border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/40 p-6 text-center text-sm text-gray-500 dark:text-gray-400">
    {message}
  </div>
)

export default EnhancedRAGMetrics
