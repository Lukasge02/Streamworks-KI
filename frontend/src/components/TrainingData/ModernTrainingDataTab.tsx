import React, { useState, useEffect, useCallback } from 'react';
import { 
  Upload, FileText, Database, Search, AlertCircle, 
  CheckCircle, Clock, Trash2, RefreshCw, Archive,
  FolderOpen, Plus, Filter
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../../services/apiService';
import { motion, AnimatePresence } from 'framer-motion';

interface TrainingFile {
  id: string;
  filename: string;
  display_name?: string;
  category: 'help_data' | 'stream_templates';
  file_path: string;
  upload_date: string;
  file_size: number;
  status: 'uploading' | 'processing' | 'ready' | 'error' | 'indexed';
  error_message?: string;
  is_indexed: boolean;
  indexed_at?: string;
  chunk_count: number;
  index_status?: string;
  index_error?: string;
}

interface ChromaDBStats {
  indexed_files: number;
  total_chunks: number;
  collection_documents: number;
  by_category: {
    help_data: number;
    stream_templates: number;
  };
  vector_db_path: string;
  embedding_model: string;
}

const ModernTrainingDataTab: React.FC = () => {
  const [files, setFiles] = useState<TrainingFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);
  const [stats, setStats] = useState<ChromaDBStats | null>(null);

  const categories = [
    { id: 'all', name: 'Alle Dateien', icon: FolderOpen },
    { id: 'help_data', name: 'Hilfe-Daten', icon: FileText },
    { id: 'stream_templates', name: 'Stream-Templates', icon: Database }
  ];

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'indexed': return 'text-green-600 bg-green-50';
      case 'ready': return 'text-blue-600 bg-blue-50';
      case 'processing': return 'text-yellow-600 bg-yellow-50';
      case 'error': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'indexed': return <CheckCircle className="w-4 h-4" />;
      case 'ready': return <CheckCircle className="w-4 h-4" />;
      case 'processing': return <Clock className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const loadFiles = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiService.getTrainingFiles();
      setFiles(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Error loading files:', err);
      setError('Fehler beim Laden der Dateien');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const response = await apiService.getChromaDBStats();
      setStats(response.data || null);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  }, []);

  useEffect(() => {
    loadFiles();
    loadStats();
  }, [loadFiles, loadStats]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    try {
      for (const file of acceptedFiles) {
        await apiService.uploadTrainingFile(file, selectedCategory === 'all' ? 'help_data' : selectedCategory as any);
      }
      await loadFiles();
      await loadStats();
    } catch (err) {
      console.error('Upload error:', err);
      setError('Fehler beim Hochladen der Dateien');
    } finally {
      setUploading(false);
    }
  }, [selectedCategory, loadFiles, loadStats]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/markdown': ['.md'],
      'text/html': ['.html']
    },
    multiple: true
  });

  const deleteFile = async (fileId: string) => {
    try {
      await apiService.deleteTrainingFile(fileId);
      await loadFiles();
      await loadStats();
    } catch (err) {
      console.error('Delete error:', err);
      setError('Fehler beim Löschen der Datei');
    }
  };

  const filteredFiles = files.filter(file => {
    const matchesCategory = selectedCategory === 'all' || file.category === selectedCategory;
    const matchesSearch = file.filename.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="h-full bg-gradient-to-br from-gray-50 via-white to-gray-50 rounded-2xl shadow-2xl backdrop-blur-lg border border-gray-200/50 flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-gray-200/50 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg">
              <Database className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">Training Data Management</h2>
              <p className="text-sm text-gray-500">Dokumentenverwaltung und Indexierung</p>
            </div>
          </div>
          {stats && (
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>{stats.indexed_files} Dateien indexiert</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>{stats.total_chunks} Chunks</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Filter & Search */}
      <div className="flex-shrink-0 bg-white/50 backdrop-blur-sm border-b border-gray-200/50 p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select 
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 bg-white/80 border border-gray-300/50 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500/50"
            >
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Dateien durchsuchen..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white/80 border border-gray-300/50 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500/50"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Upload Area */}
      <div className="flex-shrink-0 p-6 border-b border-gray-200/50">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
            isDragActive 
              ? 'border-green-500 bg-green-50/50' 
              : 'border-gray-300 hover:border-green-400 hover:bg-green-50/30'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center space-y-4">
            {uploading ? (
              <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center animate-pulse">
                <Upload className="w-6 h-6 text-white" />
              </div>
            ) : (
              <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                <Plus className="w-6 h-6 text-gray-500" />
              </div>
            )}
            <div>
              <p className="text-lg font-medium text-gray-800">
                {uploading ? 'Dateien werden hochgeladen...' : 'Dateien hier ablegen oder klicken'}
              </p>
              <p className="text-sm text-gray-500">
                Unterstützte Formate: PDF, DOCX, TXT, MD, HTML
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Files List */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center space-x-3">
              <RefreshCw className="w-5 h-5 text-green-600 animate-spin" />
              <span className="text-gray-600">Dateien werden geladen...</span>
            </div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        ) : filteredFiles.length === 0 ? (
          <div className="text-center py-12">
            <Archive className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Keine Dateien gefunden</p>
          </div>
        ) : (
          <div className="space-y-3">
            <AnimatePresence>
              {filteredFiles.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-lg p-4 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-gray-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-medium text-gray-800 truncate">
                            {file.display_name || file.filename}
                          </h3>
                          <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(file.status)}`}>
                            {getStatusIcon(file.status)}
                            <span>{file.status === 'indexed' ? 'Indexiert' : file.status}</span>
                          </span>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                          <span>{formatFileSize(file.file_size)}</span>
                          <span>{file.category === 'help_data' ? 'Hilfe-Daten' : 'Stream-Templates'}</span>
                          <span>{file.chunk_count} Chunks</span>
                          <span>{new Date(file.upload_date).toLocaleDateString('de-DE')}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => deleteFile(file.id)}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        title="Datei löschen"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  {file.error_message && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-800">{file.error_message}</p>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModernTrainingDataTab;