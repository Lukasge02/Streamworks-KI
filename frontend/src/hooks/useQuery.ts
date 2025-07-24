/**
 * Enhanced React Query hooks for StreamWorks-KI API
 */

import { 
  useQuery, 
  useMutation, 
  useQueryClient,
  useInfiniteQuery,
  type UseQueryOptions,
  type UseMutationOptions,
  type UseInfiniteQueryOptions
} from '@tanstack/react-query';
import { streamWorksAPI } from '../services/api';
import { uiActions } from '../stores/uiStore';
import type {
  ApiResponse,
  PaginatedResponse,
  ChatMessage,
  Conversation,
  Document,
  SystemStatus,
  UsageAnalytics,
  TrainingData,
  XmlTemplate,
  SystemMetrics,
} from '../types/api';

// Query Keys
export const queryKeys = {
  // Chat queries
  conversations: ['conversations'] as const,
  conversation: (id: string) => ['conversations', id] as const,
  chatHistory: (conversationId?: string) => ['chat', 'history', conversationId] as const,
  
  // Document queries
  documents: ['documents'] as const,
  document: (id: string) => ['documents', id] as const,
  documentSearch: (query: string) => ['documents', 'search', query] as const,
  
  // System queries
  systemStatus: ['system', 'status'] as const,
  healthCheck: (service?: string) => ['health', service] as const,
  systemMetrics: ['system', 'metrics'] as const,
  
  // Analytics queries
  usageAnalytics: ['analytics', 'usage'] as const,
  
  // Training queries
  trainingData: ['training', 'data'] as const,
  indexingStatus: ['training', 'indexing', 'status'] as const,
  
  // XML queries
  xmlTemplates: ['xml', 'templates'] as const,
  xmlTemplate: (id: string) => ['xml', 'templates', id] as const,
} as const;

// Default query options
const defaultQueryOptions = {
  staleTime: 5 * 60 * 1000, // 5 minutes
  gcTime: 10 * 60 * 1000, // 10 minutes (previously cacheTime)
  retry: (failureCount: number, error: any) => {
    // Don't retry on 4xx errors
    if (error?.status >= 400 && error?.status < 500) {
      return false;
    }
    return failureCount < 3;
  },
  retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
} as const;

// Chat Hooks
export function useConversations(options?: Partial<UseQueryOptions<PaginatedResponse<Conversation>>>) {
  return useQuery({
    queryKey: queryKeys.conversations,
    queryFn: () => streamWorksAPI.getConversations(),
    ...defaultQueryOptions,
    ...options,
  });
}

export function useChatHistory(
  conversationId?: string,
  options?: Partial<UseQueryOptions<PaginatedResponse<ChatMessage>>>
) {
  return useQuery({
    queryKey: queryKeys.chatHistory(conversationId),
    queryFn: () => streamWorksAPI.getChatHistory(conversationId),
    enabled: !!conversationId,
    ...defaultQueryOptions,
    ...options,
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: streamWorksAPI.sendMessage,
    onSuccess: (data, variables) => {
      // Invalidate chat history for the conversation
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.chatHistory(variables.conversation_id) 
      });
      
      // Update conversations list to reflect new message count
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.conversations 
      });
      
      uiActions.showSuccess('Message sent successfully');
    },
    onError: (error: Error) => {
      uiActions.showError(error.message, 'Failed to send message');
    },
  });
}

// Document Hooks
export function useDocuments(
  page = 1,
  pageSize = 20,
  search?: string,
  options?: Partial<UseQueryOptions<PaginatedResponse<Document>>>
) {
  return useQuery({
    queryKey: ['documents', page, pageSize, search],
    queryFn: () => streamWorksAPI.getDocuments(page, pageSize, search),
    ...defaultQueryOptions,
    ...options,
  });
}

export function useInfiniteDocuments(
  pageSize = 20,
  search?: string,
  options?: Partial<UseInfiniteQueryOptions<PaginatedResponse<Document>>>
) {
  return useInfiniteQuery({
    queryKey: ['documents', 'infinite', pageSize, search],
    queryFn: ({ pageParam = 1 }) => streamWorksAPI.getDocuments(pageParam as number, pageSize, search),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      const hasNextPage = lastPage.page < lastPage.total_pages;
      return hasNextPage ? lastPage.page + 1 : undefined;
    },
    ...defaultQueryOptions,
    ...options,
  });
}

export function useDocument(id: string, options?: Partial<UseQueryOptions<ApiResponse<Document>>>) {
  return useQuery({
    queryKey: queryKeys.document(id),
    queryFn: () => streamWorksAPI.getDocument(id),
    enabled: !!id,
    ...defaultQueryOptions,
    ...options,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ file, onProgress }: { file: File; onProgress?: (progress: any) => void }) =>
      streamWorksAPI.uploadDocument(file, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.documents });
      uiActions.showSuccess('Document uploaded successfully');
    },
    onError: (error: Error) => {
      uiActions.showError(error.message, 'Upload failed');
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: streamWorksAPI.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.documents });
      uiActions.showSuccess('Document deleted successfully');
    },
    onError: (error: Error) => {
      uiActions.showError(error.message, 'Failed to delete document');
    },
  });
}

export function useBulkDocumentOperation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: streamWorksAPI.bulkDocumentOperation,
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.documents });
      
      const operation = variables.operation;
      const processed = data.data.processed;
      const failed = data.data.failed;
      
      if (failed > 0) {
        uiActions.showWarning(
          `${operation} completed: ${processed} succeeded, ${failed} failed`
        );
      } else {
        uiActions.showSuccess(`${operation} completed successfully for ${processed} documents`);
      }
    },
    onError: (error: Error) => {
      uiActions.showError(error.message, 'Bulk operation failed');
    },
  });
}

