'use client'

/**
 * FE-006: Action Card Component
 *
 * Displays a single action with key information:
 * - Title (prominent)
 * - Avoidance weight indicator (1-5 dots)
 * - Time estimate
 * - Status-based styling
 */

import { forwardRef } from 'react'
import { cn } from '@/lib/utils'
import { AvoidanceIndicator } from '@/components/ui/AvoidanceIndicator'
import type { Action, ActionStatus } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export interface ActionCardProps {
  /** The action to display */
  action: Action
  /** Click handler */
  onClick?: () => void
  /** Whether to show avoidance indicator */
  showAvoidance?: boolean
  /** Whether to show time estimate */
  showEstimate?: boolean
  /** Card variant */
  variant?: 'default' | 'compact' | 'focus'
  /** Whether the card is draggable */
  draggable?: boolean
  /** Whether the card is currently selected */
  selected?: boolean
  /** Additional class names */
  className?: string
}

// ============================================================================
// Status Styling
// ============================================================================

const statusStyles: Record<ActionStatus, string> = {
  inbox: 'border-l-4 border-l-muted-foreground/30',
  candidate: 'border-l-4 border-l-amber-400',
  planned: 'border-l-4 border-l-blue-500',
  active: 'border-l-4 border-l-green-500 bg-green-50/50 dark:bg-green-950/20',
  done: 'border-l-4 border-l-green-600 opacity-60',
  dropped: 'border-l-4 border-l-red-400 opacity-50',
  rolled: 'border-l-4 border-l-orange-400',
}

const statusLabels: Record<ActionStatus, string> = {
  inbox: 'Inbox',
  candidate: 'Suggested',
  planned: 'Planned',
  active: 'In Progress',
  done: 'Done',
  dropped: 'Dropped',
  rolled: 'Rolled',
}

// ============================================================================
// Component
// ============================================================================

export const ActionCard = forwardRef<HTMLDivElement, ActionCardProps>(
  function ActionCard(
    {
      action,
      onClick,
      showAvoidance = true,
      showEstimate = true,
      variant = 'default',
      draggable = false,
      selected = false,
      className,
    },
    ref
  ) {
    const isDone = action.status === 'done'
    const isDropped = action.status === 'dropped'

    return (
      <div
        ref={ref}
        className={cn(
          // Base styles
          'rounded-lg border bg-card shadow-sm',
          'transition-all duration-150 ease-out',
          // Variant styles
          variant === 'default' && 'p-4',
          variant === 'compact' && 'p-3',
          variant === 'focus' && 'p-6 text-center',
          // Status styles
          statusStyles[action.status],
          // Interactive styles
          onClick && 'cursor-pointer hover:shadow-md hover:border-primary/20',
          draggable && 'cursor-grab active:cursor-grabbing',
          // Selected state
          selected && 'ring-2 ring-primary ring-offset-2',
          // Custom classes
          className
        )}
        onClick={onClick}
        onKeyDown={(e) => {
          if ((e.key === 'Enter' || e.key === ' ') && onClick) {
            e.preventDefault()
            onClick()
          }
        }}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
        draggable={draggable}
        aria-selected={selected}
        data-action-id={action.id}
      >
        {/* Title */}
        <h3
          className={cn(
            'font-medium text-foreground',
            variant === 'focus' && 'text-xl',
            variant === 'compact' && 'text-sm',
            isDone && 'line-through text-muted-foreground',
            isDropped && 'line-through text-muted-foreground'
          )}
        >
          {action.title}
        </h3>

        {/* Metadata row */}
        <div
          className={cn(
            'flex items-center gap-3 mt-2',
            variant === 'focus' && 'justify-center mt-4',
            variant === 'compact' && 'mt-1.5 gap-2'
          )}
        >
          {/* Avoidance indicator */}
          {showAvoidance && (
            <AvoidanceIndicator
              weight={action.avoidance_weight}
              size={variant === 'compact' ? 'sm' : 'md'}
            />
          )}

          {/* Time estimate */}
          {showEstimate && action.estimated_minutes && (
            <span
              className={cn(
                'text-muted-foreground',
                variant === 'compact' ? 'text-xs' : 'text-sm'
              )}
            >
              ~{formatDuration(action.estimated_minutes)}
            </span>
          )}

          {/* Complexity badge for composite/project */}
          {action.complexity !== 'atomic' && (
            <span
              className={cn(
                'px-1.5 py-0.5 rounded text-xs font-medium',
                action.complexity === 'composite' &&
                  'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
                action.complexity === 'project' &&
                  'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
              )}
            >
              {action.complexity === 'composite' ? 'Multi-step' : 'Project'}
            </span>
          )}
        </div>

        {/* Status label (only in focus variant or when active) */}
        {(variant === 'focus' || action.status === 'active') && (
          <div
            className={cn(
              'mt-3 text-xs font-medium uppercase tracking-wide',
              action.status === 'active' && 'text-green-600 dark:text-green-400',
              action.status !== 'active' && 'text-muted-foreground'
            )}
          >
            {statusLabels[action.status]}
          </div>
        )}
      </div>
    )
  }
)

// ============================================================================
// Helpers
// ============================================================================

/**
 * Format minutes into a human-readable duration
 */
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

// ============================================================================
// Skeleton
// ============================================================================

export function ActionCardSkeleton({
  variant = 'default',
}: {
  variant?: 'default' | 'compact' | 'focus'
}) {
  return (
    <div
      className={cn(
        'rounded-lg border bg-card animate-pulse',
        variant === 'default' && 'p-4',
        variant === 'compact' && 'p-3',
        variant === 'focus' && 'p-6'
      )}
    >
      <div
        className={cn(
          'h-5 bg-muted rounded w-3/4',
          variant === 'focus' && 'mx-auto',
          variant === 'compact' && 'h-4'
        )}
      />
      <div
        className={cn(
          'flex items-center gap-3 mt-2',
          variant === 'focus' && 'justify-center mt-4'
        )}
      >
        <div className="flex gap-0.5">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="w-2 h-2 bg-muted rounded-full" />
          ))}
        </div>
        <div className="h-4 bg-muted rounded w-12" />
      </div>
    </div>
  )
}
