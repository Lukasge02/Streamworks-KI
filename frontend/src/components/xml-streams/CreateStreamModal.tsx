/**
 * CreateStreamModal - Simple modal for creating new XML streams
 */
'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Wand2,
  MessageSquare,
  ArrowRight,
  Loader2,
} from 'lucide-react'

import { useCreateStream } from '@/hooks/useXMLStreams'
import { CreateStreamRequest } from '@/services/xmlStreamsApi'

interface CreateStreamModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

type CreationMode = 'wizard' | 'chat'

export const CreateStreamModal: React.FC<CreateStreamModalProps> = ({
  open,
  onOpenChange,
}) => {
  const router = useRouter()
  const createStream = useCreateStream()

  // Simplified form state
  const [formData, setFormData] = useState<{
    stream_name: string
    mode: CreationMode
  }>({
    stream_name: '',
    mode: 'wizard',
  })

  // Event handlers
  const handleInputChange = (field: keyof typeof formData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    if (!formData.stream_name.trim()) {
      return
    }

    try {
      const streamRequest: CreateStreamRequest = {
        stream_name: formData.stream_name.trim(),
        job_type: 'standard', // Default, will be set in wizard
        status: 'draft',
        wizard_data: {
          streamProperties: {
            streamName: formData.stream_name.trim(),
            contactPerson: {
              firstName: 'Ravel-Lukas',
              lastName: 'Geck',
              company: 'Arvato Systems',
              department: ''
            }
          }
        }
      }

      const newStream = await createStream.mutateAsync(streamRequest)
      
      // Close modal
      onOpenChange(false)
      resetForm()
      
      // Navigate to stream editor
      if (formData.mode === 'wizard') {
        router.push(`/xml/edit/${newStream.id}`)
      } else {
        // Navigate to chat mode
        router.push(`/xml/create/chat`)
      }
    } catch (error) {
      console.error('Error creating stream:', error)
    }
  }

  const resetForm = () => {
    setFormData({
      stream_name: '',
      mode: 'wizard',
    })
  }

  const handleClose = () => {
    onOpenChange(false)
    resetForm()
  }

  const canSubmit = formData.stream_name.trim() && !createStream.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Wand2 className="w-5 h-5 text-blue-600" />
            Neuen Stream erstellen
          </DialogTitle>
          <DialogDescription>
            Erstellen Sie einen neuen XML Stream. Wählen Sie zwischen dem geführten Wizard oder dem Chat-Modus.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Stream Name */}
          <div className="space-y-2">
            <Label htmlFor="stream_name">Stream Name *</Label>
            <Input
              id="stream_name"
              placeholder="Geben Sie einen aussagekräftigen Namen ein..."
              value={formData.stream_name}
              onChange={(e) => handleInputChange('stream_name', e.target.value)}
              autoFocus
            />
          </div>

          {/* Creation Mode Selection */}
          <div className="space-y-3">
            <Label>Erstellungsmodus auswählen</Label>
            <div className="grid grid-cols-1 gap-3">
              {/* Wizard Mode */}
              <div
                className={`
                  p-4 border-2 rounded-lg cursor-pointer transition-all
                  ${formData.mode === 'wizard' 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-950 ring-2 ring-blue-500/20' 
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }
                `}
                onClick={() => handleInputChange('mode', 'wizard')}
              >
                <div className="flex items-center gap-4">
                  <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-blue-500 text-white flex-shrink-0">
                    <Wand2 className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                      🧙‍♂️ Wizard
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Geführte Schritt-für-Schritt Konfiguration mit Formular
                    </p>
                  </div>
                  {formData.mode === 'wizard' && (
                    <div className="flex items-center justify-center w-6 h-6 bg-blue-500 rounded-full flex-shrink-0">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>

              {/* Chat Mode */}
              <div
                className={`
                  p-4 border-2 rounded-lg cursor-pointer transition-all
                  ${formData.mode === 'chat'
                    ? 'border-green-500 bg-green-50 dark:bg-green-950 ring-2 ring-green-500/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }
                `}
                onClick={() => handleInputChange('mode', 'chat')}
              >
                <div className="flex items-center gap-4">
                  <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-green-500 text-white flex-shrink-0">
                    <MessageSquare className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                      💬 Chat-Modus
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      KI-gestützte Konversation mit natürlicher Sprache
                    </p>
                  </div>
                  {formData.mode === 'chat' && (
                    <div className="flex items-center justify-center w-6 h-6 bg-green-500 rounded-full flex-shrink-0">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={createStream.isPending}>
            Abbrechen
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={!canSubmit}
          >
            {createStream.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Erstellen...
              </>
            ) : (
              <>
                Stream erstellen
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default CreateStreamModal