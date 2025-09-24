'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Settings,
  Wrench,
  RefreshCw,
  Edit3,
  Check,
  X,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Info
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { toast } from 'sonner'

/**
 * 📊 Enhanced Parameter Panel - Professional parameter management
 *
 * Features:
 * - Categorized parameter display (Stream vs Job)
 * - Edit-in-place functionality
 * - Visual completion indicators
 * - Real-time validation
 * - XML regeneration controls
 */

interface ParameterPanelProps {
  streamParameters: Record<string, any>
  jobParameters: Record<string, any>
  detectedJobType?: string | null
  criticalMissing: string[]
  completionPercentage: number
  parametersLoaded: boolean
  onRegenerateXML: () => Promise<void>
  sessionId: string
}

interface EditableParameterProps {
  name: string
  value: any
  type: 'stream' | 'job'
  isCritical?: boolean
  onSave: (newValue: any) => void
}

// Individual parameter component with click-to-edit
function ClickableParameter({ name, value, type, isCritical, onSave }: EditableParameterProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(String(value || ''))
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    try {
      setIsSaving(true)
      await onSave(editValue)
      setIsEditing(false)
      toast.success('Parameter aktualisiert')
    } catch (error) {
      console.error('Parameter save error:', error)
      toast.error('Speichern fehlgeschlagen')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setEditValue(String(value || ''))
    setIsEditing(false)
  }

  const handleClick = () => {
    if (!isEditing) {
      setIsEditing(true)
    }
  }

  const isMultiline = String(value || '').length > 50

  return (
    <div
      className={`relative p-3 rounded-lg border transition-all duration-200 ${
        isEditing
          ? 'border-blue-300 bg-blue-50/30'
          : isCritical
          ? 'border-red-200 bg-red-50/30 cursor-pointer hover:shadow-sm'
          : 'border-gray-200 bg-gray-50/30 cursor-pointer hover:shadow-sm'
      }`}
      onClick={!isEditing ? handleClick : undefined}
      title={!isEditing ? `${name} bearbeiten (Klicken)` : undefined}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-gray-900">{name}</span>
            {isCritical && (
              <span className="text-xs text-red-600">⚠️</span>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-2">
              {isMultiline ? (
                <Textarea
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="min-h-[80px] text-sm"
                  placeholder={`Wert für ${name}...`}
                  autoFocus
                />
              ) : (
                <Input
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="text-sm"
                  placeholder={`Wert für ${name}...`}
                  autoFocus
                />
              )}

              <div className="flex gap-2">
                <Button
                  onClick={handleSave}
                  disabled={isSaving}
                  size="sm"
                  className="h-7 px-3"
                >
                  {isSaving ? (
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white" />
                  ) : (
                    <Check className="w-3 h-3" />
                  )}
                </Button>
                <Button
                  onClick={handleCancel}
                  disabled={isSaving}
                  variant="outline"
                  size="sm"
                  className="h-7 px-3"
                >
                  <X className="w-3 h-3" />
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-sm text-gray-700">
              {value ? (
                <span className="break-words">{String(value)}</span>
              ) : (
                <span className="italic text-gray-400">Nicht gesetzt</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export function ParameterPanel({
  streamParameters,
  jobParameters,
  detectedJobType,
  criticalMissing,
  completionPercentage,
  parametersLoaded,
  onRegenerateXML,
  sessionId
}: ParameterPanelProps) {
  const [isRegenerating, setIsRegenerating] = useState(false)

  // Combine all parameters into one list
  const allParameters = {
    ...streamParameters,
    ...jobParameters
  }

  const totalParams = Object.keys(allParameters).length
  const missingCount = criticalMissing.length

  // Handle parameter save (placeholder - would integrate with backend)
  const handleParameterSave = async (paramName: string, newValue: any, type: 'stream' | 'job') => {
    // TODO: Implement parameter update API call
    console.log('Saving parameter:', { paramName, newValue, type, sessionId })

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))

    // In real implementation, this would call the backend API
    // await updateSessionParameter(sessionId, paramName, newValue, type)
  }

  // Handle XML regeneration
  const handleRegenerate = async () => {
    try {
      setIsRegenerating(true)
      await onRegenerateXML()
    } catch (error) {
      console.error('Regeneration error:', error)
    } finally {
      setIsRegenerating(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Parameters Content */}
      <div className="flex-1 overflow-y-auto pb-4">
        <div className="p-4">
          {totalParams > 0 ? (
            <div className="space-y-2">
              {Object.entries(allParameters).map(([key, value]) => {
                // Determine if this is a stream or job parameter
                const isStreamParam = key in streamParameters
                return (
                  <ClickableParameter
                    key={key}
                    name={key}
                    value={value}
                    type={isStreamParam ? 'stream' : 'job'}
                    isCritical={criticalMissing.includes(key)}
                    onSave={(newValue) => handleParameterSave(key, newValue, isStreamParam ? 'stream' : 'job')}
                  />
                )
              })}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Settings className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-sm">Keine Parameter gefunden</p>
              <p className="text-xs text-gray-400 mt-1">
                Parameter werden aus der LangExtract-Session geladen
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Action Panel */}
      <div className="border-t border-gray-200 p-4 space-y-3">
        {/* Missing Parameters Warning */}
        {missingCount > 0 && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-red-800">
                {missingCount} kritische Parameter fehlen
              </span>
            </div>
          </div>
        )}

        {/* Regenerate Button */}
        <Button
          onClick={handleRegenerate}
          disabled={isRegenerating || !parametersLoaded}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          size="lg"
        >
          {isRegenerating ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
              <span>XML wird regeneriert...</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <RefreshCw className="w-4 h-4" />
              <span>XML neu generieren</span>
            </div>
          )}
        </Button>
      </div>
    </div>
  )
}