// System Hooks
export function useSystemStatus(options?: Partial<UseQueryOptions<ApiResponse<SystemStatus>>>) {
  return useQuery({
    queryKey: queryKeys.systemStatus,
    queryFn: () => streamWorksAPI.getSystemStatus(),
    refetchInterval: 30000, // Refetch every 30 seconds
    ...defaultQueryOptions,
    ...options,
  });
}

export function useSystemMetrics(options?: Partial<UseQueryOptions<ApiResponse<SystemMetrics>>>) {
  return useQuery({
    queryKey: queryKeys.systemMetrics,
    queryFn: () => streamWorksAPI.getSystemMetrics(),
    refetchInterval: 10000, // Refetch every 10 seconds
    ...defaultQueryOptions,
    ...options,
  });
}

export function useHealthCheck(
  service?: string,
  options?: Partial<UseQueryOptions<any>>
) {
  return useQuery({
    queryKey: queryKeys.healthCheck(service),
    queryFn: () => streamWorksAPI.getHealthCheck(service),
    refetchInterval: 30000,
    ...defaultQueryOptions,
    ...options,
  });
}

// Analytics Hooks
export function useUsageAnalytics(
  filter?: any,
  options?: Partial<UseQueryOptions<ApiResponse<UsageAnalytics>>>
) {
  return useQuery({
    queryKey: ['analytics', 'usage', filter],
    queryFn: () => streamWorksAPI.getUsageAnalytics(filter),
    ...defaultQueryOptions,
    ...options,
  });
}

export function useExportAnalytics() {
  return useMutation({
    mutationFn: streamWorksAPI.exportAnalytics,
    onSuccess: () => {
      uiActions.showSuccess('Export started successfully');
    },
    onError: (error: Error) => {
      uiActions.showError(error.message, 'Export failed');
    },
  });
}

// Training Hooks
export function useTrainingData(
  page = 1,
  pageSize = 50,
  category?: string,
  options?: Partial<UseQueryOptions<PaginatedResponse<TrainingData>>>
) {
  return useQuery({
    queryKey: ['training', 'data', page, pageSize, category],
    queryFn: () => streamWorksAPI.getTrainingData(page, pageSize, category),
    ...defaultQueryOptions,
    ...options,
  });
}

export function useIndexingStatus(options?: Partial<UseQueryOptions<any>>) {
  return useQuery({
    queryKey: queryKeys.indexingStatus,
    queryFn: () => streamWorksAPI.getIndexingStatus(),
    refetchInterval: (data) => {
      // Refetch more frequently if indexing is in progress
      return data?.data?.status === 'indexing' ? 2000 : 10000;
    },
    ...defaultQueryOptions,
    ...options,
  });
}

export function useUploadTrainingFile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: streamWorksAPI.uploadTrainingFile,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.trainingData });
      queryClient.invalidateQueries({ queryKey: queryKeys.indexingStatus });
      
      const { imported, errors } = data.data;
      if (errors.length > 0) {
        uiActions.showWarning(`Training file uploaded: ${imported} imported, ${errors.length} errors`);
      } else {
        uiActions.showSuccess(`Training file uploaded successfully: ${imported} entries imported`);
      }
    },
    onError: (error: Error) => {
      uiActions.showError(error.message, 'Training file upload failed');
    },
  });
}

export function useReindexData() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => streamWorksAPI.reindexData(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.indexingStatus });
      uiActions.showInfo('Reindexing started');
    },
    onError: (error: Error) => {
      uiActions.showError(error.message, 'Failed to start reindexing');
    },
  });
}

// XML Hooks
export function useXmlTemplates(
  category?: string,
  options?: Partial<UseQueryOptions<ApiResponse<XmlTemplate[]>>>
) {
  return useQuery({
    queryKey: ['xml', 'templates', category],
    queryFn: () => streamWorksAPI.getXmlTemplates(category),
    ...defaultQueryOptions,
    ...options,
  });
}

export function useXmlTemplate(
  id: string,
  options?: Partial<UseQueryOptions<ApiResponse<XmlTemplate>>>
) {
  return useQuery({
    queryKey: queryKeys.xmlTemplate(id),
    queryFn: () => streamWorksAPI.getXmlTemplate(id),
    enabled: !!id,
    ...defaultQueryOptions,
    ...options,
  });
}

export function useGenerateXml() {
  return useMutation({
    mutationFn: streamWorksAPI.generateXml,
    onSuccess: () => {
      uiActions.showSuccess('XML generated successfully');
    },
    onError: (error: Error) => {
      uiActions.showError(error.message, 'XML generation failed');
    },
  });
}

export function useValidateXml() {
  return useMutation({
    mutationFn: ({ xml, schemaUrl }: { xml: string; schemaUrl?: string }) =>
      streamWorksAPI.validateXml(xml, schemaUrl),
    onError: (error: Error) => {
      uiActions.showError(error.message, 'XML validation failed');
    },
  });
}

// Utility hooks
export function usePrefetchQuery() {
  const queryClient = useQueryClient();
  
  return {
    prefetchConversations: () => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.conversations,
        queryFn: () => streamWorksAPI.getConversations(),
        ...defaultQueryOptions,
      });
    },
    
    prefetchDocuments: (page = 1, pageSize = 20) => {
      queryClient.prefetchQuery({
        queryKey: ['documents', page, pageSize],
        queryFn: () => streamWorksAPI.getDocuments(page, pageSize),
        ...defaultQueryOptions,
      });
    },
    
    prefetchSystemStatus: () => {
      queryClient.prefetchQuery({
        queryKey: queryKeys.systemStatus,
        queryFn: () => streamWorksAPI.getSystemStatus(),
        ...defaultQueryOptions,
      });
    },
  };
}