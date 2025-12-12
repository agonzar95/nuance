'use client'

import { useEffect, useMemo } from 'react'

interface Action {
  id: string
  title: string
  avoidance_weight: number
}

interface AvoidanceAcknowledgmentProps {
  action: Action
  onContinue: () => void
}

const ACKNOWLEDGMENT_MESSAGES = [
  "That one was hard, and you did it anyway.",
  "You pushed through something you'd been avoiding.",
  "That took real effort. Well done.",
  "The hard ones count extra. Nice work."
]

export function AvoidanceAcknowledgment({
  action,
  onContinue
}: AvoidanceAcknowledgmentProps) {
  const message = useMemo(() => {
    const index = Math.floor(Math.random() * ACKNOWLEDGMENT_MESSAGES.length)
    return ACKNOWLEDGMENT_MESSAGES[index]
  }, [])

  // Auto-continue after delay
  useEffect(() => {
    const timer = setTimeout(onContinue, 4000)
    return () => clearTimeout(timer)
  }, [onContinue])

  return (
    <div className="w-full max-w-md text-center space-y-6 animate-fade-in">
      {/* Enhanced Visual */}
      <div className="relative">
        <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
          <StarIcon className="w-10 h-10 text-white" />
        </div>
        <div className="absolute -inset-4 rounded-full bg-amber-400/20 animate-pulse" />
      </div>

      {/* Message */}
      <div className="space-y-2">
        <h2 className="text-xl font-medium">{message}</h2>
        <p className="text-muted-foreground">
          {action.title}
        </p>
      </div>

      {/* Continue */}
      <button
        onClick={onContinue}
        className="text-sm text-muted-foreground hover:text-foreground"
      >
        Continue
      </button>
    </div>
  )
}

function StarIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  )
}
