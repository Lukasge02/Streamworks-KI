'use client'

import { useEffect } from 'react'
import { ChatXMLInterface } from '@/components/xml-chat/ChatXMLInterface'

export default function XMLChatPage() {
  useEffect(() => {
    // Set page title
    document.title = 'XML Chat Generator | Streamworks'
  }, [])

  return (
    <div className="h-screen bg-gray-50 dark:bg-gray-900">
      <ChatXMLInterface />
    </div>
  )
}