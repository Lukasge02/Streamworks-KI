/**
 * StreamDataDisplay Component - Hybrid Data System
 * Intelligente Fusion von echten wizard_data und Fallback-Mock-Daten
 */
'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import {
  ChevronDown,
  ChevronRight,
  Zap,
  Database,
  FolderOpen,
  Settings,
  Calendar,
  GitBranch,
  Server,
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Code2
} from 'lucide-react'

import { XMLStream } from '@/services/xmlStreamsApi'
import { cn } from '@/lib/utils'

interface StreamDataDisplayProps {
  stream: XMLStream
  className?: string
}

export const StreamDataDisplay: React.FC<StreamDataDisplayProps> = ({
  stream,
  className
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['job', 'stream', 'scheduling'])
  )

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId)
    } else {
      newExpanded.add(sectionId)
    }
    setExpandedSections(newExpanded)
  }

  // Echte Wizard-Daten ohne Fallbacks
  const getWizardData = () => {
    const wizardData = stream.wizard_data || {}
    const hasRealData = wizardData && Object.keys(wizardData).length > 0

    console.log('🔄 StreamDataDisplay Real Data Analysis:', {
      streamId: stream.id,
      hasRealWizardData: hasRealData,
      realDataKeys: Object.keys(wizardData),
      realDataStructure: wizardData,
      streamJobType: stream.job_type
    })

    // Nur echte Werte holen, keine Fallbacks
    const getFieldValue = (paths: string[]) => {
      for (const path of paths) {
        const keys = path.split('.')
        let value = wizardData

        for (const key of keys) {
          value = value?.[key]
          if (value === undefined || value === null) break
        }

        if (value !== undefined && value !== null && value !== '') {
          return value
        }
      }
      return null // Keine Fallbacks!
    }

    // Base Job Configuration - nur echte Daten
    const baseData = {
      jobName: getFieldValue([
        'jobName', 'streamName', 'name', 'title',
        'streamProperties.name', 'basic.name'
      ]) || stream.stream_name || null,

      description: getFieldValue([
        'description', 'jobDescription', 'streamDescription',
        'basic.description', 'details.description'
      ]) || stream.description || null,

      jobType: getFieldValue([
        'jobType', 'type', 'streamType', 'workflowType'
      ]) || stream.job_type || null,

      priority: getFieldValue([
        'priority', 'jobPriority', 'executionPriority'
      ]),

      createdBy: stream.created_by || null
    }

    // Scheduling Configuration - nur echte Daten
    const schedulingData = {
      type: getFieldValue([
        'scheduling.type', 'schedule.type', 'scheduleType', 'timing.type'
      ]),

      startTime: getFieldValue([
        'scheduling.startTime', 'schedule.startTime', 'startTime', 'timing.startTime'
      ]),

      frequency: getFieldValue([
        'scheduling.frequency', 'schedule.frequency', 'frequency', 'timing.frequency'
      ]),

      nextRun: getFieldValue([
        'scheduling.nextRun', 'schedule.nextRun', 'nextExecution'
      ]),

      days: getFieldValue([
        'scheduling.days', 'schedule.days', 'executionDays'
      ])
    }

    // Stream Properties - nur echte Daten
    const streamProperties = {
      streamName: getFieldValue([
        'streamProperties.name', 'stream.name', 'streamName', 'name'
      ]) || stream.stream_name || null,

      streamType: getFieldValue([
        'streamProperties.type', 'stream.type', 'streamType'
      ]),

      sourceSystem: getFieldValue([
        'streamProperties.source', 'source.system', 'sourceConfig.system', 'dataSource'
      ]),

      targetSystem: getFieldValue([
        'streamProperties.target', 'target.system', 'targetConfig.system', 'dataTarget'
      ]),

      dataFormat: getFieldValue([
        'streamProperties.format', 'stream.format', 'dataFormat', 'outputFormat'
      ]),

      encoding: getFieldValue([
        'streamProperties.encoding', 'stream.encoding', 'dataEncoding'
      ]),

      status: stream.status || null
    }

    // Job Type Specific Data mit echten Daten
    let jobSpecificData = null

    if (stream.job_type === 'sap') {
      jobSpecificData = {
        connectionHost: getFieldValue([
          'sapConnection.host', 'sap.host', 'connection.host'
        ]),

        client: getFieldValue([
          'sapConnection.client', 'sap.client', 'connection.client'
        ]),

        systemId: getFieldValue([
          'sapConnection.system', 'sapConnection.systemId', 'sap.system'
        ]),

        username: getFieldValue([
          'sapConnection.username', 'sapConnection.user', 'sap.username'
        ]),

        language: getFieldValue([
          'sapConnection.language', 'sap.language'
        ]),

        connectionPool: getFieldValue([
          'sapConnection.pool', 'sap.connectionPool'
        ])
      }
    } else if (stream.job_type === 'file_transfer') {
      jobSpecificData = {
        sourceType: getFieldValue([
          'sourceConfig.type', 'source.type', 'fileSource.type'
        ]),

        sourcePath: getFieldValue([
          'sourceConfig.path', 'source.path', 'fileSource.path'
        ]),

        sourcePattern: getFieldValue([
          'sourceConfig.pattern', 'source.pattern', 'fileSource.pattern'
        ]),

        targetType: getFieldValue([
          'targetConfig.type', 'target.type', 'fileTarget.type'
        ]),

        targetEndpoint: getFieldValue([
          'targetConfig.endpoint', 'target.endpoint', 'fileTarget.endpoint'
        ]),

        transferMode: getFieldValue([
          'transferConfig.mode', 'transfer.mode', 'fileTransfer.mode'
        ])
      }
    } else if (stream.job_type === 'custom') {
      jobSpecificData = {
        apiEndpoint: getFieldValue([
          'customConfig.apiEndpoint', 'custom.endpoint', 'api.endpoint'
        ]),

        authMethod: getFieldValue([
          'customConfig.authMethod', 'custom.auth', 'authentication.method'
        ]),

        timeout: getFieldValue([
          'customConfig.timeout', 'custom.timeout', 'api.timeout'
        ]),

        retryCount: getFieldValue([
          'customConfig.retryCount', 'custom.retries', 'api.retries'
        ]),

        customLogic: getFieldValue([
          'customConfig.customLogic', 'custom.logic', 'processing.logic'
        ])
      }
    }

    const realData = {
      basic: baseData,
      scheduling: schedulingData,
      streamProperties: streamProperties,
      jobSpecific: jobSpecificData,
      dataSource: hasRealData ? 'real' : 'empty'
    }

    console.log('✅ StreamDataDisplay Real Data Result:', {
      streamId: stream.id,
      dataSource: realData.dataSource,
      realData: realData
    })

    return realData
  }

  const data = getWizardData()

  return (
    <div className={cn("space-y-4", className)}>
      {/* Data Source Indicator */}
      {data.dataSource === 'real' && (
        <div className="mb-4 p-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-green-700 dark:text-green-300">
            <CheckCircle2 className="w-4 h-4" />
            <span>Zeigt echte Wizard-Daten aus der Datenbank (keine Mock-Daten)</span>
          </div>
        </div>
      )}

      {data.dataSource === 'empty' && (
        <div className="mb-4 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center gap-2 text-sm text-red-700 dark:text-red-300">
            <AlertCircle className="w-4 h-4" />
            <span>⚠️ Keine Wizard-Daten vorhanden - muss behoben werden!</span>
          </div>
        </div>
      )}

      {/* Job Configuration */}
      <ConfigSection
        id="job"
        title="Job-Konfiguration"
        icon={Zap}
        expanded={expandedSections.has('job')}
        onToggle={() => toggleSection('job')}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InfoItem label="Job-Name" value={data.basic.jobName} />
          <InfoItem label="Beschreibung" value={data.basic.description} />
          <InfoItem
            label="Job-Typ"
            value={
              <Badge variant="outline">
                {data.basic.jobType === 'standard' ? 'Standard' :
                 data.basic.jobType === 'sap' ? 'SAP Integration' :
                 data.basic.jobType === 'file_transfer' ? 'File Transfer' :
                 'Custom'}
              </Badge>
            }
          />
          <InfoItem label="Priorität" value={data.basic.priority} />
          <InfoItem label="Erstellt von" value={data.basic.createdBy} />
        </div>
      </ConfigSection>

      {/* Stream Properties */}
      <ConfigSection
        id="stream"
        title="Stream-Eigenschaften"
        icon={GitBranch}
        expanded={expandedSections.has('stream')}
        onToggle={() => toggleSection('stream')}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InfoItem label="Stream-Name" value={data.streamProperties.streamName} />
          <InfoItem label="Stream-Typ" value={data.streamProperties.streamType} />
          <InfoItem label="Quelle" value={data.streamProperties.sourceSystem} />
          <InfoItem label="Ziel" value={data.streamProperties.targetSystem} />
          <InfoItem label="Datenformat" value={data.streamProperties.dataFormat} />
          <InfoItem label="Encoding" value={data.streamProperties.encoding} />
        </div>
      </ConfigSection>

      {/* Scheduling Configuration */}
      <ConfigSection
        id="scheduling"
        title="Zeitplanung"
        icon={Calendar}
        expanded={expandedSections.has('scheduling')}
        onToggle={() => toggleSection('scheduling')}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InfoItem label="Typ" value={data.scheduling.type} />
          <InfoItem label="Startzeit" value={data.scheduling.startTime} />
          <InfoItem label="Häufigkeit" value={data.scheduling.frequency} />
          <InfoItem label="Nächste Ausführung" value={data.scheduling.nextRun} />
          {data.scheduling.days && (
            <InfoItem
              label="Ausführungstage"
              value={Array.isArray(data.scheduling.days) ?
                data.scheduling.days.join(', ') :
                data.scheduling.days}
            />
          )}
        </div>
      </ConfigSection>

      {/* Job Type Specific Configuration */}
      {data.jobSpecific && stream.job_type === 'sap' && (
        <ConfigSection
          id="sap"
          title="SAP-Konfiguration"
          icon={Database}
          expanded={expandedSections.has('sap')}
          onToggle={() => toggleSection('sap')}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InfoItem label="Host" value={data.jobSpecific.connectionHost} />
            <InfoItem label="Client" value={data.jobSpecific.client} />
            <InfoItem label="System-ID" value={data.jobSpecific.systemId} />
            <InfoItem label="Benutzer" value={data.jobSpecific.username} />
            <InfoItem label="Sprache" value={data.jobSpecific.language} />
            <InfoItem label="Connection Pool" value={data.jobSpecific.connectionPool} />
          </div>
        </ConfigSection>
      )}

      {data.jobSpecific && stream.job_type === 'file_transfer' && (
        <ConfigSection
          id="filetransfer"
          title="File Transfer-Konfiguration"
          icon={FolderOpen}
          expanded={expandedSections.has('filetransfer')}
          onToggle={() => toggleSection('filetransfer')}
        >
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300">Quelle</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-4 border-l-2 border-blue-200">
                <InfoItem label="Typ" value={data.jobSpecific.sourceType} />
                <InfoItem label="Pfad" value={data.jobSpecific.sourcePath} />
                <InfoItem label="Pattern" value={data.jobSpecific.sourcePattern} />
              </div>
            </div>
            <div>
              <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300">Ziel</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-4 border-l-2 border-green-200">
                <InfoItem label="Typ" value={data.jobSpecific.targetType} />
                <InfoItem label="Endpoint" value={data.jobSpecific.targetEndpoint} />
                <InfoItem label="Transfer-Modus" value={data.jobSpecific.transferMode} />
              </div>
            </div>
          </div>
        </ConfigSection>
      )}

      {data.jobSpecific && stream.job_type === 'custom' && (
        <ConfigSection
          id="custom"
          title="Custom-Konfiguration"
          icon={Settings}
          expanded={expandedSections.has('custom')}
          onToggle={() => toggleSection('custom')}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InfoItem label="API Endpoint" value={data.jobSpecific.apiEndpoint} />
            <InfoItem label="Authentifizierung" value={data.jobSpecific.authMethod} />
            <InfoItem label="Timeout" value={data.jobSpecific.timeout} />
            <InfoItem label="Retry Count" value={data.jobSpecific.retryCount} />
            <InfoItem label="Custom Logic" value={data.jobSpecific.customLogic} />
          </div>
        </ConfigSection>
      )}

      {/* Wizard Data Debug Section (nur in Development) */}
      {process.env.NODE_ENV === 'development' && (
        <WizardDataDebugSection
          stream={stream}
          expanded={expandedSections.has('debug')}
          onToggle={() => toggleSection('debug')}
        />
      )}
    </div>
  )
}

