/**
 * XML Generation Hook
 * Clean API integration for XML generation
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import { useXMLChatStore } from '../store/xmlChatStore'
import { XMLGenerationRequest, XMLGenerationResponse } from '../types'

// ================================
// API FUNCTIONS
// ================================

async function generateXMLFromConversation(request: XMLGenerationRequest): Promise<XMLGenerationResponse> {
  const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

  const response = await fetch(`${API_BASE_URL}/api/chat-xml/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      conversation: request.conversation,
      job_type: request.jobType || 'STANDARD',
      parameters: request.parameters || {}
    })
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Generation failed' }))
    throw new Error(error.error || 'Failed to generate XML')
  }

  const data = await response.json()

  return {
    success: true,
    xml: data.xml,
    metadata: {
      jobType: data.job_type || request.jobType || 'STANDARD',
      parameters: data.parameters || {},
      generationTime: data.generation_time || 0
    }
  }
}

function validateXML(xml: string) {
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(xml, 'application/xml')
    const errors = doc.getElementsByTagName('parsererror')

    return {
      valid: errors.length === 0,
      errors: Array.from(errors).map(error => error.textContent || 'Parse error'),
      warnings: []
    }
  } catch (error) {
    return {
      valid: false,
      errors: ['Invalid XML format'],
      warnings: []
    }
  }
}

// ================================
// CUSTOM HOOKS
// ================================

export function useXMLGeneration() {
  const queryClient = useQueryClient()
  const { setGenerationStatus } = useXMLChatStore()

  const mutation = useMutation({
    mutationFn: generateXMLFromConversation,
    onMutate: () => {
      setGenerationStatus('generating')
    },
    onSuccess: (data) => {
      setGenerationStatus('success')

      // Validate the generated XML
      const validation = validateXML(data.xml || '')
      if (!validation.valid) {
        console.warn('Generated XML has validation errors:', validation.errors)
      }
    },
    onError: (error) => {
      setGenerationStatus('error')
      console.error('XML generation error:', error)
      toast.error(`Generation failed: ${error.message}`)
    }
  })

  return {
    generateXMLFromChat: async (conversation: string, options?: Partial<XMLGenerationRequest>) => {
      return mutation.mutateAsync({
        conversation,
        jobType: options?.jobType || 'STANDARD',
        parameters: options?.parameters || {}
      })
    },
    isLoading: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset
  }
}

export function useXMLValidation() {
  return {
    validateXML,
    isValidXML: (xml: string) => validateXML(xml).valid
  }
}

// ================================
// UTILITY HOOKS
// ================================

export function useXMLExport() {
  const downloadXML = (xml: string, filename?: string) => {
    try {
      const blob = new Blob([xml], { type: 'application/xml' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename || `xml-config-${new Date().toISOString().split('T')[0]}.xml`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      return true
    } catch (error) {
      console.error('Download error:', error)
      return false
    }
  }

  const copyToClipboard = async (xml: string) => {
    try {
      await navigator.clipboard.writeText(xml)
      return true
    } catch (error) {
      console.error('Copy error:', error)
      return false
    }
  }

  const shareXML = async (xml: string, title?: string) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title || 'Generated XML Configuration',
          text: xml,
          files: [new File([xml], 'config.xml', { type: 'application/xml' })]
        })
        return true
      } catch (error) {
        console.error('Share error:', error)
        return false
      }
    }
    return false
  }

  return {
    downloadXML,
    copyToClipboard,
    shareXML,
    canShare: !!navigator.share
  }
}

// ================================
// MOCK DATA FOR DEVELOPMENT
// ================================

export const mockXMLGeneration = async (conversation: string): Promise<XMLGenerationResponse> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000))

  const mockXML = `<?xml version="1.0" encoding="UTF-8"?>
<job-definition xmlns="http://streamworks.example.com/job" version="1.0">
  <metadata>
    <name>Data Processing Job</name>
    <description>Generated from conversation: ${conversation.substring(0, 50)}...</description>
    <created>${new Date().toISOString()}</created>
    <version>1.0</version>
  </metadata>

  <parameters>
    <input-source type="file">
      <path>/data/input</path>
      <format>csv</format>
    </input-source>

    <output-target type="database">
      <connection>postgresql://localhost:5432/data</connection>
      <table>processed_data</table>
    </output-target>

    <processing>
      <transformation>normalize</transformation>
      <validation enabled="true" />
      <batch-size>1000</batch-size>
    </processing>
  </parameters>

  <schedule>
    <frequency>daily</frequency>
    <time>02:00</time>
    <timezone>UTC</timezone>
  </schedule>

  <notifications>
    <email>admin@example.com</email>
    <on-success>true</on-success>
    <on-failure>true</on-failure>
  </notifications>
</job-definition>`

  return {
    success: true,
    xml: mockXML,
    metadata: {
      jobType: 'STANDARD',
      parameters: {
        inputType: 'file',
        outputType: 'database',
        schedule: 'daily'
      },
      generationTime: 2000
    }
  }
}
