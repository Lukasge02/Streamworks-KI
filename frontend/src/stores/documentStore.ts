import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { Document, DocumentEvent, DocumentFilter, UploadJobProgress, OptimisticOperation } from '@/types/document.types'

interface DocumentStoreState {
  // Core data
  documents: Document[]
  uploads: Map<string, UploadJobProgress>
  folders: any[] // TODO: Add folder type
  
  // UI state
  selectedDocuments: Set<string>
  filter: DocumentFilter
  viewMode: 'grid' | 'list'
  isLoading: boolean
  
  // Document Viewer state
  viewerOpen: boolean
  viewingDocumentId: string | null
  viewerPanelSizes: { document: number; summary: number; chunks: number }
  
  // WebSocket state
  isConnected: boolean
  lastSyncTime: string | null
  
  // Optimistic operations
  pendingOperations: Map<string, OptimisticOperation>
  
  // Actions
  setDocuments: (documents: Document[]) => void
  addDocument: (document: Document) => void
  updateDocument: (id: string, updates: Partial<Document>) => void
  removeDocument: (id: string) => void
  
  // Upload management
  addUploadJob: (upload: UploadJobProgress) => void
  updateUploadJob: (jobId: string, updates: Partial<UploadJobProgress>) => void
  removeUploadJob: (jobId: string) => void
  
  // Selection
  toggleDocumentSelection: (id: string) => void
  selectAllDocuments: () => void
  clearSelection: () => void
  
  // Filtering
  setFilter: (filter: Partial<DocumentFilter>) => void
  clearFilter: () => void
  
  // Document Viewer
  openDocumentViewer: (documentId: string) => void
  closeDocumentViewer: () => void
  setViewerPanelSizes: (sizes: { document: number; summary: number; chunks: number }) => void
  
  // WebSocket events
  handleWebSocketEvent: (event: DocumentEvent) => void
  setConnectionStatus: (connected: boolean) => void
  
  // Optimistic operations
  addOptimisticOperation: (operation: OptimisticOperation) => void
  removeOptimisticOperation: (id: string) => void
  rollbackOperation: (id: string) => void
  rollbackAllOperations: () => void
  
  // Computed getters
  getFilteredDocuments: () => Document[]
  getDocumentById: (id: string) => Document | undefined
  getUploadProgress: (jobId: string) => UploadJobProgress | undefined
}

