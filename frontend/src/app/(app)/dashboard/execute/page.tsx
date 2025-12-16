'use client'

/**
 * EXE-013: Focus Mode Page
 *
 * Page-level state machine managing focus mode phases:
 * - loading: Fetching action data
 * - breakdown: Show breakdown prompt for complex tasks
 * - working: Main focus mode with timer
 * - stuck-options: Show stuck reason picker
 * - coaching: AI coaching overlay
 * - completing: Task completion flow
 * - avoidance-ack: Celebrate high-avoidance completions
 * - rest: Rest screen before next task
 *
 * Coordinates all execution components (EXE-001 through EXE-012).
 */

import { useReducer, useEffect, useCallback } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { FocusModeContainer } from '@/components/execution/FocusModeContainer'
import { FocusTaskCard } from '@/components/execution/FocusTaskCard'
import { BreakdownPrompt } from '@/components/execution/BreakdownPrompt'
import { StuckOptions } from '@/components/execution/StuckOptions'
import { CoachingOverlay, type StuckReason } from '@/components/execution/CoachingOverlay'
import { CompleteTaskFlow } from '@/components/execution/CompleteTaskFlow'
import { AvoidanceAcknowledgment } from '@/components/execution/AvoidanceAcknowledgment'
import { RestScreen } from '@/components/execution/RestScreen'
import { Spinner } from '@/components/ui/Loading'
import { api } from '@/lib/api'
import { queryKeys } from '@/lib/query'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

type FocusPhase =
  | 'loading'
  | 'breakdown'
  | 'working'
  | 'stuck-options'
  | 'coaching'
  | 'completing'
  | 'avoidance-ack'
  | 'rest'

interface FocusState {
  phase: FocusPhase
  action: Action | null
  elapsedSeconds: number
  stuckReason: StuckReason | null
}

type FocusAction =
  | { type: 'SET_ACTION'; action: Action }
  | { type: 'SET_PHASE'; phase: FocusPhase }
  | { type: 'SET_STUCK_REASON'; reason: StuckReason }
  | { type: 'TICK' }
  | { type: 'RESET' }

// ============================================================================
// Reducer
// ============================================================================

const initialState: FocusState = {
  phase: 'loading',
  action: null,
  elapsedSeconds: 0,
  stuckReason: null,
}

function focusReducer(state: FocusState, action: FocusAction): FocusState {
  switch (action.type) {
    case 'SET_ACTION':
      return {
        ...state,
        action: action.action,
        phase: determineInitialPhase(action.action),
      }

    case 'SET_PHASE':
      return {
        ...state,
        phase: action.phase,
      }

    case 'SET_STUCK_REASON':
      return {
        ...state,
        stuckReason: action.reason,
      }

    case 'TICK':
      return {
        ...state,
        elapsedSeconds: state.elapsedSeconds + 1,
      }

    case 'RESET':
      return initialState

    default:
      return state
  }
}

function determineInitialPhase(action: Action): FocusPhase {
  // If complex and no subtasks, show breakdown first
  if (action.complexity === 'composite' || action.complexity === 'project') {
    return 'breakdown'
  }
  return 'working'
}

// ============================================================================
// Component
// ============================================================================

