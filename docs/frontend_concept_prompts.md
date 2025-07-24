# 🚀 Claude Code: StreamWorks-KI Frontend Build Prompts

## 📋 **EXECUTION STRATEGY**

Führe diese Prompts **schrittweise** in Claude Code aus. Jeder Prompt baut auf dem vorherigen auf und erstellt ein voll funktionsfähiges Modul.

**⚠️ WICHTIG:** Nach jedem Prompt teste das Ergebnis mit `npm run dev` bevor du zum nächsten gehst!

---

## 🏗️ **PHASE 1: FOUNDATION SETUP**

### **Prompt 1.1: Project Initialization & Backup**
```
Create a new modern React TypeScript project for StreamWorks-KI enterprise frontend:

1. FIRST: Backup existing frontend
   - Rename current 'frontend' directory to 'frontend_backup_[current_date]'
   - Ensure backup is complete before proceeding

2. Initialize new Vite React TypeScript project in 'frontend' directory (clean slate)
2. Install these exact dependencies:
   - @tanstack/react-query @tanstack/react-query-devtools
   - zustand
   - react-router-dom @types/react-router-dom
   - framer-motion
   - lucide-react
   - @headlessui/react
   - react-hook-form @hookform/resolvers zod
   - recharts
   - @monaco-editor/react
   - tailwindcss postcss autoprefixer
   - @tailwindcss/forms @tailwindcss/typography

3. Configure Tailwind CSS with these exact settings:
   - Modern color palette (primary blues, neutral grays)
   - Custom animations (fade-in, slide-up, pulse-slow)
   - Inter font family
   - Dark mode support
   - Accessibility plugins

4. Create this exact folder structure:
   ```
   src/
   ├── app/
   │   ├── store/
   │   ├── router/
   │   └── providers/
   ├── shared/
   │   ├── components/
   │   ├── hooks/
   │   ├── services/
   │   ├── types/
   │   ├── utils/
   │   └── constants/
   ├── features/
   │   ├── dashboard/
   │   ├── chat/
   │   ├── documents/
   │   ├── xml-generator/
   │   ├── analytics/
   │   ├── monitoring/
   │   ├── training/
   │   └── settings/
   └── assets/
   ```

5. Replace default App.tsx with a simple "StreamWorks-KI Loading..." message
6. Ensure the project starts successfully with `npm run dev`

Requirements:
- Use latest stable versions of all packages
- Configure TypeScript with strict mode
- Setup ESLint and Prettier
- Include error boundaries for development
```

### **Prompt 1.2: Core Types & Constants**
```
Create comprehensive TypeScript definitions and constants for the StreamWorks-KI application:

1. Create `src/shared/types/index.ts` with these interfaces:
   - User (id, name, email, role, preferences)
   - Document (id, filename, file_size, file_type, category_name, folder_name, upload_date, is_indexed, processing_status, error_message)
   - ChatMessage (id, content, isUser, timestamp, sources, metadata)
   - AnalyticsData (total_queries, avg_response_time, success_rate, top_queries, daily_usage)
   - SystemHealth (status, services, version, uptime)
   - CategoryStats (total, ready, processing, error)
   - XMLTemplate (id, name, description, content, category)
   - ProcessingStatus as union type
   - ApiResponse generic type

2. Create `src/shared/constants/index.ts` with:
   - API_BASE_URL configuration
   - FILE_TYPES allowed for upload
   - PROCESSING_STATUSES
   - SYSTEM_THEMES
   - NAVIGATION_ITEMS
   - ERROR_MESSAGES

3. Create `src/shared/utils/index.ts` with utility functions:
   - formatFileSize (bytes to human readable)
   - formatDate (various date formats)
   - generateId (unique ID generation)
   - validateFile (file type and size validation)
   - debounce and throttle functions
   - API error handling utilities

4. Export everything from barrel exports (index.ts files)

Requirements:
- Full TypeScript coverage with strict typing
- JSDoc comments for all interfaces
- Utility functions should be pure and testable
- Include proper error handling types
```

---

## 🔧 **PHASE 2: CORE INFRASTRUCTURE**

### **Prompt 2.1: API Service Layer**
```
Create a comprehensive, type-safe API service layer for StreamWorks-KI:

1. Create `src/shared/services/api.ts` with a StreamWorksAPI class:
   - Base HTTP client with error handling
   - Automatic token management
   - Request/response interceptors
   - TypeScript generic methods

2. Implement these service modules:
   - ChatService: sendMessage, getChatHistory, clearHistory
   - DocumentService: uploadDocument, getDocuments, deleteDocument, getCategories, getFolders
   - AnalyticsService: getAnalytics, exportAnalytics, getSystemMetrics
   - MonitoringService: getSystemHealth, getServiceStatus, getLogs
   - TrainingService: getTrainingData, uploadTrainingFile, reindexData
   - XMLService: getTemplates, validateXML, saveTemplate

3. Create `src/shared/services/websocket.ts` for real-time features:
   - WebSocket connection management
   - Event handling for chat streaming
   - System health updates
   - Reconnection logic

4. Add proper error handling:
   - Custom error classes (APIError, NetworkError, ValidationError)
   - Retry logic for failed requests
   - Timeout handling
   - Offline detection

5. Include React Query integration hooks:
   - useQuery wrappers for GET requests
   - useMutation wrappers for POST/PUT/DELETE
   - Optimistic updates
   - Cache invalidation strategies

Requirements:
- Full TypeScript coverage
- Comprehensive error handling
- Retry mechanisms for reliability
- Clean separation of concerns
- Easy to test and mock
```

