/**
 * Document Navigation Hook
 * Handles navigation to documents with source highlighting and context
 */

import { useState, useCallback } from 'react'
import { toast } from 'sonner'
import { useRouter } from 'next/navigation'

// Types
interface SourceReference {
  document_id: string
  filename: string
  page_number?: number
  section?: string
  relevance_score: number
  snippet: string
  chunk_index: number
  confidence: number
  doc_type?: string
  chunk_id?: string
}

interface NavigationOptions {
  openInNewTab?: boolean
  highlightText?: string
  focusChunk?: boolean
  showContext?: boolean
}

interface NavigationResult {
  success: boolean
  url?: string
  error?: string
}

interface UseDocumentNavigationReturn {
  navigateToSource: (source: SourceReference, options?: NavigationOptions) => Promise<NavigationResult>
  navigateToDocument: (documentId: string, options?: NavigationOptions) => Promise<NavigationResult>
  isNavigating: boolean
  lastNavigation: NavigationResult | null
}

export function useDocumentNavigation(): UseDocumentNavigationReturn {
  const [isNavigating, setIsNavigating] = useState(false)
  const [lastNavigation, setLastNavigation] = useState<NavigationResult | null>(null)
  const router = useRouter()

  /**
   * Generate navigation URL for a document source
   */
  const generateNavigationUrl = useCallback(async (
    source: SourceReference,
    options: NavigationOptions = {}
  ): Promise<string> => {
    try {
      // Call backend API to generate proper navigation URL
      const response = await fetch('/api/rag-metrics/navigate-to-source', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: source.document_id,
          page_number: source.page_number,
          chunk_id: source.chunk_id,
          highlight_text: options.highlightText || source.snippet.substring(0, 50)
        })
      })

      if (!response.ok) {
        throw new Error('Failed to generate navigation URL')
      }

      const result = await response.json()
      if (result.success) {
        return result.document_url
      } else {
        throw new Error(result.error || 'Navigation failed')
      }
    } catch (error) {
      console.warn('API navigation failed, using fallback URL:', error)

      // Fallback to constructing URL manually
      return buildFallbackUrl(source, options)
    }
  }, [])

  /**
   * Build fallback URL when API is unavailable
   */
  const buildFallbackUrl = useCallback((
    source: SourceReference,
    options: NavigationOptions = {}
  ): string => {
    let url = `/documents/${source.document_id}`
    const params = new URLSearchParams()

    // Add navigation parameters
    if (source.page_number) {
      params.append('page', source.page_number.toString())
    }

    if (source.chunk_id) {
      params.append('chunk', source.chunk_id)
    }

    if (options.highlightText || source.snippet) {
      const textToHighlight = options.highlightText || source.snippet.substring(0, 100)
      params.append('highlight', encodeURIComponent(textToHighlight))
    }

    if (options.showContext) {
      params.append('context', 'true')
    }

    if (options.focusChunk) {
      params.append('focus', 'chunk')
    }

    // Add source metadata for context
    params.append('from', 'rag')
    params.append('relevance', source.relevance_score.toString())

    if (params.toString()) {
      url += '?' + params.toString()
    }

    return url
  }, [])

  /**
   * Navigate to a document source with highlighting and context
   */
  const navigateToSource = useCallback(async (
    source: SourceReference,
    options: NavigationOptions = {}
  ): Promise<NavigationResult> => {
    setIsNavigating(true)

    try {
      // Generate navigation URL
      const url = await generateNavigationUrl(source, options)

      // Navigate to document
      if (options.openInNewTab !== false) {
        // Open in new tab by default
        window.open(url, '_blank')
      } else {
        // Navigate in same tab
        router.push(url)
      }

      // Show success toast
      toast.success(`📄 Öffne: ${source.filename}`)

      const result: NavigationResult = {
        success: true,
        url
      }

      setLastNavigation(result)
      return result

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Navigation failed'

      toast.error(`Fehler beim Öffnen: ${errorMessage}`)

      const result: NavigationResult = {
        success: false,
        error: errorMessage
      }

      setLastNavigation(result)
      return result

    } finally {
      setIsNavigating(false)
    }
  }, [generateNavigationUrl, router])

  /**
   * Navigate to a document by ID (without source context)
   */
  const navigateToDocument = useCallback(async (
    documentId: string,
    options: NavigationOptions = {}
  ): Promise<NavigationResult> => {
    setIsNavigating(true)

    try {
      let url = `/documents/${documentId}`
      const params = new URLSearchParams()

      if (options.highlightText) {
        params.append('highlight', encodeURIComponent(options.highlightText))
      }

      if (options.showContext) {
        params.append('context', 'true')
      }

      if (params.toString()) {
        url += '?' + params.toString()
      }

      // Navigate to document
      if (options.openInNewTab !== false) {
        window.open(url, '_blank')
      } else {
        router.push(url)
      }

      toast.success('📄 Dokument geöffnet')

      const result: NavigationResult = {
        success: true,
        url
      }

      setLastNavigation(result)
      return result

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Navigation failed'

      toast.error(`Fehler beim Öffnen: ${errorMessage}`)

      const result: NavigationResult = {
        success: false,
        error: errorMessage
      }

      setLastNavigation(result)
      return result

    } finally {
      setIsNavigating(false)
    }
  }, [router])

  return {
    navigateToSource,
    navigateToDocument,
    isNavigating,
    lastNavigation
  }
}