/**
 * Source Grounding Components Export Index
 * Zentrale Exportstelle für alle Source-Grounded Parameter Components
 */

// Core Components
export { default as SourceHighlightedText } from './SourceHighlightedText'
export { default as ParameterProvenancePanel } from './ParameterProvenancePanel'
export { default as ParameterCorrectionModal } from './ParameterCorrectionModal'

// Types
export type {
  SourceGroundedParameter,
  HighlightRange
} from './SourceHighlightedText'

export type {
  FilterType,
  SortType
} from './ParameterProvenancePanel'

export type {
  ValidationResult
} from './ParameterCorrectionModal'

// Re-export common types for convenience
export interface EnhancedExtractionResult {
  detected_job_type: string
  job_type_confidence: number
  stream_parameters: SourceGroundedParameter[]
  job_parameters: SourceGroundedParameter[]
  source_grounding_data: {
    highlighted_ranges: Array<[number, number, string]>
    parameter_sources: Array<{
      name: string
      source_text: string
      character_offsets: [number, number]
      confidence: number
      highlight_color: string
    }>
    full_text: string
    extraction_quality: string
    overall_confidence: number
  }
  completion_percentage: number
  next_required_parameter?: string
  missing_parameters: string[]
  suggested_questions: string[]
  contextual_suggestions: string[]
  overall_confidence: number
  extraction_quality: string
  needs_review: boolean
  timestamp: string
  extraction_duration: number
  metadata: {
    extraction_method: string
    job_type_detected: string
    parameters_extracted: number
    processing_time: number
  }
}

export interface ParameterHighlightInfo {
  parameter_name: string
  source_text: string
  character_offsets: [number, number]
  confidence: number
  context_preview: string
  alternative_interpretations: string[]
}

export interface ParameterCorrectionRequest {
  session_id: string
  parameter_name: string
  old_value: any
  new_value: any
  correction_reason?: string
  user_feedback?: string
}

export interface ParameterCorrectionResponse {
  success: boolean
  message: string
  updated_parameter?: SourceGroundedParameter
  needs_revalidation: boolean
  updated_source_grounding?: any
  affected_parameters: string[]
  completion_percentage: number
  suggested_next_questions: string[]
}

export interface SessionAnalytics {
  session_id: string
  total_messages: number
  total_parameters_extracted: number
  average_confidence: number
  extraction_method: string
  average_extraction_time: number
  total_corrections_made: number
  user_satisfaction_score?: number
  highlight_coverage_percentage: number
  parameters_with_high_confidence: number
  parameters_needing_review: number
  extraction_accuracy: number
  user_confirmation_rate: number
  session_start: string
  session_end?: string
  total_duration?: number
}