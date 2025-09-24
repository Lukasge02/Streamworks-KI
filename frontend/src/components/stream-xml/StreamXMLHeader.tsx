'use client'

import React from 'react'
import {
  ArrowLeft,
  Code2,
  List,
  Calendar,
  Clock
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

/**
 * 🎯 StreamXMLHeader - Professional header for XML stream page
 *
 * Features:
 * - Session info and job type display
 * - Completion progress indicator
 * - Navigation controls
 * - Status indicators
 * - Responsive design
 */

interface StreamXMLHeaderProps {
  sessionId: string
  streamName?: string
  createdAt?: string | Date
  lastUpdated?: string | Date
  onBackToChat: () => void
  onBackToStreams?: () => void
}

export function StreamXMLHeader({
  sessionId,
  streamName,
  createdAt,
  lastUpdated,
  onBackToChat,
  onBackToStreams
}: StreamXMLHeaderProps) {

  // Format date helper function
  const formatDate = (date: string | Date | undefined): string => {
    if (!date) return '-'
    const d = new Date(date)
    return d.toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left Side - Navigation & Title */}
        <div className="flex items-center gap-4">
          {/* Back Button */}
          <Button
            onClick={onBackToChat}
            variant="ghost"
            size="sm"
            className="flex items-center gap-2 hover:bg-gray-100"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="hidden sm:inline">Zurück zum Chat</span>
          </Button>

          {/* Back to Streams Button */}
          {onBackToStreams && (
            <Button
              onClick={onBackToStreams}
              variant="outline"
              size="sm"
              className="flex items-center gap-2 hover:bg-gray-50"
            >
              <List className="w-4 h-4" />
              <span className="hidden sm:inline">Zu Streams</span>
            </Button>
          )}

          {/* Title */}
          <div className="flex items-center gap-2">
            <Code2 className="w-5 h-5 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">
              XML Stream Editor
            </h1>
          </div>
        </div>

      </div>


      {/* Breadcrumb Navigation */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between">
          {/* Left: Breadcrumb */}
          <nav className="flex items-center space-x-2 text-sm text-gray-500">
            <span>Streamworks</span>
            <span>/</span>
            <span>LangExtract</span>
            <span>/</span>
            <span className="text-gray-900 font-medium">XML Stream Editor</span>
            {streamName && (
              <>
                <span>/</span>
                <span className="text-blue-600 font-medium">{streamName}</span>
              </>
            )}
          </nav>

          {/* Right: Metadata */}
          <div className="hidden sm:flex items-center gap-4 text-xs text-gray-500">
            {createdAt && (
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                <span>Erstellt: {formatDate(createdAt)}</span>
              </div>
            )}
            {lastUpdated && (
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <span>Update: {formatDate(lastUpdated)}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}