import { ApiResponse, StreamConfig } from '../types';

export interface TrainingFile {
  id: string;
  filename: string;
  category: 'help_data' | 'stream_templates';
  file_path: string;
  upload_date: string;
  file_size: number;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  error_message?: string;
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
}

export const apiService = new ApiService();