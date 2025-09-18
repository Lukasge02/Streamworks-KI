'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChartBarIcon,
  DocumentTextIcon,
  CpuChipIcon,
  ServerIcon,
  BeakerIcon,
  CodeBracketSquareIcon,
  ShieldCheckIcon,
  ClockIcon,
  CheckBadgeIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ArrowPathIcon,
  PlayIcon,
  CloudIcon,
  BuildingOfficeIcon,
  AcademicCapIcon,
  RocketLaunchIcon,
  BoltIcon,
  CogIcon
} from '@heroicons/react/24/outline'

interface SystemHealth {
  status: string
  service: string
  version: string
  features: Record<string, boolean>
  services: Record<string, string>
  timestamp: string
}

interface PipelineInfo {
  pipelines: Array<{
    name: string
    description: string
    status: string
    phase: number
    endpoints: string[]
  }>
  active_pipelines: string[]
  planned_pipelines: string[]
}

interface ProductionStatus {
  deployment_ready: boolean
  enterprise_grade: boolean
  thesis_ready: boolean
  production_ready: boolean
  checks: Record<string, boolean>
  status: string
  phase: number
}

const ArvatoEnterpriseDashboard = () => {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)
  const [pipelineInfo, setPipelineInfo] = useState<PipelineInfo | null>(null)
  const [productionStatus, setProductionStatus] = useState<ProductionStatus | null>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [qaResponse, setQaResponse] = useState<string>('')
  const [xmlResponse, setXmlResponse] = useState<string>('')
  const [testQuery, setTestQuery] = useState('Was ist Streamworks?')

  // Arvato Systems Brand Colors
  const arvatoColors = {
    primary: '#0066CC',     // Arvato Blue
    secondary: '#FF6B35',   // Arvato Orange
    success: '#10B981',     // Green
    warning: '#F59E0B',     // Yellow
    error: '#EF4444',       // Red
    dark: '#1F2937',        // Dark Gray
    light: '#F8FAFC'        // Light Gray
  }

  const fetchSystemData = async () => {
    try {
      setLoading(true)
      
      // Parallel fetch for better performance
      const [healthResponse, pipelineResponse, productionResponse] = await Promise.all([
        fetch('/api/system/health'),
        fetch('/graph/pipelines'),
        fetch('/production/deployment/readiness')
      ])

      if (healthResponse.ok) {
        setSystemHealth(await healthResponse.json())
      }
      
      if (pipelineResponse.ok) {
        setPipelineInfo(await pipelineResponse.json())
      }
      
      if (productionResponse.ok) {
        setProductionStatus(await productionResponse.json())
      }

      setLastUpdate(new Date())
    } catch (error) {
      console.error('Failed to fetch system data:', error)
    } finally {
      setLoading(false)
    }
  }

  const testQAPipeline = async () => {
    try {
      const response = await fetch('/graph/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: testQuery,
          top_k: 6,
          confidence_threshold: 0.7
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setQaResponse(JSON.stringify(result, null, 2))
      }
    } catch (error) {
      setQaResponse('Error: ' + error)
    }
  }

  const testXMLPipeline = async () => {
    try {
      const response = await fetch('/graph/xml', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: 'Erstelle eine Streamworks XML-Konfiguration für Testing',
          template_type: 'custom-workflow',
          dry_run: true
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        setXmlResponse(JSON.stringify(result, null, 2))
      }
    } catch (error) {
      setXmlResponse('Error: ' + error)
    }
  }

  useEffect(() => {
    fetchSystemData()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'active':
      case 'true':
        return arvatoColors.success
      case 'degraded':
      case 'warning':
        return arvatoColors.warning
      case 'unhealthy':
      case 'error':
        return arvatoColors.error
      default:
        return arvatoColors.primary
    }
  }

  const tabs = [
    { 
      id: 'overview', 
      name: 'System Overview', 
      icon: ChartBarIcon,
      description: 'Enterprise System Status' 
    },
    { 
      id: 'pipelines', 
      name: 'AI Pipelines', 
      icon: CpuChipIcon,
      description: 'LangGraph Q&A & XML' 
    },
    { 
      id: 'documents', 
      name: 'Documents', 
      icon: DocumentTextIcon,
      description: 'Document Management' 
    },
    { 
      id: 'testing', 
      name: 'Live Testing', 
      icon: BeakerIcon,
      description: 'Pipeline Testing' 
    },
    { 
      id: 'production', 
      name: 'Production', 
      icon: RocketLaunchIcon,
      description: 'Deployment Status' 
    },
    { 
      id: 'monitoring', 
      name: 'Monitoring', 
      icon: ServerIcon,
      description: 'Enterprise Monitoring' 
    }
  ]

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-xl shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-sm font-medium">System Status</p>
              <p className="text-2xl font-bold">{systemHealth?.status || 'Loading...'}</p>
            </div>
            <CheckBadgeIcon className="w-12 h-12 text-blue-200" />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6 rounded-xl shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-200 text-sm font-medium">Active Pipelines</p>
              <p className="text-2xl font-bold">{pipelineInfo?.active_pipelines.length || 0}</p>
            </div>
            <CpuChipIcon className="w-12 h-12 text-green-200" />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-r from-purple-600 to-purple-700 text-white p-6 rounded-xl shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-200 text-sm font-medium">Production Ready</p>
              <p className="text-2xl font-bold">{productionStatus?.production_ready ? 'YES' : 'NO'}</p>
            </div>
            <RocketLaunchIcon className="w-12 h-12 text-purple-200" />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-r from-orange-600 to-orange-700 text-white p-6 rounded-xl shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-200 text-sm font-medium">Version</p>
              <p className="text-2xl font-bold">{systemHealth?.version || '1.0.0'}</p>
            </div>
            <BuildingOfficeIcon className="w-12 h-12 text-orange-200" />
          </div>
        </motion.div>
      </div>

      {/* Enterprise Features Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center space-x-3 mb-4">
            <BoltIcon className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">Enterprise Features</h3>
          </div>
          <div className="space-y-3">
            {systemHealth?.features && Object.entries(systemHealth.features).map(([feature, enabled]) => (
              <div key={feature} className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400 capitalize">
                  {feature.replace(/_/g, ' ')}
                </span>
                <div className={`w-3 h-3 rounded-full ${enabled ? 'bg-green-500' : 'bg-red-500'}`} />
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center space-x-3 mb-4">
            <ServerIcon className="w-6 h-6 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">Service Health</h3>
          </div>
          <div className="space-y-3">
            {systemHealth?.services && Object.entries(systemHealth.services).map(([service, status]) => (
              <div key={service} className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400 capitalize">
                  {service.replace(/_/g, ' ')}
                </span>
                <span 
                  className={`px-2 py-1 rounded-full text-xs font-medium text-white`}
                  style={{ backgroundColor: getStatusColor(status) }}
                >
                  {status}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )

  const renderPipelines = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {pipelineInfo?.pipelines.map((pipeline, index) => (
          <motion.div
            key={pipeline.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <CpuChipIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 uppercase">
                    {pipeline.name} Pipeline
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Phase {pipeline.phase}</p>
                </div>
              </div>
              <span 
                className={`px-3 py-1 rounded-full text-xs font-medium text-white`}
                style={{ backgroundColor: getStatusColor(pipeline.status) }}
              >
                {pipeline.status}
              </span>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{pipeline.description}</p>
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Endpoints:</p>
              {pipeline.endpoints.map(endpoint => (
                <code key={endpoint} className="block bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-xs">
                  {endpoint}
                </code>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )

  const renderTesting = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Q&A Pipeline Test */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center space-x-3 mb-4">
            <BeakerIcon className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">Q&A Pipeline Test</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Test Query:
              </label>
              <input
                type="text"
                value={testQuery}
                onChange={(e) => setTestQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                placeholder="Enter your question..."
              />
            </div>
            <button
              onClick={testQAPipeline}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
            >
              <PlayIcon className="w-4 h-4" />
              <span>Test Q&A Pipeline</span>
            </button>
            {qaResponse && (
              <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                <pre className="text-xs overflow-auto max-h-64 text-gray-800 dark:text-gray-200">
                  {qaResponse}
                </pre>
              </div>
            )}
          </div>
        </motion.div>

        {/* XML Pipeline Test */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center space-x-3 mb-4">
            <CodeBracketSquareIcon className="w-6 h-6 text-orange-600" />
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">XML Pipeline Test</h3>
          </div>
          <div className="space-y-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Test XML generation with HITL workflow
            </p>
            <button
              onClick={testXMLPipeline}
              className="w-full bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
            >
              <PlayIcon className="w-4 h-4" />
              <span>Test XML Pipeline</span>
            </button>
            {xmlResponse && (
              <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                <pre className="text-xs overflow-auto max-h-64 text-gray-800 dark:text-gray-200">
                  {xmlResponse}
                </pre>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )

  const renderProduction = () => (
    <div className="space-y-6">
      {/* Production Status Banner */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`p-6 rounded-xl shadow-lg text-white ${
          productionStatus?.status === 'ENTERPRISE-READY' 
            ? 'bg-gradient-to-r from-green-600 to-green-700'
            : 'bg-gradient-to-r from-yellow-600 to-yellow-700'
        }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
              <RocketLaunchIcon className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">{productionStatus?.status}</h2>
              <p className="text-lg opacity-90">Phase {productionStatus?.phase} Complete</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm opacity-80">Enterprise Grade</p>
            <p className="text-xl font-bold">{productionStatus?.enterprise_grade ? 'CERTIFIED' : 'PENDING'}</p>
          </div>
        </div>
      </motion.div>

      {/* Production Checks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {productionStatus?.checks && Object.entries(productionStatus.checks).map(([check, passed], index) => (
          <motion.div
            key={check}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                {check.replace(/_/g, ' ')}
              </span>
              <div className={`w-4 h-4 rounded-full ${passed ? 'bg-green-500' : 'bg-red-500'}`} />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Arvato Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                  <BuildingOfficeIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">Streamworks RAG Enterprise</h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Arvato Systems • Enterprise AI Platform</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={fetchSystemData}
                disabled={loading}
                className="flex items-center space-x-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                <ArrowPathIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
              
              <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                <ClockIcon className="w-4 h-4" />
                <span>Last update: {lastUpdate.toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Navigation */}
          <div className="w-full lg:w-80 space-y-2">
            <nav className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">Navigation</h2>
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  <div>
                    <div className="font-medium">{tab.name}</div>
                    <div className={`text-xs ${
                      activeTab === tab.id ? 'text-blue-200' : 'text-gray-500 dark:text-gray-400'
                    }`}>
                      {tab.description}
                    </div>
                  </div>
                </button>
              ))}
            </nav>

            {/* Quick Stats */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">Quick Stats</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">System Status</span>
                  <span className="font-medium" style={{ color: getStatusColor(systemHealth?.status || '') }}>
                    {systemHealth?.status || 'Loading...'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Active Pipelines</span>
                  <span className="font-medium text-green-600">
                    {pipelineInfo?.active_pipelines.length || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Production Ready</span>
                  <span className={`font-medium ${productionStatus?.production_ready ? 'text-green-600' : 'text-red-600'}`}>
                    {productionStatus?.production_ready ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                {activeTab === 'overview' && renderOverview()}
                {activeTab === 'pipelines' && renderPipelines()}
                {activeTab === 'documents' && (
                  <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
                    <div className="text-center">
                      <DocumentTextIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">Document Management</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        Document management features coming soon. Use the API endpoints for now.
                      </p>
                    </div>
                  </div>
                )}
                {activeTab === 'testing' && renderTesting()}
                {activeTab === 'production' && renderProduction()}
                {activeTab === 'monitoring' && (
                  <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
                    <div className="text-center">
                      <ServerIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">Enterprise Monitoring</h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        Prometheus & Grafana monitoring dashboards configured.
                      </p>
                      <div className="mt-4 space-y-2">
                        <p className="text-sm text-gray-500 dark:text-gray-400">Available endpoints:</p>
                        <code className="block bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-xs">
                          /production/metrics/enterprise
                        </code>
                        <code className="block bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-xs">
                          /production/health/comprehensive  
                        </code>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-4">
              <span>© 2024 Arvato Systems</span>
              <span>Streamworks RAG Enterprise Platform</span>
            </div>
            <div className="flex items-center space-x-2">
              <AcademicCapIcon className="w-4 h-4" />
              <span>Bachelor Thesis Project</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ArvatoEnterpriseDashboard