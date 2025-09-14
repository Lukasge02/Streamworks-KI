/**
 * Interactive StatusBadge Component with Workflow Actions
 * Provides inline status management and workflow transitions
 */
'use client'

import React, { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import {
  Send,
  CheckCircle,
  XCircle,
  Rocket,
  ChevronDown,
  Clock,
  AlertCircle,
  Eye
} from 'lucide-react'

import { XMLStream } from '@/services/xmlStreamsApi'
import { getStreamStatusConfig, getStreamActions, getWorkflowStep } from '@/utils/streamHelpers'
import { cn } from '@/lib/utils'

interface StatusBadgeProps {
  stream: XMLStream
  userRole?: 'user' | 'expert'
  onSubmitForReview?: () => void
  onApprove?: () => void
  onReject?: () => void
  onPublish?: () => void
  className?: string
  showWorkflowActions?: boolean
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  stream,
  userRole = 'user',
  onSubmitForReview,
  onApprove,
  onReject,
  onPublish,
  className,
  showWorkflowActions = true
}) => {
  const [isOpen, setIsOpen] = useState(false)

  const statusInfo = getStreamStatusConfig(stream)
  const actions = getStreamActions(stream, userRole)
  const workflowStep = getWorkflowStep(stream.status)

  // Get available workflow actions
  const workflowActions = []

  if (actions.canSubmitForReview && onSubmitForReview) {
    workflowActions.push({
      label: 'Zur Freigabe einreichen',
      icon: Send,
      onClick: onSubmitForReview,
      className: 'text-blue-600 focus:text-blue-600'
    })
  }

  if (actions.canApprove && onApprove) {
    workflowActions.push({
      label: 'Freigeben',
      icon: CheckCircle,
      onClick: onApprove,
      className: 'text-green-600 focus:text-green-600'
    })
  }

  if (actions.canReject && onReject) {
    workflowActions.push({
      label: 'Ablehnen',
      icon: XCircle,
      onClick: onReject,
      className: 'text-orange-600 focus:text-orange-600'
    })
  }

  if (actions.canPublish && onPublish) {
    workflowActions.push({
      label: 'Veröffentlichen',
      icon: Rocket,
      onClick: onPublish,
      className: 'text-blue-600 focus:text-blue-600'
    })
  }

  const hasActions = workflowActions.length > 0 && showWorkflowActions

  // Debug logging
  console.log('🏷️ StatusBadge Debug:', {
    streamStatus: stream.status,
    userRole,
    actions: {
      canSubmitForReview: actions.canSubmitForReview,
      canApprove: actions.canApprove,
      canReject: actions.canReject,
      canPublish: actions.canPublish
    },
    workflowActionsCount: workflowActions.length,
    hasActions,
    showWorkflowActions,
    availableHandlers: {
      onSubmitForReview: !!onSubmitForReview,
      onApprove: !!onApprove,
      onReject: !!onReject,
      onPublish: !!onPublish
    }
  })

  // Status icon mapping
  const statusIcons = {
    draft: Clock,
    zur_freigabe: Send,
    freigegeben: CheckCircle,
    abgelehnt: AlertCircle,
    published: Rocket,
    complete: Send // Legacy
  }

  const StatusIcon = statusIcons[stream.status as keyof typeof statusIcons] || Eye

  return (
    <div className={cn("flex items-center", className)}>
      {/* Interactive Status Badge */}
      {hasActions ? (
        <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className={cn(
                "h-auto p-0 hover:bg-transparent",
                isOpen && "bg-transparent"
              )}
            >
              <Badge
                className={cn(
                  "cursor-pointer flex items-center gap-1.5 pr-1",
                  statusInfo.textColor,
                  statusInfo.bgColor,
                  hasActions && "hover:opacity-80 transition-opacity"
                )}
              >
                <StatusIcon className="w-3 h-3" />
                {statusInfo.label}
                <ChevronDown className="w-3 h-3 ml-1" />
              </Badge>
            </Button>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="start" className="min-w-48">
            {/* Current Status Info */}
            <div className="px-3 py-2 border-b">
              <div className="flex items-center gap-2">
                <StatusIcon className="w-4 h-4 text-gray-500" />
                <div>
                  <div className="font-medium text-sm">{statusInfo.label}</div>
                  <div className="text-xs text-gray-500">{statusInfo.description}</div>
                </div>
              </div>
            </div>

            {/* Workflow Actions */}
            {workflowActions.map((action, index) => {
              const ActionIcon = action.icon
              return (
                <DropdownMenuItem
                  key={index}
                  onClick={() => {
                    action.onClick()
                    setIsOpen(false)
                  }}
                  className={action.className}
                >
                  <ActionIcon className="w-4 h-4 mr-2" />
                  {action.label}
                </DropdownMenuItem>
              )
            })}
          </DropdownMenuContent>
        </DropdownMenu>
      ) : (
        // Static Badge (no actions available)
        <Badge
          className={cn(
            "flex items-center gap-1.5",
            statusInfo.textColor,
            statusInfo.bgColor
          )}
        >
          <StatusIcon className="w-3 h-3" />
          {statusInfo.label}
        </Badge>
      )}
    </div>
  )
}

export default StatusBadge