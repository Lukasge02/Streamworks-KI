import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  Database, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  BarChart3, 
  Eye, 
  RefreshCw, 
  Trash2,
  Download,
  Search,
  Filter,
  TrendingUp,
  Activity,
  Zap
} from 'lucide-react';
import { TrainingFile, FileAnalytics, SystemOverview } from '../../types';
import { apiService } from '../../services/apiService';

interface EnterpriseTrainingDataProps {
  // Props if needed
}

const EnterpriseTrainingData: React.FC<EnterpriseTrainingDataProps> = () => {
  const [files, setFiles] = useState<TrainingFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [systemOverview, setSystemOverview] = useState<SystemOverview | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileAnalytics, setFileAnalytics] = useState<FileAnalytics | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load files
      const filesResponse = await apiService.get<TrainingFile[]>('/api/v1/files/files');
      if (filesResponse.success && filesResponse.data) {
        setFiles(filesResponse.data);
      }

      // Load system overview
      const overviewResponse = await apiService.get<SystemOverview>('/api/v1/chunks/overview');
      if (overviewResponse.success && overviewResponse.data) {
        setSystemOverview(overviewResponse.data);
      }
    } catch (error) {
      console.error('Error loading training data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileAnalytics = async (fileId: string) => {
    try {
      const response = await apiService.get<FileAnalytics>(`/api/v1/chunks/files/${fileId}/chunks`);
      if (response.success && response.data) {
        setFileAnalytics(response.data);
        setSelectedFile(fileId);
      }
    } catch (error) {
      console.error('Error loading file analytics:', error);
    }
  };

  const handleReindex = async (fileId: string) => {
    try {
      const response = await apiService.post(`/api/v1/chunks/reindex/${fileId}`);
      if (response.success) {
        // Reload data after reindexing
        await loadData();
      }
    } catch (error) {
      console.error('Error reindexing file:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'indexed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      indexed: { bg: 'bg-green-100', text: 'text-green-800', label: 'Indexiert' },
      processing: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Verarbeitung' },
      uploaded: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Hochgeladen' },
      error: { bg: 'bg-red-100', text: 'text-red-800', label: 'Fehler' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.uploaded;
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {getStatusIcon(status)}
        <span className="ml-1">{config.label}</span>
      </span>
    );
  };

  const getQualityBadge = (score: number) => {
    if (score >= 0.85) return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Exzellent</span>;
    if (score >= 0.75) return <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">Gut</span>;
    if (score >= 0.6) return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">Akzeptabel</span>;
    return <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">Niedrig</span>;
  };

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.filename.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || file.processing_status === filterStatus;
    const matchesCategory = filterCategory === 'all' || file.category === filterCategory;
    
    return matchesSearch && matchesStatus && matchesCategory;
  });

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
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">🏆 Enterprise Training Data Management</h1>
        <p className="text-blue-100">Intelligente Dokumentenverwaltung mit Enterprise-Level Chunking und Analytics</p>
      </div>

      {/* System Overview Cards */}
      {systemOverview && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Gesamte Dateien</p>
                <p className="text-2xl font-bold text-gray-900">{systemOverview.overview.total_files}</p>
              </div>
              <Database className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Chunks Total</p>
                <p className="text-2xl font-bold text-gray-900">{systemOverview.overview.total_chunks}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Indexiert</p>
                <p className="text-2xl font-bold text-gray-900">{systemOverview.overview.indexed_files}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">System Health</p>
                <p className="text-2xl font-bold text-gray-900">{systemOverview.system_health.success_rate}%</p>
              </div>
              <Activity className={`w-8 h-8 ${
                systemOverview.system_health.status === 'excellent' ? 'text-green-500' :
                systemOverview.system_health.status === 'good' ? 'text-blue-500' :
                systemOverview.system_health.status === 'fair' ? 'text-yellow-500' : 'text-red-500'
              }`} />
            </div>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Dateien durchsuchen..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">Alle Status</option>
              <option value="indexed">Indexiert</option>
              <option value="processing">Verarbeitung</option>
              <option value="uploaded">Hochgeladen</option>
              <option value="error">Fehler</option>
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">Alle Kategorien</option>
              <option value="qa_docs">Q&A Docs</option>
              <option value="stream-xml">Stream XML</option>
              <option value="streamworks-api">StreamWorks API</option>
            </select>
          </div>
        </div>
      </div>

      {/* Files Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Dateien ({filteredFiles.length})</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Datei
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Chunks
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Qualität
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Kategorie
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hochgeladen
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Aktionen
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredFiles.map((file) => (
                <tr key={file.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{file.filename}</div>
                        <div className="text-sm text-gray-500">{(file.file_size / 1024).toFixed(1)} KB</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(file.processing_status || file.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <BarChart3 className="w-4 h-4 text-gray-400 mr-1" />
                      <span className="text-sm font-medium text-gray-900">{file.chunk_count || 0}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {file.quality_score ? getQualityBadge(file.quality_score) : (
                      <span className="text-sm text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">{file.category}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-500">
                      {new Date(file.upload_date).toLocaleDateString('de-DE')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleFileAnalytics(file.id)}
                        className="text-blue-600 hover:text-blue-900"
                        title="Chunk-Analyse anzeigen"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleReindex(file.id)}
                        className="text-green-600 hover:text-green-900"
                        title="Neu indexieren"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* File Analytics Modal */}
      {selectedFile && fileAnalytics && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">
                  📊 Chunk-Analyse: {fileAnalytics.file_info.filename}
                </h3>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6">
              {/* File Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-blue-600">Chunks Total</span>
                    <Zap className="w-5 h-5 text-blue-500" />
                  </div>
                  <p className="text-2xl font-bold text-blue-900">{fileAnalytics.statistics.total_chunks}</p>
                </div>
                
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-green-600">Ø Qualität</span>
                    <TrendingUp className="w-5 h-5 text-green-500" />
                  </div>
                  <p className="text-2xl font-bold text-green-900">{fileAnalytics.statistics.average_quality.toFixed(3)}</p>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-purple-600">Ø Länge</span>
                    <BarChart3 className="w-5 h-5 text-purple-500" />
                  </div>
                  <p className="text-2xl font-bold text-purple-900">{Math.round(fileAnalytics.statistics.average_length)}</p>
                </div>
              </div>

              {/* Quality Distribution */}
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Qualitätsverteilung</h4>
                <div className="flex space-x-2">
                  {Object.entries(fileAnalytics.statistics.quality_distribution).map(([quality, count]) => (
                    <div key={quality} className="flex-1 bg-gray-100 rounded-lg p-3 text-center">
                      <div className="text-sm font-medium text-gray-600 capitalize">{quality}</div>
                      <div className="text-xl font-bold text-gray-900">{count}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Chunks Preview */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">Chunks Vorschau</h4>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {fileAnalytics.chunks.slice(0, 5).map((chunk, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Chunk {chunk.index + 1}</span>
                        <div className="flex items-center space-x-2">
                          {getQualityBadge(chunk.quality_score)}
                          <span className="text-xs text-gray-500">{chunk.chunk_type}</span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600">{chunk.content.substring(0, 150)}...</p>
                      <div className="mt-2 text-xs text-gray-500">
                        Länge: {chunk.content_length} | Semantic: {chunk.semantic_density.toFixed(3)} | Readability: {chunk.readability_score.toFixed(3)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnterpriseTrainingData;