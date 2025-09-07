/**
 * Error Handler - Professional error display with German messages
 * Comprehensive error handling with actionable solutions
 */

import React, { useState } from 'react'
import { 
  ExclamationTriangleIcon, 
  XMarkIcon,
  InformationCircleIcon,
  ArrowPathIcon,
  DocumentIcon
} from '@heroicons/react/24/outline'
import { cn } from '@/lib/utils'

interface FileRejection {
  readonly file: File
  readonly errors: ReadonlyArray<{
    code: string
    message: string
  }>
}

interface ErrorHandlerProps {
  fileRejections?: readonly FileRejection[]
  onDismiss?: () => void
  onRetry?: (file: File) => void
  className?: string
}

export function ErrorHandler({ fileRejections = [], onDismiss, onRetry, className }: ErrorHandlerProps) {
  const [expandedErrors, setExpandedErrors] = useState<Set<string>>(new Set())

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getErrorTranslation = (errorCode: string) => {
    const translations: Record<string, { title: string; description: string; solution: string }> = {
      'file-too-large': {
        title: 'Datei zu groß',
        description: 'Die Datei überschreitet die maximale Größe von 100 MB',
        solution: 'Komprimieren Sie die Datei oder teilen Sie sie in kleinere Teile auf'
      },
      'file-too-small': {
        title: 'Datei zu klein',
        description: 'Die Datei ist kleiner als die Mindestgröße',
        solution: 'Stellen Sie sicher, dass die Datei gültigen Inhalt enthält'
      },
      'too-many-files': {
        title: 'Zu viele Dateien',
        description: 'Sie können maximal 10 Dateien gleichzeitig hochladen',
        solution: 'Laden Sie die Dateien in kleineren Gruppen hoch'
      },
      'file-invalid-type': {
        title: 'Ungültiger Dateityp',
        description: 'Dieser Dateityp wird nicht unterstützt',
        solution: 'Verwenden Sie PDF, DOC, DOCX, TXT, MD, CSV, JSON, XML, HTML, JPG, PNG oder GIF'
      },
      'file-not-supported': {
        title: 'Dateityp nicht unterstützt',
        description: 'Dieser spezielle Dateityp kann nicht verarbeitet werden',
        solution: 'Konvertieren Sie die Datei in ein unterstütztes Format'
      },
      'upload-failed': {
        title: 'Upload fehlgeschlagen',
        description: 'Die Datei konnte nicht hochgeladen werden',
        solution: 'Überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut'
      },
      'network-error': {
        title: 'Netzwerkfehler',
        description: 'Die Verbindung zum Server wurde unterbrochen',
        solution: 'Überprüfen Sie Ihre Internetverbindung und laden Sie die Seite neu'
      },
      'server-error': {
        title: 'Serverfehler',
        description: 'Ein Fehler auf dem Server verhinderte den Upload',
        solution: 'Versuchen Sie es in ein paar Minuten erneut oder kontaktieren Sie den Support'
      },
      'quota-exceeded': {
        title: 'Speicherplatz überschritten',
        description: 'Nicht genügend Speicherplatz verfügbar',
        solution: 'Löschen Sie andere Dateien oder erweitern Sie Ihren Speicherplan'
      },
      'permission-denied': {
        title: 'Berechtigung verweigert',
        description: 'Sie haben keine Berechtigung, Dateien in diesen Ordner hochzuladen',
        solution: 'Wenden Sie sich an einen Administrator für die erforderlichen Berechtigungen'
      }
    }

    return translations[errorCode] || {
      title: 'Unbekannter Fehler',
      description: 'Ein unerwarteter Fehler ist aufgetreten',
      solution: 'Versuchen Sie es erneut oder kontaktieren Sie den Support'
    }
  }

  const getFileTypeIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase()
    return DocumentIcon // Simplified for this component
  }

  const toggleErrorExpansion = (filename: string) => {
    setExpandedErrors(prev => {
      const newSet = new Set(prev)
      if (newSet.has(filename)) {
        newSet.delete(filename)
      } else {
        newSet.add(filename)
      }
      return newSet
    })
  }

  const getErrorSeverity = (errorCode: string) => {
    const highSeverity = ['server-error', 'network-error', 'quota-exceeded', 'permission-denied']
    const mediumSeverity = ['file-too-large', 'too-many-files']
    
    if (highSeverity.includes(errorCode)) return 'high'
    if (mediumSeverity.includes(errorCode)) return 'medium'
    return 'low'
  }

  // Safety check: Return null if no file rejections
  if (!fileRejections || fileRejections.length === 0) return null

  const errorCounts = fileRejections.reduce((acc, rejection) => {
    rejection.errors.forEach(error => {
      acc[error.code] = (acc[error.code] || 0) + 1
    })
    return acc
  }, {} as Record<string, number>)

  const uniqueErrors = Object.keys(errorCounts)
  const totalFiles = fileRejections.length
  const hasHighSeverityErrors = uniqueErrors.some(code => getErrorSeverity(code) === 'high')

  return (
    <div className={cn(
      "animate-in slide-in-from-top-2 fade-in duration-300",
      className
    )}>
      <div className={cn(
        "rounded-xl border-2 p-6 backdrop-blur-sm",
        hasHighSeverityErrors 
          ? "bg-gradient-to-br from-red-50 via-rose-50 to-red-100/50 border-red-300/70"
          : "bg-gradient-to-br from-orange-50 via-yellow-50 to-orange-100/50 border-orange-300/70"
      )}>
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={cn(
              "p-2 rounded-full",
              hasHighSeverityErrors ? "bg-red-100 text-red-600" : "bg-orange-100 text-orange-600"
            )}>
              <ExclamationTriangleIcon className="w-5 h-5" />
            </div>
            <div>
              <h4 className={cn(
                "text-sm font-semibold",
                hasHighSeverityErrors ? "text-red-800" : "text-orange-800"
              )}>
                {totalFiles === 1 ? 'Datei konnte nicht hochgeladen werden' : `${totalFiles} Dateien konnten nicht hochgeladen werden`}
              </h4>
              <p className="text-xs text-gray-600 mt-1">
                {uniqueErrors.length === 1 ? '1 Problem gefunden' : `${uniqueErrors.length} verschiedene Probleme gefunden`}
              </p>
            </div>
          </div>
          
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Error Summary */}
        <div className="mb-4">
          <div className="grid gap-2">
            {uniqueErrors.map(errorCode => {
              const errorInfo = getErrorTranslation(errorCode)
              const count = errorCounts[errorCode]
              const severity = getErrorSeverity(errorCode)
              
              return (
                <div
                  key={errorCode}
                  className={cn(
                    "flex items-center justify-between p-3 rounded-lg border",
                    severity === 'high' && "bg-red-50/50 border-red-200/70 text-red-800",
                    severity === 'medium' && "bg-orange-50/50 border-orange-200/70 text-orange-800",
                    severity === 'low' && "bg-yellow-50/50 border-yellow-200/70 text-yellow-800"
                  )}
                >
                  <div className="flex items-center space-x-3">
                    <InformationCircleIcon className="w-4 h-4 flex-shrink-0" />
                    <div>
                      <div className="text-sm font-medium">{errorInfo.title}</div>
                      <div className="text-xs opacity-80">{errorInfo.description}</div>
                    </div>
                  </div>
                  <div className="text-xs font-medium bg-white/50 px-2 py-1 rounded-full">
                    {count} Datei{count !== 1 ? 'en' : ''}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Individual File Errors */}
        <div className="space-y-3">
          <div className="text-xs font-medium text-gray-700 uppercase tracking-wide">
            Betroffene Dateien:
          </div>
          
          {fileRejections.map((rejection, index) => {
            const FileIcon = getFileTypeIcon(rejection.file.name)
            const primaryError = rejection.errors[0]
            const errorInfo = getErrorTranslation(primaryError.code)
            const isExpanded = expandedErrors.has(rejection.file.name)
            const severity = getErrorSeverity(primaryError.code)
            
            return (
              <div
                key={`${rejection.file.name}-${index}`}
                className={cn(
                  "rounded-lg border transition-all duration-200",
                  severity === 'high' && "bg-red-50/30 border-red-200/50",
                  severity === 'medium' && "bg-orange-50/30 border-orange-200/50",
                  severity === 'low' && "bg-yellow-50/30 border-yellow-200/50"
                )}
              >
                <div 
                  className="p-4 cursor-pointer hover:bg-white/50 transition-colors"
                  onClick={() => toggleErrorExpansion(rejection.file.name)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <FileIcon className="w-5 h-5 text-gray-500 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-medium text-gray-900 truncate">
                          {rejection.file.name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {formatFileSize(rejection.file.size)} • {errorInfo.title}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {onRetry && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            onRetry(rejection.file)
                          }}
                          className={cn(
                            "px-3 py-1 text-xs font-medium rounded-lg transition-colors",
                            "bg-white hover:bg-gray-50 border border-gray-300 text-gray-700"
                          )}
                        >
                          <ArrowPathIcon className="w-3 h-3 mr-1 inline" />
                          Wiederholen
                        </button>
                      )}
                      
                      <div className={cn(
                        "text-xs font-medium px-2 py-1 rounded-full",
                        severity === 'high' && "bg-red-100 text-red-700",
                        severity === 'medium' && "bg-orange-100 text-orange-700",
                        severity === 'low' && "bg-yellow-100 text-yellow-700"
                      )}>
                        {rejection.errors.length} Fehler
                      </div>
                    </div>
                  </div>
                  
                  {/* Expanded Error Details */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-gray-200/50 space-y-3">
                      {rejection.errors.map((error, errorIndex) => {
                        const errorDetails = getErrorTranslation(error.code)
                        return (
                          <div key={errorIndex} className="bg-white/60 rounded-lg p-3">
                            <div className="text-sm font-medium text-gray-900 mb-2">
                              {errorDetails.title}
                            </div>
                            <div className="text-xs text-gray-600 mb-2">
                              {errorDetails.description}
                            </div>
                            <div className="text-xs text-blue-600 bg-blue-50 rounded-lg p-2 border border-blue-200/50">
                              <strong>Lösung:</strong> {errorDetails.solution}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200/50">
          <div className="text-xs text-gray-500">
            Probleme beheben und erneut versuchen
          </div>
          
          <div className="flex items-center space-x-2">
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="px-3 py-1.5 text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-300 rounded-lg transition-colors"
              >
                Schließen
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}