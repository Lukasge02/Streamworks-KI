/**
 * UI Component and State Type Definitions
 */

import type { ReactNode } from 'react';

// Theme Types
export type Theme = 'light' | 'dark' | 'system';

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  error: string;
  warning: string;
  success: string;
  info: string;
}

// Notification Types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  persistent?: boolean;
  actions?: Array<{
    label: string;
    action: () => void;
    variant?: 'primary' | 'secondary';
  }>;
  timestamp: string;
}

// Modal Types
export interface Modal {
  id: string;
  type: 'confirm' | 'info' | 'form' | 'custom';
  title: string;
  content: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closable?: boolean;
  actions?: Array<{
    label: string;
    action: () => void;
    variant?: 'primary' | 'secondary' | 'danger';
    loading?: boolean;
  }>;
}

// Loading States
export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
}

export interface AsyncOperationState<T = any> {
  data?: T;
  loading: boolean;
  error?: string;
  lastUpdated?: string;
}

// Form Types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'textarea' | 'select' | 'checkbox' | 'file';
  required?: boolean;
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    custom?: (value: any) => string | undefined;
  };
}

export interface FormState<T = Record<string, any>> {
  values: T;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
}

// Table Types
export interface TableColumn<T = any> {
  key: keyof T;
  title: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, row: T) => ReactNode;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
}

export interface TableState<T = any> {
  data: T[];
  loading: boolean;
  pagination: {
    page: number;
    pageSize: number;
    total: number;
  };
  sorting: {
    field?: keyof T;
    direction: 'asc' | 'desc';
  };
  filters: Record<string, any>;
  selection: T[];
}

// Navigation Types
export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: string;
  badge?: {
    text: string;
    variant: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  };
  children?: NavigationItem[];
  permissions?: string[];
}

// Layout Types
export interface LayoutState {
  sidebarCollapsed: boolean;
  sidebarWidth: number;
  headerHeight: number;
  footerVisible: boolean;
  breadcrumbs: Array<{
    label: string;
    path?: string;
  }>;
}

// Search Types
export interface SearchState {
  query: string;
  filters: Record<string, any>;
  results: any[];
  loading: boolean;
  suggestions: string[];
  recentSearches: string[];
}

// File Upload Types
export interface FileUploadState {
  files: Array<{
    id: string;
    file: File;
    progress: number;
    status: 'pending' | 'uploading' | 'completed' | 'error';
    error?: string;
    url?: string;
  }>;
  maxFiles: number;
  maxSize: number;
  acceptedTypes: string[];
  multiple: boolean;
}

// Chart Types
export interface ChartDataPoint {
  x: string | number;
  y: number;
  label?: string;
  color?: string;
}

export interface ChartSeries {
  name: string;
  data: ChartDataPoint[];
  color?: string;
  type?: 'line' | 'bar' | 'area' | 'pie';
}

export interface ChartConfig {
  title?: string;
  subtitle?: string;
  xAxis?: {
    title?: string;
    type?: 'category' | 'datetime' | 'numeric';
    format?: string;
  };
  yAxis?: {
    title?: string;
    format?: string;
    min?: number;
    max?: number;
  };
  legend?: {
    show: boolean;
    position?: 'top' | 'bottom' | 'left' | 'right';
  };
  tooltip?: {
    format?: string;
    shared?: boolean;
  };
}

// Context Menu Types
export interface ContextMenuItem {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;
  disabled?: boolean;
  separator?: boolean;
  children?: ContextMenuItem[];
  action: () => void;
}

// Drag and Drop Types
export interface DragDropState {
  isDragging: boolean;
  draggedItem?: any;
  dropZone?: string;
  canDrop: boolean;
}

// Keyboard Shortcut Types
export interface KeyboardShortcut {
  keys: string[];
  description: string;
  action: () => void;
  global?: boolean;
  preventDefault?: boolean;
}

// Virtual List Types
export interface VirtualListItem {
  id: string;
  height: number;
  data: any;
}

export interface VirtualListState {
  items: VirtualListItem[];
  visibleRange: {
    start: number;
    end: number;
  };
  scrollTop: number;
  containerHeight: number;
}

// Responsive Types
export type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';

export interface ResponsiveState {
  breakpoint: Breakpoint;
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
}

// Component Prop Types
export interface BaseComponentProps {
  className?: string;
  children?: ReactNode;
  id?: string;
  'data-testid'?: string;
}

export interface ClickableProps {
  onClick?: (event: React.MouseEvent) => void;
  onDoubleClick?: (event: React.MouseEvent) => void;
  disabled?: boolean;
  loading?: boolean;
}

export interface FocusableProps {
  onFocus?: (event: React.FocusEvent) => void;
  onBlur?: (event: React.FocusEvent) => void;
  autoFocus?: boolean;
  tabIndex?: number;
}

// Animation Types
export interface AnimationProps {
  duration?: number;
  delay?: number;
  easing?: string;
  direction?: 'normal' | 'reverse' | 'alternate';
  fillMode?: 'none' | 'forwards' | 'backwards' | 'both';
}

export interface TransitionState {
  entering: boolean;
  entered: boolean;
  exiting: boolean;
  exited: boolean;
}