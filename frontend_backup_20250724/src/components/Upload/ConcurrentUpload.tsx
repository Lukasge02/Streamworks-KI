import React, { useState, useCallback, useRef } from 'react';
import { Upload, X, CheckCircle, AlertCircle, Clock, FileText, Trash2 } from 'lucide-react';

interface UploadProgress {
  id: string;
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  message?: string;
  response?: any;
}

interface ConcurrentUploadProps {
  categorySlug: string;
  folderId: string;
  onUploadComplete?: () => void;
  maxConcurrent?: number;
}

export const ConcurrentUpload: React.FC<ConcurrentUploadProps> = ({
  categorySlug,
  folderId,
  onUploadComplete,
  maxConcurrent = 3
}) => {
  const [uploads, setUploads] = useState<UploadProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const uploadQueue = useRef<UploadProgress[]>([]);
  const activeUploads = useRef<Set<string>>(new Set());
  const fileInputRef = useRef<HTMLInputElement>(null);

  const updateUpload = useCallback((id: string, updates: Partial<UploadProgress>) => {
    setUploads(prev => prev.map(upload => 
      upload.id === id ? { ...upload, ...updates } : upload
    ));
  }, []);

  const removeUpload = useCallback((id: string) => {
    setUploads(prev => prev.filter(upload => upload.id !== id));
    activeUploads.current.delete(id);
  }, []);

  const uploadFile = useCallback(async (uploadItem: UploadProgress) => {
    const { id, file } = uploadItem;
    
    try {
      activeUploads.current.add(id);
      updateUpload(id, { status: 'uploading', progress: 0 });

      const formData = new FormData();
      formData.append('file', file);
      formData.append('category_slug', categorySlug);
      formData.append('folder_id', folderId);

      const xhr = new XMLHttpRequest();
      
      const uploadPromise = new Promise<any>((resolve, reject) => {
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100);
            updateUpload(id, { progress });
          }
        };

        xhr.onload = () => {
          if (xhr.status === 200) {
            try {
              const response = JSON.parse(xhr.responseText);
              resolve(response);
            } catch (e) {
              reject(new Error('Invalid response format'));
            }
          } else {
            reject(new Error(`Upload failed: ${xhr.status}`));
          }
        };

        xhr.onerror = () => reject(new Error('Network error'));
        xhr.ontimeout = () => reject(new Error('Upload timeout'));
      });

      xhr.open('POST', '/api/v1/files/upload');
      xhr.timeout = 300000; // 5 minutes
      xhr.send(formData);

      const response = await uploadPromise;
      
      updateUpload(id, { 
        status: 'success', 
        progress: 100, 
        message: `Upload erfolgreich: ${response.filename}`,
        response
      });

      onUploadComplete?.();
      
    } catch (error) {
      updateUpload(id, { 
        status: 'error', 
        progress: 0, 
        message: `Upload fehlgeschlagen: ${error.message}` 
      });
    } finally {
      activeUploads.current.delete(id);
      processQueue();
    }
  }, [categorySlug, folderId, updateUpload, onUploadComplete]);

  const processQueue = useCallback(() => {
    while (uploadQueue.current.length > 0 && activeUploads.current.size < maxConcurrent) {
      const nextUpload = uploadQueue.current.shift();
      if (nextUpload) {
        uploadFile(nextUpload);
      }
    }
    
    // Check if all uploads are complete
    if (uploadQueue.current.length === 0 && activeUploads.current.size === 0) {
      setIsUploading(false);
    }
  }, [uploadFile, maxConcurrent]);

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    const newUploads: UploadProgress[] = files.map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      file,
      progress: 0,
      status: 'pending' as const
    }));

    setUploads(prev => [...prev, ...newUploads]);
    uploadQueue.current.push(...newUploads);
    
    setIsUploading(true);
    processQueue();

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [processQueue]);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    const files = Array.from(event.dataTransfer.files);
    
    if (files.length === 0) return;

    const newUploads: UploadProgress[] = files.map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      file,
      progress: 0,
      status: 'pending' as const
    }));

    setUploads(prev => [...prev, ...newUploads]);
    uploadQueue.current.push(...newUploads);
    
    setIsUploading(true);
    processQueue();
  }, [processQueue]);

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
  }, []);

  const clearCompleted = useCallback(() => {
    setUploads(prev => prev.filter(upload => upload.status === 'uploading' || upload.status === 'pending'));
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4 text-gray-500" />;
      case 'uploading': return <Upload className="w-4 h-4 text-blue-500" />;
      case 'success': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />;
      default: return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-gray-100 border-gray-200';
      case 'uploading': return 'bg-blue-50 border-blue-200';
      case 'success': return 'bg-green-50 border-green-200';
      case 'error': return 'bg-red-50 border-red-200';
      default: return 'bg-gray-100 border-gray-200';
    }
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors"
      >
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <div className="space-y-2">
          <h3 className="text-lg font-medium text-gray-900">Mehrere Dateien hochladen</h3>
          <p className="text-sm text-gray-500">
            Ziehe Dateien hierher oder klicke zum Auswählen
          </p>
          <div className="flex justify-center">
            <label className="cursor-pointer bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
              Dateien auswählen
              <input
                ref={fileInputRef}
                type="file"
                multiple
                className="hidden"
                onChange={handleFileSelect}
              />
            </label>
          </div>
          <p className="text-xs text-gray-400">
            Bis zu {maxConcurrent} Dateien werden gleichzeitig hochgeladen
          </p>
        </div>
      </div>

      {/* Upload Progress */}
      {uploads.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-medium text-gray-900">
              Upload Progress ({uploads.length} Dateien)
            </h4>
            <button
              onClick={clearCompleted}
              className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
            >
              Abgeschlossene löschen
            </button>
          </div>
          
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {uploads.map((upload) => (
              <div
                key={upload.id}
                className={`p-3 rounded-lg border ${getStatusColor(upload.status)}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    {getStatusIcon(upload.status)}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {upload.file.name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {(upload.file.size / 1024).toFixed(1)} KB
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {upload.status === 'uploading' && (
                      <div className="text-xs text-blue-600 font-medium">
                        {upload.progress}%
                      </div>
                    )}
                    
                    {(upload.status === 'success' || upload.status === 'error') && (
                      <button
                        onClick={() => removeUpload(upload.id)}
                        className="text-gray-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
                
                {upload.status === 'uploading' && (
                  <div className="mt-2">
                    <div className="bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${upload.progress}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {upload.message && (
                  <div className={`mt-2 text-xs ${
                    upload.status === 'error' ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {upload.message}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};