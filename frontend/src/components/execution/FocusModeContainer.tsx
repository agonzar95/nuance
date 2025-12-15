'use client'

import { useState, useEffect } from 'react'
import { FocusTimer, useFocusTimer } from '@/components/execution/FocusTimer'
import type { Action } from '@/types/api'

interface FocusModeContainerProps {
  action: Action
  onComplete: () => void
  onStuck: () => void
  onExit: () => void
  children?: React.ReactNode
}

/**
 * Full-screen container for distraction-free focus mode.
 * Hides navigation, displays timer, and provides minimal controls.
 */
export function FocusModeContainer({
  action,
  onComplete,
  onStuck,
  onExit,
  children
}: FocusModeContainerProps) {
  const [showExitConfirm, setShowExitConfirm] = useState(false)
  const { seconds } = useFocusTimer(action.id)

  // Hide navbar on mount by adding class to body
  useEffect(() => {
    document.body.classList.add('focus-mode')
    return () => document.body.classList.remove('focus-mode')
  }, [])

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setShowExitConfirm(true)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className="fixed inset-0 bg-background z-50 flex flex-col">
      {/* Minimal Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <button
          onClick={() => setShowExitConfirm(true)}
          className="text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Exit focus mode"
        >
          <ArrowLeftIcon className="w-5 h-5" />
        </button>
        <FocusTimer seconds={seconds} />
        <div className="w-5" /> {/* Spacer for centering */}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 overflow-y-auto">
        {children}
      </div>

      {/* Action Bar */}
      <div className="p-4 border-t flex items-center justify-center gap-4">
        <button
          onClick={onStuck}
          className="px-6 py-3 rounded-lg border hover:bg-muted transition-colors"
        >
          I'm stuck
        </button>
        <button
          onClick={onComplete}
          className="px-8 py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
        >
          Done
        </button>
      </div>

      {/* Exit Confirmation Dialog */}
      <ExitConfirmDialog
        open={showExitConfirm}
        onConfirm={onExit}
        onCancel={() => setShowExitConfirm(false)}
        elapsedSeconds={seconds}
      />
    </div>
  )
}

interface ExitConfirmDialogProps {
  open: boolean
  onConfirm: () => void
  onCancel: () => void
  elapsedSeconds: number
}

function ExitConfirmDialog({
  open,
  onConfirm,
  onCancel,
  elapsedSeconds
}: ExitConfirmDialogProps) {
  if (!open) return null

  const minutes = Math.floor(elapsedSeconds / 60)

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-background rounded-lg p-6 max-w-sm w-full space-y-4">
        <h3 className="text-lg font-medium">Exit focus mode?</h3>
        <p className="text-muted-foreground">
          {minutes > 0
            ? `You've been working for ${minutes} minute${minutes === 1 ? '' : 's'}. Your progress will be saved.`
            : 'Your progress will be saved.'}
        </p>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 py-2 rounded-lg border hover:bg-muted transition-colors"
          >
            Keep going
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
          >
            Exit
          </button>
        </div>
      </div>
    </div>
  )
}

function ArrowLeftIcon({ className }: { className?: string }) {
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
      <path d="M19 12H5" />
      <path d="m12 19-7-7 7-7" />
    </svg>
  )
}
