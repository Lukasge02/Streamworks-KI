/**
 * StreamFiltersPanel - Advanced filtering for stream lists
 */
'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { X, Filter } from 'lucide-react'

import { StreamFilters } from '@/services/xmlStreamsApi'

interface StreamFiltersPanelProps {
  filters: StreamFilters
  onFiltersChange: (filters: Partial<StreamFilters>) => void
  onClose: () => void
}

export const StreamFiltersPanel: React.FC<StreamFiltersPanelProps> = ({
  filters,
  onFiltersChange,
  onClose,
}) => {
  const jobTypes = [
    { value: 'standard', label: 'Standard' },
    { value: 'sap', label: 'SAP' },
    { value: 'file_transfer', label: 'File Transfer' },
    { value: 'custom', label: 'Custom' },
  ]

  const statuses = [
    { value: 'draft', label: 'Entwurf' },
    { value: 'zur_freigabe', label: 'Zur Freigabe' },
    { value: 'freigegeben', label: 'Freigegeben' },
    { value: 'abgelehnt', label: 'Abgelehnt' },
    { value: 'published', label: 'Veröffentlicht' },
    // Legacy status for backward compatibility
    { value: 'complete', label: 'Vollständig (Legacy)' },
  ]

  const handleJobTypeToggle = (jobType: string, checked: boolean) => {
    const currentTypes = filters.job_types || []
    const newTypes = checked
      ? [...currentTypes, jobType]
      : currentTypes.filter(type => type !== jobType)
    
    onFiltersChange({
      job_types: newTypes.length > 0 ? newTypes : undefined
    })
  }

  const handleStatusToggle = (status: string, checked: boolean) => {
    const currentStatuses = filters.statuses || []
    const newStatuses = checked
      ? [...currentStatuses, status]
      : currentStatuses.filter(s => s !== status)
    
    onFiltersChange({
      statuses: newStatuses.length > 0 ? newStatuses : undefined
    })
  }

  const clearFilters = () => {
    onFiltersChange({
      job_types: undefined,
      statuses: undefined,
      is_favorite: undefined,
      created_after: undefined,
      created_before: undefined,
    })
  }

  const hasActiveFilters = Boolean(
    filters.job_types?.length ||
    filters.statuses?.length ||
    filters.is_favorite !== undefined ||
    filters.created_after ||
    filters.created_before
  )

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            <span className="font-medium">Filter</span>
          </div>
          <div className="flex items-center gap-2">
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Zurücksetzen
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Job Types */}
          <div>
            <h4 className="font-medium mb-3">Job-Typ</h4>
            <div className="space-y-2">
              {jobTypes.map((jobType) => (
                <div key={jobType.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={`job-${jobType.value}`}
                    checked={filters.job_types?.includes(jobType.value) || false}
                    onCheckedChange={(checked) => 
                      handleJobTypeToggle(jobType.value, checked as boolean)
                    }
                  />
                  <label
                    htmlFor={`job-${jobType.value}`}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    {jobType.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Status */}
          <div>
            <h4 className="font-medium mb-3">Status</h4>
            <div className="space-y-2">
              {statuses.map((status) => (
                <div key={status.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={`status-${status.value}`}
                    checked={filters.statuses?.includes(status.value) || false}
                    onCheckedChange={(checked) => 
                      handleStatusToggle(status.value, checked as boolean)
                    }
                  />
                  <label
                    htmlFor={`status-${status.value}`}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                  >
                    {status.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Other Filters */}
          <div>
            <h4 className="font-medium mb-3">Weitere Filter</h4>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="favorites-only"
                  checked={filters.is_favorite === true}
                  onCheckedChange={(checked) => 
                    onFiltersChange({
                      is_favorite: checked ? true : undefined
                    })
                  }
                />
                <label
                  htmlFor="favorites-only"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Nur Favoriten
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="mt-4 pt-4 border-t">
            <div className="flex flex-wrap gap-2">
              {filters.job_types?.map((jobType) => (
                <Badge key={jobType} variant="secondary">
                  {jobTypes.find(jt => jt.value === jobType)?.label}
                  <button
                    onClick={() => handleJobTypeToggle(jobType, false)}
                    className="ml-1 hover:text-red-600"
                  >
                    ×
                  </button>
                </Badge>
              ))}
              
              {filters.statuses?.map((status) => (
                <Badge key={status} variant="secondary">
                  {statuses.find(s => s.value === status)?.label}
                  <button
                    onClick={() => handleStatusToggle(status, false)}
                    className="ml-1 hover:text-red-600"
                  >
                    ×
                  </button>
                </Badge>
              ))}
              
              {filters.is_favorite && (
                <Badge variant="secondary">
                  Favoriten
                  <button
                    onClick={() => onFiltersChange({ is_favorite: undefined })}
                    className="ml-1 hover:text-red-600"
                  >
                    ×
                  </button>
                </Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default StreamFiltersPanel