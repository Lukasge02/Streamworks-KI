/**
 * Modern ActionToolbar Component
 * Professional toolbar for bulk operations and view controls with German UI
 */

import { 
  Squares2X2Icon, 
  ListBulletIcon,
  TrashIcon,
  FolderArrowDownIcon,
  CheckIcon,
  XMarkIcon,
  CloudArrowUpIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'
import { ActionToolbarProps } from '@/types/api.types'
import { t, formatDocumentCount } from '@/lib/translations'
import { cn } from '@/lib/utils'

interface EnhancedActionToolbarProps extends ActionToolbarProps {
  showUploadToggle?: boolean
  isUploadVisible?: boolean
  onToggleUpload?: () => void
  onOpenUploadModal?: () => void
  onBulkReprocess?: () => void
}

export function ActionToolbar({
  selectedCount,
  totalCount,
  onBulkDelete,
  onBulkMove,
  onSelectAll,
  onClearSelection,
  onToggleViewMode,
  viewMode,
  showUploadToggle = false,
  isUploadVisible = false,
  onToggleUpload,
  onOpenUploadModal,
  onBulkReprocess
}: EnhancedActionToolbarProps) {
  return (
    <div className="flex items-center justify-between px-6 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      {/* Left side - Selection info and bulk actions */}
      <div className="flex items-center space-x-4">
        {selectedCount > 0 ? (
          <>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {t('documents.selectedCount', { selected: selectedCount, total: totalCount })}
              </span>
              <button
                onClick={onClearSelection}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                title={t('documents.clearSelection')}
                aria-label={t('documents.clearSelection')}
              >
                <XMarkIcon className="w-4 h-4" />
              </button>
            </div>
            
            <div className="h-4 w-px bg-gray-300 dark:bg-gray-600" />
            
            <div className="flex items-center space-x-2">
              <button
                onClick={onBulkDelete}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
              >
                <TrashIcon className="w-4 h-4 mr-1.5" />
                {t('documents.bulkDelete', { count: selectedCount })}
              </button>
              
              <button
                onClick={onBulkMove}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
              >
                <FolderArrowDownIcon className="w-4 h-4 mr-1.5" />
                {t('documents.bulkMove', { count: selectedCount })}
              </button>
              
              {onBulkReprocess && (
                <button
                  onClick={onBulkReprocess}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-orange-700 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors"
                >
                  <ArrowPathIcon className="w-4 h-4 mr-1.5" />
                  {selectedCount === 1 ? 'Neu verarbeiten' : `${selectedCount} neu verarbeiten`}
                </button>
              )}
            </div>
          </>
        ) : (
          <>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {formatDocumentCount(totalCount)}
            </span>
            
            {totalCount > 0 && (
              <>
                <div className="h-4 w-px bg-gray-300 dark:bg-gray-600" />
                <button
                  onClick={onSelectAll}
                  className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded transition-colors"
                  aria-label={t('documents.selectAll')}
                >
                  {t('documents.selectAll')}
                </button>
              </>
            )}
            
            {/* Upload Modal Button */}
            {showUploadToggle && onOpenUploadModal && (
              <>
                <div className="h-4 w-px bg-gray-300 dark:bg-gray-600" />
                <button
                  onClick={onOpenUploadModal}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-lg transition-all duration-200 bg-blue-600 hover:bg-blue-700 text-white border border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  title="Upload-Fenster öffnen"
                >
                  <CloudArrowUpIcon className="w-4 h-4 mr-1.5" />
                  Upload
                </button>
              </>
            )}
          </>
        )}
      </div>

      {/* Right side - View controls */}
      <div className="flex items-center space-x-2">
        <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={onToggleViewMode}
            className={`
              p-1.5 rounded transition-colors
              ${viewMode === 'grid'
                ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-sm'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }
            `}
            title={t('view.gridView')}
            aria-label={t('view.gridView')}
          >
            <Squares2X2Icon className="w-4 h-4" />
          </button>
          <button
            onClick={onToggleViewMode}
            className={`
              p-1.5 rounded transition-colors
              ${viewMode === 'list'
                ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-sm'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }
            `}
            title={t('view.listView')}
            aria-label={t('view.listView')}
          >
            <ListBulletIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}