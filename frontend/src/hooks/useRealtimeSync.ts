'use client'

/**
 * FE-004: Real-time Handler with React Query Integration
 *
 * Integrates Supabase real-time subscriptions with React Query cache.
 * Automatically syncs changes from any source (other tabs, Telegram, etc.) to the UI.
 */

import { useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { createClient } from '@/lib/supabase/client'
import { queryKeys } from '@/lib/query'
import type { Action, Profile } from '@/types/api'
import type { RealtimePostgresChangesPayload, RealtimeChannel } from '@supabase/supabase-js'

// ============================================================================
// Types
// ============================================================================

type ActionPayload = RealtimePostgresChangesPayload<Action>
type ProfilePayload = RealtimePostgresChangesPayload<Profile>

interface RealtimeSyncOptions {
  /** Whether to subscribe to action changes */
  actions?: boolean
  /** Whether to subscribe to profile changes */
  profile?: boolean
  /** User ID for filtering (required if actions or profile enabled) */
  userId?: string
  /** Callback when subscription status changes */
  onStatusChange?: (status: 'connecting' | 'connected' | 'disconnected' | 'error') => void
}

// ============================================================================
// Main Hook
// ============================================================================

/**
 * Subscribe to Supabase real-time changes and sync with React Query cache.
 *
 * @example
 * ```tsx
 * function App() {
 *   const { userId } = useSession()
 *
 *   // Start real-time sync when user is authenticated
 *   useRealtimeSync({
 *     actions: true,
 *     profile: true,
 *     userId,
 *     onStatusChange: (status) => console.log('Realtime:', status)
 *   })
 *
 *   // ... rest of app
 * }
 * ```
 */
export function useRealtimeSync(options: RealtimeSyncOptions = {}) {
  const { actions = true, profile = true, userId, onStatusChange } = options
  const queryClient = useQueryClient()
  const channelRef = useRef<RealtimeChannel | null>(null)

  useEffect(() => {
    if (!userId) return
    if (!actions && !profile) return

    const supabase = createClient()

    // Create a combined channel for all subscriptions
    const channel = supabase.channel(`user-${userId}-realtime`)
    channelRef.current = channel

    // Subscribe to actions table changes
    if (actions) {
      channel.on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'actions',
          filter: `user_id=eq.${userId}`,
        },
        (payload: ActionPayload) => {
          handleActionChange(queryClient, payload)
        }
      )
    }

    // Subscribe to profile table changes
    if (profile) {
      channel.on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'profiles',
          filter: `id=eq.${userId}`,
        },
        (payload: ProfilePayload) => {
          handleProfileChange(queryClient, payload)
        }
      )
    }

    // Subscribe and track status
    onStatusChange?.('connecting')

    channel.subscribe((status) => {
      switch (status) {
        case 'SUBSCRIBED':
          onStatusChange?.('connected')
          break
        case 'CHANNEL_ERROR':
          onStatusChange?.('error')
          break
        case 'TIMED_OUT':
          onStatusChange?.('error')
          break
        case 'CLOSED':
          onStatusChange?.('disconnected')
          break
      }
    })

    // Cleanup on unmount or when dependencies change
    return () => {
      supabase.removeChannel(channel)
      channelRef.current = null
      onStatusChange?.('disconnected')
    }
  }, [userId, actions, profile, queryClient, onStatusChange])

  return {
    /** Whether the real-time channel is active */
    isActive: !!channelRef.current,
  }
}

// ============================================================================
// Change Handlers
// ============================================================================

/**
 * Handle action table changes and update React Query cache
 */
