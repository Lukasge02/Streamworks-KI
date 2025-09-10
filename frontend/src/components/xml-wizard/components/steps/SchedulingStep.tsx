/**
 * Scheduling Configuration Step
 * Configure when and how the stream should run
 */
'use client'

import React from 'react'
import { ScheduleMode, WizardStepProps } from '../../types/wizard.types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { 
  ChevronLeft, 
  ChevronRight, 
  Clock,
  Calendar,
  Zap,
  Info
} from 'lucide-react'

const WEEKDAYS = [
  { id: 0, name: 'Montag', short: 'Mo' },
  { id: 1, name: 'Dienstag', short: 'Di' },
  { id: 2, name: 'Mittwoch', short: 'Mi' },
  { id: 3, name: 'Donnerstag', short: 'Do' },
  { id: 4, name: 'Freitag', short: 'Fr' },
  { id: 5, name: 'Samstag', short: 'Sa' },
  { id: 6, name: 'Sonntag', short: 'So' }
]

const PRESET_SCHEDULES = [
  { value: 'manual', label: 'Manuell', description: 'Stream nur manuell starten' },
  { value: 'daily', label: 'Täglich', description: 'Jeden Tag zur angegebenen Zeit' },
  { value: 'weekly', label: 'Wöchentlich', description: 'An bestimmten Wochentagen' },
  { value: 'monthly', label: 'Monatlich', description: 'Einmal pro Monat' }
]

