'use client'

/**
 * PLN-001: Inbox View
 *
 * Displays AI-curated candidate actions for today's planning.
 * - Shows up to 12 suggested actions
 * - Each action shows avoidance weight, estimate, and AI reasoning
 * - Supports selecting actions to add to today's plan
 */

import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { AvoidanceIndicator } from '@/components/ui/AvoidanceIndicator'
import { EmptyInbox } from '@/components/ui/EmptyState'
import { ActionCardSkeleton } from '@/components/actions/ActionCard'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export interface Suggestion {
  action: Action
  reasoning: string
  priorityScore: number
}

export interface InboxViewProps {
  /** Array of AI-generated suggestions */
  suggestions: Suggestion[]
  /** IDs of currently selected actions */
  selectedIds: string[]
  /** Handler for selecting an action */
  onSelect: (actionId: string) => void
  /** Handler for deselecting an action */
  onDeselect: (actionId: string) => void
  /** Whether data is loading */
  isLoading?: boolean
  /** Maximum number of suggestions to show */
  maxItems?: number
  /** Additional class names */
  className?: string
}

// ============================================================================
// Component
// ============================================================================

export function InboxView({
  suggestions,
  selectedIds,
  onSelect,
  onDeselect,
  isLoading,
  maxItems = 12,
  className,
}: InboxViewProps) {
  if (isLoading) {
    return (
      <div className={cn('space-y-3', className)}>
        {Array.from({ length: 5 }).map((_, i) => (
          <ActionCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (suggestions.length === 0) {
    return <EmptyInbox />
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h2 className="font-medium text-lg">
          Today&apos;s Candidates
          <span className="text-muted-foreground text-sm ml-2">
            ({suggestions.length})
          </span>
        </h2>
      </div>

      <div className="space-y-3">
        {suggestions.slice(0, maxItems).map(({ action, reasoning }) => {
          const isSelected = selectedIds.includes(action.id)

          return (
            <InboxCard
              key={action.id}
              action={action}
              reasoning={reasoning}
              isSelected={isSelected}
              onToggle={() =>
                isSelected ? onDeselect(action.id) : onSelect(action.id)
              }
            />
          )
        })}
      </div>
    </div>
  )
}

// ============================================================================
// InboxCard Component
// ============================================================================

interface InboxCardProps {
  action: Action
  reasoning: string
  isSelected: boolean
  onToggle: () => void
}

function InboxCard({ action, reasoning, isSelected, onToggle }: InboxCardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border p-4 cursor-pointer transition-all',
        'hover:border-primary/30 hover:shadow-sm',
        isSelected && 'ring-2 ring-primary bg-primary/5'
      )}
      onClick={onToggle}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onToggle()
        }
      }}
      role="checkbox"
      aria-checked={isSelected}
      tabIndex={0}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-medium truncate">{action.title}</h3>
          <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
            <AvoidanceIndicator weight={action.avoidance_weight} size="sm" />
            {action.estimated_minutes && (
              <span>~{formatDuration(action.estimated_minutes)}</span>
            )}
          </div>
        </div>

        {/* Selection indicator */}
        <div
          className={cn(
            'w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0',
            isSelected
              ? 'bg-primary border-primary'
              : 'border-muted-foreground/30'
          )}
        >
          {isSelected && <Check className="w-4 h-4 text-primary-foreground" />}
        </div>
      </div>

      {/* AI reasoning */}
      <p className="text-sm text-muted-foreground mt-2 italic line-clamp-2">
        &quot;{reasoning}&quot;
      </p>
    </div>
  )
}

// ============================================================================
// Helpers
// ============================================================================

function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}min`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (mins === 0) {
    return `${hours}h`
  }
  return `${hours}h ${mins}m`
}
