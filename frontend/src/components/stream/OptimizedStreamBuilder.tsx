'use client'

import { useState, useCallback, useMemo, Suspense } from 'react'
import { 
  Settings, MessageCircle, Download, Copy, Maximize2,
  Code, CheckCircle, RefreshCw, FileText, Save, Play,
  Monitor, Split, Zap, AlertTriangle
} from 'lucide-react'
import { DynamicEditor, StreamForm, StreamChatInput } from './LazyStreamBuilder'

interface OptimizedStreamBuilderProps {
  className?: string
  mode?: 'basic' | 'advanced' | 'enterprise'
  onStreamGenerated?: (data: any) => void
}

interface StreamData {
  stream_name: string
  description: string
  agent_detail?: string
  calendar_id?: string
  max_stream_runs?: number
  jobs: Array<{
    job_name: string
    type: 'SAP' | 'Windows' | 'Unix'
    main_script?: string
    system?: string
    report?: string
    variant?: string
    user?: string
    [key: string]: any
  }>
  schedule?: {
    type: 'daily' | 'interval' | 'once'
    startTime: string
    interval?: string
    weekends: boolean
  }
  dependencies?: any[]
}

export function OptimizedStreamBuilder({ 
  className = '', 
  mode = 'basic',
  onStreamGenerated 
}: OptimizedStreamBuilderProps) {
  const [activeInputMode, setActiveInputMode] = useState<'form' | 'chat'>('form')
  const [xmlContent, setXmlContent] = useState('')
  const [streamData, setStreamData] = useState<StreamData | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [lastGenerated, setLastGenerated] = useState<Date | null>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)

  // Memoized XML generation function to prevent unnecessary re-renders
  const generateXML = useCallback(async (data: StreamData) => {
    setIsGenerating(true)
    try {
      const response = await fetch('/api/simple-streams/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      
      if (response.ok) {
        const result = await response.json()
        return result.xml || generateMockXML(data)
      } else {
        return generateMockXML(data)
      }
    } catch (error) {
      console.error('XML generation failed:', error)
      return generateMockXML(data)
    } finally {
      setIsGenerating(false)
    }
  }, [])

  // Optimized mock XML generation
  const generateMockXML = useCallback((data: StreamData): string => {
    const jobs = data.jobs.map(job => `
    <job>
      <name>${job.job_name}</name>
      <type>${job.type}</type>
      ${job.system ? `<system>${job.system}</system>` : ''}
      ${job.report ? `<report>${job.report}</report>` : ''}
      ${job.variant ? `<variant>${job.variant}</variant>` : ''}
      ${job.main_script ? `<script>${job.main_script}</script>` : ''}
    </job>`).join('')

    return `<?xml version="1.0" encoding="UTF-8"?>
<stream>
  <metadata>
    <name>${data.stream_name}</name>
    <description>${data.description}</description>
    ${data.agent_detail ? `<agent>${data.agent_detail}</agent>` : ''}
    ${data.calendar_id ? `<calendar>${data.calendar_id}</calendar>` : ''}
    ${data.max_stream_runs ? `<max_runs>${data.max_stream_runs}</max_runs>` : ''}
    <generated>${new Date().toISOString()}</generated>
  </metadata>
  <jobs>${jobs}
  </jobs>
  ${data.schedule ? `
  <schedule>
    <type>${data.schedule.type}</type>
    <start_time>${data.schedule.startTime}</start_time>
    ${data.schedule.interval ? `<interval>${data.schedule.interval}</interval>` : ''}
    <weekends>${data.schedule.weekends}</weekends>
  </schedule>` : ''}
</stream>`
  }, [])

  const handleStreamGenerated = useCallback(async (data: any) => {
    setStreamData(data)
    const xml = await generateXML(data)
    setXmlContent(xml)
    setLastGenerated(new Date())
    onStreamGenerated?.(data)
  }, [generateXML, onStreamGenerated])

  const copyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(xmlContent)
      // Could add toast notification here
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }, [xmlContent])

  const downloadXML = useCallback(() => {
    const blob = new Blob([xmlContent], { type: 'application/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${streamData?.stream_name || 'stream'}.xml`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [xmlContent, streamData?.stream_name])

  // Memoized status display
  const statusDisplay = useMemo(() => {
    if (isGenerating) {
      return (
        <div className="flex items-center space-x-2 text-blue-600">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span className="text-sm">Generiere XML...</span>
        </div>
      )
    }
    
    if (lastGenerated) {
      return (
        <div className="flex items-center space-x-2 text-green-600">
          <CheckCircle className="h-4 w-4" />
          <span className="text-sm">
            Generiert um {lastGenerated.toLocaleTimeString()}
          </span>
        </div>
      )
    }
    
    return null
  }, [isGenerating, lastGenerated])

  const containerClasses = `flex flex-col h-full bg-white dark:bg-gray-900 ${isFullscreen ? 'fixed inset-0 z-50' : ''} ${className}`

  return (
    <div className={containerClasses}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            StreamWorks Builder
            {mode !== 'basic' && (
              <span className="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </span>
            )}
          </h2>
          {statusDisplay}
        </div>
        
        <div className="flex items-center space-x-2">
          {xmlContent && (
            <>
              <button
                onClick={copyToClipboard}
                className="p-2 text-gray-600 hover:text-blue-600 transition-colors"
                title="XML kopieren"
              >
                <Copy className="h-4 w-4" />
              </button>
              <button
                onClick={downloadXML}
                className="p-2 text-gray-600 hover:text-green-600 transition-colors"
                title="XML herunterladen"
              >
                <Download className="h-4 w-4" />
              </button>
            </>
          )}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 text-gray-600 hover:text-gray-900 transition-colors"
            title="Vollbild umschalten"
          >
            <Maximize2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Input */}
        <div className="flex-1 flex flex-col border-r border-gray-200 dark:border-gray-700">
          {/* Input Mode Toggle */}
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveInputMode('form')}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeInputMode === 'form'
                  ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-500'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Settings className="inline h-4 w-4 mr-2" />
              Formular
            </button>
            <button
              onClick={() => setActiveInputMode('chat')}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeInputMode === 'chat'
                  ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-500'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <MessageCircle className="inline h-4 w-4 mr-2" />
              Chat
            </button>
          </div>

          {/* Input Content */}
          <div className="flex-1 p-4 overflow-auto">
            <Suspense fallback={
              <div className="flex items-center justify-center h-40">
                <RefreshCw className="h-6 w-6 animate-spin text-blue-600" />
              </div>
            }>
              {activeInputMode === 'form' ? (
                <StreamForm onStreamGenerated={handleStreamGenerated} />
              ) : (
                <StreamChatInput onStreamGenerated={handleStreamGenerated} />
              )}
            </Suspense>
          </div>
        </div>

        {/* Right Panel - XML Editor */}
        <div className="flex-1 flex flex-col">
          {/* Editor Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center space-x-2">
              <Code className="h-4 w-4 text-gray-600" />
              <span className="font-medium text-gray-900 dark:text-white">XML Stream</span>
            </div>
            
            {streamData && (
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {streamData.stream_name}
              </div>
            )}
          </div>

          {/* Editor Content */}
          <div className="flex-1 relative">
            <Suspense fallback={
              <div className="flex items-center justify-center h-full bg-gray-50 dark:bg-gray-800">
                <div className="text-center">
                  <RefreshCw className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">XML-Editor wird geladen...</p>
                </div>
              </div>
            }>
              <DynamicEditor
                height="100%"
                language="xml"
                theme="vs-dark"
                value={xmlContent}
                onChange={(value) => setXmlContent(value || '')}
                options={{
                  readOnly: false,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 14,
                  wordWrap: 'on',
                  lineNumbers: 'on',
                  folding: true,
                  automaticLayout: true,
                }}
              />
            </Suspense>
            
            {!xmlContent && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-800 text-gray-500">
                <div className="text-center">
                  <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p className="text-sm">
                    Erstelle einen Stream über das Formular oder den Chat, um XML zu generieren
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}