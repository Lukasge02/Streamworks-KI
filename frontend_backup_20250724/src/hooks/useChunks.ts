import { useState, useEffect, useCallback, useRef } from 'react';
import { chunksApiService, ChunksApiError } from '../services/chunksApiService';
import { 
  Chunk, 
  ChunkDetailsResponse, 
  ChunksStatisticsResponse 
} from '../types';

// Hook options and configurations
interface UseChunksOptions {
  limit?: number;
  autoLoad?: boolean;
  enableCache?: boolean;
  refetchInterval?: number;
}

interface UseChunksSearchOptions {
  debounceMs?: number;
  minQueryLength?: number;
  autoSearch?: boolean;
}

interface UseChunkDetailsOptions {
  autoLoad?: boolean;
  enableCache?: boolean;
}

// Loading states
interface LoadingState {
  initial: boolean;
  refresh: boolean;
  loadMore: boolean;
  search: boolean;
}

// Error state
interface ErrorState {
  message: string;
  code?: string;
  retryable: boolean;
  timestamp: number;
}

// Chunks list hook return type
interface UseChunksReturn {
  // Data
  chunks: Chunk[];
  total: number;
  hasMore: boolean;
  currentPage: number;
  
  // Loading states
  loading: LoadingState;
  
  // Error handling
  error: ErrorState | null;
  
  // Actions
  loadChunks: () => Promise<void>;
  loadMore: () => Promise<void>;
  refresh: () => Promise<void>;
  setPage: (page: number) => void;
  clearError: () => void;
  retry: () => Promise<void>;
  
  // Filters
  filters: {
    search: string;
    sourceFile: string;
    category: string;
    sortBy: string;
    sortOrder: string;
  };
  updateFilters: (newFilters: Partial<UseChunksReturn['filters']>) => void;
  clearFilters: () => void;
}

// Search hook return type
interface UseChunksSearchReturn {
  // Data
  searchResults: Chunk[];
  searchQuery: string;
  
  // Loading and error
  isSearching: boolean;
  searchError: ErrorState | null;
  
  // Actions
  search: (query: string) => Promise<void>;
  clearSearch: () => void;
  clearSearchError: () => void;
}

// Chunk details hook return type
interface UseChunkDetailsReturn {
  // Data
  chunk: ChunkDetailsResponse | null;
  
  // Loading and error
  loading: boolean;
  error: ErrorState | null;
  
  // Actions
  loadChunk: (chunkId: string) => Promise<void>;
  clearError: () => void;
  retry: () => Promise<void>;
}

// Statistics hook return type
interface UseChunksStatisticsReturn {
  // Data
  statistics: ChunksStatisticsResponse | null;
  
  // Loading and error
  loading: boolean;
  error: ErrorState | null;
  
  // Actions
  loadStatistics: () => Promise<void>;
  refresh: () => Promise<void>;
  clearError: () => void;
}

/**
 * Hook for managing chunks list with pagination, filtering, and caching
 */
