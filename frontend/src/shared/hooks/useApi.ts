import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/services/api';
import { handleApiError } from '@/shared/utils';
import { useNotificationStore } from '@/app/store/notificationStore';

/**
 * Hook for making API GET requests with React Query
 */
export function useApiQuery<T>(
  key: string | string[],
  endpoint: string,
  options?: {
    enabled?: boolean;
    staleTime?: number;
    gcTime?: number;
  }
) {
  const { addNotification } = useNotificationStore();

  return useQuery<T>({
    queryKey: Array.isArray(key) ? key : [key],
    queryFn: async () => {
      try {
        return await apiClient.get<T>(endpoint);
      } catch (error) {
        const message = handleApiError(error);
        addNotification({
          type: 'error',
          title: 'API Fehler',
          message,
        });
        throw error;
      }
    },
    staleTime: options?.staleTime ?? 5 * 60 * 1000, // 5 minutes
    gcTime: options?.gcTime ?? 10 * 60 * 1000, // 10 minutes
    enabled: options?.enabled ?? true,
  });
}

/**
 * Hook for making API POST/PUT/DELETE requests with React Query
 */
export function useApiMutation<TData = any, TVariables = any>(
  endpoint: string,
  method: 'POST' | 'PUT' | 'DELETE' = 'POST',
  options?: {
    onSuccess?: (data: TData) => void;
    onError?: (error: any) => void;
    invalidateQueries?: string[];
  }
) {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation<TData, Error, TVariables>({
    mutationFn: async (variables: TVariables) => {
      try {
        switch (method) {
          case 'POST':
            return await apiClient.post<TData>(endpoint, variables);
          case 'PUT':
            return await apiClient.put<TData>(endpoint, variables);
          case 'DELETE':
            return await apiClient.delete<TData>(endpoint);
          default:
            throw new Error(`Unsupported method: ${method}`);
        }
      } catch (error) {
        const message = handleApiError(error);
        addNotification({
          type: 'error',
          title: 'API Fehler',
          message,
        });
        throw error;
      }
    },
    onSuccess: (data) => {
      // Invalidate related queries
      if (options?.invalidateQueries) {
        options.invalidateQueries.forEach((queryKey) => {
          queryClient.invalidateQueries({ queryKey: [queryKey] });
        });
      }
      
      options?.onSuccess?.(data);
    },
    ...(options?.onError && { onError: options.onError }),
  });
}

/**
 * Hook for health check queries
 */
export function useHealthCheck(service: string) {
  return useApiQuery<{ status: string; ready?: boolean }>(
    ['health', service],
    `/${service}/health`,
    {
      staleTime: 30 * 1000, // 30 seconds
      gcTime: 60 * 1000, // 1 minute
    }
  );
}

/**
 * Hook for system status overview
 */
export function useSystemStatus() {
  const qaHealth = useHealthCheck('qa');
  const chatHealth = useHealthCheck('chat');
  const documentsHealth = useHealthCheck('documents');
  const trainingHealth = useHealthCheck('training');
  const xmlHealth = useHealthCheck('xml');

  const services = [
    { name: 'Q&A System', ...qaHealth },
    { name: 'Chat Service', ...chatHealth },
    { name: 'Document Management', ...documentsHealth },
    { name: 'Training Data', ...trainingHealth },
    { name: 'XML Generator', ...xmlHealth },
  ];

  const isLoading = services.some(service => service.isLoading);
  const hasError = services.some(service => service.error);
  const allHealthy = services.every(service => 
    service.data?.status === 'healthy' || 
    service.data?.ready === true
  );

  return {
    services,
    isLoading,
    hasError,
    allHealthy,
    overallStatus: allHealthy ? 'healthy' : hasError ? 'error' : 'loading'
  };
}