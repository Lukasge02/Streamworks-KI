'use client'

import { useEffect } from 'react'
import { useParams } from 'next/navigation'
import XmlGenerator from '@/components/xml-wizard/XmlGenerator'
import { useStream } from '@/hooks/useXMLStreams'
import { Loader2 } from 'lucide-react'

export default function EditStreamPage() {
  const params = useParams()
  const streamId = params.id as string

  const { data: stream, isLoading, error } = useStream(streamId)

  useEffect(() => {
    // Set page title
    document.title = stream 
      ? `${stream.stream_name} bearbeiten | Streamworks`
      : 'Stream bearbeiten | Streamworks'
  }, [stream])

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
          <a 
            href="/xml" 
            className="text-blue-600 hover:text-blue-800 underline"
          >
            Zurück zur Stream-Liste
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full">
      <XmlGenerator 
        className="h-full"
        streamId={streamId}
        initialData={stream}
      />
    </div>
  )
}