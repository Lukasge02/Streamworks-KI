/**
 * Unified Base Store Pattern for StreamWorks Frontend
 * Provides consistent structure, TypeScript patterns, and common utilities
 */

import { create, StoreApi, UseBoundStore } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import { enableMapSet } from 'immer'

// Enable Immer MapSet plugin for all stores
enableMapSet()

// ================================
// BASE TYPES
// ================================

export interface BaseStoreState {
  // Common UI state
  isLoading: boolean
  error: string | null
  lastUpdated: string | null
  
  // Common actions
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
  setLastUpdated: (timestamp: string) => void
}

export interface AsyncState<T> {
  data: T | null
  isLoading: boolean
  error: string | null
  lastFetched: string | null
}

export interface AsyncActions<T> {
  setData: (data: T) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearData: () => void
  refetch: () => Promise<void>
}

// ================================
// BASE STORE WITH MIDDLEWARE
// ================================

export interface StoreConfig<TState> {
  name: string
  devtoolsName?: string
  persistOptions?: {
    name: string
    partialize?: (state: TState) => Partial<TState>
  }
  enableDevtools?: boolean
  enablePersist?: boolean
}

export function createBaseStore<TState extends object>(
  initialState: TState,
  config: StoreConfig<TState>
) {
  let storeCreator = create<TState>
  
  // Add Immer middleware
  storeCreator = immer(storeCreator)
  
  // Add DevTools middleware
  if (config.enableDevtools !== false) {
    storeCreator = devtools(storeCreator, {
      name: config.devtoolsName || config.name
    })
  }
  
  // Add Persist middleware
  if (config.enablePersist && config.persistOptions) {
    storeCreator = persist(storeCreator, config.persistOptions)
  }
  
  return storeCreator(initialState)
}

// ================================
// ASYNC STATE HELPERS
// ================================

export function createAsyncState<T>(initialData: T | null = null): AsyncState<T> {
  return {
    data: initialData,
    isLoading: false,
    error: null,
    lastFetched: null
  }
}

export function createAsyncActions<T>(
  set: StoreApi<AsyncState<T>>['setState'],
  get: StoreApi<AsyncState<T>>['getState'],
  fetchFn: () => Promise<T>
): AsyncActions<T> {
  return {
    setData: (data: T) => set((state) => {
      state.data = data
      state.error = null
      state.lastFetched = new Date().toISOString()
    }),
    
    setLoading: (loading: boolean) => set((state) => {
      state.isLoading = loading
    }),
    
    setError: (error: string | null) => set((state) => {
      state.error = error
      state.isLoading = false
    }),
    
    clearData: () => set((state) => {
      state.data = null
      state.error = null
      state.lastFetched = null
    }),
    
    refetch: async () => {
      set((state) => {
        state.isLoading = true
        state.error = null
      })
      
      try {
        const data = await fetchFn()
        set((state) => {
          state.data = data
          state.error = null
          state.isLoading = false
          state.lastFetched = new Date().toISOString()
        })
      } catch (error) {
        set((state) => {
          state.error = error instanceof Error ? error.message : 'Unknown error'
          state.isLoading = false
        })
      }
    }
  }
}

// ================================
// COMMON STORE UTILITIES
// ================================

export function createBaseActions<TState extends BaseStoreState>(
  set: StoreApi<TState>['setState']
) {
  return {
    setLoading: (loading: boolean) => set((state) => {
      state.isLoading = loading
    }),
    
    setError: (error: string | null) => set((state) => {
      state.error = error
    }),
    
    clearError: () => set((state) => {
      state.error = null
    }),
    
    setLastUpdated: (timestamp: string) => set((state) => {
      state.lastUpdated = timestamp
    })
  }
}

// ================================
// SELECTION UTILITIES
// ================================

export function createSelectors<TState>(store: UseBoundStore<StoreApi<TState>>) {
  return {
    getState: store.getState,
    subscribe: store.subscribe,
    destroy: store.destroy,
    
    // Common derived state helpers
    isLoading: () => store.getState().isLoading,
    error: () => store.getState().error,
    hasError: () => !!store.getState().error,
    lastUpdated: () => store.getState().lastUpdated
  }
}

// ================================
// PAGINATION HELPERS
// ================================

