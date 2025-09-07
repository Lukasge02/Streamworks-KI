/**
 * Modern FolderTree Component
 * Hierarchical folder navigation with German UI and accessibility
 */

import { useState } from 'react'
import { ChevronRightIcon, ChevronDownIcon, FolderIcon, PlusIcon, TrashIcon, DocumentIcon } from '@heroicons/react/24/outline'
import { FolderTree as FolderTreeType, FolderTreeProps } from '@/types/api.types'
import { t } from '@/lib/translations'
import { cn } from '@/lib/utils'

interface FolderTreeItemProps {
  folder: FolderTreeType
  level: number
  selectedFolder?: string
  expandedFolders: Set<string>
  onFolderSelect: (folderId: string) => void
  onFolderCreate: (parentId: string) => void
  onFolderDelete: (folderId: string) => void
  onToggleExpand: (folderId: string) => void
}

function FolderTreeItem({
  folder,
  level,
  selectedFolder,
  expandedFolders,
  onFolderSelect,
  onFolderCreate,
  onFolderDelete,
  onToggleExpand
}: FolderTreeItemProps) {
  const [isHovered, setIsHovered] = useState(false)
  const isExpanded = expandedFolders.has(folder.id)
  const isSelected = selectedFolder === folder.id
  const hasChildren = folder.children && folder.children.length > 0

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    onFolderSelect(folder.id)
  }

  const handleToggleExpand = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (hasChildren) {
      onToggleExpand(folder.id)
    }
  }

  const handleCreateSubfolder = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    onFolderCreate(folder.id)
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    onFolderDelete(folder.id)
  }

  return (
    <div>
      <div
        className={cn(
          "flex items-center px-2 py-1.5 text-sm rounded-lg cursor-pointer group",
          "transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
          isSelected 
            ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium" 
            : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Expand/Collapse Button */}
        <button
          onClick={handleToggleExpand}
          className={cn(
            "flex-shrink-0 w-4 h-4 mr-1 p-0.5 rounded transition-colors",
            hasChildren ? "hover:bg-gray-200 dark:hover:bg-gray-600 focus:bg-gray-200 dark:focus:bg-gray-600" : "invisible"
          )}
          aria-label={isExpanded ? t('a11y.collapseFolder') : t('a11y.expandFolder')}
        >
          {hasChildren && (
            isExpanded ? (
              <ChevronDownIcon className="w-3 h-3" />
            ) : (
              <ChevronRightIcon className="w-3 h-3" />
            )
          )}
        </button>

        {/* Folder Icon */}
        <FolderIcon className="flex-shrink-0 w-4 h-4 mr-2 text-gray-500 dark:text-gray-400" />

        {/* Folder Name */}
        <span className="flex-1 truncate">
          {folder.name}
        </span>

        {/* Document Count */}
        {folder.document_count > 0 && (
          <span className="flex-shrink-0 text-xs text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded-full ml-2">
            {folder.document_count}
          </span>
        )}

        {/* Action Buttons (show on hover) */}
        {isHovered && (
          <div className="flex-shrink-0 flex items-center ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCreateSubfolder}
              className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-gray-300 transition-colors"
              title={t('folders.createSubfolder')}
              aria-label={t('folders.createSubfolder')}
            >
              <PlusIcon className="w-3 h-3" />
            </button>
            <button
              onClick={handleDelete}
              className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded ml-1 focus:outline-none focus:ring-1 focus:ring-red-300 transition-colors"
              title={t('folders.deleteFolder')}
              aria-label={t('folders.deleteFolder')}
            >
              <TrashIcon className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>

      {/* Children */}
      {isExpanded && hasChildren && (
        <div className="mt-1">
          {folder.children.map(child => (
            <FolderTreeItem
              key={child.id}
              folder={child}
              level={level + 1}
              selectedFolder={selectedFolder}
              expandedFolders={expandedFolders}
              onFolderSelect={onFolderSelect}
              onFolderCreate={onFolderCreate}
              onFolderDelete={onFolderDelete}
              onToggleExpand={onToggleExpand}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function FolderTree({
  folders,
  selectedFolder,
  isGlobalView = false,
  onFolderSelect,
  onGlobalViewSelect,
  onFolderCreate,
  onFolderDelete,
  expandedFolders,
  onToggleExpand
}: FolderTreeProps) {
  if (!folders || folders.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-gray-500">
        <FolderIcon className="w-12 h-12 mb-3 text-gray-300 dark:text-gray-600" />
        <p className="text-sm text-center">
          {t('folders.noFolders')}
        </p>
        <button
          onClick={() => onFolderCreate(null)}
          className="mt-3 px-3 py-1.5 text-xs bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
        >
          {t('folders.createFirstFolder')}
        </button>
      </div>
    )
  }

  // Calculate total document count across all folders
  const totalDocumentCount = folders.reduce((total, folder) => {
    const countRecursive = (f: FolderTreeType): number => {
      return f.document_count + (f.children || []).reduce((sum, child) => sum + countRecursive(child), 0)
    }
    return total + countRecursive(folder)
  }, 0)

  return (
    <div className="space-y-1">
      {/* Alle Dokumente (Global View) Option */}
      <div
        className={cn(
          "flex items-center px-2 py-1.5 text-sm rounded-lg cursor-pointer group",
          "transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
          isGlobalView
            ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium" 
            : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
        )}
        onClick={onGlobalViewSelect}
      >
        {/* Document Icon for Global View */}
        <DocumentIcon className="flex-shrink-0 w-4 h-4 mr-2 text-gray-500 dark:text-gray-400" />

        {/* Label */}
        <span className="flex-1 truncate">
          {t('documents.allDocuments')}
        </span>

        {/* Total Document Count */}
        {totalDocumentCount > 0 && (
          <span className="flex-shrink-0 text-xs text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded-full ml-2">
            {totalDocumentCount}
          </span>
        )}
      </div>

      {/* Divider */}
      <hr className="border-gray-200 my-2" />

      {/* Root Level Folders */}
      {folders.map(folder => (
        <FolderTreeItem
          key={folder.id}
          folder={folder}
          level={0}
          selectedFolder={selectedFolder}
          expandedFolders={expandedFolders}
          onFolderSelect={onFolderSelect}
          onFolderCreate={onFolderCreate}
          onFolderDelete={onFolderDelete}
          onToggleExpand={onToggleExpand}
        />
      ))}

      {/* Create New Root Folder Button */}
      <button
        onClick={() => onFolderCreate(null)}
        className="flex items-center w-full px-2 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors mt-2"
        aria-label={t('folders.newFolder')}
      >
        <PlusIcon className="w-4 h-4 mr-2" />
        <span>{t('folders.newFolder')}</span>
      </button>
    </div>
  )
}