function handleActionChange(
  queryClient: ReturnType<typeof useQueryClient>,
  payload: ActionPayload
) {
  const { eventType } = payload

  if (eventType === 'INSERT') {
    const newAction = payload.new as Action

    // Update all list queries that might include this action
    queryClient.setQueriesData<{ actions: Action[]; total: number }>(
      { queryKey: queryKeys.actions.lists() },
      (old) => {
        if (!old) return old
        // Check if action already exists (avoid duplicates from optimistic updates)
        if (old.actions.some((a) => a.id === newAction.id)) {
          return old
        }
        return {
          ...old,
          actions: [...old.actions, newAction],
          total: old.total + 1,
        }
      }
    )

    // Also set the detail query
    queryClient.setQueryData(queryKeys.actions.detail(newAction.id), newAction)
  }

  if (eventType === 'UPDATE') {
    const updatedAction = payload.new as Action

    // Update in all list queries
    queryClient.setQueriesData<{ actions: Action[]; total: number }>(
      { queryKey: queryKeys.actions.lists() },
      (old) => {
        if (!old) return old

        // Check if action exists in this list
        const existingIndex = old.actions.findIndex((a) => a.id === updatedAction.id)

        if (existingIndex >= 0) {
          // Check if action still belongs in this list (status/date might have changed)
          // For now, just update - filtering will happen on next refetch
          const newActions = [...old.actions]
          newActions[existingIndex] = updatedAction
          return { ...old, actions: newActions }
        }

        return old
      }
    )

    // Update detail query
    queryClient.setQueryData(queryKeys.actions.detail(updatedAction.id), updatedAction)
  }

  if (eventType === 'DELETE') {
    const deletedAction = payload.old as Action

    // Remove from all list queries
    queryClient.setQueriesData<{ actions: Action[]; total: number }>(
      { queryKey: queryKeys.actions.lists() },
      (old) => {
        if (!old) return old
        const filtered = old.actions.filter((a) => a.id !== deletedAction.id)
        if (filtered.length === old.actions.length) return old
        return {
          ...old,
          actions: filtered,
          total: old.total - 1,
        }
      }
    )

    // Remove detail query
    queryClient.removeQueries({ queryKey: queryKeys.actions.detail(deletedAction.id) })
  }
}

/**
 * Handle profile table changes and update React Query cache
 */
function handleProfileChange(
  queryClient: ReturnType<typeof useQueryClient>,
  payload: ProfilePayload
) {
  if (payload.eventType === 'UPDATE') {
    const updatedProfile = payload.new as Profile
    queryClient.setQueryData(queryKeys.profile.current(), updatedProfile)
  }
}

// ============================================================================
// Specialized Hooks
// ============================================================================

/**
 * Hook specifically for syncing today's actions in real-time.
 * Use this in the Today/Plan view.
 */
export function useRealtimeTodayActions(userId: string | undefined, date?: string) {
  const queryClient = useQueryClient()
  const today = date ?? new Date().toISOString().split('T')[0]

  useEffect(() => {
    if (!userId) return

    const supabase = createClient()

    const channel = supabase
      .channel(`today-${userId}-${today}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'actions',
          filter: `user_id=eq.${userId}`,
        },
        (payload: ActionPayload) => {
          // Only invalidate today's query - let React Query refetch
          if (payload.eventType !== 'UPDATE') {
            queryClient.invalidateQueries({
              queryKey: queryKeys.actions.today(today),
            })
            return
          }

          // For updates, check if planned_date changed
          const action = payload.new as Action
          const oldAction = payload.old as Partial<Action>

          if (
            action.planned_date === today ||
            oldAction.planned_date === today
          ) {
            queryClient.invalidateQueries({
              queryKey: queryKeys.actions.today(today),
            })
          }
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [userId, today, queryClient])
}

/**
 * Hook specifically for syncing inbox actions in real-time.
 * Use this in the Inbox view.
 */
export function useRealtimeInboxActions(userId: string | undefined) {
  const queryClient = useQueryClient()

  useEffect(() => {
    if (!userId) return

    const supabase = createClient()

    const channel = supabase
      .channel(`inbox-${userId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'actions',
          filter: `user_id=eq.${userId}`,
        },
        (payload: ActionPayload) => {
          const action = (payload.new || payload.old) as Action

          // Check if this affects inbox
          if (
            action.status === 'inbox' ||
            (payload.old as Partial<Action>)?.status === 'inbox'
          ) {
            queryClient.invalidateQueries({
              queryKey: queryKeys.actions.inbox(),
            })
          }
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [userId, queryClient])
}
