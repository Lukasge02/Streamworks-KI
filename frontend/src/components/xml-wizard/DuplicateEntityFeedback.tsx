'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Trash2,
  Edit3,
  Info
} from 'lucide-react'

// ================================
// TYPES
// ================================

export interface DuplicateEntityFeedback {
  entityField: string
  existingValue: string
  newValue: string
  confidence: number
  duplicateReason: string
  suggestionType: 'keep_existing' | 'accept_new' | 'manual_edit'
}

interface DuplicateEntityFeedbackProps {
  duplicates: DuplicateEntityFeedback[]
  onResolveDuplicate: (entityField: string, action: 'keep' | 'update' | 'edit', newValue?: string) => void
  className?: string
}

// ================================
// COMPONENT
// ================================

/**
 * Duplicate Entity Feedback Component
 *
 * Provides user control over duplicate entity handling
 * - Shows detected duplicates with reasoning
 * - Allows users to choose which value to keep
 * - Prevents repetitive questions while allowing corrections
 */
export const DuplicateEntityFeedback: React.FC<DuplicateEntityFeedbackProps> = ({
  duplicates,
  onResolveDuplicate,
  className = ''
}) => {
  const [editingField, setEditingField] = React.useState<string | null>(null)
  const [editValue, setEditValue] = React.useState<string>('')

  const formatFieldLabel = (field: string): string => {
    const labelMap: Record<string, string> = {
      'sap_system': 'SAP System',
      'report_name': 'Report Name',
      'source_path': 'Source Path',
      'target_path': 'Target Path',
      'script_path': 'Script Path',
    }

    return labelMap[field] || field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const getDuplicateReasonIcon = (reason: string) => {
    if (reason.includes('exact match')) return <CheckCircle className="w-4 h-4 text-green-500" />
    if (reason.includes('fuzzy match')) return <RefreshCw className="w-4 h-4 text-yellow-500" />
    if (reason.includes('semantic match')) return <Info className="w-4 h-4 text-blue-500" />
    return <AlertTriangle className="w-4 h-4 text-orange-500" />
  }

  const getDuplicateReasonColor = (reason: string): string => {
    if (reason.includes('exact match')) return 'bg-green-50 border-green-200 text-green-800'
    if (reason.includes('fuzzy match')) return 'bg-yellow-50 border-yellow-200 text-yellow-800'
    if (reason.includes('semantic match')) return 'bg-blue-50 border-blue-200 text-blue-800'
    return 'bg-orange-50 border-orange-200 text-orange-800'
  }

  const handleStartEdit = (duplicate: DuplicateEntityFeedback) => {
    setEditingField(duplicate.entityField)
    setEditValue(duplicate.newValue)
  }

  const handleCancelEdit = () => {
    setEditingField(null)
    setEditValue('')
  }

  const handleSaveEdit = (field: string) => {
    onResolveDuplicate(field, 'edit', editValue)
    setEditingField(null)
    setEditValue('')
  }

  if (duplicates.length === 0) {
    return null
  }

  return (
    <div className={`duplicate-entity-feedback ${className}`}>
      <Card className="border-amber-200 bg-amber-50 dark:bg-amber-900/10 dark:border-amber-800">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h4 className="font-medium text-amber-900 dark:text-amber-100">
              Ähnliche Werte erkannt
            </h4>
          </div>

          <p className="text-sm text-amber-800 dark:text-amber-200 mb-4">
            Die KI hat ähnliche oder identische Werte für bereits extrahierte Parameter erkannt.
            Möchten Sie die bestehenden Werte behalten oder aktualisieren?
          </p>

          <div className="space-y-3">
            {duplicates.map((duplicate) => (
              <Card
                key={duplicate.entityField}
                className="border border-gray-200 dark:border-gray-700"
              >
                <CardContent className="p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 dark:text-gray-100">
                        {formatFieldLabel(duplicate.entityField)}
                      </span>
                      <Badge
                        variant="outline"
                        className={`text-xs ${getDuplicateReasonColor(duplicate.duplicateReason)}`}
                      >
                        <div className="flex items-center gap-1">
                          {getDuplicateReasonIcon(duplicate.duplicateReason)}
                          {duplicate.duplicateReason}
                        </div>
                      </Badge>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <div className="space-y-1">
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Bestehender Wert:
                      </div>
                      <div className="p-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded text-sm font-mono">
                        {duplicate.existingValue}
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Neuer Wert:
                      </div>
                      {editingField === duplicate.entityField ? (
                        <div className="flex gap-1">
                          <input
                            type="text"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded text-sm font-mono bg-white dark:bg-gray-800"
                            placeholder="Wert bearbeiten..."
                          />
                          <Button
                            size="sm"
                            onClick={() => handleSaveEdit(duplicate.entityField)}
                            className="px-2"
                          >
                            <CheckCircle className="w-3 h-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={handleCancelEdit}
                            className="px-2"
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      ) : (
                        <div className="p-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded text-sm font-mono">
                          {duplicate.newValue}
                          <Badge variant="secondary" className="ml-2 text-xs">
                            {Math.round(duplicate.confidence * 100)}%
                          </Badge>
                        </div>
                      )}
                    </div>
                  </div>

                  {editingField !== duplicate.entityField && (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => onResolveDuplicate(duplicate.entityField, 'keep')}
                        className="flex-1"
                      >
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Bestehend behalten
                      </Button>

                      <Button
                        size="sm"
                        onClick={() => onResolveDuplicate(duplicate.entityField, 'update')}
                        className="flex-1"
                      >
                        <RefreshCw className="w-3 h-3 mr-1" />
                        Auf neuen Wert aktualisieren
                      </Button>

                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleStartEdit(duplicate)}
                      >
                        <Edit3 className="w-3 h-3" />
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

/**
 * Hook to manage duplicate entity feedback state
 */
export const useDuplicateEntityFeedback = () => {
  const [duplicates, setDuplicates] = React.useState<DuplicateEntityFeedback[]>([])

  const addDuplicate = (duplicate: DuplicateEntityFeedback) => {
    setDuplicates(prev => [...prev.filter(d => d.entityField !== duplicate.entityField), duplicate])
  }

  const resolveDuplicate = (entityField: string, action: 'keep' | 'update' | 'edit', newValue?: string) => {
    setDuplicates(prev => prev.filter(d => d.entityField !== entityField))

    // Return the action for the caller to handle
    return { entityField, action, newValue }
  }

  const clearDuplicates = () => {
    setDuplicates([])
  }

  return {
    duplicates,
    addDuplicate,
    resolveDuplicate,
    clearDuplicates
  }
}