export interface PaginationState {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

export interface PaginationActions {
  setPage: (page: number) => void
  setPageSize: (pageSize: number) => void
  setTotal: (total: number) => void
  nextPage: () => void
  prevPage: () => void
  resetPagination: () => void
}

export function createPaginationState(initialPageSize = 20): PaginationState {
  return {
    page: 1,
    pageSize: initialPageSize,
    total: 0,
    totalPages: 0
  }
}

export function createPaginationActions(
  set: StoreApi<PaginationState>['setState'],
  get: StoreApi<PaginationState>['getState']
): PaginationActions {
  return {
    setPage: (page: number) => set((state) => {
      state.page = Math.max(1, page)
    }),
    
    setPageSize: (pageSize: number) => set((state) => {
      state.pageSize = Math.max(1, pageSize)
      state.page = 1 // Reset to first page when changing page size
    }),
    
    setTotal: (total: number) => set((state) => {
      state.total = total
      state.totalPages = Math.ceil(total / state.pageSize)
    }),
    
    nextPage: () => set((state) => {
      if (state.page < state.totalPages) {
        state.page += 1
      }
    }),
    
    prevPage: () => set((state) => {
      if (state.page > 1) {
        state.page -= 1
      }
    }),
    
    resetPagination: () => set((state) => {
      state.page = 1
      state.total = 0
      state.totalPages = 0
    })
  }
}

// ================================
// SEARCH AND FILTER HELPERS
// ================================

export interface SearchFilters {
  query: string
  category?: string
  status?: string
  dateRange?: {
    start: string | null
    end: string | null
  }
  tags?: string[]
}

export interface FilterActions {
  setQuery: (query: string) => void
  setCategory: (category: string | undefined) => void
  setStatus: (status: string | undefined) => void
  setDateRange: (range: { start: string | null; end: string | null }) => void
  setTags: (tags: string[]) => void
  addTag: (tag: string) => void
  removeTag: (tag: string) => void
  clearFilters: () => void
}

export function createSearchFilters(): SearchFilters {
  return {
    query: '',
    category: undefined,
    status: undefined,
    dateRange: { start: null, end: null },
    tags: []
  }
}

export function createFilterActions(
  set: StoreApi<SearchFilters>['setState'],
  get: StoreApi<SearchFilters>['getState']
): FilterActions {
  return {
    setQuery: (query: string) => set((state) => {
      state.query = query
      return state
    }),
    
    setCategory: (category: string | undefined) => set((state) => {
      state.category = category
      return state
    }),
    
    setStatus: (status: string | undefined) => set((state) => {
      state.status = status
      return state
    }),
    
    setDateRange: (range: { start: string | null; end: string | null }) => set((state) => {
      state.dateRange = range
      return state
    }),
    
    setTags: (tags: string[]) => set((state) => {
      state.tags = tags
      return state
    }),
    
    addTag: (tag: string) => set((state) => {
      if (!state.tags?.includes(tag)) {
        state.tags = state.tags || []
        state.tags.push(tag)
      }
      return state
    }),
    
    removeTag: (tag: string) => set((state) => {
      state.tags = state.tags?.filter(t => t !== tag) || []
      return state
    }),
    
    clearFilters: () => set((state) => {
      state.query = ''
      state.category = undefined
      state.status = undefined
      state.dateRange = { start: null, end: null }
      state.tags = []
      return state
    })
  }
}

// ================================
// STORE COMPOSITION HELPERS
// ================================

export function composeStores<T extends object, U extends object>(
  storeA: UseBoundStore<StoreApi<T>>,
  storeB: UseBoundStore<StoreApi<U>>
): UseBoundStore<StoreApi<T & U>> {
  return create<T & U>()((set, get, api) => ({
    ...storeA.getState(),
    ...storeB.getState(),
    ...Object.fromEntries(
      Object.entries(storeA.getState()).map(([key, value]) => [
        key,
        typeof value === 'function' ? (...args: any[]) => value(...args) : value
      ])
    ),
    ...Object.fromEntries(
      Object.entries(storeB.getState()).map(([key, value]) => [
        key,
        typeof value === 'function' ? (...args: any[]) => value(...args) : value
      ])
    )
  }))
}