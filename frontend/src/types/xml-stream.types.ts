import { Document } from './document.types'

export type CustomerCategory = 
  | 'Beta'
  | 'Demo'
  | 'Production'
  | 'CR'
  | 'Training'
  | 'Development'
  | 'Test'

export type StreamType =
  | 'processing'
  | 'monitoring' 
  | 'integration'
  | 'reporting'
  | 'maintenance'
  | 'backup'
  | 'deployment'

export type ValidationLevel = 
  | 'syntax'
  | 'schema' 
  | 'business_logic'
  | 'streamworks_compatibility'
  | 'performance'

export type XMLChunkingStrategy =
  | 'xpath_semantic'
  | 'hierarchical'
  | 'functional'
  | 'hybrid'

export interface XMLStreamMetadata {
  stream_name: string
  customer_category: CustomerCategory
  job_count: number
  dependency_count: number
  complexity_score: number
  patterns: string[]
  anti_patterns: string[]
  stream_type: StreamType
  validation_results: XMLValidationResult[]
  chunking_strategy: XMLChunkingStrategy
  last_modified: string
  author?: string
  version?: string
}

export interface XMLStreamDocument extends Document {
  category: 'xml'
  xml_metadata: XMLStreamMetadata
  rag_indexed: boolean
  similarity_score?: number
  template_suitable?: boolean
  generation_source?: 'uploaded' | 'generated' | 'modified'
}

export interface XMLValidationResult {
  level: ValidationLevel
  status: 'valid' | 'warning' | 'error'
  message: string
  line_number?: number
  xpath?: string
  severity: 'low' | 'medium' | 'high' | 'critical'
}

export interface XMLChunk {
  chunk_id: string
  content: string
  chunk_type: 'job_definition' | 'dependency' | 'parameter' | 'condition' | 'script'
  xpath_location: string
  job_name?: string
  job_type?: string
  metadata: {
    complexity_score: number
    dependencies: string[]
    parameters: Record<string, any>
    patterns: string[]
    line_start: number
    line_end: number
  }
}

export interface XMLSimilarityMatch {
  document_id: string
  similarity_score: number
  matching_chunks: XMLChunk[]
  stream_name: string
  customer_category: CustomerCategory
  patterns_matched: string[]
}

export interface XMLTemplateRecommendation {
  template_id: string
  template_name: string
  confidence_score: number
  similarity_matches: XMLSimilarityMatch[]
  customization_suggestions: string[]
  estimated_complexity: number
  required_modifications: string[]
  customer_compatibility: CustomerCategory[]
}

export interface StreamBuilderConfig {
  requirements: string
  customer_category: CustomerCategory
  template_base?: string[]
  job_definitions: JobDefinition[]
  dependencies: DependencyMap
  validation_level: ValidationLevel[]
  generation_options: {
    include_comments: boolean
    optimize_performance: boolean
    validate_dependencies: boolean
    generate_documentation: boolean
  }
}

export interface JobDefinition {
  job_id: string
  job_name: string
  job_type: 'StartPoint' | 'EndPoint' | 'Processing' | 'Condition' | 'Script' | 'FileTransfer' | 'DatabaseOperation'
  parameters: Record<string, any>
  position: { x: number; y: number }
  connections: string[]
  validation_status: XMLValidationResult[]
  metadata: {
    description?: string
    estimated_duration?: number
    resource_requirements?: string[]
    error_handling?: string
  }
}

export interface DependencyMap {
  [jobId: string]: {
    depends_on: string[]
    dependency_type: 'sequential' | 'parallel' | 'conditional'
    conditions?: string[]
  }
}

export interface StreamFlow {
  jobs: JobDefinition[]
  dependencies: DependencyEdge[]
  critical_path: string[]
  potential_issues: ValidationWarning[]
  execution_estimate: number
  performance_metrics: {
    estimated_duration: number
    resource_usage: Record<string, number>
    bottlenecks: string[]
  }
}

export interface DependencyEdge {
  from_job: string
  to_job: string
  dependency_type: 'success' | 'failure' | 'always' | 'condition'
  condition?: string
  delay?: number
}

export interface ValidationWarning {
  type: 'performance' | 'dependency' | 'configuration' | 'compatibility'
  severity: 'info' | 'warning' | 'error' | 'critical'
  message: string
  affected_jobs: string[]
  suggested_fix?: string
}

export interface XMLGenerationContext {
  user_query: string
  selected_templates: string[]
  customer_environment: CustomerCategory
  complexity_preference: 'simple' | 'advanced' | 'enterprise'
  validation_requirements: ValidationLevel[]
  constraints: {
    max_jobs?: number
    max_dependencies?: number
    performance_target?: number
    resource_limits?: Record<string, number>
  }
}

