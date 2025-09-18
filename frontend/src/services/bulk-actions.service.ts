/**
 * Bulk Actions Service
 * Professional bulk operations with progress tracking and error handling
 */

import { toastService } from './toast.service'
import { undoRedoService, UndoableAction } from './undo-redo.service'

export interface BulkOperation<T = any> {
  id: string
  type: string
  description: string
  items: T[]
  operation: (item: T) => Promise<void>
  undoOperation?: (item: T) => Promise<void>
  onProgress?: (completed: number, total: number, currentItem: T) => void
  onSuccess?: (results: T[]) => void
  onError?: (error: Error, failedItems: T[]) => void
  concurrency?: number
  continueOnError?: boolean
}

export interface BulkOperationResult<T = any> {
  success: boolean
  completed: T[]
  failed: Array<{ item: T; error: Error }>
  totalItems: number
  duration: number
}

export interface BulkOperationStatus {
  id: string
  isRunning: boolean
  progress: number
  currentItem?: any
  startTime?: Date
  estimatedCompletion?: Date
}

class BulkActionsService {
  private activeOperations: Map<string, BulkOperationStatus> = new Map()
  private abortControllers: Map<string, AbortController> = new Map()

  /**
   * Execute a bulk operation with progress tracking
   */
  async executeBulkOperation<T>(operation: BulkOperation<T>): Promise<BulkOperationResult<T>> {
    const {
      id,
      description,
      items,
      operation: operationFn,
      undoOperation,
      onProgress,
      onSuccess,
      onError,
      concurrency = 3,
      continueOnError = true
    } = operation

    const startTime = new Date()
    const completed: T[] = []
    const failed: Array<{ item: T; error: Error }> = []

    // Initialize status tracking
    this.activeOperations.set(id, {
      id,
      isRunning: true,
      progress: 0,
      startTime
    })

    // Create abort controller
    const abortController = new AbortController()
    this.abortControllers.set(id, abortController)

    // Show initial progress toast
    const progressToastId = toastService.progress(description, 0)

    try {
      // Process items in chunks with controlled concurrency
      const chunks = this.chunkArray(items, concurrency)
      let processedCount = 0

      for (const chunk of chunks) {
        if (abortController.signal.aborted) {
          throw new Error('Operation was cancelled')
        }

        // Process chunk concurrently
        const chunkPromises = chunk.map(async (item) => {
          try {
            await operationFn(item)
            completed.push(item)
          } catch (error) {
            failed.push({ item, error: error as Error })
            if (!continueOnError) {
              throw error
            }
          }

          processedCount++
          const progress = Math.round((processedCount / items.length) * 100)

          // Update status
          this.activeOperations.set(id, {
            id,
            isRunning: true,
            progress,
            currentItem: item,
            startTime,
            estimatedCompletion: this.estimateCompletion(startTime, progress)
          })

          // Update progress toast
          toastService.updateProgress(
            progressToastId,
            progress,
            `${description} (${processedCount}/${items.length})`
          )

          // Call progress callback
          onProgress?.(processedCount, items.length, item)
        })

        await Promise.all(chunkPromises)
      }

      const duration = Date.now() - startTime.getTime()
      const result: BulkOperationResult<T> = {
        success: failed.length === 0,
        completed,
        failed,
        totalItems: items.length,
        duration
      }

      // Complete progress toast
      if (failed.length === 0) {
        toastService.completeProgress(
          progressToastId,
          `${description} erfolgreich abgeschlossen (${completed.length} Elemente)`
        )
      } else {
        toastService.errorProgress(
          progressToastId,
          `${description} mit Fehlern abgeschlossen (${completed.length}/${items.length} erfolgreich)`
        )
      }

      // Create undoable action if undo operation is provided
      if (undoOperation && completed.length > 0) {
        const undoAction: UndoableAction = {
          id: `bulk-undo-${id}`,
          type: 'bulk-operation',
          description: `Rückgängig: ${description}`,
          timestamp: new Date(),
          execute: async () => {
            // This is already executed
          },
          undo: async () => {
            const undoProgressId = toastService.progress(`Rückgängig: ${description}`, 0)

            try {
              for (let i = 0; i < completed.length; i++) {
                await undoOperation(completed[i])
                const progress = Math.round(((i + 1) / completed.length) * 100)
                toastService.updateProgress(undoProgressId, progress, `Rückgängig: ${i + 1}/${completed.length}`)
              }

              toastService.completeProgress(undoProgressId, `${description} erfolgreich rückgängig gemacht`)
            } catch (error) {
              toastService.errorProgress(undoProgressId, `Fehler beim Rückgängigmachen: ${error}`)
              throw error
            }
          }
        }

        await undoRedoService.executeAction(undoAction)
      }

      // Call success callback
      onSuccess?.(completed)

      // Call error callback if there were failures
      if (failed.length > 0) {
        const aggregateError = new Error(`${failed.length} von ${items.length} Operationen fehlgeschlagen`)
        onError?.(aggregateError, failed.map(f => f.item))
      }

      return result

    } catch (error) {
      // Handle operation failure
      toastService.errorProgress(progressToastId, `${description} fehlgeschlagen: ${error}`)

      const result: BulkOperationResult<T> = {
        success: false,
        completed,
        failed: [...failed, ...items.slice(completed.length + failed.length).map(item => ({ item, error: error as Error }))],
        totalItems: items.length,
        duration: Date.now() - startTime.getTime()
      }

      onError?.(error as Error, items)
      return result

    } finally {
      // Cleanup
      this.activeOperations.delete(id)
      this.abortControllers.delete(id)
    }
  }

