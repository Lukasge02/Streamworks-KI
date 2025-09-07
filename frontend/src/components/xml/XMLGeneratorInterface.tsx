'use client'

import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { FileText, Settings, Download, CheckCircle, AlertCircle, Clock, Eye, RefreshCw } from 'lucide-react'

interface XMLGenerationRequest {
  description: string
  template_type: string
  context_keywords: string[]
  dry_run: boolean
  auto_validate: boolean
}

interface XMLGenerationResponse {
  success: boolean
  xml_content?: string
  plan?: {
    description: string
    full_plan: string
    steps: Array<{
      title: string
      description: string
      order: number
    }>
    template_type: string
    created_at: string
  }
  validation_results?: {
    valid: boolean
    errors: string[]
  }
  human_review_status?: string
  thread_id?: string
  workflow_step?: string
  error?: string
}

export const XMLGeneratorInterface = () => {
  const [request, setRequest] = useState<XMLGenerationRequest>({
    description: '',
    template_type: 'enterprise',
    context_keywords: ['StreamWorks', 'ETL'],
    dry_run: true,
    auto_validate: true
  })
  const [response, setResponse] = useState<XMLGenerationResponse | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [activeTab, setActiveTab] = useState<'generator' | 'preview' | 'plan'>('generator')
  const xmlPreviewRef = useRef<HTMLPreElement>(null)

  const templateTypes = [
    { value: 'basic', label: 'Basic ETL Pipeline', description: 'Einfache Datenverarbeitung' },
    { value: 'enterprise', label: 'Enterprise', description: 'Vollständige Enterprise-Lösung' },
    { value: 'custom-workflow', label: 'Custom Workflow', description: 'Benutzerdefinierte Workflows' },
    { value: 'batch-processing', label: 'Batch Processing', description: 'Stapelverarbeitung' }
  ]

  const keywordSuggestions = [
    'StreamWorks', 'ETL', 'Pipeline', 'Monitoring', 'Database', 'API', 'Transform', 
    'Validation', 'Error-Handling', 'Scheduling', 'Integration', 'Data-Warehouse'
  ]

  const generateXML = async () => {
    setIsGenerating(true)
    try {
      const response = await fetch('/graph/xml', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      const data = await response.json()
      setResponse(data)
      
      if (data.success && data.xml_content) {
        setActiveTab('preview')
      }
    } catch (error) {
      setResponse({
        success: false,
        error: error instanceof Error ? error.message : 'Generation failed'
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadXML = () => {
    if (!response?.xml_content) return
    
    const blob = new Blob([response.xml_content], { type: 'application/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `streamworks-config-${Date.now()}.xml`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const addKeyword = (keyword: string) => {
    if (!request.context_keywords.includes(keyword)) {
      setRequest(prev => ({
        ...prev,
        context_keywords: [...prev.context_keywords, keyword]
      }))
    }
  }

  const removeKeyword = (keyword: string) => {
    setRequest(prev => ({
      ...prev,
      context_keywords: prev.context_keywords.filter(k => k !== keyword)
    }))
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                XML Generator mit HITL
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                StreamWorks XML-Konfigurationen mit Human-in-the-Loop Review
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="px-6">
          <div className="flex space-x-8">
            {[
              { id: 'generator', label: 'Generator', icon: Settings },
              { id: 'preview', label: 'XML Preview', icon: Eye },
              { id: 'plan', label: 'Generation Plan', icon: FileText }
            ].map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-4 border-b-2 transition-colors ${
                    isActive
                      ? 'border-purple-600 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'generator' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto space-y-6"
          >
            {/* Description */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Beschreibung der XML-Konfiguration
              </label>
              <textarea
                value={request.description}
                onChange={(e) => setRequest(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Beschreibe die StreamWorks XML-Konfiguration die du erstellen möchtest..."
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Template Type */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Template Typ
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templateTypes.map((template) => (
                  <div
                    key={template.value}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                      request.template_type === template.value
                        ? 'border-purple-600 bg-purple-50 dark:bg-purple-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                    }`}
                    onClick={() => setRequest(prev => ({ ...prev, template_type: template.value }))}
                  >
                    <h3 className="font-medium text-gray-900 dark:text-white">{template.label}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{template.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Context Keywords */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Context Keywords
              </label>
              
              {/* Selected Keywords */}
              <div className="flex flex-wrap gap-2 mb-4">
                {request.context_keywords.map((keyword) => (
                  <span
                    key={keyword}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-200"
                  >
                    {keyword}
                    <button
                      onClick={() => removeKeyword(keyword)}
                      className="ml-2 text-purple-600 hover:text-purple-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>

              {/* Keyword Suggestions */}
              <div className="space-y-2">
                <p className="text-xs text-gray-500">Vorschläge:</p>
                <div className="flex flex-wrap gap-2">
                  {keywordSuggestions
                    .filter(k => !request.context_keywords.includes(k))
                    .map((keyword) => (
                    <button
                      key={keyword}
                      onClick={() => addKeyword(keyword)}
                      className="px-3 py-1 text-sm border border-gray-300 rounded-full hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700"
                    >
                      + {keyword}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Options */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">Optionen</h3>
              <div className="space-y-4">
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={request.dry_run}
                    onChange={(e) => setRequest(prev => ({ ...prev, dry_run: e.target.checked }))}
                    className="w-4 h-4 text-purple-600 rounded"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Dry Run (nur Validierung)</span>
                </label>
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={request.auto_validate}
                    onChange={(e) => setRequest(prev => ({ ...prev, auto_validate: e.target.checked }))}
                    className="w-4 h-4 text-purple-600 rounded"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Automatische XSD-Validierung</span>
                </label>
              </div>
            </div>

            {/* Generate Button */}
            <div className="flex justify-center">
              <button
                onClick={generateXML}
                disabled={!request.description.trim() || isGenerating}
                className="px-8 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-3"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <span>Generiere XML...</span>
                  </>
                ) : (
                  <>
                    <FileText className="w-5 h-5" />
                    <span>XML Generieren</span>
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}

        {activeTab === 'preview' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-6xl mx-auto"
          >
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              {/* Preview Header */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                      XML Preview
                    </h2>
                    {response?.validation_results && (
                      <div className="flex items-center space-x-2">
                        {response.validation_results.valid ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-red-600" />
                        )}
                        <span className={`text-sm ${
                          response.validation_results.valid ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {response.validation_results.valid ? 'Valid' : 'Invalid'}
                        </span>
                      </div>
                    )}
                  </div>
                  {response?.xml_content && (
                    <button
                      onClick={downloadXML}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Preview Content */}
              <div className="p-6">
                {response?.xml_content ? (
                  <div className="space-y-4">
                    <pre
                      ref={xmlPreviewRef}
                      className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto text-sm font-mono"
                      style={{ maxHeight: '500px' }}
                    >
                      {response.xml_content}
                    </pre>
                    
                    {/* Validation Errors */}
                    {response.validation_results && !response.validation_results.valid && (
                      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                        <h4 className="text-sm font-medium text-red-800 dark:text-red-200 mb-2">
                          Validierungsfehler:
                        </h4>
                        <ul className="text-sm text-red-700 dark:text-red-300 space-y-1">
                          {response.validation_results.errors.map((error, index) => (
                            <li key={index}>• {error}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : response?.error ? (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <AlertCircle className="w-5 h-5 text-red-600" />
                      <span className="text-red-800 dark:text-red-200">Error: {response.error}</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Keine XML-Konfiguration generiert</p>
                    <p className="text-sm mt-2">Verwende den Generator, um eine Konfiguration zu erstellen.</p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'plan' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto"
          >
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Generation Plan
                </h2>
                {response?.plan?.created_at && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Created: {new Date(response.plan.created_at).toLocaleString()}
                  </p>
                )}
              </div>

              <div className="p-6">
                {response?.plan ? (
                  <div className="space-y-6">
                    {/* Plan Description */}
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white mb-2">Beschreibung</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {response.plan.description}
                      </p>
                    </div>

                    {/* Steps */}
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white mb-4">
                        Implementierungsschritte ({response.plan.steps?.length || 0})
                      </h3>
                      <div className="space-y-4">
                        {response.plan.steps?.slice(0, 10).map((step, index) => (
                          <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                            <div className="flex items-start space-x-3">
                              <span className="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-800 rounded-full flex items-center justify-center text-xs font-medium">
                                {step.order}
                              </span>
                              <div className="flex-1">
                                <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                                  {step.title}
                                </h4>
                                {step.description && (
                                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                    {step.description}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Kein Generierungsplan verfügbar</p>
                    <p className="text-sm mt-2">Generiere eine XML-Konfiguration, um den Plan zu sehen.</p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}