export interface XMLGenerationResult {
  xml_content: string
  generation_metadata: {
    templates_used: string[]
    generation_time: number
    validation_results: XMLValidationResult[]
    optimization_applied: string[]
  }
  suggested_improvements: string[]
  deployment_ready: boolean
}

export interface XMLStreamFilter {
  search: string
  // Removed extending DocumentFilter as it's not available
  customer_category: CustomerCategory | 'all'
  stream_type: StreamType | 'all'
  complexity_range: {
    min: number
    max: number
  }
  job_count_range: {
    min: number
    max: number
  }
  patterns: string[]
  validation_status: 'valid' | 'warning' | 'error' | 'all'
  rag_indexed?: boolean
  template_suitable?: boolean
  dateRange?: any
}

export interface XMLBulkOperation {
  operation: 'validate' | 'index' | 'migrate' | 'generate' | 'export'
  document_ids: string[]
  options: Record<string, any>
  progress?: {
    total: number
    completed: number
    failed: number
    current_operation?: string
  }
}

export interface XMLPatternAnalysis {
  common_patterns: {
    pattern: string
    frequency: number
    examples: string[]
    description: string
  }[]
  anti_patterns: {
    pattern: string
    risk_level: 'low' | 'medium' | 'high'
    description: string
    suggested_alternative: string
  }[]
  trend_analysis: {
    emerging_patterns: string[]
    declining_patterns: string[]
    customer_specific_patterns: Record<CustomerCategory, string[]>
  }
}

export const XML_CUSTOMER_CATEGORIES: { value: CustomerCategory; label: string; color: string }[] = [
  { value: 'Production', label: 'Produktion', color: 'red' },
  { value: 'Demo', label: 'Demo', color: 'blue' },
  { value: 'Beta', label: 'Beta', color: 'purple' },
  { value: 'CR', label: 'Change Request', color: 'orange' },
  { value: 'Training', label: 'Schulung', color: 'green' },
  { value: 'Development', label: 'Entwicklung', color: 'yellow' },
  { value: 'Test', label: 'Test', color: 'gray' },
]

export const XML_STREAM_TYPES: { value: StreamType; label: string; icon: string }[] = [
  { value: 'processing', label: 'Verarbeitung', icon: '⚙️' },
  { value: 'monitoring', label: 'Überwachung', icon: '👁️' },
  { value: 'integration', label: 'Integration', icon: '🔌' },
  { value: 'reporting', label: 'Berichterstattung', icon: '📊' },
  { value: 'maintenance', label: 'Wartung', icon: '🔧' },
  { value: 'backup', label: 'Sicherung', icon: '💾' },
  { value: 'deployment', label: 'Bereitstellung', icon: '🚀' },
]

export const VALIDATION_LEVELS: { value: ValidationLevel; label: string; description: string }[] = [
  { value: 'syntax', label: 'Syntax', description: 'XML-Syntax und Struktur' },
  { value: 'schema', label: 'Schema', description: 'XSD-Schema Validierung' },
  { value: 'business_logic', label: 'Geschäftslogik', description: 'Logische Konsistenz' },
  { value: 'streamworks_compatibility', label: 'Streamworks', description: 'Streamworks Kompatibilität' },
  { value: 'performance', label: 'Performance', description: 'Leistungsoptimierung' },
]

export const JOB_TYPES = [
  { value: 'StartPoint', label: 'Startpunkt', icon: '🟢', color: 'green' },
  { value: 'EndPoint', label: 'Endpunkt', icon: '🔴', color: 'red' },
  { value: 'Processing', label: 'Verarbeitung', icon: '⚙️', color: 'blue' },
  { value: 'Condition', label: 'Bedingung', icon: '❓', color: 'yellow' },
  { value: 'Script', label: 'Skript', icon: '📜', color: 'purple' },
  { value: 'FileTransfer', label: 'Dateitransfer', icon: '📁', color: 'orange' },
  { value: 'DatabaseOperation', label: 'Datenbankoperation', icon: '🗃️', color: 'cyan' },
] as const

export const CHUNKING_STRATEGIES: { value: XMLChunkingStrategy; label: string; description: string }[] = [
  { value: 'xpath_semantic', label: 'XPath Semantisch', description: 'Semantische Analyse basierend auf XPath' },
  { value: 'hierarchical', label: 'Hierarchisch', description: 'Basierend auf XML-Hierarchie' },
  { value: 'functional', label: 'Funktional', description: 'Nach Funktionalität gruppiert' },
  { value: 'hybrid', label: 'Hybrid', description: 'Kombination aller Strategien' },
]