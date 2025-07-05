import React, { useState, useCallback } from 'react';
import { 
  Upload, FileText, CheckCircle, AlertCircle, X, 
  Trash2, Play, Pause, RotateCcw
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { apiService } from '../../services/apiService';
import { 
  SUPPORTED_EXTENSIONS, 
  TOTAL_SUPPORTED_FORMATS,
  validateFile,
  getDropzoneAcceptConfig 
} from '../../utils/fileFormats';

interface UploadFile {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  progress: number;
  error?: string;
  result?: any;
}

interface BatchUploaderProps {
  onUploadComplete?: () => void;
  maxFiles?: number;
  allowedCategory?: 'help_data' | 'stream_templates';
}

const BatchUploader: React.FC<BatchUploaderProps> = ({ 
  onUploadComplete, 
  maxFiles = 20,
  allowedCategory = 'help_data'
}) => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentUploadIndex, setCurrentUploadIndex] = useState(0);

  // Use centralized format configuration
  const allowedExtensions = SUPPORTED_EXTENSIONS;

  // Drag & Drop Setup
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadFile[] = acceptedFiles
      .filter(file => {
        const validation = validateFile(file);
        return validation.isValid;
      })
      .slice(0, maxFiles - files.length) // Limitiere auf maxFiles
      .map(file => ({
        file,
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        status: 'pending' as const,
        progress: 0
      }));

    setFiles(prev => [...prev, ...newFiles]);
  }, [files.length, maxFiles, allowedExtensions]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: getDropzoneAcceptConfig(),
    maxFiles: maxFiles - files.length,
    disabled: isUploading
  });

  // Einzelne Datei entfernen
  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  // Alle Dateien entfernen
  const clearAllFiles = () => {
    if (!isUploading) {
      setFiles([]);
      setCurrentUploadIndex(0);
    }
  };

  // Einzelne Datei hochladen mit Progress-Tracking
  const uploadSingleFile = async (uploadFile: UploadFile): Promise<boolean> => {
    try {
      // Status auf uploading setzen
      setFiles(prev => prev.map(f => 
        f.id === uploadFile.id 
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      ));

      // FormData erstellen
      const formData = new FormData();
      formData.append('file', uploadFile.file);
      formData.append('category', allowedCategory);

      // Upload mit Progress-Simulation (real: XMLHttpRequest für echten Progress)
      const progressInterval = setInterval(() => {
        setFiles(prev => prev.map(f => 
          f.id === uploadFile.id && f.progress < 90
            ? { ...f, progress: f.progress + 10 }
            : f
        ));
      }, 200);

      // API-Aufruf
      const result = await apiService.uploadTrainingFile(uploadFile.file, allowedCategory);

      clearInterval(progressInterval);

      if (result.success) {
        // Erfolg
        setFiles(prev => prev.map(f => 
          f.id === uploadFile.id 
            ? { ...f, status: 'completed', progress: 100, result: result.data }
            : f
        ));
        return true;
      } else {
        // Fehler
        setFiles(prev => prev.map(f => 
          f.id === uploadFile.id 
            ? { ...f, status: 'error', progress: 0, error: result.error }
            : f
        ));
        return false;
      }

    } catch (error) {
      // Exception
      setFiles(prev => prev.map(f => 
        f.id === uploadFile.id 
          ? { ...f, status: 'error', progress: 0, error: String(error) }
          : f
      ));
      return false;
    }
  };

  // Alle Dateien sequenziell hochladen
  const uploadAllFiles = async () => {
    if (files.length === 0 || isUploading) return;

    setIsUploading(true);
    setIsPaused(false);
    setCurrentUploadIndex(0);

    let successCount = 0;
    let errorCount = 0;

    for (let i = 0; i < files.length; i++) {
      if (isPaused) {
        break; // Upload pausiert
      }

      const file = files[i];
      if (file.status === 'pending') {
        setCurrentUploadIndex(i);
        const success = await uploadSingleFile(file);
        
        if (success) {
          successCount++;
        } else {
          errorCount++;
        }

        // Kurze Pause zwischen Uploads
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }

    setIsUploading(false);
    setCurrentUploadIndex(0);

    // Callback aufrufen
    if (onUploadComplete) {
      onUploadComplete();
    }

    // Status-Meldung
    console.log(`📊 Batch-Upload abgeschlossen: ${successCount} erfolgreich, ${errorCount} Fehler`);
  };

  // Upload pausieren/fortsetzen
  const togglePause = () => {
    setIsPaused(!isPaused);
  };

  // Upload abbrechen
  const cancelUpload = () => {
    setIsUploading(false);
    setIsPaused(false);
    setCurrentUploadIndex(0);
    
    // Zurücksetzen auf pending für nicht hochgeladene Dateien
    setFiles(prev => prev.map(f => 
      f.status === 'uploading' 
        ? { ...f, status: 'pending', progress: 0 }
        : f
    ));
  };

  // Fehlgeschlagene Uploads wiederholen
  const retryFailedUploads = async () => {
    const failedFiles = files.filter(f => f.status === 'error');
    
    for (const file of failedFiles) {
      if (!isPaused) {
        await uploadSingleFile(file);
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
  };

  // Statistiken berechnen
  const stats = {
    total: files.length,
    pending: files.filter(f => f.status === 'pending').length,
    uploading: files.filter(f => f.status === 'uploading').length,
    completed: files.filter(f => f.status === 'completed').length,
    error: files.filter(f => f.status === 'error').length
  };

  return (
    <div className="space-y-6">
      {/* Drag & Drop Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
          isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
        } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        
        {isDragActive ? (
          <p className="text-blue-600 font-medium">Dateien hier ablegen...</p>
        ) : (
          <div>
            <p className="text-gray-600 font-medium mb-2">
              Mehrere Dateien gleichzeitig hochladen
            </p>
            <p className="text-sm text-gray-500">
              {TOTAL_SUPPORTED_FORMATS} Formate unterstützt (max. {maxFiles} Dateien, 50MB pro Datei)
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Dateien hierher ziehen oder klicken zum Auswählen
            </p>
          </div>
        )}
      </div>

      {/* Statistiken */}
      {files.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-900">
              Dateien zur Verarbeitung ({stats.total})
            </h3>
            <div className="flex gap-2">
              {!isUploading && stats.pending > 0 && (
                <button
                  onClick={uploadAllFiles}
                  className="flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                >
                  <Play className="h-4 w-4" />
                  Alle hochladen
                </button>
              )}
              
              {isUploading && (
                <div className="flex gap-2">
                  <button
                    onClick={togglePause}
                    className="flex items-center gap-2 px-3 py-1 bg-yellow-500 text-white rounded text-sm hover:bg-yellow-600"
                  >
                    {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
                    {isPaused ? 'Fortsetzen' : 'Pausieren'}
                  </button>
                  
                  <button
                    onClick={cancelUpload}
                    className="flex items-center gap-2 px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                  >
                    <X className="h-4 w-4" />
                    Abbrechen
                  </button>
                </div>
              )}
              
              {stats.error > 0 && !isUploading && (
                <button
                  onClick={retryFailedUploads}
                  className="flex items-center gap-2 px-3 py-1 bg-orange-500 text-white rounded text-sm hover:bg-orange-600"
                >
                  <RotateCcw className="h-4 w-4" />
                  Erneut versuchen
                </button>
              )}
              
              {!isUploading && (
                <button
                  onClick={clearAllFiles}
                  className="flex items-center gap-2 px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600"
                >
                  <Trash2 className="h-4 w-4" />
                  Alle entfernen
                </button>
              )}
            </div>
          </div>

          {/* Status-Übersicht */}
          <div className="grid grid-cols-5 gap-4 text-sm">
            <div className="text-center">
              <div className="text-lg font-bold text-gray-600">{stats.pending}</div>
              <div className="text-gray-500">Wartend</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">{stats.uploading}</div>
              <div className="text-gray-500">Upload läuft</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">{stats.completed}</div>
              <div className="text-gray-500">Erfolgreich</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-red-600">{stats.error}</div>
              <div className="text-gray-500">Fehler</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-gray-800">{stats.total}</div>
              <div className="text-gray-500">Gesamt</div>
            </div>
          </div>
        </div>
      )}

      {/* Datei-Liste */}
      {files.length > 0 && (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {files.map((uploadFile, index) => (
            <div 
              key={uploadFile.id} 
              className={`flex items-center justify-between p-3 rounded-lg border ${
                index === currentUploadIndex && isUploading 
                  ? 'border-blue-200 bg-blue-50' 
                  : 'border-gray-200 bg-white'
              }`}
            >
              {/* Datei-Info */}
              <div className="flex items-center flex-1 min-w-0">
                <FileText className="h-5 w-5 text-gray-400 mr-3 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {uploadFile.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>

              {/* Status & Progress */}
              <div className="flex items-center gap-3">
                {/* Progress Bar */}
                {uploadFile.status === 'uploading' && (
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadFile.progress}%` }}
                    />
                  </div>
                )}

                {/* Status Icon */}
                {uploadFile.status === 'pending' && (
                  <div className="w-6 h-6 rounded-full border-2 border-gray-300" />
                )}
                
                {uploadFile.status === 'uploading' && (
                  <div className="w-6 h-6 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
                )}
                
                {uploadFile.status === 'completed' && (
                  <CheckCircle className="h-6 w-6 text-green-500" />
                )}
                
                {uploadFile.status === 'error' && (
                  <AlertCircle 
                    className="h-6 w-6 text-red-500" 
                  />
                )}

                {/* Remove Button */}
                {!isUploading && (
                  <button
                    onClick={() => removeFile(uploadFile.id)}
                    className="p-1 text-gray-400 hover:text-red-500"
                    title="Datei entfernen"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Status */}
      {isUploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-900">
                {isPaused ? 'Upload pausiert' : `Uploading Datei ${currentUploadIndex + 1} von ${files.length}`}
              </p>
              <p className="text-xs text-blue-700 mt-1">
                {isPaused ? 'Klicken Sie auf "Fortsetzen" um fortzufahren' : 'Bitte warten...'}
              </p>
            </div>
            
            {/* Overall Progress */}
            <div className="text-right">
              <div className="text-sm font-bold text-blue-900">
                {Math.round(((stats.completed + stats.error) / stats.total) * 100)}%
              </div>
              <div className="w-24 bg-blue-200 rounded-full h-2 mt-1">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${((stats.completed + stats.error) / stats.total) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Summary */}
      {stats.error > 0 && !isUploading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-red-900 mb-2">
            {stats.error} Datei(en) konnten nicht hochgeladen werden
          </h4>
          <div className="space-y-1">
            {files
              .filter(f => f.status === 'error')
              .map(f => (
                <p key={f.id} className="text-xs text-red-700">
                  • {f.file.name}: {f.error}
                </p>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BatchUploader;