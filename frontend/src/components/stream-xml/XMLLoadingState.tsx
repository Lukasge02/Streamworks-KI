'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Loader2,
  Database,
  Bot,
  Code2,
  Settings,
  CheckCircle,
  Clock
} from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'

/**
 * 🔄 Enhanced XML Loading State Component
 *
 * Features:
 * - Multi-stage loading with progress indication
 * - Animated step transitions
 * - Informative loading messages
 * - Estimated time remaining
 * - Professional loading experience
 */

interface XMLLoadingStateProps {
  sessionId: string
  currentStage?: 'initializing' | 'loading_session' | 'generating_xml' | 'finalizing'
  progress?: number
}

interface LoadingStage {
  key: string
  icon: React.ComponentType<any>
  title: string
  description: string
  estimatedTime: number // in seconds
  color: string
}

export function XMLLoadingState({
  sessionId,
  currentStage = 'initializing',
  progress = 0
}: XMLLoadingStateProps) {
  const [elapsedTime, setElapsedTime] = useState(0)

  // Loading stages configuration
  const stages: LoadingStage[] = [
    {
      key: 'initializing',
      icon: Database,
      title: 'System initialisieren',
      description: 'Verbindung zur Session wird hergestellt...',
      estimatedTime: 2,
      color: 'text-blue-600'
    },
    {
      key: 'loading_session',
      icon: Settings,
      title: 'Session laden',
      description: 'Parameter und Chat-Historie werden geladen...',
      estimatedTime: 3,
      color: 'text-green-600'
    },
    {
      key: 'generating_xml',
      icon: Bot,
      title: 'XML generieren',
      description: 'KI erstellt XML-Stream basierend auf Parametern...',
      estimatedTime: 4,
      color: 'text-purple-600'
    },
    {
      key: 'finalizing',
      icon: Code2,
      title: 'Editor vorbereiten',
      description: 'Monaco Editor und Interface werden geladen...',
      estimatedTime: 2,
      color: 'text-orange-600'
    }
  ]

  const currentStageIndex = stages.findIndex(s => s.key === currentStage)
  const currentStageData = stages[currentStageIndex] || stages[0]
  const CurrentIcon = currentStageData.icon

  // Timer for elapsed time
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime(prev => prev + 1)
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // Calculate overall progress
  const getOverallProgress = () => {
    const baseProgress = (currentStageIndex / stages.length) * 100
    const stageProgress = (progress / 100) * (100 / stages.length)
    return Math.min(baseProgress + stageProgress, 100)
  }

  const overallProgress = getOverallProgress()
  const estimatedTotal = stages.reduce((sum, stage) => sum + stage.estimatedTime, 0)
  const remainingTime = Math.max(estimatedTotal - elapsedTime, 0)

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg w-full"
      >
        <Card className="p-8 shadow-xl border-0">
          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className={`inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 mb-4`}
            >
              <CurrentIcon className="w-8 h-8 text-white" />
            </motion.div>

            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              XML Stream wird geladen...
            </h1>

            <Badge variant="outline" className="font-mono text-xs">
              Session: {sessionId.slice(0, 8)}...
            </Badge>
          </div>

          {/* Current Stage */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-lg bg-blue-50 border border-blue-200`}>
                <CurrentIcon className={`w-4 h-4 ${currentStageData.color}`} />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">
                  {currentStageData.title}
                </h3>
                <p className="text-sm text-gray-600">
                  {currentStageData.description}
                </p>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                Fortschritt
              </span>
              <span className="text-sm text-gray-600">
                {Math.round(overallProgress)}%
              </span>
            </div>
            <Progress value={overallProgress} className="h-2" />
          </div>

          {/* Stage Progress */}
          <div className="mb-6">
            <div className="flex justify-between items-center space-x-2">
              {stages.map((stage, index) => {
                const StageIcon = stage.icon
                const isCompleted = index < currentStageIndex
                const isCurrent = index === currentStageIndex
                const isPending = index > currentStageIndex

                return (
                  <div
                    key={stage.key}
                    className={`flex-1 flex flex-col items-center p-2 rounded-lg transition-all ${
                      isCompleted ? 'bg-green-50 border border-green-200' :
                      isCurrent ? 'bg-blue-50 border border-blue-200' :
                      'bg-gray-50 border border-gray-200'
                    }`}
                  >
                    <div className={`p-1.5 rounded-full mb-1 ${
                      isCompleted ? 'bg-green-100' :
                      isCurrent ? 'bg-blue-100' :
                      'bg-gray-100'
                    }`}>
                      {isCompleted ? (
                        <CheckCircle className="w-3 h-3 text-green-600" />
                      ) : (
                        <StageIcon className={`w-3 h-3 ${
                          isCurrent ? stage.color :
                          'text-gray-400'
                        }`} />
                      )}
                    </div>
                    <span className={`text-xs font-medium ${
                      isCompleted ? 'text-green-700' :
                      isCurrent ? 'text-blue-700' :
                      'text-gray-500'
                    }`}>
                      {stage.title.split(' ')[0]}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Time Information */}
          <div className="flex items-center justify-between mb-6 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-600" />
              <span className="text-sm text-gray-700">Verstrichene Zeit:</span>
              <Badge variant="outline" className="font-mono text-xs">
                {Math.floor(elapsedTime / 60)}:{(elapsedTime % 60).toString().padStart(2, '0')}
              </Badge>
            </div>
            {remainingTime > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-700">Noch ca.:</span>
                <Badge variant="outline" className="font-mono text-xs">
                  {remainingTime}s
                </Badge>
              </div>
            )}
          </div>

        </Card>
      </motion.div>
    </div>
  )
}