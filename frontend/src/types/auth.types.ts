/**
 * Auth Types for Streamworks-KI RBAC System
 * Enterprise-grade TypeScript definitions for authentication and authorization
 */

// User Role Enum with hierarchy
export enum UserRole {
  OWNER = 'owner',
  STREAMWORKS_ADMIN = 'streamworks_admin',
  KUNDE = 'kunde'
}

// Role display configuration
export interface RoleConfig {
  value: UserRole
  label: string // German label for UI
  hierarchyLevel: number
  description: string
  color: string // Color for UI indicators
}

export const ROLE_CONFIGS: Record<UserRole, RoleConfig> = {
  [UserRole.OWNER]: {
    value: UserRole.OWNER,
    label: 'System-Eigentümer',
    hierarchyLevel: 100,
    description: 'Vollzugriff auf das gesamte System',
    color: 'bg-red-500'
  },
  [UserRole.STREAMWORKS_ADMIN]: {
    value: UserRole.STREAMWORKS_ADMIN,
    label: 'Streamworks Admin',
    hierarchyLevel: 50,
    description: 'Administration innerhalb der eigenen Company',
    color: 'bg-blue-500'
  },
  [UserRole.KUNDE]: {
    value: UserRole.KUNDE,
    label: 'Kunde',
    hierarchyLevel: 10,
    description: 'Standardzugriff auf eigene Daten',
    color: 'bg-green-500'
  }
}

// Company/Tenant
export interface Company {
  id: string
  name: string
  domain?: string
  settings: Record<string, any>
  created_at: string
  updated_at: string
}

// User
export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  fullName: string
  role: UserRole
  roleDisplayName: string
  companyId?: string
  isActive: boolean
  createdAt: string
  lastLoginAt?: string
}

// Auth State
export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  permissions: string[]
  company?: Company
}

// Login/Register Request Models
export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  firstName: string
  lastName: string
  companyName?: string
}

// API Response Models
export interface TokenResponse {
  user: User
  token: string
  tokenType: 'bearer'
  expiresIn: number
  company?: Company
}

export interface UserResponse {
  id: string
  email: string
  firstName: string
  lastName: string
  fullName: string
  role: string
  roleDisplayName: string
  companyId?: string
  isActive: boolean
  createdAt: string
  lastLoginAt?: string
}

// Profile Management
export interface ProfileUpdate {
  firstName?: string
  lastName?: string
}

export interface PasswordUpdate {
  currentPassword: string
  newPassword: string
}

// Permission System
export type Permission =
  | 'documents.read'
  | 'documents.write'
  | 'documents.delete'
  | 'documents.admin'
  | 'folders.read'
  | 'folders.write'
  | 'folders.delete'
  | 'folders.admin'
  | 'users.read'
  | 'users.write'
  | 'users.delete'
  | 'users.admin'
  | 'system.read'
  | 'system.write'
  | 'system.admin'

export interface PermissionMatrix {
  [UserRole.OWNER]: Permission[]
  [UserRole.STREAMWORKS_ADMIN]: Permission[]
  [UserRole.KUNDE]: Permission[]
}