### **Prompt 2.2: State Management Setup**
```
Create a robust state management system using Zustand for StreamWorks-KI:

1. Create `src/app/store/chatStore.ts`:
   - Messages array with optimistic updates
   - Loading states for different operations
   - sendMessage action with error handling
   - clearMessages, deleteMessage actions
   - Message filtering and search
   - Export conversation functionality

2. Create `src/app/store/documentStore.ts`:
   - Documents array with CRUD operations
   - Upload progress tracking
   - Batch operations (select multiple, delete multiple)
   - Filtering and sorting
   - Category and folder management
   - Search functionality

3. Create `src/app/store/uiStore.ts`:
   - Theme management (dark/light mode)
   - Sidebar state (collapsed/expanded)
   - Modal management
   - Toast notifications
   - Loading states
   - Error states

4. Create `src/app/store/userStore.ts`:
   - User authentication state
   - User preferences
   - Recent activities
   - Settings management

5. Create `src/app/store/index.ts`:
   - Combine all stores
   - Create store hooks with TypeScript
   - Development tools integration
   - Store persistence for user preferences

6. Add middleware for:
   - Local storage persistence
   - Development debugging
   - State synchronization
   - Performance monitoring

Requirements:
- Type-safe store definitions
- Immer integration for immutable updates
- DevTools support for debugging
- Persistence for important state
- Clean action patterns
```

---

## 🎨 **PHASE 3: DESIGN SYSTEM**

### **Prompt 3.1: Base UI Components**
Add essential enterprise-grade components to enhance the existing StreamWorks-KI frontend:

CONTEXT:
- Current UI is working and should be preserved
- Need to add professional components for advanced features
- Focus on components that enable new functionality
- Use existing Tailwind/Framer Motion setup

TASKS:

1. **CREATE CODE EDITOR COMPONENT**

Create `src/shared/components/ui/CodeEditor.tsx`:
- Monaco Editor integration for XML/JSON editing
- Syntax highlighting with StreamWorks-specific keywords
- Error underlining and validation tooltips
- Auto-completion and code snippets
- Theme switching (dark/light mode support)
- Full-screen editing mode with toggle
- Find and replace functionality
- Minimap for large files
- Proper TypeScript interfaces for props

Props interface:
- language: 'xml' | 'json' | 'javascript' | 'typescript'
- value: string
- onChange: (value: string) => void
- height?: string
- theme?: 'vs-dark' | 'vs-light'
- readOnly?: boolean
- showMinimap?: boolean

2. **CREATE ADVANCED DATA TABLE**

Create `src/shared/components/ui/DataTable.tsx`:
- Sortable columns with visual indicators
- Filterable columns with search functionality
- Pagination with configurable page sizes
- Row selection (single and multiple)
- Virtual scrolling for large datasets (1000+ rows)
- Expandable rows for detailed information
- Custom cell renderers for different data types
- Export functionality (CSV, Excel, JSON)
- Loading states and empty state handling
- Mobile-responsive with horizontal scroll

Props interface:
- data: any[]
- columns: Column[]
- sortable?: boolean
- filterable?: boolean
- selectable?: boolean | 'single' | 'multiple'
- exportable?: boolean
- pagination?: boolean
- pageSize?: number
- onRowSelect?: (selectedRows: any[]) => void

3. **CREATE CHART COMPONENTS**

Create `src/shared/components/ui/Chart.tsx`:
- Recharts integration wrapper
- Multiple chart types: LineChart, BarChart, PieChart, AreaChart
- Interactive tooltips and legends
- Zoom and pan capabilities for time-series data
- Real-time data update support
- Export chart as PNG/SVG/PDF
- Responsive design with breakpoint handling
- Custom color schemes matching app theme
- Animation support for data transitions

Create specific chart components:
- `LineChart.tsx` - for analytics trends
- `BarChart.tsx` - for categorical data
- `PieChart.tsx` - for distribution data
- `AreaChart.tsx` - for cumulative metrics

Props interfaces:
- data: ChartData[]
- xKey: string
- yKey: string | string[]
- title?: string
- colors?: string[]
- animated?: boolean
- exportable?: boolean

4. **CREATE ADVANCED MODAL SYSTEM**

Create `src/shared/components/ui/Modal.tsx`:
- Full accessibility with focus management
- Backdrop blur with glassmorphism effect
- Size variants: sm, md, lg, xl, fullscreen
- Smooth enter/exit animations with Framer Motion
- Portal rendering for proper z-index handling
- Escape key and click-outside-to-close
- Nested modal support
- Custom header, body, footer sections
- Mobile-responsive with proper touch handling

Props interface:
- isOpen: boolean
- onClose: () => void
- title?: string
- size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
- showCloseButton?: boolean
- closeOnBackdrop?: boolean
- closeOnEscape?: boolean

5. **CREATE PROFESSIONAL TOAST SYSTEM**

Create `src/shared/components/ui/Toast.tsx` and `ToastProvider.tsx`:
- Toast types: success, error, warning, info, loading
- Auto-dismiss with configurable timing
- Action buttons support (Undo, Retry, etc.)
- Queue management for multiple toasts
- Position variants (top-right, bottom-left, etc.)
- Stack animation effects
- Custom icons and styling
- Accessibility announcements

Hook interface:
- useToast() returning: toast.success(), toast.error(), toast.info(), toast.warning()

REQUIREMENTS:
- All components fully typed with TypeScript
- Consistent with existing Tailwind theme
- Framer Motion animations matching current style
- Proper error boundaries and loading states
- Mobile-responsive and touch-friendly
- WCAG 2.1 accessibility compliance
- Storybook-ready component structure
- Easy integration with existing components

