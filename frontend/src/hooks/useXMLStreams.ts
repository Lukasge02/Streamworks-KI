/**
 * React Query hooks for XML Stream management
 * Provides reactive state management for streams with caching and optimistic updates
 */
'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import xmlStreamsApi, { 
  XMLStream, 
  StreamFilters, 
  CreateStreamRequest, 
  UpdateStreamRequest,
  AutoSaveRequest 
} from '@/services/xmlStreamsApi'

// Query keys for consistent cache management
export const streamQueryKeys = {
  all: ['xml-streams'] as const,
  lists: () => [...streamQueryKeys.all, 'list'] as const,
  list: (filters: StreamFilters, sortBy: string, limit: number, offset: number) => 
    [...streamQueryKeys.lists(), { filters, sortBy, limit, offset }] as const,
  details: () => [...streamQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...streamQueryKeys.details(), id] as const,
  stats: () => [...streamQueryKeys.all, 'stats'] as const,
}

/**
 * Hook to fetch list of streams with filtering and pagination
 */
export function useStreamList(
  filters: StreamFilters = {},
  sortBy: string = 'updated_desc',
  limit: number = 50,
  offset: number = 0,
  options?: {
    enabled?: boolean
    refetchInterval?: number
  }
) {
  return useQuery({
    queryKey: streamQueryKeys.list(filters, sortBy, limit, offset),
    queryFn: () => xmlStreamsApi.listStreams(filters, sortBy, limit, offset),
    enabled: options?.enabled !== false,
    refetchInterval: options?.refetchInterval,
    staleTime: 30000, // 30 seconds
    gcTime: 300000, // 5 minutes
  })
}

/**
 * Hook to fetch a specific stream by ID
 */
export function useStream(streamId: string | undefined, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: streamQueryKeys.detail(streamId || ''),
    queryFn: () => xmlStreamsApi.getStream(streamId!),
    enabled: !!streamId && options?.enabled !== false,
    staleTime: 60000, // 1 minute
    gcTime: 300000, // 5 minutes
  })
}

/**
 * Hook to fetch stream statistics
 */
export function useStreamStats() {
  return useQuery({
    queryKey: streamQueryKeys.stats(),
    queryFn: () => xmlStreamsApi.getStats(),
    staleTime: 60000, // 1 minute
    gcTime: 300000, // 5 minutes
  })
}

/**
 * Hook to create a new stream
 */
export function useCreateStream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateStreamRequest) => xmlStreamsApi.createStream(data),
    onSuccess: (newStream) => {
      // Invalidate and refetch stream lists
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.stats() })
      
      // Add to cache
      queryClient.setQueryData(streamQueryKeys.detail(newStream.id), newStream)
      
      toast.success(`Stream "${newStream.stream_name}" erfolgreich erstellt!`)
    },
    onError: (error: Error) => {
      toast.error(`Fehler beim Erstellen: ${error.message}`)
    },
  })
}

/**
 * Hook to update an existing stream
 */
export function useUpdateStream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ 
      streamId, 
      data, 
      createVersion = true 
    }: { 
      streamId: string
      data: UpdateStreamRequest
      createVersion?: boolean 
    }) => xmlStreamsApi.updateStream(streamId, data, createVersion),
    onMutate: async ({ streamId, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: streamQueryKeys.detail(streamId) })

      // Snapshot previous value
      const previousStream = queryClient.getQueryData<XMLStream>(streamQueryKeys.detail(streamId))

      // Optimistically update the cache
      if (previousStream) {
        queryClient.setQueryData<XMLStream>(streamQueryKeys.detail(streamId), (old) => ({
          ...old!,
          ...data,
          updated_at: new Date().toISOString(),
        }))
      }

      return { previousStream }
    },
    onSuccess: (updatedStream, { streamId }) => {
      // Update cache with server response
      queryClient.setQueryData(streamQueryKeys.detail(streamId), updatedStream)
      
      // Invalidate lists to refresh
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.stats() })
      
      toast.success(`Stream "${updatedStream.stream_name}" aktualisiert!`)
    },
    onError: (error: Error, { streamId }, context) => {
      console.error('❌ useUpdateStream - Error occurred:', {
        error,
        streamId,
        errorName: error.name,
        errorMessage: error.message,
        errorStack: error.stack,
        response: (error as any)?.response,
        status: (error as any)?.response?.status,
        statusText: (error as any)?.response?.statusText,
        data: (error as any)?.response?.data
      })

      // Revert optimistic update on error
      if (context?.previousStream) {
        console.log('🔄 Reverting optimistic update for stream:', streamId)
        queryClient.setQueryData(streamQueryKeys.detail(streamId), context.previousStream)
      }

      // Enhanced error message based on error type
      let errorMessage = error.message || 'Unbekannter Fehler'

      if ((error as any)?.response?.status === 404) {
        errorMessage = 'Stream nicht gefunden'
      } else if ((error as any)?.response?.status === 422) {
        errorMessage = 'Ungültige Daten - bitte überprüfen Sie Ihre Eingaben'
      } else if ((error as any)?.response?.status === 500) {
        errorMessage = 'Server-Fehler - bitte versuchen Sie es später erneut'
      } else if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
        errorMessage = 'Netzwerk-Fehler - bitte überprüfen Sie Ihre Internetverbindung'
      }

      toast.error(`Fehler beim Aktualisieren: ${errorMessage}`)
    },
  })
}

