/**
 * Wizard State Management Hook
 * Manages form data, navigation, and validation across all wizard steps
 */
'use client'

import { useState, useCallback, useEffect } from 'react'
import { 
  WizardState, 
  WizardFormData, 
  JobType, 
  WizardError,
  WizardPersistence,
  WizardChapter,
  SubChapter
} from '../types/wizard.types'

const WIZARD_STORAGE_KEY = 'streamworks_xml_wizard'
const SESSION_DURATION = 60 * 60 * 1000 // 1 hour

// Default chapter structure
const createDefaultChapters = (): WizardChapter[] => [
  {
    id: 'stream-properties',
    title: 'Stream-Eigenschaften',
    description: 'Grundkonfiguration des Streams',
    icon: 'settings',
    isCompleted: false,
    isExpanded: true,
    subChapters: [
      {
        id: 'basic-info',
        title: 'Grunddaten',
        description: 'Name, Beschreibung & Pfad',
        isCompleted: false,
        isValid: false,
        hasErrors: false
      },
      {
        id: 'contact-person',
        title: 'Kontaktperson',
        description: 'Ansprechpartner & Zuständigkeit',
        isCompleted: false,
        isValid: false,
        hasErrors: false
      }
    ]
  },
  {
    id: 'job-configuration',
    title: 'Job-Konfiguration',
    description: 'Job-Typ und Parameter',
    icon: 'play',
    isCompleted: false,
    isExpanded: false,
    subChapters: [
      {
        id: 'job-type',
        title: 'Job-Typ auswählen',
        description: 'Standard, SAP oder File Transfer',
        isCompleted: false,
        isValid: false,
        hasErrors: false
      },
      {
        id: 'job-parameters',
        title: 'Job-Parameter',
        description: 'Spezifische Konfiguration je Job-Typ',
        isCompleted: false,
        isValid: false,
        hasErrors: false
      },
      {
        id: 'advanced-options',
        title: 'Erweiterte Optionen',
        description: 'Zusätzliche Job-Einstellungen',
        isCompleted: false,
        isValid: false,
        hasErrors: false
      }
    ]
  },
  {
    id: 'scheduling',
    title: 'Zeitplanung',
    description: 'Ausführungszeiten definieren',
    icon: 'clock',
    isCompleted: false,
    isExpanded: false,
    subChapters: [
      {
        id: 'execution-mode',
        title: 'Ausführungsmodus',
        description: 'Manuell, zeitgesteuert oder erweitert',
        isCompleted: false,
        isValid: false,
        hasErrors: false
      },
      {
        id: 'time-settings',
        title: 'Zeit & Wiederholung',
        description: 'Zeiten, Wochentage & Wiederholungen',
        isCompleted: false,
        isValid: false,
        hasErrors: false
      }
    ]
  },
  {
    id: 'review',
    title: 'Überprüfung & Export',
    description: 'Zusammenfassung und XML-Generierung',
    icon: 'target',
    isCompleted: false,
    isExpanded: false,
    subChapters: [
      {
        id: 'summary',
        title: 'Zusammenfassung',
        description: 'Überblick aller Einstellungen',
        isCompleted: false,
        isValid: false,
        hasErrors: false
      },
      {
        id: 'xml-generation',
        title: 'XML-Generierung',
        description: 'Erstellen und validieren der XML-Datei',
        isCompleted: false,
        isValid: false,
        hasErrors: false
      }
    ]
  }
]

interface UseWizardStateProps {
  totalSteps?: number
  enablePersistence?: boolean
}

