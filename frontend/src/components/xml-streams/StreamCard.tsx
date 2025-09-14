/**
 * StreamCard Component - Individual stream display with actions
 */
'use client'

import React from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import {
  Star,
  StarOff,
  MoreHorizontal,
  Edit,
  Eye,
  Copy,
  Download,
  Trash2,
  Clock,
  User,
  FileText,
  Zap,
  Database,
  FolderOpen,
  Settings,
  Send,
  CheckCircle,
  XCircle,
  Rocket,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { de } from 'date-fns/locale'

import { XMLStream } from '@/services/xmlStreamsApi'
import { cn } from '@/lib/utils'
import { getStreamStatusConfig, getJobTypeConfig, getStreamActions } from '@/utils/streamHelpers'

interface StreamCardProps {
  stream: XMLStream
  viewMode: 'grid' | 'list'
  isSelected: boolean
  onSelect: (selected: boolean) => void
  onEdit: () => void
  onView: () => void
  onDelete: () => void
  onToggleFavorite: () => void
  onDuplicate: () => void
  onExport: (format: 'xml' | 'json') => void
  // Workflow actions
  onSubmitForReview?: () => void
  onApprove?: () => void
  onReject?: () => void
  onPublish?: () => void
  userRole?: 'user' | 'expert'
}

export const StreamCard: React.FC<StreamCardProps> = ({
  stream,
  viewMode,
  isSelected,
  onSelect,
  onEdit,
  onView,
  onDelete,
  onToggleFavorite,
  onDuplicate,
  onExport,
  onSubmitForReview,
  onApprove,
  onReject,
  onPublish,
  userRole = 'user',
}) => {
  // Job type configuration
  const jobTypeIconConfig = {
    standard: Zap,
    sap: Database,
    file_transfer: FolderOpen,
    custom: Settings,
  }

  const jobTypeInfo = getJobTypeConfig(stream.job_type || 'custom')
  const statusInfo = getStreamStatusConfig(stream)
  const JobTypeIcon = jobTypeIconConfig[stream.job_type as keyof typeof jobTypeIconConfig] || Settings
  const actions = getStreamActions(stream, userRole)

  const formatDate = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), {
        addSuffix: true,
        locale: de,
      })
    } catch {
      return 'Unbekannt'
    }
  }

  if (viewMode === 'list') {
    return (
      <Card className={cn(
        "transition-all duration-200",
        isSelected && "ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-950"
      )}>
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            {/* Selection */}
            <Checkbox
              checked={isSelected}
              onCheckedChange={onSelect}
            />

            {/* Icon & Basic Info */}
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div className={cn(
                "flex items-center justify-center w-10 h-10 rounded-lg text-white",
                jobTypeInfo.color
              )}>
                <JobTypeIcon className="w-5 h-5" />
              </div>
              
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                    {stream.stream_name}
                  </h3>
                  {stream.is_favorite && (
                    <Star className="w-4 h-4 text-yellow-500 fill-current flex-shrink-0" />
                  )}
                </div>
                
                {stream.description && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                    {stream.description}
                  </p>
                )}
              </div>
            </div>

            {/* Badges */}
            <div className="flex items-center gap-2 flex-shrink-0">
              <Badge variant="outline" className="text-xs">
                {jobTypeInfo.label}
              </Badge>
              <Badge
                className={cn("text-xs", statusInfo.textColor, statusInfo.bgColor)}
              >
                {statusInfo.label}
              </Badge>
            </div>

            {/* Meta Info */}
            <div className="flex items-center gap-4 text-xs text-gray-500 flex-shrink-0">
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatDate(stream.updated_at)}
              </div>
              
              {stream.tags && stream.tags.length > 0 && (
                <div className="flex items-center gap-1">
                  <span>{stream.tags.length} Tags</span>
                </div>
              )}
              
              <div className="flex items-center gap-1">
                <span>v{stream.version}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 flex-shrink-0">
              <Button
                size="sm"
                variant="ghost"
                onClick={onToggleFavorite}
                className="h-8 w-8 p-0"
              >
                {stream.is_favorite ? (
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                ) : (
                  <StarOff className="w-4 h-4 text-gray-400" />
                )}
              </Button>

              <Button
                size="sm"
                variant="outline"
                onClick={onView}
              >
                <Eye className="w-4 h-4 mr-2" />
                Anzeigen
              </Button>

              <Button
                size="sm"
                onClick={onEdit}
              >
                <Edit className="w-4 h-4 mr-2" />
                Bearbeiten
              </Button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button size="sm" variant="ghost" className="h-8 w-8 p-0">
                    <MoreHorizontal className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {/* Workflow Actions */}
                  {actions.canSubmitForReview && onSubmitForReview && (
                    <>
                      <DropdownMenuItem onClick={onSubmitForReview}>
                        <Send className="w-4 h-4 mr-2" />
                        Zur Freigabe einreichen
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                    </>
                  )}
                  {actions.canApprove && onApprove && (
                    <DropdownMenuItem onClick={onApprove} className="text-green-600 focus:text-green-600">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Freigeben
                    </DropdownMenuItem>
                  )}
                  {actions.canReject && onReject && (
                    <DropdownMenuItem onClick={onReject} className="text-orange-600 focus:text-orange-600">
                      <XCircle className="w-4 h-4 mr-2" />
                      Ablehnen
                    </DropdownMenuItem>
                  )}
                  {actions.canPublish && onPublish && (
                    <DropdownMenuItem onClick={onPublish} className="text-blue-600 focus:text-blue-600">
                      <Rocket className="w-4 h-4 mr-2" />
                      Veröffentlichen
                    </DropdownMenuItem>
                  )}
                  {(actions.canApprove || actions.canReject || actions.canPublish) && (
                    <DropdownMenuSeparator />
                  )}

                  {/* Standard Actions */}
                  {actions.canDuplicate && (
                    <DropdownMenuItem onClick={onDuplicate}>
                      <Copy className="w-4 h-4 mr-2" />
                      Duplizieren
                    </DropdownMenuItem>
                  )}
                  {actions.canExport && (
                    <>
                      <DropdownMenuItem onClick={() => onExport('xml')}>
                        <Download className="w-4 h-4 mr-2" />
                        Als XML exportieren
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => onExport('json')}>
                        <Download className="w-4 h-4 mr-2" />
                        Als JSON exportieren
                      </DropdownMenuItem>
                    </>
                  )}
                  {actions.canDelete && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={onDelete}
                        className="text-red-600 focus:text-red-600"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Löschen
                      </DropdownMenuItem>
                    </>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Grid view
  return (
    <Card className={cn(
      "group relative transition-all duration-200 hover:shadow-md",
      isSelected && "ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-950"
    )}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <Checkbox
              checked={isSelected}
              onCheckedChange={onSelect}
              className="mt-1"
            />
            
            <div className={cn(
              "flex items-center justify-center w-10 h-10 rounded-lg text-white",
              jobTypeInfo.color
            )}>
              <JobTypeIcon className="w-5 h-5" />
            </div>
          </div>

          <div className="flex items-center gap-1">
            <Button
              size="sm"
              variant="ghost"
              onClick={onToggleFavorite}
              className="h-8 w-8 p-0 opacity-60 group-hover:opacity-100 transition-opacity"
            >
              {stream.is_favorite ? (
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
              ) : (
                <StarOff className="w-4 h-4 text-gray-400" />
              )}
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  size="sm" 
                  variant="ghost" 
                  className="h-8 w-8 p-0 opacity-60 group-hover:opacity-100 transition-opacity"
                >
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {/* Main Actions */}
                {actions.canView && (
                  <DropdownMenuItem onClick={onView}>
                    <Eye className="w-4 h-4 mr-2" />
                    Anzeigen
                  </DropdownMenuItem>
                )}
                {actions.canEdit && (
                  <DropdownMenuItem onClick={onEdit}>
                    <Edit className="w-4 h-4 mr-2" />
                    Bearbeiten
                  </DropdownMenuItem>
                )}
                {(actions.canView || actions.canEdit) && <DropdownMenuSeparator />}

                {/* Workflow Actions */}
                {actions.canSubmitForReview && onSubmitForReview && (
                  <>
                    <DropdownMenuItem onClick={onSubmitForReview}>
                      <Send className="w-4 h-4 mr-2" />
                      Zur Freigabe einreichen
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                  </>
                )}
                {actions.canApprove && onApprove && (
                  <DropdownMenuItem onClick={onApprove} className="text-green-600 focus:text-green-600">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Freigeben
                  </DropdownMenuItem>
                )}
                {actions.canReject && onReject && (
                  <DropdownMenuItem onClick={onReject} className="text-orange-600 focus:text-orange-600">
                    <XCircle className="w-4 h-4 mr-2" />
                    Ablehnen
                  </DropdownMenuItem>
                )}
                {actions.canPublish && onPublish && (
                  <DropdownMenuItem onClick={onPublish} className="text-blue-600 focus:text-blue-600">
                    <Rocket className="w-4 h-4 mr-2" />
                    Veröffentlichen
                  </DropdownMenuItem>
                )}
                {(actions.canApprove || actions.canReject || actions.canPublish) && (
                  <DropdownMenuSeparator />
                )}

                {/* Standard Actions */}
                {actions.canDuplicate && (
                  <DropdownMenuItem onClick={onDuplicate}>
                    <Copy className="w-4 h-4 mr-2" />
                    Duplizieren
                  </DropdownMenuItem>
                )}
                {actions.canExport && (
                  <>
                    <DropdownMenuItem onClick={() => onExport('xml')}>
                      <Download className="w-4 h-4 mr-2" />
                      Als XML exportieren
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => onExport('json')}>
                      <Download className="w-4 h-4 mr-2" />
                      Als JSON exportieren
                    </DropdownMenuItem>
                  </>
                )}
                {actions.canDelete && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      onClick={onDelete}
                      className="text-red-600 focus:text-red-600"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Löschen
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <div className="mt-3">
          <h3 className="font-semibold text-gray-900 dark:text-white line-clamp-2 mb-1">
            {stream.stream_name}
          </h3>
          
          {stream.description && (
            <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
              {stream.description}
            </p>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Badges */}
        <div className="flex items-center gap-2 mb-3">
          <Badge variant="outline" className="text-xs">
            {jobTypeInfo.label}
          </Badge>
          <Badge
            className={cn("text-xs", statusInfo.textColor, statusInfo.bgColor)}
          >
            {statusInfo.label}
          </Badge>
        </div>

        {/* Tags */}
        {stream.tags && stream.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {stream.tags.slice(0, 3).map((tag) => (
              <Badge 
                key={tag} 
                variant="secondary" 
                className="text-xs py-0 px-2"
              >
                {tag}
              </Badge>
            ))}
            {stream.tags.length > 3 && (
              <Badge variant="secondary" className="text-xs py-0 px-2">
                +{stream.tags.length - 3}
              </Badge>
            )}
          </div>
        )}

        {/* Meta Info */}
        <div className="space-y-2 text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>{formatDate(stream.updated_at)}</span>
          </div>
          
          {stream.last_generated_at && (
            <div className="flex items-center gap-1">
              <FileText className="w-3 h-3" />
              <span>XML: {formatDate(stream.last_generated_at)}</span>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1">
              <User className="w-3 h-3" />
              <span>{stream.created_by}</span>
            </div>
            <span>v{stream.version}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-4">
          <Button
            size="sm"
            variant="outline"
            onClick={onView}
            className="flex-1"
          >
            <Eye className="w-4 h-4 mr-2" />
            Anzeigen
          </Button>
          <Button
            size="sm"
            onClick={onEdit}
            className="flex-1"
          >
            <Edit className="w-4 h-4 mr-2" />
            Bearbeiten
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default StreamCard