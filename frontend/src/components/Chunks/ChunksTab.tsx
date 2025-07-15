import React, { useState, useEffect } from 'react';
import { Search, Database, FileText, Clock, Filter, Grid, BarChart3 } from 'lucide-react';
import { apiService } from '../../services/apiService';
import { Chunk, ChunksStatisticsResponse } from '../../types';

interface ChunksTabProps {}

export const ChunksTab: React.FC<ChunksTabProps> = () => {
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Chunk[]>([]);
  const [statistics, setStatistics] = useState<ChunksStatisticsResponse | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalChunks, setTotalChunks] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [showStatistics, setShowStatistics] = useState(false);

  const pageSize = 20;

  useEffect(() => {
    loadChunks();
    loadStatistics();
  }, [currentPage]);

  const loadChunks = async () => {
    try {
      setLoading(true);
      const offset = (currentPage - 1) * pageSize;
      const response = await apiService.getChunks(pageSize, offset);
      
      if (response.success && response.data) {
        setChunks(response.data.chunks);
        setTotalChunks(response.data.total);
        setHasMore(response.data.has_more);
      } else {
        setError(response.error || 'Failed to load chunks');
      }
    } catch (error) {
      setError('Error loading chunks');
      console.error('Load chunks error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await apiService.getChunksStatistics();
      if (response.success && response.data) {
        setStatistics(response.data);
      }
    } catch (error) {
      console.error('Load statistics error:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setIsSearching(true);
      const response = await apiService.searchChunks(searchQuery, 50);
      
      if (response.success && response.data) {
        setSearchResults(response.data.chunks);
      } else {
        setError(response.error || 'Search failed');
      }
    } catch (error) {
      setError('Search error');
      console.error('Search error:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
  };

  const displayedChunks = searchResults.length > 0 ? searchResults : chunks;

  const formatMetadata = (metadata: any) => {
    const keys = Object.keys(metadata).filter(key => 
      key !== 'chunk_id' && key !== 'chunk_index' && metadata[key]
    );
    return keys.slice(0, 3).map(key => `${key}: ${metadata[key]}`).join(', ');
  };

  const truncateContent = (content: string, maxLength: number = 150) => {
    return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Database className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">ChromaDB Chunks</h1>
        </div>
        <button
          onClick={() => setShowStatistics(!showStatistics)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <BarChart3 className="h-4 w-4" />
          <span>Statistics</span>
        </button>
      </div>

      {/* Statistics Panel */}
      {showStatistics && statistics && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Database Statistics</h2>
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
        </div>
      )}

      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search chunks by content..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
          {searchResults.length > 0 && (
            <button
              onClick={clearSearch}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Results Info */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {searchResults.length > 0 ? (
            <span>Found {searchResults.length} chunks for "{searchQuery}"</span>
          ) : (
            <span>Showing {chunks.length} of {totalChunks} chunks</span>
          )}
        </div>
        {searchResults.length === 0 && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Page {currentPage}</span>
            <div className="flex space-x-1">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(p => p + 1)}
                disabled={!hasMore}
                className="px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-red-800">{error}</div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading chunks...</p>
        </div>
      )}

      {/* Chunks List */}
      {!loading && (
        <div className="space-y-4">
          {displayedChunks.map((chunk) => (
            <div key={chunk.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Grid className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-mono text-gray-500">{chunk.id}</span>
                </div>
                {chunk.score && (
                  <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                    Score: {chunk.score.toFixed(3)}
                  </div>
                )}
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
          ))}

          {displayedChunks.length === 0 && !loading && (
            <div className="text-center py-8">
              <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No chunks found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};