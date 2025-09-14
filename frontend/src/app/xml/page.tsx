'use client'

import { useEffect } from 'react'
import StreamList from '@/components/xml-streams/StreamList'

export default function XMLPage() {
  useEffect(() => {
    // Set page title
    document.title = 'XML Streams | Streamworks'
  }, [])

  return (
    <div className="container mx-auto px-4 py-6">
      <StreamList />
    </div>
  )
}