'use client'

import { ReactNode, useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/components/theme-provider'
import { ThemeEnhancer } from '@/components/ThemeEnhancer'
import { DocumentSyncProvider } from '@/providers/DocumentSyncProvider'
import { Toaster } from 'sonner'
import { enableMapSet } from 'immer'

// Enable Immer MapSet plugin for Zustand stores
enableMapSet()

interface ProvidersProps {
  children: ReactNode
}

export function Providers({ children }: ProvidersProps) {
  // Create a client instance for React Query
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000,   // 10 minutes
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        attribute="class"
        defaultTheme="light"
        enableSystem={true}
        disableTransitionOnChange={false}
      >
        <DocumentSyncProvider>
          <ThemeEnhancer />
          {children}
          <Toaster position="top-right" />
        </DocumentSyncProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}