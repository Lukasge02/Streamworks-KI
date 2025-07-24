/**
 * Comprehensive API Type Definitions for StreamWorks-KI
 * Matches backend schemas and provides type safety
 */

// Base API Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  error: string;
  detail?: string;
  status_code: number;
}

// Chat & RAG Types
export interface ChatMessage {
  id: string;
  conversation_id: string;
  message: string;
  response?: string;
  sources?: string[];
  processing_time?: number;
  timestamp: string;
  metadata?: {
    model?: string;
    temperature?: number;
    confidence?: number;
  };
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  tags?: string[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context_limit?: number;
  temperature?: number;
}

export interface StreamingChatResponse {
  token: string;
  is_complete: boolean;
  conversation_id: string;
  message_id: string;
  sources?: string[];
}

// Document Management Types
export interface Document {
  id: string;
  filename: string;
  original_name: string;
  file_size: number;
  mime_type: string;
  upload_date: string;
  processed: boolean;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  chunk_count?: number;
  metadata?: {
    author?: string;
    created_date?: string;
    language?: string;
    keywords?: string[];
  };
  error_message?: string;
}

export interface DocumentUploadProgress {
  file_id: string;
  filename: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

export interface BulkOperationRequest {
  operation: 'delete' | 'reprocess' | 'export';
  document_ids: string[];
}

export interface BulkOperationResponse {
  operation: string;
  processed: number;
  failed: number;
  errors?: string[];
}

// Analytics Types
export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_connections: number;
  requests_per_minute: number;
  error_rate: number;
  timestamp: string;
}

export interface UsageAnalytics {
  total_queries: number;
  avg_response_time: number;
  most_asked_topics: Array<{ topic: string; count: number }>;
  user_activity: Array<{ date: string; queries: number }>;
  document_usage: Array<{ document_id: string; filename: string; access_count: number }>;
  error_distribution: Array<{ error_type: string; count: number }>;
  period: {
    start_date: string;
    end_date: string;
  };
}

export interface AnalyticsFilter {
  start_date?: string;
  end_date?: string;
  user_id?: string;
  document_ids?: string[];
  query_types?: string[];
}

// Training Data Types
export interface TrainingData {
  id: string;
  question: string;
  answer: string;
  source_document?: string;
  category?: string;
  quality_score?: number;
  created_at: string;
  updated_at: string;
  validated: boolean;
  feedback_score?: number;
}

export interface TrainingUploadRequest {
  file: File;
  format: 'json' | 'csv' | 'xlsx';
  category?: string;
  overwrite_existing?: boolean;
}

export interface IndexingStatus {
  status: 'idle' | 'indexing' | 'completed' | 'error';
  progress: number;
  total_documents: number;
  processed_documents: number;
  current_document?: string;
  estimated_time_remaining?: number;
  error_message?: string;
}

// XML Generator Types
export interface XmlTemplate {
  id: string;
  name: string;
  description: string;
  category: 'basic' | 'advanced' | 'enterprise';
  schema_url?: string;
  template_content: string;
  variables: Array<{
    name: string;
    type: 'string' | 'number' | 'boolean' | 'array';
    required: boolean;
    description: string;
    default_value?: any;
  }>;
  created_at: string;
  updated_at: string;
}

export interface XmlGenerationRequest {
  template_id?: string;
  prompt?: string;
  variables?: Record<string, any>;
  output_format?: 'xml' | 'formatted';
  validate_schema?: boolean;
}

export interface XmlValidationResult {
  is_valid: boolean;
  errors: Array<{
    line: number;
    column: number;
    message: string;
    severity: 'error' | 'warning';
  }>;
  schema_validation?: {
    valid: boolean;
    errors: string[];
  };
}

// System Health Types
export interface HealthCheck {
  service: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  checks: Array<{
    name: string;
    status: 'pass' | 'fail' | 'warn';
    time: string;
    output?: string;
  }>;
  timestamp: string;
}

export interface SystemStatus {
  overall_status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    database: HealthCheck;
    rag_service: HealthCheck;
    vector_db: HealthCheck;
    llm_service: HealthCheck;
    file_storage: HealthCheck;
  };
  uptime: number;
  version: string;
  environment: string;
}

// User & Authentication Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
  created_at: string;
  last_login?: string;
  preferences: {
    theme: 'light' | 'dark' | 'system';
    language: 'en' | 'de';
    notifications: boolean;
    auto_save: boolean;
  };
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// WebSocket Types
export interface WebSocketMessage<T = any> {
  type: string;
  data: T;
  timestamp: string;
  id?: string;
}

export interface ChatStreamMessage extends WebSocketMessage<StreamingChatResponse> {
  type: 'chat_stream';
}

export interface SystemAlertMessage extends WebSocketMessage<SystemAlert> {
  type: 'system_alert';
}

export interface SystemAlert {
  id: string;
  level: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  component?: string;
  timestamp: string;
  acknowledged: boolean;
}

// Form Validation Types
export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// Export Types
export interface ExportRequest {
  format: 'json' | 'csv' | 'xlsx' | 'pdf';
  data_type: 'conversations' | 'documents' | 'analytics' | 'training_data';
  filters?: Record<string, any>;
  include_metadata?: boolean;
}

export interface ExportResponse {
  export_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  download_url?: string;
  expires_at?: string;
  file_size?: number;
  error_message?: string;
}