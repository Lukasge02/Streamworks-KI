'use client'

import { useState, useEffect, useCallback } from 'react'
import { 
  Settings, MessageCircle, FileText, Play, Download, 
  Save, RefreshCw, CheckCircle, AlertTriangle, Code,
  Layers, Monitor, Split, Maximize2, Copy, Zap
} from 'lucide-react'
import Editor from '@monaco-editor/react'
import { StreamForm } from './StreamForm'
import { StreamChatInput } from './StreamChatInput'

interface EnterpriseStreamBuilderProps {
  className?: string
}

interface StreamData {
  stream_name: string
  description: string
  jobs: Array<{
    type: string
    name: string
    [key: string]: any
  }>
  schedule?: any
  dependencies?: any[]
}

export function EnterpriseStreamBuilder({ className }: EnterpriseStreamBuilderProps) {
  const [activeInputMode, setActiveInputMode] = useState<'form' | 'chat'>('form')
  const [xmlContent, setXmlContent] = useState('')
  const [streamData, setStreamData] = useState<StreamData | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [lastGenerated, setLastGenerated] = useState<Date | null>(null)
  const [editorHeight, setEditorHeight] = useState('100%')
  const [isFullscreen, setIsFullscreen] = useState(false)

  // Mock XML generation function - replace with actual API call
  const generateXML = useCallback(async (data: StreamData) => {
    setIsGenerating(true)
    try {
      // Simulate API call to generate XML
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
      // Fallback to mock XML if API fails
      return generateMockXML(data)
    } finally {
      setIsGenerating(false)
    }
  }, [])

  // Generate mock XML based on our analyzed examples
  const generateMockXML = (data: StreamData): string => {
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19)
    return `<?xml version="1.0" encoding="utf-8"?>
<ExportableStream>
  <Stream>
    <StreamName>${data.stream_name}</StreamName>
    <StreamDocumentation><![CDATA[${data.description}]]></StreamDocumentation>
    <AgentDetail>gtasswvk05445</AgentDetail>
    <AccountNoId />
    <CalendarId />
    <StreamType>Normal</StreamType>
    <MaxStreamRuns>5</MaxStreamRuns>
    <ShortDescription><![CDATA[${data.description}]]></ShortDescription>
    <SchedulingRequiredFlag>False</SchedulingRequiredFlag>
    <Jobs>
      <!-- StartPoint -->
      <Job>
        <JobName>StartPoint</JobName>
        <JobDocumentation IsNull="True" />
        <ShortDescription><![CDATA[Start Point for the Stream]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>StartPoint</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>None</JobType>
        <DisplayOrder>1</DisplayOrder>
        <TemplateType>Normal</TemplateType>
        <CoordinateX>0</CoordinateX>
        <CoordinateY>0</CoordinateY>
        <JobInternalSuccessors>
          <JobInternalSuccessor>
            <JobName>${data.jobs[0]?.name || 'MainJob'}</JobName>
            <EdgeEndPosition>2</EdgeEndPosition>
            <EdgeStartPosition>6</EdgeStartPosition>
          </JobInternalSuccessor>
        </JobInternalSuccessors>
      </Job>
      
      <!-- Main Job -->
      <Job>
        <JobName>${data.jobs[0]?.name || 'MainJob'}</JobName>
        <JobDocumentation IsNull="True" />
        <ShortDescription><![CDATA[${data.jobs[0]?.description || 'Main Job'}]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Job</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>${data.jobs[0]?.type === 'powershell' ? 'Windows' : data.jobs[0]?.type === 'sap' ? 'SAP' : 'Windows'}</JobType>
        <DisplayOrder>2</DisplayOrder>
        <TemplateType>${data.jobs[0]?.type === 'filetransfer' ? 'FileTransfer' : 'Normal'}</TemplateType>
        <CoordinateX>0</CoordinateX>
        <CoordinateY>208</CoordinateY>
        ${data.jobs[0]?.script || data.jobs[0]?.report ? `<MainScript><![CDATA[${data.jobs[0].script || data.jobs[0].report}]]></MainScript>` : '<MainScript IsNull="True" />'}
        <JobInternalSuccessors>
          <JobInternalSuccessor>
            <JobName>EndPoint</JobName>
            <EdgeEndPosition>2</EdgeEndPosition>
            <EdgeStartPosition>6</EdgeStartPosition>
          </JobInternalSuccessor>
        </JobInternalSuccessors>
      </Job>
      
      <!-- EndPoint -->
      <Job>
        <JobName>EndPoint</JobName>
        <JobDocumentation IsNull="True" />
        <ShortDescription><![CDATA[End Point for the Stream]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Endpoint</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>None</JobType>
        <DisplayOrder>3</DisplayOrder>
        <TemplateType>Normal</TemplateType>
        <CoordinateX>0</CoordinateX>
        <CoordinateY>416</CoordinateY>
        <JobInternalSuccessors />
      </Job>
    </Jobs>
    
    <StreamContactPersons>
      <StreamContactPerson>
        <FirstName>System</FirstName>
        <LastName>Generated</LastName>
        <CompanyName>StreamWorks Self-Service</CompanyName>
        <ContactType>None</ContactType>
        <HierarchyLevelCd>1</HierarchyLevelCd>
      </StreamContactPerson>
    </StreamContactPersons>
    
    <StreamVersionDetail>
      <StreamVersionType>Current</StreamVersionType>
      <StreamVersion>1.0</StreamVersion>
      <DeploymentDateTime>${timestamp}</DeploymentDateTime>
      <DeployAsActive>True</DeployAsActive>
      <AutoDeploymentStatus>Finished</AutoDeploymentStatus>
    </StreamVersionDetail>
    
    <StatusFlag>True</StatusFlag>
  </Stream>
</ExportableStream>`
  }

  // Auto-generate XML when stream data changes
  useEffect(() => {
    if (streamData) {
      generateXML(streamData).then(xml => {
        setXmlContent(xml)
        setLastGenerated(new Date())
      })
    }
  }, [streamData, generateXML])

  const handleStreamGenerated = (data: any) => {
    setStreamData(data)
  }

  const downloadXML = () => {
    if (!xmlContent || !streamData) return
    
    const blob = new Blob([xmlContent], { type: 'text/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${streamData.stream_name || 'stream'}.xml`
    a.click()
    URL.revokeObjectURL(url)
  }

  const copyXML = () => {
    navigator.clipboard.writeText(xmlContent)
  }

  const validateXML = () => {
    // Simple XML validation - could be enhanced
    try {
      const parser = new DOMParser()
      const doc = parser.parseFromString(xmlContent, 'text/xml')
      const errorNode = doc.querySelector('parsererror')
      return !errorNode
    } catch {
      return false
    }
  }

  const isValidXML = validateXML()

  return (
    <div className={`flex h-full bg-gray-50 dark:bg-gray-900 ${className}`}>
      {/* Left Panel - Input Methods */}
      <div className={`${isFullscreen ? 'hidden' : 'w-1/2'} border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col`}>
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Enterprise Stream Builder
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Erstellen Sie StreamWorks-Konfigurationen mit professionellen Tools
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                Enterprise Ready
              </div>
              <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                Live Preview
              </div>
            </div>
          </div>
        </div>

        {/* Input Mode Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700 px-6">
          <nav className="flex space-x-8">
            {[
              { id: 'form', label: 'Visual Builder', icon: Settings },
              { id: 'chat', label: 'AI Assistant', icon: MessageCircle },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveInputMode(id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeInputMode === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Icon className="w-4 h-4" />
                  <span>{label}</span>
                </div>
              </button>
            ))}
          </nav>
        </div>

        {/* Input Content */}
        <div className="flex-1 overflow-auto">
          {activeInputMode === 'form' ? (
            <div className="p-6">
              <StreamForm onStreamGenerated={handleStreamGenerated} />
            </div>
          ) : (
            <div className="p-6">
              <StreamChatInput onStreamGenerated={handleStreamGenerated} />
            </div>
          )}
        </div>
      </div>

      {/* Right Panel - XML Editor */}
      <div className={`${isFullscreen ? 'w-full' : 'w-1/2'} bg-gray-900 flex flex-col`}>
        {/* Editor Header */}
        <div className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Code className="w-5 h-5 text-gray-400" />
              <div>
                <h3 className="text-white font-medium">StreamWorks XML</h3>
                <p className="text-gray-400 text-sm">
                  Live Preview • {xmlContent.length.toLocaleString()} Zeichen
                  {lastGenerated && (
                    <span className="ml-2">
                      • Aktualisiert {lastGenerated.toLocaleTimeString()}
                    </span>
                  )}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Status Indicator */}
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
                isGenerating 
                  ? 'bg-yellow-900 text-yellow-200' 
                  : isValidXML 
                  ? 'bg-green-900 text-green-200'
                  : 'bg-red-900 text-red-200'
              }`}>
                {isGenerating ? (
                  <RefreshCw className="w-3 h-3 animate-spin" />
                ) : isValidXML ? (
                  <CheckCircle className="w-3 h-3" />
                ) : (
                  <AlertTriangle className="w-3 h-3" />
                )}
                <span>
                  {isGenerating ? 'Generierung...' : isValidXML ? 'Valid' : 'Fehler'}
                </span>
              </div>

              {/* Action Buttons */}
              <button
                onClick={copyXML}
                disabled={!xmlContent}
                className="p-2 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                title="XML kopieren"
              >
                <Copy className="w-4 h-4" />
              </button>
              
              <button
                onClick={downloadXML}
                disabled={!xmlContent || !streamData}
                className="p-2 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                title="XML herunterladen"
              >
                <Download className="w-4 h-4" />
              </button>

              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-2 text-gray-400 hover:text-white"
                title="Vollbild umschalten"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Monaco Editor */}
        <div className="flex-1 relative">
          <Editor
            height="100%"
            defaultLanguage="xml"
            value={xmlContent}
            theme="vs-dark"
            options={{
              readOnly: true,
              minimap: { enabled: true },
              fontSize: 14,
              lineNumbers: 'on',
              wordWrap: 'on',
              folding: true,
              bracketPairColorization: { enabled: true },
              renderWhitespace: 'selection',
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
            loading={
              <div className="flex items-center justify-center h-full text-gray-400">
                <div className="text-center">
                  <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
                  <p>Editor wird geladen...</p>
                </div>
              </div>
            }
          />
          
          {/* Overlay for empty state */}
          {!xmlContent && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-90">
              <div className="text-center text-gray-400 max-w-md">
                <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <h3 className="text-xl font-medium mb-2">XML Preview</h3>
                <p className="mb-4">
                  Erstellen Sie einen Stream mit dem {activeInputMode === 'form' ? 'Visual Builder' : 'AI Assistant'} 
                  links, um hier die Live-Vorschau zu sehen.
                </p>
                <div className="flex items-center justify-center space-x-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <Zap className="w-4 h-4 text-green-400" />
                    <span>Live Updates</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Monitor className="w-4 h-4 text-blue-400" />
                    <span>Syntax Highlighting</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}