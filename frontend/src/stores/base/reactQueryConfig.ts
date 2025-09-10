/**
 * React Query Configuration and Optimization
 * Provides standardized query patterns, caching strategies, and error handling
 */

import { 
  QueryClient, 
  QueryKey, 
  UseQueryOptions, 
  UseMutationOptions,
  UseInfiniteQueryOptions,
  QueryFunction,
  MutationFunction,
  MutationKey
} from '@tanstack/react-query'
import { toast } from 'sonner'

// ================================
// QUERY CLIENT CONFIGURATION
// ================================

export const createOptimizedQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.status >= 400 && error?.status < 500) {
          return false
        }
        return failureCount < 3
      },
      refetchOnWindowFocus: false,
      refetchOnMount: false,
      refetchOnReconnect: true,
      networkMode: 'online'
    },
    mutations: {
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.status >= 400 && error?.status < 500) {
          return false
        }
        return failureCount < 2
      },
      networkMode: 'online'
    }
  }
})

// ================================
// STANDARDIZED QUERY OPTIONS
// ================================

export interface QueryConfig<TData = unknown, TError = unknown> {
  key: QueryKey
  queryFn: QueryFunction<TData>
  options?: Partial<UseQueryOptions<TData, TError>>
  showToast?: boolean
  successMessage?: string
  errorMessage?: string
}

export interface MutationConfig<TData = unknown, TVariables = void, TError = unknown> {
  key: MutationKey
  mutationFn: MutationFunction<TData, TVariables>
  options?: Partial<UseMutationOptions<TData, TError, TVariables>>
  showToast?: boolean
  successMessage?: string
  errorMessage?: string
  invalidateQueries?: QueryKey[]
}

// ================================
// STANDARDIZED QUERY HOOKS
// ================================

export function createStandardQuery<TData = unknown, TError = unknown>(
  config: QueryConfig<TData, TError>
) {
  const {
    key,
    queryFn,
    options = {},
    showToast = true,
    successMessage,
    errorMessage = 'Failed to fetch data'
  } = config

  return {
    queryKey: key,
    queryFn,
    ...options,
    onSuccess: (data: TData) => {
      if (showToast && successMessage) {
        toast.success(successMessage)
      }
      options.onSuccess?.(data)
    },
    onError: (error: TError) => {
      if (showToast) {
        toast.error(errorMessage)
      }
      options.onError?.(error)
    }
  } as UseQueryOptions<TData, TError>
}

export function createStandardMutation<TData = unknown, TVariables = void, TError = unknown>(
  config: MutationConfig<TData, TVariables, TError>
) {
  const {
    key,
    mutationFn,
    options = {},
    showToast = true,
    successMessage,
    errorMessage = 'Failed to perform action',
    invalidateQueries = []
  } = config

  const queryClient = createOptimizedQueryClient()

  return {
    mutationKey: key,
    mutationFn,
    ...options,
    onSuccess: (data: TData, variables: TVariables, context: unknown) => {
      // Invalidate related queries
      invalidateQueries.forEach(queryKey => {
        queryClient.invalidateQueries({ queryKey })
      })

      if (showToast && successMessage) {
        toast.success(successMessage)
      }
      options.onSuccess?.(data, variables, context)
    },
    onError: (error: TError, variables: TVariables, context: unknown) => {
      if (showToast) {
        toast.error(errorMessage)
      }
      options.onError?.(error, variables, context)
    }
  } as UseMutationOptions<TData, TError, TVariables>
}

// ================================
// INFINITE QUERY HELPERS
// ================================

export interface InfiniteQueryConfig<TData = unknown, TError = unknown> {
  key: QueryKey
  queryFn: QueryFunction<TData>
  getNextPageParam: (lastPage: TData, allPages: TData[]) => unknown
  options?: Partial<UseInfiniteQueryOptions<TData, TError>>
}

export function createStandardInfiniteQuery<TData = unknown, TError = unknown>(
  config: InfiniteQueryConfig<TData, TError>
) {
  const {
    key,
    queryFn,
    getNextPageParam,
    options = {}
  } = config

  return {
    queryKey: key,
    queryFn: ({ pageParam = 1 }) => queryFn({ pageParam }),
    getNextPageParam,
    ...options,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false
  } as UseInfiniteQueryOptions<TData, TError>
}

// ================================
// COMMON QUERY KEYS
// ================================

export const queryKeys = {
  // Document queries
  documents: {
    all: ['documents'] as const,
    list: (filters?: Record<string, any>) => ['documents', 'list', filters] as const,
    detail: (id: string) => ['documents', 'detail', id] as const,
    search: (query: string) => ['documents', 'search', query] as const,
    upload: () => ['documents', 'upload'] as const,
  },
  
  // Chat queries
  chat: {
    sessions: () => ['chat', 'sessions'] as const,
    messages: (sessionId: string) => ['chat', 'messages', sessionId] as const,
    session: (sessionId: string) => ['chat', 'session', sessionId] as const,
  },
  
  // User queries
  user: {
    profile: () => ['user', 'profile'] as const,
    settings: () => ['user', 'settings'] as const,
  },
  
  // System queries
  system: {
    status: () => ['system', 'status'] as const,
    health: () => ['system', 'health'] as const,
  },
  
  // Upload queries
  upload: {
    jobs: () => ['upload', 'jobs'] as const,
    job: (jobId: string) => ['upload', 'job', jobId] as const,
    progress: (jobId: string) => ['upload', 'progress', jobId] as const,
  }
}

