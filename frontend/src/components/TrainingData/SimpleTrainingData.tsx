import React, { useState, useEffect, useRef } from 'react';
import { Folder, Plus, Upload, Trash2, FileText, RefreshCw, Database, Layers, Settings, X, Search, CheckSquare, Square } from 'lucide-react';

interface Category {
  id: string;
  slug: string;
  name: string;
  folder_count: number;
}

interface Folder {
  id: string;
  name: string;
  slug: string;
}

interface FileItem {
  id: string;
  filename: string;
  file_size: number;
  upload_date: string;
  status: string;
  folder_id: string | null;
}

export const SimpleTrainingData: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{[key: string]: number}>({});
  const [refreshing, setRefreshing] = useState(false);
  
  // Create folder states
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [creating, setCreating] = useState(false);
  
  // File upload ref
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  
  // Enterprise features
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  // Load categories
  const loadCategories = async () => {
    try {
      const response = await fetch('/api/v1/files/categories');
      if (!response.ok) throw new Error('Failed to load categories');
      const data = await response.json();
      setCategories(data || []);
      if (data && data.length > 0 && !selectedCategory) {
        setSelectedCategory(data[0].slug);
      }
    } catch (err) {
      setError('Kategorien laden fehlgeschlagen');
      console.error(err);
    }
  };

  // Load folders with force refresh
  const loadFolders = async (forceRefresh = false) => {
    if (!selectedCategory) return;
    
    try {
      const headers: HeadersInit = {};
      if (forceRefresh) {
        headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
        headers['Pragma'] = 'no-cache';
        headers['Expires'] = '0';
      }
      
      // Add timestamp for additional cache busting
      const url = forceRefresh 
        ? `/api/v1/folders/categories/${selectedCategory}/folders?t=${Date.now()}`
        : `/api/v1/folders/categories/${selectedCategory}/folders`;
      
      console.log(`🔄 Loading folders from: ${url}${forceRefresh ? ' (force refresh)' : ''}`);
      
      const response = await fetch(url, { headers });
      
      if (!response.ok) {
        if (response.status === 404) {
          console.log(`📁 Keine Ordner gefunden für ${selectedCategory}`);
          setFolders([]);
          return;
        }
        throw new Error('Failed to load folders');
      }
      
      const data = await response.json();
      const folders = data.folders || [];
      
      console.log(`📁 ${folders.length} Ordner geladen:`, folders.map(f => f.name));
      setFolders(folders);
      
      // If selected folder no longer exists, reset selection
      const folderIds = folders.map((f: Folder) => f.id);
      if (selectedFolder && !folderIds.includes(selectedFolder)) {
        console.log(`🗑️ Ausgewählter Ordner ${selectedFolder} existiert nicht mehr - Auswahl zurückgesetzt`);
        setSelectedFolder('');
      }
    } catch (err) {
      console.error('❌ Folders load error:', err);
      setFolders([]);
    }
  };

  // Load files filtered by folder
  const loadFiles = async () => {
    if (!selectedCategory || !selectedFolder) {
      setFiles([]);
      return;
    }
    
    try {
      const response = await fetch(`/api/v1/files/files?category_slug=${selectedCategory}`);
      if (!response.ok) throw new Error('Failed to load files');
      const data = await response.json();
      
      console.log(`📁 Alle Files in ${selectedCategory}:`, data.length);
      console.log(`🔍 Filter für Ordner: ${selectedFolder}`);
      
      // Filter files by selected folder
      const filteredFiles = (data || []).filter((file: FileItem) => {
        console.log(`📄 File: ${file.filename} - folder_id: ${file.folder_id}`);
        return file.folder_id === selectedFolder;
      });
      
      console.log(`✅ Gefilterte Files:`, filteredFiles.length);
      setFiles(filteredFiles);
    } catch (err) {
      console.error('Files load error:', err);
      setFiles([]);
    }
  };

  // Create folder
  const createFolder = async () => {
    if (!newFolderName.trim() || !selectedCategory) return;
    
    setCreating(true);
    try {
      const formData = new FormData();
      formData.append('name', newFolderName.trim());
      
      const response = await fetch(`/api/v1/folders/categories/${selectedCategory}/folders`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Fehler beim Erstellen');
      }
      
      setNewFolderName('');
      setShowCreateFolder(false);
      await loadFolders();
      await loadCategories();
      setError('');
      
    } catch (err: any) {
      setError(`Ordner erstellen fehlgeschlagen: ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  // Delete folder with proper sync
  const deleteFolder = async (folderId: string, folderName: string) => {
    if (!confirm(`Ordner "${folderName}" wirklich löschen?`)) return;
    
    try {
      const deleteUrl = `/api/v1/folders/folders/${folderId}`;
      console.log(`🗑️ Sende DELETE Request: ${deleteUrl}`);
      
      // Backend deletion first
      const response = await fetch(deleteUrl, {
        method: 'DELETE'
      });
      
      console.log(`📡 DELETE Response Status: ${response.status}`);
      console.log(`📡 DELETE Response Headers:`, Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error(`❌ DELETE fehlgeschlagen:`, errorData);
        throw new Error(errorData.detail || 'Fehler beim Löschen');
      }
      
      const responseData = await response.json();
      console.log(`✅ Backend: Ordner ${folderId} erfolgreich gelöscht:`, responseData);
      
      // IMMEDIATE UI UPDATE (genau wie bei Files!)
      setFolders(prev => prev.filter(f => f.id !== folderId));
      
      // Clear selection if deleting selected folder
      if (selectedFolder === folderId) {
        setSelectedFolder('');
        setFiles([]);
        setSelectedFiles(new Set());
      }
      
      // Then reload to ensure backend sync (genau wie bei Files!)
      await Promise.all([
        loadFolders(true), // Force reload with cache bypass
        loadCategories(),  // Update category counts
      ]);
      
      console.log(`✅ Frontend: Ordner-Liste aktualisiert`);
      setError('');
      
    } catch (err: any) {
      console.error('❌ Ordner löschen fehlgeschlagen:', err);
      setError(`Ordner löschen fehlgeschlagen: ${err.message}`);
      
      // Force reload on error to ensure consistency
      await loadFolders(true);
    }
  };

  // Delete file
  const deleteFile = async (fileId: string, filename: string) => {
    if (!confirm(`Datei "${filename}" wirklich löschen?`)) return;
    
    try {
      const response = await fetch(`/api/v1/files/files/${fileId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Fehler beim Löschen');
      }
      
      // Immediate UI update
      setFiles(prev => prev.filter(f => f.id !== fileId));
      setSelectedFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
      
      // Reload files to ensure sync
      await loadFiles();
      
      setError('');
      
    } catch (err: any) {
      setError(`Datei löschen fehlgeschlagen: ${err.message}`);
    }
  };

  // Batch delete files
  const batchDeleteFiles = async () => {
    if (selectedFiles.size === 0) return;
    
    const fileNames = files.filter(f => selectedFiles.has(f.id)).map(f => f.filename);
    if (!confirm(`${selectedFiles.size} Dateien wirklich löschen?\n\n${fileNames.join('\n')}`)) return;
    
    setError('');
    const errors: string[] = [];
    
    try {
      for (const fileId of selectedFiles) {
        try {
          const response = await fetch(`/api/v1/files/files/${fileId}`, {
            method: 'DELETE'
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            errors.push(`${fileId}: ${errorData.detail || 'Unbekannter Fehler'}`);
          }
        } catch (err: any) {
          errors.push(`${fileId}: ${err.message}`);
        }
      }
      
      if (errors.length > 0) {
        setError(`Einige Dateien konnten nicht gelöscht werden:\n${errors.join('\n')}`);
      }
      
      // Clear selection and reload
      setSelectedFiles(new Set());
      await loadFiles();
      
    } catch (err: any) {
      setError(`Batch-Löschung fehlgeschlagen: ${err.message}`);
    }
  };

  // Toggle file selection
  const toggleFileSelection = (fileId: string) => {
    setSelectedFiles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(fileId)) {
        newSet.delete(fileId);
      } else {
        newSet.add(fileId);
      }
      return newSet;
    });
  };

  // Select all visible files
  const selectAllFiles = () => {
    const filteredFiles = getFilteredFiles();
    const allSelected = filteredFiles.every(f => selectedFiles.has(f.id));
    
    if (allSelected) {
      // Deselect all
      setSelectedFiles(new Set());
    } else {
      // Select all visible
      setSelectedFiles(new Set(filteredFiles.map(f => f.id)));
    }
  };

  // Filter files by search term
  const getFilteredFiles = () => {
    if (!searchTerm.trim()) return files;
    
    return files.filter(file =>
      file.filename.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  // Handle file upload
  const handleFileUpload = async (uploadFiles: FileList) => {
    if (!uploadFiles || uploadFiles.length === 0) return;
    if (!selectedCategory || !selectedFolder) {
      setError('Bitte wählen Sie erst eine Kategorie und einen Ordner');
      return;
    }

    setUploading(true);
    setError('');
    
    try {
      for (let i = 0; i < uploadFiles.length; i++) {
        const file = uploadFiles[i];
        const fileId = `${file.name}-${Date.now()}`;
        setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category_slug', selectedCategory);
        formData.append('folder_id', selectedFolder);
        
        const xhr = new XMLHttpRequest();
        
        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            setUploadProgress(prev => ({ ...prev, [fileId]: percentComplete }));
          }
        });
        
        // Handle completion
        await new Promise((resolve, reject) => {
          xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              setUploadProgress(prev => {
                const newProgress = { ...prev };
                delete newProgress[fileId];
                return newProgress;
              });
              resolve(xhr.response);
            } else {
              reject(new Error(`Upload failed: ${xhr.statusText}`));
            }
          };
          
          xhr.onerror = () => reject(new Error('Upload failed'));
          
          xhr.open('POST', '/api/v1/training/upload');
          xhr.send(formData);
        });
      }
      
      // Reload files after upload
      await loadFiles();
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
    } catch (err: any) {
      setError(`Upload fehlgeschlagen: ${err.message}`);
    } finally {
      setUploading(false);
      setUploadProgress({});
    }
  };

  // File input handler
  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      handleFileUpload(files);
    }
  };

  // Initialize
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await loadCategories();
      setLoading(false);
    };
    init();
  }, []);

  // Load data when category changes
  useEffect(() => {
    if (selectedCategory) {
      loadFolders();
      setSelectedFolder(''); // Reset folder selection when category changes
    }
  }, [selectedCategory]);

  // Load files when folder selection changes
  useEffect(() => {
    setSelectedFiles(new Set()); // Clear selection when changing folders
    if (selectedFolder) {
      loadFiles();
    }
  }, [selectedFolder]);

  // Clear selection when search term changes
  useEffect(() => {
    setSelectedFiles(new Set());
  }, [searchTerm]);

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">System wird geladen...</p>
        </div>
      </div>
    );
  }

  // Get category icon
  const getCategoryIcon = (slug: string) => {
    switch (slug) {
      case 'qa_docs':
        return <Database className="w-4 h-4" />;
      case 'stream_xml_xsd':
        return <Layers className="w-4 h-4" />;
      case 'streamworks_api':
        return <Settings className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Modern Top Navigation */}
      <div className="bg-white/80 backdrop-blur-lg border-b border-white/20 shadow-lg">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex space-x-1">
            {categories.map(cat => (
              <button
                key={cat.slug}
                onClick={() => {
                  setSelectedCategory(cat.slug);
                  setSelectedFolder('');
                }}
                className={`group relative px-6 py-3 font-medium text-sm rounded-xl transition-all duration-300 ${
                  selectedCategory === cat.slug
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25'
                    : 'bg-white/60 text-gray-700 hover:bg-white/80 hover:shadow-md border border-gray-200/50'
                }`}
              >
                <div className="flex items-center space-x-2">
                  {getCategoryIcon(cat.slug)}
                  <span>{cat.name}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    selectedCategory === cat.slug 
                      ? 'bg-white/20 text-white' 
                      : 'bg-blue-100 text-blue-700'
                  }`}>
                    {cat.folder_count}
                  </span>
                </div>
                {selectedCategory === cat.slug && (
                  <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-6 h-1 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-full"></div>
                )}
              </button>
            ))}
          </div>
          <button
            onClick={() => window.location.reload()}
            className="p-3 text-gray-600 hover:text-gray-800 hover:bg-white/60 rounded-xl transition-all duration-300"
            title="Seite aktualisieren"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-6 mt-4 p-4 bg-red-50/80 backdrop-blur-sm border border-red-200/50 rounded-xl text-red-700 shadow-sm">
          <div className="flex items-center justify-between">
            <span>{error}</span>
            <button 
              onClick={() => setError('')} 
              className="text-red-500 hover:text-red-700 p-1 rounded-lg hover:bg-red-100/50"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Main Content with Sidebar Layout */}
      <div className="flex-1 flex overflow-hidden p-6 space-x-6">
        {/* Left Sidebar - Folders */}
        <div className="w-80 bg-white/60 backdrop-blur-sm border border-white/20 rounded-2xl shadow-xl flex flex-col overflow-hidden">
          <div className="p-6 border-b border-gray-200/50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-xl text-gray-900 flex items-center">
                <Folder className="w-6 h-6 mr-3 text-blue-600" />
                Ordner
              </h3>
              <button
                onClick={() => setShowCreateFolder(true)}
                className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/25 transition-all duration-300"
                title="Neuer Ordner"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
            <div className="text-sm text-gray-600">
              {folders.length} {folders.length === 1 ? 'Ordner' : 'Ordner'} verfügbar
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4">
            {folders.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Folder className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="font-medium">Keine Ordner</p>
                <p className="text-sm mt-1">Erstellen Sie einen neuen Ordner</p>
              </div>
            ) : (
              <div className="space-y-2">
                {folders.map(folder => (
                  <div
                    key={folder.id}
                    className={`group flex items-center justify-between px-4 py-3 rounded-xl cursor-pointer transition-all duration-300 ${
                      selectedFolder === folder.id
                        ? 'bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 border-2 border-blue-200 shadow-md'
                        : 'hover:bg-white/60 text-gray-700 border-2 border-transparent hover:shadow-sm'
                    }`}
                    onClick={() => setSelectedFolder(folder.id)}
                  >
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      <Folder className={`w-5 h-5 flex-shrink-0 ${selectedFolder === folder.id ? 'text-blue-600' : 'text-gray-400'}`} />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{folder.name}</p>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteFolder(folder.id, folder.name);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-2 text-red-500 hover:bg-red-50 rounded-lg transition-all duration-300"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Content - Upload & Files */}
        <div className="flex-1 flex flex-col">
          {/* Modern Upload Zone */}
          {selectedFolder && (
            <div className="mb-6">
              <div className="relative overflow-hidden rounded-2xl border-2 border-dashed border-gray-300 bg-white/40 hover:bg-white/60 hover:border-blue-400 backdrop-blur-sm transition-all duration-300">
                <div className="p-8 text-center">
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    onChange={handleFileInputChange}
                    className="hidden"
                    accept=".pdf,.txt,.md,.json,.xml,.docx,.xlsx"
                  />
                  
                  <div className="flex flex-col items-center">
                    <div className="p-4 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl shadow-lg mb-6">
                      <Upload className="w-12 h-12 text-white" />
                    </div>
                    
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      Dateien hochladen
                    </h3>
                    
                    <p className="text-gray-600 mb-1">
                      Klicken Sie zum Auswählen der Dateien
                    </p>
                    
                    <p className="text-sm text-gray-500 mb-6">
                      In Ordner: <span className="font-semibold text-blue-600">
                        {folders.find(f => f.id === selectedFolder)?.name}
                      </span>
                    </p>
                    
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading}
                      className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium shadow-lg shadow-blue-500/25 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 transition-all duration-300"
                    >
                      {uploading ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Wird hochgeladen...</span>
                        </div>
                      ) : (
                        'Dateien auswählen'
                      )}
                    </button>
                  </div>
                  
                  {/* Upload Progress */}
                  {Object.entries(uploadProgress).map(([fileId, progress]) => (
                    <div key={fileId} className="mt-4 text-left">
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                        <span className="truncate">{fileId.split('-')[0]}</span>
                        <span>{Math.round(progress)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Files List */}
          <div className="flex-1 bg-white/60 backdrop-blur-sm border border-white/20 rounded-2xl shadow-xl overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200/50">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-xl text-gray-900 flex items-center">
                  <FileText className="w-6 h-6 mr-3 text-green-600" />
                  Dateien
                  {selectedFolder && (
                    <span className="ml-2 text-sm text-gray-500">
                      in {folders.find(f => f.id === selectedFolder)?.name}
                    </span>
                  )}
                </h3>
                
                {/* Search and Batch Operations */}
                {selectedFolder && files.length > 0 && (
                  <div className="flex items-center space-x-3">
                    {/* Search */}
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Dateien suchen..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white/80"
                      />
                    </div>
                    
                    {/* Batch Operations */}
                    {selectedFiles.size > 0 && (
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600">
                          {selectedFiles.size} ausgewählt
                        </span>
                        <button
                          onClick={batchDeleteFiles}
                          className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all duration-300 text-sm flex items-center space-x-1"
                        >
                          <Trash2 className="w-4 h-4" />
                          <span>Löschen</span>
                        </button>
                      </div>
                    )}
                    
                    {/* Select All */}
                    <button
                      onClick={selectAllFiles}
                      className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-300"
                      title="Alle auswählen/abwählen"
                    >
                      {getFilteredFiles().every(f => selectedFiles.has(f.id)) && getFilteredFiles().length > 0 ? (
                        <CheckSquare className="w-4 h-4" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                )}
              </div>
              
              {/* File Statistics */}
              {selectedFolder && files.length > 0 && (
                <div className="flex items-center space-x-6 text-sm text-gray-600">
                  <span>{getFilteredFiles().length} von {files.length} Dateien</span>
                  <span>•</span>
                  <span>{formatFileSize(files.reduce((sum, file) => sum + file.file_size, 0))} gesamt</span>
                  {searchTerm && (
                    <>
                      <span>•</span>
                      <span>Suche: "{searchTerm}"</span>
                    </>
                  )}
                </div>
              )}
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              {!selectedFolder ? (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <Folder className="w-20 h-20 mx-auto mb-6 text-gray-300" />
                    <h4 className="text-lg font-medium mb-2">Wählen Sie einen Ordner</h4>
                    <p>Wählen Sie links einen Ordner aus, um dessen Dateien anzuzeigen</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {getFilteredFiles().length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                      <FileText className="w-20 h-20 mx-auto mb-6 text-gray-300" />
                      <h4 className="text-lg font-medium mb-2">
                        {searchTerm ? 'Keine passenden Dateien gefunden' : 'Keine Dateien'}
                      </h4>
                      <p>{searchTerm ? `Keine Dateien gefunden für "${searchTerm}"` : 'Laden Sie Dateien hoch, um hier zu beginnen'}</p>
                    </div>
                  ) : (
                    getFilteredFiles().map(file => (
                      <div 
                        key={file.id} 
                        className={`group bg-white/80 backdrop-blur-sm p-5 rounded-xl shadow-sm border transition-all duration-300 ${
                          selectedFiles.has(file.id)
                            ? 'border-blue-300 shadow-md bg-blue-50/30'
                            : 'border-white/30 hover:shadow-md'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            {/* Selection Checkbox */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleFileSelection(file.id);
                              }}
                              className="p-1 hover:bg-gray-100 rounded transition-all duration-300"
                            >
                              {selectedFiles.has(file.id) ? (
                                <CheckSquare className="w-5 h-5 text-blue-600" />
                              ) : (
                                <Square className="w-5 h-5 text-gray-400 group-hover:text-gray-600" />
                              )}
                            </button>
                            
                            <div className="p-2 bg-blue-50 rounded-lg">
                              <FileText className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900">{file.filename}</p>
                              <div className="flex items-center space-x-4 text-sm text-gray-500">
                                <span>{formatFileSize(file.file_size)}</span>
                                <span>•</span>
                                <span>{new Date(file.upload_date).toLocaleDateString('de-DE')}</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-3">
                            <span className={`text-sm px-3 py-1 rounded-full font-medium ${
                              file.status === 'completed' || file.status === 'indexed'
                                ? 'bg-green-100 text-green-800'
                                : file.status === 'processing' || file.status === 'indexing'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {file.status}
                            </span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteFile(file.id, file.filename);
                              }}
                              className="opacity-0 group-hover:opacity-100 p-2 text-red-500 hover:bg-red-50 rounded-lg transition-all duration-300"
                              title="Datei löschen"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Create Folder Modal */}
      {showCreateFolder && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white/95 backdrop-blur-lg rounded-2xl p-8 w-full max-w-md mx-4 shadow-2xl border border-white/20">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Neuen Ordner erstellen</h3>
            <input
              type="text"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder="Ordner-Name eingeben"
              className="w-full p-4 border border-gray-300 rounded-xl mb-6 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white/80 backdrop-blur-sm"
              autoFocus
              onKeyPress={(e) => e.key === 'Enter' && createFolder()}
            />
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => {
                  setShowCreateFolder(false);
                  setNewFolderName('');
                }}
                className="px-6 py-3 text-gray-600 hover:text-gray-800 font-medium rounded-xl hover:bg-gray-100 transition-all duration-300"
              >
                Abbrechen
              </button>
              <button
                onClick={createFolder}
                disabled={!newFolderName.trim() || creating}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-medium shadow-lg shadow-blue-500/25 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 transition-all duration-300"
              >
                {creating ? 'Erstelle...' : 'Erstellen'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};