export const API_BASE_URL = 'http://localhost:8000/api/v1';

export const API_ENDPOINTS = {
  // Q&A System
  QA_ASK: '/qa/ask',
  QA_HEALTH: '/qa/health',
  QA_STATS: '/qa/stats',
  
  // Document Management
  DOCUMENTS_UPLOAD: '/documents/upload',
  DOCUMENTS_BATCH_CONVERT: '/documents/batch-convert',
  DOCUMENTS_CONVERSION_STATS: '/documents/conversion-stats',
  
  // Analytics
  ANALYTICS_DOCUMENT_PROCESSING: '/analytics/document-processing',
  ANALYTICS_BATCH_STATISTICS: '/analytics/batch-statistics',
  ANALYTICS_SYSTEM_METRICS: '/analytics/system-metrics',
  ANALYTICS_EXPORT_CSV: '/analytics/export/csv',
  
  // Categories & Folders
  CATEGORIES: '/categories',
  SIMPLE_FOLDERS: '/simple-folders',
  
  // Training Data
  TRAINING_UPLOAD: '/training/upload',
  TRAINING_UPLOAD_BATCH: '/training/upload-batch',
  TRAINING_FILES: '/training/files',
  TRAINING_FORMATS_SUPPORTED: '/training/formats/supported',
  TRAINING_ANALYZE_FILE: '/training/analyze-file',
  
  // XML Generation
  XML_GENERATE_FROM_CHAT: '/xml/generate-from-chat',
  XML_GENERATE_FROM_FORM: '/xml/generate-from-form',
  XML_GENERATE_FROM_TEMPLATE: '/xml/generate-from-template',
  XML_VALIDATE: '/xml/validate',
  XML_TEMPLATES: '/xml/templates',
  
  // Chat
  CHAT: '/chat/',
  CHAT_CONVERSATIONS: '/chat/conversations',
  CHAT_HEALTH: '/chat/health',
} as const;