'use client'

import { useEffect } from 'react'
import { ChatInterface } from '@/components/chat/ChatInterface'

export default function ChatPage() {
  useEffect(() => {
    // Set page title
    document.title = 'Streamworks Chat | Streamworks'
  }, [])

  return <ChatInterface />
}