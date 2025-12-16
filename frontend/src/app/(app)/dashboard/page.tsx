'use client'

/**
 * Dashboard Page
 *
 * Main authenticated view showing daily workflow options:
 * - Capture: Add new thoughts/tasks
 * - Plan: Organize today's work
 * - Execute: Focus mode for current task
 * - Reflect: End of day review
 */

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { signOut } from '@/lib/auth'
import { api } from '@/lib/api'
import { queryKeys } from '@/lib/query'

type WorkflowPhase = 'capture' | 'plan' | 'execute' | 'reflect'

const phases: { id: WorkflowPhase; label: string; description: string; icon: string }[] = [
  {
    id: 'capture',
    label: 'Capture',
    description: 'Dump thoughts and tasks without organizing',
    icon: '💭',
  },
  {
    id: 'plan',
    label: 'Plan',
    description: 'Choose what to work on today',
    icon: '📋',
  },
  {
    id: 'execute',
    label: 'Execute',
    description: 'Focus on one task at a time',
    icon: '🎯',
  },
  {
    id: 'reflect',
    label: 'Reflect',
    description: 'Review your day and prepare for tomorrow',
    icon: '🌙',
  },
]

function getTodayDateString(): string {
  return new Date().toISOString().split('T')[0]
}

export default function DashboardPage() {
  const router = useRouter()
  const [isSigningOut, setIsSigningOut] = useState(false)
  const today = getTodayDateString()

  // Fetch today's planned actions
  const plannedQuery = useQuery({
    queryKey: queryKeys.actions.today(today),
    queryFn: () => api.actions.list({ planned_date: today, status: ['planned', 'active'] }),
  })

  // Fetch today's completed actions
  const completedQuery = useQuery({
    queryKey: ['actions', 'completed', today],
    queryFn: () => api.actions.list({ planned_date: today, status: 'done' }),
  })

  // Calculate stats
  const stats = useMemo(() => {
    const planned = plannedQuery.data?.actions?.length || 0
    const completed = completedQuery.data?.actions?.length || 0
    const totalMinutes = completedQuery.data?.actions?.reduce(
      (sum, action) => sum + (action.actual_minutes || action.estimated_minutes || 0),
      0
    ) || 0

    return { planned, completed, totalMinutes }
  }, [plannedQuery.data, completedQuery.data])

  async function handleSignOut() {
    setIsSigningOut(true)
    await signOut()
    router.push('/')
    router.refresh()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">Nuance</h1>
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard/settings"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Settings
            </Link>
            <button
              onClick={handleSignOut}
              disabled={isSigningOut}
              className="text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50"
            >
              {isSigningOut ? 'Signing out...' : 'Sign out'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            What would you like to do?
          </h2>
          <p className="text-gray-600">
            Choose a phase of your workflow to get started.
          </p>
        </div>

        {/* Workflow Phase Cards */}
        <div className="grid gap-4 sm:grid-cols-2">
          {phases.map((phase) => (
            <Link
              key={phase.id}
              href={`/dashboard/${phase.id}`}
              className="block p-6 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all group"
            >
              <div className="flex items-start gap-4">
                <span className="text-3xl" role="img" aria-hidden="true">
                  {phase.icon}
                </span>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                    {phase.label}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {phase.description}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="mt-8 p-6 bg-white rounded-xl border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Today</h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.planned}</div>
              <div className="text-sm text-gray-500">Tasks planned</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.completed}</div>
              <div className="text-sm text-gray-500">Completed</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{stats.totalMinutes}m</div>
              <div className="text-sm text-gray-500">Time worked</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
