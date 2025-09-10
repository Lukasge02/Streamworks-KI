'use client'

import { ReactNode, useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/components/theme-provider'
import { ThemeEnhancer } from '@/components/ThemeEnhancer'
import { DocumentSyncProvider } from '@/providers/DocumentSyncProvider'
import { Toaster } from 'sonner'
import { enableMapSet } from 'immer'
import { 
  StreamWorksErrorBoundary, 
  setupGlobalErrorHandlers
} from '@/components/shared/errorBoundaries'
import { LoadingOverlay } from '@/components/shared/loadingStates'
import { createOptimizedQueryClient } from '@/stores/base/reactQueryConfig'
import { useLoadingState } from '@/components/shared/loadingStates'

// Enable Immer MapSet plugin for Zustand stores
enableMapSet()

interface ProvidersProps {
  children: ReactNode
}

function AppProviders({ children }: ProvidersProps) {
  // Create a client instance for React Query
  const [queryClient] = useState(() => createOptimizedQueryClient())
  const { isLoading, startLoading, stopLoading } = useLoadingState()

  // Setup global error handlers
  useEffect(() => {
    setupGlobalErrorHandlers()
    
    // Initialize app
    startLoading('Initializing StreamWorks...')
    
    // Simulate app initialization
    const timer = setTimeout(() => {
      stopLoading()
    }, 1000)
    
    return () => clearTimeout(timer)
  }, [startLoading, stopLoading])

  return (
    <StreamWorksErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem={true}
          disableTransitionOnChange={false}
        >
          <DocumentSyncProvider>
            <ThemeEnhancer />
            <LoadingOverlay 
              isLoading={isLoading}
              text="Initializing StreamWorks..."
              size="lg"
            />
            {children}
            <Toaster position="top-right" />
          </DocumentSyncProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </StreamWorksErrorBoundary>
  )
}

export function Providers({ children }: ProvidersProps) {
  return <AppProviders>{children}</AppProviders>
}