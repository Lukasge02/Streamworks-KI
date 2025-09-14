/**
 * Stream Properties Overview
 * Hauptseite für das Stream-Properties Kapitel
 */
'use client'

import React from 'react'
import { WizardStepProps } from '../../types/wizard.types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { 
  Settings,
  User,
  FileText,
  Info,
  CheckCircle2,
  Circle,
  ChevronRight
} from 'lucide-react'
import InfoTooltip from '../../../ui/InfoTooltip'

export const StreamPropertiesOverview: React.FC<WizardStepProps> = ({
  formData,
  navigateToSubChapter
}) => {
  const streamProps = formData.streamProperties
  const hasStreamName = !!(streamProps?.streamName?.trim())
  const hasDescription = !!(streamProps?.description?.trim())
  const hasContactPerson = !!(streamProps?.contactPerson?.firstName?.trim() && streamProps?.contactPerson?.lastName?.trim())

  const handleNavigateToBasicInfo = () => {
    if (navigateToSubChapter) {
      navigateToSubChapter('stream-properties', 'basic-info')
    }
  }

  const handleNavigateToContact = () => {
    if (navigateToSubChapter) {
      navigateToSubChapter('stream-properties', 'contact-person')
    }
  }

  const completionCount = [hasStreamName, hasDescription, hasContactPerson].filter(Boolean).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
            <Settings className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
        </div>
        <div className="flex items-center justify-center gap-2 mb-2">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Stream-Eigenschaften
          </h2>
          <InfoTooltip 
            content="Grundlegende Konfiguration - definieren Sie Name, Beschreibung und Ansprechpartner für Ihren Stream"
            position="bottom"
          />
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Grundlegende Konfiguration und Metadaten für Ihren Stream
        </p>
      </div>


      {/* Configuration Sections */}
      <div className="space-y-4">
        {/* Basic Info */}
        <Card 
          className={`p-4 cursor-pointer transition-all duration-200 ${
            hasStreamName && hasDescription 
              ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-900/20' 
              : 'hover:shadow-md'
          }`}
          onClick={handleNavigateToBasicInfo}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg ${
                hasStreamName && hasDescription 
                  ? 'bg-green-100 dark:bg-green-800' 
                  : 'bg-gray-100 dark:bg-gray-800'
              }`}>
                {hasStreamName && hasDescription ? (
                  <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400" />
                ) : (
                  <FileText className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-gray-900 dark:text-white">Grunddaten</h3>
                  <InfoTooltip 
                    content="Stream-Name und Beschreibung zur Identifikation und besseren Übersicht"
                    position="right"
                  />
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {hasStreamName 
                    ? `Stream: "${streamProps?.streamName}"` 
                    : 'Stream-Name und Beschreibung festlegen'
                  }
                </p>
                {hasDescription && (
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 truncate">
                    {streamProps?.description}
                  </p>
                )}
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </div>
        </Card>

        {/* Contact Person */}
        <Card 
          className={`p-4 cursor-pointer transition-all duration-200 ${
            hasContactPerson 
              ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-900/20' 
              : 'hover:shadow-md'
          }`}
          onClick={handleNavigateToContact}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg ${
                hasContactPerson 
                  ? 'bg-green-100 dark:bg-green-800' 
                  : 'bg-gray-100 dark:bg-gray-800'
              }`}>
                {hasContactPerson ? (
                  <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400" />
                ) : (
                  <User className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-gray-900 dark:text-white">Kontaktperson</h3>
                  <InfoTooltip 
                    content="Ansprechpartner für Rückfragen zum Stream - hilft bei Support und Wartung"
                    position="right"
                  />
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {hasContactPerson 
                    ? `${streamProps?.contactPerson?.firstName} ${streamProps?.contactPerson?.lastName}` 
                    : 'Ansprechpartner für den Stream festlegen'
                  }
                </p>
                {hasContactPerson && streamProps?.contactPerson?.department && (
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {streamProps.contactPerson.department} - {streamProps.contactPerson.company}
                  </p>
                )}
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </div>
        </Card>
      </div>

      {/* Summary Card */}
      {completionCount > 0 && (
        <Card className="p-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-blue-100 dark:bg-blue-800 rounded-lg">
              <Info className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Stream-Konfiguration Zusammenfassung
              </h3>
              {hasStreamName && (
                <p className="text-gray-700 dark:text-gray-300 mb-1">
                  <strong>Stream:</strong> {streamProps?.streamName}
                </p>
              )}
              {hasDescription && (
                <p className="text-gray-700 dark:text-gray-300 mb-1">
                  <strong>Beschreibung:</strong> {streamProps?.description}
                </p>
              )}
              {hasContactPerson && (
                <p className="text-gray-700 dark:text-gray-300">
                  <strong>Kontakt:</strong> {streamProps?.contactPerson?.firstName} {streamProps?.contactPerson?.lastName}
                  {streamProps?.contactPerson?.department && ` (${streamProps.contactPerson.department})`}
                </p>
              )}
            </div>
          </div>
        </Card>
      )}

    </div>
  )
}

export default StreamPropertiesOverview