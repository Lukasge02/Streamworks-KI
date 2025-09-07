/**
 * Modern DocumentManager Component
 * Enterprise-grade document and folder management interface with German UI
 */

import { useState, useCallback, useEffect } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { 
  XMarkIcon, 
  TrashIcon, 
  FolderArrowDownIcon, 
  ArrowPathIcon,
  CloudArrowUpIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  Squares2X2Icon,
  ListBulletIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline'
import { useDocuments } from '@/hooks/useDocuments'
import { useFolders } from '@/hooks/useFolders'
import { FolderTree } from './FolderTree'
import { DocumentGrid } from './DocumentGrid'
import { DocumentViewerModal } from './DocumentViewerModal'
import { UploadModal } from './professional-upload/UploadModal'
import { BottomProgressBar, UploadFile } from './professional-upload/TopProgressBar'
import { ActionToolbar } from './ActionToolbar'
import { FolderCreateModal } from './modals/FolderCreateModal'
import { ConfirmModal } from '@/components/ui/modal'
import { DocumentSort, ViewState, SelectionState, UploadRequest, DocumentViewerState } from '@/types/api.types'
import { apiService } from '@/services/api.service'
import { t, formatDocumentCount } from '@/lib/translations'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

interface DocumentManagerProps {
  defaultView?: 'global' | 'folder'
}

export function DocumentManager({ defaultView }: DocumentManagerProps) {
  
  // State management
  const [viewState, setViewState] = useState<ViewState>({
    currentFolder: undefined,
    viewMode: 'grid',
    sortBy: 'created_desc',
    filter: {},
    searchQuery: '',
    isGlobalView: defaultView === 'global'
  })

  const [selectionState, setSelectionState] = useState<SelectionState>({
    selectedDocuments: new Set(),
    selectedFolders: new Set(),
    selectionMode: false
  })

  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
  const [showUploadArea, setShowUploadArea] = useState(false)
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)
  const [activeUploads, setActiveUploads] = useState<UploadFile[]>([])
  
  // Modal states
  const [folderCreateModal, setFolderCreateModal] = useState<{
    isOpen: boolean
    parentId: string | null
    parentName?: string
  }>({ isOpen: false, parentId: null })
  
  const [deleteConfirmModal, setDeleteConfirmModal] = useState<{
    isOpen: boolean
    type: 'folder' | 'document' | 'bulk'
    id?: string
    name?: string
    count?: number
  }>({ isOpen: false, type: 'document' })

  // Document Viewer state
  const [documentViewer, setDocumentViewer] = useState<DocumentViewerState>({
    isOpen: false,
    currentDocumentId: null,
    documents: [],
    currentIndex: 0
  })

  // Hooks
  const {
    folders,
    folderTree,
    loading: foldersLoading,
    error: foldersError,
    createFolder,
    deleteFolder,
    refreshFolders
  } = useFolders()

  const {
    documents,
    loading: documentsLoading,
    error: documentsError,
    uploadDocuments,
    deleteDocument,
    bulkDeleteDocuments,
    bulkMoveDocuments,
    bulkReprocessDocuments,
    refreshDocuments
  } = useDocuments({
    folderId: viewState.currentFolder,
    filter: {
      ...viewState.filter,
      search_query: viewState.searchQuery || undefined
    },
    sort: viewState.sortBy,
    isGlobalView: viewState.isGlobalView
  })

  // Event handlers
  const handleFolderSelect = useCallback((folderId: string) => {
    setViewState(prev => ({ 
      ...prev, 
      currentFolder: folderId,
      isGlobalView: false 
    }))
    setSelectionState(prev => ({ 
      ...prev, 
      selectedDocuments: new Set(),
      selectionMode: false 
    }))
  }, [])

  const handleGlobalViewSelect = useCallback(() => {
    setViewState(prev => ({ 
      ...prev, 
      currentFolder: undefined,
      isGlobalView: true 
    }))
    setSelectionState(prev => ({ 
      ...prev, 
      selectedDocuments: new Set(),
      selectionMode: false 
    }))
  }, [])

  const handleFolderCreate = useCallback((parentId: string | null) => {
    const parentFolder = parentId ? folders.find(f => f.id === parentId) : null
    setFolderCreateModal({
      isOpen: true,
      parentId,
      parentName: parentFolder?.name
    })
  }, [folders])
  
  const handleFolderCreateConfirm = useCallback(async (name: string, description?: string) => {
    try {
      await createFolder({
        name,
        description,
        parent_id: folderCreateModal.parentId || undefined
      })
      await refreshFolders()
      toast.success(t('folders.createFolderSuccess', { name }))
    } catch (error) {
      toast.error(t('folders.createFolderError'))
      throw error // Re-throw to handle in modal
    }
  }, [createFolder, refreshFolders, folderCreateModal.parentId])
  
  const handleCloseCreateModal = useCallback(() => {
    setFolderCreateModal({ isOpen: false, parentId: null })
  }, [])

  const handleFolderDelete = useCallback((folderId: string) => {
    const folder = folders.find(f => f.id === folderId)
    setDeleteConfirmModal({
      isOpen: true,
      type: 'folder',
      id: folderId,
      name: folder?.name
    })
  }, [folders])
  
  const handleFolderDeleteConfirm = useCallback(async () => {
    if (!deleteConfirmModal.id) return
    
    try {
      await deleteFolder(deleteConfirmModal.id, true) // force delete with contents
      await refreshFolders()
      
      // If we're currently viewing the deleted folder, go back to root
      if (viewState.currentFolder === deleteConfirmModal.id) {
        setViewState(prev => ({ ...prev, currentFolder: undefined }))
      }
      
      toast.success(t('folders.deleteFolderSuccess', { name: deleteConfirmModal.name || 'Unknown' }))
    } catch (error) {
      toast.error(t('folders.deleteFolderError'))
    }
  }, [deleteFolder, refreshFolders, viewState.currentFolder, deleteConfirmModal])

  const handleToggleExpand = useCallback((folderId: string) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev)
      if (newSet.has(folderId)) {
        newSet.delete(folderId)
      } else {
        newSet.add(folderId)
      }
      return newSet
    })
  }, [])

  const handleDocumentSelect = useCallback((documentId: string) => {
    setSelectionState(prev => {
      const newSelected = new Set(prev.selectedDocuments)
      if (newSelected.has(documentId)) {
        newSelected.delete(documentId)
      } else {
        newSelected.add(documentId)
      }
      return {
        ...prev,
        selectedDocuments: newSelected,
        selectionMode: newSelected.size > 0
      }
    })
  }, [])

  const handleDocumentOpen = useCallback((documentId: string) => {
    setDocumentViewer({
      isOpen: true,
      currentDocumentId: documentId,
      documents: documents,
      currentIndex: documents.findIndex(doc => doc.id === documentId)
    })
  }, [documents])

  const handleDocumentDelete = useCallback((documentId: string) => {
    const document = documents.find(d => d.id === documentId)
    setDeleteConfirmModal({
      isOpen: true,
      type: 'document',
      id: documentId,
      name: document?.filename
    })
  }, [documents])
  
  const handleDocumentDeleteConfirm = useCallback(async () => {
    if (!deleteConfirmModal.id) return
    
    try {
      await deleteDocument(deleteConfirmModal.id)
      await refreshDocuments()
      toast.success(t('documents.deleteSuccess'))
    } catch (error) {
      toast.error(t('documents.deleteError'))
    }
  }, [deleteDocument, refreshDocuments, deleteConfirmModal])

  const handleUploadComplete = useCallback(async (uploadedDocuments: any[]) => {
    await refreshDocuments()
    // Success message is shown by UploadDropzone component
  }, [refreshDocuments])

  // Upload management functions
  const addUpload = useCallback((file: File): string => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
    const uploadFile: UploadFile = {
      id,
      file,
      progress: 0,
      status: 'pending'
    }
    setActiveUploads(prev => [...prev, uploadFile])
    return id
  }, [])

  const updateUpload = useCallback((id: string, updates: Partial<UploadFile>) => {
    setActiveUploads(prev => prev.map(upload => 
      upload.id === id ? { ...upload, ...updates } : upload
    ))
  }, [])

  const removeUpload = useCallback((id: string) => {
    setActiveUploads(prev => prev.filter(upload => upload.id !== id))
  }, [])

  const clearAllUploads = useCallback(() => {
    setActiveUploads([])
  }, [])

  // Main upload function with progress tracking
  const performUpload = useCallback(async (files: File[]) => {
    if (!viewState.currentFolder) {
      toast.error('Kein Ordner ausgewählt')
      return
    }

    const uploadIds: string[] = []
    
    try {
      // Add all files to upload queue
      files.forEach(file => {
        const id = addUpload(file)
        uploadIds.push(id)
      })

      // Process uploads sequentially for better progress tracking
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        const uploadId = uploadIds[i]

        try {
          // Update status to uploading
          updateUpload(uploadId, { status: 'uploading', progress: 0 })

          // Simulate progress updates during upload
          const progressInterval = setInterval(() => {
            setActiveUploads(prev => prev.map(upload => 
              upload.id === uploadId 
                ? { ...upload, progress: Math.min(upload.progress + Math.random() * 15, 85) }
                : upload
            ))
          }, 200)

          // Perform actual upload
          const uploadData: UploadRequest = {
            file,
            folder_id: viewState.currentFolder!
          }

          const response = await apiService.uploadDocument(uploadData)

          // Clear progress interval
          clearInterval(progressInterval)

          // Update to analyzing status
          updateUpload(uploadId, { 
            status: 'analyzing', 
            progress: 90 
          })

          // Brief analyzing phase
          await new Promise(resolve => setTimeout(resolve, 500))

          // Mark as completed
          updateUpload(uploadId, { 
            status: 'completed', 
            progress: 100,
            uploadedAt: new Date()
          })

          toast.success(`"${file.name}" erfolgreich hochgeladen!`)

        } catch (uploadError) {
          console.error('Upload failed for file:', file.name, uploadError)
          updateUpload(uploadId, { 
            status: 'error', 
            error: uploadError instanceof Error ? uploadError.message : 'Upload failed'
          })
          toast.error(`Upload fehlgeschlagen: ${file.name}`)
        }
      }

      // Refresh documents after all uploads
      await handleUploadComplete([])

      // Auto-remove completed uploads after 3 seconds
      setTimeout(() => {
        uploadIds.forEach(id => {
          setActiveUploads(prev => {
            const upload = prev.find(u => u.id === id)
            if (upload && upload.status === 'completed') {
              return prev.filter(u => u.id !== id)
            }
            return prev
          })
        })
      }, 3000)

    } catch (error) {
      console.error('Upload process failed:', error)
      toast.error('Upload-Prozess fehlgeschlagen')
      
      // Clean up failed uploads
      uploadIds.forEach(id => removeUpload(id))
    }
  }, [viewState.currentFolder, addUpload, updateUpload, removeUpload, handleUploadComplete])

  const handleBulkDelete = useCallback(() => {
    const documentIds = Array.from(selectionState.selectedDocuments)
    if (documentIds.length === 0) return

    setDeleteConfirmModal({
      isOpen: true,
      type: 'bulk',
      count: documentIds.length
    })
  }, [selectionState.selectedDocuments])
  
  const handleBulkDeleteConfirm = useCallback(async () => {
    const documentIds = Array.from(selectionState.selectedDocuments)
    if (documentIds.length === 0) return

    try {
      await bulkDeleteDocuments(documentIds)
      setSelectionState(prev => ({
        ...prev,
        selectedDocuments: new Set(),
        selectionMode: false
      }))
      await refreshDocuments()
      toast.success(t('documents.bulkDeleteSuccess', { count: documentIds.length }))
    } catch (error) {
      toast.error(t('documents.deleteError'))
    }
  }, [selectionState.selectedDocuments, bulkDeleteDocuments, refreshDocuments])

  const handleBulkMove = useCallback(async () => {
    const documentIds = Array.from(selectionState.selectedDocuments)
    if (documentIds.length === 0) return

    // TODO: Implement folder picker dialog
    toast.info('Ordner-Auswahl wird noch implementiert')
    
    // Temporary implementation with prompt
    // const targetFolderId = prompt('Ziel-Ordner ID eingeben:')
    // if (!targetFolderId) return

    // try {
    //   await bulkMoveDocuments(documentIds, targetFolderId)
    //   setSelectionState(prev => ({
    //     ...prev,
    //     selectedDocuments: new Set(),
    //     selectionMode: false
    //   }))
    //   await refreshDocuments()
    // } catch (error) {
    //   toast.error(t('documents.moveError'))
    // }
  }, [selectionState.selectedDocuments])

  const handleBulkReprocess = useCallback(async () => {
    const documentIds = Array.from(selectionState.selectedDocuments)
    if (documentIds.length === 0) return

    try {
      await bulkReprocessDocuments(documentIds)
      setSelectionState(prev => ({
        ...prev,
        selectedDocuments: new Set(),
        selectionMode: false
      }))
      await refreshDocuments()
    } catch (error) {
      toast.error('Fehler beim Neuverarbeiten der Dokumente')
    }
  }, [selectionState.selectedDocuments, bulkReprocessDocuments, refreshDocuments])

  const handleSelectAll = useCallback(() => {
    const allDocumentIds = new Set(documents.map(doc => doc.id))
    setSelectionState(prev => ({
      ...prev,
      selectedDocuments: allDocumentIds,
      selectionMode: allDocumentIds.size > 0
    }))
  }, [documents])

  const handleClearSelection = useCallback(() => {
    setSelectionState(prev => ({
      ...prev,
      selectedDocuments: new Set(),
      selectionMode: false
    }))
  }, [])

  const handleToggleViewMode = useCallback(() => {
    setViewState(prev => ({
      ...prev,
      viewMode: prev.viewMode === 'grid' ? 'list' : 'grid'
    }))
  }, [])

  const handleSortChange = useCallback((sort: DocumentSort) => {
    setViewState(prev => ({ ...prev, sortBy: sort }))
  }, [])

  // Helper functions
  const handleCloseDeleteModal = useCallback(() => {
    setDeleteConfirmModal({ isOpen: false, type: 'document' })
  }, [])
  
  const getDeleteConfirmText = useCallback(() => {
    switch (deleteConfirmModal.type) {
      case 'folder':
        return t('folders.deleteFolderConfirm')
      case 'bulk':
        return t('documents.bulkDeleteConfirm', { count: deleteConfirmModal.count || 0 })
      default:
        return t('documents.deleteConfirm')
    }
  }, [deleteConfirmModal])
  
  const handleDeleteConfirm = useCallback(async () => {
    switch (deleteConfirmModal.type) {
      case 'folder':
        await handleFolderDeleteConfirm()
        break
      case 'bulk':
        await handleBulkDeleteConfirm()
        break
      default:
        await handleDocumentDeleteConfirm()
        break
    }
    handleCloseDeleteModal()
  }, [deleteConfirmModal.type, handleFolderDeleteConfirm, handleBulkDeleteConfirm, handleDocumentDeleteConfirm, handleCloseDeleteModal])

  // Document Viewer handlers
  const handleCloseDocumentViewer = useCallback(() => {
    setDocumentViewer(prev => ({ ...prev, isOpen: false }))
  }, [])

  const handleDocumentViewerNavigate = useCallback((documentId: string) => {
    setDocumentViewer(prev => ({
      ...prev,
      currentDocumentId: documentId,
      currentIndex: documents.findIndex(doc => doc.id === documentId)
    }))
  }, [documents])

  // Get current view name for breadcrumb
  const currentViewName = viewState.isGlobalView
    ? t('documents.allDocuments')
    : viewState.currentFolder 
      ? folders.find(f => f.id === viewState.currentFolder)?.name || t('general.unknown')
      : t('documents.selectFolder')

  // Handle default view activation
  useEffect(() => {
    if (defaultView === 'global') {
      setViewState(prev => ({
        ...prev,
        currentFolder: undefined,
        isGlobalView: true
      }))
    }
  }, [defaultView])

  const loading = foldersLoading || documentsLoading
  const error = foldersError || documentsError

  return (
    <div className="h-full flex flex-col overflow-hidden">
      
      {/* Error Display */}
      {error && (
        <div className="flex-shrink-0 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 mx-6 mt-4">
          <div className="text-red-700 dark:text-red-400">{error}</div>
        </div>
      )}

      {/* Main Content with Split Headers */}
      <div className="flex-1 overflow-hidden">
        <PanelGroup direction="horizontal">
          
          {/* Sidebar with integrated Header */}
          <Panel defaultSize={25} minSize={20} maxSize={40}>
            <div className="h-full border-r bg-gray-50 dark:bg-gray-800 flex flex-col overflow-hidden">
              
              {/* Sidebar Header */}
              <div className="flex-shrink-0 h-[73px] border-b bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 px-4 py-4 flex flex-col justify-center">
                <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  {t('documents.title')}
                </h1>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                  {viewState.isGlobalView ? t('documents.allDocuments') : `${t('documents.currentFolder')}: ${currentViewName}`}
                </p>
              </div>
              
              {/* Scrollable Folder Tree */}
              <div className="flex-1 overflow-y-auto overflow-x-hidden p-4">
                <FolderTree
                  folders={folderTree}
                  selectedFolder={viewState.currentFolder}
                  isGlobalView={viewState.isGlobalView}
                  onFolderSelect={handleFolderSelect}
                  onGlobalViewSelect={handleGlobalViewSelect}
                  onFolderCreate={handleFolderCreate}
                  onFolderDelete={handleFolderDelete}
                  expandedFolders={expandedFolders}
                  onToggleExpand={handleToggleExpand}
                />
              </div>
            </div>
          </Panel>

          <PanelResizeHandle className="w-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors" />

          {/* Main Content Area with integrated Action Bar Header */}
          <Panel defaultSize={75}>
            <div className="h-full flex flex-col bg-white dark:bg-gray-900 overflow-hidden">
              
              {/* Document Area Header with Action Bar */}
              <div className="flex-shrink-0 min-h-[73px] border-b bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 px-4 sm:px-6 py-3 sm:py-4">
                
                {/* Mobile Search Bar - Only visible on smaller screens */}
                <div className="lg:hidden mb-3">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <MagnifyingGlassIcon className="h-4 w-4 text-gray-400" />
                    </div>
                    <input
                      type="text"
                      value={viewState.searchQuery}
                      onChange={(e) => setViewState(prev => ({ ...prev, searchQuery: e.target.value }))}
                      className="block w-full pl-10 pr-10 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-colors"
                      placeholder={t('search.placeholder')}
                    />
                    {viewState.searchQuery && (
                      <button
                        onClick={() => setViewState(prev => ({ ...prev, searchQuery: '' }))}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
                        title={t('search.clear')}
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
                
                <div className="w-full flex flex-col lg:flex-row lg:items-center justify-between space-y-3 lg:space-y-0">
                  
                  {/* Action Bar */}
                  <div className="flex items-center space-x-2 sm:space-x-3 flex-wrap">
                    {selectionState.selectedDocuments.size > 0 ? (
                      <>
                        {/* Selection Info */}
                        <div className="flex items-center space-x-2">
                          <span className="text-sm sm:text-base font-medium text-gray-900 dark:text-gray-100 whitespace-nowrap">
                            {t('documents.selectedCount', { selected: selectionState.selectedDocuments.size, total: documents.length })}
                          </span>
                          <button
                            onClick={handleClearSelection}
                            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 p-1"
                            title={t('documents.clearSelection')}
                          >
                            <XMarkIcon className="w-4 h-4" />
                          </button>
                        </div>
                        
                        <div className="h-4 w-px bg-gray-300 dark:bg-gray-600" />
                        
                        {/* Bulk Actions */}
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={handleBulkDelete}
                            className="inline-flex items-center px-3 py-2 text-sm font-medium text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                          >
                            <TrashIcon className="w-4 h-4 mr-1" />
                            Löschen ({selectionState.selectedDocuments.size})
                          </button>
                          
                          <button
                            onClick={handleBulkMove}
                            className="inline-flex items-center px-3 py-2 text-sm font-medium text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                          >
                            <FolderArrowDownIcon className="w-4 h-4 mr-1" />
                            Verschieben ({selectionState.selectedDocuments.size})
                          </button>
                          
                          {handleBulkReprocess && (
                            <button
                              onClick={handleBulkReprocess}
                              className="inline-flex items-center px-3 py-2 text-sm font-medium text-orange-700 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors"
                            >
                              <ArrowPathIcon className="w-4 h-4 mr-1" />
                              Neu verarbeiten ({selectionState.selectedDocuments.size})
                            </button>
                          )}
                        </div>
                      </>
                    ) : (
                      <>
                        {/* Document Count */}
                        <span className="text-sm sm:text-base text-gray-600 dark:text-gray-400 whitespace-nowrap">
                          {formatDocumentCount(documents.length)}
                        </span>
                        
                        {documents.length > 0 && (
                          <>
                            <div className="h-5 w-px bg-gray-300 dark:bg-gray-600" />
                            <button
                              onClick={handleSelectAll}
                              className="text-sm sm:text-base text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium transition-colors whitespace-nowrap"
                            >
                              {t('documents.selectAll')}
                            </button>
                          </>
                        )}
                        
                        {/* Upload Modal Button */}
                        {viewState.currentFolder && !viewState.isGlobalView && (
                          <>
                            <div className="h-5 w-px bg-gray-300 dark:bg-gray-600" />
                            <button
                              onClick={() => setIsUploadModalOpen(true)}
                              className="inline-flex items-center px-3 py-2 text-sm font-medium rounded transition-colors bg-blue-600 hover:bg-blue-700 text-white border border-blue-600"
                              title="Upload-Fenster öffnen"
                            >
                              <CloudArrowUpIcon className="w-4 h-4 mr-1" />
                              Upload
                            </button>
                          </>
                        )}
                      </>
                    )}
                  </div>
                  
                  {/* Right: Search and Controls */}
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    {/* Search Field - Hidden on mobile */}
                    <div className="hidden lg:block w-64">
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <MagnifyingGlassIcon className="h-4 w-4 text-gray-400" />
                        </div>
                        <input
                          type="text"
                          value={viewState.searchQuery}
                          onChange={(e) => setViewState(prev => ({ ...prev, searchQuery: e.target.value }))}
                          className="block w-full pl-10 pr-10 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-colors"
                          placeholder={t('search.placeholder')}
                        />
                        {viewState.searchQuery && (
                          <button
                            onClick={() => setViewState(prev => ({ ...prev, searchQuery: '' }))}
                            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
                            title={t('search.clear')}
                          >
                            <XMarkIcon className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    {/* Refresh Button - Icon only */}
                    <button
                      onClick={() => window.location.reload()}
                      className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      title={t('general.refresh')}
                    >
                      <ArrowPathIcon className="w-4 h-4" />
                    </button>
                    
                    {/* View Toggle */}
                    <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                      <button
                        onClick={handleToggleViewMode}
                        className={cn(
                          "p-1 rounded transition-colors",
                          viewState.viewMode === 'grid'
                            ? "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-sm"
                            : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                        )}
                        title={t('view.gridView')}
                      >
                        <Squares2X2Icon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={handleToggleViewMode}
                        className={cn(
                          "p-1 rounded transition-colors",
                          viewState.viewMode === 'list'
                            ? "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-sm"
                            : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                        )}
                        title={t('view.listView')}
                      >
                        <ListBulletIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>


              {/* Scrollable Document Grid - ONLY this area scrolls */}
              <div className="flex-1 overflow-y-auto overflow-x-hidden bg-gray-50 dark:bg-gray-900">
                {!viewState.currentFolder && !viewState.isGlobalView ? (
                  <div className="h-full flex items-center justify-center">
                    <div className="text-center">
                      <div className="text-gray-400 mb-4">
                        <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 5a2 2 0 012-2h2a2 2 0 012 2v0M8 5a2 2 0 000 4h8a2 2 0 000-4v0" />
                        </svg>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {t('documents.selectFolder')}
                      </h3>
                      <p className="text-gray-600">
                        {t('documents.selectFolderDescription')}
                      </p>
                    </div>
                  </div>
                ) : (
                  <DocumentGrid
                    documents={documents}
                    loading={loading}
                    selectedDocuments={selectionState.selectedDocuments}
                    onDocumentSelect={handleDocumentSelect}
                    onDocumentOpen={handleDocumentOpen}
                    onDocumentDelete={handleDocumentDelete}
                    viewMode={viewState.viewMode}
                    showFolderInfo={viewState.isGlobalView}
                  />
                )}
              </div>
            </div>
          </Panel>
        </PanelGroup>
      </div>
      
      {/* Modals */}
      <FolderCreateModal
        isOpen={folderCreateModal.isOpen}
        onClose={handleCloseCreateModal}
        onConfirm={handleFolderCreateConfirm}
        parentFolderName={folderCreateModal.parentName}
        loading={foldersLoading}
      />
      
      <ConfirmModal
        isOpen={deleteConfirmModal.isOpen}
        onClose={handleCloseDeleteModal}
        onConfirm={handleDeleteConfirm}
        title={deleteConfirmModal.type === 'folder' ? t('folders.deleteFolder') : t('general.delete')}
        message={getDeleteConfirmText()}
        confirmText={t('general.delete')}
        cancelText={t('general.cancel')}
        variant="danger"
        loading={foldersLoading || documentsLoading}
      />

      {/* Upload Modal */}
      {viewState.currentFolder && (
        <UploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          onFilesSelected={async (files) => {
            setIsUploadModalOpen(false)
            await performUpload(files)
          }}
          maxFiles={10}
          maxSize={100 * 1024 * 1024}
          folderId={viewState.currentFolder}
        />
      )}

      {/* Document Viewer Modal */}
      {documentViewer.isOpen && documentViewer.currentDocumentId && (
        <DocumentViewerModal
          isOpen={documentViewer.isOpen}
          onClose={handleCloseDocumentViewer}
          documents={documentViewer.documents}
          initialDocumentId={documentViewer.currentDocumentId}
          onNavigate={handleDocumentViewerNavigate}
        />
      )}

      {/* Bottom Progress Bar - Fixed position, floats over everything */}
      <BottomProgressBar 
        uploads={activeUploads}
        onRemoveUpload={removeUpload}
        onClearAll={clearAllUploads}
      />
    </div>
  )
}