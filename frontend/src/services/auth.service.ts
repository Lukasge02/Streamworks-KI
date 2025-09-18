/**
 * Auth Service for Streamworks-KI RBAC System
 * Enterprise-grade authentication service with JWT management
 */

import {
  LoginCredentials,
  RegisterData,
  TokenResponse,
  UserResponse,
  ProfileUpdate,
  PasswordUpdate,
  User,
  UserRole,
  Permission,
  AuthServiceInterface,
  AuthError,
  AUTH_CONFIG,
  PERMISSION_MATRIX
} from '@/types/auth.types'

class AuthService implements AuthServiceInterface {
  private baseUrl: string
  private tokenRefreshTimeout?: NodeJS.Timeout

  constructor() {
    this.baseUrl = AUTH_CONFIG.API_BASE_URL
  }

  // ===========================
  // HTTP CLIENT METHODS
  // ===========================

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json'
    }

    // Add auth header if token exists
    const token = this.getStoredToken()
    if (token) {
      defaultHeaders['Authorization'] = `Bearer ${token}`
    }

    try {
      const response = await fetch(url, {
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          error: `HTTP ${response.status}`,
          detail: response.statusText
        }))

        // Handle specific error cases
        if (response.status === 401) {
          this.clearAuthData()
          throw new AuthError('INVALID_CREDENTIALS', errorData.detail || 'Authentication failed')
        }

        if (response.status === 403) {
          throw new AuthError('PERMISSION_DENIED', errorData.detail || 'Access denied')
        }

        throw new AuthError('NETWORK_ERROR', errorData.detail || errorData.error || 'Request failed')
      }

      // Handle 204 No Content responses
      if (response.status === 204) {
        return null as T
      }

      return await response.json()
    } catch (error: any) {
      if (error instanceof AuthError) {
        throw error
      }

      console.error('Auth service request failed:', error)
      throw new AuthError('NETWORK_ERROR', error.message || 'Network request failed')
    }
  }

  // ===========================
  // AUTHENTICATION METHODS
  // ===========================

  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    try {
      const response = await this.request<TokenResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      })

      // Store auth data
      this.storeAuthData(response)

      // Schedule token refresh
      this.scheduleTokenRefresh()

      return response
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  async register(data: RegisterData): Promise<TokenResponse> {
    try {
      const response = await this.request<TokenResponse>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      })

      // Store auth data
      this.storeAuthData(response)

      // Schedule token refresh
      this.scheduleTokenRefresh()

      return response
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    }
  }

  async logout(): Promise<void> {
    try {
      const token = this.getStoredToken()

      if (token) {
        await this.request('/auth/logout', {
          method: 'POST',
        })
      }
    } catch (error) {
      console.warn('Logout request failed:', error)
    } finally {
      // Always clear local data
      this.clearAuthData()
    }
  }

  async refreshToken(): Promise<TokenResponse> {
    try {
      // For now, we'll implement a simple refresh by verifying current token
      // In a production system, you'd have separate refresh token logic
      const response = await this.request<{ valid: boolean; user: any }>('/auth/verify-token')

      if (!response.valid || !response.user) {
        throw new AuthError('TOKEN_EXPIRED', 'Token is no longer valid')
      }

      // Return current token info (simplified refresh)
      const token = this.getStoredToken()!
      const storedUser = this.getStoredUser()!

      return {
        user: storedUser,
        token,
        tokenType: 'bearer',
        expiresIn: 3600, // 1 hour
        company: this.getStoredCompany()
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
      this.clearAuthData()
      throw error
    }
  }

  // ===========================
  // USER MANAGEMENT METHODS
  // ===========================

  async getCurrentUser(): Promise<UserResponse> {
    return this.request<UserResponse>('/auth/me')
  }

  async updateProfile(data: ProfileUpdate): Promise<UserResponse> {
    return this.request<UserResponse>('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async changePassword(data: PasswordUpdate): Promise<void> {
    await this.request('/auth/me/password', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  // ===========================
  // TOKEN MANAGEMENT METHODS
  // ===========================

  getStoredToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(AUTH_CONFIG.TOKEN_KEY)
  }

  getStoredUser(): User | null {
    if (typeof window === 'undefined') return null
    const userData = localStorage.getItem(AUTH_CONFIG.USER_KEY)
    return userData ? JSON.parse(userData) : null
  }

  getStoredCompany() {
    if (typeof window === 'undefined') return null
    const companyData = localStorage.getItem(AUTH_CONFIG.COMPANY_KEY)
    return companyData ? JSON.parse(companyData) : null
  }

  private storeAuthData(response: TokenResponse): void {
    if (typeof window === 'undefined') return

    localStorage.setItem(AUTH_CONFIG.TOKEN_KEY, response.token)
    localStorage.setItem(AUTH_CONFIG.USER_KEY, JSON.stringify(response.user))

    if (response.company) {
      localStorage.setItem(AUTH_CONFIG.COMPANY_KEY, JSON.stringify(response.company))
    }
  }

  private clearAuthData(): void {
    if (typeof window === 'undefined') return

    localStorage.removeItem(AUTH_CONFIG.TOKEN_KEY)
    localStorage.removeItem(AUTH_CONFIG.USER_KEY)
    localStorage.removeItem(AUTH_CONFIG.COMPANY_KEY)
    localStorage.removeItem(AUTH_CONFIG.REFRESH_TOKEN_KEY)

    this.clearTokenRefresh()
  }

  isTokenValid(token: string): boolean {
    if (!token) return false

    try {
      const payload = this.decodeToken(token)
      const now = Math.floor(Date.now() / 1000)
      return payload.exp > now
    } catch {
      return false
    }
  }

  decodeToken(token: string): any {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      return JSON.parse(jsonPayload)
    } catch {
      throw new AuthError('TOKEN_EXPIRED', 'Invalid token format')
    }
  }

  // ===========================
  // PERMISSION METHODS
  // ===========================

  hasPermission(permission: Permission): boolean {
    const user = this.getStoredUser()
    if (!user) return false

    const userRole = user.role as UserRole
    return PERMISSION_MATRIX[userRole]?.includes(permission) || false
  }

  hasRole(role: UserRole): boolean {
    const user = this.getStoredUser()
    if (!user) return false
    return user.role === role
  }

  hasMinRole(role: UserRole): boolean {
    const user = this.getStoredUser()
    if (!user) return false

    const userRole = user.role as UserRole
    const roleHierarchy: Record<UserRole, number> = {
      [UserRole.OWNER]: 100,
      [UserRole.STREAMWORKS_ADMIN]: 50,
      [UserRole.KUNDE]: 10
    }

    return roleHierarchy[userRole] >= roleHierarchy[role]
  }

  canAccessResource(resourceId: string): boolean {
    const user = this.getStoredUser()
    if (!user) return false

    // Owner can access everything
    if (user.role === UserRole.OWNER) return true

    // For now, simplified access control
    // In production, you'd check actual resource ownership
    return true
  }

  canManageUser(targetUser: User): boolean {
    const currentUser = this.getStoredUser()
    if (!currentUser) return false

    // Owner can manage everyone
    if (currentUser.role === UserRole.OWNER) return true

    // Streamworks Admin can manage customers in their companies
    if (currentUser.role === UserRole.STREAMWORKS_ADMIN) {
      return (
        targetUser.role === UserRole.KUNDE &&
        targetUser.companyId === currentUser.companyId
      )
    }

    // Users can only manage themselves
    return currentUser.id === targetUser.id
  }

  canAccessCompany(companyId: string): boolean {
    const user = this.getStoredUser()
    if (!user) return false

    // Owner can access all companies
    if (user.role === UserRole.OWNER) return true

    // Other roles can only access their own company
    return user.companyId === companyId
  }

  // ===========================
  // TOKEN REFRESH SCHEDULING
  // ===========================

  scheduleTokenRefresh(): void {
    this.clearTokenRefresh()

    this.tokenRefreshTimeout = setTimeout(() => {
      this.refreshToken().catch((error) => {
        console.warn('Scheduled token refresh failed:', error)
        // Don't clear auth data here - let the UI handle it
      })
    }, AUTH_CONFIG.TOKEN_REFRESH_INTERVAL)
  }

  clearTokenRefresh(): void {
    if (this.tokenRefreshTimeout) {
      clearTimeout(this.tokenRefreshTimeout)
      this.tokenRefreshTimeout = undefined
    }
  }

  // ===========================
  // UTILITY METHODS
  // ===========================

  getCurrentUserRole(): UserRole | null {
    const user = this.getStoredUser()
    return user?.role as UserRole || null
  }

  getPermissionsForRole(role: UserRole): Permission[] {
    return PERMISSION_MATRIX[role] || []
  }

  getRoleDisplayName(role: UserRole): string {
    const roleLabels = {
      [UserRole.OWNER]: 'System-Eigentümer',
      [UserRole.STREAMWORKS_ADMIN]: 'Streamworks Admin',
      [UserRole.KUNDE]: 'Kunde'
    }
    return roleLabels[role] || role
  }

  // ===========================
  // SESSION VALIDATION
  // ===========================

  async validateSession(): Promise<boolean> {
    const token = this.getStoredToken()
    if (!token) return false

    if (!this.isTokenValid(token)) {
      this.clearAuthData()
      return false
    }

    try {
      const response = await this.request<{ valid: boolean }>('/auth/verify-token')
      if (!response.valid) {
        this.clearAuthData()
        return false
      }
      return true
    } catch {
      this.clearAuthData()
      return false
    }
  }
}

// AuthError class implementation
class AuthError extends Error {
  code: 'INVALID_CREDENTIALS' | 'TOKEN_EXPIRED' | 'PERMISSION_DENIED' | 'NETWORK_ERROR' | 'UNKNOWN_ERROR'
  details?: string

  constructor(code: AuthError['code'], message: string, details?: string) {
    super(message)
    this.name = 'AuthError'
    this.code = code
    this.details = details
  }
}

// Export singleton instance
export const authService = new AuthService()
export default authService
export { AuthError }