export function useChunks(options: UseChunksOptions = {}): UseChunksReturn {
  const {
    limit = 20,
    autoLoad = true,
    refetchInterval
  } = options;

  // State
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState<LoadingState>({
    initial: false,
    refresh: false,
    loadMore: false,
    search: false,
  });
  const [error, setError] = useState<ErrorState | null>(null);
  
  // Filters
  const [filters, setFilters] = useState({
    search: '',
    sourceFile: '',
    category: '',
    sortBy: 'creation_date',
    sortOrder: 'desc',
  });

  // Refs for cleanup and current values
  const abortControllerRef = useRef<AbortController | null>(null);
  const refetchIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const filtersRef = useRef(filters);
  filtersRef.current = filters;

  // Helper to create error state
  const createErrorState = useCallback((error: any): ErrorState => ({
    message: error instanceof ChunksApiError ? error.message : error.message || 'Unknown error',
    code: error instanceof ChunksApiError ? error.code : undefined,
    retryable: error instanceof ChunksApiError ? error.retryable : true,
    timestamp: Date.now(),
  }), []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Load chunks with current filters and page
  const loadChunks = useCallback(async (page: number = currentPage, append: boolean = false) => {
    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      // Set appropriate loading state
      if (page === 1 && !append) {
        setLoading(prev => ({ ...prev, initial: !chunks.length, refresh: chunks.length > 0 }));
      } else {
        setLoading(prev => ({ ...prev, loadMore: true }));
      }

      clearError();

      const offset = (page - 1) * limit;
      const response = await chunksApiService.getChunks({
        limit,
        offset,
        search: filtersRef.current.search || undefined,
        sourceFile: filtersRef.current.sourceFile || undefined,
        category: filtersRef.current.category || undefined,
        sortBy: filtersRef.current.sortBy,
        sortOrder: filtersRef.current.sortOrder,
      });

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to load chunks');
      }

      const { chunks: newChunks, total: newTotal, has_more } = response.data;

      if (append && page > 1) {
        setChunks(prev => [...prev, ...newChunks]);
      } else {
        setChunks(newChunks);
      }
      
      setTotal(newTotal);
      setHasMore(has_more);
      setCurrentPage(page);

    } catch (error: any) {
      if (error.name !== 'AbortError') {
        setError(createErrorState(error));
      }
    } finally {
      setLoading({
        initial: false,
        refresh: false,
        loadMore: false,
        search: false,
      });
      abortControllerRef.current = null;
    }
  }, [currentPage, limit, chunks.length, createErrorState]);

  // Load more chunks
  const loadMore = useCallback(async () => {
    if (!hasMore || loading.loadMore) return;
    await loadChunks(currentPage + 1, true);
  }, [hasMore, loading.loadMore, loadChunks, currentPage]);

  // Refresh current data
  const refresh = useCallback(async () => {
    await loadChunks(1, false);
  }, [loadChunks]);

  // Set page
  const setPage = useCallback((page: number) => {
    if (page !== currentPage) {
      loadChunks(page, false);
    }
  }, [currentPage, loadChunks]);

  // Retry last operation
  const retry = useCallback(async () => {
    await loadChunks(currentPage, false);
  }, [loadChunks, currentPage]);

  // Update filters
  const updateFilters = useCallback((newFilters: Partial<typeof filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    // Reset to first page when filters change
    if (Object.keys(newFilters).length > 0) {
      setCurrentPage(1);
    }
  }, []);

  // Clear filters
  const clearFilters = useCallback(() => {
    setFilters({
      search: '',
      sourceFile: '',
      category: '',
      sortBy: 'creation_date',
      sortOrder: 'desc',
    });
    setCurrentPage(1);
  }, []);

  // Effect for auto-loading
  useEffect(() => {
    if (autoLoad) {
      loadChunks(1, false);
    }
  }, [filters]); // Reload when filters change

  // Effect for refetch interval
  useEffect(() => {
    if (refetchInterval && refetchInterval > 0) {
      refetchIntervalRef.current = setInterval(() => {
        if (!loading.initial && !loading.refresh && !loading.loadMore) {
          refresh();
        }
      }, refetchInterval);

      return () => {
        if (refetchIntervalRef.current) {
          clearInterval(refetchIntervalRef.current);
        }
      };
    }
  }, [refetchInterval, loading, refresh]);

  // Cleanup effect
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (refetchIntervalRef.current) {
        clearInterval(refetchIntervalRef.current);
      }
    };
  }, []);

  return {
    // Data
    chunks,
    total,
    hasMore,
    currentPage,
    
    // Loading states
    loading,
    
    // Error handling
    error,
    
    // Actions
    loadChunks: () => loadChunks(1, false),
    loadMore,
    refresh,
    setPage,
    clearError,
    retry,
    
    // Filters
    filters,
    updateFilters,
    clearFilters,
  };
}

/**
 * Hook for searching chunks with debouncing
 */
