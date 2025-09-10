'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface DocumentDetailPageProps {
  params: Promise<{
    id: string
  }>
}

export default function DocumentDetailPage({ params }: DocumentDetailPageProps) {
  const router = useRouter()

  useEffect(() => {
    // Redirect to documents page - the modal will be opened from there
    // This page only exists as a fallback for direct links
    params.then((resolvedParams) => {
      // Store the document ID in sessionStorage so DocumentManager can open it
      if (resolvedParams?.id) {
        sessionStorage.setItem('openDocumentId', resolvedParams.id)
      }
      router.push('/documents')
    })
  }, [params, router])

  // Show minimal loading while redirecting
  return (
    <div className="h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    </div>
  )
}