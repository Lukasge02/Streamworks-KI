/**
 * Auth Store for Streamworks-KI RBAC System
 * Zustand store for authentication state management with persistence
 */

import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { persist } from 'zustand/middleware'
import {
  User,
  Company,
  UserRole,
  Permission,
  AuthStore,
  AUTH_CONFIG
} from '@/types/auth.types'

interface AuthStoreState extends AuthStore {
  // Additional UI state
  isLoading: boolean
  error: string | null

  // Token refresh state
  isRefreshing: boolean
  refreshTimeout?: NodeJS.Timeout

  // Actions
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setRefreshing: (refreshing: boolean) => void

  // Computed getters
  isAuthenticated: () => boolean
  getUserRole: () => UserRole | null
  getUserPermissions: () => Permission[]
  canAccess: (permission: Permission) => boolean
}

const useAuthStore = create<AuthStoreState>()(
  persist(
    immer((set, get) => ({
      // Core auth state
      token: null,
      refreshToken: null,
      user: null,
      company: undefined,

      // UI state
      isLoading: false,
      error: null,
      isRefreshing: false,
      refreshTimeout: undefined,

      // ===========================
      // CORE AUTH ACTIONS
      // ===========================

      setAuth: (token, user, company) => set((state) => {
        state.token = token
        state.user = user
        state.company = company
        state.error = null

        // Clear any existing refresh timeout
        if (state.refreshTimeout) {
          clearTimeout(state.refreshTimeout)
        }

        // Schedule token refresh if token is valid
        if (token) {
          state.refreshTimeout = setTimeout(() => {
            // This will be handled by the AuthContext
            // The store just tracks the timeout
          }, AUTH_CONFIG.TOKEN_REFRESH_INTERVAL)
        }
      }),

      clearAuth: () => set((state) => {
        state.token = null
        state.refreshToken = null
        state.user = null
        state.company = undefined
        state.error = null
        state.isLoading = false
        state.isRefreshing = false

        // Clear refresh timeout
        if (state.refreshTimeout) {
          clearTimeout(state.refreshTimeout)
          state.refreshTimeout = undefined
        }
      }),

      updateUser: (updates) => set((state) => {
        if (state.user) {
          Object.assign(state.user, updates)
        }
      }),

      setCompany: (company) => set((state) => {
        state.company = company
      }),

      // ===========================
      // TOKEN MANAGEMENT
      // ===========================

      getToken: () => {
        return get().token
      },

      hasValidToken: () => {
        const { token } = get()
        if (!token) return false

        try {
          // Decode JWT to check expiry
          const base64Url = token.split('.')[1]
          const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
          const jsonPayload = decodeURIComponent(
            atob(base64)
              .split('')
              .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
              .join('')
          )
          const payload = JSON.parse(jsonPayload)
          const now = Math.floor(Date.now() / 1000)

          return payload.exp > now
        } catch {
          return false
        }
      },

      scheduleTokenRefresh: () => set((state) => {
        // Clear existing timeout
        if (state.refreshTimeout) {
          clearTimeout(state.refreshTimeout)
        }

        // Schedule new refresh
        state.refreshTimeout = setTimeout(() => {
          // The actual refresh will be handled by AuthContext
          // This just tracks the schedule
        }, AUTH_CONFIG.TOKEN_REFRESH_INTERVAL)
      }),

      clearTokenRefresh: () => set((state) => {
        if (state.refreshTimeout) {
          clearTimeout(state.refreshTimeout)
          state.refreshTimeout = undefined
        }
      }),

      // ===========================
      // UI STATE ACTIONS
      // ===========================

      setLoading: (loading) => set((state) => {
        state.isLoading = loading
      }),

      setError: (error) => set((state) => {
        state.error = error
      }),

      setRefreshing: (refreshing) => set((state) => {
        state.isRefreshing = refreshing
      }),

      // ===========================
      // COMPUTED GETTERS
      // ===========================

      isAuthenticated: () => {
        const { token, user } = get()
        return !!token && !!user && get().hasValidToken()
      },

      getUserRole: () => {
        const { user } = get()
        return user?.role as UserRole || null
      },

      getUserPermissions: () => {
        const role = get().getUserRole()
        if (!role) return []

        // Import permission matrix here to avoid circular dependency
        const PERMISSION_MATRIX = {
          [UserRole.OWNER]: [
            'documents.read', 'documents.write', 'documents.delete', 'documents.admin',
            'folders.read', 'folders.write', 'folders.delete', 'folders.admin',
            'users.read', 'users.write', 'users.delete', 'users.admin',
            'system.read', 'system.write', 'system.admin'
          ],
          [UserRole.STREAMWORKS_ADMIN]: [
            'documents.read', 'documents.write', 'documents.delete',
            'folders.read', 'folders.write', 'folders.delete',
            'users.read', 'users.write',
            'system.read'
          ],
          [UserRole.KUNDE]: [
            'documents.read', 'documents.write',
            'folders.read', 'folders.write',
            'system.read'
          ]
        }

        return PERMISSION_MATRIX[role] as Permission[] || []
      },

      canAccess: (permission) => {
        const permissions = get().getUserPermissions()
        return permissions.includes(permission)
      }
    })),
    {
      name: 'streamworks-auth', // localStorage key
      partialize: (state) => ({
        // Only persist essential data
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        company: state.company
      }),
      version: 1,
      migrate: (persistedState: any, version) => {
        // Handle migration if needed in the future
        if (version < 1) {
          // Migration logic for future versions
        }
        return persistedState as AuthStoreState
      }
    }
  )
)

