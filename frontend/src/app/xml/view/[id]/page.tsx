'use client'

import { useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import {
  Edit,
  Download,
  Copy,
  ArrowLeft,
  Star,
  Loader2,
  FileText,
  Clock,
  User,
  Zap,
  Database,
  FolderOpen,
  Settings,
  ChevronDown,
  ExternalLink
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { de } from 'date-fns/locale'
import { useRouter } from 'next/navigation'

import {
  useStream,
  useToggleFavorite,
  useExportStream,
  useSubmitForReview,
  useApproveStream,
  useRejectStream,
  usePublishStream
} from '@/hooks/useXMLStreams'
import { WorkflowStatusBadge } from '@/components/xml-streams/WorkflowStatusBadge'
import { WizardDataRenderer } from '@/components/xml-streams/WizardDataRenderer'
import { cn } from '@/lib/utils'
import { getJobTypeConfig } from '@/utils/streamHelpers'

export default function ViewStreamPage() {
  const params = useParams()
  const router = useRouter()
  const streamId = params.id as string

  const { data: stream, isLoading, error } = useStream(streamId)
  const toggleFavorite = useToggleFavorite()
  const exportStream = useExportStream()

  // Workflow hooks
  const submitForReview = useSubmitForReview()
  const approveStream = useApproveStream()
  const rejectStream = useRejectStream()
  const publishStream = usePublishStream()

  // TODO: Get user role from auth context - temporarily set to 'expert' for testing
  const userRole: 'user' | 'expert' = 'expert'

  useEffect(() => {
    // Set page title
    document.title = stream
      ? `${stream.stream_name} | Streamworks`
      : 'Stream anzeigen | Streamworks'
  }, [stream])

  // Using helpers for consistent configuration
  const jobTypeConfig = {
    standard: { icon: Zap, ...getJobTypeConfig('standard') },
    sap: { icon: Database, ...getJobTypeConfig('sap') },
    file_transfer: { icon: FolderOpen, ...getJobTypeConfig('file_transfer') },
    custom: { icon: Settings, ...getJobTypeConfig('custom') },
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex items-center gap-2">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Stream wird geladen...</span>
        </div>
      </div>
    )
  }

  if (error || !stream) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">
            {error?.message || 'Stream nicht gefunden'}
          </p>
          <Button onClick={() => router.push('/xml')} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Zurück zur Stream-Liste
          </Button>
        </div>
      </div>
    )
  }

  const jobTypeInfo = jobTypeConfig[stream.job_type as keyof typeof jobTypeConfig] || jobTypeConfig.custom
  const JobTypeIcon = jobTypeInfo.icon

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

  const handleEdit = () => {
    router.push(`/xml/edit/${streamId}`)
  }

  const handleExport = (format: 'xml' | 'json' | 'pdf') => {
    console.log('📥 Export clicked:', format, 'for stream:', streamId)
    if (format === 'pdf') {
      // PDF export would generate a formatted document with stream config
      console.log('📄 PDF export not yet implemented')
      alert('PDF-Export wird in einer zukünftigen Version verfügbar sein.')
      return
    }
    console.log('🚀 Starting export with:', { streamId, format })
    exportStream.mutate({ streamId, format })
  }

  const handleToggleFavorite = () => {
    toggleFavorite.mutate(streamId)
  }

  // Workflow handlers
  const handleSubmitForReview = async () => {
    if (confirm(`Möchten Sie den Stream "${stream.stream_name}" zur Freigabe einreichen?`)) {
      await submitForReview.mutateAsync(streamId)
    }
  }

  const handleApprove = async () => {
    if (confirm(`Möchten Sie den Stream "${stream.stream_name}" freigeben?`)) {
      await approveStream.mutateAsync(streamId)
    }
  }

  const handleReject = async () => {
    const reason = prompt(`Grund für die Ablehnung des Streams "${stream.stream_name}":`)
    if (reason && reason.trim()) {
      await rejectStream.mutateAsync({ streamId, reason: reason.trim() })
    }
  }

  const handlePublish = async () => {
    if (confirm(`Möchten Sie den Stream "${stream.stream_name}" veröffentlichen? Dies macht ihn produktiv verfügbar.`)) {
      await publishStream.mutateAsync(streamId)
    }
  }

  // Enhanced Debug logging for wizard_data integration
  console.log('🔍 ViewStreamPage Debug:', {
    streamId,
    userRole,
    stream: stream ? {
      id: stream.id,
      name: stream.stream_name,
      status: stream.status,
      job_type: stream.job_type,
      wizard_data: stream.wizard_data,
      hasWizardData: !!stream.wizard_data && Object.keys(stream.wizard_data || {}).length > 0,
      wizardDataKeys: stream.wizard_data ? Object.keys(stream.wizard_data) : [],
      created_at: stream.created_at,
      updated_at: stream.updated_at
    } : null,
    isLoading,
    error: error ? (error as Error)?.message || 'An error occurred' : null
  })

  return (
    <div className="container mx-auto px-4 py-6 max-w-6xl">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button onClick={() => router.push('/xml')} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Zurück
          </Button>

          <div className={cn(
            "flex items-center justify-center w-12 h-12 rounded-lg text-white",
            jobTypeInfo.color
          )}>
            <JobTypeIcon className="w-6 h-6" />
          </div>

          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {stream.stream_name}
              </h1>
              <Button
                size="sm"
                variant="ghost"
                onClick={handleToggleFavorite}
                disabled={toggleFavorite.isPending}
              >
                <Star className={cn(
                  "w-5 h-5",
                  stream.is_favorite ? "text-yellow-500 fill-current" : "text-gray-400"
                )} />
              </Button>
            </div>

            {stream.description && (
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                {stream.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Edit Button */}
          <Button onClick={handleEdit} variant="outline">
            <Edit className="w-4 h-4 mr-2" />
            Bearbeiten
          </Button>

          {/* Export Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Exportieren
                <ChevronDown className="w-4 h-4 ml-2" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleExport('xml')}>
                <FileText className="w-4 h-4 mr-2" />
                Als XML exportieren
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleExport('json')}>
                <FileText className="w-4 h-4 mr-2" />
                Als JSON exportieren
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleExport('pdf')}>
                <ExternalLink className="w-4 h-4 mr-2" />
                Als PDF dokumentieren
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Status Badge with Workflow Actions */}
          <WorkflowStatusBadge
            stream={stream}
            userRole={userRole}
            onSubmitForReview={handleSubmitForReview}
            onApprove={handleApprove}
            onReject={handleReject}
            onPublish={handlePublish}
          />
        </div>
      </div>

      {/* Jira-style Layout: Main content + Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content Area (70%) */}
        <div className="lg:col-span-3 space-y-6">
          {/* Stream Configuration Data */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Stream-Konfiguration
            </h2>
            <WizardDataRenderer stream={stream} />
          </div>

          {/* XML Content Preview */}
          {stream.xml_content && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Generierter XML-Inhalt
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4 max-h-96 overflow-auto">
                  <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
                    {stream.xml_content}
                  </pre>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigator.clipboard.writeText(stream.xml_content!)}
                  >
                    <Copy className="w-4 h-4 mr-2" />
                    Kopieren
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleExport('xml')}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar: Basic Info + Activity (30%) */}
        <div className="space-y-4">
          {/* Basic Information */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Grundinformationen</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Job-Typ</span>
                  <Badge variant="outline" className="text-xs">{jobTypeInfo.label}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Erstellt von</span>
                  <div className="flex items-center gap-1 text-sm">
                    <User className="w-3 h-3 text-gray-400" />
                    <span className="text-xs">{stream.created_by}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Version</span>
                  <span className="text-xs font-medium">{stream.version}</span>
                </div>
              </div>

              {stream.tags && stream.tags.length > 0 && (
                <div className="mt-4 pt-3 border-t">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm text-gray-500">Tags</span>
                    <Badge variant="secondary" className="text-xs">{stream.tags.length}</Badge>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {stream.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                    ))}
                    {stream.tags.length > 3 && (
                      <Badge variant="secondary" className="text-xs">+{stream.tags.length - 3}</Badge>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Activity Information */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Aktivität</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="w-3 h-3 text-gray-400" />
                    <span className="text-sm text-gray-500">Erstellt</span>
                  </div>
                  <span className="text-xs">{formatDate(stream.created_at)}</span>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="w-3 h-3 text-gray-400" />
                    <span className="text-sm text-gray-500">Bearbeitet</span>
                  </div>
                  <span className="text-xs">{formatDate(stream.updated_at)}</span>
                </div>

                {stream.last_generated_at && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FileText className="w-3 h-3 text-gray-400" />
                      <span className="text-sm text-gray-500">XML generiert</span>
                    </div>
                    <span className="text-xs">{formatDate(stream.last_generated_at)}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}