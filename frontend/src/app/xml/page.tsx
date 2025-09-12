'use client'

import { useEffect } from 'react'
import XmlGenerator from '@/components/xml-wizard/XmlGenerator'

export default function XMLPage() {
  useEffect(() => {
    // Set page title
    document.title = 'XML Generator | Streamworks'
  }, [])

  return (
    <div className="h-full">
      <XmlGenerator className="h-full" />
    </div>
  )
}