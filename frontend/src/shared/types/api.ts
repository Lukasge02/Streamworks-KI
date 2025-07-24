/**
 * Legacy API types - kept for backward compatibility
 * New types should be added to ./index.ts
 */

// Re-export from main types file for backward compatibility
export type {
  QARequest,
  QAResponse,
  ChatMessageRequest,
  ChatMessageResponse,
  DocumentUploadResponse,
  XMLChatRequest,
  XMLFormRequest,
  ValidationResult,
  XMLGenerationResponse,
  DocumentProcessingAnalytics,
  SystemMetrics,
  TrainingFile,
  ApiError,
  ApiResponse,
} from './index';