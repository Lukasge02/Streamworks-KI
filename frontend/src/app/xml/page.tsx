'use client'

import { useEffect } from 'react'
import { XMLGenerator } from '@/components/xml/XMLGenerator'

export default function XMLPage() {
  useEffect(() => {
    // Set page title
    document.title = 'XML Generator | Streamworks'
  }, [])

  return <XMLGenerator />
}