INTEGRATION POINTS:
- CodeEditor: Will be used in XML Generator module
- DataTable: Will enhance Document Management
- Charts: Will power Analytics Dashboard
- Modal: Will improve all dialogs and forms
- Toast: Will provide better user feedback

Test each component with sample data and ensure they work seamlessly with the existing UI.

### **Prompt 3.2: Advanced UI Components**
Create advanced enhancement components that upgrade existing functionality in StreamWorks-KI:

CONTEXT:
- Essential components from Prompt 3.1 are implemented
- Need to add sophisticated interaction components
- Focus on upgrading existing functionality without breaking it
- Maintain consistency with established UI patterns

TASKS:

1. **CREATE ADVANCED FILE UPLOADER**

Create `src/shared/components/ui/AdvancedFileUploader.tsx`:
- Enhanced drag-and-drop with visual feedback states
- Multiple file selection with preview thumbnails
- File type validation with custom error messages
- Progress tracking with individual file progress bars
- Error handling and retry functionality for failed uploads
- Batch operations (select all, remove all, retry failed)
- Image preview with zoom functionality
- File size and type restrictions with clear indicators
- Queue management with pause/resume capabilities

Props interface:
- accept?: string[]
- maxSize?: number
- maxFiles?: number
- onUpload: (files: File[]) => Promise<void>
- onProgress?: (progress: UploadProgress[]) => void
- multiple?: boolean
- preview?: boolean

Enhancement over existing uploader:
- Better visual feedback
- More robust error handling
- Preview capabilities
- Batch management

2. **CREATE ADVANCED SEARCH COMPONENT**

Create `src/shared/components/ui/SearchBox.tsx`:
- Instant search with intelligent debouncing
- Recent searches history with persistence
- Search suggestions and autocomplete
- Advanced filters with expandable panel
- Keyboard navigation (arrow keys, enter, tab)
- Clear and cancel actions with animations
- Loading states and search indicators
- Global search shortcut (⌘K) support
- Search highlighting in results

Props interface:
- placeholder?: string
- suggestions?: string[]
- filters?: FilterConfig[]
- onSearch: (query: string, filters?: any) => void
- showHistory?: boolean
- showFilters?: boolean
- globalShortcut?: boolean

3. **CREATE PROFESSIONAL FORM COMPONENTS**

Create enhanced form components in `src/shared/components/ui/forms/`:
- `FormField.tsx` - Wrapper with label, error, help text
- `Input.tsx` - Enhanced input with validation states
- `Select.tsx` - Custom select with search and multi-select
- `Checkbox.tsx` - Custom checkbox with indeterminate state
- `RadioGroup.tsx` - Radio button group with better styling
- `TextArea.tsx` - Auto-resizing textarea with character count

Features:
- Real-time validation with Zod integration
- Consistent error and success states
- Better accessibility with proper ARIA labels
- Custom styling that matches glassmorphism theme
- Form state management integration

4. **CREATE NAVIGATION COMPONENTS**

Create `src/shared/components/ui/navigation/`:
- `Breadcrumbs.tsx` - Dynamic breadcrumb navigation
- `Tabs.tsx` - Enhanced tab system with animations
- `Sidebar.tsx` - Collapsible sidebar with search
- `CommandPalette.tsx` - Global command search (⌘K)

Features:
- Smooth animations and transitions
- Keyboard navigation support
- Mobile-responsive behavior
- Integration with React Router
- State persistence

5. **CREATE UTILITY COMPONENTS**

Create utility components in `src/shared/components/ui/`:
- `Badge.tsx` - Status indicators with variants
- `Avatar.tsx` - User avatars with online status
- `Spinner.tsx` - Loading indicators with sizes
- `Progress.tsx` - Linear and circular progress bars
- `Skeleton.tsx` - Loading skeletons for content
- `Tooltip.tsx` - Accessible tooltips with positioning

Features:
- Consistent design tokens
- Animation support
- Accessibility features
- Multiple variants and sizes

6. **CREATE LAYOUT COMPONENTS**

Create layout helpers in `src/shared/components/ui/layout/`:
- `Container.tsx` - Responsive container with max-widths
- `Grid.tsx` - CSS Grid wrapper with responsive breakpoints
- `Stack.tsx` - Flexbox stack with spacing
- `Divider.tsx` - Visual separators with variants

REQUIREMENTS:
- Performance optimized with React.memo where appropriate
- Full keyboard accessibility and screen reader support
- Touch-friendly design for mobile devices
- Error boundaries for component robustness
- Loading states and skeleton screens
- Consistent animation timing (200ms for quick, 300ms for standard)
- TypeScript strict mode compliance

INTEGRATION STRATEGY:
- These components should complement, not replace existing UI
- Provide upgrade paths for current components
- Maintain visual consistency with current theme
- Easy to adopt incrementally

TESTING:
- Each component should include usage examples
- Test with real data from your backend APIs
- Verify accessibility with screen readers
- Test on mobile devices and touch interfaces
- Ensure smooth animations on lower-end devices

After implementation, you'll have a professional component library that can be used to build any enterprise feature while maintaining the existing functionality.

## PROMPT 3.2: ADVANCED ENHANCEMENT COMPONENTS

---

## 🧭 **PHASE 4: LAYOUT & NAVIGATION**