export function useChunksSearch(options: UseChunksSearchOptions = {}): UseChunksSearchReturn {
  const {
    debounceMs = 300,
    minQueryLength = 2,
    autoSearch = true
  } = options;

  const [searchResults, setSearchResults] = useState<Chunk[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<ErrorState | null>(null);

  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const createErrorState = useCallback((error: any): ErrorState => ({
    message: error instanceof ChunksApiError ? error.message : error.message || 'Search failed',
    code: error instanceof ChunksApiError ? error.code : undefined,
    retryable: error instanceof ChunksApiError ? error.retryable : true,
    timestamp: Date.now(),
  }), []);

  const performSearch = useCallback(async (query: string) => {
    if (!query || query.length < minQueryLength) {
      setSearchResults([]);
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      setIsSearching(true);
      setSearchError(null);

      const response = await chunksApiService.searchChunks(query, 50);

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Search failed');
      }

      setSearchResults(response.data.chunks);

    } catch (error: any) {
      if (error.name !== 'AbortError') {
        setSearchError(createErrorState(error));
      }
    } finally {
      setIsSearching(false);
      abortControllerRef.current = null;
    }
  }, [minQueryLength, createErrorState]);

  const search = useCallback(async (query: string) => {
    setSearchQuery(query);

    // Clear existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    if (autoSearch) {
      // Debounce the search
      debounceTimeoutRef.current = setTimeout(() => {
        performSearch(query);
      }, debounceMs);
    } else {
      // Immediate search when not auto-searching
      await performSearch(query);
    }
  }, [autoSearch, debounceMs, performSearch]);

  const clearSearch = useCallback(() => {
    setSearchQuery('');
    setSearchResults([]);
    setSearchError(null);
    
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const clearSearchError = useCallback(() => {
    setSearchError(null);
  }, []);

  // Cleanup effect
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    searchResults,
    searchQuery,
    isSearching,
    searchError,
    search,
    clearSearch,
    clearSearchError,
  };
}

/**
 * Hook for loading chunk details
 */
export function useChunkDetails(options: UseChunkDetailsOptions = {}): UseChunkDetailsReturn {
  const { } = options;

  const [chunk, setChunk] = useState<ChunkDetailsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const currentChunkIdRef = useRef<string | null>(null);

  const createErrorState = useCallback((error: any): ErrorState => ({
    message: error instanceof ChunksApiError ? error.message : error.message || 'Failed to load chunk details',
    code: error instanceof ChunksApiError ? error.code : undefined,
    retryable: error instanceof ChunksApiError ? error.retryable : true,
    timestamp: Date.now(),
  }), []);

  const loadChunk = useCallback(async (chunkId: string) => {
    if (!chunkId) return;

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;
    currentChunkIdRef.current = chunkId;

    try {
      setLoading(true);
      setError(null);

      const response = await chunksApiService.getChunkDetails(chunkId);

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to load chunk details');
      }

      setChunk(response.data);

    } catch (error: any) {
      if (error.name !== 'AbortError') {
        setError(createErrorState(error));
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }, [createErrorState]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const retry = useCallback(async () => {
    if (currentChunkIdRef.current) {
      await loadChunk(currentChunkIdRef.current);
    }
  }, [loadChunk]);

  // Cleanup effect
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    chunk,
    loading,
    error,
    loadChunk,
    clearError,
    retry,
  };
}

/**
 * Hook for loading chunks statistics
 */
export function useChunksStatistics(): UseChunksStatisticsReturn {
  const [statistics, setStatistics] = useState<ChunksStatisticsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const createErrorState = useCallback((error: any): ErrorState => ({
    message: error instanceof ChunksApiError ? error.message : error.message || 'Failed to load statistics',
    code: error instanceof ChunksApiError ? error.code : undefined,
    retryable: error instanceof ChunksApiError ? error.retryable : true,
    timestamp: Date.now(),
  }), []);

  const loadStatistics = useCallback(async () => {
    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      setLoading(true);
      setError(null);

      const response = await chunksApiService.getChunksStatistics();

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to load statistics');
      }

      setStatistics(response.data);

    } catch (error: any) {
      if (error.name !== 'AbortError') {
        setError(createErrorState(error));
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }, [createErrorState]);

  const refresh = useCallback(async () => {
    await loadStatistics();
  }, [loadStatistics]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Cleanup effect
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    statistics,
    loading,
    error,
    loadStatistics,
    refresh,
    clearError,
  };
}