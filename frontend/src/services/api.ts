/**
 * Comprehensive API Service Layer for StreamWorks-KI
 * Provides type-safe methods for all backend interactions
 */

import io, { Socket } from 'socket.io-client';
import type {
  ApiResponse,
  PaginatedResponse,
  ChatMessage,
  ChatRequest,
  StreamingChatResponse,
  Conversation,
  Document,
  DocumentUploadProgress,
  BulkOperationRequest,
  BulkOperationResponse,
  SystemMetrics,
  UsageAnalytics,
  AnalyticsFilter,
  TrainingData,
  TrainingUploadRequest,
  IndexingStatus,
  XmlTemplate,
  XmlGenerationRequest,
  XmlValidationResult,
  SystemStatus,
  HealthCheck,
  User,
  AuthTokens,
  ExportRequest,
  ExportResponse,
  WebSocketMessage,
} from '../types/api';

// API Configuration
const API_CONFIG = {
  BASE_URL: import.meta.env['VITE_API_BASE_URL'] || 'http://localhost:8000/api/v1',
  WS_URL: import.meta.env['VITE_WS_URL'] || 'ws://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

// Request interceptor type
type RequestInterceptor = (config: RequestInit) => RequestInit | Promise<RequestInit>;
type ResponseInterceptor = (response: Response) => Response | Promise<Response>;

/**
 * Enhanced HTTP client with retry logic and offline detection
 */
class HttpClient {
  private baseURL: string;
  private defaultHeaders: HeadersInit;
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  addRequestInterceptor(interceptor: RequestInterceptor): void {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor: ResponseInterceptor): void {
    this.responseInterceptors.push(interceptor);
  }

  private async applyRequestInterceptors(config: RequestInit): Promise<RequestInit> {
    let processedConfig = { ...config };
    for (const interceptor of this.requestInterceptors) {
      processedConfig = await interceptor(processedConfig);
    }
    return processedConfig;
  }

  private async applyResponseInterceptors(response: Response): Promise<Response> {
    let processedResponse = response;
    for (const interceptor of this.responseInterceptors) {
      processedResponse = await interceptor(processedResponse);
    }
    return processedResponse;
  }

  private async retryRequest<T>(
    url: string,
    config: RequestInit,
    attempt: number = 1
  ): Promise<T> {
    try {
      const processedConfig = await this.applyRequestInterceptors({
        ...config,
        headers: { ...this.defaultHeaders, ...config.headers },
      });

      const response = await fetch(`${this.baseURL}${url}`, processedConfig);
      const processedResponse = await this.applyResponseInterceptors(response);

      if (!processedResponse.ok) {
        throw new Error(`HTTP ${processedResponse.status}: ${processedResponse.statusText}`);
      }

      const data = await processedResponse.json();
      return data;
    } catch (error) {
      if (attempt < API_CONFIG.RETRY_ATTEMPTS) {
        await new Promise(resolve => setTimeout(resolve, API_CONFIG.RETRY_DELAY * attempt));
        return this.retryRequest<T>(url, config, attempt + 1);
      }
      throw error;
    }
  }

  async get<T>(url: string, config?: RequestInit): Promise<T> {
    return this.retryRequest<T>(url, { method: 'GET', ...config });
  }

  async post<T>(url: string, data?: any, config?: RequestInit): Promise<T> {
    return this.retryRequest<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      ...config,
    });
  }

  async put<T>(url: string, data?: any, config?: RequestInit): Promise<T> {
    return this.retryRequest<T>(url, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
      ...config,
    });
  }

  async delete<T>(url: string, config?: RequestInit): Promise<T> {
    return this.retryRequest<T>(url, { method: 'DELETE', ...config });
  }

  async upload<T>(url: string, formData: FormData, config?: RequestInit): Promise<T> {
    const uploadConfig = {
      method: 'POST',
      body: formData,
      ...config,
      headers: {
        // Don't set Content-Type for FormData, let browser set it
        ...config?.headers,
      },
    };
    
    // Remove Content-Type from default headers for uploads
    const { 'Content-Type': _, ...headersWithoutContentType } = this.defaultHeaders as any;
    this.defaultHeaders = headersWithoutContentType;
    
    try {
      return await this.retryRequest<T>(url, uploadConfig);
    } finally {
      // Restore Content-Type
      this.defaultHeaders = { 'Content-Type': 'application/json', ...headersWithoutContentType };
    }
  }
}

/**
 * Main API service class with all StreamWorks-KI endpoints
 */
export class StreamWorksAPI {
  private http: HttpClient;
  private socket: Socket | null = null;
  private authToken: string | null = null;

