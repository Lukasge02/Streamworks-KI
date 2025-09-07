'use client'

import { useState, useEffect, useCallback } from 'react'
import { 
  Settings, MessageCircle, Download, Copy, Maximize2,
  Code, CheckCircle, AlertTriangle, RefreshCw, ChevronDown,
  Clock, Server, User, Calendar, Mail, Zap, FileText
} from 'lucide-react'
import Editor from '@monaco-editor/react'

interface StreamFormAdvancedProps {
  className?: string
}

interface FormData {
  // Stream basics
  stream: {
    name: string
    shortDescription: string
    agent: string
    contacts: {
      ownerEmail: string
      distributionList: string
    }
  }
  
  // Categories (toggleable)
  categories: {
    scheduling: boolean
    orchestration: boolean
    runtime: boolean
    notifications: boolean
  }
  
  // Scheduling
  scheduling: {
    mode: 'manual' | 'once' | 'recurring'
    startDate: string
    startTime: string
    interval: string
    timeWindow: {
      from: string
      to: string
    }
    weekends: boolean
    holidayCalendar: string
  }
  
  // Orchestration
  orchestration: {
    predecessorJob: string
    noOverlapPhase: string
  }
  
  // Job
  job: {
    name: string
    type: 'Windows' | 'Unix'
    systemClient: string
    execUser: string
    targetHost: string
    mode: 'sap' | 'script'
    sap: {
      report: string
      variant: string
    }
    script: {
      command: string
    }
    runtime: {
      maxDuration: string
    }
    output: 'none' | 'email' | 'print'
    onError: 'bypass_notify' | 'stop_escalate' | 'retry'
  }
}

