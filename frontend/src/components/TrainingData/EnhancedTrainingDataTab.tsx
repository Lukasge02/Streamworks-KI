import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Upload, FileText, Database, Search, AlertCircle, 
  CheckCircle, Clock, Trash2, RefreshCw, Archive,
  FolderOpen, Plus, Filter, Calendar,
  ArrowUpDown, Square, CheckSquare
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../../services/apiService';

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

type SortField = 'filename' | 'upload_date' | 'file_size' | 'status' | 'chunk_count';
type SortOrder = 'asc' | 'desc';

const EnhancedTrainingDataTab: React.FC = () => {
  const [files, setFiles] = useState<TrainingFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);
  const [stats, setStats] = useState<ChromaDBStats | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [sortField, setSortField] = useState<SortField>('upload_date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  // const [showBulkActions, setShowBulkActions] = useState(false); // TODO: Implement if needed
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>({ start: '', end: '' });

  const categories = [
    { id: 'all', name: 'Alle Dateien', icon: FolderOpen },
    { id: 'help_data', name: 'Hilfe-Daten', icon: FileText },
    { id: 'stream_templates', name: 'Stream-Templates', icon: Database }
  ];

  const statusOptions = [
    { id: 'all', name: 'Alle Status', color: 'gray' },
    { id: 'indexed', name: 'Indexiert', color: 'green' },
    { id: 'ready', name: 'Bereit', color: 'blue' },
    { id: 'processing', name: 'Verarbeitung', color: 'yellow' },
    { id: 'error', name: 'Fehler', color: 'red' }
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
      case 'indexed': return 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-900/20';
      case 'ready': return 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/20';
      case 'processing': return 'text-yellow-600 bg-yellow-50 dark:text-yellow-400 dark:bg-yellow-900/20';
      case 'error': return 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-900/20';
      default: return 'text-gray-600 bg-gray-50 dark:text-gray-400 dark:bg-gray-800';
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

  const filteredAndSortedFiles = useMemo(() => {
    let filtered = files.filter(file => {
      const matchesCategory = selectedCategory === 'all' || file.category === selectedCategory;
      const matchesSearch = file.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (file.display_name || '').toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || file.status === statusFilter;
      
      let matchesDateRange = true;
      if (dateRange.start || dateRange.end) {
        const fileDate = new Date(file.upload_date);
        if (dateRange.start && fileDate < new Date(dateRange.start)) matchesDateRange = false;
        if (dateRange.end && fileDate > new Date(dateRange.end)) matchesDateRange = false;
      }
      
      return matchesCategory && matchesSearch && matchesStatus && matchesDateRange;
    });

    // Sortierung
    filtered.sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];
      
      if (sortField === 'upload_date') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }
      
      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [files, selectedCategory, searchTerm, statusFilter, dateRange, sortField, sortOrder]);

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

  const bulkDeleteFiles = async () => {
    if (selectedFiles.size === 0) return;
    
    try {
      setLoading(true);
      await Promise.all(Array.from(selectedFiles).map(id => apiService.deleteTrainingFile(id)));
      setSelectedFiles(new Set());
      await loadFiles();
      await loadStats();
    } catch (err) {
      console.error('Bulk delete error:', err);
      setError('Fehler beim Löschen der Dateien');
    } finally {
      setLoading(false);
    }
  };

  const toggleFileSelection = (fileId: string) => {
    const newSelection = new Set(selectedFiles);
    if (newSelection.has(fileId)) {
      newSelection.delete(fileId);
    } else {
      newSelection.add(fileId);
    }
    setSelectedFiles(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedFiles.size === filteredAndSortedFiles.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(filteredAndSortedFiles.map(f => f.id)));
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const clearFilters = () => {
    setSelectedCategory('all');
    setSearchTerm('');
    setStatusFilter('all');
    setDateRange({ start: '', end: '' });
  };

  return (
    <div className="h-full bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 rounded-2xl shadow-2xl backdrop-blur-lg border border-gray-200/50 dark:border-gray-700/50 flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg">
              <Database className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">Training Data Management</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {filteredAndSortedFiles.length} von {files.length} Dateien
                {selectedFiles.size > 0 && ` • ${selectedFiles.size} ausgewählt`}
              </p>
            </div>
          </div>
          {stats && (
            <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-300">
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
      <div className="flex-shrink-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border-b border-gray-200/50 dark:border-gray-700/50 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Category Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            <select 
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="flex-1 px-3 py-2 bg-white/80 dark:bg-gray-700/80 border border-gray-300/50 dark:border-gray-600/50 rounded-lg text-sm text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500/50"
            >
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
            <select 
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="flex-1 px-3 py-2 bg-white/80 dark:bg-gray-700/80 border border-gray-300/50 dark:border-gray-600/50 rounded-lg text-sm text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500/50"
            >
              {statusOptions.map(status => (
                <option key={status.id} value={status.id}>{status.name}</option>
              ))}
            </select>
          </div>

          {/* Date Range */}
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
              className="flex-1 px-3 py-2 bg-white/80 dark:bg-gray-700/80 border border-gray-300/50 dark:border-gray-600/50 rounded-lg text-sm text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500/50"
            />
          </div>

          {/* Search */}
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            <input
              type="text"
              placeholder="Suchen..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-3 py-2 bg-white/80 dark:bg-gray-700/80 border border-gray-300/50 dark:border-gray-600/50 rounded-lg text-sm text-gray-800 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500/50"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center space-x-2">
            <button
              onClick={toggleSelectAll}
              className="flex items-center space-x-2 px-3 py-1.5 bg-white/80 border border-gray-300/50 rounded-lg text-sm hover:bg-gray-50 transition-colors"
            >
              {selectedFiles.size === filteredAndSortedFiles.length ? (
                <CheckSquare className="w-4 h-4 text-green-600" />
              ) : (
                <Square className="w-4 h-4 text-gray-500" />
              )}
              <span className="text-gray-800 dark:text-gray-100">Alle auswählen</span>
            </button>
            
            {selectedFiles.size > 0 && (
              <button
                onClick={bulkDeleteFiles}
                className="flex items-center space-x-2 px-3 py-1.5 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                <span className="text-white">{selectedFiles.size} löschen</span>
              </button>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={clearFilters}
              className="px-3 py-1.5 bg-white/80 border border-gray-300/50 rounded-lg text-sm hover:bg-gray-50 transition-colors"
            >
              <span className="text-gray-800 dark:text-gray-100">Filter zurücksetzen</span>
            </button>
            <button
              onClick={loadFiles}
              className="flex items-center space-x-2 px-3 py-1.5 bg-green-500 text-white rounded-lg text-sm hover:bg-green-600 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-white">Aktualisieren</span>
            </button>
          </div>
        </div>
      </div>

      {/* Upload Area */}
      <div className="flex-shrink-0 p-6 border-b border-gray-200/50">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer ${
            isDragActive 
              ? 'border-green-500 bg-green-50/50' 
              : 'border-gray-300 hover:border-green-400 hover:bg-green-50/30'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex items-center justify-center space-x-4">
            {uploading ? (
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center animate-pulse">
                <Upload className="w-4 h-4 text-white" />
              </div>
            ) : (
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <Plus className="w-4 h-4 text-gray-500" />
              </div>
            )}
            <div>
              <p className="font-medium text-gray-800 dark:text-gray-100">
                {uploading ? 'Hochladen...' : 'Dateien ablegen oder klicken'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">PDF, DOCX, TXT, MD, HTML</p>
            </div>
          </div>
        </div>
      </div>

      {/* Table Header */}
      <div className="flex-shrink-0 bg-gray-50/80 border-b border-gray-200/50 px-6 py-3">
        <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-700">
          <div className="col-span-1 flex items-center">
            <Square className="w-4 h-4 text-gray-400" />
          </div>
          <div className="col-span-4 flex items-center space-x-2 cursor-pointer" onClick={() => handleSort('filename')}>
            <span>Dateiname</span>
            <ArrowUpDown className="w-3 h-3" />
          </div>
          <div className="col-span-2 flex items-center space-x-2 cursor-pointer" onClick={() => handleSort('status')}>
            <span>Status</span>
            <ArrowUpDown className="w-3 h-3" />
          </div>
          <div className="col-span-2 flex items-center space-x-2 cursor-pointer" onClick={() => handleSort('file_size')}>
            <span>Größe</span>
            <ArrowUpDown className="w-3 h-3" />
          </div>
          <div className="col-span-2 flex items-center space-x-2 cursor-pointer" onClick={() => handleSort('upload_date')}>
            <span>Datum</span>
            <ArrowUpDown className="w-3 h-3" />
          </div>
          <div className="col-span-1">
            <span>Aktionen</span>
          </div>
        </div>
      </div>

      {/* Files List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center space-x-3">
              <RefreshCw className="w-5 h-5 text-green-600 animate-spin" />
              <span className="text-gray-600">Dateien werden geladen...</span>
            </div>
          </div>
        ) : error ? (
          <div className="m-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        ) : filteredAndSortedFiles.length === 0 ? (
          <div className="text-center py-12">
            <Archive className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Keine Dateien gefunden</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200/50">
            {filteredAndSortedFiles.map((file) => (
              <div
                key={file.id}
                className={`px-6 py-4 hover:bg-gray-50/50 transition-colors ${
                  selectedFiles.has(file.id) ? 'bg-blue-50/50' : ''
                }`}
              >
                <div className="grid grid-cols-12 gap-4 items-center">
                  <div className="col-span-1">
                    <button
                      onClick={() => toggleFileSelection(file.id)}
                      className="p-1 rounded hover:bg-gray-200 transition-colors"
                    >
                      {selectedFiles.has(file.id) ? (
                        <CheckSquare className="w-4 h-4 text-green-600" />
                      ) : (
                        <Square className="w-4 h-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                  <div className="col-span-4 flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-4 h-4 text-gray-600" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-medium text-gray-800 dark:text-gray-100 truncate">
                        {file.display_name || file.filename}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                        {file.category === 'help_data' ? 'Hilfe-Daten' : 'Stream-Templates'}
                      </p>
                    </div>
                  </div>
                  <div className="col-span-2">
                    <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(file.status)}`}>
                      {getStatusIcon(file.status)}
                      <span>{file.status === 'indexed' ? 'Indexiert' : file.status}</span>
                    </span>
                  </div>
                  <div className="col-span-2 text-sm text-gray-600">
                    {formatFileSize(file.file_size)}
                  </div>
                  <div className="col-span-2 text-sm text-gray-600">
                    {new Date(file.upload_date).toLocaleDateString('de-DE')}
                  </div>
                  <div className="col-span-1">
                    <button
                      onClick={() => deleteFile(file.id)}
                      className="p-1 text-red-500 hover:bg-red-50 rounded transition-colors"
                      title="Löschen"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                {file.error_message && (
                  <div className="col-span-12 mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800">{file.error_message}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedTrainingDataTab;