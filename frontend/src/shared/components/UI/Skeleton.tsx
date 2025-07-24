/**
 * Skeleton Component
 * Loading skeletons for content placeholders
 */

import React from 'react';
import { motion } from 'framer-motion';

interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'rectangular' | 'circular';
  animation?: 'pulse' | 'wave' | 'none';
  lines?: number;
}

export function Skeleton({
  className = '',
  width,
  height,
  variant = 'rectangular',
  animation = 'pulse',
  lines = 1,
}: SkeletonProps) {
  const baseClasses = 'bg-neutral-200 dark:bg-neutral-700';
  
  const variantClasses = {
    text: 'rounded h-4',
    rectangular: 'rounded-md',
    circular: 'rounded-full',
  };

  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  };

  const style = {
    width: width || (variant === 'text' ? '100%' : undefined),
    height: height || (variant === 'circular' ? width : undefined),
  };

  if (variant === 'text' && lines > 1) {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={`
              ${baseClasses}
              ${variantClasses[variant]}
              ${animationClasses[animation]}
            `}
            style={{
              width: index === lines - 1 ? '75%' : '100%',
              height: height || '1rem',
            }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${animationClasses[animation]}
        ${className}
      `}
      style={style}
    />
  );
}

// Skeleton presets for common layouts
export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`p-4 space-y-4 ${className}`}>
      <div className="flex items-center space-x-3">
        <Skeleton variant="circular" width="2.5rem" height="2.5rem" />
        <div className="space-y-2 flex-1">
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" />
        </div>
      </div>
      <Skeleton variant="rectangular" height="12rem" />
      <Skeleton variant="text" lines={3} />
    </div>
  );
}

export function SkeletonTable({ 
  rows = 5, 
  columns = 4, 
  className = '' 
}: { 
  rows?: number; 
  columns?: number; 
  className?: string; 
}) {
  return (
    <div className={`space-y-3 ${className}`}>
      {/* Header */}
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton key={`header-${index}`} variant="text" height="1.25rem" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div 
          key={`row-${rowIndex}`} 
          className="grid gap-4" 
          style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton 
              key={`cell-${rowIndex}-${colIndex}`} 
              variant="text" 
              width={colIndex === 0 ? '80%' : '60%'} 
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export function SkeletonList({ 
  items = 5, 
  showAvatar = true, 
  className = '' 
}: { 
  items?: number; 
  showAvatar?: boolean; 
  className?: string; 
}) {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="flex items-center space-x-3">
          {showAvatar && (
            <Skeleton variant="circular" width="2rem" height="2rem" />
          )}
          <div className="flex-1 space-y-2">
            <Skeleton variant="text" width="75%" />
            <Skeleton variant="text" width="50%" />
          </div>
        </div>
      ))}
    </div>
  );
}

// Add shimmer animation styles
const shimmerKeyframes = `
  @keyframes shimmer {
    0% {
      background-position: -468px 0;
    }
    100% {
      background-position: 468px 0;
    }
  }
`;

export function SkeletonProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      <style>{shimmerKeyframes}</style>
      <style jsx global>{`
        .animate-shimmer {
          background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.4),
            transparent
          );
          background-size: 468px 104px;
          animation: shimmer 1.6s ease-in-out infinite;
        }
        
        .dark .animate-shimmer {
          background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
          );
          background-size: 468px 104px;
        }
      `}</style>
      {children}
    </>
  );
}