### **Prompt 4.1: App Shell & Router**
```
Create the main application shell with routing and navigation for StreamWorks-KI:

1. Create `src/app/router/AppRouter.tsx`:
   - React Router v6 setup with nested routes
   - Protected routes with authentication
   - Lazy loading for code splitting
   - Error boundaries for route errors
   - Loading states between route changes
   - Breadcrumb generation from routes

2. Create `src/shared/components/layout/AppLayout.tsx`:
   - Responsive sidebar navigation
   - Top header with user menu
   - Main content area with proper spacing
   - Mobile-first responsive design
   - Keyboard navigation support
   - Theme toggle integration

3. Create `src/shared/components/layout/Sidebar.tsx`:
   - Collapsible sidebar with animations
   - Navigation items with icons and badges
   - Active state highlighting
   - Nested menu support
   - Search functionality for menu items
   - Keyboard shortcuts display
   - User profile section

4. Create `src/shared/components/layout/Header.tsx`:
   - Breadcrumb navigation
   - Global search bar
   - Notification center
   - User dropdown menu
   - Theme switcher
   - Settings access
   - System status indicator

5. Set up these routes:
   - `/dashboard` - Main dashboard
   - `/chat` - AI Chat interface
   - `/documents` - Document management
   - `/xml-generator` - XML creation tools
   - `/analytics` - Analytics dashboard
   - `/monitoring` - System monitoring
   - `/training` - Training data management
   - `/settings` - Application settings

6. Create `src/app/providers/AppProviders.tsx`:
   - React Query provider with configuration
   - Theme provider for dark/light mode
   - Error boundary for global error handling
   - Toast notification provider
   - Authentication context

Requirements:
- Smooth route transitions with Framer Motion
- Mobile-responsive navigation
- Keyboard shortcuts for navigation
- Proper loading states
- Error handling for failed route loads
- SEO-friendly route structure
```

### **Prompt 4.2: Navigation & Breadcrumbs**
```
Enhance the navigation system with advanced features for StreamWorks-KI:

1. Create `src/shared/components/layout/Navigation.tsx`:
   - Dynamic navigation based on user permissions
   - Badge notifications for modules (document count, unread messages)
   - Recent items quick access
   - Favorite/bookmarked sections
   - Contextual actions per navigation item
   - Search within navigation

2. Create `src/shared/components/layout/Breadcrumbs.tsx`:
   - Auto-generated from route structure
   - Clickable segments for quick navigation
   - Dynamic titles based on current content
   - Dropdown for skipped segments in deep paths
   - Copy current path functionality
   - Custom breadcrumb override support

3. Create `src/shared/components/layout/CommandPalette.tsx`:
   - Global command search (⌘K shortcut)
   - Quick actions (create document, start chat, etc.)
   - Recent commands history
   - Fuzzy search across all app functions
   - Keyboard-only navigation
   - Custom action plugins

4. Create `src/shared/components/layout/QuickActions.tsx`:
   - Floating action button on mobile
   - Context-aware actions per page
   - Bulk operations when items selected
   - Keyboard shortcuts display
   - Recently used actions

5. Add navigation enhancements:
   - Progress indicators for long operations
   - Contextual help tooltips
   - Onboarding tour integration points
   - Activity indicators (live updates)
   - Offline mode indicators

6. Create `src/shared/hooks/useNavigation.ts`:
   - Programmatic navigation with state
   - Back/forward navigation handling
   - Deep linking support
   - Navigation analytics tracking
   - Route-based permissions checking

Requirements:
- Intuitive user experience
- Fast navigation performance
- Accessibility compliance
- Mobile gesture support
- Keyboard shortcut system
- Context preservation during navigation
```

---

## 💬 **PHASE 5: CHAT MODULE**

### **Prompt 5.1: AI Chat Interface**
```
Create an advanced AI chat interface with RAG capabilities for StreamWorks-KI:

1. Create `src/features/chat/components/ChatInterface.tsx`:
   - Modern chat UI with bubble design
   - Real-time message streaming
   - Source citation display for RAG responses
   - Message timestamps and status indicators
   - Copy message functionality
   - Message threading support
   - Typing indicators
   - Auto-scroll to bottom with manual override

2. Create `src/features/chat/components/MessageBubble.tsx`:
   - User and AI message variants
   - Markdown rendering for formatted responses
   - Code syntax highlighting
   - Link previews and click handling
   - Image attachments display
   - Message actions (copy, share, delete)
   - Citation expandable sections
   - Message reactions/rating

3. Create `src/features/chat/components/ChatInput.tsx`:
   - Auto-expanding textarea
   - File attachment button
   - Send button with loading state
   - Character count indicator
   - Message suggestions/quick replies
   - Voice input integration
   - Emoji picker
   - Drag and drop file uploads

4. Create `src/features/chat/components/ChatSidebar.tsx`:
   - Conversation history list
   - Search conversations
   - Create new chat button
   - Conversation folders/categories
   - Export conversation options
   - Delete conversation with confirmation
   - Conversation metadata (date, message count)

5. Add advanced chat features:
   - Message search within conversation
   - Conversation branching (explore topics)
   - Quick document upload during chat
   - Response regeneration
   - Context-aware suggestions
   - Chat templates for common queries

6. Create `src/features/chat/hooks/useChat.ts`:
   - WebSocket connection for streaming
   - Message state management
   - Optimistic updates
   - Error handling and retry
   - Auto-save draft messages
   - Conversation persistence

Requirements:
- Real-time streaming responses
- Excellent mobile experience
- Accessibility for screen readers
- Smooth animations and transitions
- Robust error handling
- Performance optimization for long conversations
```

