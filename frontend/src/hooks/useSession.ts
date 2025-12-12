/**
 * SUB-006: Session Handling
 *
 * React hooks for managing authentication session state.
 * Handles session persistence, refresh, and auth state changes.
 */

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import type { User, Session, AuthChangeEvent } from '@supabase/supabase-js'

interface UseSessionReturn {
  user: User | null
  session: Session | null
  isLoading: boolean
  isAuthenticated: boolean
  signOut: () => Promise<void>
}

/**
 * Hook for managing auth session with automatic refresh and state sync.
 *
 * @example
 * ```tsx
 * const { user, isLoading, isAuthenticated, signOut } = useSession()
 *
 * if (isLoading) return <Loading />
 *
 * if (!isAuthenticated) {
 *   return <Redirect to="/login" />
 * }
 *
 * return <div>Welcome, {user?.email}</div>
 * ```
 */
export function useSession(): UseSessionReturn {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const supabase = createClient()

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setIsLoading(false)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, session: Session | null) => {
        setSession(session)
        setUser(session?.user ?? null)

        if (event === 'SIGNED_OUT') {
          router.push('/login')
        } else if (event === 'TOKEN_REFRESHED') {
          // Session refreshed automatically by Supabase
          console.debug('Session token refreshed')
        } else if (event === 'USER_UPDATED') {
          // User data changed
          setUser(session?.user ?? null)
        }
      }
    )

    return () => {
      subscription.unsubscribe()
    }
  }, [router])

  const signOut = useCallback(async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    // Router redirect handled by onAuthStateChange
  }, [])

  return {
    user,
    session,
    isLoading,
    isAuthenticated: !!session,
    signOut,
  }
}

/**
 * Hook that redirects to login if not authenticated.
 * Use this in protected pages/components.
 *
 * @example
 * ```tsx
 * // In a protected page
 * const { user, isLoading } = useRequireAuth()
 *
 * if (isLoading) return <Loading />
 *
 * // User is guaranteed to be authenticated here
 * return <Dashboard user={user!} />
 * ```
 */
export function useRequireAuth(redirectTo = '/login') {
  const { user, session, isLoading, signOut } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !session) {
      router.push(redirectTo)
    }
  }, [isLoading, session, router, redirectTo])

  return { user, session, isLoading, signOut }
}

/**
 * Hook that redirects to dashboard if already authenticated.
 * Use this in login/signup pages.
 *
 * @example
 * ```tsx
 * // In login page
 * useRedirectIfAuthenticated('/dashboard')
 * ```
 */
export function useRedirectIfAuthenticated(redirectTo = '/dashboard') {
  const { session, isLoading } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && session) {
      router.push(redirectTo)
    }
  }, [isLoading, session, router, redirectTo])
}
