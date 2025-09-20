'use client'

import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { MessageSquare, FileText, Settings, FolderOpen, BarChart3 } from 'lucide-react'
import { SettingsModal } from '@/components/settings/SettingsModal'
import { useAuthContext } from '@/contexts/AuthContext'
import { UserAvatar } from '@/components/auth/UserAvatar'
import { PermissionGuard } from '@/components/auth/PermissionGuard'

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { isAuthenticated, user } = useAuthContext()
  const [systemStatus, setSystemStatus] = useState<{status: string, backend_online: boolean}>({
    status: 'checking',
    backend_online: false
  })
  const [settingsOpen, setSettingsOpen] = useState(false)

  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/health', {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
        const data = await response.json()
        setSystemStatus({ status: 'healthy', backend_online: response.ok })
      } catch (error) {
        console.warn('Backend health check failed:', error)
        setSystemStatus({ status: 'error', backend_online: false })
      }
    }
    checkSystemHealth()
    const interval = setInterval(checkSystemHealth, 15000)
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

        {/* User Avatar - only show when authenticated */}
        {isAuthenticated && user && (
          <UserAvatar
            user={user}
            size="md"
            showRole={true}
            showMenu={true}
          />
        )}

        {/* Login Link - only show when not authenticated */}
        {!isAuthenticated && (
          <Link
            href="/auth/login"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            Anmelden
          </Link>
        )}
      </div>
    </div>
  )

  // Sidebar Navigation
  const Sidebar = () => {
    const menuItems = [
      {
        id: 'documents',
        label: 'Dokumentenverwaltung',
        icon: FolderOpen,
        href: '/documents',
        description: 'Dokumente verwalten & synchronisieren',
        permission: 'documents.read' as const
      },
      {
        id: 'chat',
        label: 'Streamworks Chat',
        icon: MessageSquare,
        href: '/chat',
        description: 'KI-Assistent für Dokumentation',
        permission: 'system.read' as const
      },
      {
        id: 'xml',
        label: 'XML Generator',
        icon: FileText,
        href: '/xml',
        description: 'Konfiguration erstellen',
        permission: 'documents.write' as const
      },
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

          {/* Admin Panel Link - only for admins and owners */}
          <PermissionGuard
            requiredPermission="users.read"
            fallback={null}
          >
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700 mt-4">
              <Link
                href="/admin"
                className={`sidebar-item w-full flex items-start space-x-3 p-4 rounded-xl text-left group ${
                  pathname.startsWith('/admin')
                    ? 'bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/30 dark:to-orange-900/30 text-red-600 dark:text-red-400 shadow-lg border border-red-200 dark:border-red-800'
                    : 'hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 dark:hover:from-gray-700 dark:hover:to-gray-600 text-gray-700 dark:text-gray-300 hover:shadow-md'
                }`}
              >
                <Settings className={`w-5 h-5 mt-0.5 flex-shrink-0 transition-all duration-200 group-hover:scale-110 ${
                  pathname.startsWith('/admin') ? 'text-red-600 dark:text-red-400' : 'text-gray-500 group-hover:text-red-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">Administration</span>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Benutzer- und Systemverwaltung</div>
                </div>
              </Link>
            </div>
          </PermissionGuard>
        </nav>
      </div>
    )
  }

  // Don't render sidebar on homepage and auth pages
  if (pathname === '/' || pathname === '/home' || pathname.startsWith('/auth')) {
    return <>{children}</>
  }

  return (
    <>
      <div className="h-screen w-screen overflow-hidden bg-gray-50 dark:bg-gray-900 flex flex-col">
        <CleanHeader />

        <div className="flex flex-1 overflow-hidden min-w-0">
          <Sidebar />

          <main className="flex-1 overflow-hidden min-w-0">
            <motion.div
              key={pathname}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.15, ease: "easeOut" }}
              className="h-full w-full"
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