// Helper Components (unverändert)
interface ConfigSectionProps {
  id: string
  title: string
  icon: React.ComponentType<any>
  expanded: boolean
  onToggle: () => void
  children: React.ReactNode
}

const ConfigSection: React.FC<ConfigSectionProps> = ({
  title,
  icon: Icon,
  expanded,
  onToggle,
  children
}) => {
  return (
    <Card>
      <Collapsible open={expanded} onOpenChange={onToggle}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors pb-3">
            <CardTitle className="text-base flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Icon className="w-5 h-5 text-blue-600" />
                {title}
              </div>
              {expanded ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </CardTitle>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="pt-0">
            {children}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}

interface InfoItemProps {
  label: string
  value: React.ReactNode | string
}

const InfoItem: React.FC<InfoItemProps> = ({ label, value }) => {
  if (!value) return null

  return (
    <div className="space-y-1">
      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">{label}</dt>
      <dd className="text-sm text-gray-900 dark:text-white">
        {typeof value === 'string' ? value : value}
      </dd>
    </div>
  )
}

// Wizard Data Debug Section - Nur echte Daten, keine Fallbacks
interface WizardDataDebugSectionProps {
  stream: XMLStream
  expanded: boolean
  onToggle: () => void
}

const WizardDataDebugSection: React.FC<WizardDataDebugSectionProps> = ({
  stream,
  expanded,
  onToggle
}) => {
  const wizardData = stream.wizard_data || {}
  const hasWizardData = Object.keys(wizardData).length > 0

  // Analysiere vorhandene vs. fehlende Daten
  const analyzeWizardData = () => {
    const present: string[] = []
    const missing: string[] = []

    // Erwartete Felder basierend auf Job-Typ
    const expectedFields = {
      basic: ['jobType', 'streamProperties'],
      streamProperties: ['streamName', 'description', 'contactPerson'],
      contactPerson: ['firstName', 'lastName', 'company'],
      scheduling: ['mode', 'simple', 'advanced'],
      jobForm: ['script', 'parameters', 'agent'] // Standard Job
    }

    // Prüfe vorhandene Daten
    Object.keys(wizardData).forEach(key => {
      if (wizardData[key] && wizardData[key] !== '') {
        present.push(key)
      }
    })

    // Prüfe erwartete Felder
    expectedFields.basic.forEach(field => {
      if (!wizardData[field] || wizardData[field] === '') {
        missing.push(`Basic: ${field}`)
      }
    })

    if (wizardData.streamProperties) {
      expectedFields.streamProperties.forEach(field => {
        if (!wizardData.streamProperties[field] || wizardData.streamProperties[field] === '') {
          missing.push(`StreamProperties: ${field}`)
        }
      })
    } else {
      missing.push('Komplette StreamProperties Sektion fehlt')
    }

    return { present, missing }
  }

  const { present, missing } = analyzeWizardData()

  if (!hasWizardData) {
    return (
      <Card className="border-red-200 dark:border-red-800">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2 text-red-600 dark:text-red-400">
            <XCircle className="w-5 h-5" />
            🚨 Keine Wizard-Daten vorhanden
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="text-sm text-red-700 dark:text-red-300">
              <p className="font-medium mb-2">Dieser Stream hat keine wizard_data!</p>
              <p>Das muss behoben werden, um die Konfiguration vollständig anzuzeigen.</p>
              <p className="mt-2">Stream ID: <code className="bg-red-100 dark:bg-red-800 px-1 rounded">{stream.id}</code></p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-blue-200 dark:border-blue-800">
      <Collapsible open={expanded} onOpenChange={onToggle}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors pb-3">
            <CardTitle className="text-base flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Code2 className="w-5 h-5 text-blue-600" />
                🔍 Debug: Echte Wizard-Daten
                <Badge variant={missing.length === 0 ? "default" : "destructive"} className="ml-2">
                  {missing.length === 0 ? 'Vollständig' : `${missing.length} fehlen`}
                </Badge>
              </div>
              {expanded ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </CardTitle>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="pt-0 space-y-4">

            {/* Stream Metadaten */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <h4 className="font-medium text-sm mb-3 flex items-center gap-2">
                <Server className="w-4 h-4 text-gray-600" />
                Stream Metadaten
              </h4>
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-gray-500">ID:</span>
                  <code className="ml-2 bg-gray-200 dark:bg-gray-700 px-1 rounded">{stream.id}</code>
                </div>
                <div>
                  <span className="text-gray-500">Status:</span>
                  <span className="ml-2">{stream.status}</span>
                </div>
                <div>
                  <span className="text-gray-500">Job-Typ:</span>
                  <span className="ml-2">{stream.job_type || 'nicht gesetzt'}</span>
                </div>
                <div>
                  <span className="text-gray-500">Datenfelder:</span>
                  <span className="ml-2">{present.length} vorhanden</span>
                </div>
              </div>
            </div>

            {/* Vorhandene Daten */}
            {present.length > 0 && (
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <h4 className="font-medium text-sm mb-3 flex items-center gap-2 text-green-700 dark:text-green-300">
                  <CheckCircle2 className="w-4 h-4" />
                  ✅ Vorhandene Wizard-Daten ({present.length})
                </h4>
                <div className="space-y-3">
                  {present.map(field => {
                    const value = wizardData[field]
                    return (
                      <div key={field} className="text-sm">
                        <div className="flex items-start gap-2">
                          <code className="bg-green-100 dark:bg-green-800 px-2 py-1 rounded text-xs font-mono min-w-0">
                            {field}
                          </code>
                          <div className="text-green-700 dark:text-green-300 flex-1 min-w-0">
                            {typeof value === 'object' ? (
                              <details className="cursor-pointer">
                                <summary className="font-medium">Objekt ({Object.keys(value || {}).length} Felder)</summary>
                                <pre className="mt-2 text-xs bg-green-100 dark:bg-green-800 p-2 rounded overflow-x-auto">
                                  {JSON.stringify(value, null, 2)}
                                </pre>
                              </details>
                            ) : (
                              <span className="break-all">{String(value)}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Fehlende Daten */}
            {missing.length > 0 && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <h4 className="font-medium text-sm mb-3 flex items-center gap-2 text-red-700 dark:text-red-300">
                  <AlertCircle className="w-4 h-4" />
                  ❌ Fehlende Daten ({missing.length}) - Muss behoben werden!
                </h4>
                <div className="space-y-2">
                  {missing.map((field, index) => (
                    <div key={index} className="text-sm text-red-700 dark:text-red-300 flex items-center gap-2">
                      <XCircle className="w-3 h-3" />
                      <code className="bg-red-100 dark:bg-red-800 px-2 py-1 rounded text-xs">
                        {field}
                      </code>
                    </div>
                  ))}
                </div>
                <div className="mt-3 text-xs text-red-600 dark:text-red-400">
                  💡 Diese Felder müssen im Wizard ergänzt werden, damit die Anzeige vollständig ist.
                </div>
              </div>
            )}

            {/* Rohe JSON Daten (collapsible) */}
            <details className="bg-gray-50 dark:bg-gray-800 rounded-lg">
              <summary className="p-4 cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300">
                📄 Rohe JSON-Daten zur Kontrolle
              </summary>
              <div className="px-4 pb-4">
                <pre className="text-xs text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-900 p-3 rounded border overflow-x-auto">
                  {JSON.stringify(wizardData, null, 2)}
                </pre>
              </div>
            </details>

          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}

export default StreamDataDisplay