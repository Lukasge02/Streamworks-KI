/**
 * Auth Context for Streamworks-KI RBAC System
 * React Context provider for authentication state and actions
 */

'use client'

import React, { createContext, useContext, useEffect, useCallback, ReactNode, useMemo } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  User,
  UserRole,
  Permission,
  LoginCredentials,
  RegisterData,
  ProfileUpdate,
  PasswordUpdate,
  AuthContextValue,
  AuthError
} from '@/types/auth.types'
import { useAuth } from '@/stores/authStore'
import { authService, AuthError as ServiceAuthError } from '@/services/auth.service'
import { toast } from 'sonner'

// Create the context
const AuthContext = createContext<AuthContextValue | null>(null)

// Provider props
interface AuthProviderProps {
  children: ReactNode
}

/**
 * AuthProvider component that wraps the app with authentication context
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const queryClient = useQueryClient()

  // Zustand store for state management
  const {
    user,
    token,
    company,
    isAuthenticated,
    isLoading,
    error,
    setAuth,
    clearAuth,
    updateUser,
    setLoading,
    setError,
    role,
    permissions,
    canAccess,
    hasValidToken,
    scheduleTokenRefresh
  } = useAuth()

  // ===========================
  // SESSION VALIDATION
  // ===========================

  const { data: sessionValid } = useQuery({
    queryKey: ['auth', 'validate-session', token],
    queryFn: async () => {
      if (!token || !hasValidToken) {
        return false
      }

      try {
        const isValid = await authService.validateSession()
        if (!isValid) {
          clearAuth()
        }
        return isValid
      } catch (error) {
        console.warn('Session validation failed:', error)
        clearAuth()
        return false
      }
    },
    enabled: !!token,
    refetchInterval: 5 * 60 * 1000, // Check every 5 minutes
    refetchIntervalInBackground: false,
    retry: false,
    staleTime: 60 * 1000, // Consider data fresh for 1 minute
    gcTime: 5 * 60 * 1000 // Keep in cache for 5 minutes
  })

  // ===========================
  // AUTHENTICATION ACTIONS
  // ===========================

  const login = useCallback(async (credentials: LoginCredentials): Promise<void> => {
    console.log('🔑 AuthContext.login called with:', { email: credentials.email, hasPassword: !!credentials.password })
    setLoading(true)
    setError(null)

    try {
      console.log('📡 Calling authService.login...')
      const response = await authService.login(credentials)
      console.log('✅ authService.login successful:', { hasToken: !!response.token, user: response.user?.firstName })

      // Store auth data in Zustand
      console.log('💾 Storing auth data in Zustand...')
      setAuth(response.token, response.user, response.company)

      // Invalidate queries that might need fresh data
      console.log('🔄 Invalidating queries...')
      await queryClient.invalidateQueries({ queryKey: ['auth'] })
      await queryClient.invalidateQueries({ queryKey: ['user'] })

      console.log('🎉 Login completed successfully!')
      toast.success(`Willkommen zurück, ${response.user.firstName}!`)
    } catch (error) {
      console.error('❌ AuthContext login error:', error)
      const authError = error as ServiceAuthError
      const message = authError.code === 'INVALID_CREDENTIALS'
        ? 'Ungültige E-Mail oder Passwort'
        : 'Anmeldung fehlgeschlagen. Bitte versuchen Sie es erneut.'

      console.error('❌ Login error message:', message)
      setError(message)
      toast.error(message)
      throw error
    } finally {
      console.log('🏁 AuthContext login finished (finally block)')
      setLoading(false)
    }
  }, [setLoading, setError, setAuth, queryClient])

  const register = useCallback(async (data: RegisterData): Promise<void> => {
    setLoading(true)
    setError(null)

    try {
      const response = await authService.register(data)

      // Store auth data in Zustand
      setAuth(response.token, response.user, response.company)

      // Invalidate queries
      await queryClient.invalidateQueries({ queryKey: ['auth'] })
      await queryClient.invalidateQueries({ queryKey: ['user'] })

      toast.success(`Willkommen bei Streamworks, ${response.user.firstName}!`)
    } catch (error) {
      const authError = error as ServiceAuthError
      const message = authError.code === 'NETWORK_ERROR' && authError.message.includes('already exists')
        ? 'Ein Account mit dieser E-Mail-Adresse existiert bereits'
        : 'Registrierung fehlgeschlagen. Bitte versuchen Sie es erneut.'

      setError(message)
      toast.error(message)
      throw error
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError, setAuth, queryClient])

  const logout = useCallback(async (): Promise<void> => {
    setLoading(true)

    try {
      await authService.logout()
    } catch (error) {
      console.warn('Logout request failed:', error)
    } finally {
      // Always clear local state
      clearAuth()

      // Clear all cached data
      queryClient.clear()

      setLoading(false)
      toast.info('Sie wurden erfolgreich abgemeldet')
    }
  }, [setLoading, clearAuth, queryClient])

  const refreshSession = useCallback(async (): Promise<void> => {
    if (!token) return

    try {
      const response = await authService.refreshToken()
      setAuth(response.token, response.user, response.company)

      // Reschedule next refresh
      scheduleTokenRefresh()
    } catch (error) {
      console.warn('Token refresh failed:', error)
      clearAuth()
      toast.error('Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.')
    }
  }, [token, setAuth, clearAuth, scheduleTokenRefresh])

  // ===========================
  // PROFILE MANAGEMENT
  // ===========================

  const updateProfile = useCallback(async (data: ProfileUpdate): Promise<void> => {
    if (!user) throw new Error('No user logged in')

    setLoading(true)
    try {
      const updatedUser = await authService.updateProfile(data)

      // Update user in store
      updateUser({
        firstName: updatedUser.firstName,
        lastName: updatedUser.lastName,
        fullName: updatedUser.fullName
      })

      toast.success('Profil erfolgreich aktualisiert')
    } catch (error) {
      const message = 'Profil-Update fehlgeschlagen'
      setError(message)
      toast.error(message)
      throw error
    } finally {
      setLoading(false)
    }
  }, [user, setLoading, updateUser, setError])

  const changePassword = useCallback(async (data: PasswordUpdate): Promise<void> => {
    setLoading(true)
    try {
      await authService.changePassword(data)
      toast.success('Passwort erfolgreich geändert')
    } catch (error) {
      const authError = error as ServiceAuthError
      const message = authError.code === 'INVALID_CREDENTIALS'
        ? 'Das aktuelle Passwort ist falsch'
        : 'Passwort-Änderung fehlgeschlagen'

      setError(message)
      toast.error(message)
      throw error
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  // ===========================
  // PERMISSION HELPERS
  // ===========================

  const hasPermission = useCallback((permission: Permission): boolean => {
    return canAccess(permission)
  }, [canAccess])

  const hasRole = useCallback((requiredRole: UserRole): boolean => {
    return role === requiredRole
  }, [role])

  const hasMinRole = useCallback((requiredRole: UserRole): boolean => {
    if (!role) return false

    const roleHierarchy = {
      [UserRole.OWNER]: 100,
      [UserRole.STREAMWORKS_ADMIN]: 50,
      [UserRole.KUNDE]: 10
    }

    return roleHierarchy[role] >= roleHierarchy[requiredRole]
  }, [role])

  const canAccessResource = useCallback((resource: string, action: string): boolean => {
    const permission = `${resource}.${action}` as Permission
    return hasPermission(permission)
  }, [hasPermission])

  const canManageUser = useCallback((targetUser: User): boolean => {
    if (!user) return false
    return authService.canManageUser(targetUser)
  }, [user])

  const canAccessCompany = useCallback((companyId: string): boolean => {
    if (!user) return false
    return authService.canAccessCompany(companyId)
  }, [user])

  // ===========================
  // INITIALIZATION EFFECT
  // ===========================

  useEffect(() => {
    // Initialize auth state on mount
    const initializeAuth = async () => {
      const storedToken = authService.getStoredToken()
      const storedUser = authService.getStoredUser()

      if (storedToken && storedUser && authService.isTokenValid(storedToken)) {
        // Validate stored session
        try {
          const isValid = await authService.validateSession()
          if (isValid) {
            setAuth(storedToken, storedUser, authService.getStoredCompany())
            scheduleTokenRefresh()
          } else {
            clearAuth()
          }
        } catch (error) {
          console.warn('Session validation failed on init:', error)
          clearAuth()
        }
      } else {
        // Clear invalid stored data
        clearAuth()
      }
    }

    initializeAuth()
  }, [setAuth, clearAuth, scheduleTokenRefresh])

  // ===========================
  // CONTEXT VALUE
  // ===========================

  const contextValue: AuthContextValue = useMemo(() => ({
    // State
    user,
    isAuthenticated,
    isLoading,
    permissions,
    company,
    error,

    // Actions
    login,
    register,
    logout,
    refreshSession,
    updateProfile,
    changePassword,

    // Permission helpers
    hasPermission,
    hasRole,
    hasMinRole,
    canAccess: canAccessResource,
    canManageUser,
    canAccessCompany
  }), [
    user,
    isAuthenticated,
    isLoading,
    permissions,
    company,
    error,
    login,
    register,
    logout,
    refreshSession,
    updateProfile,
    changePassword,
    hasPermission,
    hasRole,
    hasMinRole,
    canAccessResource,
    canManageUser,
    canAccessCompany
  ])

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

/**
 * Hook to use authentication context
 */
export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider')
  }

  return context
}

// Export for convenience
export { AuthContext }
export default AuthProvider