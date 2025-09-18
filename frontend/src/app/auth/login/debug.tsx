'use client'

import { useAuthContext } from '@/contexts/AuthContext'

export function AuthDebug() {
  const auth = useAuthContext()

  console.log('Auth Context State:', {
    user: auth.user,
    isLoading: auth.isLoading,
    isAuthenticated: auth.isAuthenticated,
    error: auth.error
  })

  return (
    <div className="fixed bottom-4 right-4 bg-black/80 text-white p-4 rounded text-xs max-w-xs">
      <div>Auth Debug:</div>
      <div>User: {auth.user?.email || 'none'}</div>
      <div>Loading: {auth.isLoading ? 'yes' : 'no'}</div>
      <div>Authenticated: {auth.isAuthenticated ? 'yes' : 'no'}</div>
      <div>Error: {auth.error || 'none'}</div>
    </div>
  )
}