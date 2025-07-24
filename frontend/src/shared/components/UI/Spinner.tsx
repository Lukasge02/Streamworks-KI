/**
 * Spinner Component
 * Loading indicators with different sizes and variants
 */

import React from 'react';
import { motion } from 'framer-motion';

interface SpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'white';
  className?: string;
  label?: string;
}

export function Spinner({
  size = 'md',
  variant = 'primary',
  className = '',
  label,
}: SpinnerProps) {
  const sizeClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  };

  const variantClasses = {
    primary: 'text-primary-600',
    secondary: 'text-neutral-600',
    white: 'text-white',
  };

  return (
    <div className={`inline-flex items-center ${className}`}>
      <motion.svg
        className={`animate-spin ${sizeClasses[size]} ${variantClasses[variant]}`}
        fill="none"
        viewBox="0 0 24 24"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        aria-hidden={!label}
        role={label ? 'status' : undefined}
        aria-label={label}
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </motion.svg>
      
      {label && (
        <span className="ml-2 text-sm text-neutral-600 dark:text-neutral-400">
          {label}
        </span>
      )}
    </div>
  );
}

// Pulse Spinner variant
export function PulseSpinner({
  size = 'md',
  variant = 'primary',
  className = '',
}: Omit<SpinnerProps, 'label'>) {
  const sizeClasses = {
    xs: 'h-2 w-2',
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-6 w-6',
    xl: 'h-8 w-8',
  };

  const variantClasses = {
    primary: 'bg-primary-600',
    secondary: 'bg-neutral-600',
    white: 'bg-white',
  };

  return (
    <div className={`inline-flex space-x-1 ${className}`}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className={`
            rounded-full
            ${sizeClasses[size]}
            ${variantClasses[variant]}
          `}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.7, 1, 0.7],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: index * 0.2,
          }}
        />
      ))}
    </div>
  );
}

// Dots Spinner variant
export function DotsSpinner({
  size = 'md',
  variant = 'primary',
  className = '',
}: Omit<SpinnerProps, 'label'>) {
  const sizeClasses = {
    xs: 'h-1 w-1',
    sm: 'h-1.5 w-1.5',
    md: 'h-2 w-2',
    lg: 'h-3 w-3',
    xl: 'h-4 w-4',
  };

  const variantClasses = {
    primary: 'bg-primary-600',
    secondary: 'bg-neutral-600',
    white: 'bg-white',
  };

  return (
    <div className={`flex space-x-1 ${className}`}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className={`
            rounded-full
            ${sizeClasses[size]}
            ${variantClasses[variant]}
          `}
          animate={{
            y: [0, -8, 0],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: index * 0.1,
          }}
        />
      ))}
    </div>
  );
}