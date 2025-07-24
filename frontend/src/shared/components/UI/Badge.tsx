/**
 * Badge Component
 * Status indicators with variants and sizes
 */

import React from 'react';
import { motion } from 'framer-motion';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  dot?: boolean;
  pulse?: boolean;
}

export function Badge({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  dot = false,
  pulse = false,
}: BadgeProps) {
  const baseClasses = 'inline-flex items-center font-medium rounded-full transition-all duration-200';
  
  const variantClasses = {
    primary: 'bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300',
    secondary: 'bg-neutral-100 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-300',
    success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    error: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  };

  const sizeClasses = {
    sm: dot ? 'h-2 w-2' : 'px-2 py-0.5 text-xs',
    md: dot ? 'h-2.5 w-2.5' : 'px-2.5 py-1 text-xs',
    lg: dot ? 'h-3 w-3' : 'px-3 py-1.5 text-sm',
  };

  const dotClasses = dot ? 'rounded-full' : '';
  const pulseClasses = pulse ? 'animate-pulse' : '';

  return (
    <motion.span
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.2 }}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${dotClasses}
        ${pulseClasses}
        ${className}
      `}
    >
      {!dot && children}
    </motion.span>
  );
}