  /**
   * Cancel a running bulk operation
   */
  cancelOperation(operationId: string): void {
    const abortController = this.abortControllers.get(operationId)
    if (abortController) {
      abortController.abort()
      toastService.warning(`Operation "${operationId}" wurde abgebrochen`)
    }
  }

  /**
   * Get status of a bulk operation
   */
  getOperationStatus(operationId: string): BulkOperationStatus | undefined {
    return this.activeOperations.get(operationId)
  }

  /**
   * Get all active operations
   */
  getActiveOperations(): BulkOperationStatus[] {
    return Array.from(this.activeOperations.values())
  }

  /**
   * Create common bulk operations
   */
  createDocumentBulkDelete(documentIds: string[]): BulkOperation<string> {
    return {
      id: `bulk-delete-docs-${Date.now()}`,
      type: 'document-delete',
      description: `${documentIds.length} Dokumente löschen`,
      items: documentIds,
      operation: async (documentId: string) => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))
        console.log(`Deleting document ${documentId}`)
      },
      undoOperation: async (documentId: string) => {
        // Simulate restore
        await new Promise(resolve => setTimeout(resolve, 300))
        console.log(`Restoring document ${documentId}`)
      },
      concurrency: 5,
      continueOnError: true
    }
  }

  createDocumentBulkMove(documentIds: string[], targetFolderId: string): BulkOperation<string> {
    return {
      id: `bulk-move-docs-${Date.now()}`,
      type: 'document-move',
      description: `${documentIds.length} Dokumente verschieben`,
      items: documentIds,
      operation: async (documentId: string) => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 300))
        console.log(`Moving document ${documentId} to folder ${targetFolderId}`)
      },
      undoOperation: async (documentId: string) => {
        // Simulate move back
        await new Promise(resolve => setTimeout(resolve, 300))
        console.log(`Moving document ${documentId} back to original location`)
      },
      concurrency: 3,
      continueOnError: true
    }
  }

  createDocumentBulkDownload(documentIds: string[]): BulkOperation<string> {
    return {
      id: `bulk-download-docs-${Date.now()}`,
      type: 'document-download',
      description: `${documentIds.length} Dokumente herunterladen`,
      items: documentIds,
      operation: async (documentId: string) => {
        // Simulate download
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log(`Downloading document ${documentId}`)
      },
      concurrency: 2, // Slower for downloads
      continueOnError: true
    }
  }

  createFolderBulkDelete(folderIds: string[]): BulkOperation<string> {
    return {
      id: `bulk-delete-folders-${Date.now()}`,
      type: 'folder-delete',
      description: `${folderIds.length} Ordner löschen`,
      items: folderIds,
      operation: async (folderId: string) => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 400))
        console.log(`Deleting folder ${folderId}`)
      },
      undoOperation: async (folderId: string) => {
        // Simulate restore
        await new Promise(resolve => setTimeout(resolve, 400))
        console.log(`Restoring folder ${folderId}`)
      },
      concurrency: 3,
      continueOnError: false // Don't continue on folder delete errors
    }
  }

  /**
   * Utility methods
   */
  private chunkArray<T>(array: T[], chunkSize: number): T[][] {
    const chunks: T[][] = []
    for (let i = 0; i < array.length; i += chunkSize) {
      chunks.push(array.slice(i, i + chunkSize))
    }
    return chunks
  }

  private estimateCompletion(startTime: Date, progress: number): Date | undefined {
    if (progress <= 0) return undefined

    const elapsed = Date.now() - startTime.getTime()
    const rate = progress / elapsed
    const remaining = (100 - progress) / rate

    return new Date(Date.now() + remaining)
  }
}

export const bulkActionsService = new BulkActionsService()

// Import React for the hook
import React from 'react'

// React hook for easier integration
export const useBulkActions = () => {
  const [activeOperations, setActiveOperations] = React.useState<BulkOperationStatus[]>([])

  React.useEffect(() => {
    const interval = setInterval(() => {
      setActiveOperations(bulkActionsService.getActiveOperations())
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  return {
    activeOperations,
    executeOperation: (operation: BulkOperation) => bulkActionsService.executeBulkOperation(operation),
    cancelOperation: (id: string) => bulkActionsService.cancelOperation(id),
    getStatus: (id: string) => bulkActionsService.getOperationStatus(id),

    // Predefined operations
    bulkDeleteDocuments: (ids: string[]) => bulkActionsService.createDocumentBulkDelete(ids),
    bulkMoveDocuments: (ids: string[], folderId: string) => bulkActionsService.createDocumentBulkMove(ids, folderId),
    bulkDownloadDocuments: (ids: string[]) => bulkActionsService.createDocumentBulkDownload(ids),
    bulkDeleteFolders: (ids: string[]) => bulkActionsService.createFolderBulkDelete(ids)
  }
}