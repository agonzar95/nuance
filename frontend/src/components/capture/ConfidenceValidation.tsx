'use client'

/**
 * CAP-005: Confidence Validation
 *
 * Prompts user to confirm or correct AI extractions when
 * confidence is low (< 0.7). Shows what the AI understood
 * with options to confirm as-is or edit.
 */

import { cn } from '@/lib/utils'
import type { EnrichedAction } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export interface ExtractionForValidation {
  actions: EnrichedAction[]
  confidence: number
  ambiguities: string[]
}

export interface ConfidenceValidationProps {
  /** Extraction result to validate */
  extraction: ExtractionForValidation
  /** Called when user confirms the extraction as-is */
  onConfirm: (actions: EnrichedAction[]) => void
  /** Called when user wants to edit an action */
  onEdit: (action: EnrichedAction, index: number) => void
  /** Called when user dismisses/cancels */
  onDismiss?: () => void
  /** Additional class names */
  className?: string
}

// ============================================================================
// Component
// ============================================================================

export function ConfidenceValidation({
  extraction,
  onConfirm,
  onEdit,
  onDismiss,
  className,
}: ConfidenceValidationProps) {
  const { actions, confidence, ambiguities } = extraction
  const isLowConfidence = confidence < 0.7

  // Format confidence as percentage
  const confidencePercent = Math.round(confidence * 100)

  return (
    <div
      className={cn(
        'rounded-lg border p-4',
        isLowConfidence
          ? 'bg-amber-50/50 border-amber-200 dark:bg-amber-950/20 dark:border-amber-800'
          : 'bg-card border-border',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div className="flex-shrink-0 mt-0.5">
          {isLowConfidence ? (
            <AlertCircleIcon className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          ) : (
            <CheckCircleIcon className="w-5 h-5 text-green-600 dark:text-green-400" />
          )}
        </div>
        <div>
          <p className="font-medium text-foreground">
            {isLowConfidence ? 'Did I get this right?' : 'Here\'s what I understood'}
          </p>
          <p className="text-sm text-muted-foreground mt-0.5">
            {confidencePercent}% confident
          </p>
        </div>
      </div>

      {/* Extracted actions */}
      <div className="space-y-3 mb-4">
        {actions.map((action, index) => (
          <div
            key={index}
            className="bg-background rounded-lg p-3 border border-border/50"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="font-medium text-foreground">{action.title}</p>
                <div className="flex items-center gap-3 mt-1.5 text-sm text-muted-foreground">
                  {action.estimated_minutes && (
                    <span>~{action.estimated_minutes} min</span>
                  )}
                  {action.avoidance.weight > 1 && (
                    <span className="flex items-center gap-1">
                      <AvoidanceDots weight={action.avoidance.weight} />
                    </span>
                  )}
                  {action.complexity.complexity !== 'atomic' && (
                    <span
                      className={cn(
                        'px-1.5 py-0.5 rounded text-xs font-medium',
                        action.complexity.complexity === 'composite'
                          ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300'
                          : 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
                      )}
                    >
                      {action.complexity.complexity === 'composite'
                        ? 'Multi-step'
                        : 'Project'}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => onEdit(action, index)}
                className="text-sm text-primary hover:underline flex-shrink-0"
              >
                Edit
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Ambiguities */}
      {ambiguities.length > 0 && (
        <div className="mb-4 text-sm">
          <p className="text-muted-foreground mb-1.5">I wasn&apos;t sure about:</p>
          <ul className="list-disc list-inside space-y-0.5 text-muted-foreground/80">
            {ambiguities.map((ambiguity, i) => (
              <li key={i}>{ambiguity}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={() => onConfirm(actions)}
          className={cn(
            'flex-1 px-4 py-2 rounded-md text-sm font-medium',
            'bg-primary text-primary-foreground',
            'hover:bg-primary/90 transition-colors'
          )}
        >
          {actions.length === 1 ? "Yes, that's right" : `Confirm all ${actions.length}`}
        </button>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={cn(
              'px-4 py-2 rounded-md text-sm font-medium',
              'text-muted-foreground hover:bg-muted transition-colors'
            )}
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  )
}

// ============================================================================
// Single Action Validation (simplified)
// ============================================================================

export interface SingleActionValidationProps {
  /** Single action to validate */
  action: EnrichedAction
  /** Confidence score (0-1) */
  confidence: number
  /** Called when user confirms */
  onConfirm: () => void
  /** Called when user wants to edit */
  onEdit: () => void
  /** Additional class names */
  className?: string
}

export function SingleActionValidation({
  action,
  confidence,
  onConfirm,
  onEdit,
  className,
}: SingleActionValidationProps) {
  const isLowConfidence = confidence < 0.7
  const confidencePercent = Math.round(confidence * 100)

  return (
    <div
      className={cn(
        'rounded-lg border p-4',
        isLowConfidence
          ? 'bg-amber-50/50 border-amber-200 dark:bg-amber-950/20 dark:border-amber-800'
          : 'bg-card border-border',
        className
      )}
    >
      <div className="flex items-center gap-2 mb-3">
        {isLowConfidence ? (
          <AlertCircleIcon className="w-5 h-5 text-amber-600 dark:text-amber-400" />
        ) : (
          <CheckCircleIcon className="w-5 h-5 text-green-600 dark:text-green-400" />
        )}
        <p className="font-medium text-foreground">
          {isLowConfidence ? 'Did I get this right?' : 'Got it!'}
        </p>
        <span className="text-sm text-muted-foreground">
          ({confidencePercent}%)
        </span>
      </div>

      <div className="bg-background rounded-lg p-3 border border-border/50 mb-3">
        <p className="font-medium">{action.title}</p>
        {action.estimated_minutes && (
          <p className="text-sm text-muted-foreground mt-1">
            ~{action.estimated_minutes} min
          </p>
        )}
      </div>

      <div className="flex gap-2">
        <button
          onClick={onConfirm}
          className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90"
        >
          Yes, that&apos;s right
        </button>
        <button
          onClick={onEdit}
          className="px-4 py-2 text-muted-foreground text-sm font-medium hover:bg-muted rounded-md"
        >
          Let me fix it
        </button>
      </div>
    </div>
  )
}

// ============================================================================
// Helper Components
// ============================================================================

function AvoidanceDots({ weight }: { weight: number }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'w-1.5 h-1.5 rounded-full',
            i < weight
              ? weight >= 4
                ? 'bg-red-500'
                : weight >= 2
                  ? 'bg-amber-500'
                  : 'bg-muted-foreground'
              : 'bg-muted'
          )}
        />
      ))}
    </div>
  )
}

// ============================================================================
// Icons
// ============================================================================

function AlertCircleIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" x2="12" y1="8" y2="12" />
      <line x1="12" x2="12.01" y1="16" y2="16" />
    </svg>
  )
}

function CheckCircleIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  )
}
