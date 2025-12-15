'use client'

import { useState, useEffect } from 'react'

interface RestScreenProps {
  suggestedMinutes?: number
  onReady: () => void
  onSkip: () => void
}

/**
 * Calming rest screen shown between focus blocks.
 * Provides guilt-free break time with optional countdown.
 */
export function RestScreen({
  suggestedMinutes = 5,
  onReady,
  onSkip
}: RestScreenProps) {
  const [secondsRemaining, setSecondsRemaining] = useState(suggestedMinutes * 60)
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    if (isPaused || secondsRemaining <= 0) return

    const interval = setInterval(() => {
      setSecondsRemaining(s => s - 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [isPaused, secondsRemaining])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-b from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-slate-800 flex flex-col items-center justify-center p-6 z-50">
      {/* Calming Visual */}
      <div className="w-32 h-32 rounded-full bg-white/50 dark:bg-white/10 flex items-center justify-center mb-8">
        <CoffeeIcon className="w-16 h-16 text-muted-foreground" />
      </div>

      {/* Message */}
      <h2 className="text-2xl font-light mb-2">Take a moment</h2>
      <p className="text-muted-foreground mb-8">
        You've earned a break
      </p>

      {/* Timer */}
      {secondsRemaining > 0 ? (
        <div className="text-4xl font-light font-mono mb-8">
          {formatTime(secondsRemaining)}
        </div>
      ) : (
        <p className="text-lg mb-8">Ready when you are</p>
      )}

      {/* Actions */}
      <div className="space-y-3 w-full max-w-xs">
        <button
          onClick={onReady}
          className="w-full px-8 py-3 rounded-lg bg-white dark:bg-slate-700 shadow-sm font-medium hover:shadow-md transition-shadow"
        >
          I'm ready to continue
        </button>

        {secondsRemaining > 0 && (
          <button
            onClick={onSkip}
            className="block w-full text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Skip break
          </button>
        )}
      </div>
    </div>
  )
}

function CoffeeIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M17 8h1a4 4 0 1 1 0 8h-1" />
      <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z" />
      <line x1="6" x2="6" y1="2" y2="4" />
      <line x1="10" x2="10" y1="2" y2="4" />
      <line x1="14" x2="14" y1="2" y2="4" />
    </svg>
  )
}
