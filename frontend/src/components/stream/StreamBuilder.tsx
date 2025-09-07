'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { 
  Settings, MessageCircle, Download, Copy, Maximize2,
  Code, CheckCircle, RefreshCw, Database, Cog, Clock,
  Server, Layers, PlayCircle, Bell, Shield, FolderOpen,
  AlertTriangle, Mail, Link, FileText
} from 'lucide-react'
import Editor from '@monaco-editor/react'

interface StreamBuilderProps {
  className?: string
}

interface StreamData {
  stream_name: string
  description: string
  agent_detail: string
  calendar_id: string
  max_stream_runs: number
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

export function StreamBuilder({ className }: StreamBuilderProps) {
  const [activeMode, setActiveMode] = useState<'form' | 'chat'>('form')
  const [xmlContent, setXmlContent] = useState('')
  const [streamData, setStreamData] = useState<StreamData | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [leftPanelWidth, setLeftPanelWidth] = useState(50) // Prozent
  const [isResizing, setIsResizing] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const editorRef = useRef<any>(null)

  // Form state
  const [formData, setFormData] = useState({
    // Stream-Basis
    stream_name: '',
    description: '',
    short_description: '',
    agent_detail: 'gtasswvk05445',
    calendar_id: 'Default Calendar',
    max_stream_runs: 5,
    stream_type: 'Normal',
    severity_group: '',
    
    // Jobs
    job_name: 'MainJob',
    job_type: 'SAP' as 'SAP' | 'Windows' | 'Unix',
    main_script: '',
    job_short_name: '',
    
    // SAP-specific
    sap_system: '',
    batch_user: '',
    report: '',
    variant: '',
    sap_parameters: '',
    selection_options: '',
    
    // File Transfer
    source_path: '',
    target_path: '',
    file_pattern: '',
    
    // RunProps-Defaults & Timing
    schedule_type: 'daily',
    start_time: '06:00',
    interval: '00:15',
    weekends: false,
    max_job_duration: '',
    latest_start_time: '',
    
    // Storage & Logging
    runtime_data_storage_days: '',
    central_job_log_flag: false,
    max_job_log_size: '',
    
    // Notifications & Error Handling
    notification_required: false,
    notification_email: '',
    report_to_incident_management: false,
    
    // Dependencies
    predecessor_job: '',
    external_dependencies: ''
  })

  const generateXML = useCallback(async (data: StreamData) => {
    setIsGenerating(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      const mainJob = data.jobs[0] || { job_name: 'MainJob', type: 'SAP' }
      
      const xml = `<?xml version="1.0" encoding="utf-8"?>
<ExportableStream>
  <Stream>
    <StreamName>${data.stream_name}</StreamName>
    <StreamDocumentation><![CDATA[${data.description}]]></StreamDocumentation>
    <AgentDetail>${data.agent_detail}</AgentDetail>
    <AccountNoId />
    <CalendarId>${data.calendar_id}</CalendarId>
    <StreamType>Normal</StreamType>
    <MaxStreamRuns>${data.max_stream_runs}</MaxStreamRuns>
    <ShortDescription><![CDATA[${data.description}]]></ShortDescription>
    <SchedulingRequiredFlag>True</SchedulingRequiredFlag>
    <ScheduleRuleObject />
    <RuntimeDataStorageDays IsNull="True" />
    <RuntimeDataStorageDaySource IsNull="True" />
    <StreamRunDeletionSource IsNull="True" />
    <StreamRunDeletionType>None</StreamRunDeletionType>
    <StreamRunDeletionTime IsNull="True" />
    <StreamRunDeletionDays IsNull="True" />
    <StreamRunDeletionDayType IsNull="True" />
    <DeletionTimeTimeZoneId />
    <DeletionTimeValidFlag IsNull="True" />
    <DeletionTimeValidSource IsNull="True" />
    <StreamRunTimeStatisticsDays IsNull="True" />
    <AvgRunTimeCalcInDays>0</AvgRunTimeCalcInDays>
    <SeverityGroup />
    <MaxStreamRunDuration IsNull="True" />
    <MinStreamRunDuration IsNull="True" />
    <CentralJobLogAreaFlag IsNull="True" />
    <CentralJobLogSource IsNull="True" />
    <CentralJobLogStorageDays IsNull="True" />
    <AgentJobLogStorageDays IsNull="True" />
    <AgentJobLogStorageDaySource IsNull="True" />
    <StreamRunInterval IsNull="True" />
    <MaxJobLogSize IsNull="True" />
    <ReorgType IsNull="True" />
    <ExternalJobScriptRequired IsNull="True" />
    <KeepPreparedRuns IsNull="True" />
    <InteractivePslFlag>False</InteractivePslFlag>
    <ConcurrentPlanDatesEnabled>False</ConcurrentPlanDatesEnabled>
    <UncatExclusion IsNull="True" />
    <Jobs>
      <Job>
        <JobName>StartPoint</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[Start Point for the Stream]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>StartPoint</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>None</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        <MainScript IsNull="True" />
        <DisplayOrder>1</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>Normal</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>0</CoordinateX>
        <CoordinateY>0</CoordinateY>
        <JobInternalSuccessors>
          <JobInternalSuccessor>
            <JobName>${mainJob.job_name}</JobName>
          </JobInternalSuccessor>
        </JobInternalSuccessors>
      </Job>
      <Job>
        <JobName>${mainJob.job_name}</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[${data.description}]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Job</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>${mainJob.type}</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        ${mainJob.main_script ? `<MainScript><![CDATA[${mainJob.main_script}]]></MainScript>` : '<MainScript IsNull="True" />'}
        <DisplayOrder>2</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>Normal</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>0</CoordinateX>
        <CoordinateY>200</CoordinateY>
        <JobInternalSuccessors>
          <JobInternalSuccessor>
            <JobName>EndPoint</JobName>
          </JobInternalSuccessor>
        </JobInternalSuccessors>
      </Job>
      <Job>
        <JobName>EndPoint</JobName>
        <JobDocumentation IsNull="True" />
        <JobNotificationRules />
        <LoginObject />
        <ShortDescription><![CDATA[End Point for the Stream]]></ShortDescription>
        <StatusFlag>True</StatusFlag>
        <JobCategory>Endpoint</JobCategory>
        <NormalJobFlag>True</NormalJobFlag>
        <JobType>None</JobType>
        <MinJobDuration IsNull="True" />
        <CentralJobLogStorageDays IsNull="True" />
        <ReportToIncidentManagementFlag IsNull="True" />
        <ExternalJobScriptRequired IsNull="True" />
        <MainScript IsNull="True" />
        <DisplayOrder>3</DisplayOrder>
        <JobShortName IsNull="True" />
        <TemplateType>Normal</TemplateType>
        <ControlFilePath IsNull="True" />
        <IsNotificationRequired>False</IsNotificationRequired>
        <CoordinateX>0</CoordinateX>
        <CoordinateY>400</CoordinateY>
      </Job>
    </Jobs>
    <StatusFlag>True</StatusFlag>
  </Stream>
</ExportableStream>`
      setXmlContent(xml)
    } finally {
      setIsGenerating(false)
    }
  }, [])

  // Auto-generate when form changes
  useEffect(() => {
    if (formData.stream_name.trim()) {
      // Generate main script based on job type
      let mainScript = ''
      if (formData.job_type === 'SAP' && formData.report) {
        mainScript = formData.report
        if (formData.variant) {
          mainScript += ` - Variant: ${formData.variant}`
        }
        if (formData.sap_system) {
          mainScript += ` (${formData.sap_system})`
        }
      } else if (formData.main_script) {
        mainScript = formData.main_script
      }
      
      const data: StreamData = {
        stream_name: formData.stream_name,
        description: formData.description || `${formData.job_type} Stream`,
        agent_detail: formData.agent_detail,
        calendar_id: formData.calendar_id,
        max_stream_runs: formData.max_stream_runs,
        jobs: [{
          job_name: formData.job_name,
          type: formData.job_type,
          main_script: mainScript,
          system: formData.sap_system,
          report: formData.report,
          variant: formData.variant,
          user: formData.batch_user
        }],
        schedule: {
          type: formData.schedule_type as 'daily' | 'interval' | 'once',
          startTime: formData.start_time,
          interval: formData.interval,
          weekends: formData.weekends
        }
      }
      setStreamData(data)
      generateXML(data)
    }
  }, [formData, generateXML])

  const downloadXML = () => {
    if (!xmlContent) return
    const blob = new Blob([xmlContent], { type: 'text/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${formData.stream_name || 'stream'}.xml`
    a.click()
    URL.revokeObjectURL(url)
  }

  const copyXML = () => {
    navigator.clipboard.writeText(xmlContent)
  }

  // Handle resizing
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsResizing(true)
  }, [])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing || !containerRef.current) return
    
