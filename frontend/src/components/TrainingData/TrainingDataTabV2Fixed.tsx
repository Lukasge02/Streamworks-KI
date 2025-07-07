import React, { useState, useEffect, useCallback } from 'react';
import { 
  Upload, FileText, Database, Search, AlertCircle, 
  CheckCircle, Clock, Trash2, RefreshCw, Archive,
  Eye, X, FolderOpen
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { apiService, SourceCategory } from '../../services/apiService';
import { 
  TOTAL_SUPPORTED_FORMATS,
  getDropzoneAcceptConfig,
  formatFileSize as utilFormatFileSize 
} from '../../utils/fileFormats';
import FormatInfoPanel from './FormatInfoPanel';

interface TrainingFile {
  id: string;
  filename: string;
  display_name?: string;  // Clean user-friendly name
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

const TrainingDataTabV2Fixed: React.FC = () => {
  const [files, setFiles] = useState<TrainingFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [chromaStats, setChromaStats] = useState<ChromaDBStats | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [previewFile, setPreviewFile] = useState<TrainingFile | null>(null);
  const [indexingFiles, setIndexingFiles] = useState<Set<string>>(new Set());
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [showSourceSelector, setShowSourceSelector] = useState(false);
  const [selectedSourceCategory, setSelectedSourceCategory] = useState<SourceCategory>('Testdaten');
  const [uploadDescription, setUploadDescription] = useState('');
  const [uploadProgress, setUploadProgress] = useState<{show: boolean, current: number, total: number}>({show: false, current: 0, total: 0});
  const [recentActivity, setRecentActivity] = useState<Array<{id: string, message: string, type: 'success' | 'error' | 'info', timestamp: Date}>>([]);

  // Safe console logging
  const logMessage = (type: 'success' | 'error' | 'warning', message: string) => {
    const emoji = type === 'success' ? '✅' : type === 'error' ? '❌' : '⚠️';
    console.log(`${emoji} ${message}`);
  };

  // Load data safely
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load files
      const filesResult = await apiService.getTrainingFiles();
      if (filesResult.success && Array.isArray(filesResult.data)) {
        setFiles(filesResult.data);
        logMessage('success', `${filesResult.data.length} Dateien geladen`);
      } else {
        setFiles([]);
        logMessage('warning', `Fehler beim Laden der Dateien: ${filesResult.error || 'Unbekannter Fehler'}`);
      }
      
      // Try to load ChromaDB stats
      try {
        const statsResponse = await apiService.getChromaDBStats();
        if (statsResponse && statsResponse.success && statsResponse.data) {
          setChromaStats(statsResponse.data);
          logMessage('success', 'ChromaDB Stats geladen');
        } else {
          // Set safe defaults
          setChromaStats({
            indexed_files: 0,
            total_chunks: 0,
            collection_documents: 0,
            by_category: { help_data: 0, stream_templates: 0 },
            vector_db_path: 'data/vector_db/',
            embedding_model: 'all-MiniLM-L6-v2'
          });
          logMessage('warning', 'ChromaDB Stats nicht verfügbar - verwende Defaults');
        }
      } catch (statsError) {
        console.warn('ChromaDB stats error:', statsError);
        setChromaStats({
          indexed_files: 0,
          total_chunks: 0,
          collection_documents: 0,
          by_category: { help_data: 0, stream_templates: 0 },
          vector_db_path: 'data/vector_db/',
          embedding_model: 'all-MiniLM-L6-v2'
        });
      }
    } catch (error) {
      console.error('Load data error:', error);
      setError(`Fehler beim Laden: ${error}`);
      logMessage('error', 'Fehler beim Laden der Daten');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // File upload handling - show source selector first
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setPendingFiles(acceptedFiles);
      setShowSourceSelector(true);
      logMessage('success', `${acceptedFiles.length} Dateien ausgewählt - bitte Quelle auswählen`);
    }
  }, []);

  // Actual upload after source selection
  const handleUploadWithSource = async () => {
    if (pendingFiles.length === 0) return;
    
    // Close modal immediately and show upload started message
    const filesToUpload = [...pendingFiles];
    const sourceCategory = selectedSourceCategory;
    const description = uploadDescription || undefined;
    
    // Reset modal state immediately
    setPendingFiles([]);
    setShowSourceSelector(false);
    setUploadDescription('');
    
    // Show upload started message and progress
    logMessage('success', `Upload gestartet: ${filesToUpload.length} Dateien werden verarbeitet...`);
    setUploadProgress({show: true, current: 0, total: filesToUpload.length});
    
    // Add to recent activity
    const activityId = Date.now().toString();
    setRecentActivity(prev => [{
      id: activityId,
      message: `Upload gestartet: ${filesToUpload.length} Dateien`,
      type: 'info',
      timestamp: new Date()
    }, ...prev.slice(0, 4)]);
    
    try {
      const result = await apiService.uploadTrainingFilesBatch(
        filesToUpload,
        sourceCategory,
        description
      );
      
      if (result.success && result.data) {
        const uploadResult = result.data;
        setUploadProgress({show: true, current: uploadResult.uploaded_files, total: filesToUpload.length});
        
        if (uploadResult.failed_files > 0) {
          const failedList = uploadResult.details.failed.map(f => `${f.filename}: ${f.error}`).join('\n');
          alert(`Upload abgeschlossen!\n\n✅ Erfolgreich: ${uploadResult.uploaded_files}\n❌ Fehlgeschlagen: ${uploadResult.failed_files}\n\nFehler:\n${failedList}`);
          setRecentActivity(prev => [{
            id: Date.now().toString(),
            message: `Upload abgeschlossen: ${uploadResult.uploaded_files} erfolgreich, ${uploadResult.failed_files} fehlgeschlagen`,
            type: 'error',
            timestamp: new Date()
          }, ...prev.slice(0, 4)]);
        } else {
          logMessage('success', `🎉 Alle ${uploadResult.uploaded_files} Dateien erfolgreich hochgeladen!`);
          setRecentActivity(prev => [{
            id: Date.now().toString(),
            message: `🎉 ${uploadResult.uploaded_files} Dateien erfolgreich hochgeladen`,
            type: 'success',
            timestamp: new Date()
          }, ...prev.slice(0, 4)]);
        }
        await loadData();
      } else {
        logMessage('error', `Upload fehlgeschlagen: ${result.error}`);
        setRecentActivity(prev => [{
          id: Date.now().toString(),
          message: `Upload fehlgeschlagen: ${result.error}`,
          type: 'error',
          timestamp: new Date()
        }, ...prev.slice(0, 4)]);
      }
    } catch (error) {
      console.error('Upload error:', error);
      logMessage('error', `Fehler beim Upload: ${error}`);
      setRecentActivity(prev => [{
        id: Date.now().toString(),
        message: `Upload-Fehler: ${error}`,
        type: 'error',
        timestamp: new Date()
      }, ...prev.slice(0, 4)]);
    } finally {
      // Hide progress after a delay
      setTimeout(() => {
        setUploadProgress({show: false, current: 0, total: 0});
      }, 3000);
    }
  };

  // Cancel upload
  const handleCancelUpload = () => {
    setPendingFiles([]);
    setShowSourceSelector(false);
    setUploadDescription('');
    logMessage('warning', 'Upload abgebrochen');
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: getDropzoneAcceptConfig()
  });

  // Delete file safely
  const handleDeleteFile = async (fileId: string) => {
    if (!window.confirm('Datei wirklich löschen?')) return;

    try {
      // Optimistic UI update - remove from local state immediately
      setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
      
      await apiService.deleteTrainingFile(fileId);
      logMessage('success', 'Datei gelöscht');
      
      // Refresh data to ensure consistency
      try {
        await loadData();
      } catch (refreshError) {
        console.warn('Warning: Could not refresh data after deletion:', refreshError);
        // UI already updated optimistically, so continue
      }
    } catch (error) {
      console.error('Delete error:', error);
      logMessage('error', 'Fehler beim Löschen');
      
      // Revert optimistic update on error by refreshing data
      try {
        await loadData();
      } catch (revertError) {
        console.error('Critical: Could not revert UI state after failed deletion:', revertError);
        logMessage('error', 'Kritischer Fehler: UI-Status konnte nicht wiederhergestellt werden');
      }
    }
  };

  // Bulk delete selected files
  const handleBulkDelete = async () => {
    if (selectedFiles.size === 0) return;
    
    const fileCount = selectedFiles.size;
    if (!window.confirm(`${fileCount} Dateien wirklich löschen?`)) return;

    const fileIds = Array.from(selectedFiles);
    let successCount = 0;
    let errorCount = 0;

    try {
      // Optimistic UI update - remove from local state immediately
      setFiles(prevFiles => prevFiles.filter(file => !selectedFiles.has(file.id)));
      setSelectedFiles(new Set());

      // Delete files in parallel
      const deletePromises = fileIds.map(async (fileId) => {
        try {
          await apiService.deleteTrainingFile(fileId);
          successCount++;
        } catch (error) {
          console.error(`Error deleting file ${fileId}:`, error);
          errorCount++;
        }
      });

      await Promise.all(deletePromises);

      // Show results
      if (successCount > 0) {
        logMessage('success', `${successCount} Dateien erfolgreich gelöscht`);
      }
      if (errorCount > 0) {
        logMessage('error', `${errorCount} Dateien konnten nicht gelöscht werden`);
      }

      // Refresh data to ensure consistency
      try {
        await loadData();
      } catch (refreshError) {
        console.warn('Warning: Could not refresh data after bulk deletion:', refreshError);
      }
    } catch (error) {
      console.error('Bulk delete error:', error);
      logMessage('error', 'Fehler beim Löschen der Dateien');
      
      // Revert optimistic update on error by refreshing data
      try {
        await loadData();
      } catch (revertError) {
        console.error('Critical: Could not revert UI state after failed bulk deletion:', revertError);
      }
    }
  };

  // Index file safely
  const handleIndexFile = async (fileId: string) => {
    try {
      setIndexingFiles(prev => new Set(prev).add(fileId));
      const result = await apiService.indexToChromaDB(fileId);
      if (result && result.success) {
        logMessage('success', 'Datei erfolgreich indexiert');
        await loadData();
      } else {
        logMessage('error', `Fehler beim Indexieren: ${result?.error || 'Unbekannter Fehler'}`);
      }
    } catch (error) {
      console.error('Index error:', error);
      logMessage('error', 'Fehler beim Indexieren');
    } finally {
      setIndexingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
    }
  };

  // Remove from index safely
  const handleRemoveFromIndex = async (fileId: string) => {
    try {
      const result = await apiService.removeFromChromaDB(fileId);
      if (result && result.success) {
        logMessage('success', 'Aus Index entfernt');
        await loadData();
      } else {
        logMessage('error', `Fehler beim Entfernen: ${result?.error || 'Unbekannter Fehler'}`);
      }
    } catch (error) {
      console.error('Remove from index error:', error);
      logMessage('error', 'Fehler beim Entfernen aus Index');
    }
  };

  // Use utility function for file size formatting
  const formatFileSize = utilFormatFileSize;

  // Filter files safely
  const filteredFiles = files.filter(file => {
    if (!file) return false;
    const matchesCategory = selectedCategory === 'all' || file.category === selectedCategory;
    const displayName = file.display_name || file.filename;
    const matchesSearch = displayName?.toLowerCase().includes(searchTerm.toLowerCase()) || false;
    return matchesCategory && matchesSearch;
  });

  // Get status icon
  const getStatusIcon = (file: TrainingFile) => {
    if (indexingFiles.has(file.id)) {
      return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
    }
    if (file.is_indexed) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
    if (file.index_status === 'failed') {
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
    return <Clock className="h-4 w-4 text-gray-400" />;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-2">Lade Training Data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-semibold">Fehler</h3>
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadData}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Erneut versuchen
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header with Stats */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <h2 className="text-2xl font-bold mb-4">Training Data & RAG Management</h2>
        
        {chromaStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <Database className="h-8 w-8" />
                <span className="text-2xl font-bold">{chromaStats.indexed_files || 0}</span>
              </div>
              <p className="text-sm mt-2">Indexierte Dateien</p>
            </div>
            
            <div className="bg-white/10 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <Archive className="h-8 w-8" />
                <span className="text-2xl font-bold">{chromaStats.total_chunks || 0}</span>
              </div>
              <p className="text-sm mt-2">Dokument-Chunks</p>
            </div>
            
            <div className="bg-white/10 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <FileText className="h-8 w-8" />
                <span className="text-2xl font-bold">{chromaStats.by_category?.help_data || 0}</span>
              </div>
              <p className="text-sm mt-2">Help Data Docs</p>
            </div>
            
            <div className="bg-white/10 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <FileText className="h-8 w-8" />
                <span className="text-2xl font-bold">{chromaStats.by_category?.stream_templates || 0}</span>
              </div>
              <p className="text-sm mt-2">XML Templates</p>
            </div>
          </div>
        )}
      </div>

      {/* Upload Area */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Training Data Upload</h3>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          {isDragActive ? (
            <p className="text-lg">Dateien hier ablegen...</p>
          ) : (
            <div>
              <p className="text-lg mb-2">Dateien hier ablegen oder klicken zum Auswählen</p>
              <p className="text-sm text-gray-500">
                {TOTAL_SUPPORTED_FORMATS} Formate unterstützt (max. 50MB pro Datei)
              </p>
              <p className="text-xs text-gray-400 mt-2">
                Office-Dokumente, Code, XML, JSON, CSV, E-Mails und mehr • Nach der Auswahl können Sie die Datenquelle festlegen
              </p>
              <div className="mt-2">
                <FormatInfoPanel showDetailed={false} />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center flex-1">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FolderOpen className="h-5 w-5 text-blue-600" />
              Datei-Management
            </h3>
            
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Dateien durchsuchen..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white min-w-0"
            >
              <option value="all">Alle Kategorien</option>
              <option value="help_data">Help Data</option>
              <option value="stream_templates">Stream Templates</option>
            </select>

            <button
              onClick={loadData}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Aktualisieren
            </button>
          </div>
        </div>
        
        {/* File Statistics */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{filteredFiles.length}</div>
              <div className="text-sm text-gray-500">Dateien gesamt</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {filteredFiles.filter(f => f.is_indexed).length}
              </div>
              <div className="text-sm text-gray-500">Indexiert</div>
            </div>
            <div className="text-center p-3 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {filteredFiles.filter(f => f.status === 'processing').length}
              </div>
              <div className="text-sm text-gray-500">In Bearbeitung</div>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {filteredFiles.filter(f => f.status === 'error').length}
              </div>
              <div className="text-sm text-gray-500">Fehler</div>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {uploadProgress.show && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-800">Upload-Fortschritt</span>
            <span className="text-sm text-blue-600">{uploadProgress.current} / {uploadProgress.total}</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{width: `${(uploadProgress.current / uploadProgress.total) * 100}%`}}
            ></div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {recentActivity.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Clock className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Letzte Aktivitäten</span>
          </div>
          <div className="space-y-2">
            {recentActivity.map(activity => (
              <div key={activity.id} className="flex items-start gap-2 text-sm">
                <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                  activity.type === 'success' ? 'bg-green-500' :
                  activity.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                }`}></div>
                <div className="flex-1">
                  <span className="text-gray-700">{activity.message}</span>
                  <div className="text-xs text-gray-500">
                    {activity.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bulk Actions */}
      {selectedFiles.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-blue-800">
                  {selectedFiles.size} Datei(en) ausgewählt
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSelectedFiles(new Set())}
                className="px-3 py-1.5 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-100 rounded transition-colors"
              >
                Auswahl aufheben
              </button>
              <button
                onClick={handleBulkDelete}
                className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 flex items-center gap-2 transition-all"
              >
                <Trash2 className="h-4 w-4" />
                Ausgewählte löschen
              </button>
            </div>
          </div>
        </div>
      )}

      {/* File List */}
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <table className="w-full table-fixed">
          <thead className="bg-gray-50">
            <tr>
              <th className="w-12 px-3 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selectedFiles.size === filteredFiles.length && filteredFiles.length > 0}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedFiles(new Set(filteredFiles.map(f => f.id)));
                    } else {
                      setSelectedFiles(new Set());
                    }
                  }}
                  className="rounded"
                />
              </th>
            <th className="w-1/4 px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Dateiname
            </th>
            <th className="w-20 px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Kategorie
            </th>
            <th className="w-16 px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Größe
            </th>
            <th className="w-20 px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="w-24 px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ChromaDB
            </th>
            <th className="w-16 px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Chunks
            </th>
            <th className="w-32 px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Aktionen
            </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={8} className="px-6 py-8 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
                    <span className="text-sm text-gray-600">Lade Dateien...</span>
                  </div>
                </td>
              </tr>
            ) : filteredFiles.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-6 py-12 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <FileText className="h-12 w-12 text-gray-300" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Keine Dateien gefunden</p>
                      <p className="text-sm text-gray-500">Laden Sie Dateien hoch, um zu beginnen</p>
                    </div>
                  </div>
                </td>
              </tr>
            ) : (
              filteredFiles.map((file) => (
                <tr key={file.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-3 py-4">
                    <input
                      type="checkbox"
                      checked={selectedFiles.has(file.id)}
                      onChange={(e) => {
                        const newSet = new Set(selectedFiles);
                        if (e.target.checked) {
                          newSet.add(file.id);
                        } else {
                          newSet.delete(file.id);
                        }
                        setSelectedFiles(newSet);
                      }}
                      className="rounded"
                    />
                  </td>
                  <td className="px-3 py-4">
                    <div className="flex items-center min-w-0">
                      <FileText className="h-4 w-4 text-gray-400 mr-2 flex-shrink-0" />
                      <span className="text-sm font-medium text-gray-900 truncate" title={file.display_name || file.filename}>
                        {file.display_name || file.filename}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full whitespace-nowrap ${
                      file.category === 'help_data' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {file.category === 'help_data' ? 'Help' : 'XML'}
                    </span>
                  </td>
                  <td className="px-3 py-4 text-sm text-gray-500">
                    {formatFileSize(file.file_size)}
                  </td>
                  <td className="px-3 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full whitespace-nowrap ${
                      file.status === 'ready' || file.status === 'indexed'
                        ? 'bg-green-100 text-green-800'
                        : file.status === 'error'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {file.status === 'ready' ? 'Bereit' : file.status === 'indexed' ? 'Indexed' : file.status === 'error' ? 'Fehler' : 'Verarbeitung'}
                    </span>
                  </td>
                  <td className="px-3 py-4">
                    <div className="flex items-center gap-1">
                      {getStatusIcon(file)}
                      <span className="text-xs text-gray-500">
                        {file.is_indexed ? 'Ja' : 'Nein'}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-4 text-sm text-gray-500">
                    {file.chunk_count > 0 ? file.chunk_count : '-'}
                  </td>
                  <td className="px-3 py-4">
                    <div className="flex items-center gap-1">
                      {!file.is_indexed && !indexingFiles.has(file.id) && (
                        <button
                          onClick={() => handleIndexFile(file.id)}
                          className="p-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                          title="Zu ChromaDB hinzufügen"
                        >
                          <Database className="h-3.5 w-3.5" />
                        </button>
                      )}
                      
                      {file.is_indexed && (
                        <button
                          onClick={() => handleRemoveFromIndex(file.id)}
                          className="p-1 text-yellow-600 hover:text-yellow-800 hover:bg-yellow-50 rounded transition-colors"
                          title="Aus ChromaDB entfernen"
                        >
                          <Archive className="h-3.5 w-3.5" />
                        </button>
                      )}
                      
                      <button
                        onClick={() => setPreviewFile(file)}
                        className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded transition-colors"
                        title="Vorschau"
                      >
                        <Eye className="h-3.5 w-3.5" />
                      </button>
                      
                      <button
                        onClick={() => handleDeleteFile(file.id)}
                        className="p-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
                        title="Löschen"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Info Box */}
      {chromaStats && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <Database className="h-5 w-5 text-blue-600 mt-0.5 mr-2" />
            <div>
              <h4 className="font-semibold text-blue-900">ChromaDB Vector Store</h4>
              <p className="text-sm text-blue-700 mt-1">
                Embedding Model: {chromaStats.embedding_model}<br />
                Vector DB Pfad: {chromaStats.vector_db_path}<br />
                Dokumente in Collection: {chromaStats.collection_documents}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Source Selection Modal */}
      {showSourceSelector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">Datenquelle auswählen</h3>
              <button
                onClick={handleCancelUpload}
                className="p-1 hover:bg-gray-100 rounded-lg"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <p className="text-sm text-gray-600 mb-4">
                  {pendingFiles.length} Datei(en) ausgewählt. Bitte wählen Sie die Datenquelle:
                </p>
                <div className="space-y-2">
                  {pendingFiles.map((file, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm text-gray-700 bg-gray-50 px-3 py-2 rounded">
                      <FileText className="h-4 w-4" />
                      {file.name}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Datenquelle *
                </label>
                <select
                  value={selectedSourceCategory}
                  onChange={(e) => setSelectedSourceCategory(e.target.value as SourceCategory)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="Testdaten">📚 Testdaten</option>
                  <option value="StreamWorks Hilfe">🏢 StreamWorks Hilfe</option>
                  <option value="SharePoint">☁️ SharePoint</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Beschreibung (optional)
                </label>
                <textarea
                  value={uploadDescription}
                  onChange={(e) => setUploadDescription(e.target.value)}
                  placeholder="Optionale Beschreibung für die hochgeladenen Dateien..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={2}
                />
              </div>
            </div>
            
            <div className="flex items-center justify-end gap-3 p-4 border-t bg-gray-50">
              <button
                onClick={handleCancelUpload}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Abbrechen
              </button>
              <button
                onClick={handleUploadWithSource}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Hochladen
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Document Preview Modal */}
      {previewFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">{previewFile.filename}</h3>
              <button
                onClick={() => setPreviewFile(null)}
                className="p-1 hover:bg-gray-100 rounded-lg"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="p-4 overflow-auto">
              <div className="space-y-3">
                <div><strong>Kategorie:</strong> {previewFile.category}</div>
                <div><strong>Größe:</strong> {formatFileSize(previewFile.file_size)}</div>
                <div><strong>Status:</strong> {previewFile.status}</div>
                <div><strong>Upload:</strong> {new Date(previewFile.upload_date).toLocaleString('de-DE')}</div>
                <div><strong>Indexiert:</strong> {previewFile.is_indexed ? 'Ja' : 'Nein'}</div>
                {previewFile.is_indexed && (
                  <div><strong>Chunks:</strong> {previewFile.chunk_count}</div>
                )}
                {previewFile.indexed_at && (
                  <div><strong>Indexiert am:</strong> {new Date(previewFile.indexed_at).toLocaleString('de-DE')}</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrainingDataTabV2Fixed;