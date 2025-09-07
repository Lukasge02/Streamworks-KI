/**
 * Folder Creation Modal Component
 * Professional modal for creating new folders with validation
 */

import { useState, useCallback, useEffect } from 'react'
import { FolderIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { Modal, ModalBody, ModalFooter } from '@/components/ui/modal'
import { Button } from '@/components/ui/button'
import { t } from '@/lib/translations'
import { cn } from '@/lib/utils'

interface FolderCreateModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (name: string, description?: string) => Promise<void>
  parentFolderName?: string
  loading?: boolean
}

export function FolderCreateModal({
  isOpen,
  onClose,
  onConfirm,
  parentFolderName,
  loading = false
}: FolderCreateModalProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setName('')
      setDescription('')
      setErrors({})
      setIsSubmitting(false)
    }
  }, [isOpen])

  const validateForm = useCallback(() => {
    const newErrors: Record<string, string> = {}

    if (!name.trim()) {
      newErrors.name = 'Ordnername ist erforderlich'
    } else if (name.trim().length < 2) {
      newErrors.name = 'Ordnername muss mindestens 2 Zeichen lang sein'
    } else if (name.trim().length > 100) {
      newErrors.name = 'Ordnername darf maximal 100 Zeichen lang sein'
    } else if (!/^[a-zA-Z0-9\s\-_.äöüÄÖÜß]+$/.test(name.trim())) {
      newErrors.name = 'Ordnername enthält ungültige Zeichen'
    }

    if (description.length > 500) {
      newErrors.description = 'Beschreibung darf maximal 500 Zeichen lang sein'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }, [name, description])

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm() || isSubmitting || loading) {
      return
    }

    setIsSubmitting(true)
    
    try {
      await onConfirm(name.trim(), description.trim() || undefined)
      onClose()
    } catch (error) {
      // Error handling is done by the parent component
      console.error('Failed to create folder:', error)
    } finally {
      setIsSubmitting(false)
    }
  }, [validateForm, isSubmitting, loading, onConfirm, name, description, onClose])

  const handleClose = useCallback(() => {
    if (!isSubmitting && !loading) {
      onClose()
    }
  }, [isSubmitting, loading, onClose])

  const canSubmit = name.trim().length > 0 && Object.keys(errors).length === 0 && !isSubmitting && !loading

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      size="md"
      closeOnOverlayClick={!isSubmitting && !loading}
      closeOnEscape={!isSubmitting && !loading}
      className="max-w-md"
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <FolderIcon className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {t('folders.createFolder')}
              </h2>
              {parentFolderName && (
                <p className="text-sm text-gray-600 mt-1">
                  in "{parentFolderName}"
                </p>
              )}
            </div>
          </div>
          <button
            onClick={handleClose}
            disabled={isSubmitting || loading}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label={t('general.close')}
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Folder Name */}
          <div>
            <label htmlFor="folderName" className="block text-sm font-medium text-gray-700 mb-2">
              {t('folders.folderName')} *
            </label>
            <input
              id="folderName"
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value)
                if (errors.name) {
                  setErrors(prev => ({ ...prev, name: '' }))
                }
              }}
              onBlur={validateForm}
              disabled={isSubmitting || loading}
              className={cn(
                "w-full px-3 py-2 border rounded-lg",
                "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "transition-colors",
                errors.name
                  ? "border-red-300 bg-red-50"
                  : "border-gray-300 hover:border-gray-400"
              )}
              placeholder="z.B. Projektdokumente"
              maxLength={100}
              autoFocus
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600" role="alert">
                {errors.name}
              </p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              {name.length}/100 Zeichen
            </p>
          </div>

          {/* Description (Optional) */}
          <div>
            <label htmlFor="folderDescription" className="block text-sm font-medium text-gray-700 mb-2">
              {t('folders.folderDescription')} <span className="text-gray-500">(optional)</span>
            </label>
            <textarea
              id="folderDescription"
              value={description}
              onChange={(e) => {
                setDescription(e.target.value)
                if (errors.description) {
                  setErrors(prev => ({ ...prev, description: '' }))
                }
              }}
              onBlur={validateForm}
              disabled={isSubmitting || loading}
              className={cn(
                "w-full px-3 py-2 border rounded-lg resize-none",
                "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "transition-colors",
                errors.description
                  ? "border-red-300 bg-red-50"
                  : "border-gray-300 hover:border-gray-400"
              )}
              placeholder="Beschreibung des Ordners..."
              maxLength={500}
              rows={3}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600" role="alert">
                {errors.description}
              </p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              {description.length}/500 Zeichen
            </p>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSubmitting || loading}
            >
              {t('general.cancel')}
            </Button>
            <Button
              type="submit"
              disabled={!canSubmit}
              className="inline-flex items-center"
            >
              {(isSubmitting || loading) && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
              )}
              {t('general.create')}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  )
}