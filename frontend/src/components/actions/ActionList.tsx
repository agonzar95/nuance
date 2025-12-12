'use client'

/**
 * FE-005: Action List Component
 *
 * Displays a list of actions using ActionCard components.
 * Supports:
 * - Different variants (default, compact, planning)
 * - Click handling
 * - Empty states
 * - Loading states
 */

import { cn } from '@/lib/utils'
import { ActionCard, ActionCardSkeleton } from './ActionCard'
import { EmptyState } from '@/components/ui/EmptyState'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export interface ActionListProps {
  /** List of actions to display */
  actions: Action[]
  /** Click handler for individual actions */
  onActionClick?: (action: Action) => void
  /** Message to show when list is empty */
  emptyMessage?: string
  /** Title for empty state */
  emptyTitle?: string
  /** Whether to show avoidance indicators */
  showAvoidance?: boolean
  /** Whether to show time estimates */
  showEstimate?: boolean
  /** List variant */
  variant?: 'default' | 'compact' | 'planning'
  /** Currently selected action ID */
  selectedId?: string
  /** Whether cards are draggable */
  draggable?: boolean
  /** Loading state */
  isLoading?: boolean
  /** Number of skeleton items to show when loading */
  skeletonCount?: number
  /** Additional class names */
  className?: string
}

// ============================================================================
// Component
// ============================================================================

export function ActionList({
  actions,
  onActionClick,
  emptyMessage = 'No actions',
  emptyTitle,
  showAvoidance = true,
  showEstimate = true,
  variant = 'default',
  selectedId,
  draggable = false,
  isLoading = false,
  skeletonCount = 3,
  className,
}: ActionListProps) {
  // Loading state
  if (isLoading) {
    return (
      <ul
        className={cn('space-y-2', className)}
        role="list"
        aria-busy="true"
        aria-label="Loading actions"
      >
        {Array.from({ length: skeletonCount }).map((_, i) => (
          <li key={i}>
            <ActionCardSkeleton variant={variant === 'compact' ? 'compact' : 'default'} />
          </li>
        ))}
      </ul>
    )
  }

  // Empty state
  if (actions.length === 0) {
    return (
      <EmptyState
        title={emptyTitle}
        message={emptyMessage}
      />
    )
  }

  // Card variant based on list variant
  const cardVariant = variant === 'compact' ? 'compact' : 'default'

  return (
    <ul
      className={cn(
        variant === 'compact' ? 'space-y-1.5' : 'space-y-2',
        className
      )}
      role="list"
    >
      {actions.map((action) => (
        <li key={action.id}>
          <ActionCard
            action={action}
            onClick={onActionClick ? () => onActionClick(action) : undefined}
            showAvoidance={showAvoidance}
            showEstimate={showEstimate}
            variant={cardVariant}
            draggable={draggable}
            selected={selectedId === action.id}
          />
        </li>
      ))}
    </ul>
  )
}

// ============================================================================
// Pre-configured Variants
// ============================================================================

/**
 * Inbox-specific action list with appropriate empty state
 */
export function InboxActionList({
  actions,
  onActionClick,
  isLoading,
  ...props
}: Omit<ActionListProps, 'emptyMessage' | 'emptyTitle'>) {
  return (
    <ActionList
      actions={actions}
      onActionClick={onActionClick}
      emptyTitle="Inbox is clear"
      emptyMessage="Nothing waiting for your attention. Enjoy the calm."
      isLoading={isLoading}
      {...props}
    />
  )
}

/**
 * Today view action list with appropriate empty state
 */
export function TodayActionList({
  actions,
  onActionClick,
  isLoading,
  ...props
}: Omit<ActionListProps, 'emptyMessage' | 'emptyTitle'>) {
  return (
    <ActionList
      actions={actions}
      onActionClick={onActionClick}
      emptyTitle="No plan yet"
      emptyMessage="Drag some tasks from inbox to start your day."
      isLoading={isLoading}
      {...props}
    />
  )
}

/**
 * Compact action list for sidebars or secondary views
 */
export function CompactActionList({
  actions,
  onActionClick,
  showAvoidance = false,
  ...props
}: Omit<ActionListProps, 'variant'>) {
  return (
    <ActionList
      actions={actions}
      onActionClick={onActionClick}
      showAvoidance={showAvoidance}
      variant="compact"
      {...props}
    />
  )
}

// ============================================================================
// Grouped Action List
// ============================================================================

interface GroupedActionListProps {
  /** Actions grouped by some key */
  groups: Array<{
    key: string
    title: string
    actions: Action[]
  }>
  /** Click handler for individual actions */
  onActionClick?: (action: Action) => void
  /** Whether to show avoidance indicators */
  showAvoidance?: boolean
  /** Whether to show time estimates */
  showEstimate?: boolean
  /** Additional class names */
  className?: string
}

/**
 * Display actions in groups with headers
 */
export function GroupedActionList({
  groups,
  onActionClick,
  showAvoidance = true,
  showEstimate = true,
  className,
}: GroupedActionListProps) {
  if (groups.length === 0 || groups.every((g) => g.actions.length === 0)) {
    return (
      <EmptyState
        title="No actions"
        message="Nothing to show here."
      />
    )
  }

  return (
    <div className={cn('space-y-6', className)}>
      {groups.map((group) => {
        if (group.actions.length === 0) return null

        return (
          <div key={group.key}>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">
              {group.title}
              <span className="ml-2 text-xs">({group.actions.length})</span>
            </h3>
            <ActionList
              actions={group.actions}
              onActionClick={onActionClick}
              showAvoidance={showAvoidance}
              showEstimate={showEstimate}
            />
          </div>
        )
      })}
    </div>
  )
}
