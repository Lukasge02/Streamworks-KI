/**
 * Professional Status Bar Component
 * Sleek file upload progress indicator with modern design
 */

import { useState, useEffect } from 'react'
import { XMarkIcon, CheckCircleIcon, ExclamationCircleIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import { cn } from '@/lib/utils'
import { t, formatFileSize } from '@/lib/translations'

export interface UploadProgress {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
  id?: string
}

interface StatusBarProps {
  uploads: UploadProgress[]
  onRemoveUpload: (index: number) => void
  onClearAll: () => void
  className?: string
}

interface StatusBarItemProps {
  upload: UploadProgress
  index: number
  onRemove: (index: number) => void
}

function StatusBarItem({ upload, index, onRemove }: StatusBarItemProps) {
  const [isRemoving, setIsRemoving] = useState(false)

  const handleRemove = () => {
    setIsRemoving(true)
    setTimeout(() => onRemove(index), 150)
  }

  const getStatusIcon = () => {
    switch (upload.status) {
      case 'completed':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />
      case 'error':
        return <ExclamationCircleIcon className="w-4 h-4 text-red-500" />
      case 'uploading':
        return <ArrowPathIcon className="w-4 h-4 text-blue-500 animate-spin" />
      default:
        return <div className="w-4 h-4 bg-gray-300 rounded-full" />
    }
  }

  const getStatusText = () => {
    switch (upload.status) {
      case 'completed':
        return t('upload.completed')
      case 'error':
        return t('upload.failed')
      case 'uploading':
        return `${upload.progress}%`
      default:
        return t('upload.pending')
    }
  }

  return (
    <div
      className={cn(
        "bg-white border border-gray-200 rounded-lg shadow-sm",
        "transform transition-all duration-200 ease-out",
        isRemoving
          ? "scale-95 opacity-0 translate-x-4"
          : "scale-100 opacity-100 translate-x-0"
      )}
    >
      <div className="p-4">
        {/* File Info */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {upload.file.name}
            </p>
            <p className="text-xs text-gray-500">
              {formatFileSize(upload.file.size)}
            </p>
          </div>
          
          <div className="flex items-center ml-3">
            <div className="flex items-center space-x-2">
              {getStatusIcon()}
              <span
                className={cn(
                  "text-xs font-medium",
                  upload.status === 'completed' && "text-green-600",
                  upload.status === 'error' && "text-red-600",
                  upload.status === 'uploading' && "text-blue-600",
                  upload.status === 'pending' && "text-gray-600"
                )}
              >
                {getStatusText()}
              </span>
            </div>
            
            <button
              onClick={handleRemove}
              className="ml-3 p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
              aria-label={t('a11y.removeFromQueue')}
            >
              <XMarkIcon className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        {upload.status === 'uploading' && (
          <div className="mb-2">
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300 ease-out rounded-full"
                style={{ width: `${Math.min(upload.progress, 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Message */}
        {upload.status === 'error' && upload.error && (
          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
            {upload.error}
          </div>
        )}
      </div>
    </div>
  )
}

export function StatusBar({ uploads, onRemoveUpload, onClearAll, className }: StatusBarProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [isExpanded, setIsExpanded] = useState(true)

  useEffect(() => {
    setIsVisible(uploads.length > 0)
  }, [uploads.length])

  if (!isVisible || uploads.length === 0) return null

  const completedCount = uploads.filter(u => u.status === 'completed').length
  const errorCount = uploads.filter(u => u.status === 'error').length
  const uploadingCount = uploads.filter(u => u.status === 'uploading').length
  const pendingCount = uploads.filter(u => u.status === 'pending').length

  const totalProgress = uploads.reduce((acc, upload) => {
    if (upload.status === 'completed') return acc + 100
    if (upload.status === 'uploading') return acc + upload.progress
    return acc
  }, 0) / uploads.length

  return (
    <div
      className={cn(
        "fixed bottom-6 right-6 z-40 max-w-sm w-full",
        "transform transition-all duration-300 ease-out",
        isVisible
          ? "translate-y-0 opacity-100"
          : "translate-y-4 opacity-0 pointer-events-none",
        className
      )}
    >
      {/* Summary Header */}
      <div className="bg-white border border-gray-200 rounded-t-lg shadow-lg">
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <h3 className="text-sm font-semibold text-gray-900">
                {t('upload.uploadProgress', { count: uploads.length })}
              </h3>
              {uploadingCount > 0 && (
                <div className="ml-2 w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors text-xs"
              >
                {isExpanded ? 'Minimieren' : 'Erweitern'}
              </button>
              <button
                onClick={onClearAll}
                className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                aria-label={t('general.close')}
              >
                <XMarkIcon className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Overall Progress */}
          <div className="mb-3">
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Gesamt-Fortschritt</span>
              <span>{Math.round(totalProgress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500 ease-out rounded-full"
                style={{ width: `${totalProgress}%` }}
              />
            </div>
          </div>

          {/* Status Summary */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-4">
              {completedCount > 0 && (
                <span className="flex items-center text-green-600">
                  <CheckCircleIcon className="w-3 h-3 mr-1" />
                  {completedCount}
                </span>
              )}
              {uploadingCount > 0 && (
                <span className="flex items-center text-blue-600">
                  <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin" />
                  {uploadingCount}
                </span>
              )}
              {errorCount > 0 && (
                <span className="flex items-center text-red-600">
                  <ExclamationCircleIcon className="w-3 h-3 mr-1" />
                  {errorCount}
                </span>
              )}
              {pendingCount > 0 && (
                <span className="flex items-center text-gray-600">
                  <div className="w-3 h-3 bg-gray-300 rounded-full mr-1" />
                  {pendingCount}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Upload Items */}
      {isExpanded && (
        <div className="max-h-80 overflow-y-auto bg-gray-50 border-x border-gray-200">
          <div className="p-2 space-y-2">
            {uploads.map((upload, index) => (
              <StatusBarItem
                key={`${upload.file.name}-${index}`}
                upload={upload}
                index={index}
                onRemove={onRemoveUpload}
              />
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="bg-gray-50 border border-t-0 border-gray-200 rounded-b-lg p-2">
        <button
          onClick={onClearAll}
          className="w-full text-xs text-gray-600 hover:text-gray-800 py-1 hover:bg-gray-100 rounded transition-colors"
        >
          Alle entfernen
        </button>
      </div>
    </div>
  )
}