import React, { useState, useEffect } from 'react';
import { 
  Database, BarChart3, FileText, TrendingUp, Activity, Zap, 
  RefreshCw, Eye, Clock, AlertCircle, CheckCircle, Target,
  PieChart, LineChart, Settings, Download
} from 'lucide-react';
import { apiService } from '../../services/apiService';
import { ChunkingExplanation } from './ChunkingExplanation';
import { FileListTable } from './FileListTable';

interface EnterpriseData {
  timestamp: string;
  system_overview: {
    total_files: number;
    total_chunks: number;
    total_characters: number;
    avg_chunks_per_file: number;
    indexing_efficiency: number;
  };
  file_analytics: Array<{
    file_id: string;
    filename: string;
    total_chunks: number;
    total_characters: number;
    avg_chunk_size: number;
    min_chunk_size: number;
    max_chunk_size: number;
    avg_quality: number;
    quality_distribution: {
      excellent: number;
      good: number;
      acceptable: number;
      poor: number;
    };
    chunk_types: Record<string, number>;
    file_size_bytes: number;
    compression_ratio: number;
    indexed_at: string;
  }>;
  system_analytics: {
    chunk_size_stats: {
      avg_size: number;
      min_size: number;
      max_size: number;
      std_deviation: number;
      size_distribution: {
        small: number;
        medium: number;
        large: number;
      };
    };
    quality_stats: {
      avg_quality: number;
      quality_std_dev: number;
      quality_range: {
        min: number;
        max: number;
      };
    };
    indexing_timeline: any;
    content_density: number;
  };
  performance_metrics: {
    embedding_efficiency: {
      avg_semantic_density: number;
      high_density_chunks: number;
      low_density_chunks: number;
    };
    readability_metrics: {
      avg_readability: number;
      highly_readable: number;
      poorly_readable: number;
    };
    retrieval_potential: {
      optimal_chunks: number;
      suboptimal_chunks: number;
    };
  };
  quality_insights: string[];
  recommendations: string[];
}

