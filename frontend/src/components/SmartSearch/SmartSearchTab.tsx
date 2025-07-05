import React, { useState, useEffect } from 'react';
import { Search, Filter, Brain, BarChart3, Settings, Zap } from 'lucide-react';
import { apiService } from '../../services/apiService';
import { 
  SmartSearchRequest, 
  SmartSearchResponse, 
  AdvancedSearchRequest, 
  QueryAnalysis, 
  FilterOptions,
  SearchFilter
} from '../../types';
import { SearchFilters } from './SearchFilters';
import { QueryAnalysisDisplay } from './QueryAnalysisDisplay';
import { SmartSearchResults } from './SmartSearchResults';

interface SmartSearchTabProps {
  className?: string;
}

export const SmartSearchTab: React.FC<SmartSearchTabProps> = ({ className = '' }) => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [searchMode, setSearchMode] = useState<'smart' | 'advanced'>('smart');
  const [showFilters, setShowFilters] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  
  // Results and analysis state
  const [searchResults, setSearchResults] = useState<SmartSearchResponse | null>(null);
  const [queryAnalysis, setQueryAnalysis] = useState<QueryAnalysis | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  
  // Filter state
  const [activeFilters, setActiveFilters] = useState<SearchFilter>({});
  const [topK, setTopK] = useState(5);
  const [includeAnalysis, setIncludeAnalysis] = useState(true);
  
  // Load filter options on component mount
  useEffect(() => {
    loadFilterOptions();
  }, []);

  const loadFilterOptions = async () => {
    try {
      const response = await apiService.getFilterOptions();
      if (response.success && response.data) {
        setFilterOptions(response.data);
      }
    } catch (error) {
      console.error('Failed to load filter options:', error);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isSearching) return;

    setIsSearching(true);
    setSearchResults(null);

    try {
      let response;
      
      if (searchMode === 'smart') {
        const request: SmartSearchRequest = {
          query: query.trim(),
          top_k: topK,
          include_analysis: includeAnalysis
        };
        response = await apiService.smartSearch(request);
      } else {
        const request: AdvancedSearchRequest = {
          query: query.trim(),
          top_k: topK,
          filters: Object.keys(activeFilters).length > 0 ? activeFilters : undefined,
          include_analysis: includeAnalysis
        };
        response = await apiService.advancedSearch(request);
      }

      if (response.success && response.data) {
        setSearchResults(response.data);
        
        // Extract query analysis if available
        if (response.data.query_analysis) {
          setQueryAnalysis(response.data.query_analysis);
        }
      } else {
        console.error('Search failed:', response.error);
        // TODO: Show error toast
      }
    } catch (error) {
      console.error('Search error:', error);
      // TODO: Show error toast
    } finally {
      setIsSearching(false);
    }
  };

  const handleAnalyzeQuery = async () => {
    if (!query.trim() || isAnalyzing) return;

    setIsAnalyzing(true);
    setQueryAnalysis(null);

    try {
      const response = await apiService.analyzeQuery(query.trim());
      if (response.success && response.data) {
        setQueryAnalysis(response.data.analysis);
        setShowAnalysis(true);
      } else {
        console.error('Query analysis failed:', response.error);
        // TODO: Show error toast
      }
    } catch (error) {
      console.error('Query analysis error:', error);
      // TODO: Show error toast
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFiltersChange = (filters: SearchFilter) => {
    setActiveFilters(filters);
  };

  const clearFilters = () => {
    setActiveFilters({});
  };

  const hasActiveFilters = Object.keys(activeFilters).length > 0;

  return (
    <div className={`bg-white rounded-xl shadow-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Brain className="w-8 h-8" />
          <h1 className="text-2xl font-bold">Smart Search</h1>
        </div>
        <p className="text-purple-100">
          Intelligente Suche mit automatischer Strategieauswahl und erweiterten Filtern
        </p>
      </div>

      {/* Search Interface */}
      <div className="p-6 border-b border-gray-200">
        {/* Mode Selection */}
        <div className="flex items-center space-x-4 mb-4">
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setSearchMode('smart')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                searchMode === 'smart'
                  ? 'bg-white text-purple-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Zap className="w-4 h-4 inline mr-2" />
              Smart Search
            </button>
            <button
              onClick={() => setSearchMode('advanced')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                searchMode === 'advanced'
                  ? 'bg-white text-purple-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Settings className="w-4 h-4 inline mr-2" />
              Advanced
            </button>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                showFilters || hasActiveFilters
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Filter className="w-4 h-4" />
              <span>Filter</span>
              {hasActiveFilters && (
                <span className="bg-purple-600 text-white text-xs px-2 py-1 rounded-full">
                  {Object.keys(activeFilters).length}
                </span>
              )}
            </button>
            
            <button
              onClick={() => setShowAnalysis(!showAnalysis)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                showAnalysis
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Analyse</span>
            </button>
          </div>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Suche in StreamWorks-Dokumentation..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            
            <button
              type="button"
              onClick={handleAnalyzeQuery}
              disabled={!query.trim() || isAnalyzing}
              className="px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isAnalyzing ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <Brain className="w-5 h-5" />
              )}
            </button>
            
            <button
              type="submit"
              disabled={!query.trim() || isSearching}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {isSearching ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Suche...</span>
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  <span>Suchen</span>
                </>
              )}
            </button>
          </div>

          {/* Search Options */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Ergebnisse:</label>
              <select
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="px-3 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={15}>15</option>
                <option value={20}>20</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="includeAnalysis"
                checked={includeAnalysis}
                onChange={(e) => setIncludeAnalysis(e.target.checked)}
                className="text-purple-600 focus:ring-purple-500"
              />
              <label htmlFor="includeAnalysis" className="text-sm text-gray-700">
                Query-Analyse einbeziehen
              </label>
            </div>
            
            {hasActiveFilters && (
              <button
                type="button"
                onClick={clearFilters}
                className="text-sm text-purple-600 hover:text-purple-700"
              >
                Filter zurücksetzen
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Filters Panel */}
      {showFilters && filterOptions && (
        <div className="border-b border-gray-200">
          <SearchFilters
            filterOptions={filterOptions}
            activeFilters={activeFilters}
            onFiltersChange={handleFiltersChange}
          />
        </div>
      )}

      {/* Query Analysis Panel */}
      {showAnalysis && queryAnalysis && (
        <div className="border-b border-gray-200">
          <QueryAnalysisDisplay analysis={queryAnalysis} />
        </div>
      )}

      {/* Results Section */}
      <div className="p-6">
        {searchResults ? (
          <SmartSearchResults results={searchResults} />
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Search className="w-16 h-16 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Bereit für intelligente Suche
              </h3>
              <p className="text-sm text-gray-600 max-w-md mx-auto">
                Geben Sie eine Suchanfrage ein, um die erweiterten Suchfunktionen zu nutzen.
                Die KI wählt automatisch die beste Suchstrategie aus.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto mt-8">
              <div className="bg-purple-50 p-4 rounded-lg">
                <Zap className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                <h4 className="font-medium text-purple-900">Smart Search</h4>
                <p className="text-sm text-purple-700">Automatische Strategieauswahl</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <Filter className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                <h4 className="font-medium text-blue-900">Advanced Filter</h4>
                <p className="text-sm text-blue-700">39+ Dateiformate unterstützt</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <BarChart3 className="w-6 h-6 text-green-600 mx-auto mb-2" />
                <h4 className="font-medium text-green-900">Query Analysis</h4>
                <p className="text-sm text-green-700">Intent-Erkennung & Optimierung</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};