/**
 * Job Type Selection Step
 * First step of the wizard - choose job type
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
  Clock,
  ChevronRight 
} from 'lucide-react'

const JOB_TYPE_OPTIONS = [
  {
    type: JobType.STANDARD,
    title: 'Standard Job',
    description: 'Windows oder Unix Script ausführen',
    icon: Terminal,
    complexity: 'Einfach',
    estimatedTime: '2-3 Minuten',
    examples: ['Batch-Scripts', 'Shell-Commands', 'PowerShell'],
    color: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
  },
  {
    type: JobType.SAP,
    title: 'SAP Job',
    description: 'SAP Report oder Programm ausführen',
    icon: Database,
    complexity: 'Mittel',
    estimatedTime: '4-5 Minuten',
    examples: ['SAP Reports', 'ABAP Programme', 'Batch Jobs'],
    color: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
  },
  {
    type: JobType.FILE_TRANSFER,
    title: 'File Transfer',
    description: 'Dateien zwischen Systemen übertragen',
    icon: FolderSync,
    complexity: 'Einfach',
    estimatedTime: '3-4 Minuten',
    examples: ['FTP Transfer', 'Lokale Kopie', 'Netzwerk-Copy'],
    color: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800'
  },
  {
    type: JobType.CUSTOM,
    title: 'Benutzerdefiniert',
    description: 'Eigene Job-Konfiguration erstellen',
    icon: Settings,
    complexity: 'Komplex',
    estimatedTime: '8-10 Minuten',
    examples: ['REST API Calls', 'Complex Workflows', 'Custom Scripts'],
    color: 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800'
  }
]

export const JobTypeStep: React.FC<WizardStepProps> = ({
  formData,
  onUpdateData,
  onNext,
  canProceed,
  isLastStep
}) => {
  const selectedJobType = formData.jobType

  const handleJobTypeSelect = (jobType: JobType) => {
    onUpdateData({ jobType })
    
    // Auto-advance after selection
    setTimeout(() => {
      if (onNext) {
        onNext()
      }
    }, 500)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Job-Typ auswählen
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Wählen Sie den Typ des Jobs aus, den Sie in Ihrem Stream ausführen möchten
        </p>
      </div>

      {/* Job Type Cards */}
      <div className="space-y-4">
        {JOB_TYPE_OPTIONS.map((option) => {
          const Icon = option.icon
          const isSelected = selectedJobType === option.type
          
          return (
            <Card
              key={option.type}
              className={`relative cursor-pointer transition-all duration-200 hover:shadow-md ${
                isSelected 
                  ? `${option.color} ring-2 ring-blue-500 dark:ring-blue-400` 
                  : 'hover:shadow-lg'
              }`}
              onClick={() => handleJobTypeSelect(option.type)}
            >
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      isSelected 
                        ? 'bg-blue-100 dark:bg-blue-900' 
                        : 'bg-gray-100 dark:bg-gray-800'
                    }`}>
                      <Icon className={`w-6 h-6 ${
                        isSelected 
                          ? 'text-blue-600 dark:text-blue-400' 
                          : 'text-gray-600 dark:text-gray-300'
                      }`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {option.title}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {option.description}
                      </p>
                    </div>
                  </div>
                  
                  {isSelected && (
                    <ChevronRight className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  )}
                </div>

                {/* Metadata */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">Komplexität:</span>
                    <span className={`font-medium ${
                      option.complexity === 'Einfach' 
                        ? 'text-green-600 dark:text-green-400'
                        : option.complexity === 'Mittel'
                        ? 'text-yellow-600 dark:text-yellow-400'
                        : 'text-red-600 dark:text-red-400'
                    }`}>
                      {option.complexity}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">
                      <Clock className="w-4 h-4 inline mr-1" />
                      Geschätzte Zeit:
                    </span>
                    <span className="text-gray-700 dark:text-gray-300 font-medium">
                      {option.estimatedTime}
                    </span>
                  </div>

                  {/* Examples */}
                  <div className="mt-4">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                      Beispiele:
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {option.examples.map((example, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                        >
                          {example}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Selection Info */}
      {selectedJobType && (
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>{JOB_TYPE_OPTIONS.find(opt => opt.type === selectedJobType)?.title}</strong> ausgewählt. 
              Klicken Sie "Weiter", um zur Job-Konfiguration zu gelangen.
            </p>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
        <div></div> {/* Empty div for spacing */}
        
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

export default JobTypeStep