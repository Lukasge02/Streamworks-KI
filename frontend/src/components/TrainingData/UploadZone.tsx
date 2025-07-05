import React, { useCallback, useState } from 'react';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { FileCategory } from './TrainingDataTab';

interface UploadZoneProps {
  category: FileCategory;
  onFilesUploaded: (files: File[]) => void;
  isLoading?: boolean;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  category,
  onFilesUploaded,
  isLoading = false
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const allowedExtensions = ['.txt', '.csv', '.md', '.pdf', '.docx', '.xml']; // Unified list

  const maxFileSize = 50 * 1024 * 1024; // 50MB

  const validateFiles = (files: File[]): { valid: File[], errors: string[] } => {
    const valid: File[] = [];
    const errors: string[] = [];

    files.forEach(file => {
      // Check file extension
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!allowedExtensions.includes(extension)) {
        errors.push(`${file.name}: Nicht erlaubte Dateiendung. Erlaubt: ${allowedExtensions.join(', ')}`);
        return;
      }

      // Check file size
      if (file.size > maxFileSize) {
        errors.push(`${file.name}: Datei zu groß (max. 50MB)`);
        return;
      }

      valid.push(file);
    });

    return { valid, errors };
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const { valid, errors } = validateFiles(files);
    
    setErrors(errors);
    
    if (valid.length > 0) {
      onFilesUploaded(valid);
    }
  }, [onFilesUploaded]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const { valid, errors } = validateFiles(files);
    
    setErrors(errors);
    
    if (valid.length > 0) {
      onFilesUploaded(valid);
    }
    
    // Reset input
    e.target.value = '';
  };

  // Simplified - no category-specific info needed

  return (
    <div>
      {isLoading && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-blue-700 font-medium">📤 Upload läuft...</p>
        </div>
      )}

      {/* Upload Zone */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragOver 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
      >
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          accept={allowedExtensions.join(',')}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={isLoading}
        />
        
        <div className="space-y-4">
          <div className={`
            w-16 h-16 mx-auto rounded-full flex items-center justify-center
            ${isDragOver ? 'bg-blue-100' : 'bg-gray-100'}
          `}>
            <Upload className={`
              w-8 h-8
              ${isDragOver ? 'text-blue-600' : 'text-gray-500'}
            `} />
          </div>
          
          <div>
            <p className={`
              text-lg font-medium mb-2
              ${isDragOver ? 'text-blue-600' : 'text-gray-900'}
            `}>
              {isDragOver ? 'Dateien hier ablegen' : 'Dateien hier ablegen oder klicken'}
            </p>
            
            <p className="text-gray-500 text-sm">
              Erlaubte Formate: {allowedExtensions.join(', ')} • Max. 50MB pro Datei • Bis zu 20 Dateien gleichzeitig
            </p>
          </div>
        </div>
      </div>

      {/* File Format Info */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-start space-x-3">
          <FileText className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-900 mb-1">Unterstützte Dateiformate</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {allowedExtensions.map((ext) => (
                <span key={ext} className="text-sm text-blue-700 font-mono">
                  {ext}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="mt-4 p-4 bg-red-50 rounded-lg">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-red-900 mb-2">Upload-Fehler</h3>
              <ul className="space-y-1">
                {errors.map((error, index) => (
                  <li key={index} className="text-sm text-red-700">
                    {error}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};