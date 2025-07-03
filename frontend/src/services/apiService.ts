import { ApiResponse, StreamConfig } from '../types';

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
}

export const apiService = new ApiService();