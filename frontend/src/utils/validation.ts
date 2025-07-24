/**
 * Validation utilities using Zod schemas
 */

import { z } from 'zod';

// Common validation schemas
export const emailSchema = z
  .string()
  .email('Please enter a valid email address')
  .min(1, 'Email is required');

export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters long')
  .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Password must contain at least one uppercase letter, one lowercase letter, and one number');

export const urlSchema = z
  .string()
  .url('Please enter a valid URL')
  .optional()
  .or(z.literal(''));

export const fileSchema = z
  .instanceof(File)
  .refine((file) => file.size <= 50 * 1024 * 1024, { message: 'File size must be less than 50MB' })
  .refine(
    (file) => ['application/pdf', 'text/plain', 'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/csv', 'application/json'].includes(file.type),
    { message: 'File type not supported' }
  );

// Chat validation schemas
export const chatMessageSchema = z.object({
  message: z
    .string()
    .min(1, 'Message cannot be empty')
    .max(4000, 'Message is too long (max 4000 characters)'),
  conversation_id: z.string().uuid().optional(),
  context_limit: z.number().min(1).max(50).optional(),
  temperature: z.number().min(0).max(2).optional(),
});

export const conversationSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(100, 'Title is too long (max 100 characters)'),
});

// Document validation schemas
export const documentFilterSchema = z.object({
  search: z.string().optional(),
  status: z.enum(['all', 'processed', 'processing', 'failed']).optional(),
  dateRange: z.object({
    start: z.string().datetime(),
    end: z.string().datetime(),
  }).optional(),
  fileType: z.array(z.string()).optional(),
});

export const bulkOperationSchema = z.object({
  operation: z.enum(['delete', 'reprocess', 'export']),
  document_ids: z.array(z.string().uuid()).min(1, 'At least one document must be selected'),
});

// Training data validation schemas
export const trainingUploadSchema = z.object({
  file: fileSchema,
  format: z.enum(['json', 'csv', 'xlsx']),
  category: z.string().max(50).optional(),
  overwrite_existing: z.boolean().optional(),
});

export const trainingDataSchema = z.object({
  question: z
    .string()
    .min(1, 'Question is required')
    .max(1000, 'Question is too long (max 1000 characters)'),
  answer: z
    .string()
    .min(1, 'Answer is required')
    .max(4000, 'Answer is too long (max 4000 characters)'),
  source_document: z.string().optional(),
  category: z.string().max(50).optional(),
  quality_score: z.number().min(0).max(10).optional(),
});

// XML validation schemas
export const xmlGenerationSchema = z.object({
  template_id: z.string().uuid().optional(),
  prompt: z.string().min(1, 'Prompt is required').optional(),
  variables: z.record(z.any()).optional(),
  output_format: z.enum(['xml', 'formatted']).optional(),
  validate_schema: z.boolean().optional(),
}).refine((data) => data.template_id || data.prompt, {
  message: 'Either template ID or prompt is required',
});

export const xmlValidationSchema = z.object({
  xml: z.string().min(1, 'XML content is required'),
  schema_url: urlSchema,
});

// Analytics validation schemas
export const analyticsFilterSchema = z.object({
  start_date: z.string().datetime().optional(),
  end_date: z.string().datetime().optional(),
  user_id: z.string().uuid().optional(),
  document_ids: z.array(z.string().uuid()).optional(),
  query_types: z.array(z.string()).optional(),
});

export const exportRequestSchema = z.object({
  format: z.enum(['json', 'csv', 'xlsx', 'pdf']),
  data_type: z.enum(['conversations', 'documents', 'analytics', 'training_data']),
  filters: z.record(z.any()).optional(),
  include_metadata: z.boolean().optional(),
});

// Form validation schemas
export const loginFormSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

export const registerFormSchema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters long')
    .max(50, 'Name is too long (max 50 characters)'),
  email: emailSchema,
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

export const profileUpdateSchema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters long')
    .max(50, 'Name is too long (max 50 characters)'),
  email: emailSchema,
  preferences: z.object({
    theme: z.enum(['light', 'dark', 'system']),
    language: z.enum(['en', 'de']),
    notifications: z.boolean(),
    auto_save: z.boolean(),
  }),
});

