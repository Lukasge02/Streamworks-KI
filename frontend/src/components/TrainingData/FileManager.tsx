import React, { useState } from 'react';
import { Trash2, RefreshCw, Filter, FileText, Clock, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { TrainingFile, FileCategory } from './TrainingDataTab';

interface FileManagerProps {
  files: TrainingFile[];
  selectedCategory: FileCategory;
  onFileDelete: (fileId: string) => void;
  onRefresh: () => void;
  isLoading: boolean;
}

export const FileManager: React.FC<FileManagerProps> = ({
  files,
  selectedCategory,
  onFileDelete,
  onRefresh,
  isLoading
}) => {
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // Filter files by category and status
  const filteredFiles = files.filter(file => {
    const categoryMatch = file.category === selectedCategory;
    const statusMatch = filterStatus === 'all' || file.status === filterStatus;
    return categoryMatch && statusMatch;
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading':
        return <Loader className="w-4 h-4 text-blue-600 animate-spin" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-600" />;
      case 'ready':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <FileText className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'uploading':
        return 'bg-blue-100 text-blue-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'ready':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const statusCounts = {
    all: filteredFiles.length,
    uploading: files.filter(f => f.category === selectedCategory && f.status === 'uploading').length,
    processing: files.filter(f => f.category === selectedCategory && f.status === 'processing').length,
    ready: files.filter(f => f.category === selectedCategory && f.status === 'ready').length,
    error: files.filter(f => f.category === selectedCategory && f.status === 'error').length,
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Datei-Manager
            {selectedCategory === 'help_data' ? ' - StreamWorks Hilfe' : ' - Stream Templates'}
          </h2>
          
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center space-x-2 px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Aktualisieren</span>
          </button>
        </div>

        {/* Status Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <div className="flex space-x-1">
            {[
              { key: 'all', label: 'Alle', count: statusCounts.all },
              { key: 'ready', label: 'Bereit', count: statusCounts.ready },
              { key: 'processing', label: 'Verarbeitung', count: statusCounts.processing },
              { key: 'uploading', label: 'Upload', count: statusCounts.uploading },
              { key: 'error', label: 'Fehler', count: statusCounts.error },
            ].map(({ key, label, count }) => (
              <button
                key={key}
                onClick={() => setFilterStatus(key)}
                className={`
                  px-3 py-1 text-sm rounded-full transition-colors
                  ${filterStatus === key
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                  }
                `}
              >
                {label} ({count})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* File List */}
      <div className="p-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader className="w-6 h-6 text-blue-600 animate-spin mr-2" />
            <span className="text-gray-600">Dateien werden geladen...</span>
          </div>
        ) : filteredFiles.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Keine Dateien gefunden</h3>
            <p className="text-gray-600">
              {filterStatus === 'all' 
                ? 'Laden Sie Dateien hoch, um hier zu beginnen.'
                : `Keine Dateien mit Status "${filterStatus}" gefunden.`
              }
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <div className="flex items-center space-x-4 flex-1">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(file.status)}
                    <FileText className="w-5 h-5 text-gray-500" />
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 truncate">
                      {file.filename}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                      <span>{formatFileSize(file.file_size)}</span>
                      <span>{formatDate(file.upload_date)}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`
                      px-2 py-1 text-xs font-medium rounded-full
                      ${getStatusColor(file.status)}
                    `}>
                      {file.status === 'uploading' && 'Upload läuft'}
                      {file.status === 'processing' && 'Verarbeitung'}
                      {file.status === 'ready' && 'Bereit'}
                      {file.status === 'error' && 'Fehler'}
                    </span>
                  </div>
                </div>
                
                <button
                  onClick={() => onFileDelete(file.id)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Datei löschen"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};