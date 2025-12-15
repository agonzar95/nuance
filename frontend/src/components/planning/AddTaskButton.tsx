'use client'

/**
 * PLN-007: Add More Tasks
 *
 * Button and dialog for adding more tasks to today's plan:
 * - Quick capture: Type a new task directly
 * - Browse existing: Select from all actions
 */

import { useState, useCallback } from 'react'
import { cn } from '@/lib/utils'
import type { Action } from '@/types/api'

// ============================================================================
// Types
// ============================================================================

export interface AddTaskButtonProps {
  /** Handler when a task is added */
  onAddTask: (action: Action) => void
  /** Handler for quick capture text (creates new action) */
  onQuickCapture?: (text: string) => Promise<Action | undefined>
  /** All available actions to browse (excluding already planned) */
  availableActions?: Action[]
  /** Whether quick capture is in progress */
  isCapturing?: boolean
  /** Additional class names */
  className?: string
}

type Mode = 'choose' | 'capture' | 'browse' | null

// ============================================================================
// Component
// ============================================================================

export function AddTaskButton({
  onAddTask,
  onQuickCapture,
  availableActions = [],
  isCapturing,
  className,
}: AddTaskButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [mode, setMode] = useState<Mode>(null)
  const [captureText, setCaptureText] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  const handleClose = useCallback(() => {
    setIsOpen(false)
    setMode(null)
    setCaptureText('')
    setSearchQuery('')
  }, [])

  const handleQuickCapture = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      if (!captureText.trim() || !onQuickCapture) return

      const action = await onQuickCapture(captureText.trim())
      if (action) {
        onAddTask(action)
        handleClose()
      }
    },
    [captureText, onQuickCapture, onAddTask, handleClose]
  )

  const handleSelectAction = useCallback(
    (action: Action) => {
      onAddTask(action)
      handleClose()
    },
    [onAddTask, handleClose]
  )

  // Filter actions by search query
  const filteredActions = searchQuery.trim()
    ? availableActions.filter((a) =>
        a.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : availableActions

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={cn(
          'w-full py-3 border-2 border-dashed rounded-lg',
          'text-muted-foreground transition-colors',
          'hover:border-primary hover:text-primary',
          className
        )}
      >
        <PlusIcon className="w-5 h-5 inline mr-2" />
        Add more tasks
      </button>

      {/* Dialog */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50"
            onClick={handleClose}
            aria-hidden="true"
          />

          {/* Dialog Content */}
          <div className="relative bg-background rounded-lg shadow-lg w-full max-w-md p-6">
            {/* Close button */}
            <button
              onClick={handleClose}
              className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
              aria-label="Close"
            >
              <XIcon className="w-5 h-5" />
            </button>

            {/* Mode Selection */}
            {!mode && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Add a task</h3>

                <button
                  onClick={() => setMode('capture')}
                  className="w-full p-4 text-left border rounded-lg hover:bg-muted transition-colors"
                >
                  <span className="font-medium">Quick capture</span>
                  <p className="text-sm text-muted-foreground mt-1">
                    Describe what you need to do
                  </p>
                </button>

                {availableActions.length > 0 && (
                  <button
                    onClick={() => setMode('browse')}
                    className="w-full p-4 text-left border rounded-lg hover:bg-muted transition-colors"
                  >
                    <span className="font-medium">Browse existing</span>
                    <p className="text-sm text-muted-foreground mt-1">
                      Add from your task list ({availableActions.length} available)
                    </p>
                  </button>
                )}
              </div>
            )}

            {/* Quick Capture Mode */}
            {mode === 'capture' && (
              <div className="space-y-4">
                <button
                  onClick={() => setMode(null)}
                  className="text-sm text-muted-foreground hover:text-foreground"
                >
                  <ArrowLeftIcon className="w-4 h-4 inline mr-1" />
                  Back
                </button>

                <h3 className="text-lg font-medium">Quick capture</h3>

                <form onSubmit={handleQuickCapture}>
                  <input
                    type="text"
                    value={captureText}
                    onChange={(e) => setCaptureText(e.target.value)}
                    placeholder="What do you need to do?"
                    className="w-full rounded-md border p-3 focus:outline-none focus:ring-2 focus:ring-primary"
                    autoFocus
                    disabled={isCapturing}
                  />
                  <div className="flex justify-end gap-2 mt-4">
                    <button
                      type="button"
                      onClick={handleClose}
                      className="px-4 py-2 text-muted-foreground"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={!captureText.trim() || isCapturing}
                      className={cn(
                        'px-4 py-2 bg-primary text-primary-foreground rounded-md',
                        'disabled:opacity-50 disabled:cursor-not-allowed'
                      )}
                    >
                      {isCapturing ? 'Adding...' : 'Add to Today'}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Browse Mode */}
            {mode === 'browse' && (
              <div className="space-y-4">
                <button
                  onClick={() => setMode(null)}
                  className="text-sm text-muted-foreground hover:text-foreground"
                >
                  <ArrowLeftIcon className="w-4 h-4 inline mr-1" />
                  Back
                </button>

                <h3 className="text-lg font-medium">Select a task</h3>

                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search tasks..."
                  className="w-full rounded-md border p-2 focus:outline-none focus:ring-2 focus:ring-primary"
                  autoFocus
                />

                <div className="max-h-64 overflow-y-auto space-y-2">
                  {filteredActions.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      {searchQuery ? 'No matching tasks' : 'No tasks available'}
                    </p>
                  ) : (
                    filteredActions.map((action) => (
                      <button
                        key={action.id}
                        onClick={() => handleSelectAction(action)}
                        className="w-full p-3 text-left border rounded-lg hover:bg-muted transition-colors"
                      >
                        <span className="font-medium text-sm">{action.title}</span>
                        {action.estimated_minutes && (
                          <span className="text-xs text-muted-foreground ml-2">
                            ~{action.estimated_minutes}min
                          </span>
                        )}
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}

// ============================================================================
// Icons
// ============================================================================

function PlusIcon({ className }: { className?: string }) {
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
      <line x1="12" x2="12" y1="5" y2="19" />
      <line x1="5" x2="19" y1="12" y2="12" />
    </svg>
  )
}

function XIcon({ className }: { className?: string }) {
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
      <line x1="18" x2="6" y1="6" y2="18" />
      <line x1="6" x2="18" y1="6" y2="18" />
    </svg>
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
