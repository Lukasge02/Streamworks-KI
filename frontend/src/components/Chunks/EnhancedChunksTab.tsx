import React, { useState, useEffect, useCallback } from 'react';
import { 
  Search, Database, FileText, Clock, Filter, Grid, BarChart3, 
  RefreshCw, WifiOff, ChevronDown, ChevronUp,
  Download, Copy, Eye
} from 'lucide-react';
import { 
  useChunks, 
  useChunksSearch, 
  useChunksStatistics,
  useChunkDetails 
} from '../../hooks/useChunks';
import { useSmartSearchDebounce } from '../../hooks/useDebounce';
import { useOffline } from '../../hooks/useOffline';
import { ErrorBoundary } from '../ErrorHandling/ErrorBoundary';
import { ErrorAlert, OfflineErrorAlert } from '../ErrorHandling/ErrorAlert';

interface ChunksTabProps {}

export const EnhancedChunksTab: React.FC<ChunksTabProps> = () => {
  // State management
  const [showStatistics, setShowStatistics] = useState(false);
  const [selectedChunk, setSelectedChunk] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Offline management
  const { isOnline, isConnecting, retryConnection } = useOffline({
    onOnline: () => {
      // Refresh data when coming back online
      refresh();
    }
  });

  // Chunks data management
  const {
    chunks,
    total,
    hasMore,
    currentPage,
    loading,
    error,
    loadMore,
    refresh,
    setPage,
    clearError,
    retry,
    filters,
    updateFilters,
    clearFilters,
  } = useChunks({
    limit: 20,
    autoLoad: true,
    enableCache: true,
    refetchInterval: isOnline ? 5 * 60 * 1000 : 0, // 5 minutes when online
  });

  // Search functionality
  const {
    searchResults,
    searchQuery: currentSearchQuery,
    isSearching,
    searchError,
    search,
    clearSearch,
    clearSearchError,
  } = useChunksSearch({
    debounceMs: 300,
    minQueryLength: 2,
    autoSearch: true,
  });

  // Statistics
  const {
    statistics,
    loading: statisticsLoading,
    error: statisticsError,
    loadStatistics,
    refresh: refreshStatistics,
    clearError: clearStatisticsError,
  } = useChunksStatistics();

  // Chunk details
  const {
    chunk: chunkDetails,
    loading: detailsLoading,
    error: detailsError,
    loadChunk,
    clearError: clearDetailsError,
  } = useChunkDetails();

  // Smart search with debouncing
  const debouncedSearch = useSmartSearchDebounce(search, {
    shortQueryDelay: 800,
    mediumQueryDelay: 400,
    longQueryDelay: 200,
    minLength: 2,
  });

  // Handle search input
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    if (query.trim()) {
      debouncedSearch(query);
    } else {
      clearSearch();
    }
  }, [debouncedSearch, clearSearch]);

  // Clear search
  const handleClearSearch = useCallback(() => {
    setSearchQuery('');
    clearSearch();
  }, [clearSearch]);

  // Load statistics on mount
  useEffect(() => {
    if (isOnline && showStatistics && !statistics) {
      loadStatistics();
    }
  }, [showStatistics, statistics, loadStatistics, isOnline]);

  // Handle chunk selection
  const handleChunkSelect = useCallback((chunkId: string) => {
    setSelectedChunk(chunkId === selectedChunk ? null : chunkId);
    if (chunkId !== selectedChunk) {
      loadChunk(chunkId);
    }
  }, [selectedChunk, loadChunk]);

  // Copy chunk content
  const copyChunkContent = useCallback((content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      // Could add toast notification here
    });
  }, []);

  // Export chunks
  const exportChunks = useCallback(() => {
    const chunksToExport = searchResults.length > 0 ? searchResults : chunks;
    const dataStr = JSON.stringify(chunksToExport, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chunks-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [chunks, searchResults]);

  // Format metadata display
  const formatMetadata = useCallback((metadata: any) => {
    const keys = Object.keys(metadata).filter(key => 
      key !== 'chunk_id' && key !== 'chunk_index' && metadata[key]
    );
    return keys.slice(0, 3).map(key => `${key}: ${metadata[key]}`).join(', ');
  }, []);

  // Truncate content for display
  const truncateContent = useCallback((content: string, maxLength: number = 150) => {
    return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
  }, []);

  // Get displayed chunks (search results or regular chunks)
  const displayedChunks = searchResults.length > 0 ? searchResults : chunks;

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Database className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">ChromaDB Chunks</h1>
            {!isOnline && (
              <div className="flex items-center space-x-1 text-orange-600">
                <WifiOff className="h-4 w-4" />
                <span className="text-sm">Offline</span>
              </div>
            )}
            {isConnecting && (
              <div className="flex items-center space-x-1 text-blue-600">
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span className="text-sm">Connecting...</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={exportChunks}
              disabled={displayedChunks.length === 0}
              className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
            
            <button
              onClick={() => setShowStatistics(!showStatistics)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <BarChart3 className="h-4 w-4" />
              <span>Statistics</span>
            </button>
          </div>
        </div>

        {/* Offline Alert */}
        {!isOnline && (
          <OfflineErrorAlert
            onRetry={retryConnection}
            variant="banner"
            className="mb-4"
          />
        )}

        {/* Error Alerts */}
        {error && (
          <ErrorAlert
            error={error}
            onRetry={retry}
            onDismiss={clearError}
            className="mb-4"
          />
        )}

        {searchError && (
          <ErrorAlert
            error={searchError}
            onDismiss={clearSearchError}
            className="mb-4"
          />
        )}

        {/* Statistics Panel */}
        {showStatistics && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Database Statistics</h2>
              <button
                onClick={refreshStatistics}
                disabled={statisticsLoading || !isOnline}
                className="flex items-center space-x-1 px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`h-3 w-3 ${statisticsLoading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>

            {statisticsError && (
              <ErrorAlert
                error={statisticsError}
                onRetry={loadStatistics}
                onDismiss={clearStatisticsError}
                variant="inline"
                className="mb-4"
              />
            )}

            {statisticsLoading ? (
              <div className="flex justify-center py-8">
                <RefreshCw className="h-6 w-6 animate-spin text-blue-600" />
              </div>
            ) : statistics ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{statistics.total_chunks}</div>
                  <div className="text-sm text-gray-600">Total Chunks</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{statistics.total_documents}</div>
                  <div className="text-sm text-gray-600">Total Documents</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{Math.round(statistics.chunk_size_avg)}</div>
                  <div className="text-sm text-gray-600">Avg. Chunk Size</div>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">
                No statistics available
              </div>
            )}
          </div>
        )}

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow p-6">
          {/* Search Bar */}
          <div className="flex items-center space-x-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search chunks by content..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchQuery}
                onChange={handleSearchChange}
                disabled={!isOnline}
              />
              {isSearching && (
                <RefreshCw className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 animate-spin text-blue-600" />
              )}
            </div>
            
            {(searchQuery || searchResults.length > 0) && (
              <button
                onClick={handleClearSearch}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Clear
              </button>
            )}
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <Filter className="h-4 w-4" />
              <span>Filters</span>
              {showFilters ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Source File</label>
                <input
                  type="text"
                  placeholder="Filter by filename..."
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={filters.sourceFile}
                  onChange={(e) => updateFilters({ sourceFile: e.target.value })}
                  disabled={!isOnline}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={filters.category}
                  onChange={(e) => updateFilters({ category: e.target.value })}
                  disabled={!isOnline}
                >
                  <option value="">All Categories</option>
                  <option value="help_data">Help Data</option>
                  <option value="stream_templates">Stream Templates</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={`${filters.sortBy}-${filters.sortOrder}`}
                  onChange={(e) => {
                    const [sortBy, sortOrder] = e.target.value.split('-');
                    updateFilters({ sortBy, sortOrder });
                  }}
                  disabled={!isOnline}
                >
                  <option value="creation_date-desc">Newest First</option>
                  <option value="creation_date-asc">Oldest First</option>
                  <option value="filename-asc">Filename A-Z</option>
                  <option value="filename-desc">Filename Z-A</option>
                </select>
              </div>
              
              <div className="md:col-span-3 flex justify-end">
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Results Info */}
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {searchResults.length > 0 ? (
              <span>Found {searchResults.length} chunks for "{currentSearchQuery}"</span>
            ) : (
              <span>Showing {displayedChunks.length} of {total} chunks</span>
            )}
          </div>
          
          {searchResults.length === 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Page {currentPage}</span>
              <div className="flex space-x-1">
                <button
                  onClick={() => setPage(currentPage - 1)}
                  disabled={currentPage === 1 || loading.initial || !isOnline}
                  className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50 hover:bg-gray-300 transition-colors"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(currentPage + 1)}
                  disabled={!hasMore || loading.loadMore || !isOnline}
                  className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50 hover:bg-gray-300 transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading.initial && (
          <div className="text-center py-8">
            <RefreshCw className="h-8 w-8 border-b-2 border-blue-600 mx-auto animate-spin mb-2" />
            <p className="text-gray-600">Loading chunks...</p>
          </div>
        )}

        {/* Chunks List */}
        {!loading.initial && (
          <div className="space-y-4">
            {displayedChunks.map((chunk) => (
              <div key={chunk.id} className="bg-white rounded-lg shadow overflow-hidden">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <Grid className="h-4 w-4 text-gray-400" />
                      <span className="text-sm font-mono text-gray-500">{chunk.id}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {chunk.score && (
                        <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          Score: {chunk.score.toFixed(3)}
                        </div>
                      )}
                      
                      <button
                        onClick={() => copyChunkContent(chunk.content)}
                        className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                        title="Copy content"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                      
                      <button
                        onClick={() => handleChunkSelect(chunk.id)}
                        className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                        title="View details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="prose max-w-none mb-4">
                    <p className="text-gray-700">{truncateContent(chunk.content)}</p>
                  </div>
                  
                  {chunk.metadata && (
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <FileText className="h-4 w-4" />
                        <span>{chunk.metadata.filename || 'Unknown'}</span>
                      </div>
                      {chunk.metadata.timestamp && (
                        <div className="flex items-center space-x-1">
                          <Clock className="h-4 w-4" />
                          <span>{new Date(chunk.metadata.timestamp).toLocaleDateString()}</span>
                        </div>
                      )}
                      {formatMetadata(chunk.metadata) && (
                        <div className="flex items-center space-x-1">
                          <Filter className="h-4 w-4" />
                          <span>{formatMetadata(chunk.metadata)}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Chunk Details */}
                {selectedChunk === chunk.id && (
                  <div className="border-t bg-gray-50 p-6">
                    {detailsLoading ? (
                      <div className="flex justify-center py-4">
                        <RefreshCw className="h-5 w-5 animate-spin text-blue-600" />
                      </div>
                    ) : detailsError ? (
                      <ErrorAlert
                        error={detailsError}
                        onRetry={() => loadChunk(chunk.id)}
                        onDismiss={clearDetailsError}
                        variant="inline"
                      />
                    ) : chunkDetails ? (
                      <div className="space-y-4">
                        <h4 className="font-semibold text-gray-900">Full Content</h4>
                        <div className="bg-white p-4 rounded border max-h-64 overflow-y-auto">
                          <pre className="whitespace-pre-wrap text-sm text-gray-700">
                            {chunkDetails.chunk.content}
                          </pre>
                        </div>
                        
                        {chunkDetails.similar_chunks.length > 0 && (
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-2">Similar Chunks</h4>
                            <div className="space-y-2">
                              {chunkDetails.similar_chunks.slice(0, 3).map((similarChunk) => (
                                <div key={similarChunk.id} className="bg-white p-3 rounded border">
                                  <div className="text-sm text-gray-600 mb-1">
                                    {similarChunk.metadata?.filename || 'Unknown file'}
                                  </div>
                                  <div className="text-sm text-gray-700">
                                    {truncateContent(similarChunk.content, 100)}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : null}
                  </div>
                )}
              </div>
            ))}

            {/* Load More Button */}
            {hasMore && searchResults.length === 0 && (
              <div className="text-center py-4">
                <button
                  onClick={loadMore}
                  disabled={loading.loadMore || !isOnline}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {loading.loadMore ? (
                    <>
                      <RefreshCw className="inline h-4 w-4 animate-spin mr-2" />
                      Loading...
                    </>
                  ) : (
                    'Load More'
                  )}
                </button>
              </div>
            )}

            {/* Empty State */}
            {displayedChunks.length === 0 && !loading.initial && (
              <div className="text-center py-8">
                <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  {searchQuery ? 'No chunks found for your search' : 'No chunks available'}
                </p>
                {searchQuery && (
                  <button
                    onClick={handleClearSearch}
                    className="mt-2 text-blue-600 hover:text-blue-700"
                  >
                    Clear search
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};