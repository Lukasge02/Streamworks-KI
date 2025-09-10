/**
 * XmlGenerator - Main Component
 * Split-panel interface with Wizard (left) and XML Display (right)
 */
'use client'

import React, { useState, useCallback } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import WizardForm from './components/WizardForm'
import XmlDisplay from './components/XmlDisplay'
import { generateStreamworksXML, validateXML } from './utils/xmlGenerator'
import { WizardFormData } from './types/wizard.types'
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
  Code2
} from 'lucide-react'
import { toast } from 'sonner'

interface XmlGeneratorProps {
  className?: string
}

export const XmlGenerator: React.FC<XmlGeneratorProps> = ({
  className = ''
}) => {
  const [xmlContent, setXmlContent] = useState('')
  const [validationResults, setValidationResults] = useState<any>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [viewMode, setViewMode] = useState<'split' | 'wizard-only' | 'xml-only'>('split')
  const [currentFormData, setCurrentFormData] = useState<Partial<WizardFormData>>({})

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
    if (!currentFormData.jobType || !currentFormData.streamProperties) {
      toast.error('Bitte füllen Sie zuerst alle erforderlichen Formulardaten aus')
      return
    }

    setIsGenerating(true)
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate processing
      
      const result = generateStreamworksXML(currentFormData)
      
      if (result.success && result.xmlContent) {
        const validation = validateXML(result.xmlContent)
        handleXMLGenerated(result.xmlContent, validation)
        toast.success('XML wurde erfolgreich neu generiert!')
      } else {
        toast.error(`Fehler bei der XML-Generierung: ${result.error}`)
      }
    } catch (error) {
      toast.error('Unerwarteter Fehler bei der XML-Generierung')
    } finally {
      setIsGenerating(false)
    }
  }, [currentFormData, handleXMLGenerated])

  const handleFormDataChange = useCallback((data: Partial<WizardFormData>) => {
    setCurrentFormData(prev => ({ ...prev, ...data }))
  }, [])

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
    setCurrentFormData({})
    setViewMode('split')
    toast.info('Generator wurde zurückgesetzt')
  }

  return (
    <div className={`flex flex-col h-full bg-gray-50 dark:bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Wand2 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                XML Generator
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Erstellen Sie Streamworks-XML durch einen geführten Wizard
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRegenerate}
              disabled={isGenerating || !currentFormData.jobType}
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
      <div className="flex-1 overflow-hidden">
        {viewMode === 'xml-only' ? (
          // XML Only View
          <div className="h-full p-6">
            <XmlDisplay
              xmlContent={xmlContent}
              isGenerating={isGenerating}
              validationResults={validationResults}
              className="h-full"
            />
          </div>
        ) : viewMode === 'wizard-only' ? (
          // Wizard Only View
          <div className="h-full bg-white dark:bg-gray-800">
            <WizardForm
              onXMLGenerated={handleXMLGenerated}
              className="h-full"
            />
          </div>
        ) : (
          // Split Panel Layout
          <PanelGroup direction="horizontal" className="h-full">
            {/* Left Panel - Wizard Form */}
            <Panel defaultSize={50} minSize={30}>
              <div className="h-full bg-white dark:bg-gray-800">
                <WizardForm
                  onXMLGenerated={handleXMLGenerated}
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
                  className="h-full"
                />
              </div>
            </Panel>
          </PanelGroup>
        )}
      </div>

      {/* Help/Info Footer */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-3">
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