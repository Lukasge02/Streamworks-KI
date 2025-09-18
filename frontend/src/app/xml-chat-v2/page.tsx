/**
 * XML Chat V2 Demo Page
 * Showcase the new modern XML chat interface
 */

'use client'

import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'

import { XMLChatInterface } from '@/components/xml-chat-v2'

// Create a local query client for this demo
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
})

export default function XMLChatV2Page() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                XML Chat V2 - Modern Interface
              </h1>
              <p className="text-sm text-gray-500">
                Next-generation XML generation through natural conversation
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                New Design
              </div>
              <div className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                Beta
              </div>
            </div>
          </div>
        </div>

        {/* Main Interface */}
        <div className="h-[calc(100vh-73px)]">
          <XMLChatInterface />
        </div>

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            className: 'bg-white border border-gray-200 text-gray-900',
          }}
        />
      </div>
    </QueryClientProvider>
  )
}