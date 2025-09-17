'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Zap,
  ArrowRight,
  Clock,
  CheckCircle,
  FastForward,
  Info
} from 'lucide-react'

// ================================
// TYPES
// ================================

export interface PhaseJumpInfo {
  fromPhase: string
  toPhase: string
  reason: string
  skippedPhases?: string[]
  timestamp: string
}

interface PhaseJumpNotificationProps {
  phaseJump?: PhaseJumpInfo
  onAcknowledge?: () => void
  className?: string
}

// ================================
// COMPONENT
// ================================

/**
 * Phase Jump Notification Component
 *
 * Shows users when the AI intelligently skips phases based on available data
 * - Transparent about AI decision-making
 * - Explains why phases were skipped
 * - Builds trust in the system's intelligence
 */
export const PhaseJumpNotification: React.FC<PhaseJumpNotificationProps> = ({
  phaseJump,
  onAcknowledge,
  className = ''
}) => {
  const [isVisible, setIsVisible] = React.useState(false)

  React.useEffect(() => {
    if (phaseJump) {
      setIsVisible(true)

      // Auto-hide after 5 seconds if no acknowledge handler
      if (!onAcknowledge) {
        const timer = setTimeout(() => setIsVisible(false), 5000)
        return () => clearTimeout(timer)
      }
    }
  }, [phaseJump, onAcknowledge])

  const formatPhase = (phase: string): string => {
    const phaseLabels: Record<string, string> = {
      'initialization': 'Initialisierung',
      'job_configuration': 'Job-Konfiguration',
      'stream_properties': 'Stream-Eigenschaften',
      'scheduling': 'Zeitplanung',
      'validation': 'Validierung',
      'creation': 'Erstellung',
      'completed': 'Abgeschlossen'
    }

    return phaseLabels[phase] || phase.replace('_', ' ')
  }

  const getPhaseIcon = (phase: string) => {
    switch (phase) {
      case 'creation':
        return <FastForward className="w-4 h-4 text-green-500" />
      case 'validation':
        return <CheckCircle className="w-4 h-4 text-blue-500" />
      case 'scheduling':
        return <Clock className="w-4 h-4 text-purple-500" />
      default:
        return <Zap className="w-4 h-4 text-orange-500" />
    }
  }

  const getReasonIcon = (reason: string) => {
    if (reason.includes('all required data')) return <CheckCircle className="w-4 h-4 text-green-500" />
    if (reason.includes('sufficient')) return <Zap className="w-4 h-4 text-blue-500" />
    return <Info className="w-4 h-4 text-purple-500" />
  }

  const handleAcknowledge = () => {
    setIsVisible(false)
    if (onAcknowledge) {
      onAcknowledge()
    }
  }

  if (!phaseJump || !isVisible) {
    return null
  }

  return (
    <div className={`phase-jump-notification ${className}`}>
      <Card className="border-blue-200 bg-blue-50 dark:bg-blue-900/10 dark:border-blue-800 animate-slide-down">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            {/* Jump Icon */}
            <div className="mt-1">
              <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-full">
                <FastForward className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="font-medium text-blue-900 dark:text-blue-100">
                  🚀 Intelligenter Phasen-Sprung
                </h4>
                <Badge variant="outline" className="text-xs border-blue-300 text-blue-700 dark:border-blue-600 dark:text-blue-300">
                  Smart AI
                </Badge>
              </div>

              <p className="text-sm text-blue-800 dark:text-blue-200 mb-3">
                Die KI hat genügend Informationen erkannt, um Schritte zu überspringen und direkt zur passenden Phase zu springen.
              </p>

              {/* Phase Jump Visualization */}
              <div className="flex items-center gap-2 mb-3 p-3 bg-white dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1">
                    {getPhaseIcon(phaseJump.fromPhase)}
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {formatPhase(phaseJump.fromPhase)}
                    </span>
                  </div>

                  <ArrowRight className="w-4 h-4 text-blue-500" />

                  <div className="flex items-center gap-1">
                    {getPhaseIcon(phaseJump.toPhase)}
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {formatPhase(phaseJump.toPhase)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Skipped Phases */}
              {phaseJump.skippedPhases && phaseJump.skippedPhases.length > 0 && (
                <div className="mb-3">
                  <div className="text-xs text-blue-700 dark:text-blue-300 mb-1">
                    Übersprungene Phasen:
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {phaseJump.skippedPhases.map((phase) => (
                      <Badge
                        key={phase}
                        variant="secondary"
                        className="text-xs bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-300"
                      >
                        {formatPhase(phase)}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Reason */}
              <div className="flex items-start gap-2 mb-3">
                {getReasonIcon(phaseJump.reason)}
                <div>
                  <div className="text-xs text-blue-700 dark:text-blue-300 font-medium mb-1">
                    Grund für den Sprung:
                  </div>
                  <div className="text-xs text-blue-600 dark:text-blue-400">
                    {phaseJump.reason}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between">
                <div className="text-xs text-blue-500 dark:text-blue-400">
                  {new Date(phaseJump.timestamp).toLocaleTimeString('de-DE')}
                </div>

                {onAcknowledge && (
                  <button
                    onClick={handleAcknowledge}
                    className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 underline decoration-dotted transition-colors"
                  >
                    OK, verstanden
                  </button>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

/**
 * Hook to manage phase jump notifications
 */
export const usePhaseJumpNotification = () => {
  const [currentPhaseJump, setCurrentPhaseJump] = React.useState<PhaseJumpInfo | null>(null)

  const showPhaseJump = (phaseJump: PhaseJumpInfo) => {
    setCurrentPhaseJump(phaseJump)
  }

  const acknowledgePhaseJump = () => {
    setCurrentPhaseJump(null)
  }

  const clearPhaseJump = () => {
    setCurrentPhaseJump(null)
  }

  return {
    currentPhaseJump,
    showPhaseJump,
    acknowledgePhaseJump,
    clearPhaseJump
  }
}

// CSS for the slide-down animation (add to your global CSS)
/*
@keyframes slide-down {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-down {
  animation: slide-down 0.3s ease-out;
}
*/