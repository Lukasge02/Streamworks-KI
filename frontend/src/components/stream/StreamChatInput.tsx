'use client'

import { useState } from 'react'
import { Send, MessageCircle, Sparkles, AlertCircle, CheckCircle, FileText } from 'lucide-react'

interface StreamChatInputProps {
  onStreamGenerated?: (formData: any) => void
}

export function StreamChatInput({ onStreamGenerated }: StreamChatInputProps) {
  const [chatInput, setChatInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [parsedData, setParsedData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [xmlResult, setXmlResult] = useState<string>('')

  const examples = [
    "Ich brauche einen Report RBDAGAIN alle 15 Min von 5:30 bis 23:00 auf PA1_100",
    "PowerShell Script täglich um 6 Uhr morgens mit Batch_PUR User",
    "File Processing Job stündlich, kein Wochenende, nach L10PESG26",
    "SAP Report ZESGHR01 Variante ZXY-UFA alle 30 Min auf HP1_ERP"
  ]

  const parseAndGenerate = async () => {
    if (!chatInput.trim()) return

    setLoading(true)
    setError(null)
    setParsedData(null)
    setXmlResult('')

    try {
      // Step 1: Parse natural language
      const parseResponse = await fetch('/api/simple-streams/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: chatInput })
      })
      
      const parseData = await parseResponse.json()
      
      if (!parseData.success) {
        throw new Error('Failed to parse request')
      }

      setParsedData(parseData.data)

      // Step 2: Generate XML
      const generateResponse = await fetch('/api/simple-streams/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parseData.data)
      })
      
      const generateData = await generateResponse.json()
      
      if (generateData.success) {
        setXmlResult(generateData.xml)
        onStreamGenerated?.(parseData.data)
      } else {
        setError(generateData.errors?.join(', ') || 'Generation failed')
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process request')
    } finally {
      setLoading(false)
    }
  }

  const selectExample = (example: string) => {
    setChatInput(example)
  }

  const downloadXML = () => {
    if (!xmlResult || !parsedData) return
    
    const blob = new Blob([xmlResult], { type: 'text/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${parsedData.stream_name || 'stream'}.xml`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center space-x-3">
            <MessageCircle className="w-8 h-8 text-blue-500" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Stream Chat Generator
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Beschreiben Sie Ihre Anforderungen in natürlicher Sprache
              </p>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Examples */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Beispiele (klicken zum Verwenden):
            </h3>
            <div className="grid grid-cols-1 gap-2">
              {examples.map((example, index) => (
                <button
                  key={index}
                  onClick={() => selectExample(example)}
                  className="text-left p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 text-sm transition-colors"
                >
                  "{example}"
                </button>
              ))}
            </div>
          </div>

          {/* Chat Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Beschreiben Sie Ihre Stream-Anforderung:
            </label>
            <div className="relative">
              <textarea
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="z.B. 'Ich brauche einen Report RBDAGAIN alle 15 Min von 5:30 bis 23:00'"
                className="w-full h-32 p-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none pr-12"
              />
              <button
                onClick={parseAndGenerate}
                disabled={loading || !chatInput.trim()}
                className="absolute bottom-3 right-3 p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <div>
                <p className="text-red-800 font-medium">Fehler</p>
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Parsed Data */}
          {parsedData && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <h3 className="text-green-800 font-medium">Erkannte Anforderungen</h3>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Stream Name:</span>
                  <div className="text-gray-600">{parsedData.stream_name}</div>
                </div>
                
                {parsedData.jobs?.length > 0 && (
                  <div>
                    <span className="font-medium text-gray-700">Job Typ:</span>
                    <div className="text-gray-600">{parsedData.jobs[0].type.toUpperCase()}</div>
                  </div>
                )}
                
                {parsedData.jobs?.[0]?.report && (
                  <div>
                    <span className="font-medium text-gray-700">Report:</span>
                    <div className="text-gray-600">{parsedData.jobs[0].report}</div>
                  </div>
                )}
                
                {parsedData.jobs?.[0]?.system && (
                  <div>
                    <span className="font-medium text-gray-700">System:</span>
                    <div className="text-gray-600">{parsedData.jobs[0].system}</div>
                  </div>
                )}
                
                {parsedData.schedule?.interval && (
                  <div>
                    <span className="font-medium text-gray-700">Intervall:</span>
                    <div className="text-gray-600">{parsedData.schedule.interval}</div>
                  </div>
                )}
                
                {parsedData.schedule?.timeframe_start && parsedData.schedule?.timeframe_end && (
                  <div>
                    <span className="font-medium text-gray-700">Zeitfenster:</span>
                    <div className="text-gray-600">
                      {parsedData.schedule.timeframe_start} - {parsedData.schedule.timeframe_end}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Generated XML */}
          {xmlResult && (
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-purple-600" />
                  <h3 className="text-gray-900 dark:text-white font-medium">
                    StreamWorks XML generiert
                  </h3>
                </div>
                <button
                  onClick={downloadXML}
                  className="flex items-center space-x-2 px-3 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm"
                >
                  <FileText className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
              
              <div className="bg-white dark:bg-gray-800 rounded border p-3 max-h-60 overflow-y-auto">
                <pre className="text-xs text-gray-800 dark:text-gray-200">
                  {xmlResult}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}