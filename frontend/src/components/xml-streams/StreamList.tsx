/**
 * StreamList Component - Main XML streams listing with filtering and management
 */
'use client'

import React, { useState, useMemo, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal,
  Star,
  StarOff,
  Copy,
  Download,
  Trash2,
  Edit,
  FileText,
  Clock,
  User,
  Zap,
  Database,
  FolderOpen,
  Settings,
  SortAsc,
  SortDesc,
  RefreshCw,
  Grid,
  List as ListIcon
} from 'lucide-react'
import { useRouter } from 'next/navigation'
import { formatDistanceToNow } from 'date-fns'
import { de } from 'date-fns/locale'

import {
  useStreamList,
  useDeleteStream,
  useToggleFavorite,
  useDuplicateStream,
  useExportStream,
  useBulkOperations,
  useSubmitForReview,
  useApproveStream,
  useRejectStream,
  usePublishStream
} from '@/hooks/useXMLStreams'
import { XMLStream, StreamFilters } from '@/services/xmlStreamsApi'
import { StreamCard } from './StreamCard'
import { StreamFiltersPanel } from './StreamFiltersPanel'
import { cn } from '@/lib/utils'
import { usePersistedViewMode, usePersistedSortBy, usePersistedFiltersVisible } from '@/hooks/usePersistedState'
import { useHybridSearch, enhancedStreamSearch } from '@/hooks/useHybridSearch'

interface StreamListProps {
  className?: string
}

type ViewMode = 'grid' | 'list'
type SortBy = 'updated_desc' | 'updated_asc' | 'created_desc' | 'created_asc' | 'name_asc' | 'name_desc' | 'favorites_first'

