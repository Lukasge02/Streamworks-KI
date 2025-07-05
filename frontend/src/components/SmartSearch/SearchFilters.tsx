import React, { useState } from 'react';
import { X, ChevronDown, ChevronUp, Filter } from 'lucide-react';
import { FilterOptions, SearchFilter } from '../../types';

interface SearchFiltersProps {
  filterOptions: FilterOptions;
  activeFilters: SearchFilter;
  onFiltersChange: (filters: SearchFilter) => void;
}

export const SearchFilters: React.FC<SearchFiltersProps> = ({
  filterOptions,
  activeFilters,
  onFiltersChange
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['document_types']));

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const handleArrayFilterChange = (
    filterKey: keyof SearchFilter,
    value: string,
    checked: boolean
  ) => {
    const currentValues = (activeFilters[filterKey] as string[]) || [];
    let newValues: string[];
    
    if (checked) {
      newValues = [...currentValues, value];
    } else {
      newValues = currentValues.filter(v => v !== value);
    }
    
    const newFilters = {
      ...activeFilters,
      [filterKey]: newValues.length > 0 ? newValues : undefined
    };
    
    // Remove undefined values
    Object.keys(newFilters).forEach(key => {
      if (newFilters[key as keyof SearchFilter] === undefined) {
        delete newFilters[key as keyof SearchFilter];
      }
    });
    
    onFiltersChange(newFilters);
  };

  const handleComplexityChange = (type: 'min' | 'max', value: number) => {
    const newFilters = {
      ...activeFilters,
      [`complexity_${type}`]: value || undefined
    };
    
    // Remove undefined values
    Object.keys(newFilters).forEach(key => {
      if (newFilters[key as keyof SearchFilter] === undefined) {
        delete newFilters[key as keyof SearchFilter];
      }
    });
    
    onFiltersChange(newFilters);
  };

  const removeFilter = (filterKey: keyof SearchFilter, value?: string) => {
    if (value && Array.isArray(activeFilters[filterKey])) {
      // Remove specific value from array
      const currentValues = (activeFilters[filterKey] as string[]) || [];
      const newValues = currentValues.filter(v => v !== value);
      const newFilters = {
        ...activeFilters,
        [filterKey]: newValues.length > 0 ? newValues : undefined
      };
      
      // Remove undefined values
      Object.keys(newFilters).forEach(key => {
        if (newFilters[key as keyof SearchFilter] === undefined) {
          delete newFilters[key as keyof SearchFilter];
        }
      });
      
      onFiltersChange(newFilters);
    } else {
      // Remove entire filter
      const newFilters = { ...activeFilters };
      delete newFilters[filterKey];
      onFiltersChange(newFilters);
    }
  };

  const renderFilterSection = (
    title: string,
    key: string,
    options: string[],
    filterKey: keyof SearchFilter
  ) => {
    const isExpanded = expandedSections.has(key);
    const activeValues = (activeFilters[filterKey] as string[]) || [];
    
    return (
      <div key={key} className="border border-gray-200 rounded-lg">
        <button
          onClick={() => toggleSection(key)}
          className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50"
        >
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-900">{title}</span>
            {activeValues.length > 0 && (
              <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
                {activeValues.length}
              </span>
            )}
          </div>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          )}
        </button>
        
        {isExpanded && (
          <div className="px-4 pb-4 border-t border-gray-100">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 mt-3">
              {options.map((option) => (
                <label key={option} className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={activeValues.includes(option)}
                    onChange={(e) => handleArrayFilterChange(filterKey, option, e.target.checked)}
                    className="text-purple-600 focus:ring-purple-500 rounded"
                  />
                  <span className="text-gray-700 truncate" title={option}>
                    {option}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const activeFilterCount = Object.keys(activeFilters).length;

  return (
    <div className="p-6 bg-gray-50">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-medium text-gray-900">Erweiterte Filter</h3>
          {activeFilterCount > 0 && (
            <span className="bg-purple-600 text-white text-sm px-2 py-1 rounded-full">
              {activeFilterCount}
            </span>
          )}
        </div>
      </div>

      {/* Active Filters Summary */}
      {activeFilterCount > 0 && (
        <div className="mb-6 p-4 bg-white rounded-lg border border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Aktive Filter:</h4>
          <div className="flex flex-wrap gap-2">
            {/* Document Types */}
            {activeFilters.document_types?.map((type) => (
              <span
                key={`doc-${type}`}
                className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
              >
                <span className="mr-1">📄</span>
                {type}
                <button
                  onClick={() => removeFilter('document_types', type)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            
            {/* File Formats */}
            {activeFilters.file_formats?.map((format) => (
              <span
                key={`format-${format}`}
                className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
              >
                <span className="mr-1">📁</span>
                {format}
                <button
                  onClick={() => removeFilter('file_formats', format)}
                  className="ml-2 text-green-600 hover:text-green-800"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            
            {/* Source Categories */}
            {activeFilters.source_categories?.map((category) => (
              <span
                key={`source-${category}`}
                className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full"
              >
                <span className="mr-1">🗂️</span>
                {category}
                <button
                  onClick={() => removeFilter('source_categories', category)}
                  className="ml-2 text-purple-600 hover:text-purple-800"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            
            {/* Complexity Range */}
            {(activeFilters.complexity_min || activeFilters.complexity_max) && (
              <span className="inline-flex items-center px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full">
                <span className="mr-1">🎯</span>
                Komplexität: {activeFilters.complexity_min || 1}-{activeFilters.complexity_max || 10}
                <button
                  onClick={() => {
                    const newFilters = { ...activeFilters };
                    delete newFilters.complexity_min;
                    delete newFilters.complexity_max;
                    onFiltersChange(newFilters);
                  }}
                  className="ml-2 text-orange-600 hover:text-orange-800"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
          </div>
        </div>
      )}

      {/* Filter Sections */}
      <div className="space-y-4">
        {/* Document Types */}
        {renderFilterSection(
          'Dokumenttypen',
          'document_types',
          filterOptions.document_types,
          'document_types'
        )}

        {/* File Formats */}
        {renderFilterSection(
          'Dateiformate',
          'file_formats',
          filterOptions.file_formats,
          'file_formats'
        )}

        {/* Source Categories */}
        {renderFilterSection(
          'Quellkategorien',
          'source_categories',
          filterOptions.source_categories,
          'source_categories'
        )}

        {/* Chunk Types */}
        {renderFilterSection(
          'Chunk-Typen',
          'chunk_types',
          filterOptions.chunk_types,
          'chunk_types'
        )}

        {/* Processing Methods */}
        {renderFilterSection(
          'Verarbeitungsmethoden',
          'processing_methods',
          filterOptions.processing_methods,
          'processing_methods'
        )}

        {/* Complexity Range */}
        <div className="border border-gray-200 rounded-lg">
          <button
            onClick={() => toggleSection('complexity')}
            className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50"
          >
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-900">Komplexitätsstufe</span>
              {(activeFilters.complexity_min || activeFilters.complexity_max) && (
                <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
                  {activeFilters.complexity_min || 1}-{activeFilters.complexity_max || 10}
                </span>
              )}
            </div>
            {expandedSections.has('complexity') ? (
              <ChevronUp className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            )}
          </button>
          
          {expandedSections.has('complexity') && (
            <div className="px-4 pb-4 border-t border-gray-100">
              <div className="grid grid-cols-2 gap-4 mt-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Minimum
                  </label>
                  <select
                    value={activeFilters.complexity_min || ''}
                    onChange={(e) => handleComplexityChange('min', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Keine Grenze</option>
                    {Array.from({ length: 10 }, (_, i) => i + 1).map(num => (
                      <option key={num} value={num}>{num}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Maximum
                  </label>
                  <select
                    value={activeFilters.complexity_max || ''}
                    onChange={(e) => handleComplexityChange('max', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Keine Grenze</option>
                    {Array.from({ length: 10 }, (_, i) => i + 1).map(num => (
                      <option key={num} value={num}>{num}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="mt-3 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>🟢 Basic (1-3)</span>
                  <span>🟡 Intermediate (3-7)</span>
                  <span>🔴 Advanced (6-10)</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};