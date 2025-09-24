'use client'

import { ReactNode, useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/components/theme-provider'
import { ThemeEnhancer } from '@/components/ThemeEnhancer'
import { DocumentSyncProvider } from '@/providers/DocumentSyncProvider'
import { ToastContainer } from '@/components/ui/ToastContainer'
import { enableMapSet } from 'immer'
import {
  StreamworksErrorBoundary,
  setupGlobalErrorHandlers
} from '@/components/shared/errorBoundaries'
import { LoadingOverlay } from '@/components/shared/loadingStates'
import { createOptimizedQueryClient } from '@/stores/base/reactQueryConfig'
import { useLoadingState } from '@/components/shared/loadingStates'
import { AuthProvider } from '@/contexts/AuthContext'

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
    startLoading('Initializing Streamworks...')
    
    // Simulate app initialization
    const timer = setTimeout(() => {
      stopLoading()
    }, 1000)
    
    return () => clearTimeout(timer)
  }, [startLoading, stopLoading])

  return (
    <StreamworksErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
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
                text="Initializing Streamworks..."
                size="lg"
              />
              {children}
              <ToastContainer />
            </DocumentSyncProvider>
          </ThemeProvider>
        </AuthProvider>
      </QueryClientProvider>
    </StreamworksErrorBoundary>
  )
}

export function Providers({ children }: ProvidersProps) {
  return <AppProviders>{children}</AppProviders>
}