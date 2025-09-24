'use client'

import React, { useState } from 'react'
import {
  Download,
  Copy,
  Eye,
  Code2,
  Palette,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Settings,
  FileDown,
  Share2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

/**
 * 🔧 XML Toolbar - Professional XML operations
 *
 * Features:
 * - Download XML as file
 * - Copy to clipboard
 * - Format XML
 * - Validate XML
 * - Theme switching
 * - Export options
 */

interface XMLToolbarProps {
  xmlContent: string
  onFormat: (formattedXml: string) => void
  sessionId: string
  streamName: string
}

export function XMLToolbar({
  xmlContent,
  onFormat,
  sessionId,
  streamName
}: XMLToolbarProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const [isCopying, setIsCopying] = useState(false)

  // Format XML with proper indentation
  const formatXML = () => {
    try {
      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(xmlContent, 'text/xml')

      // Check for parsing errors
      const parseError = xmlDoc.getElementsByTagName('parsererror')
      if (parseError.length > 0) {
        toast.error('XML kann nicht formatiert werden', {
          description: 'Ungültige XML-Syntax gefunden'
        })
        return
      }

      // Format XML with indentation
      const serializer = new XMLSerializer()
      const xmlString = serializer.serializeToString(xmlDoc)

      // Add proper indentation
      const formatted = formatXMLString(xmlString)
      onFormat(formatted)

      toast.success('XML erfolgreich formatiert')
    } catch (error) {
      console.error('XML formatting error:', error)
      toast.error('Formatierung fehlgeschlagen')
    }
  }

  // Helper function to format XML string
  const formatXMLString = (xml: string): string => {
    const PADDING = '  ' // 2 spaces for indentation
    const reg = /(>)(<)(\/*)/g
    let formatted = xml.replace(reg, '$1\r\n$2$3')

    let pad = 0
    return formatted.split('\r\n').map((node: string) => {
      let indent = 0
      if (node.match(/.+<\/\w[^>]*>$/)) {
        indent = 0
      } else if (node.match(/^<\/\w/) && pad > 0) {
        pad -= 1
      } else if (node.match(/^<\w[^>]*[^\/]>.*$/)) {
        indent = 1
      } else {
        indent = 0
      }

      const padding = PADDING.repeat(pad)
      pad += indent
      return padding + node
    }).join('\r\n')
  }

  // Download XML as file
  const downloadXML = async () => {
    try {
      setIsDownloading(true)

      // Generate safe filename
      const safeStreamName = streamName.replace(/[^a-zA-Z0-9_-]/g, '_')
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
      const filename = `${safeStreamName}_${timestamp}.xml`

      // Create blob and download
      const blob = new Blob([xmlContent], { type: 'application/xml' })
      const url = URL.createObjectURL(blob)

      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      toast.success('XML-Datei heruntergeladen', {
        description: filename
      })
    } catch (error) {
      console.error('Download error:', error)
      toast.error('Download fehlgeschlagen')
    } finally {
      setIsDownloading(false)
    }
  }

  // Copy XML to clipboard
  const copyToClipboard = async () => {
    try {
      setIsCopying(true)
      await navigator.clipboard.writeText(xmlContent)

      toast.success('XML in Zwischenablage kopiert', {
        description: `${xmlContent.length} Zeichen kopiert`
      })
    } catch (error) {
      console.error('Copy error:', error)
      toast.error('Kopieren fehlgeschlagen')
    } finally {
      setIsCopying(false)
    }
  }

  // Validate XML
  const validateXML = () => {
    try {
      const parser = new DOMParser()
      const xmlDoc = parser.parseFromString(xmlContent, 'text/xml')

      const parseError = xmlDoc.getElementsByTagName('parsererror')
      if (parseError.length > 0) {
        toast.error('XML Validation fehlgeschlagen', {
          description: parseError[0].textContent || 'Unbekannter Parsing-Fehler'
        })
        return
      }

      // Streamworks specific validation
      const errors: string[] = []

      if (!xmlDoc.querySelector('ExportableStream')) {
        errors.push('Fehlendes Root-Element: ExportableStream')
      }

      if (!xmlDoc.querySelector('Stream')) {
        errors.push('Fehlendes Element: Stream')
      }

      if (!xmlDoc.querySelector('StreamName')) {
        errors.push('Fehlendes Element: StreamName')
      }

      if (errors.length > 0) {
        toast.error('Streamworks Validation fehlgeschlagen', {
          description: errors.join(', ')
        })
      } else {
        toast.success('XML Validation erfolgreich', {
          description: 'Alle Streamworks-Anforderungen erfüllt'
        })
      }
    } catch (error) {
      console.error('Validation error:', error)
      toast.error('Validation fehlgeschlagen')
    }
  }

  // Share XML (placeholder for future implementation)
  const shareXML = () => {
    toast.info('Share-Funktion', {
      description: 'Wird in einer zukünftigen Version verfügbar sein'
    })
  }

  return (
    <div className="flex items-center gap-2">
      {/* Quick Actions */}
      <Button
        onClick={copyToClipboard}
        disabled={isCopying || !xmlContent.trim()}
        variant="outline"
        size="sm"
        className="flex items-center gap-2"
      >
        {isCopying ? (
          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-current" />
        ) : (
          <Copy className="w-3 h-3" />
        )}
        <span className="hidden sm:inline">Kopieren</span>
      </Button>

      <Button
        onClick={downloadXML}
        disabled={isDownloading || !xmlContent.trim()}
        variant="outline"
        size="sm"
        className="flex items-center gap-2"
      >
        {isDownloading ? (
          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-current" />
        ) : (
          <Download className="w-3 h-3" />
        )}
        <span className="hidden sm:inline">Download</span>
      </Button>

      {/* More Options Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <Settings className="w-3 h-3" />
            <span className="hidden sm:inline ml-2">Mehr</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuItem onClick={formatXML} disabled={!xmlContent.trim()}>
            <Code2 className="w-4 h-4 mr-2" />
            XML formatieren
          </DropdownMenuItem>

          <DropdownMenuItem onClick={validateXML} disabled={!xmlContent.trim()}>
            <CheckCircle className="w-4 h-4 mr-2" />
            XML validieren
          </DropdownMenuItem>

          <DropdownMenuSeparator />

          <DropdownMenuItem onClick={shareXML} disabled={!xmlContent.trim()}>
            <Share2 className="w-4 h-4 mr-2" />
            XML teilen
          </DropdownMenuItem>

          <DropdownMenuItem
            onClick={() => window.open(`data:application/xml,${encodeURIComponent(xmlContent)}`, '_blank')}
            disabled={!xmlContent.trim()}
          >
            <Eye className="w-4 h-4 mr-2" />
            In neuem Tab öffnen
          </DropdownMenuItem>

          <DropdownMenuSeparator />

          <DropdownMenuItem
            onClick={() => {
              const stats = {
                lines: xmlContent.split('\n').length,
                characters: xmlContent.length,
                words: xmlContent.split(/\s+/).length,
                size: new Blob([xmlContent]).size
              }

              toast.info('XML Statistiken', {
                description: `${stats.lines} Zeilen, ${stats.characters} Zeichen, ${(stats.size / 1024).toFixed(1)} KB`
              })
            }}
            disabled={!xmlContent.trim()}
          >
            <AlertTriangle className="w-4 h-4 mr-2" />
            XML Statistiken
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}