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
  success: 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200/70 text-green-800 dark:from-green-900/20 dark:to-emerald-900/20 dark:border-green-800/70 dark:text-green-300 shadow-green-100/50',
  error: 'bg-gradient-to-r from-red-50 to-rose-50 border-red-200/70 text-red-800 dark:from-red-900/20 dark:to-rose-900/20 dark:border-red-800/70 dark:text-red-300 shadow-red-100/50',
  warning: 'bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200/70 text-yellow-800 dark:from-yellow-900/20 dark:to-amber-900/20 dark:border-yellow-800/70 dark:text-yellow-300 shadow-yellow-100/50',
  info: 'bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200/70 text-primary-800 dark:from-primary-900/20 dark:to-blue-900/20 dark:border-primary-800/70 dark:text-primary-300 shadow-primary-100/50',
  loading: 'bg-gradient-to-r from-arvato-gray-light to-gray-50 border-gray-200/70 text-gray-800 dark:from-gray-800/50 dark:to-gray-700/50 dark:border-gray-600/70 dark:text-gray-300 shadow-gray-100/50',
}

const iconColors = {
  success: 'text-green-600 dark:text-green-400 drop-shadow-sm',
  error: 'text-arvato-accent-red dark:text-red-400 drop-shadow-sm',
  warning: 'text-arvato-accent-yellow dark:text-yellow-400 drop-shadow-sm',
  info: 'text-primary-600 dark:text-primary-400 drop-shadow-sm',
  loading: 'text-arvato-gray-medium dark:text-gray-400 drop-shadow-sm',
}

export function ToastContainer() {
  const { toasts, remove } = useToasts()

  return (
    <div className="fixed top-4 right-4 z-50 space-y-3 max-w-sm w-full pointer-events-none">
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
      initial={{ opacity: 0, y: -50, scale: 0.9, rotateX: -15 }}
      animate={{ opacity: 1, y: 0, scale: 1, rotateX: 0 }}
      exit={{ opacity: 0, x: 300, scale: 0.9, rotateX: 15 }}
      transition={{
        duration: 0.4,
        ease: [0.25, 0.46, 0.45, 0.94],
        type: "spring",
        damping: 25,
        stiffness: 300
      }}
      whileHover={{
        scale: 1.02,
        rotateY: 1,
        transition: { duration: 0.2 }
      }}
      className={cn(
        "relative overflow-hidden rounded-xl border-2 shadow-xl backdrop-blur-md pointer-events-auto",
        "transform-gpu will-change-transform",
        "shadow-2xl dark:shadow-black/20",
        colors[toast.type]
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        backdropFilter: 'blur(12px) saturate(180%)',
        WebkitBackdropFilter: 'blur(12px) saturate(180%)'
      }}
    >
      {/* Enhanced Progress bar */}
      {progressPercentage !== null && (
        <>
          <div className="absolute top-0 left-0 right-0 h-1 bg-black/10 dark:bg-white/10" />
          <motion.div
            className="absolute top-0 left-0 h-1 bg-gradient-to-r from-current to-current/80 shadow-sm"
            initial={{ width: "0%" }}
            animate={{ width: `${progressPercentage}%` }}
            transition={{
              duration: 0.3,
              ease: "easeOut",
              type: "spring",
              damping: 20
            }}
          />
        </>
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