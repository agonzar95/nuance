'use client'

/**
 * REF-006: Tomorrow Quick Capture
 *
 * Quick capture interface at end of reflection for tomorrow's tasks:
 * - Simple text input for quick thoughts
 * - Items go directly to inbox
 * - Shows list of captured items
 * - Frictionless and quick
 */

import { useState, useRef, useEffect } from 'react'
import { Plus, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Spinner } from '@/components/ui/Loading'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

interface CapturedItem {
  id: string
  text: string
}

export interface TomorrowQuickCaptureProps {
  /** Handler to capture a thought - returns the created action */
  onCapture: (text: string) => Promise<Action>
  /** Handler when user is done capturing */
  onDone: () => void
  /** Additional class names */
  className?: string
}

// ============================================================================
// Component
// ============================================================================

export function TomorrowQuickCapture({
  onCapture,
  onDone,
  className,
}: TomorrowQuickCaptureProps) {
  const [input, setInput] = useState('')
  const [captured, setCaptured] = useState<CapturedItem[]>([])
  const [isCapturing, setIsCapturing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || isCapturing) return

    setInput('')
    setError(null)
    setIsCapturing(true)

    try {
      const action = await onCapture(text)
      setCaptured((prev) => [...prev, { id: action.id, text }])
      inputRef.current?.focus()
    } catch (err) {
      setError('Failed to capture. Please try again.')
      setInput(text) // Restore input on error
      console.error('Capture error:', err)
    } finally {
      setIsCapturing(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Allow Escape to skip/finish
    if (e.key === 'Escape') {
      onDone()
    }
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-xl font-medium">Anything for tomorrow?</h2>
        <p className="text-muted-foreground">
          Capture thoughts so you can let go of today
        </p>
      </div>

      {/* Capture form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g., Follow up with Alex..."
          className={cn(
            'flex-1 px-4 py-3 rounded-lg border bg-background',
            'focus:outline-none focus:ring-2 focus:ring-primary',
            'placeholder:text-muted-foreground'
          )}
          disabled={isCapturing}
          aria-label="Task to capture for tomorrow"
        />
        <button
          type="submit"
          disabled={!input.trim() || isCapturing}
          className={cn(
            'px-4 py-3 rounded-lg',
            'bg-primary text-primary-foreground',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'transition-colors hover:bg-primary/90'
          )}
          aria-label="Add task"
        >
          {isCapturing ? (
            <Spinner size="sm" />
          ) : (
            <Plus className="w-5 h-5" />
          )}
        </button>
      </form>

      {/* Error message */}
      {error && (
        <p className="text-sm text-destructive text-center">{error}</p>
      )}

      {/* Captured items list */}
      {captured.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">Added for tomorrow:</p>
          <div className="space-y-2">
            {captured.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-2 text-sm p-2 rounded bg-muted/50"
              >
                <Check className="w-4 h-4 text-green-500 shrink-0" />
                <span className="truncate">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Done button */}
      <button
        onClick={onDone}
        className={cn(
          'w-full py-4 rounded-lg font-medium transition-colors',
          'bg-primary text-primary-foreground',
          'hover:bg-primary/90'
        )}
      >
        {captured.length > 0 ? 'Finish' : 'Skip for now'}
      </button>

      {/* Keyboard hint */}
      <p className="text-xs text-center text-muted-foreground">
        Press <kbd className="px-1 py-0.5 rounded bg-muted text-xs">Esc</kbd> to
        skip
      </p>
    </div>
  )
}
