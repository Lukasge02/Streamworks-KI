'use client'

import { useState, useCallback } from 'react'
// import { useToastContext } from '@/contexts/ToastContext'

interface ValidationRule {
  validate: (value: any) => boolean
  message: string
}

interface FieldValidation {
  rules: ValidationRule[]
  value?: any
}

interface FormValidationConfig {
  [key: string]: ValidationRule[]
}

export function useFormValidation(config: FormValidationConfig) {
  // const toast = useToastContext() // Temporarily disabled
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  const validateField = useCallback((fieldName: string, value: any) => {
    const rules = config[fieldName] || []
    
    for (const rule of rules) {
      if (!rule.validate(value)) {
        setErrors(prev => ({ ...prev, [fieldName]: rule.message }))
        return false
      }
    }
    
    setErrors(prev => {
      const newErrors = { ...prev }
      delete newErrors[fieldName]
      return newErrors
    })
    return true
  }, [config])

  const validateForm = useCallback((data: Record<string, any>) => {
    let isValid = true
    const newErrors: Record<string, string> = {}

    Object.keys(config).forEach(fieldName => {
      const value = data[fieldName]
      const rules = config[fieldName]
      
      for (const rule of rules) {
        if (!rule.validate(value)) {
          newErrors[fieldName] = rule.message
          isValid = false
          break
        }
      }
    })

    setErrors(newErrors)

    if (!isValid) {
      const errorCount = Object.keys(newErrors).length
      alert(`Formular unvollständig: Bitte korrigiere ${errorCount} Fehler, bevor du fortfährst`)
    }

    return isValid
  }, [config])

  const markFieldTouched = useCallback((fieldName: string) => {
    setTouched(prev => ({ ...prev, [fieldName]: true }))
  }, [])

  const clearErrors = useCallback(() => {
    setErrors({})
    setTouched({})
  }, [])

  const getFieldError = useCallback((fieldName: string) => {
    return touched[fieldName] ? errors[fieldName] : undefined
  }, [errors, touched])

  const hasError = useCallback((fieldName: string) => {
    return touched[fieldName] && !!errors[fieldName]
  }, [errors, touched])

  const isFormValid = useCallback(() => {
    return Object.keys(errors).length === 0
  }, [errors])

  return {
    errors,
    touched,
    validateField,
    validateForm,
    markFieldTouched,
    clearErrors,
    getFieldError,
    hasError,
    isFormValid
  }
}

// Common validation rules
export const ValidationRules = {
  required: (message = 'Dieses Feld ist erforderlich'): ValidationRule => ({
    validate: (value: any) => {
      if (typeof value === 'string') return value.trim().length > 0
      return value != null && value !== ''
    },
    message
  }),

  minLength: (min: number, message?: string): ValidationRule => ({
    validate: (value: string) => !value || value.length >= min,
    message: message || `Mindestens ${min} Zeichen erforderlich`
  }),

  maxLength: (max: number, message?: string): ValidationRule => ({
    validate: (value: string) => !value || value.length <= max,
    message: message || `Maximal ${max} Zeichen erlaubt`
  }),

  email: (message = 'Bitte gib eine gültige E-Mail-Adresse ein'): ValidationRule => ({
    validate: (value: string) => {
      if (!value) return true
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
    },
    message
  }),

  number: (message = 'Bitte gib eine gültige Zahl ein'): ValidationRule => ({
    validate: (value: any) => {
      if (!value && value !== 0) return true
      return !isNaN(Number(value))
    },
    message
  }),

  min: (min: number, message?: string): ValidationRule => ({
    validate: (value: any) => {
      if (!value && value !== 0) return true
      return Number(value) >= min
    },
    message: message || `Wert muss mindestens ${min} sein`
  }),

  max: (max: number, message?: string): ValidationRule => ({
    validate: (value: any) => {
      if (!value && value !== 0) return true
      return Number(value) <= max
    },
    message: message || `Wert darf maximal ${max} sein`
  }),

  url: (message = 'Bitte gib eine gültige URL ein'): ValidationRule => ({
    validate: (value: string) => {
      if (!value) return true
      try {
        new URL(value)
        return true
      } catch {
        return false
      }
    },
    message
  }),

  custom: (validator: (value: any) => boolean, message: string): ValidationRule => ({
    validate: validator,
    message
  })
}