export const useWizardState = ({ 
  totalSteps = 5, 
  enablePersistence = true 
}: UseWizardStateProps = {}) => {
  
  // Initialize state
  const [state, setState] = useState<WizardState>({
    currentStep: 1,
    totalSteps,
    currentChapter: 'stream-properties',
    currentSubChapter: 'basic-info',
    chapters: createDefaultChapters(),
    jobType: null,
    formData: {},
    isValid: false,
    canProceed: false,
    isGenerating: false
  })

  const [error, setError] = useState<WizardError | null>(null)

  // Load persisted data on mount
  useEffect(() => {
    if (enablePersistence) {
      loadPersistedData()
    }
  }, [enablePersistence])

  // Save data when state changes
  useEffect(() => {
    if (enablePersistence && (state.formData || state.currentStep > 1)) {
      savePersistedData()
    }
  }, [state.formData, state.currentStep, enablePersistence])

  // Persistence functions
  const loadPersistedData = useCallback(() => {
    try {
      const stored = localStorage.getItem(WIZARD_STORAGE_KEY)
      if (!stored) return

      const persistence: WizardPersistence = JSON.parse(stored)
      
      // Check if session is still valid (not expired)
      const now = new Date()
      const lastSaved = new Date(persistence.lastSaved)
      const isExpired = (now.getTime() - lastSaved.getTime()) > SESSION_DURATION

      if (!isExpired && persistence.formData) {
        setState(prev => ({
          ...prev,
          currentStep: persistence.currentStep,
          formData: persistence.formData,
          jobType: persistence.formData.jobType || null
        }))
      } else if (isExpired) {
        // Clean up expired data
        localStorage.removeItem(WIZARD_STORAGE_KEY)
      }
    } catch (error) {
      console.warn('Failed to load persisted wizard data:', error)
      localStorage.removeItem(WIZARD_STORAGE_KEY)
    }
  }, [])

  const savePersistedData = useCallback(() => {
    try {
      const persistence: WizardPersistence = {
        sessionId: generateSessionId(),
        lastSaved: new Date(),
        formData: state.formData,
        currentStep: state.currentStep
      }
      localStorage.setItem(WIZARD_STORAGE_KEY, JSON.stringify(persistence))
    } catch (error) {
      console.warn('Failed to save wizard data:', error)
    }
  }, [state.formData, state.currentStep])

  const clearPersistedData = useCallback(() => {
    localStorage.removeItem(WIZARD_STORAGE_KEY)
  }, [])

  // Form data management
  const updateFormData = useCallback((updates: Partial<WizardFormData>) => {
    setState(prev => {
      const newFormData = { ...prev.formData, ...updates }
      const isValid = validateFormData(newFormData, prev.currentStep)
      
      return {
        ...prev,
        formData: newFormData,
        jobType: newFormData.jobType || prev.jobType,
        isValid,
        canProceed: isValid
      }
    })
  }, [])

  const setJobType = useCallback((jobType: JobType) => {
    setState(prev => ({
      ...prev,
      jobType,
      formData: { ...prev.formData, jobType }
    }))
  }, [])

  // Navigation
  const goToStep = useCallback((step: number) => {
    if (step < 1 || step > totalSteps) return
    
    setState(prev => ({
      ...prev,
      currentStep: step,
      canProceed: validateFormData(prev.formData, step)
    }))
  }, [totalSteps])

  const nextStep = useCallback(() => {
    setState(prev => {
      const nextStep = Math.min(prev.currentStep + 1, totalSteps)
      return {
        ...prev,
        currentStep: nextStep,
        canProceed: validateFormData(prev.formData, nextStep)
      }
    })
  }, [totalSteps])

  const previousStep = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentStep: Math.max(prev.currentStep - 1, 1)
    }))
  }, [])

  const canGoNext = useCallback(() => {
    return state.currentStep < totalSteps && state.canProceed && !state.isGenerating
  }, [state.currentStep, state.canProceed, state.isGenerating, totalSteps])

  const canGoPrevious = useCallback(() => {
    return state.currentStep > 1 && !state.isGenerating
  }, [state.currentStep, state.isGenerating])

  // XML Generation
  const setGenerating = useCallback((isGenerating: boolean) => {
    setState(prev => ({ ...prev, isGenerating }))
  }, [])

  const setGeneratedXML = useCallback((xmlContent: string, validationResults?: any) => {
    setState(prev => ({
      ...prev,
      generatedXML: xmlContent,
      validationResults,
      isGenerating: false
    }))
  }, [])

  // Error handling
  const setWizardError = useCallback((error: WizardError | null) => {
    setError(error)
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  // Reset wizard
  const resetWizard = useCallback(() => {
    setState({
      currentStep: 1,
      totalSteps,
      jobType: null,
      formData: {},
      isValid: false,
      canProceed: false,
      isGenerating: false
    })
    setError(null)
    clearPersistedData()
  }, [totalSteps, clearPersistedData])

  // Validation logic
  const validateFormData = (formData: Partial<WizardFormData>, step: number): boolean => {
    switch (step) {
      case 1: // Stream Properties (now first!)
        return !!(formData.streamProperties?.streamName && 
                 formData.streamProperties?.description &&
                 formData.streamProperties?.contactPerson?.firstName &&
                 formData.streamProperties?.contactPerson?.lastName)
        
      case 2: // Job Type Selection  
        return !!formData.jobType
        
      case 3: // Job Form
        if (!formData.jobForm) return false
        
        // Basic validation based on job type
        if (formData.jobType === JobType.STANDARD) {
          const standardForm = formData.jobForm as any
          return !!(standardForm.jobName && standardForm.agent && standardForm.os && standardForm.script)
        }
        
        if (formData.jobType === JobType.SAP) {
          const sapForm = formData.jobForm as any
          return !!(sapForm.jobName && sapForm.system && sapForm.report && sapForm.batchUser)
        }
        
        if (formData.jobType === JobType.FILE_TRANSFER) {
          const ftForm = formData.jobForm as any
          return !!(ftForm.jobName && ftForm.sourceAgent && ftForm.sourcePath && 
                   ftForm.targetAgent && ftForm.targetPath)
        }
        
        return true
        
      case 4: // Scheduling
        return !!formData.scheduling?.mode
        
      case 5: // Review
        return validateFormData(formData, 1) && 
               validateFormData(formData, 2) && 
               validateFormData(formData, 3) && 
               validateFormData(formData, 4)
               
      default:
        return true
    }
  }

  // Progress calculation
  const getProgress = useCallback(() => {
    let completedSteps = 0
    
    if (state.formData.streamProperties && validateFormData(state.formData, 1)) completedSteps++
    if (state.jobType) completedSteps++
    if (state.formData.jobForm && validateFormData(state.formData, 3)) completedSteps++
    if (state.formData.scheduling) completedSteps++
    if (state.generatedXML) completedSteps++
    
    return Math.round((completedSteps / totalSteps) * 100)
  }, [state, totalSteps])

  // Form completion status
  const isComplete = useCallback(() => {
    return validateFormData(state.formData, 5) && !!state.generatedXML
  }, [state.formData, state.generatedXML])

  // Chapter navigation functions
  const navigateToChapter = useCallback((chapterId: string) => {
    setState(prev => ({
      ...prev,
      currentChapter: chapterId,
      currentSubChapter: prev.chapters.find(c => c.id === chapterId)?.subChapters[0]?.id || ''
    }))
  }, [])

  const navigateToSubChapter = useCallback((chapterId: string, subChapterId: string) => {
    setState(prev => ({
      ...prev,
      currentChapter: chapterId,
      currentSubChapter: subChapterId
    }))
  }, [])

  const toggleChapterExpansion = useCallback((chapterId: string) => {
    setState(prev => ({
      ...prev,
      chapters: prev.chapters.map(chapter => 
        chapter.id === chapterId 
          ? { ...chapter, isExpanded: !chapter.isExpanded }
          : chapter
      )
    }))
  }, [])

  const updateChapterStatus = useCallback(() => {
    setState(prev => ({
      ...prev,
      chapters: prev.chapters.map(chapter => {
        // Update sub-chapters based on form data
        const updatedSubChapters = chapter.subChapters.map(subChapter => {
          let isValid = false
          let isCompleted = false
          let hasErrors = false
          let validationMessage = ''

          // Validate based on chapter and sub-chapter combination
          if (chapter.id === 'stream-properties') {
            if (subChapter.id === 'basic-info') {
              isValid = !!(prev.formData.streamProperties?.streamName && 
                          prev.formData.streamProperties?.description)
              isCompleted = isValid
            } else if (subChapter.id === 'contact-person') {
              isValid = !!(prev.formData.streamProperties?.contactPerson?.firstName && 
                          prev.formData.streamProperties?.contactPerson?.lastName)
              isCompleted = isValid
            }
          } else if (chapter.id === 'job-configuration') {
            if (subChapter.id === 'job-type') {
              isValid = !!prev.jobType
              isCompleted = isValid
            } else if (subChapter.id === 'job-parameters') {
              isValid = !!prev.formData.jobForm
              isCompleted = isValid
            }
          } else if (chapter.id === 'scheduling') {
            if (subChapter.id === 'execution-mode' || subChapter.id === 'time-settings') {
              isValid = !!prev.formData.scheduling
              isCompleted = isValid
            }
          } else if (chapter.id === 'review') {
            if (subChapter.id === 'summary') {
              isValid = validateFormData(prev.formData, 5)
              isCompleted = isValid
            } else if (subChapter.id === 'xml-generation') {
              isValid = !!prev.generatedXML
              isCompleted = isValid
            }
          }

          return {
            ...subChapter,
            isValid,
            isCompleted,
            hasErrors,
            validationMessage
          }
        })

        // Update chapter completion status
        const chapterCompleted = updatedSubChapters.every(sc => sc.isCompleted)

        return {
          ...chapter,
          subChapters: updatedSubChapters,
          isCompleted: chapterCompleted
        }
      })
    }))
  }, [])

  // Update chapter status when form data changes
  useEffect(() => {
    updateChapterStatus()
  }, [state.formData, state.jobType, state.generatedXML, updateChapterStatus])

  return {
    // State
    state,
    error,
    
    // Form data
    updateFormData,
    setJobType,
    
    // Navigation  
    goToStep,
    nextStep,
    previousStep,
    canGoNext: canGoNext(),
    canGoPrevious: canGoPrevious(),
    
    // Chapter Navigation
    navigateToChapter,
    navigateToSubChapter,
    toggleChapterExpansion,
    
    // XML Generation
    setGenerating,
    setGeneratedXML,
    
    // Error handling
    setWizardError,
    clearError,
    
    // Utility
    resetWizard,
    getProgress,
    isComplete: isComplete(),
    
    // Persistence
    clearPersistedData
  }
}

// Helper functions
function generateSessionId(): string {
  return `wizard_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Default form data factories
export const createDefaultStandardForm = (): Partial<WizardFormData> => ({
  jobType: JobType.STANDARD,
  jobForm: {
    jobName: '',
    agent: 'gtasswvk05445',
    os: 'Windows' as any,
    script: 'rem Default Windows Script\ndir',
    parameters: []
  }
})

export const createDefaultSAPForm = (): Partial<WizardFormData> => ({
  jobType: JobType.SAP,
  jobForm: {
    jobName: '',
    system: '',
    report: '',
    variant: '',
    batchUser: '',
    selectionParameters: []
  }
})

export const createDefaultFileTransferForm = (): Partial<WizardFormData> => ({
  jobType: JobType.FILE_TRANSFER,
  jobForm: {
    jobName: '',
    sourceAgent: 'gtasswvv15778',
    sourcePath: 'E:\\streamworks\\ft\\source\\',
    targetAgent: 'gtasswvw15779',
    targetPath: 'E:\\streamworks\\ft\\target\\',
    onExistsBehavior: 'Overwrite',
    deleteAfterTransfer: false
  }
})

export const createDefaultStreamProperties = (): Partial<WizardFormData> => ({
  streamProperties: {
    streamName: '',
    description: '',
    documentation: 'Meine Dokumentation',
    contactPerson: {
      firstName: 'Ravel-Lukas',
      lastName: 'Geck',
      company: 'Arvato Systems',
      department: ''
    },
    maxRuns: 5,
    retentionDays: 30,
    severityGroup: '',
    streamPath: '/'
  }
})

export const createDefaultScheduling = (): Partial<WizardFormData> => ({
  scheduling: {
    mode: 'simple' as any,
    simple: {
      preset: 'manual',
      time: '06:00',
      weekdays: [true, true, true, true, true, false, false] // Mon-Fri
    }
  }
})