/**
 * Advanced Search Component
 * Enhanced search with autocomplete, filters, history, and keyboard navigation
 */

import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import { Search, X, Clock, Filter, ChevronDown, Command, ArrowUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './Button';
import { Badge } from './Badge';
import { Input } from './Input';

export interface FilterConfig {
  key: string;
  label: string;
  type: 'select' | 'multiselect' | 'date' | 'range' | 'text';
  options?: { value: string; label: string }[];
  placeholder?: string;
}

interface SearchBoxProps {
  placeholder?: string;
  suggestions?: string[];
  filters?: FilterConfig[];
  onSearch: (query: string, filters?: Record<string, any>) => void;
  showHistory?: boolean;
  showFilters?: boolean;
  globalShortcut?: boolean;
  className?: string;
  disabled?: boolean;
  loading?: boolean;
  defaultQuery?: string;
  maxSuggestions?: number;
}

const STORAGE_KEY = 'streamworks-search-history';
const MAX_HISTORY_ITEMS = 10;

function useSearchHistory() {
  const [history, setHistory] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const addToHistory = useCallback((query: string) => {
    if (!query.trim() || query.length < 2) return;
    
    setHistory(prev => {
      const filtered = prev.filter(item => item !== query);
      const newHistory = [query, ...filtered].slice(0, MAX_HISTORY_ITEMS);
      
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newHistory));
      } catch {
        // Ignore storage errors
      }
      
      return newHistory;
    });
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignore storage errors
    }
  }, []);

  return { history, addToHistory, clearHistory };
}

