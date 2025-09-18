/**
 * Login Page for Streamworks-KI RBAC System
 * Professional login page with security features and demo accounts
 */

'use client'

import React, { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthContext } from '@/contexts/AuthContext'
import LoginForm from '@/components/auth/LoginForm'
import { toast } from 'sonner'

export default function LoginPage() {
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

  const handleLoginSuccess = () => {
    const redirectTo = searchParams.get('redirect') || '/dashboard'
    router.push(redirectTo)
  }

  const handleLoginError = (error: string) => {
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
      <LoginForm
        onSuccess={handleLoginSuccess}
        onError={handleLoginError}
        redirectTo={searchParams.get('redirect') || '/dashboard'}
        showRegisterLink={true}
      />

      {/* Security Notice */}
      <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-blue-400"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
              Sicherheitshinweis
            </h3>
            <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
              <p>
                Ihre Anmeldedaten werden verschlüsselt übertragen und sicher gespeichert.
                Bei Problemen mit der Anmeldung wenden Sie sich an den Administrator.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}