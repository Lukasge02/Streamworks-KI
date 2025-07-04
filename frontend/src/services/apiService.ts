import { ApiResponse, StreamConfig } from '../types';

export interface TrainingFile {
  id: string;
  filename: string;
  category: 'help_data' | 'stream_templates';
  file_path: string;
  upload_date: string;
  file_size: number;
  status: 'uploading' | 'processing' | 'ready' | 'error' | 'indexed';
  error_message?: string;
  // ChromaDB Integration
  is_indexed: boolean;
  indexed_at?: string;
  chunk_count: number;
  index_status?: string;
  index_error?: string;
}

export interface CategoryStats {
  total: number;
  ready: number;
  processing: number;
  error: number;
}

export interface TrainingStatus {
  help_data_stats: CategoryStats;
  stream_template_stats: CategoryStats;
  last_updated: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  source_path: string;
  chunks: number;
  total_size: number;
  upload_date?: string;
  status: string;
}

export interface DocumentsResponse {
  documents: DocumentInfo[];
  total_count: number;
  total_chunks: number;
}

export interface DocumentDetails {
  id: string;
  filename: string;
  chunks: number;
  preview: string;
  metadata: Record<string, any>;
}

export interface SearchResult {
  content: string;
  metadata: Record<string, any>;
  score?: number;
  source: string;
}

export interface SearchDocumentsResponse {
  query: string;
  results_count: number;
  results: SearchResult[];
}

class ApiService {
  private baseUrl = 'http://localhost:8000/api/v1';

  async sendMessage(message: string): Promise<ApiResponse<string>> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data: data.response };
    } catch (error) {
      console.error('API Error:', error);
      return { success: false, error: `API-Fehler: ${error}` };
    }
  }

  async sendDualModeMessage(
    message: string, 
    mode: 'qa' | 'xml_generator'
  ): Promise<{
    response: string;
    mode_used: string;
    processing_time: number;
    metadata: Record<string, any>;
    sources?: string[];
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/dual-mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message, 
          mode,
          session_id: 'current_session'
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Dual-Mode API Error:', error);
      throw new Error(`Dual-Mode Chat fehlgeschlagen: ${error}`);
    }
  }

  async generateStream(config: StreamConfig): Promise<ApiResponse<string>> {
    try {
      const response = await fetch(`${this.baseUrl}/streams/generate-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      
      const data = await response.json();
      return { success: true, data: data.xml };
    } catch (error) {
      return { success: false, error: 'Stream-Generierung fehlgeschlagen' };
    }
  }

  async uploadFile(file: File): Promise<ApiResponse<string>> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${this.baseUrl}/upload`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      return { success: true, data: data.analysis };
    } catch (error) {
      return { success: false, error: 'File-Upload fehlgeschlagen' };
    }
  }

  // Training Data API Methods
  async uploadTrainingFile(file: File, category: 'help_data' | 'stream_templates'): Promise<ApiResponse<TrainingFile>> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', category);
      
      const response = await fetch(`${this.baseUrl}/training/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Training file upload error:', error);
      return { success: false, error: `Training-Datei Upload fehlgeschlagen: ${error}` };
    }
  }

  async getTrainingFiles(category?: string, status?: string): Promise<ApiResponse<TrainingFile[]>> {
    try {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (status) params.append('status', status);
      
      const queryString = params.toString();
      const url = `${this.baseUrl}/training/files${queryString ? `?${queryString}` : ''}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Get training files error:', error);
      return { success: false, error: `Training-Dateien laden fehlgeschlagen: ${error}` };
    }
  }

  async deleteTrainingFile(fileId: string): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(`${this.baseUrl}/training/files/${fileId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return { success: true };
    } catch (error) {
      console.error('Delete training file error:', error);
      return { success: false, error: `Training-Datei löschen fehlgeschlagen: ${error}` };
    }
  }

  async getTrainingStatus(): Promise<ApiResponse<TrainingStatus>> {
    try {
      const response = await fetch(`${this.baseUrl}/training/status`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Get training status error:', error);
      return { success: false, error: `Training-Status laden fehlgeschlagen: ${error}` };
    }
  }

  async processTrainingFile(fileId: string): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(`${this.baseUrl}/training/process/${fileId}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return { success: true };
    } catch (error) {
      console.error('Process training file error:', error);
      return { success: false, error: `Training-Datei verarbeiten fehlgeschlagen: ${error}` };
    }
  }

  // Document Management API Methods
  async getDocuments(): Promise<ApiResponse<DocumentsResponse>> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/documents`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Get documents error:', error);
      return { success: false, error: `Dokumente laden fehlgeschlagen: ${error}` };
    }
  }

  async getDocumentDetails(docId: string): Promise<ApiResponse<DocumentDetails>> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/documents/${encodeURIComponent(docId)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Get document details error:', error);
      return { success: false, error: `Dokument-Details laden fehlgeschlagen: ${error}` };
    }
  }

  async deleteDocument(docId: string): Promise<ApiResponse<{ success: boolean; message: string }>> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/documents/${encodeURIComponent(docId)}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Delete document error:', error);
      return { success: false, error: `Dokument löschen fehlgeschlagen: ${error}` };
    }
  }

  async searchDocuments(query: string, topK: number = 5): Promise<ApiResponse<SearchDocumentsResponse>> {
    try {
      const params = new URLSearchParams();
      params.append('query', query);
      params.append('top_k', topK.toString());
      
      const response = await fetch(`${this.baseUrl}/chat/documents/search?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Search documents error:', error);
      return { success: false, error: `Dokumente suchen fehlgeschlagen: ${error}` };
    }
  }

  async uploadDocuments(files: File[]): Promise<ApiResponse<{ message: string; documents_added: number; chunks_created: number }>> {
    try {
      const formData = new FormData();
      
      files.forEach(file => {
        formData.append('files', file);
      });
      
      const response = await fetch(`${this.baseUrl}/chat/upload-docs`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Upload documents error:', error);
      return { success: false, error: `Dokumente hochladen fehlgeschlagen: ${error}` };
    }
  }

  // ChromaDB Integration Methods
  async indexToChromaDB(fileId: string): Promise<ApiResponse<{ file_id: string; filename: string; chunk_count: number; indexed_at: string; status: string }>> {
    try {
      const response = await fetch(`${this.baseUrl}/training/index/${fileId}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Index to ChromaDB error:', error);
      return { success: false, error: `ChromaDB Indexierung fehlgeschlagen: ${error}` };
    }
  }

  async batchIndexToChromaDB(fileIds: string[]): Promise<ApiResponse<{ success: any[]; failed: any[]; not_found: string[] }>> {
    try {
      const response = await fetch(`${this.baseUrl}/training/index/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_ids: fileIds }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Batch index to ChromaDB error:', error);
      return { success: false, error: `Batch ChromaDB Indexierung fehlgeschlagen: ${error}` };
    }
  }

  async removeFromChromaDB(fileId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await fetch(`${this.baseUrl}/training/index/${fileId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Remove from ChromaDB error:', error);
      return { success: false, error: `ChromaDB Entfernung fehlgeschlagen: ${error}` };
    }
  }

  async getChromaDBStats(): Promise<ApiResponse<{
    indexed_files: number;
    total_chunks: number;
    collection_documents: number;
    by_category: { help_data: number; stream_templates: number };
    vector_db_path: string;
    embedding_model: string;
  }>> {
    try {
      const response = await fetch(`${this.baseUrl}/training/chromadb/stats`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Get ChromaDB stats error:', error);
      return { success: false, error: `ChromaDB Statistiken laden fehlgeschlagen: ${error}` };
    }
  }
}

export const apiService = new ApiService();