// Selectors for common use cases
export const authSelectors = {
  // Basic auth state
  isAuthenticated: (state: AuthStoreState) => state.isAuthenticated(),
  user: (state: AuthStoreState) => state.user,
  token: (state: AuthStoreState) => state.token,
  company: (state: AuthStoreState) => state.company,

  // UI state
  isLoading: (state: AuthStoreState) => state.isLoading,
  error: (state: AuthStoreState) => state.error,
  isRefreshing: (state: AuthStoreState) => state.isRefreshing,

  // Role & permissions
  role: (state: AuthStoreState) => state.getUserRole(),
  permissions: (state: AuthStoreState) => state.getUserPermissions(),

  // Permission checkers
  hasPermission: (permission: Permission) => (state: AuthStoreState) =>
    state.canAccess(permission),
  hasRole: (role: UserRole) => (state: AuthStoreState) =>
    state.getUserRole() === role,
  hasMinRole: (role: UserRole) => (state: AuthStoreState) => {
    const currentRole = state.getUserRole()
    if (!currentRole) return false

    const roleHierarchy = {
      [UserRole.OWNER]: 100,
      [UserRole.STREAMWORKS_ADMIN]: 50,
      [UserRole.KUNDE]: 10
    }

    return roleHierarchy[currentRole] >= roleHierarchy[role]
  },

  // Company access
  canAccessCompany: (companyId: string) => (state: AuthStoreState) => {
    const user = state.user
    if (!user) return false

    // Owner can access all companies
    if (user.role === UserRole.OWNER) return true

    // Others can only access their own company
    return user.companyId === companyId
  }
}

// Hook for easier usage in components
export const useAuth = () => {
  const store = useAuthStore()

  // Calculate derived values consistently to avoid hook order changes
  const isAuthenticated = store.isAuthenticated()
  const role = store.getUserRole()
  const permissions = store.getUserPermissions()
  const hasValidToken = store.hasValidToken()

  return {
    // State
    user: store.user,
    token: store.token,
    company: store.company,
    isAuthenticated,
    isLoading: store.isLoading,
    error: store.error,
    isRefreshing: store.isRefreshing,

    // Actions
    setAuth: store.setAuth,
    clearAuth: store.clearAuth,
    updateUser: store.updateUser,
    setCompany: store.setCompany,
    setLoading: store.setLoading,
    setError: store.setError,
    setRefreshing: store.setRefreshing,

    // Computed
    role,
    permissions,
    canAccess: store.canAccess,
    hasValidToken,

    // Token management
    getToken: store.getToken,
    scheduleTokenRefresh: store.scheduleTokenRefresh,
    clearTokenRefresh: store.clearTokenRefresh
  }
}

// Export the store
export { useAuthStore }
export default useAuthStore