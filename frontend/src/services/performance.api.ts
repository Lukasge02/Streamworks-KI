/**
 * Performance API Service
 * Real-time performance metrics and analytics integration
 */

import { apiService } from './api.service'

export interface PerformanceMetrics {
  timestamp: string
  performance: {
    status: string
    overall: {
      avg_response_time_ms: number
      p95_response_time_ms: number
      target_response_time_ms: number
      performance_status: string
      total_queries: number
    }
    cache: {
      hit_rate_percent: number
      target_hit_rate_percent: number
      cache_status: string
      total_hits: number
      total_misses: number
    }
    components: Record<string, {
      avg_ms: number
      p95_ms: number
      count: number
      error_rate: number
    }>
    bottlenecks: Array<{
      component: string
      avg_duration_ms: number
      benchmark_ms: number
      slowdown_factor: number
      impact: string
    }>
    recent_alerts: Array<{
      timestamp: string
      type: string
      component: string
      operation: string
      severity: string
    }>
  }
  cache: {
    hits: number
    misses: number
    hit_rate: number
    cache_size: number
    max_size: number
    ttl_seconds: number
  }
  rag_services: {
    unified_rag: {
      service: string
      status: string
      initialized: boolean
    }
    base_rag: {
      service: string
      status: string
      initialized: boolean
    }
  }
  system_status: string
}

export interface DashboardMetrics {
  timestamp: string
  time_window_minutes: number
  dashboard_metrics: {
    processing_time: {
      current_ms: number
      target_ms: number
      status: string
      trend: string
    }
    source_quality: {
      percentage: number
      target_percentage: number
      status: string
      total_sources: number
    }
    cache_performance: {
      hit_rate_percentage: number
      target_percentage: number
      status: string
      total_requests: number
    }
    system_health: {
      overall_status: string
      components: Record<string, string>
      bottlenecks: Array<any>
      alerts: Array<any>
    }
  }
  raw_performance_data: PerformanceMetrics
}

export interface OptimizationRecommendations {
  timestamp: string
  optimization_analysis: {
    analysis_timestamp: string
    performance_status: string
    recommendations: Array<{
      type: string
      priority: string
      action: string
      description: string
      implementation: string
      component?: string
    }>
    auto_optimizable: number
  }
  actionable_recommendations: Array<{
    title: string
    priority: string
    component: string
    action: string
    implementation: string
    type: string
  }>
  priority_actions: Array<any>
}

class PerformanceApiService {
  private baseUrl = '/api/performance'

  /**
   * Get real-time performance metrics
   */
  async getRealtimeMetrics(): Promise<PerformanceMetrics> {
    try {
      const response = await apiService.get(`${this.baseUrl}/metrics/realtime`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch realtime metrics:', error)
      // Return fallback data to prevent UI crashes
      return this.getFallbackMetrics()
    }
  }

  /**
   * Get dashboard-formatted metrics
   */
  async getDashboardMetrics(timeWindowMinutes: number = 5): Promise<DashboardMetrics> {
    try {
      const response = await apiService.get(
        `${this.baseUrl}/metrics/dashboard?time_window_minutes=${timeWindowMinutes}`
      )
      return response.data
    } catch (error) {
      console.error('Failed to fetch dashboard metrics:', error)
      // Return fallback dashboard data
      return this.getFallbackDashboardMetrics()
    }
  }

  /**
   * Get optimization recommendations
   */
  async getOptimizationRecommendations(): Promise<OptimizationRecommendations> {
    try {
      const response = await apiService.get(`${this.baseUrl}/optimization/recommendations`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch optimization recommendations:', error)
      throw error
    }
  }

  /**
   * Reset performance statistics (admin only)
   */
  async resetPerformanceStats(): Promise<{ message: string; timestamp: string }> {
    try {
      const response = await apiService.post(`${this.baseUrl}/reset-stats`)
      return response.data
    } catch (error) {
      console.error('Failed to reset performance stats:', error)
      throw error
    }
  }

  /**
   * Start real-time metrics polling
   */
  startRealtimePolling(
    onUpdate: (metrics: PerformanceMetrics) => void,
    interval: number = 5000
  ): () => void {
    const poll = async () => {
      try {
        const metrics = await this.getRealtimeMetrics()
        onUpdate(metrics)
      } catch (error) {
        console.error('Polling error:', error)
      }
    }

    // Initial poll
    poll()

    // Set up interval
    const intervalId = setInterval(poll, interval)

    // Return cleanup function
    return () => clearInterval(intervalId)
  }

  /**
   * Get performance status color
   */
  getStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'excellent':
        return 'text-emerald-600'
      case 'good':
        return 'text-green-600'
      case 'acceptable':
        return 'text-amber-600'
      case 'poor':
      case 'degraded':
        return 'text-red-600'
      default:
        return 'text-gray-500'
    }
  }

