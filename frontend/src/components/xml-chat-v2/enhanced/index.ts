/**
 * Enhanced XML Chat Components Export Index
 * Enhanced Components mit LangExtract Source Grounding Integration
 */

// Enhanced Components
export { default as EnhancedChatMessage } from './EnhancedChatMessage'

// Types
export type {
  EnhancedChatMessageProps,
  XMLChatMessage
} from './EnhancedChatMessage'

// Re-export Source Grounding Components for convenience
export {
  SourceHighlightedText,
  ParameterProvenancePanel,
  ParameterCorrectionModal,
  type SourceGroundedParameter,
  type EnhancedExtractionResult,
  type ParameterHighlightInfo,
  type ParameterCorrectionRequest,
  type ParameterCorrectionResponse,
  type SessionAnalytics
} from '../source-grounding'