// ================================
// OPTIMISTIC UPDATE HELPERS
// ================================

export interface OptimisticUpdateConfig<TData, TVariables> {
  queryKey: QueryKey
  updateFn: (oldData: TData | undefined, variables: TVariables) => TData
  rollbackFn?: (oldData: TData | undefined) => TData
}

export function createOptimisticUpdate<TData = unknown, TVariables = void>(
  config: OptimisticUpdateConfig<TData, TVariables>
) {
  const { queryKey, updateFn, rollbackFn } = config
  const queryClient = createOptimizedQueryClient()

  return {
    onMutate: async (variables: TVariables) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey })
      
      // Snapshot the previous value
      const previousData = queryClient.getQueryData<TData>(queryKey)
      
      // Optimistically update to the new value
      queryClient.setQueryData<TData>(queryKey, (oldData) => 
        updateFn(oldData, variables)
      )
      
      // Return a context object with the snapshotted value
      return { previousData }
    },
    
    onError: (err: any, variables: TVariables, context: { previousData?: TData } | undefined) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      if (rollbackFn && context?.previousData !== undefined) {
        queryClient.setQueryData<TData>(queryKey, () => 
          rollbackFn(context.previousData)
        )
      } else {
        queryClient.setQueryData<TData>(queryKey, context?.previousData)
      }
    },
    
    onSettled: () => {
      // Always refetch after error or success to make sure we're in sync
      queryClient.invalidateQueries({ queryKey })
    }
  }
}

// ================================
// PREFETCHING STRATEGIES
// ================================

export class QueryPrefetcher {
  constructor(private queryClient: QueryClient) {}
  
  async prefetchDocumentList(filters?: Record<string, any>) {
    await this.queryClient.prefetchQuery({
      queryKey: queryKeys.documents.list(filters),
      queryFn: async () => {
        // This would be replaced with actual API call
        const response = await fetch('/api/documents?' + new URLSearchParams(filters || {}))
        return response.json()
      },
      staleTime: 5 * 60 * 1000 // 5 minutes
    })
  }
  
  async prefetchChatSessions() {
    await this.queryClient.prefetchQuery({
      queryKey: queryKeys.chat.sessions(),
      queryFn: async () => {
        const response = await fetch('/api/chat/sessions')
        return response.json()
      },
      staleTime: 2 * 60 * 1000 // 2 minutes
    })
  }
  
  async prefetchDocumentDetail(id: string) {
    await this.queryClient.prefetchQuery({
      queryKey: queryKeys.documents.detail(id),
      queryFn: async () => {
        const response = await fetch(`/api/documents/${id}`)
        return response.json()
      },
      staleTime: 10 * 60 * 1000 // 10 minutes
    })
  }
}

// ================================
// BACKGROUND REFETCHING
// ================================

export function setupBackgroundRefetch(queryClient: QueryClient) {
  // Set up interval-based refetching for critical data
  const intervals = [
    {
      key: queryKeys.system.status(),
      interval: 30 * 1000, // 30 seconds
      enabled: true
    },
    {
      key: queryKeys.upload.jobs(),
      interval: 5 * 1000, // 5 seconds
      enabled: true
    }
  ]
  
  intervals.forEach(({ key, interval, enabled }) => {
    if (!enabled) return
    
    const intervalId = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: key })
    }, interval)
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
      clearInterval(intervalId)
    })
  })
}

// ================================
// OFFLINE SUPPORT HELPERS
// ================================

export interface OfflineMutationConfig<TData, TVariables> {
  key: MutationKey
  mutationFn: MutationFunction<TData, TVariables>
  storageKey: string
  retryStrategy?: {
    maxRetries: number
    retryDelay: number
  }
}

export function createOfflineMutation<TData = unknown, TVariables = void>(
  config: OfflineMutationConfig<TData, TVariables>
) {
  const { key, mutationFn, storageKey, retryStrategy = { maxRetries: 3, retryDelay: 5000 } } = config
  
  return {
    mutationKey: key,
    mutationFn: async (variables: TVariables) => {
      try {
        // Try to execute the mutation
        const result = await mutationFn(variables)
        
        // Clear any stored retry data
        localStorage.removeItem(storageKey)
        
        return result
      } catch (error) {
        if (!navigator.onLine) {
          // Store the mutation for retry when online
          const retryData = {
            variables,
            timestamp: Date.now(),
            retryCount: 0
          }
          localStorage.setItem(storageKey, JSON.stringify(retryData))
        }
        throw error
      }
    },
    
    retry: (failureCount, error: any) => {
      if (failureCount >= retryStrategy.maxRetries) {
        return false
      }
      
      // Don't retry on 4xx errors
      if (error?.status >= 400 && error?.status < 500) {
        return false
      }
      
      return true
    }
  }
}

// Setup online event listener to retry offline mutations
export function setupOfflineRetry(queryClient: QueryClient) {
  window.addEventListener('online', () => {
    // Check for stored mutations and retry them
    const keys = Object.keys(localStorage)
    const mutationKeys = keys.filter(key => key.startsWith('offline_mutation_'))
    
    mutationKeys.forEach(key => {
      try {
        const mutationData = JSON.parse(localStorage.getItem(key) || '{}')
        if (mutationData.variables && mutationData.retryCount < 3) {
          // Retry the mutation
          // This would need to be integrated with the actual mutation system
          localStorage.removeItem(key)
        }
      } catch (error) {
        console.error('Failed to retry offline mutation:', error)
        localStorage.removeItem(key)
      }
    })
  })
}