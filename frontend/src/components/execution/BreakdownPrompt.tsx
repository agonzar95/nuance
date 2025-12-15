'use client'

import { useState } from 'react'
import type { Action } from '@/types/api'

interface BreakdownPromptProps {
  action: Action
  onSubmitStep: (step: string) => Promise<void>
  onSkip: () => void
  isLoading?: boolean
}

/**
 * Prompts user to identify the smallest first step for complex tasks.
 * Helps overcome paralysis by focusing on immediate, concrete actions.
 */
export function BreakdownPrompt({
  action,
  onSubmitStep,
  onSkip,
  isLoading
}: BreakdownPromptProps) {
  const [step, setStep] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!step.trim()) return
    await onSubmitStep(step.trim())
  }

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-xl font-medium">
          This looks like a bigger task
        </h2>
        <p className="text-muted-foreground">
          What's the smallest first step you can take?
        </p>
      </div>

      {/* Task context */}
      <div className="px-4 py-3 bg-muted/50 rounded-lg text-center">
        <p className="font-medium">{action.title}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          value={step}
          onChange={(e) => setStep(e.target.value)}
          placeholder="e.g., Open the document and read the first paragraph"
          className="w-full px-4 py-3 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
          autoFocus
          disabled={isLoading}
        />

        <div className="flex gap-3">
          <button
            type="button"
            onClick={onSkip}
            className="flex-1 py-3 rounded-lg border hover:bg-muted transition-colors"
            disabled={isLoading}
          >
            Skip for now
          </button>
          <button
            type="submit"
            disabled={!step.trim() || isLoading}
            className="flex-1 py-3 rounded-lg bg-primary text-primary-foreground disabled:opacity-50 transition-opacity"
          >
            {isLoading ? 'Saving...' : 'Start with this'}
          </button>
        </div>
      </form>
    </div>
  )
}
