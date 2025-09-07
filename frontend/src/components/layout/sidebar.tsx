'use client'

import { motion } from 'framer-motion'
import { Upload, MessageSquare, FileText, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState, useEffect } from 'react'

interface SidebarProps {
  activePanel: string
  onPanelChange: (panel: 'upload' | 'chat' | 'documents') => void
}

interface SystemStats {
  total_documents: number
  total_chunks: number
  vector_store_status: string
}

export function Sidebar({ activePanel, onPanelChange }: SidebarProps) {
  const [stats, setStats] = useState<SystemStats>({
    total_documents: 0,
    total_chunks: 0,
    vector_store_status: 'loading'
  })

  const loadStats = async () => {
    try {
      const response = await fetch('/api/admin/stats')
      if (response.ok) {
        const data = await response.json()
        setStats({
          total_documents: data.vectorstore?.total_documents || 0,
          total_chunks: data.vectorstore?.total_chunks || 0,
          vector_store_status: 'active'
        })
      }
    } catch (error) {
      console.error('Failed to load stats:', error)
      setStats(prev => ({ ...prev, vector_store_status: 'error' }))
    }
  }

  useEffect(() => {
    loadStats()
    const interval = setInterval(loadStats, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const menuItems = [
    {
      id: 'upload',
      label: 'Upload Documents',
      icon: Upload,
      description: 'Docling Processing'
    },
    {
      id: 'chat',
      label: 'RAG Chat',
      icon: MessageSquare,
      description: 'Q&A with Sources'
    },
    {
      id: 'documents',
      label: 'Document Library',
      icon: FileText,
      description: 'Manage Chunks'
    }
  ]

  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4"
    >
      <nav className="space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = activePanel === item.id
          
          return (
            <motion.button
              key={item.id}
              onClick={() => onPanelChange(item.id as any)}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                'w-full flex items-start space-x-3 p-3 rounded-lg text-left transition-colors',
                isActive
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 border border-primary-200 dark:border-primary-700'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
              )}
            >
              <Icon className={cn(
                'w-5 h-5 mt-0.5 flex-shrink-0',
                isActive 
                  ? 'text-primary-600 dark:text-primary-400' 
                  : 'text-gray-500 dark:text-gray-400'
              )} />
              <div className="min-w-0">
                <div className={cn(
                  'font-medium text-sm',
                  isActive
                    ? 'text-primary-700 dark:text-primary-300'
                    : 'text-gray-900 dark:text-gray-100'
                )}>
                  {item.label}
                </div>
                <div className={cn(
                  'text-xs mt-0.5',
                  isActive
                    ? 'text-primary-600 dark:text-primary-400'
                    : 'text-gray-500 dark:text-gray-400'
                )}>
                  {item.description}
                </div>
              </div>
            </motion.button>
          )
        })}
      </nav>

      {/* System Stats */}
      <div className="mt-8 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
          System Status
        </h3>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Vector Store</span>
            <span className={`font-medium ${
              stats.vector_store_status === 'active' ? 'text-green-600' : 
              stats.vector_store_status === 'error' ? 'text-red-600' : 'text-yellow-600'
            }`}>
              {stats.vector_store_status === 'active' ? 'Active' : 
               stats.vector_store_status === 'error' ? 'Error' : 'Loading...'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Embeddings</span>
            <span className="text-green-600 font-medium">Ready</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Documents</span>
            <span className="text-gray-900 dark:text-gray-100 font-medium">{stats.total_documents}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Chunks</span>
            <span className="text-gray-900 dark:text-gray-100 font-medium">{stats.total_chunks}</span>
          </div>
        </div>
      </div>
    </motion.aside>
  )
}