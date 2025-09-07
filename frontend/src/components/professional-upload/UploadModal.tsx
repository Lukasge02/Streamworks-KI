/**
 * Upload Modal - Large professional upload interface that opens in modal
 * Auto-closes after upload starts, shows progress in top bar
 */

import React, { useState, useCallback, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { CloudArrowUpIcon, DocumentArrowUpIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { Modal } from '@/components/ui/modal'
import { cn } from '@/lib/utils'

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  onFilesSelected: (files: File[]) => void
  maxFiles?: number
  maxSize?: number
  folderId: string
  className?: string
}

export function UploadModal({
  isOpen,
  onClose,
  onFilesSelected,
  maxFiles = 10,
  maxSize = 100 * 1024 * 1024, // 100MB
  folderId,
  className
}: UploadModalProps) {
  const [dragState, setDragState] = useState<'idle' | 'active' | 'reject'>('idle')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const validateFiles = useCallback((files: File[]) => {
    const validFiles: File[] = []
    const errors: string[] = []

    // Check file count
    if (files.length > maxFiles) {
      errors.push(`Zu viele Dateien. Maximum: ${maxFiles}`)
      return { validFiles, errors }
    }

    // Validate each file
    files.forEach(file => {
      if (file.size > maxSize) {
        errors.push(`${file.name}: Datei zu groß (${formatFileSize(file.size)}). Maximum: ${formatFileSize(maxSize)}`)
      } else {
        validFiles.push(file)
      }
    })

    return { validFiles, errors }
  }, [maxFiles, maxSize])

  const handleFiles = useCallback((files: File[]) => {
    const { validFiles, errors } = validateFiles(files)
    
    if (errors.length > 0) {
      // Show errors but don't prevent valid files from being processed
      console.warn('Upload validation errors:', errors)
    }

    if (validFiles.length > 0) {
      onFilesSelected(validFiles)
      onClose() // Auto-close modal after files selected
    }
  }, [validateFiles, onFilesSelected, onClose])

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (rejectedFiles.length > 0) {
      setDragState('reject')
      setTimeout(() => setDragState('idle'), 2000)
      return
    }
    
    handleFiles(acceptedFiles)
  }, [handleFiles])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    multiple: true,
    maxFiles,
    maxSize,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/xml': ['.xml'],
      'text/html': ['.html'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/gif': ['.gif']
    }
  })

  // Update drag state based on dropzone state
  React.useEffect(() => {
    if (isDragReject) {
      setDragState('reject')
    } else if (isDragActive) {
      setDragState('active')
    } else {
      setDragState('idle')
    }
  }, [isDragActive, isDragReject])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      handleFiles(selectedFiles)
    }
  }, [handleFiles])

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="xl"
      className={className}
      closeOnOverlayClick={true}
    >
      <div className="p-8">
        {/* Large Upload Area */}
        <div
          className={cn(
            "relative overflow-hidden rounded-2xl border-2 border-dashed transition-all duration-500 ease-out",
            "bg-gradient-to-br from-slate-50/80 via-blue-50/40 to-indigo-50/30 backdrop-blur-sm",
            "shadow-lg shadow-blue-500/5 cursor-pointer",
            {
              // Idle state
              "border-gray-300/60 hover:border-blue-400/70 hover:bg-gradient-to-br hover:from-blue-50/60 hover:via-indigo-50/40 hover:to-purple-50/30 hover:shadow-xl hover:shadow-blue-500/10 hover:scale-[1.01]": dragState === 'idle',
              
              // Active drag state
              "border-blue-500/80 bg-gradient-to-br from-blue-100/80 via-indigo-100/60 to-purple-100/40 shadow-2xl shadow-blue-500/20 scale-[1.02]": dragState === 'active',
              
              // Reject state
              "border-red-500/80 bg-gradient-to-br from-red-50/80 via-pink-50/60 to-rose-50/40 shadow-2xl shadow-red-500/20 scale-[1.02] animate-pulse": dragState === 'reject'
            }
          )}
        >
          <div
            {...getRootProps()}
            onClick={(e) => {
              // Nur klicken wenn nicht der X-Button gedrückt wurde
              if (!(e.target as Element).closest('button')) {
                fileInputRef.current?.click()
              }
            }}
            className="relative p-12 text-center cursor-pointer"
          >
            <input
              {...getInputProps()}
              ref={fileInputRef}
              onChange={handleFileSelect}
            />

            {/* X-Button oben rechts */}
            <div className="absolute top-4 right-4 z-20">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onClose()
                }}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
                title="Schließen"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            {/* Animated Background Gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-transparent via-blue-500/5 to-indigo-500/10 animate-pulse opacity-50" />
            
            {/* Content */}
            <div className="relative z-10">
              {/* Large Icon */}
              <div className="relative mb-8">
                <div className={cn(
                  "absolute inset-0 rounded-full transition-all duration-700 ease-out",
                  "w-20 h-20 mx-auto blur-xl opacity-30",
                  {
                    "bg-gradient-to-br from-blue-400 to-indigo-600": dragState === 'idle',
                    "bg-gradient-to-br from-green-400 to-emerald-600 animate-pulse": dragState === 'active',
                    "bg-gradient-to-br from-red-400 to-rose-600 animate-bounce": dragState === 'reject'
                  }
                )} />
                
                {dragState === 'active' ? (
                  <DocumentArrowUpIcon className="relative mx-auto h-20 w-20 text-green-600 animate-bounce" />
                ) : (
                  <CloudArrowUpIcon className={cn(
                    "relative mx-auto h-20 w-20 transition-all duration-500 ease-out",
                    {
                      "text-blue-500 hover:text-blue-600 hover:scale-110": dragState === 'idle',
                      "text-red-500 animate-shake": dragState === 'reject'
                    }
                  )} />
                )}
              </div>

              {/* Dynamic Content */}
              {dragState === 'reject' ? (
                <div className="text-red-600 animate-fadeIn">
                  <h3 className="text-2xl font-bold mb-3 bg-gradient-to-r from-red-600 to-rose-700 bg-clip-text text-transparent">
                    Ungültige Dateien
                  </h3>
                  <p className="text-lg opacity-90 mb-4">
                    Diese Dateitypen werden nicht unterstützt
                  </p>
                </div>
              ) : dragState === 'active' ? (
                <div className="text-green-600 animate-fadeIn">
                  <h3 className="text-2xl font-bold mb-3 bg-gradient-to-r from-green-600 to-emerald-700 bg-clip-text text-transparent">
                    Dateien hier ablegen
                  </h3>
                  <p className="text-lg opacity-90 mb-4">
                    Loslassen zum Hochladen
                  </p>
                </div>
              ) : (
                <div className="animate-fadeIn">
                  <h3 className="text-2xl font-bold mb-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    Klicken oder Dateien hierher ziehen
                  </h3>
                  
                  <p className="text-gray-600 mb-6 text-lg">
                    Drag & Drop oder klicken zum Auswählen
                  </p>

                  {/* File Info */}
                  <div className="text-sm text-gray-500 space-y-2">
                    <div className="font-medium">Bis zu {maxFiles} Dateien • Max {formatFileSize(maxSize)} pro Datei</div>
                    <div>Unterstützte Formate:</div>
                    <div className="flex flex-wrap justify-center gap-2 mt-3">
                      {['PDF', 'DOC', 'DOCX', 'TXT', 'MD', 'CSV', 'JSON', 'XML', 'HTML', 'JPG', 'PNG', 'GIF'].map(format => (
                        <span key={format} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                          {format}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </Modal>
  )
}