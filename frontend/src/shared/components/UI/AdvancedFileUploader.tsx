/**
 * Advanced File Uploader Component
 * Enhanced drag-and-drop uploader with preview, batch operations, and error handling
 */

import React, { useState, useRef, useCallback, useMemo } from 'react';
import { Upload, X, Eye, Pause, Play, RefreshCw, Check, AlertCircle, Files, Image, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './Button';
import { Progress } from './Progress';
import { Badge } from './Badge';
import { useToast } from './Toast';

export interface UploadProgress {
  id: string;
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error' | 'paused';
  error?: string;
}

interface AdvancedFileUploaderProps {
  accept?: string[];
  maxSize?: number; // in bytes
  maxFiles?: number;
  onUpload: (files: File[]) => Promise<void>;
  onProgress?: (progress: UploadProgress[]) => void;
  multiple?: boolean;
  preview?: boolean;
  className?: string;
  disabled?: boolean;
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getFileType = (file: File): 'image' | 'document' | 'other' => {
  if (file.type.startsWith('image/')) return 'image';
  if (file.type.includes('pdf') || file.type.includes('document') || file.type.includes('text')) return 'document';
  return 'other';
};

const FileIcon = ({ file, size = 24 }: { file: File; size?: number }) => {
  const type = getFileType(file);
  
  switch (type) {
    case 'image':
      return <Image size={size} className="text-blue-500" />;
    case 'document':
      return <FileText size={size} className="text-green-500" />;
    default:
      return <Files size={size} className="text-gray-500" />;
  }
};

export function AdvancedFileUploader({
  accept = [],
  maxSize = 10 * 1024 * 1024, // 10MB default
  maxFiles = 10,
  onUpload,
  onProgress,
  multiple = true,
  preview = true,
  className = '',
  disabled = false,
}: AdvancedFileUploaderProps) {
  const [files, setFiles] = useState<UploadProgress[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [previewFile, setPreviewFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { showError, showSuccess } = useToast();

  const validateFile = useCallback((file: File): string | null => {
    if (accept.length > 0 && !accept.some(type => file.type.includes(type))) {
      return `File type ${file.type} is not supported. Accepted types: ${accept.join(', ')}`;
    }
    
    if (file.size > maxSize) {
      return `File size ${formatFileSize(file.size)} exceeds maximum allowed size of ${formatFileSize(maxSize)}`;
    }
    
    return null;
  }, [accept, maxSize]);

  const handleFiles = useCallback((newFiles: FileList | File[]) => {
    const fileArray = Array.from(newFiles);
    
    if (files.length + fileArray.length > maxFiles) {
      showError(`Maximum ${maxFiles} files allowed. You can upload ${maxFiles - files.length} more files.`);
      return;
    }

    const validatedFiles: UploadProgress[] = [];
    
    fileArray.forEach(file => {
      const error = validateFile(file);
      validatedFiles.push({
        id: `${file.name}-${Date.now()}-${Math.random()}`,
        file,
        progress: 0,
        status: error ? 'error' : 'pending',
        error,
      });
    });

    setFiles(prev => [...prev, ...validatedFiles]);
  }, [files.length, maxFiles, validateFile, showError]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    
    if (disabled) return;
    
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      handleFiles(droppedFiles);
    }
  }, [disabled, handleFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      handleFiles(selectedFiles);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [handleFiles]);

  const removeFile = useCallback((id: string) => {
    setFiles(prev => prev.filter(file => file.id !== id));
  }, []);

  const retryFile = useCallback((id: string) => {
    setFiles(prev => prev.map(file => 
      file.id === id 
        ? { ...file, status: 'pending', error: undefined, progress: 0 }
        : file
    ));
  }, []);

  const pauseFile = useCallback((id: string) => {
    setFiles(prev => prev.map(file => 
      file.id === id && file.status === 'uploading'
        ? { ...file, status: 'paused' }
        : file
    ));
  }, []);

  const resumeFile = useCallback((id: string) => {
    setFiles(prev => prev.map(file => 
      file.id === id && file.status === 'paused'
        ? { ...file, status: 'uploading' }
        : file
    ));
  }, []);

  const clearAll = useCallback(() => {
    setFiles([]);
  }, []);

  const removeCompleted = useCallback(() => {
    setFiles(prev => prev.filter(file => file.status !== 'completed'));
  }, []);

  const retryFailed = useCallback(() => {
    setFiles(prev => prev.map(file => 
      file.status === 'error'
        ? { ...file, status: 'pending', error: undefined, progress: 0 }
        : file
    ));
  }, []);

  const uploadFiles = useCallback(async () => {
    const pendingFiles = files.filter(file => file.status === 'pending');
    if (pendingFiles.length === 0) return;

    setIsUploading(true);
    
    try {
      // Mark files as uploading
      setFiles(prev => prev.map(file => 
        file.status === 'pending'
          ? { ...file, status: 'uploading' }
          : file
      ));

      // Simulate progress updates (replace with real upload logic)
      for (const file of pendingFiles) {
        try {
          // Simulate upload progress
          for (let progress = 0; progress <= 100; progress += 10) {
            await new Promise(resolve => setTimeout(resolve, 100));
            setFiles(prev => prev.map(f => 
              f.id === file.id
                ? { ...f, progress }
                : f
            ));
          }
          
          // Mark as completed
          setFiles(prev => prev.map(f => 
            f.id === file.id
              ? { ...f, status: 'completed', progress: 100 }
              : f
          ));
        } catch (error) {
          setFiles(prev => prev.map(f => 
            f.id === file.id
              ? { ...f, status: 'error', error: 'Upload failed' }
              : f
          ));
        }
      }

      await onUpload(pendingFiles.map(f => f.file));
      showSuccess(`Successfully uploaded ${pendingFiles.length} files`);
    } catch (error) {
      showError('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  }, [files, onUpload, showSuccess, showError]);

  const stats = useMemo(() => {
    const total = files.length;
    const completed = files.filter(f => f.status === 'completed').length;
    const failed = files.filter(f => f.status === 'error').length;
    const pending = files.filter(f => f.status === 'pending').length;
    const uploading = files.filter(f => f.status === 'uploading').length;
    
    return { total, completed, failed, pending, uploading };
  }, [files]);

  // Notify parent about progress changes
  React.useEffect(() => {
    if (onProgress) {
      onProgress(files);
    }
  }, [files, onProgress]);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
          ${isDragOver 
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
            : 'border-neutral-300 dark:border-neutral-600 hover:border-primary-400 dark:hover:border-primary-500'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept.join(',')}
          multiple={multiple}
          onChange={handleFileSelect}
          className="hidden"
          disabled={disabled}
        />
        
        <motion.div
          animate={{ scale: isDragOver ? 1.05 : 1 }}
          transition={{ duration: 0.2 }}
          className="space-y-4"
        >
          <div className="w-16 h-16 mx-auto bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
            <Upload size={32} className="text-primary-600 dark:text-primary-400" />
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
              {isDragOver ? 'Drop files here' : 'Upload files'}
            </h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              Drag and drop files here, or click to select files
            </p>
            <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
              Max {maxFiles} files, up to {formatFileSize(maxSize)} each
              {accept.length > 0 && ` • Accepted: ${accept.join(', ')}`}
            </p>
          </div>
        </motion.div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-4">
          {/* Stats and Actions */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-sm text-neutral-600 dark:text-neutral-400">
                {stats.total} files • {stats.completed} completed • {stats.failed} failed
              </div>
              {stats.total > 0 && (
                <div className="flex items-center space-x-2">
                  {stats.completed > 0 && (
                    <Badge variant="success" size="sm">
                      {stats.completed} completed
                    </Badge>
                  )}
                  {stats.failed > 0 && (
                    <Badge variant="error" size="sm">
                      {stats.failed} failed
                    </Badge>
                  )}
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              {stats.pending > 0 && (
                <Button
                  size="sm"
                  onClick={uploadFiles}
                  loading={isUploading}
                  disabled={disabled}
                >
                  Upload {stats.pending} files
                </Button>
              )}
              {stats.failed > 0 && (
                <Button size="sm" variant="outline" onClick={retryFailed}>
                  Retry Failed
                </Button>
              )}
              {stats.completed > 0 && (
                <Button size="sm" variant="outline" onClick={removeCompleted}>
                  Clear Completed
                </Button>
              )}
              <Button size="sm" variant="ghost" onClick={clearAll}>
                Clear All
              </Button>
            </div>
          </div>

          {/* Files */}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            <AnimatePresence>
              {files.map((fileProgress) => (
                <motion.div
                  key={fileProgress.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="border border-neutral-200 dark:border-neutral-700 rounded-lg p-4 bg-white dark:bg-neutral-800"
                >
                  <div className="flex items-center space-x-3">
                    <FileIcon file={fileProgress.file} />
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate">
                          {fileProgress.file.name}
                        </p>
                        <div className="flex items-center space-x-2">
                          {preview && getFileType(fileProgress.file) === 'image' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setPreviewFile(fileProgress.file)}
                              className="h-6 w-6 p-0"
                            >
                              <Eye size={14} />
                            </Button>
                          )}
                          
                          {fileProgress.status === 'uploading' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => pauseFile(fileProgress.id)}
                              className="h-6 w-6 p-0"
                            >
                              <Pause size={14} />
                            </Button>
                          )}
                          
                          {fileProgress.status === 'paused' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => resumeFile(fileProgress.id)}
                              className="h-6 w-6 p-0"
                            >
                              <Play size={14} />
                            </Button>
                          )}
                          
                          {fileProgress.status === 'error' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => retryFile(fileProgress.id)}
                              className="h-6 w-6 p-0"
                            >
                              <RefreshCw size={14} />
                            </Button>
                          )}
                          
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeFile(fileProgress.id)}
                            className="h-6 w-6 p-0 text-red-600 hover:text-red-700"
                          >
                            <X size={14} />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2 text-xs text-neutral-500 dark:text-neutral-400">
                        <span>{formatFileSize(fileProgress.file.size)}</span>
                        <span>•</span>
                        <span className="capitalize">{fileProgress.status}</span>
                        {fileProgress.status === 'completed' && (
                          <>
                            <Check size={12} className="text-green-500" />
                            <span className="text-green-600 dark:text-green-400">Complete</span>
                          </>
                        )}
                        {fileProgress.status === 'error' && (
                          <>
                            <AlertCircle size={12} className="text-red-500" />
                            <span className="text-red-600 dark:text-red-400">
                              {fileProgress.error || 'Error'}
                            </span>
                          </>
                        )}
                      </div>
                      
                      {(fileProgress.status === 'uploading' || fileProgress.status === 'paused') && (
                        <div className="mt-2">
                          <Progress 
                            value={fileProgress.progress} 
                            className="h-1"
                            variant={fileProgress.status === 'paused' ? 'warning' : 'primary'}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Image Preview Modal */}
      <AnimatePresence>
        {previewFile && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
            onClick={() => setPreviewFile(null)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="relative max-w-4xl max-h-full"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={URL.createObjectURL(previewFile)}
                alt={previewFile.name}
                className="max-w-full max-h-full object-contain rounded-lg"
              />
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPreviewFile(null)}
                className="absolute top-2 right-2 bg-black/50 text-white hover:bg-black/70"
              >
                <X size={16} />
              </Button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}