  /**
   * Get performance status background color
   */
  getStatusBgColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'excellent':
        return 'bg-emerald-100 dark:bg-emerald-900/30'
      case 'good':
        return 'bg-green-100 dark:bg-green-900/30'
      case 'acceptable':
        return 'bg-amber-100 dark:bg-amber-900/30'
      case 'poor':
      case 'degraded':
        return 'bg-red-100 dark:bg-red-900/30'
      default:
        return 'bg-gray-100 dark:bg-gray-900/30'
    }
  }

  /**
   * Format milliseconds to human readable
   */
  formatDuration(ms: number): string {
    if (ms < 1000) {
      return `${Math.round(ms)}ms`
    } else if (ms < 60000) {
      return `${(ms / 1000).toFixed(1)}s`
    } else {
      return `${(ms / 60000).toFixed(1)}m`
    }
  }

  /**
   * Format percentage with appropriate precision
   */
  formatPercentage(value: number): string {
    return `${value.toFixed(1)}%`
  }

  /**
   * Get trend indicator
   */
  getTrendIcon(trend: string): string {
    switch (trend.toLowerCase()) {
      case 'improving':
        return '📈'
      case 'degrading':
        return '📉'
      case 'stable':
      default:
        return '➡️'
    }
  }

  /**
   * Fallback metrics for offline/error states
   */
  private getFallbackMetrics(): PerformanceMetrics {
    return {
      timestamp: new Date().toISOString(),
      performance: {
        status: 'no_data',
        overall: {
          avg_response_time_ms: 0,
          p95_response_time_ms: 0,
          target_response_time_ms: 2000,
          performance_status: 'unknown',
          total_queries: 0
        },
        cache: {
          hit_rate_percent: 0,
          target_hit_rate_percent: 95,
          cache_status: 'unknown',
          total_hits: 0,
          total_misses: 0
        },
        components: {},
        bottlenecks: [],
        recent_alerts: []
      },
      cache: {
        hits: 0,
        misses: 0,
        hit_rate: 0,
        cache_size: 0,
        max_size: 0,
        ttl_seconds: 0
      },
      rag_services: {
        unified_rag: {
          service: 'UnifiedRAGService',
          status: 'unknown',
          initialized: false
        },
        base_rag: {
          service: 'QdrantRAGService',
          status: 'unknown',
          initialized: false
        }
      },
      system_status: 'unknown'
    }
  }

  /**
   * Fallback dashboard metrics
   */
  private getFallbackDashboardMetrics(): DashboardMetrics {
    return {
      timestamp: new Date().toISOString(),
      time_window_minutes: 5,
      dashboard_metrics: {
        processing_time: {
          current_ms: 0,
          target_ms: 2000,
          status: 'unknown',
          trend: 'stable'
        },
        source_quality: {
          percentage: 0,
          target_percentage: 80,
          status: 'unknown',
          total_sources: 0
        },
        cache_performance: {
          hit_rate_percentage: 0,
          target_percentage: 95,
          status: 'unknown',
          total_requests: 0
        },
        system_health: {
          overall_status: 'unknown',
          components: {},
          bottlenecks: [],
          alerts: []
        }
      },
      raw_performance_data: this.getFallbackMetrics()
    }
  }
}

export const performanceApi = new PerformanceApiService()