export const PERMISSION_MATRIX: PermissionMatrix = {
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

// Auth Context Value
export interface AuthContextValue {
  // State
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  permissions: Permission[]
  company?: Company
  error: string | null

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshSession: () => Promise<void>
  updateProfile: (data: ProfileUpdate) => Promise<void>
  changePassword: (data: PasswordUpdate) => Promise<void>

  // Permission helpers
  hasPermission: (permission: Permission) => boolean
  hasRole: (role: UserRole) => boolean
  hasMinRole: (role: UserRole) => boolean
  canAccess: (resource: string, action: string) => boolean
  canManageUser: (targetUser: User) => boolean
  canAccessCompany: (companyId: string) => boolean
}

// Auth Store (Zustand)
export interface AuthStore {
  // Persistent state
  token: string | null
  refreshToken: string | null
  user: User | null
  company?: Company

  // Session management
  setAuth: (token: string, user: User, company?: Company) => void
  clearAuth: () => void
  updateUser: (user: Partial<User>) => void
  setCompany: (company: Company) => void

  // Token management
  getToken: () => string | null
  hasValidToken: () => boolean
  scheduleTokenRefresh: () => void
  clearTokenRefresh: () => void
}

// Auth Service Interface
export interface AuthServiceInterface {
  // Authentication
  login: (credentials: LoginCredentials) => Promise<TokenResponse>
  register: (data: RegisterData) => Promise<TokenResponse>
  logout: () => Promise<void>
  refreshToken: () => Promise<TokenResponse>

  // User management
  getCurrentUser: () => Promise<UserResponse>
  updateProfile: (data: ProfileUpdate) => Promise<UserResponse>
  changePassword: (data: PasswordUpdate) => Promise<void>

  // Token management
  getStoredToken: () => string | null
  isTokenValid: (token: string) => boolean
  decodeToken: (token: string) => any

  // Permission helpers
  hasPermission: (permission: Permission) => boolean
  hasRole: (role: UserRole) => boolean
  canAccessResource: (resourceId: string) => boolean
}

// UI Component Props
export interface LoginFormProps {
  onSuccess?: (user: User) => void
  onError?: (error: string) => void
  redirectTo?: string
  showRegisterLink?: boolean
}

export interface RegisterFormProps {
  onSuccess?: (user: User) => void
  onError?: (error: string) => void
  redirectTo?: string
  showLoginLink?: boolean
}

export interface PermissionGuardProps {
  children: React.ReactNode
  requiredPermission?: Permission
  requiredRole?: UserRole
  requireOwnership?: boolean
  resourceUserId?: string
  resourceCompanyId?: string
  fallback?: React.ReactNode
  loading?: React.ReactNode
  debug?: boolean
}

export interface UserAvatarProps {
  user?: User
  size?: 'sm' | 'md' | 'lg'
  showRole?: boolean
  showMenu?: boolean
  onClick?: () => void
}

export interface RoleIndicatorProps {
  role: UserRole
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  showTooltip?: boolean
}

// Error Types
export interface AuthError extends Error {
  code: 'INVALID_CREDENTIALS' | 'TOKEN_EXPIRED' | 'PERMISSION_DENIED' | 'NETWORK_ERROR' | 'UNKNOWN_ERROR'
  details?: string
}

// Session Management
export interface SessionInfo {
  user: User
  token: string
  expiresAt: Date
  refreshToken?: string
  company?: Company
}

export interface SessionTimeoutProps {
  warningTimeMinutes?: number
  onExtendSession: () => void
  onForceLogout: () => void
}

// Admin Types
export interface UserCreateRequest {
  email: string
  password: string
  firstName: string
  lastName: string
  role?: UserRole
  companyId?: string
  companyName?: string
}

export interface UserListResponse {
  users: UserResponse[]
  total: number
  page: number
  perPage: number
  hasNext: boolean
  hasPrev: boolean
}

export interface UserFilter {
  role?: UserRole
  companyId?: string
  isActive?: boolean
  search?: string
}

// Route Protection
export type RouteAccessLevel = 'public' | 'authenticated' | 'admin' | 'owner'

export interface ProtectedRouteConfig {
  path: string
  accessLevel: RouteAccessLevel
  requiredRole?: UserRole
  requiredPermission?: Permission
  redirectTo?: string
}

// Constants for configuration
export const AUTH_CONFIG = {
  TOKEN_KEY: 'streamworks_auth_token',
  REFRESH_TOKEN_KEY: 'streamworks_refresh_token',
  USER_KEY: 'streamworks_user',
  COMPANY_KEY: 'streamworks_company',
  TOKEN_REFRESH_INTERVAL: 1000 * 60 * 50, // 50 minutes
  SESSION_WARNING_TIME: 1000 * 60 * 5, // 5 minutes before expiry
  API_BASE_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
}

export const ROUTE_PATHS = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  PROFILE: '/profile',
  ADMIN: '/admin',
  DASHBOARD: '/dashboard',
  HOME: '/'
}