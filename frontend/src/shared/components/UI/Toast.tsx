/**
 * Professional Toast Notification System
 * Accessible toast notifications with queue management and animations
 */

import React, { createContext, useContext, useCallback, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Info, 
  X, 
  RotateCcw,
  ExternalLink,
  Copy,
} from 'lucide-react';
import { Button } from './Button';

export type ToastType = 'success' | 'error' | 'warning' | 'info' | 'loading';
export type ToastPosition = 
  | 'top-left' 
  | 'top-center' 
  | 'top-right' 
  | 'bottom-left' 
  | 'bottom-center' 
  | 'bottom-right';

export interface ToastAction {
  label: string;
  action: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
}

export interface Toast {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
  persistent?: boolean;
  actions?: ToastAction[];
  icon?: React.ReactNode;
  onClose?: () => void;
  progress?: number;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearAllToasts: () => void;
  updateToast: (id: string, updates: Partial<Toast>) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

// Toast Icons
const toastIcons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
  loading: () => (
    <div className="animate-spin rounded-full h-5 w-5 border-2 border-current border-t-transparent" />
  ),
};

// Toast Styles
const toastStyles = {
  success: {
    bg: 'bg-green-50 dark:bg-green-900/30',
    border: 'border-green-200 dark:border-green-700',
    icon: 'text-green-600 dark:text-green-400',
    title: 'text-green-900 dark:text-green-100',
    message: 'text-green-700 dark:text-green-200',
  },
  error: {
    bg: 'bg-red-50 dark:bg-red-900/30',
    border: 'border-red-200 dark:border-red-700',
    icon: 'text-red-600 dark:text-red-400',
    title: 'text-red-900 dark:text-red-100',
    message: 'text-red-700 dark:text-red-200',
  },
  warning: {
    bg: 'bg-yellow-50 dark:bg-yellow-900/30',
    border: 'border-yellow-200 dark:border-yellow-700',
    icon: 'text-yellow-600 dark:text-yellow-400',
    title: 'text-yellow-900 dark:text-yellow-100',
    message: 'text-yellow-700 dark:text-yellow-200',
  },
  info: {
    bg: 'bg-blue-50 dark:bg-blue-900/30',
    border: 'border-blue-200 dark:border-blue-700',
    icon: 'text-blue-600 dark:text-blue-400',
    title: 'text-blue-900 dark:text-blue-100',
    message: 'text-blue-700 dark:text-blue-200',
  },
  loading: {
    bg: 'bg-neutral-50 dark:bg-neutral-800',
    border: 'border-neutral-200 dark:border-neutral-600',
    icon: 'text-neutral-600 dark:text-neutral-400',
    title: 'text-neutral-900 dark:text-neutral-100',
    message: 'text-neutral-700 dark:text-neutral-300',
  },
};

// Position Classes
const positionClasses: Record<ToastPosition, string> = {
  'top-left': 'top-4 left-4',
  'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
  'top-right': 'top-4 right-4',
  'bottom-left': 'bottom-4 left-4',
  'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2',
  'bottom-right': 'bottom-4 right-4',
};

// Animation Variants
const getToastVariants = (position: ToastPosition) => {
  const isTop = position.includes('top');
  const isLeft = position.includes('left');
  const isRight = position.includes('right');
  
  let x = 0;
  let y = isTop ? -100 : 100;
  
  if (isLeft) x = -100;
  if (isRight) x = 100;
  
  return {
    initial: { opacity: 0, x, y, scale: 0.95 },
    animate: { 
      opacity: 1, 
      x: 0, 
      y: 0, 
      scale: 1,
      transition: { 
        type: 'spring', 
        damping: 25, 
        stiffness: 300 
      }
    },
    exit: { 
      opacity: 0, 
      x, 
      y: y * 0.5, 
      scale: 0.95,
      transition: { duration: 0.2 }
    },
  };
};

