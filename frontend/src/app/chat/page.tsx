'use client'

import { useEffect } from 'react'
import { ChatProvider } from '@/components/chat/ChatProvider'
import { ModernChatInterface } from '@/components/chat/ModernChatInterface'

export default function ChatPage() {
  useEffect(() => {
    // Set page title
    document.title = 'Streamworks Chat | Streamworks'
  }, [])

  return (
    <ChatProvider>
      <ModernChatInterface />
    </ChatProvider>
  )
}