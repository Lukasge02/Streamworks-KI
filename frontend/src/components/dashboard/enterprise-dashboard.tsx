'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, Upload, MessageSquare, Search, Filter, Trash2, MoreVertical, RefreshCw, Activity } from 'lucide-react'
import { formatDate, formatBytes } from '@/lib/utils'

interface Document {
  id: string
  filename: string
  doctype: string
  upload_date: string
  size_bytes: number
  chunk_count: number
  status: string
}

export function EnterpriseDashboard() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDocs, setSelectedDocs] = useState<Set<string>>(new Set())
  
  const loadDocuments = async () => {
    try {
      console.log('🔄 Loading documents...')
      const response = await fetch('/api/documents')
      if (!response.ok) throw new Error('Failed to fetch')
      const data = await response.json()
      console.log('📄 Documents loaded:', data)
      setDocuments(data)
    } catch (error) {
      console.error('❌ Error loading documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const deleteDocument = async (docId: string) => {
    try {
      // Call backend API to delete completely (Supabase + files + vector store)
      const response = await fetch(`http://localhost:8000/api/documents/${docId}`, { 
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Delete failed')
      }
      
      const result = await response.json()
      console.log('✅ Document deleted successfully:', result)
      
      // Update UI after successful backend deletion
      setDocuments(prev => prev.filter(doc => doc.id !== docId))
      setSelectedDocs(prev => {
        const newSet = new Set(prev)
        newSet.delete(docId)
        return newSet
      })
    } catch (error) {
      console.error('❌ Delete failed:', error)
      alert(`Fehler beim Löschen: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`)
    }
  }

  useEffect(() => {
    loadDocuments()
    const interval = setInterval(loadDocuments, 5000) // Auto-refresh
    return () => clearInterval(interval)
  }, [])

  const filteredDocuments = documents.filter(doc => 
    !searchTerm || 
    doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.doctype.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading documents...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Document Management</h1>
            <p className="text-gray-600 dark:text-gray-400">Enterprise RAG System</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <span className="font-medium text-primary-600">{documents.length}</span> documents
            </div>
            <button onClick={loadDocuments} className="btn-secondary btn">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-primary-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-primary-900 dark:text-primary-100">{documents.length}</p>
                <p className="text-primary-600 text-sm">Documents</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
            <div className="flex items-center">
              <Activity className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                  {documents.reduce((sum, doc) => sum + doc.chunk_count, 0)}
                </p>
                <p className="text-green-600 text-sm">Chunks</p>
              </div>
            </div>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <div className="flex items-center">
              <Upload className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                  {formatBytes(documents.reduce((sum, doc) => sum + doc.size_bytes, 0))}
                </p>
                <p className="text-blue-600 text-sm">Total Size</p>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
            <div className="flex items-center">
              <MessageSquare className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">Ready</p>
                <p className="text-purple-600 text-sm">RAG Status</p>
              </div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Document Grid */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        {filteredDocuments.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {documents.length === 0 ? 'No documents uploaded' : 'No matching documents'}
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {documents.length === 0 
                ? 'Upload documents to get started with RAG'
                : 'Try adjusting your search terms'
              }
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {filteredDocuments.map((document, index) => (
              <motion.div
                key={document.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1">
                    <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
                      <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                    </div>
                    
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                        {document.filename.replace(/^[a-f0-9-]+_/, '').replace(/\.txt$/, '')}
                      </h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                        <span className="badge badge-primary">{document.doctype}</span>
                        <span>{formatDate(document.upload_date)}</span>
                        <span>{formatBytes(document.size_bytes)}</span>
                        <span>{document.chunk_count} chunks</span>
                        <span className="text-green-600 font-medium">{document.status}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => deleteDocument(document.id)}
                      className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 transition-colors"
                      title="Delete document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-500 transition-colors">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}