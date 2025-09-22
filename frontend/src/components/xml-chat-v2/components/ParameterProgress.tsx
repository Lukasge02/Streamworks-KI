/**
 * Parameter Progress Component
 * Shows collected vs missing parameters with visual progress
 */

'use client'

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CheckCircle,
  Circle,
  Clock,
  ArrowRight,
  Database,
  Server,
  FileCode,
  AlertCircle,
  TrendingUp
} from 'lucide-react'

// ================================
// TYPES
// ================================

interface ParameterItem {
  name: string
  value?: any
  status: 'collected' | 'missing' | 'optional'
  displayName: string
  description: string
  type: 'required' | 'optional'
}

interface ParameterProgressProps {
  streamType: 'SAP' | 'FILE_TRANSFER' | 'STANDARD' | null
  extractedParameters: Record<string, any>
  completionPercentage: number
  nextParameter?: string
  className?: string
}

// ================================
// STREAM TYPE CONFIGS
// ================================

const STREAM_CONFIGS = {
  SAP: {
    icon: Database,
    color: 'blue',
    label: 'SAP Integration',
    requiredParams: [
      { name: 'stream_name', displayName: 'Stream Name', description: 'Eindeutiger Name des Streams' },
      { name: 'stream_documentation', displayName: 'Dokumentation', description: 'Kurze Beschreibung des Streams' },
      { name: 'short_description', displayName: 'Kurzbeschreibung', description: 'Kurze Zweckbeschreibung' },
      { name: 'system', displayName: 'SAP System', description: 'SAP System (z.B. PA1_100)' },
      { name: 'report', displayName: 'Report/Transaktion', description: 'SAP Report oder Transaktion' }
    ],
    optionalParams: [
      { name: 'max_stream_runs', displayName: 'Max. Läufe', description: 'Maximale parallele Ausführungen' },
      { name: 'variant', displayName: 'Variant', description: 'Report-Variante (optional)' },
      { name: 'batch_user', displayName: 'Batch User', description: 'Batch-Benutzer für SAP' },
      { name: 'scheduling_required_flag', displayName: 'Scheduling', description: 'Benötigt Planung?' }
    ]
  },
  FILE_TRANSFER: {
    icon: Server,
    color: 'green',
    label: 'File Transfer',
    requiredParams: [
      { name: 'stream_name', displayName: 'Stream Name', description: 'Eindeutiger Name des Streams' },
      { name: 'stream_documentation', displayName: 'Dokumentation', description: 'Kurze Beschreibung des Transfers' },
      { name: 'short_description', displayName: 'Kurzbeschreibung', description: 'Was wird übertragen?' },
      { name: 'source_agent', displayName: 'Quell-Agent', description: 'Agent für Dateiübertragung' },
      { name: 'target_agent', displayName: 'Ziel-Agent', description: 'Empfangender Agent' },
      { name: 'source_path', displayName: 'Quellpfad', description: 'Pfad der Quelldateien' },
      { name: 'target_path', displayName: 'Zielpfad', description: 'Pfad für Zieldateien' }
    ],
    optionalParams: [
      { name: 'transfer_method', displayName: 'Transfer-Methode', description: 'COPY, FTP, SFTP, etc.' },
      { name: 'file_pattern', displayName: 'Dateifilter', description: 'z.B. *.xml, *.csv' },
      { name: 'platform', displayName: 'Plattform', description: 'Windows/Linux/Unix' },
      { name: 'max_stream_runs', displayName: 'Max. Läufe', description: 'Maximale parallele Ausführungen' }
    ]
  },
  STANDARD: {
    icon: FileCode,
    color: 'purple',
    label: 'Standard Job',
    requiredParams: [
      { name: 'stream_name', displayName: 'Stream Name', description: 'Eindeutiger Name des Streams' },
      { name: 'stream_documentation', displayName: 'Dokumentation', description: 'Kurze Beschreibung des Jobs' },
      { name: 'short_description', displayName: 'Kurzbeschreibung', description: 'Zweck des Jobs' },
      { name: 'max_stream_runs', displayName: 'Max. Läufe', description: 'Maximale parallele Ausführungen' },
      { name: 'job_name', displayName: 'Job Name', description: 'Interner Name des Jobs' },
      { name: 'job_category', displayName: 'Job Kategorie', description: 'Kategorie / Type des Jobs' }
    ],
    optionalParams: [
      { name: 'scheduling_required_flag', displayName: 'Scheduling', description: 'Benötigt Planung?' },
      { name: 'stream_run_deletion_type', displayName: 'Löschtyp', description: 'Umgang mit alten Läufen' },
      { name: 'is_notification_required', displayName: 'Benachrichtigung', description: 'Benachrichtigungen aktivieren?' }
    ]
  }
}

// ================================
// COMPONENT
// ================================

