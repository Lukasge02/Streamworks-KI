/**
 * Type definitions for XML Chat V2
 * Clean, focused types for the new system
 */

// Re-export store types for convenience
export type {
  XMLChatMessage,
  XMLChatSession,
  XMLGenerationStatus
} from '../store/xmlChatStore'

// ================================
// API TYPES
// ================================

export interface XMLGenerationRequest {
  conversation: string
  jobType?: 'STANDARD' | 'SAP' | 'FILE_TRANSFER' | 'CUSTOM'
  parameters?: Record<string, any>
}

export interface XMLGenerationResponse {
  success: boolean
  xml?: string
  error?: string
  metadata?: {
    jobType: string
    parameters: Record<string, any>
    generationTime: number
  }
}

export interface XMLValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
}

// ================================
// COMPONENT PROPS
// ================================

export interface ChatMessageProps {
  message: XMLChatMessage
  onGenerateXML?: () => void
  isGeneratingXML?: boolean
}

export interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  onKeyDown?: (e: React.KeyboardEvent) => void
  disabled?: boolean
  placeholder?: string
}

export interface XMLPreviewProps {
  xml: string
  status: XMLGenerationStatus
  onClose: () => void
  onDownload?: () => void
  onCopy?: () => void
}

export interface SessionManagerProps {
  className?: string
}

// ================================
// UTILITY TYPES
// ================================

export interface ExportOptions {
  format: 'xml' | 'json'
  includeMetadata: boolean
  filename?: string
}

export interface ChatTheme {
  primary: string
  secondary: string
  accent: string
  background: string
  surface: string
  text: string
  muted: string
}

// ================================
// CONSTANTS
// ================================

export const XML_JOB_TYPES = {
  STANDARD: {
    label: 'Standard Job',
    description: 'Basic data processing job',
    icon: '⚡'
  },
  SAP: {
    label: 'SAP Interface',
    description: 'SAP system integration',
    icon: '🔗'
  },
  FILE_TRANSFER: {
    label: 'File Transfer',
    description: 'File movement and processing',
    icon: '📁'
  },
  CUSTOM: {
    label: 'Custom Configuration',
    description: 'Tailored XML structure',
    icon: '🛠️'
  }
} as const

export const CHAT_LIMITS = {
  MAX_MESSAGE_LENGTH: 4000,
  MAX_MESSAGES_PER_SESSION: 100,
  MAX_SESSIONS: 50
} as const