export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: passwordSchema,
  confirmNewPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmNewPassword, {
  message: "Passwords don't match",
  path: ['confirmNewPassword'],
});

// System settings validation schemas
export const systemSettingsSchema = z.object({
  api_base_url: urlSchema,
  websocket_url: urlSchema,
  max_file_size: z.number().min(1).max(100), // MB
  supported_file_types: z.array(z.string()),
  default_language: z.enum(['en', 'de']),
  auto_save_interval: z.number().min(30).max(3600), // seconds
});

// Validation helper functions
export function validateWithSchema<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; errors: Record<string, string> } {
  const result = schema.safeParse(data);
  
  if (result.success) {
    return { success: true, data: result.data };
  }
  
  const errors: Record<string, string> = {};
  result.error.issues.forEach((error: any) => {
    const path = error.path.join('.');
    errors[path] = error.message;
  });
  
  return { success: false, errors };
}

export function createFormValidator<T>(schema: z.ZodSchema<T>) {
  return (data: unknown) => validateWithSchema(schema, data);
}

// Custom validation functions
export function validateFileSize(file: File, maxSizeMB: number = 50): boolean {
  return file.size <= maxSizeMB * 1024 * 1024;
}

export function validateFileType(file: File, allowedTypes: string[]): boolean {
  return allowedTypes.includes(file.type);
}

export function validateDateRange(startDate: string, endDate: string): boolean {
  const start = new Date(startDate);
  const end = new Date(endDate);
  return start <= end;
}

export function validateXmlSyntax(xml: string): { valid: boolean; error?: string } {
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(xml, 'application/xml');
    
    const parseError = doc.getElementsByTagName('parsererror')[0];
    if (parseError) {
      return {
        valid: false,
        error: parseError.textContent || 'Invalid XML syntax',
      };
    }
    
    return { valid: true };
  } catch (error) {
    return {
      valid: false,
      error: error instanceof Error ? error.message : 'XML validation failed',
    };
  }
}

export function validateJsonSyntax(json: string): { valid: boolean; error?: string } {
  try {
    JSON.parse(json);
    return { valid: true };
  } catch (error) {
    return {
      valid: false,
      error: error instanceof Error ? error.message : 'Invalid JSON syntax',
    };
  }
}

// Validation error formatting
export function formatValidationErrors(errors: Record<string, string>): string[] {
  return Object.entries(errors).map(([field, message]) => {
    const fieldName = field.split('.').pop() || field;
    const formattedFieldName = fieldName.charAt(0).toUpperCase() + fieldName.slice(1);
    return `${formattedFieldName}: ${message}`;
  });
}

export function getFirstValidationError(errors: Record<string, string>): string | null {
  const errorEntries = Object.entries(errors);
  if (errorEntries.length === 0) return null;
  
  const [field, message] = errorEntries[0];
  const fieldName = field.split('.').pop() || field;
  const formattedFieldName = fieldName.charAt(0).toUpperCase() + fieldName.slice(1);
  return `${formattedFieldName}: ${message}`;
}

// Type exports for TypeScript
export type ChatMessageForm = z.infer<typeof chatMessageSchema>;
export type ConversationForm = z.infer<typeof conversationSchema>;
export type DocumentFilter = z.infer<typeof documentFilterSchema>;
export type BulkOperationForm = z.infer<typeof bulkOperationSchema>;
export type TrainingUploadForm = z.infer<typeof trainingUploadSchema>;
export type TrainingDataForm = z.infer<typeof trainingDataSchema>;
export type XmlGenerationForm = z.infer<typeof xmlGenerationSchema>;
export type XmlValidationForm = z.infer<typeof xmlValidationSchema>;
export type AnalyticsFilter = z.infer<typeof analyticsFilterSchema>;
export type ExportRequestForm = z.infer<typeof exportRequestSchema>;
export type LoginForm = z.infer<typeof loginFormSchema>;
export type RegisterForm = z.infer<typeof registerFormSchema>;
export type ProfileUpdateForm = z.infer<typeof profileUpdateSchema>;
export type ChangePasswordForm = z.infer<typeof changePasswordSchema>;
export type SystemSettingsForm = z.infer<typeof systemSettingsSchema>;