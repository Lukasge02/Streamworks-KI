'use client'

import { useToasts } from '@/services/toast.service'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckCircle2, 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  Loader2, 
  X,
  ArrowRight 
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useEffect, useState } from 'react'

const icons = {
  success: CheckCircle2,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
  loading: Loader2,
}

const colors = {
  success: 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300',
  error: 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300',
  info: 'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300',
  loading: 'bg-gray-50 border-gray-200 text-gray-800 dark:bg-gray-800/50 dark:border-gray-700 dark:text-gray-300',
}

const iconColors = {
  success: 'text-green-600 dark:text-green-400',
  error: 'text-red-600 dark:text-red-400',
  warning: 'text-yellow-600 dark:text-yellow-400',
  info: 'text-blue-600 dark:text-blue-400',
  loading: 'text-gray-600 dark:text-gray-400',
}

export function ToastContainer() {
  const { toasts, remove } = useToasts()

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm w-full">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <ToastItem
            key={toast.id}
            toast={toast}
            onRemove={() => remove(toast.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}

interface ToastItemProps {
  toast: ReturnType<typeof useToasts>['toasts'][0]
  onRemove: () => void
}

function ToastItem({ toast, onRemove }: ToastItemProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [remainingTime, setRemainingTime] = useState<number | null>(null)

  const Icon = icons[toast.type]

  useEffect(() => {
    if (!toast.duration || toast.persistent) return

    const startTime = Date.now()
    const endTime = toast.created_at.getTime() + toast.duration

    const updateTimer = () => {
      const now = Date.now()
      const remaining = Math.max(0, endTime - now)
      setRemainingTime(remaining)

      if (remaining <= 0) {
        onRemove()
      }
    }

    updateTimer()
    const interval = setInterval(updateTimer, 100)

    return () => clearInterval(interval)
  }, [toast.duration, toast.persistent, toast.created_at, onRemove])

  const progressPercentage = toast.progress 
    ? (toast.progress.current / toast.progress.total) * 100 
    : remainingTime && toast.duration 
      ? ((toast.duration - remainingTime) / toast.duration) * 100
      : null

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.9 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={cn(
        "relative overflow-hidden rounded-lg border shadow-lg backdrop-blur-sm",
        colors[toast.type]
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Progress bar */}
      {progressPercentage !== null && (
        <motion.div
          className="absolute top-0 left-0 h-1 bg-current opacity-30"
          initial={{ width: "0%" }}
          animate={{ width: `${progressPercentage}%` }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />
      )}

      <div className="p-4">
        <div className="flex items-start space-x-3">
          {/* Icon */}
          <div className={cn("flex-shrink-0 mt-0.5", iconColors[toast.type])}>
            {toast.type === 'loading' ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Icon className="h-5 w-5" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium">
              {toast.title}
            </div>
            
            {toast.message && (
              <div className="mt-1 text-sm opacity-90">
                {toast.message}
              </div>
            )}

            {/* Progress indicator */}
            {toast.progress && (
              <div className="mt-2 text-xs opacity-75">
                {toast.progress.label && (
                  <div className="mb-1">{toast.progress.label}</div>
                )}
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-black/10 dark:bg-white/10 rounded-full h-1.5">
                    <motion.div
                      className="bg-current h-full rounded-full"
                      initial={{ width: "0%" }}
                      animate={{ width: `${(toast.progress.current / toast.progress.total) * 100}%` }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                  <span className="text-xs font-mono">
                    {toast.progress.current}/{toast.progress.total}
                  </span>
                </div>
              </div>
            )}

            {/* Actions */}
            {toast.actions && toast.actions.length > 0 && (
              <div className="mt-3 flex space-x-2">
                {toast.actions.map((action, index) => (
                  <button
                    key={index}
                    onClick={action.action}
                    className={cn(
                      "text-xs font-medium px-2 py-1 rounded transition-colors",
                      action.variant === 'primary'
                        ? "bg-current/20 hover:bg-current/30"
                        : "hover:bg-current/10"
                    )}
                  >
                    <span className="flex items-center space-x-1">
                      <span>{action.label}</span>
                      <ArrowRight className="h-3 w-3" />
                    </span>
                  </button>
                ))}
              </div>
            )}

            {/* Time remaining indicator */}
            {remainingTime !== null && remainingTime > 0 && isHovered && (
              <div className="mt-2 text-xs opacity-60">
                Schließt in {Math.ceil(remainingTime / 1000)}s
              </div>
            )}
          </div>

          {/* Dismiss button */}
          {toast.dismissible && (
            <button
              onClick={onRemove}
              className={cn(
                "flex-shrink-0 p-1 rounded-full transition-colors",
                "hover:bg-current/10 focus:outline-none focus:ring-2 focus:ring-current/30",
                iconColors[toast.type]
              )}
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default ToastContainer