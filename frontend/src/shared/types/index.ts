/**
 * Comprehensive TypeScript definitions for StreamWorks-KI application
 */

/**
 * User interface representing an authenticated user
 */
export interface User {
  /** Unique identifier for the user */
  id: string;
  /** Display name of the user */
  name: string;
  /** Email address of the user */
  email: string;
  /** Role of the user in the system */
  role: 'admin' | 'user' | 'viewer';
  /** User preferences and settings */
  preferences: {
    theme: 'light' | 'dark' | 'system';
    language: 'de' | 'en';
    notifications: boolean;
    autoSave: boolean;
  };
}

/**
 * Document interface for file management system
 */
export interface Document {
  /** Unique identifier for the document */
  id: string;
  /** Original filename with extension */
  filename: string;
  /** File size in bytes */
  file_size: number;
  /** MIME type or file extension */
  file_type: string;
  /** Category name the document belongs to */
  category_name: string;
  /** Folder name within the category */
  folder_name: string | null;
  /** Upload timestamp */
  upload_date: string;
  /** Whether the document is indexed in ChromaDB */
  is_indexed: boolean;
  /** Current processing status */
  processing_status: ProcessingStatus;
  /** Error message if processing failed */
  error_message: string | null;
  /** Additional metadata */
  metadata?: Record<string, any>;
}

/**
 * Chat message interface for conversation system
 */
export interface ChatMessage {
  /** Unique identifier for the message */
  id: string;
  /** Message content */
  content: string;
  /** Whether the message is from the user (true) or assistant (false) */
  isUser: boolean;
  /** Message timestamp */
  timestamp: string;
  /** Source documents used for RAG responses */
  sources?: string[];
  /** Additional metadata for the message */
  metadata?: {
    processing_time?: number;
    model_used?: string;
    confidence?: number;
    mode?: 'chat' | 'rag' | 'hybrid';
  };
}

/**
 * Analytics data interface for dashboard metrics
 */
export interface AnalyticsData {
  /** Total number of queries processed */
  total_queries: number;
  /** Average response time in seconds */
  avg_response_time: number;
  /** Success rate as percentage (0-100) */
  success_rate: number;
  /** Most frequently asked queries */
  top_queries: Array<{
    query: string;
    count: number;
    avg_response_time: number;
  }>;
  /** Daily usage statistics */
  daily_usage: Array<{
    date: string;
    queries: number;
    avg_response_time: number;
    success_rate: number;
  }>;
  /** Document processing statistics */
  document_stats: {
    total_documents: number;
    processed_today: number;
    avg_processing_time: number;
    success_rate: number;
  };
}

/**
 * System health interface for monitoring
 */
export interface SystemHealth {
  /** Overall system status */
  status: 'healthy' | 'degraded' | 'unhealthy';
  /** Individual service statuses */
  services: {
    database: ServiceStatus;
    chromadb: ServiceStatus;
    mistral_llm: ServiceStatus;
    document_processor: ServiceStatus;
    api: ServiceStatus;
  };
  /** Application version */
  version: string;
  /** System uptime in seconds */
  uptime: number;
  /** Last health check timestamp */
  last_check: string;
}

/**
 * Service status interface
 */
export interface ServiceStatus {
  /** Service health status */
  status: 'healthy' | 'degraded' | 'unhealthy';
  /** Response time in milliseconds */
  response_time?: number;
  /** Last error message if any */
  last_error?: string;
  /** Service-specific metadata */
  metadata?: Record<string, any>;
}

/**
 * Category statistics interface
 */
export interface CategoryStats {
  /** Total documents in category */
  total: number;
  /** Documents ready for use */
  ready: number;
  /** Documents currently processing */
  processing: number;
  /** Documents with errors */
  error: number;
  /** Category metadata */
  metadata?: {
    last_updated: string;
    avg_processing_time: number;
  };
}

/**
 * XML template interface for generator
 */
export interface XMLTemplate {
  /** Unique identifier for the template */
  id: string;
  /** Template display name */
  name: string;
  /** Template description */
  description: string;
  /** XML template content */
  content: string;
  /** Template category */
  category: 'data-sync' | 'workflow' | 'integration' | 'custom';
  /** Template parameters */
  parameters: Array<{
    name: string;
    type: 'string' | 'number' | 'boolean' | 'select';
    required: boolean;
    default?: any;
    options?: string[];
    description?: string;
  }>;
  /** Creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
}

/**
 * Processing status union type
 */
export type ProcessingStatus = 
  | 'pending' 
  | 'processing' 
  | 'completed' 
  | 'failed' 
  | 'cancelled'
  | 'indexed'
  | 'ready';

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T = any> {
  /** Whether the request was successful */
  success: boolean;
  /** Response data */
  data: T;
  /** Human-readable message */
  message: string;
  /** Response timestamp */
  timestamp: string;
  /** Additional metadata */
  metadata?: Record<string, any>;
}

/**
 * API error response interface
 */
export interface ApiError {
  /** Error message */
  detail: string;
  /** HTTP status code */
  status_code: number;
  /** Error type classification */
  error_type: string;
  /** Error timestamp */
  timestamp: string;
  /** Additional error context */
  context?: Record<string, any>;
}

/**
 * File upload interface
 */
export interface FileUpload {
  /** File object */
  file: File;
  /** Upload progress (0-100) */
  progress: number;
  /** Upload status */
  status: 'pending' | 'uploading' | 'completed' | 'failed';
  /** Error message if upload failed */
  error?: string;
  /** Upload metadata */
  metadata?: {
    category?: string;
    folder?: string;
    description?: string;
  };
}

/**
 * Navigation item interface
 */
export interface NavigationItem {
  /** Unique identifier */
  id: string;
  /** Display label */
  label: string;
  /** Route path */
  path: string;
  /** Icon name (from lucide-react) */
  icon: string;
  /** Whether item is active */
  active?: boolean;
  /** Badge count for notifications */
  badge?: number;
  /** Child navigation items */
  children?: NavigationItem[];
}

/**
 * Theme configuration interface
 */
export interface ThemeConfig {
  /** Theme identifier */
  id: string;
  /** Theme display name */
  name: string;
  /** Color palette */
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    foreground: string;
    muted: string;
    border: string;
  };
  /** Whether it's a dark theme */
  dark: boolean;
}

