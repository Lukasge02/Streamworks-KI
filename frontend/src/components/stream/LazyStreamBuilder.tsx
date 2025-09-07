'use client'

import dynamic from 'next/dynamic'
import { Suspense } from 'react'
import { RefreshCw } from 'lucide-react'

// Lazy load Monaco Editor to reduce initial bundle size
const DynamicEditor = dynamic(
  () => import('@monaco-editor/react'),
  {
    loading: () => (
      <div className="flex items-center justify-center h-96 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="flex flex-col items-center space-y-3">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-sm text-gray-600 dark:text-gray-400">XML-Editor wird geladen...</p>
        </div>
      </div>
    ),
    ssr: false,
  }
)

// Lazy load the form components
const StreamForm = dynamic(() => import('./StreamForm').then(mod => ({ default: mod.StreamForm })), {
  loading: () => (
    <div className="animate-pulse">
      <div className="space-y-4">
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        <div className="h-32 bg-gray-200 rounded"></div>
      </div>
    </div>
  )
})

const StreamChatInput = dynamic(() => import('./StreamChatInput').then(mod => ({ default: mod.StreamChatInput })), {
  loading: () => (
    <div className="animate-pulse">
      <div className="h-20 bg-gray-200 rounded"></div>
    </div>
  )
})

interface LazyStreamBuilderProps {
  className?: string
  mode?: 'basic' | 'advanced' | 'enterprise'
}

export { DynamicEditor, StreamForm, StreamChatInput }
export type { LazyStreamBuilderProps }