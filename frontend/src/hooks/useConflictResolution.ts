import { useState, useCallback, useEffect } from 'react'
import { useDocumentStore } from '@/stores/documentStore'
import { useOptimisticOperations } from '@/hooks/useOptimisticOperations'
import { Document, OptimisticOperation } from '@/types/document.types'

export interface ConflictInfo {
  id: string
  type: 'concurrent_edit' | 'stale_update' | 'delete_modified' | 'version_mismatch'
  documentId: string
  localOperation: OptimisticOperation
  remoteDocument: Document
  timestamp: string
  description: string
}

export type ConflictResolutionStrategy = 
  | 'accept_local'    // Keep local changes, discard remote
  | 'accept_remote'   // Discard local changes, accept remote
  | 'merge_changes'   // Attempt automatic merge
  | 'user_resolve'    // Let user manually resolve

export interface ConflictResolution {
  conflictId: string
  strategy: ConflictResolutionStrategy
  resolvedData?: any
  userChoice?: 'local' | 'remote' | 'merged'
}

export function useConflictResolution() {
  const documentStore = useDocumentStore()
  const { 
    getPendingOperations, 
    rollbackOperation, 
    confirmOperation 
  } = useOptimisticOperations()

  // Conflict state
  const [activeConflicts, setActiveConflicts] = useState<Map<string, ConflictInfo>>(new Map())
  const [resolutionHistory, setResolutionHistory] = useState<ConflictResolution[]>([])
  
  // Detect conflicts when remote changes arrive
  const detectConflicts = useCallback((remoteDocument: Document): ConflictInfo[] => {
    const conflicts: ConflictInfo[] = []
    const pendingOps = getPendingOperations(remoteDocument.id)
    
    for (const operation of pendingOps) {
      const conflict = analyzeConflict(operation, remoteDocument)
      if (conflict) {
        conflicts.push(conflict)
      }
    }
    
    return conflicts
  }, [getPendingOperations])

  // Analyze specific conflict types
  const analyzeConflict = (operation: OptimisticOperation, remoteDocument: Document): ConflictInfo | null => {
    const conflictId = `conflict-${operation.id}-${Date.now()}`
    const baseInfo = {
      id: conflictId,
      documentId: remoteDocument.id,
      localOperation: operation,
      remoteDocument,
      timestamp: new Date().toISOString()
    }

    switch (operation.type) {
      case 'update':
        // Check if remote document was modified after our operation started
        const remoteModified = new Date(remoteDocument.upload_date)
        const operationStarted = new Date(operation.timestamp)
        
        if (remoteModified > operationStarted) {
          return {
            ...baseInfo,
            type: 'concurrent_edit',
            description: `Document was modified remotely while you were editing. Remote changes may conflict with your updates.`
          }
        }
        break
        
      case 'delete':
        // Check if document was modified remotely (delete on modified document)
        if (hasRemoteChanges(operation.data, remoteDocument)) {
          return {
            ...baseInfo,
            type: 'delete_modified',
            description: `Document was modified remotely while you were trying to delete it. The remote version may contain important changes.`
          }
        }
        break
        
      case 'create':
        // Check for potential duplicate or naming conflicts
        if (remoteDocument.filename === operation.data.filename) {
          return {
            ...baseInfo,
            type: 'version_mismatch',
            description: `A document with the same filename already exists. This might be a duplicate upload or version conflict.`
          }
        }
        break
    }
    
    return null
  }

  // Check if remote document has changes compared to local operation baseline
  const hasRemoteChanges = (localData: any, remoteDocument: Document): boolean => {
    // Compare key fields that indicate changes
    if (localData.originalDocument) {
      const original = localData.originalDocument
      return (
        original.upload_date !== remoteDocument.upload_date ||
        original.status !== remoteDocument.status ||
        original.chunk_count !== remoteDocument.chunk_count ||
        JSON.stringify(original.tags) !== JSON.stringify(remoteDocument.tags) ||
        original.category !== remoteDocument.category
      )
    }
    
    return true // Assume changes if we can't compare
  }

  // Add conflict to active list
  const addConflict = useCallback((conflict: ConflictInfo) => {
    setActiveConflicts(prev => new Map(prev.set(conflict.id, conflict)))
  }, [])

  // Remove conflict from active list
  const removeConflict = useCallback((conflictId: string) => {
    setActiveConflicts(prev => {
      const updated = new Map(prev)
      updated.delete(conflictId)
      return updated
    })
  }, [])

  // Resolve conflict with strategy
  const resolveConflict = useCallback(async (
    conflictId: string, 
    strategy: ConflictResolutionStrategy,
    userChoice?: 'local' | 'remote' | 'merged',
    customResolution?: any
  ) => {
    const conflict = activeConflicts.get(conflictId)
    if (!conflict) return

    let resolution: ConflictResolution = {
      conflictId,
      strategy,
      userChoice
    }

    try {
      switch (strategy) {
        case 'accept_local':
          // Keep local changes, ignore remote
          // No action needed - optimistic operation continues
          resolution.resolvedData = conflict.localOperation.data
          break

        case 'accept_remote':
          // Discard local changes, accept remote
          rollbackOperation(conflict.localOperation.id, 'Conflict resolved: accepting remote changes')
          // Update local store with remote data
          documentStore.updateDocument(conflict.documentId, conflict.remoteDocument)
          resolution.resolvedData = conflict.remoteDocument
          break

        case 'merge_changes':
          // Attempt automatic merge
          const mergedData = await attemptAutoMerge(conflict)
          if (mergedData) {
            // Apply merged changes
            documentStore.updateDocument(conflict.documentId, mergedData)
            confirmOperation(conflict.localOperation.id, mergedData)
            resolution.resolvedData = mergedData
          } else {
            // Fallback to user resolution if auto-merge fails
            return resolveConflict(conflictId, 'user_resolve')
          }
          break

        case 'user_resolve':
          // Use custom resolution provided by user
          if (customResolution) {
            documentStore.updateDocument(conflict.documentId, customResolution)
            confirmOperation(conflict.localOperation.id, customResolution)
            resolution.resolvedData = customResolution
          } else {
            // This should be handled by UI component
            throw new Error('User resolution requires custom resolution data')
          }
          break
      }

      // Record resolution
      setResolutionHistory(prev => [...prev, resolution])
      
      // Remove from active conflicts
      removeConflict(conflictId)
      
      console.log(`Conflict ${conflictId} resolved with strategy: ${strategy}`)
      
    } catch (error) {
      console.error(`Failed to resolve conflict ${conflictId}:`, error)
      throw error
    }
  }, [activeConflicts, rollbackOperation, documentStore, confirmOperation, removeConflict])

  // Attempt automatic merge of changes
  const attemptAutoMerge = async (conflict: ConflictInfo): Promise<Document | null> => {
    const { localOperation, remoteDocument } = conflict
    
    if (localOperation.type !== 'update') {
      return null // Can only auto-merge updates
    }

    const localChanges = localOperation.data.updates
    const mergedDocument = { ...remoteDocument }

    try {
      // Merge non-conflicting fields
      for (const [field, localValue] of Object.entries(localChanges)) {
        if (field === 'id' || field === 'upload_date') {
          continue // Skip system fields
        }

        // Handle arrays (like tags) - merge unique values
        if (Array.isArray(localValue) && Array.isArray(remoteDocument[field as keyof Document])) {
          const remoteArray = remoteDocument[field as keyof Document] as string[]
          const mergedArray = [...new Set([...remoteArray, ...localValue])]
          mergedDocument[field as keyof Document] = mergedArray as any
        }
        // Handle strings - use local value if different from remote
        else if (localValue !== remoteDocument[field as keyof Document]) {
          // Check if this is a potentially conflicting change
          if (field === 'filename' || field === 'category') {
            // These fields might conflict - return null to trigger user resolution
            return null
          }
          mergedDocument[field as keyof Document] = localValue
        }
      }

      return mergedDocument

    } catch (error) {
      console.error('Auto-merge failed:', error)
      return null
    }
  }

  // Batch resolve all conflicts with same strategy
  const resolveBatch = useCallback(async (
    conflictIds: string[], 
    strategy: ConflictResolutionStrategy
  ) => {
    const results = await Promise.allSettled(
      conflictIds.map(id => resolveConflict(id, strategy))
    )
    
    const successful = results.filter(r => r.status === 'fulfilled').length
    const failed = results.filter(r => r.status === 'rejected').length
    
    console.log(`Batch resolution completed: ${successful} successful, ${failed} failed`)
    
    return { successful, failed }
  }, [resolveConflict])

  // Get suggested resolution strategy
  const getSuggestedStrategy = useCallback((conflict: ConflictInfo): ConflictResolutionStrategy => {
    switch (conflict.type) {
      case 'concurrent_edit':
        // Suggest merge for concurrent edits
        return 'merge_changes'
        
      case 'delete_modified':
        // Suggest user resolution for delete conflicts
        return 'user_resolve'
        
      case 'version_mismatch':
        // Suggest accepting remote for version conflicts
        return 'accept_remote'
        
      case 'stale_update':
        // Suggest merge for stale updates
        return 'merge_changes'
        
      default:
        return 'user_resolve'
    }
  }, [])

  // Handle incoming remote document changes
  const handleRemoteDocumentChange = useCallback((document: Document) => {
    const conflicts = detectConflicts(document)
    
    conflicts.forEach(conflict => {
      addConflict(conflict)
    })
    
    // Auto-resolve simple conflicts if enabled
    const autoResolvableConflicts = conflicts.filter(c => 
      c.type === 'stale_update' || 
      (c.type === 'concurrent_edit' && c.localOperation.type === 'update')
    )
    
    autoResolvableConflicts.forEach(conflict => {
      const strategy = getSuggestedStrategy(conflict)
      if (strategy === 'merge_changes') {
        // Attempt auto-resolution
        resolveConflict(conflict.id, strategy).catch(error => {
          console.warn(`Auto-resolution failed for conflict ${conflict.id}:`, error)
        })
      }
    })
  }, [detectConflicts, addConflict, getSuggestedStrategy, resolveConflict])

  // Statistics
  const getConflictStats = useCallback(() => {
    const activeCount = activeConflicts.size
    const totalResolved = resolutionHistory.length
    const resolutionsByStrategy = resolutionHistory.reduce((acc, resolution) => {
      acc[resolution.strategy] = (acc[resolution.strategy] || 0) + 1
      return acc
    }, {} as Record<ConflictResolutionStrategy, number>)

    return {
      active: activeCount,
      totalResolved,
      resolutionsByStrategy,
      successRate: totalResolved / (totalResolved + activeCount) * 100
    }
  }, [activeConflicts, resolutionHistory])

  // Setup listeners for document changes
  useEffect(() => {
    // This would be connected to the WebSocket document sync events
    // For now, we'll expose the handler for external use
    // The DocumentSyncProvider would call handleRemoteDocumentChange
  }, [])

  return {
    // Conflict state
    activeConflicts: Array.from(activeConflicts.values()),
    conflictCount: activeConflicts.size,
    resolutionHistory,
    
    // Conflict operations
    resolveConflict,
    resolveBatch,
    addConflict,
    removeConflict,
    
    // Analysis
    detectConflicts,
    getSuggestedStrategy,
    handleRemoteDocumentChange,
    
    // Statistics
    getConflictStats,
    
    // Utilities
    hasActiveConflicts: activeConflicts.size > 0,
    getConflictById: (id: string) => activeConflicts.get(id),
    getConflictsForDocument: (docId: string) => 
      Array.from(activeConflicts.values()).filter(c => c.documentId === docId)
  }
}