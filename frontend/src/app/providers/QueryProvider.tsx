import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import type { ReactNode } from 'react';
import { uiActions } from '../../stores/uiStore';

// Enhanced query client with better defaults and error handling
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors
        if (error && typeof error === 'object' && 'status' in error) {
          const status = error.status as number;
          if (status >= 400 && status < 500) {
            return false;
          }
        }
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false, // Disable automatic refetch on window focus
      refetchOnReconnect: true, // Refetch when connection is restored
    },
    mutations: {
      retry: 1,
      onError: (error) => {
        // Global mutation error handling
        const message = error instanceof Error ? error.message : 'An unexpected error occurred';
        uiActions.showError(message);
      },
    },
  },
});

// Global error handler for network errors
queryClient.setMutationDefaults(['upload'], {
  retry: 2,
  retryDelay: 1000,
});

// Global query error handler is set up in the default options above

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {import.meta.env.DEV && (
        <ReactQueryDevtools 
          initialIsOpen={false}
        />
      )}
    </QueryClientProvider>
  );
}