/**
 * Hook for auto-saving stream data (lightweight updates)
 */
export function useAutoSaveStream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ streamId, data }: { streamId: string; data: AutoSaveRequest }) =>
      xmlStreamsApi.autoSaveStream(streamId, data),
    onSuccess: (updatedStream, { streamId }) => {
      // Update cache silently (no toast notification for auto-save)
      queryClient.setQueryData(streamQueryKeys.detail(streamId), updatedStream)
      
      // Update lists cache if present
      queryClient.setQueriesData(
        { queryKey: streamQueryKeys.lists() },
        (oldData: any) => {
          if (!oldData?.streams) return oldData
          return {
            ...oldData,
            streams: oldData.streams.map((stream: XMLStream) =>
              stream.id === streamId ? updatedStream : stream
            ),
          }
        }
      )
    },
    onError: (error: Error) => {
      console.warn('Auto-save failed:', error.message)
      // Don't show toast for auto-save failures to avoid spam
    },
  })
}

/**
 * Hook to delete a stream
 */
export function useDeleteStream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (streamId: string) => xmlStreamsApi.deleteStream(streamId),
    onMutate: async (streamId) => {
      // Get stream name for toast
      const stream = queryClient.getQueryData<XMLStream>(streamQueryKeys.detail(streamId))
      return { streamName: stream?.stream_name || 'Stream' }
    },
    onSuccess: (_, streamId, context) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: streamQueryKeys.detail(streamId) })
      
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.stats() })
      
      toast.success(`"${context?.streamName}" wurde gelöscht`)
    },
    onError: (error: Error) => {
      toast.error(`Fehler beim Löschen: ${error.message}`)
    },
  })
}

/**
 * Hook to duplicate a stream
 */
export function useDuplicateStream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ streamId, newName }: { streamId: string; newName?: string }) =>
      xmlStreamsApi.duplicateStream(streamId, newName),
    onSuccess: (newStream) => {
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.stats() })
      
      // Add to cache
      queryClient.setQueryData(streamQueryKeys.detail(newStream.id), newStream)
      
      toast.success(`Stream "${newStream.stream_name}" wurde dupliziert!`)
    },
    onError: (error: Error) => {
      toast.error(`Fehler beim Duplizieren: ${error.message}`)
    },
  })
}

/**
 * Hook to toggle favorite status
 */
export function useToggleFavorite() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (streamId: string) => xmlStreamsApi.toggleFavorite(streamId),
    onMutate: async (streamId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: streamQueryKeys.detail(streamId) })

      // Get previous value
      const previousStream = queryClient.getQueryData<XMLStream>(streamQueryKeys.detail(streamId))

      // Optimistically update
      if (previousStream) {
        queryClient.setQueryData<XMLStream>(streamQueryKeys.detail(streamId), {
          ...previousStream,
          is_favorite: !previousStream.is_favorite,
        })
      }

      return { previousStream }
    },
    onSuccess: (updatedStream, streamId) => {
      // Update cache
      queryClient.setQueryData(streamQueryKeys.detail(streamId), updatedStream)
      
      // Update lists
      queryClient.setQueriesData(
        { queryKey: streamQueryKeys.lists() },
        (oldData: any) => {
          if (!oldData?.streams) return oldData
          return {
            ...oldData,
            streams: oldData.streams.map((stream: XMLStream) =>
              stream.id === streamId ? updatedStream : stream
            ),
          }
        }
      )
      
      // Refresh stats
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.stats() })
      
      const action = updatedStream.is_favorite ? 'zu Favoriten hinzugefügt' : 'aus Favoriten entfernt'
      toast.success(`"${updatedStream.stream_name}" ${action}`)
    },
    onError: (error: Error, streamId, context) => {
      // Revert optimistic update
      if (context?.previousStream) {
        queryClient.setQueryData(streamQueryKeys.detail(streamId), context.previousStream)
      }
      toast.error(`Fehler beim Favorisieren: ${error.message}`)
    },
  })
}

