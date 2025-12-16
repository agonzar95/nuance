'use client'

/**
 * Dashboard Layout
 *
 * Wraps all dashboard pages and ensures:
 * 1. User is authenticated (redirects to /login if not)
 * 2. User has completed onboarding (redirects to /onboarding if not)
 */

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useProfile } from '@/hooks/useProfile'
import { useSession } from '@/hooks/useSession'
import { PageLoader } from '@/components/ui/Loading'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { session, isLoading: sessionLoading } = useSession()
  const { profile, isLoading: profileLoading } = useProfile()

  const isLoading = sessionLoading || profileLoading

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!sessionLoading && !session) {
      router.replace('/login')
    }
  }, [session, sessionLoading, router])

  // Redirect to onboarding if not completed
  useEffect(() => {
    if (!profileLoading && profile && !profile.onboarding_completed) {
      router.replace('/onboarding')
    }
  }, [profile, profileLoading, router])

  // Show loading while checking auth and onboarding status
  if (isLoading) {
    return <PageLoader />
  }

  // Not authenticated - show loading while redirecting
  if (!session) {
    return <PageLoader />
  }

  // Not onboarded - show loading while redirecting
  if (profile && !profile.onboarding_completed) {
    return <PageLoader />
  }

  return <>{children}</>
}
