'use client'

/**
 * EXE-010: Complete Task Flow
 *
 * Handles task completion with optional reflection.
 * Shows success message, duration, and optional notes capture.
 */

import { useState } from 'react'
import { Check } from 'lucide-react'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export interface CompleteTaskFlowProps {
  action: Action
  elapsedSeconds: number
  onComplete: (reflection?: string) => Promise<void>
  onSkipReflection: () => void
}

// ============================================================================
// Helper Functions
// ============================================================================

function formatDuration(seconds: number): string {
  const minutes = Math.round(seconds / 60)
  if (minutes < 60) {
    return `${minutes} minute${minutes !== 1 ? 's' : ''}`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (mins === 0) {
    return `${hours} hour${hours !== 1 ? 's' : ''}`
  }
  return `${hours}h ${mins}m`
}

// ============================================================================
// Component
// ============================================================================

export function CompleteTaskFlow({
  action,
  elapsedSeconds,
  onComplete,
  onSkipReflection
}: CompleteTaskFlowProps) {
  const [showReflection, setShowReflection] = useState(true)
  const [reflection, setReflection] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleComplete = async () => {
    setIsSubmitting(true)
    try {
      await onComplete(reflection || undefined)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSkip = () => {
    setShowReflection(false)
    onSkipReflection()
  }

  return (
    <div className="w-full max-w-md space-y-6 text-center">
      {/* Success Header */}
      <div className="space-y-3">
        <div className="w-16 h-16 mx-auto rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
          <Check className="w-8 h-8 text-green-600 dark:text-green-400" />
        </div>
        <h2 className="text-xl font-medium">Nice work!</h2>
        <p className="text-muted-foreground">
          Completed in {formatDuration(elapsedSeconds)}
        </p>
      </div>

      {/* Task Title */}
      <div className="px-4 py-3 bg-muted/50 rounded-lg">
        <p className="font-medium text-sm">{action.title}</p>
      </div>

      {/* Optional Reflection */}
      {showReflection && (
        <div className="space-y-3">
          <label className="text-sm text-muted-foreground block">
            Any thoughts on how it went? (optional)
          </label>
          <textarea
            value={reflection}
            onChange={(e) => setReflection(e.target.value)}
            placeholder="It was easier than I expected..."
            className="w-full px-4 py-3 rounded-lg border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
            rows={3}
            disabled={isSubmitting}
          />
        </div>
      )}

      {/* Actions */}
      <div className="space-y-2">
        <button
          onClick={handleComplete}
          disabled={isSubmitting}
          className="w-full py-3 rounded-lg bg-primary text-primary-foreground font-medium disabled:opacity-50 transition-opacity"
        >
          {isSubmitting ? 'Saving...' : 'Continue'}
        </button>
        {showReflection && (
          <button
            onClick={handleSkip}
            disabled={isSubmitting}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Skip reflection
          </button>
        )}
      </div>
    </div>
  )
}
