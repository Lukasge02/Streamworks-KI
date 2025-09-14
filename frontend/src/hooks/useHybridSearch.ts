/**
 * useHybridSearch Hook
 * Provides seamless search experience with instant client-side filtering
 * and background server-side synchronization
 */
'use client'

import { useState, useMemo, useCallback, useRef } from 'react'
import { useDebouncedCallback } from './useDebounced'
import { XMLStream } from '@/services/xmlStreamsApi'
import { doesStreamMatchSearch } from '@/utils/streamHelpers'

interface UseHybridSearchProps {
  streams: XMLStream[]
  onBackgroundSearch?: (searchTerm: string) => void
  debounceDelay?: number
}

interface UseHybridSearchReturn {
  searchValue: string
  filteredStreams: XMLStream[]
  isBackgroundSearching: boolean
  setSearchValue: (value: string) => void
  clearSearch: () => void
}

/**
 * Hook that provides hybrid search functionality:
 * - Instant client-side filtering for immediate response
 * - Background server-side search for comprehensive results
 * - No UI blocking during input
 */
export function useHybridSearch({
  streams,
  onBackgroundSearch,
  debounceDelay = 500
}: UseHybridSearchProps): UseHybridSearchReturn {
  const [searchValue, setSearchValue] = useState('')
  const [isBackgroundSearching, setIsBackgroundSearching] = useState(false)
  const backgroundSearchRef = useRef<string>('')

  // Instant client-side filtering for immediate response
  const filteredStreams = useMemo(() => {
    if (!searchValue.trim()) {
      return streams
    }

    return streams.filter(stream => 
      doesStreamMatchSearch(stream, searchValue.trim())
    )
  }, [streams, searchValue])

  // Background server search with debouncing
  const debouncedBackgroundSearch = useDebouncedCallback(
    useCallback((searchTerm: string) => {
      if (backgroundSearchRef.current === searchTerm) {
        // Skip if already searched for this term
        return
      }

      backgroundSearchRef.current = searchTerm
      setIsBackgroundSearching(true)

      if (onBackgroundSearch) {
        onBackgroundSearch(searchTerm)
      }

      // Reset background searching state after a delay
      setTimeout(() => {
        setIsBackgroundSearching(false)
      }, 1000)
    }, [onBackgroundSearch]),
    debounceDelay
  )

  // Handle search input changes
  const handleSearchChange = useCallback((value: string) => {
    setSearchValue(value)
    
    // Trigger background search if value is significant
    if (value.trim().length >= 2) {
      debouncedBackgroundSearch(value.trim())
    }
  }, [debouncedBackgroundSearch])

  // Clear search
  const clearSearch = useCallback(() => {
    setSearchValue('')
    backgroundSearchRef.current = ''
    setIsBackgroundSearching(false)
    
    if (onBackgroundSearch) {
      onBackgroundSearch('')
    }
  }, [onBackgroundSearch])

  return {
    searchValue,
    filteredStreams,
    isBackgroundSearching,
    setSearchValue: handleSearchChange,
    clearSearch
  }
}

/**
 * Enhanced search matching with better relevance scoring
 */
export function enhancedStreamSearch(streams: XMLStream[], searchTerm: string): XMLStream[] {
  if (!searchTerm.trim()) {
    return streams
  }

  const normalizedSearch = searchTerm.toLowerCase().trim()
  
  return streams
    .map(stream => ({
      stream,
      relevance: calculateSearchRelevance(stream, normalizedSearch)
    }))
    .filter(({ relevance }) => relevance > 0)
    .sort((a, b) => b.relevance - a.relevance)
    .map(({ stream }) => stream)
}

/**
 * Calculate search relevance score for a stream
 */
function calculateSearchRelevance(stream: XMLStream, searchTerm: string): number {
  let score = 0
  const term = searchTerm.toLowerCase()

  // Exact name match gets highest score
  if (stream.stream_name.toLowerCase() === term) {
    score += 100
  }
  
  // Name starts with search term
  if (stream.stream_name.toLowerCase().startsWith(term)) {
    score += 50
  }
  
  // Name contains search term
  if (stream.stream_name.toLowerCase().includes(term)) {
    score += 25
  }

  // Description contains search term
  if (stream.description?.toLowerCase().includes(term)) {
    score += 15
  }

  // Job type match
  if (stream.job_type?.toLowerCase().includes(term)) {
    score += 10
  }

  // Status match
  if (stream.status?.toLowerCase().includes(term)) {
    score += 10
  }

  // Tags match
  if (stream.tags?.some(tag => tag.toLowerCase().includes(term))) {
    score += 8
  }

  // Creator match
  if (stream.created_by?.toLowerCase().includes(term)) {
    score += 5
  }

  return score
}