export default function ExecutePage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const queryClient = useQueryClient()
  const actionId = searchParams.get('actionId')

  const [state, dispatch] = useReducer(focusReducer, initialState)

  // Fetch action data
  const actionQuery = useQuery({
    queryKey: queryKeys.actions.detail(actionId || ''),
    queryFn: () => api.actions.get(actionId!),
    enabled: !!actionId,
  })

  // Complete action mutation
  const completeMutation = useMutation({
    mutationFn: async (actualMinutes: number) => {
      return api.actions.complete(actionId!, actualMinutes)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
    },
  })

  // Set action when loaded
  useEffect(() => {
    if (actionQuery.data) {
      dispatch({ type: 'SET_ACTION', action: actionQuery.data })
    }
  }, [actionQuery.data])

  // Timer tick
  useEffect(() => {
    if (state.phase === 'working') {
      const interval = setInterval(() => {
        dispatch({ type: 'TICK' })
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [state.phase])

  // Handlers
  const handleBreakdownComplete = useCallback(() => {
    dispatch({ type: 'SET_PHASE', phase: 'working' })
  }, [])

  const handleStuck = useCallback(() => {
    dispatch({ type: 'SET_PHASE', phase: 'stuck-options' })
  }, [])

  const handleStuckReasonSelect = useCallback((reason: StuckReason) => {
    dispatch({ type: 'SET_STUCK_REASON', reason })
    if (reason === 'too_big') {
      dispatch({ type: 'SET_PHASE', phase: 'breakdown' })
    } else {
      dispatch({ type: 'SET_PHASE', phase: 'coaching' })
    }
  }, [])

  const handleStuckCancel = useCallback(() => {
    dispatch({ type: 'SET_PHASE', phase: 'working' })
  }, [])

  const handleCoachingClose = useCallback(() => {
    dispatch({ type: 'SET_PHASE', phase: 'working' })
  }, [])

  const handleComplete = useCallback(() => {
    dispatch({ type: 'SET_PHASE', phase: 'completing' })
  }, [])

  const handleCompleteConfirm = useCallback(async () => {
    const actualMinutes = Math.ceil(state.elapsedSeconds / 60)
    await completeMutation.mutateAsync(actualMinutes)

    if (state.action && state.action.avoidance_weight >= 4) {
      dispatch({ type: 'SET_PHASE', phase: 'avoidance-ack' })
    } else {
      dispatch({ type: 'SET_PHASE', phase: 'rest' })
    }
  }, [completeMutation, state.elapsedSeconds, state.action])

  const handleAvoidanceAckContinue = useCallback(() => {
    dispatch({ type: 'SET_PHASE', phase: 'rest' })
  }, [])

  const handleNext = useCallback(async () => {
    // Fetch next planned action
    const today = new Date().toISOString().split('T')[0]
    const response = await api.actions.list({ planned_date: today, status: 'planned', limit: 1 })

    if (response.actions.length > 0) {
      const nextAction = response.actions[0]
      dispatch({ type: 'RESET' })
      router.push(`/dashboard/execute?actionId=${nextAction.id}`)
    } else {
      router.push('/dashboard/reflect')
    }
  }, [router])

  const handleExit = useCallback(() => {
    router.push('/dashboard')
  }, [router])

  // No action ID provided
  if (!actionId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <h1 className="text-xl font-semibold mb-4">No Task Selected</h1>
        <p className="text-gray-600 mb-6">Select a task from your plan to start focus mode.</p>
        <button
          onClick={() => router.push('/dashboard/plan')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Go to Planning
        </button>
      </div>
    )
  }

  // Loading state
  if (state.phase === 'loading' || actionQuery.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
      </div>
    )
  }

  // Error state
  if (actionQuery.error || !state.action) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <h1 className="text-xl font-semibold mb-4">Task Not Found</h1>
        <p className="text-gray-600 mb-6">The requested task could not be loaded.</p>
        <button
          onClick={() => router.push('/dashboard')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Go to Dashboard
        </button>
      </div>
    )
  }

  const { action, phase, stuckReason, elapsedSeconds } = state

  return (
    <>
      {/* Breakdown Phase */}
      {phase === 'breakdown' && (
        <div className="min-h-screen bg-background p-6 flex items-center justify-center">
          <BreakdownPrompt
            action={action}
            onSubmitStep={async (step) => {
              // Could save the step as a subtask here
              console.log('First step:', step)
              handleBreakdownComplete()
            }}
            onSkip={handleBreakdownComplete}
          />
        </div>
      )}

      {/* Working Phase */}
      {phase === 'working' && (
        <FocusModeContainer
          action={action}
          onComplete={handleComplete}
          onStuck={handleStuck}
          onExit={handleExit}
        >
          <FocusTaskCard action={action} />
        </FocusModeContainer>
      )}

      {/* Stuck Options Phase */}
      {phase === 'stuck-options' && (
        <div className="fixed inset-0 bg-background/95 z-50 flex items-center justify-center p-6">
          <StuckOptions
            onSelect={handleStuckReasonSelect}
            onCancel={handleStuckCancel}
          />
        </div>
      )}

      {/* Coaching Phase */}
      {phase === 'coaching' && stuckReason && (
        <CoachingOverlay
          action={action}
          stuckReason={stuckReason}
          open={true}
          onClose={handleCoachingClose}
        />
      )}

      {/* Completing Phase */}
      {phase === 'completing' && (
        <div className="fixed inset-0 bg-background z-50 flex items-center justify-center p-6">
          <CompleteTaskFlow
            action={action}
            elapsedSeconds={elapsedSeconds}
            onComplete={async () => handleCompleteConfirm()}
            onSkipReflection={handleCompleteConfirm}
          />
        </div>
      )}

      {/* Avoidance Acknowledgment Phase */}
      {phase === 'avoidance-ack' && (
        <div className="fixed inset-0 bg-background z-50 flex items-center justify-center p-6">
          <AvoidanceAcknowledgment
            action={action}
            onContinue={handleAvoidanceAckContinue}
          />
        </div>
      )}

      {/* Rest Phase */}
      {phase === 'rest' && (
        <div className="fixed inset-0 bg-background z-50">
          <RestScreen
            onReady={handleNext}
            onSkip={handleNext}
          />
        </div>
      )}
    </>
  )
}
