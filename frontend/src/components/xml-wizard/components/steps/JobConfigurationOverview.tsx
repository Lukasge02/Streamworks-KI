/**
 * Job Configuration Overview
 * Hauptseite für das Job-Configuration Kapitel
 */
'use client'

import React from 'react'
import { JobType, WizardStepProps } from '../../types/wizard.types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { 
  Terminal, 
  Database, 
  FolderSync, 
  Settings,
  ChevronRight,
  CheckCircle2,
  Circle,
  Play
} from 'lucide-react'

const JOB_TYPE_INFO = [
  {
    type: JobType.STANDARD,
    title: 'Standard Job',
    description: 'Windows oder Unix Script ausführen',
    icon: Terminal,
    examples: ['Batch-Scripts', 'Shell-Commands', 'PowerShell'],
    color: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
    textColor: 'text-blue-600 dark:text-blue-400'
  },
  {
    type: JobType.SAP,
    title: 'SAP Job',
    description: 'SAP Report oder Programm ausführen',
    icon: Database,
    examples: ['SAP Reports', 'ABAP Programme', 'Batch Jobs'],
    color: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    textColor: 'text-green-600 dark:text-green-400'
  },
  {
    type: JobType.FILE_TRANSFER,
    title: 'File Transfer',
    description: 'Dateien zwischen Systemen übertragen',
    icon: FolderSync,
    examples: ['FTP Transfer', 'Lokale Kopie', 'Netzwerk-Copy'],
    color: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800',
    textColor: 'text-purple-600 dark:text-purple-400'
  },
  {
    type: JobType.CUSTOM,
    title: 'Benutzerdefiniert',
    description: 'Eigene Job-Konfiguration erstellen',
    icon: Settings,
    examples: ['REST API Calls', 'Complex Workflows', 'Custom Scripts'],
    color: 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800',
    textColor: 'text-orange-600 dark:text-orange-400'
  }
]

export const JobConfigurationOverview: React.FC<WizardStepProps> = ({
  formData,
  onUpdateData,
  navigateToSubChapter
}) => {
  const selectedJobType = formData.jobType

  const handleJobTypeSelect = (jobType: JobType) => {
    onUpdateData({ jobType })
    
    // Direkt zu Job-Parametern navigieren
    setTimeout(() => {
      if (navigateToSubChapter) {
        navigateToSubChapter('job-configuration', 'job-parameters')
      }
    }, 300)
  }

  const handleNavigateToJobType = () => {
    if (navigateToSubChapter) {
      navigateToSubChapter('job-configuration', 'job-type')
    }
  }

  const handleNavigateToParameters = () => {
    if (navigateToSubChapter) {
      navigateToSubChapter('job-configuration', 'job-parameters')
    }
  }

  const isJobTypeSelected = !!selectedJobType
  const selectedJobInfo = JOB_TYPE_INFO.find(info => info.type === selectedJobType)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
            <Play className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Job-Konfiguration
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Konfigurieren Sie den Job-Typ und dessen Parameter für Ihren Stream
        </p>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Job Type Selection */}
        <Card 
          className={`p-4 cursor-pointer transition-all duration-200 ${
            isJobTypeSelected ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-900/20' : 'hover:shadow-md'
          }`}
          onClick={handleNavigateToJobType}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg ${
                isJobTypeSelected ? 'bg-green-100 dark:bg-green-800' : 'bg-gray-100 dark:bg-gray-800'
              }`}>
                {isJobTypeSelected ? (
                  <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400" />
                ) : (
                  <Circle className="w-5 h-5 text-gray-400" />
                )}
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Job-Typ auswählen</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {isJobTypeSelected ? selectedJobInfo?.title : 'Standard, SAP, File Transfer oder Custom'}
                </p>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </div>
        </Card>

        {/* Job Parameters */}
        <Card 
          className={`p-4 cursor-pointer transition-all duration-200 ${
            isJobTypeSelected ? 'hover:shadow-md' : 'opacity-60 cursor-not-allowed'
          }`}
          onClick={isJobTypeSelected ? handleNavigateToParameters : undefined}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800">
                <Settings className="w-5 h-5 text-gray-400" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Job-Parameter</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {isJobTypeSelected ? 'Parameter konfigurieren' : 'Erst Job-Typ auswählen'}
                </p>
              </div>
            </div>
            {isJobTypeSelected && <ChevronRight className="w-5 h-5 text-gray-400" />}
          </div>
        </Card>
      </div>

      {/* Selected Job Type Details */}
      {selectedJobInfo && (
        <Card className={`p-6 ${selectedJobInfo.color}`}>
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
              <selectedJobInfo.icon className={`w-6 h-6 ${selectedJobInfo.textColor}`} />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Gewählter Job-Typ: {selectedJobInfo.title}
              </h3>
              <p className="text-gray-700 dark:text-gray-300 mb-3">
                {selectedJobInfo.description}
              </p>
              <div className="flex flex-wrap gap-2">
                {selectedJobInfo.examples.map((example, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                  >
                    {example}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </Card>
      )}

    </div>
  )
}

export default JobConfigurationOverview