export const useDocumentStore = create<DocumentStoreState>()(
  immer((set, get) => ({
    // Initial state
    documents: [],
    uploads: new Map(),
    folders: [],
    selectedDocuments: new Set(),
    filter: {},
    viewMode: 'grid',
    isLoading: false,
    viewerOpen: false,
    viewingDocumentId: null,
    viewerPanelSizes: { document: 50, summary: 25, chunks: 25 },
    isConnected: false,
    lastSyncTime: null,
    pendingOperations: new Map(),
    
    // Document actions
    setDocuments: (documents) => set((state) => {
      state.documents = documents
      state.lastSyncTime = new Date().toISOString()
    }),
    
    addDocument: (document) => set((state) => {
      const existingIndex = state.documents.findIndex(d => d.id === document.id)
      if (existingIndex >= 0) {
        state.documents[existingIndex] = document
      } else {
        state.documents.push(document)
      }
      state.lastSyncTime = new Date().toISOString()
    }),
    
    updateDocument: (id, updates) => set((state) => {
      const index = state.documents.findIndex(d => d.id === id)
      if (index >= 0) {
        Object.assign(state.documents[index], updates)
        state.lastSyncTime = new Date().toISOString()
      }
    }),
    
    removeDocument: (id) => set((state) => {
      state.documents = state.documents.filter(d => d.id !== id)
      state.selectedDocuments.delete(id)
      state.lastSyncTime = new Date().toISOString()
    }),
    
    // Upload management (legacy - will be removed)
    addUploadJob: (upload) => set((state) => {
      state.uploads.set(upload.job_id, upload)
    }),
    
    updateUploadJob: (jobId, updates) => set((state) => {
      const existing = state.uploads.get(jobId)
      if (existing) {
        state.uploads.set(jobId, { ...existing, ...updates })
      }
    }),
    
    removeUploadJob: (jobId) => set((state) => {
      state.uploads.delete(jobId)
    }),
    
    // Selection
    toggleDocumentSelection: (id) => set((state) => {
      if (state.selectedDocuments.has(id)) {
        state.selectedDocuments.delete(id)
      } else {
        state.selectedDocuments.add(id)
      }
    }),
    
    selectAllDocuments: () => set((state) => {
      const filteredDocs = get().getFilteredDocuments()
      filteredDocs.forEach(doc => state.selectedDocuments.add(doc.id))
    }),
    
    clearSelection: () => set((state) => {
      state.selectedDocuments.clear()
    }),
    
    // Filtering
    setFilter: (filter) => set((state) => {
      Object.assign(state.filter, filter)
    }),
    
    clearFilter: () => set((state) => {
      state.filter = {}
    }),
    
    // Document Viewer actions
    openDocumentViewer: (documentId) => set((state) => {
      state.viewerOpen = true
      state.viewingDocumentId = documentId
    }),
    
    closeDocumentViewer: () => set((state) => {
      state.viewerOpen = false
      state.viewingDocumentId = null
    }),
    
    setViewerPanelSizes: (sizes) => set((state) => {
      state.viewerPanelSizes = sizes
    }),
    
    // WebSocket events
    handleWebSocketEvent: (event) => set((state) => {
      switch (event.type) {
        case 'document_added':
          const newDoc = event.data as Document
          get().addDocument(newDoc)
          break
          
        case 'document_updated':
          const updatedDoc = event.data as Document
          get().updateDocument(updatedDoc.id, updatedDoc)
          break
          
        case 'document_deleted':
          const deletedDoc = event.data as Document
          get().removeDocument(deletedDoc.id)
          break
          
        case 'upload_progress':
          const progress = event.data as UploadJobProgress
          get().updateUploadJob(progress.job_id, progress)
          break
      }
      
      state.lastSyncTime = event.timestamp
    }),
    
    setConnectionStatus: (connected) => set((state) => {
      state.isConnected = connected
    }),
    
    // Optimistic operations
    addOptimisticOperation: (operation) => set((state) => {
      state.pendingOperations.set(operation.id, operation)
    }),
    
    removeOptimisticOperation: (id) => set((state) => {
      state.pendingOperations.delete(id)
    }),
    
    rollbackOperation: (id) => {
      const operation = get().pendingOperations.get(id)
      if (operation) {
        operation.rollback()
        get().removeOptimisticOperation(id)
      }
    },
    
    rollbackAllOperations: () => {
      const operations = Array.from(get().pendingOperations.values())
      operations.forEach(op => op.rollback())
      set((state) => {
        state.pendingOperations.clear()
      })
    },
    
    // Computed getters
    getFilteredDocuments: () => {
      const { documents, filter } = get()
      
      return documents.filter(doc => {
        if (filter.category && doc.category !== filter.category) return false
        if (filter.doctype && doc.doctype !== filter.doctype) return false
        if (filter.status && doc.status !== filter.status) return false
        if (filter.folder_id && doc.folder_id !== filter.folder_id) return false
        if (filter.tags && filter.tags.length > 0) {
          const hasMatchingTag = filter.tags.some(tag => doc.tags.includes(tag))
          if (!hasMatchingTag) return false
        }
        if (filter.search && filter.search.length > 0) {
          const searchLower = filter.search.toLowerCase()
          const matchesSearch = 
            doc.filename.toLowerCase().includes(searchLower) ||
            doc.original_filename.toLowerCase().includes(searchLower) ||
            doc.tags.some(tag => tag.toLowerCase().includes(searchLower))
          if (!matchesSearch) return false
        }
        
        return true
      })
    },
    
    getDocumentById: (id) => {
      return get().documents.find(d => d.id === id)
    },
    
    getUploadProgress: (jobId) => {
      return get().uploads.get(jobId)
    }
  }))
)