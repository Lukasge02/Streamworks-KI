/**
 * Register Form Component for Streamworks-KI RBAC System
 * Multi-step registration form with password strength validation
 */

'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { EyeIcon, EyeSlashIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { useAuthContext } from '@/contexts/AuthContext'
import { RegisterFormProps, RegisterData } from '@/types/auth.types'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { clsx } from 'clsx'

interface PasswordStrength {
  score: number
  checks: {
    length: boolean
    uppercase: boolean
    lowercase: boolean
    number: boolean
    special: boolean
  }
}

/**
 * Professional registration form with multi-step flow and password strength validation
 */
export function RegisterForm({
  onSuccess,
  onError,
  redirectTo = '/dashboard',
  showLoginLink = true
}: RegisterFormProps) {
  const { register, isLoading } = useAuthContext()
  const router = useRouter()

  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState<RegisterData>({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    companyName: ''
  })

  const [errors, setErrors] = useState<Partial<RegisterData>>({})
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [acceptedTerms, setAcceptedTerms] = useState(false)

  // Password strength calculation
  const calculatePasswordStrength = (password: string): PasswordStrength => {
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?\":{}|<>]/.test(password)
    }

    const score = Object.values(checks).filter(Boolean).length
    return { score, checks }
  }

  const passwordStrength = calculatePasswordStrength(formData.password)

  // Real-time validation
  const validateField = (name: keyof RegisterData, value: string) => {
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
      case 'firstName':
        if (!value || value.trim().length < 2) {
          newErrors.firstName = 'Vorname muss mindestens 2 Zeichen lang sein'
        } else {
          delete newErrors.firstName
        }
        break
      case 'lastName':
        if (!value || value.trim().length < 2) {
          newErrors.lastName = 'Nachname muss mindestens 2 Zeichen lang sein'
        } else {
          delete newErrors.lastName
        }
        break
      case 'companyName':
        // Company name is optional
        delete newErrors.companyName
        break
    }

    setErrors(newErrors)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))

    // Real-time validation
    validateField(name as keyof RegisterData, value)
  }

  const handleNextStep = () => {
    // Validate current step
    if (step === 1) {
      validateField('firstName', formData.firstName)
      validateField('lastName', formData.lastName)
      validateField('companyName', formData.companyName || '')

      if (!formData.firstName || !formData.lastName) return
    }

    setStep(step + 1)
  }

  const handlePrevStep = () => {
    setStep(step - 1)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate all fields
    Object.keys(formData).forEach(key => {
      validateField(key as keyof RegisterData, formData[key as keyof RegisterData] || '')
    })

    // Check for errors
    if (Object.keys(errors).length > 0) return

    // Check terms acceptance
    if (!acceptedTerms) {
      alert('Bitte akzeptieren Sie die Nutzungsbedingungen')
      return
    }

    setIsSubmitting(true)

    try {
      await register(formData)

      // Success callback
      if (onSuccess && typeof onSuccess === 'function') {
        onSuccess({} as any)
      }

      // Redirect
      router.push(redirectTo)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registrierung fehlgeschlagen'

      if (onError) {
        onError(errorMessage)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const getPasswordStrengthColor = (score: number) => {
    if (score <= 2) return 'bg-red-500'
    if (score <= 3) return 'bg-yellow-500'
    if (score <= 4) return 'bg-blue-500'
    return 'bg-green-500'
  }

  const getPasswordStrengthText = (score: number) => {
    if (score <= 2) return 'Schwach'
    if (score <= 3) return 'Mittel'
    if (score <= 4) return 'Stark'
    return 'Sehr stark'
  }

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
          Konto erstellen
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-2 text-sm text-gray-600 dark:text-gray-400"
        >
          Erstellen Sie Ihr Streamworks-Account
        </motion.p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-center space-x-2">
          {[1, 2, 3].map((stepNumber) => (
            <div key={stepNumber} className="flex items-center">
              <div
                className={clsx(
                  'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                  step >= stepNumber
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                )}
              >
                {step > stepNumber ? <CheckIcon className="w-4 h-4" /> : stepNumber}
              </div>
              {stepNumber < 3 && (
                <div
                  className={clsx(
                    'w-8 h-0.5 mx-2',
                    step > stepNumber ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                  )}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Form */}
      <motion.form
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        onSubmit={handleSubmit}
        className="space-y-6"
      >
        {/* Step 1: Personal Information */}
        {step === 1 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            {/* First Name */}
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Vorname
              </label>
              <input
                id="firstName"
                name="firstName"
                type="text"
                required
                value={formData.firstName}
                onChange={handleChange}
                className={clsx(
                  'w-full px-4 py-3 rounded-lg border transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500',
                  errors.firstName
                    ? 'border-red-300 bg-red-50 dark:bg-red-900/20'
                    : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800',
                  'text-gray-900 dark:text-white placeholder-gray-400'
                )}
                placeholder="Max"
              />
              {errors.firstName && (
                <p className="mt-1 text-sm text-red-600">{errors.firstName}</p>
              )}
            </div>

            {/* Last Name */}
            <div>
              <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nachname
              </label>
              <input
                id="lastName"
                name="lastName"
                type="text"
                required
                value={formData.lastName}
                onChange={handleChange}
                className={clsx(
                  'w-full px-4 py-3 rounded-lg border transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500',
                  errors.lastName
                    ? 'border-red-300 bg-red-50 dark:bg-red-900/20'
                    : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800',
                  'text-gray-900 dark:text-white placeholder-gray-400'
                )}
                placeholder="Mustermann"
              />
              {errors.lastName && (
                <p className="mt-1 text-sm text-red-600">{errors.lastName}</p>
              )}
            </div>

            {/* Company Name (Optional) */}
            <div>
              <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Firmenname <span className="text-gray-500">(Optional)</span>
              </label>
              <input
                id="companyName"
                name="companyName"
                type="text"
                value={formData.companyName}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="ACME Corp"
              />
            </div>

            <button
              type="button"
              onClick={handleNextStep}
              disabled={!formData.firstName || !formData.lastName}
              className={clsx(
                'w-full py-3 px-4 rounded-lg font-medium text-white transition-all',
                formData.firstName && formData.lastName
                  ? 'bg-blue-600 hover:bg-blue-700'
                  : 'bg-gray-300 cursor-not-allowed'
              )}
            >
              Weiter
            </button>
          </motion.div>
        )}

        {/* Step 2: Account Details */}
        {step === 2 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-4"
          >
            {/* Email */}
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
                    ? 'border-red-300 bg-red-50 dark:bg-red-900/20'
                    : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800',
                  'text-gray-900 dark:text-white placeholder-gray-400'
                )}
                placeholder="max@firma.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Passwort
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className={clsx(
                    'w-full px-4 py-3 pr-12 rounded-lg border transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500',
                    errors.password
                      ? 'border-red-300 bg-red-50 dark:bg-red-900/20'
                      : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800',
                    'text-gray-900 dark:text-white placeholder-gray-400'
                  )}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3"
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>

              {/* Password Strength Indicator */}
              {formData.password && (
                <div className="mt-2">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className={clsx(
                          'h-2 rounded-full transition-all',
                          getPasswordStrengthColor(passwordStrength.score)
                        )}
                        style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {getPasswordStrengthText(passwordStrength.score)}
                    </span>
                  </div>

                  {/* Password Requirements */}
                  <div className="grid grid-cols-2 gap-1 text-xs">
                    {Object.entries(passwordStrength.checks).map(([key, passed]) => (
                      <div key={key} className="flex items-center space-x-1">
                        {passed ? (
                          <CheckIcon className="w-3 h-3 text-green-500" />
                        ) : (
                          <XMarkIcon className="w-3 h-3 text-gray-400" />
                        )}
                        <span className={passed ? 'text-green-600' : 'text-gray-400'}>
                          {key === 'length' && 'Min. 8 Zeichen'}
                          {key === 'uppercase' && 'Großbuchstabe'}
                          {key === 'lowercase' && 'Kleinbuchstabe'}
                          {key === 'number' && 'Zahl'}
                          {key === 'special' && 'Sonderzeichen'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={handlePrevStep}
                className="flex-1 py-3 px-4 rounded-lg font-medium text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Zurück
              </button>
              <button
                type="button"
                onClick={handleNextStep}
                disabled={!formData.email || !formData.password || !!errors.email || !!errors.password}
                className={clsx(
                  'flex-1 py-3 px-4 rounded-lg font-medium text-white transition-all',
                  formData.email && formData.password && !errors.email && !errors.password
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-300 cursor-not-allowed'
                )}
              >
                Weiter
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 3: Confirmation */}
        {step === 3 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {/* Summary */}
            <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                Zusammenfassung
              </h3>
              <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                <p><strong>Name:</strong> {formData.firstName} {formData.lastName}</p>
                <p><strong>E-Mail:</strong> {formData.email}</p>
                {formData.companyName && (
                  <p><strong>Firma:</strong> {formData.companyName}</p>
                )}
              </div>
            </div>

            {/* Terms & Conditions */}
            <div className="flex items-start space-x-3">
              <input
                id="terms"
                type="checkbox"
                checked={acceptedTerms}
                onChange={(e) => setAcceptedTerms(e.target.checked)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="terms" className="text-sm text-gray-600 dark:text-gray-400">
                Ich akzeptiere die{' '}
                <a href="#" className="text-blue-600 hover:text-blue-500">
                  Nutzungsbedingungen
                </a>{' '}
                und{' '}
                <a href="#" className="text-blue-600 hover:text-blue-500">
                  Datenschutzerklärung
                </a>
              </label>
            </div>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={handlePrevStep}
                className="flex-1 py-3 px-4 rounded-lg font-medium text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Zurück
              </button>
              <button
                type="submit"
                disabled={!acceptedTerms || isLoading || isSubmitting}
                className={clsx(
                  'flex-1 py-3 px-4 rounded-lg font-medium text-white transition-all',
                  acceptedTerms && !isLoading && !isSubmitting
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-300 cursor-not-allowed'
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
                    Registrierung...
                  </div>
                ) : (
                  'Account erstellen'
                )}
              </button>
            </div>
          </motion.div>
        )}
      </motion.form>

      {/* Login Link */}
      {showLoginLink && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 text-center"
        >
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Bereits ein Account?{' '}
            <Link
              href="/auth/login"
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
            >
              Hier anmelden
            </Link>
          </p>
        </motion.div>
      )}
    </motion.div>
  )
}

export default RegisterForm