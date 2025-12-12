'use client'

/**
 * REF-005: Roll/Drop Controls
 *
 * Provides controls for remaining (uncompleted) tasks at end of day:
 * - Roll button: Move task to tomorrow's inbox
 * - Drop button: Remove from active list (with confirmation)
 */

import { useState } from 'react'
import { ArrowRight, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { AvoidanceIndicator } from '@/components/ui/AvoidanceIndicator'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export interface RemainingTaskCardProps {
  /** The uncompleted action */
  action: Action
  /** Handler to roll task to tomorrow */
  onRoll: () => void
  /** Handler to drop/remove task */
  onDrop: () => void
  /** Whether roll action is in progress */
  isRolling?: boolean
  /** Whether drop action is in progress */
  isDropping?: boolean
  /** Additional class names */
  className?: string
}

// ============================================================================
// Component
// ============================================================================

export function RemainingTaskCard({
  action,
  onRoll,
  onDrop,
  isRolling,
  isDropping,
  className,
}: RemainingTaskCardProps) {
  const [showDropConfirm, setShowDropConfirm] = useState(false)

  const handleDropClick = () => {
    setShowDropConfirm(true)
  }

  const handleDropConfirm = () => {
    onDrop()
    setShowDropConfirm(false)
  }

  const handleDropCancel = () => {
    setShowDropConfirm(false)
  }

  return (
    <div className={cn('relative', className)}>
      <div
        className={cn(
          'flex items-center gap-3 p-3 rounded-lg border bg-card',
          'transition-all',
          showDropConfirm && 'opacity-50'
        )}
      >
        {/* Action content */}
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{action.title}</p>
          <div className="flex items-center gap-2 mt-1">
            <AvoidanceIndicator weight={action.avoidance_weight} size="sm" />
            {action.estimated_minutes && (
              <span className="text-xs text-muted-foreground">
                ~{action.estimated_minutes}min
              </span>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          {/* Roll button */}
          <button
            onClick={onRoll}
            disabled={isRolling || isDropping || showDropConfirm}
            className={cn(
              'px-3 py-1.5 text-sm rounded-md border',
              'hover:bg-muted transition-colors',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'flex items-center gap-1'
            )}
            title="Move to tomorrow"
            aria-label="Roll task to tomorrow"
          >
            <ArrowRight className="w-4 h-4" />
            <span className="hidden sm:inline">Tomorrow</span>
          </button>

          {/* Drop button */}
          <button
            onClick={handleDropClick}
            disabled={isRolling || isDropping || showDropConfirm}
            className={cn(
              'px-3 py-1.5 text-sm rounded-md',
              'text-destructive hover:bg-destructive/10 transition-colors',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
            title="Drop task"
            aria-label="Drop task"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Drop confirmation overlay */}
      {showDropConfirm && (
        <DropConfirmDialog
          actionTitle={action.title}
          onConfirm={handleDropConfirm}
          onCancel={handleDropCancel}
          isDropping={isDropping}
        />
      )}
    </div>
  )
}

// ============================================================================
// DropConfirmDialog Component
// ============================================================================

interface DropConfirmDialogProps {
  actionTitle: string
  onConfirm: () => void
  onCancel: () => void
  isDropping?: boolean
}

function DropConfirmDialog({
  actionTitle,
  onConfirm,
  onCancel,
  isDropping,
}: DropConfirmDialogProps) {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm rounded-lg z-10">
      <div className="bg-card border rounded-lg p-4 shadow-lg max-w-xs mx-4">
        <h4 className="font-medium">Drop this task?</h4>
        <p className="text-sm text-muted-foreground mt-1">
          &quot;{actionTitle}&quot; will be removed from your active list. You
          can still find it in history.
        </p>
        <div className="flex gap-2 mt-4 justify-end">
          <button
            onClick={onCancel}
            disabled={isDropping}
            className="px-3 py-1.5 text-sm rounded-md border hover:bg-muted transition-colors"
          >
            Keep it
          </button>
          <button
            onClick={onConfirm}
            disabled={isDropping}
            className={cn(
              'px-3 py-1.5 text-sm rounded-md',
              'bg-destructive text-destructive-foreground',
              'hover:bg-destructive/90 transition-colors',
              'disabled:opacity-50'
            )}
          >
            {isDropping ? 'Dropping...' : 'Drop it'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// Batch Controls Component (for multiple remaining tasks)
// ============================================================================

export interface BatchRollDropControlsProps {
  /** Number of remaining tasks */
  remainingCount: number
  /** Handler to roll all tasks */
  onRollAll: () => void
  /** Handler to drop all tasks */
  onDropAll: () => void
  /** Whether batch operation is in progress */
  isProcessing?: boolean
}

export function BatchRollDropControls({
  remainingCount,
  onRollAll,
  onDropAll,
  isProcessing,
}: BatchRollDropControlsProps) {
  const [showDropAllConfirm, setShowDropAllConfirm] = useState(false)

  if (remainingCount === 0) return null

  return (
    <div className="flex items-center justify-between p-3 border rounded-lg bg-muted/50">
      <span className="text-sm text-muted-foreground">
        {remainingCount} task{remainingCount !== 1 ? 's' : ''} remaining
      </span>

      <div className="flex items-center gap-2">
        <button
          onClick={onRollAll}
          disabled={isProcessing}
          className={cn(
            'px-3 py-1.5 text-sm rounded-md border',
            'hover:bg-background transition-colors',
            'disabled:opacity-50'
          )}
        >
          Roll all to tomorrow
        </button>

        {showDropAllConfirm ? (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowDropAllConfirm(false)}
              disabled={isProcessing}
              className="px-2 py-1 text-xs rounded border"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                onDropAll()
                setShowDropAllConfirm(false)
              }}
              disabled={isProcessing}
              className="px-2 py-1 text-xs rounded bg-destructive text-destructive-foreground"
            >
              Confirm drop all
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowDropAllConfirm(true)}
            disabled={isProcessing}
            className={cn(
              'px-3 py-1.5 text-sm rounded-md',
              'text-destructive hover:bg-destructive/10 transition-colors',
              'disabled:opacity-50'
            )}
          >
            Drop all
          </button>
        )}
      </div>
    </div>
  )
}
