/**
 * Stream Helper Utilities
 * Provides utility functions for XML stream operations and calculations
 */

import { XMLStream } from '@/services/xmlStreamsApi'

export interface StreamCompleteness {
  isComplete: boolean
  completionPercentage: number
  missingFields: string[]
}

/**
 * Calculate stream completeness based on wizard_data and required fields
 */
export function calculateStreamCompleteness(stream: XMLStream): StreamCompleteness {
  if (!stream.wizard_data) {
    return {
      isComplete: false,
      completionPercentage: 0,
      missingFields: ['wizard_data']
    }
  }

  const wizardData = stream.wizard_data
  const missingFields: string[] = []
  let completedFields = 0
  let totalRequiredFields = 0

  // Required fields based on job type
  const requiredFieldsByJobType = {
    standard: [
      'jobName',
      'description', 
      'scheduleType',
      'streamProperties'
    ],
    sap: [
      'jobName',
      'description',
      'scheduleType',
      'sapConnection',
      'streamProperties'
    ],
    file_transfer: [
      'jobName',
      'description',
      'scheduleType',
      'sourceConfig',
      'targetConfig',
      'streamProperties'
    ],
    custom: [
      'jobName',
      'description',
      'customConfig'
    ]
  }

  const requiredFields = requiredFieldsByJobType[stream.job_type as keyof typeof requiredFieldsByJobType] || requiredFieldsByJobType.standard
  totalRequiredFields = requiredFields.length

  // Check each required field
  requiredFields.forEach(field => {
    const fieldValue = wizardData[field]
    
    if (!fieldValue) {
      missingFields.push(field)
    } else {
      // More detailed validation for complex objects
      if (typeof fieldValue === 'object') {
        if (field === 'streamProperties') {
          const streamProps = fieldValue as any
          if (!streamProps.name || !streamProps.type) {
            missingFields.push(`${field}.details`)
          } else {
            completedFields++
          }
        } else if (field === 'sapConnection') {
          const sapConn = fieldValue as any
          if (!sapConn.host || !sapConn.client) {
            missingFields.push(`${field}.details`)
          } else {
            completedFields++
          }
        } else if (field === 'sourceConfig' || field === 'targetConfig') {
          const config = fieldValue as any
          if (!config.path || !config.type) {
            missingFields.push(`${field}.details`)
          } else {
            completedFields++
          }
        } else {
          completedFields++
        }
      } else if (typeof fieldValue === 'string' && fieldValue.trim().length > 0) {
        completedFields++
      } else if (typeof fieldValue === 'number' || typeof fieldValue === 'boolean') {
        completedFields++
      } else {
        missingFields.push(field)
      }
    }
  })

  const completionPercentage = totalRequiredFields > 0 ? Math.round((completedFields / totalRequiredFields) * 100) : 0
  const isComplete = completionPercentage >= 100 && missingFields.length === 0

  return {
    isComplete,
    completionPercentage,
    missingFields
  }
}

/**
 * Get appropriate status configuration based on actual DB status
 */
export function getStreamStatusConfig(stream: XMLStream) {
  const statusConfigs = {
    // Primary workflow statuses
    draft: {
      label: 'Entwurf',
      color: 'bg-gray-500',
      textColor: 'text-gray-700',
      bgColor: 'bg-gray-50',
      description: 'Stream wird bearbeitet'
    },
    zur_freigabe: {
      label: 'Zur Freigabe',
      color: 'bg-yellow-500',
      textColor: 'text-yellow-700',
      bgColor: 'bg-yellow-50',
      description: 'Wartet auf Experten-Prüfung'
    },
    freigegeben: {
      label: 'Freigegeben',
      color: 'bg-emerald-500',
      textColor: 'text-emerald-700',
      bgColor: 'bg-emerald-50',
      description: 'Von Experte genehmigt'
    },
    abgelehnt: {
      label: 'Abgelehnt',
      color: 'bg-red-500',
      textColor: 'text-red-700',
      bgColor: 'bg-red-50',
      description: 'Von Experte abgelehnt'
    },
    published: {
      label: 'Veröffentlicht',
      color: 'bg-green-500',
      textColor: 'text-green-700',
      bgColor: 'bg-green-50',
      description: 'Live/Produktiv'
    },

    // Legacy status mappings for backward compatibility
    complete: {
      label: 'Zur Freigabe',
      color: 'bg-yellow-500',
      textColor: 'text-yellow-700',
      bgColor: 'bg-yellow-50',
      description: 'Wartet auf Experten-Prüfung (Legacy)'
    },
    in_bearbeitung: {
      label: 'In Bearbeitung',
      color: 'bg-blue-500',
      textColor: 'text-blue-700',
      bgColor: 'bg-blue-50',
      description: 'Legacy Status'
    },
    archiviert: {
      label: 'Archiviert',
      color: 'bg-slate-500',
      textColor: 'text-slate-700',
      bgColor: 'bg-slate-50',
      description: 'Nicht mehr aktiv'
    }
  }

  return statusConfigs[stream.status as keyof typeof statusConfigs] || statusConfigs.draft
}