export function SearchBox({
  placeholder = 'Search...',
  suggestions = [],
  filters = [],
  onSearch,
  showHistory = true,
  showFilters = false,
  globalShortcut = false,
  className = '',
  disabled = false,
  loading = false,
  defaultQuery = '',
  maxSuggestions = 8,
}: SearchBoxProps) {
  const [query, setQuery] = useState(defaultQuery);
  const [isOpen, setIsOpen] = useState(false);
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { history, addToHistory, clearHistory } = useSearchHistory();

  // Debounced search
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout>();

  const debouncedSearch = useCallback((searchQuery: string, searchFilters?: Record<string, any>) => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    const timeout = setTimeout(() => {
      onSearch(searchQuery, searchFilters);
      if (searchQuery.trim()) {
        addToHistory(searchQuery);
      }
    }, 300);

    setSearchTimeout(timeout);
  }, [onSearch, addToHistory, searchTimeout]);

  // Combined suggestions (history + provided suggestions)
  const combinedSuggestions = useMemo(() => {
    const filteredSuggestions = suggestions.filter(s => 
      s.toLowerCase().includes(query.toLowerCase())
    );
    
    const filteredHistory = showHistory 
      ? history.filter(h => 
          h.toLowerCase().includes(query.toLowerCase()) && 
          !filteredSuggestions.includes(h)
        )
      : [];

    return [...filteredHistory, ...filteredSuggestions].slice(0, maxSuggestions);
  }, [suggestions, history, query, showHistory, maxSuggestions]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'ArrowDown') {
        setIsOpen(true);
        setSelectedIndex(0);
        e.preventDefault();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < combinedSuggestions.length - 1 ? prev + 1 : prev
        );
        break;
      
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && combinedSuggestions[selectedIndex]) {
          const selectedQuery = combinedSuggestions[selectedIndex];
          setQuery(selectedQuery);
          debouncedSearch(selectedQuery, activeFilters);
          setIsOpen(false);
          setSelectedIndex(-1);
        } else {
          debouncedSearch(query, activeFilters);
          setIsOpen(false);
          setSelectedIndex(-1);
        }
        break;
      
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
      
      case 'Tab':
        if (selectedIndex >= 0 && combinedSuggestions[selectedIndex]) {
          e.preventDefault();
          setQuery(combinedSuggestions[selectedIndex]);
        }
        break;
    }
  }, [isOpen, selectedIndex, combinedSuggestions, query, debouncedSearch, activeFilters]);

  // Global keyboard shortcut
  useEffect(() => {
    if (!globalShortcut) return;

    const handleGlobalKeydown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        setIsOpen(true);
      }
    };

    document.addEventListener('keydown', handleGlobalKeydown);
    return () => document.removeEventListener('keydown', handleGlobalKeydown);
  }, [globalShortcut]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSelectedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleQueryChange = (value: string) => {
    setQuery(value);
    setSelectedIndex(-1);
    if (value.trim()) {
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    debouncedSearch(suggestion, activeFilters);
    setIsOpen(false);
    setSelectedIndex(-1);
  };

  const handleClear = () => {
    setQuery('');
    setIsOpen(false);
    setSelectedIndex(-1);
    onSearch('', activeFilters);
  };

  const handleFilterChange = (key: string, value: any) => {
    const newFilters = { ...activeFilters, [key]: value };
    setActiveFilters(newFilters);
    debouncedSearch(query, newFilters);
  };

  const removeFilter = (key: string) => {
    const newFilters = { ...activeFilters };
    delete newFilters[key];
    setActiveFilters(newFilters);
    debouncedSearch(query, newFilters);
  };

  const activeFilterCount = Object.keys(activeFilters).filter(
    key => activeFilters[key] !== undefined && activeFilters[key] !== ''
  ).length;

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Main Search Input */}
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 z-10">
          <Search size={18} className="text-neutral-500 dark:text-neutral-400" />
        </div>
        
        <Input
          ref={inputRef}
          value={query}
          onChange={(e) => handleQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          disabled={disabled}
          className={`pl-10 pr-20 ${loading ? 'animate-pulse' : ''}`}
        />
        
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center space-x-1">
          {globalShortcut && !query && (
            <Badge variant="secondary" size="sm" className="text-xs">
              <Command size={10} className="mr-1" />K
            </Badge>
          )}
          
          {showFilters && (
            <Button
              size="sm"
              variant={showFilterPanel ? 'primary' : 'ghost'}
              onClick={() => setShowFilterPanel(!showFilterPanel)}
              className="h-7 w-7 p-0 relative"
            >
              <Filter size={14} />
              {activeFilterCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-primary-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                  {activeFilterCount}
                </span>
              )}
            </Button>
          )}
          
          {query && (
            <Button
              size="sm"
              variant="ghost"
              onClick={handleClear}
              className="h-7 w-7 p-0"
            >
              <X size={14} />
            </Button>
          )}
        </div>
      </div>

      {/* Filter Panel */}
      <AnimatePresence>
        {showFilterPanel && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 right-0 mt-2 p-4 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg z-20"
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                Filters
              </h3>
              {activeFilterCount > 0 && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setActiveFilters({})}
                  className="text-xs"
                >
                  Clear all
                </Button>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {filters.map((filter) => (
                <div key={filter.key}>
                  <label className="block text-xs font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                    {filter.label}
                  </label>
                  
                  {filter.type === 'select' && (
                    <select
                      value={activeFilters[filter.key] || ''}
                      onChange={(e) => handleFilterChange(filter.key, e.target.value)}
                      className="w-full px-3 py-1.5 text-sm border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100"
                    >
                      <option value="">{filter.placeholder || 'All'}</option>
                      {filter.options?.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  )}
                  
                  {filter.type === 'text' && (
                    <Input
                      value={activeFilters[filter.key] || ''}
                      onChange={(e) => handleFilterChange(filter.key, e.target.value)}
                      placeholder={filter.placeholder}
                      size="sm"
                    />
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Suggestions Dropdown */}
      <AnimatePresence>
        {isOpen && (combinedSuggestions.length > 0 || (showHistory && history.length > 0)) && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 right-0 mt-1 py-2 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg z-30 max-h-64 overflow-y-auto"
          >
            {combinedSuggestions.length > 0 ? (
              combinedSuggestions.map((suggestion, index) => {
                const isHistory = history.includes(suggestion);
                return (
                  <button
                    key={`${suggestion}-${index}`}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className={`
                      w-full px-4 py-2 text-left text-sm hover:bg-neutral-100 dark:hover:bg-neutral-700 flex items-center space-x-2
                      ${index === selectedIndex ? 'bg-neutral-100 dark:bg-neutral-700' : ''}
                    `}
                  >
                    {isHistory ? (
                      <Clock size={14} className="text-neutral-400" />
                    ) : (
                      <Search size={14} className="text-neutral-400" />
                    )}
                    <span className="text-neutral-900 dark:text-neutral-100">
                      {suggestion}
                    </span>
                    {isHistory && (
                      <Badge variant="secondary" size="sm" className="ml-auto">
                        Recent
                      </Badge>
                    )}
                  </button>
                );
              })
            ) : showHistory && history.length > 0 && !query && (
              <>
                <div className="px-4 py-2 text-xs font-medium text-neutral-500 dark:text-neutral-400 flex items-center justify-between">
                  Recent searches
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={clearHistory}
                    className="text-xs h-auto p-1"
                  >
                    Clear
                  </Button>
                </div>
                {history.slice(0, 5).map((item, index) => (
                  <button
                    key={item}
                    onClick={() => handleSuggestionClick(item)}
                    className={`
                      w-full px-4 py-2 text-left text-sm hover:bg-neutral-100 dark:hover:bg-neutral-700 flex items-center space-x-2
                      ${index === selectedIndex ? 'bg-neutral-100 dark:bg-neutral-700' : ''}
                    `}
                  >
                    <Clock size={14} className="text-neutral-400" />
                    <span className="text-neutral-900 dark:text-neutral-100">
                      {item}
                    </span>
                  </button>
                ))}
              </>
            )}
            
            {globalShortcut && (
              <div className="border-t border-neutral-200 dark:border-neutral-700 px-4 py-2 mt-2">
                <div className="text-xs text-neutral-500 dark:text-neutral-400 flex items-center justify-between">
                  <span>Tip: Press Tab to autocomplete</span>
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary" size="sm">
                      <ArrowUp size={8} className="mr-1" />↓
                    </Badge>
                    <span>navigate</span>
                    <Badge variant="secondary" size="sm">Enter</Badge>
                    <span>select</span>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Active Filters Display */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {Object.entries(activeFilters).map(([key, value]) => {
            if (!value) return null;
            const filter = filters.find(f => f.key === key);
            const displayValue = filter?.options?.find(o => o.value === value)?.label || value;
            
            return (
              <Badge
                key={key}
                variant="primary"
                size="sm"
                className="flex items-center space-x-1"
              >
                <span>{filter?.label}: {displayValue}</span>
                <button
                  onClick={() => removeFilter(key)}
                  className="ml-1 hover:bg-primary-600 rounded-full p-0.5"
                >
                  <X size={10} />
                </button>
              </Badge>
            );
          })}
        </div>
      )}
    </div>
  );
}