import React, { useState, useEffect } from 'react';
import { X, FileText, Download, Database, Clock } from 'lucide-react';
import { apiService, TrainingFile } from '../../services/apiService';

interface DocumentPreviewProps {
  file: TrainingFile;
  onClose: () => void;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({ file, onClose }) => {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFileContent();
  }, [file.id]);

  const loadFileContent = async () => {
    try {
      setLoading(true);
      // This would need a new endpoint to get file content
      // For now, we'll show file metadata
      const metadata = `
Dateiname: ${file.filename}
Kategorie: ${file.category}
Größe: ${formatFileSize(file.file_size)}
Upload: ${new Date(file.upload_date).toLocaleString('de-DE')}
Status: ${file.status}

ChromaDB Information:
- Indexiert: ${file.is_indexed ? 'Ja' : 'Nein'}
- Chunks: ${file.chunk_count}
- Index Status: ${file.index_status || 'N/A'}
${file.indexed_at ? `- Indexiert am: ${new Date(file.indexed_at).toLocaleString('de-DE')}` : ''}
${file.index_error ? `- Fehler: ${file.index_error}` : ''}
      `;
      setContent(metadata);
    } catch (error) {
      console.error('Error loading file content:', error);
      setContent('Fehler beim Laden der Datei-Inhalte');
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-3">
            <FileText className="h-6 w-6 text-gray-600" />
            <h3 className="text-lg font-semibold">{file.filename}</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <pre className="whitespace-pre-wrap font-mono text-sm bg-gray-50 p-4 rounded-lg">
              {content}
            </pre>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t bg-gray-50">
          <div className="flex items-center gap-4 text-sm text-gray-600">
            {file.is_indexed && (
              <div className="flex items-center gap-1">
                <Database className="h-4 w-4" />
                <span>{file.chunk_count} Chunks</span>
              </div>
            )}
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              <span>{new Date(file.upload_date).toLocaleDateString('de-DE')}</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Schließen
          </button>
        </div>
      </div>
    </div>
  );
};