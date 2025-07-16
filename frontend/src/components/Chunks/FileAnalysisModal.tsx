import React, { useState, useEffect } from 'react';
import { X, FileText, BarChart3, TrendingUp, Target, Zap, RefreshCw } from 'lucide-react';
import { apiService } from '../../services/apiService';

interface FileAnalysisData {
  file_info: {
    id: string;
    filename: string;
    category: string;
    folder: string;
    chunk_count: number;
    processing_status: string;
    created_at: string;
    last_indexed_at: string;
  };
  chunks: Array<{
    index: number;
    content: string;
    content_length: number;
    metadata: Record<string, any>;
    quality_score: number;
    semantic_density: number;
    readability_score: number;
    chunk_type: string;
    strategy_used: string;
    quality_assessment: string;
    key_concepts: string[];
    entities: string[];
  }>;
  statistics: {
    total_chunks: number;
    average_quality: number;
    average_length: number;
    chunk_types: Record<string, number>;
    strategies_used: Record<string, number>;
    quality_distribution: Record<string, number>;
  };
  visualization_data: {
    chunk_timeline: Array<{
      index: number;
      start_char: number;
      end_char: number;
      length: number;
      quality: number;
      type: string;
    }>;
    quality_heatmap: Array<{
      index: number;
      quality_score: number;
      semantic_density: number;
      readability_score: number;
    }>;
  };
}

interface FileAnalysisModalProps {
  fileId: string;
  filename: string;
  onClose: () => void;
}

