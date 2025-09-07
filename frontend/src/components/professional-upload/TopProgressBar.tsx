/**
 * Bottom Progress Bar - Fixed progress display at bottom of screen
 * Shows compact upload progress for all active uploads
 */

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { XMarkIcon, DocumentTextIcon, CloudArrowUpIcon } from '@heroicons/react/24/outline'
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

            {/* Center: File Progress (only show current file) */}
            {activeUploads.length > 0 && (
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
                    {activeUploads[0].progress}%
                  </span>
                </div>
              </div>
            )}

            {/* Right: Close Button */}
            <button
              onClick={onClearAll}
              className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
              title="Schließen"
            >
              <XMarkIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}