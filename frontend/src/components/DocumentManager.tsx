import React, { useState, useEffect } from 'react';
import { apiService, DocumentInfo, DocumentDetails, SearchResult } from '../services/apiService';

interface DocumentManagerProps {
  onRefresh?: () => void;
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({ onRefresh }) => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<DocumentDetails | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.getDocuments();
      
      if (response.success) {
        setDocuments(response.data.documents);
      } else {
        setError(response.error || 'Fehler beim Laden der Dokumente');
      }
    } catch (err) {
      setError('Unerwarteter Fehler beim Laden der Dokumente');
      console.error('Error loading documents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (docId: string, filename: string) => {
    if (!confirm(`Dokument "${filename}" wirklich löschen?\n\nDies entfernt alle Chunks aus der Knowledge Base.`)) {
      return;
    }

    try {
      const response = await apiService.deleteDocument(docId);
      
      if (response.success) {
        await loadDocuments(); // Reload list
        onRefresh?.(); // Notify parent component
      } else {
        setError(response.error || 'Fehler beim Löschen des Dokuments');
      }
    } catch (err) {
      setError('Unerwarteter Fehler beim Löschen des Dokuments');
      console.error('Error deleting document:', err);
    }
  };

  const handleSearchDocuments = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      setShowSearch(false);
      return;
    }

    try {
      setSearching(true);
      setError(null);
      
      const response = await apiService.searchDocuments(query, 5);
      
      if (response.success) {
        setSearchResults(response.data.results);
        setShowSearch(true);
      } else {
        setError(response.error || 'Fehler bei der Suche');
      }
    } catch (err) {
      setError('Unerwarteter Fehler bei der Suche');
      console.error('Error searching documents:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleViewDocument = async (docId: string) => {
    try {
      const response = await apiService.getDocumentDetails(docId);
      
      if (response.success) {
        setSelectedDocument(response.data);
        setShowDetails(true);
      } else {
        setError(response.error || 'Fehler beim Laden der Dokument-Details');
      }
    } catch (err) {
      setError('Unerwarteter Fehler beim Laden der Dokument-Details');
      console.error('Error loading document details:', err);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    if (!dateString || dateString === 'unknown') return 'Unbekannt';
    try {
      return new Date(dateString).toLocaleDateString('de-DE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Unbekannt';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'indexed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string): string => {
    switch (status) {
      case 'indexed':
        return 'Indexiert';
      case 'processing':
        return 'Verarbeitung';
      case 'error':
        return 'Fehler';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2">Lade Dokumente...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">📋 Knowledge Base</h2>
          <p className="text-gray-600">
            {documents.length} Dokumente • {documents.reduce((sum, doc) => sum + doc.chunks, 0)} Chunks
          </p>
        </div>
        <button
          onClick={loadDocuments}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
        >
          🔄 Aktualisieren
        </button>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg border p-4">
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            placeholder="Dokumente durchsuchen..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearchDocuments(searchQuery)}
            className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => handleSearchDocuments(searchQuery)}
            disabled={searching}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
          >
            {searching ? '🔍 Suchen...' : '🔍 Suchen'}
          </button>
          {showSearch && (
            <button
              onClick={() => {
                setShowSearch(false);
                setSearchResults([]);
                setSearchQuery('');
              }}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
            >
              ❌ Schließen
            </button>
          )}
        </div>

        {/* Search Results */}
        {showSearch && (
          <div className="border-t pt-4">
            <h3 className="font-semibold mb-2">
              Suchergebnisse für "{searchQuery}" ({searchResults.length} Treffer)
            </h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {searchResults.map((result, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded border">
                  <div className="text-sm font-medium text-gray-700 mb-1">
                    📄 {result.source}
                  </div>
                  <div className="text-sm text-gray-600">
                    {result.content}
                  </div>
                  {result.score && (
                    <div className="text-xs text-gray-500 mt-1">
                      Relevanz: {(result.score * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Fehler</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Documents List */}
      <div className="bg-white rounded-lg border">
        {documents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-4">📭</div>
            <p>Noch keine Dokumente in der Knowledge Base.</p>
            <p className="text-sm mt-2">Lade Dokumente über den "Upload" Tab hoch.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-900">{doc.filename}</h3>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600 mt-1">
                      <span>📄 {doc.chunks} Chunks</span>
                      <span>💾 {formatFileSize(doc.total_size)}</span>
                      <span>📅 {formatDate(doc.upload_date || '')}</span>
                      <span className={`px-2 py-1 rounded text-xs ${getStatusColor(doc.status)}`}>
                        {getStatusText(doc.status)}
                      </span>
                    </div>
                    {doc.source_path && (
                      <div className="text-xs text-gray-500 mt-1 font-mono">
                        {doc.source_path}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleViewDocument(doc.id)}
                      className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                    >
                      👁️ Details
                    </button>
                    <button
                      onClick={() => handleDeleteDocument(doc.id, doc.filename)}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                    >
                      🗑️ Löschen
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Document Details Modal */}
      {showDetails && selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-bold">📄 {selectedDocument.filename}</h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ❌
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-700">Informationen</h4>
                  <div className="text-sm text-gray-600 mt-1">
                    <p>🆔 ID: {selectedDocument.id}</p>
                    <p>📄 Chunks: {selectedDocument.chunks}</p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-700">Vorschau</h4>
                  <div className="bg-gray-50 p-3 rounded border mt-1">
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                      {selectedDocument.preview}
                    </pre>
                  </div>
                </div>

                {Object.keys(selectedDocument.metadata).length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-700">Metadaten</h4>
                    <div className="bg-gray-50 p-3 rounded border mt-1">
                      <pre className="text-sm text-gray-700">
                        {JSON.stringify(selectedDocument.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowDetails(false)}
                  className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                >
                  Schließen
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};