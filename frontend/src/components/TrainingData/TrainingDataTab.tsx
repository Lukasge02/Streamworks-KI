import React, { useState, useEffect } from 'react';
import { UploadZone } from './UploadZone';
import { FileManager } from './FileManager';
import { TrainingStatus } from './TrainingStatus';
import { CategorySelector } from './CategorySelector';
import { DocumentManager } from '../DocumentManager';
import { useAppStore } from '../../store/appStore';
import { apiService, TrainingFile } from '../../services/apiService';

export type FileCategory = 'help_data' | 'stream_templates';

export const TrainingDataTab: React.FC = () => {
  const [activeView, setActiveView] = useState<'upload' | 'manage'>('upload');
  const [selectedCategory, setSelectedCategory] = useState<FileCategory>('help_data');
  const [files, setFiles] = useState<TrainingFile[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load files on mount
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getTrainingFiles();
      if (response.success && response.data) {
        setFiles(response.data);
      } else {
        console.error('Failed to load files:', response.error);
      }
    } catch (error) {
      console.error('Failed to load files:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (uploadedFiles: File[], category: FileCategory) => {
    console.log(`Uploading ${uploadedFiles.length} files to category: ${category}`);
    
    for (const file of uploadedFiles) {
      try {
        // Add temporary file entry with uploading status
        const tempFile: TrainingFile = {
          id: `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          filename: file.name,
          category,
          file_path: '',
          upload_date: new Date().toISOString(),
          file_size: file.size,
          status: 'uploading'
        };
        
        setFiles(prev => [...prev, tempFile]);
        
        // Upload file via API
        const response = await apiService.uploadTrainingFile(file, category);
        
        if (response.success && response.data) {
          // Replace temp file with real file data
          setFiles(prev => prev.map(f => 
            f.id === tempFile.id ? response.data! : f
          ));
        } else {
          // Update temp file with error status
          setFiles(prev => prev.map(f => 
            f.id === tempFile.id 
              ? { ...f, status: 'error' as const }
              : f
          ));
          console.error(`Upload failed for ${file.name}:`, response.error);
        }
      } catch (error) {
        console.error(`Upload error for ${file.name}:`, error);
      }
    }
  };

  const handleFileDelete = async (fileId: string) => {
    try {
      const response = await apiService.deleteTrainingFile(fileId);
      
      if (response.success) {
        setFiles(prev => prev.filter(f => f.id !== fileId));
        console.log(`File deleted successfully: ${fileId}`);
      } else {
        console.error('Failed to delete file:', response.error);
      }
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  };

  const getCategoryStats = (category: FileCategory) => {
    const categoryFiles = files.filter(f => f.category === category);
    return {
      total: categoryFiles.length,
      ready: categoryFiles.filter(f => f.status === 'ready').length,
      processing: categoryFiles.filter(f => f.status === 'processing').length,
      error: categoryFiles.filter(f => f.status === 'error').length
    };
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Training Data Management</h1>
        <p className="text-gray-600">
          Upload and manage training data for StreamWorks-KI fine-tuning
        </p>
        
        {/* Navigation Tabs */}
        <div className="flex gap-2 mt-4">
          <button
            onClick={() => setActiveView('upload')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeView === 'upload'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📤 Upload & Training
          </button>
          <button
            onClick={() => setActiveView('manage')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeView === 'manage'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📋 Knowledge Base
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 space-y-6 overflow-auto">
        {activeView === 'upload' && (
          <>
            {/* Training Status Dashboard */}
            <TrainingStatus 
              helpDataStats={getCategoryStats('help_data')}
              streamTemplateStats={getCategoryStats('stream_templates')}
            />

            {/* Category Selector */}
            <CategorySelector 
              selectedCategory={selectedCategory}
              onCategoryChange={setSelectedCategory}
            />

            {/* Upload Zone */}
            <UploadZone 
              category={selectedCategory}
              onFilesUploaded={handleFileUpload}
            />

            {/* File Manager */}
            <FileManager 
              files={files}
              selectedCategory={selectedCategory}
              onFileDelete={handleFileDelete}
              onRefresh={loadFiles}
              isLoading={isLoading}
            />
          </>
        )}

        {activeView === 'manage' && (
          <DocumentManager 
            onRefresh={loadFiles}
          />
        )}
      </div>
    </div>
  );
};