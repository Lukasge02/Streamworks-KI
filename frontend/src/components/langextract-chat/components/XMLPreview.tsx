/**
 * XML Preview Component for LangExtract
 * Shows generated XML with syntax highlighting and copy functionality
 */

'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileCode,
  Copy,
  Download,
  Eye,
  EyeOff,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Code,
  Maximize2,
  Minimize2
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

// ================================
// TYPES
// ================================

interface XMLPreviewProps {
  sessionId: string | null
  streamParameters: Record<string, any>
  jobParameters: Record<string, any>
  onGenerateXML?: () => Promise<any>
  xmlContent?: string
  isGenerating?: boolean
  completionPercentage?: number
  criticalMissing?: string[]
  onRegenerate?: () => void
  onDownload?: () => void
  className?: string
}

// ================================
// COMPONENT
// ================================

export default function XMLPreview({
  sessionId,
  streamParameters,
  jobParameters,
  onGenerateXML,
  xmlContent = '',
  isGenerating = false,
  completionPercentage = 0,
  criticalMissing = [],
  onRegenerate,
  onDownload,
  className = ''
}: XMLPreviewProps) {

  const [isExpanded, setIsExpanded] = useState(false)
  const [showLineNumbers, setShowLineNumbers] = useState(true)
  const [xmlLines, setXmlLines] = useState<string[]>([])
  const [localXmlContent, setLocalXmlContent] = useState('')
  const [localIsGenerating, setLocalIsGenerating] = useState(false)

  useEffect(() => {
    if (xmlContent) {
      setLocalXmlContent(xmlContent)
      setXmlLines(xmlContent.split('\n'))
    }
  }, [xmlContent])

  // Calculate completion percentage from parameters
  const allParameters = { ...streamParameters, ...jobParameters }
  const parameterCount = Object.keys(allParameters).length
  const localCompletionPercentage = completionPercentage || (parameterCount > 0 ? Math.min(parameterCount * 10, 100) : 0)

  const handleCopyXML = async () => {
    if (!localXmlContent) return

    try {
      await navigator.clipboard.writeText(localXmlContent)
      console.log('XML copied to clipboard')
    } catch (error) {
      console.error('Failed to copy XML:', error)
    }
  }

  const handleGenerateXML = async () => {
    if (!onGenerateXML || !sessionId) return

    try {
      setLocalIsGenerating(true)
      const result = await onGenerateXML()
      if (result?.xml_content) {
        setLocalXmlContent(result.xml_content)
        setXmlLines(result.xml_content.split('\n'))
        console.log('XML generated successfully')
      }
    } catch (error) {
      console.error('XML generation failed:', error)
      console.error('Generate XML error:', error)
    } finally {
      setLocalIsGenerating(false)
    }
  }

  const handleDownloadXML = () => {
    if (!localXmlContent) return

    try {
      const blob = new Blob([localXmlContent], { type: 'application/xml' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `stream-configuration-${Date.now()}.xml`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      console.log('XML file downloaded')
    } catch (error) {
      console.error('Download failed:', error)
    }

    onDownload?.()
  }

  const canGenerate = localCompletionPercentage >= 60 && criticalMissing.length === 0
  const displayIsGenerating = isGenerating || localIsGenerating

  // Simple XML syntax highlighting
  const highlightXML = (line: string, lineNumber: number) => {
    let highlighted = line

    // XML tags
    highlighted = highlighted.replace(
      /(<\/?)([a-zA-Z][a-zA-Z0-9-]*)(.*?)(\/?>)/g,
      '<span class="text-blue-600">$1</span><span class="text-primary-600 font-semibold">$2</span><span class="text-blue-600">$3$4</span>'
    )

    // Attributes
    highlighted = highlighted.replace(
      /(\s+)([a-zA-Z][a-zA-Z0-9-]*)(=)(".*?")/g,
      '$1<span class="text-emerald-600">$2</span><span class="text-gray-400">$3</span><span class="text-yellow-600">$4</span>'
    )

    // Values between tags
    highlighted = highlighted.replace(
      />([^<]+)</g,
      '><span class="text-gray-800">$1</span><'
    )

    // Comments
    highlighted = highlighted.replace(
      /(<!--.*?-->)/g,
      '<span class="text-gray-500 italic">$1</span>'
    )

    return highlighted
  }

  return (
    <motion.div
      className={`bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="bg-gray-50 border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <FileCode className="w-4 h-4 text-primary-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">XML Vorschau</h3>
              <p className="text-sm text-gray-600">
                Generierte Streamworks-Konfiguration
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Status Badge */}
            {localXmlContent ? (
              <Badge variant="default" className="text-xs">
                <CheckCircle className="w-3 h-3 mr-1" />
                Generiert
              </Badge>
            ) : canGenerate ? (
              <Badge variant="secondary" className="text-xs">
                Bereit zur Generierung
              </Badge>
            ) : (
              <Badge variant="outline" className="text-xs">
                <AlertTriangle className="w-3 h-3 mr-1" />
                Nicht bereit
              </Badge>
            )}

            {/* Generate Button */}
            {!localXmlContent && canGenerate && onGenerateXML && (
              <Button
                variant="default"
                size="sm"
                onClick={handleGenerateXML}
                disabled={displayIsGenerating}
                className="h-8"
              >
                {displayIsGenerating ? (
                  <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Code className="w-4 h-4 mr-2" />
                )}
                {displayIsGenerating ? 'Generiere...' : 'XML generieren'}
              </Button>
            )}

            {/* Controls */}
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowLineNumbers(!showLineNumbers)}
                className="h-8 w-8 p-0"
                title={showLineNumbers ? "Zeilennummern ausblenden" : "Zeilennummern anzeigen"}
              >
                {showLineNumbers ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="h-8 w-8 p-0"
                title={isExpanded ? "Minimieren" : "Maximieren"}
              >
                {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </Button>

              {localXmlContent && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleCopyXML}
                    className="h-8 w-8 p-0"
                    title="XML kopieren"
                  >
                    <Copy className="w-4 h-4" />
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleDownloadXML}
                    className="h-8 w-8 p-0"
                    title="XML herunterladen"
                  >
                    <Download className="w-4 h-4" />
                  </Button>
                </>
              )}

              {(onRegenerate || onGenerateXML) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onRegenerate || handleGenerateXML}
                  disabled={displayIsGenerating || !canGenerate}
                  className="h-8 w-8 p-0"
                  title="XML neu generieren"
                >
                  <RefreshCw className={`w-4 h-4 ${displayIsGenerating ? 'animate-spin' : ''}`} />
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Generation Status */}
        {!canGenerate && (
          <motion.div
            className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
          >
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-yellow-800 font-medium mb-1">
                  XML-Generierung nicht möglich
                </p>
                <ul className="text-yellow-700 text-xs space-y-0.5">
                  {localCompletionPercentage < 60 && (
                    <li>• Weitere Parameter erforderlich</li>
                  )}
                  {criticalMissing.length > 0 && (
                    <li>• {criticalMissing.length} kritische Parameter fehlen</li>
                  )}
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Content */}
      <div className={`${isExpanded ? 'h-96' : 'h-64'} transition-all duration-300`}>
        <AnimatePresence mode="wait">
          {displayIsGenerating ? (
            <motion.div
              key="generating"
              className="h-full flex items-center justify-center bg-gray-50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="text-center">
                <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
                <p className="text-gray-600 font-medium">XML wird generiert...</p>
                <p className="text-gray-500 text-sm mt-1">Dies kann einen Moment dauern</p>
              </div>
            </motion.div>
          ) : localXmlContent ? (
            <motion.div
              key="content"
              className="h-full overflow-auto bg-gray-900 text-gray-100 font-mono text-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="p-4">
                {xmlLines.map((line, index) => (
                  <div
                    key={index}
                    className="flex hover:bg-gray-800 transition-colors"
                  >
                    {showLineNumbers && (
                      <span className="text-gray-500 select-none w-12 flex-shrink-0 text-right pr-3">
                        {index + 1}
                      </span>
                    )}
                    <span
                      className="flex-1"
                      dangerouslySetInnerHTML={{
                        __html: highlightXML(line, index + 1) || '&nbsp;'
                      }}
                    />
                  </div>
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              className="h-full flex items-center justify-center bg-gray-50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="text-center">
                <Code className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 font-medium mb-2">Noch kein XML generiert</p>
                <p className="text-gray-400 text-sm">
                  {canGenerate
                    ? 'Klicken Sie auf "XML generieren" um zu beginnen'
                    : 'Parameter vervollständigen für XML-Generierung'
                  }
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer with Stats */}
      {localXmlContent && (
        <div className="bg-gray-50 border-t border-gray-200 px-4 py-2">
          <div className="flex justify-between items-center text-xs text-gray-600">
            <span>{xmlLines.length} Zeilen</span>
            <span>{new Blob([localXmlContent]).size} Bytes</span>
            <span>XML Format</span>
          </div>
        </div>
      )}
    </motion.div>
  )
}