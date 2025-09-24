'use client'

import { useParams, useSearchParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { StreamXMLLayout } from '@/components/stream-xml/StreamXMLLayout'
import { XMLErrorState } from '@/components/stream-xml/XMLErrorState'
import { XMLLoadingState } from '@/components/stream-xml/XMLLoadingState'
import { useLangExtractChat } from '@/components/langextract-chat/hooks/useLangExtractChat'
import { toast } from 'sonner'

/**
 * 🚀 XML Stream Editor Page
 *
 * Dedicated page for editing and managing generated XML streams
 * with Monaco editor and enhanced parameter controls
 */
export default function XMLStreamPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const router = useRouter()
  const sessionId = params.sessionId as string

  const [isLoading, setIsLoading] = useState(true)
  const [loadingStage, setLoadingStage] = useState<'initializing' | 'loading_session' | 'generating_xml' | 'finalizing'>('initializing')
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [xmlContent, setXmlContent] = useState<string>('')
  const [error, setError] = useState<{
    message: string
    type: 'network' | 'session' | 'generation' | 'validation' | 'parameters' | 'unknown'
    canRetry: boolean
  } | null>(null)

  const {
    switchSession,
    generateXML,
    streamParameters,
    jobParameters,
    detectedJobType,
    criticalMissing,
    completionPercentage,
    parametersLoaded
  } = useLangExtractChat()

  // Track initialization to prevent re-runs
  const [hasInitialized, setHasInitialized] = useState(false)
  const [localSession, setLocalSession] = useState<string | null>(null)

  // Initialize session and load XML with enhanced loading states
  useEffect(() => {
    // Prevent re-initialization
    if (hasInitialized) return

    const initializeXMLStream = async () => {
      if (!sessionId) {
        setError({
          message: 'Invalid session ID provided',
          type: 'session',
          canRetry: false
        })
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        setError(null)

        // Stage 1: Initialize system
        setLoadingStage('initializing')
        setLoadingProgress(0)
        await new Promise(resolve => setTimeout(resolve, 500)) // Smooth loading transition

        // Stage 2: Load session
        setLoadingStage('loading_session')
        setLoadingProgress(25)

        try {
          await switchSession(sessionId)
          setLocalSession(sessionId) // Store session locally
        } catch (sessionError: any) {
          throw {
            message: sessionError.message || 'Failed to load session',
            type: 'session',
            canRetry: true
          }
        }

        setLoadingProgress(50)

        // Wait a bit for session to be fully loaded
        await new Promise(resolve => setTimeout(resolve, 100))

        // Check if XML content is provided via URL params
        const urlXml = searchParams.get('xml')
        if (urlXml) {
          // Stage 4: Finalize (skip generation)
          setLoadingStage('finalizing')
          setLoadingProgress(90)
          setXmlContent(decodeURIComponent(urlXml))
        } else {
          // Stage 3: Generate XML - don't call generateXML here, wait for session to be ready
          setLoadingStage('finalizing')
          setLoadingProgress(90)
          // XML will be generated in a separate effect after session is loaded
        }

        // Stage 4: Finalize
        setLoadingStage('finalizing')
        setLoadingProgress(100)
        await new Promise(resolve => setTimeout(resolve, 300)) // Smooth completion

      } catch (error: any) {
        console.error('XML Stream initialization error:', error)

        // Enhanced error categorization
        let errorType: 'network' | 'session' | 'generation' | 'validation' | 'parameters' | 'unknown' = 'unknown'
        let canRetry = true

        if (error.type) {
          errorType = error.type
          canRetry = error.canRetry ?? true
        } else if (error.message?.includes('fetch') || error.message?.includes('network')) {
          errorType = 'network'
        } else if (error.message?.includes('session') || error.message?.includes('not found')) {
          errorType = 'session'
        } else if (error.message?.includes('parameter') || error.message?.includes('missing')) {
          errorType = 'parameters'
          canRetry = false
        }

        setError({
          message: error.message || 'Failed to initialize XML stream',
          type: errorType,
          canRetry
        })

        toast.error('Failed to load XML stream', {
          description: error.message || 'Please try again'
        })
      } finally {
        setIsLoading(false)
        // Mark as initialized to prevent re-runs
        setHasInitialized(true)
      }
    }

    initializeXMLStream()
  }, [sessionId, hasInitialized]) // Only depend on sessionId and hasInitialized

  // Generate XML after session is loaded
  useEffect(() => {
    // Skip if already has XML content or if we're in the initial load
    if (!localSession || xmlContent || !hasInitialized) return

    const generateInitialXML = async () => {
      // Wait a bit for parameters to be fully loaded
      await new Promise(resolve => setTimeout(resolve, 500))

      try {
        setIsLoading(true)
        setLoadingStage('generating_xml')
        setLoadingProgress(75)

        const response = await generateXML(false, detectedJobType || 'STANDARD')
        if (response?.success && response.xml_content) {
          setXmlContent(response.xml_content)
        } else if (response?.error) {
          setError({
            message: response.error || 'Failed to generate XML',
            type: 'generation',
            canRetry: true
          })
        }
      } catch (error: any) {
        console.error('XML generation error:', error)
        setError({
          message: error.message || 'Failed to generate XML',
          type: 'generation',
          canRetry: true
        })
      } finally {
        setIsLoading(false)
      }
    }

    generateInitialXML()
  }, [localSession, hasInitialized, xmlContent, generateXML, detectedJobType]) // React when session and parameters are ready

  // Loading state
  if (isLoading) {
    return (
      <XMLLoadingState
        sessionId={sessionId}
        currentStage={loadingStage}
        progress={loadingProgress}
      />
    )
  }

  // Error state
  if (error) {
    return (
      <XMLErrorState
        error={error.message}
        errorType={error.type}
        sessionId={sessionId}
        canRetry={error.canRetry}
        onRetry={() => window.location.reload()}
        onBackToChat={() => router.push('/langextract')}
      />
    )
  }

  // Main XML Stream Layout
  return (
    <StreamXMLLayout
      sessionId={sessionId}
      xmlContent={xmlContent}
      onXmlChange={setXmlContent}
      streamParameters={streamParameters || {}}
      jobParameters={jobParameters || {}}
      detectedJobType={detectedJobType}
      criticalMissing={criticalMissing || []}
      completionPercentage={completionPercentage || 0}
      parametersLoaded={parametersLoaded}
      onRegenerateXML={async () => {
        try {
          setIsLoading(true)
          setLoadingStage('generating_xml')
          setLoadingProgress(0)

          // Show progress during regeneration
          const progressTimer = setInterval(() => {
            setLoadingProgress(prev => Math.min(prev + 10, 90))
          }, 200)

          const response = await generateXML(true, detectedJobType || 'STANDARD')

          clearInterval(progressTimer)
          setLoadingProgress(100)

          if (response?.success && response.xml_content) {
            setXmlContent(response.xml_content)
            toast.success('XML erfolgreich regeneriert', {
              description: `${response.xml_content.split('\n').length} Zeilen generiert`
            })
          } else {
            throw {
              message: response?.error || 'Failed to regenerate XML',
              type: 'generation',
              canRetry: true
            }
          }
        } catch (error: any) {
          console.error('XML regeneration error:', error)

          // Enhanced error handling for regeneration
          const errorType = error.type || 'generation'
          const errorMessage = error.message || 'XML-Regenerierung fehlgeschlagen'

          setError({
            message: errorMessage,
            type: errorType,
            canRetry: true
          })

          toast.error('XML-Regenerierung fehlgeschlagen', {
            description: errorMessage
          })
        } finally {
          setIsLoading(false)
        }
      }}
    />
  )
}