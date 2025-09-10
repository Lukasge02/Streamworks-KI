'use client'

import { useState, useEffect } from 'react'
import { ArrowDownTrayIcon, DocumentTextIcon } from '@heroicons/react/24/outline'

interface ModernPDFViewerProps {
  documentId: string
  fileName: string
}

export function ModernPDFViewer({ documentId, fileName }: ModernPDFViewerProps) {
  const [showFallback, setShowFallback] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadSuccess, setLoadSuccess] = useState(false)
  
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  const pdfUrl = `${backendUrl}/api/v1/documents/${documentId}/pdf`
  const downloadUrl = `${backendUrl}/api/v1/documents/${documentId}/download`

  useEffect(() => {
    // Shorter timeout for better UX
    const timer = setTimeout(() => {
      if (!loadSuccess && loading) {
        console.log('PDF loading timeout after 5 seconds')
        setShowFallback(true)
        setLoading(false)
      }
    }, 5000) // 5 Sekunden

    return () => clearTimeout(timer)
  }, [loading, loadSuccess])

  const handleObjectLoad = () => {
    console.log('PDF object loaded successfully')
    setLoading(false)
    setLoadSuccess(true)
  }

  const handleObjectError = () => {
    console.log('PDF object failed, trying iframe fallback')
    // Nicht sofort fallback - iframe könnte noch funktionieren
  }

  const handleIframeLoad = () => {
    console.log('PDF iframe loaded successfully')
    setLoading(false)
    setLoadSuccess(true)
  }

  const handleIframeError = () => {
    console.log('PDF iframe also failed - showing fallback')
    setLoading(false)
    setShowFallback(true)
  }

  if (showFallback) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center p-6 max-w-md">
          <DocumentTextIcon className="w-20 h-20 mx-auto mb-6 text-gray-400" />
          
          <h4 className="text-xl font-medium text-gray-900 dark:text-gray-100 mb-2">
            PDF-Vorschau nicht verfügbar
          </h4>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            {fileName}
          </p>
          
          <button 
            onClick={() => window.open(downloadUrl, '_blank')}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            PDF herunterladen
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full relative bg-gray-50 dark:bg-gray-900">
      
      <object
        data={pdfUrl}
        type="application/pdf"
        className="w-full h-full"
        title={`PDF: ${fileName}`}
        onLoad={handleObjectLoad}
        onError={handleObjectError}
      >
        {/* Fallback zu iframe wenn object nicht funktioniert */}
        <iframe
          src={pdfUrl}
          className="w-full h-full border-0"
          title={`PDF Fallback: ${fileName}`}
          onLoad={handleIframeLoad}
          onError={handleIframeError}
        />
        {/* Fallback Text falls beide nicht funktionieren */}
        <p className="p-4 text-center text-gray-600 dark:text-gray-400">
          PDF kann nicht angezeigt werden.{' '}
          <a 
            href={downloadUrl} 
            className="text-blue-600 hover:text-blue-700 underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            Hier herunterladen
          </a>
        </p>
      </object>
    </div>
  )
}