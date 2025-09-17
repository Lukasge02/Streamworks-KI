/**
 * DocumentGrid Component
 * Display documents in grid or list view with selection
 */

import React, { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { 
  DocumentTextIcon, 
  PhotoIcon, 
  VideoCameraIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
  EllipsisVerticalIcon,
  EyeIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'
import { DocumentWithFolder, DocumentGridProps } from '@/types/api.types'
import { DocumentStatusBadge } from '@/components/ui/DocumentStatusBadge'
import { t, formatUploadDate, formatProcessingDate } from '@/lib/translations'

interface DocumentCardProps {
  document: DocumentWithFolder
  isSelected: boolean
  onSelect: () => void
  onOpen: () => void
  onDelete: () => void
  onShowInfo: () => void
  viewMode: 'grid' | 'list'
  showFolderInfo?: boolean
}

function getFileIcon(mimeType: string) {
  if (mimeType.startsWith('image/')) return PhotoIcon
  if (mimeType.startsWith('video/')) return VideoCameraIcon
  if (mimeType.startsWith('audio/')) return MusicalNoteIcon
  if (mimeType.includes('zip') || mimeType.includes('tar') || mimeType.includes('rar')) return ArchiveBoxIcon
  return DocumentTextIcon
}

function getFileTypeTheme(mimeType: string) {
  if (mimeType === 'application/pdf') {
    return {
      bgColor: 'bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20',
      iconColor: 'text-red-600 dark:text-red-400',
      borderColor: 'border-red-200/50 dark:border-red-800/50'
    }
  }
  if (mimeType.startsWith('image/')) {
    return {
      bgColor: 'bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20',
      iconColor: 'text-purple-600 dark:text-purple-400',
      borderColor: 'border-purple-200/50 dark:border-purple-800/50'
    }
  }
  if (mimeType.startsWith('video/')) {
    return {
      bgColor: 'bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20',
      iconColor: 'text-blue-600 dark:text-blue-400',
      borderColor: 'border-blue-200/50 dark:border-blue-800/50'
    }
  }
  if (mimeType.includes('sheet') || mimeType.includes('excel')) {
    return {
      bgColor: 'bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20',
      iconColor: 'text-green-600 dark:text-green-400',
      borderColor: 'border-green-200/50 dark:border-green-800/50'
    }
  }
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) {
    return {
      bgColor: 'bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20',
      iconColor: 'text-orange-600 dark:text-orange-400',
      borderColor: 'border-orange-200/50 dark:border-orange-800/50'
    }
  }
  if (mimeType.includes('zip') || mimeType.includes('tar') || mimeType.includes('rar')) {
    return {
      bgColor: 'bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20',
      iconColor: 'text-amber-600 dark:text-amber-400',
      borderColor: 'border-amber-200/50 dark:border-amber-800/50'
    }
  }
  // Default for documents
  return {
    bgColor: 'bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20',
    iconColor: 'text-primary-600 dark:text-primary-400',
    borderColor: 'border-primary-200/50 dark:border-primary-800/50'
  }
}

interface DocumentInfoModalProps {
  isOpen: boolean
  onClose: () => void
  document: DocumentWithFolder
}

function DocumentInfoModal({ isOpen, onClose, document: doc }: DocumentInfoModalProps) {
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const handleKeyDown = React.useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose()
    }
  }, [onClose])

  // Add escape key listener
  React.useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, handleKeyDown])

  if (!isOpen) return null

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {t('metadata.documentInfo')}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Left Column - Basic Info */}
            <div className="space-y-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
                  Datei-Information
                </h3>
                <div className="space-y-3">
                  <div>
                    <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.originalFilename')}:</dt>
                    <dd className="text-sm font-medium text-gray-900 dark:text-gray-100 break-all">
                      {doc.original_filename}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.filename')}:</dt>
                    <dd className="text-sm font-medium text-gray-900 dark:text-gray-100 break-all">
                      {doc.filename}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.fileSize')}:</dt>
                    <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {formatFileSize(doc.file_size)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.mimeType')}:</dt>
                    <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {doc.mime_type}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.status')}:</dt>
                    <dd className="text-sm">
                      <DocumentStatusBadge status={doc.status} size="sm" />
                    </dd>
                  </div>
                </div>
              </div>

              {/* Tags */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
                  {t('metadata.tags')}
                </h3>
                {doc.tags && doc.tags.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {doc.tags.map(tag => (
                      <span 
                        key={tag} 
                        className="inline-flex px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {t('metadata.noTags')}
                  </p>
                )}
              </div>
            </div>

            {/* Right Column - Timestamps & Technical */}
            <div className="space-y-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
                  Zeitstempel
                </h3>
                <div className="space-y-3">
                  <div>
                    <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.uploadedAt')}:</dt>
                    <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {formatUploadDate(doc.created_at)}
                    </dd>
                  </div>
                  {doc.updated_at !== doc.created_at && (
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.updatedAt')}:</dt>
                      <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {formatUploadDate(doc.updated_at)}
                      </dd>
                    </div>
                  )}
                  {doc.processed_at && (
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.processedAt')}:</dt>
                      <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {formatUploadDate(doc.processed_at)}
                      </dd>
                    </div>
                  )}
                </div>
              </div>

              {/* Technical Info */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
                  Technische Details
                </h3>
                <div className="space-y-3">
                  <div>
                    <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.fileId')}:</dt>
                    <dd className="text-xs font-mono text-gray-900 dark:text-gray-100 break-all">
                      {doc.id}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.fileHash')}:</dt>
                    <dd className="text-xs font-mono text-gray-900 dark:text-gray-100 break-all">
                      {doc.file_hash}
                    </dd>
                  </div>
                  {doc.folder && (
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">{t('metadata.folderPath')}:</dt>
                      <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        📁 {doc.folder.path.join(' / ')} / {doc.folder.name}
                      </dd>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors"
          >
            {t('actions.close')}
          </button>
        </div>
      </div>
    </div>
  )
}

function formatFileSize(bytes: number): string {
  const sizes = ['B', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`
}

function getStatusColor(status: string) {
  // Deprecated - use DocumentStatusBadge component instead
  switch (status) {
    case 'ready': return 'bg-green-100 text-green-800'
    case 'processing': return 'bg-yellow-100 text-yellow-800'
    case 'uploading': return 'bg-blue-100 text-blue-800'
    case 'error': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}


function DocumentCard({ document, isSelected, onSelect, onOpen, onDelete, onShowInfo, viewMode, showFolderInfo = false }: DocumentCardProps) {
  const [showMenu, setShowMenu] = useState(false)
  const FileIcon = getFileIcon(document.mime_type)
  const fileTheme = getFileTypeTheme(document.mime_type)
  
  // Click outside handler for menu
  const menuRef = React.useRef<HTMLDivElement>(null)
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false)
      }
    }
    if (showMenu) {
      window.document.addEventListener('mousedown', handleClickOutside)
      return () => window.document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showMenu])

  if (viewMode === 'list') {
    return (
      <div 
        className={`
          flex items-center p-3 rounded-lg border transition-all duration-150
          ${isSelected ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'}
          cursor-pointer
        `}
        onClick={onSelect}
      >
        {/* Selection Checkbox */}
        <div className="flex-shrink-0 mr-3">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onSelect}
            className="w-4 h-4 text-blue-600 dark:text-blue-400 rounded border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:bg-gray-700"
            onClick={(e) => e.stopPropagation()}
          />
        </div>

        {/* File Icon */}
        <div className="flex-shrink-0 mr-3">
          <FileIcon className="w-6 h-6 text-gray-500 dark:text-gray-400" />
        </div>

        {/* File Info */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
            {document.original_filename}
          </p>
          <div className="flex items-center mt-1 text-xs text-gray-500 dark:text-gray-400 space-x-4">
            <span>{formatFileSize(document.file_size)}</span>
            <span className="text-gray-600 dark:text-gray-300">
              {formatUploadDate(document.created_at)}
            </span>
            {showFolderInfo && document.folder && (
              <span className="text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded">📁 {document.folder.name}</span>
            )}
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex-shrink-0 mr-3">
          <DocumentStatusBadge status={document.status} size="sm" />
        </div>

        {/* Actions */}
        <div className="flex-shrink-0 relative">
          <button
            onClick={(e) => {
              e.stopPropagation()
              setShowMenu(!showMenu)
            }}
            className="p-1 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400 rounded"
          >
            <EllipsisVerticalIcon className="w-5 h-5" />
          </button>

          {showMenu && (
            <div className="absolute right-0 top-full mt-1 w-32 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-10">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onOpen()
                  setShowMenu(false)
                }}
                className="flex items-center w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <EyeIcon className="w-4 h-4 mr-2" />
                {t('actions.view')}
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onShowInfo()
                  setShowMenu(false)
                }}
                className="flex items-center w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <InformationCircleIcon className="w-4 h-4 mr-2" />
                {t('actions.showInfo')}
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  // TODO: Implement download
                  setShowMenu(false)
                }}
                className="flex items-center w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                {t('actions.download')}
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete()
                  setShowMenu(false)
                }}
                className="flex items-center w-full px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <TrashIcon className="w-4 h-4 mr-2" />
                {t('actions.delete')}
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Modern Grid Card Design with Hidden Actions
  return (
    <div className="relative group h-[200px]">
      <div 
        className={`
          relative w-full h-full rounded-xl cursor-pointer transition-all duration-300 ease-out
          border-2 shadow-sm hover:shadow-lg transform hover:-translate-y-1
          ${isSelected 
            ? 'bg-gradient-to-br from-primary-50 to-primary-100/90 dark:from-primary-900/40 dark:to-primary-800/30 border-primary-300 dark:border-primary-600 shadow-primary-200/50' 
            : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600'
          }
        `}
        onClick={onSelect}
      >
        {/* 3-Dot Menu - Always visible in top right */}
        <div className="absolute top-3 right-3 z-10">
          <button
            onClick={(e) => {
              e.stopPropagation()
              setShowMenu(!showMenu)
            }}
            className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-150 touch-manipulation min-h-[36px] min-w-[36px] flex items-center justify-center"
            aria-label="Aktionen anzeigen"
          >
            <EllipsisVerticalIcon className="w-5 h-5" />
          </button>

          {/* Dropdown Menu */}
          {showMenu && (
            <div 
              ref={menuRef}
              className="absolute right-0 top-full mt-2 w-36 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-50 py-1 animate-in fade-in slide-in-from-top-2 duration-200"
            >
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onOpen()
                  setShowMenu(false)
                }}
                className="flex items-center w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors touch-manipulation"
              >
                <EyeIcon className="w-4 h-4 mr-1.5" />
                Ansehen
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onShowInfo()
                  setShowMenu(false)
                }}
                className="flex items-center w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors touch-manipulation"
              >
                <InformationCircleIcon className="w-4 h-4 mr-1.5" />
                Informationen
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  // TODO: Implement download
                  setShowMenu(false)
                }}
                className="flex items-center w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors touch-manipulation"
              >
                <ArrowDownTrayIcon className="w-4 h-4 mr-1.5" />
                Herunterladen
              </button>
              <div className="border-t border-gray-200 dark:border-gray-600 my-1"></div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete()
                  setShowMenu(false)
                }}
                className="flex items-center w-full px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors touch-manipulation"
              >
                <TrashIcon className="w-4 h-4 mr-1.5" />
                Löschen
              </button>
            </div>
          )}
        </div>

        {/* Modern Card Content */}
        <div className="p-4 h-full flex flex-col">
          {/* Top Section - Checkbox & File Icon */}
          <div className="flex items-start justify-between mb-3">
            {/* Checkbox - Top left */}
            <div className="flex-shrink-0">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={onSelect}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            
            {/* File Icon - Top center */}
            <div className={`p-3 ${fileTheme.bgColor} rounded-xl border ${fileTheme.borderColor} shadow-sm`}>
              <FileIcon className={`w-6 h-6 ${fileTheme.iconColor}`} />
            </div>
            
            {/* Space for 3-dot menu */}
            <div className="w-6">
            </div>
          </div>

          {/* Document Title - Prominent */}
          <div className="flex-1 mb-3">
            <h3 
              className="text-sm font-semibold text-gray-900 dark:text-gray-100 cursor-pointer hover:text-primary-600 dark:hover:text-primary-400 transition-colors leading-tight mb-2"
              style={{
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}
              title={`${document.original_filename} - Doppelklick zum Öffnen`}
              onDoubleClick={(e) => {
                e.stopPropagation()
                onOpen()
              }}
            >
              {document.original_filename}
            </h3>
            
            {/* File Metadata - Clean layout */}
            <div className="space-y-2 text-xs text-gray-600 dark:text-gray-400">
              <div className="flex items-center space-x-2">
                <span className="font-medium">{formatFileSize(document.file_size)}</span>
                <span>•</span>
                <span>{formatUploadDate(document.created_at)}</span>
              </div>
              
              {/* Tags - When available */}
              {document.tags && document.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {document.tags.slice(0, 2).map(tag => (
                    <span key={tag} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                  {document.tags.length > 2 && (
                    <span className="px-1.5 py-0.5 bg-primary-100 dark:bg-primary-800 text-primary-700 dark:text-primary-300 rounded text-xs">
                      +{document.tags.length - 2}
                    </span>
                  )}
                </div>
              )}
              
              {/* Folder Info and Status on same line */}
              <div className="flex items-center justify-between">
                {showFolderInfo && document.folder && (
                  <div className="flex items-center text-primary-600 dark:text-primary-400">
                    <span className="truncate">📁 {document.folder.name}</span>
                  </div>
                )}
                <DocumentStatusBadge status={document.status} size="sm" />
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  )
}

export function DocumentGrid({
  documents,
  loading,
  selectedDocuments,
  onDocumentSelect,
  onDocumentOpen,
  onDocumentDelete,
  viewMode,
  showFolderInfo = false
}: DocumentGridProps) {
  const [infoModalDocument, setInfoModalDocument] = useState<DocumentWithFolder | null>(null)
  
  const handleShowInfo = (document: DocumentWithFolder) => {
    setInfoModalDocument(document)
  }

  const handleCloseInfoModal = () => {
    setInfoModalDocument(null)
  }
  if (loading) {
    return (
      <div className="p-6">
        <div className={`
          ${viewMode === 'grid' 
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6' 
            : 'space-y-2'
          }
        `}>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className={`
              animate-pulse bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 rounded-2xl shadow-lg border-2 border-gray-200 dark:border-gray-600
              ${viewMode === 'grid' ? 'min-h-[140px]' : 'h-16'}
            `} />
          ))}
        </div>
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500 p-8">
        <div className="relative mb-6">
          <div className="absolute inset-0 bg-gradient-to-r from-primary-400/20 to-primary-600/20 rounded-3xl blur-2xl"></div>
          <div className="relative p-6 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-3xl border-2 border-primary-200/30 dark:border-primary-700/30 shadow-xl">
            <DocumentTextIcon className="w-20 h-20 text-primary-400 dark:text-primary-500" />
          </div>
        </div>
        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
          Keine Dokumente gefunden
        </h3>
        <p className="text-gray-600 dark:text-gray-400 text-center max-w-md leading-relaxed">
          {showFolderInfo 
            ? "Es wurden noch keine Dokumente in diesem Ordner hochgeladen." 
            : "Laden Sie Dokumente über den Upload-Bereich oben hoch, um zu beginnen."}
        </p>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className={`
        ${viewMode === 'grid' 
          ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6' 
          : 'space-y-2'
        }
      `}>
        {documents.map(document => (
          <div key={document.id} className="group">
            <DocumentCard
              document={document}
              isSelected={selectedDocuments.has(document.id)}
              onSelect={() => onDocumentSelect(document.id)}
              onOpen={() => onDocumentOpen(document.id)}
              onDelete={() => onDocumentDelete(document.id)}
              onShowInfo={() => handleShowInfo(document)}
              viewMode={viewMode}
              showFolderInfo={showFolderInfo}
            />
          </div>
        ))}
      </div>
      
      {/* Document Info Modal */}
      {infoModalDocument && (
        <DocumentInfoModal
          isOpen={true}
          onClose={handleCloseInfoModal}
          document={infoModalDocument}
        />
      )}
    </div>
  )
}