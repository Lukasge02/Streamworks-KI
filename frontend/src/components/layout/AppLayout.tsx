'use client'

import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { MessageSquare, FileText, Settings, FolderOpen } from 'lucide-react'
import { SettingsModal } from '@/components/settings/SettingsModal'

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [systemStatus, setSystemStatus] = useState<{status: string, backend_online: boolean}>({ 
    status: 'checking', 
    backend_online: false 
  })
  const [settingsOpen, setSettingsOpen] = useState(false)

  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health', {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
          mode: 'cors'
        })
        const data = await response.json()
        setSystemStatus({ status: 'healthy', backend_online: response.ok })
      } catch (error) {
        console.warn('Backend health check failed:', error)
        setSystemStatus({ status: 'error', backend_online: false })
      }
    }
    checkSystemHealth()
    const interval = setInterval(checkSystemHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  // Streamworks Logo Component
  const StreamworksLogo = () => (
    <Link href="/home" className="flex flex-col items-center hover:opacity-80 transition-opacity cursor-pointer">
      <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center mb-1">
        <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z" opacity="0.3"/>
          <path d="M2 12l3-3v2h6V9l3 3-3 3v-2H5v2l-3-3zm13 0l3-3v2h4v2h-4v2l-3-3z"/>
        </svg>
      </div>
      <div className="text-center">
        <div className="text-sm font-bold text-slate-800 dark:text-slate-200 tracking-wider">STREAMWORKS</div>
        <div className="text-xs text-slate-500 dark:text-slate-400 tracking-wide -mt-0.5">WORKLOAD AUTOMATION</div>
      </div>
    </Link>
  )

  // Clean header component
  const CleanHeader = () => (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 h-24 flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center space-x-3">
        <div>
          <h1 className="font-bold text-xl text-gray-900 dark:text-gray-100">
            Streamworks Self-Service
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Intelligente Dokumentenanalyse & XML-Generation
          </p>
        </div>
      </div>
      
      <div className="absolute left-1/2 transform -translate-x-1/2">
        <StreamworksLogo />
      </div>
      
      <div className="flex items-center space-x-4">
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium glass-effect transition-all duration-300 ${
          systemStatus.backend_online ? 'text-green-800 dark:text-green-300' : 'text-red-800 dark:text-red-300'
        }`}>
          <div className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
            systemStatus.backend_online ? 'status-online shadow-green-400/50 shadow-sm' : 'bg-red-500 animate-pulse'
          }`} />
          <span>{systemStatus.backend_online ? 'Backend Online' : 'Backend Offline'}</span>
        </div>
        <button 
          onClick={() => setSettingsOpen(true)}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 group"
          title="Einstellungen öffnen"
        >
          <Settings className="w-5 h-5 text-gray-500 group-hover:text-gray-700 dark:group-hover:text-gray-300 group-hover:rotate-90 transition-all duration-300" />
        </button>
      </div>
    </div>
  )

  // Sidebar Navigation
  const Sidebar = () => {
    const menuItems = [
      { id: 'documents', label: 'Dokumentenverwaltung', icon: FolderOpen, href: '/documents', description: 'Dokumente verwalten & synchronisieren' },
      { id: 'chat', label: 'Streamworks Chat', icon: MessageSquare, href: '/chat', description: 'KI-Assistent für Dokumentation' },
      { id: 'xml', label: 'XML Generator', icon: FileText, href: '/xml', description: 'Konfiguration erstellen' },
    ]
    
    return (
      <div className="w-72 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4 flex-shrink-0 overflow-y-auto">
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link
                key={item.id}
                href={item.href}
                className={`sidebar-item w-full flex items-start space-x-3 p-4 rounded-xl text-left group ${
                  isActive
                    ? 'bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 text-primary-600 dark:text-primary-400 shadow-lg border border-primary-200 dark:border-primary-800'
                    : 'hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 dark:hover:from-gray-700 dark:hover:to-gray-600 text-gray-700 dark:text-gray-300 hover:shadow-md'
                }`}
              >
                <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 transition-all duration-200 group-hover:scale-110 ${
                  isActive ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 group-hover:text-primary-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{item.label}</span>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{item.description}</div>
                </div>
              </Link>
            )
          })}
        </nav>
      </div>
    )
  }

  // Don't render sidebar on homepage
  if (pathname === '/' || pathname === '/home') {
    return <>{children}</>
  }

  return (
    <>
      <div className="h-screen overflow-hidden bg-gray-50 dark:bg-gray-900 flex flex-col">
        <CleanHeader />
        
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          
          <main className="flex-1 overflow-hidden">
            <motion.div
              key={pathname}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.15, ease: "easeOut" }}
              className="h-full"
            >
              {children}
            </motion.div>
          </main>
        </div>
      </div>
      
      {/* Settings Modal */}
      <SettingsModal 
        isOpen={settingsOpen} 
        onClose={() => setSettingsOpen(false)} 
      />
    </>
  )
}