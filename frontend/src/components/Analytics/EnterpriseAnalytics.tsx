import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  Database, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  Zap,
  Target,
  PieChart,
  LineChart,
  RefreshCw
} from 'lucide-react';
import { QualityAnalysis, SystemOverview } from '../../types';
import { apiService } from '../../services/apiService';

const EnterpriseAnalytics: React.FC = () => {
  const [qualityAnalysis, setQualityAnalysis] = useState<QualityAnalysis | null>(null);
  const [systemOverview, setSystemOverview] = useState<SystemOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      // Load quality analysis
      const qualityResponse = await apiService.get<QualityAnalysis>('/api/v1/chunks/quality-analysis');
      if (qualityResponse.success && qualityResponse.data) {
        setQualityAnalysis(qualityResponse.data);
      }

      // Load system overview
      const overviewResponse = await apiService.get<SystemOverview>('/api/v1/chunks/overview');
      if (overviewResponse.success && overviewResponse.data) {
        setSystemOverview(overviewResponse.data);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAnalytics();
    setRefreshing(false);
  };

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'good': return 'text-blue-600 bg-blue-100';
      case 'fair': return 'text-yellow-600 bg-yellow-100';
      case 'poor': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent': return <CheckCircle className="w-5 h-5" />;
      case 'good': return <TrendingUp className="w-5 h-5" />;
      case 'fair': return <Activity className="w-5 h-5" />;
      case 'poor': return <AlertTriangle className="w-5 h-5" />;
      default: return <Database className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Enterprise Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold mb-2">📊 Enterprise Analytics Dashboard</h1>
            <p className="text-indigo-100">Performance Metriken und Qualitätsanalyse für das RAG-System</p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Aktualisieren</span>
          </button>
        </div>
      </div>

      {/* System Health Overview */}
      {systemOverview && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">🏥 System Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full ${getHealthStatusColor(systemOverview.system_health.status)} mb-3`}>
                {getHealthStatusIcon(systemOverview.system_health.status)}
              </div>
              <div className="text-2xl font-bold text-gray-900">{systemOverview.system_health.success_rate}%</div>
              <div className="text-sm text-gray-600">Erfolgsrate</div>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 text-green-600 mb-3">
                <CheckCircle className="w-5 h-5" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{systemOverview.system_health.indexed_files}</div>
              <div className="text-sm text-gray-600">Indexierte Dateien</div>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 text-blue-600 mb-3">
                <Database className="w-5 h-5" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{systemOverview.system_health.total_files}</div>
              <div className="text-sm text-gray-600">Gesamte Dateien</div>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-100 text-red-600 mb-3">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{systemOverview.system_health.failed_files}</div>
              <div className="text-sm text-gray-600">Fehlgeschlagen</div>
            </div>
          </div>
        </div>
      )}

      {/* Quality Analysis */}
      {qualityAnalysis && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Quality Metrics */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Qualitätsmetriken</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Durchschnittliche Qualität</span>
                <span className="text-lg font-bold text-gray-900">
                  {qualityAnalysis.quality_metrics.average_quality.toFixed(3)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Gesamte Chunks</span>
                <span className="text-lg font-bold text-gray-900">
                  {qualityAnalysis.quality_metrics.total_chunks}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Qualitätsbereich</span>
                <span className="text-lg font-bold text-gray-900">
                  {qualityAnalysis.quality_metrics.quality_range.min.toFixed(3)} - {qualityAnalysis.quality_metrics.quality_range.max.toFixed(3)}
                </span>
              </div>
            </div>
          </div>

          {/* Quality Distribution */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Qualitätsverteilung</h3>
            <div className="space-y-3">
              {Object.entries(qualityAnalysis.quality_metrics.quality_buckets).map(([quality, count]) => {
                const percentage = (count / qualityAnalysis.quality_metrics.total_chunks) * 100;
                const colorConfig = {
                  excellent: 'bg-green-500',
                  good: 'bg-blue-500',
                  acceptable: 'bg-yellow-500',
                  poor: 'bg-red-500'
                };
                
                return (
                  <div key={quality}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700 capitalize">{quality}</span>
                      <span className="text-sm text-gray-600">{count} ({percentage.toFixed(1)}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${colorConfig[quality as keyof typeof colorConfig]}`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Chunk Size Distribution */}
      {qualityAnalysis && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📏 Chunk-Größenverteilung</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-600">Klein (&lt;300)</span>
                <Target className="w-4 h-4 text-blue-500" />
              </div>
              <div className="text-2xl font-bold text-blue-900">{qualityAnalysis.chunk_distribution.size_distribution.small}</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-green-600">Mittel (300-800)</span>
                <Target className="w-4 h-4 text-green-500" />
              </div>
              <div className="text-2xl font-bold text-green-900">{qualityAnalysis.chunk_distribution.size_distribution.medium}</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-purple-600">Groß (&gt;800)</span>
                <Target className="w-4 h-4 text-purple-500" />
              </div>
              <div className="text-2xl font-bold text-purple-900">{qualityAnalysis.chunk_distribution.size_distribution.large}</div>
            </div>
          </div>
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Durchschnittliche Chunk-Größe</span>
              <span className="text-lg font-bold text-gray-900">{Math.round(qualityAnalysis.chunk_distribution.average_size)} Zeichen</span>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {qualityAnalysis && qualityAnalysis.recommendations && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Empfehlungen</h3>
          <div className="space-y-3">
            {qualityAnalysis.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <Zap className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-blue-900">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Categories Overview */}
      {systemOverview && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📁 Kategorien-Übersicht</h3>
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

      {/* Recent Activity */}
      {systemOverview && systemOverview.recent_files && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">⏱️ Letzte Aktivität</h3>
          <div className="space-y-3">
            {systemOverview.recent_files.slice(0, 5).map((file) => (
              <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Database className="w-4 h-4 text-blue-600" />
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">{file.filename}</div>
                    <div className="text-xs text-gray-500">{file.category}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">{file.chunks} Chunks</div>
                  <div className="text-xs text-gray-500">{file.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnterpriseAnalytics;