'use client'

import React, { useState, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react'
// import { useToastContext } from '@/contexts/ToastContext'

interface DragDropZoneProps {
  onFilesDrop: (files: File[]) => void
  accept?: string
  maxFiles?: number
  maxSize?: number // in bytes
  multiple?: boolean
  className?: string
  children?: React.ReactNode
  disabled?: boolean
}

interface FileWithStatus {
  file: File
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress?: number
  error?: string
}

export const DragDropZone: React.FC<DragDropZoneProps> = ({
  onFilesDrop,
  accept,
  maxFiles = 10,
  maxSize = 10 * 1024 * 1024, // 10MB default
  multiple = true,
  className = '',
  children,
  disabled = false
}) => {
  // const toast = useToastContext() // Temporarily disabled
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragActive, setIsDragActive] = useState(false)
  const [files, setFiles] = useState<FileWithStatus[]>([])

  const validateFile = useCallback((file: File): string | null => {
    if (maxSize && file.size > maxSize) {
      return `Datei zu groß (${formatFileSize(file.size)}). Maximum: ${formatFileSize(maxSize)}`
    }
    
    if (accept && !isFileTypeAccepted(file, accept)) {
      return `Dateityp nicht unterstützt: ${file.type || 'unbekannt'}`
    }
    
    return null
  }, [maxSize, accept])

  const handleFiles = useCallback((newFiles: File[]) => {
    if (disabled) return

    // Validate file count
    const totalFiles = files.length + newFiles.length
    if (totalFiles > maxFiles) {
      alert(`Zu viele Dateien: Maximal ${maxFiles} Dateien erlaubt. Du hast ${totalFiles} ausgewählt.`)
      return
    }

    // Validate each file
    const validFiles: File[] = []
    const errors: string[] = []

    newFiles.forEach(file => {
      const error = validateFile(file)
      if (error) {
        errors.push(`${file.name}: ${error}`)
      } else {
        validFiles.push(file)
      }
    })

    // Show validation errors
    if (errors.length > 0) {
      alert('Datei-Validierung fehlgeschlagen: ' + (errors.length === 1 ? errors[0] : `${errors.length} Dateien ungültig`))
    }

    // Add valid files
    if (validFiles.length > 0) {
      const newFileStatuses: FileWithStatus[] = validFiles.map(file => ({
        file,
        status: 'pending' as const
      }))
      
      setFiles(prev => [...prev, ...newFileStatuses])
      onFilesDrop(validFiles)
      
      // Files added successfully - no notification needed
    }
  }, [files.length, maxFiles, validateFile, onFilesDrop, toast, disabled])

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!disabled) {
      setIsDragActive(true)
    }
  }, [disabled])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!disabled) {
      setIsDragActive(false)
    }
  }, [disabled])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)

    if (disabled) return

    const droppedFiles = Array.from(e.dataTransfer.files)
    handleFiles(droppedFiles)
  }, [handleFiles, disabled])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      handleFiles(selectedFiles)
    }
    // Reset input value to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }, [handleFiles])

  const removeFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }, [])

  const openFileDialog = useCallback(() => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click()
    }
  }, [disabled])

  return (
    <div className={`relative ${className}`}>
      <motion.div
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={openFileDialog}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-200 ease-out
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 scale-105' 
            : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        animate={{ 
          scale: isDragActive ? 1.02 : 1,
          rotateX: isDragActive ? 5 : 0
        }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple={multiple}
          accept={accept}
          onChange={handleFileInput}
          className="hidden"
          disabled={disabled}
        />

        <AnimatePresence>
          {isDragActive && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="absolute inset-0 bg-primary-500/20 rounded-xl flex items-center justify-center"
            >
              <div className="text-primary-600 dark:text-primary-400">
                <Upload className="w-12 h-12 mx-auto mb-2" />
                <p className="font-medium">Dateien hier ablegen!</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {children || (
          <div className="space-y-4">
            <Upload className="w-10 h-10 text-gray-400 mx-auto" />
            <div>
              <p className="text-lg font-medium text-gray-900 dark:text-white">
                Dateien hier ablegen oder klicken zum Auswählen
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                {accept && `Unterstützt: ${accept.split(',').join(', ')}`}
                {maxSize && ` • Max: ${formatFileSize(maxSize)}`}
                {maxFiles && ` • Bis zu ${maxFiles} Dateien`}
              </p>
            </div>
          </div>
        )}
      </motion.div>

      {/* File List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 space-y-2"
          >
            {files.map((fileStatus, index) => (
              <motion.div
                key={`${fileStatus.file.name}-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center space-x-3">
                  <File className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {fileStatus.file.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatFileSize(fileStatus.file.size)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {fileStatus.status === 'success' && (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  )}
                  {fileStatus.status === 'error' && (
                    <AlertCircle className="w-5 h-5 text-red-500" />
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      removeFile(index)
                    }}
                    className="p-1 hover:bg-red-100 dark:hover:bg-red-900/20 rounded text-red-500 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Helper functions
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function isFileTypeAccepted(file: File, accept: string): boolean {
  const acceptedTypes = accept.split(',').map(type => type.trim())
  
  return acceptedTypes.some(acceptedType => {
    if (acceptedType.startsWith('.')) {
      // File extension
      return file.name.toLowerCase().endsWith(acceptedType.toLowerCase())
    } else if (acceptedType.includes('*')) {
      // Wildcard type (e.g., "image/*")
      const [type] = acceptedType.split('/')
      return file.type.startsWith(type + '/')
    } else {
      // Exact mime type
      return file.type === acceptedType
    }
  })
}