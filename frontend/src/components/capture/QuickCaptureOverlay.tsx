'use client'

/**
 * CAP-008: Quick Capture Overlay
 *
 * Minimal overlay for capturing quick thoughts during focus mode
 * without losing focus. Saves to inbox and dismisses quickly.
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { cn } from '@/lib/utils'

// ============================================================================
// Types
// ============================================================================

export interface QuickCaptureOverlayProps {
  /** Whether the overlay is open */
  isOpen: boolean
  /** Called when overlay should close */
  onClose: () => void
  /** Called when user submits a capture */
  onCapture: (text: string) => Promise<void>
  /** Position of the overlay */
  position?: 'top-right' | 'bottom-right' | 'center'
}

// ============================================================================
// Component
// ============================================================================

export function QuickCaptureOverlay({
  isOpen,
  onClose,
  onCapture,
  position = 'top-right',
}: QuickCaptureOverlayProps) {
  const [value, setValue] = useState('')
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved'>('idle')
  const inputRef = useRef<HTMLInputElement>(null)

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      // Small delay to ensure animation is complete
      const timer = setTimeout(() => {
        inputRef.current?.focus()
      }, 50)
      return () => clearTimeout(timer)
    }
  }, [isOpen])

  // Handle escape key
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  // Reset state when closed
  useEffect(() => {
    if (!isOpen) {
      setValue('')
      setStatus('idle')
    }
  }, [isOpen])

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      const trimmed = value.trim()
      if (!trimmed || status === 'saving') return

      setStatus('saving')
      try {
        await onCapture(trimmed)
        setStatus('saved')
        setValue('')

        // Auto-close after brief confirmation
        setTimeout(() => {
          setStatus('idle')
          onClose()
        }, 1000)
      } catch {
        setStatus('idle')
        // Keep value so user can retry
      }
    },
    [value, status, onCapture, onClose]
  )

  if (!isOpen) return null

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'bottom-right': 'bottom-20 right-4',
    center: 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 z-40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Overlay */}
      <div
        className={cn(
          'fixed z-50',
          positionClasses[position],
          'animate-in fade-in slide-in-from-top-2 duration-200'
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="quick-capture-title"
      >
        <div className="bg-background border rounded-lg shadow-lg p-4 w-80">
          {status === 'saved' ? (
            <SuccessMessage />
          ) : (
            <CaptureForm
              value={value}
              setValue={setValue}
              onSubmit={handleSubmit}
              onClose={onClose}
              isSaving={status === 'saving'}
              inputRef={inputRef}
            />
          )}
        </div>
      </div>
    </>
  )
}

// ============================================================================
// Sub-components
// ============================================================================

interface CaptureFormProps {
  value: string
  setValue: (value: string) => void
  onSubmit: (e: React.FormEvent) => void
  onClose: () => void
  isSaving: boolean
  inputRef: React.RefObject<HTMLInputElement | null>
}

function CaptureForm({
  value,
  setValue,
  onSubmit,
  onClose,
  isSaving,
  inputRef,
}: CaptureFormProps) {
  return (
    <form onSubmit={onSubmit}>
      <label
        id="quick-capture-title"
        className="block text-sm font-medium mb-2"
      >
        Quick thought:
      </label>
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="What's on your mind?"
        className={cn(
          'w-full rounded-md border p-2 text-sm',
          'focus:outline-none focus:ring-2 focus:ring-primary',
          isSaving && 'opacity-50'
        )}
        disabled={isSaving}
        autoComplete="off"
      />
      <div className="flex justify-end gap-2 mt-3">
        <button
          type="button"
          onClick={onClose}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          disabled={isSaving}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={!value.trim() || isSaving}
          className={cn(
            'text-sm px-3 py-1.5 rounded-md',
            'bg-primary text-primary-foreground',
            'hover:bg-primary/90 transition-colors',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          {isSaving ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  )
}

function SuccessMessage() {
  return (
    <div className="flex items-center gap-2 text-green-600 dark:text-green-400 py-2">
      <CheckIcon className="w-5 h-5" />
      <span className="font-medium">Saved to inbox</span>
    </div>
  )
}

// ============================================================================
// Trigger Button (for use in FocusModeContainer)
// ============================================================================

export interface QuickCaptureTriggerProps {
  onClick: () => void
  className?: string
}

export function QuickCaptureTrigger({ onClick, className }: QuickCaptureTriggerProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'p-2 rounded-lg text-muted-foreground',
        'hover:bg-muted hover:text-foreground transition-colors',
        className
      )}
      aria-label="Quick capture thought"
      title="Quick capture (won't interrupt your focus)"
    >
      <LightbulbIcon className="w-5 h-5" />
    </button>
  )
}

// ============================================================================
// Icons
// ============================================================================

function CheckIcon({ className }: { className?: string }) {
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
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function LightbulbIcon({ className }: { className?: string }) {
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
      <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
      <path d="M9 18h6" />
      <path d="M10 22h4" />
    </svg>
  )
}
