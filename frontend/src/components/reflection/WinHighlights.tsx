'use client'

/**
 * REF-003: Win Highlights
 *
 * Celebrates high-avoidance task completions:
 * - Special section for tasks with avoidance >= 4 that were completed
 * - Enhanced visual treatment with gradient background
 * - Supportive messaging about overcoming resistance
 */

import { Trophy, Star } from 'lucide-react'
import { cn } from '@/lib/utils'
import { AvoidanceIndicator } from '@/components/ui/AvoidanceIndicator'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export interface WinHighlightsProps {
  /** High-avoidance actions that were completed */
  wins: Action[]
  /** Additional class names */
  className?: string
}

// ============================================================================
// Constants
// ============================================================================

/** Minimum avoidance weight to be considered a "win" */
const HIGH_AVOIDANCE_THRESHOLD = 4

// ============================================================================
// Component
// ============================================================================

export function WinHighlights({ wins, className }: WinHighlightsProps) {
  // Filter to only high-avoidance wins if not already filtered
  const highAvoidanceWins = wins.filter(
    (action) => action.avoidance_weight >= HIGH_AVOIDANCE_THRESHOLD
  )

  if (highAvoidanceWins.length === 0) {
    return null
  }

  const isSingle = highAvoidanceWins.length === 1

  return (
    <section
      className={cn(
        'relative overflow-hidden rounded-xl p-6',
        'bg-gradient-to-br from-amber-50 to-orange-100',
        'dark:from-amber-950/50 dark:to-orange-900/30',
        className
      )}
    >
      {/* Decorative star */}
      <div className="absolute top-2 right-2" aria-hidden="true">
        <Star className="w-6 h-6 text-amber-400 fill-amber-400/30" />
      </div>

      <div className="space-y-4">
        {/* Header */}
        <div>
          <h2 className="font-semibold text-lg flex items-center gap-2">
            <Trophy className="w-5 h-5 text-amber-500" />
            {isSingle ? "Today's Win" : "Today's Wins"}
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            You pushed through {isSingle ? 'something' : 'things'} you&apos;d
            been avoiding
          </p>
        </div>

        {/* Win cards */}
        <div className="space-y-2">
          {highAvoidanceWins.map((action) => (
            <WinCard key={action.id} action={action} />
          ))}
        </div>
      </div>
    </section>
  )
}

// ============================================================================
// WinCard Component
// ============================================================================

interface WinCardProps {
  action: Action
}

function WinCard({ action }: WinCardProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg',
        'bg-white/50 dark:bg-black/20'
      )}
    >
      <AvoidanceIndicator weight={action.avoidance_weight} />
      <span className="font-medium flex-1 truncate">{action.title}</span>
    </div>
  )
}

// ============================================================================
// Utility - Can be used externally to filter wins
// ============================================================================

/**
 * Filter actions to only high-avoidance completions
 */
export function filterHighAvoidanceWins(actions: Action[]): Action[] {
  return actions.filter(
    (action) =>
      action.status === 'done' &&
      action.avoidance_weight >= HIGH_AVOIDANCE_THRESHOLD
  )
}
