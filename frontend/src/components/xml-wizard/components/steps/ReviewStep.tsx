/**
 * Review and Generate Step
 * Final step - review configuration and generate XML
 */
'use client'

import React, { useState, useEffect } from 'react'
import { WizardStepProps, JobType } from '../../types/wizard.types'
import { generateStreamworksXML, validateXML } from '../../utils/xmlGenerator'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { 
  ChevronLeft, 
  CheckCircle,
  AlertTriangle,
  FileText,
  User,
  Clock,
  Terminal,
  Database,
  FolderSync,
  Zap,
  Download,
  RefreshCw
} from 'lucide-react'
import { toast } from 'sonner'

export const ReviewStep: React.FC<WizardStepProps> = ({
  formData,
  onUpdateData,
  onPrevious,
  canProceed,
  isLastStep
}) => {
  const [isGenerating, setIsGenerating] = useState(false)
  const [xmlResult, setXmlResult] = useState<any>(null)
  const [validationResult, setValidationResult] = useState<any>(null)

  // Auto-generate XML when step is reached
  useEffect(() => {
    if (canProceed && !xmlResult) {
      handleGenerateXML()
    }
  }, [canProceed])

  const handleGenerateXML = async () => {
    setIsGenerating(true)
    
    try {
      // Simulate some processing time
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const result = generateStreamworksXML(formData)
      setXmlResult(result)
      
      if (result.success && result.xmlContent) {
        const validation = validateXML(result.xmlContent)
        setValidationResult(validation)
        
        // Update form data with generated XML
        onUpdateData({
          generatedXML: result.xmlContent,
          validationResults: validation
        })
        
        toast.success('XML erfolgreich generiert!')
      } else {
        toast.error(`XML-Generierung fehlgeschlagen: ${result.error}`)
      }
    } catch (error) {
      toast.error('Unerwarteter Fehler bei der XML-Generierung')
      setXmlResult({
        success: false,
        error: error instanceof Error ? error.message : 'Unbekannter Fehler'
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownloadXML = () => {
    if (!xmlResult?.xmlContent) return
    
    try {
      const blob = new Blob([xmlResult.xmlContent], { type: 'application/xml' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${formData.streamProperties?.streamName || 'streamworks'}-${new Date().toISOString().split('T')[0]}.xml`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      toast.success('XML-Datei heruntergeladen')
    } catch (error) {
      toast.error('Fehler beim Herunterladen der XML')
    }
  }

  const getJobTypeIcon = (jobType: JobType) => {
    switch (jobType) {
      case JobType.STANDARD:
        return Terminal
      case JobType.SAP:
        return Database
      case JobType.FILE_TRANSFER:
        return FolderSync
      default:
        return FileText
    }
  }

  const getJobTypeName = (jobType: JobType) => {
    switch (jobType) {
      case JobType.STANDARD:
        return 'Standard Job'
      case JobType.SAP:
        return 'SAP Job'
      case JobType.FILE_TRANSFER:
        return 'File Transfer'
      default:
        return 'Unbekannter Job-Typ'
    }
  }

  const getScheduleDescription = () => {
    const scheduling = formData.scheduling
    if (!scheduling) return 'Nicht konfiguriert'
    
    if (scheduling.simple?.preset === 'manual') {
      return 'Manueller Start'
    }
    
    if (scheduling.simple?.preset === 'daily') {
      return `Täglich um ${scheduling.simple.time || '06:00'} Uhr`
    }
    
    if (scheduling.simple?.preset === 'weekly') {
      const weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
      const selectedDays = weekdays.filter((_, index) => scheduling.simple?.weekdays?.[index])
      return `${selectedDays.join(', ')} um ${scheduling.simple.time || '06:00'} Uhr`
    }
    
    if (scheduling.mode === 'natural' && scheduling.natural?.description) {
      return scheduling.natural.description
    }
    
    return 'Konfiguriert'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Konfiguration überprüfen
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Überprüfen Sie Ihre Einstellungen und generieren Sie die Streamworks-XML
        </p>
      </div>

      {/* Configuration Summary */}
      <div className="space-y-6">
        {/* Stream Properties */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Stream-Eigenschaften
            </h3>
          </div>
          
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Name:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {formData.streamProperties?.streamName || 'Nicht festgelegt'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Beschreibung:</span>
              <span className="font-medium text-gray-900 dark:text-white text-right ml-4">
                {formData.streamProperties?.description || 'Nicht festgelegt'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Max. Läufe:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {formData.streamProperties?.maxRuns || 5}
              </span>
            </div>
            {formData.streamProperties?.streamPath && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Pfad:</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {formData.streamProperties.streamPath}
                </span>
              </div>
            )}
          </div>
        </Card>

        {/* Job Configuration */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            {React.createElement(getJobTypeIcon(formData.jobType!), {
              className: "w-5 h-5 text-green-600 dark:text-green-400"
            })}
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Job-Konfiguration
            </h3>
          </div>
          
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Typ:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {getJobTypeName(formData.jobType!)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Job-Name:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {(formData.jobForm as any)?.jobName || 'Nicht festgelegt'}
              </span>
            </div>
            {formData.jobType === JobType.STANDARD && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">OS:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {(formData.jobForm as any)?.os || 'Windows'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Agent:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {(formData.jobForm as any)?.agent || 'Nicht festgelegt'}
                  </span>
                </div>
              </>
            )}
            {formData.jobType === JobType.SAP && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">System:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {(formData.jobForm as any)?.system || 'Nicht festgelegt'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Report:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {(formData.jobForm as any)?.report || 'Nicht festgelegt'}
                  </span>
                </div>
              </>
            )}
            {formData.jobType === JobType.FILE_TRANSFER && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Quelle:</span>
                  <span className="font-medium text-gray-900 dark:text-white text-right ml-4">
                    {(formData.jobForm as any)?.sourcePath || 'Nicht festgelegt'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Ziel:</span>
                  <span className="font-medium text-gray-900 dark:text-white text-right ml-4">
                    {(formData.jobForm as any)?.targetPath || 'Nicht festgelegt'}
                  </span>
                </div>
              </>
            )}
          </div>
        </Card>

        {/* Contact Person */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <User className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Kontaktperson
            </h3>
          </div>
          
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Name:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {formData.streamProperties?.contactPerson?.firstName} {formData.streamProperties?.contactPerson?.lastName}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Unternehmen:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {formData.streamProperties?.contactPerson?.company || 'Arvato Systems'}
              </span>
            </div>
            {formData.streamProperties?.contactPerson?.department && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Abteilung:</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {formData.streamProperties.contactPerson.department}
                </span>
              </div>
            )}
          </div>
        </Card>

        {/* Scheduling */}
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Clock className="w-5 h-5 text-orange-600 dark:text-orange-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Zeitplanung
            </h3>
          </div>
          
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Zeitplan:</span>
              <span className="font-medium text-gray-900 dark:text-white text-right ml-4">
                {getScheduleDescription()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Modus:</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {formData.scheduling?.mode === 'simple' ? 'Einfach' : 
                 formData.scheduling?.mode === 'natural' ? 'Natürliche Sprache' : 'Erweitert'}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* XML Generation Status */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              XML-Generierung
            </h3>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleGenerateXML}
              disabled={isGenerating}
              className="flex items-center space-x-2"
            >
              <RefreshCw className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
              <span>Neu generieren</span>
            </Button>
            
            {xmlResult?.success && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownloadXML}
                className="flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Download</span>
              </Button>
            )}
          </div>
        </div>

        {isGenerating && (
          <div className="flex items-center justify-center py-8">
            <div className="flex flex-col items-center space-y-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="text-sm text-gray-600 dark:text-gray-300">
                XML wird generiert...
              </span>
            </div>
          </div>
        )}

        {xmlResult && !isGenerating && (
          <div className="space-y-4">
            {xmlResult.success ? (
              <div className="flex items-center space-x-2 text-green-600 dark:text-green-400">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">XML erfolgreich generiert</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
                <AlertTriangle className="w-5 h-5" />
                <span className="font-medium">XML-Generierung fehlgeschlagen</span>
              </div>
            )}

            {xmlResult.success && validationResult && (
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Validierung:
                  </span>
                  <div className="flex items-center space-x-2">
                    {validationResult.isValid ? (
                      <>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-green-600 dark:text-green-400">
                          Gültig
                        </span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="w-4 h-4 text-red-500" />
                        <span className="text-sm text-red-600 dark:text-red-400">
                          {validationResult.errors.length} Fehler
                        </span>
                      </>
                    )}
                  </div>
                </div>
                
                {xmlResult.xmlContent && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {xmlResult.xmlContent.split('\n').length} Zeilen, ~{Math.round(xmlResult.xmlContent.length / 1024)}KB
                  </div>
                )}
              </div>
            )}

            {xmlResult.error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-sm text-red-700 dark:text-red-300">
                  {xmlResult.error}
                </p>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Final Message */}
      {xmlResult?.success && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6 text-center">
          <CheckCircle className="w-12 h-12 text-green-600 dark:text-green-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-2">
            Stream erfolgreich konfiguriert!
          </h3>
          <p className="text-green-700 dark:text-green-300 mb-4">
            Ihre Streamworks-XML wurde erfolgreich generiert und kann nun in Streamworks importiert werden.
          </p>
          <div className="flex justify-center space-x-3">
            <Button onClick={handleDownloadXML} className="flex items-center space-x-2">
              <Download className="w-4 h-4" />
              <span>XML herunterladen</span>
            </Button>
          </div>
        </div>
      )}

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
        
        <div className="text-sm text-gray-500 dark:text-gray-400 flex items-center">
          Letzter Schritt - Konfiguration abgeschlossen
        </div>
      </div>
    </div>
  )
}

export default ReviewStep