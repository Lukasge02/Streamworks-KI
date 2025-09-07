'use client'

import { useEffect } from 'react'
import { DocumentManager } from '@/components/DocumentManager'

export default function DocumentsPage() {
  useEffect(() => {
    // Set page title
    document.title = 'Dokumentenverwaltung | Streamworks'
  }, [])

  return (
    <div className="h-screen bg-gray-50">
      {/* DocumentManager with automatic Global View */}
      <DocumentManagerWithGlobalView />
    </div>
  )
}

// Wrapper component to force global view on this page
function DocumentManagerWithGlobalView() {
  return (
    <div className="h-full">
      <DocumentManager defaultView="global" />
    </div>
  )
}