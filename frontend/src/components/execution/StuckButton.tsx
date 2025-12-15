'use client'

/**
 * EXE-007: Stuck Button
 *
 * Prominent but non-judgmental button for signaling when stuck.
 * Triggers the stuck flow without shame.
 */

import { cn } from '@/lib/utils'

// ============================================================================
// Types
// ============================================================================

export interface StuckButtonProps {
  /** Handler when button is clicked */
  onClick: () => void
  /** Visual variant */
  variant?: 'default' | 'subtle'
  /** Additional class names */
  className?: string
  /** Disabled state */
  disabled?: boolean
}

// ============================================================================
// Component
// ============================================================================

export function StuckButton({
  onClick,
  variant = 'default',
  className,
  disabled,
}: StuckButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'flex items-center gap-2 rounded-lg transition-colors',
        variant === 'default' &&
          'px-6 py-3 border hover:bg-muted disabled:opacity-50',
        variant === 'subtle' &&
          'px-4 py-2 text-sm text-muted-foreground hover:text-foreground',
        className
      )}
    >
      <HelpCircleIcon className="w-5 h-5" />
      <span>I&apos;m stuck</span>
    </button>
  )
}

// ============================================================================
// Icons
// ============================================================================

function HelpCircleIcon({ className }: { className?: string }) {
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
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
      <path d="M12 17h.01" />
    </svg>
  )
}