export function StreamFormAdvanced({ className }: StreamFormAdvancedProps) {
  const [activeMode, setActiveMode] = useState<'form' | 'chat'>('form')
  const [xmlContent, setXmlContent] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)

  const [formData, setFormData] = useState<FormData>({
    stream: {
      name: '',
      shortDescription: '',
      agent: 'gtasswvu15777',
      contacts: {
        ownerEmail: '',
        distributionList: ''
      }
    },
    categories: {
      scheduling: false,
      orchestration: false,
      runtime: false,
      notifications: false
    },
    scheduling: {
      mode: 'manual',
      startDate: '',
      startTime: '06:00',
      interval: 'PT15M',
      timeWindow: {
        from: '05:30',
        to: '23:00'
      },
      weekends: true,
      holidayCalendar: ''
    },
    orchestration: {
      predecessorJob: '',
      noOverlapPhase: ''
    },
    job: {
      name: '',
      type: 'Unix',
      systemClient: '',
      execUser: '',
      targetHost: '',
      mode: 'sap',
      sap: {
        report: '',
        variant: ''
      },
      script: {
        command: ''
      },
      runtime: {
        maxDuration: '00:05'
      },
      output: 'none',
      onError: 'bypass_notify'
    }
  })

  // Quick templates
  const templates = [
    {
      name: 'SAP Report (15 Min)',
      data: {
        stream: { name: 'SAP-RBDAGAIN-Stream', shortDescription: 'SAP Report alle 15 Min', agent: 'gtasswvu15777', contacts: { ownerEmail: '', distributionList: '' } },
        categories: { scheduling: true, orchestration: false, runtime: true, notifications: false },
        job: { name: '', type: 'Unix' as const, systemClient: 'PA1_100', execUser: 'Batch_PUR', targetHost: '', mode: 'sap' as const, sap: { report: 'RBDAGAIN', variant: 'ZXY-UFA' }, script: { command: '' }, runtime: { maxDuration: '00:05' }, output: 'email' as const, onError: 'bypass_notify' as const },
        scheduling: { mode: 'recurring' as const, startDate: '2025-07-23', startTime: '06:00', interval: 'PT15M', timeWindow: { from: '05:30', to: '23:00' }, weekends: true, holidayCalendar: '' }
      }
    },
    {
      name: 'PowerShell (Täglich)',
      data: {
        stream: { name: 'PowerShell-Backup-Stream', shortDescription: 'Tägliches Backup Script', agent: 'gtasswvu15777', contacts: { ownerEmail: '', distributionList: '' } },
        categories: { scheduling: true, orchestration: false, runtime: true, notifications: false },
        job: { name: '', type: 'Windows' as const, systemClient: '', execUser: 'Batch_PUR', targetHost: '', mode: 'script' as const, sap: { report: '', variant: '' }, script: { command: 'C:\\Scripts\\backup.ps1' }, runtime: { maxDuration: '00:30' }, output: 'email' as const, onError: 'stop_escalate' as const },
        scheduling: { mode: 'recurring' as const, startDate: '2025-07-23', startTime: '02:00', interval: 'P1D', timeWindow: { from: '', to: '' }, weekends: false, holidayCalendar: '' }
      }
    },
    {
      name: 'Manual Simple',
      data: {
        stream: { name: 'Manual-Test-Stream', shortDescription: 'Manuell startbarer Test-Stream', agent: 'gtasswvu15777', contacts: { ownerEmail: '', distributionList: '' } },
        categories: { scheduling: false, orchestration: false, runtime: false, notifications: false },
        job: { name: '', type: 'Windows' as const, systemClient: '', execUser: '', targetHost: '', mode: 'script' as const, sap: { report: '', variant: '' }, script: { command: 'echo Hello from RAG && exit 0' }, runtime: { maxDuration: '00:01' }, output: 'none' as const, onError: 'bypass_notify' as const },
        scheduling: { mode: 'manual' as const, startDate: '', startTime: '', interval: '', timeWindow: { from: '', to: '' }, weekends: true, holidayCalendar: '' }
      }
    }
  ]

  const generateSpec = useCallback((): any => {
    const streamName = formData.stream.name
    const jobKey = formData.job.name || `00010-${streamName}`

    // Build script based on mode
    let script = ''
    if (formData.job.mode === 'sap') {
      script = `sws_jexa4s --system ${formData.job.systemClient} --user ${formData.job.execUser} --report ${formData.job.sap.report} --variant ${formData.job.sap.variant}`
    } else {
      script = formData.job.script.command
    }

    return {
      stream: {
        name: streamName,
        agent: formData.stream.agent,
        shortDescription: formData.stream.shortDescription,
        contacts: formData.stream.contacts,
        schedulingRequired: formData.categories.scheduling && formData.scheduling.mode !== 'manual',
        calendarId: formData.scheduling.holidayCalendar
      },
      jobs: [
        { key: 'StartPoint', category: 'StartPoint' },
        {
          key: jobKey,
          category: 'Job',
          type: formData.job.type,
          execUser: formData.job.execUser,
          targetHost: formData.job.targetHost,
          systemClient: formData.job.systemClient,
          mode: formData.job.mode,
          sap: formData.job.sap,
          script: script,
          runtime: formData.job.runtime,
          output: formData.job.output,
          onError: formData.job.onError
        },
        { key: 'EndPoint', category: 'EndPoint' }
      ],
      edges: [
        ['StartPoint', jobKey],
        [jobKey, 'EndPoint']
      ],
      runProps: formData.scheduling.mode === 'manual' 
        ? { runNumber: 0, startTimeType: 'None' }
        : {
            runNumber: 1,
            startTimeType: 'AbsoluteStartTime',
            startTimeDayType: 'CalendarDay',
            startDate: formData.scheduling.startDate,
            startTime: formData.scheduling.startTime,
            intervalIso: formData.scheduling.interval,
            timeWindow: formData.scheduling.timeWindow,
            weekends: formData.scheduling.weekends,
            holidayCalendar: formData.scheduling.holidayCalendar
          },
      orchestration: formData.categories.orchestration ? formData.orchestration : {}
    }
  }, [formData])

  const generateXML = useCallback(async (spec: any) => {
    setIsGenerating(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 800))
      
      const xml = `<?xml version="1.0" encoding="utf-8"?>
<ExportableStream>
  <Stream>
    <StreamName>${spec.stream.name}</StreamName>
    <StreamDocumentation><![CDATA[${spec.stream.shortDescription}]]></StreamDocumentation>
    <AgentDetail>${spec.stream.agent}</AgentDetail>
    <StreamType>Normal</StreamType>
    <MaxStreamRuns>5</MaxStreamRuns>
    <ShortDescription><![CDATA[${spec.stream.shortDescription}]]></ShortDescription>
    <SchedulingRequiredFlag>${spec.stream.schedulingRequired ? 'True' : 'False'}</SchedulingRequiredFlag>
    <CalendarId>${spec.stream.calendarId || ''}</CalendarId>
    <Jobs>
      ${spec.jobs.map((job: any, idx: number) => `
      <Job>
        <JobName>${job.key}</JobName>
        <ShortDescription><![CDATA[${job.category === 'StartPoint' ? 'Start Point for the Stream' : 
                                     job.category === 'EndPoint' ? 'End Point for the Stream' : 
                                     job.mode === 'sap' ? `SAP ${job.sap.report}` : 'Script Job'}]]></ShortDescription>
        <JobCategory>${job.category}</JobCategory>
        <JobType>${job.type || 'None'}</JobType>
        <NormalJobFlag>True</NormalJobFlag>
        <DisplayOrder>${idx + 1}</DisplayOrder>
        <CoordinateX>0</CoordinateX>
        <CoordinateY>${idx * 200}</CoordinateY>
        ${job.script ? `<MainScript><![CDATA[${job.script}]]></MainScript>` : '<MainScript IsNull="True" />'}
        ${idx < spec.jobs.length - 1 ? `
        <JobInternalSuccessors>
          <JobInternalSuccessor>
            <JobName>${spec.jobs[idx + 1].key}</JobName>
          </JobInternalSuccessor>
        </JobInternalSuccessors>` : '<JobInternalSuccessors />'}
        <StreamRunJobProperties>
          <StreamRunJobProperty>
            <RunNumber>${spec.runProps.runNumber || 0}</RunNumber>
            ${spec.runProps.startTimeType === 'AbsoluteStartTime' ? `
            <StartTime>${spec.runProps.startTime}</StartTime>
            <StartTimeDayType>${spec.runProps.startTimeDayType}</StartTimeDayType>` : `
            <StartTime IsNull="True" />
            <StartTimeDayType />`}
          </StreamRunJobProperty>
        </StreamRunJobProperties>
      </Job>`).join('')}
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
    if (formData.stream.name.trim()) {
      const spec = generateSpec()
      generateXML(spec)
    }
  }, [formData, generateSpec, generateXML])

  const applyTemplate = (template: any) => {
    setFormData(prev => ({
      ...prev,
      ...template.data,
      // Merge categories properly
      categories: {
        ...prev.categories,
        ...template.data.categories
      }
    }))
  }

  const toggleCategory = (category: keyof FormData['categories']) => {
    setFormData(prev => ({
      ...prev,
      categories: {
        ...prev.categories,
        [category]: !prev.categories[category]
      }
    }))
  }

  const downloadXML = () => {
    if (!xmlContent) return
    const blob = new Blob([xmlContent], { type: 'text/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${formData.stream.name || 'stream'}.xml`
    a.click()
    URL.revokeObjectURL(url)
  }

  const copyXML = () => {
    navigator.clipboard.writeText(xmlContent)
  }

  return (
    <div className={`flex h-full bg-white ${className}`}>
      {/* Left Panel */}
      <div className={`${isFullscreen ? 'hidden' : 'w-1/2'} border-r border-gray-200 flex flex-col`}>
        
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
        <div className="flex-1 overflow-auto">
          {activeMode === 'form' ? (
            <div className="p-6 space-y-6">
              {/* Quick Templates */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Vorlagen
                </label>
                <div className="grid grid-cols-1 gap-2 mb-4">
                  {templates.map((template, idx) => (
                    <button
                      key={idx}
                      onClick={() => applyTemplate(template)}
                      className="p-3 text-left bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors"
                    >
                      <div className="text-sm font-medium text-blue-700">{template.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Basic Stream Info */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-gray-700">Stream Grundlagen</h3>
                
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Stream Name *
                  </label>
                  <input
                    type="text"
                    value={formData.stream.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, stream: { ...prev.stream, name: e.target.value } }))}
                    placeholder="CUST-P-PA1-PUR-0013"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Beschreibung
                  </label>
                  <textarea
                    value={formData.stream.shortDescription}
                    onChange={(e) => setFormData(prev => ({ ...prev, stream: { ...prev.stream, shortDescription: e.target.value } }))}
                    placeholder="SAP-Report RBDAGAIN, Bereich PUR; 15-Min-Takt 05:30–23:00"
                    rows={2}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Agent
                  </label>
                  <input
                    type="text"
                    value={formData.stream.agent}
                    onChange={(e) => setFormData(prev => ({ ...prev, stream: { ...prev.stream, agent: e.target.value } }))}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Job Configuration */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-gray-700">Job Konfiguration</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Job Typ *
                    </label>
                    <select
                      value={formData.job.type}
                      onChange={(e) => setFormData(prev => ({ ...prev, job: { ...prev.job, type: e.target.value as 'Windows' | 'Unix' } }))}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="Unix">Unix</option>
                      <option value="Windows">Windows</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Modus *
                    </label>
                    <select
                      value={formData.job.mode}
                      onChange={(e) => setFormData(prev => ({ ...prev, job: { ...prev.job, mode: e.target.value as 'sap' | 'script' } }))}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="sap">SAP</option>
                      <option value="script">Script</option>
                    </select>
                  </div>
                </div>

                {/* Conditional Job Fields */}
                {formData.job.mode === 'sap' && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Report
                      </label>
                      <input
                        type="text"
                        value={formData.job.sap.report}
                        onChange={(e) => setFormData(prev => ({ ...prev, job: { ...prev.job, sap: { ...prev.job.sap, report: e.target.value } } }))}
                        placeholder="RBDAGAIN"
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Variante
                      </label>
                      <input
                        type="text"
                        value={formData.job.sap.variant}
                        onChange={(e) => setFormData(prev => ({ ...prev, job: { ...prev.job, sap: { ...prev.job.sap, variant: e.target.value } } }))}
                        placeholder="ZXY-UFA"
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                )}

                {formData.job.mode === 'script' && (
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Script/Command
                    </label>
                    <textarea
                      value={formData.job.script.command}
                      onChange={(e) => setFormData(prev => ({ ...prev, job: { ...prev.job, script: { command: e.target.value } } }))}
                      placeholder="echo Hello && exit 0"
                      rows={3}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      System/Client
                    </label>
                    <input
                      type="text"
                      value={formData.job.systemClient}
                      onChange={(e) => setFormData(prev => ({ ...prev, job: { ...prev.job, systemClient: e.target.value } }))}
                      placeholder="PA1_100"
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Exec User
                    </label>
                    <input
                      type="text"
                      value={formData.job.execUser}
                      onChange={(e) => setFormData(prev => ({ ...prev, job: { ...prev.job, execUser: e.target.value } }))}
                      placeholder="Batch_PUR"
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              {/* Expandable Categories */}
              <div className="space-y-3">
                {/* Scheduling */}
                <div>
                  <button
                    onClick={() => toggleCategory('scheduling')}
                    className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <span className="text-sm font-medium">Scheduling</span>
                      {formData.categories.scheduling && (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Aktiv</span>
                      )}
                    </div>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${formData.categories.scheduling ? 'rotate-180' : ''}`} />
                  </button>
                  
                  {formData.categories.scheduling && (
                    <div className="mt-3 space-y-3 pl-4">
                      <div className="grid grid-cols-3 gap-2">
                        {['manual', 'once', 'recurring'].map((mode) => (
                          <button
                            key={mode}
                            onClick={() => setFormData(prev => ({ ...prev, scheduling: { ...prev.scheduling, mode: mode as any } }))}
                            className={`px-3 py-2 text-xs rounded-lg border transition-colors ${
                              formData.scheduling.mode === mode
                                ? 'border-blue-500 bg-blue-50 text-blue-700'
                                : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                            }`}
                          >
                            {mode.charAt(0).toUpperCase() + mode.slice(1)}
                          </button>
                        ))}
                      </div>
                      
                      {formData.scheduling.mode !== 'manual' && (
                        <>
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <label className="block text-xs font-medium text-gray-600 mb-1">Start Datum</label>
                              <input
                                type="date"
                                value={formData.scheduling.startDate}
                                onChange={(e) => setFormData(prev => ({ ...prev, scheduling: { ...prev.scheduling, startDate: e.target.value } }))}
                                className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-medium text-gray-600 mb-1">Start Zeit</label>
                              <input
                                type="time"
                                value={formData.scheduling.startTime}
                                onChange={(e) => setFormData(prev => ({ ...prev, scheduling: { ...prev.scheduling, startTime: e.target.value } }))}
                                className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                              />
                            </div>
                          </div>
                          
                          {formData.scheduling.mode === 'recurring' && (
                            <div>
                              <label className="block text-xs font-medium text-gray-600 mb-1">Intervall</label>
                              <select
                                value={formData.scheduling.interval}
                                onChange={(e) => setFormData(prev => ({ ...prev, scheduling: { ...prev.scheduling, interval: e.target.value } }))}
                                className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                              >
                                <option value="PT15M">15 Minuten</option>
                                <option value="PT30M">30 Minuten</option>
                                <option value="PT1H">1 Stunde</option>
                                <option value="P1D">Täglich</option>
                                <option value="P1W">Wöchentlich</option>
                              </select>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Runtime Settings */}
                <div>
                  <button
                    onClick={() => toggleCategory('runtime')}
                    className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Zap className="w-4 h-4 text-gray-500" />
                      <span className="text-sm font-medium">Runtime & Error Handling</span>
                      {formData.categories.runtime && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Aktiv</span>
                      )}
                    </div>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${formData.categories.runtime ? 'rotate-180' : ''}`} />
                  </button>
                  
                  {formData.categories.runtime && (
                    <div className="mt-3 space-y-3 pl-4">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">Max Duration</label>
                          <input
                            type="text"
                            value={formData.job.runtime.maxDuration}
                            onChange={(e) => setFormData(prev => ({ ...prev, job: { ...prev.job, runtime: { maxDuration: e.target.value } } }))}
                            placeholder="00:05"
                            className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">Bei Fehler</label>
                          <select
                            value={formData.job.onError}
                            onChange={(e) => setFormData(prev => ({ ...prev, job: { ...prev.job, onError: e.target.value as any } }))}
                            className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="bypass_notify">Bypass & Notify</option>
                            <option value="stop_escalate">Stop & Escalate</option>
                            <option value="retry">Retry</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Orchestration */}
                <div>
                  <button
                    onClick={() => toggleCategory('orchestration')}
                    className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Server className="w-4 h-4 text-gray-500" />
                      <span className="text-sm font-medium">Orchestrierung</span>
                      {formData.categories.orchestration && (
                        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">Aktiv</span>
                      )}
                    </div>
                    <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${formData.categories.orchestration ? 'rotate-180' : ''}`} />
                  </button>
                  
                  {formData.categories.orchestration && (
                    <div className="mt-3 space-y-3 pl-4">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Vorgänger Job</label>
                        <input
                          type="text"
                          value={formData.orchestration.predecessorJob}
                          onChange={(e) => setFormData(prev => ({ ...prev, orchestration: { ...prev.orchestration, predecessorJob: e.target.value } }))}
                          placeholder="L10PESG26"
                          className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <MessageCircle className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                <p className="text-gray-600">AI Chat Interface</p>
                <p className="text-sm text-gray-500 mt-1">Kommende Version</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Panel - XML Editor */}
      <div className={`${isFullscreen ? 'w-full' : 'w-1/2'} bg-gray-900 flex flex-col`}>
        
        {/* Editor Header */}
        <div className="bg-gray-800 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Code className="w-4 h-4 text-gray-400" />
            <span className="text-white text-sm font-medium">StreamWorks XML</span>
            <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs ${
              isGenerating ? 'bg-yellow-900 text-yellow-200' : 'bg-green-900 text-green-200'
            }`}>
              {isGenerating ? (
                <RefreshCw className="w-3 h-3 animate-spin" />
              ) : (
                <CheckCircle className="w-3 h-3" />
              )}
              <span>{isGenerating ? 'Generiere...' : 'Bereit'}</span>
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
        <div className="flex-1">
          <Editor
            height="100%"
            defaultLanguage="xml"
            value={xmlContent}
            theme="vs-dark"
            options={{
              readOnly: true,
              minimap: { enabled: false },
              fontSize: 13,
              lineNumbers: 'on',
              wordWrap: 'on',
              folding: true,
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
          />
        </div>
      </div>
    </div>
  )
}