export const StreamList: React.FC<StreamListProps> = ({ className }) => {
  const router = useRouter()
  
  // State with persistence
  const [filters, setFilters] = useState<StreamFilters>({})
  const [sortBy, setSortBy] = usePersistedSortBy('updated_desc')
  const [viewMode, setViewMode] = usePersistedViewMode('grid')
  const [selectedStreams, setSelectedStreams] = useState<Set<string>>(new Set())
  const [showFilters, setShowFilters] = usePersistedFiltersVisible(false)
  const [currentPage, setCurrentPage] = useState(0)
  
  // Background search callback 
  const handleBackgroundSearch = useCallback((searchTerm: string) => {
    setFilters(prev => ({ ...prev, search: searchTerm || undefined }))
  }, [])
  
  const limit = 20
  const offset = currentPage * limit

  // Hooks
  const {
    data: streamsData,
    isLoading,
    error,
    refetch,
    isFetching
  } = useStreamList(filters, sortBy, limit, offset, {
    refetchInterval: 30000 // Refresh every 30 seconds
  })

  // Computed values - Must be declared before useHybridSearch
  const streams = streamsData?.streams || []

  // Use hybrid search for seamless UX
  const {
    searchValue,
    filteredStreams,
    isBackgroundSearching,
    setSearchValue,
    clearSearch
  } = useHybridSearch({
    streams,
    onBackgroundSearch: handleBackgroundSearch,
    debounceDelay: 500
  })

  // Enhanced local search with relevance scoring
  const displayStreams = useMemo(() => {
    return enhancedStreamSearch(filteredStreams, searchValue)
  }, [filteredStreams, searchValue])

  const deleteStream = useDeleteStream()
  const toggleFavorite = useToggleFavorite()
  const duplicateStream = useDuplicateStream()
  const exportStream = useExportStream()
  const { bulkDelete, bulkToggleFavorite } = useBulkOperations()

  // Workflow hooks
  const submitForReview = useSubmitForReview()
  const approveStream = useApproveStream()
  const rejectStream = useRejectStream()
  const publishStream = usePublishStream()
  const totalCount = streamsData?.total_count || 0
  const hasMore = streamsData?.has_more || false
  const isAllSelected = selectedStreams.size === streams.length && streams.length > 0
  const isSomeSelected = selectedStreams.size > 0 && selectedStreams.size < streams.length

  // Job type icon mapping
  const jobTypeIcons = {
    standard: Zap,
    sap: Database,
    file_transfer: FolderOpen,
    custom: Settings,
  }

  const jobTypeLabels = {
    STANDARD: '⚙️ Standard Job',
    SAP: '🏢 SAP Integration',
    FILE_TRANSFER: '📁 Datentransfer',
    UNKNOWN: '❓ Typ nicht erkannt',
    // Legacy support
    standard: '⚙️ Standard Job',
    sap: '🏢 SAP Integration',
    file_transfer: '📁 Datentransfer',
    custom: '❓ Typ nicht erkannt',
  }

  const statusColors = {
    parameter_complete: 'bg-green-600',
    parameter_partial: 'bg-blue-500',
    parameter_minimal: 'bg-yellow-500',
    parameter_empty: 'bg-gray-400',
    // Legacy support
    draft: 'bg-gray-400',
    complete: 'bg-green-600',
    published: 'bg-green-600',
  }

  const statusLabels = {
    parameter_complete: 'Parameter vollständig',
    parameter_partial: 'Grundkonfiguration',
    parameter_minimal: 'Erste Parameter',
    parameter_empty: 'Neue Session',
    // Legacy support
    draft: 'Neue Session',
    complete: 'Parameter vollständig',
    published: 'Parameter vollständig',
  }

  // Event handlers
  const handleCreateStream = async () => {
    try {
      // Neue LangExtract Session erstellen
      const response = await fetch('/api/streamworks/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}) // Ohne spezifischen job_type, lässt AI erkennen
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const newSession = await response.json()

      // Direkt zu LangExtract mit neuer Session weiterleiten
      router.push(`/langextract?sessionId=${newSession.session_id}`)
    } catch (error) {
      console.error('Fehler beim Erstellen einer neuen Session:', error)
      // Fallback: Gehe zu LangExtract ohne Session-ID (erstellt neue Session dort)
      router.push('/langextract')
    }
  }

  const handleEditStream = (stream: XMLStream) => {
    // Redirect to LangExtract with stream ID for parameter editing
    router.push(`/langextract?streamId=${stream.id}`)
  }

  const handleViewStream = (stream: XMLStream) => {
    // Redirect to XML Stream viewer for read-only display
    router.push(`/xml/stream/${stream.id}`)
  }

  const handleDeleteStream = async (stream: XMLStream) => {
    if (confirm(`Möchten Sie den Stream "${stream.stream_name}" wirklich löschen?`)) {
      await deleteStream.mutateAsync(stream.id)
      setSelectedStreams(prev => {
        const next = new Set(prev)
        next.delete(stream.id)
        return next
      })
    }
  }

  const handleToggleFavorite = async (stream: XMLStream) => {
    await toggleFavorite.mutateAsync(stream.id)
  }

  const handleDuplicateStream = async (stream: XMLStream) => {
    await duplicateStream.mutateAsync({ 
      streamId: stream.id, 
      newName: `${stream.stream_name} (Kopie)` 
    })
  }

  const handleExportStream = async (stream: XMLStream, format: 'xml' | 'json' = 'xml') => {
    await exportStream.mutateAsync({ streamId: stream.id, format })
  }

  const handleSelectStream = (streamId: string, selected: boolean) => {
    setSelectedStreams(prev => {
      const next = new Set(prev)
      if (selected) {
        next.add(streamId)
      } else {
        next.delete(streamId)
      }
      return next
    })
  }

  const handleSelectAll = (selected: boolean) => {
    if (selected) {
      setSelectedStreams(new Set(streams.map(s => s.id)))
    } else {
      setSelectedStreams(new Set())
    }
  }

  const handleBulkDelete = async () => {
    if (selectedStreams.size === 0) return
    
    if (confirm(`Möchten Sie ${selectedStreams.size} Stream(s) wirklich löschen?`)) {
      await bulkDelete.mutateAsync(Array.from(selectedStreams))
      setSelectedStreams(new Set())
    }
  }

  const handleBulkToggleFavorite = async () => {
    if (selectedStreams.size === 0) return

    await bulkToggleFavorite.mutateAsync(Array.from(selectedStreams))
    setSelectedStreams(new Set())
  }

  // Workflow handlers
  const handleSubmitForReview = async (stream: XMLStream) => {
    if (confirm(`Möchten Sie den Stream "${stream.stream_name}" zur Freigabe einreichen?`)) {
      await submitForReview.mutateAsync(stream.id)
    }
  }

  const handleApprove = async (stream: XMLStream) => {
    if (confirm(`Möchten Sie den Stream "${stream.stream_name}" freigeben?`)) {
      await approveStream.mutateAsync(stream.id)
    }
  }

  const handleReject = async (stream: XMLStream) => {
    const reason = prompt(`Grund für die Ablehnung des Streams "${stream.stream_name}":`)
    if (reason && reason.trim()) {
      await rejectStream.mutateAsync({ streamId: stream.id, reason: reason.trim() })
    }
  }

  const handlePublish = async (stream: XMLStream) => {
    if (confirm(`Möchten Sie den Stream "${stream.stream_name}" veröffentlichen? Dies macht ihn produktiv verfügbar.`)) {
      await publishStream.mutateAsync(stream.id)
    }
  }

  const handleSearchChange = useCallback((value: string) => {
    setSearchValue(value)
    setCurrentPage(0) // Reset to first page
  }, [setSearchValue])

  const handleFilterChange = (newFilters: Partial<StreamFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
    setCurrentPage(0)
  }

  const handleSortChange = (newSortBy: SortBy) => {
    setSortBy(newSortBy)
    setCurrentPage(0)
  }

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage)
    setSelectedStreams(new Set()) // Clear selection on page change
  }

  // Render loading state  
  if (isLoading && streams.length === 0) {
    return (
      <div className={cn("flex items-center justify-center h-64", className)}>
        <RefreshCw className="w-6 h-6 animate-spin text-gray-500" />
        <span className="ml-2 text-gray-500">Streams werden geladen...</span>
      </div>
    )
  }
  
  // Show search indicator for background search
  const showSearchIndicator = isBackgroundSearching && searchValue.length > 0

  // Render error state
  if (error) {
    return (
      <div className={cn("flex flex-col items-center justify-center h-64", className)}>
        <div className="text-red-500 mb-4">
          <FileText className="w-12 h-12" />
        </div>
        <p className="text-red-600 mb-4">Fehler beim Laden der Streams</p>
        <p className="text-sm text-gray-500 mb-4">{error.message}</p>
        <Button onClick={() => refetch()} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Erneut versuchen
        </Button>
      </div>
    )
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            XML Streams
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Verwalten Sie Ihre XML Stream-Konfigurationen
            {totalCount > 0 && (
              <span className="ml-2">
                ({totalCount} Stream{totalCount !== 1 ? 's' : ''})
              </span>
            )}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            onClick={() => refetch()}
            variant="outline"
            size="sm"
            disabled={isFetching}
          >
            <RefreshCw className={cn("w-4 h-4", isFetching && "animate-spin")} />
          </Button>
          
          <Button onClick={handleCreateStream} className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Stream erstellen
          </Button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Streams durchsuchen..."
            value={searchValue}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10"
          />
          {showSearchIndicator && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <RefreshCw className="w-4 h-4 animate-spin text-gray-400" />
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          {/* Filters */}
          <Button
            variant={showFilters ? "default" : "outline"}
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>

          {/* Sort */}
          <Select value={sortBy} onValueChange={handleSortChange}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="updated_desc">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-2" />
                  Zuletzt bearbeitet
                </div>
              </SelectItem>
              <SelectItem value="updated_asc">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-2" />
                  Älteste zuerst
                </div>
              </SelectItem>
              <SelectItem value="name_asc">
                <div className="flex items-center">
                  <SortAsc className="w-4 h-4 mr-2" />
                  Name A-Z
                </div>
              </SelectItem>
              <SelectItem value="name_desc">
                <div className="flex items-center">
                  <SortDesc className="w-4 h-4 mr-2" />
                  Name Z-A
                </div>
              </SelectItem>
              <SelectItem value="favorites_first">
                <div className="flex items-center">
                  <Star className="w-4 h-4 mr-2" />
                  Favoriten zuerst
                </div>
              </SelectItem>
            </SelectContent>
          </Select>

          {/* View Mode */}
          <div className="flex border rounded-md">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
              className="rounded-r-none"
            >
              <Grid className="w-4 h-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className="rounded-l-none"
            >
              <ListIcon className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <StreamFiltersPanel
          filters={filters}
          onFiltersChange={handleFilterChange}
          onClose={() => setShowFilters(false)}
        />
      )}

      {/* Bulk Actions */}
      {selectedStreams.size > 0 && (
        <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <CardContent className="py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Checkbox
                  checked={isAllSelected}
                  onCheckedChange={handleSelectAll}
                  ref={(el) => {
                    if (el) {
                      el.indeterminate = isSomeSelected
                    }
                  }}
                />
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                  {selectedStreams.size} Stream{selectedStreams.size !== 1 ? 's' : ''} ausgewählt
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleBulkToggleFavorite}
                  disabled={bulkToggleFavorite.isPending}
                >
                  <Star className="w-4 h-4 mr-2" />
                  Favoriten umschalten
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleBulkDelete}
                  disabled={bulkDelete.isPending}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Löschen
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stream List/Grid */}
      {displayStreams.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Keine Streams gefunden
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            {searchValue.length > 0
              ? `Keine Streams für "${searchValue}" gefunden. Versuchen Sie andere Suchbegriffe.`
              : Object.keys(filters).length > 0 
              ? "Versuchen Sie, die Filter zu ändern oder zu entfernen."
              : "Erstellen Sie Ihren ersten XML Stream, um loszulegen."
            }
          </p>
          <Button onClick={handleCreateStream}>
            <Plus className="w-4 h-4 mr-2" />
            Stream erstellen
          </Button>
        </div>
      ) : (
        <>
          <div className={cn(
            viewMode === 'grid'
              ? "grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
              : "space-y-2"
          )}>
            {displayStreams.map((stream) => (
              <StreamCard
                key={stream.id}
                stream={stream}
                viewMode={viewMode}
                isSelected={selectedStreams.has(stream.id)}
                onSelect={(selected) => handleSelectStream(stream.id, selected)}
                onEdit={() => handleEditStream(stream)}
                onView={() => handleViewStream(stream)}
                onDelete={() => handleDeleteStream(stream)}
                onToggleFavorite={() => handleToggleFavorite(stream)}
                onDuplicate={() => handleDuplicateStream(stream)}
                onExport={(format) => handleExportStream(stream, format)}
                onSubmitForReview={() => handleSubmitForReview(stream)}
                onApprove={() => handleApprove(stream)}
                onReject={() => handleReject(stream)}
                onPublish={() => handlePublish(stream)}
                userRole="user"
              />
            ))}
          </div>

          {/* Pagination - only show if not searching locally */}
          {!searchValue && totalCount > limit && (
            <div className="flex items-center justify-between pt-4">
              <div className="text-sm text-gray-500">
                Zeige {offset + 1} bis {Math.min(offset + limit, totalCount)} von {totalCount} Streams
              </div>
              
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 0}
                >
                  Zurück
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={!hasMore}
                >
                  Weiter
                </Button>
              </div>
            </div>
          )}
        </>
      )}

    </div>
  )
}

export default StreamList