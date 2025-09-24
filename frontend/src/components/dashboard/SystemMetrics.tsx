'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Activity,
  Clock,
  Database,
  HardDrive,
  Zap,
  TrendingUp,
  Users,
  Server,
  Cpu,
  MemoryStick,
  Upload,
  Download,
  AlertTriangle
} from 'lucide-react'
import { useRealTime } from '@/services/realtime.service'
import { SystemMetrics as SystemMetricsType } from '@/services/realtime.service'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ComponentType<any>
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'gray'
  trend?: {
    value: number
    isPositive: boolean
    label?: string
  }
  loading?: boolean
}

function MetricCard({ title, value, subtitle, icon: Icon, color, trend, loading }: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400',
    green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400',
    red: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
    gray: 'bg-gray-50 dark:bg-gray-700/50 text-gray-600 dark:text-gray-400'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          {loading ? (
            <div className="animate-pulse h-8 w-20 bg-gray-200 dark:bg-gray-600 rounded mt-2"></div>
          ) : (
            <div className="flex items-baseline space-x-2 mt-2">
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                {typeof value === 'number' ? value.toLocaleString() : value}
              </p>
              {trend && (
                <div className={cn(
                  "flex items-center space-x-1 text-sm font-medium",
                  trend.isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
                )}>
                  <TrendingUp className={cn(
                    "h-3 w-3",
                    !trend.isPositive && "rotate-180"
                  )} />
                  <span>{trend.value}%</span>
                </div>
              )}
            </div>
          )}
          {subtitle && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={cn("p-3 rounded-lg", colorClasses[color])}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </motion.div>
  )
}

interface ProgressBarProps {
  title: string
  value: number
  max: number
  color: 'blue' | 'green' | 'yellow' | 'red'
  subtitle?: string
}

function ProgressBar({ title, value, max, color, subtitle }: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100)
  
  const colorClasses = {
    blue: 'bg-primary-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500'
  }

  const bgColorClasses = {
    blue: 'bg-primary-100 dark:bg-primary-900/20',
    green: 'bg-green-100 dark:bg-green-900/20',
    yellow: 'bg-yellow-100 dark:bg-yellow-900/20',
    red: 'bg-red-100 dark:bg-red-900/20'
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
        <p className="text-sm font-semibold text-gray-900 dark:text-white">
          {percentage.toFixed(1)}%
        </p>
      </div>
      
      <div className={cn("h-2 rounded-full", bgColorClasses[color])}>
        <motion.div
          className={cn("h-full rounded-full", colorClasses[color])}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>
      
      {subtitle && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">{subtitle}</p>
      )}
    </div>
  )
}