// Individual Toast Component
function ToastItem({ 
  toast, 
  onRemove, 
  position 
}: { 
  toast: Toast; 
  onRemove: (id: string) => void; 
  position: ToastPosition;
}) {
  const timeoutRef = React.useRef<NodeJS.Timeout>();
  const [progress, setProgress] = React.useState(100);
  
  const styles = toastStyles[toast.type];
  const IconComponent = toast.icon ? () => toast.icon : toastIcons[toast.type];
  
  // Auto-dismiss logic
  useEffect(() => {
    if (!toast.persistent && toast.duration && toast.duration > 0) {
      const startTime = Date.now();
      const updateInterval = 50; // Update every 50ms for smooth progress
      
      const updateProgress = () => {
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(0, toast.duration! - elapsed);
        const progressPercent = (remaining / toast.duration!) * 100;
        
        setProgress(progressPercent);
        
        if (remaining <= 0) {
          onRemove(toast.id);
        } else {
          timeoutRef.current = setTimeout(updateProgress, updateInterval);
        }
      };
      
      updateProgress();
    }
    
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [toast.duration, toast.persistent, toast.id, onRemove]);
  
  const handleClose = () => {
    toast.onClose?.();
    onRemove(toast.id);
  };
  
  const variants = getToastVariants(position);
  
  return (
    <motion.div
      layout
      variants={variants}
      initial="initial"
      animate="animate"
      exit="exit"
      className={`
        relative max-w-sm w-full shadow-lg rounded-lg border overflow-hidden
        ${styles.bg} ${styles.border}
      `}
      role="alert"
      aria-live={toast.type === 'error' ? 'assertive' : 'polite'}
    >
      {/* Progress Bar */}
      {!toast.persistent && toast.duration && toast.duration > 0 && (
        <div className="absolute top-0 left-0 right-0 h-1 bg-black/10">
          <motion.div
            className="h-full bg-current opacity-40"
            initial={{ width: '100%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.1, ease: 'linear' }}
          />
        </div>
      )}
      
      <div className="p-4">
        <div className="flex items-start space-x-3">
          {/* Icon */}
          <div className={`flex-shrink-0 ${styles.icon}`}>
            <IconComponent />
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            {toast.title && (
              <h4 className={`text-sm font-semibold ${styles.title} mb-1`}>
                {toast.title}
              </h4>
            )}
            <p className={`text-sm ${styles.message}`}>
              {toast.message}
            </p>
            
            {/* Actions */}
            {toast.actions && toast.actions.length > 0 && (
              <div className="flex items-center space-x-2 mt-3">
                {toast.actions.map((action, index) => (
                  <Button
                    key={index}
                    variant={action.variant || 'ghost'}
                    size="sm"
                    onClick={() => {
                      action.action();
                      if (action.variant !== 'ghost') {
                        handleClose();
                      }
                    }}
                    className="text-xs h-7"
                  >
                    {action.label}
                  </Button>
                ))}
              </div>
            )}
          </div>
          
          {/* Close Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClose}
            className="flex-shrink-0 w-6 h-6 p-0 opacity-70 hover:opacity-100"
            title="Schließen"
          >
            <X size={14} />
          </Button>
        </div>
      </div>
    </motion.div>
  );
}

// Toast Container Component
interface ToastContainerProps {
  position?: ToastPosition;
  maxToasts?: number;
}

function ToastContainer({ position = 'top-right', maxToasts = 5 }: ToastContainerProps) {
  const context = useContext(ToastContext);
  if (!context) return null;
  
  const { toasts, removeToast } = context;
  const visibleToasts = toasts.slice(-maxToasts);
  
  if (typeof document === 'undefined') return null;
  
  return createPortal(
    <div className={`fixed z-50 pointer-events-none ${positionClasses[position]}`}>
      <div className="flex flex-col space-y-2 pointer-events-auto">
        <AnimatePresence mode="popLayout">
          {visibleToasts.map((toast) => (
            <ToastItem
              key={toast.id}
              toast={toast}
              onRemove={removeToast}
              position={position}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>,
    document.body
  );
}

// Toast Provider Component
interface ToastProviderProps {
  children: React.ReactNode;
  position?: ToastPosition;
  maxToasts?: number;
}

export function ToastProvider({ 
  children, 
  position = 'top-right', 
  maxToasts = 5 
}: ToastProviderProps) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);
  
  const addToast = useCallback((toastData: Omit<Toast, 'id'>) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const toast: Toast = {
      id,
      duration: 5000, // Default 5 seconds
      persistent: false,
      ...toastData,
    };
    
    setToasts(prev => [...prev, toast]);
    return id;
  }, []);
  
  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);
  
  const clearAllToasts = useCallback(() => {
    setToasts([]);
  }, []);
  
  const updateToast = useCallback((id: string, updates: Partial<Toast>) => {
    setToasts(prev => prev.map(toast => 
      toast.id === id ? { ...toast, ...updates } : toast
    ));
  }, []);
  
  const contextValue: ToastContextType = {
    toasts,
    addToast,
    removeToast,
    clearAllToasts,
    updateToast,
  };
  
  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer position={position} maxToasts={maxToasts} />
    </ToastContext.Provider>
  );
}

// Toast Hook
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  
  const { addToast, removeToast, clearAllToasts, updateToast } = context;
  
  // Convenience methods
  const success = useCallback((message: string, options?: Partial<Toast>) => {
    return addToast({ type: 'success', message, ...options });
  }, [addToast]);
  
  const error = useCallback((message: string, options?: Partial<Toast>) => {
    return addToast({ 
      type: 'error', 
      message, 
      persistent: true, // Errors are persistent by default
      ...options 
    });
  }, [addToast]);
  
  const warning = useCallback((message: string, options?: Partial<Toast>) => {
    return addToast({ type: 'warning', message, duration: 7000, ...options });
  }, [addToast]);
  
  const info = useCallback((message: string, options?: Partial<Toast>) => {
    return addToast({ type: 'info', message, ...options });
  }, [addToast]);
  
  const loading = useCallback((message: string, options?: Partial<Toast>) => {
    return addToast({ 
      type: 'loading', 
      message, 
      persistent: true, 
      ...options 
    });
  }, [addToast]);
  
  // Promise-based toast for async operations
  const promise = useCallback(<T,>(
    promise: Promise<T>,
    {
      loading: loadingMessage = 'Loading...',
      success: successMessage = 'Success!',
      error: errorMessage = 'Something went wrong',
    }: {
      loading?: string;
      success?: string | ((data: T) => string);
      error?: string | ((error: any) => string);
    }
  ) => {
    const toastId = loading(loadingMessage);
    
    return promise
      .then((data) => {
        const message = typeof successMessage === 'function' 
          ? successMessage(data) 
          : successMessage;
        
        removeToast(toastId);
        success(message);
        return data;
      })
      .catch((err) => {
        const message = typeof errorMessage === 'function' 
          ? errorMessage(err) 
          : errorMessage;
        
        removeToast(toastId);
        error(message);
        throw err;
      });
  }, [loading, success, error, removeToast]);
  
  // Utility methods
  const dismiss = useCallback((id: string) => {
    removeToast(id);
  }, [removeToast]);
  
  const dismissAll = useCallback(() => {
    clearAllToasts();
  }, [clearAllToasts]);
  
  const update = useCallback((id: string, updates: Partial<Toast>) => {
    updateToast(id, updates);
  }, [updateToast]);
  
  return {
    // Basic methods
    success,
    error,
    warning,
    info,
    loading,
    
    // Advanced methods
    promise,
    dismiss,
    dismissAll,
    update,
    
    // Raw method for custom toasts
    custom: addToast,
  };
}

// Preset toast configurations
export const toastPresets = {
  copySuccess: (text?: string) => ({
    type: 'success' as const,
    title: 'Kopiert!',
    message: text ? `"${text}" wurde in die Zwischenablage kopiert` : 'In die Zwischenablage kopiert',
    duration: 2000,
  }),
  
  saveSuccess: (item = 'Änderungen') => ({
    type: 'success' as const,
    title: 'Gespeichert',
    message: `${item} wurden erfolgreich gespeichert`,
    duration: 3000,
  }),
  
  deleteSuccess: (item = 'Element') => ({
    type: 'success' as const,
    title: 'Gelöscht',
    message: `${item} wurde erfolgreich gelöscht`,
    duration: 3000,
  }),
  
  networkError: () => ({
    type: 'error' as const,
    title: 'Verbindungsfehler',
    message: 'Überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut',
    persistent: true,
    actions: [
      {
        label: 'Erneut versuchen',
        action: () => window.location.reload(),
        variant: 'secondary' as const,
      },
    ],
  }),
  
  undoAction: (actionName: string, undoFn: () => void) => ({
    type: 'info' as const,
    message: `${actionName} rückgängig gemacht`,
    duration: 8000,
    actions: [
      {
        label: 'Rückgängig',
        action: undoFn,
        variant: 'primary' as const,
      },
    ],
  }),
};