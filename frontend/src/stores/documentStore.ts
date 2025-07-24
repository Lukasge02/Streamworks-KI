/**
 * Document Store - Manages file uploads, document operations, and filters
 */

import { create } from 'zustand';
import { subscribeWithSelector, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { 
  Document, 
  DocumentUploadProgress, 
  BulkOperationRequest,
  BulkOperationResponse 
} from '../types/api';
import { streamWorksAPI } from '../services/api';

interface DocumentFilter {
  search?: string;
  status?: 'all' | 'processed' | 'processing' | 'failed';
  dateRange?: {
    start: string;
    end: string;
  };
  fileType?: string[];
}

interface DocumentStore {
  // State
  documents: Document[];
  totalDocuments: number;
  currentPage: number;
  pageSize: number;
  filters: DocumentFilter;
  selectedDocuments: string[];
  uploads: Record<string, DocumentUploadProgress>;
  isLoading: boolean;
  error: string | null;
  sortBy: keyof Document;
  sortOrder: 'asc' | 'desc';

  // Actions
  loadDocuments: (page?: number) => Promise<void>;
  uploadDocument: (file: File) => Promise<void>;
  deleteDocument: (documentId: string) => Promise<void>;
  reprocessDocument: (documentId: string) => Promise<void>;
  bulkOperation: (operation: BulkOperationRequest) => Promise<void>;
  setFilters: (filters: Partial<DocumentFilter>) => void;
  setSelectedDocuments: (documentIds: string[]) => void;
  toggleDocumentSelection: (documentId: string) => void;
  selectAllDocuments: () => void;
  clearSelection: () => void;
  setSorting: (field: keyof Document, order: 'asc' | 'desc') => void;
  setPageSize: (size: number) => void;
  clearError: () => void;
  removeUpload: (uploadId: string) => void;
}

export const useDocumentStore = create<DocumentStore>()(
  devtools(
    subscribeWithSelector(
      immer((set, get) => ({
        // Initial state
        documents: [],
        totalDocuments: 0,
        currentPage: 1,
        pageSize: 20,
        filters: {},
        selectedDocuments: [],
        uploads: {},
        isLoading: false,
        error: null,
        sortBy: 'upload_date',
        sortOrder: 'desc',

        // Actions
        loadDocuments: async (page) => {
          const state = get();
          const targetPage = page || state.currentPage;

          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });

          try {
            const response = await streamWorksAPI.getDocuments(
              targetPage,
              state.pageSize,
              state.filters.search
            );

            set((draft) => {
              draft.documents = response.items;
              draft.totalDocuments = response.total;
              draft.currentPage = response.page;
              draft.isLoading = false;
            });
          } catch (error) {
            set((draft) => {
              draft.error = error instanceof Error ? error.message : 'Failed to load documents';
              draft.isLoading = false;
            });
          }
        },

        uploadDocument: async (file) => {
          const uploadId = `${Date.now()}_${file.name}`;
          
          // Initialize upload progress
          set((draft) => {
            draft.uploads[uploadId] = {
              file_id: uploadId,
              filename: file.name,
              progress: 0,
              status: 'uploading',
            };
          });

          try {
            const response = await streamWorksAPI.uploadDocument(
              file,
              (progress) => {
                set((draft) => {
                  if (draft.uploads[uploadId]) {
                    draft.uploads[uploadId] = { ...draft.uploads[uploadId], ...progress };
                  }
                });
              }
            );

            // Mark upload as completed
            set((draft) => {
              if (draft.uploads[uploadId]) {
                draft.uploads[uploadId].status = 'completed';
                draft.uploads[uploadId].progress = 100;
              }
              
              // Add new document to the list
              draft.documents.unshift(response.data);
              draft.totalDocuments += 1;
            });

            // Auto-remove upload after 3 seconds
            setTimeout(() => {
              get().removeUpload(uploadId);
            }, 3000);

          } catch (error) {
            set((draft) => {
              if (draft.uploads[uploadId]) {
                draft.uploads[uploadId].status = 'error';
                draft.uploads[uploadId].error = error instanceof Error ? error.message : 'Upload failed';
              }
            });
          }
        },

        deleteDocument: async (documentId) => {
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });

          try {
            await streamWorksAPI.deleteDocument(documentId);
            
            set((draft) => {
              draft.documents = draft.documents.filter(doc => doc.id !== documentId);
              draft.selectedDocuments = draft.selectedDocuments.filter(id => id !== documentId);
              draft.totalDocuments -= 1;
              draft.isLoading = false;
            });
          } catch (error) {
            set((draft) => {
              draft.error = error instanceof Error ? error.message : 'Failed to delete document';
              draft.isLoading = false;
            });
          }
        },

        reprocessDocument: async (documentId) => {
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });

          try {
            await streamWorksAPI.reprocessDocument(documentId);
            
            // Update document status optimistically
            set((draft) => {
              const docIndex = draft.documents.findIndex(doc => doc.id === documentId);
              if (docIndex !== -1) {
                draft.documents[docIndex].processing_status = 'processing';
              }
              draft.isLoading = false;
            });
          } catch (error) {
            set((draft) => {
              draft.error = error instanceof Error ? error.message : 'Failed to reprocess document';
              draft.isLoading = false;
            });
          }
        },

        bulkOperation: async (operation) => {
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });

          try {
            const response = await streamWorksAPI.bulkDocumentOperation(operation);
            const result = response.data;

            set((draft) => {
              if (operation.operation === 'delete') {
                // Remove deleted documents
                draft.documents = draft.documents.filter(
                  doc => !operation.document_ids.includes(doc.id)
                );
                draft.totalDocuments -= result.processed;
                draft.selectedDocuments = [];
              } else if (operation.operation === 'reprocess') {
                // Update processing status for reprocessed documents
                operation.document_ids.forEach(docId => {
                  const docIndex = draft.documents.findIndex(doc => doc.id === docId);
                  if (docIndex !== -1) {
                    draft.documents[docIndex].processing_status = 'processing';
                  }
                });
              }
              
              draft.isLoading = false;
            });

            // Show success message if some operations failed
            if (result.failed > 0) {
              set((draft) => {
                draft.error = `Operation completed with ${result.failed} failures`;
              });
            }

          } catch (error) {
            set((draft) => {
              draft.error = error instanceof Error ? error.message : 'Bulk operation failed';
              draft.isLoading = false;
            });
          }
        },

        setFilters: (newFilters) => {
          set((draft) => {
            draft.filters = { ...draft.filters, ...newFilters };
            draft.currentPage = 1; // Reset to first page when filtering
          });
          
          // Reload documents with new filters
          get().loadDocuments(1);
        },

        setSelectedDocuments: (documentIds) => {
          set((draft) => {
            draft.selectedDocuments = documentIds;
          });
        },

        toggleDocumentSelection: (documentId) => {
          set((draft) => {
            const index = draft.selectedDocuments.indexOf(documentId);
            if (index > -1) {
              draft.selectedDocuments.splice(index, 1);
            } else {
              draft.selectedDocuments.push(documentId);
            }
          });
        },

        selectAllDocuments: () => {
          set((draft) => {
            draft.selectedDocuments = draft.documents.map(doc => doc.id);
          });
        },

        clearSelection: () => {
          set((draft) => {
            draft.selectedDocuments = [];
          });
        },

        setSorting: (field, order) => {
          set((draft) => {
            draft.sortBy = field;
            draft.sortOrder = order;
          });
          
          // Re-sort documents locally
          set((draft) => {
            draft.documents.sort((a, b) => {
              const aVal = a[field];
              const bVal = b[field];
              
              if (aVal === bVal) return 0;
              
              const comparison = aVal < bVal ? -1 : 1;
              return order === 'asc' ? comparison : -comparison;
            });
          });
        },

        setPageSize: (size) => {
          set((draft) => {
            draft.pageSize = size;
            draft.currentPage = 1; // Reset to first page
          });
          
          get().loadDocuments(1);
        },

        clearError: () => {
          set((draft) => {
            draft.error = null;
          });
        },

        removeUpload: (uploadId) => {
          set((draft) => {
            delete draft.uploads[uploadId];
          });
        },
      }))
    ),
    {
      name: 'DocumentStore',
    }
  )
);

