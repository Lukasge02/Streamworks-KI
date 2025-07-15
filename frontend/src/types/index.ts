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

export type TabType = 'chat' | 'training' | 'chunks';

export type MessageType = 'text' | 'code' | 'xml';

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

// ChromaDB Chunks Types
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