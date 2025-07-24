/**
 * Advanced Modal System
 * Accessible, animated modal with portal rendering and focus management
 */

import React, { useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Maximize2, Minimize2 } from 'lucide-react';
import { Button } from './Button';

type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: ModalSize;
  showCloseButton?: boolean;
  closeOnBackdrop?: boolean;
  closeOnEscape?: boolean;
  showHeader?: boolean;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
  overlayClassName?: string;
  preventScroll?: boolean;
  focusTrap?: boolean;
  initialFocus?: React.RefObject<HTMLElement>;
  onAfterOpen?: () => void;
  onAfterClose?: () => void;
}

const sizeClasses: Record<ModalSize, string> = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  full: 'max-w-[95vw] h-[95vh]',
};

const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

const modalVariants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: -20,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: 'spring',
      damping: 25,
      stiffness: 300,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: -20,
    transition: {
      duration: 0.2,
    },
  },
};

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
  closeOnBackdrop = true,
  closeOnEscape = true,
  showHeader = true,
  header,
  footer,
  className = '',
  overlayClassName = '',
  preventScroll = true,
  focusTrap = true,
  initialFocus,
  onAfterOpen,
  onAfterClose,
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);
  const [isFullscreen, setIsFullscreen] = React.useState(false);

  // Handle escape key
  const handleEscape = useCallback(
    (event: KeyboardEvent) => {
      if (closeOnEscape && event.key === 'Escape') {
        onClose();
      }
    },
    [closeOnEscape, onClose]
  );

  // Handle backdrop click
  const handleBackdropClick = useCallback(
    (event: React.MouseEvent) => {
      if (closeOnBackdrop && event.target === event.currentTarget) {
        onClose();
      }
    },
    [closeOnBackdrop, onClose]
  );

  // Focus management
  const handleFocusTrap = useCallback((event: KeyboardEvent) => {
    if (!focusTrap || !modalRef.current) return;

    const focusableElements = modalRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    if (event.key === 'Tab') {
      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    }
  }, [focusTrap]);

  // Effects
  useEffect(() => {
    if (isOpen) {
      // Store previously focused element
      previousActiveElement.current = document.activeElement as HTMLElement;
      
      // Add event listeners
      document.addEventListener('keydown', handleEscape);
      document.addEventListener('keydown', handleFocusTrap);
      
      // Prevent body scroll
      if (preventScroll) {
        document.body.style.overflow = 'hidden';
      }
      
      // Focus management
      setTimeout(() => {
        if (initialFocus?.current) {
          initialFocus.current.focus();
        } else if (modalRef.current) {
          const firstFocusable = modalRef.current.querySelector(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          ) as HTMLElement;
          firstFocusable?.focus();
        }
      }, 100);
      
      onAfterOpen?.();
    } else {
      // Cleanup
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('keydown', handleFocusTrap);
      
      if (preventScroll) {
        document.body.style.overflow = '';
      }
      
      // Restore focus
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
      
      onAfterClose?.();
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('keydown', handleFocusTrap);
      if (preventScroll) {
        document.body.style.overflow = '';
      }
    };
  }, [
    isOpen,
    handleEscape,
    handleFocusTrap,
    preventScroll,
    initialFocus,
    onAfterOpen,
    onAfterClose,
  ]);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const modalContent = (
    <AnimatePresence mode="wait">
      {isOpen && (
        <motion.div
          className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${overlayClassName}`}
          variants={backdropVariants}
          initial="hidden"
          animate="visible"
          exit="hidden"
          onClick={handleBackdropClick}
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
          
          {/* Modal */}
          <motion.div
            ref={modalRef}
            className={`
              relative w-full bg-white dark:bg-neutral-900 rounded-lg shadow-xl border border-neutral-200 dark:border-neutral-700
              ${isFullscreen ? 'max-w-[95vw] h-[95vh]' : sizeClasses[size]}
              ${size === 'full' || isFullscreen ? 'flex flex-col' : ''}
              ${className}
            `}
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'modal-title' : undefined}
          >
            {/* Header */}
            {(showHeader || header) && (
              <div className="flex items-center justify-between p-6 border-b border-neutral-200 dark:border-neutral-700">
                <div className="flex-1">
                  {header ? (
                    header
                  ) : title ? (
                    <h2
                      id="modal-title"
                      className="text-xl font-semibold text-neutral-900 dark:text-neutral-100"
                    >
                      {title}
                    </h2>
                  ) : null}
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  {size !== 'full' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={toggleFullscreen}
                      title={isFullscreen ? 'Vollbild verlassen' : 'Vollbild'}
                      className="w-8 h-8 p-0"
                    >
                      {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                    </Button>
                  )}
                  
                  {showCloseButton && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={onClose}
                      title="Schließen (Esc)"
                      className="w-8 h-8 p-0"
                    >
                      <X size={16} />
                    </Button>
                  )}
                </div>
              </div>
            )}
            
            {/* Content */}
            <div className={`${size === 'full' || isFullscreen ? 'flex-1 overflow-auto' : ''} p-6`}>
              {children}
            </div>
            
            {/* Footer */}
            {footer && (
              <div className="flex items-center justify-end space-x-3 p-6 border-t border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800 rounded-b-lg">
                {footer}
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );

  // Render in portal
  if (typeof document !== 'undefined') {
    return createPortal(modalContent, document.body);
  }

  return null;
}

// Confirmation Modal Component
interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  loading?: boolean;
}

export function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Bestätigen',
  cancelText = 'Abbrechen',
  variant = 'info',
  loading = false,
}: ConfirmModalProps) {
  const handleConfirm = () => {
    onConfirm();
    if (!loading) {
      onClose();
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'danger':
        return {
          icon: '⚠️',
          confirmVariant: 'danger' as const,
          iconColor: 'text-red-600 dark:text-red-400',
          bgColor: 'bg-red-100 dark:bg-red-900/30',
        };
      case 'warning':
        return {
          icon: '⚠️',
          confirmVariant: 'secondary' as const,
          iconColor: 'text-yellow-600 dark:text-yellow-400',
          bgColor: 'bg-yellow-100 dark:bg-yellow-900/30',
        };
      default:
        return {
          icon: 'ℹ️',
          confirmVariant: 'primary' as const,
          iconColor: 'text-blue-600 dark:text-blue-400',
          bgColor: 'bg-blue-100 dark:bg-blue-900/30',
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      closeOnBackdrop={!loading}
      closeOnEscape={!loading}
      footer={
        <>
          <Button
            variant="ghost"
            onClick={onClose}
            disabled={loading}
          >
            {cancelText}
          </Button>
          <Button
            variant={styles.confirmVariant}
            onClick={handleConfirm}
            loading={loading}
          >
            {confirmText}
          </Button>
        </>
      }
    >
      <div className="flex items-start space-x-4">
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${styles.bgColor}`}>
          <span className={`text-lg ${styles.iconColor}`}>
            {styles.icon}
          </span>
        </div>
        <div className="flex-1">
          <p className="text-neutral-700 dark:text-neutral-300">
            {message}
          </p>
        </div>
      </div>
    </Modal>
  );
}