// Selectors
export const useDocumentSelectors = {
  filteredDocuments: () => {
    const { documents, filters } = useDocumentStore();
    
    return documents.filter(doc => {
      // Status filter
      if (filters.status && filters.status !== 'all') {
        if (filters.status !== doc.processing_status) {
          return false;
        }
      }
      
      // File type filter
      if (filters.fileType && filters.fileType.length > 0) {
        if (!filters.fileType.includes(doc.mime_type)) {
          return false;
        }
      }
      
      // Date range filter
      if (filters.dateRange) {
        const docDate = new Date(doc.upload_date);
        const startDate = new Date(filters.dateRange.start);
        const endDate = new Date(filters.dateRange.end);
        
        if (docDate < startDate || docDate > endDate) {
          return false;
        }
      }
      
      return true;
    });
  },
  
  uploadProgress: () => {
    const { uploads } = useDocumentStore();
    return Object.values(uploads);
  },
  
  hasActiveUploads: () => {
    const { uploads } = useDocumentStore();
    return Object.values(uploads).some(upload => 
      upload.status === 'uploading' || upload.status === 'processing'
    );
  },
  
  selectedDocumentsData: () => {
    const { documents, selectedDocuments } = useDocumentStore();
    return documents.filter(doc => selectedDocuments.includes(doc.id));
  },
  
  paginationInfo: () => {
    const { currentPage, pageSize, totalDocuments } = useDocumentStore();
    const totalPages = Math.ceil(totalDocuments / pageSize);
    
    return {
      currentPage,
      pageSize,
      totalDocuments,
      totalPages,
      hasNextPage: currentPage < totalPages,
      hasPreviousPage: currentPage > 1,
    };
  },
};