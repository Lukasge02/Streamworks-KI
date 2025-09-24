'use client'

import { useState, useEffect } from 'react'
import { 
  FileText, Plus, Trash2, Download, Send, 
  Clock, Calendar, Server, User, AlertCircle, CheckCircle
} from 'lucide-react'

interface StreamJob {
  name?: string
  type: 'sap' | 'unix' | 'windows' | 'powershell'
  system?: string
  report?: string
  variant?: string
  script?: string
  server?: string
  user?: string
  maxRuntime?: number
}

interface StreamSchedule {
  startDate?: string
  startTime?: string
  interval?: string
  timeframe_start?: string
  timeframe_end?: string
  weekends?: boolean
  calendar?: string
}

interface StreamFormData {
  stream_name: string
  description?: string
  agent?: string
  contact?: string
  jobs: StreamJob[]
  schedule?: StreamSchedule
  predecessor?: string
  noOverlap?: boolean
  error_action?: 'BYPASS' | 'STOP' | 'RESTART'
  notify?: string
}

interface StreamFormProps {
  onStreamGenerated?: (formData: any) => void
}

export function StreamForm({ onStreamGenerated }: StreamFormProps = {}) {
  const [formData, setFormData] = useState<StreamFormData>({
    stream_name: '',
    description: '',
    agent: 'TestAgent1',
    contact: '',
    jobs: [],
    schedule: {
      weekends: true
    },
    error_action: 'BYPASS',
    notify: ''
  })

  const [suggestions, setSuggestions] = useState<{[key: string]: string[]}>({})
  const [loading, setLoading] = useState(false)
  const [xmlResult, setXmlResult] = useState<string>('')
  const [errors, setErrors] = useState<string[]>([])

  // Common suggestions (will be loaded from API)
  useEffect(() => {
    loadSuggestions('agent')
    loadSuggestions('system')
    loadSuggestions('report')
    loadSuggestions('user')
  }, [])

  const loadSuggestions = async (field: string) => {
    try {
      const response = await fetch('/api/simple-streams/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field })
      })
      const data = await response.json()
      if (data.success) {
        setSuggestions(prev => ({ ...prev, [field]: data.suggestions }))
      }
    } catch (err) {
      console.error('Error loading suggestions:', err)
    }
  }

  const addJob = () => {
    setFormData(prev => ({
      ...prev,
      jobs: [...prev.jobs, { type: 'sap' }]
    }))
  }

  const updateJob = (index: number, updates: Partial<StreamJob>) => {
    setFormData(prev => ({
      ...prev,
      jobs: prev.jobs.map((job, i) => 
        i === index ? { ...job, ...updates } : job
      )
    }))
  }

  const removeJob = (index: number) => {
    setFormData(prev => ({
      ...prev,
      jobs: prev.jobs.filter((_, i) => i !== index)
    }))
  }

  const generateXML = async () => {
    setLoading(true)
    setErrors([])
    setXmlResult('')

    try {
      const response = await fetch('/api/simple-streams/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      const data = await response.json()
      
      if (data.success) {
        setXmlResult(data.xml)
        // Notify parent component about the generated stream
        onStreamGenerated?.(formData)
      } else {
        setErrors(data.errors || ['Generation failed'])
      }
    } catch (err) {
      setErrors(['Failed to generate XML'])
    } finally {
      setLoading(false)
    }
  }

  const downloadXML = () => {
    if (!xmlResult) return
    
    const blob = new Blob([xmlResult], { type: 'text/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${formData.stream_name || 'stream'}.xml`
    a.click()
    URL.revokeObjectURL(url)
  }

  const loadTemplate = async (templateName: string) => {
    try {
      const response = await fetch('/api/simple-streams/templates')
      const data = await response.json()
      
      const template = data.templates?.find((t: any) => t.name === templateName)
      if (template) {
        setFormData(template.data)
      }
    } catch (err) {
      console.error('Error loading template:', err)
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Streamworks Stream Generator
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Erstellen Sie Streamworks-konforme XML-Streams über ein einfaches Formular
          </p>
        </div>

        {/* Quick Templates */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Vorlagen:
            </span>
            <button
              onClick={() => loadTemplate('SAP Report - 15 Min Interval')}
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
            >
              SAP Report (15 Min)
            </button>
            <button
              onClick={() => loadTemplate('PowerShell Script - Daily')}
              className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
            >
              PowerShell (Täglich)
            </button>
            <button
              onClick={() => loadTemplate('File Processing - Hourly')}
              className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
            >
              File Processing (Stündlich)
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Stream Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Stream Name *
              </label>
              <input
                type="text"
                value={formData.stream_name}
                onChange={(e) => setFormData({ ...formData, stream_name: e.target.value })}
                placeholder="CUST-P-PA1-PUR-0013"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Agent/Server
              </label>
              <select
                value={formData.agent}
                onChange={(e) => setFormData({ ...formData, agent: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {suggestions.agent?.map(agent => (
                  <option key={agent} value={agent}>{agent}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Beschreibung
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="SAP Report für Bestellungen..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows={2}
            />
          </div>

          {/* Jobs */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Jobs
              </h3>
              <button
                onClick={addJob}
                className="flex items-center space-x-2 px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                <Plus className="w-4 h-4" />
                <span>Job hinzufügen</span>
              </button>
            </div>

            {formData.jobs.map((job, index) => (
              <div key={index} className="mb-4 p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    Job {index + 1}: {job.name || `00${index + 1}0-${formData.stream_name}`}
                  </h4>
                  <button
                    onClick={() => removeJob(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Typ
                    </label>
                    <select
                      value={job.type}
                      onChange={(e) => updateJob(index, { type: e.target.value as any })}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                    >
                      <option value="sap">SAP</option>
                      <option value="windows">Windows</option>
                      <option value="powershell">PowerShell</option>
                      <option value="unix">Unix</option>
                    </select>
                  </div>

                  {job.type === 'sap' && (
                    <>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          System
                        </label>
                        <input
                          type="text"
                          value={job.system || ''}
                          onChange={(e) => updateJob(index, { system: e.target.value })}
                          placeholder="PA1_100"
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Report
                        </label>
                        <input
                          type="text"
                          value={job.report || ''}
                          onChange={(e) => updateJob(index, { report: e.target.value })}
                          placeholder="RBDAGAIN"
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Variante
                        </label>
                        <input
                          type="text"
                          value={job.variant || ''}
                          onChange={(e) => updateJob(index, { variant: e.target.value })}
                          placeholder="ZXY-UFA"
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                        />
                      </div>
                    </>
                  )}

                  {(job.type === 'windows' || job.type === 'powershell' || job.type === 'unix') && (
                    <div className="col-span-2">
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Script
                      </label>
                      <input
                        type="text"
                        value={job.script || ''}
                        onChange={(e) => updateJob(index, { script: e.target.value })}
                        placeholder="Get-Process | Export-Csv..."
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                    </div>
                  )}

                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      User
                    </label>
                    <input
                      type="text"
                      value={job.user || ''}
                      onChange={(e) => updateJob(index, { user: e.target.value })}
                      placeholder="Batch_PUR"
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Max Runtime (Min)
                    </label>
                    <input
                      type="number"
                      value={job.maxRuntime || ''}
                      onChange={(e) => updateJob(index, { maxRuntime: parseInt(e.target.value) })}
                      placeholder="5"
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                    />
                  </div>
                </div>
              </div>
            ))}

            {formData.jobs.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                Keine Jobs definiert. Fügen Sie mindestens einen Job hinzu.
              </div>
            )}
          </div>

          {/* Schedule */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              Scheduling
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Start Datum
                </label>
                <input
                  type="date"
                  value={formData.schedule?.startDate || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule: { ...formData.schedule, startDate: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Start Zeit
                </label>
                <input
                  type="time"
                  value={formData.schedule?.startTime || '06:00'}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule: { ...formData.schedule, startTime: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Intervall
                </label>
                <select
                  value={formData.schedule?.interval || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule: { ...formData.schedule, interval: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Kein Intervall</option>
                  <option value="5min">Alle 5 Minuten</option>
                  <option value="15min">Alle 15 Minuten</option>
                  <option value="30min">Alle 30 Minuten</option>
                  <option value="1h">Stündlich</option>
                  <option value="daily">Täglich</option>
                  <option value="weekly">Wöchentlich</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Zeitfenster Start
                </label>
                <input
                  type="time"
                  value={formData.schedule?.timeframe_start || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule: { ...formData.schedule, timeframe_start: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Zeitfenster Ende
                </label>
                <input
                  type="time"
                  value={formData.schedule?.timeframe_end || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    schedule: { ...formData.schedule, timeframe_end: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.schedule?.weekends ?? true}
                    onChange={(e) => setFormData({
                      ...formData,
                      schedule: { ...formData.schedule, weekends: e.target.checked }
                    })}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Wochenenden
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* Dependencies & Error Handling */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Vorgänger Job
              </label>
              <input
                type="text"
                value={formData.predecessor || ''}
                onChange={(e) => setFormData({ ...formData, predecessor: e.target.value })}
                placeholder="L10PESG26"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Fehlerbehandlung
              </label>
              <select
                value={formData.error_action}
                onChange={(e) => setFormData({ ...formData, error_action: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="BYPASS">BYPASS + NOTIFY</option>
                <option value="STOP">STOP & ESCALATE</option>
                <option value="RESTART">RESTART</option>
              </select>
            </div>
          </div>

          {/* Errors */}
          {errors.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 text-red-800 mb-2">
                <AlertCircle className="w-5 h-5" />
                <span className="font-medium">Validierungsfehler</span>
              </div>
              <ul className="list-disc list-inside text-red-600 text-sm">
                {errors.map((error, i) => (
                  <li key={i}>{error}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-500">
              * Pflichtfelder
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={generateXML}
                disabled={loading || !formData.stream_name}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                <span>XML Generieren</span>
              </button>

              {xmlResult && (
                <button
                  onClick={downloadXML}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                >
                  <Download className="w-4 h-4" />
                  <span>Download XML</span>
                </button>
              )}
            </div>
          </div>

          {/* XML Result */}
          {xmlResult && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Generiertes XML
                </h3>
                <div className="flex items-center space-x-2 text-green-600">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm">Erfolgreich generiert</span>
                </div>
              </div>
              <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto text-xs">
                {xmlResult}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}