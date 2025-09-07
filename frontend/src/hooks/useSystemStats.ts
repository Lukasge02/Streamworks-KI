/**
 * Hook for fetching live system statistics
 * Provides real-time data for dashboard
 */

import { useState, useEffect } from 'react'
import { apiService } from '@/services/api.service'

interface SystemStats {
  totalDocuments: number
  totalFolders: number  
  totalChunks: number
  activeUploadJobs: number
  processingJobs: number
  errorCount: number
  systemUptime: string
  storageUsed: number // in bytes
  lastProcessedDocument?: {
    filename: string
    processedAt: string
  }
}

interface UseSystemStatsReturn {
  stats: SystemStats | null
  loading: boolean
  error: string | null
  refreshStats: () => Promise<void>
}

export function useSystemStats(autoRefresh: boolean = true): UseSystemStatsReturn {
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async (): Promise<void> => {
    try {
      setError(null)
      
      // Fetch multiple endpoints in parallel for comprehensive stats
      const [documentsResponse, foldersResponse, healthResponse] = await Promise.all([
        apiService.getDocuments(undefined, undefined, 'created_desc'),
        apiService.getFolders(),
        apiService.healthCheck()
      ])

      // Calculate stats from real data
      const documents = documentsResponse || []
      const folders = foldersResponse || []

      const totalChunks = documents.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0)
      const processingDocs = documents.filter(doc => 
        ['uploading', 'analyzing', 'processing'].includes(doc.status)
      ).length
      const errorDocs = documents.filter(doc => doc.status === 'error').length
      
      // Calculate storage usage  
      const storageUsed = documents.reduce((sum, doc) => sum + (doc.file_size || 0), 0)

      // Find last processed document
      const processedDocs = documents
        .filter(doc => doc.processed_at)
        .sort((a, b) => new Date(b.processed_at!).getTime() - new Date(a.processed_at!).getTime())
      
      const lastProcessed = processedDocs[0]

      const systemStats: SystemStats = {
        totalDocuments: documents.length,
        totalFolders: folders.length,
        totalChunks,
        activeUploadJobs: 0, // Could be enhanced with real upload job tracking
        processingJobs: processingDocs,
        errorCount: errorDocs,
        systemUptime: 'Online', // Could be enhanced with actual uptime calculation
        storageUsed,
        lastProcessedDocument: lastProcessed ? {
          filename: lastProcessed.original_filename,
          processedAt: lastProcessed.processed_at!
        } : undefined
      }

      setStats(systemStats)
      
    } catch (err) {
      console.error('Failed to fetch system stats:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch stats')
    } finally {
      setLoading(false)
    }
  }

  const refreshStats = async (): Promise<void> => {
    setLoading(true)
    await fetchStats()
  }

  // Initial fetch
  useEffect(() => {
    fetchStats()
  }, [])

  // Auto-refresh every 30 seconds if enabled
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [autoRefresh])

  return {
    stats,
    loading,
    error,
    refreshStats
  }
}