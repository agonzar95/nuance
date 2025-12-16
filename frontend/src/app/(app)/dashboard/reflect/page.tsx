'use client'

/**
 * REF: Reflection Page
 *
 * End-of-day review page that helps users:
 * - Celebrate wins (high-avoidance completions)
 * - Review remaining tasks (roll to tomorrow or drop)
 * - Capture thoughts for tomorrow
 *
 * Uses:
 * - WinHighlights (REF-003)
 * - RemainingTaskCard (REF-005)
 * - TomorrowQuickCapture (REF-006)
 */

import { useState, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { WinHighlights } from '@/components/reflection/WinHighlights'
import { RemainingTaskCard } from '@/components/reflection/RemainingTaskCard'
import { TomorrowQuickCapture } from '@/components/reflection/TomorrowQuickCapture'
import { Spinner } from '@/components/ui/Loading'
import { api } from '@/lib/api'
import { queryKeys } from '@/lib/query'
import type { Action } from '@/types/api'

// ============================================================================
// Helpers
// ============================================================================

function getTodayDateString(): string {
  return new Date().toISOString().split('T')[0]
}

function getTomorrowDateString(): string {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
}

// ============================================================================
// Component
// ============================================================================

type ReflectionPhase = 'wins' | 'remaining' | 'capture' | 'done'

export default function ReflectPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const today = getTodayDateString()
  const tomorrow = getTomorrowDateString()

  const [phase, setPhase] = useState<ReflectionPhase>('wins')

  // Fetch today's completed actions
  const completedQuery = useQuery({
    queryKey: ['actions', 'completed', today],
    queryFn: () => api.actions.list({ status: 'done', planned_date: today }),
  })

  // Fetch today's remaining (not completed) actions
  const remainingQuery = useQuery({
    queryKey: ['actions', 'remaining', today],
    queryFn: () => api.actions.list({ status: 'planned', planned_date: today }),
  })

  // Completed actions with high avoidance (wins)
  const wins = useMemo(() => {
    if (!completedQuery.data?.actions) return []
    return completedQuery.data.actions.filter((a) => a.avoidance_weight >= 4)
  }, [completedQuery.data])

  // Remaining actions
  const remainingActions = useMemo(() => {
    return remainingQuery.data?.actions || []
  }, [remainingQuery.data])

  // Roll mutation (move to tomorrow)
  const rollMutation = useMutation({
    mutationFn: async (actionId: string) => {
      return api.actions.update(actionId, {
        status: 'rolled',
        planned_date: tomorrow,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
    },
  })

  // Drop mutation
  const dropMutation = useMutation({
    mutationFn: async (actionId: string) => {
      return api.actions.update(actionId, {
        status: 'dropped',
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
    },
  })

  // Capture mutation
  const captureMutation = useMutation({
    mutationFn: async (text: string) => {
      return api.actions.create({
        title: text,
        status: 'inbox',
        estimated_minutes: 15,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
    },
  })

  // Handlers
  const handleContinueFromWins = useCallback(() => {
    if (remainingActions.length > 0) {
      setPhase('remaining')
    } else {
      setPhase('capture')
    }
  }, [remainingActions.length])

  const handleContinueFromRemaining = useCallback(() => {
    setPhase('capture')
  }, [])

  const handleCapture = useCallback(
    async (text: string) => {
      return captureMutation.mutateAsync(text)
    },
    [captureMutation]
  )

  const handleDone = useCallback(() => {
    setPhase('done')
  }, [])

  const handleFinish = useCallback(() => {
    router.push('/dashboard')
  }, [router])

  const isLoading = completedQuery.isLoading || remainingQuery.isLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="text-gray-500 hover:text-gray-700"
              aria-label="Back to dashboard"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Link>
            <h1 className="text-lg font-semibold text-gray-900">End of Day Reflection</h1>
          </div>
          <span className="text-sm text-gray-500">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 py-8">
        {/* Wins Phase */}
        {phase === 'wins' && (
          <div className="space-y-6">
            {wins.length > 0 ? (
              <>
                <WinHighlights wins={wins} />
                <div className="text-center pt-4">
                  <button
                    onClick={handleContinueFromWins}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    {remainingActions.length > 0 ? 'Review Remaining Tasks' : 'Capture Thoughts for Tomorrow'}
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">
                  <span role="img" aria-label="Calendar">
                    {completedQuery.data?.actions?.length ? '📊' : '🌅'}
                  </span>
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  {completedQuery.data?.actions?.length
                    ? `You completed ${completedQuery.data.actions.length} task${completedQuery.data.actions.length === 1 ? '' : 's'} today`
                    : "No tasks completed today - that's okay!"}
                </h2>
                <p className="text-gray-600 mb-6">
                  {completedQuery.data?.actions?.length
                    ? 'Every step forward counts.'
                    : "Tomorrow is a new opportunity."}
                </p>
                <button
                  onClick={handleContinueFromWins}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {remainingActions.length > 0 ? 'Review Remaining Tasks' : 'Continue'}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Remaining Tasks Phase */}
        {phase === 'remaining' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Remaining Tasks
              </h2>
              <p className="text-gray-600">
                Decide what to do with tasks you didn't get to today.
              </p>
            </div>

            {remainingActions.length > 0 ? (
              <div className="space-y-3">
                {remainingActions.map((action) => (
                  <RemainingTaskCard
                    key={action.id}
                    action={action}
                    onRoll={() => rollMutation.mutate(action.id)}
                    onDrop={() => dropMutation.mutate(action.id)}
                    isRolling={rollMutation.isPending}
                    isDropping={dropMutation.isPending}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                All remaining tasks have been processed.
              </div>
            )}

            <div className="text-center pt-4">
              <button
                onClick={handleContinueFromRemaining}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Continue to Capture
              </button>
            </div>
          </div>
        )}

        {/* Capture Phase */}
        {phase === 'capture' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Thoughts for Tomorrow
              </h2>
              <p className="text-gray-600">
                Capture any quick thoughts before you wrap up.
              </p>
            </div>

            <TomorrowQuickCapture
              onCapture={handleCapture}
              onDone={handleDone}
            />
          </div>
        )}

        {/* Done Phase */}
        {phase === 'done' && (
          <div className="text-center py-12">
            <div className="text-5xl mb-4">
              <span role="img" aria-label="Moon">
                🌙
              </span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Day Complete
            </h2>
            <p className="text-gray-600 mb-8">
              Rest well. Tomorrow is ready for you.
            </p>
            <button
              onClick={handleFinish}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Finish
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
