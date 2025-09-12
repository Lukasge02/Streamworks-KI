/**
 * WizardForm Component
 * Main wizard interface with step navigation and form management
 */
'use client'

import React from 'react'
import { useWizardState } from '../hooks/useWizardState'
import { WizardFormData } from '../types/wizard.types'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  CheckCircle, 
  Circle, 
  RefreshCw,
  AlertTriangle
} from 'lucide-react'

// Import step components
import JobTypeStep from './steps/JobTypeStep'
import JobConfigurationStep from './steps/JobConfigurationStep'
import StreamPropertiesStep from './steps/StreamPropertiesStep'
import SchedulingStep from './steps/SchedulingStep'
import ReviewStep from './steps/ReviewStep'
import ChapterNavigation from './ChapterNavigation'

interface WizardFormProps {
  onXMLGenerated?: (xmlContent: string, validationResults?: any) => void
  className?: string
  // External state props (optional - if provided, use external state instead of internal hook)
  externalWizardState?: ReturnType<typeof import('../hooks/useWizardState').useWizardState>
}

// Chapter to step component mapping
const getStepComponent = (chapterId: string, subChapterId: string) => {
  switch (chapterId) {
    case 'stream-properties':
      return StreamPropertiesStep
    case 'job-configuration':
      if (subChapterId === 'job-type') return JobTypeStep
      return JobConfigurationStep
    case 'scheduling':
      return SchedulingStep
    case 'review':
      return ReviewStep
    default:
      return StreamPropertiesStep
  }
}

export const WizardForm: React.FC<WizardFormProps> = ({
  onXMLGenerated,
  className = '',
  externalWizardState
}) => {
  // Use external state if provided, otherwise use internal hook
  const internalWizard = useWizardState({ totalSteps: 5 })
  const wizard = externalWizardState || internalWizard

  // Handle XML generation callback
  React.useEffect(() => {
    if (wizard.state.generatedXML && onXMLGenerated) {
      onXMLGenerated(wizard.state.generatedXML, wizard.state.validationResults)
    }
  }, [wizard.state.generatedXML, wizard.state.validationResults, onXMLGenerated])

  const CurrentStepComponent = getStepComponent(
    wizard.state.currentChapter, 
    wizard.state.currentSubChapter
  )

  return (
    <div className={`flex h-full ${className}`}>
      {/* Left Sidebar - Vertical Navigation */}
      <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            XML Generator
          </h2>
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
            <span>Kapitel: {wizard.state.chapters.find(c => c.id === wizard.state.currentChapter)?.title}</span>
            <span>{wizard.getProgress()}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-2">
            <div 
              className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${wizard.getProgress()}%` }}
            />
          </div>
        </div>

        {/* Chapter Navigation */}
        <div className="flex-1 p-4 overflow-y-auto">
          <ChapterNavigation
            chapters={wizard.state.chapters}
            currentChapter={wizard.state.currentChapter}
            currentSubChapter={wizard.state.currentSubChapter}
            onChapterClick={wizard.navigateToChapter}
            onSubChapterClick={wizard.navigateToSubChapter}
            onToggleChapter={wizard.toggleChapterExpansion}
          />
        </div>

      </div>

      {/* Step Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          {wizard.error && (
            <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
                <div>
                  <p className="text-sm font-medium text-red-800 dark:text-red-200">
                    {wizard.error.message}
                  </p>
                  {wizard.error.details && (
                    <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                      {wizard.error.details}
                    </p>
                  )}
                  {wizard.error.canRetry && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={wizard.clearError}
                      className="mt-2"
                    >
                      Wiederholen
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )}

          {CurrentStepComponent && (
            <CurrentStepComponent
              formData={wizard.state.formData}
              onUpdateData={wizard.updateFormData}
              onNext={wizard.nextStep}
              onPrevious={wizard.previousStep}
              canProceed={wizard.canGoNext}
              isLastStep={wizard.state.currentStep === wizard.state.totalSteps}
            />
          )}
        </div>
      </div>

    </div>
  )
}

export default WizardForm