### **Prompt 5.2: Chat History & Management**
```
Enhance the chat system with conversation management and search capabilities:

1. Create `src/features/chat/components/ConversationList.tsx`:
   - Virtualized list for performance
   - Conversation previews with last message
   - Search and filter conversations
   - Sort by date, relevance, or custom
   - Bulk operations (delete, export, archive)
   - Conversation folders/categories
   - Star/favorite conversations
   - Conversation sharing

2. Create `src/features/chat/components/ChatSearch.tsx`:
   - Full-text search across all conversations
   - Advanced filters (date range, participants, keywords)
   - Search result highlighting
   - Jump to message in conversation
   - Search suggestions and history
   - Export search results
   - Save search queries

3. Create `src/features/chat/components/ExportDialog.tsx`:
   - Multiple export formats (PDF, Markdown, HTML, JSON)
   - Date range selection
   - Include/exclude attachments
   - Custom formatting options
   - Bulk export multiple conversations
   - Email export option
   - Progress indicator for large exports

4. Create `src/features/chat/components/ChatSettings.tsx`:
   - Message retention policies
   - Notification preferences
   - Chat appearance customization
   - Auto-save settings
   - Privacy settings
   - Integration preferences
   - Keyboard shortcuts configuration

5. Add conversation analytics:
   - Message frequency charts
   - Most discussed topics
   - Response time analytics
   - Conversation quality metrics
   - Usage patterns
   - Export analytics data

6. Create `src/features/chat/services/chatAnalytics.ts`:
   - Track conversation metrics
   - Generate insights
   - Performance monitoring
   - User behavior analysis
   - A/B testing support
   - Quality scoring

Requirements:
- Fast search across large conversation histories
- Efficient data loading and caching
- Privacy and security considerations
- Intuitive user interface
- Mobile-optimized interactions
- Data export capabilities
```

---

## 📁 **PHASE 6: DOCUMENT MANAGEMENT**

### **Prompt 6.1: Document Management Core**
```
Create a comprehensive document management system for StreamWorks-KI:

1. Create `src/features/documents/components/DocumentManager.tsx`:
   - Three-panel layout (categories, files, preview)
   - Hierarchical folder structure display
   - Drag and drop file organization
   - Bulk selection and operations
   - Context menus for all actions
   - Real-time status updates
   - Search and filter integration

2. Create `src/features/documents/components/FileGrid.tsx`:
   - Grid and list view modes
   - File thumbnails and previews
   - Sort options (name, date, size, type)
   - Multi-select with checkboxes
   - File status indicators (processing, indexed, error)
   - Quick actions overlay
   - Infinite scroll for large collections
   - File type icons and colors

3. Create `src/features/documents/components/FileUpload.tsx`:
   - Modern drag-and-drop interface
   - Multiple file selection
   - Progress tracking with cancellation
   - File validation and error handling
   - Category and folder selection
   - Batch metadata assignment
   - Preview before upload
   - Automatic duplicate detection

4. Create `src/features/documents/components/DocumentPreview.tsx`:
   - PDF viewer integration
   - Text file syntax highlighting
   - Image gallery with zoom
   - Video and audio players
   - Markdown rendering
   - XML tree view
   - Metadata editor panel
   - Download and share options

5. Create `src/features/documents/components/CategoryTree.tsx`:
   - Expandable tree structure
   - Drag and drop between categories
   - Category creation and editing
   - File count badges
   - Search within categories
   - Category permissions display
   - Sorting and filtering options

6. Add advanced features:
   - Version history tracking
   - Document tagging system
   - Automated content extraction
   - Duplicate file detection
   - Bulk metadata editing
   - Advanced search with filters

Requirements:
- High performance with large file collections
- Intuitive drag-and-drop interactions
- Mobile-responsive design
- Accessibility compliance
- Real-time updates
- Robust error handling
```

### **Prompt 6.2: Document Processing & Search**
```
Add advanced document processing and search capabilities to the document management system:

1. Create `src/features/documents/components/ProcessingQueue.tsx`:
   - Live processing status display
   - Queue management with priorities
   - Error details and retry options
   - Processing time estimates
   - Batch processing controls
   - Processing history log
   - Resource usage monitoring
   - Pause/resume functionality

2. Create `src/features/documents/components/AdvancedSearch.tsx`:
   - Full-text content search
   - Metadata filtering (date, size, type, category)
   - Saved search queries
   - Search result highlighting
   - Faceted search with counts
   - Search suggestions and autocomplete
   - Export search results
   - Search analytics tracking

3. Create `src/features/documents/components/DocumentAnalytics.tsx`:
   - Upload trends and statistics
   - File type distribution charts
   - Processing performance metrics
   - Storage usage monitoring
   - Access patterns analysis
   - Error rate tracking
   - User activity reports
   - Automated insights

4. Create `src/features/documents/components/BulkOperations.tsx`:
   - Multi-select interface
   - Batch actions (move, delete, tag, reprocess)
   - Progress tracking for bulk operations
   - Undo functionality
   - Bulk metadata editing
   - Batch export options
   - Operation scheduling
   - Error handling and reporting

5. Create `src/features/documents/components/DocumentMetadata.tsx`:
   - Editable metadata fields
   - Custom field definitions
   - Metadata templates
   - Auto-extraction from content
   - Metadata validation rules
   - History tracking
   - Bulk metadata import/export
   - Metadata search and filtering

6. Add integration features:
   - OCR for scanned documents
   - Content-based categorization
   - Automatic tagging suggestions
   - Document similarity detection
   - Integration with external storage
   - API access for document operations

Requirements:
- Real-time processing updates
- Efficient search performance
- Scalable for large document collections
- User-friendly bulk operations
- Comprehensive error handling
- Mobile-optimized interface
```

---

## 🔧 **PHASE 7: XML GENERATOR**

