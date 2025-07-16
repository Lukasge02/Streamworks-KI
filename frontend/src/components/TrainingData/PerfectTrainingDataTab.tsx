import React, { useState, useEffect, useCallback } from 'react';
import { 
  Upload, FileText, Database, Folder, Plus, Trash2, 
  CheckCircle, Clock, AlertCircle, FolderOpen, 
  Square, CheckSquare, Calendar, Download
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../../services/apiService';

interface Category {
  id: string;
  slug: string;
  name: string;
  description?: string;
  folder_count: number;
}

interface Folder {
  id: string;
  slug: string;
  name: string;
  description?: string;
}

interface FileItem {
  id: string;
  filename: string;
  category_slug: string;
  category_name: string;
  folder_slug?: string;
  folder_name?: string;
  file_size: number;
  upload_date: string;
  status: string;
  chunk_count?: number;
  indexed_at?: string;
}

const PerfectTrainingDataTab: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Selection states
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  
  // Management states
  const [showFolderManager, setShowFolderManager] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderDescription, setNewFolderDescription] = useState('');
  
  // File management states
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  // Load categories
  const loadCategories = useCallback(async () => {
    try {
      const result = await apiService.getCategories();
      if (result.success) {
        setCategories(result.data || []);
        // Auto-select first category if none selected
        if (!selectedCategory && result.data && result.data.length > 0) {
          setSelectedCategory(result.data[0].slug);
        }
      } else {
        setError(result.error || 'Unbekannter Fehler');
      }
    } catch (err) {
      setError('Fehler beim Laden der Kategorien');
    }
  }, [selectedCategory]);

  // Load folders for selected category
  const loadFolders = useCallback(async () => {
    if (!selectedCategory) return;
    
    try {
      const result = await apiService.getFolders(selectedCategory);
      if (result.success) {
        setFolders(result.data || []);
        // Reset folder selection when category changes
        setSelectedFolder(null);
      } else {
        setError(result.error || 'Unbekannter Fehler');
      }
    } catch (err) {
      setError('Fehler beim Laden der Ordner');
    }
  }, [selectedCategory]);

  // Load files
  const loadFiles = useCallback(async () => {
    try {
      const result = await apiService.getFiles();
      if (result.success) {
        setFiles(result.data || []);
      } else {
        setError(result.error || 'Unbekannter Fehler');
      }
    } catch (err) {
      setError('Fehler beim Laden der Dateien');
    }
  }, []);

  // Create folder
  const createFolder = useCallback(async () => {
    if (!newFolderName.trim()) {
      setError('Bitte geben Sie einen Ordner-Namen ein');
      return;
    }

    if (!selectedCategory) {
      setError('Bitte wählen Sie zuerst eine Kategorie aus');
      return;
    }

    try {
      const result = await apiService.createFolder(selectedCategory, newFolderName, newFolderDescription);
      if (result.success) {
        setNewFolderName('');
        setNewFolderDescription('');
        setShowFolderManager(false);
        await loadFolders();
        await loadCategories(); // Refresh folder counts
        setError(null);
      } else {
        setError(result.error || 'Unbekannter Fehler');
      }
    } catch (err) {
      setError('Fehler beim Erstellen des Ordners');
    }
  }, [newFolderName, newFolderDescription, selectedCategory, loadFolders, loadCategories]);

  // Delete folder
  const deleteFolder = useCallback(async (folderId: string) => {
    if (!confirm('Sind Sie sicher, dass Sie diesen Ordner löschen möchten?')) {
      return;
    }

    try {
      const result = await apiService.deleteFolder(folderId);
      if (result.success) {
        await loadFolders();
        await loadCategories(); // Refresh folder counts
        await loadFiles();
        // Reset selection if deleted folder was selected
        if (selectedFolder === folderId) {
          setSelectedFolder(null);
        }
        setError(null);
      } else {
        setError(result.error || 'Unbekannter Fehler');
      }
    } catch (err) {
      setError('Fehler beim Löschen des Ordners');
    }
  }, [loadFolders, loadCategories, loadFiles, selectedFolder]);

  // File management functions
  const toggleFileSelection = useCallback((fileId: string) => {
    const newSelection = new Set(selectedFiles);
    if (newSelection.has(fileId)) {
      newSelection.delete(fileId);
    } else {
      newSelection.add(fileId);
    }
    setSelectedFiles(newSelection);
  }, [selectedFiles]);

  const filteredFiles = files.filter(file => {
    // Show all files if no category is selected
    if (!selectedCategory) return true;
    
    // Filter by category
    if (file.category_slug !== selectedCategory) return false;
    
    // If a folder is selected, only show files in that folder
    if (selectedFolder) {
      return file.folder_slug === selectedFolder;
    }
    
    // If no folder is selected, show all files in the category
    return true;
  });

  const toggleSelectAll = useCallback(() => {
    if (selectedFiles.size === filteredFiles.length) {
      setSelectedFiles(new Set());
    } else {
      setSelectedFiles(new Set(filteredFiles.map(f => f.id)));
    }
  }, [selectedFiles.size, filteredFiles]);

  const deleteSelectedFiles = useCallback(async () => {
    if (selectedFiles.size === 0) return;
    
    setLoading(true);
    try {
      const promises = Array.from(selectedFiles).map(fileId => 
        apiService.deleteFile(fileId)
      );
      
      const results = await Promise.allSettled(promises);
      const failed = results.filter(r => r.status === 'rejected').length;
      
      if (failed > 0) {
        setError(`${failed} Dateien konnten nicht gelöscht werden`);
      }
      
      setSelectedFiles(new Set());
      setShowDeleteConfirm(false);
      await loadFiles();
      await loadCategories();
    } catch (err) {
      setError('Fehler beim Löschen der Dateien');
    } finally {
      setLoading(false);
    }
  }, [selectedFiles, loadFiles, loadCategories]);

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Initialize data
  useEffect(() => {
    const initializeData = async () => {
      setLoading(true);
      await loadCategories();
      await loadFiles();
      setLoading(false);
    };
    
    initializeData();
  }, [loadCategories, loadFiles]);

  // Load folders when category changes
  useEffect(() => {
    if (selectedCategory) {
      loadFolders();
    }
  }, [selectedCategory, loadFolders]);

  // Handle file upload
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (!selectedCategory) {
      setError('Bitte wählen Sie zuerst eine Kategorie aus');
      return;
    }

    setUploading(true);
    setError(null);
    
    try {
      const uploadResults = [];
      
      for (const file of acceptedFiles) {
        try {
          const result = await apiService.uploadFile(
            file, 
            selectedCategory, 
            selectedFolder || undefined
          );
          
          if (result.success) {
            uploadResults.push(`✅ ${file.name}`);
          } else {
            uploadResults.push(`❌ ${file.name}: ${result.error}`);
          }
        } catch (fileError) {
          uploadResults.push(`❌ ${file.name}: ${fileError}`);
        }
      }
      
      // Show results
      if (uploadResults.length > 0) {
        const successCount = uploadResults.filter(r => r.startsWith('✅')).length;
        const errorCount = uploadResults.filter(r => r.startsWith('❌')).length;
        
        if (errorCount > 0) {
          setError(`Upload abgeschlossen: ${successCount} erfolgreich, ${errorCount} fehlgeschlagen`);
        }
      }
      
      // Reload files after upload
      await loadFiles();
      await loadCategories(); // Refresh file counts
      
    } catch (err) {
      setError(`Upload fehlgeschlagen: ${err}`);
    } finally {
      setUploading(false);
    }
  }, [selectedCategory, selectedFolder, loadFiles, loadCategories]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/*': ['.txt', '.md', '.rtf', '.log'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc', '.docx'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/json': ['.json'],
      'text/xml': ['.xml'],
      'text/html': ['.html'],
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls', '.xlsx']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'uploaded': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'ready': return <Database className="w-4 h-4 text-blue-500" />;
      case 'indexed': return <Database className="w-4 h-4 text-blue-500" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };
  
  const getStatusText = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return 'Ausstehend';
      case 'uploaded': return 'Hochgeladen';
      case 'completed': return 'Hochgeladen';
      case 'ready': return 'Indexiert';
      case 'indexed': return 'Indexiert';
      case 'error': return 'Fehler';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">System wird geladen...</p>
        </div>
      </div>
    );
  }

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
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">
                Perfekte Trainings-Daten
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Dynamische Kategorien • Enterprise-Ready • Saubere Struktur
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-600 dark:text-gray-300">
              {categories.length} Kategorien • {files.length} Dateien
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {files.filter(f => f.status === 'ready').length} indexiert • {files.reduce((sum, f) => sum + (f.chunk_count || 0), 0)} Chunks
            </div>
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex-shrink-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border-b border-gray-200/50 dark:border-gray-700/50">
        <div className="flex items-center justify-between">
          <div className="flex overflow-x-auto">
            {categories.map(category => (
              <div key={category.slug} className="flex items-center">
                <button
                  onClick={() => setSelectedCategory(category.slug)}
                  className={`flex-shrink-0 px-6 py-4 text-sm font-medium border-b-2 transition-all duration-200 ${
                    selectedCategory === category.slug
                      ? 'border-green-500 text-green-600 dark:text-green-400 bg-green-50/50 dark:bg-green-900/20'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <span>{category.name}</span>
                    {category.folder_count > 0 && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                        {category.folder_count}
                      </span>
                    )}
                  </div>
                </button>
              </div>
            ))}
          </div>
          
        </div>

        {/* Folder Management (only show if category selected) */}
        {selectedCategory && (
          <div className="px-6 py-3 bg-gray-50/50 dark:bg-gray-800/50 border-t border-gray-200/50 dark:border-gray-700/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Folder className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Ordner:</span>
                
                {folders.length > 0 ? (
                  <div className="flex items-center space-x-2">
                    <select
                      value={selectedFolder || ''}
                      onChange={(e) => setSelectedFolder(e.target.value || null)}
                      className="px-3 py-1 bg-white/80 dark:bg-gray-700/80 border border-gray-300/50 dark:border-gray-600/50 rounded text-sm text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500/50"
                    >
                      <option value="">-- Direkt in Kategorie --</option>
                      {folders.map(folder => (
                        <option key={folder.slug} value={folder.slug}>
                          {folder.name}
                        </option>
                      ))}
                    </select>
                    
                    {selectedFolder && (
                      <button
                        onClick={() => {
                          const folder = folders.find(f => f.slug === selectedFolder);
                          if (folder) deleteFolder(folder.id);
                        }}
                        className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                        title="Ordner löschen"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ) : (
                  <span className="text-sm text-gray-500 dark:text-gray-400">Keine Ordner vorhanden</span>
                )}
              </div>
              
              <button
                onClick={() => setShowFolderManager(true)}
                className="flex items-center space-x-1 px-2 py-1 text-xs font-medium text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300 hover:bg-green-50 dark:hover:bg-green-900/20 rounded transition-colors"
              >
                <Plus className="w-3 h-3" />
                <span>Ordner</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Upload Area */}
      <div className="flex-shrink-0 p-4">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all duration-200 ${
            isDragActive
              ? 'border-green-500 bg-green-50/50 dark:bg-green-900/20'
              : selectedCategory
              ? 'border-gray-300 dark:border-gray-600 hover:border-green-500 hover:bg-green-50/30 dark:hover:bg-green-900/10'
              : 'border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50 opacity-50 cursor-not-allowed'
          }`}
        >
          <input {...getInputProps()} disabled={!selectedCategory} />
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          {uploading ? (
            <div>
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto mb-2"></div>
              <p className="text-sm text-gray-600 dark:text-gray-300">Upload läuft...</p>
            </div>
          ) : selectedCategory ? (
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                Dateien hierher ziehen oder klicken zum Auswählen
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Upload nach: <span className="font-medium">{categories.find(c => c.slug === selectedCategory)?.name}</span>
                {selectedFolder && (
                  <span> &gt; <span className="font-medium">{folders.find(f => f.slug === selectedFolder)?.name}</span></span>
                )}
              </p>
            </div>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Bitte wählen Sie zuerst eine Kategorie aus
            </p>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="flex-shrink-0 mx-4 mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Files List */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {filteredFiles.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center py-8">
              <FolderOpen className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                {selectedCategory ? 'Keine Dateien in dieser Auswahl' : 'Wählen Sie eine Kategorie aus'}
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* Files Header with Actions */}
            <div className="flex-shrink-0 px-4 py-3 bg-white/30 dark:bg-gray-800/30 border-b border-gray-200/50 dark:border-gray-700/50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={toggleSelectAll}
                      className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                    >
                      {selectedFiles.size === filteredFiles.length ? (
                        <CheckSquare className="w-4 h-4" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                    </button>
                    <span className="text-sm text-gray-600 dark:text-gray-300">
                      {selectedFiles.size > 0 ? `${selectedFiles.size} ausgewählt` : `${filteredFiles.length} Dateien`}
                    </span>
                  </div>
                  
                  {selectedFiles.size > 0 && (
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="flex items-center space-x-1 px-3 py-1 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors text-sm"
                    >
                      <Trash2 className="w-4 h-4" />
                      <span>Löschen ({selectedFiles.size})</span>
                    </button>
                  )}
                </div>
                
                <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                  <span>{formatFileSize(filteredFiles.reduce((sum, file) => sum + file.file_size, 0))} gesamt</span>
                  <span>•</span>
                  <span>{filteredFiles.filter(f => f.status === 'ready').length} indexiert</span>
                  <span>•</span>
                  <span>{filteredFiles.reduce((sum, f) => sum + (f.chunk_count || 0), 0)} Chunks</span>
                </div>
              </div>
            </div>

            {/* Files Table */}
            <div className="flex-1 overflow-y-auto">
              <table className="w-full">
                <thead className="bg-gray-50/50 dark:bg-gray-800/50 sticky top-0">
                  <tr className="border-b border-gray-200/50 dark:border-gray-700/50">
                    <th className="text-left p-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Datei
                    </th>
                    <th className="text-left p-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Ordner
                    </th>
                    <th className="text-left p-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Größe
                    </th>
                    <th className="text-left p-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="text-center p-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Chunks
                    </th>
                    <th className="text-left p-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Hochgeladen
                    </th>
                    <th className="text-left p-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Indexiert
                    </th>
                    <th className="text-right p-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Aktionen
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200/50 dark:divide-gray-700/50">
                  {filteredFiles.map(file => (
                    <tr
                      key={file.id}
                      className={`hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-colors ${
                        selectedFiles.has(file.id) ? 'bg-green-50/50 dark:bg-green-900/20' : ''
                      }`}
                    >
                      <td className="p-3">
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => toggleFileSelection(file.id)}
                            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                          >
                            {selectedFiles.has(file.id) ? (
                              <CheckSquare className="w-4 h-4" />
                            ) : (
                              <Square className="w-4 h-4" />
                            )}
                          </button>
                          <FileText className="w-4 h-4 text-gray-500" />
                          <div>
                            <p className="font-medium text-gray-800 dark:text-gray-100 text-sm">
                              {file.filename}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {file.category_name}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="p-3 text-sm text-gray-600 dark:text-gray-300">
                        {file.folder_name || (
                          <span className="text-gray-400 dark:text-gray-500 italic">Direkt in Kategorie</span>
                        )}
                      </td>
                      <td className="p-3 text-sm text-gray-600 dark:text-gray-300">
                        {formatFileSize(file.file_size)}
                      </td>
                      <td className="p-3">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(file.status)}
                          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {getStatusText(file.status)}
                          </span>
                        </div>
                      </td>
                      <td className="p-3 text-center">
                        <div className="flex items-center justify-center">
                          {file.chunk_count && file.chunk_count > 0 ? (
                            <div className="flex items-center space-x-1">
                              <Database className="w-4 h-4 text-blue-500" />
                              <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                                {file.chunk_count}
                              </span>
                            </div>
                          ) : (
                            <div className="flex items-center space-x-1">
                              <Database className="w-4 h-4 text-gray-400" />
                              <span className="text-sm text-gray-400">
                                0
                              </span>
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="p-3 text-sm text-gray-600 dark:text-gray-300">
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3 text-green-500" />
                          <span>{formatDateTime(file.upload_date)}</span>
                        </div>
                      </td>
                      <td className="p-3 text-sm text-gray-600 dark:text-gray-300">
                        <div className="flex items-center space-x-1">
                          {file.indexed_at ? (
                            <>
                              <Calendar className="w-3 h-3 text-blue-500" />
                              <span className="text-blue-600 dark:text-blue-400 font-medium">
                                {formatDateTime(file.indexed_at)}
                              </span>
                            </>
                          ) : (
                            <>
                              <Clock className="w-3 h-3 text-gray-400" />
                              <span className="text-gray-400 italic">
                                Noch nicht indexiert
                              </span>
                            </>
                          )}
                        </div>
                      </td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => {
                            setSelectedFiles(new Set([file.id]));
                            setShowDeleteConfirm(true);
                          }}
                          className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                          title="Datei löschen"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Folder Manager Modal */}
      {showFolderManager && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
              Neuen Ordner erstellen
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Ordner-Name
                </label>
                <input
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="z.B. SharePoint Dokumente"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Beschreibung (optional)
                </label>
                <input
                  type="text"
                  value={newFolderDescription}
                  onChange={(e) => setNewFolderDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Beschreibung des Ordners"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowFolderManager(false);
                    setNewFolderName('');
                    setNewFolderDescription('');
                  }}
                  className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                >
                  Abbrechen
                </button>
                <button
                  onClick={createFolder}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Erstellen
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
              Dateien löschen
            </h3>
            <div className="mb-6">
              <p className="text-gray-600 dark:text-gray-300 mb-2">
                Sind Sie sicher, dass Sie {selectedFiles.size} Datei(en) löschen möchten?
              </p>
              <div className="max-h-32 overflow-y-auto bg-gray-50 dark:bg-gray-700 rounded p-2">
                {Array.from(selectedFiles).map(fileId => {
                  const file = filteredFiles.find(f => f.id === fileId);
                  return file ? (
                    <div key={fileId} className="text-sm text-gray-600 dark:text-gray-300 py-1">
                      • {file.filename}
                    </div>
                  ) : null;
                })}
              </div>
              <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                Diese Aktion kann nicht rückgängig gemacht werden.
              </p>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setSelectedFiles(new Set());
                }}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
              >
                Abbrechen
              </button>
              <button
                onClick={deleteSelectedFiles}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Löschen
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PerfectTrainingDataTab;