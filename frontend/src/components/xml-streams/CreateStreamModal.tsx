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
import { EnhancedButton } from '@/components/ui/EnhancedButton'
import { EnhancedInput } from '@/components/ui/EnhancedInput'
import {
  Wand2,
  ArrowRight,
  Loader2,
} from 'lucide-react'

import { useCreateStream } from '@/hooks/useXMLStreams'
import { CreateStreamRequest } from '@/services/xmlStreamsApi'

interface CreateStreamModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export const CreateStreamModal: React.FC<CreateStreamModalProps> = ({
  open,
  onOpenChange,
}) => {
  const router = useRouter()
  const createStream = useCreateStream()

  // Simplified form state
  const [streamName, setStreamName] = useState('')

  const handleSubmit = async () => {
    if (!streamName.trim()) {
      return
    }

    try {
      const streamRequest: CreateStreamRequest = {
        stream_name: streamName.trim(),
        job_type: 'standard', // Default, will be set in wizard
        status: 'draft',
        wizard_data: {
          streamProperties: {
            streamName: streamName.trim(),
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

      // Navigate directly to new XML Chat Generator
      router.push('/xml/chat')
    } catch (error) {
      console.error('Error creating stream:', error)
    }
  }

  const resetForm = () => {
    setStreamName('')
  }

  const handleClose = () => {
    onOpenChange(false)
    resetForm()
  }

  const canSubmit = streamName.trim() && !createStream.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Wand2 className="w-5 h-5 text-blue-600" />
            Neuen Stream erstellen
          </DialogTitle>
          <DialogDescription>
            Erstellen Sie einen neuen XML Stream mit dem geführten Wizard.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Stream Name */}
          <div className="space-y-2">
            <EnhancedInput
              label="Stream Name *"
              placeholder="Geben Sie einen aussagekräftigen Namen ein..."
              value={streamName}
              onChange={(e) => setStreamName(e.target.value)}
              validation={[
                { test: (v) => v.trim().length >= 3, message: 'Mindestens 3 Zeichen erforderlich' },
                { test: (v) => v.trim().length <= 50, message: 'Maximal 50 Zeichen erlaubt' }
              ]}
              leftIcon={<Wand2 className="h-4 w-4" />}
              description="Eindeutiger Name für den XML-Stream"
              autoFocus
            />
          </div>
        </div>

        <DialogFooter>
          <EnhancedButton
            variant="secondary"
            onClick={handleClose}
            disabled={createStream.isPending}
          >
            Abbrechen
          </EnhancedButton>
          <EnhancedButton
            variant="primary"
            onClick={handleSubmit}
            disabled={!canSubmit}
            loading={createStream.isPending}
            icon={createStream.isPending ? <Loader2 className="w-4 h-4" /> : <ArrowRight className="w-4 h-4" />}
          >
            {createStream.isPending ? 'Erstellen...' : 'Stream erstellen'}
          </EnhancedButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default CreateStreamModal