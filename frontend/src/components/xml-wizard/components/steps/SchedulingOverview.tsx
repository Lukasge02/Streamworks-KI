/**
 * Scheduling Overview
 * Hauptseite für das Scheduling Kapitel
 */
'use client'

import React from 'react'
import { WizardStepProps, ScheduleMode } from '../../types/wizard.types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { 
  Clock,
  Calendar,
  Play,
  Zap,
  CheckCircle2,
  Circle,
  ChevronRight,
  Info
} from 'lucide-react'
import InfoTooltip from '../../../ui/InfoTooltip'

const SCHEDULE_MODE_INFO = {
  [ScheduleMode.SIMPLE]: {
    title: 'Einfache Planung',
    description: 'Vorgefertigte Zeitpläne wie täglich, wöchentlich oder monatlich',
    icon: Clock,
    examples: ['Täglich um 08:00', 'Wöchentlich montags', 'Monatlich am 1.'],
    color: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    textColor: 'text-green-600 dark:text-green-400'
  },
  [ScheduleMode.ADVANCED]: {
    title: 'Erweiterte Planung',
    description: 'Komplexe Zeitpläne mit Cron-Expressions und XML-Regeln',
    icon: Zap,
    examples: ['Cron: 0 8 * * 1-5', 'Abhängigkeiten', 'Bedingungen'],
    color: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800',
    textColor: 'text-purple-600 dark:text-purple-400'
  }
}

export const SchedulingOverview: React.FC<WizardStepProps> = ({
  formData,
  navigateToSubChapter
}) => {
  const scheduling = formData.scheduling
  const hasScheduling = !!scheduling?.mode
  const scheduleInfo = scheduling?.mode ? SCHEDULE_MODE_INFO[scheduling.mode] : null

  const handleNavigateToScheduling = () => {
    if (navigateToSubChapter) {
      navigateToSubChapter('scheduling', '')
    }
  }

  const getScheduleDescription = () => {
    if (!scheduling) return null

    if (scheduling.mode === ScheduleMode.SIMPLE && scheduling.simple) {
      const simple = scheduling.simple
      if (simple.preset === 'manual') return 'Manuell starten'
      if (simple.preset === 'daily' && simple.time) return `Täglich um ${simple.time}`
      if (simple.preset === 'weekly') return 'Wöchentlich'
      if (simple.preset === 'monthly') return 'Monatlich'
      return `${simple.preset} Zeitplan`
    }

    if (scheduling.mode === ScheduleMode.ADVANCED && scheduling.advanced) {
      const advanced = scheduling.advanced
      if (advanced.cron_expression) return `Cron: ${advanced.cron_expression}`
      if (advanced.schedule_rule_xml) return 'Benutzerdefinierte XML-Regel'
      return 'Erweiterte Planung'
    }

    return scheduleInfo?.title || 'Zeitplan konfiguriert'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
            <Clock className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
        </div>
        <div className="flex items-center justify-center gap-2 mb-2">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Stream-Planung
          </h2>
          <InfoTooltip 
            content="Optional: Legen Sie fest wann der Stream automatisch ausgeführt wird. Kann auch manuell gestartet werden. Zeitpläne können jederzeit geändert werden."
            position="bottom"
          />
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Definieren Sie, wann und wie oft Ihr Stream ausgeführt werden soll
        </p>
      </div>

      {/* Current Status */}
      <Card className={`p-6 ${hasScheduling ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : ''}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`p-3 rounded-lg ${
              hasScheduling ? 'bg-green-100 dark:bg-green-800' : 'bg-gray-100 dark:bg-gray-800'
            }`}>
              {hasScheduling ? (
                <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-400" />
              ) : (
                <Circle className="w-6 h-6 text-gray-400" />
              )}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {hasScheduling ? 'Zeitplan konfiguriert' : 'Zeitplan offen'}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {hasScheduling ? getScheduleDescription() : 'Stream-Ausführung noch nicht geplant'}
              </p>
            </div>
          </div>
          <Button
            onClick={handleNavigateToScheduling}
            variant={hasScheduling ? "outline" : "default"}
          >
            {hasScheduling ? 'Ändern' : 'Konfigurieren'}
          </Button>
        </div>
      </Card>

      {/* Schedule Mode Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(SCHEDULE_MODE_INFO).map(([mode, info]) => {
          const Icon = info.icon
          const isSelected = scheduling?.mode === mode
          
          return (
            <Card
              key={mode}
              className={`p-4 cursor-pointer transition-all duration-200 ${
                isSelected 
                  ? `${info.color} ring-2 ring-blue-500` 
                  : 'hover:shadow-md'
              }`}
              onClick={handleNavigateToScheduling}
            >
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${
                  isSelected ? 'bg-white dark:bg-gray-800' : 'bg-gray-100 dark:bg-gray-800'
                }`}>
                  <Icon className={`w-5 h-5 ${isSelected ? info.textColor : 'text-gray-600 dark:text-gray-400'}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                    {info.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {info.description}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {info.examples.map((example, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                      >
                        {example}
                      </span>
                    ))}
                  </div>
                </div>
                {isSelected && (
                  <CheckCircle2 className={`w-5 h-5 ${info.textColor}`} />
                )}
              </div>
            </Card>
          )
        })}
      </div>

      {/* Current Schedule Details */}
      {scheduleInfo && (
        <Card className={`p-6 ${scheduleInfo.color}`}>
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
              <scheduleInfo.icon className={`w-6 h-6 ${scheduleInfo.textColor}`} />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Aktuelle Planung: {scheduleInfo.title}
              </h3>
              <p className="text-gray-700 dark:text-gray-300 mb-2">
                <strong>Ausführung:</strong> {getScheduleDescription()}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {scheduleInfo.description}
              </p>
            </div>
          </div>
        </Card>
      )}


      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button 
          onClick={handleNavigateToScheduling}
          className="flex-1"
          variant={hasScheduling ? "outline" : "default"}
        >
          <Calendar className="w-4 h-4 mr-2" />
          {hasScheduling ? 'Zeitplan ändern' : 'Zeitplan erstellen'}
        </Button>
        
        <Button 
          variant="outline"
          className="flex-1"
          onClick={() => {
            // Optional: Zum nächsten Schritt ohne Scheduling
            if (navigateToSubChapter) {
              navigateToSubChapter('review', '')
            }
          }}
        >
          <Play className="w-4 h-4 mr-2" />
          Ohne Zeitplan weiter
        </Button>
      </div>
    </div>
  )
}

export default SchedulingOverview