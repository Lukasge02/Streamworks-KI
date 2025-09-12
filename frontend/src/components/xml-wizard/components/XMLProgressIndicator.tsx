/**
 * XMLProgressIndicator - Shows completion status and placeholders
 */
'use client'

import React from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  FileText,
  Zap,
  AlertTriangle
} from 'lucide-react'

interface XMLProgressIndicatorProps {
  completionPercentage: number
  placeholderCount: number
  generationTimeMs: number
  isGenerating: boolean
  error?: string | null
  lastGenerated?: Date | null
  className?: string
}

export const XMLProgressIndicator: React.FC<XMLProgressIndicatorProps> = ({
  completionPercentage,
  placeholderCount,
  generationTimeMs,
  isGenerating,
  error,
  lastGenerated,
  className = ''
}) => {
  const getStatusColor = () => {
    if (error) return 'text-red-600 dark:text-red-400'
    if (isGenerating) return 'text-blue-600 dark:text-blue-400'
    if (completionPercentage >= 90) return 'text-green-600 dark:text-green-400'
    if (completionPercentage >= 60) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-gray-600 dark:text-gray-400'
  }
  
  const getStatusIcon = () => {
    if (error) return <AlertTriangle className="w-4 h-4" />
    if (isGenerating) return <Clock className="w-4 h-4 animate-spin" />
    if (completionPercentage >= 90) return <CheckCircle className="w-4 h-4" />
    if (completionPercentage >= 60) return <AlertCircle className="w-4 h-4" />
    return <FileText className="w-4 h-4" />
  }
  
  const getStatusText = () => {
    if (error) return 'Fehler bei Generierung'
    if (isGenerating) return 'Generiere Preview...'
    if (completionPercentage >= 90) return 'Fast vollständig'
    if (completionPercentage >= 60) return 'In Bearbeitung'
    return 'Wizard ausfüllen'
  }
  
  const formatTime = (ms: number) => {
    if (ms < 100) return `${ms}ms`
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }
  
  return (
    <Card className={`p-4 ${className}`}>
      <div className="space-y-3">
        {/* Header with status */}
        <div className="flex items-center justify-between">
          <div className={`flex items-center space-x-2 ${getStatusColor()}`}>
            {getStatusIcon()}
            <span className="font-medium text-sm">
              {getStatusText()}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            {generationTimeMs > 0 && (
              <div className="flex items-center space-x-1 text-xs text-gray-500 dark:text-gray-400">
                <Zap className="w-3 h-3" />
                <span>{formatTime(generationTimeMs)}</span>
              </div>
            )}
            
            {lastGenerated && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {lastGenerated.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
        
        {/* Progress bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              XML Vollständigkeit
            </span>
            <span className={`font-medium ${getStatusColor()}`}>
              {completionPercentage}%
            </span>
          </div>
          
          <Progress 
            value={completionPercentage} 
            className="h-2"
          />
        </div>
        
        {/* Placeholder indicators */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-gray-600 dark:text-gray-400">
                Ausgefüllt: {Math.max(0, 15 - placeholderCount)}
              </span>
            </div>
            
            {placeholderCount > 0 && (
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span className="text-gray-600 dark:text-gray-400">
                  Platzhalter: {placeholderCount}
                </span>
              </div>
            )}
          </div>
          
          {/* Completion badges */}
          <div className="flex items-center space-x-1">
            {completionPercentage >= 90 && (
              <Badge variant="default" className="text-xs">
                Ready
              </Badge>
            )}
            {completionPercentage >= 60 && completionPercentage < 90 && (
              <Badge variant="secondary" className="text-xs">
                Preview
              </Badge>
            )}
            {completionPercentage < 60 && (
              <Badge variant="outline" className="text-xs">
                Draft
              </Badge>
            )}
          </div>
        </div>
        
        {/* Error message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
            <p className="text-sm text-red-700 dark:text-red-300">
              {error}
            </p>
          </div>
        )}
        
        {/* Helpful tips based on completion */}
        {!error && !isGenerating && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
            <p className="text-xs text-blue-700 dark:text-blue-300">
              {completionPercentage < 30 && "💡 Wählen Sie zuerst einen Job-Typ aus"}
              {completionPercentage >= 30 && completionPercentage < 60 && "📝 Füllen Sie die Stream-Eigenschaften aus"}
              {completionPercentage >= 60 && completionPercentage < 90 && "⚙️ Konfigurieren Sie Job-Details für beste Ergebnisse"}
              {completionPercentage >= 90 && "✨ XML ist bereit zum Export!"}
            </p>
          </div>
        )}
      </div>
    </Card>
  )
}

export default XMLProgressIndicator