/**
 * German Status Badge Component
 * Professional status indicators with German labels and proper styling
 */

import { DocumentStatus } from '@/types/api.types'
import { cn } from '@/lib/utils'
import {
  CloudArrowUpIcon,
  MagnifyingGlassIcon,
  CogIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  ForwardIcon,
  ClockIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline'

interface StatusBadgeProps {
  status: DocumentStatus
  className?: string
  showIcon?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const STATUS_CONFIG = {
  pending: {
    label: 'Wartend',
    color: 'bg-gray-100 text-gray-600 border-gray-200',
    icon: ClockIcon,
    pulse: false
  },
  uploading: {
    label: 'Wird hochgeladen',
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: CloudArrowUpIcon,
    pulse: true
  },
  analyzing: {
    label: 'Wird analysiert',
    color: 'bg-purple-100 text-purple-800 border-purple-200',
    icon: MagnifyingGlassIcon,
    pulse: true
  },
  processing: {
    label: 'Wird verarbeitet',
    color: 'bg-orange-100 text-orange-800 border-orange-200',
    icon: CogIcon,
    pulse: true
  },
  ready: {
    label: 'Bereit',
    color: 'bg-green-100 text-green-800 border-green-200',
    icon: CheckCircleIcon,
    pulse: false
  },
  completed: {
    label: 'Abgeschlossen',
    color: 'bg-green-100 text-green-800 border-green-200',
    icon: CheckCircleIcon,
    pulse: false
  },
  skipped: {
    label: 'Übersprungen',
    color: 'bg-gray-100 text-gray-800 border-gray-200',
    icon: ForwardIcon,
    pulse: false
  },
  error: {
    label: 'Fehler',
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: XCircleIcon,
    pulse: false
  }
} as const

// Fallback configuration for unknown status values
const FALLBACK_CONFIG = {
  label: 'Unbekannt',
  color: 'bg-gray-100 text-gray-600 border-gray-300',
  icon: QuestionMarkCircleIcon,
  pulse: false
}

export function StatusBadge({ 
  status, 
  className, 
  showIcon = true, 
  size = 'md' 
}: StatusBadgeProps) {
  // Defensive programming: use fallback config if status is unknown
  const config = STATUS_CONFIG[status] || FALLBACK_CONFIG
  const Icon = config.icon

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-2.5 py-1.5 text-sm',
    lg: 'px-3 py-2 text-base'
  }

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4', 
    lg: 'w-5 h-5'
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-medium border rounded-full',
        'transition-all duration-200',
        config.color,
        sizeClasses[size],
        config.pulse && 'animate-pulse',
        className
      )}
    >
      {showIcon && (
        <Icon 
          className={cn(
            iconSizes[size],
            config.pulse && 'animate-spin'
          )} 
        />
      )}
      {config.label}
    </span>
  )
}

// Utility function to get German status label
export function getGermanStatusLabel(status: DocumentStatus): string {
  return STATUS_CONFIG[status]?.label || status
}

// Utility function to check if status is in progress
export function isStatusInProgress(status: DocumentStatus): boolean {
  return ['uploading', 'analyzing', 'processing'].includes(status)
}

// Utility function to check if status indicates completion
export function isStatusComplete(status: DocumentStatus): boolean {
  return status === 'ready'
}

// Utility function to check if status indicates an issue
export function isStatusIssue(status: DocumentStatus): boolean {
  return ['error', 'skipped'].includes(status)
}