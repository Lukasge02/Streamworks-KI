'use client'

import { useState, useRef } from 'react'
import { X, Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import { XMLStreamAPI } from '@/services/xmlStreamApi'
import { XML_CUSTOMER_CATEGORIES } from '@/types/xml-stream.types'

interface XMLUploadModalProps {
  isOpen: boolean
  onClose: () => void
  onUploadComplete: () => void
}

export function XMLUploadModal({ isOpen, onClose, onUploadComplete }: XMLUploadModalProps) {
  const [files, setFiles] = useState<File[]>([])
  const [customerCategory, setCustomerCategory] = useState('Demo')
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})
  const [uploadResults, setUploadResults] = useState<Array<{file: string, success: boolean, message: string}>>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  if (!isOpen) return null

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const xmlFiles = Array.from(selectedFiles).filter(file => 
      file.name.toLowerCase().endsWith('.xml') || 
      file.type === 'application/xml' ||
      file.type === 'text/xml'
    )

    if (xmlFiles.length !== selectedFiles.length) {
      alert('Bitte wählen Sie nur XML-Dateien aus.')
    }

    setFiles(prev => [...prev, ...xmlFiles])
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const addTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags(prev => [...prev, tagInput.trim()])
      setTagInput('')
    }
  }

  const removeTag = (tag: string) => {
    setTags(prev => prev.filter(t => t !== tag))
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)
    setUploadResults([])
    setUploadProgress({})

    try {
      const results = []

      for (const file of files) {
        try {
          // Simulate progress
          setUploadProgress(prev => ({ ...prev, [file.name]: 50 }))

          const result = await XMLStreamAPI.uploadXMLStream(
            file,
            customerCategory,
            tags,
            'auto'
          )

          setUploadProgress(prev => ({ ...prev, [file.name]: 100 }))
          results.push({
            file: file.name,
            success: true,
            message: `Upload erfolgreich - Job ID: ${result.job_id}`
          })

        } catch (err) {
          results.push({
            file: file.name,
            success: false,
            message: err instanceof Error ? err.message : 'Upload fehlgeschlagen'
          })
        }
      }

      setUploadResults(results)

      // If all uploads successful, refresh the parent and close after delay
      if (results.every(r => r.success)) {
        setTimeout(() => {
          onUploadComplete()
          onClose()
          resetModal()
        }, 2000)
      }

    } catch (err) {
      alert('Upload fehlgeschlagen: ' + (err instanceof Error ? err.message : 'Unknown error'))
    } finally {
      setUploading(false)
    }
  }

  const resetModal = () => {
    setFiles([])
    setCustomerCategory('Demo')
    setTags([])
    setTagInput('')
    setUploadProgress({})
    setUploadResults([])
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            XML Streams hochladen
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* File Upload Area */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              XML-Dateien auswählen
            </label>
            
            <div
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault()
                handleFileSelect(e.dataTransfer.files)
              }}
            >
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400 mb-2">
                Klicken Sie hier oder ziehen Sie XML-Dateien hierher
              </p>
              <p className="text-sm text-gray-500">
                Unterstützte Formate: .xml
              </p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept=".xml,application/xml,text/xml"
              multiple
              onChange={(e) => handleFileSelect(e.target.files)}
              className="hidden"
            />
          </div>

          {/* Selected Files */}
          {files.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Ausgewählte Dateien ({files.length})
              </h3>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(file.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {uploadProgress[file.name] && (
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${uploadProgress[file.name]}%` }}
                          />
                        </div>
                      )}
                      
                      {!uploading && (
                        <button
                          onClick={() => removeFile(index)}
                          className="text-red-500 hover:text-red-700 p-1"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upload Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* Customer Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Kundenkategorie
              </label>
              <select
                value={customerCategory}
                onChange={(e) => setCustomerCategory(e.target.value)}
                className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500"
                disabled={uploading}
              >
                {XML_CUSTOMER_CATEGORIES.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tags
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addTag()}
                  placeholder="Tag hinzufügen..."
                  className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500"
                  disabled={uploading}
                />
                <button
                  onClick={addTag}
                  className="px-4 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg disabled:opacity-50"
                  disabled={uploading || !tagInput.trim()}
                >
                  +
                </button>
              </div>
              
              {tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center space-x-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                    >
                      <span>{tag}</span>
                      {!uploading && (
                        <button
                          onClick={() => removeTag(tag)}
                          className="text-blue-500 hover:text-blue-700"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      )}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Upload Results */}
          {uploadResults.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Upload-Ergebnisse
              </h3>
              <div className="space-y-2">
                {uploadResults.map((result, index) => (
                  <div
                    key={index}
                    className={`flex items-center space-x-3 p-3 rounded-lg ${
                      result.success
                        ? 'bg-green-50 border border-green-200'
                        : 'bg-red-50 border border-red-200'
                    }`}
                  >
                    {result.success ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-600" />
                    )}
                    <div className="flex-1">
                      <p className={`text-sm font-medium ${
                        result.success ? 'text-green-800' : 'text-red-800'
                      }`}>
                        {result.file}
                      </p>
                      <p className={`text-xs ${
                        result.success ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {result.message}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            disabled={uploading}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
          >
            Abbrechen
          </button>
          <button
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            className="flex items-center space-x-2 px-6 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white rounded-lg"
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                <span>Upload ({files.length})</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}