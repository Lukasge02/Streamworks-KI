/**
 * InfoTooltip Component
 * Professional tooltip with info icon and hover information
 */
'use client'

import React, { useState } from 'react'
import { Info } from 'lucide-react'

interface InfoTooltipProps {
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
  iconSize?: 'sm' | 'md' | 'lg'
}

export const InfoTooltip: React.FC<InfoTooltipProps> = ({
  content,
  position = 'top',
  className = '',
  iconSize = 'sm'
}) => {
  const [isVisible, setIsVisible] = useState(false)

  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5', 
    lg: 'w-6 h-6'
  }

  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  }

  const arrowClasses = {
    top: 'top-full left-1/2 transform -translate-x-1/2 border-t-gray-800 dark:border-t-gray-200',
    bottom: 'bottom-full left-1/2 transform -translate-x-1/2 border-b-gray-800 dark:border-b-gray-200',
    left: 'left-full top-1/2 transform -translate-y-1/2 border-l-gray-800 dark:border-l-gray-200',
    right: 'right-full top-1/2 transform -translate-y-1/2 border-r-gray-800 dark:border-r-gray-200'
  }

  return (
    <div className={`relative inline-flex ${className}`}>
      {/* Info Icon */}
      <button
        type="button"
        className="inline-flex items-center justify-center text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors duration-200"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
        aria-label="Weitere Informationen"
      >
        <Info className={iconSizeClasses[iconSize]} />
      </button>

      {/* Tooltip */}
      {isVisible && (
        <>
          <div
            className={`absolute z-50 px-3 py-2 text-sm text-white bg-gray-800 dark:bg-gray-200 dark:text-gray-800 rounded-lg shadow-lg max-w-xs transition-all duration-200 ease-out opacity-100 scale-100 ${positionClasses[position]}`}
            role="tooltip"
          >
            {content}
            
            {/* Arrow */}
            <div
              className={`absolute w-0 h-0 border-4 border-transparent ${arrowClasses[position]}`}
            />
          </div>
        </>
      )}
    </div>
  )
}

export default InfoTooltip