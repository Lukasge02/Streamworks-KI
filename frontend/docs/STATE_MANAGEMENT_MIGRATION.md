# State Management Migration Guide

## Overview

This guide provides a structured approach to migrating the existing StreamWorks frontend state management to the new unified architecture. The migration focuses on maintaining existing functionality while improving consistency, performance, and developer experience.

## Migration Strategy

### Phase 1: Base Pattern Implementation ✅
- [x] Create base store patterns
- [x] Implement React Query optimization
- [x] Establish migration guidelines

### Phase 2: Store Migration (Current)
- [ ] Migrate Document Store
- [ ] Migrate Chat Store
- [ ] Create new stores for missing functionality

### Phase 3: Component Integration
- [ ] Update components to use new patterns
- [ ] Implement proper error boundaries
- [ ] Add loading states consistently

### Phase 4: Performance Optimization
- [ ] Implement selective re-renders
- [ ] Add query deduplication
- [ ] Optimize bundle size

---

## Store Migration Patterns

### 1. Document Store Migration

#### Current State
```typescript
// frontend/src/stores/documentStore.ts
export const useDocumentStore = create<DocumentStoreState>()(
  immer((set, get) => ({
    documents: [],
    uploads: new Map(),
    selectedDocuments: new Set(),
    // ... complex state management
  }))
)
```

#### Migrated State
```typescript
// frontend/src/stores/document/documentStore.ts
import { createBaseStore, createBaseActions, createPaginationActions, createFilterActions } from '@/stores/base/baseStore'

interface DocumentStoreState extends BaseStoreState {
  // Core data
  documents: Document[]
  uploads: Map<string, UploadJobProgress>
  
  // UI state
  selectedDocuments: Set<string>
  viewMode: 'grid' | 'list'
  
  // Pagination and filtering
  pagination: PaginationState
  filters: SearchFilters
  
  // Document viewer state
  viewerOpen: boolean
  viewingDocumentId: string | null
}

export const useDocumentStore = createBaseStore<DocumentStoreState>(
  {
    // Initial state
    documents: [],
    uploads: new Map(),
    selectedDocuments: new Set(),
    viewMode: 'grid',
    isLoading: false,
    error: null,
    lastUpdated: null,
    
    // Pagination
    pagination: createPaginationState(20),
    
    // Filters
    filters: createSearchFilters(),
    
    // Viewer
    viewerOpen: false,
    viewingDocumentId: null,
  },
  {
    name: 'streamworks-document-store',
    enableDevtools: true,
    enablePersist: true,
    persistOptions: {
      name: 'streamworks-document-store',
      partialize: (state) => ({
        viewMode: state.viewMode,
        selectedDocuments: Array.from(state.selectedDocuments),
      }),
    },
  }
)
```

### 2. Chat Store Migration

#### Current State (Already Well-Implemented)
```typescript
// frontend/src/stores/chatStore.ts
export const useChatStore = create<ChatState & ChatActions>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Existing implementation is already good
      })),
      {
        name: 'streamworks-chat-store',
        partialize: (state) => ({
          currentSessionId: state.currentSessionId,
          aiProvider: state.aiProvider,
        }),
      }
    )
  )
)
```

#### Migration Approach
The chat store is already well-implemented with modern patterns. We'll:
1. Keep the existing implementation
2. Add base store utilities
3. Enhance with React Query integration for server state

### 3. React Query Integration

#### Document API Queries
```typescript
// frontend/src/hooks/useDocuments.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys, createStandardQuery, createStandardMutation } from '@/stores/base/reactQueryConfig'
import { toast } from 'sonner'

export function useDocuments(filters?: Record<string, any>) {
  return useQuery(
    createStandardQuery({
      key: queryKeys.documents.list(filters),
      queryFn: async () => {
        const response = await fetch('/api/documents?' + new URLSearchParams(filters || {}))
        if (!response.ok) throw new Error('Failed to fetch documents')
        return response.json()
      },
      errorMessage: 'Failed to load documents'
    })
  )
}

export function useUploadDocument() {
  const queryClient = useQueryClient()
  
  return useMutation(
    createStandardMutation({
      key: ['documents', 'upload'],
      mutationFn: async (file: File) => {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await fetch('/api/documents/upload', {
          method: 'POST',
          body: formData,
        })
        
        if (!response.ok) throw new Error('Failed to upload document')
        return response.json()
      },
      successMessage: 'Document uploaded successfully',
      invalidateQueries: [queryKeys.documents.list()],
    })
  )
}
```

