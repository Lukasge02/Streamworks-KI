'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Activity, Server, Database, Zap, Clock, CheckCircle, 
  AlertTriangle, XCircle, Cpu, HardDrive, Wifi, 
  MemoryStick, TrendingUp, TrendingDown, RefreshCw,
  Monitor, Users, MessageSquare, FileText, Bot
} from 'lucide-react'

interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical'
  uptime: string
  last_check: string
  services: {
    api: { status: string, response_time: number }
    database: { status: string, response_time: number }
    vectordb: { status: string, response_time: number }
    llm: { status: string, response_time: number }
  }
  metrics: {
    cpu_usage: number
    memory_usage: number
    disk_usage: number
    network_latency: number
  }
  performance: {
    avg_qa_response_time: number
    avg_xml_generation_time: number
    avg_document_processing_time: number
    requests_per_minute: number
  }
}

interface PipelineHealth {
  qa_pipeline: {
    status: 'healthy' | 'degraded' | 'down'
    success_rate: number
    avg_response_time: number
    errors_last_hour: number
  }
  xml_pipeline: {
    status: 'healthy' | 'degraded' | 'down'
    success_rate: number
    avg_response_time: number
    errors_last_hour: number
  }
  document_pipeline: {
    status: 'healthy' | 'degraded' | 'down'
    success_rate: number
    avg_response_time: number
    errors_last_hour: number
  }
}

interface RecentActivity {
  timestamp: string
  type: 'qa' | 'xml' | 'upload' | 'error'
  message: string
  user?: string
  duration?: number
  status: 'success' | 'warning' | 'error'
}

