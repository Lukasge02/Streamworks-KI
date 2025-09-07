'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Activity, Database, Server, Users, FileText, MessageSquare, Zap, CheckCircle, AlertCircle, Clock } from 'lucide-react'

interface SystemMetrics {
  status: string
  service: string
  version: string
  features: {
    real_time_uploads: boolean
    websocket_support: boolean
    batch_operations: boolean
    advanced_search: boolean
    enterprise_storage: boolean
  }
  services: {
    [key: string]: string
  }
  upload_queue: {
    active_jobs: number
    queued_jobs: number
    max_concurrent: number
    total_jobs: number
  }
}

interface PipelineInfo {
  pipelines: Array<{
    name: string
    description: string
    status: string
    phase: number
    endpoints: string[]
  }>
  active_pipelines: string[]
}

export const StreamWorksRAGDashboard = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [pipelines, setPipelines] = useState<PipelineInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const fetchSystemData = async () => {
    try {
      const [metricsResponse, pipelinesResponse] = await Promise.all([
        fetch('/api/system/health'),
        fetch('/graph/pipelines')
      ])
      
      const metricsData = await metricsResponse.json()
      const pipelinesData = await pipelinesResponse.json()
      
      setMetrics(metricsData)
      setPipelines(pipelinesData)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Error fetching system data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSystemData()
    const interval = setInterval(fetchSystemData, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'active':
        return 'text-green-600'
      case 'warning':
        return 'text-yellow-600'
      case 'error':
      case 'inactive':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'active':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />
      case 'error':
      case 'inactive':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-600" />
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            StreamWorks RAG Enterprise Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Professional RAG System mit Docling Layout-Aware Parsing
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">Live</span>
          </div>
          <span className="text-sm bg-primary-100 text-primary-800 px-2 py-1 rounded-full">
            {metrics?.version || 'v2.0.0'}
          </span>
        </div>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">System Status</p>
              <p className={`text-2xl font-bold ${getStatusColor(metrics?.status || 'unknown')}`}>
                {metrics?.status || 'Unknown'}
              </p>
            </div>
            <Server className={`w-8 h-8 ${getStatusColor(metrics?.status || 'unknown')}`} />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Jobs</p>
              <p className="text-2xl font-bold text-blue-600">
                {metrics?.upload_queue.active_jobs || 0}
              </p>
            </div>
            <Activity className="w-8 h-8 text-blue-600" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Queue Capacity</p>
              <p className="text-2xl font-bold text-purple-600">
                {metrics?.upload_queue.max_concurrent || 3}
              </p>
            </div>
            <Users className="w-8 h-8 text-purple-600" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Jobs</p>
              <p className="text-2xl font-bold text-green-600">
                {metrics?.upload_queue.total_jobs || 0}
              </p>
            </div>
            <Database className="w-8 h-8 text-green-600" />
          </div>
        </motion.div>
      </div>

      {/* Features Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Enterprise Features
          </h3>
          <div className="space-y-3">
            {metrics?.features && Object.entries(metrics.features).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                  {key.replace(/_/g, ' ')}
                </span>
                {value ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-red-600" />
                )}
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Active Pipelines
          </h3>
          <div className="space-y-3">
            {pipelines?.pipelines.map((pipeline, index) => (
              <div key={pipeline.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {pipeline.name === 'qa' ? (
                    <MessageSquare className="w-5 h-5 text-blue-600" />
                  ) : (
                    <FileText className="w-5 h-5 text-purple-600" />
                  )}
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {pipeline.name.toUpperCase()}
                    </p>
                    <p className="text-xs text-gray-500">Phase {pipeline.phase}</p>
                  </div>
                </div>
                {getStatusIcon(pipeline.status)}
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Services Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Service Health
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {metrics?.services && Object.entries(metrics.services).map(([service, status]) => (
            <div key={service} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center space-x-3">
                <Zap className="w-5 h-5 text-gray-600" />
                <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                  {service.replace(/_/g, ' ')}
                </span>
              </div>
              {getStatusIcon(status)}
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}