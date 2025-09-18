/**
 * Register Page for Streamworks-KI RBAC System
 * Professional registration page with multi-step flow and legal compliance
 */

'use client'

import React, { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthContext } from '@/contexts/AuthContext'
import RegisterForm from '@/components/auth/RegisterForm'
import { toast } from 'sonner'

export default function RegisterPage() {
  const { isAuthenticated } = useAuthContext()
  const router = useRouter()
  const searchParams = useSearchParams()

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const redirectTo = searchParams.get('redirect') || '/dashboard'
      router.push(redirectTo)
    }
  }, [isAuthenticated, router, searchParams])

  const handleRegisterSuccess = () => {
    const redirectTo = searchParams.get('redirect') || '/dashboard'
    router.push(redirectTo)
  }

  const handleRegisterError = (error: string) => {
    toast.error(error)
  }

  // Don't render if already authenticated (prevents flash)
  if (isAuthenticated) {
    return (
      <div className="flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <RegisterForm
        onSuccess={handleRegisterSuccess}
        onError={handleRegisterError}
        redirectTo={searchParams.get('redirect') || '/dashboard'}
        showLoginLink={true}
      />

      {/* Features Overview */}
      <div className="mt-8 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-green-400"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-green-800 dark:text-green-200">
              Ihre Vorteile bei Streamworks
            </h3>
            <div className="mt-2 text-sm text-green-700 dark:text-green-300">
              <ul className="list-disc list-inside space-y-1">
                <li>Intelligente Dokumentenverarbeitung mit KI</li>
                <li>RAG-basierte Fragebeantwortung</li>
                <li>XML-Generierung mit Streamworks-Templates</li>
                <li>Enterprise-grade Sicherheit und Compliance</li>
                <li>24/7 Support für Business-Kunden</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Legal Compliance */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg">
        <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-2">
          Rechtliche Hinweise
        </h3>
        <div className="text-xs text-gray-600 dark:text-gray-400 space-y-2">
          <p>
            <strong>Datenschutz:</strong> Ihre persönlichen Daten werden gemäß DSGVO verarbeitet
            und ausschließlich für die Bereitstellung unserer Dienste verwendet.
          </p>
          <p>
            <strong>Compliance:</strong> Streamworks erfüllt alle relevanten Sicherheitsstandards
            für Enterprise-Anwendungen (ISO 27001, SOC 2).
          </p>
          <p>
            <strong>Support:</strong> Bei Fragen zur Registrierung oder Ihrem Account erreichen
            Sie uns unter <a href="mailto:support@streamworks.com" className="text-blue-600 hover:text-blue-500">support@streamworks.com</a>
          </p>
        </div>
      </div>
    </div>
  )
}