### **Prompt 7.1: XML Visual Builder**
```
Create a sophisticated XML generator with visual building capabilities for StreamWorks workflows:

1. Create `src/features/xml-generator/components/XMLBuilder.tsx`:
   - Split-panel layout (visual builder + code editor)
   - Drag and drop component palette
   - Visual workflow representation
   - Real-time XML generation
   - Validation with error highlighting
   - Zoom and pan controls
   - Full-screen modes
   - Template integration

2. Create `src/features/xml-generator/components/ComponentPalette.tsx`:
   - StreamWorks component library
   - Categorized components (Jobs, Streams, Agents, etc.)
   - Search components by name/function
   - Drag and drop to canvas
   - Component documentation tooltips
   - Recently used components
   - Custom component creation
   - Import/export component sets

3. Create `src/features/xml-generator/components/PropertyPanel.tsx`:
   - Context-sensitive property editing
   - Form validation with real-time feedback
   - Advanced property types (dropdowns, date pickers, etc.)
   - Property documentation and examples
   - Conditional property display
   - Property templates and presets
   - Copy/paste property values
   - Property history and undo

4. Create `src/features/xml-generator/components/XMLPreview.tsx`:
   - Monaco Editor with XML syntax highlighting
   - Error underlining and tooltips
   - Auto-formatting and indentation
   - Find and replace functionality
   - Code folding and minimap
   - Export options (file, clipboard, direct save)
   - Diff view for template comparison
   - Full-screen editing mode

5. Create `src/features/xml-generator/components/TemplateLibrary.tsx`:
   - Pre-built StreamWorks templates
   - Template categories and tags
   - Template search and filtering
   - Template preview and documentation
   - Custom template creation
   - Template sharing and import
   - Version control for templates
   - Template usage analytics

6. Add workflow features:
   - Workflow validation against StreamWorks schema
   - Dependency checking between components
   - Auto-completion for properties
   - Visual connection between related elements
   - Workflow testing and simulation
   - Integration with StreamWorks API

Requirements:
- Intuitive visual interface
- Real-time XML generation
- Comprehensive validation
- Professional code editor experience
- Template system for reusability
- StreamWorks-specific functionality
```

### **Prompt 7.2: XML Editor & Validation**
```
Enhance the XML generator with advanced editing and validation capabilities:

1. Create `src/features/xml-generator/components/XMLValidator.tsx`:
   - Real-time syntax validation
   - StreamWorks schema validation
   - Business rule validation
   - Dependency conflict detection
   - Warning and error categorization
   - Quick fix suggestions
   - Validation report generation
   - Custom validation rules

2. Create `src/features/xml-generator/components/CodeAssist.tsx`:
   - Intelligent auto-completion
   - Snippet insertion
   - Parameter hints and documentation
   - Refactoring tools (rename, extract)
   - Code navigation (go to definition)
   - Symbol outline and search
   - Bracket matching and highlighting
   - Multi-cursor editing support

3. Create `src/features/xml-generator/components/XMLDiff.tsx`:
   - Side-by-side comparison view
   - Inline diff highlighting
   - Merge conflict resolution
   - Three-way merge support
   - Change summary statistics
   - Accept/reject individual changes
   - Export diff reports
   - History comparison

4. Create `src/features/xml-generator/components/ProjectManager.tsx`:
   - XML project organization
   - Multiple file management
   - Project templates
   - Import/export projects
   - Project-wide search and replace
   - Dependency management
   - Build and deployment tools
   - Project sharing and collaboration

5. Create `src/features/xml-generator/components/XMLTesting.tsx`:
   - Syntax testing and validation
   - Dry-run execution simulation
   - Test case management
   - Performance impact analysis
   - Integration testing tools
   - Test report generation
   - Automated testing workflows
   - Regression testing

6. Add professional features:
   - Version control integration
   - Collaborative editing indicators
   - Comment and annotation system
   - Code quality metrics
   - Performance optimization suggestions
   - Integration with external XML tools

Requirements:
- Professional IDE-like experience
- Advanced validation and error handling
- Collaboration features
- Version control integration
- Extensible architecture
- High performance with large XML files
```

---

## 📊 **PHASE 8: ANALYTICS DASHBOARD**

### **Prompt 8.1: Analytics Dashboard Core**
```
Create a comprehensive analytics dashboard for StreamWorks-KI with real-time insights:

1. Create `src/features/analytics/components/AnalyticsDashboard.tsx`:
   - Grid-based dashboard layout
   - Draggable and resizable widgets
   - Custom dashboard creation
   - Real-time data updates
   - Export dashboard as PDF/image
   - Dashboard templates
   - Full-screen widget mode
   - Mobile-responsive design

2. Create `src/features/analytics/components/MetricsOverview.tsx`:
   - Key performance indicators (KPIs)
   - Trend indicators with sparklines
   - Comparison periods (vs last week/month)
   - Goal tracking and progress
   - Alert thresholds with notifications
   - Drill-down capabilities
   - Custom metric definitions
   - Real-time metric updates

3. Create `src/features/analytics/components/ChatAnalytics.tsx`:
   - Query volume trends
   - Response time analytics
   - Success rate monitoring
   - Popular queries analysis
   - User satisfaction scores
   - Topic analysis and clustering
   - Response quality metrics
   - A/B testing results

4. Create `src/features/analytics/components/DocumentAnalytics.tsx`:
   - Upload trends and patterns
   - Processing performance metrics
   - File type distribution
   - Storage usage analytics
   - Access frequency analysis
   - Content popularity rankings
   - Processing error analysis
   - User activity patterns

5. Create `src/features/analytics/components/SystemAnalytics.tsx`:
   - System performance monitoring
   - Resource utilization trends
   - API endpoint performance
   - Error rate tracking
   - Service availability metrics
   - Database performance analysis
   - Cache hit rates
   - Security event monitoring

6. Add interactive features:
   - Interactive chart drilling
   - Custom date range selection
   - Real-time filtering and segmentation
   - Comparative analysis tools
   - Forecast and trend prediction
   - Automated insight generation

Requirements:
- Real-time data visualization
- Interactive and responsive charts
- Customizable dashboard layouts
- High performance with large datasets
- Export and sharing capabilities
- Mobile-optimized experience
```