/**
 * Hook for bulk operations
 */
export function useBulkOperations() {
  const queryClient = useQueryClient()

  const bulkDelete = useMutation({
    mutationFn: (streamIds: string[]) => xmlStreamsApi.bulkDeleteStreams(streamIds),
    onSuccess: (result) => {
      // Invalidate all stream data
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.all })
      toast.success(`${result.processed} von ${result.total} Streams gelöscht`)
    },
    onError: (error: Error) => {
      toast.error(`Fehler beim Löschen: ${error.message}`)
    },
  })

  const bulkToggleFavorite = useMutation({
    mutationFn: (streamIds: string[]) => xmlStreamsApi.bulkToggleFavorite(streamIds),
    onSuccess: (result) => {
      // Invalidate all stream data
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.all })
      toast.success(`${result.processed} von ${result.total} Streams aktualisiert`)
    },
    onError: (error: Error) => {
      toast.error(`Fehler beim Favorisieren: ${error.message}`)
    },
  })

  return { bulkDelete, bulkToggleFavorite }
}

/**
 * Hook to export a stream
 */
export function useExportStream() {
  return useMutation({
    mutationFn: ({ streamId, format }: { streamId: string; format: 'xml' | 'json' }) =>
      xmlStreamsApi.exportStream(streamId, format),
    onSuccess: (blob, { streamId, format }) => {
      // Download the file
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `stream_${streamId}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success(`Stream als ${format.toUpperCase()} exportiert!`)
    },
    onError: (error: Error) => {
      toast.error(`Fehler beim Exportieren: ${error.message}`)
    },
  })
}

// Utility function to invalidate all stream queries
export function useInvalidateStreams() {
  const queryClient = useQueryClient()

  return () => {
    queryClient.invalidateQueries({ queryKey: streamQueryKeys.all })
  }
}

/**
 * Hook to submit stream for review
 */
export function useSubmitForReview() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (streamId: string) => xmlStreamsApi.submitForReview(streamId),
    onSuccess: (updatedStream) => {
      // Update cache
      queryClient.setQueryData(streamQueryKeys.detail(updatedStream.id), updatedStream)
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.stats() })

      toast.success(`Stream "${updatedStream.stream_name}" zur Freigabe eingereicht!`)
    },
    onError: (error: Error) => {
      toast.error(`Fehler bei Freigabe-Einreichung: ${error.message}`)
    },
  })
}

/**
 * Hook to approve stream (expert action)
 */
export function useApproveStream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (streamId: string) => xmlStreamsApi.approveStream(streamId),
    onSuccess: (updatedStream) => {
      // Update cache
      queryClient.setQueryData(streamQueryKeys.detail(updatedStream.id), updatedStream)
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.stats() })

      toast.success(`Stream "${updatedStream.stream_name}" freigegeben!`, {
        description: 'Stream kann nun veröffentlicht werden.'
      })
    },
    onError: (error: Error) => {
      toast.error(`Fehler bei Freigabe: ${error.message}`)
    },
  })
}

/**
 * Hook to reject stream (expert action)
 */
export function useRejectStream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ streamId, reason }: { streamId: string; reason: string }) =>
      xmlStreamsApi.rejectStream(streamId, reason),
    onSuccess: (updatedStream) => {
      // Update cache
      queryClient.setQueryData(streamQueryKeys.detail(updatedStream.id), updatedStream)
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.stats() })

      toast.error(`Stream "${updatedStream.stream_name}" abgelehnt`, {
        description: 'Stream wurde zur Überarbeitung zurückgeschickt.'
      })
    },
    onError: (error: Error) => {
      toast.error(`Fehler bei Ablehnung: ${error.message}`)
    },
  })
}

/**
 * Hook to publish stream (expert action)
 */
export function usePublishStream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (streamId: string) => xmlStreamsApi.publishStream(streamId),
    onSuccess: (updatedStream) => {
      // Update cache
      queryClient.setQueryData(streamQueryKeys.detail(updatedStream.id), updatedStream)
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.lists() })
      queryClient.invalidateQueries({ queryKey: streamQueryKeys.stats() })

      toast.success(`Stream "${updatedStream.stream_name}" veröffentlicht! 🎉`, {
        description: 'Stream ist jetzt live und produktiv.'
      })
    },
    onError: (error: Error) => {
      toast.error(`Fehler bei Veröffentlichung: ${error.message}`)
    },
  })
}