/**
 * Notification interface
 */
export interface Notification {
  /** Unique identifier */
  id: string;
  /** Notification type */
  type: 'success' | 'error' | 'warning' | 'info';
  /** Notification title */
  title: string;
  /** Notification message */
  message?: string;
  /** Auto-dismiss duration in milliseconds */
  duration?: number;
  /** Whether notification can be dismissed */
  dismissible?: boolean;
  /** Additional actions */
  actions?: Array<{
    label: string;
    action: () => void;
  }>;
}

/**
 * Search result interface
 */
export interface SearchResult {
  /** Result identifier */
  id: string;
  /** Result title */
  title: string;
  /** Result snippet */
  snippet: string;
  /** Result type */
  type: 'document' | 'conversation' | 'template' | 'setting';
  /** Search score */
  score: number;
  /** Source metadata */
  source: {
    filename?: string;
    category?: string;
    path?: string;
  };
  /** Highlighted matches */
  highlights?: string[];
}

/**
 * Dashboard widget interface
 */
export interface DashboardWidget {
  /** Widget identifier */
  id: string;
  /** Widget title */
  title: string;
  /** Widget type */
  type: 'metric' | 'chart' | 'list' | 'table' | 'custom';
  /** Widget size */
  size: 'small' | 'medium' | 'large' | 'full';
  /** Widget position */
  position: {
    row: number;
    col: number;
    width: number;
    height: number;
  };
  /** Widget data */
  data: any;
  /** Widget configuration */
  config?: Record<string, any>;
  /** Last update timestamp */
  lastUpdated: string;
}

/**
 * Legacy API types for backward compatibility
 */

// Q&A System Types
export interface QARequest {
  question: string;
}

export interface QAResponse {
  question: string;
  answer: string;
  sources: string[];
  processing_time: number;
  confidence: number;
  documents_analyzed: number;
  embedding_time: number;
  retrieval_time: number;
  generation_time: number;
  quality_score: number;
  language_detected: string;
  question_type: string;
  response_format: string;
}

// Chat Types
export interface ChatMessageRequest {
  message: string;
  conversation_id?: string;
  mode?: 'chat' | 'rag' | 'hybrid';
  context_window?: number;
}

export interface ChatMessageResponse {
  response: string;
  conversation_id: string;
  message_id: string;
  sources: string[];
  mode_used: string;
  processing_time: number;
  metadata: Record<string, any>;
}

// Document Types
export interface DocumentUploadResponse {
  success: boolean;
  message: string;
  document_id: string;
  original_filename: string;
  output_path: string;
  processing_time: number;
  pages_processed: number;
  file_size: number;
}

// XML Generation Types
export interface XMLChatRequest {
  prompt: string;
  context?: string;
  template_id?: string;
}

export interface XMLFormRequest {
  streamName: string;
  description?: string;
  sourceSystem: string;
  targetSystem: string;
  dataFormat?: 'JSON' | 'XML' | 'CSV' | 'XLSX';
  schedule?: 'realtime' | 'hourly' | 'daily' | 'weekly';
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface XMLGenerationResponse {
  xml: string;
  validation: ValidationResult;
  metadata: Record<string, any>;
}

// Analytics Types
export interface DocumentProcessingAnalytics {
  total_documents: number;
  avg_processing_time: number;
  max_processing_time: number;
  min_processing_time: number;
  success_rate: number;
  total_processing_hours: number;
  documents_per_hour: number;
  file_type_breakdown: Record<string, number>;
  performance_trends: Array<{
    date: string;
    documents_count: number;
    avg_processing_time: number;
    success_rate: number;
  }>;
}

export interface SystemMetrics {
  cpu_performance: {
    avg_pages_per_conversion: number;
    avg_processing_time: number;
    peak_processing_time: number;
    min_processing_time: number;
    cpu_efficiency_score: number;
  };
  memory_usage: {
    avg_file_size_mb: number;
    max_file_size_mb: number;
    total_data_processed_gb: number;
    memory_efficiency_score: number;
  };
  database_performance: {
    total_database_operations: number;
    avg_query_time_ms: number;
    database_health_score: number;
    connection_pool_efficiency: number;
  };
  error_analysis: {
    total_errors: number;
    unique_error_types: number;
    error_rate: number;
    most_common_errors: string[];
  };
  system_health_score: number;
  uptime_statistics: {
    system_uptime_days: number;
    active_processing_days: number;
    uptime_percentage: number;
    first_activity: string;
    last_activity: string;
  };
}

// Training Data Types
export interface TrainingFile {
  id: string;
  filename: string;
  category: string;
  file_path: string;
  file_size: number;
  upload_date: string;
  status: string;
  processing_time?: number;
  chromadb_indexed: boolean;
  chunk_count?: number;
  error_message?: string;
}

// All types are already exported above with their interface declarations