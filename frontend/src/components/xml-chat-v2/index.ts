/**
 * XML Chat V2 - Main Export
 * Clean, modern XML generation chat interface
 */

// Main Component
export { default as XMLChatInterface } from './XMLChatInterface'

// Components
export { default as ChatMessage } from './components/ChatMessage'
export { default as ChatInput } from './components/ChatInput'
export { default as XMLPreview } from './components/XMLPreview'
export { default as SessionManager } from './components/SessionManager'

// Store & Hooks
export { useXMLChatStore, useXMLChatSelectors } from './store/xmlChatStore'
export { useXMLGeneration, useXMLValidation, useXMLExport } from './hooks/useXMLGeneration'

// Types
export type {
  XMLChatMessage,
  XMLChatSession,
  XMLGenerationStatus,
  XMLGenerationRequest,
  XMLGenerationResponse,
  ChatMessageProps,
  ChatInputProps,
  XMLPreviewProps,
  SessionManagerProps
} from './types'

export { XML_JOB_TYPES, CHAT_LIMITS } from './types'