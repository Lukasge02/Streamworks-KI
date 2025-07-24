import React, { useState, useEffect, useRef } from 'react';
import { Folder, Plus, Upload, Trash2, FileText, ChevronRight, ChevronDown, RefreshCw, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface Category {
  id: string;
  slug: string;
  name: string;
  folder_count: number;
}

interface FolderItem {
  id: string;
  name: string;
  slug: string;
  parent_folder_id: string | null;
  file_count: number;
  subfolder_count: number;
}

interface FileItem {
  id: string;
  filename: string;
  file_size: number;
  upload_date: string;
  processing_status: string;
  folder_id?: string;
  folder_name?: string;
}

export const EnhancedTrainingData: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [folders, setFolders] = useState<FolderItem[]>([]);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{[key: string]: number}>({});
  
  // Create folder states
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [creating, setCreating] = useState(false);
  
  // File upload ref
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  // Load folders
  const loadFolders = async () => {
    if (!selectedCategory) return;
    
    try {
      const response = await fetch(`/api/v1/folders/categories/${selectedCategory}/folders`);
      if (!response.ok) {
        if (response.status === 404) {
          setFolders([]);
          return;
        }
        throw new Error('Failed to load folders');
      }
      const data = await response.json();
      setFolders(data.folders || []);
    } catch (err) {
      console.error('Folders load error:', err);
      setFolders([]);
    }
  };

  // Load files
  const loadFiles = async () => {
    if (!selectedCategory) return;
    
    try {
      const url = selectedFolder 
        ? `/api/v1/files/files?category_slug=${selectedCategory}&folder_id=${selectedFolder}`
        : `/api/v1/files/files?category_slug=${selectedCategory}`;
        
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to load files');
      const data = await response.json();
      setFiles(data || []);
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

  // Delete folder
  const deleteFolder = async (folderId: string, folderName: string) => {
    if (!confirm(`Ordner "${folderName}" wirklich löschen?`)) return;
    
    try {
      const response = await fetch(`/api/v1/folders/folders/${folderId}?force=true`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Fehler beim Löschen');
      }
      
      if (selectedFolder === folderId) setSelectedFolder('');
      await loadFolders();
      await loadCategories();
      await loadFiles();
      setError('');
      
    } catch (err: any) {
      setError(`Ordner löschen fehlgeschlagen: ${err.message}`);
    }
  };

  // Handle file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    if (!selectedCategory || !selectedFolder) {
      setError('Bitte wählen Sie erst eine Kategorie und einen Ordner');
      return;
    }

    setUploading(true);
    setError('');
    
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
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
      loadFiles();
    }
  }, [selectedCategory]);

  // Load files when folder changes
  useEffect(() => {
    if (selectedCategory) {
      loadFiles();
    }
  }, [selectedFolder]);

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
      case 'indexed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'processing':
      case 'indexing':
        return <Clock className="w-4 h-4 text-blue-600 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
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

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Top Tabs */}
      <div className="bg-white border-b shadow-sm">
        <div className="flex items-center px-4 py-2">
          <div className="flex space-x-1">
            {categories.map(cat => (
              <button
                key={cat.slug}
                onClick={() => {
                  setSelectedCategory(cat.slug);
                  setSelectedFolder('');
                }}
                className={`px-4 py-2 font-medium text-sm rounded-t-lg transition-colors ${
                  selectedCategory === cat.slug
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {cat.name}
                <span className="ml-2 text-xs opacity-80">({cat.folder_count})</span>
              </button>
            ))}
          </div>
          <div className="ml-auto flex items-center space-x-2">
            <button
              onClick={() => {
                loadFolders();
                loadFiles();
              }}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
              title="Aktualisieren"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
          <button onClick={() => setError('')} className="float-right text-red-500 hover:text-red-700">×</button>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Folders */}
        <div className="w-64 bg-white border-r flex flex-col">
          <div className="p-4 border-b">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">Ordner</h3>
              <button
                onClick={() => setShowCreateFolder(true)}
                className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                title="Neuer Ordner"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-2">
            {folders.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Folder className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p className="text-sm">Keine Ordner</p>
              </div>
            ) : (
              <div className="space-y-1">
                {folders.map(folder => (
                  <div
                    key={folder.id}
                    className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                      selectedFolder === folder.id
                        ? 'bg-blue-50 text-blue-700'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                    onClick={() => setSelectedFolder(folder.id)}
                  >
                    <div className="flex items-center space-x-2 flex-1">
                      <Folder className={`w-4 h-4 ${selectedFolder === folder.id ? 'text-blue-600' : 'text-gray-400'}`} />
                      <span className="text-sm font-medium truncate">{folder.name}</span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteFolder(folder.id, folder.name);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:bg-red-50 rounded transition-opacity"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Content - Files */}
        <div className="flex-1 flex flex-col">
          {/* Upload Area */}
          {selectedFolder && (
            <div className="p-4 bg-white border-b">
              <div className="relative">
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  onChange={handleFileUpload}
                  className="hidden"
                  accept=".pdf,.txt,.md,.json,.xml"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  <Upload className="w-5 h-5" />
                  <span>{uploading ? 'Wird hochgeladen...' : 'Dateien hochladen'}</span>
                </button>
              </div>
              
              {/* Upload Progress */}
              {Object.entries(uploadProgress).map(([fileId, progress]) => (
                <div key={fileId} className="mt-2">
                  <div className="text-sm text-gray-600 mb-1">{fileId.split('-')[0]}</div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Files List */}
          <div className="flex-1 overflow-y-auto p-4">
            {!selectedFolder ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <Folder className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p>Wählen Sie einen Ordner aus</p>
                </div>
              </div>
            ) : files.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p>Keine Dateien in diesem Ordner</p>
                  <p className="text-sm mt-2">Laden Sie Dateien hoch, um zu beginnen</p>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                {files.filter(file => !selectedFolder || file.folder_id === selectedFolder).map(file => (
                  <div key={file.id} className="bg-white p-4 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <FileText className="w-5 h-5 text-gray-400" />
                        <div>
                          <p className="font-medium text-gray-900">{file.filename}</p>
                          <p className="text-sm text-gray-500">
                            {formatFileSize(file.file_size)} • {new Date(file.upload_date).toLocaleDateString('de-DE')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(file.processing_status)}
                        <span className="text-sm text-gray-600">{file.processing_status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Folder Modal */}
      {showCreateFolder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Neuen Ordner erstellen</h3>
            <input
              type="text"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder="Ordner-Name eingeben"
              className="w-full p-3 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              autoFocus
              onKeyPress={(e) => e.key === 'Enter' && createFolder()}
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowCreateFolder(false);
                  setNewFolderName('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Abbrechen
              </button>
              <button
                onClick={createFolder}
                disabled={!newFolderName.trim() || creating}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
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