export function SystemMonitor() {
  const [health, setHealth] = useState<SystemHealth>({
    status: 'healthy',
    uptime: '0h 0m',
    last_check: '',
    services: {
      api: { status: 'healthy', response_time: 0 },
      database: { status: 'healthy', response_time: 0 },
      vectordb: { status: 'healthy', response_time: 0 },
      llm: { status: 'healthy', response_time: 0 }
    },
    metrics: {
      cpu_usage: 0,
      memory_usage: 0,
      disk_usage: 0,
      network_latency: 0
    },
    performance: {
      avg_qa_response_time: 0,
      avg_xml_generation_time: 0,
      avg_document_processing_time: 0,
      requests_per_minute: 0
    }
  })
  const [pipelines, setPipelines] = useState<PipelineHealth>({
    qa_pipeline: { status: 'healthy', success_rate: 0, avg_response_time: 0, errors_last_hour: 0 },
    xml_pipeline: { status: 'healthy', success_rate: 0, avg_response_time: 0, errors_last_hour: 0 },
    document_pipeline: { status: 'healthy', success_rate: 0, avg_response_time: 0, errors_last_hour: 0 }
  })
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const loadSystemHealth = async () => {
    try {
      const response = await fetch('/api/system/health')
      if (response.ok) {
        const data = await response.json()
        
        // Mock comprehensive health data - in production this would come from backend
        setHealth({
          status: data.status === 'healthy' ? 'healthy' : 'warning',
          uptime: data.uptime || '24h 15m',
          last_check: new Date().toISOString(),
          services: {
            api: { status: 'healthy', response_time: 45 },
            database: { status: 'healthy', response_time: 12 },
            vectordb: { status: 'healthy', response_time: 89 },
            llm: { status: 'healthy', response_time: 1200 }
          },
          metrics: {
            cpu_usage: Math.floor(Math.random() * 30) + 15, // 15-45%
            memory_usage: Math.floor(Math.random() * 25) + 35, // 35-60%
            disk_usage: Math.floor(Math.random() * 20) + 40, // 40-60%
            network_latency: Math.floor(Math.random() * 20) + 5 // 5-25ms
          },
          performance: {
            avg_qa_response_time: 1.2,
            avg_xml_generation_time: 3.8,
            avg_document_processing_time: 12.5,
            requests_per_minute: Math.floor(Math.random() * 20) + 5
          }
        })

        // Mock pipeline health
        setPipelines({
          qa_pipeline: {
            status: 'healthy',
            success_rate: 0.98,
            avg_response_time: 1.2,
            errors_last_hour: Math.floor(Math.random() * 3)
          },
          xml_pipeline: {
            status: 'healthy',
            success_rate: 0.95,
            avg_response_time: 3.8,
            errors_last_hour: Math.floor(Math.random() * 2)
          },
          document_pipeline: {
            status: 'healthy',
            success_rate: 0.99,
            avg_response_time: 12.5,
            errors_last_hour: Math.floor(Math.random() * 1)
          }
        })

        // Mock recent activity
        const activities: RecentActivity[] = [
          { timestamp: new Date(Date.now() - 120000).toISOString(), type: 'qa', message: 'Q&A request processed successfully', user: 'admin', duration: 1.1, status: 'success' },
          { timestamp: new Date(Date.now() - 180000).toISOString(), type: 'upload', message: 'Document processed: "Streamworks Manual.pdf"', duration: 8.5, status: 'success' },
          { timestamp: new Date(Date.now() - 240000).toISOString(), type: 'xml', message: 'XML workflow generated for ETL pipeline', duration: 4.2, status: 'success' },
          { timestamp: new Date(Date.now() - 300000).toISOString(), type: 'qa', message: 'Q&A request processed successfully', user: 'user1', duration: 0.9, status: 'success' },
          { timestamp: new Date(Date.now() - 360000).toISOString(), type: 'error', message: 'Vector database connection timeout', status: 'error' }
        ]
        setRecentActivity(activities)
      }
    } catch (error) {
      console.error('Failed to load system health:', error)
      setHealth(prev => ({ ...prev, status: 'critical' }))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSystemHealth()
    
    if (autoRefresh) {
      const interval = setInterval(loadSystemHealth, 15000) // Refresh every 15 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600'
      case 'warning': case 'degraded': return 'text-yellow-600'
      case 'critical': case 'down': case 'error': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'warning': case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'critical': case 'down': case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <Activity className="w-5 h-5 text-gray-500" />
    }
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'qa': return <MessageSquare className="w-4 h-4 text-blue-600" />
      case 'xml': return <FileText className="w-4 h-4 text-purple-600" />
      case 'upload': return <FileText className="w-4 h-4 text-green-600" />
      case 'error': return <XCircle className="w-4 h-4 text-red-600" />
      default: return <Activity className="w-4 h-4 text-gray-600" />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading system health...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-auto bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
              <Monitor className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                System Health Monitoring
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Real-time system status - GET /api/system/health
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="autoRefresh"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="autoRefresh" className="text-sm text-gray-600 dark:text-gray-400">
                Auto-refresh
              </label>
            </div>
            
            <button
              onClick={loadSystemHealth}
              className="flex items-center space-x-2 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Overall Status */}
        <div className="mt-4 flex items-center space-x-4">
          <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
            health.status === 'healthy' ? 'bg-green-100 text-green-800' :
            health.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {getStatusIcon(health.status)}
            <span className="font-medium">System {health.status}</span>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <Clock className="w-4 h-4" />
            <span>Uptime: {health.uptime}</span>
          </div>
          
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Last check: {formatTimestamp(health.last_check)}
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* System Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { 
              label: 'CPU Usage', 
              value: health.metrics.cpu_usage, 
              unit: '%',
              icon: Cpu, 
              color: health.metrics.cpu_usage > 80 ? 'text-red-600' : health.metrics.cpu_usage > 60 ? 'text-yellow-600' : 'text-green-600',
              bg: health.metrics.cpu_usage > 80 ? 'bg-red-50 dark:bg-red-900/20' : health.metrics.cpu_usage > 60 ? 'bg-yellow-50 dark:bg-yellow-900/20' : 'bg-green-50 dark:bg-green-900/20'
            },
            { 
              label: 'Memory Usage', 
              value: health.metrics.memory_usage, 
              unit: '%',
              icon: MemoryStick, 
              color: health.metrics.memory_usage > 85 ? 'text-red-600' : health.metrics.memory_usage > 70 ? 'text-yellow-600' : 'text-blue-600',
              bg: health.metrics.memory_usage > 85 ? 'bg-red-50 dark:bg-red-900/20' : health.metrics.memory_usage > 70 ? 'bg-yellow-50 dark:bg-yellow-900/20' : 'bg-blue-50 dark:bg-blue-900/20'
            },
            { 
              label: 'Disk Usage', 
              value: health.metrics.disk_usage, 
              unit: '%',
              icon: HardDrive, 
              color: health.metrics.disk_usage > 90 ? 'text-red-600' : health.metrics.disk_usage > 75 ? 'text-yellow-600' : 'text-purple-600',
              bg: health.metrics.disk_usage > 90 ? 'bg-red-50 dark:bg-red-900/20' : health.metrics.disk_usage > 75 ? 'bg-yellow-50 dark:bg-yellow-900/20' : 'bg-purple-50 dark:bg-purple-900/20'
            },
            { 
              label: 'Network Latency', 
              value: health.metrics.network_latency, 
              unit: 'ms',
              icon: Wifi, 
              color: health.metrics.network_latency > 100 ? 'text-red-600' : health.metrics.network_latency > 50 ? 'text-yellow-600' : 'text-orange-600',
              bg: health.metrics.network_latency > 100 ? 'bg-red-50 dark:bg-red-900/20' : health.metrics.network_latency > 50 ? 'bg-yellow-50 dark:bg-yellow-900/20' : 'bg-orange-50 dark:bg-orange-900/20'
            }
          ].map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`${metric.bg} rounded-lg p-4`}
            >
              <div className="flex items-center justify-between mb-2">
                <metric.icon className={`w-6 h-6 ${metric.color}`} />
                <span className={`text-2xl font-bold ${metric.color}`}>
                  {metric.value}{metric.unit}
                </span>
              </div>
              <p className={`${metric.color} text-sm font-medium`}>{metric.label}</p>
              <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-500 ${
                    metric.value > 80 ? 'bg-red-500' :
                    metric.value > 60 ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(metric.value, 100)}%` }}
                />
              </div>
            </motion.div>
          ))}
        </div>

        {/* Services Status */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Services Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(health.services).map(([service, data]) => (
              <div key={service} className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900 dark:text-white capitalize">
                    {service === 'vectordb' ? 'Vector DB' : service.toUpperCase()}
                  </h3>
                  {getStatusIcon(data.status)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Response: {data.response_time}ms
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Pipeline Health */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Pipeline Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(pipelines).map(([pipeline, data]) => (
              <div key={pipeline} className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900 dark:text-white capitalize">
                    {pipeline.replace('_', ' ')}
                  </h3>
                  {getStatusIcon(data.status)}
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Success Rate:</span>
                    <span className={`font-medium ${
                      data.success_rate > 0.95 ? 'text-green-600' : 
                      data.success_rate > 0.9 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {(data.success_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Avg Response:</span>
                    <span className="text-gray-900 dark:text-white font-medium">
                      {data.avg_response_time}s
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Errors (1h):</span>
                    <span className={`font-medium ${
                      data.errors_last_hour === 0 ? 'text-green-600' : 
                      data.errors_last_hour < 5 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {data.errors_last_hour}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Performance Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'Q&A Response Time', value: health.performance.avg_qa_response_time, unit: 's', icon: MessageSquare, target: 2.0 },
              { label: 'XML Generation Time', value: health.performance.avg_xml_generation_time, unit: 's', icon: FileText, target: 5.0 },
              { label: 'Document Processing', value: health.performance.avg_document_processing_time, unit: 's', icon: FileText, target: 15.0 },
              { label: 'Requests/min', value: health.performance.requests_per_minute, unit: '', icon: TrendingUp, target: 50 }
            ].map((metric, index) => (
              <div key={metric.label} className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <metric.icon className="w-5 h-5 text-gray-600" />
                  <div className="text-right">
                    <span className="text-lg font-bold text-gray-900 dark:text-white">
                      {metric.value}{metric.unit}
                    </span>
                    {metric.value <= metric.target ? (
                      <TrendingUp className="w-4 h-4 text-green-500 inline ml-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-500 inline ml-1" />
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{metric.label}</p>
                <p className="text-xs text-gray-500 dark:text-gray-500">
                  Target: {metric.target}{metric.unit}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {recentActivity.map((activity, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50"
              >
                {getActivityIcon(activity.type)}
                <div className="flex-1">
                  <p className="text-sm text-gray-900 dark:text-white">{activity.message}</p>
                  <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                    <span>{formatTimestamp(activity.timestamp)}</span>
                    {activity.user && (
                      <>
                        <span>•</span>
                        <span>{activity.user}</span>
                      </>
                    )}
                    {activity.duration && (
                      <>
                        <span>•</span>
                        <span>{activity.duration}s</span>
                      </>
                    )}
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium ${
                  activity.status === 'success' ? 'bg-green-100 text-green-800' :
                  activity.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {activity.status}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}