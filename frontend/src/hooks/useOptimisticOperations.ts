import { useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { useDocumentStore } from '@/stores/documentStore'
import { Document, OptimisticOperation, DocumentUploadRequest } from '@/types/document.types'

export function useOptimisticOperations() {
  const documentStore = useDocumentStore()

  // Create optimistic document
  const createDocumentOptimistically = useCallback(
    async (uploadRequest: DocumentUploadRequest): Promise<string> => {
      const operationId = uuidv4()
      const tempDocumentId = `temp-${uuidv4()}`
      
      // Create optimistic document
      const optimisticDocument: Document = {
        id: tempDocumentId,
        filename: uploadRequest.file.name,
        original_filename: uploadRequest.file.name,
        doctype: uploadRequest.doctype,
        category: uploadRequest.category,
        folder_id: uploadRequest.folder_id,
        upload_date: new Date().toISOString(),
        size_bytes: uploadRequest.file.size,
        chunk_count: 0,
        vector_count: 0,
        status: 'uploading',
        tags: uploadRequest.tags,
        visibility: uploadRequest.visibility,
        metadata: {
          title: uploadRequest.file.name,
          language: 'de'
        }
      }

      // Define rollback function
      const rollback = () => {
        documentStore.removeDocument(tempDocumentId)
      }

      // Create optimistic operation
      const operation: OptimisticOperation = {
        id: operationId,
        type: 'create',
        entity: 'document',
        data: optimisticDocument,
        rollback,
        timestamp: new Date().toISOString()
      }

      // Add document optimistically
      documentStore.addDocument(optimisticDocument)
      documentStore.addOptimisticOperation(operation)

      return operationId
    },
    [documentStore]
  )

  // Update document optimistically
  const updateDocumentOptimistically = useCallback(
    (documentId: string, updates: Partial<Document>): string => {
      const operationId = uuidv4()
      const currentDoc = documentStore.getDocumentById(documentId)
      
      if (!currentDoc) {
        throw new Error(`Document ${documentId} not found`)
      }

      // Store original state for rollback
      const originalDoc = { ...currentDoc }

      // Define rollback function
      const rollback = () => {
        documentStore.updateDocument(documentId, originalDoc)
      }

      // Create optimistic operation
      const operation: OptimisticOperation = {
        id: operationId,
        type: 'update',
        entity: 'document',
        data: { id: documentId, updates },
        rollback,
        timestamp: new Date().toISOString()
      }

      // Update document optimistically
      documentStore.updateDocument(documentId, updates)
      documentStore.addOptimisticOperation(operation)

      return operationId
    },
    [documentStore]
  )

  // Delete document optimistically
  const deleteDocumentOptimistically = useCallback(
    (documentId: string): string => {
      const operationId = uuidv4()
      const currentDoc = documentStore.getDocumentById(documentId)
      
      if (!currentDoc) {
        throw new Error(`Document ${documentId} not found`)
      }

      // Store original document for rollback
      const originalDoc = { ...currentDoc }

      // Define rollback function
      const rollback = () => {
        documentStore.addDocument(originalDoc)
      }

      // Create optimistic operation
      const operation: OptimisticOperation = {
        id: operationId,
        type: 'delete',
        entity: 'document',
        data: { documentId },
        rollback,
        timestamp: new Date().toISOString()
      }

      // Remove document optimistically
      documentStore.removeDocument(documentId)
      documentStore.addOptimisticOperation(operation)

      return operationId
    },
    [documentStore]
  )

  // Batch operations
  const batchOperations = useCallback(
    (operations: Array<() => string>): string[] => {
      const operationIds: string[] = []
      
      // Execute all operations
      operations.forEach(operation => {
        try {
          const id = operation()
          operationIds.push(id)
        } catch (error) {
          console.error('Failed to execute optimistic operation:', error)
          // Rollback previously executed operations in this batch
          operationIds.forEach(id => {
            documentStore.rollbackOperation(id)
          })
          throw error
        }
      })

      return operationIds
    },
    [documentStore]
  )

  // Confirm operation (called when backend confirms success)
  const confirmOperation = useCallback(
    (operationId: string, finalData?: any) => {
      const operation = documentStore.pendingOperations.get(operationId)
      
      if (operation) {
        // Update with final data if provided
        if (finalData && operation.type === 'create') {
          // Replace temporary document with real one
          if (operation.entity === 'document') {
            documentStore.removeDocument(operation.data.id)
            documentStore.addDocument(finalData)
          }
        } else if (finalData && operation.type === 'update') {
          documentStore.updateDocument(finalData.id, finalData)
        }

        // Remove operation
        documentStore.removeOptimisticOperation(operationId)
      }
    },
    [documentStore]
  )

  // Rollback specific operation
  const rollbackOperation = useCallback(
    (operationId: string, reason?: string) => {
      console.warn(`Rolling back operation ${operationId}${reason ? `: ${reason}` : ''}`)
      documentStore.rollbackOperation(operationId)
    },
    [documentStore]
  )

  // Rollback all pending operations
  const rollbackAllOperations = useCallback(
    (reason?: string) => {
      console.warn(`Rolling back all operations${reason ? `: ${reason}` : ''}`)
      documentStore.rollbackAllOperations()
    },
    [documentStore]
  )

  // Check if document has pending operations
  const hasPendingOperations = useCallback(
    (documentId: string): boolean => {
      return Array.from(documentStore.pendingOperations.values()).some(
        op => {
          if (op.entity === 'document') {
            if (op.type === 'create' || op.type === 'update') {
              return op.data.id === documentId || (op.data.updates && op.data.id === documentId)
            } else if (op.type === 'delete') {
              return op.data.documentId === documentId
            }
          }
          return false
        }
      )
    },
    [documentStore]
  )

  // Get pending operations for a document
  const getPendingOperations = useCallback(
    (documentId?: string): OptimisticOperation[] => {
      const allOperations = Array.from(documentStore.pendingOperations.values())
      
      if (!documentId) {
        return allOperations
      }

      return allOperations.filter(op => {
        if (op.entity === 'document') {
          if (op.type === 'create' || op.type === 'update') {
            return op.data.id === documentId
          } else if (op.type === 'delete') {
            return op.data.documentId === documentId
          }
        }
        return false
      })
    },
    [documentStore]
  )

  // Operation status helpers
  const getOperationStatus = useCallback(
    (operationId: string): 'pending' | 'confirmed' | 'not_found' => {
      return documentStore.pendingOperations.has(operationId) 
        ? 'pending' 
        : 'not_found' // We assume confirmed operations are removed
    },
    [documentStore]
  )

  return {
    // Core operations
    createDocumentOptimistically,
    updateDocumentOptimistically,
    deleteDocumentOptimistically,
    
    // Batch operations
    batchOperations,
    
    // Operation management
    confirmOperation,
    rollbackOperation,
    rollbackAllOperations,
    
    // Status checks
    hasPendingOperations,
    getPendingOperations,
    getOperationStatus,
    
    // Stats
    get pendingOperationsCount() {
      return documentStore.pendingOperations.size
    },
    
    get pendingOperations() {
      return Array.from(documentStore.pendingOperations.values())
    }
  }
}