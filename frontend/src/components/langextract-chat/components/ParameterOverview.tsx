/**
 * Parameter Overview Component for LangExtract
 * Shows extracted stream and job parameters with modern UI
 */

'use client'

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CheckCircle,
  AlertCircle,
  Clock,
  Settings,
  Zap,
  Copy,
  Sparkles,
  Edit3,
  Target,
  Info
} from 'lucide-react'
import { toast } from 'sonner'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

// ================================
// TYPES
// ================================

interface ParameterOverviewProps {
  streamParameters: Record<string, any>
  jobParameters: Record<string, any>
  completionPercentage: number
  criticalMissing: string[]
  onParameterEdit?: (parameterName: string, currentValue: any) => void
  className?: string
}

interface ParameterItem {
  key: string
  value: any
  label: string
  status: 'extracted' | 'missing' | 'critical'
  category: 'stream' | 'job'
  description: string
}

// ================================
// PARAMETER DEFINITIONS
// ================================

const STREAM_PARAMETER_DEFINITIONS = {
  StreamName: { label: 'Stream Name', description: 'Eindeutiger Name für den Stream' },
  Beschreibung: { label: 'Beschreibung', description: 'Ausführliche Beschreibung' },
  Kurzbeschreibung: { label: 'Kurzbeschreibung', description: 'Kurze Übersicht' },
  'Max_Läufe': { label: 'Max. Läufe', description: 'Maximale Stream-Ausführungen' },
  Zeitplanung: { label: 'Zeitplanung', description: 'Zeitplanung erforderlich' },
  'E_Mail': { label: 'E-Mail', description: 'Benachrichtigungs-E-Mail' }
}

// Common job parameters (shown for all job types)
const COMMON_JOB_PARAMETER_DEFINITIONS = {
  JobName: { label: 'Job Name', description: 'Name des Jobs' },
  JobTyp: { label: 'Job Typ', description: 'Art des Jobs (SAP, FILE_TRANSFER, etc.)' },
  System: { label: 'System', description: 'Zielsystem' },
  Agent: { label: 'Agent', description: 'Ausführender Agent' },
  Benutzername: { label: 'Benutzername', description: 'System-Benutzername' }
}

// Standard job parameters
const STANDARD_JOB_PARAMETER_DEFINITIONS = {
  Programm: { label: 'Programm', description: 'Auszuführendes Programm' }
}

// FILE_TRANSFER specific parameters
const FILE_TRANSFER_PARAMETER_DEFINITIONS = {
  SourceServer: { label: 'Quellserver', description: 'Server von dem übertragen wird' },
  TargetServer: { label: 'Zielserver', description: 'Server zu dem übertragen wird' },
  Protocol: { label: 'Protokoll', description: 'Übertragungsprotokoll (SFTP, FTP, HTTP)' },
  FilePattern: { label: 'Dateimuster', description: 'Dateimuster (*.csv, *.xlsx, etc.)' },
  Quellpfad: { label: 'Quellpfad', description: 'Quellverzeichnis' },
  Zielpfad: { label: 'Zielpfad', description: 'Zielverzeichnis' }
}

// SAP specific parameters
const SAP_PARAMETER_DEFINITIONS = {
  SAPSystem: { label: 'SAP System', description: 'SAP-System (ZTV, GT123, PRD, DEV)' },
  TableName: { label: 'Tabellen Name', description: 'SAP-Tabelle (PA1, ZTV_CALENDAR)' },
  ExportFormat: { label: 'Export Format', description: 'Export-Format (CSV, XLSX, XML)' },
  SAPUser: { label: 'SAP Benutzer', description: 'SAP-Benutzer (SAPCOMM, etc.)' }
}

