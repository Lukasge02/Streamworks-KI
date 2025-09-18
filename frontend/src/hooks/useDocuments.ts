/**
 * Modern React Hook for Document Management
 * Enterprise-grade state management with optimistic updates
 */

import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useToasts } from '@/services/toast.service'
import { apiService } from '@/services/api.service'
import { 
  DocumentWithFolder, 
  DocumentUpdate, 
  UploadRequest, 
  Document,
  DocumentFilter,
  DocumentSort,
  BulkDeleteResponse,
  BulkMoveResponse,
  BulkReprocessResponse,
  UseDocumentsReturn 
} from '@/types/api.types'

interface UseDocumentsOptions {
  folderId?: string
  filter?: DocumentFilter
  sort?: DocumentSort
  autoRefresh?: boolean
  refreshInterval?: number
  isGlobalView?: boolean // When true, fetches all documents across folders
}

export function useDocuments(options: UseDocumentsOptions = {}): UseDocumentsReturn {
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const toast = useToasts()
  
  const {
    folderId,
    filter,
    sort = 'created_desc',
    autoRefresh = false,
    refreshInterval = 30000, // 30 seconds
    isGlobalView = false
  } = options

  // Main documents query
  const {
    data: documents = [],
    isLoading,
    error: queryError,
    refetch
  } = useQuery({
    queryKey: ['documents', folderId, filter, sort, isGlobalView],
    queryFn: () => {
      if (isGlobalView) {
        // Global view: fetch all documents across folders
        return apiService.getDocuments(undefined, filter, sort)
      } else if (folderId) {
        // Folder-specific view
        return apiService.getDocumentsByFolder(folderId, sort)
      } else {
        // No folder selected, return empty array
        return Promise.resolve([])
      }
    },
    staleTime: autoRefresh ? refreshInterval / 2 : 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchInterval: autoRefresh ? refreshInterval : false,
  })

  // Upload mutation with progress tracking
  const uploadMutation = useMutation({
    mutationFn: async (uploads: UploadRequest[]) => {
      const results: Document[] = []
      
      // Process uploads sequentially to avoid overwhelming server
      for (const upload of uploads) {
        try {
          const response = await apiService.uploadDocument(upload)
          results.push(response.document)
          
          // Optimistically add to cache
          queryClient.setQueryData(
            ['documents', upload.folder_id, filter, sort],
            (old: DocumentWithFolder[] = []) => [
              {
                ...response.document,
                folder: undefined // Will be populated on next fetch
              },
              ...old
            ]
          )
        } catch (error) {
          console.error(`Failed to upload ${upload.file.name}:`, error)
          throw error
        }
      }
      
      return results
    },
    onSuccess: (documents) => {
      // Invalidate queries to get fresh data with folder info
      queryClient.invalidateQueries({ queryKey: ['documents'] })

      if (documents.length === 1) {
        toast.success(
          'Upload erfolgreich',
          `${documents[0].filename} wurde erfolgreich hochgeladen`
        )
      } else {
        toast.success(
          'Upload erfolgreich',
          `${documents.length} Dokumente wurden erfolgreich hochgeladen`
        )
      }
      setError(null)
    },
    onError: (error: Error) => {
      const message = error.message || 'Unbekannter Upload-Fehler'
      setError(message)
      toast.systemError('upload-failed', message)
    }
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiService.deleteDocument(id),
    onMutate: async (documentId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['documents'] })
      
      // Snapshot previous values
      const previousDocuments = queryClient.getQueriesData({ queryKey: ['documents'] })
      
      // Optimistically remove document
      queryClient.setQueriesData(
        { queryKey: ['documents'] },
        (old: DocumentWithFolder[] = []) =>
          old.filter(doc => doc.id !== documentId)
      )
      
      return { previousDocuments }
    },
    onError: (error, documentId, context) => {
      // Rollback optimistic update
      if (context?.previousDocuments) {
        context.previousDocuments.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data)
        })
      }

      const message = error.message || 'Fehler beim Löschen des Dokuments'
      setError(message)
      toast.systemError('delete-failed', message)
    },
    onSuccess: () => {
      toast.success('Dokument gelöscht', 'Das Dokument wurde erfolgreich gelöscht')
      setError(null)
    },
    onSettled: () => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    }
  })

  // Bulk delete mutation
  const bulkDeleteMutation = useMutation({
    mutationFn: (documentIds: string[]) =>
      apiService.bulkDeleteDocuments({ document_ids: documentIds }),
    onSuccess: (result) => {
      const { total_deleted, total_failed } = result

      queryClient.invalidateQueries({ queryKey: ['documents'] })

      if (total_failed > 0) {
        toast.warning(
          'Bulk-Löschung teilweise erfolgreich',
          `${total_deleted} Dokumente gelöscht, ${total_failed} fehlgeschlagen`
        )
      } else {
        toast.success(
          'Bulk-Löschung erfolgreich',
          `${total_deleted} Dokumente wurden erfolgreich gelöscht`
        )
      }
      setError(null)
    },
    onError: (error: Error) => {
      const message = error.message || 'Fehler beim Bulk-Löschen der Dokumente'
      setError(message)
      toast.systemError('bulk-delete-failed', message)
    }
  })

  // Bulk move mutation
  const bulkMoveMutation = useMutation({
    mutationFn: ({ documentIds, folderId }: { documentIds: string[]; folderId: string }) =>
      apiService.bulkMoveDocuments({ document_ids: documentIds, target_folder_id: folderId }),
    onSuccess: (result) => {
      const { total_moved, total_failed } = result

      // Invalidate immediately for move operations since folder changes
      queryClient.invalidateQueries({ queryKey: ['documents'] })

      if (total_failed > 0) {
        toast.warning(
          'Bulk-Verschiebung teilweise erfolgreich',
          `${total_moved} Dokumente verschoben, ${total_failed} fehlgeschlagen`
        )
      } else {
        toast.success(
          'Bulk-Verschiebung erfolgreich',
          `${total_moved} Dokumente wurden erfolgreich verschoben`
        )
      }
      setError(null)
    },
    onError: (error: Error) => {
      const message = error.message || 'Fehler beim Verschieben der Dokumente'
      setError(message)
      toast.systemError('bulk-move-failed', message)
    }
  })

  // Bulk reprocess mutation with optimistic updates
  const bulkReprocessMutation = useMutation({
    mutationFn: (documentIds: string[]) =>
      apiService.bulkReprocessDocuments({ document_ids: documentIds }),
    onMutate: async (documentIds: string[]) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['documents'] })
      
      // Snapshot previous values
      const previousDocuments = queryClient.getQueriesData({ queryKey: ['documents'] })
      
      // Optimistically update document statuses to 'processing'
      queryClient.setQueriesData(
        { queryKey: ['documents'] },
        (old: DocumentWithFolder[] = []) =>
          old.map(doc => 
            documentIds.includes(doc.id) 
              ? { ...doc, status: 'processing' as const }
              : doc
          )
      )
      
      return { previousDocuments, documentIds }
    },
    onSuccess: (result) => {
      const { total_reprocessed, total_failed } = result

      if (total_failed > 0) {
        toast.warning(
          'Neu-Verarbeitung teilweise erfolgreich',
          `${total_reprocessed} Dokumente neu verarbeitet, ${total_failed} fehlgeschlagen`
        )
      } else {
        toast.success(
          'Neu-Verarbeitung erfolgreich',
          `${total_reprocessed} Dokumente wurden erfolgreich neu verarbeitet`
        )
      }
      setError(null)

      // Invalidate and refetch to get updated status
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['documents'] })
      }, 1000) // Delay to show processing status briefly
    },
    onError: (error: Error, documentIds, context) => {
      // Rollback optimistic update on error
      if (context?.previousDocuments) {
        context.previousDocuments.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data)
        })
      }

      const message = error.message || 'Fehler bei der Neu-Verarbeitung der Dokumente'
      setError(message)
      toast.systemError('bulk-reprocess-failed', message)
    }
  })

  // Hook methods
  const uploadDocuments = useCallback(async (uploads: UploadRequest[]): Promise<Document[]> => {
    return uploadMutation.mutateAsync(uploads)
  }, [uploadMutation])

  const deleteDocument = useCallback(async (id: string): Promise<void> => {
    return deleteMutation.mutateAsync(id)
  }, [deleteMutation])

  const bulkDeleteDocuments = useCallback(async (ids: string[]): Promise<BulkDeleteResponse> => {
    return bulkDeleteMutation.mutateAsync(ids)
  }, [bulkDeleteMutation])

  const bulkMoveDocuments = useCallback(async (ids: string[], folderId: string): Promise<BulkMoveResponse> => {
    return bulkMoveMutation.mutateAsync({ documentIds: ids, folderId })
  }, [bulkMoveMutation])

  const bulkReprocessDocuments = useCallback(async (ids: string[]): Promise<BulkReprocessResponse> => {
    return bulkReprocessMutation.mutateAsync(ids)
  }, [bulkReprocessMutation])

  const refreshDocuments = useCallback(async (): Promise<void> => {
    await refetch()
  }, [refetch])

  const loading = isLoading || 
    uploadMutation.isPending || 
    deleteMutation.isPending || 
    bulkDeleteMutation.isPending || 
    bulkMoveMutation.isPending ||
    bulkReprocessMutation.isPending

  const combinedError = error || queryError?.message || null

  return {
    documents,
    loading,
    error: combinedError,
    uploadDocuments,
    deleteDocument,
    bulkDeleteDocuments,
    bulkMoveDocuments,
    bulkReprocessDocuments,
    refreshDocuments
  }
}