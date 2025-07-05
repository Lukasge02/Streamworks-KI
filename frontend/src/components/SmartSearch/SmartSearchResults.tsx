import React, { useState } from 'react';
import { 
  FileText, 
  Clock, 
  Zap, 
  Copy, 
  ChevronDown,
  ChevronUp,
  Filter,
  BarChart3,
  Info,
  CheckCircle,
  Target
} from 'lucide-react';
import { SmartSearchResponse } from '../../types';

interface SmartSearchResultsProps {
  results: SmartSearchResponse;
}

export const SmartSearchResults: React.FC<SmartSearchResultsProps> = ({ results }) => {
  const [expandedResults, setExpandedResults] = useState<Set<number>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const toggleResult = (index: number) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedResults(newExpanded);
  };

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getComplexityColor = (complexity: number) => {
    if (complexity <= 3) return 'text-green-600';
    if (complexity <= 7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getFileTypeIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    const icons: Record<string, string> = {
      'pdf': '📄',
      'doc': '📝',
      'docx': '📝',
      'txt': '📄',
      'md': '📋',
      'html': '🌐',
      'xml': '🔗',
      'json': '📊',
      'csv': '📊',
      'xlsx': '📊',
      'py': '🐍',
      'js': '📜',
      'ts': '📜'
    };
    return icons[extension || ''] || '📄';
  };

  const formatResponseTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const getStrategyDisplayName = (strategy: string) => {
    const strategies: Record<string, string> = {
      'semantic_only': 'Semantic Only',
      'filtered': 'Filtered Search',
      'hybrid': 'Hybrid Search',
      'contextual': 'Contextual Search',
      'concept_based': 'Concept-Based'
    };
    return strategies[strategy] || strategy;
  };

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border border-green-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Suchergebnisse</h3>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <FileText className="w-4 h-4" />
              <span>{results.total_results} Ergebnisse</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="w-4 h-4" />
              <span>{formatResponseTime(results.response_time_ms)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Zap className="w-4 h-4" />
              <span>{getStrategyDisplayName(results.search_strategy_used)}</span>
            </div>
          </div>
        </div>
        
        <div className="text-sm text-gray-700">
          <strong>Query:</strong> "{results.query}"
        </div>
        
        {/* Performance Metrics */}
        {results.performance_metrics && (
          <div className="mt-3 grid grid-cols-3 gap-4 text-xs">
            <div className="text-center p-2 bg-white rounded">
              <div className="font-medium text-gray-900">Strategy Selection</div>
              <div className="text-blue-600">{results.performance_metrics.strategy_selection_time.toFixed(1)}ms</div>
            </div>
            <div className="text-center p-2 bg-white rounded">
              <div className="font-medium text-gray-900">Search Execution</div>
              <div className="text-green-600">{results.performance_metrics.search_execution_time.toFixed(1)}ms</div>
            </div>
            <div className="text-center p-2 bg-white rounded">
              <div className="font-medium text-gray-900">Result Processing</div>
              <div className="text-purple-600">{results.performance_metrics.result_processing_time.toFixed(1)}ms</div>
            </div>
          </div>
        )}
      </div>

      {/* Applied Filters */}
      {results.filter_applied && Object.keys(results.filter_applied).length > 0 && (
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <Filter className="w-4 h-4 text-blue-600" />
            <span className="font-medium text-blue-900">Angewendete Filter</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {results.filter_applied.document_types?.map((type) => (
              <span key={type} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                📄 {type}
              </span>
            ))}
            {results.filter_applied.file_formats?.map((format) => (
              <span key={format} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                📁 {format}
              </span>
            ))}
            {results.filter_applied.source_categories?.map((category) => (
              <span key={category} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                🗂️ {category}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Search Results */}
      <div className="space-y-4">
        {results.results.map((result, index) => (
          <div key={index} className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
            {/* Result Header */}
            <div className="p-4 border-b border-gray-100">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg">{getFileTypeIcon(result.metadata.filename)}</span>
                    <h4 className="font-medium text-gray-900">{result.metadata.filename}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreColor(result.score)}`}>
                      {Math.round(result.score * 100)}% Relevanz
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>📂 {result.metadata.source_type}</span>
                    <span>🔧 {result.metadata.chunk_type}</span>
                    <span className={getComplexityColor(result.metadata.complexity_score)}>
                      🎯 Komplexität {result.metadata.complexity_score}/10
                    </span>
                    <span>⚡ {result.metadata.processing_method}</span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => copyToClipboard(result.content, `result-${index}`)}
                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                    title="Inhalt kopieren"
                  >
                    {copiedId === `result-${index}` ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                  <button
                    onClick={() => toggleResult(index)}
                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {expandedResults.has(index) ? (
                      <ChevronUp className="w-4 h-4" />
                    ) : (
                      <ChevronDown className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Result Content Preview */}
            <div className="p-4">
              <div className="text-sm text-gray-700 leading-relaxed">
                {expandedResults.has(index) ? (
                  <div className="whitespace-pre-wrap">{result.content}</div>
                ) : (
                  <div>
                    {result.content.length > 200 
                      ? `${result.content.substring(0, 200)}...` 
                      : result.content
                    }
                  </div>
                )}
              </div>
              
              {/* Explanation */}
              {result.explanation && (
                <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-start space-x-2">
                    <Info className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="font-medium text-yellow-900 text-sm">Warum dieses Ergebnis relevant ist:</div>
                      <div className="text-yellow-800 text-sm mt-1">{result.explanation}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Metadata Details (when expanded) */}
              {expandedResults.has(index) && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-xs text-gray-600 space-y-1">
                    <div><strong>Relevanz-Score:</strong> {result.metadata.relevance_score.toFixed(3)}</div>
                    <div><strong>Quelle:</strong> {result.source}</div>
                    {Object.entries(result.metadata).map(([key, value]) => (
                      key !== 'filename' && key !== 'source_type' && key !== 'chunk_type' && 
                      key !== 'processing_method' && key !== 'complexity_score' && key !== 'relevance_score' && (
                        <div key={key}>
                          <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {
                            typeof value === 'object' ? JSON.stringify(value) : String(value)
                          }
                        </div>
                      )
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* No Results */}
      {results.total_results === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-4">
            <Target className="w-16 h-16 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Keine Ergebnisse gefunden
            </h3>
            <p className="text-sm text-gray-600 max-w-md mx-auto">
              Versuchen Sie es mit anderen Suchbegriffen oder passen Sie die Filter an.
            </p>
          </div>
        </div>
      )}

      {/* Search Summary */}
      {results.total_results > 0 && (
        <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-600">
          <div className="flex items-center space-x-2 mb-2">
            <BarChart3 className="w-4 h-4" />
            <span className="font-medium">Such-Zusammenfassung</span>
          </div>
          <div className="space-y-1">
            <div>
              <strong>Strategie:</strong> {getStrategyDisplayName(results.search_strategy_used)} 
              wurde automatisch für optimale Ergebnisse ausgewählt.
            </div>
            <div>
              <strong>Performance:</strong> {results.total_results} Ergebnisse in {formatResponseTime(results.response_time_ms)} 
              mit durchschnittlicher Relevanz von {
                results.results.length > 0 
                  ? Math.round((results.results.reduce((sum, r) => sum + r.score, 0) / results.results.length) * 100)
                  : 0
              }%.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};