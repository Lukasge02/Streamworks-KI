/**
 * Avatar Component
 * User avatars with online status and fallbacks
 */

import React, { useState } from 'react';
import { User } from 'lucide-react';
import { motion } from 'framer-motion';

interface AvatarProps {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  status?: 'online' | 'offline' | 'away' | 'busy';
  showStatus?: boolean;
  fallback?: string;
  className?: string;
  onClick?: () => void;
}

export function Avatar({
  src,
  alt,
  name,
  size = 'md',
  status,
  showStatus = false,
  fallback,
  className = '',
  onClick,
}: AvatarProps) {
  const [imageError, setImageError] = useState(false);

  const sizeClasses = {
    xs: 'h-6 w-6 text-xs',
    sm: 'h-8 w-8 text-sm',
    md: 'h-10 w-10 text-base',
    lg: 'h-12 w-12 text-lg',
    xl: 'h-16 w-16 text-xl',
    '2xl': 'h-20 w-20 text-2xl',
  };

  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-neutral-400',
    away: 'bg-yellow-500',
    busy: 'bg-red-500',
  };

  const statusSizes = {
    xs: 'h-1.5 w-1.5',
    sm: 'h-2 w-2',
    md: 'h-2.5 w-2.5',
    lg: 'h-3 w-3',
    xl: 'h-3.5 w-3.5',
    '2xl': 'h-4 w-4',
  };

  // Generate initials from name
  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const displayFallback = fallback || (name ? getInitials(name) : '');

  return (
    <div className={`relative inline-block ${className}`}>
      <motion.div
        className={`
          relative inline-flex items-center justify-center rounded-full overflow-hidden
          bg-neutral-100 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-300
          ${sizeClasses[size]}
          ${onClick ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
        `}
        onClick={onClick}
        whileHover={onClick ? { scale: 1.05 } : undefined}
        whileTap={onClick ? { scale: 0.95 } : undefined}
      >
        {src && !imageError ? (
          <img
            src={src}
            alt={alt || name}
            className="h-full w-full object-cover"
            onError={() => setImageError(true)}
          />
        ) : displayFallback ? (
          <span className="font-medium select-none">
            {displayFallback}
          </span>
        ) : (
          <User className="h-1/2 w-1/2" />
        )}
      </motion.div>

      {/* Status indicator */}
      {showStatus && status && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className={`
            absolute bottom-0 right-0 rounded-full border-2 border-white dark:border-neutral-800
            ${statusSizes[size]}
            ${statusColors[status]}
          `}
        />
      )}
    </div>
  );
}

// Avatar Group Component
interface AvatarGroupProps {
  avatars: Array<{
    src?: string;
    name?: string;
    alt?: string;
  }>;
  max?: number;
  size?: AvatarProps['size'];
  className?: string;
}

export function AvatarGroup({
  avatars,
  max = 4,
  size = 'md',
  className = '',
}: AvatarGroupProps) {
  const visibleAvatars = avatars.slice(0, max);
  const remainingCount = Math.max(0, avatars.length - max);

  const spacing = {
    xs: '-ml-1',
    sm: '-ml-1.5',
    md: '-ml-2',
    lg: '-ml-2.5',
    xl: '-ml-3',
    '2xl': '-ml-4',
  };

  return (
    <div className={`flex items-center ${className}`}>
      {visibleAvatars.map((avatar, index) => (
        <div
          key={index}
          className={`
            relative ring-2 ring-white dark:ring-neutral-800 rounded-full
            ${index > 0 ? spacing[size] : ''}
          `}
          style={{ zIndex: visibleAvatars.length - index }}
        >
          <Avatar
            src={avatar.src}
            name={avatar.name}
            alt={avatar.alt}
            size={size}
          />
        </div>
      ))}
      
      {remainingCount > 0 && (
        <div
          className={`
            relative ring-2 ring-white dark:ring-neutral-800 rounded-full
            ${spacing[size]}
          `}
        >
          <div className={`
            inline-flex items-center justify-center rounded-full
            bg-neutral-200 dark:bg-neutral-600 text-neutral-600 dark:text-neutral-300
            font-medium text-xs
            ${sizeClasses[size]}
          `}>
            +{remainingCount}
          </div>
        </div>
      )}
    </div>
  );
}