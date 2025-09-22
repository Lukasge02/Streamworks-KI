/**
 * XML Preview Component
 * Side panel for viewing and managing generated XML
 */

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X,
  Download,
  Copy,
  Check,
  CheckCircle,
  AlertTriangle,
  Code2,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  FileText
} from 'lucide-react'
import { toast } from 'sonner'

import { XMLPreviewProps } from '../types'

export default function XMLPreview({
  xml,
  status,
  onClose,
  onDownload,
  onCopy
}: XMLPreviewProps) {
  const [copied, setCopied] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [showFormatted, setShowFormatted] = useState(true)

  // Format XML for display
  const formatXML = (xmlString: string) => {
    try {
      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(xmlString, 'application/xml')
      const serializer = new XMLSerializer()
      const formatted = serializer.serializeToString(xmlDoc)

      // Add indentation (simple version)
      return formatted
        .replace(/></g, '>\n<')
        .split('\n')
        .map((line, index) => {
          const depth = (line.match(/</g) || []).length - (line.match(/\//g) || []).length
          return '  '.repeat(Math.max(0, depth)) + line.trim()
        })
        .join('\n')
    } catch {
      return xmlString
    }
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(xml)
      setCopied(true)
      toast.success('XML copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
      onCopy?.()
    } catch (error) {
      toast.error('Failed to copy XML')
    }
  }

  const handleDownload = () => {
    try {
      const blob = new Blob([xml], { type: 'application/xml' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `job-config-${new Date().toISOString().split('T')[0]}.xml`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success('XML downloaded successfully')
      onDownload?.()
    } catch (error) {
      toast.error('Failed to download XML')
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'error':
        return <AlertTriangle className="w-5 h-5 text-red-600" />
      case 'generating':
        return <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      default:
        return <Code2 className="w-5 h-5 text-gray-600" />
    }
  }

  const displayXML = showFormatted ? formatXML(xml) : xml

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 20 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="h-full bg-white border-l border-gray-200 shadow-xl flex flex-col overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <div>
              <h2 className="font-semibold text-gray-900">Generated XML</h2>
              <p className="text-sm text-gray-500">
                {status === 'generating' ? 'Generating...' : 'Ready to use'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Expand/Collapse */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
              title={isExpanded ? 'Minimize' : 'Expand'}
            >
              {isExpanded ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </button>

            {/* Close */}
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between p-4 bg-gray-50 border-b border-gray-200">
          {/* View Options */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFormatted(!showFormatted)}
              className={`
                flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg transition-colors
                ${showFormatted
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              {showFormatted ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
              {showFormatted ? 'Formatted' : 'Raw'}
            </button>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {/* Copy */}
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-green-600" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  Copy
                </>
              )}
            </button>

            {/* Download */}
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-3 h-3" />
              Download
            </button>
          </div>
        </div>

        {/* XML Content */}
        <div className="flex-1 overflow-hidden">
          {status === 'generating' ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <h3 className="font-medium text-gray-900 mb-2">Generating XML</h3>
                <p className="text-sm text-gray-500">
                  Processing your requirements...
                </p>
              </div>
            </div>
          ) : (
            <div className="h-full overflow-auto">
              <pre className={`
                p-4 text-sm font-mono leading-relaxed
                ${showFormatted ? 'text-gray-800' : 'text-gray-600'}
              `}>
                <code className="block whitespace-pre-wrap">
                  {displayXML}
                </code>
              </pre>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              <span>{xml.split('\n').length} lines</span>
              <span>•</span>
              <span>{(xml.length / 1024).toFixed(1)}KB</span>
            </div>
            <div>
              Generated {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}