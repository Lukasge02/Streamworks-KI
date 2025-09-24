'use client'

import React from 'react'
import { motion } from 'framer-motion'
import {
  Settings,
  Code2,
  ChevronLeft,
  ChevronRight,
  Maximize2,
  Minimize2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

/**
 * 📱 Mobile Optimized Tabs Component
 *
 * Features:
 * - Touch-friendly tab switching
 * - Gesture support for swipe navigation
 * - Fullscreen mode for better mobile experience
 * - Enhanced visual feedback
 * - Responsive animations
 */

interface MobileOptimizedTabsProps {
  activeTab: 'parameters' | 'xml'
  onTabChange: (tab: 'parameters' | 'xml') => void
  parameterCount: number
  completionPercentage: number
  isFullscreen?: boolean
  onToggleFullscreen?: () => void
}

export function MobileOptimizedTabs({
  activeTab,
  onTabChange,
  parameterCount,
  completionPercentage,
  isFullscreen = false,
  onToggleFullscreen
}: MobileOptimizedTabsProps) {
  return (
    <div className="lg:hidden">
      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        {/* Main Tab Buttons */}
        <div className="flex p-2 gap-1 relative">
          {/* Tab Background Indicator */}
          <motion.div
            layout
            className="absolute inset-y-2 bg-blue-100 rounded-lg border border-blue-200"
            initial={false}
            animate={{
              x: activeTab === 'parameters' ? 4 : '50%',
              width: 'calc(50% - 6px)'
            }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          />

          {/* Parameters Tab */}
          <Button
            onClick={() => onTabChange('parameters')}
            variant="ghost"
            className={cn(
              "flex-1 relative z-10 h-12 justify-center gap-2 transition-colors",
              "touch-manipulation select-none",
              activeTab === 'parameters'
                ? 'text-blue-700 bg-transparent'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            <Settings className="w-4 h-4" />
            <div className="flex flex-col items-center">
              <span className="text-sm font-medium">Parameter</span>
              <div className="flex items-center gap-1">
                <Badge
                  variant={activeTab === 'parameters' ? 'default' : 'secondary'}
                  className="text-xs h-4 px-1.5"
                >
                  {parameterCount}
                </Badge>
                {completionPercentage > 0 && (
                  <span className="text-xs text-green-600 font-medium">
                    {Math.round(completionPercentage)}%
                  </span>
                )}
              </div>
            </div>
          </Button>

          {/* XML Tab */}
          <Button
            onClick={() => onTabChange('xml')}
            variant="ghost"
            className={cn(
              "flex-1 relative z-10 h-12 justify-center gap-2 transition-colors",
              "touch-manipulation select-none",
              activeTab === 'xml'
                ? 'text-blue-700 bg-transparent'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            <Code2 className="w-4 h-4" />
            <div className="flex flex-col items-center">
              <span className="text-sm font-medium">XML Editor</span>
              <Badge
                variant={activeTab === 'xml' ? 'default' : 'secondary'}
                className="text-xs h-4 px-1.5"
              >
                Monaco
              </Badge>
            </div>
          </Button>
        </div>

        {/* Secondary Controls */}
        <div className="flex items-center justify-between px-4 py-2 bg-gray-50 border-t border-gray-100">
          {/* Quick Navigation */}
          <div className="flex items-center gap-1">
            <Button
              onClick={() => onTabChange(activeTab === 'parameters' ? 'xml' : 'parameters')}
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 touch-manipulation"
            >
              {activeTab === 'parameters' ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronLeft className="w-4 h-4" />
              )}
            </Button>
            <span className="text-xs text-gray-500 ml-2">
              Wischen zum Wechseln
            </span>
          </div>

          {/* Fullscreen Toggle */}
          {onToggleFullscreen && (
            <Button
              onClick={onToggleFullscreen}
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 touch-manipulation"
              title={isFullscreen ? 'Vollbild beenden' : 'Vollbild'}
            >
              {isFullscreen ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Progress Indicator */}
      {activeTab === 'parameters' && completionPercentage > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-green-50 px-4 py-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-blue-700 font-medium">
              Parameter Status
            </span>
            <span className="text-green-700 font-bold">
              Aktiv
            </span>
          </div>
          <div className="mt-1 bg-white rounded-full h-1.5 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 to-green-500"
              initial={{ width: 0 }}
              animate={{ width: `${completionPercentage}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            />
          </div>
        </div>
      )}
    </div>
  )
}