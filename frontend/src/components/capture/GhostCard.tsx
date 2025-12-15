'use client'

/**
 * CAP-004: Ghost Card
 *
 * Visual feedback during extraction process:
 * - Shows shimmer animation while AI processes input
 * - Transforms into real ActionCard when extraction completes
 * - Error state for failed extractions
 */

import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'
import { ActionCard } from '@/components/actions/ActionCard'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export type GhostCardStatus = 'extracting' | 'extracted' | 'error'

export interface GhostCardProps {
  /** Raw text being processed */
  rawText: string
  /** Current status of extraction */
  status: GhostCardStatus
  /** Extracted action (when status is 'extracted') */
  extractedAction?: Partial<Action>
  /** Called when user confirms the extraction */
  onConfirm?: (action: Partial<Action>) => void
  /** Called when user wants to edit */
  onEdit?: (action: Partial<Action>) => void
  /** Called when user dismisses error */
  onDismiss?: () => void
  /** Error message (when status is 'error') */
  errorMessage?: string
  /** Additional class names */
  className?: string
}

// ============================================================================
// Component
// ============================================================================

export function GhostCard({
  rawText,
  status,
  extractedAction,
  onConfirm,
  onEdit,
  onDismiss,
  errorMessage,
  className,
}: GhostCardProps) {
  const [isAnimatingOut, setIsAnimatingOut] = useState(false)

  // Handle status transition animation
  useEffect(() => {
    if (status === 'extracted' && extractedAction) {
      // Small delay for smooth transition
      const timer = setTimeout(() => setIsAnimatingOut(false), 50)
      return () => clearTimeout(timer)
    }
  }, [status, extractedAction])

  // Extracted state - show real card with confirm/edit options
  if (status === 'extracted' && extractedAction) {
    const mockAction: Action = {
      id: 'ghost-preview',
      user_id: '',
      title: extractedAction.title || rawText,
      status: 'inbox',
      complexity: extractedAction.complexity || 'atomic',
      avoidance_weight: extractedAction.avoidance_weight || 1,
      estimated_minutes: extractedAction.estimated_minutes || 15,
      position: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    return (
      <div
        className={cn(
          'transition-all duration-200 ease-out',
          isAnimatingOut ? 'opacity-0 scale-95' : 'opacity-100 scale-100',
          className
        )}
      >
        <ActionCard action={mockAction} />
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => onConfirm?.(extractedAction)}
            className={cn(
              'flex-1 px-4 py-2 rounded-md text-sm font-medium',
              'bg-primary text-primary-foreground',
              'hover:bg-primary/90 transition-colors'
            )}
          >
            Looks good
          </button>
          <button
            onClick={() => onEdit?.(extractedAction)}
            className={cn(
              'px-4 py-2 rounded-md text-sm font-medium',
              'text-muted-foreground hover:bg-muted transition-colors'
            )}
          >
            Edit
          </button>
        </div>
      </div>
    )
  }

  // Error state
  if (status === 'error') {
    return (
      <div
        className={cn(
          'rounded-lg border border-destructive/30 bg-destructive/5 p-4',
          className
        )}
      >
        <div className="flex items-start gap-3">
          <AlertCircleIcon className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-destructive">
              {errorMessage || 'Failed to process'}
            </p>
            <p className="text-sm text-muted-foreground mt-1 break-words">
              &ldquo;{truncateText(rawText, 100)}&rdquo;
            </p>
          </div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="mt-3 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Dismiss
          </button>
        )}
      </div>
    )
  }

  // Extracting state - shimmer animation
  return (
    <div
      className={cn(
        'rounded-lg border bg-card p-4 relative overflow-hidden',
        className
      )}
    >
      {/* Shimmer overlay */}
      <div className="absolute inset-0 ghost-shimmer" />

      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
          <SpinnerIcon className="w-4 h-4 animate-spin" />
          <span>Processing...</span>
        </div>
        <p className="text-sm text-muted-foreground/80 break-words">
          &ldquo;{truncateText(rawText, 80)}&rdquo;
        </p>
      </div>

      {/* Inline shimmer styles */}
      <style jsx>{`
        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }

        .ghost-shimmer {
          background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 100%
          );
          animation: shimmer 1.5s infinite;
        }

        :global(.dark) .ghost-shimmer {
          background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.05) 50%,
            transparent 100%
          );
        }
      `}</style>
    </div>
  )
}

// ============================================================================
// Multiple Ghost Cards Container
// ============================================================================

export interface PendingExtraction {
  id: string
  rawText: string
  status: GhostCardStatus
  extractedAction?: Partial<Action>
  errorMessage?: string
}

export interface GhostCardListProps {
  extractions: PendingExtraction[]
  onConfirm?: (id: string, action: Partial<Action>) => void
  onEdit?: (id: string, action: Partial<Action>) => void
  onDismiss?: (id: string) => void
}

export function GhostCardList({
  extractions,
  onConfirm,
  onEdit,
  onDismiss,
}: GhostCardListProps) {
  if (extractions.length === 0) return null

  return (
    <div className="space-y-3">
      {extractions.map((extraction) => (
        <GhostCard
          key={extraction.id}
          rawText={extraction.rawText}
          status={extraction.status}
          extractedAction={extraction.extractedAction}
          errorMessage={extraction.errorMessage}
          onConfirm={(action) => onConfirm?.(extraction.id, action)}
          onEdit={(action) => onEdit?.(extraction.id, action)}
          onDismiss={() => onDismiss?.(extraction.id)}
        />
      ))}
    </div>
  )
}

// ============================================================================
// Helpers
// ============================================================================

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return `${text.slice(0, maxLength)}...`
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

function SpinnerIcon({ className }: { className?: string }) {
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
      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    </svg>
  )
}
