import React, { useState, useEffect, useCallback } from 'react';
import { 
  Upload, FileText, Database, Search, AlertCircle, 
  CheckCircle, Clock, Trash2, RefreshCw, Archive,
  Eye, X
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
    
    try {
      logMessage('success', `Uploading ${pendingFiles.length} files as ${selectedSourceCategory}...`);
      
      const result = await apiService.uploadTrainingFilesBatch(
        pendingFiles,
        selectedSourceCategory,
        uploadDescription || undefined
      );
      
      if (result.success && result.data) {
        const uploadResult = result.data;
        if (uploadResult.failed_files > 0) {
          const failedList = uploadResult.details.failed.map(f => `${f.filename}: ${f.error}`).join('\n');
          alert(`Upload abgeschlossen!\n\n✅ Erfolgreich: ${uploadResult.uploaded_files}\n❌ Fehlgeschlagen: ${uploadResult.failed_files}\n\nFehler:\n${failedList}`);
        } else {
          logMessage('success', `🎉 Alle ${uploadResult.uploaded_files} Dateien erfolgreich hochgeladen!`);
        }
        await loadData();
      } else {
        logMessage('error', `Upload fehlgeschlagen: ${result.error}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      logMessage('error', `Fehler beim Upload: ${error}`);
    } finally {
      // Reset
      setPendingFiles([]);
      setShowSourceSelector(false);
      setUploadDescription('');
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
      await apiService.deleteTrainingFile(fileId);
      logMessage('success', 'Datei gelöscht');
      await loadData();
    } catch (error) {
      console.error('Delete error:', error);
      logMessage('error', 'Fehler beim Löschen');
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
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Dateien suchen..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">Alle Kategorien</option>
          <option value="help_data">Help Data</option>
          <option value="stream_templates">Stream Templates</option>
        </select>

        <button
          onClick={loadData}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
        >
          <RefreshCw className="h-5 w-5" />
          Aktualisieren
        </button>
      </div>

      {/* File List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left">
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Dateiname
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Kategorie
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Größe
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ChromaDB
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Chunks
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Aktionen
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={8} className="px-6 py-4 text-center">
                  <RefreshCw className="h-6 w-6 animate-spin mx-auto text-gray-400" />
                </td>
              </tr>
            ) : filteredFiles.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                  Keine Dateien gefunden
                </td>
              </tr>
            ) : (
              filteredFiles.map((file) => (
                <tr key={file.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
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
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-sm font-medium text-gray-900">{file.display_name || file.filename}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      file.category === 'help_data' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {file.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatFileSize(file.file_size)}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      file.status === 'ready' || file.status === 'indexed'
                        ? 'bg-green-100 text-green-800'
                        : file.status === 'error'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {file.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(file)}
                      <span className="text-sm text-gray-500">
                        {file.is_indexed ? 'Indexiert' : 'Nicht indexiert'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {file.chunk_count > 0 ? file.chunk_count : '-'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {!file.is_indexed && !indexingFiles.has(file.id) && (
                        <button
                          onClick={() => handleIndexFile(file.id)}
                          className="text-blue-600 hover:text-blue-800"
                          title="Zu ChromaDB hinzufügen"
                        >
                          <Database className="h-5 w-5" />
                        </button>
                      )}
                      
                      {file.is_indexed && (
                        <button
                          onClick={() => handleRemoveFromIndex(file.id)}
                          className="text-yellow-600 hover:text-yellow-800"
                          title="Aus ChromaDB entfernen"
                        >
                          <Archive className="h-5 w-5" />
                        </button>
                      )}
                      
                      <button
                        onClick={() => setPreviewFile(file)}
                        className="text-gray-600 hover:text-gray-800"
                        title="Vorschau"
                      >
                        <Eye className="h-5 w-5" />
                      </button>
                      
                      <button
                        onClick={() => handleDeleteFile(file.id)}
                        className="text-red-600 hover:text-red-800"
                        title="Löschen"
                      >
                        <Trash2 className="h-5 w-5" />
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