/**
 * Get job type configuration with icons and colors
 */
export function getJobTypeConfig(jobType: string) {
  const configs = {
    standard: {
      label: 'Standard',
      color: 'bg-blue-500',
      textColor: 'text-blue-700',
      bgColor: 'bg-blue-50'
    },
    sap: {
      label: 'SAP',
      color: 'bg-orange-500',
      textColor: 'text-orange-700',
      bgColor: 'bg-orange-50'
    },
    file_transfer: {
      label: 'File Transfer',
      color: 'bg-purple-500',
      textColor: 'text-purple-700',
      bgColor: 'bg-purple-50'
    },
    custom: {
      label: 'Custom',
      color: 'bg-gray-500',
      textColor: 'text-gray-700',
      bgColor: 'bg-gray-50'
    }
  }
  
  return configs[jobType as keyof typeof configs] || configs.custom
}

/**
 * Format stream tags for display
 */
export function formatStreamTags(tags: string[] | null): string[] {
  if (!tags || !Array.isArray(tags)) return []
  
  return tags
    .filter(tag => typeof tag === 'string' && tag.trim().length > 0)
    .map(tag => tag.trim())
    .slice(0, 10) // Limit to 10 tags for performance
}

/**
 * Get stream search keywords for better filtering
 */
export function getStreamSearchKeywords(stream: XMLStream): string {
  const keywords: string[] = []
  
  if (stream.stream_name) keywords.push(stream.stream_name)
  if (stream.description) keywords.push(stream.description)
  if (stream.job_type) keywords.push(stream.job_type)
  if (stream.created_by) keywords.push(stream.created_by)
  if (stream.tags) keywords.push(...stream.tags)
  
  return keywords.join(' ').toLowerCase()
}

/**
 * Check if stream matches search criteria
 */
export function doesStreamMatchSearch(stream: XMLStream, searchTerm: string): boolean {
  if (!searchTerm || searchTerm.trim().length === 0) return true

  const keywords = getStreamSearchKeywords(stream)
  const normalizedSearch = searchTerm.trim().toLowerCase()

  return keywords.includes(normalizedSearch)
}

/**
 * Get available actions for a stream based on status and user role
 */
export function getStreamActions(stream: XMLStream, userRole: 'user' | 'expert' = 'user') {
  const actions = {
    canEdit: false,
    canView: true,
    canDelete: false,
    canSubmitForReview: false,
    canApprove: false,
    canReject: false,
    canPublish: false,
    canExport: true,
    canDuplicate: true
  }

  switch (stream.status) {
    case 'draft':
      actions.canEdit = true
      actions.canDelete = userRole === 'user' // Only creator can delete drafts
      actions.canSubmitForReview = userRole === 'user'
      break

    case 'zur_freigabe':
      actions.canEdit = false // No editing while in review
      actions.canDelete = false
      actions.canApprove = userRole === 'expert'
      actions.canReject = userRole === 'expert'
      break

    case 'freigegeben':
      actions.canEdit = false
      actions.canDelete = false
      actions.canPublish = userRole === 'expert'
      break

    case 'abgelehnt':
      actions.canEdit = userRole === 'user' // User can edit after rejection
      actions.canDelete = userRole === 'user'
      actions.canSubmitForReview = userRole === 'user' // Can resubmit after changes
      break

    case 'published':
      actions.canEdit = false
      actions.canDelete = false
      break

    // Legacy status handling
    case 'complete':
      if (userRole === 'expert') {
        actions.canApprove = true
        actions.canReject = true
      }
      break
  }

  return actions
}

/**
 * Get workflow step indicator
 */
export function getWorkflowStep(status: string): { step: number; totalSteps: number; label: string } {
  const steps = {
    draft: { step: 1, totalSteps: 4, label: 'Entwurf' },
    zur_freigabe: { step: 2, totalSteps: 4, label: 'Zur Freigabe' },
    freigegeben: { step: 3, totalSteps: 4, label: 'Freigegeben' },
    published: { step: 4, totalSteps: 4, label: 'Veröffentlicht' },
    abgelehnt: { step: 1, totalSteps: 4, label: 'Überarbeitung' }, // Back to step 1
    complete: { step: 2, totalSteps: 4, label: 'Zur Freigabe (Legacy)' }
  }

  return steps[status as keyof typeof steps] || steps.draft
}