### **Prompt 8.2: Advanced Analytics & Reporting**
```
Add advanced analytics capabilities and reporting features to the analytics dashboard:

1. Create `src/features/analytics/components/ReportBuilder.tsx`:
   - Drag-and-drop report creation
   - Multiple visualization types
   - Custom data filtering and grouping
   - Scheduled report generation
   - Report templates and themes
   - Interactive parameter controls
   - Export to multiple formats
   - Report sharing and distribution

2. Create `src/features/analytics/components/DataExplorer.tsx`:
   - Interactive data table with filtering
   - Ad-hoc query builder
   - Data visualization wizard
   - Statistical analysis tools
   - Data correlation analysis
   - Custom calculated fields
   - Data sampling and aggregation
   - Export to CSV/Excel/JSON

3. Create `src/features/analytics/components/AlertManager.tsx`:
   - Custom alert condition creation
   - Real-time alert monitoring
   - Alert history and trends
   - Notification channel management
   - Alert escalation workflows
   - Threshold-based alerting
   - Anomaly detection alerts
   - Alert dashboard and status

4. Create `src/features/analytics/components/ForecastingEngine.tsx`:
   - Time series forecasting
   - Trend analysis and projection
   - Seasonal pattern detection
   - Confidence interval display
   - Multiple forecasting models
   - Forecast accuracy tracking
   - What-if scenario analysis
   - Automated model selection

5. Create `src/features/analytics/components/PerformanceInsights.tsx`:
   - Automated insight generation
   - Performance bottleneck identification
   - Optimization recommendations
   - Comparative benchmarking
   - Resource usage optimization
   - Cost analysis and projections
   - Efficiency scoring
   - Action item prioritization

6. Add enterprise features:
   - Role-based access to analytics
   - Data governance and lineage
   - Audit trail for data access
   - Integration with BI tools
   - API access for external tools
   - Data backup and archival

Requirements:
- Advanced statistical analysis
- Machine learning integration
- Scalable data processing
- Enterprise security features
- Comprehensive reporting
- API-driven architecture
```

---

## 🔍 **PHASE 9: SYSTEM MONITORING**

### **Prompt 9.1: System Health Dashboard**
```
Create a comprehensive system monitoring dashboard for StreamWorks-KI operations:

1. Create `src/features/monitoring/components/SystemDashboard.tsx`:
   - Real-time system status overview
   - Service health indicators
   - Performance metrics visualization
   - Alert and notification center
   - System topology view
   - Resource utilization charts
   - Incident management integration
   - Mobile-responsive monitoring

2. Create `src/features/monitoring/components/ServiceStatus.tsx`:
   - Individual service health cards
   - Uptime and availability metrics
   - Response time monitoring
   - Error rate tracking
   - Dependency status visualization
   - Service restart capabilities
   - Configuration status
   - Performance trend analysis

3. Create `src/features/monitoring/components/PerformanceMonitor.tsx`:
   - Real-time performance charts
   - CPU, memory, and disk usage
   - Network traffic monitoring
   - Database performance metrics
   - API endpoint response times
   - Throughput and latency analysis
   - Performance baseline comparison
   - Capacity planning insights

4. Create `src/features/monitoring/components/LogViewer.tsx`:
   - Real-time log streaming
   - Log level filtering and search
   - Contextual log highlighting
   - Log export and download
   - Error pattern detection
   - Log aggregation and analysis
   - Custom log parsing rules
   - Log retention management

5. Create `src/features/monitoring/components/AlertCenter.tsx`:
   - Active alert management
   - Alert history and trends
   - Alert rule configuration
   - Escalation workflow management
   - Multi-channel notifications
   - Alert correlation analysis
   - Incident response tracking
   - Alert acknowledgment system

6. Add monitoring features:
   - Custom metric creation
   - Synthetic monitoring tests
   - Infrastructure monitoring
   - Application performance monitoring
   - User experience monitoring
   - Security event monitoring

Requirements:
- Real-time data streaming
- High-performance visualization
- Customizable alert rules
- Multi-level monitoring
- Comprehensive logging
- Mobile accessibility
```

### **Prompt 9.2: Advanced Monitoring & Diagnostics**
```
Enhance the monitoring system with advanced diagnostics and troubleshooting capabilities:

1. Create `src/features/monitoring/components/DiagnosticCenter.tsx`:
   - Automated health checks
   - System diagnostic reports
   - Performance bottleneck analysis
   - Resource conflict detection
   - Configuration validation
   - Dependency verification
   - Security scan results
   - Remediation recommendations

2. Create `src/features/monitoring/components/TroubleshootingWizard.tsx`:
   - Step-by-step problem diagnosis
   - Interactive decision trees
   - Automated fix suggestions
   - Knowledge base integration
   - Escalation to support
   - Solution tracking and rating
   - Common issues database
   - Fix history and analytics

3. Create `src/features/monitoring/components/MetricsExplorer.tsx`:
   - Custom metric visualization
   - Multi-dimensional data analysis
   - Correlation analysis between metrics
   - Anomaly detection and highlighting
   - Threshold-based alerting
   - Metric comparison tools
   - Time series analysis
   - Predictive analytics

4. Create `src/features/monitoring/components/IncidentManagement.tsx`:
   - Incident creation and tracking
   - Severity classification
   - Response team coordination
   - Timeline and activity tracking
   - Root cause analysis tools
   - Post-incident review
   - Incident analytics and trends
   - Integration with external tools

5. Create `src/features/monitoring/components/MaintenanceScheduler.tsx`:
   - Scheduled maintenance planning
   - Impact assessment tools
   - User notification system
   - Rollback and recovery planning
   - Maintenance history tracking
   - Automated maintenance tasks
   - Maintenance window optimization
   - Change management integration

6. Add enterprise features:
   - Multi-tenant monitoring
   - Role-based access control
   - Audit trail and compliance
   - Integration with ITSM tools
   - Custom monitoring plugins
   - API for external integrations

Requirements:
- Advanced diagnostic capabilities
- Automated problem resolution
- Enterprise-grade incident management
- Predictive analytics
- Comprehensive audit trails
- High availability monitoring
```

