'use client'

import React from 'react'
import { CheckCircle, AlertTriangle, XCircle, Clock, Zap } from 'lucide-react'

interface StatusIndicatorProps {
  status: 'success' | 'warning' | 'error' | 'processing' | 'high-confidence' | 'medium-confidence' | 'low-confidence'
  label?: string
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  className?: string
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  size = 'md',
  showIcon = true,
  className = ''
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'success':
        return {
          icon: CheckCircle,
          className: 'badge-enterprise-success',
          label: label || 'Erfolgreich'
        }
      case 'warning':
        return {
          icon: AlertTriangle,
          className: 'badge-enterprise-warning',
          label: label || 'Warnung'
        }
      case 'error':
        return {
          icon: XCircle,
          className: 'badge-enterprise-error',
          label: label || 'Fehler'
        }
      case 'processing':
        return {
          icon: Clock,
          className: 'badge-enterprise-info animate-pulse',
          label: label || 'Verarbeitung'
        }
      case 'high-confidence':
        return {
          icon: Zap,
          className: 'confidence-high',
          label: label || 'Hoch'
        }
      case 'medium-confidence':
        return {
          icon: AlertTriangle,
          className: 'confidence-medium',
          label: label || 'Mittel'
        }
      case 'low-confidence':
        return {
          icon: AlertTriangle,
          className: 'confidence-low',
          label: label || 'Niedrig'
        }
      default:
        return {
          icon: CheckCircle,
          className: 'badge-enterprise-neutral',
          label: label || 'Status'
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2'
  }

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  }

  return (
    <span className={`${config.className} ${sizeClasses[size]} ${className}`}>
      {showIcon && <Icon className={`${iconSizes[size]} mr-1.5`} />}
      {config.label}
    </span>
  )
}

// Specialized confidence indicator
export const ConfidenceIndicator: React.FC<{
  score: number
  label?: string
  className?: string
}> = ({ score, label, className = '' }) => {
  const getConfidenceStatus = (score: number): 'high-confidence' | 'medium-confidence' | 'low-confidence' => {
    if (score >= 0.8) return 'high-confidence'
    if (score >= 0.6) return 'medium-confidence'
    return 'low-confidence'
  }

  const status = getConfidenceStatus(score)
  const confidenceLabel = label || `${Math.round(score * 100)}% Vertrauen`

  return (
    <StatusIndicator
      status={status}
      label={confidenceLabel}
      className={className}
    />
  )
}

// Processing status indicator with animation
export const ProcessingIndicator: React.FC<{
  processingTime?: string
  isActive?: boolean
  className?: string
}> = ({ processingTime, isActive = true, className = '' }) => {
  return (
    <StatusIndicator
      status="processing"
      label={isActive ? 'Verarbeite...' : processingTime || 'Abgeschlossen'}
      className={`${className} ${isActive ? 'animate-pulse' : ''}`}
      showIcon={isActive}
    />
  )
}

export default StatusIndicator