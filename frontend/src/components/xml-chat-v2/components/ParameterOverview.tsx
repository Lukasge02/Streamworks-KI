/**
 * Parameter Overview Component
 * Shows extracted parameters and missing parameters in a beautiful right panel
 */

'use client'

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
  Target,
  Copy,
  Eye,
  Settings,
  ArrowRight,
  Sparkles,
  FileCode,
  Info
} from 'lucide-react'
import { toast } from 'sonner'

// ================================
// TYPES
// ================================

interface ParameterOverviewProps {
  streamType?: 'SAP' | 'FILE_TRANSFER' | 'STANDARD' | null
  extractedParameters: Record<string, any>
  completionPercentage: number
  nextParameter?: string
  className?: string
}

interface ParameterDisplayItem {
  key: string
  value: any
  label: string
  status: 'extracted' | 'missing' | 'optional'
  category: 'basic' | 'connection' | 'advanced'
  description: string
}

// ================================
// PARAMETER DEFINITIONS
// ================================

const PARAMETER_DEFINITIONS = {
  SAP: {
    basic: [
      { key: 'StreamName', label: 'Stream Name', description: 'Eindeutiger Name für den Stream' },
      { key: 'Description', label: 'Beschreibung', description: 'Beschreibung des Streams' },
      { key: 'SystemName', label: 'SAP System', description: 'SAP-System (z.B. ZTV, PA1)' },
      { key: 'Client', label: 'Mandant', description: 'SAP-Mandant (z.B. 100)' }
    ],
    connection: [
      { key: 'AgentName', label: 'Agent', description: 'Ausführender Agent' },
      { key: 'Username', label: 'Benutzername', description: 'SAP-Benutzername' },
      { key: 'Language', label: 'Sprache', description: 'SAP-Sprache (z.B. DE, EN)' }
    ],
    advanced: [
      { key: 'Program', label: 'Programm', description: 'SAP-Programm oder Report' },
      { key: 'Parameters', label: 'Parameter', description: 'SAP-spezifische Parameter' },
      { key: 'Scheduling', label: 'Zeitplanung', description: 'Ausführungszeiten' }
    ]
  },
  FILE_TRANSFER: {
    basic: [
      { key: 'StreamName', label: 'Stream Name', description: 'Eindeutiger Name für den Transfer' },
      { key: 'Description', label: 'Beschreibung', description: 'Beschreibung des Transfers' },
      { key: 'FilePattern', label: 'Dateimuster', description: 'Datei-Pattern (z.B. *.xml)' }
    ],
    connection: [
      { key: 'SourceAgent', label: 'Quell-Agent', description: 'Agent für Quelle' },
      { key: 'TargetAgent', label: 'Ziel-Agent', description: 'Agent für Ziel' },
      { key: 'SourcePath', label: 'Quellpfad', description: 'Quellverzeichnis' },
      { key: 'TargetPath', label: 'Zielpfad', description: 'Zielverzeichnis' },
      { key: 'Protocol', label: 'Protokoll', description: 'Übertragungsprotokoll (FTP, SFTP)' }
    ],
    advanced: [
      { key: 'Encryption', label: 'Verschlüsselung', description: 'Verschlüsselungseinstellungen' },
      { key: 'Validation', label: 'Validierung', description: 'Dateivalidierung' },
      { key: 'Compression', label: 'Komprimierung', description: 'Komprimierungsoptionen' }
    ]
  },
  STANDARD: {
    basic: [
      { key: 'StreamName', label: 'Stream Name', description: 'Eindeutiger Name für den Job' },
      { key: 'Description', label: 'Beschreibung', description: 'Beschreibung des Jobs' },
      { key: 'Command', label: 'Befehl', description: 'Auszuführender Befehl' }
    ],
    connection: [
      { key: 'AgentName', label: 'Agent', description: 'Ausführender Agent' },
      { key: 'WorkingDirectory', label: 'Arbeitsverzeichnis', description: 'Arbeitsverzeichnis' },
      { key: 'Environment', label: 'Umgebung', description: 'Umgebungsvariablen' }
    ],
    advanced: [
      { key: 'Timeout', label: 'Timeout', description: 'Maximale Ausführungszeit' },
      { key: 'RetryCount', label: 'Wiederholungen', description: 'Anzahl Wiederholungen bei Fehlern' },
      { key: 'Priority', label: 'Priorität', description: 'Ausführungspriorität' }
    ]
  }
}

// ================================
// COMPONENT
// ================================

