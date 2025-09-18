/**
 * Permission Guard Component for Streamworks-KI RBAC System
 * Conditional rendering based on user permissions and roles
 */

'use client'

import React from 'react'
import { useAuthContext } from '@/contexts/AuthContext'
import { PermissionGuardProps, UserRole } from '@/types/auth.types'

/**
 * PermissionGuard component for role-based conditional rendering
 *
 * @param children - Content to render if user has permission
 * @param requiredPermission - Specific permission required
 * @param requiredRole - Specific role required
 * @param requireOwnership - Whether to check resource ownership
 * @param resourceUserId - User ID of resource owner (for ownership check)
 * @param resourceCompanyId - Company ID of resource (for company access check)
 * @param fallback - Component to render if no permission
 * @param loading - Component to render while loading
 * @param debug - Show debug information in development
 */
export function PermissionGuard({
  children,
  requiredPermission,
  requiredRole,
  requireOwnership = false,
  resourceUserId,
  resourceCompanyId,
  fallback = null,
  loading = null,
  debug = false
}: PermissionGuardProps) {
  const {
    user,
    isAuthenticated,
    isLoading,
    hasPermission,
    hasRole,
    canAccessCompany
  } = useAuthContext()

  // Show loading state
  if (isLoading) {
    return loading || (
      <div className="animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-24"></div>
      </div>
    )
  }

  // Not authenticated - show fallback
  if (!isAuthenticated || !user) {
    if (debug && process.env.NODE_ENV === 'development') {
      console.log('PermissionGuard: User not authenticated')
    }
    return fallback
  }

  // Check specific permission
  if (requiredPermission && !hasPermission(requiredPermission)) {
    if (debug && process.env.NODE_ENV === 'development') {
      console.log(`PermissionGuard: User lacks required permission: ${requiredPermission}`)
    }
    return fallback
  }

  // Check specific role
  if (requiredRole && !hasRole(requiredRole)) {
    if (debug && process.env.NODE_ENV === 'development') {
      console.log(`PermissionGuard: User lacks required role: ${requiredRole}`)
    }
    return fallback
  }

  // Check resource ownership
  if (requireOwnership && resourceUserId && resourceUserId !== user.id) {
    // Owner can access everything
    if (user.role !== 'owner') {
      if (debug && process.env.NODE_ENV === 'development') {
        console.log('PermissionGuard: User does not own this resource')
      }
      return fallback
    }
  }

  // Check company access
  if (resourceCompanyId && !canAccessCompany(resourceCompanyId)) {
    if (debug && process.env.NODE_ENV === 'development') {
      console.log(`PermissionGuard: User cannot access company: ${resourceCompanyId}`)
    }
    return fallback
  }

  // Debug info in development
  if (debug && process.env.NODE_ENV === 'development') {
    console.log('PermissionGuard: Access granted', {
      user: user.email,
      role: user.role,
      requiredPermission,
      requiredRole,
      requireOwnership,
      resourceUserId,
      resourceCompanyId
    })
  }

  // All checks passed - render children
  return <>{children}</>
}

/**
 * Higher-order component version of PermissionGuard
 */
export function withPermissionGuard<P extends object>(
  Component: React.ComponentType<P>,
  guardProps: Omit<PermissionGuardProps, 'children'>
) {
  return function PermissionGuardedComponent(props: P) {
    return (
      <PermissionGuard {...guardProps}>
        <Component {...props} />
      </PermissionGuard>
    )
  }
}

/**
 * Convenience components for common permission checks
 */
export function OwnerOnly({ children, fallback = null }: { children: React.ReactNode; fallback?: React.ReactNode }) {
  return (
    <PermissionGuard requiredRole={UserRole.OWNER} fallback={fallback}>
      {children}
    </PermissionGuard>
  )
}

export function AdminOnly({ children, fallback = null }: { children: React.ReactNode; fallback?: React.ReactNode }) {
  return (
    <PermissionGuard requiredRole={UserRole.STREAMWORKS_ADMIN} fallback={fallback}>
      {children}
    </PermissionGuard>
  )
}

export function AdminOrOwner({ children, fallback = null }: { children: React.ReactNode; fallback?: React.ReactNode }) {
  const { user } = useAuthContext()

  if (user?.role === 'owner' || user?.role === 'streamworks_admin') {
    return <>{children}</>
  }

  return <>{fallback}</>
}

export function CustomerOnly({ children, fallback = null }: { children: React.ReactNode; fallback?: React.ReactNode }) {
  return (
    <PermissionGuard requiredRole={UserRole.KUNDE} fallback={fallback}>
      {children}
    </PermissionGuard>
  )
}

/**
 * Permission-based render functions
 */
export function CanRead({ resource, children, fallback = null }: {
  resource: string
  children: React.ReactNode
  fallback?: React.ReactNode
}) {
  const permission = `${resource}.read` as any
  return (
    <PermissionGuard requiredPermission={permission} fallback={fallback}>
      {children}
    </PermissionGuard>
  )
}

export function CanWrite({ resource, children, fallback = null }: {
  resource: string
  children: React.ReactNode
  fallback?: React.ReactNode
}) {
  const permission = `${resource}.write` as any
  return (
    <PermissionGuard requiredPermission={permission} fallback={fallback}>
      {children}
    </PermissionGuard>
  )
}

export function CanDelete({ resource, children, fallback = null }: {
  resource: string
  children: React.ReactNode
  fallback?: React.ReactNode
}) {
  const permission = `${resource}.delete` as any
  return (
    <PermissionGuard requiredPermission={permission} fallback={fallback}>
      {children}
    </PermissionGuard>
  )
}

export function CanAdmin({ resource, children, fallback = null }: {
  resource: string
  children: React.ReactNode
  fallback?: React.ReactNode
}) {
  const permission = `${resource}.admin` as any
  return (
    <PermissionGuard requiredPermission={permission} fallback={fallback}>
      {children}
    </PermissionGuard>
  )
}

export default PermissionGuard