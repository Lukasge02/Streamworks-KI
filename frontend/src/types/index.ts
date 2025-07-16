export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  type?: MessageType;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export type TabType = 'chat' | 'training' | 'chunks' | 'analytics' | 'xml' | 'settings';

export type MessageType = 'text' | 'code' | 'xml';

export type FileCategory = 'help_data' | 'stream_templates' | 'qa_docs' | 'stream-xml' | 'streamworks-api';

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
  // Enterprise enhancements
  processing_status?: 'uploaded' | 'processing' | 'indexed' | 'error';
  quality_score?: number;
  semantic_density?: number;
  readability_score?: number;
  chunk_quality_distribution?: Record<string, number>;
  reindex_count?: number;
  last_reindex_at?: string;
}

// Enterprise Chunk Types
export interface ChunkMetadata {
  chunk_id?: number;
  chunk_index?: number;
  content_type?: string;
  file_path?: string;
  file_type?: string;
  filename?: string;
  page?: number;
  section?: string;
  source?: string;
  timestamp?: string;
  total_chunks?: number;
  // Enterprise chunk metadata
  quality_score?: number;
  semantic_density?: number;
  readability_score?: number;
  chunk_type?: string;
  strategy_used?: string;
  quality_assessment?: string;
  key_concepts?: string;
  entities?: string;
  start_char?: number;
  end_char?: number;
  content_hash?: string;
  [key: string]: any;
}

export interface Chunk {
  id: string;
  content: string;
  metadata: ChunkMetadata;
  embedding?: number[];
  score?: number;
}

export interface ChunksListResponse {
  chunks: Chunk[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface ChunkDetailsResponse {
  chunk: Chunk;
  similar_chunks: Chunk[];
  statistics: {
    content_length: number;
    word_count: number;
    unique_words: number;
    metadata_keys: string[];
  };
}

export interface ChunksStatisticsResponse {
  total_chunks: number;
  total_documents: number;
  chunk_size_avg: number;
  chunk_size_min: number;
  chunk_size_max: number;
  metadata_keys: string[];
  source_distribution: Record<string, number>;
  file_type_distribution: Record<string, number>;
  creation_timeline: Array<{
    date: string;
    count: number;
  }>;
}

// Enterprise Analytics Types
export interface FileAnalytics {
  file_info: {
    id: string;
    filename: string;
    category: string;
    folder?: string;
    chunk_count: number;
    processing_status: string;
    created_at: string;
    last_indexed_at?: string;
  };
  chunks: Array<{
    index: number;
    content: string;
    content_length: number;
    quality_score: number;
    semantic_density: number;
    readability_score: number;
    chunk_type: string;
    strategy_used: string;
    quality_assessment: string;
    key_concepts: string[];
    entities: string[];
    metadata: ChunkMetadata;
  }>;
  statistics: {
    total_chunks: number;
    average_length: number;
    average_quality: number;
    chunk_types: Record<string, number>;
    strategies_used: Record<string, number>;
    quality_distribution: Record<string, number>;
  };
  visualization_data: {
    chunk_timeline: Array<{
      index: number;
      start_char: number;
      end_char: number;
      length: number;
      quality: number;
      type: string;
    }>;
    quality_heatmap: Array<{
      index: number;
      quality_score: number;
      semantic_density: number;
      readability_score: number;
    }>;
  };
}

export interface SystemOverview {
  overview: {
    total_files: number;
    total_chunks: number;
    indexed_files: number;
    pending_files: number;
    failed_files: number;
    categories: Record<string, { files: number; chunks: number; slug: string }>;
    folders: Record<string, { files: number; chunks: number; slug?: string }>;
  };
  recent_files: Array<{
    id: string;
    filename: string;
    category: string;
    folder?: string;
    chunks: number;
    status: string;
    indexed_at?: string;
  }>;
  system_health: {
    status: 'excellent' | 'good' | 'fair' | 'poor' | 'no_data';
    success_rate: number;
    indexed_files: number;
    total_files: number;
    failed_files: number;
  };
}

export interface QualityAnalysis {
  quality_metrics: {
    total_chunks: number;
    average_quality: number;
    quality_range: {
      min: number;
      max: number;
    };
    quality_buckets: {
      excellent: number;
      good: number;
      acceptable: number;
      poor: number;
    };
  };
  recommendations: string[];
  chunk_distribution: {
    size_distribution: {
      small: number;
      medium: number;
      large: number;
    };
    average_size: number;
    size_range: {
      min: number;
      max: number;
    };
  };
}