'use client'

import { useState, useEffect } from 'react'
import { 
  FileText, 
  MessageSquare, 
  Database, 
  FolderOpen, 
  HardDrive,
  RefreshCw,
  BarChart3,
  Users,
  Globe,
  Activity,
  Shield,
  Cpu
} from 'lucide-react'
import { useSystemStats } from '@/hooks/useSystemStats'

export default function HomePage() {
  const [systemStatus, setSystemStatus] = useState<{status: string, backend_online: boolean}>({ 
    status: 'checking', 
    backend_online: false 
  })
  
  const { stats, loading: statsLoading, error: statsError, refreshStats } = useSystemStats(true)
  
  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/health', {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          }
        })
        
        if (response.ok) {
          setSystemStatus({ status: 'online', backend_online: true })
        } else {
          setSystemStatus({ status: 'offline', backend_online: false })
        }
      } catch (error) {
        setSystemStatus({ status: 'offline', backend_online: false })
      }
    }

    checkSystemHealth()
    const interval = setInterval(checkSystemHealth, 30000) // Check every 30 seconds
    
    return () => clearInterval(interval)
  }, [])

  // Helper function to format bytes
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // Live Dashboard Stats from API
  const dashboardStats = [
    { 
      name: 'Dokumente', 
      value: stats?.totalDocuments?.toString() || '–', 
      icon: FileText, 
      color: 'text-blue-600 bg-blue-50 border-blue-200',
      trend: '+12% diese Woche'
    },
    { 
      name: 'Verarbeitete Chunks', 
      value: stats?.totalChunks?.toString() || '–', 
      icon: Database, 
      color: 'text-green-600 bg-green-50 border-green-200',
      trend: `${stats?.processingJobs || 0} in Bearbeitung`
    },
    { 
      name: 'Aktive Ordner', 
      value: stats?.totalFolders?.toString() || '–', 
      icon: FolderOpen, 
      color: 'text-purple-600 bg-purple-50 border-purple-200',
      trend: 'Organisiert & strukturiert'
    },
    { 
      name: 'Speichernutzung', 
      value: stats ? formatBytes(stats.storageUsed) : '–', 
      icon: HardDrive, 
      color: 'text-orange-600 bg-orange-50 border-orange-200',
      trend: 'Optimiert für Performance'
    }
  ]

  // Current Features
  const currentFeatures = [
    {
      title: 'Dokumentenverwaltung',
      description: 'Enterprise-grade Dokumentenmanagement mit intelligenter OCR-Erkennung',
      icon: FolderOpen,
      href: '/documents',
      gradient: 'from-blue-600 to-blue-700'
    },
    {
      title: 'KI-gestützter Chat',
      description: 'Intelligenter Assistent für Dokumentenanalyse und Workflow-Automatisierung',
      icon: MessageSquare,
      href: '/chat', 
      gradient: 'from-green-600 to-green-700'
    },
    {
      title: 'XML Generator',
      description: 'Automatisierte Konfigurationserstellung für komplexe Workflows',
      icon: FileText,
      href: '/xml',
      gradient: 'from-purple-600 to-purple-700'
    }
  ]

  return (
    <div className="h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 overflow-hidden flex flex-col">
      {/* Background Pattern */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-50/50 to-slate-50/50" />
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23e2e8f0' fill-opacity='0.3'%3E%3Ccircle cx='30' cy='30' r='1.5'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />
      </div>

      {/* System Status - Top Right */}
      <div className="absolute top-0 right-0 p-6 z-10">
        <div className="flex items-center space-x-2">
          <div className="flex items-center px-3 py-1.5 bg-green-50 border border-green-200 rounded-full">
            <div className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            <span className="text-xs font-medium text-green-700">System Online</span>
          </div>
          <button 
            onClick={refreshStats}
            className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="relative flex-1 flex flex-col">
        {/* Center - Hero Section */}
        <div className="flex-1 flex flex-col justify-center items-center px-6">
          {/* Logo - Even Bigger */}
          <div className="flex justify-center mb-8">
            <img src="/streamworks-produktlogo.png" alt="Streamworks" className="h-48 w-auto" />
          </div>

          <h1 className="text-6xl font-bold text-gray-900 mb-6 text-center">
            Willkommen bei <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Streamworks-KI</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl text-center">
            Enterprise-grade KI-Plattform für intelligente Dokumentenanalyse und automatisierte Workflows
          </p>

          {/* Login Buttons - Centered */}
          <div className="flex items-center space-x-4">
            <button 
              className="px-8 py-3 text-lg font-medium text-gray-700 hover:text-gray-900 transition-colors border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Anmelden
            </button>
            <button 
              className="px-8 py-3 bg-blue-600 text-white text-lg font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
            >
              Registrieren
            </button>
          </div>
        </div>

        {/* Bottom - Modules Section */}
        <div className="px-6 pb-8">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 text-center mb-6">Verfügbare Module</h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              {currentFeatures.map((feature, index) => (
                <div 
                  key={feature.title}
                  className="bg-white/90 backdrop-blur-sm rounded-xl border border-gray-200/60 p-6 shadow-sm hover:shadow-lg transition-all duration-300 hover:scale-105"
                >
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.gradient} text-white mb-4`}>
                    <feature.icon className="w-6 h-6" />
                  </div>
                  
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600 text-sm mb-4">{feature.description}</p>
                  
                  <button 
                    onClick={() => window.location.href = feature.href}
                    className={`w-full px-4 py-3 bg-gradient-to-r ${feature.gradient} text-white rounded-lg text-sm font-semibold hover:shadow-md transition-all duration-300`}
                  >
                    Modul öffnen
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}