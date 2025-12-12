/**
 * SUB-005: Profile Management
 *
 * React hook for fetching and updating user profile data.
 * Provides optimistic updates and error handling.
 */

import { useState, useEffect, useCallback } from 'react'
import { createClient } from '@/lib/supabase/client'

export interface Profile {
  id: string
  timezone: string
  telegram_chat_id: string | null
  notification_channel: 'email' | 'telegram' | 'both'
  notification_enabled: boolean
  onboarding_completed: boolean
  created_at: string
  updated_at: string
}

export interface ProfileUpdate {
  timezone?: string
  telegram_chat_id?: string | null
  notification_channel?: 'email' | 'telegram' | 'both'
  notification_enabled?: boolean
  onboarding_completed?: boolean
}

interface UseProfileReturn {
  profile: Profile | null
  isLoading: boolean
  error: Error | null
  updateProfile: (updates: ProfileUpdate) => Promise<void>
  refetch: () => Promise<void>
}

/**
 * Hook for managing user profile data.
 *
 * @example
 * ```tsx
 * const { profile, isLoading, updateProfile } = useProfile()
 *
 * if (isLoading) return <Loading />
 *
 * return (
 *   <div>
 *     <p>Timezone: {profile?.timezone}</p>
 *     <button onClick={() => updateProfile({ timezone: 'America/New_York' })}>
 *       Change timezone
 *     </button>
 *   </div>
 * )
 * ```
 */
export function useProfile(): UseProfileReturn {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchProfile = useCallback(async () => {
    const supabase = createClient()

    try {
      setIsLoading(true)
      setError(null)

      // Get current user
      const { data: { user }, error: userError } = await supabase.auth.getUser()

      if (userError) {
        throw new Error(userError.message)
      }

      if (!user) {
        setProfile(null)
        return
      }

      // Fetch profile
      const { data, error: profileError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single()

      if (profileError) {
        throw new Error(profileError.message)
      }

      setProfile(data as Profile)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch profile'))
    } finally {
      setIsLoading(false)
    }
  }, [])

  const updateProfile = useCallback(async (updates: ProfileUpdate) => {
    const supabase = createClient()

    if (!profile) {
      throw new Error('No profile loaded')
    }

    // Optimistic update
    const previousProfile = profile
    setProfile({ ...profile, ...updates, updated_at: new Date().toISOString() })

    try {
      const { error: updateError } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', profile.id)

      if (updateError) {
        throw new Error(updateError.message)
      }
    } catch (err) {
      // Rollback on error
      setProfile(previousProfile)
      throw err
    }
  }, [profile])

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  return {
    profile,
    isLoading,
    error,
    updateProfile,
    refetch: fetchProfile,
  }
}

/**
 * Detect user's timezone from browser.
 */
export function detectTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone
  } catch {
    return 'UTC'
  }
}

/**
 * Get list of common timezones for selection.
 */
export const COMMON_TIMEZONES = [
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'America/Anchorage',
  'Pacific/Honolulu',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'Asia/Tokyo',
  'Asia/Shanghai',
  'Asia/Kolkata',
  'Australia/Sydney',
  'Pacific/Auckland',
] as const
