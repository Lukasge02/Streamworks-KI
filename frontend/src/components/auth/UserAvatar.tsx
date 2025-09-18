/**
 * User Avatar Component for Streamworks-KI RBAC System
 * Professional user avatar with role indicators and dropdown menu
 */

'use client'

import React, { Fragment } from 'react'
import { Menu, Transition } from '@headlessui/react'
import {
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  UserIcon,
  Cog6ToothIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline'
import { UserAvatarProps, ROLE_CONFIGS, User } from '@/types/auth.types'
import { useAuthContext } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { clsx } from 'clsx'

/**
 * UserAvatar component with role indicator and dropdown menu
 */
export function UserAvatar({
  user: propUser,
  size = 'md',
  showRole = true,
  showMenu = true,
  onClick
}: UserAvatarProps) {
  const { user: contextUser, logout } = useAuthContext()
  const router = useRouter()

  // Use prop user or context user
  const user = propUser || contextUser

  if (!user) {
    return (
      <div className="flex items-center space-x-3">
        <UserCircleIcon className="h-8 w-8 text-gray-400" />
        <span className="text-sm text-gray-500">Nicht angemeldet</span>
      </div>
    )
  }

  const roleConfig = ROLE_CONFIGS[user.role]

  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-10 w-10'
  }

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  }

  // Handle simple click (no menu)
  if (!showMenu) {
    return (
      <div
        className={clsx(
          'flex items-center space-x-3 cursor-pointer',
          onClick && 'hover:opacity-75 transition-opacity'
        )}
        onClick={onClick}
      >
        <UserAvatar user={user} size={size} showRole={false} showMenu={false} />
        <div className="flex flex-col">
          <span className={clsx('font-medium text-gray-900 dark:text-white', textSizeClasses[size])}>
            {user.fullName}
          </span>
          {showRole && (
            <span className={clsx('text-gray-500 dark:text-gray-400', textSizeClasses[size])}>
              {roleConfig.label}
            </span>
          )}
        </div>
      </div>
    )
  }

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/auth/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const handleProfile = () => {
    router.push('/profile')
  }

  const handleAdmin = () => {
    router.push('/admin')
  }

  // Get user initials for avatar
  const getInitials = (firstName: string, lastName: string): string => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
  }

  return (
    <Menu as="div" className="relative inline-block text-left">
      <div>
        <Menu.Button className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500">
          {/* Avatar */}
          <div className={clsx(
            'relative flex items-center justify-center rounded-full text-white font-medium',
            sizeClasses[size],
            roleConfig.color
          )}>
            {getInitials(user.firstName, user.lastName)}

            {/* Role indicator dot */}
            {showRole && (
              <div className={clsx(
                'absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white dark:border-gray-900',
                roleConfig.color
              )} />
            )}
          </div>

          {/* User info */}
          <div className="flex flex-col items-start min-w-0">
            <span className={clsx('font-medium text-gray-900 dark:text-white truncate', textSizeClasses[size])}>
              {user.fullName}
            </span>
            {showRole && (
              <span className={clsx('text-gray-500 dark:text-gray-400 truncate', textSizeClasses[size])}>
                {roleConfig.label}
              </span>
            )}
          </div>

          {/* Dropdown indicator */}
          <ChevronDownIcon className="h-4 w-4 text-gray-400" />
        </Menu.Button>
      </div>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute right-0 z-10 mt-2 w-56 origin-top-right divide-y divide-gray-100 dark:divide-gray-700 rounded-lg bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          {/* User Info Section */}
          <div className="px-4 py-3">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {user.fullName}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
              {user.email}
            </p>
            <div className="mt-1 flex items-center">
              <div className={clsx('w-2 h-2 rounded-full mr-2', roleConfig.color)} />
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {roleConfig.label}
              </span>
            </div>
          </div>

          {/* Menu Actions */}
          <div className="py-1">
            <Menu.Item>
              {({ active }) => (
                <button
                  onClick={handleProfile}
                  className={clsx(
                    active ? 'bg-gray-100 dark:bg-gray-700' : '',
                    'group flex w-full items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200'
                  )}
                >
                  <UserIcon className="mr-3 h-4 w-4" />
                  Profil bearbeiten
                </button>
              )}
            </Menu.Item>

            {/* Admin menu item - only for admins and owners */}
            {(user.role === 'owner' || user.role === 'streamworks_admin') && (
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={handleAdmin}
                    className={clsx(
                      active ? 'bg-gray-100 dark:bg-gray-700' : '',
                      'group flex w-full items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200'
                    )}
                  >
                    <Cog6ToothIcon className="mr-3 h-4 w-4" />
                    Administration
                  </button>
                )}
              </Menu.Item>
            )}
          </div>

          {/* Logout Section */}
          <div className="py-1">
            <Menu.Item>
              {({ active }) => (
                <button
                  onClick={handleLogout}
                  className={clsx(
                    active ? 'bg-gray-100 dark:bg-gray-700' : '',
                    'group flex w-full items-center px-4 py-2 text-sm text-red-700 dark:text-red-400'
                  )}
                >
                  <ArrowRightOnRectangleIcon className="mr-3 h-4 w-4" />
                  Abmelden
                </button>
              )}
            </Menu.Item>
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  )
}

/**
 * Simple avatar without dropdown (for display purposes)
 */
export function SimpleUserAvatar({ user, size = 'md', showRole = false }: {
  user: User
  size?: 'sm' | 'md' | 'lg'
  showRole?: boolean
}) {
  if (!user) return null

  const roleConfig = ROLE_CONFIGS[user.role]

  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-10 w-10'
  }

  const getInitials = (firstName: string, lastName: string): string => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
  }

  return (
    <div className="flex items-center space-x-2">
      <div className={clsx(
        'relative flex items-center justify-center rounded-full text-white font-medium text-sm',
        sizeClasses[size],
        roleConfig.color
      )}>
        {getInitials(user.firstName, user.lastName)}

        {showRole && (
          <div className={clsx(
            'absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border border-white',
            roleConfig.color
          )} />
        )}
      </div>

      {showRole && (
        <span className="text-xs text-gray-500">
          {roleConfig.label}
        </span>
      )}
    </div>
  )
}

export default UserAvatar