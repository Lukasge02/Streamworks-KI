/**
 * WizardDataRenderer Component
 * Konvertiert wizard_data JSON zurück ins benutzerfreundliche Wizard-Format
 */
'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Zap,
  Database,
  FolderOpen,
  Settings,
  Calendar,
  GitBranch,
  User,
  Building2
} from 'lucide-react'

import { XMLStream } from '@/services/xmlStreamsApi'
import { cn } from '@/lib/utils'

interface WizardDataRendererProps {
  stream: XMLStream
  className?: string
  mode?: 'view' | 'edit'
}

export const WizardDataRenderer: React.FC<WizardDataRendererProps> = ({
  stream,
  className,
  mode = 'view'
}) => {
  // Alle Sektionen immer ausgeklappt
  const expandedSections = new Set(['basic', 'streamProperties', 'scheduling', 'jobConfiguration'])
  const [editMode, setEditMode] = useState(mode === 'edit')

  // Keine Toggle-Funktionalität mehr nötig, da immer ausgeklappt

  // Wizard-Daten extrahieren und strukturieren
  const getWizardStructure = () => {
    const wizardData = stream.wizard_data || {}

    // Comprehensive debug logging to analyze wizard_data structure
    console.log('🔍 WizardDataRenderer Comprehensive Debug:', {
      streamId: stream.id,
      streamName: stream.stream_name,
      jobType: stream.job_type,
      fullWizardData: wizardData,
      wizardDataKeys: Object.keys(wizardData),
      wizardDataStringified: JSON.stringify(wizardData, null, 2),

      // Specific structure analysis
      hasJobForm: !!wizardData.jobForm,
      jobFormKeys: wizardData.jobForm ? Object.keys(wizardData.jobForm) : null,
      jobFormData: wizardData.jobForm,

      hasStreamProperties: !!wizardData.streamProperties,
      streamPropertiesKeys: wizardData.streamProperties ? Object.keys(wizardData.streamProperties) : null,
      streamPropertiesData: wizardData.streamProperties,

      hasScheduling: !!wizardData.scheduling,
      schedulingKeys: wizardData.scheduling ? Object.keys(wizardData.scheduling) : null,
      schedulingData: wizardData.scheduling,

      // Check for alternative structures
      topLevelFields: Object.entries(wizardData).map(([key, value]) => ({
        key,
        type: typeof value,
        isArray: Array.isArray(value),
        isObject: typeof value === 'object' && value !== null && !Array.isArray(value),
        keys: (typeof value === 'object' && value !== null && !Array.isArray(value)) ? Object.keys(value) : null
      }))
    })

    const getFieldValue = (paths: string[], fallback: any = null, fieldName?: string) => {
      const debugInfo = {
        fieldName: fieldName || 'unknown',
        searchPaths: paths,
        attempts: [] as any[]
      }

      for (const path of paths) {
        const keys = path.split('.')
        let value = wizardData
        let traversal = []

        for (const key of keys) {
          traversal.push({ key, currentValue: value, hasKey: value && key in value })
          value = value?.[key]
          if (value === undefined || value === null) break
        }

        debugInfo.attempts.push({
          path,
          traversal,
          finalValue: value,
          valueType: typeof value,
          found: value !== undefined && value !== null && value !== ''
        })

        if (value !== undefined && value !== null && value !== '') {
          console.log(`✅ Found ${fieldName || 'field'} at path: ${path}`, { value, type: typeof value })
          return value
        }
      }

      // Enhanced fallback: Try to find field name anywhere in the wizard data structure
      const searchInObject = (obj: any, targetKey: string, currentPath: string = ''): any => {
        if (!obj || typeof obj !== 'object') return null

        // Direct key match
        if (obj.hasOwnProperty(targetKey)) {
          console.log(`✅ Found ${fieldName || 'field'} via fallback search at: ${currentPath}.${targetKey}`, { value: obj[targetKey] })
          return obj[targetKey]
        }

        // Recursive search in nested objects
        for (const [key, value] of Object.entries(obj)) {
          if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            const found = searchInObject(value, targetKey, currentPath ? `${currentPath}.${key}` : key)
            if (found !== null && found !== undefined && found !== '') {
              return found
            }
          }
        }

        return null
      }

      // Fallback: Try to find the last part of the path anywhere
      if (fieldName && paths.length > 0) {
        const lastKey = paths[0].split('.').pop()
        if (lastKey) {
          const fallbackValue = searchInObject(wizardData, lastKey)
          if (fallbackValue !== null && fallbackValue !== undefined && fallbackValue !== '') {
            return fallbackValue
          }
        }
      }

      // Log debug info only for fields we're actively looking for
      if (fieldName && (fieldName.includes('job') || fieldName.includes('script') || fieldName.includes('agent'))) {
        console.log(`❌ Field '${fieldName}' not found in any path:`, debugInfo)
      }

      return fallback
    }

    // Determine the actual job type from wizard_data (more reliable than stream.job_type)
    const actualJobType = getFieldValue(['jobType', 'type', 'streamType']) || stream.job_type

    console.log('🎯 Job Type Detection:', {
      streamJobType: stream.job_type,
      wizardDataJobType: getFieldValue(['jobType', 'type', 'streamType']),
      actualJobType: actualJobType,
      usingWizardData: !!getFieldValue(['jobType', 'type', 'streamType'])
    })

    return {
      // Basis-Konfiguration
      basic: {
        jobType: actualJobType,
        description: getFieldValue(['description', 'jobDescription']) || stream.description,
      },

      // Stream-Eigenschaften
      streamProperties: {
        streamName: getFieldValue(['streamProperties.streamName', 'streamName', 'name']) || stream.stream_name,
        description: getFieldValue(['streamProperties.description', 'description']),
        documentation: getFieldValue(['streamProperties.documentation', 'documentation']),
        contactPerson: {
          firstName: getFieldValue(['streamProperties.contactPerson.firstName', 'contactPerson.firstName']),
          lastName: getFieldValue(['streamProperties.contactPerson.lastName', 'contactPerson.lastName']),
          company: getFieldValue(['streamProperties.contactPerson.company', 'contactPerson.company'], 'Arvato Systems'),
          department: getFieldValue(['streamProperties.contactPerson.department', 'contactPerson.department']),
        }
      },

      // Job-Form Konfiguration - erweitert mit mehr Suchpfaden
      jobForm: {
        // Standard Job Fields - erweitert mit verschiedenen möglichen Strukturen
        jobName: getFieldValue([
          'jobForm.jobName', 'jobName', 'job.name', 'name',
          'basic.jobName', 'configuration.jobName',
          // Entity-basierte Pfade vom Backend
          'entities.job_name', 'entities.jobName', 'entities.name',
          'collected_data.job_name', 'collected_data.jobName',
          'extracted_entities.job_name', 'extracted_entities.jobName'
        ], null, 'jobName'),

        script: getFieldValue([
          'jobForm.script', 'script', 'job.script', 'command',
          'execution.script', 'configuration.script',
          // Entity-basierte Pfade vom Backend
          'entities.script', 'entities.command', 'entities.report_name',
          'collected_data.script', 'collected_data.command', 'collected_data.report_name',
          'extracted_entities.script', 'extracted_entities.report_name'
        ], null, 'script'),

        parameters: getFieldValue([
          'jobForm.parameters', 'parameters', 'job.parameters', 'args',
          'execution.parameters', 'configuration.parameters'
        ], null, 'parameters'),

        agent: getFieldValue([
          'jobForm.agent', 'agent', 'job.agent', 'executor',
          'execution.agent', 'configuration.agent',
          // Entity-basierte Pfade vom Backend
          'entities.agent', 'entities.server', 'entities.target_server',
          'collected_data.agent', 'collected_data.target_server', 'collected_data.server_name',
          'extracted_entities.agent', 'extracted_entities.target_server'
        ], null, 'agent'),

        os: getFieldValue([
          'jobForm.os', 'os', 'job.os', 'operatingSystem', 'platform',
          'execution.os', 'configuration.os'
        ], null, 'os'),

        timeout: getFieldValue([
          'jobForm.timeout', 'timeout', 'job.timeout', 'timeoutSeconds',
          'execution.timeout', 'configuration.timeout'
        ], null, 'timeout'),

        retries: getFieldValue([
          'jobForm.retries', 'retries', 'job.retries', 'retryCount',
          'execution.retries', 'configuration.retries'
        ], null, 'retries'),

        exitCodes: getFieldValue([
          'jobForm.exitCodes', 'exitCodes', 'job.exitCodes', 'successCodes',
          'execution.exitCodes', 'configuration.exitCodes'
        ], null, 'exitCodes'),

        workingDirectory: getFieldValue([
          'jobForm.workingDirectory', 'workingDirectory', 'job.workingDirectory', 'workDir',
          'execution.workingDirectory', 'configuration.workingDirectory'
        ], null, 'workingDirectory'),

        environmentVariables: getFieldValue([
          'jobForm.environmentVariables', 'environmentVariables', 'job.environmentVariables',
          'envVars', 'env', 'execution.environmentVariables', 'configuration.environmentVariables'
        ], null, 'environmentVariables'),

        priority: getFieldValue([
          'jobForm.priority', 'priority', 'job.priority',
          'execution.priority', 'configuration.priority'
        ], null, 'priority'),

        notification: getFieldValue([
          'jobForm.notification', 'notification', 'job.notification',
          'notifications', 'execution.notification', 'configuration.notification'
        ], null, 'notification'),

        logLevel: getFieldValue([
          'jobForm.logLevel', 'logLevel', 'job.logLevel', 'logging.level',
          'execution.logLevel', 'configuration.logLevel'
        ], null, 'logLevel'),

        // SAP Job Fields - erweitert
        system: getFieldValue(['jobForm.system', 'system']),
        report: getFieldValue(['jobForm.report', 'report']),
        variant: getFieldValue(['jobForm.variant', 'variant']),
        batchUser: getFieldValue(['jobForm.batchUser', 'batchUser']),
        selectionParameters: getFieldValue(['jobForm.selectionParameters', 'selectionParameters']),
        language: getFieldValue(['jobForm.language', 'language']),
        outputFormat: getFieldValue(['jobForm.outputFormat', 'outputFormat']),
        spool: getFieldValue(['jobForm.spool', 'spool']),
        archive: getFieldValue(['jobForm.archive', 'archive']),

        // File Transfer Fields - erweitert
        sourceAgent: getFieldValue(['jobForm.sourceAgent', 'sourceAgent']),
        sourcePath: getFieldValue(['jobForm.sourcePath', 'sourcePath']),
        targetAgent: getFieldValue(['jobForm.targetAgent', 'targetAgent']),
        targetPath: getFieldValue(['jobForm.targetPath', 'targetPath']),
        onExistsBehavior: getFieldValue(['jobForm.onExistsBehavior', 'onExistsBehavior']),
        deleteAfterTransfer: getFieldValue(['jobForm.deleteAfterTransfer', 'deleteAfterTransfer']),
        compression: getFieldValue(['jobForm.compression', 'compression']),
        encryption: getFieldValue(['jobForm.encryption', 'encryption']),
        checksum: getFieldValue(['jobForm.checksum', 'checksum']),
        retryCount: getFieldValue(['jobForm.retryCount', 'retryCount']),
        transferMode: getFieldValue(['jobForm.transferMode', 'transferMode']),

        // Custom Job Fields
        customType: getFieldValue(['jobForm.customType', 'customType']),
        customConfiguration: getFieldValue(['jobForm.customConfiguration', 'customConfiguration']),
        customCommand: getFieldValue(['jobForm.customCommand', 'customCommand']),
        customOptions: getFieldValue(['jobForm.customOptions', 'customOptions'])
      },

      // Zeitplanung - erweiterte Pfade basierend auf useWizardState
      scheduling: {
        mode: getFieldValue([
          'scheduling.mode',
          'scheduleMode',
          'scheduling.simple.preset',
          'scheduling.advanced.preset'
        ], 'simple'),
        simple: {
          frequency: getFieldValue([
            'scheduling.simple.frequency',
            'frequency',
            'scheduling.simple.preset',
            'scheduling.preset'
          ]),
          startTime: getFieldValue([
            'scheduling.simple.startTime',
            'startTime',
            'scheduling.simple.time',
            'scheduling.time'
          ]),
          preset: getFieldValue([
            'scheduling.simple.preset',
            'scheduling.preset'
          ]),
          weekdays: getFieldValue([
            'scheduling.simple.weekdays',
            'scheduling.weekdays'
          ])
        },
        advanced: {
          cronExpression: getFieldValue([
            'scheduling.advanced.cronExpression',
            'cronExpression',
            'scheduling.cron'
          ]),
          timezone: getFieldValue([
            'scheduling.advanced.timezone',
            'timezone',
            'scheduling.timezone'
          ]),
          description: getFieldValue([
            'scheduling.advanced.description',
            'scheduling.description'
          ]),
        }
      },

      // Erweiterte Konfigurationen
      advanced: {
        notifications: {
          onSuccess: getFieldValue(['notifications.onSuccess', 'notification.success']),
          onFailure: getFieldValue(['notifications.onFailure', 'notification.failure']),
          onWarning: getFieldValue(['notifications.onWarning', 'notification.warning']),
          recipients: getFieldValue(['notifications.recipients', 'notification.recipients']),
          template: getFieldValue(['notifications.template', 'notification.template'])
        },
        dependencies: {
          predecessorJobs: getFieldValue(['dependencies.predecessors', 'deps.predecessors']),
          conditions: getFieldValue(['dependencies.conditions', 'deps.conditions']),
          waitForCompletion: getFieldValue(['dependencies.waitForCompletion', 'deps.waitForCompletion'])
        },
        logging: {
          logLevel: getFieldValue(['logging.level', 'log.level']),
          logRetention: getFieldValue(['logging.retention', 'log.retention']),
          customLogPath: getFieldValue(['logging.customPath', 'log.customPath'])
        },
        security: {
          runAsUser: getFieldValue(['security.runAsUser', 'sec.runAsUser']),
          permissions: getFieldValue(['security.permissions', 'sec.permissions']),
          encryptionLevel: getFieldValue(['security.encryption', 'sec.encryption'])
        }
      }
    }
  }

  const wizardStructure = getWizardStructure()

  const jobTypeConfig = {
    standard: { icon: Zap, label: 'Standard Job', color: 'bg-blue-600' },
    sap: { icon: Database, label: 'SAP Integration', color: 'bg-orange-600' },
    file_transfer: { icon: FolderOpen, label: 'File Transfer', color: 'bg-green-600' },
    custom: { icon: Settings, label: 'Custom Job', color: 'bg-purple-600' },
  }

  // Use the job type from wizard_data for consistent display
  const actualJobTypeFromWizard = wizardStructure.basic.jobType || stream.job_type
  const currentJobType = jobTypeConfig[actualJobTypeFromWizard as keyof typeof jobTypeConfig] || jobTypeConfig.custom
  const JobTypeIcon = currentJobType.icon

  return (
    <div className={cn("space-y-6", className)}>

      {/* Stream-Eigenschaften */}
      <WizardSection
        id="streamProperties"
        title="Stream-Eigenschaften"
        icon={GitBranch}
        expanded={expandedSections.has('streamProperties')}
      >
        <div className="space-y-6">
          {/* Stammdaten */}
          <div>
            <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Stammdaten
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-blue-200">
              <WizardField
                label="Stream-Name"
                value={wizardStructure.streamProperties.streamName}
                required
                editMode={editMode}
              />
              <WizardField
                label="Beschreibung"
                value={wizardStructure.streamProperties.description}
                editMode={editMode}
                type="textarea"
              />
              <WizardField
                label="Dokumentation"
                value={wizardStructure.streamProperties.documentation}
                editMode={editMode}
                type="textarea"
                colSpan={2}
              />
            </div>
          </div>

          {/* Kontaktdaten */}
          <div>
            <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <User className="w-4 h-4" />
              Kontaktperson
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-green-200">
              <WizardField
                label="Vorname"
                value={wizardStructure.streamProperties.contactPerson.firstName}
                required
                editMode={editMode}
              />
              <WizardField
                label="Nachname"
                value={wizardStructure.streamProperties.contactPerson.lastName}
                required
                editMode={editMode}
              />
              <WizardField
                label="Unternehmen"
                value={wizardStructure.streamProperties.contactPerson.company}
                editMode={editMode}
              />
              <WizardField
                label="Abteilung"
                value={wizardStructure.streamProperties.contactPerson.department}
                editMode={editMode}
              />
            </div>
          </div>
        </div>
      </WizardSection>

      {/* Job-Konfiguration */}
      <WizardSection
        id="jobConfiguration"
        title="Job-Konfiguration"
        icon={currentJobType.icon}
        expanded={expandedSections.has('jobConfiguration')}
      >
        <div className="space-y-4">
          {/* Use actualJobType from wizard_data instead of stream.job_type */}
          {wizardStructure.basic.jobType === 'standard' && (
            <>
              {/* Basis Job-Konfiguration */}
              <div>
                <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Basis-Konfiguration
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-blue-200">
                  <WizardField
                    label="Job-Name"
                    value={wizardStructure.jobForm.jobName}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Agent"
                    value={wizardStructure.jobForm.agent}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Betriebssystem"
                    value={wizardStructure.jobForm.os}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Priorität"
                    value={wizardStructure.jobForm.priority}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Arbeitsverzeichnis"
                    value={wizardStructure.jobForm.workingDirectory}
                    editMode={editMode}
                    colSpan={2}
                  />
                </div>
              </div>

              {/* Script und Parameter */}
              <div>
                <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300">
                  Script und Parameter
                </h4>
                <div className="space-y-4 pl-4 border-l-2 border-green-200">
                  <WizardField
                    label="Script"
                    value={wizardStructure.jobForm.script}
                    editMode={editMode}
                    type="textarea"
                  />
                  <WizardField
                    label="Parameter"
                    value={Array.isArray(wizardStructure.jobForm.parameters) ?
                      wizardStructure.jobForm.parameters.join(', ') :
                      wizardStructure.jobForm.parameters}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Umgebungsvariablen"
                    value={typeof wizardStructure.jobForm.environmentVariables === 'object' ?
                      JSON.stringify(wizardStructure.jobForm.environmentVariables, null, 2) :
                      wizardStructure.jobForm.environmentVariables}
                    editMode={editMode}
                    type="textarea"
                  />
                </div>
              </div>

              {/* Fehlerbehandlung und Logging */}
              <div>
                <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300">
                  Fehlerbehandlung & Logging
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-orange-200">
                  <WizardField
                    label="Timeout (Sekunden)"
                    value={wizardStructure.jobForm.timeout}
                    editMode={editMode}
                    type="number"
                  />
                  <WizardField
                    label="Wiederholungen"
                    value={wizardStructure.jobForm.retries}
                    editMode={editMode}
                    type="number"
                  />
                  <WizardField
                    label="Exit-Codes"
                    value={Array.isArray(wizardStructure.jobForm.exitCodes) ?
                      wizardStructure.jobForm.exitCodes.join(', ') :
                      wizardStructure.jobForm.exitCodes}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Log-Level"
                    value={wizardStructure.jobForm.logLevel}
                    editMode={editMode}
                  />
                </div>
              </div>

              {/* Benachrichtigungen */}
              {wizardStructure.jobForm.notification && (
                <div>
                  <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300">
                    Benachrichtigungen
                  </h4>
                  <div className="pl-4 border-l-2 border-purple-200">
                    <WizardField
                      label="Benachrichtigung"
                      value={typeof wizardStructure.jobForm.notification === 'object' ?
                        JSON.stringify(wizardStructure.jobForm.notification, null, 2) :
                        wizardStructure.jobForm.notification}
                      editMode={editMode}
                      type="textarea"
                    />
                  </div>
                </div>
              )}
            </>
          )}

          {wizardStructure.basic.jobType === 'sap' && (
            <>
              {/* SAP System-Konfiguration */}
              <div>
                <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <Database className="w-4 h-4" />
                  SAP System-Konfiguration
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-orange-200">
                  <WizardField
                    label="System"
                    value={wizardStructure.jobForm.system}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Benutzer"
                    value={wizardStructure.jobForm.batchUser}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Sprache"
                    value={wizardStructure.jobForm.language}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Report"
                    value={wizardStructure.jobForm.report}
                    editMode={editMode}
                  />
                </div>
              </div>

              {/* SAP Job-Details */}
              <div>
                <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300">
                  Report und Varianten
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-blue-200">
                  <WizardField
                    label="Variante"
                    value={wizardStructure.jobForm.variant}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Ausgabeformat"
                    value={wizardStructure.jobForm.outputFormat}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Spool"
                    value={wizardStructure.jobForm.spool ? 'Ja' : 'Nein'}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Archivierung"
                    value={wizardStructure.jobForm.archive ? 'Ja' : 'Nein'}
                    editMode={editMode}
                  />
                </div>
              </div>

              {/* Selektions-Parameter */}
              {wizardStructure.jobForm.selectionParameters && (
                <div>
                  <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300">
                    Selektions-Parameter
                  </h4>
                  <div className="pl-4 border-l-2 border-green-200">
                    <WizardField
                      label="Parameter"
                      value={typeof wizardStructure.jobForm.selectionParameters === 'object' ?
                        JSON.stringify(wizardStructure.jobForm.selectionParameters, null, 2) :
                        wizardStructure.jobForm.selectionParameters}
                      editMode={editMode}
                      type="textarea"
                    />
                  </div>
                </div>
              )}
            </>
          )}

          {/* Show File Transfer section if any file transfer fields are present */}
          {(wizardStructure.basic.jobType === 'file_transfer' ||
            wizardStructure.jobForm.sourceAgent ||
            wizardStructure.jobForm.targetAgent ||
            wizardStructure.jobForm.sourcePath ||
            wizardStructure.jobForm.targetPath) && (
            <>
              {/* Quelle */}
              <div>
                <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <FolderOpen className="w-4 h-4" />
                  Quell-Konfiguration
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-blue-200">
                  <WizardField
                    label="Quell-Agent"
                    value={wizardStructure.jobForm.sourceAgent}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Quell-Pfad"
                    value={wizardStructure.jobForm.sourcePath}
                    editMode={editMode}
                  />
                </div>
              </div>

              {/* Ziel */}
              <div>
                <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300">
                  Ziel-Konfiguration
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-green-200">
                  <WizardField
                    label="Ziel-Agent"
                    value={wizardStructure.jobForm.targetAgent}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Ziel-Pfad"
                    value={wizardStructure.jobForm.targetPath}
                    editMode={editMode}
                  />
                </div>
              </div>

              {/* Transfer-Optionen */}
              <div>
                <h4 className="font-medium text-sm mb-3 text-gray-700 dark:text-gray-300">
                  Transfer-Optionen
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-purple-200">
                  <WizardField
                    label="Verhalten bei Existenz"
                    value={wizardStructure.jobForm.onExistsBehavior}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Nach Transfer löschen"
                    value={wizardStructure.jobForm.deleteAfterTransfer ? 'Ja' : 'Nein'}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Komprimierung"
                    value={wizardStructure.jobForm.compression ? 'Aktiviert' : 'Deaktiviert'}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Verschlüsselung"
                    value={wizardStructure.jobForm.encryption ? 'Aktiviert' : 'Deaktiviert'}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Prüfsumme"
                    value={wizardStructure.jobForm.checksum ? 'Aktiviert' : 'Deaktiviert'}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Transfer-Modus"
                    value={wizardStructure.jobForm.transferMode}
                    editMode={editMode}
                  />
                  <WizardField
                    label="Wiederholungsversuche"
                    value={wizardStructure.jobForm.retryCount}
                    editMode={editMode}
                    type="number"
                  />
                </div>
              </div>
            </>
          )}
        </div>
      </WizardSection>

      {/* Zeitplanung */}
      <WizardSection
        id="scheduling"
        title="Zeitplanung"
        icon={Calendar}
        expanded={expandedSections.has('scheduling')}
      >
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Badge variant={wizardStructure.scheduling.mode === 'advanced' ? "default" : "secondary"}>
              {wizardStructure.scheduling.mode === 'advanced' ? 'Erweitert' : 'Einfach'}
            </Badge>
          </div>

          {wizardStructure.scheduling.mode === 'simple' ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <WizardField
                  label="Häufigkeit"
                  value={wizardStructure.scheduling.simple.frequency}
                  editMode={editMode}
                />
                <WizardField
                  label="Preset"
                  value={wizardStructure.scheduling.simple.preset}
                  editMode={editMode}
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <WizardField
                  label="Startzeit"
                  value={wizardStructure.scheduling.simple.startTime}
                  editMode={editMode}
                  type="time"
                />
                <WizardField
                  label="Wochentage"
                  value={wizardStructure.scheduling.simple.weekdays ?
                    wizardStructure.scheduling.simple.weekdays
                      .map((day, i) => day ? ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'][i] : null)
                      .filter(Boolean)
                      .join(', ')
                    : null
                  }
                  editMode={editMode}
                />
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <WizardField
                label="Cron-Expression"
                value={wizardStructure.scheduling.advanced.cronExpression}
                editMode={editMode}
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <WizardField
                  label="Zeitzone"
                  value={wizardStructure.scheduling.advanced.timezone}
                  editMode={editMode}
                />
                <WizardField
                  label="Beschreibung"
                  value={wizardStructure.scheduling.advanced.description}
                  editMode={editMode}
                />
              </div>
            </div>
          )}
        </div>
      </WizardSection>
    </div>
  )
}

