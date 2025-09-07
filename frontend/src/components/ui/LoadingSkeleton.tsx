'use client'

import { motion } from 'framer-motion'

interface LoadingSkeletonProps {
  lines?: number
  height?: string
  className?: string
  animated?: boolean
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  lines = 3, 
  height = 'h-4', 
  className = '',
  animated = true 
}) => {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <motion.div
          key={index}
          initial={animated ? { opacity: 0.6 } : {}}
          animate={animated ? { opacity: [0.6, 1, 0.6] } : {}}
          transition={animated ? { 
            duration: 1.5, 
            repeat: Infinity, 
            delay: index * 0.1 
          } : {}}
          className={`bg-gray-200 dark:bg-gray-700 rounded-lg ${height} ${
            index === lines - 1 ? 'w-3/4' : 'w-full'
          }`}
        />
      ))}
    </div>
  )
}

export const DocumentCardSkeleton: React.FC = () => {
  return (
    <div className="card-enterprise p-6 space-y-4">
      <div className="flex items-start justify-between">
        <div className="space-y-2 flex-1">
          <LoadingSkeleton lines={1} height="h-6" className="w-3/4" />
          <LoadingSkeleton lines={1} height="h-4" className="w-1/2" />
        </div>
        <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded-full shimmer" />
      </div>
      <LoadingSkeleton lines={2} height="h-4" />
      <div className="flex space-x-2">
        <div className="w-16 h-6 bg-gray-200 dark:bg-gray-700 rounded-full shimmer" />
        <div className="w-20 h-6 bg-gray-200 dark:bg-gray-700 rounded-full shimmer" />
      </div>
    </div>
  )
}

export const ChatMessageSkeleton: React.FC = () => {
  return (
    <div className="flex items-start space-x-3 p-4">
      <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full shimmer flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <LoadingSkeleton lines={1} height="h-4" className="w-1/4" />
        <LoadingSkeleton lines={3} height="h-4" />
      </div>
    </div>
  )
}

export const XMLStreamSkeleton: React.FC = () => {
  return (
    <div className="card-enterprise p-6 space-y-4">
      <div className="flex items-center justify-between">
        <LoadingSkeleton lines={1} height="h-6" className="w-1/3" />
        <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded shimmer" />
      </div>
      <LoadingSkeleton lines={4} height="h-4" />
      <div className="flex items-center space-x-4">
        <div className="w-24 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg shimmer" />
        <div className="w-20 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg shimmer" />
      </div>
    </div>
  )
}