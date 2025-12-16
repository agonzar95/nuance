'use client'

/**
 * PLN-009: Planning Page Container
 *
 * Page-level container that orchestrates planning components:
 * - InboxView (PLN-001) - AI suggestions
 * - TodayView (PLN-002) - Today's planned tasks
 * - PlanningLayout (PLN-003) - Drag-drop between zones
 * - TimeBudget (PLN-006) - Time tracking
 * - AddTaskButton (PLN-007) - Quick add
 *
 * Flow:
 * 1. Fetch AI suggestions and today's actions
 * 2. User drags tasks from inbox to today
 * 3. User can reorder tasks within today
 * 4. User commits plan and navigates to focus mode
 */

import { useState, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { PlanningLayout } from '@/components/planning/PlanningLayout'
import { AddTaskButton } from '@/components/planning/AddTaskButton'
import { Spinner } from '@/components/ui/Loading'
import { api } from '@/lib/api'
import { queryKeys } from '@/lib/query'
import type { Action } from '@/types/api'
import type { Suggestion } from '@/components/planning/InboxView'

// ============================================================================
// Helpers
// ============================================================================

function getTodayDateString(): string {
  return new Date().toISOString().split('T')[0]
}

// Convert inbox actions to suggestions (simulate AI reasoning)
function actionsToSuggestions(actions: Action[]): Suggestion[] {
  return actions.map((action, index) => ({
    action,
    reasoning: getReasoningForAction(action),
    priorityScore: calculatePriorityScore(action, index),
  }))
}

function getReasoningForAction(action: Action): string {
  const reasons: string[] = []

  if (action.avoidance_weight >= 4) {
    reasons.push('High avoidance - tackling it will feel great')
  } else if (action.avoidance_weight >= 2) {
    reasons.push('Moderate avoidance - good to address')
  }

  if (action.estimated_minutes <= 15) {
    reasons.push('Quick win potential')
  } else if (action.estimated_minutes <= 30) {
    reasons.push('Manageable size')
  }

  if (action.complexity === 'atomic') {
    reasons.push('Single-step task')
  }

  return reasons.join(' | ') || 'Available for today'
}

function calculatePriorityScore(action: Action, index: number): number {
  // Higher avoidance = higher priority (tackle hard things)
  // Lower time = higher priority (quick wins)
  // Earlier in list = higher priority
  const avoidanceScore = action.avoidance_weight * 10
  const timeScore = Math.max(0, 30 - action.estimated_minutes)
  const positionScore = Math.max(0, 12 - index)

  return avoidanceScore + timeScore + positionScore
}

// ============================================================================
// Component
// ============================================================================

export default function PlanPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const today = getTodayDateString()

  const [selectedIds, setSelectedIds] = useState<string[]>([])

  // Fetch inbox actions (not planned)
  const inboxQuery = useQuery({
    queryKey: queryKeys.actions.inbox(),
    queryFn: () => api.actions.list({ status: 'inbox', limit: 12 }),
  })

  // Fetch today's planned actions
  const todayQuery = useQuery({
    queryKey: queryKeys.actions.today(today),
    queryFn: () => api.actions.list({ planned_date: today, status: 'planned' }),
  })

  // Convert inbox to suggestions
  const suggestions = useMemo(() => {
    if (!inboxQuery.data?.actions) return []
    return actionsToSuggestions(inboxQuery.data.actions)
  }, [inboxQuery.data])

  // Today's actions
  const todayActions = useMemo(() => {
    return todayQuery.data?.actions || []
  }, [todayQuery.data])

  // Mutation: Add to today
  const addToTodayMutation = useMutation({
    mutationFn: async (actionId: string) => {
      return api.actions.plan(actionId, today)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
    },
  })

  // Mutation: Remove from today
  const removeFromTodayMutation = useMutation({
    mutationFn: async (actionId: string) => {
      return api.actions.unplan(actionId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
    },
  })

  // Mutation: Reorder today
  const reorderMutation = useMutation({
    mutationFn: async (actionIds: string[]) => {
      // Update positions for each action
      const updates = actionIds.map((id, index) =>
        api.actions.update(id, { position: index })
      )
      return Promise.all(updates)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
    },
  })

  // Handlers
  const handleSelect = useCallback((actionId: string) => {
    setSelectedIds((prev) => [...prev, actionId])
  }, [])

  const handleDeselect = useCallback((actionId: string) => {
    setSelectedIds((prev) => prev.filter((id) => id !== actionId))
  }, [])

  const handleAddToToday = useCallback(
    (actionId: string) => {
      addToTodayMutation.mutate(actionId)
    },
    [addToTodayMutation]
  )

  const handleRemoveFromToday = useCallback(
    (actionId: string) => {
      removeFromTodayMutation.mutate(actionId)
    },
    [removeFromTodayMutation]
  )

  const handleReorderToday = useCallback(
    (actionIds: string[]) => {
      reorderMutation.mutate(actionIds)
    },
    [reorderMutation]
  )

  const handleStartDay = useCallback(() => {
    if (todayActions.length > 0) {
      // Navigate to focus mode with first task
      router.push(`/dashboard/execute?actionId=${todayActions[0].id}`)
    }
  }, [router, todayActions])

  const handleAddTask = useCallback(
    (action: Action) => {
      // When a task is added from browse, plan it for today
      addToTodayMutation.mutate(action.id)
    },
    [addToTodayMutation]
  )

  const handleQuickCapture = useCallback(
    async (text: string) => {
      const action = await api.actions.create({
        title: text,
        status: 'inbox',
        estimated_minutes: 15,
      })
      queryClient.invalidateQueries({ queryKey: queryKeys.actions.all })
      return action
    },
    [queryClient]
  )

  const isLoading = inboxQuery.isLoading || todayQuery.isLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
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
            <h1 className="text-lg font-semibold text-gray-900">Plan Your Day</h1>
          </div>
          <AddTaskButton
            onAddTask={handleAddTask}
            onQuickCapture={handleQuickCapture}
            availableActions={inboxQuery.data?.actions || []}
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
        <PlanningLayout
          suggestions={suggestions}
          selectedIds={selectedIds}
          onSelect={handleSelect}
          onDeselect={handleDeselect}
          todayActions={todayActions}
          onAddToToday={handleAddToToday}
          onRemoveFromToday={handleRemoveFromToday}
          onReorderToday={handleReorderToday}
          onStartDay={handleStartDay}
          isInboxLoading={inboxQuery.isLoading}
          isStarting={false}
        />
      </main>
    </div>
  )
}