// Helper-Komponenten
interface WizardSectionProps {
  id: string
  title: string
  icon: React.ComponentType<any>
  expanded: boolean
  children: React.ReactNode
}

const WizardSection: React.FC<WizardSectionProps> = ({
  title,
  icon: Icon,
  children
}) => {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-3">
          <Icon className="w-5 h-5 text-blue-600" />
          <div className="text-base font-semibold">{title}</div>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        {children}
      </CardContent>
    </Card>
  )
}

interface WizardFieldProps {
  label: string
  value: any
  required?: boolean
  editMode?: boolean
  type?: 'text' | 'textarea' | 'number' | 'time'
  colSpan?: number
}

const WizardField: React.FC<WizardFieldProps> = ({
  label,
  value,
  required = false,
  editMode = false,
  type = 'text',
  colSpan = 1
}) => {
  const [editValue, setEditValue] = useState(value || '')

  // Enhanced value handling for different data types
  const formatDisplayValue = (val: any): string => {
    if (val === null || val === undefined) return ''

    if (typeof val === 'boolean') {
      return val ? 'Ja' : 'Nein'
    }

    if (Array.isArray(val)) {
      if (val.length === 0) return 'Leer'
      return val.join(', ')
    }

    if (typeof val === 'object') {
      try {
        return JSON.stringify(val, null, 2)
      } catch {
        return 'Komplexes Objekt'
      }
    }

    return String(val)
  }

  // Improved hasValue logic - more inclusive
  const hasValue = (() => {
    if (value === null || value === undefined) return false

    if (typeof value === 'boolean') return true  // Always show booleans
    if (typeof value === 'number') return true  // Always show numbers (including 0)

    if (typeof value === 'string') {
      return value.trim() !== ''  // Show non-empty strings
    }

    if (Array.isArray(value)) {
      return value.length > 0  // Show non-empty arrays
    }

    if (typeof value === 'object') {
      return Object.keys(value).length > 0  // Show non-empty objects
    }

    return false
  })()

  const displayValue = formatDisplayValue(value)

  // Show field if it has value OR if we're in edit mode OR if it's an important field that should always be visible
  const shouldShow = hasValue || editMode ||
                    (label && ['Job-Name', 'Script', 'Agent', 'Betriebssystem'].includes(label))

  if (!shouldShow) return null

  const fieldClasses = colSpan === 2 ? 'md:col-span-2' : ''

  return (
    <div className={`space-y-2 ${fieldClasses}`}>
      <Label className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </Label>

      {editMode ? (
        <>
          {type === 'textarea' ? (
            <Textarea
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="min-h-[80px]"
              placeholder={`${label} eingeben...`}
            />
          ) : (
            <Input
              type={type}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              placeholder={`${label} eingeben...`}
            />
          )}
        </>
      ) : (
        <div className="p-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md">
          {typeof value === 'object' && value !== null && !Array.isArray(value) ? (
            <pre className="text-xs text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
              {displayValue}
            </pre>
          ) : (
            <span className="text-sm text-gray-900 dark:text-gray-100">
              {displayValue || <em className="text-gray-500">Nicht gesetzt</em>}
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export default WizardDataRenderer