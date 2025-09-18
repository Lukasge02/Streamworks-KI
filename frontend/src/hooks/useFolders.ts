/**
 * Modern React Hook for Folder Management
 * Enterprise-grade state management with React Query
 */

import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useToasts } from '@/services/toast.service'
import { apiService } from '@/services/api.service'
import { Folder, FolderTree, FolderCreate, FolderUpdate, UseFoldersReturn } from '@/types/api.types'

export function useFolders(): UseFoldersReturn {
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const toast = useToasts()

  // Queries
  const {
    data: folders = [],
    isLoading: foldersLoading,
    error: foldersError,
    refetch: refetchFolders
  } = useQuery({
    queryKey: ['folders'],
    queryFn: () => apiService.getFolders(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000,   // 10 minutes
  })

  const {
    data: folderTree = [],
    isLoading: treeLoading,
    error: treeError,
    refetch: refetchTree
  } = useQuery({
    queryKey: ['folders', 'tree'],
    queryFn: () => apiService.getFolderTree(),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  })

  // Mutations
  const createFolderMutation = useMutation({
    mutationFn: (data: FolderCreate) => apiService.createFolder(data),
    onSuccess: (newFolder) => {
      // Invalidate and refetch folder queries
      queryClient.invalidateQueries({ queryKey: ['folders'] })
      queryClient.invalidateQueries({ queryKey: ['folders', 'tree'] })
      
      // Optimistically update cache
      queryClient.setQueryData(['folders'], (old: Folder[] = []) => [
        ...old,
        newFolder
      ])
      
      toast.success(
        'Ordner erstellt',
        `Ordner "${newFolder.name}" wurde erfolgreich erstellt`
      )
      setError(null)
    },
    onError: (error: Error) => {
      const message = error.message || 'Fehler beim Erstellen des Ordners'
      setError(message)
      toast.systemError('folder-create-failed', message)
    }
  })

  const updateFolderMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: FolderUpdate }) => 
      apiService.updateFolder(id, data),
    onSuccess: (updatedFolder) => {
      // Update folder in cache
      queryClient.setQueryData(['folders'], (old: Folder[] = []) =>
        old.map(folder => folder.id === updatedFolder.id ? updatedFolder : folder)
      )
      
      // Invalidate tree to rebuild hierarchy
      queryClient.invalidateQueries({ queryKey: ['folders', 'tree'] })
      
      toast.success(
        'Ordner aktualisiert',
        `Ordner "${updatedFolder.name}" wurde erfolgreich aktualisiert`
      )
      setError(null)
    },
    onError: (error: Error) => {
      const message = error.message || 'Fehler beim Aktualisieren des Ordners'
      setError(message)
      toast.systemError('folder-update-failed', message)
    }
  })

  const deleteFolderMutation = useMutation({
    mutationFn: ({ id, force = false }: { id: string; force?: boolean }) => 
      apiService.deleteFolder(id, force),
    onSuccess: (_, { id }) => {
      // Remove folder from cache
      queryClient.setQueryData(['folders'], (old: Folder[] = []) =>
        old.filter(folder => folder.id !== id)
      )
      
      // Invalidate tree to rebuild hierarchy
      queryClient.invalidateQueries({ queryKey: ['folders', 'tree'] })
      
      // Also invalidate documents that might be in this folder
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      
      toast.success(
        'Ordner gelöscht',
        'Der Ordner wurde erfolgreich gelöscht'
      )
      setError(null)
    },
    onError: (error: Error) => {
      const message = error.message || 'Fehler beim Löschen des Ordners'
      setError(message)
      toast.systemError('folder-delete-failed', message)
    }
  })

  // Hook methods
  const createFolder = useCallback(async (data: FolderCreate): Promise<Folder> => {
    return createFolderMutation.mutateAsync(data)
  }, [createFolderMutation])

  const updateFolder = useCallback(async (id: string, data: FolderUpdate): Promise<Folder> => {
    return updateFolderMutation.mutateAsync({ id, data })
  }, [updateFolderMutation])

  const deleteFolder = useCallback(async (id: string, force: boolean = false): Promise<void> => {
    return deleteFolderMutation.mutateAsync({ id, force })
  }, [deleteFolderMutation])

  const refreshFolders = useCallback(async (): Promise<void> => {
    await Promise.all([refetchFolders(), refetchTree()])
  }, [refetchFolders, refetchTree])

  const loading = foldersLoading || treeLoading || 
    createFolderMutation.isPending || 
    updateFolderMutation.isPending || 
    deleteFolderMutation.isPending

  const combinedError = error || 
    foldersError?.message || 
    treeError?.message || 
    null

  return {
    folders,
    folderTree,
    loading,
    error: combinedError,
    createFolder,
    updateFolder,
    deleteFolder,
    refreshFolders
  }
}

// Additional hooks for specific use cases

export function useFolderTree(rootId?: string, maxDepth: number = 10) {
  return useQuery({
    queryKey: ['folders', 'tree', rootId, maxDepth],
    queryFn: () => apiService.getFolderTree(rootId, maxDepth),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  })
}

export function useFolder(id: string) {
  return useQuery({
    queryKey: ['folders', id],
    queryFn: () => apiService.getFolder(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  })
}

export function useFolderSearch() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')

  // Debounce search query
  useState(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, 300)
    
    return () => clearTimeout(timer)
  })

  const { data: results = [], isLoading, error } = useQuery({
    queryKey: ['folders', 'search', debouncedQuery],
    queryFn: () => apiService.searchFolders(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
    staleTime: 2 * 60 * 1000, // 2 minutes for search results
  })

  return {
    query,
    setQuery,
    results,
    loading: isLoading,
    error: error?.message || null
  }
}