export const EnterpriseChunksAnalysis: React.FC = () => {
  const [data, setData] = useState<EnterpriseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadEnterpriseData();
  }, []);

  const loadEnterpriseData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.get<EnterpriseData>('/chunks/enterprise-analysis');
      if (response.success && response.data) {
        setData(response.data);
      } else {
        setError(response.error || 'Failed to load enterprise data');
      }
    } catch (err) {
      setError('Failed to load enterprise analysis');
      console.error('Error loading enterprise data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadEnterpriseData();
    setRefreshing(false);
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const getQualityColor = (quality: number): string => {
    if (quality >= 0.8) return 'text-green-600';
    if (quality >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getQualityBadge = (quality: number): string => {
    if (quality >= 0.8) return 'bg-green-100 text-green-800';
    if (quality >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-500 mb-4">{error}</div>
        <button 
          onClick={loadEnterpriseData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) {
    return <div className="text-center py-8">No data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Enterprise Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold mb-2">🏢 Enterprise Chunks Analysis</h1>
            <p className="text-blue-100">Comprehensive RAG System Analytics & Intelligence</p>
            <p className="text-xs text-blue-200 mt-1">Last updated: {new Date(data.timestamp).toLocaleString('de-DE')}</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors">
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>

      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Files</p>
              <p className="text-2xl font-bold text-gray-900">{data.system_overview.total_files}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-500" />
          </div>
          <div className="mt-2 text-xs text-gray-500">
            {(data.system_overview.indexing_efficiency * 100).toFixed(1)}% indexed
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Chunks</p>
              <p className="text-2xl font-bold text-gray-900">{data.system_overview.total_chunks}</p>
            </div>
            <Database className="w-8 h-8 text-green-500" />
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Ø {data.system_overview.avg_chunks_per_file.toFixed(1)} per file
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Characters</p>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(data.system_overview.total_characters)}</p>
            </div>
            <BarChart3 className="w-8 h-8 text-purple-500" />
          </div>
          <div className="mt-2 text-xs text-gray-500">
            {Math.round(data.system_analytics.content_density)} per file
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Quality</p>
              <p className={`text-2xl font-bold ${getQualityColor(data.system_analytics.quality_stats.avg_quality)}`}>
                {(data.system_analytics.quality_stats.avg_quality * 100).toFixed(1)}%
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Range: {(data.system_analytics.quality_stats.quality_range.min * 100).toFixed(1)}% - {(data.system_analytics.quality_stats.quality_range.max * 100).toFixed(1)}%
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Chunk Size</p>
              <p className="text-2xl font-bold text-gray-900">{Math.round(data.system_analytics.chunk_size_stats.avg_size)}</p>
            </div>
            <Target className="w-8 h-8 text-orange-500" />
          </div>
          <div className="mt-2 text-xs text-gray-500">
            {data.system_analytics.chunk_size_stats.min_size} - {data.system_analytics.chunk_size_stats.max_size}
          </div>
        </div>
      </div>

      {/* Chunk Size Distribution */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📏 Chunk Size Distribution</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-blue-600">Small (&lt;300)</span>
              <PieChart className="w-4 h-4 text-blue-500" />
            </div>
            <div className="text-2xl font-bold text-blue-900">{data.system_analytics.chunk_size_stats.size_distribution.small}</div>
            <div className="text-xs text-blue-700">
              {((data.system_analytics.chunk_size_stats.size_distribution.small / data.system_overview.total_chunks) * 100).toFixed(1)}%
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-green-600">Medium (300-800)</span>
              <PieChart className="w-4 h-4 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-green-900">{data.system_analytics.chunk_size_stats.size_distribution.medium}</div>
            <div className="text-xs text-green-700">
              {((data.system_analytics.chunk_size_stats.size_distribution.medium / data.system_overview.total_chunks) * 100).toFixed(1)}%
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-purple-600">Large (&gt;800)</span>
              <PieChart className="w-4 h-4 text-purple-500" />
            </div>
            <div className="text-2xl font-bold text-purple-900">{data.system_analytics.chunk_size_stats.size_distribution.large}</div>
            <div className="text-xs text-purple-700">
              {((data.system_analytics.chunk_size_stats.size_distribution.large / data.system_overview.total_chunks) * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ Performance Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Avg Semantic Density</span>
              <span className="text-sm font-medium text-gray-900">
                {(data.performance_metrics.embedding_efficiency.avg_semantic_density * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">High Density Chunks</span>
              <span className="text-sm font-medium text-green-600">
                {data.performance_metrics.embedding_efficiency.high_density_chunks}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Avg Readability</span>
              <span className="text-sm font-medium text-gray-900">
                {(data.performance_metrics.readability_metrics.avg_readability * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Optimal Chunks</span>
              <span className="text-sm font-medium text-green-600">
                {data.performance_metrics.retrieval_potential.optimal_chunks}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 Quality Insights</h3>
          <div className="space-y-3">
            {data.quality_insights.map((insight, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <Activity className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-blue-900">{insight}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Enterprise Recommendations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.recommendations.map((recommendation, index) => (
            <div key={index} className="flex items-start space-x-3 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <Zap className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-yellow-900">{recommendation}</span>
            </div>
          ))}
        </div>
      </div>

      {/* File Analytics Table */}
      <FileListTable files={data.file_analytics} onRefresh={handleRefresh} />

      {/* Chunking Explanation */}
      <ChunkingExplanation />

      {/* System Health Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🏥 System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <div>
              <div className="text-sm font-medium text-gray-900">Indexing Efficiency</div>
              <div className="text-xs text-gray-600">{(data.system_overview.indexing_efficiency * 100).toFixed(1)}%</div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Activity className="w-6 h-6 text-blue-500" />
            <div>
              <div className="text-sm font-medium text-gray-900">Quality Score</div>
              <div className="text-xs text-gray-600">{(data.system_analytics.quality_stats.avg_quality * 100).toFixed(1)}%</div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Database className="w-6 h-6 text-purple-500" />
            <div>
              <div className="text-sm font-medium text-gray-900">Content Density</div>
              <div className="text-xs text-gray-600">{Math.round(data.system_analytics.content_density)} chars/file</div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Target className="w-6 h-6 text-orange-500" />
            <div>
              <div className="text-sm font-medium text-gray-900">Optimal Chunks</div>
              <div className="text-xs text-gray-600">{data.performance_metrics.retrieval_potential.optimal_chunks}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};