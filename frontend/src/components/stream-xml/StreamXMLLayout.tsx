'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  PanelLeftOpen,
  PanelLeftClose,
  Settings,
  Download,
  Copy,
  RefreshCw,
  Monitor,
  Smartphone,
  Code2,
  Eye
} from 'lucide-react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import ParameterOverview from '@/components/langextract-chat/components/ParameterOverview'
import { MonacoXMLEditor } from './MonacoXMLEditor'
import { XMLToolbar } from './XMLToolbar'
import { StreamXMLHeader } from './StreamXMLHeader'
import { MobileOptimizedTabs } from './MobileOptimizedTabs'
import { useSwipeGesture } from '@/hooks/useSwipeGesture'

/**
 * 🚀 StreamXMLLayout - The Ultimate Split-Screen XML Experience
 *
 * Professional split-screen layout with:
 * - Left: Enhanced Parameter Panel (40%)
 * - Right: Monaco XML Editor (60%)
 * - Responsive design with mobile optimization
 */

interface StreamXMLLayoutProps {
  sessionId: string
  xmlContent: string
  onXmlChange: (content: string) => void
  streamParameters: Record<string, any>
  jobParameters: Record<string, any>
  detectedJobType?: string | null
  criticalMissing: string[]
  completionPercentage: number
  parametersLoaded: boolean
  onRegenerateXML: () => Promise<void>
}

