/**
 * TypeScript interfaces for XML Wizard
 * Defines all form data structures and API types
 */

// Enums
export enum JobType {
  STANDARD = 'standard',
  SAP = 'sap',
  FILE_TRANSFER = 'fileTransfer',
  CUSTOM = 'custom'
}

export enum OSType {
  WINDOWS = 'Windows',
  UNIX = 'Unix'
}

export enum ScheduleMode {
  SIMPLE = 'simple',
  NATURAL = 'natural',
  ADVANCED = 'advanced'
}

export enum ValidationSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error'
}

// Navigation & Chapter Types
export interface SubChapter {
  id: string
  title: string
  description: string
  isCompleted: boolean
  isValid: boolean
  hasErrors: boolean
  validationMessage?: string
}

export interface WizardChapter {
  id: string
  title: string
  description: string
  icon: string
  subChapters: SubChapter[]
  isCompleted: boolean
  isExpanded: boolean
  currentSubChapter?: string
}

// Contact Person
export interface ContactPerson {
  firstName: string
  lastName: string
  company: string
  department?: string
}

// Job-specific forms
export interface StandardJobForm {
  jobName: string
  agent: string
  os: OSType
  script: string
  parameters?: string[]
}

export interface SAPParameter {
  parameter: string
  value: string
  type: string // SIGN, OPTION, LOW, HIGH
}

export interface SAPJobForm {
  jobName: string
  system: string
  report: string
  variant: string
  batchUser: string
  selectionParameters: SAPParameter[]
}

export interface FileTransferForm {
  jobName: string
  sourceAgent: string
  sourcePath: string
  targetAgent: string
  targetPath: string
  filePattern?: string
  onExistsBehavior: string // Overwrite, Abort, Append
  deleteAfterTransfer: boolean
}

// Union type for job forms
export type JobFormData = StandardJobForm | SAPJobForm | FileTransferForm | Record<string, any>

// Stream properties
export interface StreamProperties {
  streamName: string
  description: string
  documentation?: string
  contactPerson: ContactPerson
  maxRuns: number
  retentionDays?: number
  severityGroup?: string
  streamPath?: string
}

// Scheduling
export interface SimpleSchedule {
  preset: string // manual, daily, weekly, monthly
  time?: string // HH:MM
  weekdays: boolean[]
}

export interface NaturalSchedule {
  description: string
}

export interface AdvancedSchedule {
  cronExpression?: string
  scheduleRuleXml?: string
}

export interface SchedulingForm {
  mode: ScheduleMode
  simple?: SimpleSchedule
  natural?: NaturalSchedule
  advanced?: AdvancedSchedule
}

// Complete wizard data
export interface WizardFormData {
  jobType: JobType
  jobForm: JobFormData
  streamProperties: StreamProperties
  scheduling: SchedulingForm
}

// Wizard state management
export interface WizardState {
  currentStep: number
  totalSteps: number
  currentChapter: string
  currentSubChapter: string
  chapters: WizardChapter[]
  jobType: JobType | null
  formData: Partial<WizardFormData>
  isValid: boolean
  canProceed: boolean
  generatedXML?: string
  validationResults?: ValidationResult
  isGenerating: boolean
}

// Step definitions
export interface WizardStep {
  id: string
  title: string
  description: string
  component: React.ComponentType<WizardStepProps>
  isValid: (formData: Partial<WizardFormData>) => boolean
  canSkip?: boolean
}

export interface WizardStepProps {
  formData: Partial<WizardFormData>
  onUpdateData: (data: Partial<WizardFormData>) => void
  onNext: () => void
  onPrevious: () => void
  canProceed: boolean
  isLastStep: boolean
}

// API Types - mirroring backend schemas

// Template search and matching
export interface XMLTemplate {
  id: string
  filename: string
  filePath: string
  jobType: JobType
  description: string
  complexityScore: number
  jobCount: number
  patterns: string[]
  xmlContent: string
  metadata: Record<string, any>
}

export interface TemplateMatch {
  template: XMLTemplate
  similarityScore: number
  reasons: string[]
}

export interface TemplateSearchQuery {
  query: string
  jobType?: JobType
  maxResults?: number
}

export interface TemplateSearchResponse {
  templates: TemplateMatch[]
  totalFound: number
  searchTimeMs: number
}

// Validation
export interface ValidationError {
  line?: number
  column?: number
  severity: ValidationSeverity
  message: string
  suggestion?: string
}

export interface ValidationResult {
  valid: boolean
  errors: ValidationError[]
  warnings: ValidationError[]
  schemaVersion?: string
}

export interface ValidationResponse {
  validationResult: ValidationResult
  validationTimeMs: number
}

// XML Generation
export interface XMLGenerationResult {
  success: boolean
  xmlContent?: string
  templateUsed?: TemplateMatch
  validationResults?: ValidationResult
  requiresHumanReview: boolean
  reviewReasons: string[]
  generationTimeMs?: number
  errorMessage?: string
}

// Job Type Information
export interface JobTypeInfo {
  type: JobType
  title: string
  description: string
  complexity: string
  estimatedTime: string
  icon: string
  examples: string[]
  templateCount: number
}

export interface JobTypesResponse {
  jobTypes: JobTypeInfo[]
}

// Schedule parsing
export interface ScheduleRule {
  scheduleRuleXml: string
  description: string
  nextExecutions: Date[]
}

export interface ScheduleParsingResponse {
  scheduleRule: ScheduleRule
  parsingTimeMs: number
}

// UI Components
export interface JobTypeCard {
  type: JobType
  title: string
  description: string
  complexity: 'simple' | 'medium' | 'complex'
  estimatedTime: string
  icon: string
  examples: string[]
  templateCount: number
  onClick: () => void
  selected: boolean
}

// Form validation
export interface FieldValidation {
  field: string
  isValid: boolean
  errorMessage?: string
}

export interface FormValidation {
  isValid: boolean
  errors: FieldValidation[]
}

// Navigation
export interface WizardNavigation {
  canGoBack: boolean
  canGoForward: boolean
  currentStep: number
  totalSteps: number
  stepTitles: string[]
  onStepClick?: (step: number) => void
}

// Loading states
export interface LoadingState {
  isLoading: boolean
  message?: string
  progress?: number
}

// Error handling
export interface WizardError {
  type: 'validation' | 'api' | 'generation' | 'system'
  message: string
  details?: string
  field?: string
  canRetry: boolean
}

export interface ErrorState {
  hasError: boolean
  error?: WizardError
  showError: boolean
}

// Local storage / persistence
export interface WizardPersistence {
  sessionId: string
  lastSaved: Date
  formData: Partial<WizardFormData>
  currentStep: number
}

// Analytics / tracking
export interface WizardAnalytics {
  sessionId: string
  startTime: Date
  stepTimes: Record<number, number>
  jobType?: JobType
  completed: boolean
  abandonedAtStep?: number
}