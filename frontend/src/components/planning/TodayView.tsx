'use client'

/**
 * PLN-002: Today View
 *
 * Displays today's committed plan with:
 * - Ordered list of actions for the day
 * - Cumulative time estimate
 * - Drag handles for reordering (PLN-004)
 * - Remove buttons
 * - "Start Day" button to begin focus mode (PLN-005)
 */

import { GripVertical, X } from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'
import { AvoidanceIndicator } from '@/components/ui/AvoidanceIndicator'
import { EmptyToday } from '@/components/ui/EmptyState'
import { Spinner } from '@/components/ui/Loading'
import type { Action } from '@/types/api'
import type { DraggableProvidedDragHandleProps } from '@hello-pangea/dnd'

// ============================================================================
// Types
// ============================================================================

export interface TodayViewProps {
  /** Today's planned actions in order */
  actions: Action[]
  /** Total planned minutes */
  totalMinutes: number
  /** Handler for reordering actions - receives new order of action IDs */
  onReorder: (actionIds: string[]) => void
  /** Handler for starting the day */
  onStartDay: () => void
  /** Handler for removing an action from today */
  onRemove: (actionId: string) => void
  /** Whether the user can start the day (has at least one action) */
  canStart: boolean
  /** Whether the start action is in progress */
  isStarting?: boolean
  /** Additional class names */
  className?: string
}

// ============================================================================
// Component
// ============================================================================

export function TodayView({
  actions,
  totalMinutes,
  onReorder,
  onStartDay,
  onRemove,
  canStart,
  isStarting,
  className,
}: TodayViewProps) {
  if (actions.length === 0) {
    return <EmptyToday />
  }

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Header with date and time */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-medium text-lg">
          Today — {format(new Date(), 'EEEE, MMMM d')}
        </h2>
        <span className="text-muted-foreground">
          {formatTime(totalMinutes)} planned
        </span>
      </div>

      {/* Action list - Note: Actual DnD wrapping happens in parent component */}
      <div className="flex-1 space-y-2 overflow-y-auto">
        {actions.map((action, index) => (
          <TodayActionCard
            key={action.id}
            action={action}
            position={index + 1}
            onRemove={() => onRemove(action.id)}
          />
        ))}
      </div>

      {/* Start Day button */}
      <div className="mt-4 pt-4 border-t">
        <button
          onClick={onStartDay}
          disabled={!canStart || isStarting}
          className={cn(
            'w-full py-3 rounded-lg font-medium transition-colors',
            'bg-primary text-primary-foreground',
            'hover:bg-primary/90',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          {isStarting ? (
            <span className="flex items-center justify-center gap-2">
              <Spinner size="sm" />
              Starting...
            </span>
          ) : (
            'Start Day'
          )}
        </button>
      </div>
    </div>
  )
}

// ============================================================================
// TodayActionCard Component
// ============================================================================

export interface TodayActionCardProps {
  action: Action
  /** Position in the list (1-indexed) */
  position?: number
  /** Drag handle props from react-beautiful-dnd / @hello-pangea/dnd */
  dragHandleProps?: DraggableProvidedDragHandleProps | null
  /** Whether the card is currently being dragged */
  isDragging?: boolean
  /** Handler to remove this action from today */
  onRemove: () => void
}

export function TodayActionCard({
  action,
  position,
  dragHandleProps,
  isDragging,
  onRemove,
}: TodayActionCardProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-3 rounded-lg border bg-card p-3',
        'transition-shadow',
        isDragging && 'shadow-lg ring-2 ring-primary'
      )}
    >
      {/* Drag Handle */}
      <div
        {...dragHandleProps}
        className={cn(
          'p-1 text-muted-foreground',
          dragHandleProps && 'cursor-grab active:cursor-grabbing'
        )}
        aria-label="Drag to reorder"
      >
        <GripVertical className="w-5 h-5" />
      </div>

      {/* Position number */}
      {position && (
        <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center text-xs font-medium text-muted-foreground">
          {position}
        </div>
      )}

      {/* Action Content */}
      <div className="flex-1 min-w-0">
        <h4 className="font-medium truncate">{action.title}</h4>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <AvoidanceIndicator weight={action.avoidance_weight} size="sm" />
          {action.estimated_minutes && (
            <span>~{formatTime(action.estimated_minutes)}</span>
          )}
        </div>
      </div>

      {/* Remove Button */}
      <button
        onClick={(e) => {
          e.stopPropagation()
          onRemove()
        }}
        className="p-2 text-muted-foreground hover:text-destructive transition-colors rounded-md hover:bg-destructive/10"
        aria-label="Remove from today"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

// ============================================================================
// Helpers
// ============================================================================

function formatTime(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (mins === 0) {
    return `${hours}h`
  }
  return `${hours}h ${mins}m`
}
