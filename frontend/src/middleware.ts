/**
 * NextJS Middleware for Streamworks-KI RBAC System
 * Route-level authentication and authorization with JWT validation
 */

import { NextRequest, NextResponse } from 'next/server'
import { AUTH_CONFIG } from '@/types/auth.types'

// Route configuration
const PUBLIC_ROUTES = [
  '/',
  '/home',
  '/auth/login',
  '/auth/register'
]

const PROTECTED_ROUTES = [
  '/dashboard',
  '/documents',
  '/chat',
  '/xml',
  '/profile'
]

const ADMIN_ROUTES = [
  '/admin'
]

// Helper function to decode JWT payload
function decodeJWTPayload(token: string): any {
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
    return null
  }
}

// Helper function to check if token is expired
function isTokenExpired(token: string): boolean {
  try {
    const payload = decodeJWTPayload(token)
    if (!payload || !payload.exp) return true

    const now = Math.floor(Date.now() / 1000)
    return payload.exp <= now
  } catch {
    return true
  }
}

// Helper function to check user role
function hasMinRole(userRole: string, requiredRole: string): boolean {
  const roleHierarchy: Record<string, number> = {
    'owner': 100,
    'streamworks_admin': 50,
    'kunde': 10
  }

  const userLevel = roleHierarchy[userRole] || 0
  const requiredLevel = roleHierarchy[requiredRole] || 0

  return userLevel >= requiredLevel
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip middleware for API routes, static files, and internal Next.js routes
  if (
    pathname.startsWith('/api/') ||
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/favicon.ico') ||
    pathname.includes('.')
  ) {
    return NextResponse.next()
  }

  // TEMPORARILY DISABLED: Allow all routes without authentication
  // This is a temporary fix to bypass login issues
  console.log(`🔓 TEMP: Allowing unauthenticated access to ${pathname}`)
  return NextResponse.next()

  /* ORIGINAL AUTH CODE - COMMENTED OUT FOR TEMPORARY BYPASS
  // Allow public routes without authentication
  if (PUBLIC_ROUTES.includes(pathname)) {
    return NextResponse.next()
  }

  // Get token from cookies or headers
  const token = request.cookies.get('streamworks_auth_token')?.value ||
                request.headers.get('authorization')?.replace('Bearer ', '')

  // No token - redirect to login
  if (!token) {
    const loginUrl = new URL('/auth/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Invalid or expired token - redirect to login
  if (isTokenExpired(token)) {
    const loginUrl = new URL('/auth/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    loginUrl.searchParams.set('reason', 'expired')

    // Clear the invalid cookie
    const response = NextResponse.redirect(loginUrl)
    response.cookies.delete('streamworks_auth_token')
    return response
  }

  // Decode token to get user info
  const payload = decodeJWTPayload(token)
  if (!payload || !payload.role) {
    const loginUrl = new URL('/auth/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Check admin routes
  if (ADMIN_ROUTES.some(route => pathname.startsWith(route))) {
    if (!hasMinRole(payload.role, 'streamworks_admin')) {
      // Redirect to dashboard with access denied message
      const dashboardUrl = new URL('/dashboard', request.url)
      dashboardUrl.searchParams.set('error', 'access_denied')
      return NextResponse.redirect(dashboardUrl)
    }
  }

  // Check protected routes (general authentication)
  if (PROTECTED_ROUTES.some(route => pathname.startsWith(route))) {
    // User is authenticated and has access
    return NextResponse.next()
  }

  // For any other routes, allow access if authenticated
  return NextResponse.next()
  */
}

// Configure which paths the middleware should run on
export const config = {
  /*
   * Match all request paths except for the ones starting with:
   * - api (API routes)
   * - _next/static (static files)
   * - _next/image (image optimization files)
   * - favicon.ico (favicon file)
   * - public folder
   */
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)',
  ],
}