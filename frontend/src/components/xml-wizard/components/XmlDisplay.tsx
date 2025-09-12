/**
 * XmlDisplay Component
 * Live XML preview with Monaco Editor and progress indicators
 */
'use client'

import React, { useEffect, useRef, useState } from 'react'
import { Editor } from '@monaco-editor/react'
import { Copy, Download, CheckCircle, AlertCircle, Eye, Code2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { toast } from 'sonner'
import XMLHighlighter from './XMLHighlighter'
import { XMLPreviewHook } from '../hooks/useXMLPreview'

interface XmlDisplayProps {
  xmlContent: string
  isGenerating?: boolean
  validationResults?: {
    isValid: boolean
    errors: string[]
  }
  previewHook?: XMLPreviewHook // Optional live preview data
  className?: string
}

export const XmlDisplay: React.FC<XmlDisplayProps> = ({
  xmlContent,
  isGenerating = false,
  validationResults,
  previewHook,
  className = ''
}) => {
  const editorRef = useRef<any>(null)
  const [viewMode, setViewMode] = useState<'editor' | 'highlighted'>('editor')

  // Auto-format XML when content changes
  useEffect(() => {
    if (editorRef.current && xmlContent) {
      setTimeout(() => {
        editorRef.current?.getAction('editor.action.formatDocument')?.run()
      }, 100)
    }
  }, [xmlContent])

  const handleCopyXML = async () => {
    if (!xmlContent) {
      toast.error('Keine XML-Daten zum Kopieren verfügbar')
      return
    }

    try {
      await navigator.clipboard.writeText(xmlContent)
      toast.success('XML in Zwischenablage kopiert')
    } catch (error) {
      toast.error('Fehler beim Kopieren der XML')
    }
  }

  const handleDownloadXML = () => {
    if (!xmlContent) {
      toast.error('Keine XML-Daten zum Herunterladen verfügbar')
      return
    }

    try {
      const blob = new Blob([xmlContent], { type: 'application/xml' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `streamworks-${new Date().toISOString().split('T')[0]}.xml`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      toast.success('XML-Datei heruntergeladen')
    } catch (error) {
      toast.error('Fehler beim Herunterladen der XML')
    }
  }

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor
    
    // Configure editor
    editor.updateOptions({
      readOnly: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      automaticLayout: true
    })
  }

  const getValidationIcon = () => {
    if (!validationResults) return null
    
    if (validationResults.isValid) {
      return <CheckCircle className="w-4 h-4 text-green-500" />
    } else {
      return <AlertCircle className="w-4 h-4 text-red-500" />
    }
  }

  const getValidationMessage = () => {
    if (!validationResults) return null
    
    if (validationResults.isValid) {
      return 'XML ist gültig'
    } else {
      return `${validationResults.errors.length} Validierungsfehler gefunden`
    }
  }

  // Use preview data if available, otherwise fall back to props
  const displayXml = previewHook?.xmlContent || xmlContent
  const displayIsGenerating = previewHook?.isGenerating || isGenerating
  const displayError = previewHook?.error

  return (
    <div className={`flex flex-col h-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg ${className}`}>

      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {previewHook ? 'Live XML Preview' : 'Generated XML'}
          </h3>
          
          {validationResults && (
            <div className="flex items-center space-x-2">
              {getValidationIcon()}
              <span className={`text-sm ${
                validationResults.isValid 
                  ? 'text-green-600 dark:text-green-400' 
                  : 'text-red-600 dark:text-red-400'
              }`}>
                {getValidationMessage()}
              </span>
            </div>
          )}

          {displayError && (
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-500" />
              <span className="text-sm text-red-600 dark:text-red-400">
                Fehler bei Preview
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {/* View Mode Toggle */}
          {previewHook && previewHook.hasPlaceholders && (
            <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as any)}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="editor" className="flex items-center space-x-1">
                  <Code2 className="w-3 h-3" />
                  <span>Editor</span>
                </TabsTrigger>
                <TabsTrigger value="highlighted" className="flex items-center space-x-1">
                  <Eye className="w-3 h-3" />
                  <span>Preview</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={handleCopyXML}
            disabled={displayIsGenerating || !displayXml}
            className="flex items-center space-x-2"
          >
            <Copy className="w-4 h-4" />
            <span>Kopieren</span>
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadXML}
            disabled={displayIsGenerating || !displayXml}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download</span>
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 relative">
        {displayIsGenerating && (
          <div className="absolute inset-0 bg-white dark:bg-gray-800 bg-opacity-75 dark:bg-opacity-75 flex items-center justify-center z-10">
            <div className="flex flex-col items-center space-y-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {previewHook ? 'Preview wird generiert...' : 'XML wird generiert...'}
              </span>
            </div>
          </div>
        )}

        {displayXml ? (
          <div className="h-full">
            {/* Monaco Editor View */}
            {viewMode === 'editor' ? (
              <Editor
                height="100%"
                language="xml"
                theme="vs-light"
                value={displayXml}
                onMount={handleEditorDidMount}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  automaticLayout: true,
                  fontSize: 14,
                  lineHeight: 20,
                  padding: { top: 16, bottom: 16 },
                  scrollbar: {
                    vertical: 'visible',
                    horizontal: 'visible',
                    verticalScrollbarSize: 10,
                    horizontalScrollbarSize: 10
                  },
                  bracketPairColorization: {
                    enabled: true
                  },
                  folding: true,
                  showFoldingControls: 'always'
                }}
              />
            ) : (
              /* Custom Highlighted View */
              <div className="h-full overflow-auto p-4">
                <XMLHighlighter
                  xmlContent={displayXml}
                  highlightPlaceholders={true}
                  showLineNumbers={true}
                />
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {previewHook ? 'Live Preview startet...' : 'Noch keine XML generiert'}
              </h4>
              <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
                {previewHook 
                  ? 'Füllen Sie den Wizard aus, um sofort eine Live-Vorschau zu sehen.' 
                  : 'Füllen Sie das Formular links aus, um automatisch eine gültige Streamworks-XML zu generieren.'}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Validation Errors */}
      {validationResults && !validationResults.isValid && validationResults.errors.length > 0 && (
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <h4 className="text-sm font-semibold text-red-600 dark:text-red-400 mb-2 flex items-center">
            <AlertCircle className="w-4 h-4 mr-2" />
            Validierungsfehler
          </h4>
          <div className="space-y-1">
            {validationResults.errors.slice(0, 5).map((error, index) => (
              <p key={index} className="text-xs text-red-600 dark:text-red-400">
                • {error}
              </p>
            ))}
            {validationResults.errors.length > 5 && (
              <p className="text-xs text-red-500 dark:text-red-400">
                ... und {validationResults.errors.length - 5} weitere Fehler
              </p>
            )}
          </div>
        </div>
      )}
      
      {/* Footer Info */}
      <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>
            {displayXml ? `${displayXml.split('\n').length} Zeilen` : 'Keine Daten'}
          </span>
          <span>
            Format: XML (UTF-8)
          </span>
        </div>
      </div>
    </div>
  )
}

export default XmlDisplay