    const containerRect = containerRef.current.getBoundingClientRect()
    const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100
    
    // Begrenzen zwischen 20% und 80%
    const clampedWidth = Math.min(Math.max(newLeftWidth, 20), 80)
    setLeftPanelWidth(clampedWidth)
  }, [isResizing])

  const handleMouseUp = useCallback(() => {
    setIsResizing(false)
  }, [])

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
        document.body.style.cursor = ''
        document.body.style.userSelect = ''
      }
    }
  }, [isResizing, handleMouseMove, handleMouseUp])

  // Force Monaco Editor resize when panel width changes
  useEffect(() => {
    if (editorRef.current) {
      // Small delay to ensure DOM has updated
      setTimeout(() => {
        editorRef.current.layout()
        editorRef.current.focus()
      }, 150)
    }
  }, [leftPanelWidth, isFullscreen, xmlContent])

  return (
    <div ref={containerRef} className={`flex bg-white ${className} relative`} style={{ height: '100vh', minHeight: '600px' }}>
      {/* Left Panel */}
      <div 
        className={`${isFullscreen ? 'hidden' : 'flex flex-col'} border-r border-gray-200`}
        style={{ 
          width: isFullscreen ? '0%' : `${leftPanelWidth}%`,
          height: '100%',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        
        {/* Mode Switcher */}
        <div className="px-6 py-6 border-b border-gray-100">
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveMode('form')}
              className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeMode === 'form' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              <Settings className="w-4 h-4" />
              <span>Formular</span>
            </button>
            <button
              onClick={() => setActiveMode('chat')}
              className={`flex-1 flex items-center justify-center space-x-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeMode === 'chat' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              <MessageCircle className="w-4 h-4" />
              <span>Chat</span>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 p-6" style={{ overflow: 'auto' }}>
          {activeMode === 'form' ? (
            <div className="space-y-8">
              
              {/* Stream-Basis Section */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                <div className="flex items-center space-x-2 mb-6">
                  <Database className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-semibold text-blue-900">Stream-Basis</h3>
                  <div className="flex-1 h-px bg-blue-200"></div>
                </div>
                
                <div className="grid grid-cols-1 gap-6">
                  {/* Stream Name */}
                  <div>
                    <label className="block text-sm font-medium text-blue-800 mb-2">
                      Stream Name *
                    </label>
                    <input
                      type="text"
                      value={formData.stream_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, stream_name: e.target.value }))}
                      placeholder="CUST-P-PA1-PUR-0013"
                      className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    />
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium text-blue-800 mb-2">
                      Ausführliche Beschreibung *
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="SAP Einkauf Report für tägliche Bestellungen - Verarbeitung von Lieferantendaten und Bestellpositionen (DMG MORI System)"
                      rows={3}
                      className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    />
                  </div>
                  
                  {/* Short Description */}
                  <div>
                    <label className="block text-sm font-medium text-blue-800 mb-2">
                      Kurzbeschreibung (für Übersicht)
                    </label>
                    <input
                      type="text"
                      value={formData.short_description}
                      onChange={(e) => setFormData(prev => ({ ...prev, short_description: e.target.value }))}
                      placeholder="Täglicher Einkauf Report"
                      className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {/* Agent Detail */}
                    <div>
                      <label className="block text-sm font-medium text-blue-800 mb-2">
                        Agent/Server
                      </label>
                      <select
                        value={formData.agent_detail}
                        onChange={(e) => setFormData(prev => ({ ...prev, agent_detail: e.target.value }))}
                        className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                      >
                        <option value="gtasswvk05445">gtasswvk05445 (Standard)</option>
                        <option value="gtasswvs01709">gtasswvs01709 (MiNo)</option>
                        <option value="TestAgent1">TestAgent1 (Demo)</option>
                      </select>
                    </div>
                    
                    {/* Max Stream Runs */}
                    <div>
                      <label className="block text-sm font-medium text-blue-800 mb-2">
                        Max. parallele Ausführungen
                      </label>
                      <select
                        value={formData.max_stream_runs}
                        onChange={(e) => setFormData(prev => ({ ...prev, max_stream_runs: parseInt(e.target.value) }))}
                        className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                      >
                        <option value={1}>1</option>
                        <option value={5}>5 (Standard)</option>
                        <option value={10}>10</option>
                        <option value={21}>21</option>
                      </select>
                    </div>
                  </div>

                  {/* Calendar ID */}
                  <div>
                    <label className="block text-sm font-medium text-blue-800 mb-2">
                      Kalender
                    </label>
                    <select
                      value={formData.calendar_id}
                      onChange={(e) => setFormData(prev => ({ ...prev, calendar_id: e.target.value }))}
                      className="w-full px-4 py-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    >
                      <option value="Default Calendar">Default Calendar</option>
                      <option value="GER-NRW">GER-NRW (Deutschland)</option>
                      <option value="Calendario7GG">Calendario7GG (7-Tage)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Jobs Section */}
              <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                <div className="flex items-center space-x-2 mb-6">
                  <Layers className="w-5 h-5 text-green-600" />
                  <h3 className="text-lg font-semibold text-green-900">Jobs</h3>
                  <div className="flex-1 h-px bg-green-200"></div>
                </div>

                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    {/* Job Name */}
                    <div>
                      <label className="block text-sm font-medium text-green-800 mb-2">
                        Job Name
                      </label>
                      <input
                        type="text"
                        value={formData.job_name}
                        onChange={(e) => setFormData(prev => ({ ...prev, job_name: e.target.value }))}
                        placeholder="MainJob"
                        className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                      />
                    </div>
                    
                    {/* Job Type */}
                    <div>
                      <label className="block text-sm font-medium text-green-800 mb-2">
                        Job Typ *
                      </label>
                      <select
                        value={formData.job_type}
                        onChange={(e) => setFormData(prev => ({ ...prev, job_type: e.target.value as 'SAP' | 'Windows' | 'Unix' }))}
                        className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                      >
                        <option value="SAP">SAP Report/Programm</option>
                        <option value="Windows">Windows Batch/PowerShell</option>
                        <option value="Unix">Unix/Linux Script</option>
                        <option value="FileTransfer">File Transfer</option>
                        <option value="Database">Datenbank Query</option>
                      </select>
                    </div>
                  </div>

                  {/* SAP Fields */}
                  {formData.job_type === 'SAP' && (
                    <>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-green-800 mb-2">
                            SAP System *
                          </label>
                          <select
                            value={formData.sap_system}
                            onChange={(e) => setFormData(prev => ({ ...prev, sap_system: e.target.value }))}
                            className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                          >
                            <option value="">System auswählen</option>
                            <option value="PA1_100">PA1_100 (DMG MORI)</option>
                            <option value="HP1">HP1 (Hettich)</option>
                            <option value="JPP">JPP (HVW)</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-green-800 mb-2">
                            Batch User *
                          </label>
                          <select
                            value={formData.batch_user}
                            onChange={(e) => setFormData(prev => ({ ...prev, batch_user: e.target.value }))}
                            className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                          >
                            <option value="">User auswählen</option>
                            <option value="BATCH_PUR">BATCH_PUR (Einkauf)</option>
                            <option value="HPH_BATCH">HPH_BATCH (Hettich)</option>
                            <option value="BATCOMM">BATCOMM (Allgemein)</option>
                          </select>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-green-800 mb-2">
                            Report/Programm *
                          </label>
                          <input
                            type="text"
                            value={formData.report}
                            onChange={(e) => setFormData(prev => ({ ...prev, report: e.target.value }))}
                            placeholder="RBDAGAIN, ZWM_TO_CREATE, RSNAST00"
                            className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-green-800 mb-2">
                            Variante (optional)
                          </label>
                          <input
                            type="text"
                            value={formData.variant}
                            onChange={(e) => setFormData(prev => ({ ...prev, variant: e.target.value }))}
                            placeholder="ZXY-UFA, 0100_NEST_DEL, DAILY_PUR"
                            className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                          />
                        </div>
                      </div>
                      
                      {/* SAP Selection Options */}
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Selektionskriterien (optional)
                        </label>
                        <textarea
                          value={formData.selection_options}
                          onChange={(e) => setFormData(prev => ({ ...prev, selection_options: e.target.value }))}
                          placeholder={`Beispiele:\nCompany Code: 1000-2000\nDate Range: SY-DATUM-30 TO SY-DATUM\nVendor: 100000-199999\nMaterial Type: ROH, HALB`}
                          rows={4}
                          className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white font-mono text-sm"
                        />
                      </div>
                      
                      {/* SAP Parameters */}
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Weitere Parameter (optional)
                        </label>
                        <textarea
                          value={formData.sap_parameters}
                          onChange={(e) => setFormData(prev => ({ ...prev, sap_parameters: e.target.value }))}
                          placeholder={`Beispiele:\nLAYOUT=X (für ALV-Listen)\nP_TEST='' (Testlauf deaktivieren)\nP_BUKRS=1000 (Buchungskreis)\nP_OUTPUT=PDF (Ausgabeformat)`}
                          rows={4}
                          className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white font-mono text-sm"
                        />
                      </div>
                    </>
                  )}

                  {/* Script Fields for Windows/Unix */}
                  {(formData.job_type === 'Windows' || formData.job_type === 'Unix') && (
                    <div>
                      <label className="block text-sm font-medium text-green-800 mb-2">
                        {formData.job_type === 'Windows' ? 'Batch/PowerShell Script' : 'Shell Script'} *
                      </label>
                      <textarea
                        value={formData.main_script}
                        onChange={(e) => setFormData(prev => ({ ...prev, main_script: e.target.value }))}
                        placeholder={formData.job_type === 'Windows' 
                          ? 'C:\\Scripts\\backup.bat\ndir C:\\temp\necho "Backup completed"' 
                          : '#!/bin/bash\n/opt/scripts/backup.sh\necho "Backup completed"\n/usr/bin/rsync -av /source/ /target/'
                        }
                        rows={4}
                        className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white font-mono text-sm"
                      />
                    </div>
                  )}
                  
                  {/* File Transfer Fields */}
                  {formData.job_type === 'FileTransfer' && (
                    <>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-green-800 mb-2">
                            Quell-Pfad *
                          </label>
                          <input
                            type="text"
                            value={formData.source_path}
                            onChange={(e) => setFormData(prev => ({ ...prev, source_path: e.target.value }))}
                            placeholder="/opt/data/exports/, C:\\Export\\, \\server\\share\\"
                            className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-green-800 mb-2">
                            Ziel-Pfad *
                          </label>
                          <input
                            type="text"
                            value={formData.target_path}
                            onChange={(e) => setFormData(prev => ({ ...prev, target_path: e.target.value }))}
                            placeholder="/backup/data/, D:\\Backup\\, ftp://server/folder/"
                            className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-green-800 mb-2">
                          Datei-Pattern (optional)
                        </label>
                        <input
                          type="text"
                          value={formData.file_pattern}
                          onChange={(e) => setFormData(prev => ({ ...prev, file_pattern: e.target.value }))}
                          placeholder="*.csv, *.xml, *_YYYYMMDD.txt, order_*.dat"
                          className="w-full px-4 py-3 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                        />
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Notification & Monitoring Section */}
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
                <div className="flex items-center space-x-2 mb-6">
                  <Bell className="w-5 h-5 text-amber-600" />
                  <h3 className="text-lg font-semibold text-amber-900">Benachrichtigungen & Überwachung</h3>
                  <div className="flex-1 h-px bg-amber-200"></div>
                </div>
                
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="notification_required"
                          checked={formData.notification_required}
                          onChange={(e) => setFormData(prev => ({ ...prev, notification_required: e.target.checked }))}
                          className="w-4 h-4 text-amber-600 border-amber-300 rounded focus:ring-amber-500"
                        />
                        <label htmlFor="notification_required" className="ml-2 text-sm text-amber-800">
                          E-Mail Benachrichtigungen aktivieren
                        </label>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="report_to_incident_management"
                          checked={formData.report_to_incident_management}
                          onChange={(e) => setFormData(prev => ({ ...prev, report_to_incident_management: e.target.checked }))}
                          className="w-4 h-4 text-amber-600 border-amber-300 rounded focus:ring-amber-500"
                        />
                        <label htmlFor="report_to_incident_management" className="ml-2 text-sm text-amber-800">
                          An Incident Management melden
                        </label>
                      </div>
                    </div>
                  </div>
                  
                  {formData.notification_required && (
                    <div>
                      <label className="block text-sm font-medium text-amber-800 mb-2">
                        E-Mail Adressen (kommagetrennt)
                      </label>
                      <input
                        type="text"
                        value={formData.notification_email}
                        onChange={(e) => setFormData(prev => ({ ...prev, notification_email: e.target.value }))}
                        placeholder="admin@company.com, team@company.com, manager@company.com"
                        className="w-full px-4 py-3 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-white"
                      />
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-amber-800 mb-2">
                        Max. Laufzeit (Minuten)
                      </label>
                      <input
                        type="number"
                        value={formData.max_job_duration}
                        onChange={(e) => setFormData(prev => ({ ...prev, max_job_duration: e.target.value }))}
                        placeholder="60"
                        min="1"
                        className="w-full px-4 py-3 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-white"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-amber-800 mb-2">
                        Späteste Startzeit
                      </label>
                      <input
                        type="time"
                        value={formData.latest_start_time}
                        onChange={(e) => setFormData(prev => ({ ...prev, latest_start_time: e.target.value }))}
                        className="w-full px-4 py-3 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-white"
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              {/* RunProps-Defaults Section */}
              <div className="bg-purple-50 border border-purple-200 rounded-xl p-6">
                <div className="flex items-center space-x-2 mb-6">
                  <Clock className="w-5 h-5 text-purple-600" />
                  <h3 className="text-lg font-semibold text-purple-900">Scheduling & Ausführung</h3>
                  <div className="flex-1 h-px bg-purple-200"></div>
                </div>
                
                <div className="space-y-6">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-purple-800 mb-2">
                        Ausführungstyp
                      </label>
                      <select
                        value={formData.schedule_type}
                        onChange={(e) => setFormData(prev => ({ ...prev, schedule_type: e.target.value }))}
                        className="w-full px-4 py-3 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
                      >
                        <option value="daily">Täglich</option>
                        <option value="interval">Intervall</option>
                        <option value="once">Einmalig</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-purple-800 mb-2">
                        Startzeit
                      </label>
                      <input
                        type="time"
                        value={formData.start_time}
                        onChange={(e) => setFormData(prev => ({ ...prev, start_time: e.target.value }))}
                        className="w-full px-4 py-3 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
                      />
                    </div>
                    
                    {formData.schedule_type === 'interval' && (
                      <div>
                        <label className="block text-sm font-medium text-purple-800 mb-2">
                          Intervall
                        </label>
                        <select
                          value={formData.interval}
                          onChange={(e) => setFormData(prev => ({ ...prev, interval: e.target.value }))}
                          className="w-full px-4 py-3 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
                        >
                          <option value="00:15">Alle 15 Minuten</option>
                          <option value="00:30">Alle 30 Minuten</option>
                          <option value="01:00">Stündlich</option>
                          <option value="02:00">Alle 2 Stunden</option>
                          <option value="04:00">Alle 4 Stunden</option>
                        </select>
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="weekends"
                        checked={formData.weekends}
                        onChange={(e) => setFormData(prev => ({ ...prev, weekends: e.target.checked }))}
                        className="w-4 h-4 text-purple-600 border-purple-300 rounded focus:ring-purple-500"
                      />
                      <label htmlFor="weekends" className="ml-2 text-sm text-purple-800">
                        Am Wochenende ausführen
                      </label>
                    </div>
                    
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="central_job_log"
                        checked={formData.central_job_log_flag}
                        onChange={(e) => setFormData(prev => ({ ...prev, central_job_log_flag: e.target.checked }))}
                        className="w-4 h-4 text-purple-600 border-purple-300 rounded focus:ring-purple-500"
                      />
                      <label htmlFor="central_job_log" className="ml-2 text-sm text-purple-800">
                        Zentrales Job-Log aktivieren
                      </label>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Storage & Dependencies Section */}
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
                <div className="flex items-center space-x-2 mb-6">
                  <FolderOpen className="w-5 h-5 text-gray-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Storage & Abhängigkeiten</h3>
                  <div className="flex-1 h-px bg-gray-200"></div>
                </div>
                
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-800 mb-2">
                        Runtime Data Storage (Tage)
                      </label>
                      <select
                        value={formData.runtime_data_storage_days}
                        onChange={(e) => setFormData(prev => ({ ...prev, runtime_data_storage_days: e.target.value }))}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent bg-white"
                      >
                        <option value="">Standard (System-Default)</option>
                        <option value="7">7 Tage</option>
                        <option value="14">14 Tage</option>
                        <option value="30">30 Tage</option>
                        <option value="90">90 Tage</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-800 mb-2">
                        Max. Job-Log Größe (MB)
                      </label>
                      <select
                        value={formData.max_job_log_size}
                        onChange={(e) => setFormData(prev => ({ ...prev, max_job_log_size: e.target.value }))}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent bg-white"
                      >
                        <option value="">Standard (System-Default)</option>
                        <option value="10">10 MB</option>
                        <option value="50">50 MB</option>
                        <option value="100">100 MB</option>
                        <option value="500">500 MB</option>
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-800 mb-2">
                      Vorgänger-Job (optional)
                    </label>
                    <input
                      type="text"
                      value={formData.predecessor_job}
                      onChange={(e) => setFormData(prev => ({ ...prev, predecessor_job: e.target.value }))}
                      placeholder="JobName oder Stream.JobName für Abhängigkeiten"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent bg-white"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-800 mb-2">
                      Externe Abhängigkeiten (optional)
                    </label>
                    <textarea
                      value={formData.external_dependencies}
                      onChange={(e) => setFormData(prev => ({ ...prev, external_dependencies: e.target.value }))}
                      placeholder={`Beispiele:\nDatei existiert: /path/to/trigger.txt\nDatenbank-Table befüllt: SELECT COUNT(*) FROM orders WHERE date = today\nExterner Service verfügbar: HTTP 200 von https://api.partner.com/status`}
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent bg-white"
                    />
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6">
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-8 text-center">
                <MessageCircle className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-700 mb-2">KI-Enhanced Features</h3>
                <p className="text-gray-600 mb-3">Intelligente Stream-Erstellung mit KI-Unterstützung</p>
                <p className="text-sm text-gray-500 mb-4">✨ Automatische Template-Erkennung<br />🔍 Intelligente Feldvorschläge<br />🛡️ Human-in-the-loop Validierung</p>
                <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  <PlayCircle className="w-3 h-3 mr-1" />
                  Kommende Version
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Resize Handle */}
      {!isFullscreen && (
        <div 
          className="w-1 bg-gray-200 hover:bg-blue-400 cursor-col-resize flex-shrink-0 relative group transition-colors duration-200"
          onMouseDown={handleMouseDown}
        >
          <div className="absolute inset-y-0 -left-1 -right-1 flex items-center justify-center">
            <div className="w-1 h-8 bg-gray-400 rounded-full group-hover:bg-blue-500 transition-colors duration-200"></div>
          </div>
        </div>
      )}

      {/* Right Panel - XML Editor */}
      <div 
        className={`bg-gray-900 flex flex-col`}
        style={{ 
          width: isFullscreen ? '100%' : `${100 - leftPanelWidth}%`,
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        
        {/* Editor Header */}
        <div className="bg-gray-800 px-4 py-3 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <Code className="w-4 h-4 text-gray-400" />
            <span className="text-white text-sm font-medium">XML Preview</span>
            <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs ${
              isGenerating ? 'bg-yellow-900 text-yellow-200' : 'bg-green-900 text-green-200'
            }`}>
              {isGenerating ? (
                <RefreshCw className="w-3 h-3 animate-spin" />
              ) : (
                <CheckCircle className="w-3 h-3" />
              )}
              <span>{isGenerating ? 'Updating...' : 'Ready'}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={copyXML}
              disabled={!xmlContent}
              className="p-1.5 text-gray-400 hover:text-white disabled:opacity-50"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={downloadXML}
              disabled={!xmlContent}
              className="p-1.5 text-gray-400 hover:text-white disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-1.5 text-gray-400 hover:text-white"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Monaco Editor */}
        <div 
          className="flex-1 relative"
          style={{ 
            minHeight: 0,
            height: '100%',
            width: '100%'
          }}
        >
          <Editor
            height="100%"
            defaultLanguage="xml"
            value={xmlContent}
            theme="vs-dark"
            onMount={(editor) => {
              editorRef.current = editor
              // Force layout after mount
              setTimeout(() => {
                editor.layout()
                // Ensure scrollbars are visible
                const viewState = editor.saveViewState()
                editor.restoreViewState(viewState)
              }, 100)
            }}
            options={{
              readOnly: true,
              minimap: { enabled: false },
              fontSize: 13,
              lineNumbers: 'on',
              wordWrap: 'off',
              folding: true,
              scrollBeyondLastLine: true,
              automaticLayout: true,
              overviewRulerLanes: 0,
              hideCursorInOverviewRuler: true,
              renderLineHighlight: 'none',
              selectionHighlight: false,
              scrollbar: {
                vertical: 'visible',
                horizontal: 'visible',
                useShadows: true,
                verticalHasArrows: true,
                horizontalHasArrows: true,
                verticalScrollbarSize: 20,
                horizontalScrollbarSize: 20,
                alwaysConsumeMouseWheel: true,
                handleMouseWheel: true
              },
              mouseWheelScrollSensitivity: 1,
              fastScrollSensitivity: 5
            }}
          />
        </div>
      </div>
    </div>
  )
}