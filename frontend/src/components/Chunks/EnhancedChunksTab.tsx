import React, { useState, useEffect } from 'react';
import { 
  Search, Database, FileText, Clock, Filter, Grid, BarChart3, 
  RefreshCw, Eye, TrendingUp, Activity, CheckCircle
} from 'lucide-react';
import { SystemOverview, QualityAnalysis } from '../../types';
import { apiService } from '../../services/apiService';
import { ErrorBoundary } from '../ErrorHandling/ErrorBoundary';

interface ChunksTabProps {
  // Props if needed
}

export const EnhancedChunksTab: React.FC<ChunksTabProps> = () => {
  const [systemOverview, setSystemOverview] = useState<SystemOverview | null>(null);
  const [qualityAnalysis, setQualityAnalysis] = useState<QualityAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadChunksData();
  }, []);

  const loadChunksData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [overviewResponse, qualityResponse] = await Promise.all([
        apiService.get<SystemOverview>('/api/v1/chunks/overview'),
        apiService.get<QualityAnalysis>('/api/v1/chunks/quality-analysis')
      ]);
      
      if (overviewResponse.success && overviewResponse.data) {
        setSystemOverview(overviewResponse.data);
      }
      
      if (qualityResponse.success && qualityResponse.data) {
        setQualityAnalysis(qualityResponse.data);
      }
    } catch (err) {
      setError('Failed to load chunks data');
      console.error('Error loading chunks data:', err);
    } finally {
      setLoading(false);
    }
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
          onClick={loadChunksData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Enterprise Header */}
      <div className="bg-gradient-to-r from-orange-600 to-red-600 rounded-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold mb-2">🧩 Enterprise Chunks Analysis</h1>
            <p className="text-orange-100">Detaillierte Analyse der Chunk-Qualität und -Verteilung</p>
          </div>
          <button
            onClick={loadChunksData}
            className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Aktualisieren</span>
          </button>
        </div>
      </div>

      {/* System Overview */}
      {systemOverview && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Chunks</p>
                <p className="text-2xl font-bold text-gray-900">{systemOverview.overview.total_chunks}</p>
              </div>
              <Grid className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Indexierte Dateien</p>
                <p className="text-2xl font-bold text-gray-900">{systemOverview.overview.indexed_files}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Kategorien</p>
                <p className="text-2xl font-bold text-gray-900">{Object.keys(systemOverview.overview.categories).length}</p>
              </div>
              <Database className="w-8 h-8 text-purple-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">System Health</p>
                <p className="text-2xl font-bold text-gray-900">{systemOverview.system_health.success_rate}%</p>
              </div>
              <Activity className="w-8 h-8 text-green-500" />
            </div>
          </div>
        </div>
      )}

      {/* Quality Metrics */}
      {qualityAnalysis && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Chunk-Qualitätsmetriken</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{qualityAnalysis.quality_metrics.quality_buckets.excellent}</div>
              <div className="text-sm text-gray-600">Exzellent</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{qualityAnalysis.quality_metrics.quality_buckets.good}</div>
              <div className="text-sm text-gray-600">Gut</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{qualityAnalysis.quality_metrics.quality_buckets.acceptable}</div>
              <div className="text-sm text-gray-600">Akzeptabel</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{qualityAnalysis.quality_metrics.quality_buckets.poor}</div>
              <div className="text-sm text-gray-600">Niedrig</div>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Durchschnittliche Qualität</span>
              <span className="text-lg font-bold text-gray-900">{qualityAnalysis.quality_metrics.average_quality.toFixed(3)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Categories Distribution */}
      {systemOverview && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📁 Kategorien-Verteilung</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(systemOverview.overview.categories).map(([categoryName, data]) => (
              <div key={categoryName} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{categoryName}</span>
                  <Database className="w-4 h-4 text-gray-400" />
                </div>
                <div className="text-xl font-bold text-gray-900">{data.files} Dateien</div>
                <div className="text-sm text-gray-600">{data.chunks} Chunks</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {qualityAnalysis && qualityAnalysis.recommendations && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Empfehlungen</h3>
          <div className="space-y-2">
            {qualityAnalysis.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <TrendingUp className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-blue-900">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};