export default function ParameterOverview({
  streamType,
  extractedParameters = {},
  completionPercentage,
  nextParameter,
  className = ''
}: ParameterOverviewProps) {

  const parameterDefs = streamType ? PARAMETER_DEFINITIONS[streamType] : null

  // Enhanced Debug logging
  console.group('🔍 ParameterOverview Debug')
  console.log('📊 Basic Info:', {
    streamType,
    completionPercentage,
    nextParameter
  })
  console.log('📥 Raw Parameters:', extractedParameters)
  console.log('🔑 Parameter Keys:', Object.keys(extractedParameters))
  console.log('📝 Parameter Values:', Object.entries(extractedParameters).map(([key, value]) =>
    `${key}: "${value}" (${typeof value})`
  ))
  console.groupEnd()

  if (!parameterDefs) {
    console.log('❌ No parameter definitions found for streamType:', streamType)
    return null
  }

  // Build parameter display items with better key mapping
  const allParameters: ParameterDisplayItem[] = []

  // Helper function to check if parameter has value
  const hasValue = (paramKey: string, altKeys: string[] = []) => {
    // Check main key
    if (extractedParameters.hasOwnProperty(paramKey) &&
        extractedParameters[paramKey] !== null &&
        extractedParameters[paramKey] !== undefined &&
        extractedParameters[paramKey] !== '') {
      return true
    }

    // Check alternative keys (for different naming conventions)
    for (const altKey of altKeys) {
      if (extractedParameters.hasOwnProperty(altKey) &&
          extractedParameters[altKey] !== null &&
          extractedParameters[altKey] !== undefined &&
          extractedParameters[altKey] !== '') {
        return true
      }
    }

    return false
  }

  // Helper function to get parameter value
  const getValue = (paramKey: string, altKeys: string[] = []) => {
    if (extractedParameters[paramKey] !== undefined && extractedParameters[paramKey] !== null && extractedParameters[paramKey] !== '') {
      return extractedParameters[paramKey]
    }

    for (const altKey of altKeys) {
      if (extractedParameters[altKey] !== undefined && extractedParameters[altKey] !== null && extractedParameters[altKey] !== '') {
        return extractedParameters[altKey]
      }
    }

    return null
  }

  Object.entries(parameterDefs).forEach(([category, params]) => {
    params.forEach(param => {
      // Define alternative key mappings for ALL parameter names
      const altKeys: string[] = []
      switch (param.key) {
        case 'StreamName':
          altKeys.push('stream_name', 'streamName', 'name', 'Stream_Name')
          break
        case 'SystemName':
          altKeys.push('system_name', 'systemName', 'sap_system', 'system', 'System', 'System_Name')
          break
        case 'Client':
          altKeys.push('client', 'mandant', 'Client', 'client_number', 'mandant_number')
          break
        case 'Description':
          altKeys.push('description', 'desc', 'Description', 'beschreibung')
          break
        case 'AgentName':
          altKeys.push('agent_name', 'agentName', 'agent', 'Agent_Name')
          break
        case 'Program':
          altKeys.push('program', 'report', 'Program', 'Report', 'sap_program', 'sap_report')
          break
        // FILE_TRANSFER specific mappings
        case 'SourceAgent':
          altKeys.push('source_agent', 'sourceAgent', 'quell_agent', 'Source_Agent')
          break
        case 'TargetAgent':
          altKeys.push('target_agent', 'targetAgent', 'ziel_agent', 'Target_Agent')
          break
        case 'SourcePath':
          altKeys.push('source_path', 'sourcePath', 'quellpfad', 'Source_Path')
          break
        case 'TargetPath':
          altKeys.push('target_path', 'targetPath', 'zielpfad', 'Target_Path')
          break
        case 'FilePattern':
          altKeys.push('file_pattern', 'filePattern', 'pattern', 'File_Pattern')
          break
      }

      const paramHasValue = hasValue(param.key, altKeys)
      const paramValue = getValue(param.key, altKeys)

      // Debug parameter mapping
      if (Object.keys(extractedParameters).length > 0) {
        console.log(`🔄 Parameter ${param.key}:`, {
          hasValue: paramHasValue,
          value: paramValue,
          checkedKeys: [param.key, ...altKeys],
          availableKeys: Object.keys(extractedParameters)
        })
      }

      allParameters.push({
        key: param.key,
        value: paramValue,
        label: param.label,
        status: paramHasValue ? 'extracted' : (category === 'basic' ? 'missing' : 'optional'),
        category: category as 'basic' | 'connection' | 'advanced',
        description: param.description
      })
    })
  })

  const extractedCount = allParameters.filter(p => p.status === 'extracted').length
  const missingCount = allParameters.filter(p => p.status === 'missing').length
  const totalCount = allParameters.length

  // Recalculate completion percentage based on actual extracted parameters
  const actualCompletionPercentage = totalCount > 0 ? Math.round((extractedCount / totalCount) * 100) : 0

  console.log('📊 Parameter Overview Stats:', {
    extractedCount,
    totalCount,
    actualCompletionPercentage,
    completionPercentage
  })

  const handleCopyValue = async (value: any) => {
    try {
      await navigator.clipboard.writeText(String(value))
      toast.success('Wert in Zwischenablage kopiert!')
    } catch (error) {
      toast.error('Kopieren fehlgeschlagen')
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'basic': return Settings
      case 'connection': return Zap
      case 'advanced': return Target
      default: return Info
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'basic': return 'blue'
      case 'connection': return 'emerald'
      case 'advanced': return 'purple'
      default: return 'gray'
    }
  }

  return (
    <motion.div
      className={`w-96 bg-white border-l border-gray-200 shadow-xl flex flex-col ${className}`}
      initial={{ opacity: 0, x: 384 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      {/* Simple Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">Parameter</h3>
            <p className="text-gray-500 text-sm">{streamType} Stream</p>
          </div>
          <div className="text-right">
            <div className="text-lg font-semibold text-gray-900">{extractedCount}/{totalCount}</div>
            <div className="text-xs text-gray-500">{actualCompletionPercentage}%</div>
          </div>
        </div>
      </div>

      {/* Next Parameter Info */}
      {nextParameter && (
        <div className="bg-blue-50 border-b border-blue-100 p-3">
          <div className="text-xs text-blue-700">
            Nächster Parameter: {allParameters.find(p => p.key === nextParameter)?.label || nextParameter}
          </div>
        </div>
      )}

      {/* Parameters - Modern Layout */}
      <div className="flex-1 overflow-y-auto bg-gray-50">
        {Object.entries(parameterDefs).map(([category, params]) => {
          const CategoryIcon = getCategoryIcon(category)
          const categoryColor = getCategoryColor(category)
          const categoryParams = allParameters.filter(p => p.category === category)
          const extractedInCategory = categoryParams.filter(p => p.status === 'extracted').length

          const categoryLabels = {
            basic: 'Grundkonfiguration',
            connection: 'Verbindungsdetails',
            advanced: 'Erweiterte Optionen'
          }

          return (
            <motion.div
              key={category}
              className="mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              {/* Compact Category Header */}
              <div className="mx-4 mb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-6 h-6 bg-${categoryColor}-100 rounded flex items-center justify-center`}>
                      <CategoryIcon className={`w-3 h-3 text-${categoryColor}-600`} />
                    </div>
                    <h4 className="font-medium text-gray-900 text-sm">
                      {categoryLabels[category as keyof typeof categoryLabels]}
                    </h4>
                    <span className="text-xs text-gray-500">
                      ({extractedInCategory}/{categoryParams.length})
                    </span>
                  </div>
                  <div className={`px-2 py-0.5 bg-${categoryColor}-100 text-${categoryColor}-700 text-xs font-medium rounded`}>
                    {Math.round((extractedInCategory / categoryParams.length) * 100)}%
                  </div>
                </div>
              </div>

              {/* Compact Parameter List */}
              <div className="mx-4 space-y-1">
                <AnimatePresence>
                  {categoryParams.map((param, index) => (
                    <motion.div
                      key={param.key}
                      className={`group relative overflow-hidden rounded-lg border transition-all duration-200 ${
                        param.status === 'extracted'
                          ? 'bg-white border-emerald-200 hover:shadow-sm'
                          : param.status === 'missing'
                          ? 'bg-white border-red-200 hover:shadow-sm'
                          : 'bg-white border-gray-200 opacity-75'
                      }`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.02 }}
                      title={param.description} // Tooltip on hover
                    >
                      {/* Status Indicator */}
                      <div className={`absolute left-0 top-0 w-1 h-full ${
                        param.status === 'extracted'
                          ? 'bg-emerald-500'
                          : param.status === 'missing'
                          ? 'bg-red-500'
                          : 'bg-gray-300'
                      }`} />

                      <div className="p-3 pl-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 flex-1 min-w-0">
                            {param.status === 'extracted' ? (
                              <CheckCircle className="w-3 h-3 text-emerald-500 flex-shrink-0" />
                            ) : param.status === 'missing' ? (
                              <AlertCircle className="w-3 h-3 text-red-500 flex-shrink-0" />
                            ) : (
                              <Clock className="w-3 h-3 text-gray-400 flex-shrink-0" />
                            )}
                            <span className="font-medium text-sm text-gray-900 truncate">
                              {param.label}
                            </span>
                          </div>

                          {/* Value or Status */}
                          <div className="flex items-center gap-2">
                            {param.status === 'extracted' ? (
                              <div className="flex items-center gap-1">
                                <code className="text-xs font-mono text-gray-600 max-w-24 truncate">
                                  {String(param.value)}
                                </code>
                                <button
                                  onClick={() => handleCopyValue(param.value)}
                                  className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-gray-200 rounded transition-all"
                                  title="Kopieren"
                                >
                                  <Copy className="w-3 h-3 text-gray-500" />
                                </button>
                              </div>
                            ) : (
                              <span className="text-xs text-gray-400">
                                {param.status === 'missing' ? 'Fehlt' : 'Optional'}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Simple Summary Footer */}
      <div className="bg-gray-50 border-t border-gray-200 p-4">
        <div className="text-center text-sm text-gray-600">
          {extractedCount} von {totalCount} Parameter ({actualCompletionPercentage}%)
        </div>
      </div>
    </motion.div>
  )
}