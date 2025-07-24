/**
 * Tooltip Component
 * Accessible tooltips with positioning and animations
 */

import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';

interface TooltipProps {
  children: React.ReactNode;
  content: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  variant?: 'dark' | 'light';
  delay?: number;
  offset?: number;
  disabled?: boolean;
  className?: string;
  maxWidth?: string;
}

export function Tooltip({
  children,
  content,
  position = 'top',
  variant = 'dark',
  delay = 500,
  offset = 8,
  disabled = false,
  className = '',
  maxWidth = '200px',
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const showTooltip = () => {
    if (disabled || !content) return;
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  const updatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight,
    };

    let x = 0;
    let y = 0;

    switch (position) {
      case 'top':
        x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        y = triggerRect.top - tooltipRect.height - offset;
        break;
      case 'bottom':
        x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2;
        y = triggerRect.bottom + offset;
        break;
      case 'left':
        x = triggerRect.left - tooltipRect.width - offset;
        y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
        break;
      case 'right':
        x = triggerRect.right + offset;
        y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;
        break;
    }

    // Adjust for viewport boundaries
    if (x < 0) x = 8;
    if (x + tooltipRect.width > viewport.width) {
      x = viewport.width - tooltipRect.width - 8;
    }
    if (y < 0) y = 8;
    if (y + tooltipRect.height > viewport.height) {
      y = viewport.height - tooltipRect.height - 8;
    }

    setTooltipPosition({ x, y });
  };

  useEffect(() => {
    if (isVisible) {
      updatePosition();
      
      const handleResize = () => updatePosition();
      const handleScroll = () => updatePosition();
      
      window.addEventListener('resize', handleResize);
      window.addEventListener('scroll', handleScroll, true);
      
      return () => {
        window.removeEventListener('resize', handleResize);
        window.removeEventListener('scroll', handleScroll, true);
      };
    }
  }, [isVisible, position, offset]);

  const variantClasses = {
    dark: 'bg-neutral-900 text-white border-neutral-700',
    light: 'bg-white text-neutral-900 border-neutral-200 shadow-lg',
  };

  const arrowClasses = {
    dark: 'border-neutral-900',
    light: 'border-white',
  };

  const getArrowStyle = () => {
    const arrowSize = 6;
    const arrowStyle: React.CSSProperties = {
      position: 'absolute',
      width: 0,
      height: 0,
    };

    switch (position) {
      case 'top':
        arrowStyle.top = '100%';
        arrowStyle.left = '50%';
        arrowStyle.transform = 'translateX(-50%)';
        arrowStyle.borderLeft = `${arrowSize}px solid transparent`;
        arrowStyle.borderRight = `${arrowSize}px solid transparent`;
        arrowStyle.borderTop = `${arrowSize}px solid`;
        break;
      case 'bottom':
        arrowStyle.bottom = '100%';
        arrowStyle.left = '50%';
        arrowStyle.transform = 'translateX(-50%)';
        arrowStyle.borderLeft = `${arrowSize}px solid transparent`;
        arrowStyle.borderRight = `${arrowSize}px solid transparent`;
        arrowStyle.borderBottom = `${arrowSize}px solid`;
        break;
      case 'left':
        arrowStyle.left = '100%';
        arrowStyle.top = '50%';
        arrowStyle.transform = 'translateY(-50%)';
        arrowStyle.borderTop = `${arrowSize}px solid transparent`;
        arrowStyle.borderBottom = `${arrowSize}px solid transparent`;
        arrowStyle.borderLeft = `${arrowSize}px solid`;
        break;
      case 'right':
        arrowStyle.right = '100%';
        arrowStyle.top = '50%';
        arrowStyle.transform = 'translateY(-50%)';
        arrowStyle.borderTop = `${arrowSize}px solid transparent`;
        arrowStyle.borderBottom = `${arrowSize}px solid transparent`;
        arrowStyle.borderRight = `${arrowSize}px solid`;
        break;
    }

    return arrowStyle;
  };

  const animationVariants = {
    initial: {
      opacity: 0,
      scale: 0.8,
      y: position === 'top' ? 10 : position === 'bottom' ? -10 : 0,
      x: position === 'left' ? 10 : position === 'right' ? -10 : 0,
    },
    animate: {
      opacity: 1,
      scale: 1,
      y: 0,
      x: 0,
    },
    exit: {
      opacity: 0,
      scale: 0.8,
      y: position === 'top' ? 10 : position === 'bottom' ? -10 : 0,
      x: position === 'left' ? 10 : position === 'right' ? -10 : 0,
    },
  };

  return (
    <>
      <div
        ref={triggerRef}
        className={`inline-block ${className}`}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
      >
        {children}
      </div>

      {createPortal(
        <AnimatePresence>
          {isVisible && (
            <motion.div
              ref={tooltipRef}
              initial="initial"
              animate="animate"
              exit="exit"
              variants={animationVariants}
              transition={{ duration: 0.15, ease: 'easeOut' }}
              className={`
                fixed z-50 px-3 py-2 text-sm font-medium rounded-lg border pointer-events-none
                ${variantClasses[variant]}
              `}
              style={{
                left: tooltipPosition.x,
                top: tooltipPosition.y,
                maxWidth,
              }}
              role="tooltip"
            >
              {content}
              
              {/* Arrow */}
              <div
                className={arrowClasses[variant]}
                style={getArrowStyle()}
              />
            </motion.div>
          )}
        </AnimatePresence>,
        document.body
      )}
    </>
  );
}

// Helper hook for programmatic tooltips
export function useTooltip() {
  const [isVisible, setIsVisible] = useState(false);
  const [content, setContent] = useState<React.ReactNode>('');
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const show = (content: React.ReactNode, x: number, y: number) => {
    setContent(content);
    setPosition({ x, y });
    setIsVisible(true);
  };

  const hide = () => {
    setIsVisible(false);
  };

  return {
    isVisible,
    content,
    position,
    show,
    hide,
  };
}