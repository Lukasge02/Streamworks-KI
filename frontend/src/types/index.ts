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

export type TabType = 'chat' | 'training' | 'xml' | 'settings';

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
}