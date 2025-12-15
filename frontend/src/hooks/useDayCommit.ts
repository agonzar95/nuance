'use client'

/**
 * PLN-005: Day Commit Hook
 *
 * Handles committing to the day's plan and transitioning to focus mode.
 * - Validates at least one action is selected
 * - Updates action statuses to 'planned'
 * - Navigates to focus mode with first action
 */

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'

// ============================================================================
// Types
// ============================================================================

export interface DayCommitResult {
  /** Commit the day's plan and navigate to focus mode */
  commitDay: () => Promise<void>
  /** Whether commit is in progress */
  isCommitting: boolean
  /** Whether commit is possible (has actions) */
  canCommit: boolean
  /** Error message if commit failed */
  error: string | null
  /** Clear error state */
  clearError: () => void
}

interface CommitOptions {
  /** Callback after successful commit */
  onSuccess?: () => void
  /** Callback on error */
  onError?: (error: Error) => void
}

// ============================================================================
// Hook
// ============================================================================

export function useDayCommit(
  actionIds: string[],
  options: CommitOptions = {}
): DayCommitResult {
  const router = useRouter()
  const [isCommitting, setIsCommitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canCommit = actionIds.length > 0

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const commitDay = useCallback(async () => {
    if (!canCommit || isCommitting) return

    setIsCommitting(true)
    setError(null)

    try {
      // Update each action to 'planned' status with today's date
      const today = new Date().toISOString().split('T')[0]

      // Update all actions in parallel
      await Promise.all(
        actionIds.map((id, index) =>
          api.actions.update(id, {
            status: 'planned',
            planned_date: today,
            position: index,
          })
        )
      )

      options.onSuccess?.()

      // Navigate to focus mode with first action
      router.push(`/focus?action=${actionIds[0]}`)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start day'
      setError(errorMessage)
      options.onError?.(err instanceof Error ? err : new Error(errorMessage))
    } finally {
      setIsCommitting(false)
    }
  }, [actionIds, canCommit, isCommitting, router, options])

  return {
    commitDay,
    isCommitting,
    canCommit,
    error,
    clearError,
  }
}

// ============================================================================
// Simplified Hook (just for status tracking)
// ============================================================================

export function useDayCommitStatus(actionIds: string[]) {
  const [isCommitting, setIsCommitting] = useState(false)

  return {
    isCommitting,
    setIsCommitting,
    canCommit: actionIds.length > 0,
  }
}