---

## Component Migration Patterns

### 1. DocumentGrid Component

#### Current Pattern
```typescript
// Before
const DocumentGrid = () => {
  const { documents, isLoading, error } = useDocumentStore()
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {documents.map(doc => (
        <DocumentCard key={doc.id} document={doc} />
      ))}
    </div>
  )
}
```

#### Migrated Pattern
```typescript
// After
const DocumentGrid = () => {
  const { documents, isLoading, error } = useDocuments()
  const { selectedDocuments, toggleDocumentSelection } = useDocumentStore()
  
  // Combine Zustand (client state) with React Query (server state)
  const combinedData = documents.map(doc => ({
    ...doc,
    isSelected: selectedDocuments.has(doc.id)
  }))
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {combinedData.map(doc => (
        <DocumentCard 
          key={doc.id} 
          document={doc}
          onSelect={() => toggleDocumentSelection(doc.id)}
        />
      ))}
    </div>
  )
}
```

### 2. ChatInterface Component

#### Current Pattern
```typescript
// Already well-implemented, just needs React Query integration
const ChatInterface = () => {
  const { 
    currentSessionId, 
    getCurrentMessages, 
    isSendingMessage,
    addMessage 
  } = useChatStore()
  
  // Keep existing implementation but add React Query for:
  // - Session management
  // - Message persistence
  // - Optimistic updates
}
```

---

## Implementation Steps

### Step 1: Create Base Infrastructure
1. ✅ Create base store patterns
2. ✅ Implement React Query configuration
3. ✅ Establish migration guidelines

### Step 2: Migrate Document Store
1. Create new document store with base patterns
2. Implement React Query hooks for document operations
3. Update components gradually
4. Test thoroughly

### Step 3: Enhance Chat Store
1. Keep existing Zustand implementation
2. Add React Query integration for server state
3. Implement offline support
4. Add optimistic updates

### Step 4: Update Components
1. Create wrapper components for gradual migration
2. Update components to use new patterns
3. Implement proper error handling
4. Add loading states consistently

### Step 5: Performance Optimization
1. Implement selective re-renders
2. Add query deduplication
3. Optimize bundle size
4. Add performance monitoring

---

## Benefits of Migration

### 1. **Consistent Architecture**
- Unified patterns across all stores
- Clear separation of concerns
- Better developer experience

### 2. **Improved Performance**
- Optimal caching strategies
- Reduced re-renders
- Better memory management

### 3. **Better Error Handling**
- Centralized error management
- Consistent error boundaries
- Better user feedback

### 4. **Enhanced Developer Experience**
- TypeScript support
- Better debugging tools
- Easier testing

### 5. **Scalability**
- Easier to add new features
- Better code organization
- Improved maintainability

---

## Testing Strategy

### Unit Tests
- Test store actions and selectors
- Test React Query hooks
- Test component interactions

### Integration Tests
- Test store integration with components
- Test API interactions
- Test error scenarios

### E2E Tests
- Test user flows
- Test offline scenarios
- Test performance critical paths

---

## Rollout Strategy

### Phase 1: Internal Testing
- Test new patterns in development
- Gather feedback from team
- Fix any issues found

### Phase 2: Gradual Rollout
- Migrate one store at a time
- Monitor performance
- Gather user feedback

### Phase 3: Full Migration
- Complete all store migrations
- Update all components
- Remove old patterns

### Phase 4: Optimization
- Performance tuning
- Bug fixes
- Documentation updates