'use client'

/**
 * EXE-008: Stuck Options
 *
 * Quick options for common blockers when user is stuck.
 * Routes to appropriate help (breakdown, coaching, etc.)
 */

import { Layers, HelpCircle, XCircle, MessageCircle } from 'lucide-react'
import type { StuckReason } from './CoachingOverlay'

// ============================================================================
// Types
// ============================================================================

interface StuckOption {
  id: StuckReason
  label: string
  description: string
  icon: React.ComponentType<{ className?: string }>
}

export interface StuckOptionsProps {
  onSelect: (reason: StuckReason) => void
  onCancel: () => void
}

// ============================================================================
// Constants
// ============================================================================

const STUCK_OPTIONS: StuckOption[] = [
  {
    id: 'too_big',
    label: 'Too big',
    description: "I don't know where to start",
    icon: Layers,
  },
  {
    id: 'dont_know',
    label: "Don't know how",
    description: 'I need guidance or information',
    icon: HelpCircle,
  },
  {
    id: 'dont_want',
    label: "Don't want to",
    description: "I'm avoiding this task",
    icon: XCircle,
  },
  {
    id: 'other',
    label: 'Something else',
    description: "Let's talk it through",
    icon: MessageCircle,
  },
]

// ============================================================================
// Component
// ============================================================================

export function StuckOptions({ onSelect, onCancel }: StuckOptionsProps) {
  return (
    <div className="w-full max-w-md space-y-4">
      {/* Header */}
      <div className="text-center">
        <h3 className="font-medium text-lg">What's blocking you?</h3>
        <p className="text-sm text-muted-foreground">
          It's okay - let's figure this out
        </p>
      </div>

      {/* Options Grid */}
      <div className="grid grid-cols-2 gap-3">
        {STUCK_OPTIONS.map((option) => (
          <button
            key={option.id}
            onClick={() => onSelect(option.id)}
            className="p-4 rounded-lg border hover:bg-muted text-left transition-colors group"
          >
            <option.icon className="w-5 h-5 mb-2 text-muted-foreground group-hover:text-foreground transition-colors" />
            <p className="font-medium">{option.label}</p>
            <p className="text-xs text-muted-foreground">{option.description}</p>
          </button>
        ))}
      </div>

      {/* Cancel Button */}
      <button
        onClick={onCancel}
        className="w-full py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        Never mind, I'll keep trying
      </button>
    </div>
  )
}
