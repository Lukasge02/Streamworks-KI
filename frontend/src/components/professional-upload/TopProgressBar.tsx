/**
 * Bottom Progress Bar - Fixed progress display at bottom of screen
 * Shows compact upload progress for all active uploads
 */

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { XMarkIcon, DocumentTextIcon, CloudArrowUpIcon, ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/outline'
import { cn } from '@/lib/utils'
// Upload file interface for progress tracking
export interface UploadFile {
  id: string
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'analyzing' | 'processing' | 'completed' | 'error'
  error?: string
  uploadedAt?: Date
}

interface BottomProgressBarProps {
  uploads: UploadFile[]
  onRemoveUpload: (id: string) => void
  onClearAll: () => void
  className?: string
}

export function BottomProgressBar({
  uploads,
  onRemoveUpload,
  onClearAll,
  className
}: BottomProgressBarProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Only show active uploads (not completed or error)
  const activeUploads = uploads.filter(upload =>
    ['pending', 'uploading', 'analyzing', 'processing'].includes(upload.status)
  )

  // Don't render if no active uploads
  if (activeUploads.length === 0) return null

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const overallProgress = activeUploads.length > 0 
    ? Math.round(activeUploads.reduce((sum, upload) => sum + upload.progress, 0) / activeUploads.length)
    : 0

  const getStatusColor = (status: UploadFile['status']) => {
    switch (status) {
      case 'uploading': return 'bg-blue-500'
      case 'analyzing': return 'bg-purple-500'
      case 'processing': return 'bg-orange-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'uploading': 
        return <CloudArrowUpIcon className="w-3 h-3 text-blue-500" />
      case 'analyzing':
        return <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse" />
      case 'processing':
        return <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse" />
      default:
        return <DocumentTextIcon className="w-3 h-3 text-gray-500" />
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
        className={cn(
          "fixed bottom-0 left-0 right-0 z-50",
          "bg-white/95 backdrop-blur-md border-t border-gray-200/50",
          "shadow-lg shadow-black/10",
          className
        )}
      >
        <div className="max-w-6xl mx-auto px-4 py-2">
          {/* Compact Progress Display */}
          <div className="flex items-center justify-between">
            {/* Left: Upload Info */}
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-gray-900">
                Upload läuft
              </span>
              <span className="text-xs text-gray-600">
                {activeUploads.length} Datei{activeUploads.length !== 1 ? 'en' : ''}
              </span>
            </div>

            {/* Center: File Progress (only show current file when collapsed) */}
            {activeUploads.length > 0 && !isExpanded && (
              <div className="flex items-center space-x-3 flex-1 max-w-md mx-6">
                <div className="flex items-center space-x-2 min-w-0 flex-1">
                  {getStatusIcon(activeUploads[0].status)}
                  <span className="text-xs text-gray-700 truncate">
                    {activeUploads[0].file.name}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-1">
                    <motion.div
                      className={cn(
                        "h-full rounded-full",
                        getStatusColor(activeUploads[0].status)
                      )}
                      initial={{ width: '0%' }}
                      animate={{ width: `${activeUploads[0].progress}%` }}
                      transition={{ duration: 0.3, ease: 'easeOut' }}
                    />
                  </div>
                  <span className="text-xs text-gray-600 min-w-[2.5rem]">
                    {Math.round(activeUploads[0].progress)}%
                  </span>
                </div>
              </div>
            )}

            {/* Expand/Collapse Button */}
            {activeUploads.length > 1 && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="px-2 py-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors flex items-center space-x-1"
                title={isExpanded ? 'Zuklappen' : 'Warteschlange anzeigen'}
              >
                <span className="text-xs">
                  {isExpanded ? 'Zuklappen' : `+${activeUploads.length - 1} weitere`}
                </span>
                {isExpanded ?
                  <ChevronDownIcon className="w-3 h-3" /> :
                  <ChevronUpIcon className="w-3 h-3" />
                }
              </button>
            )}

            {/* Right: Close Button */}
            <button
              onClick={onClearAll}
              className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
              title="Alle Uploads abbrechen"
            >
              <XMarkIcon className="w-4 h-4" />
            </button>
          </div>

          {/* Expanded Upload Queue */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                className="overflow-hidden"
              >
                <div className="pt-3 border-t border-gray-200/50">
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {activeUploads.map((upload, index) => (
                      <motion.div
                        key={upload.id}
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center space-x-3 flex-1 min-w-0">
                          {getStatusIcon(upload.status)}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium text-gray-900 truncate">
                                {upload.file.name}
                              </span>
                              <span className="text-xs text-gray-500 ml-2">
                                {formatFileSize(upload.file.size)}
                              </span>
                            </div>
                            <div className="flex items-center space-x-2 mt-1">
                              <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                                <motion.div
                                  className={cn(
                                    "h-full rounded-full",
                                    getStatusColor(upload.status)
                                  )}
                                  initial={{ width: '0%' }}
                                  animate={{ width: `${upload.progress}%` }}
                                  transition={{ duration: 0.3, ease: 'easeOut' }}
                                />
                              </div>
                              <span className="text-xs text-gray-600 min-w-[2.5rem]">
                                {Math.round(upload.progress)}%
                              </span>
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {upload.status === 'uploading' && 'Wird hochgeladen...'}
                              {upload.status === 'analyzing' && 'Wird analysiert...'}
                              {upload.status === 'processing' && 'Wird verarbeitet...'}
                              {upload.status === 'pending' && 'Wartet...'}
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => onRemoveUpload(upload.id)}
                          className="ml-3 p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                          title="Upload abbrechen"
                        >
                          <XMarkIcon className="w-4 h-4" />
                        </button>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}