---

## 🎯 **PHASE 10: FINAL INTEGRATION**

### **Prompt 10.1: Final Integration & Polish**
```
Complete the StreamWorks-KI frontend with final integrations, optimizations, and polish:

1. Create `src/app/App.tsx` - Complete application integration:
   - Router setup with all feature modules
   - Global providers and context
   - Error boundary implementation
   - Loading states and suspense
   - Theme system integration
   - Performance monitoring
   - Analytics tracking setup
   - Accessibility enhancements

2. Create comprehensive error handling:
   - Global error boundary with user-friendly messages
   - API error handling with retry mechanisms
   - Network error detection and offline support
   - Form validation error display
   - Graceful degradation for missing features
   - Error reporting and logging
   - User feedback collection
   - Error recovery suggestions

3. Add performance optimizations:
   - Code splitting for all feature modules
   - Lazy loading for heavy components
   - Image optimization and lazy loading
   - Virtual scrolling for large lists
   - Memoization for expensive calculations
   - Service worker for caching
   - Bundle size optimization
   - Performance monitoring integration

4. Implement accessibility features:
   - Screen reader support throughout
   - Keyboard navigation for all features
   - ARIA labels and descriptions
   - Focus management and indicators
   - Color contrast compliance
   - Reduced motion preferences
   - Text scaling support
   - Accessibility testing integration

5. Add user experience enhancements:
   - Loading skeletons for all content
   - Smooth page transitions
   - Contextual help and tooltips
   - Onboarding tour for new users
   - Keyboard shortcuts help
   - Undo/redo functionality
   - Auto-save for forms
   - Offline mode support

6. Testing and quality assurance:
   - Unit tests for all components
   - Integration tests for user flows
   - E2E tests for critical paths
   - Performance testing
   - Accessibility testing
   - Cross-browser compatibility
   - Mobile device testing
   - Load testing preparation

Requirements:
- Production-ready code quality
- Comprehensive error handling
- Excellent performance metrics
- Full accessibility compliance
- Smooth user experience
- Robust testing coverage
```

### **Prompt 10.2: Deployment & Documentation**
```
Finalize the StreamWorks-KI frontend for production deployment with comprehensive documentation:

1. Create production build configuration:
   - Optimized Vite build setup
   - Environment variable management
   - Build script optimization
   - Asset optimization and compression
   - Source map configuration
   - Bundle analysis and optimization
   - Docker containerization
   - CI/CD pipeline preparation

2. Create comprehensive documentation:
   - README with setup instructions
   - API integration guide
   - Component library documentation
   - Deployment guide
   - Contributing guidelines
   - Architecture decision records
   - Performance optimization guide
   - Troubleshooting documentation

3. Add monitoring and analytics:
   - Application performance monitoring
   - User behavior analytics
   - Error tracking and reporting
   - Feature usage analytics
   - Performance metrics collection
   - A/B testing framework
   - User feedback collection
   - Health check endpoints

4. Security implementation:
   - Content Security Policy
   - XSS protection measures
   - Input sanitization
   - Secure cookie handling
   - HTTPS enforcement
   - Authentication integration
   - Authorization checks
   - Security audit compliance

5. Final testing and validation:
   - Cross-browser testing
   - Mobile responsiveness testing
   - Performance testing
   - Security testing
   - Accessibility audit
   - User acceptance testing
   - Load testing
   - Integration testing with backend

6. Production readiness checklist:
   - Environment configuration
   - Error monitoring setup
   - Backup and recovery procedures
   - Monitoring and alerting
   - Documentation completeness
   - Security compliance
   - Performance benchmarks
   - Deployment automation

Requirements:
- Production-grade security
- Comprehensive monitoring
- Complete documentation
- Automated deployment
- Performance optimization
- User-ready experience
```

---

## ✅ **EXECUTION CHECKLIST**

### **Phase Completion Validation**
After each phase, verify:
- [ ] All components render without errors
- [ ] TypeScript compilation succeeds
- [ ] Unit tests pass
- [ ] ESLint and Prettier checks pass
- [ ] Performance metrics are acceptable
- [ ] Mobile responsiveness works
- [ ] Accessibility standards met

### **Final Quality Gates**
Before considering complete:
- [ ] All backend APIs integrated and tested
- [ ] Full user journey testing completed
- [ ] Performance benchmarks met
- [ ] Security review passed
- [ ] Documentation complete
- [ ] Production deployment ready

### **Success Metrics**
Target achievements:
- [ ] **Performance**: First Contentful Paint < 1.5s
- [ ] **Accessibility**: WCAG 2.1 AA compliance
- [ ] **Code Quality**: 90%+ test coverage
- [ ] **User Experience**: Intuitive navigation
- [ ] **Functionality**: All backend features accessible
- [ ] **Mobile**: Fully responsive design

**RESULT: Ein enterprise-grade, modulares Frontend-System das optimal alle Backend-Features nutzt und für agile Weiterentwicklung designt ist! 🚀**