/**
 * Performance Metrics Hook
 * Real-time performance monitoring and analytics
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { performanceApi, type PerformanceMetrics, type DashboardMetrics } from '../services/performance.api'

interface UsePerformanceMetricsOptions {
  autoRefresh?: boolean
  refreshInterval?: number
  timeWindowMinutes?: number
}

interface UsePerformanceMetricsReturn {
  // Data
  metrics: PerformanceMetrics | null
  dashboardMetrics: DashboardMetrics | null

  // States
  isLoading: boolean
  isConnected: boolean
  error: string | null
  lastUpdated: Date | null

  // Actions
  refresh: () => Promise<void>
  startPolling: () => void
  stopPolling: () => void
  resetStats: () => Promise<void>

  // Computed values
  systemHealth: 'excellent' | 'good' | 'degraded' | 'unknown'
  responseTime: number
  cacheHitRate: number
  sourceQuality: number
  activeBottlenecks: number
}

export function usePerformanceMetrics({
  autoRefresh = true,
  refreshInterval = 5000,
  timeWindowMinutes = 5
}: UsePerformanceMetricsOptions = {}): UsePerformanceMetricsReturn {

  // State
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  // Refs
  const pollingRef = useRef<(() => void) | null>(null)
  const mounted = useRef(true)

  // Fetch metrics
  const fetchMetrics = useCallback(async () => {
    try {
      setError(null)

      const [unifiedData, dashboardData] = await Promise.all([
        performanceApi.getUnifiedRAGMetrics(),
        performanceApi.getDashboardMetrics(timeWindowMinutes)
      ])

      if (mounted.current) {
        // Use unified data which includes both formats
        setMetrics(unifiedData.performance || unifiedData)
        setDashboardMetrics(dashboardData)
        setIsConnected(unifiedData.is_connected)
        setLastUpdated(new Date(unifiedData.timestamp))
      }
    } catch (err) {
      if (mounted.current) {
        setError(err instanceof Error ? err.message : 'Failed to fetch metrics')
        setIsConnected(false)
      }
    } finally {
      if (mounted.current) {
        setIsLoading(false)
      }
    }
  }, [timeWindowMinutes])

  // Start polling
  const startPolling = useCallback(() => {
    if (pollingRef.current) {
      pollingRef.current() // Stop existing polling
    }

    // Use our own polling with unified API
    const poll = async () => {
      try {
        const unifiedData = await performanceApi.getUnifiedRAGMetrics()
        if (mounted.current) {
          setMetrics(unifiedData.performance || unifiedData)
          setIsConnected(unifiedData.is_connected)
          setLastUpdated(new Date(unifiedData.timestamp))
          setError(null)
        }
      } catch (err) {
        if (mounted.current) {
          setError(err instanceof Error ? err.message : 'Polling failed')
          setIsConnected(false)
        }
      }
    }

    // Initial poll
    poll()

    // Set up interval
    const intervalId = setInterval(poll, refreshInterval)

    // Return cleanup function
    const cleanup = () => clearInterval(intervalId)

    pollingRef.current = cleanup
  }, [refreshInterval])

  // Stop polling
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      pollingRef.current()
      pollingRef.current = null
    }
  }, [])

  // Manual refresh
  const refresh = useCallback(async () => {
    setIsLoading(true)
    await fetchMetrics()
  }, [fetchMetrics])

  // Reset performance statistics
  const resetStats = useCallback(async () => {
    try {
      setError(null)
      await performanceApi.resetPerformanceStats()

      // Refresh metrics after reset
      await fetchMetrics()

      return Promise.resolve()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to reset statistics'
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }, [fetchMetrics])

  // Computed values
  const systemHealth = (() => {
    if (!dashboardMetrics) return 'unknown' as const

    const status = dashboardMetrics.dashboard_metrics.system_health.overall_status
    switch (status) {
      case 'excellent':
        return 'excellent' as const
      case 'good':
      case 'acceptable':
        return 'good' as const
      case 'degraded':
      case 'poor':
        return 'degraded' as const
      default:
        return 'unknown' as const
    }
  })()

  const responseTime = dashboardMetrics?.dashboard_metrics.processing_time.current_ms || 0
  const cacheHitRate = dashboardMetrics?.dashboard_metrics.cache_performance.hit_rate_percentage || 0
  const sourceQuality = dashboardMetrics?.dashboard_metrics.source_quality.percentage || 0
  const activeBottlenecks = metrics?.performance?.bottlenecks?.length || 0

  // Effects
  useEffect(() => {
    mounted.current = true

    // Initial fetch
    fetchMetrics()

    // Start auto-refresh if enabled
    if (autoRefresh) {
      startPolling()
    }

    return () => {
      mounted.current = false
      stopPolling()
    }
  }, [fetchMetrics, autoRefresh, startPolling, stopPolling])

  // Update polling when refresh interval changes
  useEffect(() => {
    if (autoRefresh && pollingRef.current) {
      stopPolling()
      startPolling()
    }
  }, [refreshInterval, autoRefresh, startPolling, stopPolling])

  return {
    // Data
    metrics,
    dashboardMetrics,

    // States
    isLoading,
    isConnected,
    error,
    lastUpdated,

    // Actions
    refresh,
    startPolling,
    stopPolling,
    resetStats,

    // Computed values
    systemHealth,
    responseTime,
    cacheHitRate,
    sourceQuality,
    activeBottlenecks
  }
}

/**
 * Simplified hook for basic performance status
 */
export function usePerformanceStatus() {
  const { systemHealth, responseTime, cacheHitRate, sourceQuality, isConnected } = usePerformanceMetrics({
    autoRefresh: true,
    refreshInterval: 10000 // Less frequent for status-only use
  })

  return {
    systemHealth,
    responseTime,
    cacheHitRate,
    sourceQuality,
    isConnected,
    isHealthy: systemHealth === 'excellent' || systemHealth === 'good'
  }
}