export function SystemMetrics() {
  const { connected, metrics } = useRealTime()
  const [historicalData, setHistoricalData] = useState<SystemMetricsType[]>([])

  // Store historical metrics for trends
  useEffect(() => {
    if (metrics) {
      setHistoricalData(prev => {
        const newData = [...prev, metrics]
        // Keep only last 60 data points (1 minute of data at 1s intervals)
        return newData.slice(-60)
      })
    }
  }, [metrics])

  // Calculate trends
  const calculateTrend = (field: keyof SystemMetricsType): { value: number, isPositive: boolean } | undefined => {
    if (historicalData.length < 2) return undefined
    
    const recent = historicalData.slice(-5)
    const older = historicalData.slice(-10, -5)
    
    if (recent.length === 0 || older.length === 0) return undefined
    
    const recentAvg = recent.reduce((sum, item) => sum + (item[field] as number), 0) / recent.length
    const olderAvg = older.reduce((sum, item) => sum + (item[field] as number), 0) / older.length
    
    if (olderAvg === 0) return undefined
    
    const change = ((recentAvg - olderAvg) / olderAvg) * 100
    
    return {
      value: Math.abs(change),
      isPositive: field === 'system_load' ? change < 0 : change >= 0  // Lower system load is better
    }
  }

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
    return `${(ms / 60000).toFixed(1)}m`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            System-Metriken
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Echtzeit-Überwachung der Systemleistung
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className={cn(
            "w-2 h-2 rounded-full",
            connected ? "bg-green-500 animate-pulse" : "bg-red-500"
          )} />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {connected ? "Live-Updates" : "Verbindung getrennt"}
          </span>
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Upload-Warteschlange"
          value={metrics?.upload_queue_size ?? 0}
          subtitle="Dateien warten auf Verarbeitung"
          icon={Upload}
          color="blue"
          trend={calculateTrend('upload_queue_size')}
          loading={!metrics}
        />
        
        <MetricCard
          title="Aktive Uploads"
          value={metrics?.active_uploads ?? 0}
          subtitle="Werden gerade verarbeitet"
          icon={Activity}
          color="green"
          trend={calculateTrend('active_uploads')}
          loading={!metrics}
        />
        
        <MetricCard
          title="Verarbeitungsschlange"
          value={metrics?.processing_queue_size ?? 0}
          subtitle="Dokumente in der Pipeline"
          icon={Clock}
          color="yellow"
          trend={calculateTrend('processing_queue_size')}
          loading={!metrics}
        />
        
        <MetricCard
          title="Durchschn. Verarbeitungszeit"
          value={metrics ? formatDuration(metrics.average_processing_time) : '--'}
          subtitle="Pro Dokument"
          icon={Zap}
          color="purple"
          trend={calculateTrend('average_processing_time')}
          loading={!metrics}
        />
      </div>

      {/* Resource Usage */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ProgressBar
          title="System-Last"
          value={metrics?.system_load ?? 0}
          max={100}
          color={metrics && metrics.system_load > 80 ? "red" : metrics && metrics.system_load > 60 ? "yellow" : "green"}
          subtitle="CPU-Auslastung und Systemlast"
        />
        
        <ProgressBar
          title="Speicher-Auslastung"
          value={metrics?.memory_usage ?? 0}
          max={100}
          color={metrics && metrics.memory_usage > 80 ? "red" : metrics && metrics.memory_usage > 60 ? "yellow" : "green"}
          subtitle="RAM-Verbrauch des Systems"
        />
        
        <ProgressBar
          title="Speicherplatz"
          value={metrics?.storage_usage ?? 0}
          max={100}
          color={metrics && metrics.storage_usage > 90 ? "red" : metrics && metrics.storage_usage > 75 ? "yellow" : "green"}
          subtitle="Festplattenspeicher belegt"
        />
      </div>

      {/* Performance Indicators */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Performance-Indikatoren
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* System Health */}
          <div className="text-center">
            <div className={cn(
              "inline-flex items-center justify-center w-12 h-12 rounded-full mb-2",
              (!metrics || metrics.system_load < 70) ? "bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400" :
              metrics.system_load < 85 ? "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400" :
              "bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400"
            )}>
              {(!metrics || metrics.system_load < 70) ? (
                <Activity className="h-6 w-6" />
              ) : metrics.system_load < 85 ? (
                <AlertTriangle className="h-6 w-6" />
              ) : (
                <AlertTriangle className="h-6 w-6" />
              )}
            </div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">System-Zustand</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {(!metrics || metrics.system_load < 70) ? "Optimal" :
               metrics.system_load < 85 ? "Belastet" : "Überlastet"}
            </p>
          </div>

          {/* Response Time */}
          <div className="text-center">
            <div className={cn(
              "inline-flex items-center justify-center w-12 h-12 rounded-full mb-2",
              (!metrics || metrics.average_processing_time < 5000) ? "bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400" :
              metrics.average_processing_time < 10000 ? "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400" :
              "bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400"
            )}>
              <Clock className="h-6 w-6" />
            </div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">Antwortzeit</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {(!metrics || metrics.average_processing_time < 5000) ? "Schnell" :
               metrics.average_processing_time < 10000 ? "Moderat" : "Langsam"}
            </p>
          </div>

          {/* Throughput */}
          <div className="text-center">
            <div className={cn(
              "inline-flex items-center justify-center w-12 h-12 rounded-full mb-2",
              (!metrics || (metrics.active_uploads + metrics.processing_queue_size) < 10) ? "bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400" :
              (metrics.active_uploads + metrics.processing_queue_size) < 25 ? "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400" :
              "bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400"
            )}>
              <Database className="h-6 w-6" />
            </div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">Durchsatz</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {(!metrics || (metrics.active_uploads + metrics.processing_queue_size) < 10) ? "Niedrig" :
               (metrics.active_uploads + metrics.processing_queue_size) < 25 ? "Mittel" : "Hoch"}
            </p>
          </div>
        </div>
      </div>

      {/* Real-time Activity Log (if metrics available) */}
      {historicalData.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Letzte Aktivität
          </h3>
          
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {historicalData.slice(-5).reverse().map((data, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary-500"></div>
                  <span>
                    {data.active_uploads} aktive, {data.processing_queue_size} wartend
                  </span>
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  vor {index === 0 ? 'jetzt' : `${index}s`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SystemMetrics