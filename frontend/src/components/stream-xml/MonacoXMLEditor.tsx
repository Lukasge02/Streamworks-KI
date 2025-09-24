'use client'

import React, { useEffect, useRef, useState } from 'react'
import { Editor } from '@monaco-editor/react'
import { toast } from 'sonner'
import { Loader2, AlertTriangle, CheckCircle } from 'lucide-react'

/**
 * 🎨 Monaco XML Editor - Professional XML editing experience
 *
 * Features:
 * - XML syntax highlighting
 * - Streamworks XML schema validation
 * - Auto-formatting and IntelliSense
 * - Error markers and live validation
 * - Multiple themes support
 */

interface MonacoXMLEditorProps {
  value: string
  onChange: (value: string) => void
  language?: string
  theme?: 'vs-light' | 'vs-dark' | 'hc-black'
  options?: any
  height?: string | number
  width?: string | number
  onMount?: (editor: any, monaco: any) => void
}

export function MonacoXMLEditor({
  value,
  onChange,
  language = 'xml',
  theme = 'vs-light',
  options = {},
  height = '100%',
  width = '100%',
  onMount
}: MonacoXMLEditorProps) {
  const editorRef = useRef<any>(null)
  const monacoRef = useRef<any>(null)
  const [isValidXML, setIsValidXML] = useState(true)
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Streamworks XML Schema definition
  const streamWorksSchema = `
    <?xml version="1.0" encoding="UTF-8"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
      <xs:element name="ExportableStream">
        <xs:complexType>
          <xs:sequence>
            <xs:element name="Stream" type="StreamType"/>
          </xs:sequence>
        </xs:complexType>
      </xs:element>

      <xs:complexType name="StreamType">
        <xs:sequence>
          <xs:element name="StreamName" type="xs:string"/>
          <xs:element name="StreamDocumentation" type="xs:string"/>
          <xs:element name="ShortDescription" type="xs:string"/>
          <xs:element name="Jobs" type="JobsType"/>
        </xs:sequence>
      </xs:complexType>

      <xs:complexType name="JobsType">
        <xs:sequence>
          <xs:element name="Job" type="JobType" maxOccurs="unbounded"/>
        </xs:sequence>
      </xs:complexType>
    </xs:schema>
  `

  // Default Monaco editor options
  const defaultOptions = {
    selectOnLineNumbers: true,
    minimap: { enabled: true },
    fontSize: 14,
    lineNumbers: 'on' as const,
    wordWrap: 'on' as const,
    automaticLayout: true,
    scrollBeyondLastLine: false,
    folding: true,
    renderLineHighlight: 'all' as const,
    cursorBlinking: 'blink' as const,
    multiCursorModifier: 'ctrlCmd' as const,
    formatOnPaste: true,
    formatOnType: true,
    bracketMatching: 'always' as const,
    autoIndent: 'full' as const,
    tabSize: 2,
    insertSpaces: true,
    ...options
  }

  // Validate XML content
  const validateXML = (xmlContent: string) => {
    try {
      if (!xmlContent.trim()) {
        setIsValidXML(true)
        setValidationErrors([])
        return
      }

      // Basic XML parsing validation
      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(xmlContent, 'text/xml')

      const parseError = xmlDoc.getElementsByTagName('parsererror')
      if (parseError.length > 0) {
        const errorText = parseError[0].textContent || 'XML parsing error'
        setIsValidXML(false)
        setValidationErrors([errorText])
        return
      }

      // Streamworks specific validation
      const errors: string[] = []

      // Check for required root element
      if (!xmlDoc.querySelector('ExportableStream')) {
        errors.push('Missing required root element: ExportableStream')
      }

      // Check for required Stream element
      if (!xmlDoc.querySelector('Stream')) {
        errors.push('Missing required element: Stream')
      }

      // Check for required StreamName
      if (!xmlDoc.querySelector('StreamName')) {
        errors.push('Missing required element: StreamName')
      }

      // Check for Jobs section
      if (!xmlDoc.querySelector('Jobs')) {
        errors.push('Missing required element: Jobs')
      }

      setIsValidXML(errors.length === 0)
      setValidationErrors(errors)

    } catch (error) {
      setIsValidXML(false)
      setValidationErrors(['Invalid XML format'])
    }
  }

  // Handle editor mounting
  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor
    monacoRef.current = monaco
    setIsLoading(false)

    // Configure XML language features
    monaco.languages.setLanguageConfiguration('xml', {
      comments: {
        blockComment: ['<!--', '-->']
      },
      brackets: [
        ['<', '>']
      ],
      autoClosingPairs: [
        { open: '<', close: '>' },
        { open: '"', close: '"' },
        { open: "'", close: "'" }
      ],
      surroundingPairs: [
        { open: '<', close: '>' },
        { open: '"', close: '"' },
        { open: "'", close: "'" }
      ]
    })

    // Add Streamworks XML snippets
    monaco.languages.registerCompletionItemProvider('xml', {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions = [
          {
            label: 'ExportableStream',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: `<ExportableStream>
  <Stream>
    <StreamName>\${1:MyStream}</StreamName>
    <StreamDocumentation><![CDATA[\${2:Stream description}]]></StreamDocumentation>
    <ShortDescription><![CDATA[\${3:Short description}]]></ShortDescription>
    <Jobs>
      <Job>
        <JobName>\${4:JobName}</JobName>
        <JobType>\${5:STANDARD}</JobType>
      </Job>
    </Jobs>
  </Stream>
</ExportableStream>`,
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Streamworks ExportableStream template'
          },
          {
            label: 'Job',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: `<Job>
  <JobName>\${1:JobName}</JobName>
  <JobType>\${2:STANDARD}</JobType>
  <JobDescription><![CDATA[\${3:Job description}]]></JobDescription>
</Job>`,
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Streamworks Job template'
          }
        ]

        return { suggestions }
      }
    })

    // Validate XML on content change
    editor.onDidChangeModelContent(() => {
      const content = editor.getValue()
      validateXML(content)
    })

    // Initial validation
    validateXML(value)

    // Call custom onMount if provided
    if (onMount) {
      onMount(editor, monaco)
    }
  }

  // Handle value changes
  const handleEditorChange = (newValue: string | undefined) => {
    if (newValue !== undefined) {
      onChange(newValue)
    }
  }

  // Format XML content
  const formatXML = () => {
    if (editorRef.current) {
      editorRef.current.getAction('editor.action.formatDocument').run()
      toast.success('XML formatiert')
    }
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeydown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + S to format
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault()
        formatXML()
      }
    }

    window.addEventListener('keydown', handleKeydown)
    return () => window.removeEventListener('keydown', handleKeydown)
  }, [])

  return (
    <div className="relative h-full w-full">
      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-10">
          <div className="flex items-center gap-2 text-gray-600">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>XML Editor wird geladen...</span>
          </div>
        </div>
      )}

      {/* Validation status bar */}
      <div className="absolute top-0 right-0 z-20 m-2">
        <div className={`flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-medium ${
          isValidXML
            ? 'bg-green-100 text-green-800 border border-green-200'
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          {isValidXML ? (
            <>
              <CheckCircle className="w-3 h-3" />
              <span>Valid XML</span>
            </>
          ) : (
            <>
              <AlertTriangle className="w-3 h-3" />
              <span>{validationErrors.length} Error(s)</span>
            </>
          )}
        </div>
      </div>

      {/* Monaco Editor */}
      <Editor
        height={height}
        width={width}
        language={language}
        theme={theme}
        value={value}
        options={defaultOptions}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        loading={
          <div className="flex items-center justify-center h-full">
            <div className="flex items-center gap-2 text-gray-600">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Editor wird initialisiert...</span>
            </div>
          </div>
        }
      />

      {/* Validation errors panel */}
      {!isValidXML && validationErrors.length > 0 && (
        <div className="absolute bottom-0 left-0 right-0 bg-red-50 border-t border-red-200 p-3 z-20">
          <h4 className="text-sm font-medium text-red-800 mb-2">XML Validation Errors:</h4>
          <ul className="text-sm text-red-700 space-y-1">
            {validationErrors.map((error, index) => (
              <li key={index} className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{error}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}