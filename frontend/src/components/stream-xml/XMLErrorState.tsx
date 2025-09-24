'use client'

import React from 'react'
import { motion } from 'framer-motion'
import {
  AlertTriangle,
  RefreshCw,
  ArrowLeft,
  Wifi,
  Database,
  FileX,
  Bot,
  Settings,
  ExternalLink
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'

/**
 * 🚨 Enhanced XML Error State Component
 *
 * Features:
 * - Categorized error types with specific icons and messages
 * - Recovery suggestions and action buttons
 * - Error details with technical information
 * - Professional error reporting
 */

interface XMLErrorStateProps {
  error: string
  errorType?: 'network' | 'session' | 'generation' | 'validation' | 'parameters' | 'unknown'
  sessionId?: string
  onRetry: () => void
  onBackToChat: () => void
  canRetry?: boolean
}

interface ErrorConfig {
  icon: React.ComponentType<any>
  title: string
  description: string
  color: string
  bgColor: string
  borderColor: string
  suggestions: string[]
}

export function XMLErrorState({
  error,
  errorType = 'unknown',
  sessionId,
  onRetry,
  onBackToChat,
  canRetry = true
}: XMLErrorStateProps) {
  // Error type configuration
  const errorConfigs: Record<string, ErrorConfig> = {
    network: {
      icon: Wifi,
      title: 'Netzwerk-Problem',
      description: 'Verbindung zum Server fehlgeschlagen',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      suggestions: [
        'Internetverbindung überprüfen',
        'VPN deaktivieren falls aktiv',
        'Browser-Cache leeren',
        'Firewall-Einstellungen prüfen'
      ]
    },
    session: {
      icon: Database,
      title: 'Session-Fehler',
      description: 'Sitzungsdaten konnten nicht geladen werden',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      suggestions: [
        'Neue Session im Chat erstellen',
        'Browser-Cookies überprüfen',
        'Anmeldung erneuern',
        'Session-ID validieren'
      ]
    },
    generation: {
      icon: Bot,
      title: 'XML-Generierung fehlgeschlagen',
      description: 'KI-System konnte XML nicht erstellen',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      suggestions: [
        'Parameter-Vollständigkeit prüfen',
        'Job-Type erneut bestimmen lassen',
        'Chat-Historie durchgehen',
        'Erneut generieren versuchen'
      ]
    },
    parameters: {
      icon: Settings,
      title: 'Parameter-Problem',
      description: 'Unvollständige oder ungültige Parameter',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      suggestions: [
        'Zurück zum Chat gehen',
        'Fehlende Parameter nachreichen',
        'Job-Description präzisieren',
        'Parameter-Übersicht prüfen'
      ]
    },
    validation: {
      icon: FileX,
      title: 'Validierungs-Fehler',
      description: 'XML-Struktur oder Daten sind ungültig',
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      suggestions: [
        'Parameter-Format überprüfen',
        'Streamworks-Schema validieren',
        'Template-Kompatibilität prüfen',
        'Eingabedaten korrigieren'
      ]
    },
    unknown: {
      icon: AlertTriangle,
      title: 'Unbekannter Fehler',
      description: 'Ein unerwarteter Fehler ist aufgetreten',
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      suggestions: [
        'Browser-Konsole prüfen',
        'Support kontaktieren',
        'Seite neu laden',
        'Andere Browser versuchen'
      ]
    }
  }

  const config = errorConfigs[errorType] || errorConfigs.unknown
  const ErrorIcon = config.icon

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50 p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl w-full"
      >
        <Card className={`p-8 border-2 ${config.borderColor} ${config.bgColor}`}>
          {/* Error Header */}
          <div className="text-center mb-6">
            <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${config.bgColor} ${config.borderColor} border-2 mb-4`}>
              <ErrorIcon className={`w-8 h-8 ${config.color}`} />
            </div>

            <h1 className={`text-2xl font-bold ${config.color} mb-2`}>
              {config.title}
            </h1>

            <p className="text-gray-600 text-lg">
              {config.description}
            </p>

            {sessionId && (
              <Badge variant="outline" className="mt-2 font-mono text-xs">
                Session: {sessionId.slice(0, 8)}...
              </Badge>
            )}
          </div>

          {/* Error Details */}
          <div className={`p-4 rounded-lg ${config.bgColor} ${config.borderColor} border mb-6`}>
            <h3 className="font-semibold text-gray-900 mb-2">Technische Details:</h3>
            <p className="text-sm text-gray-700 font-mono break-words">
              {error}
            </p>
          </div>

          {/* Recovery Suggestions */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 mb-3">Lösungsvorschläge:</h3>
            <ul className="space-y-2">
              {config.suggestions.map((suggestion, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-2 text-sm text-gray-700"
                >
                  <div className={`w-2 h-2 rounded-full ${config.color.replace('text-', 'bg-')}`} />
                  <span>{suggestion}</span>
                </motion.li>
              ))}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            {canRetry && (
              <Button
                onClick={onRetry}
                className="flex-1 flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Erneut versuchen</span>
              </Button>
            )}

            <Button
              onClick={onBackToChat}
              variant="outline"
              className="flex-1 flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Zurück zum Chat</span>
            </Button>

            {/* Support Link */}
            <Button
              variant="ghost"
              size="sm"
              className="flex items-center gap-2 text-gray-500"
              onClick={() => window.open('/support', '_blank')}
            >
              <ExternalLink className="w-3 h-3" />
              <span>Support</span>
            </Button>
          </div>

          {/* Additional Info */}
          <div className="mt-6 pt-4 border-t border-gray-200 text-center">
            <p className="text-xs text-gray-500">
              💡 Tipp: Die meisten Probleme lassen sich durch einen Neustart der Session beheben
            </p>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}