import { useState, useCallback } from 'react';
import { apiService } from '../services/apiService';
import { 
  SmartSearchRequest, 
  SmartSearchResponse, 
  AdvancedSearchRequest, 
  QueryAnalysis,
  SearchFilter,
  FilterOptions
} from '../types';

interface UseSmartSearchReturn {
  // State
  query: string;
  isSearching: boolean;
  isAnalyzing: boolean;
  searchResults: SmartSearchResponse | null;
  queryAnalysis: QueryAnalysis | null;
  filterOptions: FilterOptions | null;
  activeFilters: SearchFilter;
  searchHistory: string[];
  error: string | null;

  // Actions
  setQuery: (query: string) => void;
  setActiveFilters: (filters: SearchFilter) => void;
  performSmartSearch: (request: SmartSearchRequest) => Promise<void>;
  performAdvancedSearch: (request: AdvancedSearchRequest) => Promise<void>;
  analyzeQuery: (query: string) => Promise<void>;
  loadFilterOptions: () => Promise<void>;
  clearResults: () => void;
  clearError: () => void;
  addToHistory: (query: string) => void;
  clearHistory: () => void;
}

export const useSmartSearch = (): UseSmartSearchReturn => {
  // State
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [searchResults, setSearchResults] = useState<SmartSearchResponse | null>(null);
  const [queryAnalysis, setQueryAnalysis] = useState<QueryAnalysis | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [activeFilters, setActiveFilters] = useState<SearchFilter>({});
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Actions
  const performSmartSearch = useCallback(async (request: SmartSearchRequest) => {
    setIsSearching(true);
    setError(null);
    setSearchResults(null);

    try {
      const response = await apiService.smartSearch(request);
      
      if (response.success && response.data) {
        setSearchResults(response.data);
        
        // Extract query analysis if available
        if (response.data.query_analysis) {
          setQueryAnalysis(response.data.query_analysis);
        }
        
        // Add to search history
        if (request.query && !searchHistory.includes(request.query)) {
          setSearchHistory(prev => [request.query, ...prev.slice(0, 9)]); // Keep last 10 searches
        }
      } else {
        setError(response.error || 'Smart search failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsSearching(false);
    }
  }, [searchHistory]);

  const performAdvancedSearch = useCallback(async (request: AdvancedSearchRequest) => {
    setIsSearching(true);
    setError(null);
    setSearchResults(null);

    try {
      const response = await apiService.advancedSearch(request);
      
      if (response.success && response.data) {
        setSearchResults(response.data);
        
        // Extract query analysis if available
        if (response.data.query_analysis) {
          setQueryAnalysis(response.data.query_analysis);
        }
        
        // Add to search history
        if (request.query && !searchHistory.includes(request.query)) {
          setSearchHistory(prev => [request.query, ...prev.slice(0, 9)]);
        }
      } else {
        setError(response.error || 'Advanced search failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsSearching(false);
    }
  }, [searchHistory]);

  const analyzeQuery = useCallback(async (queryText: string) => {
    setIsAnalyzing(true);
    setError(null);
    setQueryAnalysis(null);

    try {
      const response = await apiService.analyzeQuery(queryText);
      
      if (response.success && response.data) {
        setQueryAnalysis(response.data.analysis);
      } else {
        setError(response.error || 'Query analysis failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const loadFilterOptions = useCallback(async () => {
    try {
      const response = await apiService.getFilterOptions();
      
      if (response.success && response.data) {
        setFilterOptions(response.data);
      } else {
        setError(response.error || 'Failed to load filter options');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    }
  }, []);

  const clearResults = useCallback(() => {
    setSearchResults(null);
    setQueryAnalysis(null);
    setError(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const addToHistory = useCallback((searchQuery: string) => {
    if (searchQuery && !searchHistory.includes(searchQuery)) {
      setSearchHistory(prev => [searchQuery, ...prev.slice(0, 9)]);
    }
  }, [searchHistory]);

  const clearHistory = useCallback(() => {
    setSearchHistory([]);
  }, []);

  return {
    // State
    query,
    isSearching,
    isAnalyzing,
    searchResults,
    queryAnalysis,
    filterOptions,
    activeFilters,
    searchHistory,
    error,

    // Actions
    setQuery,
    setActiveFilters,
    performSmartSearch,
    performAdvancedSearch,
    analyzeQuery,
    loadFilterOptions,
    clearResults,
    clearError,
    addToHistory,
    clearHistory
  };
};