// Modal Hook for programmatic usage
export function useModal() {
  const [isOpen, setIsOpen] = React.useState(false);

  const openModal = useCallback(() => setIsOpen(true), []);
  const closeModal = useCallback(() => setIsOpen(false), []);
  const toggleModal = useCallback(() => setIsOpen(prev => !prev), []);

  return {
    isOpen,
    openModal,
    closeModal,
    toggleModal,
  };
}

// Modal Stack Provider for nested modals
interface ModalStackContextType {
  modals: string[];
  addModal: (id: string) => void;
  removeModal: (id: string) => void;
  isTopModal: (id: string) => boolean;
}

const ModalStackContext = React.createContext<ModalStackContextType | null>(null);

export function ModalStackProvider({ children }: { children: React.ReactNode }) {
  const [modals, setModals] = React.useState<string[]>([]);

  const addModal = useCallback((id: string) => {
    setModals(prev => [...prev, id]);
  }, []);

  const removeModal = useCallback((id: string) => {
    setModals(prev => prev.filter(modalId => modalId !== id));
  }, []);

  const isTopModal = useCallback((id: string) => {
    return modals[modals.length - 1] === id;
  }, [modals]);

  return (
    <ModalStackContext.Provider value={{ modals, addModal, removeModal, isTopModal }}>
      {children}
    </ModalStackContext.Provider>
  );
}

export function useModalStack() {
  const context = React.useContext(ModalStackContext);
  if (!context) {
    throw new Error('useModalStack must be used within ModalStackProvider');
  }
  return context;
}