export const FileAnalysisModal: React.FC<FileAnalysisModalProps> = ({ fileId, filename, onClose }) => {
  const [data, setData] = useState<FileAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'chunks' | 'quality' | 'performance'>('overview');

  useEffect(() => {
    loadFileAnalysis();
  }, [fileId]);

  const loadFileAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.get<FileAnalysisData>(`/chunks/files/${fileId}/chunks`);
      if (response.success && response.data) {
        setData(response.data);
      } else {
        setError(response.error || 'Failed to load file analysis');
      }
    } catch (err) {
      setError('Failed to load file analysis');
      console.error('Error loading file analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const getQualityColor = (quality: number): string => {
    if (quality >= 0.85) return 'text-green-600';
    if (quality >= 0.75) return 'text-blue-600';
    if (quality >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getQualityBadge = (quality: number): string => {
    if (quality >= 0.85) return 'bg-green-100 text-green-800';
    if (quality >= 0.75) return 'bg-blue-100 text-blue-800';
    if (quality >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getQualityLabel = (quality: number): string => {
    if (quality >= 0.85) return 'Exzellent';
    if (quality >= 0.75) return 'Gut';
    if (quality >= 0.6) return 'Akzeptabel';
    return 'Niedrig';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg p-6">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-center text-gray-600">Analyzing file...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg p-6 max-w-md w-full">
          <div className="text-center">
            <div className="text-red-500 mb-4">{error}</div>
            <div className="space-x-2">
              <button 
                onClick={loadFileAnalysis}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Retry
              </button>
              <button 
                onClick={onClose}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 sticky top-0 bg-white">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold text-gray-900">📊 File Analysis</h2>
              <p className="text-sm text-gray-600 mt-1">{filename}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          
          {/* Tabs */}
          <div className="mt-4 flex space-x-1 bg-gray-100 p-1 rounded-lg">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'chunks', label: 'Chunks', icon: FileText },
              { id: 'quality', label: 'Quality', icon: TrendingUp },
              { id: 'performance', label: 'Performance', icon: Target }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* File Info */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-blue-600">Total Chunks</div>
                  <div className="text-2xl font-bold text-blue-900">{data.statistics.total_chunks}</div>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-green-600">Avg Quality</div>
                  <div className={`text-2xl font-bold ${getQualityColor(data.statistics.average_quality)}`}>
                    {(data.statistics.average_quality * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-purple-600">Avg Length</div>
                  <div className="text-2xl font-bold text-purple-900">{Math.round(data.statistics.average_length)}</div>
                </div>
                <div className="bg-orange-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-orange-600">Last Indexed</div>
                  <div className="text-sm font-bold text-orange-900">
                    {data.file_info.last_indexed_at ? new Date(data.file_info.last_indexed_at).toLocaleDateString('de-DE') : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Quality Distribution */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Quality Distribution</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(data.statistics.quality_distribution).map(([quality, count]) => (
                    <div key={quality} className="text-center">
                      <div className="text-lg font-bold text-gray-900">{count}</div>
                      <div className="text-xs text-gray-600 capitalize">{quality}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Chunk Types */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Chunk Types</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {Object.entries(data.statistics.chunk_types).map(([type, count]) => (
                    <div key={type} className="bg-gray-50 rounded p-3">
                      <div className="text-sm font-medium text-gray-900">{type}</div>
                      <div className="text-xs text-gray-600">{count} chunks</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'chunks' && (
            <div className="space-y-4">
              <div className="text-sm text-gray-600">
                Showing {data.chunks.length} chunks from {filename}
              </div>
              {data.chunks.slice(0, 10).map((chunk, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Chunk {chunk.index + 1}</span>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getQualityBadge(chunk.quality_score)}`}>
                        {getQualityLabel(chunk.quality_score)}
                      </span>
                      <span className="text-xs text-gray-500">{chunk.chunk_type}</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{chunk.content.substring(0, 300)}...</p>
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span>Length: {chunk.content_length}</span>
                    <span>Quality: {(chunk.quality_score * 100).toFixed(1)}%</span>
                    <span>Semantic: {(chunk.semantic_density * 100).toFixed(1)}%</span>
                    <span>Readability: {(chunk.readability_score * 100).toFixed(1)}%</span>
                  </div>
                </div>
              ))}
              {data.chunks.length > 10 && (
                <div className="text-center py-4 text-gray-500">
                  ... and {data.chunks.length - 10} more chunks
                </div>
              )}
            </div>
          )}

          {activeTab === 'quality' && (
            <div className="space-y-6">
              {/* Quality Heatmap */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Quality Heatmap</h4>
                <div className="grid grid-cols-10 gap-1">
                  {data.visualization_data.quality_heatmap.map((point, index) => (
                    <div
                      key={index}
                      className={`h-8 w-8 rounded ${getQualityBadge(point.quality_score).replace('text-', 'bg-').replace('-800', '-200')}`}
                      title={`Chunk ${point.index + 1}: ${(point.quality_score * 100).toFixed(1)}%`}
                    />
                  ))}
                </div>
              </div>

              {/* Quality Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-blue-600">Average Quality</div>
                  <div className="text-2xl font-bold text-blue-900">
                    {(data.statistics.average_quality * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-green-600">Best Chunk</div>
                  <div className="text-2xl font-bold text-green-900">
                    {Math.max(...data.chunks.map(c => c.quality_score * 100)).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-red-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-red-600">Lowest Quality</div>
                  <div className="text-2xl font-bold text-red-900">
                    {Math.min(...data.chunks.map(c => c.quality_score * 100)).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div className="space-y-6">
              {/* Performance Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-purple-600">Avg Semantic Density</div>
                  <div className="text-2xl font-bold text-purple-900">
                    {(data.chunks.reduce((sum, c) => sum + c.semantic_density, 0) / data.chunks.length * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-indigo-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-indigo-600">Avg Readability</div>
                  <div className="text-2xl font-bold text-indigo-900">
                    {(data.chunks.reduce((sum, c) => sum + c.readability_score, 0) / data.chunks.length * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-teal-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-teal-600">Optimal Chunks</div>
                  <div className="text-2xl font-bold text-teal-900">
                    {data.chunks.filter(c => c.quality_score > 0.8 && c.content_length > 200).length}
                  </div>
                </div>
              </div>

              {/* Performance Chart */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Performance Distribution</h4>
                <div className="space-y-3">
                  {data.chunks.slice(0, 10).map((chunk, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <span className="text-xs text-gray-500 w-12">#{chunk.index + 1}</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${chunk.quality_score * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600 w-12">{(chunk.quality_score * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              File ID: {data.file_info.id}
            </div>
            <div className="flex space-x-2">
              <button className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                <RefreshCw className="w-4 h-4 inline mr-1" />
                Reindex
              </button>
              <button 
                onClick={onClose}
                className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};