export default function ParameterProgress({
  streamType,
  extractedParameters,
  completionPercentage,
  nextParameter,
  className = ''
}: ParameterProgressProps) {
  if (!streamType) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2 text-gray-500">
          <Clock className="w-4 h-4" />
          <span className="text-sm">Wählen Sie einen Stream-Typ zum Starten</span>
        </div>
      </div>
    )
  }

  const config = STREAM_CONFIGS[streamType]
  const IconComponent = config.icon

  // Build parameter list
  const allParams: ParameterItem[] = [
    ...config.requiredParams.map(p => ({
      ...p,
      type: 'required' as const,
      status: extractedParameters[p.name] ? 'collected' as const : 'missing' as const,
      value: extractedParameters[p.name]
    })),
    ...config.optionalParams.map(p => ({
      ...p,
      type: 'optional' as const,
      status: extractedParameters[p.name] ? 'collected' as const : 'optional' as const,
      value: extractedParameters[p.name]
    }))
  ]

  const requiredParams = allParams.filter(p => p.type === 'required')
  const optionalParams = allParams.filter(p => p.type === 'optional')
  const collectedRequired = requiredParams.filter(p => p.status === 'collected').length
  const totalRequired = requiredParams.length
  const roundedCompletion = Number.isFinite(completionPercentage)
    ? Math.round(completionPercentage)
    : 0

  return (
    <motion.div
      className={`bg-white border border-gray-200 rounded-lg overflow-hidden ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className={`bg-gradient-to-r from-${config.color}-50 to-${config.color}-100 border-b border-gray-200 p-4`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 bg-${config.color}-500 text-white rounded-lg`}>
              <IconComponent className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{config.label}</h3>
              <p className="text-sm text-gray-600">Parameter-Sammlung</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500">
              {collectedRequired}/{totalRequired} erforderlich
            </div>
          </div>
        </div>

      </div>

      {/* Parameters List */}
      <div className="p-4 space-y-4">
        {/* Required Parameters */}
        <div>
          <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-500" />
            Erforderliche Parameter
          </h4>
          <div className="space-y-2">
            {requiredParams.map((param) => (
              <ParameterItem
                key={param.name}
                param={param}
                isNext={param.name === nextParameter}
                config={config}
              />
            ))}
          </div>
        </div>

        {/* Optional Parameters */}
        {optionalParams.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-500" />
              Optionale Parameter
            </h4>
            <div className="space-y-2">
              {optionalParams.map((param) => (
                <ParameterItem
                  key={param.name}
                  param={param}
                  isNext={param.name === nextParameter}
                  config={config}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Next Parameter Hint */}
      {nextParameter && (
        <motion.div
          className={`bg-${config.color}-50 border-t border-${config.color}-200 p-3`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="flex items-center gap-2 text-sm">
            <ArrowRight className={`w-4 h-4 text-${config.color}-500`} />
            <span className="text-gray-700">
              Nächster Parameter: <strong>{nextParameter}</strong>
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

// ================================
// PARAMETER ITEM COMPONENT
// ================================

interface ParameterItemProps {
  param: ParameterItem
  isNext: boolean
  config: typeof STREAM_CONFIGS[keyof typeof STREAM_CONFIGS]
}

function ParameterItem({ param, isNext, config }: ParameterItemProps) {
  const getStatusIcon = () => {
    switch (param.status) {
      case 'collected':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'missing':
        return <Circle className="w-4 h-4 text-gray-400" />
      case 'optional':
        return <Circle className="w-4 h-4 text-blue-400" />
    }
  }

  const getStatusColor = () => {
    switch (param.status) {
      case 'collected':
        return 'border-green-200 bg-green-50'
      case 'missing':
        return isNext ? `border-${config.color}-300 bg-${config.color}-50 ring-1 ring-${config.color}-200` : 'border-gray-200 bg-gray-50'
      case 'optional':
        return 'border-blue-200 bg-blue-50'
    }
  }

  return (
    <motion.div
      className={`p-3 rounded-lg border transition-all duration-200 ${getStatusColor()}`}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-start gap-3">
        {getStatusIcon()}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h5 className="font-medium text-gray-900 text-sm">
              {param.displayName}
              {param.type === 'required' && (
                <span className="text-red-500 ml-1">*</span>
              )}
            </h5>
            {isNext && (
              <span className={`px-2 py-1 text-xs font-medium bg-${config.color}-100 text-${config.color}-700 rounded-full`}>
                Aktuell
              </span>
            )}
          </div>
          <p className="text-xs text-gray-600 mt-1">{param.description}</p>

          {param.value && (
            <div className="mt-2 p-2 bg-white rounded border">
              <code className="text-xs text-gray-800 font-mono">
                {typeof param.value === 'object' ? JSON.stringify(param.value) : String(param.value)}
              </code>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
