/**
 * Job Configuration Step
 * Dynamic form based on selected job type
 */
'use client'

import React from 'react'
import { JobType, WizardStepProps, OSType } from '../../types/wizard.types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { 
  ChevronLeft, 
  ChevronRight, 
  Terminal,
  Database,
  FolderSync,
  Plus,
  Trash2,
  Info
} from 'lucide-react'

export const JobConfigurationStep: React.FC<WizardStepProps> = ({
  formData,
  onUpdateData,
  onNext,
  onPrevious,
  canProceed,
  isLastStep
}) => {
  const jobType = formData.jobType
  const jobForm = formData.jobForm || {}

  const handleFieldChange = (field: string, value: any) => {
    onUpdateData({
      jobForm: {
        ...jobForm,
        [field]: value
      }
    })
  }

  const renderStandardJobForm = () => {
    const form = jobForm as any

    return (
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Terminal className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            Standard Job Konfiguration
          </h3>
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="jobName" className="text-sm font-medium">
              Job-Name *
            </Label>
            <Input
              id="jobName"
              type="text"
              value={form.jobName || ''}
              onChange={(e) => handleFieldChange('jobName', e.target.value)}
              placeholder="z.B. backup_daily"
              className="mt-1"
              required
            />
          </div>

          <div>
            <Label htmlFor="agent" className="text-sm font-medium">
              Agent *
            </Label>
            <Input
              id="agent"
              type="text"
              value={form.agent || 'gtasswvk05445'}
              onChange={(e) => handleFieldChange('agent', e.target.value)}
              placeholder="gtasswvk05445"
              className="mt-1"
              required
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Streamworks Agent auf dem der Job ausgeführt werden soll
            </p>
          </div>

          <div>
            <Label className="text-sm font-medium">Betriebssystem *</Label>
            <div className="flex space-x-4 mt-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="os"
                  value={OSType.WINDOWS}
                  checked={form.os === OSType.WINDOWS}
                  onChange={(e) => handleFieldChange('os', e.target.value)}
                  className="mr-2"
                />
                <span className="text-sm">Windows</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="os"
                  value={OSType.UNIX}
                  checked={form.os === OSType.UNIX}
                  onChange={(e) => handleFieldChange('os', e.target.value)}
                  className="mr-2"
                />
                <span className="text-sm">Unix/Linux</span>
              </label>
            </div>
          </div>

          <div>
            <Label htmlFor="script" className="text-sm font-medium">
              Script-Inhalt *
            </Label>
            <textarea
              id="script"
              value={form.script || ''}
              onChange={(e) => handleFieldChange('script', e.target.value)}
              placeholder={form.os === OSType.WINDOWS ? 
                'echo "Hello World"\npause' : 
                '#!/bin/bash\necho "Hello World"'
              }
              className="mt-1 w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
              rows={6}
              required
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {form.os === OSType.WINDOWS ? 'Batch/PowerShell Commands' : 'Shell Commands'}
            </p>
          </div>
        </div>
      </Card>
    )
  }

  const renderSAPJobForm = () => {
    const form = jobForm as any

    return (
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Database className="w-5 h-5 text-green-600 dark:text-green-400" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            SAP Job Konfiguration
          </h3>
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="jobName" className="text-sm font-medium">
              Job-Name *
            </Label>
            <Input
              id="jobName"
              type="text"
              value={form.jobName || ''}
              onChange={(e) => handleFieldChange('jobName', e.target.value)}
              placeholder="z.B. sap_report_daily"
              className="mt-1"
              required
            />
          </div>

          <div className="space-y-4">
            <div>
              <Label htmlFor="system" className="text-sm font-medium">
                SAP System *
              </Label>
              <Input
                id="system"
                type="text"
                value={form.system || ''}
                onChange={(e) => handleFieldChange('system', e.target.value)}
                placeholder="z.B. PRD, DEV, QAS"
                className="mt-1"
                required
              />
            </div>

            <div>
              <Label htmlFor="batchUser" className="text-sm font-medium">
                Batch User *
              </Label>
              <Input
                id="batchUser"
                type="text"
                value={form.batchUser || ''}
                onChange={(e) => handleFieldChange('batchUser', e.target.value)}
                placeholder="z.B. BATCH01"
                className="mt-1"
                required
              />
            </div>
          </div>

          <div>
            <Label htmlFor="report" className="text-sm font-medium">
              Report/Programm *
            </Label>
            <Input
              id="report"
              type="text"
              value={form.report || ''}
              onChange={(e) => handleFieldChange('report', e.target.value)}
              placeholder="z.B. RSCLTCOP, Z_CUSTOM_REPORT"
              className="mt-1"
              required
            />
          </div>

          <div>
            <Label htmlFor="variant" className="text-sm font-medium">
              Variante
            </Label>
            <Input
              id="variant"
              type="text"
              value={form.variant || ''}
              onChange={(e) => handleFieldChange('variant', e.target.value)}
              placeholder="Standard-Variante (optional)"
              className="mt-1"
            />
          </div>
        </div>
      </Card>
    )
  }

  const renderFileTransferForm = () => {
    const form = jobForm as any

    return (
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <FolderSync className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            File Transfer Konfiguration
          </h3>
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="jobName" className="text-sm font-medium">
              Job-Name *
            </Label>
            <Input
              id="jobName"
              type="text"
              value={form.jobName || ''}
              onChange={(e) => handleFieldChange('jobName', e.target.value)}
              placeholder="z.B. transfer_daily_files"
              className="mt-1"
              required
            />
          </div>

          {/* Source Configuration */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">Quelle</h4>
            
            <div className="space-y-3">
              <div>
                <Label htmlFor="sourceAgent" className="text-sm font-medium">
                  Quell-Agent *
                </Label>
                <Input
                  id="sourceAgent"
                  type="text"
                  value={form.sourceAgent || ''}
                  onChange={(e) => handleFieldChange('sourceAgent', e.target.value)}
                  placeholder="gtasswvv15778"
                  className="mt-1"
                  required
                />
              </div>

              <div>
                <Label htmlFor="sourcePath" className="text-sm font-medium">
                  Quell-Pfad *
                </Label>
                <Input
                  id="sourcePath"
                  type="text"
                  value={form.sourcePath || ''}
                  onChange={(e) => handleFieldChange('sourcePath', e.target.value)}
                  placeholder="C:\Data\Export\*.txt"
                  className="mt-1"
                  required
                />
              </div>
            </div>
          </div>

          {/* Target Configuration */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">Ziel</h4>
            
            <div className="space-y-3">
              <div>
                <Label htmlFor="targetAgent" className="text-sm font-medium">
                  Ziel-Agent *
                </Label>
                <Input
                  id="targetAgent"
                  type="text"
                  value={form.targetAgent || ''}
                  onChange={(e) => handleFieldChange('targetAgent', e.target.value)}
                  placeholder="gtasswvw15779"
                  className="mt-1"
                  required
                />
              </div>

              <div>
                <Label htmlFor="targetPath" className="text-sm font-medium">
                  Ziel-Pfad *
                </Label>
                <Input
                  id="targetPath"
                  type="text"
                  value={form.targetPath || ''}
                  onChange={(e) => handleFieldChange('targetPath', e.target.value)}
                  placeholder="D:\Import\"
                  className="mt-1"
                  required
                />
              </div>
            </div>
          </div>

          {/* Transfer Options */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">Transfer-Optionen</h4>
            
            <div className="space-y-3">
              <div>
                <Label className="text-sm font-medium">
                  Verhalten bei existierender Datei
                </Label>
                <select
                  value={form.onExistsBehavior || 'Overwrite'}
                  onChange={(e) => handleFieldChange('onExistsBehavior', e.target.value)}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="Overwrite">Überschreiben</option>
                  <option value="Abort">Abbrechen</option>
                  <option value="Append">Anhängen</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="deleteAfterTransfer"
                  checked={form.deleteAfterTransfer || false}
                  onChange={(e) => handleFieldChange('deleteAfterTransfer', e.target.checked)}
                  className="mr-2"
                />
                <Label htmlFor="deleteAfterTransfer" className="text-sm">
                  Quelldatei nach Transfer löschen
                </Label>
              </div>
            </div>
          </div>
        </div>
      </Card>
    )
  }

  const renderJobForm = () => {
    switch (jobType) {
      case JobType.STANDARD:
        return renderStandardJobForm()
      case JobType.SAP:
        return renderSAPJobForm()
      case JobType.FILE_TRANSFER:
        return renderFileTransferForm()
      default:
        return (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">
              Bitte wählen Sie zuerst einen Job-Typ aus.
            </p>
          </div>
        )
    }
  }

  const getJobTypeTitle = () => {
    switch (jobType) {
      case JobType.STANDARD:
        return 'Standard Job'
      case JobType.SAP:
        return 'SAP Job'
      case JobType.FILE_TRANSFER:
        return 'File Transfer'
      default:
        return 'Job'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {getJobTypeTitle()} konfigurieren
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Definieren Sie die spezifischen Parameter für Ihren Job
        </p>
      </div>

      {/* Job Configuration Form */}
      {renderJobForm()}

      {/* Info Box */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Info className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-yellow-800 dark:text-yellow-200">
              Tipp zur Job-Konfiguration
            </h4>
            <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
              {jobType === JobType.STANDARD && 
                "Verwenden Sie absolute Pfade und testen Sie Ihre Scripts lokal, bevor Sie sie in den Stream einbinden."
              }
              {jobType === JobType.SAP && 
                "Stellen Sie sicher, dass der angegebene Batch User die nötigen Berechtigungen für das Report/Programm hat."
              }
              {jobType === JobType.FILE_TRANSFER && 
                "Prüfen Sie die Netzwerkkonnektivität zwischen den Agenten und die Pfad-Berechtigungen."
              }
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
        <Button
          variant="outline"
          onClick={onPrevious}
          className="flex items-center space-x-2"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Zurück</span>
        </Button>
        
        <Button
          onClick={onNext}
          disabled={!canProceed}
          className="flex items-center space-x-2"
        >
          <span>Weiter</span>
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}

export default JobConfigurationStep