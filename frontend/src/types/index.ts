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

export type TabType = 'chat' | 'generator' | 'docs' | 'training';