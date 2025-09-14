/**
 * XmlGenerator - Main Component
 * Split-panel interface with Wizard (left) and XML Display (right)
 */
'use client'

import React, { useState, useCallback, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import WizardForm from './components/WizardForm'
import XmlDisplay from './components/XmlDisplay'
import { generateStreamworksXML, validateXML } from './utils/xmlGenerator'
import { WizardFormData } from './types/wizard.types'
import { useWizardState } from './hooks/useWizardState'
import { useXMLPreview } from './hooks/useXMLPreview'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Wand2, 
  FileText, 
  Maximize2, 
  Minimize2,
  RotateCcw,
  HelpCircle,
  Eye,
  EyeOff,
  Code2,
  ArrowLeft,
  Save,
  CheckCircle2
} from 'lucide-react'
import { toast } from 'sonner'
import { useUpdateStream } from '@/hooks/useXMLStreams'
import { XMLStream } from '@/services/xmlStreamsApi'

interface XmlGeneratorProps {
  className?: string
  streamId?: string
  initialData?: XMLStream
}

export const XmlGenerator: React.FC<XmlGeneratorProps> = ({
  className = '',
  streamId,
  initialData
}) => {
  const router = useRouter()
  const [xmlContent, setXmlContent] = useState(initialData?.xml_content || '')
  const [validationResults, setValidationResults] = useState<any>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [viewMode, setViewMode] = useState<'split' | 'wizard-only' | 'xml-only'>('split')
  // Stream management hooks
  const updateStream = useUpdateStream()
  
  // Central wizard state management with integrated auto-save
  const wizard = useWizardState({
    totalSteps: 5,
    enablePersistence: !streamId, // Only use localStorage persistence when not editing a stream
    streamId,
    enableAutoSave: !!streamId, // Enable auto-save when editing an existing stream
    autoSaveDelay: 2000
  })
  
  // Live XML preview functionality
  const xmlPreview = useXMLPreview({
    debounceMs: 500,
    enableAutoPreview: true,
    apiBaseUrl: '/api/xml-generator'
  })

  // Initialize wizard with stream data
  useEffect(() => {
    if (initialData && initialData.wizard_data) {
      wizard.updateFormData(initialData.wizard_data)
      if (initialData.job_type) {
        wizard.setJobType(initialData.job_type as any)
      }
    }
  }, [initialData])

  // Trigger preview when form data changes
  useEffect(() => {
    if (wizard.state.formData) {
      xmlPreview.generatePreview(wizard.state.formData)
    }
  }, [wizard.state.formData, xmlPreview.generatePreview])

  // Update wizard state when XML content changes (for auto-save inclusion)
  useEffect(() => {
    if (xmlContent) {
      wizard.setGeneratedXML(xmlContent, validationResults)
    }
  }, [xmlContent, validationResults])

  const handleXMLGenerated = useCallback(async (content: string, validation?: any) => {
    setXmlContent(content)
    setValidationResults(validation)
    
    // If no validation provided, validate the content
    if (!validation && content) {
      const validationResult = validateXML(content)
      setValidationResults(validationResult)
    }
  }, [])

  const handleRegenerate = useCallback(async () => {
    if (!wizard.state.jobType || !wizard.state.formData.streamProperties) {
      toast.error('Bitte füllen Sie zuerst alle erforderlichen Formulardaten aus')
      return
    }

    setIsGenerating(true)
    wizard.setGenerating(true)
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate processing
      
      const result = generateStreamworksXML(wizard.state.formData)
      
      if (result.success && result.xmlContent) {
        const validation = validateXML(result.xmlContent)
        handleXMLGenerated(result.xmlContent, validation)
        wizard.setGeneratedXML(result.xmlContent, validation)
        toast.success('XML wurde erfolgreich neu generiert!')
      } else {
        toast.error(`Fehler bei der XML-Generierung: ${result.error}`)
      }
    } catch (error) {
      toast.error('Unerwarteter Fehler bei der XML-Generierung')
    } finally {
      setIsGenerating(false)
      wizard.setGenerating(false)
    }
  }, [wizard, handleXMLGenerated])

  // Remove handleFormDataChange as we'll use wizard.updateFormData directly

  const handleToggleViewMode = () => {
    switch (viewMode) {
      case 'split':
        setViewMode('xml-only') // Maximize XML
        break
      case 'xml-only':
        setViewMode('wizard-only') // Hide XML, show only wizard
        break
      case 'wizard-only':
        setViewMode('split') // Return to split view
        break
    }
  }

  const handleToggleXmlVisibility = () => {
    if (viewMode === 'wizard-only') {
      setViewMode('split') // Show XML in split view
    } else {
      setViewMode('wizard-only') // Hide XML
    }
  }

  const handleReset = () => {
    setXmlContent('')
    setValidationResults(null)
    wizard.resetWizard()
    setViewMode('split')
    toast.info('Generator wurde zurückgesetzt')
  }

  const handleSave = async () => {
    console.log('🔄 Save button clicked - starting save process...')

    if (!streamId) {
      console.error('❌ Save failed: No streamId available')
      toast.error('Fehler: Keine Stream-ID verfügbar')
      return
    }

    if (!wizard.state.formData) {
      console.error('❌ Save failed: No form data available')
      toast.error('Fehler: Keine Formulardaten verfügbar')
      return
    }

    console.log('📋 Save data prepared:', {
      streamId,
      hasFormData: !!wizard.state.formData,
      formDataKeys: wizard.state.formData ? Object.keys(wizard.state.formData) : [],
      hasXmlContent: !!xmlContent,
      xmlContentLength: xmlContent ? xmlContent.length : 0
    })

    try {
      const savePayload = {
        streamId,
        data: {
          wizard_data: wizard.state.formData,
          xml_content: xmlContent || undefined
          // Note: Removed 'status: complete' as backend expects German status values
          // Let the backend keep the current status unchanged
        },
        createVersion: true
      }

      console.log('📤 Sending save request:', savePayload)

      const result = await updateStream.mutateAsync(savePayload)

      console.log('✅ Save successful:', result)
      toast.success('Stream gespeichert!')
    } catch (error) {
      console.error('❌ Save failed with error:', error)
      console.error('Error details:', {
        name: error?.name,
        message: error?.message,
        stack: error?.stack,
        response: error?.response,
        status: error?.response?.status,
        statusText: error?.response?.statusText,
        data: error?.response?.data
      })

      const errorMessage = error?.message || 'Unbekannter Fehler'
      toast.error(`Fehler beim Speichern: ${errorMessage}`)
    }
  }

  const handleBackToList = () => {
    if (wizard.autoSave.hasUnsavedChanges) {
      if (confirm('Sie haben ungespeicherte Änderungen. Möchten Sie wirklich zur Stream-Liste zurückkehren?')) {
        router.push('/xml')
      }
    } else {
      router.push('/xml')
    }
  }

  const formatLastSaved = (date: Date) => {
    return date.toLocaleTimeString('de-DE', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className={`flex flex-col h-full bg-gray-50 dark:bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {streamId && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBackToList}
                className="mr-2"
              >
                <ArrowLeft className="w-4 h-4" />
              </Button>
            )}
            
            <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Wand2 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {initialData?.stream_name || 'XML Generator'}
              </h1>
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <p>
                  {streamId
                    ? `Stream bearbeiten${wizard.autoSave.hasUnsavedChanges ? ' •' : ''}`
                    : 'Erstellen Sie Streamworks-XML durch einen geführten Wizard'
                  }
                </p>
                
                {streamId && (
                  <div className="flex items-center gap-2 text-sm">
                    {wizard.autoSave.isAutoSaving && (
                      <span className="text-blue-600 flex items-center gap-1">
                        <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                        Speichert automatisch...
                      </span>
                    )}

                    {wizard.autoSave.lastAutoSaved && !wizard.autoSave.hasUnsavedChanges && (
                      <span className="text-green-600 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        Gespeichert um {formatLastSaved(wizard.autoSave.lastAutoSaved)}
                      </span>
                    )}

                    {wizard.autoSave.hasUnsavedChanges && !wizard.autoSave.isAutoSaving && (
                      <span className="text-amber-600">
                        Ungespeicherte Änderungen
                      </span>
                    )}

                    {wizard.autoSave.autoSaveError && (
                      <span className="text-red-600 text-xs">
                        Auto-Save Fehler
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {streamId && (
              <Button
                variant="default"
                size="sm"
                onClick={handleSave}
                disabled={updateStream.isPending || (!wizard.autoSave.hasUnsavedChanges && !wizard.state.formData)}
                className="flex items-center space-x-2"
                onMouseOver={() => {
                  const canSave = !updateStream.isPending && (wizard.autoSave.hasUnsavedChanges || wizard.state.formData)
                  console.log('🔘 Save Button Debug Info:', {
                    streamId,
                    isPending: updateStream.isPending,
                    hasUnsavedChanges: wizard.autoSave.hasUnsavedChanges,
                    hasFormData: !!wizard.state.formData,
                    canSave,
                    autoSaveState: wizard.autoSave,
                    formDataKeys: wizard.state.formData ? Object.keys(wizard.state.formData) : []
                  })
                }}
              >
                <Save className="w-4 h-4" />
                <span>{updateStream.isPending ? 'Speichert...' : 'Speichern'}</span>
              </Button>
            )}
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleRegenerate}
              disabled={isGenerating || !wizard.state.jobType}
              className="flex items-center space-x-2"
            >
              <RotateCcw className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
              <span>Regenerieren</span>
            </Button>
            
            {/* XML Visibility Toggle */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleToggleXmlVisibility}
              className="flex items-center space-x-2"
            >
              {viewMode === 'wizard-only' ? (
                <>
                  <Eye className="w-4 h-4" />
                  <span>XML anzeigen</span>
                </>
              ) : (
                <>
                  <EyeOff className="w-4 h-4" />
                  <span>XML ausblenden</span>
                </>
              )}
            </Button>
            
            {/* View Mode Toggle */}
            {viewMode !== 'wizard-only' && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleToggleViewMode}
                className="flex items-center space-x-2"
              >
                {viewMode === 'xml-only' ? (
                  <>
                    <Minimize2 className="w-4 h-4" />
                    <span>Aufteilen</span>
                  </>
                ) : (
                  <>
                    <Maximize2 className="w-4 h-4" />
                    <span>XML maximieren</span>
                  </>
                )}
              </Button>
            )}

            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="flex items-center space-x-2 text-gray-500 hover:text-gray-700"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {viewMode === 'xml-only' ? (
          // XML Only View
          <div className="h-full p-6">
            <XmlDisplay
              xmlContent={xmlContent}
              isGenerating={isGenerating}
              validationResults={validationResults}
              previewHook={xmlPreview}
              className="h-full"
            />
          </div>
        ) : viewMode === 'wizard-only' ? (
          // Wizard Only View
          <div className="h-full bg-white dark:bg-gray-800 min-h-0">
            <WizardForm
              onXMLGenerated={handleXMLGenerated}
              externalWizardState={wizard}
              className="h-full"
            />
          </div>
        ) : (
          // Split Panel Layout
          <PanelGroup direction="horizontal" className="h-full">
            {/* Left Panel - Wizard Form */}
            <Panel defaultSize={50} minSize={30} maxSize={70}>
              <div className="h-full bg-white dark:bg-gray-800 min-h-0">
                <WizardForm
                  onXMLGenerated={handleXMLGenerated}
                  externalWizardState={wizard}
                  className="h-full"
                />
              </div>
            </Panel>

            {/* Resize Handle */}
            <PanelResizeHandle className="w-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
              <div className="w-1 h-full bg-gray-300 dark:bg-gray-600 mx-auto" />
            </PanelResizeHandle>

            {/* Right Panel - XML Display */}
            <Panel defaultSize={50} minSize={30}>
              <div className="h-full p-6">
                <XmlDisplay
                  xmlContent={xmlContent}
                  isGenerating={isGenerating}
                  validationResults={validationResults}
                  previewHook={xmlPreview}
                  className="h-full"
                />
              </div>
            </Panel>
          </PanelGroup>
        )}
      </div>

      {/* Help/Info Footer */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4 text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-1">
              <FileText className="w-4 h-4" />
              <span>Streamworks XML Generator v1.0</span>
            </div>
            
            {xmlContent && (
              <div className="flex items-center space-x-4">
                <span>
                  {xmlContent.split('\n').length} Zeilen
                </span>
                <span>
                  ~{Math.round(xmlContent.length / 1024)}KB
                </span>
                {validationResults && (
                  <span className={
                    validationResults.isValid 
                      ? 'text-green-600 dark:text-green-400' 
                      : 'text-red-600 dark:text-red-400'
                  }>
                    {validationResults.isValid ? '✓ Gültig' : `✗ ${validationResults.errors.length} Fehler`}
                  </span>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center space-x-2 text-gray-400 dark:text-gray-500">
            <HelpCircle className="w-4 h-4" />
            <span>Verwenden Sie den Wizard links, um XML rechts zu generieren</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default XmlGenerator