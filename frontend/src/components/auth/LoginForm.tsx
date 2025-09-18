/**
 * Login Form Component for Streamworks-KI RBAC System
 * Professional login form with validation and enterprise design
 */

'use client'

import React, { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useAuthContext } from '@/contexts/AuthContext'
import { LoginFormProps, LoginCredentials } from '@/types/auth.types'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { clsx } from 'clsx'

/**
 * Professional login form with real-time validation and Streamworks branding
 */
export function LoginForm({
  onSuccess,
  onError,
  redirectTo = '/dashboard',
  showRegisterLink = true
}: LoginFormProps) {
  const { login, isLoading } = useAuthContext()
  const router = useRouter()

  const [formData, setFormData] = useState<LoginCredentials>({
    email: '',
    password: ''
  })

  const [errors, setErrors] = useState<Partial<LoginCredentials>>({})
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Real-time validation
  const validateField = (name: keyof LoginCredentials, value: string) => {
    const newErrors = { ...errors }

    switch (name) {
      case 'email':
        if (!value) {
          newErrors.email = 'E-Mail-Adresse ist erforderlich'
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          newErrors.email = 'Ungültige E-Mail-Adresse'
        } else {
          delete newErrors.email
        }
        break
      case 'password':
        if (!value) {
          newErrors.password = 'Passwort ist erforderlich'
        } else if (value.length < 6) {
          newErrors.password = 'Passwort muss mindestens 6 Zeichen lang sein'
        } else {
          delete newErrors.password
        }
        break
    }

    setErrors(newErrors)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))

    // Real-time validation
    validateField(name as keyof LoginCredentials, value)
  }

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    console.log('🚀 LOGIN ATTEMPT:', { email: formData.email, hasPassword: !!formData.password })

    // Synchronous validation - calculate errors directly
    const validationErrors: Partial<LoginCredentials> = {}

    // Validate email
    if (!formData.email) {
      validationErrors.email = 'E-Mail-Adresse ist erforderlich'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      validationErrors.email = 'Ungültige E-Mail-Adresse'
    }

    // Validate password
    if (!formData.password) {
      validationErrors.password = 'Passwort ist erforderlich'
    } else if (formData.password.length < 6) {
      validationErrors.password = 'Passwort muss mindestens 6 Zeichen lang sein'
    }

    console.log('📋 VALIDATION RESULT:', { errors: validationErrors, errorCount: Object.keys(validationErrors).length })

    // Update state with errors
    setErrors(validationErrors)

    // Check for errors
    if (Object.keys(validationErrors).length > 0) {
      console.log('❌ LOGIN BLOCKED - Validation errors:', validationErrors)
      return
    }

    console.log('✅ VALIDATION PASSED - Starting login request...')
    setIsSubmitting(true)

    try {
      console.log('🔄 Calling login function...')
      await login(formData)
      console.log('✅ Login function completed successfully!')

      // Success callback
      if (onSuccess && typeof onSuccess === 'function') {
        console.log('📞 Calling onSuccess callback...')
        onSuccess({} as any)
      }

      // Avoid immediate navigation during auth context updates
      console.log(`🚀 Starting navigation to: ${redirectTo}`)
      setTimeout(() => {
        console.log(`🎯 Executing router.push to: ${redirectTo}`)
        router.push(redirectTo)
      }, 100)
    } catch (error) {
      console.error('❌ LOGIN ERROR:', error)
      const errorMessage = error instanceof Error ? error.message : 'Anmeldung fehlgeschlagen'
      console.error('❌ LOGIN ERROR MESSAGE:', errorMessage)

      if (onError) {
        onError(errorMessage)
      }
    } finally {
      setIsSubmitting(false)
    }
  }, [formData, errors, login, onSuccess, onError, router, redirectTo])

  const isFormValid = formData.email && formData.password && Object.keys(errors).length === 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-md mx-auto"
    >
      {/* Header */}
      <div className="text-center mb-8">
        <motion.h1
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-3xl font-bold text-gray-900 dark:text-white"
        >
          Willkommen zurück
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-2 text-sm text-gray-600 dark:text-gray-400"
        >
          Melden Sie sich bei Ihrem Streamworks-Account an
        </motion.p>
      </div>

      {/* Form */}
      <motion.form
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        onSubmit={handleSubmit}
        className="space-y-6"
      >
        {/* Email Field */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            E-Mail-Adresse
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={formData.email}
            onChange={handleChange}
            className={clsx(
              'w-full px-4 py-3 rounded-lg border transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500',
              errors.email
                ? 'border-red-300 bg-red-50 dark:bg-red-900/20 dark:border-red-600'
                : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800',
              'text-gray-900 dark:text-white placeholder-gray-400'
            )}
            placeholder="ihre.email@firma.com"
            disabled={isLoading || isSubmitting}
          />
          {errors.email && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-1 text-sm text-red-600 dark:text-red-400"
            >
              {errors.email}
            </motion.p>
          )}
        </div>

        {/* Password Field */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Passwort
          </label>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              required
              value={formData.password}
              onChange={handleChange}
              className={clsx(
                'w-full px-4 py-3 pr-12 rounded-lg border transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500',
                errors.password
                  ? 'border-red-300 bg-red-50 dark:bg-red-900/20 dark:border-red-600'
                  : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800',
                'text-gray-900 dark:text-white placeholder-gray-400'
              )}
              placeholder="••••••••"
              disabled={isLoading || isSubmitting}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 flex items-center pr-3"
              disabled={isLoading || isSubmitting}
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              ) : (
                <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              )}
            </button>
          </div>
          {errors.password && (
            <motion.p
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-1 text-sm text-red-600 dark:text-red-400"
            >
              {errors.password}
            </motion.p>
          )}
        </div>

        {/* Submit Button */}
        <motion.button
          type="submit"
          disabled={!isFormValid || isLoading || isSubmitting}
          whileHover={{ scale: isFormValid ? 1.02 : 1 }}
          whileTap={{ scale: isFormValid ? 0.98 : 1 }}
          className={clsx(
            'w-full py-3 px-4 rounded-lg font-medium text-white transition-all duration-200',
            isFormValid && !isLoading && !isSubmitting
              ? 'bg-blue-600 hover:bg-blue-700 shadow-lg hover:shadow-xl'
              : 'bg-gray-300 dark:bg-gray-700 cursor-not-allowed',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          )}
        >
          {isLoading || isSubmitting ? (
            <div className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Anmelden...
            </div>
          ) : (
            'Anmelden'
          )}
        </motion.button>
      </motion.form>

      {/* Register Link */}
      {showRegisterLink && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 text-center"
        >
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Noch kein Account?{' '}
            <Link
              href="/auth/register"
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
            >
              Jetzt registrieren
            </Link>
          </p>
        </motion.div>
      )}

      {/* Demo Users (Development only) */}
      {process.env.NODE_ENV === 'development' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-8 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border"
        >
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Demo-Accounts (Development)
          </h3>
          <div className="space-y-2 text-xs">
            <div>
              <strong>Owner:</strong> owner@streamworks.dev / password123
            </div>
            <div>
              <strong>Admin:</strong> admin@streamworks.dev / password123
            </div>
            <div>
              <strong>Kunde:</strong> kunde@test.dev / password123
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default LoginForm