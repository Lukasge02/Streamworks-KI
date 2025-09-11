/**
 * Stream Properties Step  
 * Configure stream metadata and contact information
 */
'use client'

import React from 'react'
import { WizardStepProps } from '../../types/wizard.types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { 
  ChevronLeft, 
  ChevronRight, 
  Info,
  User,
  Building2,
  Settings,
  FileText
} from 'lucide-react'

export const StreamPropertiesStep: React.FC<WizardStepProps> = ({
  formData,
  onUpdateData,
  onNext,
  onPrevious,
  canProceed,
  isLastStep
}) => {
  const streamProps = formData.streamProperties || {
    streamName: '',
    description: '',
    documentation: '',
    contactPerson: {
      firstName: '',
      lastName: '',
      company: 'Arvato Systems',
      department: ''
    }
  }

  const handleFieldChange = (field: string, value: any) => {
    onUpdateData({
      streamProperties: {
        ...streamProps,
        [field]: value
      }
    })
  }

  const handleContactChange = (field: string, value: string) => {
    onUpdateData({
      streamProperties: {
        ...streamProps,
        contactPerson: {
          ...streamProps.contactPerson,
          [field]: value
        }
      }
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Stream-Eigenschaften
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Definieren Sie die Grundeinstellungen und Metadaten für Ihren Stream
        </p>
      </div>

      <div className="space-y-6">
        {/* Basic Stream Properties */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Settings className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Stammdaten
            </h3>
          </div>

          <div className="space-y-4">
            <div>
              <Label htmlFor="streamName" className="text-sm font-medium">
                Stream-Name *
              </Label>
              <Input
                id="streamName"
                type="text"
                value={streamProps.streamName}
                onChange={(e) => handleFieldChange('streamName', e.target.value)}
                placeholder="z.B. daily_backup_stream"
                className="mt-1"
                required
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Eindeutiger Name für den Stream (keine Leerzeichen)
              </p>
            </div>

            <div>
              <Label htmlFor="description" className="text-sm font-medium">
                Kurzbeschreibung *
              </Label>
              <Input
                id="description"
                type="text"
                value={streamProps.description}
                onChange={(e) => handleFieldChange('description', e.target.value)}
                placeholder="Kurze Beschreibung des Streams"
                className="mt-1"
                required
              />
            </div>

            <div>
              <Label htmlFor="documentation" className="text-sm font-medium">
                Dokumentation
              </Label>
              <textarea
                id="documentation"
                value={streamProps.documentation}
                onChange={(e) => handleFieldChange('documentation', e.target.value)}
                placeholder="Detaillierte Beschreibung, Zweck und Besonderheiten..."
                className="mt-1 w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                rows={3}
              />
            </div>

          </div>
        </Card>

        {/* Contact Person */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <User className="w-5 h-5 text-green-600 dark:text-green-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Kontaktperson
            </h3>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="firstName" className="text-sm font-medium">
                  Vorname *
                </Label>
                <Input
                  id="firstName"
                  type="text"
                  value={streamProps.contactPerson.firstName}
                  onChange={(e) => handleContactChange('firstName', e.target.value)}
                  placeholder="Max"
                  className="mt-1"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="lastName" className="text-sm font-medium">
                  Nachname *
                </Label>
                <Input
                  id="lastName"
                  type="text"
                  value={streamProps.contactPerson.lastName}
                  onChange={(e) => handleContactChange('lastName', e.target.value)}
                  placeholder="Mustermann"
                  className="mt-1"
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="company" className="text-sm font-medium">
                Unternehmen
              </Label>
              <Input
                id="company"
                type="text"
                value={streamProps.contactPerson.company}
                onChange={(e) => handleContactChange('company', e.target.value)}
                placeholder="Arvato Systems"
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="department" className="text-sm font-medium">
                Abteilung
              </Label>
              <Input
                id="department"
                type="text"
                value={streamProps.contactPerson.department}
                onChange={(e) => handleContactChange('department', e.target.value)}
                placeholder="IT Operations"
                className="mt-1"
              />
            </div>
          </div>
        </Card>

      </div>

      {/* Info Box */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-200">
              Hinweis zu den Stream-Eigenschaften
            </h4>
            <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
              Diese Informationen werden in die XML-Konfiguration eingebettet und von Streamworks 
              zur Verwaltung und Monitoring des Streams verwendet. Kontaktdaten sind wichtig für 
              Benachrichtigungen bei Fehlern.
            </p>
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

export default StreamPropertiesStep