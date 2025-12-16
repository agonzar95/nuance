'use client'

/**
 * INF-009: Onboarding Page
 *
 * Displays the onboarding wizard for new users.
 * Users are redirected here if profile.onboarding_completed is false.
 */

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { OnboardingWizard } from '@/components/onboarding/OnboardingWizard'
import { useProfile } from '@/hooks/useProfile'
import { Spinner } from '@/components/ui/Loading'

export default function OnboardingPage() {
  const router = useRouter()
  const { profile, isLoading, updateProfile } = useProfile()

  // Redirect to dashboard if already onboarded
  useEffect(() => {
    if (profile && profile.onboarding_completed) {
      router.replace('/dashboard')
    }
  }, [profile, router])

  // Show loading while checking profile
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner size="lg" />
      </div>
    )
  }

  // If no profile, something is wrong - redirect to login
  if (!profile) {
    router.replace('/login')
    return null
  }

  // If already onboarded, show loading (will redirect)
  if (profile.onboarding_completed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <OnboardingWizard
      initialTimezone={profile.timezone}
      onUpdateProfile={updateProfile}
      onComplete={() => {
        // The wizard handles the redirect
      }}
    />
  )
}