  constructor() {
    this.http = new HttpClient(API_CONFIG.BASE_URL);
    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Add auth token to requests
    this.http.addRequestInterceptor((config) => {
      if (this.authToken) {
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${this.authToken}`,
        };
      }
      return config;
    });

    // Handle auth errors
    this.http.addResponseInterceptor(async (response) => {
      if (response.status === 401) {
        this.clearAuth();
        // Emit auth error event
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      }
      return response;
    });
  }

  // Authentication Methods
  setAuthToken(token: string): void {
    this.authToken = token;
  }

  clearAuth(): void {
    this.authToken = null;
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Chat & RAG Methods
  async sendMessage(request: ChatRequest): Promise<ApiResponse<ChatMessage>> {
    return this.http.post('/chat/message', request);
  }

  async getChatHistory(conversationId?: string, page = 1, pageSize = 50): Promise<PaginatedResponse<ChatMessage>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...(conversationId && { conversation_id: conversationId }),
    });
    return this.http.get(`/chat/history?${params}`);
  }

  async getConversations(page = 1, pageSize = 20): Promise<PaginatedResponse<Conversation>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    return this.http.get(`/chat/conversations?${params}`);
  }

  async createConversation(title: string): Promise<ApiResponse<Conversation>> {
    return this.http.post('/chat/conversations', { title });
  }

  async deleteConversation(conversationId: string): Promise<ApiResponse<void>> {
    return this.http.delete(`/chat/conversations/${conversationId}`);
  }

  async exportConversation(conversationId: string, format: 'json' | 'txt' | 'pdf' = 'json'): Promise<ApiResponse<ExportResponse>> {
    return this.http.post('/chat/export', { conversation_id: conversationId, format });
  }

  // Document Management Methods
  async uploadDocument(file: File, onProgress?: (progress: DocumentUploadProgress) => void): Promise<ApiResponse<Document>> {
    const formData = new FormData();
    formData.append('file', file);

    // If progress callback provided, use XMLHttpRequest for upload progress
    if (onProgress) {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const progress = (event.loaded / event.total) * 100;
            onProgress({
              file_id: file.name,
              filename: file.name,
              progress,
              status: 'uploading',
            });
          }
        };

        xhr.onload = () => {
          if (xhr.status === 200) {
            resolve(JSON.parse(xhr.responseText));
          } else {
            reject(new Error(`Upload failed: ${xhr.statusText}`));
          }
        };

        xhr.onerror = () => reject(new Error('Upload failed'));
        
        xhr.open('POST', `${API_CONFIG.BASE_URL}/documents/upload`);
        if (this.authToken) {
          xhr.setRequestHeader('Authorization', `Bearer ${this.authToken}`);
        }
        xhr.send(formData);
      });
    }

    return this.http.upload('/documents/upload', formData);
  }

  async getDocuments(page = 1, pageSize = 20, search?: string): Promise<PaginatedResponse<Document>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...(search && { search }),
    });
    return this.http.get(`/documents?${params}`);
  }

  async getDocument(documentId: string): Promise<ApiResponse<Document>> {
    return this.http.get(`/documents/${documentId}`);
  }

  async deleteDocument(documentId: string): Promise<ApiResponse<void>> {
    return this.http.delete(`/documents/${documentId}`);
  }

  async bulkDocumentOperation(request: BulkOperationRequest): Promise<ApiResponse<BulkOperationResponse>> {
    return this.http.post('/documents/bulk', request);
  }

  async reprocessDocument(documentId: string): Promise<ApiResponse<void>> {
    return this.http.post(`/documents/${documentId}/reprocess`);
  }

  // Analytics Methods
  async getSystemMetrics(): Promise<ApiResponse<SystemMetrics>> {
    return this.http.get('/analytics/metrics');
  }

  async getUsageAnalytics(filter?: AnalyticsFilter): Promise<ApiResponse<UsageAnalytics>> {
    const params = new URLSearchParams();
    if (filter) {
      Object.entries(filter).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, Array.isArray(value) ? value.join(',') : value.toString());
        }
      });
    }
    return this.http.get(`/analytics/usage?${params}`);
  }

  async exportAnalytics(request: ExportRequest): Promise<ApiResponse<ExportResponse>> {
    return this.http.post('/analytics/export', request);
  }

  // Training Data Methods
  async getTrainingData(page = 1, pageSize = 50, category?: string): Promise<PaginatedResponse<TrainingData>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...(category && { category }),
    });
    return this.http.get(`/training/data?${params}`);
  }

  async uploadTrainingFile(request: TrainingUploadRequest): Promise<ApiResponse<{ imported: number; errors: string[] }>> {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('format', request.format);
    if (request.category) formData.append('category', request.category);
    if (request.overwrite_existing) formData.append('overwrite_existing', 'true');

    return this.http.upload('/training/upload', formData);
  }

  async reindexData(): Promise<ApiResponse<void>> {
    return this.http.post('/training/reindex');
  }

  async getIndexingStatus(): Promise<ApiResponse<IndexingStatus>> {
    return this.http.get('/training/status');
  }

  // XML Generator Methods
  async getXmlTemplates(category?: string): Promise<ApiResponse<XmlTemplate[]>> {
    const params = category ? new URLSearchParams({ category }) : '';
    return this.http.get(`/xml/templates?${params}`);
  }

  async getXmlTemplate(templateId: string): Promise<ApiResponse<XmlTemplate>> {
    return this.http.get(`/xml/templates/${templateId}`);
  }

  async generateXml(request: XmlGenerationRequest): Promise<ApiResponse<{ xml: string; variables_used: Record<string, any> }>> {
    return this.http.post('/xml/generate', request);
  }

  async validateXml(xml: string, schemaUrl?: string): Promise<ApiResponse<XmlValidationResult>> {
    return this.http.post('/xml/validate', { xml, schema_url: schemaUrl });
  }

  // System Health Methods
  async getSystemStatus(): Promise<ApiResponse<SystemStatus>> {
    return this.http.get('/health/system');
  }

  async getHealthCheck(service?: string): Promise<ApiResponse<HealthCheck | HealthCheck[]>> {
    const url = service ? `/health/${service}` : '/health';
    return this.http.get(url);
  }

  // WebSocket Methods
  connectWebSocket(userId?: string): Socket {
    if (this.socket?.connected) {
      return this.socket;
    }

    const wsUrl = `${API_CONFIG.WS_URL}${userId ? `?user_id=${userId}` : ''}`;
    this.socket = io(wsUrl, {
      transports: ['websocket'],
      auth: this.authToken ? { token: this.authToken } : undefined,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    return this.socket;
  }

  disconnectWebSocket(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Streaming Chat
  async streamChat(
    request: ChatRequest,
    onToken: (token: StreamingChatResponse) => void,
    onComplete: (response: ChatMessage) => void,
    onError: (error: Error) => void
  ): Promise<void> {
    const socket = this.connectWebSocket();
    
    const streamId = `stream_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    socket.emit('chat:stream:start', { ...request, stream_id: streamId });
    
    const tokenHandler = (data: StreamingChatResponse) => {
      if (data.is_complete) {
        socket.off(`chat:stream:token:${streamId}`, tokenHandler);
        socket.off(`chat:stream:complete:${streamId}`, completeHandler);
        socket.off(`chat:stream:error:${streamId}`, errorHandler);
      } else {
        onToken(data);
      }
    };
    
    const completeHandler = (data: ChatMessage) => {
      socket.off(`chat:stream:token:${streamId}`, tokenHandler);
      socket.off(`chat:stream:complete:${streamId}`, completeHandler);
      socket.off(`chat:stream:error:${streamId}`, errorHandler);
      onComplete(data);
    };
    
    const errorHandler = (error: any) => {
      socket.off(`chat:stream:token:${streamId}`, tokenHandler);
      socket.off(`chat:stream:complete:${streamId}`, completeHandler);
      socket.off(`chat:stream:error:${streamId}`, errorHandler);
      onError(new Error(error.message || 'Streaming error'));
    };
    
    socket.on(`chat:stream:token:${streamId}`, tokenHandler);
    socket.on(`chat:stream:complete:${streamId}`, completeHandler);
    socket.on(`chat:stream:error:${streamId}`, errorHandler);
  }

  // Real-time subscriptions
  subscribeToSystemAlerts(callback: (alert: any) => void): () => void {
    const socket = this.connectWebSocket();
    socket.on('system:alert', callback);
    return () => socket.off('system:alert', callback);
  }

  subscribeToDocumentProcessing(callback: (update: DocumentUploadProgress) => void): () => void {
    const socket = this.connectWebSocket();
    socket.on('document:processing', callback);
    return () => socket.off('document:processing', callback);
  }

  subscribeToIndexingStatus(callback: (status: IndexingStatus) => void): () => void {
    const socket = this.connectWebSocket();
    socket.on('training:indexing', callback);
    return () => socket.off('training:indexing', callback);
  }
}

// Export singleton instance
export const streamWorksAPI = new StreamWorksAPI();

// Export for testing
export { HttpClient };