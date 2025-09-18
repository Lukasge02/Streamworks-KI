/**
 * Profile Page for Streamworks-KI RBAC System
 * User profile management with role information and password change
 */

'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  UserIcon,
  KeyIcon,
  ShieldCheckIcon,
  BuildingOfficeIcon,
  CalendarIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { useAuthContext } from '@/contexts/AuthContext'
import { ProfileUpdate, PasswordUpdate, ROLE_CONFIGS } from '@/types/auth.types'
import { toast } from 'sonner'
import { clsx } from 'clsx'

export default function ProfilePage() {
  const { user, updateProfile, changePassword, isLoading } = useAuthContext()

  const [profileData, setProfileData] = useState<ProfileUpdate>({
    firstName: user?.firstName || '',
    lastName: user?.lastName || ''
  })

  const [passwordData, setPasswordData] = useState<PasswordUpdate>({
    currentPassword: '',
    newPassword: ''
  })

  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile')
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false)
  const [isChangingPassword, setIsChangingPassword] = useState(false)

  if (!user) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-500">Lade Benutzerdaten...</p>
        </div>
      </div>
    )
  }

  const roleConfig = ROLE_CONFIGS[user.role]

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsUpdatingProfile(true)

    try {
      await updateProfile(profileData)
      toast.success('Profil erfolgreich aktualisiert')
    } catch (error) {
      toast.error('Profil-Update fehlgeschlagen')
    } finally {
      setIsUpdatingProfile(false)
    }
  }

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsChangingPassword(true)

    try {
      await changePassword(passwordData)
      setPasswordData({ currentPassword: '', newPassword: '' })
      toast.success('Passwort erfolgreich geändert')
    } catch (error) {
      toast.error('Passwort-Änderung fehlgeschlagen')
    } finally {
      setIsChangingPassword(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto py-8 px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Mein Profil
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            Verwalten Sie Ihre Kontoinformationen und Einstellungen
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* User Info Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1"
          >
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              {/* Avatar */}
              <div className="text-center mb-6">
                <div className={clsx(
                  'w-20 h-20 rounded-full mx-auto flex items-center justify-center text-white text-xl font-bold',
                  roleConfig.color
                )}>
                  {user.firstName.charAt(0)}{user.lastName.charAt(0)}
                </div>
                <h2 className="mt-3 text-xl font-semibold text-gray-900 dark:text-white">
                  {user.fullName}
                </h2>
                <p className="text-gray-500 dark:text-gray-400">
                  {user.email}
                </p>
              </div>

              {/* Role Info */}
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <ShieldCheckIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      Rolle
                    </p>
                    <div className="flex items-center space-x-2">
                      <div className={clsx('w-2 h-2 rounded-full', roleConfig.color)} />
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {roleConfig.label}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <CalendarIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      Mitglied seit
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(user.createdAt)}
                    </p>
                  </div>
                </div>

                {user.lastLoginAt && (
                  <div className="flex items-center space-x-3">
                    <ClockIcon className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        Letzte Anmeldung
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {formatDate(user.lastLoginAt)}
                      </p>
                    </div>
                  </div>
                )}

                {user.companyId && (
                  <div className="flex items-center space-x-3">
                    <BuildingOfficeIcon className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        Firma
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {user.companyId}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>

          {/* Settings Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-2"
          >
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              {/* Tabs */}
              <div className="border-b border-gray-200 dark:border-gray-700">
                <nav className="flex space-x-8 px-6">
                  <button
                    onClick={() => setActiveTab('profile')}
                    className={clsx(
                      'py-4 px-1 border-b-2 font-medium text-sm',
                      activeTab === 'profile'
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    )}
                  >
                    <UserIcon className="w-5 h-5 inline mr-2" />
                    Profil bearbeiten
                  </button>
                  <button
                    onClick={() => setActiveTab('password')}
                    className={clsx(
                      'py-4 px-1 border-b-2 font-medium text-sm',
                      activeTab === 'password'
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    )}
                  >
                    <KeyIcon className="w-5 h-5 inline mr-2" />
                    Passwort ändern
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {activeTab === 'profile' && (
                  <motion.form
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    onSubmit={handleProfileSubmit}
                    className="space-y-6"
                  >
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Vorname
                        </label>
                        <input
                          type="text"
                          id="firstName"
                          value={profileData.firstName}
                          onChange={(e) => setProfileData(prev => ({ ...prev, firstName: e.target.value }))}
                          className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>

                      <div>
                        <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Nachname
                        </label>
                        <input
                          type="text"
                          id="lastName"
                          value={profileData.lastName}
                          onChange={(e) => setProfileData(prev => ({ ...prev, lastName: e.target.value }))}
                          className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        E-Mail-Adresse
                      </label>
                      <input
                        type="email"
                        id="email"
                        value={user.email}
                        disabled
                        className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-600 text-gray-500 dark:text-gray-400"
                      />
                      <p className="mt-1 text-xs text-gray-500">
                        Die E-Mail-Adresse kann nicht geändert werden
                      </p>
                    </div>

                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={isUpdatingProfile || isLoading}
                        className={clsx(
                          'px-6 py-3 rounded-lg font-medium text-white transition-all',
                          isUpdatingProfile || isLoading
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700'
                        )}
                      >
                        {isUpdatingProfile ? 'Speichere...' : 'Profil speichern'}
                      </button>
                    </div>
                  </motion.form>
                )}

                {activeTab === 'password' && (
                  <motion.form
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    onSubmit={handlePasswordSubmit}
                    className="space-y-6"
                  >
                    <div>
                      <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Aktuelles Passwort
                      </label>
                      <input
                        type="password"
                        id="currentPassword"
                        value={passwordData.currentPassword}
                        onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                        className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Neues Passwort
                      </label>
                      <input
                        type="password"
                        id="newPassword"
                        value={passwordData.newPassword}
                        onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                        className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        minLength={6}
                        required
                      />
                      <p className="mt-1 text-xs text-gray-500">
                        Das Passwort muss mindestens 6 Zeichen lang sein
                      </p>
                    </div>

                    <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                      <div className="flex">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                            Sicherheitshinweis
                          </h3>
                          <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                            <p>
                              Nach der Passwort-Änderung werden Sie automatisch abgemeldet
                              und müssen sich mit dem neuen Passwort erneut anmelden.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={isChangingPassword || isLoading}
                        className={clsx(
                          'px-6 py-3 rounded-lg font-medium text-white transition-all',
                          isChangingPassword || isLoading
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-red-600 hover:bg-red-700'
                        )}
                      >
                        {isChangingPassword ? 'Ändere...' : 'Passwort ändern'}
                      </button>
                    </div>
                  </motion.form>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}