export function StreamXMLLayout({
  sessionId,
  xmlContent,
  onXmlChange,
  streamParameters,
  jobParameters,
  detectedJobType,
  criticalMissing,
  completionPercentage,
  parametersLoaded,
  onRegenerateXML
}: StreamXMLLayoutProps) {
  const router = useRouter()
  const [leftPanelOpen, setLeftPanelOpen] = useState(true)
  const [viewMode, setViewMode] = useState<'desktop' | 'mobile'>('desktop')
  const [mobileTab, setMobileTab] = useState<'parameters' | 'xml'>('parameters')
  const [isMobileFullscreen, setIsMobileFullscreen] = useState(false)

  // Calculate parameter counts
  const streamParamCount = Object.keys(streamParameters).length
  const jobParamCount = Object.keys(jobParameters).length
  const totalParams = streamParamCount + jobParamCount

  // Swipe gesture support for mobile navigation
  const { ref: swipeRef } = useSwipeGesture({
    onSwipeLeft: () => {
      if (mobileTab === 'parameters') {
        setMobileTab('xml')
      }
    },
    onSwipeRight: () => {
      if (mobileTab === 'xml') {
        setMobileTab('parameters')
      }
    },
    threshold: 60,
    velocityThreshold: 0.3
  })

  return (
    <div
      ref={swipeRef}
      className="h-screen flex flex-col bg-gray-50 touch-pan-x"
    >
      {/* Header */}
      <StreamXMLHeader
        sessionId={sessionId}
        streamName={streamParameters?.StreamName || streamParameters?.streamName}
        onBackToChat={() => router.push('/langextract')}
        onBackToStreams={() => router.push('/xml')}
      />

      {/* Enhanced Mobile Tab Navigation */}
      <MobileOptimizedTabs
        activeTab={mobileTab}
        onTabChange={setMobileTab}
        parameterCount={totalParams}
        completionPercentage={completionPercentage}
        isFullscreen={isMobileFullscreen}
        onToggleFullscreen={() => setIsMobileFullscreen(!isMobileFullscreen)}
      />

      {/* Main Content - Responsive Layout */}
      <div className={`flex-1 flex overflow-hidden ${
        isMobileFullscreen ? 'fixed inset-0 z-50 bg-white' : ''
      }`} style={{ height: 'calc(100vh - 160px)' }}>
        {/* Left Panel - Parameters */}
        <AnimatePresence>
          {(leftPanelOpen || mobileTab === 'parameters') && (
            <motion.div
              initial={{ width: 0 }}
              animate={{
                width: window.innerWidth < 1024 ? '100%' : '40%'
              }}
              exit={{ width: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className={`bg-white border-r border-gray-200 overflow-hidden ${
                mobileTab === 'xml' ? 'hidden lg:flex' : 'flex'
              } lg:max-w-[600px] lg:min-w-[400px]`}
            >
              <div className="w-full flex flex-col">
                {/* Parameter Panel Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-200">
                  <div className="flex items-center gap-3">
                    <Settings className="w-5 h-5 text-blue-600" />
                    <h2 className="font-semibold text-gray-900">Parameter</h2>
                    <Badge variant="secondary" className="text-xs">
                      {totalParams} Parameter
                    </Badge>
                  </div>

                  {/* Desktop Panel Toggle */}
                  <div className="hidden lg:flex items-center gap-2">
                    <Button
                      onClick={() => setLeftPanelOpen(!leftPanelOpen)}
                      variant="ghost"
                      size="sm"
                      title={leftPanelOpen ? 'Panel ausblenden' : 'Panel einblenden'}
                    >
                      {leftPanelOpen ? (
                        <PanelLeftClose className="w-4 h-4" />
                      ) : (
                        <PanelLeftOpen className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>

                {/* Parameter Content */}
                <div className="flex-1 overflow-hidden flex flex-col">
                  <ParameterOverview
                    streamParameters={streamParameters}
                    jobParameters={jobParameters}
                    completionPercentage={completionPercentage}
                    criticalMissing={criticalMissing}
                    currentSessionId={sessionId}
                    sessions={detectedJobType ? [{
                      session_id: sessionId,
                      job_type: detectedJobType,
                      stream_name: streamParameters?.StreamName || 'Unknown Stream',
                      completion_percentage: completionPercentage,
                      created_at: new Date().toISOString(),
                      last_activity: new Date().toISOString()
                    }] : []} // Create mock session for XML editor context
                    onParameterEdit={(paramName, currentValue) => {
                      console.log('Parameter edit:', paramName, currentValue)
                      // TODO: Implement parameter editing for XML context
                    }}
                    className="flex-1"
                  />

                  {/* XML Regenerate Button */}
                  <div className="border-t border-gray-200 p-4">
                    <Button
                      onClick={onRegenerateXML}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                      size="lg"
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      XML neu generieren
                    </Button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Right Panel - XML Editor */}
        <div className={`flex-1 flex flex-col bg-white overflow-hidden ${
          mobileTab === 'parameters' ? 'hidden lg:flex' : 'flex'
        }`}>
          {/* XML Editor Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <Code2 className="w-5 h-5 text-green-600" />
              <h2 className="font-semibold text-gray-900">XML Stream Editor</h2>
            </div>

            {/* XML Toolbar */}
            <XMLToolbar
              xmlContent={xmlContent}
              onFormat={(formatted) => onXmlChange(formatted)}
              sessionId={sessionId}
              streamName={streamParameters?.StreamName || 'Unknown_Stream'}
            />
          </div>

          {/* Monaco Editor */}
          <div className="flex-1 overflow-hidden">
            <MonacoXMLEditor
              value={xmlContent}
              onChange={onXmlChange}
              language="xml"
              theme="vs-light"
              options={{
                minimap: { enabled: true },
                fontSize: 14,
                lineNumbers: 'on',
                wordWrap: 'on',
                automaticLayout: true,
                scrollBeyondLastLine: false,
                folding: true,
                renderLineHighlight: 'all',
                cursorBlinking: 'blink',
                multiCursorModifier: 'ctrlCmd',
                formatOnPaste: true,
                formatOnType: true
              }}
            />
          </div>
        </div>

        {/* Floating Panel Toggle Button (when collapsed) */}
        {!leftPanelOpen && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="absolute left-4 top-1/2 transform -translate-y-1/2 z-10 hidden lg:block"
          >
            <Button
              onClick={() => setLeftPanelOpen(true)}
              className="rounded-full shadow-lg bg-blue-600 hover:bg-blue-700 text-white p-2"
              size="sm"
            >
              <PanelLeftOpen className="w-4 h-4" />
            </Button>
          </motion.div>
        )}
      </div>

      {/* Status Bar */}
      <div className="bg-gray-100 border-t border-gray-200 px-4 py-2">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <div className="flex items-center gap-4">
            <span>Session: {sessionId}</span>
            <span>Parameter: {totalParams} extrahiert</span>
            <span>Session Active</span>
          </div>
          <div className="flex items-center gap-2">
            <span>XML Zeilen: {xmlContent.split('\n').length}</span>
            <span>Zeichen: {xmlContent.length}</span>
          </div>
        </div>
      </div>

    </div>
  )
}