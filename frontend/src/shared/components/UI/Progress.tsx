/**
 * Progress Component
 * Linear and circular progress bars with variants
 */

import React from 'react';
import { motion } from 'framer-motion';

interface ProgressProps {
  value: number;
  max?: number;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  type?: 'linear' | 'circular';
  showValue?: boolean;
  className?: string;
  animated?: boolean;
  indeterminate?: boolean;
}

export function Progress({
  value,
  max = 100,
  variant = 'primary',
  size = 'md',
  type = 'linear',
  showValue = false,
  className = '',
  animated = true,
  indeterminate = false,
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const variantClasses = {
    primary: 'bg-primary-500',
    secondary: 'bg-neutral-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
  };

  const backgroundClasses = {
    primary: 'bg-primary-100 dark:bg-primary-900/30',
    secondary: 'bg-neutral-200 dark:bg-neutral-700',
    success: 'bg-green-100 dark:bg-green-900/30',
    warning: 'bg-yellow-100 dark:bg-yellow-900/30',
    error: 'bg-red-100 dark:bg-red-900/30',
  };

  if (type === 'circular') {
    const sizeMap = {
      sm: { size: 32, strokeWidth: 2 },
      md: { size: 48, strokeWidth: 3 },
      lg: { size: 64, strokeWidth: 4 },
    };

    const { size: circleSize, strokeWidth } = sizeMap[size];
    const radius = (circleSize - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const strokeDasharray = circumference;
    const strokeDashoffset = indeterminate ? 0 : circumference - (percentage / 100) * circumference;

    return (
      <div className={`relative inline-flex items-center justify-center ${className}`}>
        <svg
          width={circleSize}
          height={circleSize}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={circleSize / 2}
            cy={circleSize / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            className={`${backgroundClasses[variant]} opacity-20`}
          />
          
          {/* Progress circle */}
          <motion.circle
            cx={circleSize / 2}
            cy={circleSize / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className={variantClasses[variant]}
            initial={animated ? { strokeDashoffset: circumference } : false}
            animate={animated ? { strokeDashoffset } : false}
            transition={{ duration: 0.5, ease: 'easeInOut' }}
            style={indeterminate ? {
              animation: 'spin 1s linear infinite',
              transformOrigin: 'center',
            } : undefined}
          />
        </svg>
        
        {showValue && !indeterminate && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
              {Math.round(percentage)}%
            </span>
          </div>
        )}
      </div>
    );
  }

  // Linear progress
  const heightClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  return (
    <div className={`w-full ${className}`}>
      {showValue && !indeterminate && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
            Progress
          </span>
          <span className="text-sm text-neutral-500 dark:text-neutral-400">
            {Math.round(percentage)}%
          </span>
        </div>
      )}
      
      <div className={`
        w-full rounded-full overflow-hidden
        ${heightClasses[size]}
        ${backgroundClasses[variant]}
      `}>
        {indeterminate ? (
          <div
            className={`
              h-full rounded-full
              ${variantClasses[variant]}
              animate-pulse
            `}
            style={{
              width: '30%',
              animation: 'indeterminate 1.5s ease-in-out infinite',
            }}
          />
        ) : (
          <motion.div
            className={`
              h-full rounded-full transition-all duration-300
              ${variantClasses[variant]}
            `}
            initial={animated ? { width: 0 } : false}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: animated ? 0.5 : 0, ease: 'easeInOut' }}
          />
        )}
      </div>
      
      <style jsx>{`
        @keyframes indeterminate {
          0% {
            transform: translateX(-100%);
          }
          50% {
            transform: translateX(0%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  );
}