export const SchedulingStep: React.FC<WizardStepProps> = ({
  formData,
  onUpdateData,
  onNext,
  onPrevious,
  canProceed,
  isLastStep
}) => {
  const scheduling = formData.scheduling || {
    mode: ScheduleMode.SIMPLE,
    simple: {
      preset: 'manual',
      time: '06:00',
      weekdays: [true, true, true, true, true, false, false] // Mo-Fr
    }
  }

  const handleModeChange = (mode: ScheduleMode) => {
    onUpdateData({
      scheduling: {
        ...scheduling,
        mode
      }
    })
  }

  const handlePresetChange = (preset: string) => {
    onUpdateData({
      scheduling: {
        ...scheduling,
        simple: {
          ...scheduling.simple,
          preset
        }
      }
    })
  }

  const handleTimeChange = (time: string) => {
    onUpdateData({
      scheduling: {
        ...scheduling,
        simple: {
          ...scheduling.simple,
          time
        }
      }
    })
  }

  const handleWeekdayToggle = (dayIndex: number) => {
    const newWeekdays = [...(scheduling.simple?.weekdays || [true, true, true, true, true, false, false])]
    newWeekdays[dayIndex] = !newWeekdays[dayIndex]
    
    onUpdateData({
      scheduling: {
        ...scheduling,
        simple: {
          ...scheduling.simple,
          weekdays: newWeekdays
        }
      }
    })
  }

  const handleNaturalDescriptionChange = (description: string) => {
    onUpdateData({
      scheduling: {
        ...scheduling,
        natural: { description }
      }
    })
  }

  const renderSimpleScheduling = () => (
    <div className="space-y-6">
      {/* Preset Selection */}
      <div>
        <Label className="text-sm font-medium mb-3 block">
          Zeitplan-Vorlage auswählen
        </Label>
        <div className="space-y-3">
          {PRESET_SCHEDULES.map((preset) => (
            <div
              key={preset.value}
              className={`cursor-pointer border rounded-lg p-3 transition-all ${
                scheduling.simple?.preset === preset.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
              }`}
              onClick={() => handlePresetChange(preset.value)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    {preset.label}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {preset.description}
                  </p>
                </div>
                <div className={`w-4 h-4 rounded-full border-2 ${
                  scheduling.simple?.preset === preset.value
                    ? 'border-blue-500 bg-blue-500'
                    : 'border-gray-300'
                }`}>
                  {scheduling.simple?.preset === preset.value && (
                    <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Time Configuration */}
      {scheduling.simple?.preset !== 'manual' && (
        <div>
          <Label htmlFor="time" className="text-sm font-medium">
            Ausführungszeit
          </Label>
          <div className="flex items-center space-x-2 mt-1">
            <Clock className="w-4 h-4 text-gray-400" />
            <Input
              id="time"
              type="time"
              value={scheduling.simple?.time || '06:00'}
              onChange={(e) => handleTimeChange(e.target.value)}
              className="w-32"
            />
          </div>
        </div>
      )}

      {/* Weekday Selection for Weekly */}
      {scheduling.simple?.preset === 'weekly' && (
        <div>
          <Label className="text-sm font-medium mb-3 block">
            Wochentage auswählen
          </Label>
          <div className="flex flex-wrap gap-2">
            {WEEKDAYS.map((day) => (
              <button
                key={day.id}
                type="button"
                onClick={() => handleWeekdayToggle(day.id)}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  scheduling.simple?.weekdays?.[day.id]
                    ? 'bg-blue-100 text-blue-700 border border-blue-300 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-700'
                    : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600'
                }`}
              >
                {day.short}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Ausgewählte Tage: {WEEKDAYS.filter((day, index) => 
              scheduling.simple?.weekdays?.[index]).map(day => day.name).join(', ') || 'Keine'
            }
          </p>
        </div>
      )}
    </div>
  )

  const renderNaturalScheduling = () => (
    <div className="space-y-4">
      <div>
        <Label htmlFor="naturalDescription" className="text-sm font-medium">
          Zeitplan in natürlicher Sprache beschreiben
        </Label>
        <textarea
          id="naturalDescription"
          value={scheduling.natural?.description || ''}
          onChange={(e) => handleNaturalDescriptionChange(e.target.value)}
          placeholder="z.B. 'Jeden Werktag um 6 Uhr morgens' oder 'Am ersten Montag jeden Monats um 8:30'"
          className="mt-1 w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          rows={3}
        />
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Beschreiben Sie den gewünschten Zeitplan in natürlicher Sprache. Das System wird versuchen, 
          daraus automatisch eine Streamworks-Regel zu generieren.
        </p>
      </div>
      
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
        <p className="text-sm text-yellow-700 dark:text-yellow-300">
          <strong>Hinweis:</strong> Die natürliche Spracherkennung für Zeitpläne ist experimentell. 
          Für produktive Umgebungen empfehlen wir die einfache oder erweiterte Konfiguration.
        </p>
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Zeitplanung konfigurieren
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Bestimmen Sie, wann und wie oft Ihr Stream ausgeführt werden soll
        </p>
      </div>

      {/* Schedule Mode Selection */}
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Calendar className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            Planungsart wählen
          </h3>
        </div>

        <div className="space-y-4 mb-6">
          <div
            className={`cursor-pointer border rounded-lg p-4 transition-all ${
              scheduling.mode === ScheduleMode.SIMPLE
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
            }`}
            onClick={() => handleModeChange(ScheduleMode.SIMPLE)}
          >
            <div className="flex items-start space-x-3">
              <Clock className="w-5 h-5 text-gray-600 dark:text-gray-300 mt-0.5" />
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white">
                  Einfache Planung
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Vorgefertigte Zeitpläne wie täglich, wöchentlich oder monatlich
                </p>
              </div>
            </div>
          </div>

          <div
            className={`cursor-pointer border rounded-lg p-4 transition-all ${
              scheduling.mode === ScheduleMode.NATURAL
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
            }`}
            onClick={() => handleModeChange(ScheduleMode.NATURAL)}
          >
            <div className="flex items-start space-x-3">
              <Zap className="w-5 h-5 text-gray-600 dark:text-gray-300 mt-0.5" />
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white">
                  Natürliche Sprache
                  <span className="ml-2 px-2 py-0.5 text-xs bg-yellow-100 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 rounded">
                    Experimentell
                  </span>
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Zeitplan in natürlicher Sprache beschreiben
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Schedule Configuration */}
        {scheduling.mode === ScheduleMode.SIMPLE && renderSimpleScheduling()}
        {scheduling.mode === ScheduleMode.NATURAL && renderNaturalScheduling()}
      </Card>

      {/* Preview/Summary */}
      {scheduling.mode === ScheduleMode.SIMPLE && scheduling.simple?.preset !== 'manual' && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2">
            Zeitplan-Vorschau
          </h4>
          <p className="text-sm text-green-700 dark:text-green-300">
            {scheduling.simple.preset === 'daily' && 
              `Stream läuft täglich um ${scheduling.simple.time || '06:00'} Uhr`
            }
            {scheduling.simple.preset === 'weekly' && 
              `Stream läuft ${WEEKDAYS.filter((day, index) => 
                scheduling.simple?.weekdays?.[index]).map(day => day.name).join(', ') || 'keine Tage ausgewählt'} um ${scheduling.simple.time || '06:00'} Uhr`
            }
            {scheduling.simple.preset === 'monthly' && 
              `Stream läuft monatlich um ${scheduling.simple.time || '06:00'} Uhr`
            }
          </p>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-200">
              Hinweise zur Zeitplanung
            </h4>
            <ul className="text-sm text-blue-700 dark:text-blue-300 mt-1 space-y-1">
              <li>• Manuelle Streams werden nur auf Anfrage ausgeführt</li>
              <li>• Zeitangaben beziehen sich auf die lokale Zeitzone des Streamworks-Servers</li>
              <li>• Bei wöchentlicher Planung muss mindestens ein Wochentag ausgewählt sein</li>
              <li>• Die Zeitplanung kann später in Streamworks angepasst werden</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
        <Button
          variant="outline"
          onClick={onPrevious}
          className="flex items-center space-x-2"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Zurück</span>
        </Button>
        
        <Button
          onClick={onNext}
          disabled={!canProceed}
          className="flex items-center space-x-2"
        >
          <span>Weiter</span>
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}

export default SchedulingStep