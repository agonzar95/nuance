/**
 * SUB-013: Real-time Subscriptions
 *
 * React hook for subscribing to real-time action updates.
 * Automatically syncs local state when actions are created,
 * updated, or deleted (e.g., from Telegram or another tab).
 */

import { useEffect, useState, useCallback } from 'react'
import { createClient } from '@/lib/supabase/client'
import type { RealtimePostgresChangesPayload } from '@supabase/supabase-js'

// Action type matching database schema
export interface Action {
  id: string
  user_id: string
  parent_id: string | null
  title: string
  raw_input: string | null
  status: 'inbox' | 'candidate' | 'planned' | 'active' | 'done' | 'dropped' | 'rolled'
  complexity: 'atomic' | 'composite' | 'project'
  avoidance_weight: number
  estimated_minutes: number
  actual_minutes: number | null
  planned_date: string | null
  completed_at: string | null
  position: number
  created_at: string
  updated_at: string
}

type ActionPayload = RealtimePostgresChangesPayload<Action>

interface UseRealtimeActionsOptions {
  /** Filter actions by status */
  status?: Action['status'] | Action['status'][]
  /** Filter actions by planned date */
  plannedDate?: string
  /** Called when an action is inserted */
  onInsert?: (action: Action) => void
  /** Called when an action is updated */
  onUpdate?: (action: Action) => void
  /** Called when an action is deleted */
  onDelete?: (action: Action) => void
}

/**
 * Hook for real-time action updates with automatic state synchronization.
 *
 * @example
 * ```tsx
 * const { actions, isSubscribed } = useRealtimeActions(initialActions, {
 *   status: ['inbox', 'candidate'],
 *   onInsert: (action) => console.log('New action:', action)
 * })
 * ```
 */
export function useRealtimeActions(
  initialActions: Action[],
  options: UseRealtimeActionsOptions = {}
) {
  const [actions, setActions] = useState<Action[]>(initialActions)
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const { status, plannedDate, onInsert, onUpdate, onDelete } = options

  // Filter function based on options
  const matchesFilter = useCallback(
    (action: Action): boolean => {
      if (status) {
        const statuses = Array.isArray(status) ? status : [status]
        if (!statuses.includes(action.status)) return false
      }
      if (plannedDate && action.planned_date !== plannedDate) return false
      return true
    },
    [status, plannedDate]
  )

  useEffect(() => {
    const supabase = createClient()

    const channel = supabase
      .channel('actions-realtime')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'actions',
        },
        (payload: ActionPayload) => {
          if (payload.eventType === 'INSERT') {
            const newAction = payload.new as Action
            if (matchesFilter(newAction)) {
              setActions((prev) => [...prev, newAction])
              onInsert?.(newAction)
            }
          } else if (payload.eventType === 'UPDATE') {
            const updatedAction = payload.new as Action
            setActions((prev) => {
              const existing = prev.find((a) => a.id === updatedAction.id)

              if (existing && matchesFilter(updatedAction)) {
                // Update existing action
                return prev.map((a) =>
                  a.id === updatedAction.id ? updatedAction : a
                )
              } else if (existing && !matchesFilter(updatedAction)) {
                // Remove action that no longer matches filter
                return prev.filter((a) => a.id !== updatedAction.id)
              } else if (!existing && matchesFilter(updatedAction)) {
                // Add action that now matches filter
                return [...prev, updatedAction]
              }
              return prev
            })
            onUpdate?.(updatedAction)
          } else if (payload.eventType === 'DELETE') {
            const deletedAction = payload.old as Action
            setActions((prev) => prev.filter((a) => a.id !== deletedAction.id))
            onDelete?.(deletedAction)
          }
        }
      )
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          setIsSubscribed(true)
          setError(null)
        } else if (status === 'CHANNEL_ERROR') {
          setError(new Error('Failed to subscribe to real-time updates'))
          setIsSubscribed(false)
        }
      })

    return () => {
      supabase.removeChannel(channel)
      setIsSubscribed(false)
    }
  }, [matchesFilter, onInsert, onUpdate, onDelete])

  // Update actions when initialActions change (e.g., after refetch)
  useEffect(() => {
    setActions(initialActions)
  }, [initialActions])

  return {
    actions,
    isSubscribed,
    error,
    /** Manually add an action to local state (optimistic update) */
    addAction: useCallback((action: Action) => {
      if (matchesFilter(action)) {
        setActions((prev) => [...prev, action])
      }
    }, [matchesFilter]),
    /** Manually update an action in local state (optimistic update) */
    updateAction: useCallback((id: string, updates: Partial<Action>) => {
      setActions((prev) =>
        prev.map((a) => (a.id === id ? { ...a, ...updates } : a))
      )
    }, []),
    /** Manually remove an action from local state (optimistic update) */
    removeAction: useCallback((id: string) => {
      setActions((prev) => prev.filter((a) => a.id !== id))
    }, []),
  }
}

/**
 * Hook for subscribing to real-time profile updates.
 */
export function useRealtimeProfile(userId: string) {
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null)
  const [isSubscribed, setIsSubscribed] = useState(false)

  useEffect(() => {
    const supabase = createClient()

    const channel = supabase
      .channel('profile-realtime')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'profiles',
          filter: `id=eq.${userId}`,
        },
        (payload) => {
          setProfile(payload.new as Record<string, unknown>)
        }
      )
      .subscribe((status) => {
        setIsSubscribed(status === 'SUBSCRIBED')
      })

    return () => {
      supabase.removeChannel(channel)
    }
  }, [userId])

  return { profile, isSubscribed }
}
