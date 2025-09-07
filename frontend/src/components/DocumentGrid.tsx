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
import { StatusBadge } from '@/components/ui/StatusBadge'
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

interface DocumentInfoModalProps {
  isOpen: boolean
  onClose: () => void
  document: DocumentWithFolder
}

function DocumentInfoModal({ isOpen, onClose, document: doc }: DocumentInfoModalProps) {
  if (!isOpen) return null

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose()
    }
  }

  // Add escape key listener
  React.useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen])

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
                      <StatusBadge status={doc.status} size="sm" />
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
  // Deprecated - use StatusBadge component instead
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
          <StatusBadge status={document.status} size="sm" />
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

  // Grid view
  return (
    <div 
      className={`
        relative p-4 rounded-lg border transition-all duration-150 cursor-pointer
        ${isSelected ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-sm'}
      `}
      onClick={onSelect}
    >
      {/* Selection Checkbox */}
      <div className="absolute top-3 left-3">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={onSelect}
          className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
          onClick={(e) => e.stopPropagation()}
        />
      </div>

      {/* Actions Menu */}
      <div className="absolute top-3 right-3">
        <button
          onClick={(e) => {
            e.stopPropagation()
            setShowMenu(!showMenu)
          }}
          className="p-1 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-400 rounded opacity-0 group-hover:opacity-100 transition-opacity"
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

      {/* File Icon */}
      <div className="flex justify-center mb-3 mt-2">
        <FileIcon className="w-12 h-12 text-gray-400 dark:text-gray-500" />
      </div>

      {/* File Info */}
      <div className="text-center">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate" title={document.original_filename}>
          {document.original_filename}
        </p>
        <div className="space-y-1 mt-2">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {formatFileSize(document.file_size)}
          </p>
          <p className="text-xs text-gray-600 dark:text-gray-300">
            {formatUploadDate(document.created_at)}
          </p>
        </div>
        {showFolderInfo && document.folder && (
          <p className="text-xs text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded mt-2">
            📁 {document.folder.name}
          </p>
        )}
      </div>

      {/* Status Badge */}
      <div className="flex justify-center mt-2">
        <StatusBadge status={document.status} size="sm" />
      </div>

      {/* Tags */}
      {document.tags && document.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {document.tags.slice(0, 2).map(tag => (
            <span key={tag} className="inline-flex px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
              {tag}
            </span>
          ))}
          {document.tags.length > 2 && (
            <span className="inline-flex px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
              +{document.tags.length - 2}
            </span>
          )}
        </div>
      )}
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
            ? 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4' 
            : 'space-y-2'
          }
        `}>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className={`
              animate-pulse bg-gray-200 rounded-lg
              ${viewMode === 'grid' ? 'h-48' : 'h-16'}
            `} />
          ))}
        </div>
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500">
        <DocumentTextIcon className="w-16 h-16 mb-4 text-gray-300" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Keine Dokumente gefunden
        </h3>
        <p className="text-gray-600 text-center max-w-sm">
          {showFolderInfo 
            ? "Es wurden noch keine Dokumente in Ordner hochgeladen." 
            : "Laden Sie Dokumente über den Upload-Bereich oben hoch, um zu beginnen."}
        </p>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className={`
        ${viewMode === 'grid' 
          ? 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4' 
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