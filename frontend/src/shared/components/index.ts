/**
 * Shared UI components for StreamWorks-KI
 */

// Layout Components
export { Layout } from './Layout/Layout';

// Navigation Components
export { Sidebar } from './Navigation/Sidebar';

// Basic UI Components
export { Button } from './UI/Button';
export { Input } from './UI/Input';
export { Card, CardHeader, CardContent, CardFooter } from './UI/Card';
export { LoadingSpinner } from './UI/LoadingSpinner';

// Advanced Enterprise Components
export { CodeEditor, useCodeEditor } from './UI/CodeEditor';
export { DataTable, type Column } from './UI/DataTable';
export { LineChart, BarChart, AreaChart, PieChart, colorSchemes, useChart } from './UI/Chart';
export { Modal, ConfirmModal, useModal, ModalStackProvider, useModalStack } from './UI/Modal';
export { ToastProvider, useToast, toastPresets, type Toast, type ToastType, type ToastPosition } from './UI/Toast';

// Error Handling
export { ErrorBoundary } from './ErrorBoundary/ErrorBoundary';

// Export types
export type { ButtonProps } from './UI/Button';
export type { InputProps } from './UI/Input';