// Function to get relevant job parameters based on job type and selection state
const getJobParameterDefinitions = (jobType: string | null) => {
  // If no job type is selected, only show JobTyp parameter
  if (!jobType) {
    return {
      JobTyp: COMMON_JOB_PARAMETER_DEFINITIONS.JobTyp
    }
  }

  // Once job type is selected, show all relevant parameters
  const definitions = { ...COMMON_JOB_PARAMETER_DEFINITIONS }

  switch (jobType) {
    case 'FILE_TRANSFER':
      return { ...definitions, ...FILE_TRANSFER_PARAMETER_DEFINITIONS }
    case 'SAP':
      return { ...definitions, ...SAP_PARAMETER_DEFINITIONS }
    case 'STANDARD':
      return { ...definitions, ...STANDARD_JOB_PARAMETER_DEFINITIONS }
    default:
      // For unknown job types, show common parameters only
      return definitions
  }
}

// ================================
// COMPONENT
// ================================

export default function ParameterOverview({
  streamParameters = {},
  jobParameters = {},
  completionPercentage,
  criticalMissing = [],
  onParameterEdit,
  className = ''
}: ParameterOverviewProps) {

  // Get current job type for adaptive parameter display
  const currentJobType = jobParameters?.JobTyp || null
  const relevantJobParameterDefinitions = getJobParameterDefinitions(currentJobType)

  // Check if we have a job type selected
  const hasJobTypeSelected = currentJobType && currentJobType.trim() !== ''

  // Build parameter display items
  const allParameters: ParameterItem[] = []

  // Stream parameters (always shown)
  Object.entries(STREAM_PARAMETER_DEFINITIONS).forEach(([key, def]) => {
    const hasValue = streamParameters.hasOwnProperty(key) &&
                    streamParameters[key] !== null &&
                    streamParameters[key] !== undefined &&
                    streamParameters[key] !== ''

    allParameters.push({
      key,
      value: streamParameters[key],
      label: def.label,
      status: criticalMissing.includes(key) ? 'critical' : (hasValue ? 'extracted' : 'missing'),
      category: 'stream',
      description: def.description
    })
  })

  // Job parameters (filtered by job type)
  Object.entries(relevantJobParameterDefinitions).forEach(([key, def]) => {
    const hasValue = jobParameters.hasOwnProperty(key) &&
                    jobParameters[key] !== null &&
                    jobParameters[key] !== undefined &&
                    jobParameters[key] !== ''

    allParameters.push({
      key,
      value: jobParameters[key],
      label: def.label,
      status: criticalMissing.includes(key) ? 'critical' : (hasValue ? 'extracted' : 'missing'),
      category: 'job',
      description: def.description
    })
  })

  const streamParams = allParameters.filter(p => p.category === 'stream')
  const jobParams = allParameters.filter(p => p.category === 'job')

  const extractedCount = allParameters.filter(p => p.status === 'extracted').length
  const totalCount = allParameters.length
  const criticalCount = allParameters.filter(p => p.status === 'critical').length

  const handleCopyValue = async (value: any) => {
    try {
      await navigator.clipboard.writeText(String(value))
      toast.success('Wert kopiert!')
    } catch (error) {
      toast.error('Kopieren fehlgeschlagen')
    }
  }

  const handleParameterEdit = (param: ParameterItem) => {
    onParameterEdit?.(param.key, param.value)
  }

  const renderParameterGroup = (
    title: string,
    parameters: ParameterItem[],
    icon: React.ComponentType<any>,
    color: string
  ) => {
    const Icon = icon
    const extractedInGroup = parameters.filter(p => p.status === 'extracted').length
    const criticalInGroup = parameters.filter(p => p.status === 'critical').length

    return (
      <motion.div
        className="mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="overflow-hidden">
          {/* Group Header */}
          <div className={`bg-${color}-50 border-b border-${color}-100 p-4`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 bg-${color}-100 rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-4 h-4 text-${color}-600`} />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{title}</h4>
                  <p className="text-sm text-gray-600">
                    {extractedInGroup}/{parameters.length} Parameter
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                {criticalInGroup > 0 && (
                  <Badge variant="destructive" className="text-xs">
                    {criticalInGroup} kritisch
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {/* Parameters */}
          <div className="p-4 space-y-3">
            <AnimatePresence>
              {parameters.map((param, index) => (
                <motion.div
                  key={param.key}
                  className={`group relative overflow-hidden rounded-lg border-2 transition-all duration-200 ${
                    param.status === 'extracted'
                      ? 'border-emerald-200 bg-emerald-50/50 hover:bg-emerald-50'
                      : param.status === 'critical'
                      ? 'border-red-200 bg-red-50/50 hover:bg-red-50'
                      : 'border-gray-200 bg-gray-50/50 hover:bg-gray-50'
                  }`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  title={param.description}
                >
                  <div className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        {param.status === 'extracted' ? (
                          <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                        ) : param.status === 'critical' ? (
                          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                        ) : (
                          <Clock className="w-5 h-5 text-gray-400 flex-shrink-0" />
                        )}

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900 truncate">
                              {param.label}
                            </span>
                            {param.status === 'critical' && (
                              <Badge variant="destructive" className="text-xs">
                                Kritisch
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {param.description}
                          </p>
                        </div>
                      </div>

                      {/* Value and Actions */}
                      <div className="flex items-center gap-2 ml-4">
                        {param.status === 'extracted' ? (
                          <div className="flex items-center gap-2">
                            <code className="text-sm font-mono text-gray-700 bg-white px-2 py-1 rounded border max-w-32 truncate">
                              {String(param.value)}
                            </code>
                            <div className="flex gap-1">
                              <button
                                onClick={() => handleCopyValue(param.value)}
                                className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-white rounded transition-all"
                                title="Kopieren"
                              >
                                <Copy className="w-4 h-4 text-gray-500" />
                              </button>
                              {onParameterEdit && (
                                <button
                                  onClick={() => handleParameterEdit(param)}
                                  className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-white rounded transition-all"
                                  title="Bearbeiten"
                                >
                                  <Edit3 className="w-4 h-4 text-gray-500" />
                                </button>
                              )}
                            </div>
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400 px-3 py-1 bg-white rounded border">
                            {param.status === 'critical' ? 'Fehlt (kritisch)' : 'Nicht gesetzt'}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </Card>
      </motion.div>
    )
  }

  return (
    <motion.div
      className={`h-full w-full flex flex-col ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
    >
      {/* Critical Missing Alert */}
      {criticalCount > 0 && (
        <motion.div
          className="m-6 p-3 bg-red-50 border border-red-200 rounded-lg"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600" />
            <span className="text-sm font-medium text-red-900">
              {criticalCount} kritische Parameter fehlen
            </span>
          </div>
        </motion.div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Stream Parameters */}
        {renderParameterGroup(
          'Stream-Konfiguration',
          streamParams,
          Settings,
          'blue'
        )}

        {/* Job Parameters - Conditional Display */}
        {!hasJobTypeSelected ? (
          // Phase 1: Only show JobTyp selection
          renderParameterGroup(
            'Job-Typ auswählen',
            jobParams.filter(p => p.key === 'JobTyp'),
            Target,
            'orange'
          )
        ) : (
          // Phase 2: Show full job configuration
          renderParameterGroup(
            `${currentJobType} Job-Konfiguration`,
            jobParams,
            Zap,
            'emerald'
          )
        )}

        {/* Empty State */}
        {extractedCount === 0 && (
          <div className="text-center py-12">
            <Target className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500">
              Noch keine Parameter extrahiert
            </p>
            <p className="text-gray-400 text-sm mt-1">
              Parameter werden während der Unterhaltung automatisch erkannt
            </p>
          </div>
        )}
      </div>

      {/* Footer Summary */}
      <div className="bg-gray-50 border-t border-gray-200 p-4">
        <div className="flex justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
            <span className="text-gray-600">{extractedCount} extrahiert</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-gray-600">{criticalCount} kritisch</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
            <span className="text-gray-600">{totalCount - extractedCount - criticalCount} ausstehend</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}