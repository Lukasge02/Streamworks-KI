export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  type?: 'text' | 'xml' | 'code';
}

export interface StreamConfig {
  streamName: string;
  jobName: string;
  startTime: string;
  dataSource: string;
  outputPath: string;
  schedule: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export type TabType = 'chat' | 'generator' | 'docs' | 'training' | 'search';

export type FileCategory = 'help_data' | 'stream_templates';

export interface TrainingFile {
  id: string;
  filename: string;
  display_name?: string;
  category: FileCategory;
  file_path: string;
  upload_date: string;
  file_size: number;
  status: 'uploading' | 'processing' | 'ready' | 'error' | 'indexed';
  error_message?: string;
  is_indexed: boolean;
  indexed_at?: string;
  chunk_count: number;
  index_status?: string;
  index_error?: string;
}

// Smart Search Types
export interface SmartSearchRequest {
  query: string;
  top_k?: number;
  include_analysis?: boolean;
}

export interface SearchFilter {
  document_types?: string[];
  file_formats?: string[];
  chunk_types?: string[];
  source_categories?: string[];
  processing_methods?: string[];
  complexity_min?: number;
  complexity_max?: number;
}

export interface AdvancedSearchRequest {
  query: string;
  top_k?: number;
  filters?: SearchFilter;
  include_analysis?: boolean;
}

export interface QueryAnalysis {
  primary_intent: string;
  confidence: number;
  complexity_level: number;
  search_strategy: string;
  preferred_doc_types: string[];
  enhancement_suggestions: string[];
  detected_entities: string[];
  query_categories: string[];
}

export interface SearchResult {
  content: string;
  metadata: {
    filename: string;
    source_type: string;
    chunk_type: string;
    processing_method: string;
    complexity_score: number;
    relevance_score: number;
    [key: string]: any;
  };
  score: number;
  source: string;
  explanation?: string;
}

export interface SmartSearchResponse {
  query: string;
  total_results: number;
  results: SearchResult[];
  search_strategy_used: string;
  response_time_ms: number;
  query_analysis?: QueryAnalysis;
  filter_applied?: SearchFilter;
  performance_metrics?: {
    strategy_selection_time: number;
    search_execution_time: number;
    result_processing_time: number;
  };
}

export interface FilterOptions {
  document_types: string[];
  file_formats: string[];
  chunk_types: string[];
  processing_methods: string[];
  source_categories: string[];
  complexity_range: {
    min: number;
    max: number;
    levels: {
      basic: string;
      intermediate: string;
      advanced: string;
    };
  };
}

export interface SearchStrategy {
  name: string;
  description: string;
  best_for: string[];
  performance: string;
}