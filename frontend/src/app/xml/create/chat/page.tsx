'use client'

import React from 'react'
import { ChatStreamCreator } from '@/components/xml-wizard/ChatStreamCreator'

export default function ChatCreatePage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <ChatStreamCreator />
    </div>
  )
}